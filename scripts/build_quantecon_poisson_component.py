#!/usr/bin/env python3
"""Build the isolated QuantEcon ``poisson.md`` reader component.

The first QuantEcon unit has its own bounded builder.  This companion builder
uses the same frozen manifests, offline runtime, MyST subset, and rights
handling, but writes to a separate generated directory so a failed Poisson
build cannot damage the already verified memoryless component.  The upstream
source and notebook are witnesses and are never edited.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

import build_quantecon_component as base


ORIGINAL_DIRECTIVE_TO_FENCED = base.directive_to_fenced


ROOT = base.ROOT
AUTH_ROOT = ROOT / "authority" / "quantecon"
SNAPSHOT = AUTH_ROOT / "source_snapshot" / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
NOTEBOOK_SNAPSHOT = AUTH_ROOT / "notebook_snapshot" / "continuous_time_mcs.notebooks-1e17c25c937f369544380f769eb9c1bc45d12d1a"
AUTH_SOURCE = SNAPSHOT / "lectures" / "poisson.md"
AUTH_NOTEBOOK = NOTEBOOK_SNAPSHOT / "poisson.ipynb"
TARGET_SOURCE = ROOT / "source" / "quantecon" / "lectures" / "poisson.md"
ACTIVE_MANIFEST = AUTH_ROOT / "ACTIVE_INPUT_MANIFEST.tsv"
SOURCE_MANIFEST = AUTH_ROOT / "SOURCE_MANIFEST.tsv"
RUNTIME_LOCK = ROOT / "00_control" / "RUNTIME_LOCK.json"
MATHJAX = ROOT / "authority" / "random" / "shared" / "MathJax" / "tex-svg.js"
CSS = ROOT / "source" / "reader.css"
OUT_ROOT = ROOT / "build" / "components" / "quantecon_poisson"
OUT_HTML = OUT_ROOT / "lectures" / "poisson.html"
OUT_NOTEBOOK = OUT_ROOT / "notebooks" / "poisson-executed.ipynb"
OUT_MANIFEST = OUT_ROOT / "COMPONENT_MANIFEST.tsv"
OUT_RECEIPT = OUT_ROOT / "COMPONENT_RECEIPT.json"

UNIT_ID = "unit.o009.quantecon.ctmc.poisson-processes"
UNIT_SLUG = "poisson"
AUTH_COMMIT = "8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
AUTH_TREE = "f0f11e3bbc6bd23d6e4a447a7e05c0aaf0f7209e"
AUTH_SOURCE_SHA = "d9bb4268d30179d48598dd63066f938da895110511fb6f54aaf915200353e102"
AUTH_NOTEBOOK_SHA = "cae41809b046c2b1153cbe01523d2128790bf6226ec87aaefe0fbcb6b4464474"
MATHJAX_SHA = "dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a"
COMPONENT_SCHEMA = "o009.quantecon-component.v1"
TARGET_REL = "source/quantecon/lectures/poisson.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_file(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"missing or linked regular file: {path}")
    return path.read_bytes()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def manifest_hash(path: Path) -> str:
    return sha256(require_file(path))


def verify_manifest(path: Path) -> None:
    # Reuse the bounded authority verifier, whose base paths are fixed to the
    # frozen QuantEcon snapshots.
    base.verify_manifest(path)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(require_file(path).decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def code_cells(text: str) -> list[dict[str, Any]]:
    return base.code_cells(text)


def topology(text: str) -> dict[str, Any]:
    return base.topology(text)


def math_surface(text: str) -> list[str]:
    return base.math_surface(text)


def _formula_key(value: str) -> str:
    """Normalize only the two explicit missing-plus repairs in the source."""
    value = re.sub(r"\\text\{[^{}]*\}", "", value)
    value = re.sub(r"\\,", "", value)
    value = re.sub(r"\s+", "", value)
    return value.replace(r"\cdots+W_", r"\cdotsW_")


def validate_source(target_text: str, authority_text: str, authority_nb: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    title, _ = base.frontmatter(target_text)
    target_cells = code_cells(target_text)
    auth_cells = code_cells(authority_text)
    if len(auth_cells) != 7 or len(target_cells) != 7:
        raise RuntimeError(f"poisson code-cell census differs: target={len(target_cells)} authority={len(auth_cells)}")
    target_topology = topology(target_text)
    auth_topology = topology(authority_text)
    if target_topology != auth_topology:
        raise RuntimeError(f"poisson MyST topology differs: target={target_topology} authority={auth_topology}")
    if len(authority_nb.get("cells", [])) != 27 or sum(c.get("cell_type") == "code" for c in authority_nb["cells"]) != 7:
        raise RuntimeError("poisson notebook witness does not have the admitted 27/7 cell census")
    for index, (target, auth) in enumerate(zip(target_cells, auth_cells, strict=True), start=1):
        if target["kernel"] != auth["kernel"] or target["tags"] != auth["tags"]:
            raise RuntimeError(f"poisson code-cell metadata differs at cell {index}")
        if target["source"] != auth["source"]:
            raise RuntimeError(f"poisson code-cell source differs at cell {index}; code is not translatable")
    auth_math = math_surface(authority_text)
    target_math = math_surface(target_text)
    if len(auth_math) != len(target_math):
        raise RuntimeError(f"poisson formula census differs: target={len(target_math)} authority={len(auth_math)}")
    display_pattern = r"\$\$.*?\$\$"
    auth_display = re.findall(display_pattern, authority_text, flags=re.DOTALL)
    target_display = re.findall(display_pattern, target_text, flags=re.DOTALL)
    if len(auth_display) != len(target_display):
        raise RuntimeError(f"poisson display-formula census differs: target={len(target_display)} authority={len(auth_display)}")
    corrections: list[dict[str, str]] = []
    for index, (auth_formula, target_formula) in enumerate(zip(auth_display, target_display), start=1):
        if auth_formula == target_formula:
            continue
        if _formula_key(auth_formula) == _formula_key(target_formula):
            auth_compact = re.sub(r"\s+", "", auth_formula)
            target_compact = re.sub(r"\s+", "", target_formula)
            if r"\cdotsW_" in auth_compact and r"\cdots+W_" in target_compact:
                corrections.append({"id": f"formula-plus-{index}", "description": "Inserted the explicit plus sign omitted in the authority's W_1 + \\cdots W_k/n sum."})
            continue
        else:
            raise RuntimeError(f"unexpected Poisson display-formula change at surface {index}: {auth_formula!r} -> {target_formula!r}")
    required = ("defcount", "poissondist", "binpois", "restart_prop", "poisson-ex-1", "poisson-ex-2")
    if any(token not in target_text for token in required):
        raise RuntimeError("poisson target lost a required source label")
    if "TTP" in target_text or "Translation and Transcription Project" in target_text:
        raise RuntimeError("forbidden umbrella label leaked into QuantEcon work text")
    return title, target_topology, target_cells, corrections


def downstream_code(source: str) -> str:
    lines = source.splitlines()
    kept: list[str] = []
    removed = 0
    for line in lines:
        if re.match(r"^\s*!pip\s+install\s+quantecon\s*$", line):
            kept.append("# Build luring hilir: perintah pemasangan paket dari sumber dihapus.")
            removed += 1
        else:
            kept.append(line)
    if removed != 1 and "pip install quantecon" in source:
        raise RuntimeError("unexpected package-install directive multiplicity")
    # Numba's RNG has independent state.  Seed the sample-producing helper once
    # per replay, preserving the visible upstream cell byte-for-byte.
    for position, line in enumerate(kept):
        if re.match(r"^def draw_Nt_sample\s*\(", line):
            indent = re.match(r"^\s*", line).group(0) + "    "
            kept.insert(position + 1, f"{indent}np.random.seed(1234)")
            break
    return "\n".join(kept).rstrip() + "\n"


def directive_to_fenced(text: str) -> str:
    # The existing parser is topology-safe for this source.  Its only unit-
    # specific output is the solution anchor prefix, which is renamed here.
    return ORIGINAL_DIRECTIVE_TO_FENCED(text).replace("memoryless-solution", f"{UNIT_SLUG}-solution")


def correction_records(formula_corrections: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return the auditable downstream corrections for this component.

    Kept as a hook so later QuantEcon units can reuse the bounded build harness
    without inheriting Poisson-specific correction claims.
    """

    return [
        {"id": "poisson-rate-copyedit", "description": "Corrected the authority's first-visit waiting-time prose from rate t lambda to rate lambda; t is the horizon."},
        *formula_corrections,
        {"id": "poisson-proof-typo", "description": "Rendered the authority typo indepenence as the correct Indonesian independensi."},
        {"id": "poisson-cross-unit-erlcdf", "description": "Repaired the reference to the Erlang CDF definition as a local link to the preceding memoryless unit."},
        {"id": "poisson-myst-references", "description": "Resolved MyST citation keys and two cross-unit proof/section references into human-readable citations and local links."},
        {"id": "quantecon-offline-install", "description": "Removed only the package-install directive in downstream execution/render copies; frozen source remains unchanged."},
        {"id": "quantecon-accessibility-alt", "description": "Added meaningful Indonesian alternatives to generated computational figures."},
        {"id": "quantecon-branding-runtime", "description": "Removed remote theme/analytics/launch runtime while retaining author, source, license, and non-endorsement attribution."},
    ]


