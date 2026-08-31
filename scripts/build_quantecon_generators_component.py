#!/usr/bin/env python3
"""Build and verify the isolated Indonesian semigroups/generators unit.

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
AUTH_SOURCE = SNAPSHOT / "lectures" / "generators.md"
AUTH_NOTEBOOK = NOTEBOOK_SNAPSHOT / "generators.ipynb"
TARGET_SOURCE = ROOT / "source" / "quantecon" / "lectures" / "generators.md"
OUT_ROOT = ROOT / "build" / "components" / "quantecon_generators"
OUT_HTML = OUT_ROOT / "lectures" / "generators.html"
OUT_NOTEBOOK = OUT_ROOT / "notebooks" / "generators-executed.ipynb"
OUT_MANIFEST = OUT_ROOT / "COMPONENT_MANIFEST.tsv"
OUT_RECEIPT = OUT_ROOT / "COMPONENT_RECEIPT.json"

UNIT_ID = "unit.o009.quantecon.ctmc.generators"
UNIT_SLUG = "generators"
TARGET_REL = "source/quantecon/lectures/generators.md"
AUTH_SOURCE_SHA = "035caa76ccc07622b6d0564f7b72a2f02a2b5d276e2848a3612f9414232d6736"
AUTH_NOTEBOOK_SHA = "8ce748db97a5a38414277e8056ab3b6a6eac8900e3a97b44991ba722033099b1"
TARGET_SHA = "db2fa074b9198d2722c8bba8adc69987ce4c5bf580a0119d7996ab0301fa1da0"
MATHJAX_SHA = "dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a"
CSS_SHA = "820f354bd797c5b5cb0e34248bc82c9b835e0fafb66fed75145f7c8180fa997c"
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra."
TICK = chr(96)
F3 = TICK * 3

ORIGINAL_RENDER = harness.render_markdown
ORIGINAL_BUILD = harness.build
ORIGINAL_CHECK = harness.check

EXPECTED_LABELS = [
    "diffexpmap",
    "ecuc",
    "generators-ex-1",
    "generators-ex-2",
    "generators-ex-3",
    "generators-prf-1",
    "generators-prf-2",
    "ucsgec",
]
EXPECTED_EQUATION_LABELS = [
    "abscp",
    "norml",
    "opexpo",
    "devlim",
    "expdiffer",
    "defgenr",
    "czsg2",
    "sgbound",
    "czsg3",
]
EXPECTED_EQUATION_REFS = [
    "abscp",
    "czsg2",
    "czsg3",
    "defgenr",
    "devlim",
    "expdiffer",
    "norml",
    "opexpo",
    "sgbound",
]
EXPECTED_CITATIONS = {
    "applebaum2019semigroups": (
        "David Applebaum, Semigroups of Linear Operators "
        "(Cambridge University Press, 2019)"
    ),
    "bobrowski2005functional": (
        "Adam Bobrowski, Functional Analysis for Probability and Stochastic "
        "Processes: An Introduction (Cambridge University Press, 2005)"
    ),
    "sahoo2011introduction": (
        "Prasanna K. Sahoo dan Palaniappan Kannappan, Introduction to "
        "Functional Equations (CRC Press, 2011)"
    ),
}
EXPECTED_CROSS_UNIT_LINKS = {
    "kolmogorov_fwd.html",
    "memoryless.html#exp_unique",
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
    if title != "Semigrup dan Generator":
        raise RuntimeError(f"unexpected translated title: {title!r}")
    if harness.sha256(target_text.encode("utf-8")) != TARGET_SHA:
        raise RuntimeError("generators target requires an explicit hash rebind")

    target_cells = core.code_cells(target_text)
    authority_cells = core.code_cells(authority_text)
    if target_cells or authority_cells:
        raise RuntimeError(
            "generators is admitted as a zero-code unit: "
            f"target={len(target_cells)} authority={len(authority_cells)}"
        )
    if re.search(r"!\[[^\]]*\]\(", target_text) or re.search(
        r"!\[[^\]]*\]\(", authority_text
    ):
        raise RuntimeError("unexpected Markdown image in zero-source-asset generators unit")
    if (
        len(authority_nb.get("cells", [])) != 28
        or sum(cell.get("cell_type") == "code" for cell in authority_nb["cells"]) != 0
        or sum(cell.get("cell_type") == "markdown" for cell in authority_nb["cells"]) != 28
    ):
        raise RuntimeError("notebook witness does not have the admitted 28/0 cell census")

    topology = fence_aware_topology(target_text)
    authority_topology = fence_aware_topology(authority_text)
    expected_counts = {
        "headings": 12,
        "code_cells": 0,
        "proof_directives": 5,
        "source_figures": 0,
        "exercises": 3,
        "solutions": 3,
    }
    for key, expected in expected_counts.items():
        if topology.get(key) != expected or authority_topology.get(key) != expected:
            raise RuntimeError(
                f"generators topology differs for {key}: "
                f"target={topology.get(key)} authority={authority_topology.get(key)}"
            )
    if topology["labels"] != EXPECTED_LABELS or authority_topology["labels"] != EXPECTED_LABELS:
        raise RuntimeError("generators directive-label identity differs")
    if topology["standalone_labels"] or authority_topology["standalone_labels"]:
        raise RuntimeError("unexpected standalone label in generators source")
    if (
        topology["equation_refs"] != EXPECTED_EQUATION_REFS
        or authority_topology["equation_refs"] != EXPECTED_EQUATION_REFS
    ):
        raise RuntimeError("generators equation-reference identity differs")
    if (
        _display_labels(target_text) != EXPECTED_EQUATION_LABELS
        or _display_labels(authority_text) != EXPECTED_EQUATION_LABELS
    ):
        raise RuntimeError("generators display-equation label order differs")
    target_displays = re.findall(r"\$\$.*?\$\$", target_text, re.DOTALL)
    authority_displays = re.findall(r"\$\$.*?\$\$", authority_text, re.DOTALL)
    if len(target_displays) != 23 or len(authority_displays) != 17:
        raise RuntimeError(
            "generators display-math census differs from the admitted solved target: "
            f"target={len(target_displays)} authority={len(authority_displays)}"
        )

    expected_target_doc = ["pembahasan kita <kolmogorov_fwd>"]
    expected_authority_doc = ["our discussion <kolmogorov_fwd>"]
    if _role_keys(target_text, "doc") != expected_target_doc:
        raise RuntimeError("translated generators doc-role surface differs")
    if _role_keys(authority_text, "doc") != expected_authority_doc:
        raise RuntimeError("authority generators doc-role surface differs")
    expected_proof_refs = [
        "diffexpmap",
        "ecuc",
        "exp_unique",
        "ucsgec",
        "ucsgec",
    ]
    if (
        _role_keys(target_text, "prf:ref") != expected_proof_refs
        or _role_keys(authority_text, "prf:ref") != expected_proof_refs
    ):
        raise RuntimeError("generators proof-reference surface differs")
    expected_citation_keys = sorted(
        [
            "applebaum2019semigroups",
            "bobrowski2005functional",
            "bobrowski2005functional",
            "sahoo2011introduction",
        ]
    )
    if (
        _role_keys(target_text, "cite") != expected_citation_keys
        or _role_keys(authority_text, "cite") != expected_citation_keys
    ):
        raise RuntimeError("generators citation-key surface differs")
    if _role_keys(target_text, "ref") or _role_keys(authority_text, "ref"):
        raise RuntimeError("unexpected generic ref role in generators source")

    required_metadata = (
        "unit_id: unit.o009.quantecon.ctmc.generators",
        "source_path: lectures/generators.md",
        "source_license: CC BY-SA 4.0",
        MODEL_PROVENANCE,
        "tidak didukung atau disahkan oleh QuantEcon maupun penulis sumber",
    )
    if any(token not in target_text for token in required_metadata):
        raise RuntimeError("generators metadata/provenance gate is incomplete")
    required_repairs = (
        r"$x_0\in D(A)$",
        "ditafsirkan sebagai solusi ringan",
        "ledakan, kehilangan",
        "massa, atau masalah ketunggalan",
        r"\lL(\ell_1(S))",
        r"operator linear terbatas pada $\ell_1(S)$ berdimensi berhingga",
        r"semigrup evolusi** pada $\BB$",
        r"operator linear $A:D(A)\subseteq\BB\to\BB$",
        r"fungsi kontinu $f$ dari $\RR_+$ ke $\RR$",
        r"- h e^{tA} A",
        r"(e^{hA} - I - hA)",
        r"kenaikan positif dan negatif; untuk $t=0$ limitnya memang limit kanan",
        r"$t_n\to t$ akhirnya dapat dipisahkan menjadi suku-suku dari kanan",
        r"{eq}`czsg3` menyiratkan {eq}`czsg2`",
    )
    if any(token not in target_text for token in required_repairs):
        raise RuntimeError("a required generators mathematical repair is missing")
    if "TTP" in target_text or "Translation and Transcription Project" in target_text:
        raise RuntimeError("forbidden umbrella metadata leaked into generators")
    forbidden_terminology = (
        "persamaan maju kolmogorov",
        "persamaan mundur kolmogorov",
    )
    if any(
        token in target_text.casefold() for token in forbidden_terminology
    ):
        raise RuntimeError("forbidden metadata or terminology leaked into generators")
    return title, topology, target_cells, []


def downstream_code(source: str) -> str:
    if source.strip():
        raise RuntimeError("generators has no admitted executable source")
    return ""


def execute_cells(
    cells: list[dict[str, Any]], _interpreter: Path
) -> list[dict[str, Any]]:
    if cells:
        raise RuntimeError("generators has no admitted executable cells")
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
            raise RuntimeError("unexpected code cell in generators renderer")

        proof = re.match(
            r"^" + re.escape(F3) + r"\{prf:(example|lemma|theorem)\}(?:\s+(.*))?$",
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
                raise RuntimeError("unexpected MyST closing fence in generators")
            stack.pop()
            output.append(":::")
            index += 1
            continue

        output.append(line)
        index += 1
    if stack:
        raise RuntimeError(f"unterminated generators MyST directives: {stack}")
    return "\n".join(output) + "\n"


def _split_role(raw: str) -> tuple[str, str]:
    match = re.fullmatch(r"(.*?)\s*<([^<>]+)>", raw, flags=re.DOTALL)
    if match:
        return " ".join(match.group(1).split()), match.group(2)
    return raw.strip(), raw.strip()


def _replace_roles(source: str) -> str:
    def doc_replacement(match: re.Match[str]) -> str:
        label, document = _split_role(match.group(1))
        if document != "kolmogorov_fwd":
            raise RuntimeError(f"unmapped generators doc role: {document}")
        return f"[{label}](kolmogorov_fwd.html)"

    source = re.sub(r"\{doc\}`([^`]+)`", doc_replacement, source)
    proof_targets = {
        "diffexpmap": ("lemma keterdiferensialan kurva eksponensial", "#diffexpmap"),
        "ecuc": ("contoh kurva eksponensial", "#ecuc"),
        "exp_unique": ("sifat tanpa ingatan fungsi eksponensial", "memoryless.html#exp_unique"),
        "ucsgec": ("teorema karakterisasi semigrup UC", "#ucsgec"),
    }

    def proof_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in proof_targets:
            raise RuntimeError(f"unmapped generators proof role: {key}")
        label, target = proof_targets[key]
        return f"[{label}]({target})"

    source = re.sub(r"\{prf:ref\}`([^`]+)`", proof_replacement, source)

    def citation_replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in EXPECTED_CITATIONS:
            raise RuntimeError(f"unmapped generators citation: {key}")
        return f"<cite>{EXPECTED_CITATIONS[key]}</cite>"

    source = re.sub(r"\{cite\}`([^`]+)`", citation_replacement, source)
    if re.search(r"\{(?:doc|ref|prf:ref|cite)\}`", source):
        raise RuntimeError("unresolved non-equation MyST role in generators")
    return source


def render_markdown(
    source: str,
    execution: list[dict[str, Any]],
    title: str,
    stage: Path,
) -> str:
    if execution:
        raise RuntimeError("generators renderer received unexpected execution output")
    rendered = ORIGINAL_RENDER(_replace_roles(source), execution, title, stage)
    soup = BeautifulSoup(rendered, "lxml")
    if soup.find("img") is not None or soup.select(".code-cell, .execution-figure"):
        raise RuntimeError("zero-code generators render unexpectedly produced media/code")
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
        raise RuntimeError("generators HTML lacks lang=id-ID")
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("generators HTML must have exactly one h1 and one main")
    nav = soup.find("nav")
    if nav is None or not str(nav.get("aria-label", "")).strip():
        raise RuntimeError("generators reader navigation lacks an accessible name")
    ids = [str(tag["id"]) for tag in soup.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate HTML id in generators component")
    core.validate_equation_ids(ids)
    required = {
        *(f"equation-{label}" for label in EXPECTED_EQUATION_LABELS),
        *EXPECTED_LABELS,
        "generators-solution-1",
        "generators-solution-2",
        "generators-solution-3",
        "quantecon-attribution",
    }
    if not required.issubset(set(ids)):
        raise RuntimeError(f"missing generators labels: {sorted(required - set(ids))}")
    classes = {name for tag in soup.find_all(True) for name in tag.get("class", [])}
    expected_classes = {"exercise", "solution", "qe-example", "qe-lemma", "qe-theorem"}
    if not expected_classes.issubset(classes):
        raise RuntimeError(
            "generators directive semantics are incomplete: "
            f"{sorted(expected_classes - classes)}"
        )
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
        raise RuntimeError("raw MyST role or directive leaked into generators HTML")
    if soup.find("img") is not None or soup.find("iframe") is not None:
        raise RuntimeError("generators zero-asset HTML unexpectedly contains media")
    if soup.select(".code-cell, .execution-figure"):
        raise RuntimeError("generators zero-code HTML unexpectedly contains execution output")
    if MODEL_PROVENANCE not in text:
        raise RuntimeError("exact model provenance missing from generators HTML")
    observed_citations = sorted(
        re.sub(r"\s+", " ", cite.get_text(" ", strip=True)).strip()
        for cite in soup.select("main cite")
    )
    expected_citations = sorted(
        [
            EXPECTED_CITATIONS["applebaum2019semigroups"],
            EXPECTED_CITATIONS["bobrowski2005functional"],
            EXPECTED_CITATIONS["bobrowski2005functional"],
            EXPECTED_CITATIONS["sahoo2011introduction"],
        ]
    )
    if observed_citations != expected_citations:
        raise RuntimeError("resolved generators bibliography surface differs")
    attribution_text = soup.select_one("#quantecon-attribution").get_text(" ", strip=True)
    if "CC BY-SA 4.0" not in attribution_text or "QuantEcon tidak mengesahkan" not in attribution_text:
        raise RuntimeError("generators attribution/license/non-endorsement differs")

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
                raise RuntimeError(f"broken same-page generators fragment: {ref}")
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
            raise RuntimeError(f"reference escapes generators component: {ref}") from exc
        if not target.is_file():
            raise RuntimeError(f"local generators component reference missing: {ref}")
    if observed_cross != EXPECTED_CROSS_UNIT_LINKS:
        raise RuntimeError(
            "generators cross-unit dependency set differs: "
            f"{sorted(observed_cross)}"
        )
    _validate_privacy_text(text, "lectures/generators.html")


def correction_records(
    _formula_corrections: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "id": "generators-classical-versus-mild-solutions",
            "description": (
                "Added the missing domain qualification for classical solutions "
                "of the abstract Cauchy problem and identified the general semigroup "
                "trajectory as a mild solution; the bounded UC case is distinguished."
            ),
        },
        {
            "id": "generators-markov-semigroup-regularity-scope",
            "description": (
                "Made the time-zero continuity assumption explicit in the finite-state "
                "claim and noted explosion, mass loss, and uniqueness hazards for "
                "unrestricted infinite-state intensity matrices."
            ),
        },
        {
            "id": "generators-finite-state-l1-space",
            "description": (
                "Made the finite-state dependence explicit as ell_1(S), avoiding "
                "the false implication that the standard infinite sequence space is finite-dimensional."
            ),
        },
        {
            "id": "generators-semigroup-carrier-space",
            "description": (
                "Corrected an evolution semigroup described as being on the operator "
                "space to a semigroup of operators acting on the Banach space B."
            ),
        },
        {
            "id": "generators-domain-of-unbounded-generator",
            "description": (
                "Typed the possibly unbounded generator as A:D(A) subset B to B "
                "instead of claiming it is defined on all of B."
            ),
        },
        {
            "id": "generators-scalar-semigroup-domain",
            "description": (
                "Restricted the scalar functional-equation statement and conclusion "
                "to nonnegative time, matching its stated hypotheses."
            ),
        },
        {
            "id": "generators-exercise-1-missing-h",
            "description": (
                "Restored both missing h factors in the authority solution, supplied "
                "the exponential-series remainder bound, and proved both derivative equalities."
            ),
        },
        {
            "id": "generators-exercise-2-continuity-closure",
            "description": (
                "Completed the one-sided argument at positive and zero time and reduced "
                "an arbitrary convergent time sequence to the required cases."
            ),
        },
        {
            "id": "generators-exercise-3-continuity-closure",
            "description": (
                "Made the strong-continuity implication and resulting semigroup bound "
                "explicit, then completed both one-sided limits and the arbitrary-sequence conclusion."
            ),
        },
        {
            "id": "generators-myst-references-and-citations",
            "description": (
                "Resolved every equation, document, proof, and bibliography role into "
                "stable local links or complete human-readable citations."
            ),
        },
        {
            "id": "generators-zero-code-zero-source-assets",
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
        "authority_markdown_bytes": 16_818,
        "authority_markdown_sha256": AUTH_SOURCE_SHA,
        "authority_notebook_bytes": 26_128,
        "authority_notebook_sha256": AUTH_NOTEBOOK_SHA,
        "authority_notebook_cells": 28,
        "authority_code_cells": 0,
        "target_markdown_bytes": 21_637,
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
        "citation_occurrences": 4,
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
        "lectures/generators.html",
        "notebooks/generators-authority.ipynb",
        "notebooks/generators-executed.ipynb",
        "reader.css",
        "source-generators.md",
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


def _validate_receipt() -> None:
    receipt = harness.load_json(OUT_RECEIPT)
    if receipt.get("schema") != harness.COMPONENT_SCHEMA or receipt.get("unit_id") != UNIT_ID:
        raise RuntimeError("generators component receipt identity differs")
    if receipt.get("target") != {
        "path": TARGET_REL,
        "sha256": TARGET_SHA,
        "title": "Semigrup dan Generator",
    }:
        raise RuntimeError("generators receipt target binding differs")
    authority = receipt.get("authority", {})
    if (
        authority.get("source_sha256") != AUTH_SOURCE_SHA
        or authority.get("notebook_sha256") != AUTH_NOTEBOOK_SHA
    ):
        raise RuntimeError("generators receipt authority binding differs")
    if receipt.get("code_cells") != [] or receipt.get("replay_match") is not True:
        raise RuntimeError("generators zero-code replay receipt differs")
    if receipt.get("corrections") != correction_records([]):
        raise RuntimeError("generators correction ledger differs")
    if receipt.get("unit_closure") != _closure_record():
        raise RuntimeError("generators unit-closure receipt differs")
    if receipt.get("manifest_sha256") != harness.sha256(harness.require_file(OUT_MANIFEST)):
        raise RuntimeError("generators receipt manifest hash differs")
    files = receipt.get("files")
    if not isinstance(files, list) or not all(isinstance(row, dict) for row in files):
        raise RuntimeError("generators receipt file inventory is malformed")
    by_path = {str(row.get("path")): row for row in files}
    expected_paths = {
        "MathJax/tex-svg.js",
        "lectures/generators.html",
        "notebooks/generators-authority.ipynb",
        "notebooks/generators-executed.ipynb",
        "reader.css",
        "source-generators.md",
    }
    if set(by_path) != expected_paths or receipt.get("file_count") != len(expected_paths):
        raise RuntimeError("generators component file closure differs")
    exact_hashes = {
        "MathJax/tex-svg.js": MATHJAX_SHA,
        "notebooks/generators-authority.ipynb": AUTH_NOTEBOOK_SHA,
        "reader.css": CSS_SHA,
        "source-generators.md": TARGET_SHA,
    }
    for relative, expected_sha in exact_hashes.items():
        if by_path[relative].get("sha256") != expected_sha:
            raise RuntimeError(f"generators component hash differs: {relative}")
    executed = harness.load_json(OUT_NOTEBOOK)
    if executed.get("cells") != [] or executed.get("nbformat") != 4:
        raise RuntimeError("generators executed-notebook zero-code witness differs")


def build() -> None:
    if _target_digest() != TARGET_SHA:
        raise RuntimeError("generators target requires an explicit hash rebind")
    _validate_static_inputs()
    ORIGINAL_BUILD()
    if _target_digest() != TARGET_SHA:
        raise RuntimeError("generators target changed during component build")
    receipt = harness.load_json(OUT_RECEIPT)
    receipt["unit_closure"] = _closure_record()
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
        raise RuntimeError("generators target requires an explicit hash rebind")
    if harness.sha256(harness.require_file(AUTH_SOURCE)) != AUTH_SOURCE_SHA:
        raise RuntimeError("frozen generators authority source hash differs")
    if harness.sha256(harness.require_file(AUTH_NOTEBOOK)) != AUTH_NOTEBOOK_SHA:
        raise RuntimeError("frozen generators notebook witness hash differs")
    _validate_static_inputs()
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
