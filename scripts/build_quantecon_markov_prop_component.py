#!/usr/bin/env python3
"""Build and verify the isolated Indonesian QuantEcon ``markov_prop`` unit.

The generic execution/render harness lives in the two preceding QuantEcon
builders.  This adapter binds the exact authority/notebook/asset identities,
admits only three explicit mathematical corrections, resolves the unit's MyST
cross references, and keeps execution offline and deterministic.
"""

from __future__ import annotations

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
SNAPSHOT = AUTH_ROOT / "source_snapshot" / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
NOTEBOOK_SNAPSHOT = AUTH_ROOT / "notebook_snapshot" / "continuous_time_mcs.notebooks-1e17c25c937f369544380f769eb9c1bc45d12d1a"
AUTH_SOURCE = SNAPSHOT / "lectures" / "markov_prop.md"
AUTH_NOTEBOOK = NOTEBOOK_SNAPSHOT / "markov_prop.ipynb"
AUTH_ASSET = SNAPSHOT / "lectures" / "_static" / "lecture_specific" / "markov_prop" / "flow_fig.png"
TARGET_SOURCE = ROOT / "source" / "quantecon" / "lectures" / "markov_prop.md"
OUT_ROOT = ROOT / "build" / "components" / "quantecon_markov_prop"
OUT_HTML = OUT_ROOT / "lectures" / "markov_prop.html"
OUT_NOTEBOOK = OUT_ROOT / "notebooks" / "markov_prop-executed.ipynb"
OUT_MANIFEST = OUT_ROOT / "COMPONENT_MANIFEST.tsv"
OUT_RECEIPT = OUT_ROOT / "COMPONENT_RECEIPT.json"

UNIT_ID = "unit.o009.quantecon.ctmc.markov-property"
UNIT_SLUG = "markov_prop"
TARGET_REL = "source/quantecon/lectures/markov_prop.md"
AUTH_SOURCE_SHA = "0380ca588468e4185391e8bf5d2d207978a958a6c954029f41399473d9d6f545"
AUTH_NOTEBOOK_SHA = "c5e3ff8f3bfe4b32d6bee0a6d15435fc738032357025e5ff8b0293b684a801db"
AUTH_ASSET_SHA = "54906c3f6f48664960d25ead98af1150014e88367db1d604f6ccc9d01e50564f"


ORIGINAL_RENDER = harness.render_markdown
ORIGINAL_DOWNSTREAM_CODE = harness.downstream_code


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


def _formula_differences(authority_text: str, target_text: str) -> list[dict[str, str]]:
    # The explicit Exercise 4 correction note adds explanatory mathematics that
    # has no authority counterpart.  Remove only that named downstream note and
    # its one support-set gloss before comparing the preserved source sequence.
    target_text = re.sub(
        r"\*\*Catatan koreksi hilir\.\*\*.*?\n\n(?=\(Pernyataan yang melibatkan)",
        "",
        target_text,
        flags=re.DOTALL,
    )
    target_text = target_text.replace(
        "banyaknya keadaan dan ``states = np.arange(n)`` mencakup seluruh ruang keadaan\n$\\{0, \\ldots, b\\}$.",
        "banyaknya keadaan dan ``states = np.arange(n)`` mencakup seluruh ruang keadaan.",
    )
    authority = core.math_surface(authority_text)
    target = core.math_surface(target_text)
    if len(authority) != len(target):
        raise RuntimeError(f"markov_prop formula census differs: target={len(target)} authority={len(authority)}")
    corrections: list[dict[str, str]] = []
    for index, (old, new) in enumerate(zip(authority, target, strict=True), start=1):
        if old == new:
            continue
        if old == "$X_0=0$" and new == "$X_0=b$":
            corrections.append({
                "id": "markov-prop-inventory-initial-state",
                "description": "Aligned the inventory-simulation prose with the preserved implementation and docstring, which start at X_0=b rather than X_0=0.",
            })
            continue
        if r"\mathbb1\{X_t=x\}" in old and r"\mathbb1\{X_t^m=x\}" in new:
            if old.replace(r"X_t=x", r"X_t^m=x") != new:
                raise RuntimeError(f"unexpected empirical-law change at formula surface {index}")
            corrections.append({
                "id": "markov-prop-empirical-replicate-index",
                "description": "Restored the missing simulation index m in the empirical cross-sectional distribution formula.",
            })
            continue
        raise RuntimeError(f"unexpected markov_prop formula change at surface {index}: {old!r} -> {new!r}")
    return corrections