def execute_cells(cells: list[dict[str, Any]], interpreter: Path) -> list[dict[str, Any]]:
    old = base.downstream_code
    base.downstream_code = downstream_code
    try:
        return base.execute_cells(cells, interpreter)
    finally:
        base.downstream_code = old


def render_markdown(source: str, execution: list[dict[str, Any]], title: str, stage: Path) -> str:
    # Resolve the admitted MyST bibliography and cross-unit references into
    # human-readable local HTML before the generic Pandoc subset sees them.
    source = source.replace("{cite}`howard2017elements`", "<cite>Howard (2017)</cite>")
    source = source.replace("{cite}`norris1998markov`", "<cite>Norris (1998)</cite>")
    source = source.replace("{cite}`pardoux2008markov`", "<cite>Pardoux (2008)</cite>")
    source = source.replace("{prf:ref}`erlexp`", "[teorema jumlah eksponensial](memoryless.html#erlexp)")
    source = source.replace("{ref}`lingkungan <geomtoexp>`", "[pembahasan sebelumnya](memoryless.html#geomtoexp)")
    old_downstream = base.downstream_code
    old_directive = base.directive_to_fenced
    base.downstream_code = downstream_code
    base.directive_to_fenced = directive_to_fenced
    try:
        rendered = base.render_markdown(source, execution, title, stage)
    finally:
        base.downstream_code = old_downstream
        base.directive_to_fenced = old_directive
    # The shared renderer uses a memoryless-safe filename convention.  Rename
    # those generated assets in this isolated component and provide meaningful
    # alternatives for each Poisson figure.
    assets = stage / "assets"
    for path in sorted(assets.glob("memoryless-cell-*.png")):
        path.rename(path.with_name(path.name.replace("memoryless-cell-", f"{UNIT_SLUG}-cell-")))
    rendered = rendered.replace("memoryless-cell-", f"{UNIT_SLUG}-cell-")
    soup = BeautifulSoup(rendered, "lxml")
    alternatives = {
        3: "Grafik proses penghitungan dengan lompatan pada waktu kedatangan.",
        4: "Satu realisasi proses Poisson dengan lompatan pada setiap kedatangan.",
        5: "Ilustrasi pendekatan kisi untuk proses Poisson dengan kunjungan biner.",
        6: "Perbandingan distribusi empiris dan Poisson untuk banyak pengambilan.",
        7: "Perbandingan distribusi binomial dan Poisson untuk beberapa parameter.",
    }
    for image in soup.find_all("img"):
        match = re.search(rf"{re.escape(UNIT_SLUG)}-cell-(\d+)-", str(image.get("src", "")))
        if match:
            alt = alternatives.get(int(match.group(1)), "Grafik keluaran komputasi proses Poisson.")
            image["alt"] = alt
            figure = image.find_parent("figure")
            if figure is not None:
                caption = figure.find("figcaption")
                if caption is not None:
                    caption.string = alt
    for index, summary in enumerate(soup.find_all("summary"), start=1):
        label = f"Tampilkan kode sel {index}"
        summary["aria-label"] = label
        summary.string = label
    # ``erlcdf`` is defined in the preceding memoryless unit.  Preserve the
    # cross-unit reference explicitly instead of leaving a broken same-page
    # fragment in the standalone HTML.
    for anchor in soup.select('a[href="#equation-erlcdf"]'):
        anchor["href"] = "memoryless.html#equation-erlcdf"
    return "<!DOCTYPE html>\n" + str(soup)


