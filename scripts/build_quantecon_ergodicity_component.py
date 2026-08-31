#!/usr/bin/env python3
"""Build and verify the isolated Indonesian stationarity/ergodicity unit."""

from __future__ import annotations

import base64
import hashlib
import json
import re
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
AUTH_SOURCE = SNAPSHOT / "lectures" / "ergodicity.md"
AUTH_NOTEBOOK = NOTEBOOK_SNAPSHOT / "ergodicity.ipynb"
TARGET_SOURCE = ROOT / "source" / "quantecon" / "lectures" / "ergodicity.md"
OUT_ROOT = ROOT / "build" / "components" / "quantecon_ergodicity"
OUT_HTML = OUT_ROOT / "lectures" / "ergodicity.html"
OUT_NOTEBOOK = OUT_ROOT / "notebooks" / "ergodicity-executed.ipynb"
OUT_MANIFEST = OUT_ROOT / "COMPONENT_MANIFEST.tsv"
OUT_RECEIPT = OUT_ROOT / "COMPONENT_RECEIPT.json"
NUMERICAL_QA = ROOT / "qa" / "QUANTECON_ERGODICITY_NUMERICAL_QA.json"

UNIT_ID = "unit.o009.quantecon.ctmc.stationarity-ergodicity"
UNIT_SLUG = "ergodicity"
TARGET_REL = "source/quantecon/lectures/ergodicity.md"
AUTH_SOURCE_SHA = "01c8f94e8016119107d6a3c14e688a0c1ed71690f678a2ae252703f7abccba84"
AUTH_NOTEBOOK_SHA = "e9daac187c07d8ba4d63cb43df2bb1874afa69a6095f91dd9f14a27c674fa881"
TARGET_SHA = "5ae7f5f06befc5c71727da6c33678af5aac3fed523e9d547fb7a0577a1af61ad"
MATHJAX_SHA = "dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a"
CSS_SHA = "820f354bd797c5b5cb0e34248bc82c9b835e0fafb66fed75145f7c8180fa997c"
NUMERICAL_QA_SHA = "b2571f0c59f067a3b6a4dc0d696a990d3dacfa3b78967c0ee1e4c539fc984eb6"
FIGURE_SHA = "cf9cecb59c93a0e74e9c6322d5497dcfe89a9fbe4d15223cc4a65d1c257fe0fc"
FIGURE_BYTES = 37_187
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra."
TICK = chr(96)
F3 = TICK * 3

ORIGINAL_RENDER = harness.render_markdown
ORIGINAL_EXECUTE = harness.execute_cells
ORIGINAL_BUILD = harness.build
ORIGINAL_CHECK = harness.check

EXPECTED_LABELS = [
    "equivirr",
    "ergodicity-ex-1",
    "ergodicity-ex-2",
    "ergodicity-ex-3",
    "perimposs",
    "sdrift",
    "sfinite",
    "stabskel",
    "statfromq",
    "strictcontract",
    "uniirr",
]
EXPECTED_EQUATION_LABELS = [
    "ptexpan",
    "qkassum",
    "unifexp",
    "rkassum",
    "asyms",
    "allmocontract",
    "mm1q",
]
EXPECTED_AUTHORITY_EQUATION_LABELS = [
    "ptexpan",
    "qkassum",
    "asyms",
    "allmocontract",
    "mm1q",
]
EXPECTED_TARGET_EQUATION_REFS = [
    "allmocontract",
    "asyms",
    "chapkol_ct2",
    "kfromqxx",
    "kfromqxy",
    "lambdafromq",
    "mm1q",
    "ptexpan",
    "qkassum",
    "rkassum",
    "unifexp",
]
EXPECTED_AUTHORITY_EQUATION_REFS = [
    "allmocontract",
    "asyms",
    "chapkol_ct2",
    "kfromqxx",
    "kfromqxy",
    "lambdafromq",
    "mm1q",
]
EXPECTED_TARGET_CODE_SHA = [
    "051b372d71f8347804f0474ac3ff09d1cc154765ef922dd4a6692ae0cde9fca9",
    "058d7b9d54b60eb553f03210bdb556b3a8cd56e3e179ab4dc80772c481b80a30",
    "65aa79e223cd5fc3f22431241528dd1588a5cdc7f20a4d1cccf7dd2fc9f42775",
    "809d41c6522066ff4b34917e4dd287730930839c2beaf3ee38d9b7ee6e82b990",
]
EXPECTED_AUTHORITY_CODE_SHA = [
    "c18d8d19d04280516dbaa4fcf818d5c05656b4c8539e7c68449e3eed34df1b4b",
    "622211bc4628c38147c98711fcd62b5dac361479f3652ea762f8cde88e252dd5",
    "65aa79e223cd5fc3f22431241528dd1588a5cdc7f20a4d1cccf7dd2fc9f42775",
    "8f89bc7dfeed244befa099db085fe8403d444f7569494eb8b340e0eca1043b10",
]
EXPECTED_NOTEBOOK_CODE_SHA = [
    "b2d2562b1a941fc815498fd5e78c415464f44818be21d3ab1cdc7f91b1217060",
    "c8eb3db2a1bb1ebe783f59942002db6a6cbae9ddec24da44570df9411f95b965",
    "0bff4cf525d9178a3b127b0af49452fdc21102cb977bd5e6a770c664cf6446c6",
    "1af9745c28653c29c861bb760cfe3cc7bd4fb06d72a5d779f96f9cb9beb272e4",
]
EXPECTED_CITATIONS = {
    "lasota1994chaos": (
        "Andrzej Lasota dan Michael C. Mackey, Chaos, Fractals, and Noise: "
        "Stochastic Aspects of Dynamics (Springer, 1994), Proposition 3.1.2"
    ),
    "pichor2012stochastic": (
        "Katarzyna Pichór, Ryszard Rudnicki, dan Marta Tyran-Kamińska, "
        "Stochastic Semigroups and Their Applications to Biological Models, "
        "Demonstratio Mathematica 45(2), 463–494 (2012)"
    ),
    "stachurski2009economic": (
        "John Stachurski, Economic Dynamics: Theory and Computation "
        "(MIT Press, 2009), Lemma 8.2.3"
    ),
}
EXPECTED_CROSS_UNIT_LINKS = {
    "kolmogorov_bwd.html#ejc_algo",
    "kolmogorov_fwd.html#solvode",
    "markov_prop.html#equation-chapkol_ct2",
    "uc_mc_semigroups.html#equation-kfromqxx",
    "uc_mc_semigroups.html#equation-kfromqxy",
    "uc_mc_semigroups.html#equation-lambdafromq",
}
FIGURE_ALT = (
    "Simpleks probabilitas tiga keadaan dengan tiga lintasan yang bergerak "
    "dari dekat titik-titik sudut menuju distribusi stasioner yang sama."
)


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


