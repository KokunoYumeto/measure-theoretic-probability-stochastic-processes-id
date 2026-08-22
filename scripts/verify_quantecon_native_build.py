#!/usr/bin/env python3
"""Freeze and verify the bounded QuantEcon native-build baseline.

This script never executes the upstream source.  It inventories already-created
disposable build trees, records the documented wrapper failure and manual PDF
follow-up, scans the native reader for release hazards, and writes deterministic
evidence under ``authority/quantecon/build_baseline``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


SCHEMA = "o009.quantecon-native-build-baseline.v1"
AUTHORITY_MANIFEST_SHA256 = (
    "6caf088583fba12eab445490f8ef3cfbece2c23b0e47a715a5da7f2ed412beb6"
)
AUTHORITY_CHECK_SUMMARY = (
    "source=34/384053 source_manifest="
    "6b9c5ae0a04281259360124f0d432dea19ff03d10cb00ced0ae3499ded58d27c "
    "notebooks=13/501361 notebook_manifest="
    "d0934f364b8655d114dc9f5e8469214909b8b7af20a9d69febf5bee1d12603ca "
    "active=17/260561 active_manifest=" + AUTHORITY_MANIFEST_SHA256
)
DETERMINISTIC_ENVIRONMENT = {
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "MKL_NUM_THREADS": "1",
    "MPLBACKEND": "Agg",
    "NUMBA_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
    "SOURCE_DATE_EPOCH": "315532800",
    "TZ": "UTC",
}
EXTRA_OFFLINE_ENVIRONMENT = {
    "PIP_DISABLE_PIP_VERSION_CHECK": "1",
    "PIP_NO_INDEX": "1",
    "PYTHONNOUSERSITE": "1",
}
HTML_WORK = "tmp/quantecon-build-work-native-offline-20260822a"
PDF_WORK = "tmp/quantecon-build-work-native-pdf-20260822a"
BUILD_A_WORK = "tmp/quantecon-upstream-build-a"
HTML_OUTPUT = f"{HTML_WORK}/_build/html"
PDF_LATEX_OUTPUT = f"{PDF_WORK}/_build/latex"
BUILD_A_HTML_OUTPUT = f"{BUILD_A_WORK}/_build/html"
BASELINE = "authority/quantecon/build_baseline"
OUTPUT_NAMES = (
    "NATIVE_HTML_MANIFEST.tsv",
    "NATIVE_PDF_LATEX_MANIFEST.tsv",
    "HAZARD_BUILD_A_HTML_MANIFEST.tsv",
    "HTML_A_B_COMPARISON.tsv",
    "WORKING_COPY_MUTATIONS.tsv",
    "NATIVE_BUILD_HAZARDS.json",
    "NATIVE_BUILD_BASELINE.json",
)
LOG_NAMES = (
    "native_html_build.log",
    "native_pdf_build.log",
    "native_pdf_manual_make.log",
)


class VerificationError(RuntimeError):
    """Raised when the baseline no longer matches its receipt."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_fact(path: Path) -> dict[str, object]:
    require(path.is_file(), f"missing file: {path}")
    require(not path.is_symlink(), f"symlink is forbidden: {path}")
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha256(data)}


def tree_rows(root: Path) -> list[tuple[str, int, str]]:
    require(root.is_dir(), f"missing build tree: {root}")
    require(not root.is_symlink(), f"build root is a symlink: {root}")
    paths: list[Path] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in dirs:
            require(
                not (current_path / name).is_symlink(),
                f"directory symlink in build tree: {current_path / name}",
            )
        for name in files:
            path = current_path / name
            require(not path.is_symlink(), f"file symlink in build tree: {path}")
            paths.append(path)
    paths.sort(key=lambda path: path.relative_to(root).as_posix().casefold())
    rows: list[tuple[str, int, str]] = []
    for path in paths:
        data = path.read_bytes()
        rows.append((path.relative_to(root).as_posix(), len(data), sha256(data)))
    return rows


def manifest_bytes(rows: list[tuple[str, int, str]]) -> bytes:
    return "".join(
        f"{relative}\t{size}\t{digest}\n" for relative, size, digest in rows
    ).encode("utf-8")


