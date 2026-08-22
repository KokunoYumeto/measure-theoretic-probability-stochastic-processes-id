#!/usr/bin/env python3
"""Freeze and prove the O009 QuantEcon Python environment.

This deliberately starts from the already-resolved virtual environment.  It
captures every installed distribution, downloads exactly one compatible wheel
for each distribution, writes a hash-required lock, and proves that lock in a
new network-disabled replay environment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import sysconfig
from datetime import datetime, timezone

from packaging.tags import sys_tags
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version


PIN_RE = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s;]+)$")
LOCK_RE = re.compile(
    r"^([A-Za-z0-9_.-]+)==([^\s;]+) --hash=sha256:([0-9a-f]{64})$"
)
MANIFEST_FIELDS = [
    "distribution",
    "canonical_name",
    "version",
    "wheel_filename",
    "bytes",
    "sha256",
    "wheel_tags",
    "compatible_tags",
]
DETERMINISTIC_ENVIRONMENT = {
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "MPLBACKEND": "Agg",
    "NUMBA_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
    # ZIP-based Windows console launchers reject pre-1980 timestamps.
    "SOURCE_DATE_EPOCH": "315532800",
    "TZ": "UTC",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, object]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def run(
    command: list[str],
    *,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )
    if completed.returncode != 0:
        rendered = subprocess.list2cmdline(command)
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {rendered}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def normalized_output(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def parse_exact_pins(text: str, *, comments_allowed: bool) -> list[dict[str, str]]:
    pins: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_line in text.replace("\r\n", "\n").split("\n"):
        stripped = raw_line.strip()
        if not stripped or (comments_allowed and stripped.startswith("#")):
            continue
        match = PIN_RE.fullmatch(stripped)
        if match is None:
            raise RuntimeError(f"Non-exact requirement is not admissible: {raw_line!r}")
        name, version = match.groups()
        canonical = canonicalize_name(name)
        if canonical in seen:
            raise RuntimeError(f"Duplicate requirement after name normalization: {name}")
        seen.add(canonical)
        pins.append(
            {
                "name": name,
                "canonical_name": canonical,
                "version": version,
                "line": stripped,
            }
        )
    if not pins:
        raise RuntimeError("The requirement set is empty.")
    return pins


def tree_record(root: Path) -> dict[str, object]:
    files = sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    total_bytes = 0
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        file_hash = sha256_file(path)
        total_bytes += size
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(file_hash))
        digest.update(b"\n")
    return {
        "path": str(root.resolve()),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def interpreter_receipt(
    resolver_python: Path, *, non_mutating: bool = False
) -> dict[str, object]:
    probe = run(
        [
            str(resolver_python),
            "-c",
            (
                "import json,platform,sys,sysconfig;"
                "print(json.dumps({"
                "'version':sys.version,'version_info':list(sys.version_info),"
                "'executable':sys.executable,"
                "'base_executable':getattr(sys,'_base_executable',None),"
                "'prefix':sys.prefix,'base_prefix':sys.base_prefix,"
                "'implementation':platform.python_implementation(),"
                "'platform':platform.platform(),"
                "'cache_tag':sys.implementation.cache_tag,"
                "'soabi':sysconfig.get_config_var('SOABI'),"
                "'ldlibrary':sysconfig.get_config_var('LDLIBRARY')},sort_keys=True))"
            ),
        ],
        environment=deterministic_subprocess_environment(non_mutating=non_mutating),
    )
    information = json.loads(probe.stdout)
    base_prefix = Path(information["base_prefix"])
    base_executable = Path(information["base_executable"])
    candidates = [
        resolver_python,
        resolver_python.with_name("pythonw.exe"),
        base_executable,
        base_executable.with_name("pythonw.exe"),
        base_prefix / "python3.dll",
        base_prefix / "python313.dll",
        base_prefix / "vcruntime140.dll",
        base_prefix / "vcruntime140_1.dll",
    ]
    artifacts: list[dict[str, object]] = []
    missing: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate.resolve()).casefold() if candidate.exists() else str(candidate).casefold()
        if key in seen:
            continue
        seen.add(key)
        if candidate.is_file():
            artifacts.append(file_record(candidate))
        else:
            missing.append(str(candidate))
    information["artifacts"] = artifacts
    information["absent_optional_artifact_candidates"] = missing
    return information


def deterministic_subprocess_environment(
    *, offline: bool = False, non_mutating: bool = False
) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(DETERMINISTIC_ENVIRONMENT)
    environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    environment["PIP_CONFIG_FILE"] = os.devnull
    if offline:
        environment["PIP_NO_INDEX"] = "1"
    else:
        environment.pop("PIP_NO_INDEX", None)
    if non_mutating:
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def scientific_and_toolchain_probe(
    replay_python: Path, *, non_mutating: bool = False
) -> dict[str, object]:
    program = r'''
import importlib
import importlib.metadata
import json
import os

import matplotlib
matplotlib.use("Agg", force=True)
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numba
import numpy as np
import quantecon as qe
import scipy
from scipy.linalg import expm

@numba.njit(cache=False)
def compiled_sum(values):
    total = 0.0
    for value in values:
        total += value
    return total

generator = np.random.default_rng(20260822)
draws = generator.standard_normal(8)
generator_matrix = np.array([[-0.25, 0.25], [0.5, -0.5]])
transition = expm(generator_matrix * 2.0)
chain = qe.MarkovChain(np.array([[0.9, 0.1], [0.2, 0.8]]))

figure = Figure(figsize=(2.0, 1.0), dpi=80)
axis = figure.subplots()
axis.plot([0.0, 1.0], [0.0, 1.0])
canvas = FigureCanvasAgg(figure)
canvas.draw()

modules = [
    "jupyter_book",
    "myst_nb",
    "quantecon_book_theme",
    "sphinx",
    "sphinx_exercise",
    "sphinx_external_toc",
    "sphinx_jupyterbook_latex",
    "sphinx_proof",
    "sphinx_togglebutton",
    "sphinx_tojupyter",
    "sphinxcontrib.youtube",
    "sphinxext.rediraffe",
]
for module in modules:
    importlib.import_module(module)

distributions = [
    "jupyter-book",
    "matplotlib",
    "numba",
    "numpy",
    "quantecon",
    "quantecon-book-theme",
    "scipy",
    "sphinx",
    "sphinx-exercise",
    "sphinx-proof",
    "sphinx-tojupyter",
]
result = {
    "deterministic_environment": {key: os.environ.get(key) for key in sorted([
        "LANG", "LC_ALL", "MPLBACKEND", "NUMBA_NUM_THREADS",
        "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
        "PYTHONHASHSEED", "PYTHONIOENCODING", "PYTHONUTF8",
        "SOURCE_DATE_EPOCH", "TZ"
    ])},
    "distribution_versions": {
        name: importlib.metadata.version(name) for name in distributions
    },
    "imported_modules": modules,
    "matplotlib_canvas": list(canvas.get_width_height()),
    "numba_compiled_sum": float(compiled_sum(draws)),
    "numpy_draws_sha256": __import__("hashlib").sha256(draws.tobytes()).hexdigest(),
    "quantecon_stationary_distributions": chain.stationary_distributions.tolist(),
    "scipy_expm": transition.tolist(),
    "scipy_expm_row_sums": transition.sum(axis=1).tolist(),
}
print(json.dumps(result, sort_keys=True))
'''
    completed = run(
        [str(replay_python), "-c", program],
        environment=deterministic_subprocess_environment(
            offline=True, non_mutating=non_mutating
        ),
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("The scientific/toolchain probe produced no JSON output.")
    return json.loads(lines[-1])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def assert_file_record(
    actual_path: Path, expected: dict[str, object], *, label: str
) -> None:
    require(actual_path.is_file(), f"Missing {label}: {actual_path}")
    expected_path = Path(str(expected.get("path", "")))
    require(
        str(expected_path.resolve()).casefold()
        == str(actual_path.resolve()).casefold(),
        f"Receipt path mismatch for {label}: {expected_path} != {actual_path}",
    )
    require(
        int(expected.get("bytes", -1)) == actual_path.stat().st_size,
        f"Receipt byte-count mismatch for {label}",
    )
    require(
        str(expected.get("sha256", "")) == sha256_file(actual_path),
        f"Receipt SHA-256 mismatch for {label}",
    )


def frozen_output_snapshot(
    requirements_in: Path,
    requirements_resolved: Path,
    requirements_lock: Path,
    wheelhouse_manifest: Path,
    wheelhouse: Path,
) -> dict[str, object]:
    named = {
        path.name: file_record(path)
        for path in (
            requirements_in,
            requirements_resolved,
            requirements_lock,
            wheelhouse_manifest,
        )
    }
    wheels = {
        path.name: {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(wheelhouse.glob("*.whl"), key=lambda item: item.name.casefold())
    }
    return {"named": named, "wheels": wheels}


def check_existing_environment(
    *,
    resolver_python: Path,
    replay_root: Path,
    output_root: Path,
    script_path: Path,
    require_current_script_record: bool,
) -> dict[str, object]:
    requirements_in = output_root / "requirements.in"
    requirements_resolved = output_root / "requirements.resolved.txt"
    requirements_lock = output_root / "requirements.lock"
    wheelhouse = output_root / "wheelhouse"
    wheelhouse_manifest = output_root / "WHEELHOUSE_MANIFEST.tsv"
    receipt_path = output_root / "ENVIRONMENT_RECEIPT.json"
    replay_python = replay_root / "Scripts" / "python.exe"

    require(
        Path(sys.executable).resolve() == resolver_python.resolve(),
        "Run the checker with the exact resolver interpreter supplied by --resolver.",
    )
    for label, path in (
        ("resolver interpreter", resolver_python),
        ("replay interpreter", replay_python),
        ("requirements.in", requirements_in),
        ("requirements.resolved.txt", requirements_resolved),
        ("requirements.lock", requirements_lock),
        ("wheelhouse manifest", wheelhouse_manifest),
        ("environment receipt", receipt_path),
    ):
        require(path.is_file(), f"Missing {label}: {path}")
    require(wheelhouse.is_dir(), f"Missing wheelhouse: {wheelhouse}")

    receipt_bytes_before = receipt_path.read_bytes()
    receipt_sha_before = hashlib.sha256(receipt_bytes_before).hexdigest()
    receipt = json.loads(receipt_bytes_before.decode("utf-8"))
    require(receipt.get("schema_version") == 1, "Unsupported environment receipt schema.")
    require(
        receipt.get("deterministic_environment") == DETERMINISTIC_ENVIRONMENT,
        "Deterministic environment in receipt differs from the checker contract.",
    )
    policy = receipt.get("policy", {})
    for key in (
        "download_only_binary",
        "one_wheel_per_distribution",
        "offline_install_no_index",
        "offline_install_require_hashes",
        "offline_install_force_reinstall",
        "resolver_and_replay_freeze_exact_match",
    ):
        require(policy.get(key) is True, f"Receipt policy flag is not true: {key}")

    receipt_files = receipt.get("files", {})
    for key, path in (
        ("requirements_in", requirements_in),
        ("requirements_resolved", requirements_resolved),
        ("requirements_lock", requirements_lock),
        ("wheelhouse_manifest", wheelhouse_manifest),
    ):
        expected = receipt_files.get(key)
        require(isinstance(expected, dict), f"Receipt lacks file record: {key}")
        assert_file_record(path, expected, label=key)
    script_record = receipt_files.get("script")
    require(isinstance(script_record, dict), "Receipt lacks the generator script record.")
    if require_current_script_record:
        assert_file_record(script_path, script_record, label="generator/checker script")
    else:
        require(
            str(Path(str(script_record.get("path", ""))).resolve()).casefold()
            == str(script_path.resolve()).casefold(),
            "Historical generator script path does not match the final checker path.",
        )
        require(
            isinstance(script_record.get("bytes"), int)
            and int(script_record["bytes"]) > 0
            and re.fullmatch(r"[0-9a-f]{64}", str(script_record.get("sha256", "")))
            is not None,
            "Historical generator script record is malformed.",
        )

    resolved_text = requirements_resolved.read_text(encoding="utf-8")
    require(
        normalized_output(resolved_text) == resolved_text,
        "requirements.resolved.txt is not canonical LF-terminated freeze output.",
    )
    resolved_pins = parse_exact_pins(resolved_text, comments_allowed=False)
    resolved_by_name = {pin["canonical_name"]: pin for pin in resolved_pins}
    top_level_pins = parse_exact_pins(
        requirements_in.read_text(encoding="utf-8"), comments_allowed=True
    )
    for requested in top_level_pins:
        actual = resolved_by_name.get(requested["canonical_name"])
        require(
            actual is not None
            and Version(actual["version"]) == Version(requested["version"]),
            f"Resolved closure no longer preserves top-level pin {requested['line']}",
        )

    with wheelhouse_manifest.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        require(reader.fieldnames == MANIFEST_FIELDS, "Wheelhouse manifest header changed.")
        manifest_rows = list(reader)
    require(
        len(manifest_rows) == len(resolved_pins),
        "Wheelhouse manifest/distribution cardinality mismatch.",
    )
    rows_by_name: dict[str, dict[str, str]] = {}
    runtime_tags = set(sys_tags())
    for row in manifest_rows:
        canonical = row["canonical_name"]
        require(canonical not in rows_by_name, f"Duplicate manifest row: {canonical}")
        pin = resolved_by_name.get(canonical)
        require(pin is not None, f"Manifest has extraneous distribution: {canonical}")
        require(
            row["distribution"] == pin["name"]
            and Version(row["version"]) == Version(pin["version"]),
            f"Manifest name/version mismatch for {canonical}",
        )
        wheel = wheelhouse / row["wheel_filename"]
        require(wheel.is_file(), f"Manifested wheel is missing: {wheel.name}")
        distribution, version, _build, tags = parse_wheel_filename(wheel.name)
        require(
            canonicalize_name(distribution) == canonical
            and version == Version(pin["version"]),
            f"Wheel filename identity mismatch: {wheel.name}",
        )
        expected_tags = ",".join(sorted(str(tag) for tag in tags))
        compatible_tags = ",".join(sorted(str(tag) for tag in tags & runtime_tags))
        require(compatible_tags, f"Wheel is not compatible with this runtime: {wheel.name}")
        require(
            row["wheel_tags"] == expected_tags
            and row["compatible_tags"] == compatible_tags,
            f"Wheel tag record mismatch: {wheel.name}",
        )
        require(
            int(row["bytes"]) == wheel.stat().st_size
            and row["sha256"] == sha256_file(wheel),
            f"Wheel byte/hash mismatch: {wheel.name}",
        )
        rows_by_name[canonical] = row

    wheel_files = sorted(wheelhouse.glob("*.whl"), key=lambda item: item.name.casefold())
    unexpected_entries = [
        item.name
        for item in wheelhouse.iterdir()
        if not item.is_file() or item.suffix != ".whl"
    ]
    require(not unexpected_entries, f"Unexpected wheelhouse entries: {unexpected_entries}")
    require(
        {path.name for path in wheel_files}
        == {row["wheel_filename"] for row in manifest_rows},
        "Wheelhouse and manifest filenames do not form an exact set.",
    )

    lock_rows: list[tuple[str, str, str]] = []
    for raw_line in requirements_lock.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = LOCK_RE.fullmatch(stripped)
        require(match is not None, f"Malformed hash-lock row: {raw_line!r}")
        lock_rows.append(match.groups())
    require(len(lock_rows) == len(resolved_pins), "Hash lock cardinality mismatch.")
    for pin, (name, version, locked_hash) in zip(resolved_pins, lock_rows, strict=True):
        canonical = canonicalize_name(name)
        require(
            canonical == pin["canonical_name"]
            and Version(version) == Version(pin["version"]),
            f"Hash lock order/identity mismatch for {pin['line']}",
        )
        require(
            locked_hash == rows_by_name[canonical]["sha256"],
            f"Hash lock does not bind manifested wheel for {canonical}",
        )

    wheelhouse_bytes = sum(path.stat().st_size for path in wheel_files)
    wheelhouse_receipt = receipt.get("wheelhouse", {})
    require(
        str(Path(str(wheelhouse_receipt.get("path", ""))).resolve()).casefold()
        == str(wheelhouse.resolve()).casefold(),
        "Receipt wheelhouse path mismatch.",
    )
    require(
        wheelhouse_receipt.get("wheel_count") == len(wheel_files)
        and wheelhouse_receipt.get("total_bytes") == wheelhouse_bytes
        and wheelhouse_receipt.get("manifest_sha256")
        == sha256_file(wheelhouse_manifest),
        "Receipt wheelhouse summary mismatch.",
    )
    require(
        receipt.get("top_level_requirement_count") == len(top_level_pins),
        "Receipt top-level requirement count mismatch.",
    )

    frozen_before = frozen_output_snapshot(
        requirements_in,
        requirements_resolved,
        requirements_lock,
        wheelhouse_manifest,
        wheelhouse,
    )
    replay_tree_before = tree_record(replay_root)
    require(
        replay_tree_before == receipt.get("offline_replay", {}).get("tree"),
        "Replay tree no longer matches the frozen receipt.",
    )

    online_environment = deterministic_subprocess_environment(non_mutating=True)
    offline_environment = deterministic_subprocess_environment(
        offline=True, non_mutating=True
    )
    resolver_pip_version = normalized_output(
        run(
            [str(resolver_python), "-m", "pip", "--version"],
            environment=online_environment,
        ).stdout
    ).strip()
    resolver_check = normalized_output(
        run(
            [str(resolver_python), "-m", "pip", "check"],
            environment=online_environment,
        ).stdout
    ).strip()
    resolver_freeze = normalized_output(
        run(
            [str(resolver_python), "-m", "pip", "freeze", "--all"],
            environment=online_environment,
        ).stdout
    )
    replay_check = normalized_output(
        run(
            [str(replay_python), "-m", "pip", "check"],
            environment=offline_environment,
        ).stdout
    ).strip()
    replay_freeze = normalized_output(
        run(
            [str(replay_python), "-m", "pip", "freeze", "--all"],
            environment=offline_environment,
        ).stdout
    )
    require(
        resolver_check == "No broken requirements found."
        and replay_check == "No broken requirements found.",
        "Resolver or replay pip check failed.",
    )
    require(
        resolver_freeze == resolved_text and replay_freeze == resolved_text,
        "Resolver/replay freeze is not byte-exact to requirements.resolved.txt.",
    )
    freeze_sha = hashlib.sha256(resolved_text.encode("utf-8")).hexdigest()
    resolver_receipt = receipt.get("resolver", {})
    require(
        resolver_receipt.get("path") == str(resolver_python)
        and resolver_receipt.get("pip_version") == resolver_pip_version
        and resolver_receipt.get("pip_check") == resolver_check
        and resolver_receipt.get("distribution_count") == len(resolved_pins)
        and resolver_receipt.get("freeze_sha256") == freeze_sha,
        "Resolver receipt does not match the live frozen resolver.",
    )
    require(
        interpreter_receipt(resolver_python, non_mutating=True)
        == receipt.get("interpreter"),
        "Interpreter/base executable/DLL receipt mismatch.",
    )

    replay_receipt = receipt.get("offline_replay", {})
    require(
        str(Path(str(replay_receipt.get("path", ""))).resolve()).casefold()
        == str(replay_root.resolve()).casefold(),
        "Replay path in receipt differs from --replay.",
    )
    assert_file_record(
        replay_python, replay_receipt.get("python", {}), label="replay Python"
    )
    require(
        replay_receipt.get("pip_check") == replay_check
        and replay_receipt.get("freeze_exact_match") is True
        and replay_receipt.get("freeze_sha256") == freeze_sha,
        "Replay pip/freeze receipt mismatch.",
    )
    replay_bin = replay_root / "Scripts"
    jupyter_book_version = normalized_output(
        run(
            [str(replay_bin / "jupyter-book.exe"), "--version"],
            environment=offline_environment,
        ).stdout
    ).strip()
    sphinx_version = normalized_output(
        run(
            [str(replay_bin / "sphinx-build.exe"), "--version"],
            environment=offline_environment,
        ).stdout
    ).strip()
    probe = scientific_and_toolchain_probe(replay_python, non_mutating=True)
    require(
        replay_receipt.get("jupyter_book_version") == jupyter_book_version
        and replay_receipt.get("sphinx_build_version") == sphinx_version
        and replay_receipt.get("probe") == probe,
        "Replay runtime/toolchain probe differs from the receipt.",
    )

    replay_tree_after = tree_record(replay_root)
    frozen_after = frozen_output_snapshot(
        requirements_in,
        requirements_resolved,
        requirements_lock,
        wheelhouse_manifest,
        wheelhouse,
    )
    receipt_bytes_after = receipt_path.read_bytes()
    require(replay_tree_after == replay_tree_before, "Check mutated the replay tree.")
    require(frozen_after == frozen_before, "Check mutated frozen environment outputs.")
    require(
        receipt_bytes_after == receipt_bytes_before,
        "Check mutated ENVIRONMENT_RECEIPT.json.",
    )

    return {
        "status": "PASS",
        "mode": "check",
        "distribution_count": len(resolved_pins),
        "wheel_count": len(wheel_files),
        "wheelhouse_bytes": wheelhouse_bytes,
        "freeze_sha256": freeze_sha,
        "requirements_lock_sha256": sha256_file(requirements_lock),
        "wheelhouse_manifest_sha256": sha256_file(wheelhouse_manifest),
        "receipt_sha256": receipt_sha_before,
        "replay_file_count": replay_tree_after["file_count"],
        "replay_total_bytes": replay_tree_after["total_bytes"],
        "replay_tree_sha256": replay_tree_after["tree_sha256"],
        "pip_check": {
            "resolver": resolver_check,
            "offline_replay": replay_check,
        },
        "runtime_probe": {
            "numpy": probe["distribution_versions"]["numpy"],
            "scipy": probe["distribution_versions"]["scipy"],
            "matplotlib": probe["distribution_versions"]["matplotlib"],
            "numba": probe["distribution_versions"]["numba"],
            "quantecon": probe["distribution_versions"]["quantecon"],
            "jupyter_book": probe["distribution_versions"]["jupyter-book"],
            "sphinx": probe["distribution_versions"]["sphinx"],
        },
        "non_mutating": {
            "receipt_unchanged": True,
            "frozen_outputs_unchanged": True,
            "replay_tree_unchanged": True,
        },
    }


def finalize_receipt(
    *,
    resolver_python: Path,
    replay_root: Path,
    output_root: Path,
    script_path: Path,
) -> dict[str, object]:
    verification = check_existing_environment(
        resolver_python=resolver_python,
        replay_root=replay_root,
        output_root=output_root,
        script_path=script_path,
        require_current_script_record=False,
    )
    receipt_path = output_root / "ENVIRONMENT_RECEIPT.json"
    previous_bytes = receipt_path.read_bytes()
    previous_sha = hashlib.sha256(previous_bytes).hexdigest()
    receipt = json.loads(previous_bytes.decode("utf-8"))
    previous_script_record = receipt["files"]["script"]
    finalized_utc = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    receipt["files"]["script"] = file_record(script_path)
    receipt["receipt_finalization"] = {
        "finalized_utc": finalized_utc,
        "previous_receipt_sha256": previous_sha,
        "previous_generator_script": previous_script_record,
        "reason": (
            "Bind the finalized generator/checker script after adding its "
            "non-mutating --check mode."
        ),
    }
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "status": "FINALIZED",
        "mode": "finalize-receipt",
        "verification_before_write": verification["status"],
        "previous_receipt_sha256": previous_sha,
        "script": file_record(script_path),
        "receipt": file_record(receipt_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolver", required=True, type=Path)
    parser.add_argument("--replay", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="Reverify the existing closure without changing it.",
    )
    mode.add_argument(
        "--finalize-receipt",
        action="store_true",
        help="Verify once, then bind the finalized checker script in the receipt.",
    )
    arguments = parser.parse_args()

    resolver_python = arguments.resolver.resolve()
    replay_root = arguments.replay.resolve()
    output_root = arguments.output.resolve()
    script_path = Path(__file__).resolve()
    requirements_in = output_root / "requirements.in"
    requirements_resolved = output_root / "requirements.resolved.txt"
    requirements_lock = output_root / "requirements.lock"
    wheelhouse = output_root / "wheelhouse"
    wheelhouse_manifest = output_root / "WHEELHOUSE_MANIFEST.tsv"
    receipt_path = output_root / "ENVIRONMENT_RECEIPT.json"

    if not resolver_python.is_file():
        raise RuntimeError(f"Resolver interpreter not found: {resolver_python}")
    if arguments.check:
        print(
            json.dumps(
                check_existing_environment(
                    resolver_python=resolver_python,
                    replay_root=replay_root,
                    output_root=output_root,
                    script_path=script_path,
                    require_current_script_record=True,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if arguments.finalize_receipt:
        print(
            json.dumps(
                finalize_receipt(
                    resolver_python=resolver_python,
                    replay_root=replay_root,
                    output_root=output_root,
                    script_path=script_path,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if not requirements_in.is_file():
        raise RuntimeError(f"Top-level requirement authority not found: {requirements_in}")
    if replay_root.exists():
        raise RuntimeError(
            f"Refusing to replace an existing replay environment: {replay_root}"
        )
    output_root.mkdir(parents=True, exist_ok=True)
    reuse_wheelhouse = wheelhouse.exists() and any(wheelhouse.iterdir())
    wheelhouse.mkdir(parents=True, exist_ok=True)

    base_environment = deterministic_subprocess_environment()
    pip_version = normalized_output(
        run(
            [str(resolver_python), "-m", "pip", "--version"],
            environment=base_environment,
        ).stdout
    ).strip()
    resolver_check = normalized_output(
        run(
            [str(resolver_python), "-m", "pip", "check"],
            environment=base_environment,
        ).stdout
    ).strip()
    if resolver_check != "No broken requirements found.":
        raise RuntimeError(f"Resolver pip check was not clean: {resolver_check!r}")

    freeze_text = normalized_output(
        run(
            [str(resolver_python), "-m", "pip", "freeze", "--all"],
            environment=base_environment,
        ).stdout
    )
    resolved_pins = parse_exact_pins(freeze_text, comments_allowed=False)
    top_level_pins = parse_exact_pins(
        requirements_in.read_text(encoding="utf-8"), comments_allowed=True
    )
    resolved_map = {pin["canonical_name"]: pin for pin in resolved_pins}
    for requested in top_level_pins:
        resolved = resolved_map.get(requested["canonical_name"])
        if resolved is None or Version(resolved["version"]) != Version(requested["version"]):
            raise RuntimeError(
                "Resolver does not preserve exact top-level pin "
                f"{requested['line']}; found {resolved!r}"
            )
    requirements_resolved.write_text(freeze_text, encoding="utf-8", newline="\n")

    download_command = [
        str(resolver_python),
        "-m",
        "pip",
        "download",
        "--disable-pip-version-check",
        "--only-binary=:all:",
        "--no-deps",
        "--progress-bar",
        "off",
        "--dest",
        str(wheelhouse),
        "--requirement",
        str(requirements_resolved),
    ]
    if not reuse_wheelhouse:
        run(download_command, environment=base_environment)

    unexpected = [path.name for path in wheelhouse.iterdir() if path.suffix != ".whl"]
    if unexpected:
        raise RuntimeError(f"Non-wheel files appeared in wheelhouse: {unexpected}")
    wheel_files = sorted(wheelhouse.glob("*.whl"), key=lambda path: path.name.casefold())
    runtime_tags = set(sys_tags())
    wheel_by_distribution: dict[str, dict[str, object]] = {}
    for wheel in wheel_files:
        distribution, version, _build, tags = parse_wheel_filename(wheel.name)
        canonical = canonicalize_name(distribution)
        if canonical in wheel_by_distribution:
            raise RuntimeError(f"Multiple wheels downloaded for {canonical}")
        compatible_tags = sorted(str(tag) for tag in tags.intersection(runtime_tags))
        if not compatible_tags:
            raise RuntimeError(f"Downloaded wheel is incompatible with resolver: {wheel.name}")
        expected = resolved_map.get(canonical)
        if expected is None:
            raise RuntimeError(f"Extraneous wheel has no resolved distribution: {wheel.name}")
        if version != Version(expected["version"]):
            raise RuntimeError(
                f"Version mismatch for {wheel.name}: expected {expected['version']}"
            )
        wheel_by_distribution[canonical] = {
            "distribution": expected["name"],
            "canonical_name": canonical,
            "version": expected["version"],
            "wheel_filename": wheel.name,
            "bytes": wheel.stat().st_size,
            "sha256": sha256_file(wheel),
            "wheel_tags": ",".join(sorted(str(tag) for tag in tags)),
            "compatible_tags": ",".join(compatible_tags),
        }

    missing_wheels = sorted(set(resolved_map) - set(wheel_by_distribution))
    if missing_wheels:
        raise RuntimeError(f"No wheel was downloaded for: {missing_wheels}")
    if len(wheel_files) != len(resolved_pins):
        raise RuntimeError(
            f"Wheel/distribution cardinality mismatch: {len(wheel_files)} != "
            f"{len(resolved_pins)}"
        )

    with wheelhouse_manifest.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "distribution",
            "canonical_name",
            "version",
            "wheel_filename",
            "bytes",
            "sha256",
            "wheel_tags",
            "compatible_tags",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for pin in resolved_pins:
            writer.writerow(wheel_by_distribution[pin["canonical_name"]])

    lock_lines = [
        "# Exact wheel-only offline lock generated from requirements.resolved.txt.",
        "# Install with --no-index --find-links=wheelhouse --require-hashes.",
    ]
    for pin in resolved_pins:
        wheel = wheel_by_distribution[pin["canonical_name"]]
        lock_lines.append(f"{pin['line']} --hash=sha256:{wheel['sha256']}")
    requirements_lock.write_text("\n".join(lock_lines) + "\n", encoding="utf-8", newline="\n")

    # Anaconda's ensurepip bootstrap is not reliable when invoked from a venv
    # nested below another venv.  Create a genuinely empty target and use the
    # resolver pip's supported --python targeting mode to seed *every* package,
    # including pip itself, solely from the hash-locked wheelhouse.
    run(
        [str(resolver_python), "-m", "venv", "--without-pip", str(replay_root)],
        environment=base_environment,
    )
    replay_python = replay_root / "Scripts" / "python.exe"
    if not replay_python.is_file():
        raise RuntimeError(f"Replay interpreter was not created: {replay_python}")
    offline_environment = deterministic_subprocess_environment(offline=True)
    install_command = [
        str(resolver_python),
        "-m",
        "pip",
        "--python",
        str(replay_python),
        "install",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "--no-index",
        "--find-links",
        str(wheelhouse),
        "--only-binary=:all:",
        "--require-hashes",
        "--force-reinstall",
        "--requirement",
        str(requirements_lock),
    ]
    run(install_command, environment=offline_environment)

    replay_check = normalized_output(
        run(
            [str(replay_python), "-m", "pip", "check"],
            environment=offline_environment,
        ).stdout
    ).strip()
    if replay_check != "No broken requirements found.":
        raise RuntimeError(f"Replay pip check was not clean: {replay_check!r}")
    replay_freeze = normalized_output(
        run(
            [str(replay_python), "-m", "pip", "freeze", "--all"],
            environment=offline_environment,
        ).stdout
    )
    if replay_freeze != freeze_text:
        raise RuntimeError(
            "Offline replay freeze differs from resolver freeze.\n"
            f"resolver sha256={hashlib.sha256(freeze_text.encode()).hexdigest()}\n"
            f"replay sha256={hashlib.sha256(replay_freeze.encode()).hexdigest()}"
        )

    probe = scientific_and_toolchain_probe(replay_python)
    replay_bin = replay_root / "Scripts"
    jupyter_book_version = normalized_output(
        run(
            [str(replay_bin / "jupyter-book.exe"), "--version"],
            environment=offline_environment,
        ).stdout
    ).strip()
    sphinx_version = normalized_output(
        run(
            [str(replay_bin / "sphinx-build.exe"), "--version"],
            environment=offline_environment,
        ).stdout
    ).strip()

    wheelhouse_bytes = sum(path.stat().st_size for path in wheel_files)
    receipt = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "purpose": (
            "Exact wheel-only Python closure and clean offline replay for the "
            "O009 QuantEcon CTMC authority/build baseline."
        ),
        "policy": {
            "resolver_was_preinstalled": True,
            "download_only_binary": True,
            "one_wheel_per_distribution": True,
            "offline_install_no_index": True,
            "offline_install_require_hashes": True,
            "offline_install_force_reinstall": True,
            "resolver_and_replay_freeze_exact_match": True,
        },
        "deterministic_environment": DETERMINISTIC_ENVIRONMENT,
        "interpreter": interpreter_receipt(resolver_python),
        "resolver": {
            "path": str(resolver_python),
            "pip_version": pip_version,
            "pip_check": resolver_check,
            "distribution_count": len(resolved_pins),
            "freeze_sha256": hashlib.sha256(freeze_text.encode("utf-8")).hexdigest(),
        },
        "top_level_requirement_count": len(top_level_pins),
        "wheelhouse": {
            "path": str(wheelhouse),
            "wheel_count": len(wheel_files),
            "total_bytes": wheelhouse_bytes,
            "manifest_sha256": sha256_file(wheelhouse_manifest),
        },
        "offline_replay": {
            "path": str(replay_root),
            "python": file_record(replay_python),
            "pip_check": replay_check,
            "freeze_exact_match": True,
            "freeze_sha256": hashlib.sha256(replay_freeze.encode("utf-8")).hexdigest(),
            "jupyter_book_version": jupyter_book_version,
            "sphinx_build_version": sphinx_version,
            "probe": probe,
            "tree": tree_record(replay_root),
        },
        "files": {
            "script": file_record(script_path),
            "requirements_in": file_record(requirements_in),
            "requirements_resolved": file_record(requirements_resolved),
            "requirements_lock": file_record(requirements_lock),
            "wheelhouse_manifest": file_record(wheelhouse_manifest),
        },
    }
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "status": "pass",
                "distribution_count": len(resolved_pins),
                "wheel_count": len(wheel_files),
                "wheelhouse_bytes": wheelhouse_bytes,
                "freeze_sha256": receipt["resolver"]["freeze_sha256"],
                "wheelhouse_manifest_sha256": receipt["wheelhouse"]["manifest_sha256"],
                "replay_file_count": receipt["offline_replay"]["tree"]["file_count"],
                "replay_total_bytes": receipt["offline_replay"]["tree"]["total_bytes"],
                "replay_tree_sha256": receipt["offline_replay"]["tree"]["tree_sha256"],
                "receipt": file_record(receipt_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
