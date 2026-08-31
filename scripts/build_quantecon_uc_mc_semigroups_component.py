#!/usr/bin/env python3
"""Build and verify the isolated Indonesian UC Markov-semigroup unit.

This unit has no executable cells and no unit-specific figures.  The builder
therefore reuses the established QuantEcon/Pandoc component harness while
adding strict zero-code/zero-source-asset gates, resolving the admitted MyST
roles, preserving every stable label, and recording the bounded mathematical
repairs made in the Indonesian derivative.
"""

from __future__ import annotations

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
AUTH_SOURCE = SNAPSHOT / "lectures" / "uc_mc_semigroups.md"
AUTH_NOTEBOOK = NOTEBOOK_SNAPSHOT / "uc_mc_semigroups.ipynb"
TARGET_SOURCE = ROOT / "source" / "quantecon" / "lectures" / "uc_mc_semigroups.md"
OUT_ROOT = ROOT / "build" / "components" / "quantecon_uc_mc_semigroups"
OUT_HTML = OUT_ROOT / "lectures" / "uc_mc_semigroups.html"
OUT_NOTEBOOK = OUT_ROOT / "notebooks" / "uc_mc_semigroups-executed.ipynb"
OUT_MANIFEST = OUT_ROOT / "COMPONENT_MANIFEST.tsv"
OUT_RECEIPT = OUT_ROOT / "COMPONENT_RECEIPT.json"
NUMERICAL_QA = ROOT / "qa" / "QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA.json"

UNIT_ID = "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups"
UNIT_SLUG = "uc_mc_semigroups"
TARGET_REL = "source/quantecon/lectures/uc_mc_semigroups.md"
AUTH_SOURCE_SHA = "cb5e67bc9a614a0169ba9b9bee479a0060b88401e0a7442154242af7bffd9b69"
AUTH_NOTEBOOK_SHA = "fd772f3a052aa9bba611bc5d419858256f1f390459e5c6cd681b6b9ebb58f9ef"
TARGET_SHA = "85dfca4029539025d63721950c74a03dab82c89e0841e3f91b0e7f426fab01f2"
MATHJAX_SHA = "dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a"
CSS_SHA = "820f354bd797c5b5cb0e34248bc82c9b835e0fafb66fed75145f7c8180fa997c"
NUMERICAL_QA_SHA = "6c960605fb9b83abd08bfb78c5b123d6b326119a79172db542c6f5bdac15da47"
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra."
TICK = chr(96)
F3 = TICK * 3

ORIGINAL_RENDER = harness.render_markdown
ORIGINAL_BUILD = harness.build
ORIGINAL_CHECK = harness.check

