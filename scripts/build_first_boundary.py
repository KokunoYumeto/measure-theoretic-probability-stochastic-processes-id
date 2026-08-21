#!/usr/bin/env python3
"""Build and verify the bounded offline O009 theory–lab reader."""

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
import tempfile
import urllib.parse
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
AUTH_RANDOM = ROOT / "authority" / "random"
LAB_SOURCE = ROOT / "source" / "labs" / "01-konvergensi-monte-carlo.Rmd"
SOURCE_INDEX = ROOT / "source" / "index.md"
SOURCE_CSS = ROOT / "source" / "reader.css"
SITE = ROOT / "build" / "site"
R_SCRIPT = ROOT / "tools" / "R-4.6.1" / "bin" / "Rscript.exe"
PANDOC = "pandoc"

RANDOM_MANIFEST_SHA256 = "2ee154a38b57201457538db8c0e7df592a052eade8dcfda217605810f04f21e4"
MATHJAX_SHA256 = "dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a"
MATHJAX_BOLDSYMBOL_SHA256 = "716cf8735d00abfb1627f8adbbf4aeb915ac9b5c55d47aeaf276e73dac6a2aa1"
RANDOM_BASE_URL = "https://www.randomservices.org/random/"
THEORY_UNITS = (
    {
        "rel": "prob/Convergence.html",
        "authority_sha256": "749de69aba8c7b54e5944ddbe4b342fec8695b32ff46e34409f7b6040241e34f",
        "source_title": "Convergence",
        "nav_label": "Konvergensi",
        "rights_id": "o009-rights-random-convergence",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Basic Theory",
            "Sequences of events",
            "The Continuity Theorems",
            "Convergence with Probability 1",
            "Convergence in Probability",
        ),
    },
    {
        "rel": "prob/Probability2.html",
        "authority_sha256": "ba442c5fac2cb1608965f974b3f346cec9515e894428accb83521465492b2d10",
        "source_title": "Probability Revisited",
        "nav_label": "Probabilitas ditinjau kembali",
        "rights_id": "o009-rights-random-probability-revisited",
        # Upstream links #tai1, but its intended limsup/liminf result is #tai12.
        "fragment_corrections": {"#tai1": "#tai12"},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Probability Revisited",
            "Measure Theory",
            "Probability Theory",
            "Equivalent Random Variables",
            "Completion",
        ),
    },
    {
        "rel": "prob/Processes.html",
        "authority_sha256": "d4a65b124face6115950e212af2acb5dccf33e1065c77fb3d6aecb727d39e6bc",
        "source_title": "Stochastic Processes",
        "nav_label": "Proses stokastik",
        "rights_id": "o009-rights-random-stochastic-processes",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Stochastic Processes",
            "Introduction",
            "Equivalent Processes",
            "The Kolmogorov Construction",
            "Applications",
        ),
    },
    {
        "rel": "prob/Stop.html",
        "authority_sha256": "9d26e78a8ee2a5a14ade3708838298ef0ba51cf9cd9658602a4f26e73b68524d",
        "source_title": "Filtrations and Stopping Times",
        "nav_label": "Filtrasi dan waktu henti",
        "rights_id": "o009-rights-random-filtrations-stopping-times",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Filtrations and Stopping Times",
            "Introduction",
            "Basic Definitions",
            "Right Continuity",
            "Stopping Times",
            "Basic Properties",
            "Basic Constructions",
            "The Sigma-Algebra of a Stopping Time",
        ),
    },
    {
        "rel": "dist/Convergence.html",
        "authority_sha256": "dc6a536ca3359f3952e1ae487a445377de1c1e73491bb56f3baa8862630dcc3d",
        "source_title": "Convergence in Distribution",
        "nav_label": "Konvergensi dalam distribusi",
        "rights_id": "o009-rights-random-convergence-in-distribution",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Convergence in Distribution",
            "Distributions on",
            "Preliminary Examples",
            "Probability Density Functions",
            "The Skorohod Representation",
            "Examples and Applications",
            "Fundamental Theorems",
            "General Spaces",
            "Skorohod's Representation Theorem",
            "Expected Value",
        ),
    },
    {
        "rel": "expect/Conditional2.html",
        "authority_sha256": "98307993d76941808cc87b7d28dfd8b2e24325913471b07c3a350a52a54c87c2",
        "source_title": "Conditional Expected Value Revisited",
        "nav_label": "Nilai harapan bersyarat",
        "rights_id": "o009-rights-random-conditional-expectation",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Conditional Expected Value Revisited",
            "Basic Theory",
            "Definition",
            "Properties",
            "Conditional Probability",
            "Basic Examples",
            "Best Predictor",
            "Conditional Variance",
            "Conditional Covariance",
        ),
    },
    {
        "rel": "expect/Uniform.html",
        "authority_sha256": "66f610030094a063be69408d3112c74353941849fe36353f4c5365380f03df2d",
        "source_title": "Uniformly Integrable Variables",
        "nav_label": "Terintegralkan seragam",
        "rights_id": "o009-rights-random-uniform-integrability",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Uniformly Integrable Variables",
            "Basic Theory",
            "Definition",
            "Properties",
            "Convergence",
            "Examples",
        ),
    },
)
MATH_RE = re.compile(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", re.DOTALL)
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.I)
R_CHUNK_RE = re.compile(
    r"^```\{r\s+o009_lab_convergence_mc\b[^}]*\}\s*$\n(.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)
PLACEHOLDER = "<!-- O009_EXECUTION_TABLE -->"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_file(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"missing or linked regular file: {path}")
    return path.read_bytes()


def theory_paths(unit: dict[str, object]) -> tuple[Path, Path]:
    rel = Path(str(unit["rel"]))
    return AUTH_RANDOM / "static" / rel, ROOT / "source" / "theory" / rel


def validate_theory_unit(unit: dict[str, object]) -> None:
    authority, target_path = theory_paths(unit)
    source_bytes = require_file(authority)
    target_bytes = require_file(target_path)
    if sha256(source_bytes) != unit["authority_sha256"]:
        raise RuntimeError(f"Random authority hash changed: {unit['rel']}")
    source_text = source_bytes.decode("utf-8")
    target_text = target_bytes.decode("utf-8")
    source = BeautifulSoup(source_text, "lxml")
    target = BeautifulSoup(target_text, "lxml")
    source_tags = source.find_all(True)
    target_tags = target.find_all(True)
    if [tag.name for tag in source_tags] != [tag.name for tag in target_tags]:
        raise RuntimeError(f"translated theory element topology differs: {unit['rel']}")
    if len(source_tags) != len(target_tags):
        raise RuntimeError(f"translated theory element count differs: {unit['rel']}")
    for index, (left, right) in enumerate(zip(source_tags, target_tags, strict=True)):
        left_attrs = deepcopy(left.attrs)
        right_attrs = deepcopy(right.attrs)
        if left.name == "html":
            left_attrs.pop("lang", None)
            right_attrs.pop("lang", None)
        if left.name == "meta" and left.get("name") == "keywords":
            left_attrs.pop("content", None)
            right_attrs.pop("content", None)
        for permitted in ("alt", "title"):
            left_attrs.pop(permitted, None)
            right_attrs.pop(permitted, None)
        if left_attrs != right_attrs:
            raise RuntimeError(
                f"translated theory attribute drift in {unit['rel']} at tag {index}: "
                f"{left.name} {left_attrs!r} != {right_attrs!r}"
            )
    if target.html is None or target.html.get("lang") != "id-ID":
        raise RuntimeError(f"translated theory must declare lang=id-ID: {unit['rel']}")
    source_math = MATH_RE.findall(source_text)
    target_math = MATH_RE.findall(target_text)
    if source_math != target_math:
        raise RuntimeError(f"translated theory TeX surface differs: {unit['rel']}")
    ids = [str(tag["id"]) for tag in target.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"duplicate id in translated theory: {unit['rel']}")
    if any(not str(tag.get("alt", "")).strip() for tag in target.select("img")):
        raise RuntimeError(f"empty image alt in translated theory: {unit['rel']}")
    visible = " ".join(target.stripped_strings)
    forbidden = tuple(str(item) for item in unit["forbidden"])
    hits = [item for item in forbidden if item in visible]
    if hits:
        raise RuntimeError(f"active English theory residue in {unit['rel']}: {hits}")


def validate_theory_translation() -> None:
    for unit in THEORY_UNITS:
        validate_theory_unit(unit)


def extract_and_run_lab(work: Path) -> tuple[str, list[dict[str, str]]]:
    text = require_file(LAB_SOURCE).decode("utf-8")
    match = R_CHUNK_RE.search(text)
    if not match:
        raise RuntimeError("labelled executable R chunk not found exactly once")
    if len(R_CHUNK_RE.findall(text)) != 1:
        raise RuntimeError("labelled executable R chunk is not unique")
    if text.count(PLACEHOLDER) != 1:
        raise RuntimeError("execution-table placeholder is not unique")
    r_bytes = match.group(1).encode("utf-8")
    script = work / "o009_lab_convergence_mc.R"
    script.write_bytes(r_bytes)
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env["R_USER"] = str(work)
    result = subprocess.run(
        [str(R_SCRIPT), "--vanilla", str(script)],
        cwd=work,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"R execution failed: {result.stderr.strip()}")
    if result.stderr.strip():
        raise RuntimeError(f"unexpected R stderr: {result.stderr.strip()}")
    rows = list(csv.DictReader(result.stdout.splitlines()))
    expected_fields = [
        "n",
        "seed",
        "estimate",
        "exact_value",
        "signed_error",
        "absolute_error",
    ]
    if not rows or list(rows[0]) != expected_fields:
        raise RuntimeError("R CSV header mismatch")
    if [row["n"] for row in rows] != ["10", "1000", "1000000"]:
        raise RuntimeError("R CSV n sequence mismatch")
    if [row["seed"] for row in rows] != ["12341", "12342", "12342"]:
        raise RuntimeError("R CSV seed sequence mismatch")
    for row in rows:
        if row["exact_value"] != "0.250000000000":
            raise RuntimeError("R CSV exact value mismatch")
        for key in ("estimate", "signed_error", "absolute_error"):
            float(row[key])
    return text, rows


def markdown_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "| n | benih | taksiran | nilai eksak | galat bertanda | galat mutlak |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {n} | {seed} | {estimate} | {exact_value} | "
            "{signed_error} | {absolute_error} |".format(**row)
        )
    return "\n".join(lines)


