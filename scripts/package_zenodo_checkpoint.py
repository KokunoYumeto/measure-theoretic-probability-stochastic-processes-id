#!/usr/bin/env python3
"""Build deterministic Zenodo checkpoint archives for the O009/D30 lane."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release"
LATEST_RECEIPT = ROOT / "00_control" / "ZENODO_PUBLICATION_RECEIPT.json"
ARTIFACT_PREFIX = "PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID"
EXPECTED_CONCEPTRECID = "22059941"
ZIP_TIME = (2026, 8, 22, 0, 0, 0)
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra."
PUBLIC_SANITIZATION_MANIFEST = "PUBLIC_SANITIZATION_MANIFEST.json"
INCOMPLETE_MANIFEST_STATE = "working edition; incomplete course"
COMPLETE_MANIFEST_STATE = "complete course"
CHECKPOINT_38_SCOPE = {
    "theory_units": 36,
    "overview_units": 3,
    "original_bridge_units": 4,
    "labs": 5,
    "quantecon_units": 8,
    "random_substantive_units": 24,
    "random_selected_pages": 27,
    "mastery_units": 14,
    "assessment_forms": 2,
}
CHECKPOINT_38_COURSE_COVERAGE = {
    "mastery_problems_required": 36,
    "mastery_problems_solved": 36,
    "assessment_forms": 2,
    "assessment_forms_equivalent": True,
}
CHECKPOINT_38_FORM_IDS = (
    "assessment.o009.d30.cumulative.form-a",
    "assessment.o009.d30.cumulative.form-b",
)
CHECKPOINT_38_BROWN_MASTERY_EXERCISE_IDS = frozenset(
    {
        "unit.o009.original.brown.drift.mastery.exercise",
        "unit.o009.original.brown.bridge.mastery.exercise",
        "unit.o009.original.brown.geometric.mastery.exercise",
    }
)
CHECKPOINT_38_PUBLIC_SCRIPT_ALLOWLIST = frozenset(
    {
        "build_backend.py",
        "build_first_boundary.py",
        "build_quantecon_component.py",
        "build_quantecon_ergodicity_component.py",
        "build_quantecon_generators_component.py",
        "build_quantecon_kolmogorov_bwd_component.py",
        "build_quantecon_kolmogorov_fwd_component.py",
        "build_quantecon_markov_prop_component.py",
        "build_quantecon_poisson_component.py",
        "build_quantecon_uc_mc_semigroups_component.py",
        "build_reader_pdf.py",
        "freeze_quantecon_environment.py",
        "freeze_random_authority.py",
        "package_zenodo_checkpoint.py",
        "qa_checkpoint31_overviews.cjs",
        "qa_lab05_brownian_browser.cjs",
        "qa_quantecon_ergodicity.py",
        "qa_quantecon_kolmogorov_fwd.py",
        "qa_quantecon_uc_mc_semigroups.py",
        "render_reader_pdf.cjs",
        "verify_published_site.py",
        "verify_quantecon_authority.py",
        "verify_quantecon_native_build.py",
        "verify_remote_pages.py",
    }
)
CHECKPOINT_38_PUBLIC_CONTROL_ALLOWLIST = frozenset(
    {
        "BUILD_BASELINE.md",
        "QUANTECON_COMPONENT_PLAN.md",
        "REPRODUCIBLE_BUILD_TIMESTAMP_UTC.txt",
        "RUNTIME_LOCK.json",
        "SELECTION_PACKET_BINDING.json",
        "SOURCE_AUTHORITY_AND_RIGHTS.md",
        "TERMINOLOGY.csv",
    }
)
CHECKPOINT_38_PUBLIC_SOURCE_SUFFIXES = frozenset(
    {".css", ".html", ".js", ".md", ".rmd"}
)
CHECKPOINT_38_PUBLIC_SOURCE_EXCLUSIONS = frozenset(
    {
        "source/labs/test.tmp",
        "scripts/run_checkpoint37_render.ps1",
        "qa/CHECKPOINT_37_RENDER_STATUS.json",
        "qa/CHECKPOINT_37_RENDER.stdout.log",
        "qa/CHECKPOINT_37_RENDER.stderr.log",
        "qa/CHECKPOINT_38_PACKAGE_REPEAT_QA.json",
        "scripts/publish_figshare_checkpoint.py",
        "scripts/publish_zenodo_checkpoint.py",
    }
)
CHECKPOINT_38_QUANTECON_COMPONENT_KEYS = (
    "quantecon_component",
    "quantecon_ergodicity_component",
    "quantecon_generators_component",
    "quantecon_kolmogorov_bwd_component",
    "quantecon_kolmogorov_fwd_component",
    "quantecon_markov_prop_component",
    "quantecon_poisson_component",
    "quantecon_uc_mc_semigroups_component",
)
CHECKPOINT_38_PUBLIC_STATIC_SOURCE_PATHS = frozenset(
    {
        "source/index.md",
        "source/reader.css",
        "source/apps/two-state.html",
        "source/labs/01-konvergensi-monte-carlo.Rmd",
        "source/labs/02-simulasi-rantai-markov.Rmd",
        "source/labs/03-konstruksi-brownian-donsker.Rmd",
        "source/labs/03-konvergensi-mode-dan-lln-clt.Rmd",
        "source/labs/04-nilai-harapan-bersyarat-martingal.Rmd",
        "source/labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.Rmd",
        "source/original/brown-bridge-offline.js",
        "source/original/brown-drift-offline.js",
        "source/original/geometric-brownian-offline.js",
    }
)
CHECKPOINT_38_METADATA_COVERAGE = (
    "36 unit teori substantif",
    "24 unit teori Random Services",
    "tiga halaman ikhtisar Random Services",
    "empat jembatan asli",
    "lima laboratorium R",
    "delapan unit teori QuantEcon",
    "27 dari 27 halaman Random Services yang dipilih",
    "14 halaman penguasaan baru",
    "36 dari 36 masalah penguasaan terpecahkan",
    "dua formulir penilaian kumulatif yang ekuivalen",
)

WINDOWS_ESCAPED_PROFILE_RE = re.compile(
    r"(?i)[A-Z]:(?P<drive_separator>\\{2,})Users"
    r"(?P<identity_separator>\\{2,})(?P<identity>[^\\/\r\n\"]+)"
    r"(?P<trailing_separator>\\{2,})"
)
WINDOWS_PROFILE_RE = re.compile(
    r"(?i)[A-Z]:\\Users\\(?P<identity>[^\\/\r\n\"]+)\\"
)
WINDOWS_FORWARD_PROFILE_RE = re.compile(
    r"(?i)[A-Z]:(?P<drive_separator>\\*/)Users"
    r"(?P<identity_separator>\\*/)(?P<identity>[^\\/\r\n\"]+)"
    r"(?P<trailing_separator>\\*/)"
)
POSIX_PROFILE_RE = re.compile(
    r"(?i)(?P<root_separator>\\*/)(?:home|Users)"
    r"(?P<identity_separator>\\*/)(?P<identity>[^\\/\r\n\"]+)"
    r"(?P<trailing_separator>\\*/)"
)
PROFILE_RESIDUE_BYTES_RE = re.compile(
    rb"(?i)(?:[A-Z]:[\\/]+Users[\\/]+[^\\/\x00\r\n\"']{1,128}[\\/]+|(?:\\*/)(?:home|Users)(?:\\*/)[^\\/\x00\r\n\"']{1,128}(?:\\*/))"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic, checkpoint-numbered Zenodo package. "
            "No checkpoint is selected implicitly."
        )
    )
    parser.add_argument("--checkpoint", type=int, required=True)
    parser.add_argument(
        "--replace-local",
        action="store_true",
        help="atomically replace files for this unpublished local checkpoint",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="validate inputs and policy without writing release files",
    )
    return parser.parse_args()


def artifact_names(checkpoint: int) -> dict[str, str]:
    if checkpoint < 1:
        raise RuntimeError("checkpoint must be a positive integer")
    return {
        "pdf": f"00_{ARTIFACT_PREFIX}_READER_CHECKPOINT_{checkpoint}.pdf",
        "reader": f"{ARTIFACT_PREFIX}_READER_CHECKPOINT_{checkpoint}.zip",
        "source": f"{ARTIFACT_PREFIX}_SOURCE_BACKEND_CHECKPOINT_{checkpoint}.zip",
        "manifest": f"RELEASE_MANIFEST_CHECKPOINT_{checkpoint}.json",
        "checksums": f"SHA256SUMS_CHECKPOINT_{checkpoint}.txt",
        "metadata": f"ZENODO_METADATA_CHECKPOINT_{checkpoint}.json",
    }


def checkpoint_from_version(version: str) -> int:
    match = re.fullmatch(r"\d{4}\.\d{2}\.\d{2}-checkpoint\.(\d+)", version)
    if not match:
        raise RuntimeError(f"unrecognized checkpoint version: {version!r}")
    return int(match.group(1))


def normalized_license(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        candidate = value.get("id")
        return candidate if isinstance(candidate, str) else None
    return None


def has_exact_disclosure_phrase(text: str, phrase: str) -> bool:
    """Match a disclosure phrase without accepting digit prefixes/suffixes."""
    parts: list[str] = []
    cursor = 0
    for match in re.finditer(r"\d+", phrase):
        parts.append(re.escape(phrase[cursor : match.start()]))
        parts.append(rf"(?<!\d){re.escape(match.group())}(?!\d)")
        cursor = match.end()
    parts.append(re.escape(phrase[cursor:]))
    return re.search(r"(?<!\w)" + "".join(parts) + r"(?!\w)", text) is not None


def validate_completion_disclosure(checkpoint: int, text: str, context: str) -> None:
    """Require the historically accurate incomplete/complete course label."""
    incomplete = "belum lengkap" in text or "incomplete" in text
    if checkpoint == 38:
        if incomplete:
            raise RuntimeError(f"{context} must not retain an incomplete-course claim")
        complete_phrases = ("edisi lengkap", "kursus lengkap", "complete course")
        if not any(has_exact_disclosure_phrase(text, phrase) for phrase in complete_phrases):
            raise RuntimeError(f"{context} must explicitly disclose complete-course status")
    elif not incomplete:
        raise RuntimeError(f"{context} must explicitly disclose the incomplete status")


def manifest_completion_state(checkpoint: int) -> str:
    return COMPLETE_MANIFEST_STATE if checkpoint == 38 else INCOMPLETE_MANIFEST_STATE


def validate_checkpoint_38_coverage(text: str) -> None:
    """Reject stale or ambiguous mastery/form coverage claims."""
    mastery_ratios = re.findall(
        r"(?<!\d)(\d+)\s+dari\s+(\d+)\s+masalah\s+penguasaan\s+terpecahkan(?!\w)",
        text,
    )
    if mastery_ratios != [("36", "36")]:
        raise RuntimeError(
            "checkpoint-38 metadata must contain exactly one 36/36 mastery claim"
        )
    equivalent_forms = re.findall(
        r"(?<!\w)(satu|dua|\d+)\s+formulir\s+penilaian\s+kumulatif\s+yang\s+ekuivalen(?!\w)",
        text,
    )
    if equivalent_forms != ["dua"]:
        raise RuntimeError(
            "checkpoint-38 metadata must contain exactly one two-equivalent-forms claim"
        )


def checkpoint_pdf_receipt(checkpoint: int, pdf_path: Path) -> dict:
    receipt_path = ROOT / "qa" / f"CHECKPOINT_{checkpoint}_READER_PDF_RECEIPT.json"
    if not receipt_path.is_file():
        raise RuntimeError(f"checkpoint PDF receipt is missing: {receipt_path}")
    if not pdf_path.is_file():
        raise RuntimeError(f"checkpoint PDF is missing: {pdf_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    expected_name = artifact_names(checkpoint)["pdf"]
    receipt_name = Path(str(receipt.get("path") or "").replace("\\", "/")).name
    if receipt.get("checkpoint") != checkpoint or receipt_name != expected_name:
        raise RuntimeError("checkpoint PDF receipt identity mismatch")
    pages = receipt.get("pages")
    if not isinstance(pages, int) or pages <= 4:
        raise RuntimeError("checkpoint PDF receipt has no usable page count")
    if int(receipt.get("bytes", -1)) != pdf_path.stat().st_size:
        raise RuntimeError("checkpoint PDF receipt byte count mismatch")
    if receipt.get("sha256") != sha256_file(pdf_path):
        raise RuntimeError("checkpoint PDF receipt SHA-256 mismatch")
    expected_scopes = {
        22: {"theory_units": 24, "labs": 2, "quantecon_units": 5},
        23: {"theory_units": 25, "labs": 2, "quantecon_units": 6},
        24: {"theory_units": 26, "labs": 2, "quantecon_units": 7},
        25: {"theory_units": 27, "labs": 2, "quantecon_units": 8},
        26: {"theory_units": 28, "labs": 2, "quantecon_units": 8},
        27: {"theory_units": 29, "labs": 2, "quantecon_units": 8},
        28: {"theory_units": 30, "labs": 2, "quantecon_units": 8},
        29: {"theory_units": 31, "labs": 2, "quantecon_units": 8},
        30: {"theory_units": 32, "labs": 2, "quantecon_units": 8},
        31: {
            "theory_units": 32,
            "overview_units": 3,
            "labs": 2,
            "quantecon_units": 8,
            "random_substantive_units": 24,
            "random_selected_pages": 27,
        },
        32: {
            "theory_units": 33,
            "overview_units": 3,
            "original_bridge_units": 1,
            "labs": 2,
            "quantecon_units": 8,
            "random_substantive_units": 24,
            "random_selected_pages": 27,
        },
        33: {
            "theory_units": 34,
            "overview_units": 3,
            "original_bridge_units": 2,
            "labs": 2,
            "quantecon_units": 8,
            "random_substantive_units": 24,
            "random_selected_pages": 27,
        },
        34: {
            "theory_units": 35,
            "overview_units": 3,
            "original_bridge_units": 3,
            "labs": 2,
            "quantecon_units": 8,
            "random_substantive_units": 24,
            "random_selected_pages": 27,
        },
        35: {
            "theory_units": 36,
            "overview_units": 3,
            "original_bridge_units": 4,
            "labs": 2,
            "quantecon_units": 8,
            "random_substantive_units": 24,
            "random_selected_pages": 27,
        },
        36: {
            "theory_units": 36,
            "overview_units": 3,
            "original_bridge_units": 4,
            "labs": 4,
            "quantecon_units": 8,
            "random_substantive_units": 24,
            "random_selected_pages": 27,
        },
        37: {
            "theory_units": 36,
            "overview_units": 3,
            "original_bridge_units": 4,
            "labs": 5,
            "quantecon_units": 8,
            "random_substantive_units": 24,
            "random_selected_pages": 27,
        },
        38: CHECKPOINT_38_SCOPE,
    }
    expected_scope = expected_scopes.get(checkpoint)
    if expected_scope is None:
        raise RuntimeError(
            f"checkpoint {checkpoint} has no explicit PDF scope policy"
        )
    for field, expected in expected_scope.items():
        if receipt.get(field) != expected:
            raise RuntimeError(
                f"checkpoint PDF receipt {field} mismatch: "
                f"expected {expected}, observed {receipt.get(field)!r}"
            )
    if checkpoint >= 36:
        if receipt.get("print_scale") != 1.25:
            raise RuntimeError("checkpoint PDF receipt does not bind print scale 1.25")
        renderer_path = ROOT / "scripts" / "render_reader_pdf.cjs"
        renderer_receipt = (receipt.get("runtime_inputs") or {}).get("renderer") or {}
        if renderer_receipt.get("sha256") != sha256_file(renderer_path):
            raise RuntimeError("checkpoint PDF receipt renderer hash is stale")
        if renderer_receipt.get("bytes") != renderer_path.stat().st_size:
            raise RuntimeError("checkpoint PDF receipt renderer byte count is stale")
    document_version = receipt.get("document_version")
    if checkpoint >= 29:
        if (
            not isinstance(document_version, str)
            or checkpoint_from_version(document_version) != checkpoint
        ):
            raise RuntimeError("checkpoint PDF receipt document version mismatch")
        expected_creator = f"{document_version}; {MODEL_PROVENANCE}"
    else:
        expected_creator = f"checkpoint-{checkpoint}; {MODEL_PROVENANCE}"
    if expected_creator not in str(receipt.get("metadata_creator") or ""):
        raise RuntimeError("checkpoint PDF receipt model/checkpoint provenance mismatch")
    return receipt


def validate_metadata_and_lineage(checkpoint: int, metadata_path: Path) -> dict:
    if not metadata_path.is_file():
        raise RuntimeError(f"required Zenodo metadata file missing: {metadata_path}")
    if not LATEST_RECEIPT.is_file():
        raise RuntimeError(f"latest public-lineage receipt missing: {LATEST_RECEIPT}")

    body = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata = body.get("metadata")
    if not isinstance(metadata, dict):
        raise RuntimeError("Zenodo metadata must contain a metadata object")
    receipt = json.loads(LATEST_RECEIPT.read_text(encoding="utf-8"))

    target_version = metadata.get("version")
    if not isinstance(target_version, str) or checkpoint_from_version(target_version) != checkpoint:
        raise RuntimeError("metadata version does not match --checkpoint")
    previous_version = receipt.get("version")
    if not isinstance(previous_version, str):
        raise RuntimeError("latest public receipt has no usable version")
    previous_checkpoint = checkpoint_from_version(previous_version)
    if checkpoint <= previous_checkpoint:
        raise RuntimeError(
            f"checkpoint must exceed the latest public-lineage value ({previous_checkpoint})"
        )
    skipped_checkpoints: list[int] = []
    for skipped in range(previous_checkpoint + 1, checkpoint):
        blocker_path = (
            ROOT
            / "00_control"
            / f"ZENODO_PUBLICATION_BLOCKED_CHECKPOINT_{skipped}.json"
        )
        if not blocker_path.is_file():
            raise RuntimeError(
                f"checkpoint gap {skipped} lacks a sanitized no-mutation blocker"
            )
        blocker = json.loads(blocker_path.read_text(encoding="utf-8"))
        attempt = blocker.get("attempt") or {}
        if (
            blocker.get("checkpoint") != skipped
            or attempt.get("mutation_observed") is not False
            or attempt.get("upload_started") is not False
            or attempt.get("publish_started") is not False
        ):
            raise RuntimeError(
                f"checkpoint gap {skipped} is not proven unpublished and mutation-free"
            )
        skipped_checkpoints.append(skipped)
    if metadata.get("title") != receipt.get("title"):
        raise RuntimeError("metadata title differs from the existing Zenodo lineage")

    publication_date = metadata.get("publication_date")
    if not isinstance(publication_date, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}", publication_date
    ):
        raise RuntimeError("metadata publication_date must be YYYY-MM-DD")
    if normalized_license(metadata.get("license")) != "other-open":
        raise RuntimeError("mixed-rights edition must use Zenodo license other-open")
    if metadata.get("access_right") != "open":
        raise RuntimeError(
            "Zenodo metadata access_right must be exactly 'open' before packaging"
        )

    serialized = json.dumps(body, ensure_ascii=False)
    if re.search(r"(?<![A-Za-z0-9])TTP(?![A-Za-z0-9])", serialized, re.IGNORECASE):
        raise RuntimeError("TTP must not appear in Zenodo work metadata")
    if re.search(r"Translation\s+and\s+Transcription\s+Project", serialized, re.IGNORECASE):
        raise RuntimeError("the umbrella expansion must not appear in work metadata")

    description = metadata.get("description")
    if not isinstance(description, str):
        raise RuntimeError("metadata description is required")
    plain_description = re.sub(r"<[^>]+>", " ", description)
    folded = plain_description.casefold()
    validate_completion_disclosure(checkpoint, folded, "metadata")
    if "campuran" not in folded and "mixed" not in folded:
        raise RuntimeError("metadata must explicitly disclose mixed component rights")
    if "licenses.md" not in folded:
        raise RuntimeError("metadata must direct readers to LICENSES.md")
    for component in ("Random Services", "Žitković", "QuantEcon"):
        if component.casefold() not in folded:
            raise RuntimeError(f"metadata rights disclosure omits {component}")
    if MODEL_PROVENANCE not in serialized:
        raise RuntimeError("metadata omits the exact required production-model disclosure")
    creator_names = {
        row.get("name")
        for row in metadata.get("creators", [])
        if isinstance(row, dict)
    }
    required_creators = {
        "Siegrist, Kyle",
        "Sargent, Thomas J.",
        "Stachurski, John",
        "Žitković, Gordan",
    }
    if not required_creators.issubset(creator_names):
        raise RuntimeError("metadata omits a required source-author credit")
    pdf_receipt: dict | None = None
    completion_evidence: dict | None = None
    if checkpoint in {18, 19}:
        for phrase in ("19 unit teori", "dua unit pertama", "209 halaman", "Enam bab"):
            if phrase.casefold() not in folded:
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 20:
        for phrase in ("19 unit teori", "tiga unit teori", "dua laboratorium", "223 halaman", "Lima unit"):
            if phrase.casefold() not in folded:
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 21:
        for phrase in (
            "19 unit teori Random Services",
            "empat unit teori QuantEcon",
            "dua laboratorium R",
            "empat dari delapan unit",
            "11 dari 25 latihan beserta solusi",
            "23 dari 35 sel sumber Python",
            "empat unit QuantEcon berikutnya",
            "Persamaan Kolmogorov Mundur",
        ):
            if phrase.casefold() not in folded:
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
        if not re.search(r"\b\d+ halaman\b", folded):
            raise RuntimeError("checkpoint coverage disclosure omits the PDF page count")
    elif checkpoint == 22:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "19 unit teori Random Services",
            "lima unit teori QuantEcon",
            "dua laboratorium R",
            "lima dari delapan unit",
            "14 dari 25 latihan beserta solusi",
            "29 dari 35 sel sumber Python",
            "tiga unit QuantEcon berikutnya",
            "Persamaan Kolmogorov Maju",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 23:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "19 unit teori Random Services",
            "enam unit teori QuantEcon",
            "dua laboratorium R",
            "enam dari delapan unit",
            "17 dari 25 latihan beserta solusi",
            "29 dari 35 sel sumber Python",
            "dua unit QuantEcon berikutnya",
            "Semigrup dan Generator",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 24:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "19 unit teori Random Services",
            "tujuh unit teori QuantEcon",
            "dua laboratorium R",
            "tujuh dari delapan unit",
            "22 dari 25 latihan beserta solusi",
            "29 dari 35 sel sumber Python",
            "satu unit QuantEcon berikutnya",
            "Semigrup Markov yang Kontinu Seragam",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 25:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "19 unit teori Random Services",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Stasioneritas dan Ergodisitas",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 26:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "20 unit teori Random Services",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Proses Poisson pada Ruang Umum",
            "enam latihan beserta jawaban",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 27:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "21 unit teori Random Services",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Gerak Brown Standar",
            "satu latihan komputasi beserta solusi asli edisi",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 28:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        if pdf_receipt["pages"] != 289:
            raise RuntimeError(
                "checkpoint 28 PDF page count mismatch: "
                f"expected 289, observed {pdf_receipt['pages']!r}"
            )
        for phrase in (
            "22 unit teori Random Services",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Gerak Brown dengan Drift",
            "satu latihan penguasaan beserta petunjuk dan solusi asli edisi",
            "289 halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 29:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "23 unit teori Random Services",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Jembatan Brown",
            "satu laboratorium luring deterministik",
            "satu latihan penguasaan beserta petunjuk dan solusi asli edisi",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 30:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "24 unit teori Random Services",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Gerak Brown geometrik",
            "satu laboratorium luring deterministik",
            "satu latihan penguasaan beserta petunjuk dan solusi asli edisi",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 31:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "24 unit teori Random Services",
            "tiga halaman ikhtisar Random Services",
            "27 dari 27 halaman Random Services yang dipilih",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Ikhtisar Martingal",
            "Ikhtisar Proses Markov",
            "Ikhtisar Gerak Brown",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 32:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "24 unit teori Random Services",
            "tiga halaman ikhtisar Random Services",
            "27 dari 27 halaman Random Services yang dipilih",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Konstruksi Kolmogorov dan proses kanonik",
            "tiga latihan penguasaan",
            "enam petunjuk progresif",
            "tiga jawaban ringkas",
            "tiga penyelesaian lengkap",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 33:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "24 unit teori Random Services",
            "tiga halaman ikhtisar Random Services",
            "27 dari 27 halaman Random Services yang dipilih",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Konstruksi Kolmogorov dan proses kanonik",
            "Keterukuran proses dan hukum lintasan",
            "enam latihan penguasaan",
            "dua belas petunjuk progresif",
            "enam jawaban ringkas",
            "enam penyelesaian lengkap",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 34:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "24 unit teori Random Services",
            "tiga halaman ikhtisar Random Services",
            "27 dari 27 halaman Random Services yang dipilih",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Konstruksi Kolmogorov dan proses kanonik",
            "Keterukuran proses dan hukum lintasan",
            "Distribusi bersyarat reguler dan disiplin versi",
            "sembilan latihan penguasaan",
            "delapan belas petunjuk progresif",
            "sembilan jawaban ringkas",
            "sembilan penyelesaian lengkap",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 35:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "24 unit teori Random Services",
            "tiga halaman ikhtisar Random Services",
            "27 dari 27 halaman Random Services yang dipilih",
            "delapan unit teori QuantEcon",
            "dua laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Konstruksi Kolmogorov dan proses kanonik",
            "Keterukuran proses dan hukum lintasan",
            "Distribusi bersyarat reguler dan disiplin versi",
            "Audit hipotesis untuk proses stokastik",
            "dua belas latihan penguasaan",
            "dua puluh empat petunjuk progresif",
            "dua belas jawaban ringkas",
            "dua belas penyelesaian lengkap",
            "340 halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 36:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "24 unit teori Random Services",
            "tiga halaman ikhtisar Random Services",
            "27 dari 27 halaman Random Services yang dipilih",
            "delapan unit teori QuantEcon",
            "empat laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Konstruksi Kolmogorov dan proses kanonik",
            "Keterukuran proses dan hukum lintasan",
            "Distribusi bersyarat reguler dan disiplin versi",
            "Audit hipotesis untuk proses stokastik",
            "Mode konvergensi dan pembanding LLN/CLT",
            "Nilai harapan bersyarat, filtrasi, dan penghentian opsional",
            "lima belas blok latihan",
            "dua puluh sembilan petunjuk",
            "empat belas jawaban ringkas",
            "lima belas penyelesaian lengkap",
            "14 dari 36 masalah penguasaan terpecahkan",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 37:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in (
            "24 unit teori Random Services",
            "tiga halaman ikhtisar Random Services",
            "27 dari 27 halaman Random Services yang dipilih",
            "delapan unit teori QuantEcon",
            "lima laboratorium R",
            "delapan dari delapan unit",
            "25 dari 25 latihan beserta solusi",
            "33 dari 33 sel sumber Python",
            "34 sel kode notebook",
            "Konstruksi Kolmogorov dan proses kanonik",
            "Keterukuran proses dan hukum lintasan",
            "Distribusi bersyarat reguler dan disiplin versi",
            "Audit hipotesis untuk proses stokastik",
            "Mode konvergensi dan pembanding LLN/CLT",
            "Nilai harapan bersyarat, filtrasi, dan penghentian opsional",
            "Gerak Brown: Donsker, variasi kuadratik, dan waktu kena",
            "enam belas blok latihan",
            "tiga puluh dua petunjuk",
            "lima belas jawaban ringkas",
            "enam belas penyelesaian lengkap",
            "15 dari 36 masalah penguasaan terpecahkan",
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
    elif checkpoint == 38:
        pdf_path = ROOT / "output" / "pdf" / artifact_names(checkpoint)["pdf"]
        pdf_receipt = checkpoint_pdf_receipt(checkpoint, pdf_path)
        for phrase in CHECKPOINT_38_METADATA_COVERAGE + (
            f"{pdf_receipt['pages']} halaman",
        ):
            if not has_exact_disclosure_phrase(folded, phrase.casefold()):
                raise RuntimeError(f"checkpoint coverage disclosure omits {phrase!r}")
        validate_checkpoint_38_coverage(folded)
        completion_evidence = validate_checkpoint_38_completion_evidence()
    else:
        raise RuntimeError(
            f"checkpoint {checkpoint} has no explicit metadata coverage policy"
        )

    conceptrecid = str(receipt.get("conceptrecid") or "")
    if conceptrecid != EXPECTED_CONCEPTRECID:
        raise RuntimeError("latest receipt is not the mandated O009 Zenodo concept")

    return {
        "body": body,
        "publication_date": publication_date,
        "previous_checkpoint": previous_checkpoint,
        "previous_record_id": receipt.get("record_id"),
        "conceptrecid": conceptrecid,
        "skipped_unpublished_checkpoints": skipped_checkpoints,
        "pdf_receipt": pdf_receipt,
        "completion_evidence": completion_evidence,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checkpoint_38_safe_file(base: Path, relative: str, context: str) -> Path:
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or re.match(r"(?i)^[A-Z]:", relative)
    ):
        raise RuntimeError(f"{context} has an unsafe relative path: {relative!r}")
    parsed = Path(relative)
    if parsed.is_absolute() or any(part in {"", ".", ".."} for part in parsed.parts):
        raise RuntimeError(f"{context} has an unsafe relative path: {relative!r}")
    candidate = base / parsed
    if not candidate.is_file():
        raise RuntimeError(f"{context} file is missing: {candidate}")
    return candidate


def _checkpoint_38_sha256_lines(values: set[str] | list[str] | tuple[str, ...]) -> str:
    payload = ("\n".join(sorted(values)) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _checkpoint_38_unique_json(text: str, context: str) -> object:
    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError(f"{context} contains duplicate JSON key {key!r}")
            result[key] = value
        return result

    return json.loads(text, object_pairs_hook=unique_object)


def _checkpoint_38_exact_nonnegative_int(value: object, context: str) -> int:
    if type(value) is not int or value < 0:
        raise RuntimeError(f"{context} must be a nonnegative integer")
    return value


def validate_checkpoint_38_completion_evidence() -> dict:
    """Derive the complete-course claim from admitted reader/backend bytes.

    This deliberately does not trust release prose or a hard-coded manifest
    count.  The reader receipt binds every supplemental source/output pair;
    the backend manifest binds the normalized entities and relations; and the
    checks below derive the 36 solved mastery items and the equivalence of the
    two cumulative forms from those exact records.
    """

    build_receipt_path = ROOT / "build" / "site" / "BUILD_RECEIPT.json"
    build_manifest_path = ROOT / "build" / "site" / "PACKAGE_MANIFEST.csv"
    backend_manifest_path = ROOT / "backend" / "BACKEND_MANIFEST.json"
    for required in (build_receipt_path, build_manifest_path, backend_manifest_path):
        if not required.is_file():
            raise RuntimeError(f"checkpoint-38 completion evidence is missing: {required}")

    build_receipt = _checkpoint_38_unique_json(
        build_receipt_path.read_text(encoding="utf-8"), "reader build receipt"
    )
    if not isinstance(build_receipt, dict):
        raise RuntimeError("checkpoint-38 reader build receipt is not a JSON object")
    if build_receipt.get("schema") != "o009.reader-build.v2":
        raise RuntimeError("checkpoint-38 reader build receipt schema mismatch")

    build_manifest_rows: dict[str, dict[str, str]] = {}
    with build_manifest_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["path", "bytes", "sha256"]:
            raise RuntimeError("checkpoint-38 reader manifest header differs")
        for row in reader:
            if None in row or set(row) != {"path", "bytes", "sha256"}:
                raise RuntimeError("checkpoint-38 reader manifest has extra columns")
            name = row.get("path")
            if not name or name in build_manifest_rows:
                raise RuntimeError("checkpoint-38 reader manifest has a duplicate path")
            path = _checkpoint_38_safe_file(
                ROOT / "build" / "site", name, "reader manifest"
            )
            try:
                expected_bytes = int(row.get("bytes") or "")
            except ValueError as exc:
                raise RuntimeError(
                    f"reader manifest has an invalid byte count: {name}"
                ) from exc
            if str(expected_bytes) != row.get("bytes") or expected_bytes < 0:
                raise RuntimeError(f"reader manifest byte count is noncanonical: {name}")
            if path.stat().st_size != expected_bytes:
                raise RuntimeError(f"reader manifest byte identity differs: {name}")
            if sha256_file(path) != row.get("sha256"):
                raise RuntimeError(f"reader manifest hash identity differs: {name}")
            build_manifest_rows[name] = row
    manifest_file_count = _checkpoint_38_exact_nonnegative_int(
        build_receipt.get("file_count"), "reader receipt file_count"
    )
    manifest_total_bytes = _checkpoint_38_exact_nonnegative_int(
        build_receipt.get("total_bytes"), "reader receipt total_bytes"
    )
    if (
        build_receipt.get("manifest_sha256") != sha256_file(build_manifest_path)
        or manifest_file_count != len(build_manifest_rows)
        or manifest_total_bytes
        != sum(int(row["bytes"]) for row in build_manifest_rows.values())
    ):
        raise RuntimeError("reader receipt does not bind the exact reader manifest census")

    backend_manifest = _checkpoint_38_unique_json(
        backend_manifest_path.read_text(encoding="utf-8"), "backend manifest"
    )
    if not isinstance(backend_manifest, dict):
        raise RuntimeError("checkpoint-38 backend manifest is not a JSON object")
    if backend_manifest.get("schema") != "o009.backend-manifest.v2":
        raise RuntimeError("checkpoint-38 backend manifest schema mismatch")
    if backend_manifest.get("qa_failures") != []:
        raise RuntimeError("checkpoint-38 backend manifest contains QA failures")
    if backend_manifest.get("build_receipt_sha256") != sha256_file(build_receipt_path):
        raise RuntimeError("backend manifest does not bind the current reader receipt")
    if backend_manifest.get("build_manifest_sha256") != sha256_file(build_manifest_path):
        raise RuntimeError("backend manifest does not bind the current reader manifest")

    backend_rows = backend_manifest.get("files")
    if not isinstance(backend_rows, list) or not backend_rows:
        raise RuntimeError("backend manifest has no file inventory")
    backend_by_name: dict[str, dict] = {}
    for row in backend_rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise RuntimeError("backend manifest contains a malformed file row")
        name = row.get("path")
        if not isinstance(name, str) or name in backend_by_name:
            raise RuntimeError("backend manifest file paths are malformed or duplicated")
        path = _checkpoint_38_safe_file(ROOT / "backend", name, "backend manifest")
        expected_bytes = _checkpoint_38_exact_nonnegative_int(
            row.get("bytes"), f"backend manifest byte count for {name}"
        )
        if path.stat().st_size != expected_bytes or sha256_file(path) != row.get("sha256"):
            raise RuntimeError(f"backend manifest byte identity differs: {name}")
        backend_by_name[name] = row
    actual_backend_files = {
        path.name
        for path in (ROOT / "backend").iterdir()
        if path.is_file() and path.name != "BACKEND_MANIFEST.json"
    }
    if set(backend_by_name) != actual_backend_files:
        raise RuntimeError("backend manifest does not exactly inventory the backend directory")
    for required_name in ("entities.jsonl", "relations.csv"):
        if required_name not in backend_by_name:
            raise RuntimeError(f"backend manifest omits {required_name}")

    supplement_rows = build_receipt.get("supplement_units")
    if not isinstance(supplement_rows, list):
        raise RuntimeError("reader receipt has no supplemental-unit evidence")
    expected_mastery_sources = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "source" / "mastery").glob("*.md")
        if path.is_file()
    }
    expected_assessment_sources = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "source" / "assessments").glob("*.md")
        if path.is_file()
    }
    if len(expected_mastery_sources) != 14 or len(expected_assessment_sources) != 2:
        raise RuntimeError("checkpoint-38 source-page inventory is not exactly 14 mastery plus 2 assessment files")
    observed_supplement_sources: dict[str, set[str]] = {
        "mastery": set(),
        "assessment": set(),
    }
    observed_supplement_outputs: set[str] = set()
    for row in supplement_rows:
        if not isinstance(row, dict):
            raise RuntimeError("reader receipt contains a malformed supplemental-unit row")
        kind = row.get("kind")
        source = row.get("source")
        output = row.get("output")
        if kind not in observed_supplement_sources or not isinstance(source, str) or not isinstance(output, str):
            raise RuntimeError("reader receipt contains an unidentified supplemental unit")
        if source in observed_supplement_sources[kind] or output in observed_supplement_outputs:
            raise RuntimeError("reader receipt duplicates a supplemental source or output")
        source_path = _checkpoint_38_safe_file(ROOT, source, "supplemental source")
        output_path = _checkpoint_38_safe_file(ROOT / "build" / "site", output, "supplemental output")
        if sha256_file(source_path) != row.get("source_sha256"):
            raise RuntimeError(f"reader receipt source hash is stale: {source}")
        if sha256_file(output_path) != row.get("target_sha256"):
            raise RuntimeError(f"reader receipt output hash is stale: {output}")
        observed_supplement_sources[kind].add(source)
        observed_supplement_outputs.add(output)
    if observed_supplement_sources["mastery"] != expected_mastery_sources:
        raise RuntimeError("reader receipt does not exactly bind the 14 mastery source pages")
    if observed_supplement_sources["assessment"] != expected_assessment_sources:
        raise RuntimeError("reader receipt does not exactly bind the two assessment source pages")

    bridge_rows = build_receipt.get("original_bridge_units")
    if not isinstance(bridge_rows, list) or len(bridge_rows) != 4:
        raise RuntimeError("reader receipt does not bind exactly four original bridges")
    bridge_outputs: set[str] = set()
    bridge_mastery_count = 0
    for row in bridge_rows:
        if not isinstance(row, dict):
            raise RuntimeError("reader receipt contains a malformed original-bridge row")
        source = row.get("source")
        output = row.get("output")
        counts = row.get("mastery_counts")
        if not isinstance(source, str) or not isinstance(output, str) or not isinstance(counts, dict):
            raise RuntimeError("original-bridge receipt row lacks source/output/mastery evidence")
        if output in bridge_outputs:
            raise RuntimeError("reader receipt duplicates an original-bridge output")
        source_path = _checkpoint_38_safe_file(ROOT, source, "original-bridge source")
        output_path = _checkpoint_38_safe_file(ROOT / "build" / "site", output, "original-bridge output")
        source_bytes = _checkpoint_38_exact_nonnegative_int(
            row.get("source_bytes"), f"original-bridge source byte count for {source}"
        )
        if source_path.stat().st_size != source_bytes or sha256_file(source_path) != row.get("source_sha256"):
            raise RuntimeError(f"original-bridge source identity differs: {source}")
        if sha256_file(output_path) != row.get("output_sha256"):
            raise RuntimeError(f"original-bridge output identity differs: {output}")
        expected_counts = {"answers": 3, "exercises": 3, "hints": 6, "solutions": 3}
        if (
            set(counts) != set(expected_counts)
            or any(type(counts[key]) is not int for key in expected_counts)
            or counts != expected_counts
        ):
            raise RuntimeError(f"original bridge lacks its exact three solved mastery items: {output}")
        bridge_mastery_count += counts["exercises"]
        bridge_outputs.add(output)
    if bridge_mastery_count != 12:
        raise RuntimeError("original-bridge mastery total is not 12")

    brown_output_by_exercise = {
        "unit.o009.original.brown.drift.mastery.exercise": "brown/Drift.html",
        "unit.o009.original.brown.bridge.mastery.exercise": "brown/Bridge.html",
        "unit.o009.original.brown.geometric.mastery.exercise": "brown/Geometric.html",
    }
    theory_unit_rows = build_receipt.get("theory_units")
    if not isinstance(theory_unit_rows, list):
        raise RuntimeError("reader receipt has no theory-unit evidence")
    theory_rows: dict[str, dict] = {}
    for row in theory_unit_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("reader receipt has a malformed theory-unit row")
        output = row["path"]
        if output in theory_rows:
            raise RuntimeError(f"reader receipt duplicates theory output: {output}")
        theory_rows[output] = row
    for output in brown_output_by_exercise.values():
        if output not in theory_rows:
            raise RuntimeError(f"reader receipt omits Brown mastery carrier: {output}")
        manifest_row = build_manifest_rows.get(output)
        if manifest_row is None:
            raise RuntimeError(f"reader manifest omits Brown mastery carrier: {output}")
        output_path = _checkpoint_38_safe_file(
            ROOT / "build" / "site", output, "Brown mastery carrier"
        )
        if sha256_file(output_path) != manifest_row.get("sha256"):
            raise RuntimeError(f"final Brown mastery carrier hash differs: {output}")

    entities_path = ROOT / "backend" / "entities.jsonl"
    entities: dict[str, dict] = {}
    with entities_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise RuntimeError(f"blank backend entity row at line {line_number}")
            row = _checkpoint_38_unique_json(
                line, f"backend entity line {line_number}"
            )
            if not isinstance(row, dict):
                raise RuntimeError(f"backend entity line {line_number} is not an object")
            entity_id = row.get("id")
            if not isinstance(entity_id, str) or not entity_id or entity_id in entities:
                raise RuntimeError(f"malformed or duplicate backend entity at line {line_number}")
            entities[entity_id] = row

    def unit_kind(entity_id: str) -> str | None:
        row = entities.get(entity_id) or {}
        return (row.get("payload") or {}).get("unit_kind")

    def is_descendant_of(entity_id: str, ancestor_id: str) -> bool:
        """Prove containment through the explicit backend parent chain."""
        seen: set[str] = set()
        current = entity_id
        while current in entities and current not in seen:
            seen.add(current)
            parent = entities[current].get("parent_id")
            if parent == ancestor_id:
                return True
            if not isinstance(parent, str) or not parent:
                return False
            current = parent
        return False

    def admitted_authored_unit(
        entity_id: str,
        expected_kind: str,
        *,
        parent_id: str | None = None,
        path: str | None = None,
        rights_id: str | None = None,
        translation_states: tuple[str, ...] = ("authored",),
    ) -> dict:
        row = entities.get(entity_id)
        if row is None or row.get("record_type") != "unit":
            raise RuntimeError(f"backend omits admitted unit: {entity_id}")
        payload = row.get("payload")
        if not isinstance(payload, dict) or payload.get("unit_kind") != expected_kind:
            raise RuntimeError(f"backend unit kind differs: {entity_id}")
        body_extent = payload.get("body_extent")
        if (
            row.get("status") != "active"
            or row.get("locale") != "id-ID"
            or row.get("source_target_relationship") != "authored"
            or row.get("translation_state") not in translation_states
            or not isinstance(row.get("rights_id"), str)
            or not row.get("rights_id")
            or not isinstance(body_extent, str)
            or not body_extent.startswith("complete-")
            or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("source_sha256") or ""))
            or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("target_sha256") or ""))
        ):
            raise RuntimeError(
                f"backend unit lacks active complete id-ID authored/rights/hash binding: {entity_id}"
            )
        if parent_id is not None and row.get("parent_id") != parent_id:
            raise RuntimeError(f"backend unit parent differs: {entity_id}")
        if path is not None and row.get("path") != path:
            raise RuntimeError(f"backend unit path differs: {entity_id}")
        if rights_id is not None and row.get("rights_id") != rights_id:
            raise RuntimeError(f"backend unit rights differ: {entity_id}")
        entity_path = str(row.get("path") or "")
        source_file_sha256 = payload.get("source_file_sha256")
        if entity_path.startswith("source/"):
            source_path = _checkpoint_38_safe_file(ROOT, entity_path, "backend source")
            if source_file_sha256 != sha256_file(source_path):
                raise RuntimeError(f"backend unit is stale relative to source: {entity_id}")
        elif source_file_sha256 is not None:
            raise RuntimeError(f"build-addition unit has an unexpected source-file hash: {entity_id}")
        return row

    source_mastery_exercises: set[str] = set()
    bridge_mastery_exercises: set[str] = set()
    brown_mastery_exercises: set[str] = set()
    for entity_id, row in entities.items():
        if row.get("record_type") != "unit" or unit_kind(entity_id) != "exercise":
            continue
        path = str(row.get("path") or "")
        if path in observed_supplement_sources["mastery"]:
            source_mastery_exercises.add(entity_id)
        elif path in bridge_outputs and entity_id.startswith("unit.o009.original.mastery."):
            bridge_mastery_exercises.add(entity_id)
        if entity_id in CHECKPOINT_38_BROWN_MASTERY_EXERCISE_IDS:
            if path != brown_output_by_exercise[entity_id]:
                raise RuntimeError(f"Brown mastery entity path differs: {entity_id}")
            brown_mastery_exercises.add(entity_id)
    if len(source_mastery_exercises) != 21:
        raise RuntimeError("backend does not contain exactly 21 new mastery exercises")
    if len(bridge_mastery_exercises) != 12:
        raise RuntimeError("backend does not contain exactly 12 original-bridge mastery exercises")
    if brown_mastery_exercises != CHECKPOINT_38_BROWN_MASTERY_EXERCISE_IDS:
        raise RuntimeError("backend does not contain the exact three admitted Brown mastery exercises")
    mastery_exercises = (
        source_mastery_exercises | bridge_mastery_exercises | brown_mastery_exercises
    )
    if len(mastery_exercises) != 36:
        raise RuntimeError("derived mastery exercise inventory is not exactly 36")
    for exercise_id in mastery_exercises:
        admitted_authored_unit(
            exercise_id,
            "exercise",
            translation_states=(
                ("built",) if exercise_id in bridge_mastery_exercises else ("authored",)
            ),
        )

    relations_path = ROOT / "backend" / "relations.csv"
    incoming: dict[tuple[str, str], list[str]] = {}
    outgoing: dict[tuple[str, str], list[str]] = {}
    relation_ids: set[str] = set()
    semantic_edges: set[tuple[str, str, str, str]] = set()
    with relations_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_fields = [
            "relation_id",
            "relation_type",
            "source_id",
            "target_id",
            "evidence",
            "status",
        ]
        if reader.fieldnames != expected_fields:
            raise RuntimeError("backend relation header differs from the admitted schema")
        for row in reader:
            if None in row or set(row) != set(expected_fields):
                raise RuntimeError("backend relation row has extra columns")
            relation_id = row.get("relation_id")
            if not relation_id or relation_id in relation_ids:
                raise RuntimeError("backend contains a malformed or duplicate relation ID")
            relation_ids.add(relation_id)
            semantic_edge = (
                str(row.get("relation_type") or ""),
                str(row.get("source_id") or ""),
                str(row.get("target_id") or ""),
                str(row.get("status") or ""),
            )
            if semantic_edge in semantic_edges:
                raise RuntimeError("backend contains a duplicate semantic relation edge")
            semantic_edges.add(semantic_edge)
            if row.get("status") != "active":
                continue
            relation_type = str(row.get("relation_type") or "")
            source_id = str(row.get("source_id") or "")
            target_id = str(row.get("target_id") or "")
            incoming.setdefault((target_id, relation_type), []).append(source_id)
            outgoing.setdefault((source_id, relation_type), []).append(target_id)

    solved_mastery: set[str] = set()
    for exercise_id in mastery_exercises:
        exercise = entities[exercise_id]
        exercise_parent = str(exercise.get("parent_id") or "")
        exercise_path = str(exercise.get("path") or "")
        exercise_rights = str(exercise.get("rights_id") or "")
        admitted_translation_states = (
            ("built",) if exercise_id in bridge_mastery_exercises else ("authored",)
        )
        solvers = incoming.get((exercise_id, "solves"), [])
        hinters = incoming.get((exercise_id, "hints"), [])
        assess_targets = outgoing.get((exercise_id, "assesses"), [])
        if len(solvers) != 1:
            raise RuntimeError(f"mastery exercise lacks exactly one worked solution: {exercise_id}")
        admitted_authored_unit(
            solvers[0],
            "solution",
            parent_id=exercise_parent,
            path=exercise_path,
            rights_id=exercise_rights,
            translation_states=admitted_translation_states,
        )
        if not hinters or len(hinters) != len(set(hinters)):
            raise RuntimeError(f"mastery exercise lacks an admitted progressive hint: {exercise_id}")
        for hint_id in hinters:
            admitted_authored_unit(
                hint_id,
                "hint",
                parent_id=exercise_parent,
                path=exercise_path,
                rights_id=exercise_rights,
                translation_states=admitted_translation_states,
            )
        if (
            not assess_targets
            or len(assess_targets) != len(set(assess_targets))
            or any(
                target not in entities or not target.startswith("outcome.o009.")
                for target in assess_targets
            )
        ):
            raise RuntimeError(f"mastery exercise lacks an admitted outcome binding: {exercise_id}")
        if exercise_id not in brown_mastery_exercises:
            answers = incoming.get((exercise_id, "answers"), [])
            if len(answers) != 1:
                raise RuntimeError(f"mastery exercise lacks exactly one concise answer: {exercise_id}")
            admitted_authored_unit(
                answers[0],
                "answer",
                parent_id=exercise_parent,
                path=exercise_path,
                rights_id=exercise_rights,
                translation_states=admitted_translation_states,
            )
        solved_mastery.add(exercise_id)
    if len(solved_mastery) != 36:
        raise RuntimeError("backend solution relations do not prove 36 solved mastery problems")

    expected_form_paths = {
        CHECKPOINT_38_FORM_IDS[0]: "source/assessments/01-formulir-kumulatif-a.md",
        CHECKPOINT_38_FORM_IDS[1]: "source/assessments/02-formulir-kumulatif-b.md",
    }
    expected_alternates = {
        CHECKPOINT_38_FORM_IDS[0]: CHECKPOINT_38_FORM_IDS[1],
        CHECKPOINT_38_FORM_IDS[1]: CHECKPOINT_38_FORM_IDS[0],
    }
    point_vectors: dict[str, list[int]] = {}
    outcome_blueprints: dict[str, dict[int, list[str]]] = {}
    for form_index, form_id in enumerate(CHECKPOINT_38_FORM_IDS):
        form = admitted_authored_unit(
            form_id, "assessment", path=expected_form_paths[form_id]
        )
        assessment = ((form.get("payload") or {}).get("front_matter") or {}).get("assessment")
        expected_metadata = {
            "course_id": "course.o009.d30",
            "assessment_id": form_id,
            "alternate_of": expected_alternates[form_id],
            "form": "A" if form_index == 0 else "B",
            "version": "1.0.0",
            "total_points": 100,
            "recommended_time_minutes": 240,
            "target_locale": "id-ID",
            "rights_id": f"rights.o009.assessment.cumulative.form-{'a' if form_index == 0 else 'b'}.cc-by-4.0",
            "license": "CC-BY-4.0",
            "model_disclosure": MODEL_PROVENANCE,
        }
        if assessment != expected_metadata:
            raise RuntimeError(f"assessment front matter differs from the equivalence contract: {form_id}")
        source_file = ROOT / expected_form_paths[form_id]
        if (form.get("payload") or {}).get("source_file_sha256") != sha256_file(source_file):
            raise RuntimeError(f"assessment backend entity is stale relative to source: {form_id}")
        problem_ids = [f"{form_id}.problem.{number:02d}" for number in range(1, 9)]
        observed_problem_ids = {
            entity_id
            for entity_id, row in entities.items()
            if row.get("record_type") == "unit"
            and unit_kind(entity_id) == "assessment-problem"
            and entity_id.startswith(form_id + ".problem.")
        }
        if observed_problem_ids != set(problem_ids):
            raise RuntimeError(f"assessment form does not contain exactly problems 01-08: {form_id}")
        point_vector: list[int] = []
        blueprint: dict[int, list[str]] = {}
        for number, problem_id in enumerate(problem_ids, start=1):
            problem = admitted_authored_unit(
                problem_id,
                "assessment-problem",
                path=expected_form_paths[form_id],
                rights_id=str(form.get("rights_id") or ""),
            )
            if not is_descendant_of(problem_id, form_id):
                raise RuntimeError(
                    f"assessment problem is not contained by its form: {problem_id}"
                )
            match = re.search(r"\((\d+) poin\)\s*$", str((problem.get("payload") or {}).get("title") or ""))
            if match is None:
                raise RuntimeError(f"assessment problem lacks a point value: {problem_id}")
            point_vector.append(int(match.group(1)))
            children = [
                row_id
                for row_id, row in entities.items()
                if row.get("record_type") == "unit" and row.get("parent_id") == problem_id
            ]
            children_by_kind: dict[str, list[str]] = {}
            for child_id in children:
                child_kind = unit_kind(child_id)
                if isinstance(child_kind, str):
                    children_by_kind.setdefault(child_kind, []).append(child_id)
            required_child_counts = {"rubric": 1, "hint": 2, "answer": 1, "solution": 1}
            for child_kind, expected_count in required_child_counts.items():
                child_ids = children_by_kind.get(child_kind, [])
                if len(child_ids) != expected_count or len(child_ids) != len(set(child_ids)):
                    raise RuntimeError(
                        f"assessment problem {problem_id} lacks exact {child_kind} closure"
                    )
                for child_id in child_ids:
                    admitted_authored_unit(
                        child_id,
                        child_kind,
                        parent_id=problem_id,
                        path=expected_form_paths[form_id],
                        rights_id=str(form.get("rights_id") or ""),
                    )
            if incoming.get((problem_id, "solves"), []) != children_by_kind["solution"]:
                raise RuntimeError(f"assessment problem lacks one solution relation: {problem_id}")
            if incoming.get((problem_id, "answers"), []) != children_by_kind["answer"]:
                raise RuntimeError(f"assessment problem lacks one answer relation: {problem_id}")
            if sorted(incoming.get((problem_id, "hints"), [])) != sorted(
                children_by_kind["hint"]
            ):
                raise RuntimeError(f"assessment problem lacks two hint relations: {problem_id}")
            outcomes = sorted(set(outgoing.get((problem_id, "assesses"), [])))
            if not outcomes or any(
                not outcome.startswith("outcome.o009.") or outcome not in entities
                for outcome in outcomes
            ):
                raise RuntimeError(f"assessment problem lacks O009 outcome coverage: {problem_id}")
            blueprint[number] = outcomes
        if sum(point_vector) != assessment["total_points"]:
            raise RuntimeError(f"assessment problem points do not total 100: {form_id}")
        point_vectors[form_id] = point_vector
        outcome_blueprints[form_id] = blueprint
        alternate_targets = sorted(outgoing.get((form_id, "alternate-form"), []))
        if alternate_targets != [expected_alternates[form_id]]:
            raise RuntimeError(f"assessment alternate-form relation is not reciprocal: {form_id}")

    if point_vectors[CHECKPOINT_38_FORM_IDS[0]] != point_vectors[CHECKPOINT_38_FORM_IDS[1]]:
        raise RuntimeError("assessment forms do not have the same point blueprint")
    if outcome_blueprints[CHECKPOINT_38_FORM_IDS[0]] != outcome_blueprints[CHECKPOINT_38_FORM_IDS[1]]:
        raise RuntimeError("assessment forms do not have the same outcome blueprint")
    common_outcomes = {
        outcome
        for outcomes in outcome_blueprints[CHECKPOINT_38_FORM_IDS[0]].values()
        for outcome in outcomes
    }
    if len(common_outcomes) != 26:
        raise RuntimeError("assessment equivalence blueprint does not cover exactly 26 outcomes")

    return {
        "schema": "o009.checkpoint-38-completion-evidence.v1",
        "build_receipt": {
            "path": "build/site/BUILD_RECEIPT.json",
            "sha256": sha256_file(build_receipt_path),
        },
        "reader_manifest": {
            "path": "build/site/PACKAGE_MANIFEST.csv",
            "sha256": sha256_file(build_manifest_path),
            "file_count": len(build_manifest_rows),
        },
        "backend_manifest": {
            "path": "backend/BACKEND_MANIFEST.json",
            "sha256": sha256_file(backend_manifest_path),
            "input_set_sha256": backend_manifest.get("input_set_sha256"),
        },
        "mastery": {
            "problem_count": len(mastery_exercises),
            "solved_problem_count": len(solved_mastery),
            "source_mastery_problem_count": len(source_mastery_exercises),
            "original_bridge_problem_count": len(bridge_mastery_exercises),
            "brown_reader_problem_count": len(brown_mastery_exercises),
            "problem_ids_sha256": _checkpoint_38_sha256_lines(mastery_exercises),
        },
        "assessments": {
            "form_count": len(CHECKPOINT_38_FORM_IDS),
            "equivalent": True,
            "problem_count_per_form": 8,
            "total_points_per_form": 100,
            "recommended_time_minutes_per_form": 240,
            "common_outcome_count": len(common_outcomes),
            "equivalence_basis": (
                "reciprocal alternate-form relation plus identical ordered "
                "per-problem point and learning-outcome blueprints"
            ),
            "form_ids_sha256": _checkpoint_38_sha256_lines(CHECKPOINT_38_FORM_IDS),
            "outcome_blueprint_sha256": hashlib.sha256(
                json.dumps(
                    outcome_blueprints[CHECKPOINT_38_FORM_IDS[0]],
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
        },
    }


def checked_reader_files() -> list[Path]:
    site = ROOT / "build" / "site"
    manifest_path = site / "PACKAGE_MANIFEST.csv"
    files: list[Path] = []
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            path = site / row["path"]
            if not path.is_file():
                raise RuntimeError(f"reader manifest path missing: {row['path']}")
            if path.stat().st_size != int(row["bytes"]):
                raise RuntimeError(f"reader byte mismatch: {row['path']}")
            if sha256_file(path) != row["sha256"]:
                raise RuntimeError(f"reader hash mismatch: {row['path']}")
            files.append(path)
    files.extend([manifest_path, site / "BUILD_RECEIPT.json"])
    return sorted(set(files), key=lambda p: p.relative_to(site).as_posix())


def bounded_tree(relative: str) -> list[Path]:
    base = ROOT / relative
    if not base.is_dir():
        raise RuntimeError(f"required source directory missing: {relative}")
    return sorted(
        (
            path
            for path in base.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix.lower() not in {".pyc", ".pyo"}
        ),
        key=lambda p: p.relative_to(ROOT).as_posix(),
    )


def checkpoint_38_public_source_files() -> list[Path]:
    receipt_path = ROOT / "build" / "site" / "BUILD_RECEIPT.json"
    if not receipt_path.is_file():
        raise RuntimeError("checkpoint-38 source allowlist lacks the reader receipt")
    receipt = _checkpoint_38_unique_json(
        receipt_path.read_text(encoding="utf-8"), "reader build receipt"
    )
    if not isinstance(receipt, dict) or receipt.get("schema") != "o009.reader-build.v2":
        raise RuntimeError("checkpoint-38 source allowlist has no admitted reader receipt")

    expected = set(CHECKPOINT_38_PUBLIC_STATIC_SOURCE_PATHS)
    for row in receipt.get("supplement_units", []):
        if not isinstance(row, dict) or not isinstance(row.get("source"), str):
            raise RuntimeError("checkpoint-38 source allowlist found a malformed supplement")
        expected.add(row["source"])
    for row in receipt.get("original_bridge_units", []):
        if not isinstance(row, dict) or not isinstance(row.get("source"), str):
            raise RuntimeError("checkpoint-38 source allowlist found a malformed bridge")
        expected.add(row["source"])
    for row in receipt.get("theory_units", []):
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("checkpoint-38 source allowlist found a malformed theory unit")
        expected.add("source/theory/" + row["path"])
    for key in CHECKPOINT_38_QUANTECON_COMPONENT_KEYS:
        component = receipt.get(key)
        if not isinstance(component, dict) or not isinstance(
            component.get("source_path"), str
        ):
            raise RuntimeError(
                f"checkpoint-38 source allowlist lacks admitted component {key}"
            )
        expected.add(component["source_path"])

    actual = {
        path.relative_to(ROOT).as_posix(): path for path in bounded_tree("source")
    }
    exclusions = {
        path
        for path in CHECKPOINT_38_PUBLIC_SOURCE_EXCLUSIONS
        if path.startswith("source/")
    }
    unexpected = sorted(set(actual) - expected - exclusions)
    missing = sorted(expected - set(actual))
    if unexpected or missing:
        raise RuntimeError(
            "checkpoint-38 public source allowlist differs: "
            f"unexpected={unexpected}, missing={missing}"
        )
    for relative in expected:
        if Path(relative).suffix.lower() not in CHECKPOINT_38_PUBLIC_SOURCE_SUFFIXES:
            raise RuntimeError(
                f"checkpoint-38 public source has an unapproved suffix: {relative}"
            )
    return [actual[relative] for relative in sorted(expected)]


def checkpoint_38_named_files(relative: str, names: frozenset[str]) -> list[Path]:
    base = ROOT / relative
    if not base.is_dir():
        raise RuntimeError(f"checkpoint-38 allowlisted directory is missing: {relative}")
    paths = [base / name for name in sorted(names)]
    missing = [path.name for path in paths if not path.is_file()]
    if missing:
        raise RuntimeError(
            f"checkpoint-38 {relative} allowlist is missing required files: {missing}"
        )
    return paths


def checked_source_files(checkpoint: int) -> list[Path]:
    files: list[Path] = [ROOT / "README.md", ROOT / "LICENSES.md"]
    broad_roots = [
        "backend",
        "qa",
        "authority/random",
        "authority/zitkovic/witness",
        "authority/quantecon/build_baseline",
        "authority/quantecon/evidence",
        "authority/quantecon/notebook_snapshot",
        "authority/quantecon/source_snapshot",
    ]
    if checkpoint == 38:
        files.extend(checkpoint_38_public_source_files())
        files.extend(
            checkpoint_38_named_files(
                "scripts", CHECKPOINT_38_PUBLIC_SCRIPT_ALLOWLIST
            )
        )
        files.extend(
            checkpoint_38_named_files(
                "00_control", CHECKPOINT_38_PUBLIC_CONTROL_ALLOWLIST
            )
        )
    else:
        broad_roots.extend(["source", "scripts", "00_control"])
    for relative in broad_roots:
        files.extend(bounded_tree(relative))

    for relative in (
        "authority/quantecon/ACTIVE_INPUT_MANIFEST.tsv",
        "authority/quantecon/AUTHORITY_RECEIPT.json",
        "authority/quantecon/NOTEBOOK_MANIFEST.tsv",
        "authority/quantecon/SOURCE_MANIFEST.tsv",
        "authority/quantecon/environment/ENVIRONMENT_RECEIPT.json",
        "authority/quantecon/environment/WHEELHOUSE_MANIFEST.tsv",
        "authority/quantecon/environment/requirements.in",
        "authority/quantecon/environment/requirements.lock",
        "authority/quantecon/environment/requirements.resolved.txt",
        "build/site/BUILD_RECEIPT.json",
        "build/site/PACKAGE_MANIFEST.csv",
        "runtime/pdf-node/package.json",
        "runtime/pdf-node/package-lock.json",
    ):
        files.append(ROOT / relative)

    # Work on the next original bridge began while checkpoint 31 was rendering.
    # Keep that unfinished next-boundary material out of the checkpoint-31
    # source archive without deleting it; later checkpoints include it through
    # the ordinary bounded-tree inventory once it has passed admission gates.
    checkpoint_exclusions: dict[int, set[str]] = {
        31: {
            "source/original/01-konstruksi-kolmogorov.md",
            "qa/O009_ORIGINAL_BRIDGE_01_IMPLEMENTATION_PLAN_20260826.md",
        },
        36: {
            "source/labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.Rmd",
        },
    }
    excluded = set(checkpoint_exclusions.get(checkpoint, set()))
    if checkpoint == 38:
        excluded.update(CHECKPOINT_38_PUBLIC_SOURCE_EXCLUSIONS)
    # Keep future public source packages reader/reproducibility-first: old
    # raster/debug render trees and nested evidence archives are retained
    # locally and represented by their controlling QA/authority hashes, but
    # are not needed to rebuild the current reader.
    excluded_prefixes = (
        "qa/render/",
        # Historical raster/debug and terminology scratch trees are retained
        # locally as evidence but are not needed to rebuild the current reader.
        "qa/pdf_reader_checkpoint_14/",
        "qa/pdf_reader_checkpoint_14_final/",
        "qa/pdf_reader_checkpoint_15_final/",
        "qa/terminology_uad/",
    )
    excluded_evidence_archives = {
        path.relative_to(ROOT).as_posix()
        for path in bounded_tree("authority/quantecon/evidence")
        if path.suffix.lower() == ".zip"
    }
    files = [
        path
        for path in files
        if (
            path.relative_to(ROOT).as_posix() not in excluded
            and not any(
                path.relative_to(ROOT).as_posix().startswith(prefix)
                for prefix in excluded_prefixes
            )
            and path.relative_to(ROOT).as_posix() not in excluded_evidence_archives
        )
    ]

    if checkpoint == 38:
        packaged_relatives = {path.relative_to(ROOT).as_posix() for path in files}
        forbidden = sorted(packaged_relatives & CHECKPOINT_38_PUBLIC_SOURCE_EXCLUSIONS)
        if forbidden:
            raise RuntimeError(
                f"checkpoint-38 source package contains forbidden files: {forbidden}"
            )

    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        raise RuntimeError(f"required source-package files missing: {missing}")
    return sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_identity_tokens() -> set[str]:
    values = {
        Path.home().name,
        os.environ.get("USERNAME", ""),
        os.environ.get("USER", ""),
    }
    generic = {"home", "root", "user", "users", "owner", "admin"}
    return {
        value
        for value in values
        if re.fullmatch(r"[A-Za-z0-9._-]{4,64}", value or "")
        and value.casefold() not in generic
    }


def sanitize_public_text(
    data: bytes, identity_tokens: set[str]
) -> tuple[bytes, dict[str, int], set[str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data, {}, set()

    observed_identities = {
        match.group("identity")
        for pattern in (
            WINDOWS_ESCAPED_PROFILE_RE,
            WINDOWS_PROFILE_RE,
            WINDOWS_FORWARD_PROFILE_RE,
            POSIX_PROFILE_RE,
        )
        for match in pattern.finditer(text)
    }
    safe_observed = {
        value
        for value in observed_identities
        if re.fullmatch(r"[A-Za-z0-9._-]{2,64}", value or "")
    }
    all_identities = set(identity_tokens) | safe_observed
    counts: dict[str, int] = {}

    text, count = WINDOWS_ESCAPED_PROFILE_RE.subn(
        lambda match: "%USERPROFILE%" + match.group("trailing_separator"), text
    )
    if count:
        counts["windows_json_profile_prefix"] = count
    text, count = WINDOWS_PROFILE_RE.subn(
        lambda _match: "%USERPROFILE%" + "\\", text
    )
    if count:
        counts["windows_profile_prefix"] = count
    text, count = WINDOWS_FORWARD_PROFILE_RE.subn(
        lambda match: "%USERPROFILE%" + match.group("trailing_separator"), text
    )
    if count:
        counts["windows_forward_profile_prefix"] = count
    text, count = POSIX_PROFILE_RE.subn(
        lambda match: "$HOME" + match.group("trailing_separator"), text
    )
    if count:
        counts["posix_profile_prefix"] = count

    identity_replacements = 0
    for identity in sorted(all_identities, key=str.casefold):
        identity_re = re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(identity)}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        text, count = identity_re.subn("<LOCAL_USER>", text)
        identity_replacements += count
    if identity_replacements:
        counts["local_identity_token"] = identity_replacements
    return text.encode("utf-8"), counts, safe_observed


def source_archive_entries(
    entries: list[tuple[Path, str]],
) -> tuple[list[tuple[bytes, str]], dict[str, object], frozenset[str]]:
    identity_tokens = private_identity_tokens()
    raw_entries = [(source.read_bytes(), name) for source, name in entries]
    for original, _name in raw_entries:
        try:
            text = original.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in (
            WINDOWS_ESCAPED_PROFILE_RE,
            WINDOWS_PROFILE_RE,
            WINDOWS_FORWARD_PROFILE_RE,
            POSIX_PROFILE_RE,
        ):
            identity_tokens.update(
                match.group("identity")
                for match in pattern.finditer(text)
                if re.fullmatch(
                    r"[A-Za-z0-9._-]{2,64}", match.group("identity") or ""
                )
            )
    prepared: list[tuple[bytes, str]] = []
    sanitized_rows: list[dict[str, object]] = []
    for original, name in raw_entries:
        public, counts, observed = sanitize_public_text(original, identity_tokens)
        identity_tokens.update(observed)
        if public != original:
            sanitized_rows.append(
                {
                    "path": name,
                    "original_bytes": len(original),
                    "original_sha256": sha256_bytes(original),
                    "public_bytes": len(public),
                    "public_sha256": sha256_bytes(public),
                    "replacement_counts": counts,
                }
            )
        prepared.append((public, name))
    sanitized_rows.sort(key=lambda row: str(row["path"]))

    archive_roots = {name.split("/", 1)[0] for _, name in prepared}
    if len(archive_roots) != 1:
        raise RuntimeError("source archive does not have one bounded archive root")
    manifest_name = f"{next(iter(archive_roots))}/{PUBLIC_SANITIZATION_MANIFEST}"
    if any(name == manifest_name for _, name in prepared):
        raise RuntimeError("source sanitization manifest path collides with an input")
    sanitization_manifest = {
        "schema": "o009.public-source-sanitization.v1",
        "policy": (
            "Public text bytes replace absolute local profile prefixes and private "
            "identity tokens with portable placeholders; original local evidence "
            "remains unchanged and is identified only by cryptographic hash."
        ),
        "sanitized_entry_count": len(sanitized_rows),
        "sanitized_entries": sanitized_rows,
    }
    manifest_data = (
        json.dumps(
            sanitization_manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    prepared.append((manifest_data, manifest_name))
    summary = {
        "manifest_path": manifest_name,
        "manifest_sha256": sha256_bytes(manifest_data),
        "sanitized_entry_count": len(sanitized_rows),
        "actual_zip_inventory_and_content_scan": "required",
    }
    frozen_tokens = frozenset(identity_tokens)
    verify_public_source_entries(prepared, frozen_tokens)
    return prepared, summary, frozen_tokens


def verify_public_source_member(
    name: str, data: bytes, identity_tokens: frozenset[str]
) -> None:
    parts = name.split("/")
    if (
        name.startswith("/")
        or "\\" in name
        or re.match(r"(?i)^[A-Z]:", name)
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise RuntimeError(f"unsafe public source ZIP member name: {name!r}")
    if PROFILE_RESIDUE_BYTES_RE.search(data):
        raise RuntimeError(
            f"absolute profile-path residue remains in public source ZIP: {name}"
        )
    lowered = data.lower()
    for identity in identity_tokens:
        name_boundary = re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(identity)}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        if name_boundary.search(name):
            raise RuntimeError(
                f"private identity residue remains in public source ZIP name: {name}"
            )
        encoded = identity.encode("utf-8")
        boundary = re.compile(
            rb"(?<![A-Za-z0-9])" + re.escape(encoded) + rb"(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        if boundary.search(data) or identity.casefold().encode("utf-16le") in lowered:
            raise RuntimeError(
                f"private identity residue remains in public source ZIP: {name}"
            )


def verify_public_source_entries(
    entries: list[tuple[bytes, str]], identity_tokens: frozenset[str]
) -> None:
    for data, name in entries:
        verify_public_source_member(name, data, identity_tokens)


def verify_public_source_zip(
    archive: zipfile.ZipFile, identity_tokens: frozenset[str]
) -> None:
    for info in archive.infolist():
        verify_public_source_member(info.filename, archive.read(info), identity_tokens)


def write_zip(
    output: Path,
    entries: list[tuple[Path | bytes, str]],
    *,
    privacy_tokens: frozenset[str] | None = None,
) -> dict[str, int | str]:
    temporary = output.with_name(output.name + ".tmp")
    if temporary.exists():
        raise RuntimeError(f"stale temporary output requires review: {temporary}")
    uncompressed = 0
    with zipfile.ZipFile(
        temporary,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for source, name in sorted(entries, key=lambda item: item[1]):
            data = source if isinstance(source, bytes) else source.read_bytes()
            uncompressed += len(data)
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with zipfile.ZipFile(temporary, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP CRC verification failed at {bad}")
        names = archive.namelist()
        if names != sorted(names) or len(names) != len(set(names)):
            raise RuntimeError("ZIP entry order or uniqueness check failed")
        verified_uncompressed = sum(item.file_size for item in archive.infolist())
        if verified_uncompressed != uncompressed:
            raise RuntimeError("ZIP uncompressed-byte census mismatch")
        if privacy_tokens is not None:
            verify_public_source_zip(archive, privacy_tokens)

    temporary.replace(output)

    return {
        "filename": output.name,
        "bytes": output.stat().st_size,
        "sha256": sha256_file(output),
        "entry_count": len(entries),
        "uncompressed_bytes": uncompressed,
    }


def write_text_atomic(output: Path, content: str, encoding: str) -> None:
    temporary = output.with_name(output.name + ".tmp")
    if temporary.exists():
        raise RuntimeError(f"stale temporary output requires review: {temporary}")
    temporary.write_text(content, encoding=encoding, newline="\n")
    temporary.replace(output)


def copy_binary_atomic(
    source: Path, output: Path, expected_receipt: dict | None = None
) -> dict[str, int | str]:
    if not source.is_file():
        raise RuntimeError(f"required PDF reader missing: {source}")
    temporary = output.with_name(output.name + ".tmp")
    if temporary.exists():
        raise RuntimeError(f"stale temporary output requires review: {temporary}")
    temporary.write_bytes(source.read_bytes())
    if temporary.stat().st_size != source.stat().st_size:
        raise RuntimeError("PDF copy byte-count mismatch")
    if sha256_file(temporary) != sha256_file(source):
        raise RuntimeError("PDF copy SHA-256 mismatch")
    if expected_receipt is not None:
        if temporary.stat().st_size != int(expected_receipt.get("bytes", -1)):
            raise RuntimeError("copied PDF differs from the validated receipt byte count")
        if sha256_file(temporary) != expected_receipt.get("sha256"):
            raise RuntimeError("copied PDF differs from the validated receipt SHA-256")
    temporary.replace(output)
    return {
        "filename": output.name,
        "bytes": output.stat().st_size,
        "sha256": sha256_file(output),
        "kind": "combined_pdf_reader",
    }


def main() -> int:
    args = parse_args()
    names = artifact_names(args.checkpoint)
    metadata_path = RELEASE / names["metadata"]
    policy = validate_metadata_and_lineage(args.checkpoint, metadata_path)

    site = ROOT / "build" / "site"
    reader_files = checked_reader_files()
    reader_entries = [
        (path, f"reader/{path.relative_to(site).as_posix()}")
        for path in reader_files
    ]

    source_files = checked_source_files(args.checkpoint)
    raw_source_entries = [
        (
            path,
            "probabilitas-teoretis-ukuran-proses-stokastik-id/"
            + path.relative_to(ROOT).as_posix(),
        )
        for path in source_files
    ]
    source_entries, source_privacy, privacy_tokens = source_archive_entries(
        raw_source_entries
    )
    pdf_source = ROOT / "output" / "pdf" / names["pdf"]
    if not pdf_source.is_file():
        raise RuntimeError(f"required checkpoint PDF reader missing: {pdf_source}")

    if args.validate_only:
        print(
            json.dumps(
                {
                    "status": "LOCAL_INPUTS_VALID",
                    "checkpoint": args.checkpoint,
                    "previous_checkpoint": policy["previous_checkpoint"],
                    "previous_record_id": policy["previous_record_id"],
                    "conceptrecid": policy["conceptrecid"],
                    "skipped_unpublished_checkpoints": policy[
                        "skipped_unpublished_checkpoints"
                    ],
                    "reader_entry_count": len(reader_entries),
                    "source_entry_count": len(source_entries),
                    "source_sanitized_entry_count": source_privacy[
                        "sanitized_entry_count"
                    ],
                    "source_privacy_scan": "actual ZIP scan runs before commit",
                    "completion_evidence": policy.get("completion_evidence"),
                    "metadata": str(metadata_path),
                    "credentials_read": False,
                    "network_used": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    RELEASE.mkdir(parents=True, exist_ok=True)
    output_paths = [
        RELEASE / names["pdf"],
        RELEASE / names["reader"],
        RELEASE / names["source"],
        RELEASE / names["manifest"],
        RELEASE / names["checksums"],
    ]
    existing = [str(path) for path in output_paths if path.exists()]
    if existing and not args.replace_local:
        raise RuntimeError(
            "checkpoint outputs already exist; use --replace-local only after review: "
            + ", ".join(existing)
        )

    artifacts = [
        copy_binary_atomic(
            pdf_source,
            RELEASE / names["pdf"],
            policy.get("pdf_receipt"),
        ),
        write_zip(RELEASE / names["reader"], reader_entries),
        write_zip(
            RELEASE / names["source"],
            source_entries,
            privacy_tokens=privacy_tokens,
        ),
    ]
    source_privacy["actual_zip_inventory_and_content_scan"] = "pass"
    release_manifest = {
        "schema": "o009.zenodo-checkpoint-release.v1",
        "checkpoint": args.checkpoint,
        "publication_date": policy["publication_date"],
        "completion_state": manifest_completion_state(args.checkpoint),
        "reader_payload_manifest_sha256": sha256_file(
            ROOT / "build" / "site" / "PACKAGE_MANIFEST.csv"
        ),
        "backend_manifest_sha256": sha256_file(
            ROOT / "backend" / "BACKEND_MANIFEST.json"
        ),
        "artifacts": artifacts,
        "intentional_omissions": [
            "Git metadata and credentials",
            "the 76 MB complete Žitković commit archive; the exact selected source files, root CC0 license, commit identity, and archive hash are included",
            "the 180 MB local QuantEcon wheel payload; its exact lock, wheel manifest, and environment receipt are included",
            "local R and Python runtime installations",
            "unselected workspace material and other curriculum lanes",
            "absolute local profile paths and private identity tokens; public text copies use portable placeholders and are hash-mapped in PUBLIC_SANITIZATION_MANIFEST.json",
        ],
        "rights": "Mixed component licenses; see LICENSES.md and backend rights/provenance records. No blanket license claim.",
        "source_archive_privacy": source_privacy,
        "zenodo_lineage": {
            "previous_record_id": policy["previous_record_id"],
            "conceptrecid": policy["conceptrecid"],
            "skipped_unpublished_checkpoints": policy[
                "skipped_unpublished_checkpoints"
            ],
        },
    }
    if args.checkpoint == 38:
        completion_evidence = policy.get("completion_evidence")
        if not isinstance(completion_evidence, dict):
            raise RuntimeError("checkpoint-38 completion evidence was not derived")
        mastery = completion_evidence.get("mastery") or {}
        assessments = completion_evidence.get("assessments") or {}
        derived_course_coverage = {
            "mastery_problems_required": mastery.get("problem_count"),
            "mastery_problems_solved": mastery.get("solved_problem_count"),
            "assessment_forms": assessments.get("form_count"),
            "assessment_forms_equivalent": assessments.get("equivalent"),
        }
        if derived_course_coverage != CHECKPOINT_38_COURSE_COVERAGE:
            raise RuntimeError(
                "checkpoint-38 derived course coverage does not satisfy the release contract"
            )
        release_manifest["scope"] = dict(CHECKPOINT_38_SCOPE)
        release_manifest["course_coverage"] = derived_course_coverage
        release_manifest["completion_evidence"] = completion_evidence
        release_manifest["intentional_omissions"].extend(
            [
                "task-local cleanup receipts, authentication/blocker incident artifacts, publication transaction receipts, and internal workflow prose",
                "credential-bearing publisher scripts and their local token-note defaults; they are not needed to reproduce the reader or backend",
                "obsolete checkpoint-37 render helper and task-local scratch files such as source/labs/test.tmp",
            ]
        )
    manifest_path = RELEASE / names["manifest"]
    write_text_atomic(
        manifest_path,
        json.dumps(release_manifest, ensure_ascii=False, indent=2) + "\n",
        "utf-8",
    )

    checksum_rows = [
        f"{artifact['sha256']}  {artifact['filename']}" for artifact in artifacts
    ]
    checksum_rows.append(f"{sha256_file(manifest_path)}  {manifest_path.name}")
    checksum_rows.append(f"{sha256_file(metadata_path)}  {metadata_path.name}")
    checksums_path = RELEASE / names["checksums"]
    write_text_atomic(
        checksums_path,
        "\n".join(checksum_rows) + "\n",
        "ascii",
    )

    result = {
        "checkpoint": args.checkpoint,
        "release_directory": str(RELEASE),
        "artifacts": artifacts,
        "manifest": {
            "filename": manifest_path.name,
            "bytes": manifest_path.stat().st_size,
            "sha256": sha256_file(manifest_path),
        },
        "metadata": {
            "filename": metadata_path.name,
            "bytes": metadata_path.stat().st_size,
            "sha256": sha256_file(metadata_path),
        },
        "checksums": {
            "filename": checksums_path.name,
            "bytes": checksums_path.stat().st_size,
            "sha256": sha256_file(checksums_path),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
