#!/usr/bin/env python3
"""Build and verify the isolated Indonesian Kolmogorov-forward unit.

The retained builder reuses the frozen QuantEcon authority verifier, locked
offline Python replay, Pandoc renderer, and component receipt format without
overwriting any earlier component.  It adds only the forward-unit semantics:
one frozen source figure, two deterministically replayed computational figures,
accessible CSV/table alternatives, cross-unit MyST resolution, and the exact
translation/provenance gates for this unit.
"""

from __future__ import annotations

import csv
import html
import io
import json
import math
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

import build_quantecon_component as core
import build_quantecon_poisson_component as harness


ROOT = core.ROOT
AUTH_ROOT = ROOT / "authority" / "quantecon"
SNAPSHOT = (
    AUTH_ROOT
    / "source_snapshot"
    / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
)
NOTEBOOK_SNAPSHOT = (
    AUTH_ROOT
    / "notebook_snapshot"
    / "continuous_time_mcs.notebooks-1e17c25c937f369544380f769eb9c1bc45d12d1a"
)
AUTH_SOURCE = SNAPSHOT / "lectures" / "kolmogorov_fwd.md"
AUTH_NOTEBOOK = NOTEBOOK_SNAPSHOT / "kolmogorov_fwd.ipynb"
AUTH_STATIC_ASSET = (
    SNAPSHOT
    / "lectures"
    / "_static"
    / "lecture_specific"
    / "markov_prop"
    / "flow_fig.png"
)
TARGET_SOURCE = ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_fwd.md"
NUMERICAL_QA = ROOT / "qa" / "QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA.json"
OUT_ROOT = ROOT / "build" / "components" / "quantecon_kolmogorov_fwd"
OUT_HTML = OUT_ROOT / "lectures" / "kolmogorov_fwd.html"
OUT_NOTEBOOK = OUT_ROOT / "notebooks" / "kolmogorov_fwd-executed.ipynb"
OUT_MANIFEST = OUT_ROOT / "COMPONENT_MANIFEST.tsv"
OUT_RECEIPT = OUT_ROOT / "COMPONENT_RECEIPT.json"

UNIT_ID = "unit.o009.quantecon.ctmc.kolmogorov-forward"
UNIT_SLUG = "kolmogorov_fwd"
TARGET_REL = "source/quantecon/lectures/kolmogorov_fwd.md"
AUTH_SOURCE_SHA = "21c694175c28885477fc77b62e8f6a38c8f1d80bbe61cf40c144d285aa6e4b03"
AUTH_NOTEBOOK_SHA = "cb1dd9963c3985b1e16199c4748b55363a00057dc03d89ad4c613552e174ae52"
AUTH_STATIC_ASSET_SHA = "54906c3f6f48664960d25ead98af1150014e88367db1d604f6ccc9d01e50564f"
# Exact repaired target admitted by the independent translation and math audits.
TARGET_SHA = "19abc4dc6ef33c45917684bd487ffa367e36d929b3190960f96d7a7602cb6098"
NUMERICAL_QA_SHA = "c31c816a602590497d2f48b8b3d5a5e1ba0a9a5aa49651dffecbd59290b34ada"
NUMERICAL_QA_BYTES = 3_956
NUMERICAL_QA_SCHEMA = "o009.quantecon-kolmogorov-fwd-numerical-qa.v1"
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra."
SOURCE_FIGURE_REL = "assets/kolmogorov_fwd-source-flow.png"
CELL4_CSV_REL = "assets/kolmogorov_fwd-cell-04-data.csv"
CELL6_CSV_REL = "assets/kolmogorov_fwd-cell-06-data.csv"
TICK = chr(96)
F3 = TICK * 3
F4 = TICK * 4

ORIGINAL_RENDER = harness.render_markdown
ORIGINAL_EXECUTE = harness.execute_cells
ORIGINAL_BUILD = harness.build
ORIGINAL_CHECK = harness.check
_EXECUTION_MODE = False


def _install_bindings() -> None:
    harness.AUTH_SOURCE = AUTH_SOURCE
    harness.AUTH_NOTEBOOK = AUTH_NOTEBOOK
    harness.TARGET_SOURCE = TARGET_SOURCE
    harness.OUT_ROOT = OUT_ROOT
    harness.OUT_HTML = OUT_HTML
    harness.OUT_NOTEBOOK = OUT_NOTEBOOK
    harness.OUT_MANIFEST = OUT_MANIFEST
    harness.OUT_RECEIPT = OUT_RECEIPT
    harness.UNIT_ID = UNIT_ID
    harness.UNIT_SLUG = UNIT_SLUG
    harness.AUTH_SOURCE_SHA = AUTH_SOURCE_SHA
    harness.AUTH_NOTEBOOK_SHA = AUTH_NOTEBOOK_SHA
    harness.TARGET_REL = TARGET_REL


def _directive_count(text: str, name: str) -> int:
    prefix = re.escape(F3) + "|" + re.escape(F4)
    return len(
        re.findall(
            r"^(?:" + prefix + r")\{" + re.escape(name) + r"\}",
            text,
            re.MULTILINE,
        )
    )


def _heading_count(text: str) -> int:
    lines = core.normal_text(text).splitlines()
    count = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(F3 + "{code-cell}"):
            index += 1
            while index < len(lines) and lines[index] != F3:
                index += 1
            if index >= len(lines):
                raise RuntimeError("unterminated code fence while counting headings")
            index += 1
            continue
        if re.match(r"^#{1,6}\s+", line):
            count += 1
        index += 1
    return count