def pandoc_lab_text(text: str) -> str:
    """Convert the one admitted R Markdown fence to Pandoc attributes."""
    opening = "```{r o009_lab_convergence_mc, echo=TRUE}"
    replacement = "``` {#o009_lab_convergence_mc .r}"
    if text.count(opening) != 1:
        raise RuntimeError("expected exactly one admitted R Markdown fence")
    return text.replace(opening, replacement, 1)


def build_theory_unit(stage: Path, unit: dict[str, object]) -> None:
    _, target_path = theory_paths(unit)
    rel = Path(str(unit["rel"]))
    base_url = urllib.parse.urljoin(RANDOM_BASE_URL, rel.as_posix())
    soup = BeautifulSoup(require_file(target_path).decode("utf-8"), "lxml")
    mathjax = soup.find("script", id="MathJax-script")
    if mathjax is None:
        raise RuntimeError("MathJax script marker missing")
    mathjax["src"] = "../MathJax/tex-svg.js"
    extra_css = soup.new_tag("link", rel="stylesheet", href="../reader.css")
    soup.head.append(extra_css)
    local_pages = {
        urllib.parse.urljoin(RANDOM_BASE_URL, Path(str(item["rel"])).as_posix()): Path(str(item["rel"]))
        for item in THEORY_UNITS
    }
    for metadata_link in soup.select("link[href]"):
        rel_values = {str(value).lower() for value in (metadata_link.get("rel") or [])}
        if rel_values & {"stylesheet", "icon"}:
            continue
        href = str(metadata_link.get("href", ""))
        if href and not urllib.parse.urlparse(href).scheme:
            metadata_link["href"] = urllib.parse.urljoin(base_url, href)
    for anchor in soup.select("a[href]"):
        href = str(anchor.get("href", ""))
        corrections = dict(unit["fragment_corrections"])
        if href in corrections:
            anchor["href"] = corrections[href]
            continue
        match = re.fullmatch(r"JavaScript:openAncillary\(['\"]([^'\"]+)['\"]\)", href)
        if match:
            anchor["href"] = urllib.parse.urljoin(base_url, match.group(1))
            continue
        parsed = urllib.parse.urlparse(href)
        if href.startswith("#") or parsed.scheme or not href:
            continue
        resolved = urllib.parse.urljoin(base_url, href)
        resolved_page = urllib.parse.urlunparse(urllib.parse.urlparse(resolved)._replace(fragment=""))
        if resolved_page in local_pages:
            local_target = local_pages[resolved_page]
            relative_target = os.path.relpath(local_target, rel.parent).replace(os.sep, "/")
            anchor["href"] = relative_target + (f"#{parsed.fragment}" if parsed.fragment else "")
        else:
            anchor["href"] = resolved
    official_url = urllib.parse.urljoin(RANDOM_BASE_URL, rel.as_posix())
    source_title = str(unit["source_title"])
    rights_id = str(unit["rights_id"])
    edition_links = []
    for item in THEORY_UNITS:
        local_target = Path(str(item["rel"]))
        relative_target = os.path.relpath(local_target, rel.parent).replace(os.sep, "/")
        edition_links.append(f'<a href="{relative_target}">{item["nav_label"]}</a>')
    edition_links.append(
        f'<a href="{os.path.relpath(Path("labs/01-konvergensi-monte-carlo.html"), rel.parent).replace(os.sep, "/")}">'
        "Laboratorium Monte Carlo</a>"
    )
    index_href = os.path.relpath(Path("index.html"), rel.parent).replace(os.sep, "/")
    attribution = BeautifulSoup(
        f"""<aside class="component-attribution" id="{rights_id}">
<strong>Asal komponen.</strong> Terjemahan halaman <cite>{source_title}</cite>
karya Kyle Siegrist, dari cuplikan situs Random bertanggal 13 Maret 2026.
Halaman resmi Random saat ini memuat saksi CC BY 2.0 pada beranda dan
CC BY 1.0 pada halaman Credits; keduanya mengizinkan adaptasi dengan
atribusi. <a href="{official_url}">Baca sumber resmi</a>.
</aside><nav aria-label="Navigasi edisi"><a href="{index_href}">Beranda edisi</a> ·
{' · '.join(edition_links)}</nav>""",
        "lxml",
    )
    header = soup.find("header")
    if header is None:
        raise RuntimeError("theory header missing")
    insertion_point = header
    for node in list(attribution.body.contents):
        insertion_point.insert_after(node)
        insertion_point = node
    output = stage / rel
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(str(soup), encoding="utf-8", newline="\n")