EXPECTED_LABELS = [
    "imatjc",
    "jccs",
    "scintcon",
    "uc-mc-semigroups-ex-1",
    "uc-mc-semigroups-ex-2",
    "uc-mc-semigroups-ex-3",
    "uc-mc-semigroups-ex-4",
    "uc-mc-semigroups-ex-5",
    "uc-mc-semigroups-prf-1",
    "usmg",
]
EXPECTED_EQUATION_LABELS = [
    "mmismo",
    "propp",
    "imislo",
    "poissemi2",
    "poissonq",
    "kolbackeq_inf",
    "jcinmat",
    "lambdafromq",
    "kfromqxx",
    "kfromqxy",
]
EXPECTED_EQUATION_REFS = [
    "imislo",
    "jcinmat",
    "kolbackeq",
    "kolbackeq_inf",
    "mmismo",
    "norml",
    "poissemi",
    "poissemi2",
    "poissonq",
    "propp",
]
EXPECTED_TARGET_EQUATION_REFS = sorted(
    [*EXPECTED_EQUATION_REFS, "kfromqxx", "kfromqxy"]
)
EXPECTED_CITATIONS = {
    "norris1998markov": (
        "J. R. Norris, Markov Chains "
        "(Cambridge University Press, 1998), Bagian 2.7"
    ),
}
EXPECTED_CROSS_UNIT_LINKS = {
    "generators.html#ecuc",
    "generators.html#ucsgec",
    "generators.html#equation-norml",
    "kolmogorov_fwd.html#intvsmk",
    "markov_prop.html#equation-poissemi",
    "kolmogorov_bwd.html#equation-kolbackeq",
    "kolmogorov_bwd.html",
    "kolmogorov_bwd.html#ejc_algo",
}


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
        "labels": sorted(
            re.findall(r"^:label:\s*([^\s]+)", text, re.MULTILINE)
        ),
        "standalone_labels": sorted(
            re.findall(r"^\(([^)]+)\)=\s*$", text, re.MULTILINE)
        ),
        "equation_refs": sorted(
            set(
                re.findall(
                    r"\{eq\}" + re.escape(TICK) + r"([^" + re.escape(TICK) + r"]+)" + re.escape(TICK),
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
            r"\{" + re.escape(role) + r"\}" + re.escape(TICK) + r"([^" + re.escape(TICK) + r"]+)" + re.escape(TICK),
            text,
        )
    )


def _target_digest() -> str:
    return harness.sha256(harness.require_file(TARGET_SOURCE))


def validate_source(
    target_text: str,
    authority_text: str,
    authority_nb: dict[str, Any],
) -> tuple[str, dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    title, _ = core.frontmatter(target_text)
    if title != "Semigrup Markov yang Kontinu Seragam":
        raise RuntimeError(f"unexpected translated title: {title!r}")
    if harness.sha256(target_text.encode("utf-8")) != TARGET_SHA:
        raise RuntimeError("uc_mc_semigroups target requires an explicit hash rebind")

    target_cells = core.code_cells(target_text)
    authority_cells = core.code_cells(authority_text)
    if target_cells or authority_cells:
        raise RuntimeError(
            "uc_mc_semigroups is admitted as a zero-code unit: "
            f"target={len(target_cells)} authority={len(authority_cells)}"
        )
    if re.search(r"!\[[^\]]*\]\(", target_text) or re.search(
        r"!\[[^\]]*\]\(", authority_text
    ):
        raise RuntimeError("unexpected Markdown image in zero-source-asset uc_mc_semigroups unit")
    if (
        len(authority_nb.get("cells", [])) != 34
        or sum(cell.get("cell_type") == "code" for cell in authority_nb["cells"]) != 0
        or sum(cell.get("cell_type") == "markdown" for cell in authority_nb["cells"]) != 34
    ):
        raise RuntimeError("notebook witness does not have the admitted 34/0 cell census")

    topology = fence_aware_topology(target_text)
    authority_topology = fence_aware_topology(authority_text)
    expected_counts = {
        "headings": 13,
        "code_cells": 0,
        "proof_directives": 7,
        "source_figures": 0,
        "exercises": 5,
        "solutions": 5,
    }
    for key, expected in expected_counts.items():
        if topology.get(key) != expected or authority_topology.get(key) != expected:
            raise RuntimeError(
                f"uc_mc_semigroups topology differs for {key}: "
                f"target={topology.get(key)} authority={authority_topology.get(key)}"
            )
    if topology["labels"] != EXPECTED_LABELS or authority_topology["labels"] != EXPECTED_LABELS:
        raise RuntimeError("uc_mc_semigroups directive-label identity differs")
    if topology["standalone_labels"] or authority_topology["standalone_labels"]:
        raise RuntimeError("unexpected standalone label in uc_mc_semigroups source")
    if (
        topology["equation_refs"] != EXPECTED_TARGET_EQUATION_REFS
        or authority_topology["equation_refs"] != EXPECTED_EQUATION_REFS
    ):
        raise RuntimeError("uc_mc_semigroups equation-reference identity differs")
    if (
        _display_labels(target_text) != EXPECTED_EQUATION_LABELS
        or _display_labels(authority_text) != EXPECTED_EQUATION_LABELS
    ):
        raise RuntimeError("uc_mc_semigroups display-equation label order differs")
    target_displays = re.findall(r"\$\$.*?\$\$", target_text, re.DOTALL)
    authority_displays = re.findall(r"\$\$.*?\$\$", authority_text, re.DOTALL)
    if len(target_displays) != 23 or len(authority_displays) != 20:
        raise RuntimeError(
            "uc_mc_semigroups display-math census differs from the admitted solved target: "
            f"target={len(target_displays)} authority={len(authority_displays)}"
        )

    expected_target_doc = ["kuliah sebelumnya <kolmogorov_bwd>"]
    expected_authority_doc = ["an earlier lecture <kolmogorov_bwd>"]
    if _role_keys(target_text, "doc") != expected_target_doc:
        raise RuntimeError("translated uc_mc_semigroups doc-role surface differs")
    if _role_keys(authority_text, "doc") != expected_authority_doc:
        raise RuntimeError("authority uc_mc_semigroups doc-role surface differs")
    expected_proof_refs = [
        "ecuc",
        "ejc_algo",
        "ejc_algo",
        "intvsmk",
        "jccs",
        "scintcon",
        "scintcon",
        "ucsgec",
        "ucsgec",
        "usmg",
        "usmg",
        "usmg",
        "usmg",
    ]
    if (
        _role_keys(target_text, "prf:ref") != expected_proof_refs
        or _role_keys(authority_text, "prf:ref") != expected_proof_refs
    ):
        raise RuntimeError("uc_mc_semigroups proof-reference surface differs")
    expected_citation_keys = ["norris1998markov"]
    if (
        _role_keys(target_text, "cite") != expected_citation_keys
        or _role_keys(authority_text, "cite") != expected_citation_keys
    ):
        raise RuntimeError("uc_mc_semigroups citation-key surface differs")
    if _role_keys(target_text, "ref") or _role_keys(authority_text, "ref"):
        raise RuntimeError("unexpected generic ref role in uc_mc_semigroups source")

    required_metadata = (
        "unit_id: unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups",
        "source_path: lectures/uc_mc_semigroups.md",
        "source_license: CC BY-SA 4.0",
        MODEL_PROVENANCE,
        "tidak didukung atau disahkan oleh QuantEcon maupun penulis sumber",
    )
    if any(token not in target_text for token in required_metadata):
        raise RuntimeError("uc_mc_semigroups metadata/provenance gate is incomplete")
    required_repairs = (
        "dekomposisi rantai lompatan kanonik",
        "lokal untuk syarat operator-terbatas",
        r"$\RR_+=[0,\infty)$",
        "dengan turunan kanan di $t=0$",
        "basis Schauder",
        r"$K(x,x)=0$ jika $\lambda(x)>0$",
        r"pemetaan $(\lambda,K)\mapsto Q$ tidak injektif",
        "sub-Markov: massa totalnya berkurang",
        "Realisasi minimal dari suatu matriks",
        "ketunggalannya perlu dibuktikan",
        "Jika $m=0$",
        r"(fQ)(y)=\lambda\bigl(f(y-1)-f(y)\bigr)",
        r"Untuk $m=0$, $K^0=I$",
        "Pemisahan kasus lengkap diberikan",
        "Hille–Yosida",
        "dilanjutkan sebagai solusi bernilai riil melewati waktu itu",
        "Catatan kualifikasi hilir",
    )
    if any(token not in target_text for token in required_repairs):
        raise RuntimeError("a required uc_mc_semigroups mathematical repair is missing")
    if "TTP" in target_text or "Translation and Transcription Project" in target_text:
        raise RuntimeError("forbidden umbrella metadata leaked into uc_mc_semigroups")
    forbidden_terminology = (
        "persamaan maju kolmogorov",
        "persamaan mundur kolmogorov",
    )
    if any(
        token in target_text.casefold() for token in forbidden_terminology
    ):
        raise RuntimeError("forbidden metadata or terminology leaked into uc_mc_semigroups")
    return title, topology, target_cells, []


def downstream_code(source: str) -> str:
    if source.strip():
        raise RuntimeError("uc_mc_semigroups has no admitted executable source")
    return ""


def execute_cells(
    cells: list[dict[str, Any]], _interpreter: Path
) -> list[dict[str, Any]]:
    if cells:
        raise RuntimeError("uc_mc_semigroups has no admitted executable cells")
    return []


def directive_to_fenced(text: str) -> str:
    lines = core.normal_text(text).splitlines()
    output: list[str] = []
    stack: list[str] = []
    solution_number = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(F3 + "{code-cell}"):
            raise RuntimeError("unexpected code cell in uc_mc_semigroups renderer")

        proof = re.match(
            r"^" + re.escape(F3) + r"\{prf:(example|lemma|proof|theorem)\}(?:\s+(.*))?$",
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

        solution = re.match(
            r"^" + re.escape(F3) + r"\{solution\}\s+([^\s]+)", line
        )
        if solution:
            solution_number += 1
            output.append(
                f"::: {{#{UNIT_SLUG}-solution-{solution_number} .solution}}"
            )
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
                raise RuntimeError("unexpected MyST closing fence in uc_mc_semigroups")
            stack.pop()
            output.append(":::")
            index += 1
            continue

        output.append(line)
        index += 1
    if stack:
        raise RuntimeError(f"unterminated uc_mc_semigroups MyST directives: {stack}")
    return "\n".join(output) + "\n"


def _split_role(raw: str) -> tuple[str, str]:
    match = re.fullmatch(r"(.*?)\s*<([^<>]+)>", raw, flags=re.DOTALL)
    if match:
        return " ".join(match.group(1).split()), match.group(2)
    return raw.strip(), raw.strip()


def _replace_roles(source: str) -> str:
    cross_equations = {
        "kolbackeq": "kolmogorov_bwd.html#equation-kolbackeq",
        "norml": "generators.html#equation-norml",
        "poissemi": "markov_prop.html#equation-poissemi",
    }

    def equation_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in cross_equations:
            return match.group(0)
        return f"[persamaan {key}]({cross_equations[key]})"

    source = re.sub(r"\{eq\}`([^`]+)`", equation_replacement, source)

    def doc_replacement(match: re.Match[str]) -> str:
        label, document = _split_role(match.group(1))
        if document != "kolmogorov_bwd":
            raise RuntimeError(f"unmapped uc_mc_semigroups doc role: {document}")
        return f"[{label}](kolmogorov_bwd.html)"

    source = re.sub(r"\{doc\}`([^`]+)`", doc_replacement, source)
    proof_targets = {
        "ecuc": ("contoh kurva eksponensial", "generators.html#ecuc"),
        "ejc_algo": ("algoritma rantai lompatan", "kolmogorov_bwd.html#ejc_algo"),
        "intvsmk": ("hasil matriks intensitas ruang berhingga", "kolmogorov_fwd.html#intvsmk"),
        "jccs": ("contoh pasangan rantai lompatan", "#jccs"),
        "scintcon": ("lema syarat konservatif", "#scintcon"),
        "ucsgec": ("teorema karakterisasi semigrup UC", "generators.html#ucsgec"),
        "usmg": ("teorema semigrup Markov UC", "#usmg"),
    }

    def proof_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in proof_targets:
            raise RuntimeError(f"unmapped uc_mc_semigroups proof role: {key}")
        label, target = proof_targets[key]
        return f"[{label}]({target})"

    source = re.sub(r"\{prf:ref\}`([^`]+)`", proof_replacement, source)

    def citation_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in EXPECTED_CITATIONS:
            raise RuntimeError(f"unmapped uc_mc_semigroups citation: {key}")
        return f"<cite>{EXPECTED_CITATIONS[key]}</cite>"

    source = re.sub(r"\{cite\}`([^`]+)`", citation_replacement, source)
    if re.search(r"\{(?:doc|ref|prf:ref|cite)\}`", source):
        raise RuntimeError("unresolved non-equation MyST role in uc_mc_semigroups")
    return source


def render_markdown(
    source: str,
    execution: list[dict[str, Any]],
    title: str,
    stage: Path,
) -> str:
    if execution:
        raise RuntimeError("uc_mc_semigroups renderer received unexpected execution output")
    rendered = ORIGINAL_RENDER(_replace_roles(source), execution, title, stage)
    soup = BeautifulSoup(rendered, "lxml")
    if soup.find("img") is not None or soup.select(".code-cell, .execution-figure"):
        raise RuntimeError("zero-code uc_mc_semigroups render unexpectedly produced media/code")
    # MyST labels only some proof directives.  Give every semantic directive a
    # deterministic reader fragment so backend stable IDs never point at a
    # synthetic, non-existent URL fragment.
    for kind, selector in (
        ("theorem", ".qe-theorem"),
        ("corollary", ".qe-corollary"),
        ("lemma", ".qe-lemma"),
        ("proof", ".qe-proof"),
        ("algorithm", ".qe-algorithm"),
        ("example", ".qe-example"),
    ):
        for number, node in enumerate(soup.select(selector), start=1):
            if not node.get("id"):
                node["id"] = f"{kind}-{number:03d}"
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
        raise RuntimeError("uc_mc_semigroups HTML lacks lang=id-ID")
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("uc_mc_semigroups HTML must have exactly one h1 and one main")
    nav = soup.find("nav")
    if nav is None or not str(nav.get("aria-label", "")).strip():
        raise RuntimeError("uc_mc_semigroups reader navigation lacks an accessible name")
    ids = [str(tag["id"]) for tag in soup.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate HTML id in uc_mc_semigroups component")
    core.validate_equation_ids(ids)
    required = {
        *(f"equation-{label}" for label in EXPECTED_EQUATION_LABELS),
        *EXPECTED_LABELS,
        "uc_mc_semigroups-solution-1",
        "uc_mc_semigroups-solution-2",
        "uc_mc_semigroups-solution-3",
        "uc_mc_semigroups-solution-4",
        "uc_mc_semigroups-solution-5",
        "proof-001",
        "theorem-002",
        "quantecon-attribution",
    }
    if not required.issubset(set(ids)):
        raise RuntimeError(f"missing uc_mc_semigroups labels: {sorted(required - set(ids))}")
    classes = {name for tag in soup.find_all(True) for name in tag.get("class", [])}
    expected_classes = {
        "exercise",
        "solution",
        "qe-example",
        "qe-lemma",
        "qe-proof",
        "qe-theorem",
    }
    if not expected_classes.issubset(classes):
        raise RuntimeError(
            "uc_mc_semigroups directive semantics are incomplete: "
            f"{sorted(expected_classes - classes)}"
        )
    semantic_nodes = soup.select(
        "h2, h3, h4, .exercise, .solution, .qe-example, .qe-lemma, "
        ".qe-proof, .qe-theorem, .qe-corollary, .qe-algorithm"
    )
    if any(not node.get("id") for node in semantic_nodes):
        raise RuntimeError("uc_mc_semigroups semantic node lacks a reader fragment")
    raw_tokens = (
        "O009_FIGURES_",
        "{doc}",
        "{ref}",
        "{prf:ref}",
        "{cite}",
        "{eq}",
        F3 + "{",
    )
    if any(token in text for token in raw_tokens):
        raise RuntimeError("raw MyST role or directive leaked into uc_mc_semigroups HTML")
    if soup.find("img") is not None or soup.find("iframe") is not None:
        raise RuntimeError("uc_mc_semigroups zero-asset HTML unexpectedly contains media")
    if soup.select(".code-cell, .execution-figure"):
        raise RuntimeError("uc_mc_semigroups zero-code HTML unexpectedly contains execution output")
    if MODEL_PROVENANCE not in text:
        raise RuntimeError("exact model provenance missing from uc_mc_semigroups HTML")
    observed_citations = sorted(
        re.sub(r"\s+", " ", cite.get_text(" ", strip=True)).strip()
        for cite in soup.select("main cite")
    )
    expected_citations = [EXPECTED_CITATIONS["norris1998markov"]]
    if observed_citations != expected_citations:
        raise RuntimeError("resolved uc_mc_semigroups bibliography surface differs")
    attribution_text = soup.select_one("#quantecon-attribution").get_text(" ", strip=True)
    if "CC BY-SA 4.0" not in attribution_text or "QuantEcon tidak mengesahkan" not in attribution_text:
        raise RuntimeError("uc_mc_semigroups attribution/license/non-endorsement differs")

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
                raise RuntimeError(f"broken same-page uc_mc_semigroups fragment: {ref}")
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
            raise RuntimeError(f"reference escapes uc_mc_semigroups component: {ref}") from exc
        if not target.is_file():
            raise RuntimeError(f"local uc_mc_semigroups component reference missing: {ref}")
    if observed_cross != EXPECTED_CROSS_UNIT_LINKS:
        raise RuntimeError(
            "uc_mc_semigroups cross-unit dependency set differs: "
            f"{sorted(observed_cross)}"
        )
    _validate_privacy_text(text, "lectures/uc_mc_semigroups.html")


def correction_records(
    _formula_corrections: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "id": "uc-mc-semigroups-conservative-terminology-scope",
            "description": (
                "Recorded that this source uses conservative for the stronger "
                "uniformly bounded ell_1-operator condition, whereas other CTMC "
                "literature may use the term only for zero row sums."
            ),
        },
        {
            "id": "uc-mc-semigroups-infinite-state-generator-proof",
            "description": (
                "Completed the infinite-state generator argument using delta masses, "
                "operator-norm convergence in ell_1, continuity of coordinate summation, "
                "and the Schauder-basis matrix representation."
            ),
        },
        {
            "id": "uc-mc-semigroups-time-zero-right-derivative",
            "description": (
                "Made explicit that differentiation at time zero is a right derivative "
                "on the nonnegative-time semigroup domain."
            ),
        },
        {
            "id": "uc-mc-semigroups-canonical-jump-pair-bijection",
            "description": (
                "Restricted the false claimed bijection over all jump-chain pairs to "
                "canonical decompositions, excluding self-loop reparameterizations "
                "that leave the intensity matrix unchanged."
            ),
        },
        {
            "id": "uc-mc-semigroups-bounded-rate-qualification",
            "description": (
                "Qualified the source's claim that uniformly bounded rates are a mild "
                "restriction: they suffice for nonexplosion but are not necessary and "
                "exclude standard unbounded-rate models."
            ),
        },
        {
            "id": "uc-mc-semigroups-unbounded-q-scope",
            "description": (
                "Replaced the unsupported guarantee of a Markov semigroup by the correct "
                "operator-domain, positivity, honesty, minimal sub-Markov, explosion, "
                "and possible nonuniqueness qualifications."
            ),
        },
        {
            "id": "uc-mc-semigroups-scalar-explosion-endpoint",
            "description": (
                "Corrected the scalar tangent example: the classical solution tends to "
                "infinity at its finite maximal endpoint and does not equal infinity "
                "for every later time."
            ),
        },
        {
            "id": "uc-mc-semigroups-exercise-1-absolute-convergence",
            "description": (
                "Made absolute convergence and the justified sum interchange explicit "
                "before proving the Markov operator norm and distribution preservation."
            ),
        },
        {
            "id": "uc-mc-semigroups-exercise-2-zero-rate-branch",
            "description": (
                "Handled m=0 before defining I+Q/m, eliminating division by zero in "
                "the authority solution."
            ),
        },
        {
            "id": "uc-mc-semigroups-exercise-3-operator-bound",
            "description": (
                "Replaced the authority solution's invalid double sum and shifted index "
                "with the correct coordinate identity and 2 lambda ell_1 bound."
            ),
        },
        {
            "id": "uc-mc-semigroups-exercise-4-complete-induction",
            "description": (
                "Included K^0=I and rewrote the induction step so it never evaluates K "
                "at an index outside the nonnegative state space."
            ),
        },
        {
            "id": "uc-mc-semigroups-exercise-5-reconstruction-closure",
            "description": (
                "Supplied the case-by-case reconstruction proof that the authority "
                "solution explicitly omitted."
            ),
        },
        {
            "id": "uc-mc-semigroups-myst-references-and-citations",
            "description": (
                "Resolved every equation, document, proof, and bibliography role into "
                "stable local links or a complete human-readable citation."
            ),
        },
        {
            "id": "uc-mc-semigroups-zero-code-zero-source-assets",
            "description": (
                "Proved the Markdown and notebook witnesses contain no executable cells "
                "and admitted no unit-specific source figures or generated media."
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
        "authority_markdown_bytes": 18_234,
        "authority_markdown_sha256": AUTH_SOURCE_SHA,
        "authority_notebook_bytes": 29_169,
        "authority_notebook_sha256": AUTH_NOTEBOOK_SHA,
        "authority_notebook_cells": 34,
        "authority_code_cells": 0,
        "target_markdown_bytes": len(harness.require_file(TARGET_SOURCE)),
        "target_markdown_sha256": TARGET_SHA,
        "target_code_cells": 0,
        "unit_source_assets": 0,
        "unit_generated_media": 0,
        "local_runtime_assets": [
            {"path": "MathJax/tex-svg.js", "sha256": MATHJAX_SHA},
            {"path": "reader.css", "sha256": CSS_SHA},
        ],
        "cross_unit_dependencies": sorted(EXPECTED_CROSS_UNIT_LINKS),
        "citation_keys": sorted(EXPECTED_CITATIONS),
        "citation_occurrences": 1,
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
    admitted = {
        "COMPONENT_MANIFEST.tsv",
        "COMPONENT_RECEIPT.json",
        "lectures/uc_mc_semigroups.html",
        "notebooks/uc_mc_semigroups-authority.ipynb",
        "notebooks/uc_mc_semigroups-executed.ipynb",
        "reader.css",
        "source-uc_mc_semigroups.md",
    }
    for relative in sorted(admitted):
        path = root / relative
        if not path.is_file():
            if relative in {"COMPONENT_MANIFEST.tsv", "COMPONENT_RECEIPT.json"}:
                continue
            raise RuntimeError(f"expected text privacy surface is missing: {relative}")
        _validate_privacy_text(
            harness.require_file(path).decode("utf-8"),
            relative,
        )


def _validate_static_inputs() -> None:
    if harness.sha256(harness.require_file(harness.MATHJAX)) != MATHJAX_SHA:
        raise RuntimeError("local MathJax bytes require an explicit hash rebind")
    if harness.sha256(harness.require_file(harness.CSS)) != CSS_SHA:
        raise RuntimeError("shared reader CSS requires an explicit hash rebind")


def _validate_numerical_qa() -> None:
    if harness.sha256(harness.require_file(NUMERICAL_QA)) != NUMERICAL_QA_SHA:
        raise RuntimeError("UC Markov semigroup numerical QA requires a hash rebind")
    receipt = harness.load_json(NUMERICAL_QA)
    if (
        receipt.get("status") != "pass"
        or receipt.get("authority", {}).get("sha256") != AUTH_SOURCE_SHA
        or receipt.get("target", {}).get("sha256") != TARGET_SHA
    ):
        raise RuntimeError("UC Markov semigroup numerical QA binding differs")


def _validate_receipt() -> None:
    receipt = harness.load_json(OUT_RECEIPT)
    if receipt.get("schema") != harness.COMPONENT_SCHEMA or receipt.get("unit_id") != UNIT_ID:
        raise RuntimeError("uc_mc_semigroups component receipt identity differs")
    if receipt.get("target") != {
        "path": TARGET_REL,
        "sha256": TARGET_SHA,
        "title": "Semigrup Markov yang Kontinu Seragam",
    }:
        raise RuntimeError("uc_mc_semigroups receipt target binding differs")
    authority = receipt.get("authority", {})
    if (
        authority.get("source_sha256") != AUTH_SOURCE_SHA
        or authority.get("notebook_sha256") != AUTH_NOTEBOOK_SHA
    ):
        raise RuntimeError("uc_mc_semigroups receipt authority binding differs")
    if receipt.get("code_cells") != [] or receipt.get("replay_match") is not True:
        raise RuntimeError("uc_mc_semigroups zero-code replay receipt differs")
    if receipt.get("corrections") != correction_records([]):
        raise RuntimeError("uc_mc_semigroups correction ledger differs")
    if receipt.get("unit_closure") != _closure_record():
        raise RuntimeError("uc_mc_semigroups unit-closure receipt differs")
    if receipt.get("numerical_qa") != {
        "path": "qa/QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA.json",
        "status": "pass",
        "sha256": NUMERICAL_QA_SHA,
    }:
        raise RuntimeError("uc_mc_semigroups numerical QA receipt binding differs")
    if receipt.get("manifest_sha256") != harness.sha256(harness.require_file(OUT_MANIFEST)):
        raise RuntimeError("uc_mc_semigroups receipt manifest hash differs")
    files = receipt.get("files")
    if not isinstance(files, list) or not all(isinstance(row, dict) for row in files):
        raise RuntimeError("uc_mc_semigroups receipt file inventory is malformed")
    by_path = {str(row.get("path")): row for row in files}
    expected_paths = {
        "MathJax/tex-svg.js",
        "lectures/uc_mc_semigroups.html",
        "notebooks/uc_mc_semigroups-authority.ipynb",
        "notebooks/uc_mc_semigroups-executed.ipynb",
        "reader.css",
        "source-uc_mc_semigroups.md",
    }
    if set(by_path) != expected_paths or receipt.get("file_count") != len(expected_paths):
        raise RuntimeError("uc_mc_semigroups component file closure differs")
    exact_hashes = {
        "MathJax/tex-svg.js": MATHJAX_SHA,
        "notebooks/uc_mc_semigroups-authority.ipynb": AUTH_NOTEBOOK_SHA,
        "reader.css": CSS_SHA,
        "source-uc_mc_semigroups.md": TARGET_SHA,
    }
    for relative, expected_sha in exact_hashes.items():
        if by_path[relative].get("sha256") != expected_sha:
            raise RuntimeError(f"uc_mc_semigroups component hash differs: {relative}")
    executed = harness.load_json(OUT_NOTEBOOK)
    if executed.get("cells") != [] or executed.get("nbformat") != 4:
        raise RuntimeError("uc_mc_semigroups executed-notebook zero-code witness differs")


def build() -> None:
    if _target_digest() != TARGET_SHA:
        raise RuntimeError("uc_mc_semigroups target requires an explicit hash rebind")
    _validate_static_inputs()
    _validate_numerical_qa()
    ORIGINAL_BUILD()
    if _target_digest() != TARGET_SHA:
        raise RuntimeError("uc_mc_semigroups target changed during component build")
    receipt = harness.load_json(OUT_RECEIPT)
    receipt["unit_closure"] = _closure_record()
    receipt["numerical_qa"] = {
        "path": "qa/QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA.json",
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
        raise RuntimeError("uc_mc_semigroups target requires an explicit hash rebind")
    if harness.sha256(harness.require_file(AUTH_SOURCE)) != AUTH_SOURCE_SHA:
        raise RuntimeError("frozen uc_mc_semigroups authority source hash differs")
    if harness.sha256(harness.require_file(AUTH_NOTEBOOK)) != AUTH_NOTEBOOK_SHA:
        raise RuntimeError("frozen uc_mc_semigroups notebook witness hash differs")
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
