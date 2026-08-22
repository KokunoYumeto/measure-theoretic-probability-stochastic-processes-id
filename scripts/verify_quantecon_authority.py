#!/usr/bin/env python3
"""Verify the bounded QuantEcon CTMC authority closure without network access.

The verifier is intentionally self-contained and deterministic.  It validates
the already-frozen evidence archives, extracted snapshots, authoring topology,
exercise/solution and executable-cell surfaces, rights witness, asset
disposition, and known runtime/network hazards.  It does not install or execute
the upstream Python environment.

The manifest order is explicit rather than locale-dependent.  It reproduces
the coordinator's Windows-culture sorted ``path<TAB>bytes<TAB>sha256`` evidence
exactly while remaining stable on every host.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


SCHEMA = "o009.quantecon-authority-receipt.v1"
TITLE = "Continuous Time Markov Chains"
AUTHORS = ("Thomas J. Sargent", "John Stachurski")
REPOSITORY = "https://github.com/QuantEcon/continuous_time_mcs"
OFFICIAL_READER = "https://continuous-time-mcs.quantecon.org/"
TAG = "publish-2026jul14"
COMMIT = "8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
TREE = "f0f11e3bbc6bd23d6e4a447a7e05c0aaf0f7209e"
NOTEBOOK_REPOSITORY = "https://github.com/QuantEcon/continuous_time_mcs.notebooks"
NOTEBOOK_COMMIT = "1e17c25c937f369544380f769eb9c1bc45d12d1a"

COMMIT_ARCHIVE = "continuous_time_mcs-8b06e0a.zip"
COMMIT_ARCHIVE_ROOT = f"continuous_time_mcs-{COMMIT}"
COMMIT_ARCHIVE_BYTES = 240_751
COMMIT_ARCHIVE_SHA256 = (
    "ae12b4e7724b92c16d1caa3d42c82180fd67723212fe641b22594a1bbd5a4346"
)

TAG_ARCHIVE = "continuous_time_mcs-publish-2026jul14.zip"
TAG_ARCHIVE_ROOT = f"continuous_time_mcs-{TAG}"
TAG_ARCHIVE_BYTES = 238_727
TAG_ARCHIVE_SHA256 = (
    "0b2f27dd6f502369289074917574a54d556c552c7ec66b0788121d16a55ba81d"
)

NOTEBOOK_ARCHIVE = "continuous_time_mcs.notebooks-1e17c25c.zip"
NOTEBOOK_ARCHIVE_ROOT = f"continuous_time_mcs.notebooks-{NOTEBOOK_COMMIT}"
NOTEBOOK_ARCHIVE_BYTES = 266_009
NOTEBOOK_ARCHIVE_SHA256 = (
    "02f1e55deeb9a3e4544e3af13ffbde8789d7a7488f28d8d3834855ddc7f16bd7"
)

PDF = "quantecon-ctmc-book.pdf"
PDF_BYTES = 859_224
PDF_SHA256 = "b08f4503f1ff866a40b0ef0bbedf1c599bccef3c9d6da363013bb524e93054c5"
PDF_PAGES = 100

LICENSE_WITNESS = "quantecon-ctmc-intro-license-witness.html"
LICENSE_WITNESS_BYTES = 32_586
LICENSE_WITNESS_SHA256 = (
    "ff0dd3b21c95d225b2555710bdb6217d2963954cb95e34655711529d93209e46"
)
LICENSE_NAME = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
LICENSE_STATEMENT = (
    "Creative Commons Attribution-ShareAlike 4.0 International."
)

# This exact order reproduces the root coordinator's culture-sorted manifest.
SOURCE_PATHS = (
    "_notebook_repo/environment.yml",
    "_notebook_repo/README.md",
    ".github/dependabot.yml",
    ".github/workflows/cache.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/linkcheck.yml",
    ".github/workflows/publish.yml",
    ".gitignore",
    "diagrams/cmc_inventory.tikz",
    "diagrams/markov.tikzstyles",
    "environment.yml",
    "lectures/_config.yml",
    "lectures/_static/lecture_specific/markov_prop/flow_fig.png",
    "lectures/_static/qe-logo-large.png",
    "lectures/_toc.yml",
    "lectures/ergodicity.md",
    "lectures/generators.md",
    "lectures/intro.md",
    "lectures/kolmogorov_bwd.md",
    "lectures/kolmogorov_fwd.md",
    "lectures/logo.png",
    "lectures/markov_prop.md",
    "lectures/memoryless.md",
    "lectures/old_stuff.txt",
    "lectures/poisson.md",
    "lectures/references.bib",
    "lectures/status.md",
    "lectures/uc_mc_semigroups.md",
    "lectures/zreferences.md",
    "old_notebooks/ctmc.ipynb",
    "old_notebooks/ctmc1.ipynb",
    "old_notebooks/ctmc2.ipynb",
    "old_notebooks/poisson.ipynb",
    "README.md",
)
SOURCE_FILE_COUNT = 34
SOURCE_EXPANDED_BYTES = 384_053
SOURCE_MANIFEST_SHA256 = (
    "6b9c5ae0a04281259360124f0d432dea19ff03d10cb00ced0ae3499ded58d27c"
)

NOTEBOOK_PATHS = (
    "environment.yml",
    "ergodicity.ipynb",
    "generators.ipynb",
    "intro.ipynb",
    "kolmogorov_bwd.ipynb",
    "kolmogorov_fwd.ipynb",
    "markov_prop.ipynb",
    "memoryless.ipynb",
    "poisson.ipynb",
    "README.md",
    "status.ipynb",
    "uc_mc_semigroups.ipynb",
    "zreferences.ipynb",
)
NOTEBOOK_FILE_COUNT = 13
NOTEBOOK_EXPANDED_BYTES = 501_361
NOTEBOOK_MANIFEST_SHA256 = (
    "d0934f364b8655d114dc9f5e8469214909b8b7af20a9d69febf5bee1d12603ca"
)

# Dependency-closed inputs to the official eight-chapter Jupyter Book.  The
# upstream logo remains an authority/build witness but is not reused downstream.
ACTIVE_INPUT_PATHS = (
    "environment.yml",
    "lectures/_config.yml",
    "lectures/_static/lecture_specific/markov_prop/flow_fig.png",
    "lectures/_static/qe-logo-large.png",
    "lectures/_toc.yml",
    "lectures/ergodicity.md",
    "lectures/generators.md",
    "lectures/intro.md",
    "lectures/kolmogorov_bwd.md",
    "lectures/kolmogorov_fwd.md",
    "lectures/markov_prop.md",
    "lectures/memoryless.md",
    "lectures/poisson.md",
    "lectures/references.bib",
    "lectures/status.md",
    "lectures/uc_mc_semigroups.md",
    "lectures/zreferences.md",
)
ACTIVE_INPUT_FILE_COUNT = 17
ACTIVE_INPUT_BYTES = 260_561
ACTIVE_INPUT_MANIFEST_SHA256 = (
    "6caf088583fba12eab445490f8ef3cfbece2c23b0e47a715a5da7f2ed412beb6"
)

EXCLUDED_SOURCE_PATHS = (
    "_notebook_repo/environment.yml",
    "_notebook_repo/README.md",
    ".github/dependabot.yml",
    ".github/workflows/cache.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/linkcheck.yml",
    ".github/workflows/publish.yml",
    ".gitignore",
    "diagrams/cmc_inventory.tikz",
    "diagrams/markov.tikzstyles",
    "lectures/logo.png",
    "lectures/old_stuff.txt",
    "old_notebooks/ctmc.ipynb",
    "old_notebooks/ctmc1.ipynb",
    "old_notebooks/ctmc2.ipynb",
    "old_notebooks/poisson.ipynb",
    "README.md",
)

CHAPTERS = (
    "memoryless",
    "poisson",
    "markov_prop",
    "kolmogorov_bwd",
    "kolmogorov_fwd",
    "generators",
    "uc_mc_semigroups",
    "ergodicity",
)
TOC_FILES = CHAPTERS + ("status", "zreferences")
EXERCISE_COUNTS = {
    "memoryless": 2,
    "poisson": 2,
    "markov_prop": 4,
    "kolmogorov_bwd": 3,
    "kolmogorov_fwd": 3,
    "generators": 3,
    "uc_mc_semigroups": 5,
    "ergodicity": 3,
}
MATH_CODE_CELL_COUNTS = {
    "memoryless": 5,
    "poisson": 7,
    "markov_prop": 5,
    "kolmogorov_bwd": 6,
    "kolmogorov_fwd": 6,
    "generators": 0,
    "uc_mc_semigroups": 0,
    "ergodicity": 4,
}
NOTEBOOK_CODE_CELL_COUNTS = {
    "ergodicity.ipynb": 4,
    "generators.ipynb": 0,
    "intro.ipynb": 0,
    "kolmogorov_bwd.ipynb": 7,
    "kolmogorov_fwd.ipynb": 6,
    "markov_prop.ipynb": 5,
    "memoryless.ipynb": 5,
    "poisson.ipynb": 7,
    "status.ipynb": 2,
    "uc_mc_semigroups.ipynb": 0,
    "zreferences.ipynb": 0,
}

EXPECTED_IMPORTS = (
    "from matplotlib import cm",
    "from mpl_toolkits.mplot3d import Axes3D",
    "from mpl_toolkits.mplot3d.art3d import Poly3DCollection",
    "from myst_nb import glue",
    "from numba import njit",
    "from scipy.linalg import expm",
    "from scipy.special import factorial, binom",
    "from scipy.stats import binom",
    "import matplotlib.pyplot as plt",
    "import numpy as np",
    "import quantecon as qe",
    "import scipy as sp",
)

OUTPUT_NAMES = (
    "SOURCE_MANIFEST.tsv",
    "NOTEBOOK_MANIFEST.tsv",
    "ACTIVE_INPUT_MANIFEST.tsv",
    "AUTHORITY_RECEIPT.json",
)

EXERCISE_RE = re.compile(
    r"^`{3,}\{exercise\}\s*\r?\n:label:\s*(\S+)\s*$", re.MULTILINE
)
SOLUTION_RE = re.compile(
    r"^`{3,}\{solution(?:-start)?\}\s+(\S+)\s*$", re.MULTILINE
)
CODE_CELL_OPEN_RE = re.compile(r"^(`{3,})\{code-cell\}\s+(\S+)\s*$")
NETWORK_CODE_RE = re.compile(
    r"(?:https?://|\brequests\b|\burllib\b|\burlopen\b|\bhttpx\b|"
    r"\baiohttp\b|\bsocket\b|\bwget\b|\bcurl\b)",
    re.IGNORECASE,
)


class VerificationError(RuntimeError):
    """Raised when frozen authority evidence no longer matches its contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_file(path: Path, expected_bytes: int, expected_sha256: str) -> bytes:
    require(path.is_file(), f"missing file: {path}")
    require(not path.is_symlink(), f"symlink is forbidden: {path}")
    data = path.read_bytes()
    require(len(data) == expected_bytes, f"byte mismatch: {path}")
    require(sha256(data) == expected_sha256, f"SHA-256 mismatch: {path}")
    return data


