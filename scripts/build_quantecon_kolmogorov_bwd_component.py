#!/usr/bin/env python3
"""Build and verify the isolated Indonesian Kolmogorov-backward unit."""

from __future__ import annotations

import csv
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
SNAPSHOT = AUTH_ROOT / "source_snapshot" / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
NOTEBOOK_SNAPSHOT = AUTH_ROOT / "notebook_snapshot" / "continuous_time_mcs.notebooks-1e17c25c937f369544380f769eb9c1bc45d12d1a"
AUTH_SOURCE = SNAPSHOT / "lectures" / "kolmogorov_bwd.md"
AUTH_NOTEBOOK = NOTEBOOK_SNAPSHOT / "kolmogorov_bwd.ipynb"
TARGET_SOURCE = ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_bwd.md"
NUMERICAL_QA = ROOT / "qa" / "QUANTECON_KOLMOGOROV_BWD_NUMERICAL_QA.json"
OUT_ROOT = ROOT / "build" / "components" / "quantecon_kolmogorov_bwd"
OUT_HTML = OUT_ROOT / "lectures" / "kolmogorov_bwd.html"
OUT_NOTEBOOK = OUT_ROOT / "notebooks" / "kolmogorov_bwd-executed.ipynb"
OUT_MANIFEST = OUT_ROOT / "COMPONENT_MANIFEST.tsv"
OUT_RECEIPT = OUT_ROOT / "COMPONENT_RECEIPT.json"

UNIT_ID = "unit.o009.quantecon.ctmc.kolmogorov-backward"
UNIT_SLUG = "kolmogorov_bwd"
TARGET_REL = "source/quantecon/lectures/kolmogorov_bwd.md"
AUTH_SOURCE_SHA = "ea2ada6e9eabe30fb2088d3e218076b4f949662649e2aef4b30c2cd59d090149"
AUTH_NOTEBOOK_SHA = "67ca8e73f7fe2e579d2cc3d21e9e232d49ff66d1a2c29b76881fd3bd84c47db2"
TARGET_SHA = "da75cf5a8d92f9bab26df63232be8817913e5d77238b661cc12f230fe7c695ca"
TICK = chr(96)
F3 = TICK * 3
F4 = TICK * 4

ORIGINAL_RENDER = harness.render_markdown
ORIGINAL_EXECUTE = harness.execute_cells


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
    return len(re.findall(r"^(?:" + prefix + r")\{" + re.escape(name) + r"\}", text, re.MULTILINE))


def _heading_count(text: str) -> int:
    lines = core.normal_text(text).splitlines()
    count = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(F3 + "{code-cell}") or line == F3 + "ipython3":
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
        "proof_directives": len(re.findall(r"^" + re.escape(F3) + r"\{prf:", text, re.MULTILINE)),
        "exercises": _directive_count(text, "exercise"),
        "solutions": (
            _directive_count(text, "solution")
            + _directive_count(text, "solution-start")
        ),
        "labels": sorted(re.findall(r"^:label:\s*([^\s]+)", text, re.MULTILINE)),
        "standalone_labels": sorted(re.findall(r"^\(([^)]+)\)=\s*$", text, re.MULTILINE)),
        "equation_refs": sorted(set(re.findall(r"\{eq\}" + re.escape(TICK) + r"([^" + re.escape(TICK) + r"]+)" + re.escape(TICK), text))),
    }


def _display_labels(text: str) -> list[str]:
    return re.findall(r"\$\$\s*\(([A-Za-z0-9_.:-]+)\)\s*$", text, re.MULTILINE)