def fence_aware_topology(text: str) -> dict[str, Any]:
    return {
        "headings": _heading_count(text),
        "code_cells": len(core.code_cells(text)),
        "proof_directives": len(
            re.findall(r"^" + re.escape(F3) + r"\{prf:", text, re.MULTILINE)
        ),
        "source_figures": _directive_count(text, "figure"),
        "exercises": _directive_count(text, "exercise"),
        "solutions": (
            _directive_count(text, "solution")
            + _directive_count(text, "solution-start")
        ),
        "labels": sorted(
            re.findall(r"^:label:\s*([^\s]+)", text, re.MULTILINE)
        ),
        "standalone_labels": sorted(
            re.findall(r"^\(([^)]+)\)=\s*$", text, re.MULTILINE)
        ),
        "equation_refs": sorted(
            set(
                re.findall(
                    r"\{eq\}"
                    + re.escape(TICK)
                    + r"([^"
                    + re.escape(TICK)
                    + r"]+)"
                    + re.escape(TICK),
                    text,
                )
            )
        ),
    }


def _display_labels(text: str) -> list[str]:
    return re.findall(r"\$\$\s*\(([A-Za-z0-9_.:-]+)\)\s*$", text, re.MULTILINE)


def _validate_numerical_qa() -> dict[str, Any]:
    raw = harness.require_file(NUMERICAL_QA)
    digest = harness.sha256(raw)
    if len(raw) != NUMERICAL_QA_BYTES or digest != NUMERICAL_QA_SHA:
        raise RuntimeError(
            "Kolmogorov-forward numerical QA differs from the audited receipt: "
            f"bytes={len(raw)} sha256={digest}"
        )
    try:
        numerical = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Kolmogorov-forward numerical QA is not valid UTF-8 JSON") from exc
    if not isinstance(numerical, dict) or set(numerical) != {
        "schema",
        "date",
        "status",
        "target",
        "authority",
        "runtime",
        "tolerances",
        "checks",
    }:
        raise RuntimeError("Kolmogorov-forward numerical QA envelope differs")
    if (
        numerical.get("schema") != NUMERICAL_QA_SCHEMA
        or numerical.get("date") != "2026-08-24"
        or numerical.get("status") != "pass"
    ):
        raise RuntimeError("Kolmogorov-forward numerical QA identity/status differs")
    if numerical.get("target") != {
        "path": TARGET_REL,
        "bytes": 22_210,
        "sha256": TARGET_SHA,
    }:
        raise RuntimeError("Kolmogorov-forward numerical QA target binding differs")
    if numerical.get("authority") != {
        "path": (
            "authority/quantecon/source_snapshot/"
            "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7/"
            "lectures/kolmogorov_fwd.md"
        ),
        "bytes": 16_943,
        "sha256": AUTH_SOURCE_SHA,
    }:
        raise RuntimeError("Kolmogorov-forward numerical QA authority binding differs")

    expected_runtime = {
        "implementation": "CPython",
        "version": "3.13.9",
        "executable": "tmp/quantecon-offline-replay/Scripts/python.exe",
        "executable_sha256": "0e818a1f9a0b8fbd4e7cc458a07cb7de2ea02ea326e387699a33b92f151242cd",
        "numpy": "2.4.4",
        "scipy": "1.17.1",
        "runtime_lock_sha256": "7b7009aa8abf346cd7dec13c50f03f413471e7e0585ed23563685fd4b1f86210",
        "network": "not accessed; pinned offline replay with PIP_NO_INDEX=1",
        "seed": 20_260_824,
        "environment": {
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "MKL_NUM_THREADS": "1",
            "MPLBACKEND": "Agg",
            "NUMBA_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "PIP_NO_INDEX": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONNOUSERSITE": "1",
            "PYTHONUTF8": "1",
            "SOURCE_DATE_EPOCH": "315532800",
            "TZ": "UTC",
        },
    }
    if numerical.get("runtime") != expected_runtime:
        raise RuntimeError("Kolmogorov-forward numerical QA runtime binding differs")
    expected_tolerances = {
        "matrix_identities": 1e-12,
        "central_difference": 1e-08,
        "right_derivative": 1e-05,
        "nonnegativity_floor": 1e-13,
        "uniformization": 1e-12,
    }
    if numerical.get("tolerances") != expected_tolerances:
        raise RuntimeError("Kolmogorov-forward numerical QA tolerances differ")

    checks = numerical.get("checks")
    required_checks = {
        "displayed_P_min",
        "displayed_P_row_sum_max_error",
        "corrected_start_sum_errors",
        "corrected_start_min",
        "displayed_Q_row_sum_max_error",
        "displayed_Q_off_diagonal_min",
        "displayed_Q_diagonal_max",
        "representative_times",
        "transition_row_sum_max_errors",
        "transition_min_entries",
        "evolved_distribution_sum_max_errors",
        "evolved_distribution_min_entries",
        "forward_equation_central_difference_residual",
        "backward_equation_central_difference_residual",
        "generator_commutator_residual",
        "exercise2_K_row_sum_max_error",
        "exercise2_K_diagonal_max_absolute",
        "exercise2_Q_row_sum_max_error",
        "exercise2_Q_off_diagonal_min",
        "exercise2_right_steps",
        "exercise2_right_derivative_residuals",
        "exercise3_zero_m",
        "exercise3_zero_branch",
        "exercise3_zero_identity_error",
        "exercise3_zero_P_hat_error",
        "exercise3_nontrivial_m",
        "exercise3_nontrivial_branch",
        "exercise3_P_hat_row_sum_max_error",
        "exercise3_P_hat_min",
        "exercise3_uniformization_terms",
        "exercise3_uniformization_residual",
    }
    if not isinstance(checks, dict) or set(checks) != required_checks:
        raise RuntimeError("Kolmogorov-forward numerical QA check surface differs")

    def require_finite(value: Any, label: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                require_finite(item, f"{label}.{key}")
            return
        if isinstance(value, bool):
            raise RuntimeError(f"Kolmogorov-forward numerical QA boolean at {label}")
        if isinstance(value, (int, float)):
            if not math.isfinite(float(value)):
                raise RuntimeError(f"Kolmogorov-forward numerical QA nonfinite value at {label}")
            return
        if isinstance(value, list):
            for index, item in enumerate(value):
                require_finite(item, f"{label}[{index}]")

    require_finite(checks, "checks")
    matrix_tol = expected_tolerances["matrix_identities"]
    nonnegative_floor = expected_tolerances["nonnegativity_floor"]
    if checks["representative_times"] != [0.0, 0.001, 0.1, 1.0, 10.0]:
        raise RuntimeError("Kolmogorov-forward representative-time grid differs")
    if checks["exercise2_right_steps"] != [0.001, 0.0001, 1e-05, 1e-06]:
        raise RuntimeError("Kolmogorov-forward right-derivative grid differs")
    if not (
        len(checks["corrected_start_sum_errors"]) == 3
        and len(checks["transition_row_sum_max_errors"]) == 5
        and len(checks["transition_min_entries"]) == 5
        and len(checks["evolved_distribution_sum_max_errors"]) == 5
        and len(checks["evolved_distribution_min_entries"]) == 5
        and len(checks["exercise2_right_derivative_residuals"]) == 4
    ):
        raise RuntimeError("Kolmogorov-forward numerical QA vector census differs")
    if not (
        checks["displayed_P_min"] >= -nonnegative_floor
        and checks["displayed_P_row_sum_max_error"] <= matrix_tol
        and max(checks["corrected_start_sum_errors"]) <= matrix_tol
        and checks["corrected_start_min"] >= -nonnegative_floor
        and checks["displayed_Q_row_sum_max_error"] <= matrix_tol
        and checks["displayed_Q_off_diagonal_min"] >= -nonnegative_floor
        and checks["displayed_Q_diagonal_max"] <= nonnegative_floor
        and max(checks["transition_row_sum_max_errors"]) <= matrix_tol
        and min(checks["transition_min_entries"]) >= -nonnegative_floor
        and max(checks["evolved_distribution_sum_max_errors"]) <= matrix_tol
        and min(checks["evolved_distribution_min_entries"]) >= -nonnegative_floor
        and checks["forward_equation_central_difference_residual"]
        <= expected_tolerances["central_difference"]
        and checks["backward_equation_central_difference_residual"]
        <= expected_tolerances["central_difference"]
        and checks["generator_commutator_residual"] <= matrix_tol
    ):
        raise RuntimeError("Kolmogorov-forward matrix/flow numerical checks fail")
    right_residuals = checks["exercise2_right_derivative_residuals"]
    if not (
        checks["exercise2_K_row_sum_max_error"] <= matrix_tol
        and checks["exercise2_K_diagonal_max_absolute"] <= matrix_tol
        and checks["exercise2_Q_row_sum_max_error"] <= matrix_tol
        and checks["exercise2_Q_off_diagonal_min"] >= -nonnegative_floor
        and all(left > right for left, right in zip(right_residuals, right_residuals[1:]))
        and right_residuals[-1] <= expected_tolerances["right_derivative"]
    ):
        raise RuntimeError("Kolmogorov-forward Exercise 2 numerical checks fail")
    uniformization_tol = expected_tolerances["uniformization"]
    if not (
        checks["exercise3_zero_m"] == 0.0
        and checks["exercise3_zero_branch"] == "zero_generator_identity"
        and checks["exercise3_zero_identity_error"] <= uniformization_tol
        and checks["exercise3_zero_P_hat_error"] <= uniformization_tol
        and checks["exercise3_nontrivial_m"] > 0.0
        and checks["exercise3_nontrivial_branch"] == "nontrivial_uniformization"
        and checks["exercise3_P_hat_row_sum_max_error"] <= uniformization_tol
        and checks["exercise3_P_hat_min"] >= -nonnegative_floor
        and checks["exercise3_uniformization_terms"] == 100
        and checks["exercise3_uniformization_residual"] <= uniformization_tol
    ):
        raise RuntimeError("Kolmogorov-forward Exercise 3 numerical checks fail")
    return numerical


def validate_source(
    target_text: str,
    authority_text: str,
    authority_nb: dict[str, Any],
) -> tuple[str, dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    title, _ = core.frontmatter(target_text)
    if title != "Persamaan Kolmogorov Maju":
        raise RuntimeError(f"unexpected translated title: {title!r}")
    if harness.sha256(target_text.encode("utf-8")) != TARGET_SHA:
        raise RuntimeError("Kolmogorov-forward target hash differs")
    if harness.sha256(harness.require_file(AUTH_STATIC_ASSET)) != AUTH_STATIC_ASSET_SHA:
        raise RuntimeError("frozen Kolmogorov-forward source figure hash differs")
    _validate_numerical_qa()

    target_cells = core.code_cells(target_text)
    authority_cells = core.code_cells(authority_text)
    if len(target_cells) != 6 or len(authority_cells) != 6:
        raise RuntimeError(
            f"code-cell census differs: target={len(target_cells)} "
            f"authority={len(authority_cells)}"
        )
    if (
        len(authority_nb.get("cells", [])) != 32
        or sum(cell.get("cell_type") == "code" for cell in authority_nb["cells"])
        != 6
    ):
        raise RuntimeError("notebook witness does not have the admitted 32/6 cell census")
    for index, (target, authority) in enumerate(
        zip(target_cells, authority_cells, strict=True), start=1
    ):
        if target["kernel"] != authority["kernel"] or target["tags"] != authority["tags"]:
            raise RuntimeError(f"code-cell metadata differs at cell {index}")

    topology = fence_aware_topology(target_text)
    authority_topology = fence_aware_topology(authority_text)
    expected = {
        "headings": 13,
        "code_cells": 6,
        "proof_directives": 2,
        "source_figures": 1,
        "exercises": 3,
        "solutions": 3,
    }
    for key, value in expected.items():
        if int(topology.get(key, -1)) != value:
            raise RuntimeError(f"target topology differs for {key}: {topology}")
        if int(authority_topology.get(key, -1)) != value:
            raise RuntimeError(f"authority topology differs for {key}: {authority_topology}")
    for key in ("labels", "standalone_labels", "equation_refs"):
        if topology[key] != authority_topology[key]:
            raise RuntimeError(f"source identity topology differs for {key}")
    if _display_labels(target_text) != _display_labels(authority_text):
        raise RuntimeError("display equation-label order differs")
    authority_displays = re.findall(r"\$\$.*?\$\$", authority_text, re.DOTALL)
    target_displays = re.findall(r"\$\$.*?\$\$", target_text, re.DOTALL)
    if len(authority_displays) != 19 or len(target_displays) != 21:
        raise RuntimeError(
            "display-math census differs from the admitted corrected target: "
            f"target={len(target_displays)} authority={len(authority_displays)}"
        )

    required_metadata = (
        "unit_id: unit.o009.quantecon.ctmc.kolmogorov-forward",
        "source_path: lectures/kolmogorov_fwd.md",
        "source_license: CC BY-SA 4.0",
        MODEL_PROVENANCE,
        "tidak didukung atau disahkan oleh QuantEcon",
    )
    if any(token not in target_text for token in required_metadata):
        raise RuntimeError("forward-unit metadata/provenance gate is incomplete")
    required_labels = {
        "gdiff2",
        "ode_mc",
        "solvode",
        "cmc_sol",
        "intvsmk",
        "intvsmk_c",
        "genfl",
        "qeqagain",
        "otp",
        "kolmogorov-fwd-1",
        "kolmogorov-fwd-2",
        "kolmogorov-fwd-3",
    }
    if any(token not in target_text for token in required_labels):
        raise RuntimeError("target lost a required source label or anchor")

    joined_code = "\n".join(cell["source"] for cell in target_cells)
    forbidden_code = (
        "pip install",
        "import scipy as sp",
        "import quantecon as qe",
        "from numba import njit",
        "from mpl_toolkits.mplot3d import Axes3D",
        "(0.01, 0.01, 0.99)",
    )
    if any(token in joined_code for token in forbidden_code):
        raise RuntimeError("forbidden source/runtime code survived in the target")
    required_code = (
        "def convergence_plot",
        "ψ = ψ @ P",
        "ψ_00 = np.array((0.01, 0.01, 0.98))",
        "ψ_01 = np.array((0.01, 0.98, 0.01))",
        "ψ_02 = np.array((0.98, 0.01, 0.01))",
        "def flow_plot",
        "ψ = ψ @ expm(h * Q)",
    )
    if any(token not in joined_code for token in required_code):
        raise RuntimeError("required deterministic forward-unit code is missing")
    required_corrections = (
        r"G(\dD)\subseteq\dD",
        "untuk semua $t\\geq0$",
        "P_h = I + hQ + O(h^2).",
        "Jika $m=0$",
        "K(y,y)=0",
    )
    if any(token not in target_text for token in required_corrections):
        raise RuntimeError("a required mathematical correction is missing")
    if "persamaan maju kolmogorov" in target_text.casefold():
        raise RuntimeError("terminology regression in forward-equation word order")
    if "TTP" in target_text or "Translation and Transcription Project" in target_text:
        raise RuntimeError("forbidden umbrella label leaked into the unit")
    return title, topology, target_cells, []


def _execution_instrumentation(source: str) -> str:
    if "def convergence_plot" in source:
        return """
print("langkah,p0,p1,p2")
_o009_psi = np.array((0.0, 0.0, 1.0), dtype=float)
_o009_P = np.array(P, dtype=float)
for _o009_step in range(14):
    print(f"{_o009_step},{_o009_psi[0]:.12f},{_o009_psi[1]:.12f},{_o009_psi[2]:.12f}")
    _o009_psi = _o009_psi @ _o009_P
"""
    if "def flow_plot" in source:
        return """
print("lintasan,langkah,waktu,p0,p1,p2")
_o009_transition = expm(0.001 * Q)
for _o009_name, _o009_initial in (
    ("sudut-0", psi_00), ("sudut-1", psi_01), ("sudut-2", psi_02)
):
    _o009_psi = _o009_initial.copy()
    for _o009_step in range(400):
        print(f"{_o009_name},{_o009_step},{0.001 * _o009_step:.3f},"
              f"{_o009_psi[0]:.12f},{_o009_psi[1]:.12f},{_o009_psi[2]:.12f}")
        _o009_psi = _o009_psi @ _o009_transition
""".replace("psi_00", "ψ_00").replace("psi_01", "ψ_01").replace("psi_02", "ψ_02")
    return ""


def downstream_code(source: str) -> str:
    prepared = source.rstrip() + "\n"
    if _EXECUTION_MODE:
        prepared += _execution_instrumentation(source)
    return prepared


def _parse_csv(stdout: str, expected_header: list[str], expected_rows: int) -> list[list[str]]:
    rows = list(csv.reader(io.StringIO(stdout)))
    if len(rows) != expected_rows + 1 or rows[0] != expected_header:
        raise RuntimeError(
            f"accessible execution CSV differs: header={rows[:1]} rows={len(rows)}"
        )
    if any(len(row) != len(expected_header) for row in rows):
        raise RuntimeError("accessible execution CSV has a nonrectangular row")
    return rows


def execute_cells(
    cells: list[dict[str, Any]], interpreter: Path
) -> list[dict[str, Any]]:
    global _EXECUTION_MODE
    _EXECUTION_MODE = True
    try:
        results = ORIGINAL_EXECUTE(cells, interpreter)
    finally:
        _EXECUTION_MODE = False
    figures = {
        int(item["index"]): len(item["figures"])
        for item in results
        if item["figures"]
    }
    if figures != {4: 1, 6: 1}:
        raise RuntimeError(f"forward-unit execution-figure census differs: {figures}")
    if any(item["stderr"] for item in results):
        raise RuntimeError("forward-unit execution emitted stderr")
    _parse_csv(
        str(results[3]["stdout"]),
        ["langkah", "p0", "p1", "p2"],
        14,
    )
    _parse_csv(
        str(results[5]["stdout"]),
        ["lintasan", "langkah", "waktu", "p0", "p1", "p2"],
        1200,
    )
    return results


def directive_to_fenced(text: str) -> str:
    lines = core.normal_text(text).splitlines()
    output: list[str] = []
    stack: list[tuple[str, str]] = []
    solution_number = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(F3 + "{code-cell}"):
            close = index + 1
            while close < len(lines) and lines[close] != F3:
                close += 1
            if close >= len(lines):
                raise RuntimeError("unterminated QuantEcon code cell")
            output.extend(["", "<!-- O009_CODE_CELL -->", ""])
            index = close + 1
            continue

        figure_match = re.match(
            r"^" + re.escape(F3) + r"\{figure\}\s+(.+?)\s*$", line
        )
        if figure_match:
            source_path = figure_match.group(1)
            expected_path = "_static/lecture_specific/markov_prop/flow_fig.png"
            if source_path != expected_path:
                raise RuntimeError(f"unexpected forward-unit source figure: {source_path}")
            close = index + 1
            while close < len(lines) and lines[close] != F3:
                close += 1
            if close >= len(lines):
                raise RuntimeError("unterminated source-figure directive")
            caption = " ".join(
                part.strip() for part in lines[index + 1 : close] if part.strip()
            )
            output.append(
                '<figure class="source-figure" id="kolmogorov-fwd-source-flow">'
                '<img src="../assets/kolmogorov_fwd-source-flow.png" '
                'alt="Grafik permukaan tiga dimensi aliran probabilitas persediaan '
                'pada keadaan 0 sampai 10 dan waktu 0 sampai 20; warna panas '
                'menandai waktu awal dan warna sejuk waktu akhir.">'
                f"<figcaption>{html.escape(caption)}</figcaption></figure>"
            )
            index = close + 1
            continue

        proof = re.match(
            r"^"
            + re.escape(F3)
            + r"\{prf:(theorem|corollary|proof|lemma|algorithm)\}(?:\s+(.*))?$",
            line,
        )
        if proof:
            kind, caption = proof.group(1), (proof.group(2) or "").strip()
            index += 1
            label = None
            while index < len(lines) and (
                lines[index].startswith(":") or not lines[index].strip()
            ):
                if lines[index].startswith(":label:"):
                    label = lines[index].split(":", 2)[-1].strip()
                index += 1
            attrs = f"#{label} " if label else ""
            output.append(f"::: {{{attrs}.qe-{kind}}}")
            if caption:
                output.append(f"**{caption}**")
            stack.append(("directive", F3))
            continue

        if line in {F3 + "{exercise}", F4 + "{exercise}"}:
            closing = F4 if line.startswith(F4) else F3
            index += 1
            label = None
            while index < len(lines) and (
                lines[index].startswith(":") or not lines[index].strip()
            ):
                if lines[index].startswith(":label:"):
                    label = lines[index].split(":", 2)[-1].strip()
                index += 1
            attrs = f"#{label} " if label else ""
            output.append(f"::: {{{attrs}.exercise}}")
            stack.append(("exercise", closing))
            continue

        solution = re.match(
            r"^" + re.escape(F3) + r"\{solution\}\s+([^\s]+)", line
        )
        solution_start = re.match(
            r"^" + re.escape(F3) + r"\{solution-start\}\s+([^\s]+)", line
        )
        if solution or solution_start:
            solution_number += 1
            output.append(
                f"::: {{#{UNIT_SLUG}-solution-{solution_number} .solution}}"
            )
            output.append("**Solusi**")
            stack.append(("solution", F3))
            index += 1
            while index < len(lines) and (
                lines[index].startswith(":") or not lines[index].strip()
            ):
                index += 1
            if solution_start and index < len(lines) and lines[index] == F3:
                index += 1
            continue

        if line == F3 + "{solution-end}":
            if not stack or stack[-1][0] != "solution":
                raise RuntimeError("solution-end without solution-start")
            stack.pop()
            output.append(":::")
            index += 1
            if index < len(lines) and lines[index] == F3:
                index += 1
            continue

        if line == F3 + "ipython3":
            close = index + 1
            while close < len(lines) and lines[close] != F3:
                close += 1
            if close >= len(lines):
                raise RuntimeError("unterminated nested exercise code fence")
            output.extend(lines[index : close + 1])
            index = close + 1
            continue

        if line in {F3, F4}:
            if not stack or stack[-1][1] != line:
                raise RuntimeError(f"unexpected MyST closing fence: {line!r}")
            stack.pop()
            output.append(":::")
            index += 1
            continue
        output.append(line)
        index += 1
    if stack:
        raise RuntimeError(f"unterminated MyST directives: {stack}")
    return "\n".join(output) + "\n"


def _split_role(raw: str) -> tuple[str, str]:
    match = re.fullmatch(r"(.*?)\s*<([^<>]+)>", raw, flags=re.DOTALL)
    if match:
        return " ".join(match.group(1).split()), match.group(2)
    return raw.strip(), raw.strip()


def _replace_roles(source: str) -> str:
    ref_targets = {
        "invdistflows": "markov_prop.html#invdistflows",
        "finstatediscretemc": "markov_prop.html#finstatediscretemc",
        "jdfin": "markov_prop.html#jdfin",
        "sdji": "kolmogorov_bwd.html#sdji",
    }

    def ref_replacement(match: re.Match[str]) -> str:
        label, anchor = _split_role(match.group(1))
        if anchor not in ref_targets:
            raise RuntimeError(f"unmapped forward-unit ref role: {anchor}")
        return f"[{label}]({ref_targets[anchor]})"

    source = re.sub(r"\{ref\}`([^`]+)`", ref_replacement, source)

    def doc_replacement(match: re.Match[str]) -> str:
        label, document = _split_role(match.group(1))
        if document != "kolmogorov_bwd":
            raise RuntimeError(f"unmapped forward-unit doc role: {document}")
        return f"[{label}](kolmogorov_bwd.html)"

    source = re.sub(r"\{doc\}`([^`]+)`", doc_replacement, source)
    proof_targets = {
        "jctosg": ("teorema rantai lompatan ke semigrup", "kolmogorov_bwd.html#jctosg"),
        "ejc_algo": ("algoritma rantai lompatan", "kolmogorov_bwd.html#ejc_algo"),
        "intvsmk": ("teorema ekuivalensi", "#intvsmk"),
    }

    def proof_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in proof_targets:
            raise RuntimeError(f"unmapped forward-unit proof role: {key}")
        label, target = proof_targets[key]
        return f"[{label}]({target})"

    source = re.sub(r"\{prf:ref\}`([^`]+)`", proof_replacement, source)
    source = source.replace(
        "{eq}`expoderiv`",
        "[persamaan expoderiv](kolmogorov_bwd.html#equation-expoderiv)",
    )
    return source


def _append_table(
    soup: BeautifulSoup,
    figure: Any,
    rows: list[list[str]],
    *,
    cell_index: int,
    csv_name: str,
    summary_rows: list[list[str]],
) -> None:
    details = soup.new_tag(
        "details",
        id=f"kolmogorov-fwd-data-{cell_index}",
        attrs={"class": "execution-data"},
    )
    summary = soup.new_tag("summary")
    summary_label = f"Data aksesibel untuk gambar sel {cell_index}"
    summary["aria-label"] = summary_label
    summary.string = summary_label
    details.append(summary)
    paragraph = soup.new_tag("p")
    link = soup.new_tag("a", href=f"../assets/{csv_name}")
    link.string = "Unduh seluruh data deterministik sebagai CSV"
    paragraph.append(link)
    details.append(paragraph)
    table = soup.new_tag(
        "table",
        id=f"kolmogorov-fwd-data-{cell_index}-table",
    )
    table["aria-label"] = f"Ringkasan data numerik gambar sel {cell_index}"
    thead = soup.new_tag("thead")
    header_row = soup.new_tag("tr")
    for value in rows[0]:
        cell = soup.new_tag("th")
        cell.string = value
        header_row.append(cell)
    thead.append(header_row)
    table.append(thead)
    tbody = soup.new_tag("tbody")
    for source_row in summary_rows:
        row = soup.new_tag("tr")
        for value in source_row:
            cell = soup.new_tag("td")
            cell.string = value
            row.append(cell)
        tbody.append(row)
    table.append(tbody)
    details.append(table)
    figure.insert_after(details)


def render_markdown(
    source: str,
    execution: list[dict[str, Any]],
    title: str,
    stage: Path,
) -> str:
    assets = stage / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(AUTH_STATIC_ASSET, stage / SOURCE_FIGURE_REL)
    prepared = _replace_roles(source)
    rendered = ORIGINAL_RENDER(prepared, execution, title, stage)
    for path in sorted(assets.glob("memoryless-cell-*.png")):
        path.rename(
            path.with_name(path.name.replace("memoryless-cell-", f"{UNIT_SLUG}-cell-"))
        )
    rendered = rendered.replace("memoryless-cell-", f"{UNIT_SLUG}-cell-")
    soup = BeautifulSoup(rendered, "lxml")
    alternatives = {
        4: (
            "Empat belas distribusi berturut-turut dalam simpleks tiga keadaan, "
            "bermula di (0,0,1) dan bergerak menurut matriks Markov P."
        ),
        6: (
            "Tiga lintasan aliran distribusi waktu kontinu dari dekat ketiga "
            "titik sudut simpleks menuju bagian dalam di bawah eksponensial matriks."
        ),
    }
    results = {int(item["index"]): item for item in execution}
    seen: set[int] = set()
    for image in soup.find_all("img"):
        match = re.search(
            rf"{re.escape(UNIT_SLUG)}-cell-(\d+)-", str(image.get("src", ""))
        )
        if not match:
            continue
        cell_index = int(match.group(1))
        if cell_index not in alternatives:
            raise RuntimeError(f"unexpected generated figure cell: {cell_index}")
        image["alt"] = alternatives[cell_index]
        figure = image.find_parent("figure")
        if figure is None:
            raise RuntimeError("execution image has no figure ancestor")
        caption = figure.find("figcaption")
        if caption is None:
            caption = soup.new_tag("figcaption")
            figure.append(caption)
        caption.string = alternatives[cell_index]
        if cell_index in seen:
            continue
        if cell_index == 4:
            rows = _parse_csv(
                str(results[4]["stdout"]),
                ["langkah", "p0", "p1", "p2"],
                14,
            )
            csv_name = Path(CELL4_CSV_REL).name
            (assets / csv_name).write_text(
                str(results[4]["stdout"]).rstrip() + "\n",
                encoding="utf-8",
                newline="\n",
            )
            summary_rows = rows[1:]
        else:
            rows = _parse_csv(
                str(results[6]["stdout"]),
                ["lintasan", "langkah", "waktu", "p0", "p1", "p2"],
                1200,
            )
            csv_name = Path(CELL6_CSV_REL).name
            (assets / csv_name).write_text(
                str(results[6]["stdout"]).rstrip() + "\n",
                encoding="utf-8",
                newline="\n",
            )
            summary_rows = [
                row
                for row in rows[1:]
                if row[1] in {"0", "100", "200", "300", "399"}
            ]
            if len(summary_rows) != 15:
                raise RuntimeError("forward-flow accessible summary census differs")
        _append_table(
            soup,
            figure,
            rows,
            cell_index=cell_index,
            csv_name=csv_name,
            summary_rows=summary_rows,
        )
        seen.add(cell_index)
    if seen != {4, 6}:
        raise RuntimeError(f"generated figure set differs: {sorted(seen)}")

    for index, summary in enumerate(soup.select("details.code-cell > summary"), start=1):
        label = f"Tampilkan kode sel {index}"
        summary["aria-label"] = label
        summary.string = label
    attribution = soup.select_one("#quantecon-attribution")
    if attribution is None:
        raise RuntimeError("QuantEcon attribution panel is missing")
    provenance = soup.new_tag("p", attrs={"class": "model-provenance"})
    provenance.string = (
        f"Provenans produksi: {MODEL_PROVENANCE} "
        "Kredit penulis dan kontributor manusia tetap dipertahankan."
    )
    attribution.append(provenance)
    return "<!DOCTYPE html>\n" + str(soup)


def validate_rendered(path: Path, root: Path | None = None) -> None:
    soup = BeautifulSoup(harness.require_file(path).decode("utf-8"), "lxml")
    if soup.html is None or soup.html.get("lang") != "id-ID":
        raise RuntimeError("forward-equation HTML lacks lang=id-ID")
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("forward-equation HTML must have exactly one h1 and one main")
    ids = [str(tag["id"]) for tag in soup.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate HTML id in forward-equation component")
    summary_labels = [
        str(summary.get("aria-label", "")).strip()
        for summary in soup.find_all("summary")
    ]
    if any(not label for label in summary_labels) or len(summary_labels) != len(
        set(summary_labels)
    ):
        raise RuntimeError("forward-equation disclosure labels are missing or duplicated")
    core.validate_equation_ids(ids)
    required = {
        "equation-gdiff2",
        "equation-ode_mc",
        "solvode",
        "equation-cmc_sol",
        "intvsmk",
        "intvsmk_c",
        "equation-genfl",
        "equation-qeqagain",
        "equation-otp",
        "kolmogorov-fwd-1",
        "kolmogorov-fwd-2",
        "kolmogorov-fwd-3",
        "kolmogorov_fwd-solution-1",
        "kolmogorov_fwd-solution-2",
        "kolmogorov_fwd-solution-3",
        "kolmogorov-fwd-source-flow",
        "kolmogorov-fwd-data-4",
        "kolmogorov-fwd-data-4-table",
        "kolmogorov-fwd-data-6",
        "kolmogorov-fwd-data-6-table",
        *(f"qe-cell-{index}" for index in range(1, 7)),
    }
    if not required.issubset(set(ids)):
        raise RuntimeError(f"missing forward-equation labels: {sorted(required - set(ids))}")
    classes = {name for tag in soup.find_all(True) for name in tag.get("class", [])}
    expected_classes = {
        "exercise",
        "solution",
        "qe-theorem",
        "qe-corollary",
        "source-figure",
        "execution-figure",
        "execution-data",
    }
    if not expected_classes.issubset(classes):
        raise RuntimeError(
            f"directive/accessibility semantics are incomplete: "
            f"{sorted(expected_classes - classes)}"
        )
    rendered = str(soup)
    raw_tokens = ("O009_FIGURES_", "{doc}", "{ref}", "{prf:ref}", "{eq}", F3 + "{")
    if any(token in rendered for token in raw_tokens):
        raise RuntimeError("raw MyST or figure placeholder leaked into HTML")
    if MODEL_PROVENANCE not in rendered:
        raise RuntimeError("exact model provenance missing from rendered HTML")
    if len(soup.select("figure.execution-figure")) != 2:
        raise RuntimeError("rendered execution-figure census differs")
    if len(soup.select("figure.source-figure")) != 1:
        raise RuntimeError("rendered source-figure census differs")
    for image in soup.select("img"):
        if not str(image.get("alt", "")).strip():
            raise RuntimeError("empty image alternative in forward-equation HTML")

    root = root or path.parent.parent
    csv_expectations = {
        CELL4_CSV_REL: (["langkah", "p0", "p1", "p2"], 14),
        CELL6_CSV_REL: (
            ["lintasan", "langkah", "waktu", "p0", "p1", "p2"],
            1200,
        ),
    }
    for relative, (header, row_count) in csv_expectations.items():
        csv_path = root / relative
        _parse_csv(
            harness.require_file(csv_path).decode("utf-8"),
            header,
            row_count,
        )
    if harness.sha256(harness.require_file(root / SOURCE_FIGURE_REL)) != AUTH_STATIC_ASSET_SHA:
        raise RuntimeError("rendered source-figure bytes differ from authority")
    if len(soup.select("#kolmogorov-fwd-data-4-table tbody tr")) != 14:
        raise RuntimeError("cell-4 accessible table row census differs")
    if len(soup.select("#kolmogorov-fwd-data-6-table tbody tr")) != 15:
        raise RuntimeError("cell-6 accessible summary row census differs")
    for tag in soup.select("script[src], link[href]"):
        ref = str(tag.get("src") or tag.get("href") or "")
        if ref.startswith(("http:", "https:", "//")):
            raise RuntimeError(f"external runtime asset leaked: {ref}")
    allowed_cross_unit = {
        "markov_prop.html#invdistflows",
        "markov_prop.html#finstatediscretemc",
        "markov_prop.html#jdfin",
        "kolmogorov_bwd.html",
        "kolmogorov_bwd.html#equation-expoderiv",
        "kolmogorov_bwd.html#jctosg",
        "kolmogorov_bwd.html#ejc_algo",
        "kolmogorov_bwd.html#sdji",
    }
    for tag in soup.select("a[href], img[src], script[src], link[href]"):
        ref = str(tag.get("href") or tag.get("src") or "")
        if ref.startswith(("http:", "https:", "#", "mailto:")) or not ref:
            continue
        if ref == "../../index.html" or ref in allowed_cross_unit:
            continue
        target = (path.parent / ref.split("#", 1)[0]).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise RuntimeError(f"reference escapes component: {ref}") from exc
        if not target.is_file():
            raise RuntimeError(f"local component reference missing: {ref}")


def correction_records(_formula_corrections: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {"id": "kolmogorov-fwd-numerical-qa-binding", "description": f"Bound the deterministic mathematical QA receipt at SHA-256 {NUMERICAL_QA_SHA}."},
        {"id": "kolmogorov-fwd-ambient-vector-space", "description": "Placed the linear map on ambient R^n while retaining the distribution simplex as an invariant subset."},
        {"id": "kolmogorov-fwd-simplex-initial-points", "description": "Changed the three dominant initial coordinates from 0.99 to 0.98 so every plotted vector sums exactly to one."},
        {"id": "kolmogorov-fwd-nonnegative-time-domain", "description": "Made the Markov-semigroup quantifier explicit as every t greater than or equal to zero."},
        {"id": "kolmogorov-fwd-row-sum-notation", "description": "Replaced dimensionally ambiguous lambda-vector shorthand with a pointwise row-sum proof."},
        {"id": "kolmogorov-fwd-generator-limit-completion", "description": "Completed the second solution by proving the requested generator limit through the matrix-exponential expansion."},
        {"id": "kolmogorov-fwd-zero-uniformization", "description": "Handled m=0 before defining I+Q/m in the third solution."},
        {"id": "kolmogorov-fwd-jump-kernel-diagonal", "description": "Restated the inherited K(y,y)=0 assumption required by the displayed outflow formula."},
        {"id": "kolmogorov-fwd-unused-imports-offline", "description": "Removed runtime installation and unused imports while preserving every required executable cell and its position."},
        {"id": "kolmogorov-fwd-source-figure", "description": f"Copied the frozen inventory-flow source figure exactly at SHA-256 {AUTH_STATIC_ASSET_SHA}."},
        {"id": "kolmogorov-fwd-accessible-figures", "description": "Added meaningful Indonesian alternatives, a complete 14-row simplex table, complete deterministic CSVs, and a 15-row summary of the 1,200-point continuous-time flow."},
        {"id": "kolmogorov-fwd-myst-references", "description": "Resolved local and cross-unit MyST roles without leaving raw reader markup."},
        {"id": "quantecon-branding-runtime", "description": "Removed remote runtime and branding while preserving authorship, CC BY-SA 4.0, exact model provenance, and non-endorsement."},
    ]


def build() -> None:
    numerical = _validate_numerical_qa()
    ORIGINAL_BUILD()
    receipt = harness.load_json(OUT_RECEIPT)
    receipt["authority"]["static_assets"] = [
        {
            "path": str(AUTH_STATIC_ASSET.relative_to(ROOT)),
            "bytes": len(harness.require_file(AUTH_STATIC_ASSET)),
            "sha256": AUTH_STATIC_ASSET_SHA,
            "component_path": SOURCE_FIGURE_REL,
        }
    ]
    receipt["accessibility_data"] = [
        {
            "path": CELL4_CSV_REL,
            "rows": 14,
            "sha256": harness.sha256(harness.require_file(OUT_ROOT / CELL4_CSV_REL)),
        },
        {
            "path": CELL6_CSV_REL,
            "rows": 1200,
            "sha256": harness.sha256(harness.require_file(OUT_ROOT / CELL6_CSV_REL)),
        },
    ]
    receipt["numerical_qa"] = {
        "path": str(NUMERICAL_QA.relative_to(ROOT)).replace("\\", "/"),
        "status": str(numerical["status"]),
        "sha256": NUMERICAL_QA_SHA,
    }
    OUT_RECEIPT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    validate_rendered(OUT_HTML)
    print(
        f"PASS augmented unit={UNIT_ID} "
        f"receipt_sha256={harness.sha256(harness.require_file(OUT_RECEIPT))}"
    )


def check() -> None:
    if harness.sha256(harness.require_file(TARGET_SOURCE)) != TARGET_SHA:
        raise RuntimeError("Kolmogorov-forward target requires an explicit hash rebind")
    numerical = _validate_numerical_qa()
    ORIGINAL_CHECK()
    receipt = harness.load_json(OUT_RECEIPT)
    assets = receipt.get("authority", {}).get("static_assets", [])
    if len(assets) != 1 or assets[0].get("sha256") != AUTH_STATIC_ASSET_SHA:
        raise RuntimeError("forward-unit receipt lacks the frozen source-figure binding")
    expected_numerical = {
        "path": str(NUMERICAL_QA.relative_to(ROOT)).replace("\\", "/"),
        "status": str(numerical["status"]),
        "sha256": NUMERICAL_QA_SHA,
    }
    if receipt.get("numerical_qa") != expected_numerical:
        raise RuntimeError("forward-unit receipt lacks the current numerical-QA binding")
    validate_rendered(OUT_HTML)


def install() -> None:
    _install_bindings()
    harness.validate_source = validate_source
    harness.downstream_code = downstream_code
    harness.execute_cells = execute_cells
    harness.directive_to_fenced = directive_to_fenced
    harness.render_markdown = render_markdown
    harness.validate_rendered = validate_rendered
    harness.correction_records = correction_records
    harness.build = build
    harness.check = check


def main() -> int:
    install()
    return harness.main()


if __name__ == "__main__":
    sys.exit(main())