def manifest_bytes(rows: Sequence[tuple[str, int, str]]) -> bytes:
    return (
        "".join(f"{path}\t{size}\t{digest}\n" for path, size, digest in rows)
    ).encode("utf-8")


def validate_paths(paths: Sequence[str], label: str) -> None:
    require(len(paths) == len(set(paths)), f"duplicate {label} path")
    require(
        len(paths) == len({path.casefold() for path in paths}),
        f"case-colliding {label} path",
    )
    for path in paths:
        pure = PurePosixPath(path)
        require(not pure.is_absolute(), f"absolute {label} path: {path}")
        require(
            path == pure.as_posix()
            and all(part not in ("", ".", "..") for part in pure.parts),
            f"unsafe {label} path: {path}",
        )


def rows_from_directory(root: Path, canonical_paths: Sequence[str]) -> list[tuple[str, int, str]]:
    require(root.is_dir(), f"missing snapshot directory: {root}")
    require(not root.is_symlink(), f"snapshot root is a symlink: {root}")
    actual: set[str] = set()
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in dirs:
            child = current_path / name
            require(not child.is_symlink(), f"snapshot directory symlink: {child}")
        for name in files:
            child = current_path / name
            require(not child.is_symlink(), f"snapshot file symlink: {child}")
            relative = child.relative_to(root).as_posix()
            actual.add(relative)
    require(actual == set(canonical_paths), f"snapshot path set differs: {root}")
    rows: list[tuple[str, int, str]] = []
    for relative in canonical_paths:
        data = (root / PurePosixPath(relative)).read_bytes()
        rows.append((relative, len(data), sha256(data)))
    return rows