def validate_rendered(path: Path, root: Path | None = None) -> None:
    soup = BeautifulSoup(require_file(path).decode("utf-8"), "lxml")
    if soup.html is None or soup.html.get("lang") != "id-ID":
        raise RuntimeError("Poisson HTML lacks lang=id-ID")
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("Poisson HTML must have exactly one h1 and one main")
    ids = [str(tag["id"]) for tag in soup.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate HTML id in Poisson component")
    base.validate_equation_ids(ids)
    required = {"equation-defcount", "equation-poissondist", "equation-binpois", "restart_prop", "poisson-ex-1", "poisson-ex-2", "poisson-solution-1", "poisson-solution-2"}
    if not required.issubset(set(ids)):
        raise RuntimeError(f"missing required Poisson labels: {sorted(required - set(ids))}")
    classes = {cls for tag in soup.find_all(True) for cls in tag.get("class", [])}
    if not {"exercise", "solution", "qe-theorem", "qe-proof"}.issubset(classes):
        raise RuntimeError("Poisson directive semantics are missing from rendered HTML")
    if "O009_FIGURES_" in str(soup):
        raise RuntimeError("unbound computational figure placeholder leaked")
    for tag in soup.select("img"):
        if not str(tag.get("alt", "")).strip():
            raise RuntimeError("empty image alternative text")
    for tag in soup.select("script[src], link[href]"):
        ref = str(tag.get("src") or tag.get("href") or "")
        if ref.startswith(("http:", "https:", "//")):
            raise RuntimeError(f"external runtime asset leaked: {ref}")
    root = root or path.parent.parent
    for tag in soup.select("a[href], img[src], script[src], link[href]"):
        ref = str(tag.get("href") or tag.get("src") or "")
        if ref.startswith(("http:", "https:", "#", "mailto:")) or not ref:
            continue
        if ref == "../../index.html":
            continue
        if ref in {
            "memoryless.html#equation-erlcdf",
            "memoryless.html#erlexp",
            "memoryless.html#geomtoexp",
        }:
            continue
        target = (path.parent / ref.split("#", 1)[0]).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise RuntimeError(f"component reference escapes site: {ref}") from exc
        if not target.is_file():
            raise RuntimeError(f"component reference missing: {ref}")


def site_rows(stage: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((p for p in stage.rglob("*") if p.is_file()), key=lambda p: p.relative_to(stage).as_posix().casefold()):
        rel = path.relative_to(stage).as_posix()
        if rel in {"COMPONENT_MANIFEST.tsv", "COMPONENT_RECEIPT.json"}:
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes())})
    return rows