def validate_source(
    target_text: str,
    authority_text: str,
    authority_nb: dict[str, Any],
) -> tuple[str, dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    title, _ = core.frontmatter(target_text)
    if title != "Persamaan Kolmogorov Mundur":
        raise RuntimeError(f"unexpected translated title: {title!r}")
    if harness.sha256(target_text.encode("utf-8")) != TARGET_SHA:
        raise RuntimeError("Kolmogorov-backward target hash differs")

    target_cells = core.code_cells(target_text)
    authority_cells = core.code_cells(authority_text)
    if len(target_cells) != 6 or len(authority_cells) != 6:
        raise RuntimeError(
            f"code-cell census differs: target={len(target_cells)} authority={len(authority_cells)}"
        )
    if (
        len(authority_nb.get("cells", [])) != 42
        or sum(cell.get("cell_type") == "code" for cell in authority_nb["cells"]) != 7
    ):
        raise RuntimeError("notebook witness does not have the admitted 42/7 cell census")

    topology = fence_aware_topology(target_text)
    authority_topology = fence_aware_topology(authority_text)
    for key, expected in {
        "headings": 14,
        "code_cells": 6,
        "proof_directives": 6,
        "exercises": 3,
        "solutions": 3,
    }.items():
        if int(topology.get(key, -1)) != expected:
            raise RuntimeError(f"target fence-aware topology differs for {key}: {topology}")
        if int(authority_topology.get(key, -1)) != expected:
            raise RuntimeError(f"authority fence-aware topology differs for {key}: {authority_topology}")
    for key in ("labels", "standalone_labels", "equation_refs"):
        if topology[key] != authority_topology[key]:
            raise RuntimeError(f"source identity topology differs for {key}")

    authority_displays = re.findall(r"\$\$.*?\$\$", authority_text, flags=re.DOTALL)
    target_displays = re.findall(r"\$\$.*?\$\$", target_text, flags=re.DOTALL)
    if len(authority_displays) != 21 or len(target_displays) != 21:
        raise RuntimeError(
            f"display-math census differs: target={len(target_displays)} authority={len(authority_displays)}"
        )
    if _display_labels(target_text) != _display_labels(authority_text):
        raise RuntimeError("display equation-label order differs")

    required = {
        "sdji", "jumpchainalgo", "ejc_algo", "kbinteg", "pt_split",
        "pt_first", "kolbackeq", "expsol", "expofun", "expoderiv",
        "psolq", "jctosg", "zrsnec", "gdiff", "kbinteg2",
        "kolmogorov-bwd-1", "kolmogorov-bwd-2", "kolmogorov-bwd-3",
    }
    if any(token not in target_text for token in required):
        raise RuntimeError("target lost a required source label or anchor")
    if "OpenAI Codex gpt-5.6-sol, Ultra." not in target_text:
        raise RuntimeError("exact model provenance is missing")
    if "TTP" in target_text or "Translation and Transcription Project" in target_text:
        raise RuntimeError("forbidden umbrella label leaked into the unit")
    if "persamaan mundur kolmogorov" in target_text.casefold():
        raise RuntimeError("terminology regression in backward-equation word order")
    if "ketunggalan" in target_text.casefold():
        raise RuntimeError("QuantEcon uniqueness terminology regressed")

    joined_code = "\n".join(cell["source"] for cell in target_cells)
    forbidden_code = (
        "pip install", "import scipy as sp", "import quantecon as qe",
        "np.random.binomial(b+1", "binom.pmf(states, n, 0.25)",
    )
    if any(token in joined_code for token in forbidden_code):
        raise RuntimeError("forbidden source/runtime code survived in the target")
    required_code = (
        "np.random.seed(seed)",
        "np.random.binomial(b, 0.25)",
        "raise RuntimeError",
        "binom.pmf(states, b, 0.25)",
        "T = 30",
        "n = b + 1",
        "states = np.arange(n)",
        'seed=20260824',
    )
    if any(token not in joined_code for token in required_code):
        raise RuntimeError("a required deterministic inventory correction is missing")
    required_prose = (
        "Jika $m=0$",
        "untuk setiap bilangan bulat $k\\geq1$",
        "$\\hat P'_t=Q\\hat P_t$",
        "untuk $0\\leq s\\leq t$",
        "Jika $W_k=+\\infty$, hentikan algoritma",
    )
    if any(token not in target_text for token in required_prose):
        raise RuntimeError("a required mathematical correction is missing")

    numerical = json.loads(harness.require_file(NUMERICAL_QA).decode("utf-8"))
    if numerical.get("status") != "pass":
        raise RuntimeError("numerical QA has not passed")
    if numerical.get("target", {}).get("sha256") != TARGET_SHA:
        raise RuntimeError("numerical QA does not bind the current target")
    checks = numerical.get("checks", {})
    if not checks.get("double_replay_exact") or not checks.get("simulation_double_draw_exact"):
        raise RuntimeError("numerical QA lacks exact double-replay evidence")
    if not checks.get("max_iter_zero_raises_runtime_error"):
        raise RuntimeError("numerical QA lacks the explicit max-iteration failure")
    if float(checks.get("simulation_empirical_max_error", 1.0)) >= 0.01:
        raise RuntimeError("numerical QA empirical tolerance failed")

    return title, topology, target_cells, []


def downstream_code(source: str) -> str:
    return source.rstrip() + "\n"


def execute_cells(
    cells: list[dict[str, Any]], interpreter: Path
) -> list[dict[str, Any]]:
    results = ORIGINAL_EXECUTE(cells, interpreter)
    expected_figures = {
        5: "1e4b89eaa4d6c5c6a0cc0c43713ccabef998f903bbb862b8b4b5d189a2b0e1a8",
        6: "7d57c9f3687133e6082f3206649c93a2061b3d5d84533a534b820e5fe963347a",
    }
    actual_figures: dict[int, str] = {}
    for result in results:
        if result["stderr"]:
            raise RuntimeError(f"unexpected execution stderr in cell {result['index']}")
        if result["figures"]:
            if len(result["figures"]) != 1:
                raise RuntimeError(f"unexpected figure count in cell {result['index']}")
            actual_figures[int(result["index"])] = str(result["figures"][0]["sha256"])
    if actual_figures != expected_figures:
        raise RuntimeError(
            f"deterministic execution figures differ: {actual_figures}"
        )
    for index in (5, 6):
        rows = [line for line in str(results[index - 1]["stdout"]).splitlines() if line]
        if len(rows) != 12:
            raise RuntimeError(f"numeric figure-data row count differs in cell {index}")
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

        proof = re.match(
            r"^" + re.escape(F3) + r"\{prf:(theorem|proof|lemma|algorithm)\}(?:\s+(.*))?$",
            line,
        )
        if proof:
            kind, caption = proof.group(1), (proof.group(2) or "").strip()
            index += 1
            label = None
            while index < len(lines) and (lines[index].startswith(":") or not lines[index].strip()):
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
            while index < len(lines) and (lines[index].startswith(":") or not lines[index].strip()):
                if lines[index].startswith(":label:"):
                    label = lines[index].split(":", 2)[-1].strip()
                index += 1
            attrs = f"#{label} " if label else ""
            output.append(f"::: {{{attrs}.exercise}}")
            stack.append(("exercise", closing))
            continue

        solution = re.match(r"^" + re.escape(F3) + r"\{solution\}\s+([^\s]+)", line)
        solution_start = re.match(
            r"^" + re.escape(F3) + r"\{solution-start\}\s+([^\s]+)", line
        )
        if solution or solution_start:
            solution_number += 1
            output.append(f"::: {{#{UNIT_SLUG}-solution-{solution_number} .solution}}")
            output.append("**Solusi**")
            stack.append(("solution", F3))
            index += 1
            while index < len(lines) and (lines[index].startswith(":") or not lines[index].strip()):
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


def _replace_roles(source: str) -> str:
    tick = re.escape(TICK)

    def link_doc(match: re.Match[str]) -> str:
        label = " ".join(match.group(1).split())
        return f"[{label}](markov_prop.html)"

    source = re.sub(
        r"\{doc\}" + tick + r"([^" + tick + r"]*?)\s*<markov_prop>" + tick,
        link_doc,
        source,
        flags=re.DOTALL,
    )

    def link_ref(match: re.Match[str]) -> str:
        label = " ".join(match.group(1).split())
        anchor = match.group(2)
        return f"[{label}](markov_prop.html#{anchor})"

    source = re.sub(
        r"\{ref\}" + tick + r"([^" + tick + r"]*?)\s*<(inventory_dynam|consjumptransemi)>" + tick,
        link_ref,
        source,
        flags=re.DOTALL,
    )
    source = source.replace(
        "{prf:ref}" + TICK + "ejc_algo" + TICK,
        "[algoritma rantai lompatan](#ejc_algo)",
    )
    source = source.replace(
        "{cite}" + TICK + "stroock2013introduction" + TICK,
        "<cite>Stroock (2013)</cite>",
    )
    return source


def _insert_data_table(
    soup: BeautifulSoup,
    figure: Any,
    stdout: str,
    table_id: str,
    caption: str,
) -> None:
    rows = [line.strip().split(",") for line in stdout.splitlines() if line.strip()]
    if len(rows) != 12 or any(len(row) != 2 for row in rows):
        raise RuntimeError(f"unexpected accessible figure data for {table_id}")
    table = soup.new_tag("table", id=table_id, attrs={"class": "execution-data"})
    table["aria-label"] = caption
    thead = soup.new_tag("thead")
    header_row = soup.new_tag("tr")
    for value in rows[0]:
        cell = soup.new_tag("th")
        cell.string = value.replace("_", " ")
        header_row.append(cell)
    thead.append(header_row)
    tbody = soup.new_tag("tbody")
    for source_row in rows[1:]:
        row = soup.new_tag("tr")
        for value in source_row:
            cell = soup.new_tag("td")
            cell.string = value
            row.append(cell)
        tbody.append(row)
    table.append(thead)
    table.append(tbody)
    figure.insert_after(table)


def render_markdown(
    source: str,
    execution: list[dict[str, Any]],
    title: str,
    stage: Path,
) -> str:
    prepared = _replace_roles(source)
    rendered = ORIGINAL_RENDER(prepared, execution, title, stage)
    soup = BeautifulSoup(rendered, "lxml")
    alternatives = {
        5: "Diagram batang probabilitas empiris persediaan pada waktu 30 untuk keadaan 0 sampai 10.",
        6: "Diagram batang probabilitas eksak persediaan pada waktu 30 untuk keadaan 0 sampai 10.",
    }
    results = {int(item["index"]): item for item in execution}
    seen: set[int] = set()
    for image in soup.find_all("img"):
        match = re.search(r"kolmogorov_bwd-cell-(\d+)-", str(image.get("src", "")))
        if not match:
            continue
        cell_index = int(match.group(1))
        alt = alternatives.get(cell_index)
        if alt is None:
            raise RuntimeError(f"unexpected generated figure cell: {cell_index}")
        image["alt"] = alt
        figure = image.find_parent("figure")
        if figure is None:
            raise RuntimeError("execution image has no figure ancestor")
        caption = figure.find("figcaption")
        if caption is None:
            caption = soup.new_tag("figcaption")
            figure.append(caption)
        caption.string = alt
        if cell_index not in seen:
            _insert_data_table(
                soup,
                figure,
                str(results[cell_index]["stdout"]),
                f"kolmogorov-bwd-data-{cell_index}",
                f"Data numerik untuk gambar sel {cell_index}",
            )
            seen.add(cell_index)
    if seen != {5, 6}:
        raise RuntimeError(f"generated figure set differs: {sorted(seen)}")

    for index, summary in enumerate(soup.find_all("summary"), start=1):
        label = f"Tampilkan kode sel {index}"
        summary["aria-label"] = label
        summary.string = label
    attribution = soup.select_one("#quantecon-attribution")
    if attribution is None:
        raise RuntimeError("QuantEcon attribution panel is missing")
    provenance = soup.new_tag("p", attrs={"class": "model-provenance"})
    provenance.string = (
        "Provenans produksi: OpenAI Codex gpt-5.6-sol, Ultra. "
        "Kredit penulis dan kontributor manusia tetap dipertahankan."
    )
    attribution.append(provenance)
    return "<!DOCTYPE html>\n" + str(soup)


def validate_rendered(path: Path, root: Path | None = None) -> None:
    soup = BeautifulSoup(harness.require_file(path).decode("utf-8"), "lxml")
    if soup.html is None or soup.html.get("lang") != "id-ID":
        raise RuntimeError("backward-equation HTML lacks lang=id-ID")
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("backward-equation HTML must have exactly one h1 and one main")
    ids = [str(tag["id"]) for tag in soup.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate HTML id in backward-equation component")
    core.validate_equation_ids(ids)
    required = {
        "sdji", "jumpchainalgo", "ejc_algo", "equation-kbinteg",
        "equation-pt_split", "equation-pt_first", "equation-kolbackeq",
        "equation-expsol", "equation-expofun", "equation-expoderiv",
        "equation-psolq", "jctosg", "equation-zrsnec", "equation-gdiff",
        "equation-kbinteg2", "kolmogorov-bwd-1", "kolmogorov-bwd-2",
        "kolmogorov-bwd-3", "kolmogorov_bwd-solution-1",
        "kolmogorov_bwd-solution-2", "kolmogorov_bwd-solution-3",
        "kolmogorov-bwd-data-5", "kolmogorov-bwd-data-6",
    }
    if not required.issubset(set(ids)):
        raise RuntimeError(f"missing backward-equation labels: {sorted(required - set(ids))}")
    classes = {name for tag in soup.find_all(True) for name in tag.get("class", [])}
    expected_classes = {"exercise", "solution", "qe-theorem", "qe-lemma", "qe-proof", "qe-algorithm"}
    if not expected_classes.issubset(classes):
        raise RuntimeError(f"directive semantics are incomplete: {sorted(expected_classes - classes)}")
    text = str(soup)
    if any(token in text for token in ("O009_FIGURES_", "{doc}", "{ref}", "{prf:ref}", "{cite}", F3 + "{")):
        raise RuntimeError("raw MyST or figure placeholder leaked into HTML")
    if "OpenAI Codex gpt-5.6-sol, Ultra." not in text:
        raise RuntimeError("exact model provenance missing from rendered HTML")
    if len(soup.select("figure.execution-figure")) != 2:
        raise RuntimeError("rendered execution-figure census differs")
    for image in soup.select("img"):
        if not str(image.get("alt", "")).strip():
            raise RuntimeError("empty image alternative in backward-equation HTML")
    for table_id in ("kolmogorov-bwd-data-5", "kolmogorov-bwd-data-6"):
        table = soup.find("table", id=table_id)
        if table is None or len(table.select("tbody tr")) != 11:
            raise RuntimeError(f"accessible numeric table differs: {table_id}")
    for tag in soup.select("script[src], link[href]"):
        ref = str(tag.get("src") or tag.get("href") or "")
        if ref.startswith(("http:", "https:", "//")):
            raise RuntimeError(f"external runtime asset leaked: {ref}")
    root = root or path.parent.parent
    allowed_cross_unit = {
        "markov_prop.html",
        "markov_prop.html#inventory_dynam",
        "markov_prop.html#consjumptransemi",
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
        {"id": "kolmogorov-bwd-numerical-qa-binding", "description": f"Bound the deterministic mathematical and simulation QA receipt at SHA-256 {harness.sha256(harness.require_file(NUMERICAL_QA))}."},
        {"id": "kolmogorov-bwd-conditional-holding-times", "description": "Corrected the false IID holding-time claim to conditional independence with state-dependent rates."},
        {"id": "kolmogorov-bwd-state-dependent-rates", "description": "Distinguished state dependence in a time-homogeneous chain from genuinely time-varying intensities."},
        {"id": "kolmogorov-bwd-zero-rate-absorbing-state", "description": "Allowed zero rates, infinite holding at an absorbing state, and an explicit m=0 uniformization branch."},
        {"id": "kolmogorov-bwd-probability-macro", "description": "Normalized the authority's plain P probability token to the declared PP macro."},
        {"id": "kolmogorov-bwd-positive-powers", "description": "Restricted Q^k one = 0 to integer powers k at least one."},
        {"id": "kolmogorov-bwd-binomial-support", "description": "Used b Binomial trials on states zero through b while retaining n=b+1 as the matrix dimension."},
        {"id": "kolmogorov-bwd-state-zero-rate", "description": "Corrected the simulation comment so state zero uses replenishment rate gamma."},
        {"id": "kolmogorov-bwd-max-iteration", "description": "Made simulation exhaustion raise an explicit RuntimeError."},
        {"id": "kolmogorov-bwd-deterministic-numba-rng", "description": "Seeded the Numba RNG inside the compiled entry point and proved exact double replay."},
        {"id": "kolmogorov-bwd-local-solution-state", "description": "Defined T, n, and states locally in the first solution."},
        {"id": "kolmogorov-bwd-uniqueness-notation-domain", "description": "Restored the hat on the competing semigroup equation and restricted V_s to zero through t."},
        {"id": "kolmogorov-bwd-unused-imports-offline", "description": "Removed unused imports and runtime package installation from the translated executable surface."},
        {"id": "kolmogorov-bwd-accessible-figures", "description": "Localized both plots and added exact numeric tables and meaningful Indonesian alternatives."},
        {"id": "kolmogorov-bwd-fence-aware-parser", "description": "Preserved the four-fence exercise containing its nested code example and all three solution pairings."},
        {"id": "kolmogorov-bwd-myst-references", "description": "Resolved local source roles and citations without leaving raw MyST in the reader."},
        {"id": "quantecon-branding-runtime", "description": "Removed remote runtime and branding while preserving authorship, CC BY-SA 4.0, model provenance, and non-endorsement."},
    ]


def install() -> None:
    _install_bindings()
    harness.validate_source = validate_source
    harness.downstream_code = downstream_code
    harness.execute_cells = execute_cells
    harness.directive_to_fenced = directive_to_fenced
    harness.render_markdown = render_markdown
    harness.validate_rendered = validate_rendered
    harness.correction_records = correction_records


def main() -> int:
    install()
    return harness.main()


if __name__ == "__main__":
    sys.exit(main())