def rows_from_zip(
    path: Path,
    expected_root: str,
    canonical_paths: Sequence[str],
) -> tuple[list[tuple[str, int, str]], dict[str, object]]:
    all_names: set[str] = set()
    casefold_names: set[str] = set()
    file_data: dict[str, bytes] = {}
    roots: set[str] = set()
    with zipfile.ZipFile(path, "r") as archive:
        require(archive.testzip() is None, f"ZIP CRC failure: {path}")
        for info in archive.infolist():
            raw = info.filename
            require(raw and "\x00" not in raw, f"empty/NUL ZIP entry: {path}")
            require("\\" not in raw, f"backslash ZIP entry: {raw}")
            trimmed = raw[:-1] if raw.endswith("/") else raw
            pure = PurePosixPath(trimmed)
            require(not pure.is_absolute(), f"absolute ZIP entry: {raw}")
            require(
                trimmed == pure.as_posix()
                and all(part not in ("", ".", "..") for part in pure.parts)
                and all(":" not in part for part in pure.parts),
                f"unsafe ZIP entry: {raw}",
            )
            require(trimmed not in all_names, f"duplicate ZIP entry: {raw}")
            require(
                trimmed.casefold() not in casefold_names,
                f"case-colliding ZIP entry: {raw}",
            )
            all_names.add(trimmed)
            casefold_names.add(trimmed.casefold())
            roots.add(pure.parts[0])
            require(not (info.flag_bits & 0x1), f"encrypted ZIP entry: {raw}")
            mode = (info.external_attr >> 16) & 0xFFFF
            require(not stat.S_ISLNK(mode), f"symlink ZIP entry: {raw}")
            if info.is_dir():
                require(
                    mode == 0 or stat.S_ISDIR(mode),
                    f"non-directory mode on ZIP directory: {raw}",
                )
                continue
            require(
                mode == 0 or stat.S_ISREG(mode),
                f"special ZIP entry is forbidden: {raw}",
            )
            require(len(pure.parts) >= 2, f"file outside archive root: {raw}")
            relative = PurePosixPath(*pure.parts[1:]).as_posix()
            require(relative not in file_data, f"duplicate root-stripped path: {relative}")
            file_data[relative] = archive.read(info)
    require(roots == {expected_root}, f"unexpected ZIP root: {path}: {sorted(roots)}")
    require(set(file_data) == set(canonical_paths), f"ZIP file set differs: {path}")
    rows = [
        (relative, len(file_data[relative]), sha256(file_data[relative]))
        for relative in canonical_paths
    ]
    return rows, {
        "archive": f"evidence/{path.name}",
        "entry_count_including_directories": len(all_names),
        "file_count": len(rows),
        "single_root": expected_root,
        "unsafe_entries": 0,
        "symlink_entries": 0,
        "encrypted_entries": 0,
        "crc_check": "pass",
    }