def tree_fact(rows: list[tuple[str, int, str]], manifest: bytes) -> dict[str, object]:
    return {
        "file_count": len(rows),
        "total_bytes": sum(size for _, size, _ in rows),
        "manifest_bytes": len(manifest),
        "manifest_sha256": sha256(manifest),
    }


def read_active_manifest(path: Path) -> dict[str, tuple[int, str]]:
    data = path.read_bytes()
    require(sha256(data) == AUTHORITY_MANIFEST_SHA256, "active-input manifest differs")
    rows: dict[str, tuple[int, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t")
        for row in reader:
            require(len(row) == 3, "malformed active-input manifest row")
            relative, size, digest = row
            require(relative not in rows, f"duplicate active input: {relative}")
            rows[relative] = (int(size), digest)
    require(len(rows) == 17, "active-input count differs")
    return rows


def working_copy_mutations(
    repo: Path,
    active: dict[str, tuple[int, str]],
) -> tuple[bytes, list[dict[str, object]]]:
    records: list[dict[str, object]] = []
    lines = [
        "working_copy\tpath\tstatus\texpected_bytes\texpected_sha256"
        "\tactual_bytes\tactual_sha256\n"
    ]
    for work_name in (HTML_WORK, PDF_WORK):
        work = repo / PurePosixPath(work_name)
        require(work.is_dir(), f"missing disposable working copy: {work}")
        changed = 0
        missing = 0
        for relative, (expected_size, expected_digest) in active.items():
            path = work / PurePosixPath(relative)
            if not path.is_file():
                status = "missing"
                actual_size: int | str = ""
                actual_digest = ""
                missing += 1
            else:
                data = path.read_bytes()
                actual_size = len(data)
                actual_digest = sha256(data)
                status = (
                    "unchanged"
                    if (actual_size, actual_digest) == (expected_size, expected_digest)
                    else "modified-by-native-execution"
                )
                if status != "unchanged":
                    changed += 1
            lines.append(
                f"{work_name}\t{relative}\t{status}\t{expected_size}\t"
                f"{expected_digest}\t{actual_size}\t{actual_digest}\n"
            )
        records.append(
            {
                "working_copy": work_name,
                "active_inputs": len(active),
                "modified_by_execution": changed,
                "missing": missing,
                "authority_snapshot_was_execution_target": False,
            }
        )
    return "".join(lines).encode("utf-8"), records


def comparison_bytes(
    a_rows: list[tuple[str, int, str]],
    b_rows: list[tuple[str, int, str]],
) -> tuple[bytes, dict[str, object]]:
    a = {path: (size, digest) for path, size, digest in a_rows}
    b = {path: (size, digest) for path, size, digest in b_rows}
    lines = [
        "path\tstatus\ta_bytes\ta_sha256\tb_bytes\tb_sha256\n"
    ]
    counts: Counter[str] = Counter()
    for relative in sorted(set(a) | set(b), key=str.casefold):
        if relative not in a:
            status = "only-in-offline-build-b"
            a_size: int | str = ""
            a_digest = ""
            b_size, b_digest = b[relative]
        elif relative not in b:
            status = "only-in-hazard-build-a"
            a_size, a_digest = a[relative]
            b_size = ""
            b_digest = ""
        else:
            a_size, a_digest = a[relative]
            b_size, b_digest = b[relative]
            status = "identical" if (a_size, a_digest) == (b_size, b_digest) else "different"
        counts[status] += 1
        lines.append(
            f"{relative}\t{status}\t{a_size}\t{a_digest}\t{b_size}\t{b_digest}\n"
        )
    return "".join(lines).encode("utf-8"), {
        "path_union": sum(counts.values()),
        "identical": counts["identical"],
        "different": counts["different"],
        "only_in_hazard_build_a": counts["only-in-hazard-build-a"],
        "only_in_offline_build_b": counts["only-in-offline-build-b"],
        "byte_identical": counts["different"] == 0
        and counts["only-in-hazard-build-a"] == 0
        and counts["only-in-offline-build-b"] == 0,
    }


def scan_html(root: Path) -> dict[str, object]:
    html_files = sorted(root.rglob("*.html"), key=lambda path: path.as_posix().casefold())
    require(html_files, f"no HTML files in native output: {root}")
    external_urls: list[str] = []
    remote_resources: list[str] = []
    images_total = 0
    images_missing_alt = 0
    images_empty_alt = 0
    pages_with_missing_or_empty_alt: set[str] = set()
    pattern_hits: Counter[str] = Counter()
    pages_by_pattern: dict[str, set[str]] = {
        "analytics": set(),
        "remote_mathjax": set(),
        "remote_colab": set(),
        "quantecon_branding": set(),
        "local_windows_path": set(),
        "pip_install_quantecon": set(),
        "runtime_warning": set(),
        "unresolved_question_marks": set(),
    }
    patterns = {
        "analytics": re.compile(r"googletagmanager|google-analytics|G-MVZ2FSB14W", re.I),
        "remote_mathjax": re.compile(r"cdn\.jsdelivr\.net/npm/mathjax", re.I),
        "remote_colab": re.compile(r"colab\.research\.google\.com", re.I),
        "quantecon_branding": re.compile(r"quantecon|qe-logo-large", re.I),
        "local_windows_path": re.compile(r"C:(?:\\|\\\\|&#92;|/)(?:Users|Program)", re.I),
        "pip_install_quantecon": re.compile(r"pip(?:\s|&nbsp;|&#32;)+install(?:\s|&nbsp;|&#32;)+quantecon", re.I),
        "runtime_warning": re.compile(r"FigureCanvasAgg is non-interactive|UserWarning", re.I),
        "unresolved_question_marks": re.compile(r">\?\?<|,\s*\?\?", re.I),
    }
    url_re = re.compile(r"https?://[^\s\"'<>]+", re.I)
    resource_re = re.compile(r"(?:src|href)=[\"'](https?://[^\"']+)[\"']", re.I)
    image_re = re.compile(r"<img\b[^>]*>", re.I)
    alt_re = re.compile(r"\balt\s*=\s*([\"'])(.*?)\1", re.I | re.S)
    for path in html_files:
        relative = path.relative_to(root).as_posix()
        text = path.read_text("utf-8", errors="replace")
        external_urls.extend(url_re.findall(text))
        remote_resources.extend(resource_re.findall(text))
        for label, pattern in patterns.items():
            hits = pattern.findall(text)
            if hits:
                pattern_hits[label] += len(hits)
                pages_by_pattern[label].add(relative)
        for tag in image_re.findall(text):
            images_total += 1
            alt = alt_re.search(tag)
            if alt is None:
                images_missing_alt += 1
                pages_with_missing_or_empty_alt.add(relative)
            elif not alt.group(2).strip():
                images_empty_alt += 1
                pages_with_missing_or_empty_alt.add(relative)
    domains = Counter(
        urlsplit(url.replace("&amp;", "&")).netloc.casefold()
        for url in external_urls
        if urlsplit(url.replace("&amp;", "&")).netloc
    )
    remote_domains = Counter(
        urlsplit(url.replace("&amp;", "&")).netloc.casefold()
        for url in remote_resources
        if urlsplit(url.replace("&amp;", "&")).netloc
    )
    return {
        "html_file_count": len(html_files),
        "external_url_occurrences": len(external_urls),
        "external_url_domains": dict(sorted(domains.items())),
        "remote_src_or_href_occurrences": len(remote_resources),
        "remote_src_or_href_domains": dict(sorted(remote_domains.items())),
        "pattern_occurrences": dict(sorted(pattern_hits.items())),
        "pages_by_pattern": {
            label: sorted(paths, key=str.casefold)
            for label, paths in pages_by_pattern.items()
        },
        "images": {
            "total": images_total,
            "missing_alt": images_missing_alt,
            "empty_alt": images_empty_alt,
            "pages_with_missing_or_empty_alt": sorted(
                pages_with_missing_or_empty_alt, key=str.casefold
            ),
        },
    }


def run_checked(command: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    require(completed.returncode == 0, f"command failed: {command!r}")
    return completed.stdout


def pdf_facts(pdf: Path) -> dict[str, object]:
    pdfinfo = shutil.which("pdfinfo")
    pdftotext = shutil.which("pdftotext")
    require(pdfinfo is not None, "pdfinfo is required for PDF baseline verification")
    require(pdftotext is not None, "pdftotext is required for PDF baseline verification")
    info_text = run_checked([pdfinfo, str(pdf)])
    info: dict[str, str] = {}
    for line in info_text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
    text = run_checked([pdftotext, "-layout", str(pdf), "-"])
    fact = file_fact(pdf)
    fact.update(
        {
            "physical_pages": int(info["Pages"]),
            "title": info.get("Title"),
            "author": info.get("Author"),
            "tagged": info.get("Tagged"),
            "javascript": info.get("JavaScript"),
            "encrypted": info.get("Encrypted"),
            "creation_date": info.get("CreationDate"),
            "producer": info.get("Producer"),
            "unresolved_double_question_mark_occurrences": text.count("??"),
            "local_windows_path_occurrences": len(
                re.findall(r"C:\\Users\\", text, re.I)
            ),
            "runtime_warning_occurrences": len(
                re.findall(r"FigureCanvasAgg is non-interactive|UserWarning", text, re.I)
            ),
        }
    )
    return fact


def build_expected(repo: Path) -> dict[str, bytes]:
    baseline = repo / PurePosixPath(BASELINE)
    active = read_active_manifest(repo / "authority/quantecon/ACTIVE_INPUT_MANIFEST.tsv")
    environment_receipt_path = repo / "authority/quantecon/environment/ENVIRONMENT_RECEIPT.json"
    environment_receipt = json.loads(environment_receipt_path.read_text("utf-8"))
    require(
        environment_receipt["deterministic_environment"] == DETERMINISTIC_ENVIRONMENT,
        "locked deterministic environment differs",
    )
    require(
        environment_receipt["offline_replay"]["freeze_exact_match"] is True,
        "offline replay is not admitted",
    )

    html_rows = tree_rows(repo / PurePosixPath(HTML_OUTPUT))
    pdf_rows = tree_rows(repo / PurePosixPath(PDF_LATEX_OUTPUT))
    build_a_rows = tree_rows(repo / PurePosixPath(BUILD_A_HTML_OUTPUT))
    html_manifest = manifest_bytes(html_rows)
    pdf_manifest = manifest_bytes(pdf_rows)
    build_a_manifest = manifest_bytes(build_a_rows)
    comparison, comparison_summary = comparison_bytes(build_a_rows, html_rows)
    mutations, mutation_summary = working_copy_mutations(repo, active)

    log_facts = {
        name: {
            "path": f"{BASELINE}/{name}",
            **file_fact(baseline / name),
        }
        for name in LOG_NAMES
    }
    html_log = (baseline / "native_html_build.log").read_text("utf-8", errors="replace")
    pdf_log = (baseline / "native_pdf_build.log").read_text("utf-8", errors="replace")
    manual_log = (baseline / "native_pdf_manual_make.log").read_text(
        "utf-8", errors="replace"
    )
    require("build succeeded." in html_log, "HTML success marker absent")
    require("Failed to run: make.bat" in pdf_log, "PDF wrapper failure marker absent")
    require("Output written on book.pdf (92 pages)." in manual_log,
            "manual PDF success marker absent")
    require("Latex failed to resolve 12 reference(s)" in manual_log,
            "manual PDF unresolved-reference summary differs")

    html_scan = scan_html(repo / PurePosixPath(HTML_OUTPUT))
    native_pdf = repo / PurePosixPath(PDF_LATEX_OUTPUT) / "book.pdf"
    pdf = pdf_facts(native_pdf)
    require(pdf["physical_pages"] == 92, "native PDF page count differs")
    require(pdf["tagged"] == "no", "native PDF tagging status differs")
    require(pdf["unresolved_double_question_mark_occurrences"] > 0,
            "expected unresolved PDF proof-index marker absent")

    hazards = {
        "schema": "o009.quantecon-native-build-hazards.v1",
        "classification": "upstream native baseline only; not a downstream reader",
        "html": html_scan,
        "pdf": {
            **pdf,
            "visual_qa": {
                "rendered_pages": [1, 45, 92],
                "render_dpi": 120,
                "page_1": "legible title page; deterministic epoch appears as Jan 01, 1980",
                "page_45": (
                    "legible code, but rendered notebook output exposes a local Windows "
                    "temporary path and FigureCanvasAgg warning"
                ),
                "page_92": "legible proof index with a visible unresolved ?? locator",
                "clipping_or_overlap_seen": False,
            },
            "official_pdf_comparison": {
                "official_authority_pdf_pages": 100,
                "native_locked_build_pages": 92,
                "page_count_difference": -8,
                "byte_identity_claimed": False,
            },
        },
        "execution_side_effects": {
            "working_copies": mutation_summary,
            "known_mutation": (
                "markov_prop.md executes plt.savefig against "
                "lectures/_static/lecture_specific/markov_prop/flow_fig.png"
            ),
            "policy": (
                "execute only in a manifest-verified disposable copy; run the authority "
                "verifier before and after every build"
            ),
        },
        "release_blockers": [
            "remove Google Analytics and remote runtime/resource dependencies",
            "remove or replace QuantEcon branding while preserving attribution",
            "replace six in-notebook pip-install cells with the locked offline runtime",
            "remove local Windows paths and notebook runtime warnings from rendered output",
            "supply meaningful alternative text for mathematical and decorative images",
            "resolve internal references and proof-index ?? entries",
            "produce tagged/accessible PDF and truthful release-date metadata",
            "normalize and prove deterministic downstream output separately",
        ],
        "wrapper_and_toolchain": {
            "jupyter_book_wrapper": (
                "Sphinx LaTeX generation succeeded, but Jupyter Book 1.0.4.post1 on "
                "Windows invoked bare make.bat with subprocess shell=False and raised "
                "FileNotFoundError [WinError 2]"
            ),
            "manual_follow_up": (
                "cmd.exe /d /c .\\make.bat all-pdf succeeded from the generated LaTeX "
                "directory with LATEXMKOPTS=-latexoption=-disable-installer"
            ),
            "python_environment_locked": True,
            "system_tex_toolchain_outside_python_wheel_lock": True,
            "system_tex_versions": {
                "latexmk": "4.88 (9 March 2026)",
                "miktex": "26.5",
                "xelatex": "3.141592653-2.6-0.999998 (MiKTeX 26.5)",
            },
            "package_installer_disabled": True,
            "network_access_performed": False,
            "local_miktex_font_cache_writes_observed": True,
        },
    }
    hazards_bytes = (
        json.dumps(hazards, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    generated_facts = {
        "NATIVE_HTML_MANIFEST.tsv": tree_fact(html_rows, html_manifest),
        "NATIVE_PDF_LATEX_MANIFEST.tsv": tree_fact(pdf_rows, pdf_manifest),
        "HAZARD_BUILD_A_HTML_MANIFEST.tsv": tree_fact(build_a_rows, build_a_manifest),
        "HTML_A_B_COMPARISON.tsv": {
            "bytes": len(comparison),
            "sha256": sha256(comparison),
            **comparison_summary,
        },
        "WORKING_COPY_MUTATIONS.tsv": {
            "bytes": len(mutations),
            "sha256": sha256(mutations),
            "working_copy_count": len(mutation_summary),
        },
        "NATIVE_BUILD_HAZARDS.json": {
            "bytes": len(hazards_bytes),
            "sha256": sha256(hazards_bytes),
        },
    }
    receipt = {
        "schema": SCHEMA,
        "status": (
            "native HTML proven offline; native PDF wrapper failure isolated and "
            "generated batch proven manually; downstream adaptation still required"
        ),
        "authority": {
            "check_before_and_after_each_build": "pass",
            "check_summary": AUTHORITY_CHECK_SUMMARY,
            "authority_execution_target": False,
            "active_input_manifest_sha256": AUTHORITY_MANIFEST_SHA256,
        },
        "environment": {
            "receipt": {
                "path": "authority/quantecon/environment/ENVIRONMENT_RECEIPT.json",
                **file_fact(environment_receipt_path),
            },
            "offline_replay": "tmp/quantecon-offline-replay",
            "deterministic": DETERMINISTIC_ENVIRONMENT,
            "offline_additions": EXTRA_OFFLINE_ENVIRONMENT,
        },
        "runs": [
            {
                "name": "native-html-offline-b",
                "working_copy": HTML_WORK,
                "command": (
                    "tmp/quantecon-offline-replay/Scripts/jb.exe build -W "
                    "--keep-going lectures --path-output ./"
                ),
                "started_utc": "2026-08-22T06:23:22.9688036Z",
                "ended_utc": "2026-08-22T06:24:36.4089967Z",
                "exit_code": 0,
                "log": log_facts["native_html_build.log"],
                "output": {"path": HTML_OUTPUT, **tree_fact(html_rows, html_manifest)},
            },
            {
                "name": "native-pdf-wrapper",
                "working_copy": PDF_WORK,
                "command": (
                    "tmp/quantecon-offline-replay/Scripts/jb.exe build lectures "
                    "--builder pdflatex --path-output ./ -n --keep-going"
                ),
                "started_utc": "2026-08-22T06:25:24.8224741Z",
                "ended_utc": "2026-08-22T06:28:29.2685889Z",
                "exit_code": 1,
                "sphinx_latex_generation": "success-with-one-warning",
                "wrapper_failure": "FileNotFoundError [WinError 2]: make.bat",
                "log": log_facts["native_pdf_build.log"],
            },
            {
                "name": "native-pdf-generated-batch-manual",
                "working_copy": f"{PDF_LATEX_OUTPUT}",
                "command": (
                    "LATEXMKOPTS=-latexoption=-disable-installer; "
                    "cmd.exe /d /c .\\make.bat all-pdf"
                ),
                "started_utc": "2026-08-22T06:30:12.2010425Z",
                "ended_utc": "2026-08-22T06:31:17.4405420Z",
                "exit_code": 0,
                "log": log_facts["native_pdf_manual_make.log"],
                "output": {"path": PDF_LATEX_OUTPUT, **tree_fact(pdf_rows, pdf_manifest)},
                "pdf": pdf,
            },
        ],
        "hazard_build_a_comparison": comparison_summary,
        "generated_files": generated_facts,
        "hazards": {
            "path": f"{BASELINE}/NATIVE_BUILD_HAZARDS.json",
            "bytes": len(hazards_bytes),
            "sha256": sha256(hazards_bytes),
        },
        "claims_not_made": [
            "upstream HTML is a downstream/public reader",
            "upstream HTML or PDF is byte-deterministic across clean builds",
            "native PDF is accessibility-ready",
            "system MiKTeX is included in the Python wheel lock",
            "native PDF matches the 100-page official authority PDF",
        ],
    }
    receipt_bytes = (
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return {
        "NATIVE_HTML_MANIFEST.tsv": html_manifest,
        "NATIVE_PDF_LATEX_MANIFEST.tsv": pdf_manifest,
        "HAZARD_BUILD_A_HTML_MANIFEST.tsv": build_a_manifest,
        "HTML_A_B_COMPARISON.tsv": comparison,
        "WORKING_COPY_MUTATIONS.tsv": mutations,
        "NATIVE_BUILD_HAZARDS.json": hazards_bytes,
        "NATIVE_BUILD_BASELINE.json": receipt_bytes,
    }


def write_outputs(root: Path, expected: dict[str, bytes]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    require(not root.is_symlink(), f"baseline output root is a symlink: {root}")
    for name in OUTPUT_NAMES:
        path = root / name
        require(not path.is_symlink(), f"refusing to replace symlink: {path}")
        path.write_bytes(expected[name])


def check_outputs(root: Path, expected: dict[str, bytes]) -> None:
    for name in OUTPUT_NAMES:
        path = root / name
        require(path.is_file(), f"missing generated baseline file: {path}")
        require(not path.is_symlink(), f"generated baseline file is a symlink: {path}")
        require(path.read_bytes() == expected[name], f"baseline file differs: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the verified baseline")
    mode.add_argument("--check", action="store_true", help="check the baseline byte-for-byte")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    baseline = repo / PurePosixPath(BASELINE)
    try:
        expected = build_expected(repo)
        if args.write:
            write_outputs(baseline, expected)
        check_outputs(baseline, expected)
        receipt = expected["NATIVE_BUILD_BASELINE.json"]
        parsed = json.loads(receipt)
        html = parsed["runs"][0]["output"]
        pdf = parsed["runs"][2]["pdf"]
        comparison = parsed["hazard_build_a_comparison"]
        print(
            f"PASS mode={'write' if args.write else 'check'} "
            f"html={html['file_count']}/{html['total_bytes']} "
            f"html_manifest={html['manifest_sha256']} "
            f"pdf={pdf['physical_pages']}/{pdf['bytes']} "
            f"pdf_sha256={pdf['sha256']} "
            f"a_b_identical={comparison['byte_identical']} "
            f"receipt_sha256={sha256(receipt)}"
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError, VerificationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