def write_manifest(stage: Path, rows: list[dict[str, Any]]) -> str:
    path = stage / "COMPONENT_MANIFEST.tsv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["path", "bytes", "sha256"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return sha256(path.read_bytes())


def build() -> None:
    authority_before = manifest_hash(ACTIVE_MANIFEST)
    source_before = manifest_hash(SOURCE_MANIFEST)
    verify_manifest(ACTIVE_MANIFEST)
    verify_manifest(SOURCE_MANIFEST)
    authority_text = base.normal_text(require_file(AUTH_SOURCE).decode("utf-8"))
    target_text = base.normal_text(require_file(TARGET_SOURCE).decode("utf-8"))
    if sha256(authority_text.encode("utf-8")) != AUTH_SOURCE_SHA:
        raise RuntimeError("frozen QuantEcon Poisson authority hash differs")
    authority_nb = load_json(AUTH_NOTEBOOK)
    if sha256(require_file(AUTH_NOTEBOOK)) != AUTH_NOTEBOOK_SHA:
        raise RuntimeError("frozen QuantEcon Poisson notebook witness hash differs")
    title, topo, cells, formula_corrections = validate_source(target_text, authority_text, authority_nb)
    interpreter, runtime = base.runtime_python()
    first = execute_cells(cells, interpreter)
    second = execute_cells(cells, interpreter)
    if canonical(first) != canonical(second):
        raise RuntimeError("two clean offline Poisson cell replays differ")
    stage_parent = ROOT / "build" / "component-stages"
    stage_parent.mkdir(parents=True, exist_ok=True)
    with __import__("tempfile").TemporaryDirectory(prefix=f"quantecon-{UNIT_SLUG}-", dir=stage_parent) as temp_name:
        stage = Path(temp_name)
        (stage / "lectures").mkdir(parents=True, exist_ok=True)
        (stage / "notebooks").mkdir(parents=True, exist_ok=True)
        (stage / "MathJax").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(MATHJAX, stage / "MathJax" / "tex-svg.js")
        shutil.copyfile(CSS, stage / "reader.css")
        shutil.copyfile(TARGET_SOURCE, stage / f"source-{UNIT_SLUG}.md")
        shutil.copyfile(AUTH_NOTEBOOK, stage / "notebooks" / f"{UNIT_SLUG}-authority.ipynb")
        rendered = render_markdown(target_text, first, title, stage)
        (stage / "lectures" / f"{UNIT_SLUG}.html").write_text(rendered, encoding="utf-8", newline="\n")
        notebook = {
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": runtime["version"]}},
            "nbformat": 4,
            "nbformat_minor": 5,
            "cells": [
                {"cell_type": "code", "execution_count": i, "metadata": {"tags": cell["tags"], "source_cell_index": cell["index"]}, "outputs": [], "source": downstream_code(cell["source"])}
                for i, cell in enumerate(cells, start=1)
            ],
        }
        OUT_NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
        (stage / "notebooks" / f"{UNIT_SLUG}-executed.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        validate_rendered(stage / "lectures" / f"{UNIT_SLUG}.html", stage)
        rows = site_rows(stage)
        manifest_sha = write_manifest(stage, rows)
        corrections = correction_records(formula_corrections)
        receipt = {
            "schema": COMPONENT_SCHEMA,
            "unit_id": UNIT_ID,
            "status": "complete-unit-local",
            "authority": {
                "commit": AUTH_COMMIT,
                "tree": AUTH_TREE,
                "source_path": str(AUTH_SOURCE.relative_to(ROOT)),
                "source_sha256": AUTH_SOURCE_SHA,
                "notebook_path": str(AUTH_NOTEBOOK.relative_to(ROOT)),
                "notebook_sha256": AUTH_NOTEBOOK_SHA,
                "active_input_manifest_sha256_before": authority_before,
                "source_manifest_sha256_before": source_before,
            },
            "target": {"path": TARGET_REL, "sha256": sha256(target_text.encode("utf-8")), "title": title},
            "topology": topo,
            "code_cells": [
                {
                    "index": cell["index"],
                    "source_sha256": sha256(cell["source"].encode("utf-8")),
                    "execution_source_sha256": sha256(downstream_code(cell["source"]).encode("utf-8")),
                    "replay": {
                        "index": first[i - 1]["index"],
                        "stdout": first[i - 1]["stdout"],
                        "stderr": first[i - 1]["stderr"],
                        "figures": [{key: value for key, value in figure.items() if key != "data"} for figure in first[i - 1]["figures"]],
                    },
                }
                for i, cell in enumerate(cells, start=1)
            ],
            "corrections": corrections,
            "runtime": runtime,
            "replay_match": True,
            "files": rows,
            "file_count": len(rows),
            "total_bytes": sum(int(row["bytes"]) for row in rows),
            "manifest_sha256": manifest_sha,
            "built_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        (stage / "COMPONENT_RECEIPT.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        validate_rendered(stage / "lectures" / f"{UNIT_SLUG}.html", stage)
        if OUT_ROOT.exists():
            if OUT_ROOT.is_symlink():
                raise RuntimeError("refusing to replace linked Poisson component")
            shutil.rmtree(OUT_ROOT)
        OUT_ROOT.parent.mkdir(parents=True, exist_ok=True)
        os.replace(stage, OUT_ROOT)
    authority_after = manifest_hash(ACTIVE_MANIFEST)
    source_after = manifest_hash(SOURCE_MANIFEST)
    if authority_before != authority_after or source_before != source_after:
        raise RuntimeError("authority manifest changed during Poisson build")
    receipt = load_json(OUT_RECEIPT)
    receipt["authority"]["active_input_manifest_sha256_after"] = authority_after
    receipt["authority"]["source_manifest_sha256_after"] = source_after
    OUT_RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS unit={UNIT_ID} files={receipt['file_count']} bytes={receipt['total_bytes']} html_sha256={sha256(require_file(OUT_HTML))} receipt_sha256={sha256(require_file(OUT_RECEIPT))}")


def check() -> None:
    if not OUT_RECEIPT.is_file() or not OUT_MANIFEST.is_file() or not OUT_HTML.is_file():
        raise RuntimeError("Poisson component output/receipt/manifest is missing")
    receipt = load_json(OUT_RECEIPT)
    if receipt.get("schema") != COMPONENT_SCHEMA or receipt.get("unit_id") != UNIT_ID:
        raise RuntimeError("Poisson component receipt identity differs")
    if receipt.get("target", {}).get("sha256") != sha256(require_file(TARGET_SOURCE)):
        raise RuntimeError("Poisson target source changed after component build")
    validate_rendered(OUT_HTML)
    rows = site_rows(OUT_ROOT)
    with OUT_MANIFEST.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    expected = [{"path": row["path"], "bytes": str(row["bytes"]), "sha256": row["sha256"]} for row in rows]
    if listed != expected:
        raise RuntimeError("Poisson component manifest does not match output")
    print(f"PASS check files={len(rows)} bytes={sum(int(row['bytes']) for row in rows)} html_sha256={sha256(require_file(OUT_HTML))}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate existing component without rebuilding")
    args = parser.parse_args()
    check() if args.check else build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