def validate_source(
    target_text: str,
    authority_text: str,
    authority_nb: dict[str, Any],
) -> tuple[str, dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    title, _ = core.frontmatter(target_text)
    target_cells = core.code_cells(target_text)
    authority_cells = core.code_cells(authority_text)
    if len(target_cells) != 5 or len(authority_cells) != 5:
        raise RuntimeError(f"markov_prop code-cell census differs: target={len(target_cells)} authority={len(authority_cells)}")
    target_topology = core.topology(target_text)
    authority_topology = core.topology(authority_text)
    if target_topology != authority_topology:
        raise RuntimeError(f"markov_prop MyST topology differs: target={target_topology} authority={authority_topology}")
    if len(authority_nb.get("cells", [])) != 46 or sum(cell.get("cell_type") == "code" for cell in authority_nb["cells"]) != 5:
        raise RuntimeError("markov_prop notebook witness does not have the admitted 46/5 cell census")
    for index, (target, authority) in enumerate(zip(target_cells, authority_cells, strict=True), start=1):
        if target["kernel"] != authority["kernel"] or target["tags"] != authority["tags"]:
            raise RuntimeError(f"markov_prop code-cell metadata differs at cell {index}")
        expected = authority["source"]
        if index == 5:
            expected = expected.replace(
                "ψ_0 = binom.pmf(states, n, 0.25)",
                "ψ_0 = binom.pmf(states, b, 0.25)",
            )
        if target["source"] != expected:
            raise RuntimeError(f"unexpected markov_prop code change at cell {index}")
    corrections = _formula_differences(authority_text, target_text)
    required = {
        "kernprod", "markovpropd", "update_rule", "jointdeq", "mathjointd",
        "kernprodk", "chapkol_ct2", "markovprop", "poissemi", "xfromy",
        "ijumpkern", "distflowconst", "finstatediscretemc", "jdfin",
        "inventory_dynam", "consjumptransemi", "invdistflows",
        "markov-prop-1", "markov-prop-2", "markov-prop-3", "markov-prop-4",
    }
    if any(token not in target_text for token in required):
        raise RuntimeError("markov_prop target lost a required source label or anchor")
    if "TTP" in target_text or "Translation and Transcription Project" in target_text:
        raise RuntimeError("forbidden umbrella label leaked into QuantEcon work text")
    if "OpenAI Codex gpt-5.6-sol, Ultra." not in target_text:
        raise RuntimeError("exact production model provenance is missing")
    return title, target_topology, target_cells, corrections


def downstream_code(source: str) -> str:
    text = ORIGINAL_DOWNSTREAM_CODE(source)
    kept: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "from myst_nb import glue":
            kept.append("# Build luring hilir: impor glue khusus buku dihapus.")
        elif stripped.startswith('glue("flow_fig"'):
            kept.append("# Build luring hilir: keluaran gambar ditangkap langsung.")
        elif stripped.startswith('plt.savefig("_static/lecture_specific/markov_prop/flow_fig.png")'):
            kept.append("# Build luring hilir: penulisan ke pohon sumber beku dinonaktifkan.")
        else:
            kept.append(line)
    result = "\n".join(kept).rstrip() + "\n"
    result = result.replace('xlabel="time", ylabel="inventory"', 'xlabel="waktu", ylabel="persediaan"')
    result = result.replace("ax.set_xlabel('inventory')", "ax.set_xlabel('persediaan')")
    return result


def _replace_myst_roles(source: str) -> str:
    replacements = {
        "{doc}`the introduction <intro>`": "[pendahuluan sumber](https://continuous-time-mcs.quantecon.org/intro.html)",
        "{cite}`walsh2012knowing`": "<cite>Walsh (2012)</cite>",
        "{cite}`liggett2010continuous`": "<cite>Liggett (2010)</cite>",
        "{cite}`le2016brownian`": "<cite>Le Gall (2016)</cite>",
        "{ref}`preceding discussion <jdfin>`": "[pembahasan sebelumnya](#jdfin)",
        "{doc}`later lecture <uc_mc_semigroups>`": "kuliah lanjutan tentang semigrup Markov waktu kontinu",
        "{ref}`is not memoryless <fail_mem>`": "[tidak bersifat tanpa ingatan](memoryless.html#fail_mem)",
        "{prf:ref}`exp_unique`": "[teorema keunikan eksponensial](memoryless.html#exp_unique)",
        "{doc}`previous lecture <poisson>`": "[kuliah sebelumnya](poisson.html)",
        "{ref}`restart <restart_prop>`": "[memulai ulang](poisson.html#restart_prop)",
        "{ref}`Recalling <restart_prop>`": "[Mengingat](poisson.html#restart_prop)",
        "{ref}`flow_fig`": "[gambar aliran distribusi](#flow_fig)",
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    role_patterns = (
        (r"\{doc\}`[^`]*<intro>`", "[pendahuluan sumber](https://continuous-time-mcs.quantecon.org/intro.html)"),
        (r"\{ref\}`[^`]*<jdfin>`", "[pembahasan sebelumnya](#jdfin)"),
        (r"\{doc\}`[^`]*<uc_mc_semigroups>`", "kuliah lanjutan tentang semigrup Markov waktu kontinu"),
        (r"\{ref\}`[^`]*<fail_mem>`", "[tidak bersifat tanpa ingatan](memoryless.html#fail_mem)"),
        (r"\{doc\}`[^`]*<poisson>`", "[kuliah sebelumnya](poisson.html)"),
        (r"\{ref\}`[^`]*<restart_prop>`", "[hasil memulai ulang proses Poisson](poisson.html#restart_prop)"),
        (r"\{ref\}`[^`]*<flow_fig>`", "[gambar aliran distribusi](#flow_fig)"),
    )
    for pattern, replacement in role_patterns:
        source = re.sub(pattern, replacement, source)
    return source


def _replace_glue_figure(source: str) -> str:
    pattern = re.compile(
        r'^```\{glue:figure\}\s+flow_fig\s*\n:name:\s*"flow_fig"\s*\n\s*\n(.*?)\n```\s*$',
        flags=re.MULTILINE | re.DOTALL,
    )
    replacement = (
        '<figure id="flow_fig" class="source-figure">\n'
        '<img src="../assets/markov-prop-flow-source.png" '
        'alt="Aliran probabilitas model persediaan dari distribusi awal menuju distribusi jangka panjang.">\n'
        '<figcaption>Aliran probabilitas untuk model persediaan.</figcaption>\n'
        '</figure>'
    )
    source, count = pattern.subn(replacement, source)
    if count != 1:
        raise RuntimeError(f"expected one markov_prop glue figure, found {count}")
    return source


def render_markdown(source: str, execution: list[dict[str, Any]], title: str, stage: Path) -> str:
    if harness.sha256(harness.require_file(AUTH_ASSET)) != AUTH_ASSET_SHA:
        raise RuntimeError("frozen markov_prop flow asset hash differs")
    assets = stage / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(AUTH_ASSET, assets / "markov-prop-flow-source.png")
    prepared = _replace_glue_figure(_replace_myst_roles(source))
    rendered = ORIGINAL_RENDER(prepared, execution, title, stage)
    soup = BeautifulSoup(rendered, "lxml")
    alternatives = {
        4: "Lintasan simulasi tingkat persediaan terhadap waktu.",
        5: "Aliran distribusi persediaan tiga dimensi sepanjang waktu.",
    }
    for image in soup.find_all("img"):
        src = str(image.get("src", ""))
        match = re.search(r"markov_prop-cell-(\d+)-", src)
        if match:
            alt = alternatives.get(int(match.group(1)), "Keluaran komputasi sifat Markov.")
            image["alt"] = alt
            figure = image.find_parent("figure")
            if figure is not None and figure.find("figcaption") is not None:
                figure.find("figcaption").string = alt
    for index, summary in enumerate(soup.find_all("summary"), start=1):
        label = f"Tampilkan kode sel {index}"
        summary["aria-label"] = label
        summary.string = label
    attribution = soup.select_one("#quantecon-attribution")
    if attribution is None:
        raise RuntimeError("QuantEcon attribution panel is missing")
    provenance = soup.new_tag("p", attrs={"class": "model-provenance"})
    provenance.string = "Provenans produksi: OpenAI Codex gpt-5.6-sol, Ultra. Kredit penulis dan kontributor manusia tetap dipertahankan."
    attribution.append(provenance)
    return "<!DOCTYPE html>\n" + str(soup)


def validate_rendered(path: Path, root: Path | None = None) -> None:
    soup = BeautifulSoup(harness.require_file(path).decode("utf-8"), "lxml")
    if soup.html is None or soup.html.get("lang") != "id-ID":
        raise RuntimeError("markov_prop HTML lacks lang=id-ID")
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("markov_prop HTML must have exactly one h1 and one main")
    ids = [str(tag["id"]) for tag in soup.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate HTML id in markov_prop component")
    core.validate_equation_ids(ids)
    required = {
        "equation-kernprod", "equation-markovpropd", "equation-update_rule",
        "equation-jointdeq", "equation-mathjointd", "equation-kernprodk",
        "equation-chapkol_ct2", "equation-markovprop", "equation-poissemi",
        "equation-xfromy", "equation-ijumpkern", "equation-distflowconst",
        "finstatediscretemc", "jdfin", "inventory_dynam", "consjumptransemi",
        "invdistflows", "flow_fig", "markov-prop-1", "markov-prop-2",
        "markov-prop-3", "markov-prop-4", "markov_prop-solution-1",
        "markov_prop-solution-2", "markov_prop-solution-3", "markov_prop-solution-4",
    }
    if not required.issubset(set(ids)):
        raise RuntimeError(f"missing markov_prop labels: {sorted(required - set(ids))}")
    classes = {cls for tag in soup.find_all(True) for cls in tag.get("class", [])}
    if not {"exercise", "solution", "qe-algorithm"}.issubset(classes):
        raise RuntimeError("markov_prop directive semantics are incomplete")
    text = str(soup)
    if any(token in text for token in ("O009_FIGURES_", "{doc}`", "{ref}`", "{cite}`", "{glue:")):
        raise RuntimeError("raw MyST or figure placeholder leaked into markov_prop HTML")
    if "OpenAI Codex gpt-5.6-sol, Ultra." not in text:
        raise RuntimeError("exact model provenance missing from rendered markov_prop HTML")
    for image in soup.select("img"):
        if not str(image.get("alt", "")).strip():
            raise RuntimeError("empty image alternative in markov_prop HTML")
    for tag in soup.select("script[src], link[href]"):
        ref = str(tag.get("src") or tag.get("href") or "")
        if ref.startswith(("http:", "https:", "//")):
            raise RuntimeError(f"external runtime asset leaked: {ref}")
    root = root or path.parent.parent
    allowed_cross_unit = {
        "memoryless.html#fail_mem", "memoryless.html#exp_unique",
        "poisson.html", "poisson.html#restart_prop",
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
            raise RuntimeError(f"markov_prop reference escapes component: {ref}") from exc
        if not target.is_file():
            raise RuntimeError(f"markov_prop local reference missing: {ref}")


def correction_records(formula_corrections: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        *formula_corrections,
        {"id": "markov-prop-source-typo", "description": "Rendered the authority typo 'updates at follows' as natural Indonesian prose."},
        {"id": "markov-prop-binomial-support", "description": "Kept n=b+1 for states 0 through b and used Binomial(b, 0.25) so the initial distribution has total mass one on that state space."},
        {"id": "markov-prop-offline-mutation-guards", "description": "Removed package installation, glue-only calls, and writes into the frozen source tree from downstream execution copies."},
        {"id": "markov-prop-localized-plot-labels", "description": "Localized visible time and inventory axis labels only in downstream execution copies."},
        {"id": "markov-prop-myst-references", "description": "Resolved citations, prior-unit references, same-page anchors, and the forward unit reference into human-readable local or source-safe text."},
        {"id": "markov-prop-accessibility", "description": "Added Indonesian alternatives and captions to the frozen flow asset and generated figures."},
        {"id": "quantecon-branding-runtime", "description": "Removed remote theme, analytics, and launch runtime while preserving author, source, CC BY-SA 4.0, model provenance, and non-endorsement."},
    ]


def install() -> None:
    _install_bindings()
    harness.validate_source = validate_source
    harness.downstream_code = downstream_code
    harness.render_markdown = render_markdown
    harness.validate_rendered = validate_rendered
    harness.correction_records = correction_records


def main() -> int:
    install()
    return harness.main()


if __name__ == "__main__":
    sys.exit(main())
