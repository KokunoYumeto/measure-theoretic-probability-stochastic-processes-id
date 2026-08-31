#!/usr/bin/env python3
"""Build a reader-first checkpoint PDF from the validated HTML site."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pypdf
from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "build" / "site"
OUTPUT = ROOT / "output" / "pdf"
RUNTIME_DEPENDENCIES = Path(os.environ.get(
    "O009_RUNTIME_DEPENDENCIES",
    str(
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
    ),
))
NODE = Path(os.environ.get(
    "O009_NODE",
    str(RUNTIME_DEPENDENCIES / "node" / "bin" / "node.exe"),
))
_task_local_node_modules = ROOT / "runtime" / "pdf-node" / "node_modules"
NODE_MODULES = Path(os.environ.get(
    "O009_NODE_MODULES",
    str(
        _task_local_node_modules
        if (_task_local_node_modules / "playwright" / "package.json").is_file()
        else RUNTIME_DEPENDENCIES / "node" / "node_modules"
    ),
))
CHROME = Path(os.environ.get(
    "O009_CHROME",
    str(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe"),
))
RENDERER = ROOT / "scripts" / "render_reader_pdf.cjs"
_bundled_pdftotext = (
    RUNTIME_DEPENDENCIES
    / "native"
    / "poppler"
    / "Library"
    / "bin"
    / "pdftotext.exe"
)
PDFTOTEXT = Path(os.environ.get(
    "O009_PDFTOTEXT",
    str(_bundled_pdftotext if _bundled_pdftotext.is_file() else shutil.which("pdftotext") or "pdftotext"),
))
SITE_MANIFEST = SITE / "PACKAGE_MANIFEST.csv"
SITE_RECEIPT = SITE / "BUILD_RECEIPT.json"
FRONT_PAGES = 4
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra."
EDITION_DATE_TEXT = "27 Agustus 2026"
EDITION_VERSION_PREFIX = "2026.08.27-checkpoint."
EDITION_PDF_DATE = "D:20260827000000+02'00'"


def normalize_chromium_pdf_metadata(path: Path) -> dict[str, object]:
    """Replace Chromium's run-time Info dates without changing PDF offsets.

    Chromium writes one CreationDate and one ModDate into each printed master.
    Their values have fixed width but otherwise encode the wall-clock render
    time, so two mathematically identical renders differ byte-for-byte.  An
    equal-length replacement preserves every cross-reference offset and makes
    the master suitable for the deterministic incremental finalization below.
    """
    data = path.read_bytes()
    original_length = len(data)
    fixed_date = EDITION_PDF_DATE.encode("ascii")
    counts: dict[str, int] = {}
    for key in (b"CreationDate", b"ModDate"):
        pattern = re.compile(
            rb"/" + key + rb" \(D:\d{14}[+-]\d{2}'\d{2}'\)"
        )
        replacement = b"/" + key + b" (" + fixed_date + b")"
        data, count = pattern.subn(replacement, data)
        if count != 1:
            raise RuntimeError(
                f"Expected exactly one Chromium {key.decode()} entry in "
                f"{path.name}; found {count}"
            )
        counts[key.decode("ascii")] = count
    if len(data) != original_length:
        raise RuntimeError("Chromium metadata normalization changed PDF length")
    path.write_bytes(data)
    return {
        "fixed_date": EDITION_PDF_DATE,
        "replacement_counts": counts,
        "byte_length_preserved": path.stat().st_size == original_length,
    }


@dataclass(frozen=True)
class Unit:
    kind: str
    title: str
    relpath: str


CHECKPOINT_33_UNITS = (
    Unit("Teori", "Konvergensi kejadian dan peubah acak", "prob/Convergence.html"),
    Unit("Teori", "Probabilitas ditinjau kembali", "prob/Probability2.html"),
    Unit("Teori", "Proses stokastik", "prob/Processes.html"),
    Unit("Teori", "Filtrasi dan waktu henti", "prob/Stop.html"),
    Unit("Teori", "Konvergensi dalam distribusi", "dist/Convergence.html"),
    Unit("Teori", "Nilai harapan bersyarat ditinjau kembali", "expect/Conditional2.html"),
    Unit("Teori", "Peubah terintegralkan seragam", "expect/Uniform.html"),
    Unit("Teori", "Kernel dan operator", "expect/Kernels.html"),
    Unit("Ikhtisar", "Ikhtisar martingal", "martingales/index.html"),
    Unit("Teori", "Pendahuluan martingal", "martingales/Introduction.html"),
    Unit("Teori", "Sifat dan konstruksi martingal", "martingales/Properties.html"),
    Unit("Teori", "Waktu henti martingal", "martingales/Stop.html"),
    Unit("Teori", "Pertidaksamaan martingal", "martingales/Inequalities.html"),
    Unit("Teori", "Konvergensi martingal", "martingales/Convergence.html"),
    Unit("Teori", "Martingal mundur", "martingales/Backwards.html"),
    Unit("Ikhtisar", "Ikhtisar proses Markov", "markov/index.html"),
    Unit("Teori", "Proses Markov umum", "markov/General.html"),
    Unit("Teori", "Rantai Markov waktu diskret", "markov/Discrete.html"),
    Unit("Teori", "Keadaan transien dan rekuren", "markov/Recurrence.html"),
    Unit("Teori", "Periodisitas", "markov/Periodicity.html"),
    Unit("Teori", "Distribusi invarian dan limit", "markov/Limiting.html"),
    Unit("Laboratorium", "Simulasi rantai Markov", "labs/02-simulasi-rantai-markov.html"),
    Unit("Laboratorium", "Konvergensi Monte Carlo", "labs/01-konvergensi-monte-carlo.html"),
    Unit("Teori", "Distribusi tanpa ingatan (QuantEcon)", "quantecon/lectures/memoryless.html"),
    Unit("Teori", "Proses Poisson (QuantEcon)", "quantecon/lectures/poisson.html"),
    Unit("Teori", "Sifat Markov (QuantEcon)", "quantecon/lectures/markov_prop.html"),
    Unit("Teori", "Persamaan Kolmogorov mundur (QuantEcon)", "quantecon/lectures/kolmogorov_bwd.html"),
    Unit("Teori", "Persamaan Kolmogorov maju (QuantEcon)", "quantecon/lectures/kolmogorov_fwd.html"),
    Unit("Teori", "Semigrup dan generator (QuantEcon)", "quantecon/lectures/generators.html"),
    Unit(
        "Teori",
        "Semigrup Markov yang kontinu seragam (QuantEcon)",
        "quantecon/lectures/uc_mc_semigroups.html",
    ),
    Unit(
        "Teori",
        "Stasioneritas dan ergodisitas (QuantEcon)",
        "quantecon/lectures/ergodicity.html",
    ),
    Unit(
        "Teori",
        "Proses Poisson pada ruang umum",
        "poisson/General.html",
    ),
    Unit("Ikhtisar", "Ikhtisar gerak Brown", "brown/index.html"),
    Unit(
        "Teori",
        "Gerak Brown standar",
        "brown/Standard.html",
    ),
    Unit(
        "Teori",
        "Gerak Brown dengan hanyutan",
        "brown/Drift.html",
    ),
    Unit(
        "Teori",
        "Jembatan Brown",
        "brown/Bridge.html",
    ),
    Unit(
        "Teori",
        "Gerak Brown geometrik",
        "brown/Geometric.html",
    ),
    Unit(
        "Jembatan asli",
        "Konstruksi Kolmogorov dan proses kanonik",
        "original/01-konstruksi-kolmogorov.html",
    ),
    Unit(
        "Jembatan asli",
        "Keterukuran proses dan hukum lintasan",
        "original/02-keterukuran-proses-dan-hukum-lintasan.html",
    ),
)
CHECKPOINT_34_ADDITIONAL_UNITS = (
    Unit(
        "Jembatan asli",
        "Distribusi bersyarat reguler dan disiplin versi",
        "original/03-probabilitas-bersyarat-reguler.html",
    ),
)
CHECKPOINT_35_ADDITIONAL_UNITS = (
    Unit(
        "Jembatan asli",
        "Audit hipotesis untuk proses stokastik",
        "original/04-audit-hipotesis-proses-stokastik.html",
    ),
)
CHECKPOINT_36_ADDITIONAL_UNITS = (
    Unit(
        "Laboratorium",
        "Mode konvergensi dan pembanding LLN/CLT",
        "labs/03-konvergensi-mode-dan-lln-clt.html",
    ),
    Unit(
        "Laboratorium",
        "Nilai harapan bersyarat, filtrasi, dan penghentian opsional",
        "labs/04-nilai-harapan-bersyarat-martingal.html",
    ),
)
CHECKPOINT_37_ADDITIONAL_UNITS = (
    Unit(
        "Laboratorium",
        "Gerak Brown: Donsker, variasi kuadratik, dan waktu kena",
        "labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html",
    ),
)
CHECKPOINT_38_ADDITIONAL_UNITS = (
    Unit("Penguasaan", "Penguasaan konvergensi 01–02", "mastery/01-konvergensi-01-02.html"),
    Unit("Penguasaan", "Penguasaan konvergensi 03–04", "mastery/02-konvergensi-03-04.html"),
    Unit("Penguasaan", "Penguasaan konvergensi 05", "mastery/03-konvergensi-05.html"),
    Unit("Penguasaan", "Penguasaan nilai harapan bersyarat dan kernel 01–02", "mastery/04-bersyarat-kernel-01-02.html"),
    Unit("Penguasaan", "Penguasaan nilai harapan bersyarat dan kernel 03", "mastery/05-bersyarat-kernel-03.html"),
    Unit("Penguasaan", "Penguasaan martingal 01–02", "mastery/06-martingal-01-02.html"),
    Unit("Penguasaan", "Penguasaan martingal 03–04", "mastery/07-martingal-03-04.html"),
    Unit("Penguasaan", "Penguasaan martingal 05", "mastery/08-martingal-05.html"),
    Unit("Penguasaan", "Penguasaan konstruksi ukuran acak Poisson", "mastery/09-poisson-konstruksi-01.html"),
    Unit("Penguasaan", "Penguasaan gerak Brown 01", "mastery/10-brown-01.html"),
    Unit("Penguasaan", "Penguasaan gerak Brown 02", "mastery/11-brown-02.html"),
    Unit("Penguasaan", "Penguasaan gerak Brown 03–04", "mastery/12-brown-03-04.html"),
    Unit("Penguasaan", "Penguasaan gerak Brown 05–06", "mastery/13-brown-05-06.html"),
    Unit("Penguasaan", "Penguasaan gerak Brown 07", "mastery/14-brown-07.html"),
    Unit("Penilaian", "Penilaian kumulatif — Formulir A", "assessments/01-formulir-kumulatif-a.html"),
    Unit("Penilaian", "Penilaian kumulatif — Formulir B", "assessments/02-formulir-kumulatif-b.html"),
)
UNITS = CHECKPOINT_33_UNITS
QUANTECON_CANONICAL_UNIT_COUNT = 8
RANDOM_CANONICAL_PAGE_COUNT = 27
ORIGINAL_BRIDGE_ADMITTED_COUNT = 2
OVERVIEW_KIND = "Ikhtisar"
THEORY_KIND = "Teori"
ORIGINAL_BRIDGE_KIND = "Jembatan asli"
RANDOM_RELPATH_PREFIXES = (
    "prob/",
    "dist/",
    "expect/",
    "martingales/",
    "markov/",
    "poisson/",
    "brown/",
)


def configure_checkpoint(checkpoint: int) -> None:
    """Select checkpoint-specific reader bytes without changing checkpoint 33."""
    global UNITS
    global ORIGINAL_BRIDGE_ADMITTED_COUNT
    global EDITION_DATE_TEXT
    global EDITION_VERSION_PREFIX
    global EDITION_PDF_DATE

    if checkpoint >= 38:
        UNITS = (
            CHECKPOINT_33_UNITS
            + CHECKPOINT_34_ADDITIONAL_UNITS
            + CHECKPOINT_35_ADDITIONAL_UNITS
            + CHECKPOINT_36_ADDITIONAL_UNITS
            + CHECKPOINT_37_ADDITIONAL_UNITS
            + CHECKPOINT_38_ADDITIONAL_UNITS
        )
        ORIGINAL_BRIDGE_ADMITTED_COUNT = 4
        EDITION_DATE_TEXT = "30 Agustus 2026"
        EDITION_VERSION_PREFIX = "2026.08.30-checkpoint."
        EDITION_PDF_DATE = "D:20260830000000+02'00'"
    elif checkpoint >= 37:
        UNITS = (
            CHECKPOINT_33_UNITS
            + CHECKPOINT_34_ADDITIONAL_UNITS
            + CHECKPOINT_35_ADDITIONAL_UNITS
            + CHECKPOINT_36_ADDITIONAL_UNITS
            + CHECKPOINT_37_ADDITIONAL_UNITS
        )
        ORIGINAL_BRIDGE_ADMITTED_COUNT = 4
        EDITION_DATE_TEXT = "30 Agustus 2026"
        EDITION_VERSION_PREFIX = "2026.08.30-checkpoint."
        EDITION_PDF_DATE = "D:20260830000000+02'00'"
    elif checkpoint >= 36:
        UNITS = (
            CHECKPOINT_33_UNITS
            + CHECKPOINT_34_ADDITIONAL_UNITS
            + CHECKPOINT_35_ADDITIONAL_UNITS
            + CHECKPOINT_36_ADDITIONAL_UNITS
        )
        ORIGINAL_BRIDGE_ADMITTED_COUNT = 4
        EDITION_DATE_TEXT = "29 Agustus 2026"
        EDITION_VERSION_PREFIX = "2026.08.29-checkpoint."
        EDITION_PDF_DATE = "D:20260829000000+02'00'"
    elif checkpoint >= 35:
        UNITS = (
            CHECKPOINT_33_UNITS
            + CHECKPOINT_34_ADDITIONAL_UNITS
            + CHECKPOINT_35_ADDITIONAL_UNITS
        )
        ORIGINAL_BRIDGE_ADMITTED_COUNT = 4
        EDITION_DATE_TEXT = "29 Agustus 2026"
        EDITION_VERSION_PREFIX = "2026.08.29-checkpoint."
        EDITION_PDF_DATE = "D:20260829000000+02'00'"
    elif checkpoint >= 34:
        UNITS = CHECKPOINT_33_UNITS + CHECKPOINT_34_ADDITIONAL_UNITS
        ORIGINAL_BRIDGE_ADMITTED_COUNT = 3
        EDITION_DATE_TEXT = "29 Agustus 2026"
        EDITION_VERSION_PREFIX = "2026.08.29-checkpoint."
        EDITION_PDF_DATE = "D:20260829000000+02'00'"
    else:
        UNITS = CHECKPOINT_33_UNITS
        ORIGINAL_BRIDGE_ADMITTED_COUNT = 2
        EDITION_DATE_TEXT = "27 Agustus 2026"
        EDITION_VERSION_PREFIX = "2026.08.27-checkpoint."
        EDITION_PDF_DATE = "D:20260827000000+02'00'"


def is_random_relpath(relpath: str) -> bool:
    return relpath.startswith(RANDOM_RELPATH_PREFIXES)


def scope_counts() -> dict[str, int]:
    original_bridge = sum(unit.kind == ORIGINAL_BRIDGE_KIND for unit in UNITS)
    substantive_theory = sum(
        unit.kind in {THEORY_KIND, ORIGINAL_BRIDGE_KIND}
        for unit in UNITS
    )
    overview = sum(unit.kind == OVERVIEW_KIND for unit in UNITS)
    labs = sum(unit.kind == "Laboratorium" for unit in UNITS)
    mastery = sum(unit.kind == "Penguasaan" for unit in UNITS)
    assessments = sum(unit.kind == "Penilaian" for unit in UNITS)
    quantecon = sum("quantecon/" in unit.relpath for unit in UNITS)
    random_substantive = sum(
        unit.kind == THEORY_KIND and is_random_relpath(unit.relpath)
        for unit in UNITS
    )
    random_selected_pages = sum(
        is_random_relpath(unit.relpath)
        for unit in UNITS
    )
    return {
        "substantive_theory": substantive_theory,
        "overview": overview,
        "labs": labs,
        "mastery": mastery,
        "assessments": assessments,
        "quantecon": quantecon,
        "original_bridge": original_bridge,
        "random_substantive": random_substantive,
        "random_selected_pages": random_selected_pages,
    }


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def identity(path: Path, label: str) -> dict[str, object]:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Missing or linked render input: {label}")
    return {
        "label": label,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def validate_site_inputs() -> dict[str, object]:
    """Bind the complete live site inventory and every printed unit."""
    manifest_id = identity(SITE_MANIFEST, "build/site/PACKAGE_MANIFEST.csv")
    receipt_id = identity(SITE_RECEIPT, "build/site/BUILD_RECEIPT.json")
    receipt = json.loads(SITE_RECEIPT.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise RuntimeError("Site build receipt is not a JSON object")
    if receipt.get("manifest_sha256") != manifest_id["sha256"]:
        raise RuntimeError("Site build receipt does not bind the live manifest")

    with SITE_MANIFEST.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["path", "bytes", "sha256"]:
            raise RuntimeError("Site manifest columns differ")
        listed = list(reader)

    seen: set[str] = set()
    for row in listed:
        raw = str(row.get("path", ""))
        candidate = Path(raw)
        digest = str(row.get("sha256", ""))
        try:
            count = int(str(row.get("bytes", "")))
        except ValueError as exc:
            raise RuntimeError(f"Invalid site-manifest byte count: {raw!r}") from exc
        if (
            not raw
            or raw in seen
            or candidate.is_absolute()
            or candidate.drive
            or candidate.as_posix() != raw
            or any(part in {"", ".", ".."} for part in candidate.parts)
            or count < 0
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
        ):
            raise RuntimeError(f"Unsafe or invalid site-manifest row: {row!r}")
        seen.add(raw)

    entries = list(SITE.rglob("*"))
    linked = [relative(path) for path in entries if path.is_symlink()]
    if linked:
        raise RuntimeError(f"Site contains linked paths: {linked}")
    excluded = {"PACKAGE_MANIFEST.csv", "BUILD_RECEIPT.json"}
    actual_paths = [
        path
        for path in entries
        if path.is_file() and path.relative_to(SITE).as_posix() not in excluded
    ]
    actual_paths.sort(key=lambda path: path.relative_to(SITE).as_posix().casefold())
    actual = [
        {
            "path": path.relative_to(SITE).as_posix(),
            "bytes": str(path.stat().st_size),
            "sha256": sha256(path),
        }
        for path in actual_paths
    ]
    if listed != actual:
        listed_map = {row["path"]: row for row in listed}
        actual_map = {row["path"]: row for row in actual}
        raise RuntimeError(
            "Site manifest differs from live bytes: "
            f"missing={sorted(set(listed_map) - set(actual_map))}; "
            f"unexpected={sorted(set(actual_map) - set(listed_map))}; "
            f"changed={sorted(path for path in set(listed_map) & set(actual_map) if listed_map[path] != actual_map[path])}"
        )
    if receipt.get("file_count") != len(actual) or receipt.get("total_bytes") != sum(
        int(row["bytes"]) for row in actual
    ):
        raise RuntimeError("Site build receipt totals differ from the live inventory")

    by_path = {row["path"]: row for row in actual}
    units: list[dict[str, object]] = []
    for unit in UNITS:
        row = by_path.get(unit.relpath)
        if row is None:
            raise RuntimeError(f"Printed unit is absent from the site manifest: {unit.relpath}")
        units.append(
            {
                "relpath": unit.relpath,
                "bytes": int(row["bytes"]),
                "sha256": row["sha256"],
            }
        )
    stylesheet = by_path.get("reader.css")
    if stylesheet is None:
        raise RuntimeError("Shared reader stylesheet is absent from the site manifest")
    return {
        "manifest": manifest_id,
        "build_receipt": receipt_id,
        "file_count": len(actual),
        "total_bytes": sum(int(row["bytes"]) for row in actual),
        "reader_css": {
            "label": "build/site/reader.css",
            "bytes": int(stylesheet["bytes"]),
            "sha256": stylesheet["sha256"],
        },
        "printed_units": units,
    }


def validate_render_runtime() -> dict[str, object]:
    playwright_package = NODE_MODULES / "playwright" / "package.json"
    playwright_core_package = NODE_MODULES / "playwright-core" / "package.json"
    node_id = identity(NODE, "runtime/node.exe")
    chrome_id = identity(CHROME, "runtime/chrome.exe")
    renderer_id = identity(RENDERER, "scripts/render_reader_pdf.cjs")
    pdftotext_id = identity(PDFTOTEXT, "runtime/pdftotext.exe")
    playwright_id = identity(playwright_package, "runtime/playwright/package.json")
    playwright_core_id = identity(
        playwright_core_package, "runtime/playwright-core/package.json"
    )
    node_version = subprocess.run(
        [str(NODE), "--version"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    ).stdout.strip()
    playwright_id["version"] = json.loads(
        playwright_package.read_text(encoding="utf-8")
    )["version"]
    playwright_core_id["version"] = json.loads(
        playwright_core_package.read_text(encoding="utf-8")
    )["version"]
    node_id["version"] = node_version
    return {
        "node": node_id,
        "chrome": chrome_id,
        "renderer": renderer_id,
        "pdftotext": pdftotext_id,
        "playwright": playwright_id,
        "playwright_core": playwright_core_id,
    }


def start_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    def handler(*args: object, **kwargs: object) -> QuietHandler:
        return QuietHandler(*args, directory=str(SITE), **kwargs)

    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def run_master_renderer(
    *,
    frontmatter: Path,
    output: Path,
    base_url: str,
    job_path: Path,
) -> dict[str, object]:
    job = {
        "mode": "master",
        "frontmatterUrl": frontmatter.as_uri(),
        "output": str(output),
        "units": [
            {
                "kind": unit.kind,
                "title": unit.title,
                "url": f"{base_url}/{unit.relpath}",
            }
            for unit in UNITS
        ],
    }
    job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    environment = os.environ.copy()
    environment["NODE_PATH"] = str(NODE_MODULES)
    environment["O009_CHROME"] = str(CHROME)
    try:
        result = subprocess.run(
            [str(NODE), str(RENDERER), str(job_path)],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=1200,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        raise RuntimeError(
            "Reader PDF renderer failed with "
            f"exit code {exc.returncode}; stderr={stderr!r}; stdout={stdout!r}"
        ) from exc
    return json.loads(result.stdout)


def normalized_pdf_text(value: str) -> str:
    return " ".join(
        unicodedata.normalize("NFKC", value.replace("\u00ad", "")).casefold().split()
    )


def unit_marker(index: int) -> str:
    return f"O009-U{index:03d}"


def locate_unit_starts(path: Path) -> list[int]:
    """Locate each forced unit boundary in the single Chromium document."""
    reader = PdfReader(path)
    pages = [normalized_pdf_text(page.extract_text() or "") for page in reader.pages]
    starts: list[int] = []
    search_from = FRONT_PAGES
    for number, unit in enumerate(UNITS, start=1):
        needle = normalized_pdf_text(unit_marker(number))
        found = next(
            (
                index
                for index in range(search_from, len(pages))
                if needle in pages[index]
            ),
            None,
        )
        if found is None:
            raise RuntimeError(
                "Could not locate injected unit-boundary marker in master PDF: "
                f"{unit_marker(number)} ({unit.title!r})"
            )
        starts.append(found + 1)
        search_from = found + 1
    if starts[0] != FRONT_PAGES + 1:
        raise RuntimeError(
            "Single-document pagination did not preserve the four-page front matter: "
            f"first unit starts on page {starts[0]}"
        )
    if starts != sorted(set(starts)):
        raise RuntimeError(f"Unit starts are not strictly increasing: {starts}")
    return starts


def unit_page_counts(path: Path, starts: list[int]) -> list[int]:
    total = len(PdfReader(path).pages)
    return [
        (starts[index + 1] if index + 1 < len(starts) else total + 1) - start
        for index, start in enumerate(starts)
    ]


def make_frontmatter(path: Path, starts: list[int], checkpoint: int) -> None:
    row_markup = [
        f"<tr><td class='num'>{number}</td><td><span class='kind'>{html.escape(unit.kind)}</span>"
        f"{html.escape(unit.title)}</td><td class='page'>{page}</td></tr>"
        for number, (unit, page) in enumerate(zip(UNITS, starts, strict=True), start=1)
    ]
    toc_split = (len(row_markup) + 1) // 2
    toc_rows_left = "\n".join(row_markup[:toc_split])
    toc_rows_right = "\n".join(row_markup[toc_split:])
    counts = scope_counts()
    theory_count = counts["substantive_theory"]
    overview_count = counts["overview"]
    quantecon_count = counts["quantecon"]
    original_bridge_count = counts["original_bridge"]
    lab_count = counts["labs"]
    mastery_count = counts["mastery"]
    assessment_count = counts["assessments"]
    lab_count_text = {2: "dua", 4: "empat", 5: "lima"}.get(
        lab_count,
        str(lab_count),
    )
    random_substantive_count = counts["random_substantive"]
    random_selected_pages = counts["random_selected_pages"]
    if quantecon_count > QUANTECON_CANONICAL_UNIT_COUNT:
        raise RuntimeError("QuantEcon reader count exceeds the canonical bounded selection")
    if original_bridge_count != ORIGINAL_BRIDGE_ADMITTED_COUNT:
        raise RuntimeError(
            "Original-bridge reader closure differs from the admitted seam count: "
            f"{original_bridge_count}"
        )
    if random_selected_pages != RANDOM_CANONICAL_PAGE_COUNT:
        raise RuntimeError(
            "Random reader closure differs from the 27-page canonical selection: "
            f"{random_selected_pages}"
        )
    if theory_count != (
        random_substantive_count + quantecon_count + original_bridge_count
    ):
        raise RuntimeError(
            "Substantive-theory decomposition differs from its component counts"
        )
    if len(UNITS) != (
        theory_count + overview_count + lab_count + mastery_count + assessment_count
    ):
        raise RuntimeError(
            "Reader components do not partition into theory, overview, labs, mastery, and assessments"
        )
    if original_bridge_count == 2:
        original_bridge_summary = (
            "Dua jembatan asli tentang perluasan Kolmogorov, proses koordinat "
            "kanonik, keterukuran proses, hukum lintasan, serta batas informasi "
            "FDD; seluruhnya memuat enam latihan penguasaan dengan petunjuk, "
            "jawaban, dan solusi lengkap."
        )
        original_bridge_remaining = (
            "Dua dari empat unit penghubung rigor sudah tersedia; dua unit "
            "penghubung tersisa, tiga laboratorium deterministik, 30 masalah "
            "terselesaikan tambahan, dua formulir kumulatif, dan pengikatan "
            "akhir O006 masih harus dilengkapi."
        )
        original_bridge_rights = (
            "<cite>Konstruksi Kolmogorov dan proses kanonik</cite> serta "
            "<cite>Keterukuran proses dan hukum lintasan</cite>, masing-masing "
            "dengan tiga latihan, enam petunjuk, tiga jawaban, dan tiga solusi: "
            "CC BY 4.0 di bawah "
            "<code>rights.o009.original.bridge.kolmogorov.cc-by-4.0</code> dan "
            "<code>rights.o009.original.bridge.process-measurability-path-law.cc-by-4.0</code>. "
            "Lisensi ini tidak melisensikan ulang materi <cite>Random</cite> atau "
            "<cite>QuantEcon</cite>."
        )
    elif original_bridge_count == 3:
        original_bridge_summary = (
            "Tiga jembatan asli—<cite>Konstruksi Kolmogorov dan proses "
            "kanonik</cite>, <cite>Keterukuran proses dan hukum lintasan</cite>, "
            "serta <cite>Distribusi bersyarat reguler dan disiplin versi</cite>—"
            "mencakup perluasan Kolmogorov, proses koordinat kanonik, "
            "keterukuran proses, hukum lintasan, batas informasi FDD, kernel "
            "probabilitas bersyarat, dan disiplin versi; seluruhnya memuat "
            "sembilan latihan penguasaan dengan petunjuk, jawaban, dan solusi lengkap."
        )
        original_bridge_remaining = (
            "Tiga dari empat unit penghubung rigor sudah tersedia; satu unit "
            "penghubung tersisa, tiga laboratorium deterministik, 27 masalah "
            "terselesaikan tambahan, dua formulir kumulatif, dan pengikatan "
            "akhir O006 masih harus dilengkapi."
        )
        original_bridge_rights = (
            "<cite>Konstruksi Kolmogorov dan proses kanonik</cite>, "
            "<cite>Keterukuran proses dan hukum lintasan</cite>, serta "
            "<cite>Distribusi bersyarat reguler dan disiplin versi</cite>, "
            "masing-masing dengan tiga latihan, enam petunjuk, tiga jawaban, dan "
            "tiga solusi: CC BY 4.0 di bawah "
            "<code>rights.o009.original.bridge.kolmogorov.cc-by-4.0</code>, "
            "<code>rights.o009.original.bridge.process-measurability-path-law.cc-by-4.0</code>, "
            "dan "
            "<code>rights.o009.original.bridge.regular-conditional-probability.cc-by-4.0</code>. "
            "Lisensi ini tidak melisensikan ulang materi <cite>Random</cite> atau "
            "<cite>QuantEcon</cite>."
        )
    elif original_bridge_count == 4:
        original_bridge_summary = (
            "Empat jembatan asli—<cite>Konstruksi Kolmogorov dan proses "
            "kanonik</cite>, <cite>Keterukuran proses dan hukum lintasan</cite>, "
            "<cite>Distribusi bersyarat reguler dan disiplin versi</cite>, serta "
            "<cite>Audit hipotesis untuk proses stokastik</cite>—mencakup "
            "keempat sambungan rigor yang dipilih; seluruhnya memuat dua belas "
            "latihan penguasaan, dua puluh empat petunjuk progresif, dua belas "
            "jawaban ringkas, dan dua belas penyelesaian lengkap."
        )
        if checkpoint >= 38:
            original_bridge_remaining = (
                "Keempat unit penghubung rigor, lima laboratorium, seluruh "
                "36 butir penguasaan wajib, dan dua formulir penilaian "
                "kumulatif sudah tersedia. Prasyarat O006/C140 dipertahankan "
                "sebagai dependensi bersama tanpa duplikasi."
            )
        elif checkpoint >= 37:
            original_bridge_remaining = (
                "Keempat unit penghubung rigor dan lima laboratorium sudah "
                "tersedia. Laboratorium kelima, Gerak Brown: Donsker, variasi "
                "kuadratik, dan waktu kena, memuat audit eksak tanpa Monte "
                "Carlo beserta latihan, petunjuk, jawaban, dan penyelesaian. "
                "Sebanyak 15 dari 36 butir penguasaan wajib telah "
                "diselesaikan; 21 butir penguasaan dan dua formulir kumulatif "
                "masih harus dilengkapi. Prasyarat O006/C140 dipertahankan "
                "sebagai dependensi bersama tanpa duplikasi."
            )
        elif checkpoint >= 36:
            original_bridge_remaining = (
                "Keempat unit penghubung rigor dan empat laboratorium sudah "
                "tersedia; satu laboratorium deterministik, 22 masalah "
                "terselesaikan tambahan, dua formulir kumulatif, dan pengikatan "
                "akhir O006 masih harus dilengkapi."
            )
        else:
            original_bridge_remaining = (
                "Keempat unit penghubung rigor sudah tersedia; tiga laboratorium "
                "deterministik, 24 masalah terselesaikan tambahan, dua formulir "
                "kumulatif, dan pengikatan akhir O006 masih harus dilengkapi."
            )
        original_bridge_rights = (
            "<cite>Konstruksi Kolmogorov dan proses kanonik</cite>, "
            "<cite>Keterukuran proses dan hukum lintasan</cite>, "
            "<cite>Distribusi bersyarat reguler dan disiplin versi</cite>, serta "
            "<cite>Audit hipotesis untuk proses stokastik</cite>, masing-masing "
            "dengan tiga latihan, enam petunjuk, tiga jawaban, dan tiga solusi: "
            "CC BY 4.0 di bawah "
            "<code>rights.o009.original.bridge.kolmogorov.cc-by-4.0</code>, "
            "<code>rights.o009.original.bridge.process-measurability-path-law.cc-by-4.0</code>, "
            "<code>rights.o009.original.bridge.regular-conditional-probability.cc-by-4.0</code>, "
            "dan "
            "<code>rights.o009.original.bridge.hypothesis-audits.cc-by-4.0</code>. "
            "Lisensi ini tidak melisensikan ulang materi <cite>Random</cite>, "
            "<cite>QuantEcon</cite>, atau komponen lain."
        )
    else:
        raise RuntimeError(
            "Front-matter prose has no admitted original-bridge configuration: "
            f"{original_bridge_count}"
        )
    quantecon_remaining = QUANTECON_CANONICAL_UNIT_COUNT - quantecon_count
    if quantecon_remaining:
        quantecon_status = (
            f"{quantecon_remaining} unit CTMC terpilih serta "
            "jembatan lanjutan/penguasaan akhir masih belum diterjemahkan"
        )
        quantecon_rights_status = (
            f"{quantecon_remaining} unit terpilih serta jembatan lanjutan dan "
            "penutupan penguasaan masih menunggu terjemahan"
        )
    elif checkpoint >= 38:
        quantecon_status = (
            "seluruh delapan unit CTMC terpilih, lapisan asli, 36 butir "
            "penguasaan, dan dua formulir kumulatif sudah lengkap"
        )
        quantecon_rights_status = (
            "seluruh delapan unit terpilih tersedia; setiap lapisan asli "
            "tetap mengikuti lisensi komponennya sendiri"
        )
    else:
        quantecon_status = (
            "seluruh delapan unit CTMC terpilih sudah tersedia, sedangkan "
            "lapisan asli dan penutupan penguasaan akhir kursus masih belum lengkap"
        )
        quantecon_rights_status = (
            "seluruh delapan unit terpilih sudah tersedia; lapisan asli "
            "dan penutupan penguasaan tetap mengikuti lisensi komponennya sendiri"
        )
    document = (
        FRONTMATTER_TEMPLATE
        .replace("{{TOC_ROWS_LEFT}}", toc_rows_left)
        .replace("{{TOC_ROWS_RIGHT}}", toc_rows_right)
        .replace("{{CHECKPOINT}}", str(checkpoint))
        .replace("{{SUBSTANTIVE_THEORY_COUNT}}", str(theory_count))
        .replace("{{OVERVIEW_COUNT}}", str(overview_count))
        .replace("{{ORIGINAL_BRIDGE_COUNT}}", str(original_bridge_count))
        .replace("{{LAB_COUNT_TEXT}}", lab_count_text)
        .replace("{{MASTERY_UNIT_COUNT}}", str(mastery_count))
        .replace("{{ASSESSMENT_COUNT}}", str(assessment_count))
        .replace("{{RANDOM_SUBSTANTIVE_COUNT}}", str(random_substantive_count))
        .replace("{{RANDOM_SELECTED_PAGES}}", str(random_selected_pages))
        .replace("{{QUANTECON_COUNT}}", str(quantecon_count))
        .replace(
            "{{QUANTECON_REMAINING}}",
            str(quantecon_remaining),
        )
        .replace("{{QUANTECON_STATUS}}", quantecon_status)
        .replace("{{QUANTECON_RIGHTS_STATUS}}", quantecon_rights_status)
        .replace("{{ORIGINAL_BRIDGE_SUMMARY}}", original_bridge_summary)
        .replace("{{ORIGINAL_BRIDGE_REMAINING}}", original_bridge_remaining)
        .replace("{{ORIGINAL_BRIDGE_RIGHTS}}", original_bridge_rights)
        .replace("{{MODEL_PROVENANCE}}", html.escape(MODEL_PROVENANCE))
        .replace("{{EDITION_DATE_TEXT}}", EDITION_DATE_TEXT)
        .replace(
            "{{EDITION_VERSION}}",
            f"{EDITION_VERSION_PREFIX}{checkpoint}",
        )
    )
    if checkpoint >= 38:
        document = (
            document
            .replace("Status: belum lengkap.", "Status: lengkap.")
            .replace(
                "PDF ini merekam bagian yang telah diterjemahkan, dibangun, dan diverifikasi hingga",
                "PDF ini merekam edisi lengkap yang telah diterjemahkan, dibangun, dan diverifikasi hingga",
            )
            .replace(
                "Bagian kurikulum D30 yang belum diterjemahkan tidak diwakili seolah-olah sudah tersedia.",
                "Seluruh korpus kanonis, 36 butir penguasaan, dan dua formulir kumulatif tersedia.",
            )
            .replace("Edisi parsial yang dapat dibaca.", "Edisi lengkap yang dapat dibaca.")
            .replace("Apa yang belum tersedia", "Penutupan kurikulum")
            .replace(
                "Ini belum merupakan edisi lengkap peran D30.",
                "Ini merupakan edisi lengkap peran D30.",
            )
        )
    path.write_text(document, encoding="utf-8")


FRONTMATTER_TEMPLATE = """<!doctype html>
<html lang="id-ID">
<head>
<meta charset="utf-8">
<title>Probabilitas Teoretis-Ukuran dan Proses Stokastik - Edisi Kerja Bahasa Indonesia</title>
<style>
@page { size: A4 portrait; margin: 16mm 15mm 19mm 15mm; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; color: #18242d; background: #fff; font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt; line-height: 1.45; print-color-adjust: exact; }
.front-page { min-height: 261mm; break-after: page; position: relative; }
.front-page-final { break-after: auto; }
.cover { display: flex; flex-direction: column; justify-content: center; padding: 12mm 8mm 17mm; border-top: 4mm solid #174f78; border-bottom: 1mm solid #174f78; }
.eyebrow { color: #174f78; font-size: 9pt; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
h1 { margin: 15mm 0 5mm; color: #123d5a; font-family: Georgia, "Times New Roman", serif; font-size: 32pt; line-height: 1.1; letter-spacing: -.02em; }
.subtitle { max-width: 135mm; color: #40515d; font-family: Georgia, "Times New Roman", serif; font-size: 17pt; line-height: 1.3; }
.status { margin-top: 20mm; padding: 5mm 6mm; border-left: 2.5mm solid #9a6600; background: #f8f2e5; font-size: 11pt; }
.cover-meta { margin-top: 16mm; color: #52616b; font-size: 9.5pt; line-height: 1.55; }
h2 { margin: 0 0 7mm; padding-bottom: 2.5mm; color: #123d5a; border-bottom: 1.2pt solid #174f78; font-family: Georgia, "Times New Roman", serif; font-size: 21pt; }
h3 { margin: 6mm 0 2mm; color: #174f78; font-family: Georgia, "Times New Roman", serif; font-size: 12pt; }
p { margin: 0 0 3mm; }
ul { margin: 1mm 0 4mm; padding-left: 7mm; }
.front-page ul { list-style: none; }
.front-page li { display: block; position: relative; margin-bottom: 1.4mm; }
.front-page li::before { content: "•"; position: absolute; left: -4mm; }
.notice { padding: 4mm 5mm; border: .7pt solid #b8c7d1; border-left: 2.2mm solid #174f78; background: #eef5f8; }
.warning { border-left-color: #9a6600; background: #f8f2e5; }
.rights-grid { display: grid; grid-template-columns: 34mm 1fr; gap: 2.2mm 5mm; margin-top: 3mm; font-size: 9.25pt; }
.rights-grid dt { color: #174f78; font-weight: 700; }
.rights-grid dd { margin: 0; }
.small { color: #52616b; font-size: 8.6pt; }
.toc-columns { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 5mm; align-items: start; }
.toc table { width: 100%; border-collapse: collapse; font-size: 8.35pt; line-height: 1.2; }
.toc tr { border-bottom: .45pt solid #d1dce2; }
.toc td { padding: 1.35mm .8mm; vertical-align: top; }
.toc .num { width: 7mm; color: #52616b; text-align: right; }
.toc .page { width: 10mm; color: #174f78; font-weight: 700; text-align: right; }
.kind { display: inline-block; min-width: 19mm; margin-right: 1mm; color: #52616b; font-size: 6.7pt; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
.folio { position: absolute; right: 0; bottom: 0; color: #6a7881; font-size: 8pt; }
a { color: #174f78; text-decoration: none; }
</style>
</head>
<body>
<section class="front-page cover">
  <div class="eyebrow">Edisi kerja bahasa Indonesia · Checkpoint preservasi {{CHECKPOINT}}</div>
  <h1>Probabilitas Teoretis-Ukuran dan Proses Stokastik</h1>
  <div class="subtitle">Pembaca mandiri: {{SUBSTANTIVE_THEORY_COUNT}} unit teori substantif (termasuk {{ORIGINAL_BRIDGE_COUNT}} jembatan asli), {{OVERVIEW_COUNT}} ikhtisar, {{LAB_COUNT_TEXT}} laboratorium komputasi, {{MASTERY_UNIT_COUNT}} unit bank penguasaan tambahan, dan {{ASSESSMENT_COUNT}} formulir kumulatif</div>
  <div class="status"><strong>Status: belum lengkap.</strong> PDF ini merekam bagian yang telah diterjemahkan, dibangun, dan diverifikasi hingga {{EDITION_DATE_TEXT}}. Bagian kurikulum D30 yang belum diterjemahkan tidak diwakili seolah-olah sudah tersedia.</div>
  <div class="cover-meta">Peran kurikulum O009/D30<br>Versi {{EDITION_VERSION}}<br>Rekaman preservasi: <a href="https://doi.org/10.5281/zenodo.22059941">doi:10.5281/zenodo.22059941</a> (konsep; selalu menuju versi terbaru)</div>
</section>
<section class="front-page">
  <h2>Status dan ruang lingkup</h2>
  <div class="notice warning"><strong>Edisi parsial yang dapat dibaca.</strong> Isi PDF ini mencakup {{SUBSTANTIVE_THEORY_COUNT}} unit teori substantif ({{RANDOM_SUBSTANTIVE_COUNT}} dari <cite>Random</cite>, {{QUANTECON_COUNT}} buku catatan <cite>QuantEcon</cite>, dan {{ORIGINAL_BRIDGE_COUNT}} jembatan asli), {{OVERVIEW_COUNT}} ikhtisar <cite>Random</cite>, dan {{LAB_COUNT_TEXT}} laboratorium yang dapat dijalankan ulang. Sumber HTML, sumber terjemahan, dan backend ber-ID stabil tetap menjadi artefak kanonik.</div>
  <h3>Apa yang tersedia</h3>
  <ul>
    <li>Seluruh {{RANDOM_SELECTED_PAGES}} halaman <cite>Random</cite> yang dipilih secara kanonik: {{RANDOM_SUBSTANTIVE_COUNT}} unit substantif dan tiga halaman ikhtisar untuk martingal, proses Markov, dan gerak Brown.</li>
    <li>Konvergensi, probabilitas terukur, proses stokastik, filtrasi, dan waktu henti.</li>
    <li>Konvergensi distribusi, nilai harapan bersyarat, keterintegralan seragam, serta kernel.</li>
    <li>{{ORIGINAL_BRIDGE_SUMMARY}}</li>
    <li>Pengantar, konstruksi, penghentian, pertidaksamaan, dan konvergensi martingal.</li>
    <li>Proses Markov umum, rantai waktu diskret, transiens-rekurensi, periodisitas, serta persamaan Kolmogorov maju dan mundur.</li>
    <li>Proses Poisson pada ruang ukuran umum, hukum lokasi titik bersyarat, penipisan, superposisi, dan jarak titik terdekat.</li>
    <li>Gerak Brown standar dan dengan hanyutan: distribusi berdimensi hingga, penskalaan, ketakteraturan lintasan, sifat Markov kuat, kepadatan transisi dan persamaan difusi, prinsip refleksi, waktu pencapaian, hukum arksinus, serta hukum logaritma berulang.</li>
    <li>Gerak Brown geometrik: distribusi lognormal, momen, perilaku asimtotik, martingal terdiskonto, simulator luring, dan latihan penguasaan.</li>
    <li>{{LAB_COUNT_TEXT}} laboratorium dengan kode, keluaran terbekukan, latihan penguasaan, petunjuk, jawaban, dan solusi.</li>
    <li>{{MASTERY_UNIT_COUNT}} unit bank penguasaan tambahan yang menutup keseluruhan 36 butir wajib, serta {{ASSESSMENT_COUNT}} formulir kumulatif alternatif dengan solusi lengkap.</li>
  </ul>
  <h3>Apa yang belum tersedia</h3>
  <p>Ini belum merupakan edisi lengkap peran D30. Blok <cite>Random</cite> terpilih sudah lengkap pada {{RANDOM_SELECTED_PAGES}} halaman. {{QUANTECON_COUNT}} unit dari blok <cite>Continuous Time Markov Chains</cite> QuantEcon yang tercantum dalam daftar isi tersedia di sini; {{QUANTECON_STATUS}}. {{ORIGINAL_BRIDGE_REMAINING}} Modul pengambilan sampel, hukum bilangan besar, dan teorema limit pusat dari jalur O006/C140 adalah prasyarat bersama dan tidak diduplikasi.</p>
  <h3>Cara menggunakan pembaca</h3>
  <p>Setiap panel “Rincian”, petunjuk, jawaban, dan penyelesaian yang interaktif di HTML dibuka penuh dalam PDF. Daftar isi dan bookmark PDF menuju awal setiap unit. Tautan sumber eksternal dipertahankan; navigasi lokal yang tidak bermakna di dalam berkas tunggal dihapus.</p>
  <div class="notice"><strong>Non-endorsement.</strong> Ini adalah edisi independen. Para penulis sumber dan lembaganya tidak mendukung, mensponsori, atau mengesahkan edisi ini.</div>
  <div class="folio">2</div>
</section>
<section class="front-page">
  <h2>Hak, atribusi, dan provenance</h2>
  <p>Tidak ada klaim lisensi tunggal untuk gabungan ini. Lisensi suatu komponen tidak memperluas atau menghapus hak komponen lain.</p>
  <dl class="rights-grid">
    <dt>Materi Random</dt><dd>{{RANDOM_SELECTED_PAGES}} halaman terpilih karya Kyle Siegrist, terdiri atas {{RANDOM_SUBSTANTIVE_COUNT}} unit substantif dan {{OVERVIEW_COUNT}} ikhtisar. Cuplikan URL-byte resmi yang dibekukan memuat dua saksi lisensi: beranda menyatakan CC BY 2.0, sedangkan halaman <cite>Credits</cite> menyatakan CC BY 1.0. Keduanya dipertahankan tanpa memilih satu secara sepihak.</dd>
    <dt>Donor lab</dt><dd>Potongan terpilih dari <cite>stochastic-book</cite> karya Gordan Žitković, komit <code>e2b35ad91a3689454ae6455e8ffc510a90760c0d</code>, CC0 1.0 Universal.</dd>
    <dt>Adaptasi id-ID</dt><dd>Terjemahan, adaptasi, perbaikan hilir, serta materi baru yang tidak diikat oleh baris komponen tersendiri: CC BY 4.0 sejauh hak baru timbul.</dd>
    <dt>Jembatan asli</dt><dd>{{ORIGINAL_BRIDGE_RIGHTS}}</dd>
    <dt>Runtime matematika</dt><dd>MathJax 3.1.2 dan ekstensi <code>boldsymbol</code>: Apache License 2.0.</dd>
    <dt>QuantEcon</dt><dd>{{QUANTECON_COUNT}} buku catatan <cite>Continuous Time Markov Chains</cite> yang tercantum dalam daftar isi tersedia di bawah CC BY-SA 4.0; {{QUANTECON_RIGHTS_STATUS}}.</dd>
  </dl>
  <h3>Perubahan dan integritas</h3>
  <p>Teks Indonesia merupakan terjemahan/adaptasi. Perbaikan matematis, perbaikan tautan/aksesibilitas, dan reflow deterministik diterapkan hanya pada pembaca hilir serta dicatat terpisah dalam backend. Rumus, struktur latihan, aset yang diterima, dan hubungan sumber dipertahankan dan diuji pada setiap batas.</p>
  <h3>Reproduksibilitas</h3>
  <p>PDF dibuat dari situs HTML checkpoint-{{CHECKPOINT}} yang telah divalidasi. MathJax dirender secara lokal, semua panel rincian dibuka, lalu seluruh batas pembaca dicetak sebagai satu dokumen A4 dengan Chromium. Pypdf menambahkan metadata dan bookmark sebagai pembaruan inkremental tanpa mengimpor ulang atau menumpangtindihkan konten halaman. HTML/sumber/backend tetap kanonik; PDF ini adalah permukaan pembaca tambahan.</p>
  <p class="small"><strong>Identifikasi model:</strong> {{MODEL_PROVENANCE}}</p>
  <p class="small">Rincian lengkap hak per komponen, saksi otoritas, manifest, hash, serta rekaman QA tersedia dalam paket sumber/backend checkpoint yang menyertai rilis. Tidak ada analitik atau runtime web eksternal yang diperlukan untuk membaca PDF.</p>
  <div class="folio">3</div>
</section>
<section class="front-page toc front-page-final">
  <h2>Daftar isi</h2>
  <div class="toc-columns" aria-label="Daftar isi">
    <table><tbody>{{TOC_ROWS_LEFT}}</tbody></table>
    <table><tbody>{{TOC_ROWS_RIGHT}}</tbody></table>
  </div>
  <div class="folio">4</div>
</section>
</body>
</html>
"""


def finalize_pdf(
    master: Path,
    starts: list[int],
    output: Path,
    checkpoint: int,
) -> dict[str, object]:
    """Append Info/outline objects while preserving all Chromium bytes."""
    writer = PdfWriter(master, incremental=True)
    counts = scope_counts()

    writer.add_metadata({
        "/Title": (
            "Probabilitas Teoretis-Ukuran dan Proses Stokastik - Edisi Bahasa Indonesia"
            if checkpoint >= 38
            else "Probabilitas Teoretis-Ukuran dan Proses Stokastik - Edisi Kerja Bahasa Indonesia"
        ),
        "/Author": (
            "Kyle Siegrist; Thomas J. Sargent; John Stachurski; "
            "Gordan Žitković; kontributor edisi kerja bahasa Indonesia"
        ),
        "/Subject": (
            ("Edisi lengkap: " if checkpoint >= 38 else "Edisi kerja belum lengkap: ")
            + f"{counts['substantive_theory']} unit teori substantif "
            f"({counts['random_substantive']} Random dan "
            f"{counts['quantecon']} QuantEcon dan "
            f"{counts['original_bridge']} jembatan asli), "
            f"{counts['overview']} ikhtisar Random, dan "
            f"{counts['labs']} laboratorium komputasi; "
            f"{counts['mastery']} unit bank penguasaan tambahan; "
            f"{counts['assessments']} formulir kumulatif; "
            f"seluruh {counts['random_selected_pages']} halaman Random terpilih; "
            "lisensi per komponen"
        ),
        "/Keywords": (
            "probabilitas, proses stokastik, perluasan Kolmogorov, ruang lintasan, "
            "proses kanonik, martingal, rantai Markov, proses Poisson, gerak Brown, "
            "bahasa Indonesia"
        ),
        "/Creator": (
            f"Pipeline lokal HTML/MathJax {EDITION_VERSION_PREFIX}{checkpoint}; "
            f"{MODEL_PROVENANCE}"
        ),
        "/Producer": (
            "Chromium (single print document) dan "
            f"pypdf {pypdf.__version__} (incremental)"
        ),
        "/CreationDate": EDITION_PDF_DATE,
        "/ModDate": EDITION_PDF_DATE,
    })

    writer.add_outline_item("Sampul", 0)
    writer.add_outline_item("Status dan ruang lingkup", 1)
    writer.add_outline_item("Hak, atribusi, dan provenance", 2)
    writer.add_outline_item("Daftar isi", 3)
    def outline_group(unit: Unit) -> str:
        if unit.kind == "Laboratorium":
            return "Laboratorium"
        if unit.kind == "Penguasaan":
            return "Bank penguasaan"
        if unit.kind == "Penilaian":
            return "Penilaian kumulatif"
        if unit.kind == ORIGINAL_BRIDGE_KIND:
            return "Jembatan asli"
        if "quantecon/" in unit.relpath:
            return "Unit teori QuantEcon"
        return "Materi Random"

    contiguous_groups: list[tuple[str, list[int]]] = []
    for index, unit in enumerate(UNITS):
        group_title = outline_group(unit)
        if contiguous_groups and contiguous_groups[-1][0] == group_title:
            contiguous_groups[-1][1].append(index)
        else:
            contiguous_groups.append((group_title, [index]))
    group_totals: dict[str, int] = {}
    for title, _indices in contiguous_groups:
        group_totals[title] = group_totals.get(title, 0) + 1
    group_positions: dict[str, int] = {}
    outline_groups: list[tuple[str, list[int]]] = []
    for title, indices in contiguous_groups:
        group_positions[title] = group_positions.get(title, 0) + 1
        display_title = (
            title
            if group_totals[title] == 1
            else f"{title} - blok {group_positions[title]}"
        )
        outline_groups.append((display_title, indices))
    grouped_indices = [index for _title, indices in outline_groups for index in indices]
    if grouped_indices != list(range(len(UNITS))):
        raise RuntimeError(
            "Outline groups do not preserve exact physical unit order: "
            f"{grouped_indices}"
        )
    for group_title, indices in outline_groups:
        parent = writer.add_outline_item(group_title, starts[indices[0]] - 1)
        for index in indices:
            writer.add_outline_item(
                UNITS[index].title,
                starts[index] - 1,
                parent=parent,
            )

    original_object_count = len(writer._original_hash)
    changed_ids: list[int] = []
    new_page_like_ids: list[int] = []
    for offset, obj in enumerate(writer._objects):
        if obj is None:
            continue
        changed = (
            offset >= original_object_count
            or obj.hash_bin() != writer._original_hash[offset]
        )
        if not changed:
            continue
        object_id = offset + 1
        changed_ids.append(object_id)
        if offset >= original_object_count and hasattr(obj, "get"):
            object_type = str(obj.get("/Type", ""))
            if (
                object_type in {"/Page", "/Pages"}
                or "/Resources" in obj
                or "/Contents" in obj
            ):
                new_page_like_ids.append(object_id)

    def indirect_id(value: object) -> int | None:
        reference = getattr(value, "indirect_reference", None)
        if reference is None and hasattr(value, "idnum"):
            reference = value
        return int(reference.idnum) if reference is not None else None

    allowed_existing = {indirect_id(writer.root_object), indirect_id(writer._info)}
    allowed_existing.discard(None)
    unexpected_existing = [
        object_id
        for object_id in changed_ids
        if object_id <= original_object_count and object_id not in allowed_existing
    ]
    if unexpected_existing or new_page_like_ids:
        raise RuntimeError(
            "Incremental finalization attempted to rewrite page/resource content: "
            f"unexpected existing IDs={unexpected_existing}; "
            f"new page-like IDs={new_page_like_ids}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_suffix(".tmp.pdf")
    temp_output.unlink(missing_ok=True)
    writer.write(temp_output)

    master_bytes = master.stat().st_size
    final_bytes = temp_output.stat().st_size
    if final_bytes <= master_bytes:
        temp_output.unlink(missing_ok=True)
        raise RuntimeError("Incremental output did not append to the Chromium master")
    with master.open("rb") as expected, temp_output.open("rb") as actual:
        offset = 0
        while True:
            expected_block = expected.read(1024 * 1024)
            if not expected_block:
                break
            actual_block = actual.read(len(expected_block))
            if actual_block != expected_block:
                temp_output.unlink(missing_ok=True)
                raise RuntimeError(
                    "Incremental output does not preserve the Chromium master "
                    f"at byte offset {offset}"
                )
            offset += len(expected_block)

    temp_output.replace(output)
    return {
        "mode": "pypdf incremental append",
        "pypdf_version": pypdf.__version__,
        "master_bytes_preserved_as_exact_prefix": master_bytes,
        "incremental_bytes": final_bytes - master_bytes,
        "changed_object_ids": changed_ids,
        "allowed_changed_existing_object_ids": sorted(allowed_existing),
        "unexpected_changed_existing_object_ids": unexpected_existing,
        "new_page_or_resource_object_ids": new_page_like_ids,
    }


def validate_pdf(path: Path, starts: list[int], checkpoint: int) -> dict[str, object]:
    reader = PdfReader(path)
    counts = scope_counts()
    if checkpoint >= 37:
        checkpoint_37_scope = {
            "substantive_theory": 36,
            "overview": 3,
            "original_bridge": 4,
            "labs": 5,
        }
        if checkpoint >= 38:
            checkpoint_37_scope.update({"mastery": 14, "assessments": 2})
        observed_scope = {
            key: counts[key]
            for key in checkpoint_37_scope
        }
        if observed_scope != checkpoint_37_scope:
            raise RuntimeError(
                "Reader scope differs from the admitted checkpoint closure: "
                f"{observed_scope}"
            )
    lab_count_text = {2: "dua", 4: "empat", 5: "lima"}.get(
        counts["labs"],
        str(counts["labs"]),
    )
    extraction = subprocess.run(
        [str(PDFTOTEXT), "-enc", "UTF-8", "-nopgbrk", str(path), "-"],
        check=True,
        capture_output=True,
        timeout=120,
    )
    text = extraction.stdout.decode("utf-8")
    required = [
        "Status: lengkap" if checkpoint >= 38 else "Status: belum lengkap",
        "Tidak ada klaim lisensi tunggal",
        "Non-endorsement",
        f"Seluruh {counts['random_selected_pages']} halaman Random",
        f"{lab_count_text} laboratorium",
        MODEL_PROVENANCE,
        f"{EDITION_VERSION_PREFIX}{checkpoint}",
    ]
    if checkpoint >= 38:
        required.extend([
            "Gerak Brown: Donsker, variasi kuadratik, dan waktu kena",
            "seluruh 36 butir penguasaan wajib",
            "dua formulir penilaian kumulatif",
            "Penilaian kumulatif — Formulir A",
            "Penilaian kumulatif — Formulir B",
        ])
    elif checkpoint >= 37:
        required.extend([
            "Gerak Brown: Donsker, variasi kuadratik, dan waktu kena",
            "15 dari 36 butir penguasaan wajib telah diselesaikan",
            "21 butir penguasaan dan dua formulir kumulatif",
        ])
    normalized_text = re.sub(r"\s+", " ", text).casefold()
    missing = [
        token
        for token in required
        if re.sub(r"\s+", " ", token).casefold() not in normalized_text
    ]
    normalized_required = [f"{counts['original_bridge']} jembatan asli"]
    missing.extend(
        token
        for token in normalized_required
        if re.sub(r"\s+", " ", token).casefold() not in normalized_text
    )
    missing.extend(
        unit.title
        for unit in UNITS
        if re.sub(r"\s+", " ", unit.title).casefold() not in normalized_text
    )
    if missing:
        raise RuntimeError(f"PDF text validation failed; missing: {missing}")
    if len(reader.pages) <= FRONT_PAGES:
        raise RuntimeError("PDF has no substantive reader pages")
    if starts[0] != FRONT_PAGES + 1:
        raise RuntimeError("First reader page does not follow four-page front matter")
    if path.stat().st_size >= 500_000_000:
        raise RuntimeError("PDF exceeds the 500 MB task cap")
    metadata = reader.metadata or {}
    expected_title_phrase = (
        "Edisi Bahasa Indonesia" if checkpoint >= 38 else "Edisi Kerja Bahasa Indonesia"
    )
    if expected_title_phrase not in (metadata.title or ""):
        raise RuntimeError("PDF title metadata is missing or incorrect")
    required_authors = (
        "Kyle Siegrist",
        "Thomas J. Sargent",
        "John Stachurski",
        "Gordan Žitković",
    )
    missing_authors = [
        author for author in required_authors if author not in (metadata.author or "")
    ]
    if missing_authors:
        raise RuntimeError(f"PDF author metadata omits source authors: {missing_authors}")
    expected_subject_scope = (
        f"{counts['substantive_theory']} unit teori substantif "
        f"({counts['random_substantive']} Random dan "
        f"{counts['quantecon']} QuantEcon dan "
        f"{counts['original_bridge']} jembatan asli), "
        f"{counts['overview']} ikhtisar Random"
    )
    if expected_subject_scope not in (metadata.subject or ""):
        raise RuntimeError("PDF subject metadata does not match the current reader scope")
    if f"{counts['labs']} laboratorium komputasi" not in (metadata.subject or ""):
        raise RuntimeError("PDF subject metadata omits the current laboratory count")
    expected_creator = (
        f"{EDITION_VERSION_PREFIX}{checkpoint}; {MODEL_PROVENANCE}"
    )
    if expected_creator not in (metadata.creator or ""):
        raise RuntimeError("PDF creator metadata is missing or incorrect")
    link_annotations = sum(
        1
        for page in reader.pages
        for annotation in (page.get("/Annots") or [])
        if annotation.get_object().get("/Subtype") == "/Link"
    )
    if link_annotations == 0:
        raise RuntimeError("PDF lost all meaningful link annotations")

    outline_pages: list[int] = []
    outline_titles: list[str] = []

    def collect_outline(items: list[object]) -> None:
        for item in items:
            if isinstance(item, list):
                collect_outline(item)
                continue
            page_number = reader.get_destination_page_number(item)
            if page_number < 0:
                raise RuntimeError(f"Outline destination is unresolved: {item!r}")
            outline_pages.append(page_number + 1)
            outline_titles.append(str(getattr(item, "title", "")))

    collect_outline(reader.outline)
    if outline_pages != sorted(outline_pages):
        raise RuntimeError(
            "PDF outline destinations are not in physical document order: "
            f"{outline_pages}"
        )
    invalid_outline_units = [
        unit.title for unit in UNITS if outline_titles.count(unit.title) != 1
    ]
    if invalid_outline_units:
        raise RuntimeError(
            "PDF outline must contain every unit destination exactly once: "
            f"{invalid_outline_units}"
        )
    return {
        "path": relative(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "pages": len(reader.pages),
        "text_characters": len(text),
        "text_extractor": "Poppler pdftotext UTF-8",
        "first_substantive_page": starts[0],
        "last_unit_start_page": starts[-1],
        "metadata_title": metadata.title,
        "metadata_creator": metadata.creator,
        "outline_present": bool(reader.outline),
        "outline_destinations": len(outline_pages),
        "outline_pages_monotonic": True,
        "link_annotations": link_annotations,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a reader-first PDF for one numbered checkpoint.",
    )
    parser.add_argument(
        "--checkpoint",
        type=int,
        required=True,
        help="positive checkpoint number used in the artifact and receipt identities",
    )
    args = parser.parse_args()
    if args.checkpoint <= 0:
        parser.error("--checkpoint must be a positive integer")
    return args


def main() -> None:
    args = parse_args()
    checkpoint = args.checkpoint
    configure_checkpoint(checkpoint)
    output_pdf = OUTPUT / (
        "00_PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_"
        f"READER_CHECKPOINT_{checkpoint}.pdf"
    )
    if not SITE.is_dir():
        raise SystemExit(f"Validated site not found: {SITE}")
    site_inputs = validate_site_inputs()
    if not NODE_MODULES.is_dir() or NODE_MODULES.is_symlink():
        raise SystemExit("Pinned local Node/Playwright renderer is unavailable")
    runtime_inputs = validate_render_runtime()

    server, thread = start_server()
    base_url = f"http://127.0.0.1:{server.server_port}"
    diagnostics: list[dict[str, object]] = []
    receipt: dict[str, object]
    try:
        with tempfile.TemporaryDirectory(prefix="o009-pdf-") as temp_name:
            temp = Path(temp_name)
            # Pass 1 establishes the exact page on which every forced unit
            # boundary lands.  The fixed-width TOC page-number column means
            # inserting those values cannot change the front-matter geometry,
            # but pass 2 is still checked against pass 1 before release.
            provisional_starts = [FRONT_PAGES + 1] * len(UNITS)
            front_html = temp / "frontmatter.html"
            make_frontmatter(front_html, provisional_starts, checkpoint)
            pagination_pdf = temp / "master-pagination.pdf"
            pagination_result = run_master_renderer(
                frontmatter=front_html,
                output=pagination_pdf,
                base_url=base_url,
                job_path=temp / "master-pagination-job.json",
            )
            pagination_metadata_normalization = normalize_chromium_pdf_metadata(
                pagination_pdf
            )
            diagnostics.extend(pagination_result["units"])
            bad = [
                item for item in diagnostics
                if item["brokenImages"]
                or item["emptyAltImages"]
                or item["externalRuntime"]
                or item["mathErrors"]
                or item["rawMystRoles"]
                or item["rawMathMacros"]
                or item["details"] != item["openDetails"]
                or int(item["bodyTextCharacters"]) == 0
            ]
            if bad:
                raise RuntimeError(
                    "HTML render diagnostics failed: "
                    + json.dumps(bad, ensure_ascii=False)
                )
            expected_print_reflows = [
                (
                    "labs/04-nilai-harapan-bersyarat-martingal.html",
                    [{
                        "id": "o009-results-conditional-martingale",
                        "sourceColumns": 18,
                        "sourceRows": 1,
                        "outputRows": 9,
                        "fieldsPreserved": 18,
                    }],
                )
            ]
            if checkpoint >= 37:
                expected_print_reflows.append(
                    (
                        "labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html",
                        [{
                            "id": "o009-results-brownian-diagnostics",
                            "sourceColumns": 15,
                            "sourceRows": 4,
                            "outputRows": 32,
                            "fieldsPreserved": 60,
                            "sourceOrderPreserved": True,
                        }],
                    )
                )
            observed_print_reflows = [
                (UNITS[index].relpath, item.get("printTableReflows", []))
                for index, item in enumerate(diagnostics)
                if item.get("printTableReflows")
            ]
            if observed_print_reflows != expected_print_reflows:
                raise RuntimeError(
                    "Print-only wide-table reflow closure mismatch: "
                    + json.dumps(observed_print_reflows, ensure_ascii=False)
                )
            master_broken_images = pagination_result.get("masterBrokenImages", [])
            if master_broken_images:
                raise RuntimeError(
                    "Master-document image load failed: "
                    + json.dumps(master_broken_images, ensure_ascii=False)
                )

            starts = locate_unit_starts(pagination_pdf)
            pagination_pages = len(PdfReader(pagination_pdf).pages)
            make_frontmatter(front_html, starts, checkpoint)
            master_pdf = temp / "master-final.pdf"
            final_result = run_master_renderer(
                frontmatter=front_html,
                output=master_pdf,
                base_url=base_url,
                job_path=temp / "master-final-job.json",
            )
            final_metadata_normalization = normalize_chromium_pdf_metadata(
                master_pdf
            )
            final_diagnostics = final_result["units"]
            final_bad = [
                item for item in final_diagnostics
                if item["brokenImages"]
                or item["emptyAltImages"]
                or item["externalRuntime"]
                or item["mathErrors"]
                or item["rawMystRoles"]
                or item["rawMathMacros"]
                or item["details"] != item["openDetails"]
                or int(item["bodyTextCharacters"]) == 0
            ]
            if final_bad:
                raise RuntimeError(
                    "Final-pass HTML render diagnostics failed: "
                    + json.dumps(final_bad, ensure_ascii=False)
                )
            diagnostic_keys = (
                "title", "details", "openDetails", "mathJax", "images",
                "bodyTextCharacters", "mathErrors", "rawMystRoles",
                "rawMathMacros", "printTableReflows",
            )
            first_signature = [
                tuple(item[key] for key in diagnostic_keys)
                for item in diagnostics
            ]
            final_signature = [
                tuple(item[key] for key in diagnostic_keys)
                for item in final_diagnostics
            ]
            if final_signature != first_signature:
                raise RuntimeError(
                    "Unit diagnostics changed between pagination and final render"
                )
            final_starts = locate_unit_starts(master_pdf)
            if final_starts != starts:
                raise RuntimeError(
                    "TOC insertion changed single-document pagination: "
                    f"first pass {starts}, final pass {final_starts}"
                )
            final_broken_images = final_result.get("masterBrokenImages", [])
            if final_broken_images:
                raise RuntimeError(
                    "Final master-document image load failed: "
                    + json.dumps(final_broken_images, ensure_ascii=False)
                )
            if validate_site_inputs() != site_inputs:
                raise RuntimeError("Validated site inputs changed during PDF rendering")
            if validate_render_runtime() != runtime_inputs:
                raise RuntimeError("Pinned render runtime changed during PDF rendering")
            page_counts = unit_page_counts(master_pdf, starts)

            incremental_finalization = finalize_pdf(
                master_pdf, starts, output_pdf, checkpoint
            )
            receipt = validate_pdf(output_pdf, starts, checkpoint)
            scope = scope_counts()
            receipt.update({
                "format": "A4 portrait",
                "checkpoint": checkpoint,
                "document_version": f"{EDITION_VERSION_PREFIX}{checkpoint}",
                "theory_units": scope["substantive_theory"],
                "substantive_theory_units": scope["substantive_theory"],
                "overview_units": scope["overview"],
                "labs": scope["labs"],
                "mastery_units": scope["mastery"],
                "assessment_forms": scope["assessments"],
                "quantecon_units": scope["quantecon"],
                "quantecon_notebooks": scope["quantecon"],
                "original_bridge_units": scope["original_bridge"],
                "random_substantive_units": scope["random_substantive"],
                "random_selected_pages": scope["random_selected_pages"],
                "random_selected_pages_complete": (
                    scope["random_selected_pages"] == RANDOM_CANONICAL_PAGE_COUNT
                ),
                "component_units_total": len(UNITS),
                "component_page_counts": [
                    {
                        "kind": unit.kind,
                        "title": unit.title,
                        "relpath": unit.relpath,
                        "start_page": start,
                        "pages": count,
                    }
                    for unit, start, count in zip(
                        UNITS, starts, page_counts, strict=True
                    )
                ],
                "render_diagnostics": diagnostics,
                "print_scale": final_result["printScale"],
                "render_strategy": (
                    "single Chromium print document; pypdf appends metadata/outlines "
                    "incrementally while preserving the Chromium master byte-for-byte "
                    "as the output prefix"
                ),
                "pagination_pass_pages": pagination_pages,
                "final_master_pages": len(PdfReader(master_pdf).pages),
                "incremental_finalization": incremental_finalization,
                "chromium_metadata_normalization": {
                    "pagination_pass": pagination_metadata_normalization,
                    "final_pass": final_metadata_normalization,
                },
                "site_inputs": site_inputs,
                "runtime_inputs": runtime_inputs,
            })
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    receipt_path = (
        ROOT / "qa" / f"CHECKPOINT_{checkpoint}_READER_PDF_RECEIPT.json"
    )
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