def build_theory(stage: Path) -> None:
    for unit in THEORY_UNITS:
        build_theory_unit(stage, unit)


def run_pandoc(source: Path, output: Path, css: str, mathjax: str | None = None) -> None:
    command = [
        PANDOC,
        str(source),
        "--standalone",
        "--from=markdown+fenced_divs+fenced_code_attributes+yaml_metadata_block",
        "--to=html5",
        f"--css={css}",
        "--toc",
        "--output",
        str(output),
    ]
    if mathjax:
        command.append(f"--mathjax={mathjax}")
    result = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc failed: {result.stderr.strip()}")
    output.write_bytes(output.read_bytes().replace(b"\r\n", b"\n"))


def copy_assets(stage: Path) -> None:
    mappings = {
        AUTH_RANDOM / "static" / "Screen.css": stage / "Screen.css",
        AUTH_RANDOM / "static" / "Basic.js": stage / "Basic.js",
        AUTH_RANDOM / "static" / "icons" / "Icon.svg": stage / "icons" / "Icon.svg",
        AUTH_RANDOM / "static" / "icons" / "DieBlue5.svg": stage / "icons" / "DieBlue5.svg",
        AUTH_RANDOM / "static" / "icons" / "DieGreen5.svg": stage / "icons" / "DieGreen5.svg",
        AUTH_RANDOM / "static" / "icons" / "DieRed5.svg": stage / "icons" / "DieRed5.svg",
        AUTH_RANDOM / "static" / "icons" / "Plus.svg": stage / "icons" / "Plus.svg",
        AUTH_RANDOM / "static" / "icons" / "Minus.svg": stage / "icons" / "Minus.svg",
        AUTH_RANDOM / "static" / "icons" / "Step.svg": stage / "icons" / "Step.svg",
        AUTH_RANDOM / "static" / "icons" / "Stop.svg": stage / "icons" / "Stop.svg",
        AUTH_RANDOM / "static" / "icons" / "Run.svg": stage / "icons" / "Run.svg",
        AUTH_RANDOM / "static" / "icons" / "Reset.svg": stage / "icons" / "Reset.svg",
        AUTH_RANDOM / "static" / "prob" / "Increasing1.png": stage / "prob" / "Increasing1.png",
        AUTH_RANDOM / "static" / "prob" / "Increasing2.png": stage / "prob" / "Increasing2.png",
        AUTH_RANDOM / "static" / "prob" / "Decreasing.png": stage / "prob" / "Decreasing.png",
        AUTH_RANDOM / "static" / "prob" / "InverseImage.png": stage / "prob" / "InverseImage.png",
        AUTH_RANDOM / "static" / "expect" / "ConvexFunction.png": stage / "expect" / "ConvexFunction.png",
        AUTH_RANDOM / "shared" / "MathJax" / "tex-svg.js": stage / "MathJax" / "tex-svg.js",
        AUTH_RANDOM / "shared" / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js": (
            stage / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js"
        ),
        AUTH_RANDOM / "shared" / "MathJax" / "LICENSE": stage / "licenses" / "MathJax-Apache-2.0.txt",
        SOURCE_CSS: stage / "reader.css",
    }
    if sha256(require_file(AUTH_RANDOM / "shared" / "MathJax" / "tex-svg.js")) != MATHJAX_SHA256:
        raise RuntimeError("MathJax hash changed")
    boldsymbol = AUTH_RANDOM / "shared" / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js"
    if sha256(require_file(boldsymbol)) != MATHJAX_BOLDSYMBOL_SHA256:
        raise RuntimeError("MathJax boldsymbol extension hash changed")
    for source, target in mappings.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def site_rows(site: Path) -> list[dict[str, object]]:
    excluded = {"PACKAGE_MANIFEST.csv", "BUILD_RECEIPT.json"}
    paths = [path for path in site.rglob("*") if path.is_file()]
    paths = [path for path in paths if path.relative_to(site).as_posix() not in excluded]
    paths.sort(key=lambda path: path.relative_to(site).as_posix().casefold())
    rows: list[dict[str, object]] = []
    for path in paths:
        data = path.read_bytes()
        rows.append(
            {
                "path": path.relative_to(site).as_posix(),
                "bytes": len(data),
                "sha256": sha256(data),
            }
        )
    return rows