def _heading_count(text: str) -> int:
    return len(re.findall(r"^#{1,6}\s+", core.normal_text(text), re.MULTILINE))


def _directive_count(text: str, name: str) -> int:
    return len(
        re.findall(
            r"^" + re.escape(F3) + r"\{" + re.escape(name) + r"\}",
            text,
            re.MULTILINE,
        )
    )


def fence_aware_topology(text: str) -> dict[str, Any]:
    return {
        "headings": _heading_count(text),
        "code_cells": len(core.code_cells(text)),
        "proof_directives": len(
            re.findall(r"^" + re.escape(F3) + r"\{prf:", text, re.MULTILINE)
        ),
        "source_figures": _directive_count(text, "figure"),
        "exercises": _directive_count(text, "exercise"),
        "solutions": _directive_count(text, "solution"),
        "labels": sorted(re.findall(r"^:label:\s*([^\s]+)", text, re.MULTILINE)),
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


def _role_keys(text: str, role: str) -> list[str]:
    return sorted(
        re.findall(
            r"\{"
            + re.escape(role)
            + r"\}"
            + re.escape(TICK)
            + r"([^"
            + re.escape(TICK)
            + r"]+)"
            + re.escape(TICK),
            text,
        )
    )


def _code_hashes(cells: list[dict[str, Any]]) -> list[str]:
    return [hashlib.sha256(cell["source"].encode("utf-8")).hexdigest() for cell in cells]


def _target_digest() -> str:
    return harness.sha256(harness.require_file(TARGET_SOURCE))


def validate_source(
    target_text: str,
    authority_text: str,
    authority_nb: dict[str, Any],
) -> tuple[str, dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    title, _ = core.frontmatter(target_text)
    if title != "Stasioneritas dan Ergodisitas":
        raise RuntimeError(f"unexpected translated title: {title!r}")
    if harness.sha256(target_text.encode("utf-8")) != TARGET_SHA:
        raise RuntimeError("ergodicity target requires an explicit hash rebind")

    target_cells = core.code_cells(target_text)
    authority_cells = core.code_cells(authority_text)
    if _code_hashes(target_cells) != EXPECTED_TARGET_CODE_SHA:
        raise RuntimeError("ergodicity translated code-cell identity differs")
    if _code_hashes(authority_cells) != EXPECTED_AUTHORITY_CODE_SHA:
        raise RuntimeError("ergodicity authority code-cell identity differs")
    expected_tags = [["hide-output"], [], [], ["hide-input"]]
    if [cell["tags"] for cell in target_cells] != expected_tags:
        raise RuntimeError("ergodicity target code-cell tags differ")
    if [cell["tags"] for cell in authority_cells] != expected_tags:
        raise RuntimeError("ergodicity authority code-cell tags differ")
    if re.search(r"!\[[^\]]*\]\(", target_text) or re.search(
        r"!\[[^\]]*\]\(", authority_text
    ):
        raise RuntimeError("unexpected Markdown image in ergodicity source")

    notebook_cells = authority_nb.get("cells", [])
    notebook_code = [cell for cell in notebook_cells if cell.get("cell_type") == "code"]
    notebook_code_hashes = [
        hashlib.sha256("".join(cell.get("source", [])).encode("utf-8")).hexdigest()
        for cell in notebook_code
    ]
    if (
        len(notebook_cells) != 44
        or len(notebook_code) != 4
        or sum(cell.get("cell_type") == "markdown" for cell in notebook_cells) != 40
        or sum(len(cell.get("outputs", [])) for cell in notebook_code) != 0
        or notebook_code_hashes != EXPECTED_NOTEBOOK_CODE_SHA
    ):
        raise RuntimeError("ergodicity notebook witness census or code identity differs")

    topology = fence_aware_topology(target_text)
    authority_topology = fence_aware_topology(authority_text)
    expected_target_counts = {
        "headings": 15,
        "code_cells": 4,
        "proof_directives": 14,
        "source_figures": 0,
        "exercises": 3,
        "solutions": 3,
    }
    expected_authority_counts = {**expected_target_counts, "headings": 13}
    for key, expected in expected_target_counts.items():
        if topology.get(key) != expected:
            raise RuntimeError(
                f"ergodicity target topology differs for {key}: {topology.get(key)}"
            )
    for key, expected in expected_authority_counts.items():
        if authority_topology.get(key) != expected:
            raise RuntimeError(
                "ergodicity authority topology differs for "
                f"{key}: {authority_topology.get(key)}"
            )
    if topology["labels"] != EXPECTED_LABELS or authority_topology["labels"] != EXPECTED_LABELS:
        raise RuntimeError("ergodicity directive-label identity differs")
    if topology["standalone_labels"] or authority_topology["standalone_labels"]:
        raise RuntimeError("unexpected standalone label in ergodicity source")
    if topology["equation_refs"] != EXPECTED_TARGET_EQUATION_REFS:
        raise RuntimeError("ergodicity target equation-reference identity differs")
    if authority_topology["equation_refs"] != EXPECTED_AUTHORITY_EQUATION_REFS:
        raise RuntimeError("ergodicity authority equation-reference identity differs")
    if _display_labels(target_text) != EXPECTED_EQUATION_LABELS:
        raise RuntimeError("ergodicity target display-equation label order differs")
    if _display_labels(authority_text) != EXPECTED_AUTHORITY_EQUATION_LABELS:
        raise RuntimeError("ergodicity display-equation label order differs")
    if (
        len(re.findall(r"\$\$.*?\$\$", target_text, re.DOTALL)) != 30
        or len(re.findall(r"\$\$.*?\$\$", authority_text, re.DOTALL)) != 22
    ):
        raise RuntimeError("ergodicity display-math census differs")

    if _role_keys(target_text, "ref") != ["meninjau kembali <solvode>"]:
        raise RuntimeError("translated ergodicity ref-role surface differs")
    if _role_keys(authority_text, "ref") != ["again <solvode>"]:
        raise RuntimeError("authority ergodicity ref-role surface differs")
    expected_target_proof_refs = [
        "ejc_algo",
        "equivirr",
        "equivirr",
        "perimposs",
        "sdrift",
        "sdrift",
        "sdrift",
        "sdrift",
        "sdrift",
        "sfinite",
        "stabskel",
        "statfromq",
        "strictcontract",
        "strictcontract",
        "uniirr",
    ]
    expected_authority_proof_refs = [
        "ejc_algo",
        "equivirr",
        "perimposs",
        "sdrift",
        "sdrift",
        "sdrift",
        "sdrift",
        "sdrift",
        "sfinite",
        "stabskel",
        "strictcontract",
        "strictcontract",
        "uniirr",
    ]
    if _role_keys(target_text, "prf:ref") != expected_target_proof_refs:
        raise RuntimeError("translated ergodicity proof-reference surface differs")
    if _role_keys(authority_text, "prf:ref") != expected_authority_proof_refs:
        raise RuntimeError("authority ergodicity proof-reference surface differs")
    expected_citations = sorted(EXPECTED_CITATIONS)
    if (
        _role_keys(target_text, "cite") != expected_citations
        or _role_keys(authority_text, "cite") != expected_citations
    ):
        raise RuntimeError("ergodicity citation-key surface differs")
    if _role_keys(target_text, "doc") or _role_keys(authority_text, "doc"):
        raise RuntimeError("unexpected doc role in ergodicity source")

    required_metadata = (
        "unit_id: unit.o009.quantecon.ctmc.stationarity-ergodicity",
        "source_path: lectures/ergodicity.md",
        "source_license: CC BY-SA 4.0",
        MODEL_PROVENANCE,
        "tidak didukung atau disahkan oleh QuantEcon maupun penulis sumber",
        "https://github.com/QuantEcon/continuous_time_mcs",
        "Thomas J. Sargent dan John Stachurski",
        "https://creativecommons.org/licenses/by-sa/4.0/",
    )
    if any(token not in target_text for token in required_metadata):
        raise RuntimeError("ergodicity metadata/provenance gate is incomplete")
    required_repairs = (
        "Koordinat besar diperbaiki menjadi",
        r"$D_t:=(P_t-I)/t$",
        "Jika $m=0$",
        "R:=I+Q/m",
        "setidaknya satu hasil kali positif",
        "suku $k=0$",
        r"setiap $f\in\ell_1$",
        "tumpang tindih positif",
        r"\|\psi P_1-\phi P_1\|",
        "Argumen komutasi dan",
        "syarat keterdefinisian",
        r"$M:=\lambda$",
        "koordinat-nol dan induksi",
        "mengizinkan",
    )
    missing_repairs = [token for token in required_repairs if token not in target_text]
    if missing_repairs:
        raise RuntimeError(
            f"required ergodicity mathematical repairs are missing: {missing_repairs}"
        )
    if "TTP" in target_text or "Translation and Transcription Project" in target_text:
        raise RuntimeError("forbidden umbrella metadata leaked into ergodicity")
    return title, topology, target_cells, []


def downstream_code(source: str) -> str:
    normalized = source.rstrip() + "\n"
    forbidden = ("!pip", "%pip", "pip install", "requests.", "urllib.")
    if any(token in normalized for token in forbidden):
        raise RuntimeError("network or runtime-install code leaked into ergodicity replay")
    return normalized


def _validate_execution(execution: list[dict[str, Any]]) -> None:
    if len(execution) != 4 or [row.get("index") for row in execution] != [1, 2, 3, 4]:
        raise RuntimeError("ergodicity execution census or order differs")
    for row in execution:
        if row.get("stdout") or row.get("stderr"):
            raise RuntimeError(f"ergodicity cell {row.get('index')} emitted text")
    if any(row.get("figures") for row in execution[:3]):
        raise RuntimeError("an early ergodicity cell unexpectedly emitted a figure")
    figures = execution[3].get("figures")
    if not isinstance(figures, list) or len(figures) != 1:
        raise RuntimeError("ergodicity plot cell did not emit exactly one figure")
    figure = figures[0]
    data = base64.b64decode(figure.get("data", ""), validate=True)
    if (
        figure.get("index") != 1
        or figure.get("bytes") != FIGURE_BYTES
        or figure.get("sha256") != FIGURE_SHA
        or len(data) != FIGURE_BYTES
        or hashlib.sha256(data).hexdigest() != FIGURE_SHA
        or not data.startswith(b"\x89PNG\r\n\x1a\n")
    ):
        raise RuntimeError("ergodicity deterministic figure bytes differ")


def execute_cells(
    cells: list[dict[str, Any]], interpreter: Path
) -> list[dict[str, Any]]:
    execution = ORIGINAL_EXECUTE(cells, interpreter)
    _validate_execution(execution)
    return execution


def directive_to_fenced(text: str) -> str:
    lines = core.normal_text(text).splitlines()
    output: list[str] = []
    stack: list[str] = []
    solution_number = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.match(r"^" + re.escape(F3) + r"\{code-cell\}\s*ipython3\s*$", line):
            try:
                close = next(position for position in range(index + 1, len(lines)) if lines[position] == F3)
            except StopIteration as exc:
                raise RuntimeError("unterminated ergodicity code cell") from exc
            output.extend(["", "<!-- O009_CODE_CELL -->", ""])
            index = close + 1
            continue

        proof = re.match(
            r"^"
            + re.escape(F3)
            + r"\{prf:(example|lemma|proof|theorem|corollary)\}(?:\s+(.*))?$",
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
            stack.append("directive")
            continue

        if line == F3 + "{note}":
            output.append("::: {.note}")
            stack.append("note")
            index += 1
            continue

        if line == F3 + "{exercise}":
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
            stack.append("exercise")
            continue

        solution = re.match(r"^" + re.escape(F3) + r"\{solution\}\s+([^\s]+)", line)
        if solution:
            solution_number += 1
            output.append(f"::: {{#{UNIT_SLUG}-solution-{solution_number} .solution}}")
            output.append("**Solusi**")
            stack.append("solution")
            index += 1
            while index < len(lines) and (
                lines[index].startswith(":") or not lines[index].strip()
            ):
                index += 1
            continue

        if line == F3:
            if not stack:
                raise RuntimeError("unexpected MyST closing fence in ergodicity")
            stack.pop()
            output.append(":::")
            index += 1
            continue

        output.append(line)
        index += 1
    if stack:
        raise RuntimeError(f"unterminated ergodicity MyST directives: {stack}")
    return "\n".join(output) + "\n"


def _split_role(raw: str) -> tuple[str, str]:
    match = re.fullmatch(r"(.*?)\s*<([^<>]+)>", raw, flags=re.DOTALL)
    if match:
        return " ".join(match.group(1).split()), match.group(2)
    return raw.strip(), raw.strip()


def _replace_roles(source: str) -> str:
    cross_equations = {
        "chapkol_ct2": "markov_prop.html#equation-chapkol_ct2",
        "kfromqxx": "uc_mc_semigroups.html#equation-kfromqxx",
        "kfromqxy": "uc_mc_semigroups.html#equation-kfromqxy",
        "lambdafromq": "uc_mc_semigroups.html#equation-lambdafromq",
    }

    def equation_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in cross_equations:
            return match.group(0)
        return f"[persamaan {key}]({cross_equations[key]})"

    source = re.sub(r"\{eq\}`([^`]+)`", equation_replacement, source)

    def reference_replacement(match: re.Match[str]) -> str:
        label, key = _split_role(match.group(1))
        if key != "solvode":
            raise RuntimeError(f"unmapped ergodicity ref role: {key}")
        return f"[{label}](kolmogorov_fwd.html#solvode)"

    source = re.sub(r"\{ref\}`([^`]+)`", reference_replacement, source)
    proof_targets = {
        "ejc_algo": ("algoritma rantai lompatan", "kolmogorov_bwd.html#ejc_algo"),
        "equivirr": ("teorema ekuivalensi ketercapaian", "#equivirr"),
        "perimposs": ("akibat kepositifan waktu kontinu", "#perimposs"),
        "sdrift": ("teorema kestabilan hanyutan", "#sdrift"),
        "sfinite": ("akibat ruang keadaan berhingga", "#sfinite"),
        "stabskel": ("lema rantai kerangka", "#stabskel"),
        "statfromq": ("teorema stasioneritas generator", "#statfromq"),
        "strictcontract": ("lema kontraktivitas ketat", "#strictcontract"),
        "uniirr": ("teorema ketunggalan", "#uniirr"),
    }

    def proof_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in proof_targets:
            raise RuntimeError(f"unmapped ergodicity proof role: {key}")
        label, target = proof_targets[key]
        return f"[{label}]({target})"

    source = re.sub(r"\{prf:ref\}`([^`]+)`", proof_replacement, source)

    def citation_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in EXPECTED_CITATIONS:
            raise RuntimeError(f"unmapped ergodicity citation: {key}")
        return f"<cite>{EXPECTED_CITATIONS[key]}</cite>"

    source = re.sub(r"\{cite\}`([^`]+)`", citation_replacement, source)
    if re.search(r"\{(?:doc|ref|prf:ref|cite)\}`", source):
        raise RuntimeError("unresolved non-equation MyST role in ergodicity")
    return source


def render_markdown(
    source: str,
    execution: list[dict[str, Any]],
    title: str,
    stage: Path,
) -> str:
    _validate_execution(execution)
    rendered = ORIGINAL_RENDER(_replace_roles(source), execution, title, stage)
    soup = BeautifulSoup(rendered, "lxml")

    for kind, selector in (
        ("proof", ".qe-proof"),
        ("example", ".qe-example"),
        ("note", ".note"),
    ):
        for number, node in enumerate(soup.select(selector), start=1):
            if not node.get("id"):
                node["id"] = f"{kind}-{number:03d}"

    figures = soup.select("figure.execution-figure")
    if len(figures) != 1:
        raise RuntimeError("ergodicity render did not contain exactly one figure")
    figure = figures[0]
    image = figure.find("img")
    caption = figure.find("figcaption")
    if image is None or caption is None:
        raise RuntimeError("ergodicity execution figure lacks image or caption")
    image["alt"] = FIGURE_ALT
    caption.string = FIGURE_ALT
    details = figure.find_parent("details")
    if details is not None:
        wrapper = soup.new_tag(
            "div",
            attrs={
                "class": "code-cell",
                "id": details.get("id"),
                "data-tags": details.get("data-tags", "hide-input"),
            },
        )
        details_classes = [
            name for name in details.get("class", []) if name != "code-cell"
        ]
        details["class"] = [*details_classes, "code-input"]
        details.attrs.pop("id", None)
        details.attrs.pop("data-tags", None)
        details.insert_before(wrapper)
        figure.extract()
        details.extract()
        wrapper.append(details)
        wrapper.append(figure)

    for index, summary in enumerate(
        soup.select("div.code-cell > details.code-input > summary"), start=1
    ):
        summary["aria-label"] = f"Tampilkan kode sel tersembunyi {index}"
        summary.string = f"Tampilkan kode sel tersembunyi {index}"

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
    raw = harness.require_file(path)
    text = raw.decode("utf-8")
    soup = BeautifulSoup(text, "lxml")
    if soup.html is None or soup.html.get("lang") != "id-ID":
        raise RuntimeError("ergodicity HTML lacks lang=id-ID")
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("ergodicity HTML must have exactly one h1 and one main")
    nav = soup.find("nav")
    if nav is None or not str(nav.get("aria-label", "")).strip():
        raise RuntimeError("ergodicity reader navigation lacks an accessible name")
    ids = [str(tag["id"]) for tag in soup.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate HTML id in ergodicity component")
    core.validate_equation_ids(ids)
    required = {
        *(f"equation-{label}" for label in EXPECTED_EQUATION_LABELS),
        *EXPECTED_LABELS,
        "ergodicity-solution-1",
        "ergodicity-solution-2",
        "ergodicity-solution-3",
        "proof-001",
        "proof-002",
        "proof-003",
        "proof-004",
        "example-001",
        "example-002",
        "note-001",
        "qe-cell-1",
        "qe-cell-2",
        "qe-cell-3",
        "qe-cell-4",
        "figure-ergodicity-cell-04-figure-01",
        "quantecon-attribution",
    }
    if not required.issubset(set(ids)):
        raise RuntimeError(f"missing ergodicity labels: {sorted(required - set(ids))}")
    classes = {name for tag in soup.find_all(True) for name in tag.get("class", [])}
    expected_classes = {
        "code-cell",
        "execution-figure",
        "exercise",
        "note",
        "solution",
        "qe-corollary",
        "qe-example",
        "qe-lemma",
        "qe-proof",
        "qe-theorem",
    }
    if not expected_classes.issubset(classes):
        raise RuntimeError(
            "ergodicity directive semantics are incomplete: "
            f"{sorted(expected_classes - classes)}"
        )
    semantic_nodes = soup.select(
        "h2, h3, h4, .exercise, .solution, .note, .qe-example, .qe-lemma, "
        ".qe-proof, .qe-theorem, .qe-corollary, .execution-figure"
    )
    if any(not node.get("id") for node in semantic_nodes):
        raise RuntimeError("ergodicity semantic node lacks a reader fragment")
    raw_tokens = (
        "O009_CODE_CELL",
        "O009_FIGURES_",
        "{doc}",
        "{ref}",
        "{prf:ref}",
        "{cite}",
        "{eq}",
        F3 + "{",
    )
    if any(token in text for token in raw_tokens):
        raise RuntimeError("raw MyST role or directive leaked into ergodicity HTML")
    if len(soup.select(".code-cell")) != 4 or len(soup.select(".execution-figure")) != 1:
        raise RuntimeError("ergodicity rendered code/figure census differs")
    if len(soup.select("div.code-cell > details.code-input")) != 1:
        raise RuntimeError("ergodicity hidden-input code surface differs")
    figure = soup.select_one("figure.execution-figure")
    image = figure.find("img") if figure else None
    caption = figure.find("figcaption") if figure else None
    if (
        figure is None
        or figure.find_parent("details") is not None
        or figure.find_parent(class_="code-cell") is None
        or image is None
        or image.get("src") != "../assets/ergodicity-cell-04-figure-01.png"
        or image.get("alt") != FIGURE_ALT
        or caption is None
        or caption.get_text(" ", strip=True) != FIGURE_ALT
    ):
        raise RuntimeError("ergodicity accessible execution-figure surface differs")
    if MODEL_PROVENANCE not in text:
        raise RuntimeError("exact model provenance missing from ergodicity HTML")
    rendered_code = "\n".join(
        node.get_text("\n", strip=False)
        for node in soup.select(".code-cell code[data-cell-index]")
    )
    if (
        "pip install" in rendered_code
        or "import scipy as sp" in rendered_code
        or "from numba import njit" in rendered_code
    ):
        raise RuntimeError("removed runtime installation or unused import leaked into HTML")
    observed_citations = sorted(
        re.sub(r"\s+", " ", cite.get_text(" ", strip=True)).strip()
        for cite in soup.select("main cite")
    )
    if observed_citations != sorted(EXPECTED_CITATIONS.values()):
        raise RuntimeError("resolved ergodicity bibliography surface differs")
    attribution = soup.select_one("#quantecon-attribution")
    attribution_text = attribution.get_text(" ", strip=True) if attribution else ""
    if "CC BY-SA 4.0" not in attribution_text or "QuantEcon tidak mengesahkan" not in attribution_text:
        raise RuntimeError("ergodicity attribution/license/non-endorsement differs")

    for tag in soup.select("script[src], link[href]"):
        ref = str(tag.get("src") or tag.get("href") or "")
        if ref.startswith(("http:", "https:", "//")):
            raise RuntimeError(f"external runtime asset leaked: {ref}")
    root = root or path.parent.parent
    id_set = set(ids)
    observed_cross: set[str] = set()
    for tag in soup.select("a[href], img[src], script[src], link[href]"):
        ref = str(tag.get("href") or tag.get("src") or "")
        if not ref:
            continue
        if ref.startswith("#"):
            if ref[1:] not in id_set:
                raise RuntimeError(f"broken same-page ergodicity fragment: {ref}")
            continue
        if ref.startswith(("http:", "https:", "mailto:")):
            continue
        if ref == "../../index.html":
            continue
        if ref in EXPECTED_CROSS_UNIT_LINKS:
            observed_cross.add(ref)
            continue
        target = (path.parent / ref.split("#", 1)[0]).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise RuntimeError(f"reference escapes ergodicity component: {ref}") from exc
        if not target.is_file():
            raise RuntimeError(f"local ergodicity component reference missing: {ref}")
    if observed_cross != EXPECTED_CROSS_UNIT_LINKS:
        raise RuntimeError(
            "ergodicity cross-unit dependency set differs: "
            f"{sorted(observed_cross)}"
        )
    _validate_privacy_text(text, "lectures/ergodicity.html")


def correction_records(
    _formula_corrections: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "id": "ergodicity-offline-runtime-surface",
            "description": (
                "Removed the runtime package installation and unused imports while "
                "preserving all four source code-cell positions and executable logic."
            ),
        },
        {
            "id": "ergodicity-simplex-seed-normalization",
            "description": (
                "Corrected each plotted initial vector from total mass 1.01 to one by "
                "changing its dominant coordinate from 0.99 to 0.98."
            ),
        },
        {
            "id": "ergodicity-accessible-figure",
            "description": (
                "Added a mathematical text alternative and exposed the deterministic "
                "figure outside the collapsed hide-input code control."
            ),
        },
        {
            "id": "ergodicity-irreducibility-uniformization-proof",
            "description": (
                "Replaced the invalid cancellation-prone Q-power argument and reversed "
                "accessibility premise with a nonnegative uniformization proof, including "
                "the zero-rate and diagonal cases."
            ),
        },
        {
            "id": "ergodicity-l1-contractivity-domain",
            "description": (
                "Stated and proved Markov contraction for all signed ell_1 vectors before "
                "applying it to differences of distributions."
            ),
        },
        {
            "id": "ergodicity-strict-contractivity-proof",
            "description": (
                "Completed the strict contraction argument through positive/negative "
                "parts and overlap of their everywhere-positive images."
            ),
        },
        {
            "id": "ergodicity-uniqueness-operator-notation",
            "description": (
                "Replaced the undefined P in the uniqueness contradiction with the "
                "everywhere-positive operator P_1."
            ),
        },
        {
            "id": "ergodicity-skeleton-stationarity-closure",
            "description": (
                "Proved that the skeleton stationary law is stationary for every P_h "
                "before using that identity in the full-time convergence argument."
            ),
        },
        {
            "id": "ergodicity-drift-domain-and-piecewise-scope",
            "description": (
                "Corrected the piecewise drift condition and added the summability/domain "
                "qualification needed when the Lyapunov function is unbounded."
            ),
        },
        {
            "id": "ergodicity-mm1-drift-bound",
            "description": (
                "Corrected the M/M/1 finite-set drift bound to M=lambda>0, required "
                "0<lambda<mu, and retained epsilon=mu-lambda."
            ),
        },
        {
            "id": "ergodicity-accessibility-time-convention",
            "description": (
                "Made explicit that the exercise answer uses the unit's t>=0 definition "
                "of accessibility and does not automatically cover a positive-time convention."
            ),
        },
        {
            "id": "ergodicity-pure-birth-induction",
            "description": (
                "Replaced division by a potentially zero stationary coordinate with the "
                "coordinate-zero equation and a valid induction proving every coordinate zero."
            ),
        },
        {
            "id": "ergodicity-myst-references-and-citations",
            "description": (
                "Resolved every admitted equation, cross-unit, proof, and bibliography "
                "role into stable local links or complete human-readable citations."
            ),
        },
        {
            "id": "ergodicity-deterministic-executable-replay",
            "description": (
                "Replayed all four code cells twice under the pinned offline runtime and "
                "bound the sole generated PNG by byte count and SHA-256."
            ),
        },
        {
            "id": "quantecon-branding-runtime",
            "description": (
                "Removed remote runtime and branding while preserving authorship, "
                "CC BY-SA 4.0, exact model provenance, and non-endorsement."
            ),
        },
    ]


def _closure_record() -> dict[str, Any]:
    return {
        "authoring_format": "MyST Markdown with paired Jupyter notebook witness",
        "authority_markdown_bytes": 18_548,
        "authority_markdown_sha256": AUTH_SOURCE_SHA,
        "authority_notebook_bytes": 30_306,
        "authority_notebook_sha256": AUTH_NOTEBOOK_SHA,
        "authority_notebook_cells": 44,
        "authority_code_cells": 4,
        "authority_notebook_code_source_sha256": EXPECTED_NOTEBOOK_CODE_SHA,
        "target_markdown_bytes": 27_023,
        "target_markdown_sha256": TARGET_SHA,
        "target_code_cells": 4,
        "target_code_source_sha256": EXPECTED_TARGET_CODE_SHA,
        "unit_source_assets": 0,
        "unit_generated_media": 1,
        "generated_media": [
            {
                "path": "assets/ergodicity-cell-04-figure-01.png",
                "bytes": FIGURE_BYTES,
                "sha256": FIGURE_SHA,
            }
        ],
        "local_runtime_assets": [
            {"path": "MathJax/tex-svg.js", "sha256": MATHJAX_SHA},
            {"path": "reader.css", "sha256": CSS_SHA},
        ],
        "cross_unit_dependencies": sorted(EXPECTED_CROSS_UNIT_LINKS),
        "citation_keys": sorted(EXPECTED_CITATIONS),
        "citation_occurrences": 3,
        "model_provenance": MODEL_PROVENANCE,
        "license": "CC BY-SA 4.0",
        "non_endorsement": True,
    }


def _validate_privacy_text(text: str, label: str) -> None:
    forbidden_literals = (
        "C:\\Users\\",
        "C:/Users/",
        "file://",
        "github_pat_",
        "ghp_",
        "Bearer ",
        "Authorization:",
    )
    if any(marker.casefold() in text.casefold() for marker in forbidden_literals):
        raise RuntimeError(f"private path or credential-shaped text leaked into {label}")


def _validate_component_privacy(root: Path) -> None:
    expected_files = {
        "COMPONENT_MANIFEST.tsv",
        "COMPONENT_RECEIPT.json",
        "MathJax/tex-svg.js",
        "assets/ergodicity-cell-04-figure-01.png",
        "lectures/ergodicity.html",
        "notebooks/ergodicity-authority.ipynb",
        "notebooks/ergodicity-executed.ipynb",
        "reader.css",
        "source-ergodicity.md",
    }
    actual_files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }
    if actual_files != expected_files:
        raise RuntimeError(
            "ergodicity on-disk component closure differs: "
            f"{sorted(actual_files ^ expected_files)}"
        )
    for relative in sorted(expected_files - {"assets/ergodicity-cell-04-figure-01.png"}):
        path = root / relative
        if path.is_symlink():
            raise RuntimeError(f"linked file in ergodicity component: {relative}")
        _validate_privacy_text(harness.require_file(path).decode("utf-8"), relative)
    image = harness.require_file(root / "assets" / "ergodicity-cell-04-figure-01.png")
    if not image.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("ergodicity generated asset is not a PNG")


def _validate_static_inputs() -> None:
    if harness.sha256(harness.require_file(harness.MATHJAX)) != MATHJAX_SHA:
        raise RuntimeError("local MathJax bytes require an explicit hash rebind")
    if harness.sha256(harness.require_file(harness.CSS)) != CSS_SHA:
        raise RuntimeError("shared reader CSS requires an explicit hash rebind")


def _validate_numerical_qa() -> None:
    if harness.sha256(harness.require_file(NUMERICAL_QA)) != NUMERICAL_QA_SHA:
        raise RuntimeError("ergodicity numerical QA requires a hash rebind")
    receipt = harness.load_json(NUMERICAL_QA)
    if (
        receipt.get("status") != "pass"
        or receipt.get("authority", {}).get("sha256") != AUTH_SOURCE_SHA
        or receipt.get("target", {}).get("sha256") != TARGET_SHA
    ):
        raise RuntimeError("ergodicity numerical QA binding differs")


def _validate_receipt() -> None:
    receipt = harness.load_json(OUT_RECEIPT)
    if receipt.get("schema") != harness.COMPONENT_SCHEMA or receipt.get("unit_id") != UNIT_ID:
        raise RuntimeError("ergodicity component receipt identity differs")
    if receipt.get("target") != {
        "path": TARGET_REL,
        "sha256": TARGET_SHA,
        "title": "Stasioneritas dan Ergodisitas",
    }:
        raise RuntimeError("ergodicity receipt target binding differs")
    authority = receipt.get("authority", {})
    if (
        authority.get("source_sha256") != AUTH_SOURCE_SHA
        or authority.get("notebook_sha256") != AUTH_NOTEBOOK_SHA
    ):
        raise RuntimeError("ergodicity receipt authority binding differs")
    if receipt.get("replay_match") is not True:
        raise RuntimeError("ergodicity deterministic replay receipt differs")
    if receipt.get("corrections") != correction_records([]):
        raise RuntimeError("ergodicity correction ledger differs")
    if receipt.get("unit_closure") != _closure_record():
        raise RuntimeError("ergodicity unit-closure receipt differs")
    if receipt.get("numerical_qa") != {
        "path": "qa/QUANTECON_ERGODICITY_NUMERICAL_QA.json",
        "status": "pass",
        "sha256": NUMERICAL_QA_SHA,
    }:
        raise RuntimeError("ergodicity numerical QA receipt binding differs")
    if receipt.get("manifest_sha256") != harness.sha256(harness.require_file(OUT_MANIFEST)):
        raise RuntimeError("ergodicity receipt manifest hash differs")

    code_cells = receipt.get("code_cells")
    if not isinstance(code_cells, list) or len(code_cells) != 4:
        raise RuntimeError("ergodicity receipt code-cell census differs")
    for index, (row, expected_sha) in enumerate(
        zip(code_cells, EXPECTED_TARGET_CODE_SHA), start=1
    ):
        if (
            row.get("index") != index
            or row.get("source_sha256") != expected_sha
            or row.get("execution_source_sha256") != expected_sha
            or row.get("replay", {}).get("index") != index
            or row.get("replay", {}).get("stdout") != ""
            or row.get("replay", {}).get("stderr") != ""
        ):
            raise RuntimeError(f"ergodicity receipt replay binding differs for cell {index}")
        expected_figures: list[dict[str, Any]] = []
        if index == 4:
            expected_figures = [
                {"bytes": FIGURE_BYTES, "index": 1, "sha256": FIGURE_SHA}
            ]
        if row.get("replay", {}).get("figures") != expected_figures:
            raise RuntimeError(f"ergodicity receipt figure surface differs for cell {index}")

    files = receipt.get("files")
    if not isinstance(files, list) or not all(isinstance(row, dict) for row in files):
        raise RuntimeError("ergodicity receipt file inventory is malformed")
    by_path = {str(row.get("path")): row for row in files}
    expected_paths = {
        "MathJax/tex-svg.js",
        "assets/ergodicity-cell-04-figure-01.png",
        "lectures/ergodicity.html",
        "notebooks/ergodicity-authority.ipynb",
        "notebooks/ergodicity-executed.ipynb",
        "reader.css",
        "source-ergodicity.md",
    }
    if set(by_path) != expected_paths or receipt.get("file_count") != len(expected_paths):
        raise RuntimeError("ergodicity component file closure differs")
    if receipt.get("total_bytes") != sum(int(row.get("bytes", 0)) for row in files):
        raise RuntimeError("ergodicity component byte total differs")
    exact_hashes = {
        "MathJax/tex-svg.js": MATHJAX_SHA,
        "assets/ergodicity-cell-04-figure-01.png": FIGURE_SHA,
        "notebooks/ergodicity-authority.ipynb": AUTH_NOTEBOOK_SHA,
        "reader.css": CSS_SHA,
        "source-ergodicity.md": TARGET_SHA,
    }
    for relative, expected_sha in exact_hashes.items():
        if by_path[relative].get("sha256") != expected_sha:
            raise RuntimeError(f"ergodicity component hash differs: {relative}")
    if by_path["assets/ergodicity-cell-04-figure-01.png"].get("bytes") != FIGURE_BYTES:
        raise RuntimeError("ergodicity component figure byte count differs")

    executed = harness.load_json(OUT_NOTEBOOK)
    executed_cells = executed.get("cells")
    if (
        executed.get("nbformat") != 4
        or not isinstance(executed_cells, list)
        or len(executed_cells) != 4
    ):
        raise RuntimeError("ergodicity executed-notebook census differs")
    for index, (cell, expected_sha) in enumerate(
        zip(executed_cells, EXPECTED_TARGET_CODE_SHA), start=1
    ):
        if (
            cell.get("cell_type") != "code"
            or cell.get("execution_count") != index
            or cell.get("outputs") != []
            or cell.get("metadata", {}).get("source_cell_index") != index
            or hashlib.sha256(cell.get("source", "").encode("utf-8")).hexdigest()
            != expected_sha
        ):
            raise RuntimeError(f"ergodicity executed-notebook cell {index} differs")


def build() -> None:
    if _target_digest() != TARGET_SHA:
        raise RuntimeError("ergodicity target requires an explicit hash rebind")
    _validate_static_inputs()
    _validate_numerical_qa()
    ORIGINAL_BUILD()
    if _target_digest() != TARGET_SHA:
        raise RuntimeError("ergodicity target changed during component build")
    receipt = harness.load_json(OUT_RECEIPT)
    receipt["unit_closure"] = _closure_record()
    receipt["numerical_qa"] = {
        "path": "qa/QUANTECON_ERGODICITY_NUMERICAL_QA.json",
        "status": "pass",
        "sha256": NUMERICAL_QA_SHA,
    }
    OUT_RECEIPT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    validate_rendered(OUT_HTML)
    _validate_receipt()
    _validate_component_privacy(OUT_ROOT)
    print(
        f"PASS augmented unit={UNIT_ID} files={receipt['file_count']} "
        f"bytes={receipt['total_bytes']} "
        f"html_sha256={harness.sha256(harness.require_file(OUT_HTML))} "
        f"receipt_sha256={harness.sha256(harness.require_file(OUT_RECEIPT))}"
    )


def check() -> None:
    if _target_digest() != TARGET_SHA:
        raise RuntimeError("ergodicity target requires an explicit hash rebind")
    if harness.sha256(harness.require_file(AUTH_SOURCE)) != AUTH_SOURCE_SHA:
        raise RuntimeError("frozen ergodicity authority source hash differs")
    if harness.sha256(harness.require_file(AUTH_NOTEBOOK)) != AUTH_NOTEBOOK_SHA:
        raise RuntimeError("frozen ergodicity notebook witness hash differs")
    _validate_static_inputs()
    _validate_numerical_qa()
    ORIGINAL_CHECK()
    _validate_receipt()
    _validate_component_privacy(OUT_ROOT)


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