def validate_manifest(
    rows: Sequence[tuple[str, int, str]],
    expected_count: int,
    expected_total_bytes: int,
    expected_sha256: str,
    label: str,
) -> bytes:
    require(len(rows) == expected_count, f"{label} file-count mismatch")
    require(
        sum(size for _, size, _ in rows) == expected_total_bytes,
        f"{label} expanded-byte mismatch",
    )
    data = manifest_bytes(rows)
    require(sha256(data) == expected_sha256, f"{label} manifest SHA-256 mismatch")
    return data


def extract_code_cells(text: str, label: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    cells: list[tuple[str, str]] = []
    index = 0
    while index < len(lines):
        match = CODE_CELL_OPEN_RE.match(lines[index])
        if not match:
            index += 1
            continue
        fence, language = match.groups()
        body: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != fence:
            body.append(lines[index])
            index += 1
        require(index < len(lines), f"unterminated code-cell directive: {label}")
        cells.append((language, "\n".join(body)))
        index += 1
    return cells


def validate_myst_and_teaching(source_root: Path) -> dict[str, object]:
    lectures = source_root / "lectures"
    toc_text = (lectures / "_toc.yml").read_text("utf-8")
    config_text = (lectures / "_config.yml").read_text("utf-8")
    require(re.search(r"^format:\s*jb-book\s*$", toc_text, re.MULTILINE) is not None,
            "TOC is not Jupyter Book format")
    require(re.search(r"^root:\s*intro\s*$", toc_text, re.MULTILINE) is not None,
            "TOC root differs")
    toc_files = tuple(
        re.findall(r"^\s*-\s+file:\s*([^\s#]+)\s*$", toc_text, re.MULTILINE)
    )
    require(toc_files == TOC_FILES, "TOC chapter/support order differs")
    for fragment in (
        "myst_enable_extensions:",
        "sphinx_exercise",
        "execute_notebooks: cache",
        'latex_engine: "xelatex"',
    ):
        require(fragment in config_text, f"missing MyST/Jupyter Book config: {fragment}")

    exercise_ids: list[str] = []
    solution_ids: list[str] = []
    code_cells_by_file: dict[str, int] = {}
    all_code_bodies: list[str] = []
    imports: set[str] = set()
    for chapter in CHAPTERS:
        text = (lectures / f"{chapter}.md").read_text("utf-8")
        chapter_exercises = EXERCISE_RE.findall(text)
        chapter_solutions = SOLUTION_RE.findall(text)
        require(
            len(chapter_exercises) == EXERCISE_COUNTS[chapter],
            f"exercise count differs: {chapter}",
        )
        require(
            len(chapter_solutions) == EXERCISE_COUNTS[chapter],
            f"solution count differs: {chapter}",
        )
        exercise_ids.extend(chapter_exercises)
        solution_ids.extend(chapter_solutions)
        cells = extract_code_cells(text, chapter)
        require(
            len(cells) == MATH_CODE_CELL_COUNTS[chapter],
            f"source code-cell count differs: {chapter}",
        )
        require(
            all(language == "ipython3" for language, _ in cells),
            f"unexpected mathematical code-cell language: {chapter}",
        )
        code_cells_by_file[f"lectures/{chapter}.md"] = len(cells)
        all_code_bodies.extend(body for _, body in cells)

    require(len(exercise_ids) == 25, "total exercise count differs")
    require(len(solution_ids) == 25, "total solution count differs")
    require(len(set(exercise_ids)) == 25, "exercise identifiers are not unique")
    require(len(set(solution_ids)) == 25, "solution identifiers are not unique")
    require(set(exercise_ids) == set(solution_ids), "exercise/solution IDs do not pair")

    status_text = (lectures / "status.md").read_text("utf-8")
    status_cells = extract_code_cells(status_text, "status")
    require(len(status_cells) == 2, "status code-cell count differs")
    require(
        all(language == "ipython" for language, _ in status_cells),
        "unexpected status code-cell language",
    )
    code_cells_by_file["lectures/status.md"] = 2
    all_code_bodies.extend(body for _, body in status_cells)
    require(sum(MATH_CODE_CELL_COUNTS.values()) == 33, "math code-cell invariant failed")
    require(sum(code_cells_by_file.values()) == 35, "source code-cell total differs")

    for body in all_code_bodies:
        require(NETWORK_CODE_RE.search(body) is None, "network I/O token in code cell")
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")):
                imports.add(stripped)
    require(tuple(sorted(imports)) == EXPECTED_IMPORTS, "runtime import surface differs")

    require(
        "logo: _static/qe-logo-large.png" in config_text,
        "upstream logo dependency is no longer explicit",
    )
    require(
        'plt.savefig("_static/lecture_specific/markov_prop/flow_fig.png")'
        in (lectures / "markov_prop.md").read_text("utf-8"),
        "mathematical flow figure generation witness differs",
    )
    return {
        "authoring_format": "MyST Markdown with Jupyter Book configuration",
        "chapter_count": len(CHAPTERS),
        "chapters_in_order": list(CHAPTERS),
        "toc_support_pages": ["intro", "status", "zreferences"],
        "exercise_count": len(exercise_ids),
        "solution_count": len(solution_ids),
        "exercise_solution_pairing": "25 unique IDs; exact set equality",
        "exercise_ids": exercise_ids,
        "source_code_cells": {
            "mathematical_chapters": 33,
            "status_page": 2,
            "total_directives": 35,
            "by_file": code_cells_by_file,
        },
        "runtime_import_statements": list(EXPECTED_IMPORTS),
        "direct_network_io_in_source_code_cells": False,
    }


def validate_notebooks(notebook_root: Path) -> dict[str, object]:
    expected_notebooks = set(NOTEBOOK_CODE_CELL_COUNTS)
    actual_notebooks = {path.name for path in notebook_root.glob("*.ipynb")}
    require(actual_notebooks == expected_notebooks, "generated notebook set differs")
    by_file: dict[str, int] = {}
    total_code = 0
    total_cells = 0
    for name in sorted(expected_notebooks, key=str.casefold):
        notebook = json.loads((notebook_root / name).read_text("utf-8"))
        require(notebook.get("nbformat") == 4, f"unexpected nbformat: {name}")
        cells = notebook.get("cells")
        require(isinstance(cells, list), f"missing notebook cells: {name}")
        code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
        require(
            len(code_cells) == NOTEBOOK_CODE_CELL_COUNTS[name],
            f"generated code-cell count differs: {name}",
        )
        for cell in code_cells:
            require(cell.get("execution_count") is None, f"executed cell: {name}")
            require(cell.get("outputs") == [], f"stored code output: {name}")
        kernelspec = notebook.get("metadata", {}).get("kernelspec", {})
        require(kernelspec.get("name") == "python3", f"kernelspec differs: {name}")
        by_file[name] = len(code_cells)
        total_code += len(code_cells)
        total_cells += len(cells)
    require(total_code == 36, "generated notebook code-cell total differs")
    return {
        "notebook_count": len(expected_notebooks),
        "all_notebook_cells": total_cells,
        "code_cells": total_code,
        "code_cells_by_file": by_file,
        "all_execution_counts_null": True,
        "all_code_outputs_empty": True,
        "one_extra_generated_code_cell": (
            "kolmogorov_bwd.ipynb contains one fenced ipython3 exercise cell in "
            "addition to the 35 MyST code-cell directives"
        ),
    }


def validate_runtime_witnesses(source_root: Path, notebook_root: Path) -> dict[str, object]:
    source_environment = (source_root / "environment.yml").read_text("utf-8")
    notebook_environment = (notebook_root / "environment.yml").read_text("utf-8")
    nested_notebook_environment = (
        source_root / "_notebook_repo" / "environment.yml"
    ).read_text("utf-8")
    config = (source_root / "lectures" / "_config.yml").read_text("utf-8")
    require(notebook_environment == nested_notebook_environment,
            "notebook environment witnesses differ")
    require(source_environment != notebook_environment,
            "source/notebook environment drift unexpectedly disappeared")
    for fragment in ("python=3.13", "anaconda=2026.06", "jupyter-book==1.0.4post1"):
        require(fragment in source_environment, f"source environment differs: {fragment}")
    for fragment in ("python=3.12", "anaconda=2024.10", "jupyter-book==0.15.1"):
        require(fragment in notebook_environment,
                f"notebook environment differs: {fragment}")
    hazards = {
        "analytics": "google_analytics_id: G-MVZ2FSB14W",
        "remote_mathjax": (
            "mathjax_path: https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
        ),
        "remote_colab": "colab_url: https://colab.research.google.com",
        "remote_twitter_logo": (
            "twitter_logo_url: https://assets.quantecon.org/img/qe-twitter-logo.png"
        ),
        "remote_open_graph_logo": (
            "og_logo_url: https://assets.quantecon.org/img/qe-og-logo.png"
        ),
        "remote_notebook_image_base": (
            'tojupyter_image_urlpath: "https://continuous-time-mcs.quantecon.org/_static/"'
        ),
    }
    for label, fragment in hazards.items():
        require(fragment in config, f"network hazard witness differs: {label}")
    return {
        "admission_status": "not runtime-admitted by this verifier",
        "environment_is_constraint_spec_not_hash_locked_solver_closure": True,
        "source_environment": {
            "path": "source_snapshot/%s/environment.yml" % COMMIT_ARCHIVE_ROOT,
            "python": "3.13",
            "anaconda_metapackage": "2026.06",
            "jupyter_book": "1.0.4post1",
        },
        "generated_notebook_environment": {
            "path": "notebook_snapshot/%s/environment.yml" % NOTEBOOK_ARCHIVE_ROOT,
            "python": "3.12",
            "anaconda_metapackage": "2024.10",
            "jupyter_book": "0.15.1",
        },
        "source_and_notebook_environment_specs_differ": True,
        "upstream_network_dependent_configuration": list(hazards),
        "offline_derivative_requirements": [
            "remove Google Analytics",
            "vendor or locally provide MathJax",
            "remove remote Colab and remote branding image dependencies",
            "pin a clean solver-explicit environment with artifact hashes",
            "replace QuantEcon theme/logo branding while preserving attribution",
        ],
        "environment_install_or_execution_performed": False,
    }


def build_expected(root: Path) -> dict[str, bytes]:
    require(root.is_dir(), f"missing QuantEcon authority root: {root}")
    require(not root.is_symlink(), f"authority root is a symlink: {root}")
    validate_paths(SOURCE_PATHS, "source")
    validate_paths(NOTEBOOK_PATHS, "notebook")
    validate_paths(ACTIVE_INPUT_PATHS, "active input")
    validate_paths(EXCLUDED_SOURCE_PATHS, "excluded source")
    require(set(ACTIVE_INPUT_PATHS).isdisjoint(EXCLUDED_SOURCE_PATHS),
            "active/excluded source sets overlap")
    require(
        set(ACTIVE_INPUT_PATHS) | set(EXCLUDED_SOURCE_PATHS) == set(SOURCE_PATHS),
        "active/excluded source sets do not partition authority",
    )

    evidence = root / "evidence"
    commit_archive_path = evidence / COMMIT_ARCHIVE
    tag_archive_path = evidence / TAG_ARCHIVE
    notebook_archive_path = evidence / NOTEBOOK_ARCHIVE
    checked_file(commit_archive_path, COMMIT_ARCHIVE_BYTES, COMMIT_ARCHIVE_SHA256)
    checked_file(tag_archive_path, TAG_ARCHIVE_BYTES, TAG_ARCHIVE_SHA256)
    checked_file(notebook_archive_path, NOTEBOOK_ARCHIVE_BYTES, NOTEBOOK_ARCHIVE_SHA256)
    pdf_data = checked_file(evidence / PDF, PDF_BYTES, PDF_SHA256)
    require(pdf_data.startswith(b"%PDF-"), "PDF signature differs")
    require(b"%%EOF" in pdf_data[-1024:], "PDF EOF marker is missing")
    license_data = checked_file(
        evidence / LICENSE_WITNESS,
        LICENSE_WITNESS_BYTES,
        LICENSE_WITNESS_SHA256,
    )
    license_text = html.unescape(license_data.decode("utf-8", errors="strict"))
    require(LICENSE_URL in license_text, "license URL is absent from witness")
    require(LICENSE_STATEMENT in license_text, "explicit license statement is absent")

    commit_rows, commit_safety = rows_from_zip(
        commit_archive_path, COMMIT_ARCHIVE_ROOT, SOURCE_PATHS
    )
    tag_rows, tag_safety = rows_from_zip(tag_archive_path, TAG_ARCHIVE_ROOT, SOURCE_PATHS)
    require(commit_rows == tag_rows, "tag and commit archive contents differ")
    source_manifest = validate_manifest(
        commit_rows,
        SOURCE_FILE_COUNT,
        SOURCE_EXPANDED_BYTES,
        SOURCE_MANIFEST_SHA256,
        "source",
    )

    source_root = root / "source_snapshot" / COMMIT_ARCHIVE_ROOT
    snapshot_rows = rows_from_directory(source_root, SOURCE_PATHS)
    require(snapshot_rows == commit_rows, "source snapshot differs from commit archive")

    notebook_rows, notebook_safety = rows_from_zip(
        notebook_archive_path, NOTEBOOK_ARCHIVE_ROOT, NOTEBOOK_PATHS
    )
    notebook_manifest = validate_manifest(
        notebook_rows,
        NOTEBOOK_FILE_COUNT,
        NOTEBOOK_EXPANDED_BYTES,
        NOTEBOOK_MANIFEST_SHA256,
        "notebook",
    )
    notebook_root = root / "notebook_snapshot" / NOTEBOOK_ARCHIVE_ROOT
    notebook_snapshot_rows = rows_from_directory(notebook_root, NOTEBOOK_PATHS)
    require(notebook_snapshot_rows == notebook_rows,
            "notebook snapshot differs from archive")

    source_row_map = {path: (size, digest) for path, size, digest in snapshot_rows}
    active_rows = [
        (path, source_row_map[path][0], source_row_map[path][1])
        for path in ACTIVE_INPUT_PATHS
    ]
    active_manifest = validate_manifest(
        active_rows,
        ACTIVE_INPUT_FILE_COUNT,
        ACTIVE_INPUT_BYTES,
        ACTIVE_INPUT_MANIFEST_SHA256,
        "active input",
    )

    teaching = validate_myst_and_teaching(source_root)
    notebooks = validate_notebooks(notebook_root)
    runtime = validate_runtime_witnesses(source_root, notebook_root)
    require(
        not any(PurePosixPath(path).name.casefold().startswith("license")
                and len(PurePosixPath(path).parts) == 1 for path in SOURCE_PATHS),
        "repository unexpectedly has a root license file",
    )

    manifest_facts = {
        "SOURCE_MANIFEST.tsv": {
            "bytes": len(source_manifest),
            "sha256": sha256(source_manifest),
            "files": SOURCE_FILE_COUNT,
            "expanded_bytes": SOURCE_EXPANDED_BYTES,
        },
        "NOTEBOOK_MANIFEST.tsv": {
            "bytes": len(notebook_manifest),
            "sha256": sha256(notebook_manifest),
            "files": NOTEBOOK_FILE_COUNT,
            "expanded_bytes": NOTEBOOK_EXPANDED_BYTES,
        },
        "ACTIVE_INPUT_MANIFEST.tsv": {
            "bytes": len(active_manifest),
            "sha256": sha256(active_manifest),
            "files": ACTIVE_INPUT_FILE_COUNT,
            "expanded_bytes": ACTIVE_INPUT_BYTES,
        },
    }
    receipt = {
        "schema": SCHEMA,
        "status": "authority-verified; runtime environment still requires a separate lock/build gate",
        "work": {
            "title": TITLE,
            "authors": list(AUTHORS),
            "official_reader": OFFICIAL_READER,
            "repository": REPOSITORY,
            "tag": TAG,
            "commit": COMMIT,
            "tree": TREE,
        },
        "evidence": {
            "commit_archive": {
                "path": f"evidence/{COMMIT_ARCHIVE}",
                "bytes": COMMIT_ARCHIVE_BYTES,
                "sha256": COMMIT_ARCHIVE_SHA256,
            },
            "tag_archive": {
                "path": f"evidence/{TAG_ARCHIVE}",
                "bytes": TAG_ARCHIVE_BYTES,
                "sha256": TAG_ARCHIVE_SHA256,
            },
            "notebook_archive": {
                "path": f"evidence/{NOTEBOOK_ARCHIVE}",
                "repository": NOTEBOOK_REPOSITORY,
                "commit": NOTEBOOK_COMMIT,
                "bytes": NOTEBOOK_ARCHIVE_BYTES,
                "sha256": NOTEBOOK_ARCHIVE_SHA256,
            },
            "pdf": {
                "path": f"evidence/{PDF}",
                "bytes": PDF_BYTES,
                "sha256": PDF_SHA256,
                "physical_pages": PDF_PAGES,
                "page_count_basis": "fixed authority receipt fact; byte identity is verified here",
            },
            "license_witness": {
                "path": f"evidence/{LICENSE_WITNESS}",
                "bytes": LICENSE_WITNESS_BYTES,
                "sha256": LICENSE_WITNESS_SHA256,
                "license": LICENSE_NAME,
                "license_url": LICENSE_URL,
                "explicit_statement_present": True,
            },
        },
        "archive_safety": [commit_safety, tag_safety, notebook_safety],
        "source_closure": {
            "commit_and_tag_root_stripped_contents_identical": True,
            "commit_archive_is_immutable_authority": True,
            "manifest_order": "explicit frozen Windows-culture path order; UTF-8 LF; no header",
            "manifests": manifest_facts,
            "source_snapshot_matches_commit_archive": True,
            "notebook_snapshot_matches_notebook_archive": True,
        },
        "teaching_surfaces": teaching,
        "generated_notebooks": notebooks,
        "rights": {
            "license": LICENSE_NAME,
            "repository_root_license_file_present": False,
            "official_reader_witness_required": True,
            "derivative_obligations": [
                "attribute Thomas J. Sargent and John Stachurski and identify changes",
                "license adapted QuantEcon material under CC BY-SA 4.0",
                "retain the license link and non-endorsement",
                "keep separately licensed composite components separately attributed",
            ],
        },
        "source_partition": {
            "all_source_files": SOURCE_FILE_COUNT,
            "active_official_build_inputs": list(ACTIVE_INPUT_PATHS),
            "active_file_count": ACTIVE_INPUT_FILE_COUNT,
            "active_bytes": ACTIVE_INPUT_BYTES,
            "excluded_inactive_source_files": list(EXCLUDED_SOURCE_PATHS),
            "excluded_file_count": len(EXCLUDED_SOURCE_PATHS),
            "partition_is_exact_and_disjoint": True,
        },
        "asset_disposition": {
            "mathematical_asset_retained_for_adaptation": (
                "lectures/_static/lecture_specific/markov_prop/flow_fig.png"
            ),
            "mathematical_asset_has_executable_generation_witness": True,
            "upstream_branding_build_witness_not_reused_in_derivative": (
                "lectures/_static/qe-logo-large.png"
            ),
            "additional_inactive_logo_excluded": "lectures/logo.png",
            "unused_diagram_sources_excluded": [
                "diagrams/cmc_inventory.tikz",
                "diagrams/markov.tikzstyles",
            ],
            "branding_reuse_assumed": False,
        },
        "runtime_and_network_hazards": runtime,
        "verification_scope": {
            "network_access_performed": False,
            "environment_built_or_installed": False,
            "notebooks_executed": False,
            "generated_output_is_deterministic": True,
        },
    }
    receipt_bytes = (
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return {
        "SOURCE_MANIFEST.tsv": source_manifest,
        "NOTEBOOK_MANIFEST.tsv": notebook_manifest,
        "ACTIVE_INPUT_MANIFEST.tsv": active_manifest,
        "AUTHORITY_RECEIPT.json": receipt_bytes,
    }


def write_outputs(root: Path, expected: dict[str, bytes]) -> None:
    require(set(expected) == set(OUTPUT_NAMES), "internal output-name mismatch")
    for name in OUTPUT_NAMES:
        path = root / name
        require(not path.is_symlink(), f"refusing to replace symlink: {path}")
        path.write_bytes(expected[name])


def check_outputs(root: Path, expected: dict[str, bytes]) -> None:
    for name in OUTPUT_NAMES:
        path = root / name
        require(path.is_file(), f"missing generated authority file: {path}")
        require(not path.is_symlink(), f"generated authority file is symlink: {path}")
        actual = path.read_bytes()
        require(actual == expected[name], f"generated authority file differs: {path}")


def summary(mode: str, expected: dict[str, bytes]) -> str:
    return (
        f"PASS mode={mode} source={SOURCE_FILE_COUNT}/{SOURCE_EXPANDED_BYTES} "
        f"source_manifest={SOURCE_MANIFEST_SHA256} "
        f"notebooks={NOTEBOOK_FILE_COUNT}/{NOTEBOOK_EXPANDED_BYTES} "
        f"notebook_manifest={NOTEBOOK_MANIFEST_SHA256} "
        f"active={ACTIVE_INPUT_FILE_COUNT}/{ACTIVE_INPUT_BYTES} "
        f"active_manifest={ACTIVE_INPUT_MANIFEST_SHA256} "
        f"receipt_sha256={sha256(expected['AUTHORITY_RECEIPT.json'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "authority" / "quantecon",
        help="QuantEcon authority directory (default: lane authority/quantecon)",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="verify and write outputs")
    mode.add_argument("--check", action="store_true", help="verify outputs byte-for-byte")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        expected = build_expected(root)
        if args.write:
            write_outputs(root, expected)
            check_outputs(root, expected)
            print(summary("write", expected))
        else:
            check_outputs(root, expected)
            print(summary("check", expected))
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile,
            VerificationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