def write_manifest(site: Path, r_rows: list[dict[str, str]]) -> None:
    rows = site_rows(site)
    manifest = site / "PACKAGE_MANIFEST.csv"
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["path", "bytes", "sha256"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    receipt = {
        "schema": "o009.reader-build.v2",
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_authority_manifest_sha256": RANDOM_MANIFEST_SHA256,
        "theory_units": [
            {
                "path": str(unit["rel"]),
                "authority_sha256": str(unit["authority_sha256"]),
                "target_sha256": sha256(require_file(theory_paths(unit)[1])),
            }
            for unit in THEORY_UNITS
        ],
        "lab_source_sha256": sha256(require_file(LAB_SOURCE)),
        "r_version": "R version 4.6.1 (2026-06-24 ucrt)",
        "r_rng": "Mersenne-Twister / Inversion / Rejection",
        "r_result_rows": r_rows,
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
        "manifest_sha256": sha256(manifest.read_bytes()),
    }
    (site / "BUILD_RECEIPT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify_site(site: Path, execute_r: bool = True) -> None:
    manifest = site / "PACKAGE_MANIFEST.csv"
    receipt_path = site / "BUILD_RECEIPT.json"
    if not manifest.is_file() or not receipt_path.is_file():
        raise RuntimeError("site manifest or build receipt missing")
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        expected = list(csv.DictReader(stream))
    actual = site_rows(site)
    if expected != [{key: str(value) for key, value in row.items()} for row in actual]:
        raise RuntimeError("site manifest does not match current files")
    receipt = json.loads(receipt_path.read_text("utf-8"))
    if receipt["manifest_sha256"] != sha256(manifest.read_bytes()):
        raise RuntimeError("build receipt does not bind manifest")
    html_paths = sorted(site.rglob("*.html"), key=lambda path: path.as_posix().casefold())
    for path in html_paths:
        data = path.read_bytes()
        text = data.decode("utf-8")
        soup = BeautifulSoup(text, "lxml")
        if soup.html is None or soup.html.get("lang") != "id-ID":
            raise RuntimeError(f"missing lang=id-ID: {path}")
        ids = [str(tag["id"]) for tag in soup.select("[id]")]
        if len(ids) != len(set(ids)):
            raise RuntimeError(f"duplicate id: {path}")
        for tag in soup.select("a[href], img[src], script[src], link[href]"):
            attribute = "href" if tag.has_attr("href") else "src"
            ref = str(tag.get(attribute, ""))
            parsed = urllib.parse.urlparse(ref)
            if not ref or parsed.scheme:
                continue
            if not parsed.path and parsed.fragment:
                fragment = urllib.parse.unquote(parsed.fragment)
                if soup.find(id=fragment) is None:
                    raise RuntimeError(f"missing same-page fragment: {path} -> {ref}")
                continue
            target = (path.parent / urllib.parse.unquote(parsed.path)).resolve()
            try:
                target.relative_to(site.resolve())
            except ValueError as exc:
                raise RuntimeError(f"local reference escapes site: {path} -> {ref}") from exc
            if not target.is_file():
                raise RuntimeError(f"missing local reference: {path} -> {ref}")
            if parsed.fragment:
                target_soup = BeautifulSoup(target.read_text("utf-8"), "lxml")
                if target_soup.find(id=parsed.fragment) is None:
                    raise RuntimeError(f"missing local fragment: {path} -> {ref}")
    for css_path in sorted(site.rglob("*.css"), key=lambda path: path.as_posix().casefold()):
        css_text = css_path.read_text("utf-8")
        for _, ref in CSS_URL_RE.findall(css_text):
            parsed = urllib.parse.urlparse(ref.strip())
            if not parsed.path or parsed.scheme or ref.startswith("data:"):
                continue
            target = (css_path.parent / urllib.parse.unquote(parsed.path)).resolve()
            try:
                target.relative_to(site.resolve())
            except ValueError as exc:
                raise RuntimeError(f"CSS reference escapes site: {css_path} -> {ref}") from exc
            if not target.is_file():
                raise RuntimeError(f"missing CSS asset: {css_path} -> {ref}")
    lab_html = site / "labs" / "01-konvergensi-monte-carlo.html"
    lab_soup = BeautifulSoup(lab_html.read_text("utf-8"), "lxml")
    executable = lab_soup.find(id="o009_lab_convergence_mc")
    if executable is None or executable.name not in {"div", "pre", "code"}:
        raise RuntimeError("rendered lab lacks the stable executable code-block id")
    code = executable.find("code") if executable.name != "code" else executable
    if code is None or "set.seed(12341)" not in code.get_text():
        raise RuntimeError("rendered lab R code is not a copyable code block")
    if "```{r" in lab_html.read_text("utf-8") or ">true<" in lab_html.read_text("utf-8"):
        raise RuntimeError("raw R fence or malformed author metadata leaked into rendered lab")
    theory_text = "\n".join((site / str(unit["rel"])).read_text("utf-8") for unit in THEORY_UNITS)
    boldsymbol_target = site / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js"
    if "\\boldsymbol" in theory_text and not boldsymbol_target.is_file():
        raise RuntimeError("required MathJax boldsymbol autoload extension is missing")
    joined = b"\n".join(path.read_bytes() for path in site.rglob("*") if path.is_file())
    forbidden = (b"googletagmanager", b"C:\\Users\\", b"C:/Users/", b"Floris")
    hits = [value.decode("ascii") for value in forbidden if value in joined]
    if hits:
        raise RuntimeError(f"privacy/runtime residue in site: {hits}")
    if execute_r:
        with tempfile.TemporaryDirectory(prefix="o009-check-") as temp:
            _, rows = extract_and_run_lab(Path(temp))
        if rows != receipt["r_result_rows"]:
            raise RuntimeError("fresh R execution differs from build receipt")


def build() -> None:
    validate_theory_translation()
    ROOT.joinpath("build").mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="o009-first-boundary-", dir=ROOT / "build"))
    try:
        with tempfile.TemporaryDirectory(prefix="o009-r-") as temp:
            lab_text, r_rows = extract_and_run_lab(Path(temp))
        copy_assets(stage)
        build_theory(stage)
        processed_lab = stage / "lab-build-input.md"
        processed_lab.write_text(
            pandoc_lab_text(lab_text.replace(PLACEHOLDER, markdown_table(r_rows))),
            encoding="utf-8",
            newline="\n",
        )
        lab_output = stage / "labs" / "01-konvergensi-monte-carlo.html"
        lab_output.parent.mkdir(parents=True, exist_ok=True)
        run_pandoc(processed_lab, lab_output, "../reader.css", "../MathJax/tex-svg.js")
        processed_lab.unlink()
        run_pandoc(SOURCE_INDEX, stage / "index.html", "reader.css")
        write_manifest(stage, r_rows)
        verify_site(stage)
        site_resolved = SITE.resolve()
        build_resolved = (ROOT / "build").resolve()
        try:
            site_resolved.relative_to(build_resolved)
        except ValueError as exc:
            raise RuntimeError("site target escapes build directory") from exc
        if SITE.exists():
            if SITE.is_symlink():
                raise RuntimeError("refusing to replace linked site directory")
            shutil.rmtree(SITE)
        os.replace(stage, SITE)
        receipt = json.loads((SITE / "BUILD_RECEIPT.json").read_text("utf-8"))
        print(
            f"PASS files={receipt['file_count']} bytes={receipt['total_bytes']} "
            f"manifest_sha256={receipt['manifest_sha256']}"
        )
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate_theory_translation()
        verify_site(SITE)
        receipt = json.loads((SITE / "BUILD_RECEIPT.json").read_text("utf-8"))
        print(
            f"PASS files={receipt['file_count']} bytes={receipt['total_bytes']} "
            f"manifest_sha256={receipt['manifest_sha256']}"
        )
    else:
        build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
