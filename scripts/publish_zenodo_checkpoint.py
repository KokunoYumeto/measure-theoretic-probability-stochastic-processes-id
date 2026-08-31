#!/usr/bin/env python3
"""Publish and anonymously verify one explicit next O009 Zenodo checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse

import requests

try:
    from package_zenodo_checkpoint import validate_checkpoint_38_completion_evidence
except ModuleNotFoundError:  # pragma: no cover - package-style import fallback
    from .package_zenodo_checkpoint import validate_checkpoint_38_completion_evidence


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release"
TOKEN_NOTE_ENV = "O009_ZENODO_TOKEN_NOTE"
API = "https://zenodo.org/api"
ARTIFACT_PREFIX = "PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID"
EXPECTED_CONCEPTRECID = "22059941"
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra."
CONTROL_TIMEOUT = 120
PUBLISH_TIMEOUT = 180
DOWNLOAD_TIMEOUT = 300
LATEST_RECEIPT_PATH = ROOT / "00_control" / "ZENODO_PUBLICATION_RECEIPT.json"
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
PROFILE_RESIDUE_BYTES_RE = re.compile(
    rb"(?i)(?:[A-Z]:[\\/]+Users[\\/]+[^\\/\x00\r\n\"']{1,128}[\\/]+|(?:\\*/)(?:home|Users)(?:\\*/)[^\\/\x00\r\n\"']{1,128}(?:\\*/))"
)
CURL = Path(os.environ.get("WINDIR", r"C:\Windows")) / "System32" / "curl.exe"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate or publish one explicit next Zenodo checkpoint on the "
            "existing concept lineage."
        )
    )
    parser.add_argument("--checkpoint", type=int, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--validate-only",
        action="store_true",
        help="run local validation only; do not read credentials or use the network",
    )
    action.add_argument(
        "--publish",
        action="store_true",
        help="create/reuse the next-version draft, publish, and verify public bytes",
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
        "metadata": f"ZENODO_METADATA_CHECKPOINT_{checkpoint}.json",
        "checksums": f"SHA256SUMS_CHECKPOINT_{checkpoint}.txt",
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


def compare_public_metadata(public: dict, local: dict) -> dict[str, object]:
    supported = {
        "upload_type",
        "publication_type",
        "publication_date",
        "title",
        "creators",
        "description",
        "access_right",
        "license",
        "language",
        "version",
        "keywords",
        "notes",
    }
    unsupported = sorted(set(local) - supported)
    if unsupported:
        raise RuntimeError(
            "local Zenodo metadata has fields without anonymous-readback "
            f"comparators: {unsupported}"
        )
    missing = sorted(supported - set(local))
    if missing:
        raise RuntimeError(
            f"local Zenodo metadata omits required public fields: {missing}"
        )

    direct_fields = (
        "publication_date",
        "title",
        "description",
        "access_right",
        "language",
        "version",
        "keywords",
        "notes",
    )
    for field in direct_fields:
        if public.get(field) != local.get(field):
            raise RuntimeError(f"public {field} differs from local Zenodo metadata")
    if local.get("access_right") != "open" or public.get("access_right") != "open":
        raise RuntimeError("public/local Zenodo access_right must both remain exactly open")

    local_creators = local.get("creators")
    public_creators = public.get("creators")
    if not isinstance(local_creators, list) or not isinstance(public_creators, list):
        raise RuntimeError("public/local Zenodo creators are malformed")
    if len(public_creators) != len(local_creators):
        raise RuntimeError("public Zenodo creator count differs from local metadata")
    for index, (local_creator, public_creator) in enumerate(
        zip(local_creators, public_creators, strict=True), start=1
    ):
        if not isinstance(local_creator, dict) or not isinstance(public_creator, dict):
            raise RuntimeError(f"public/local Zenodo creator {index} is malformed")
        normalized_public_creator = dict(public_creator)
        # Zenodo's legacy deposition API materializes a blank affiliation for
        # name-only creators.  Accept only that one empty server-side field;
        # a nonempty affiliation or any other unexpected creator subfield is
        # still a public-metadata mismatch.
        if normalized_public_creator.get("affiliation") in (None, ""):
            normalized_public_creator.pop("affiliation", None)
        if normalized_public_creator != local_creator:
            raise RuntimeError(
                f"public Zenodo creator {index} fields differ from local metadata"
            )

    resource_type = public.get("resource_type") or {}
    if not isinstance(resource_type, dict):
        raise RuntimeError("public Zenodo resource_type is malformed")
    public_upload_type = public.get("upload_type") or resource_type.get("type")
    public_publication_type = public.get("publication_type") or resource_type.get(
        "subtype"
    )
    if public_upload_type != local.get("upload_type"):
        raise RuntimeError("public Zenodo upload/resource type differs")
    if public_publication_type != local.get("publication_type"):
        raise RuntimeError("public Zenodo publication/resource subtype differs")
    if normalized_license(public.get("license")) != normalized_license(
        local.get("license")
    ):
        raise RuntimeError("public Zenodo license differs from local metadata")

    description = str(public.get("description") or "")
    plain = re.sub(r"<[^>]+>", " ", description)
    folded = plain.casefold()
    checkpoint = checkpoint_from_version(str(local.get("version") or ""))
    validate_completion_disclosure(checkpoint, folded, "public Zenodo description")
    if "campuran" not in folded and "mixed" not in folded:
        raise RuntimeError("public Zenodo description lost the mixed-rights disclosure")
    if "licenses.md" not in folded:
        raise RuntimeError("public Zenodo description lost the LICENSES.md direction")
    for component in ("Random Services", "Žitković", "QuantEcon"):
        if component.casefold() not in folded:
            raise RuntimeError(
                f"public Zenodo description lost the {component} rights disclosure"
            )
    if MODEL_PROVENANCE not in description:
        raise RuntimeError("public Zenodo description lost model provenance")
    return {
        "exact": True,
        "fields_compared": sorted(supported),
        "mixed_license_disclosure": True,
        "model_provenance_disclosure": True,
    }


def normalized_md5(value: object) -> str:
    """Normalize Zenodo's public-record and deposition checksum spellings."""
    text = str(value or "").strip().lower()
    return text.removeprefix("md5:")


def digest(path: Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


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
    if receipt.get("sha256") != digest(pdf_path, "sha256"):
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
        if renderer_receipt.get("sha256") != digest(renderer_path, "sha256"):
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


def credential_note_path() -> Path:
    configured = os.environ.get(TOKEN_NOTE_ENV)
    if not configured:
        raise RuntimeError(
            f"configure {TOKEN_NOTE_ENV} with the absolute credential-note path"
        )
    candidate = Path(configured).expanduser()
    if not candidate.is_absolute():
        raise RuntimeError(f"{TOKEN_NOTE_ENV} must name an absolute path")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return resolved
    raise RuntimeError(
        f"{TOKEN_NOTE_ENV} must resolve outside the packaged O009 lane"
    )


def token_candidates() -> list[str]:
    note = credential_note_path()
    if not note.is_file():
        raise RuntimeError(
            f"Zenodo credential note is unavailable; configure {TOKEN_NOTE_ENV}"
        )
    raw = note.read_text(encoding="utf-8")
    values = re.findall(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{32,}(?![A-Za-z0-9_-])", raw)
    return list(dict.fromkeys(values))


def authenticated_session() -> requests.Session:
    for candidate in token_candidates():
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {candidate}"})
        response = session.get(
            f"{API}/deposit/depositions",
            params={"size": 1, "sort": "mostrecent"},
            timeout=CONTROL_TIMEOUT,
        )
        if response.status_code == 200:
            return session
        if response.status_code not in {401, 403}:
            response.raise_for_status()
    raise RuntimeError("No credential candidate authenticated; no token value was displayed.")


def fail_response(response: requests.Response, action: str) -> None:
    if response.ok:
        return
    body = response.text[:2000]
    raise RuntimeError(f"{action} failed: HTTP {response.status_code}: {body}")


def exact_depositions(session: requests.Session, title: str) -> list[dict]:
    response = session.get(
        f"{API}/deposit/depositions",
        params={
            "q": f'metadata.title:"{title}"',
            "all_versions": "true",
            "size": 100,
            "sort": "mostrecent",
        },
        timeout=CONTROL_TIMEOUT,
    )
    fail_response(response, "exact-title inventory")
    return [
        row
        for row in response.json()
        if (row.get("metadata") or {}).get("title") == title
    ]


def desired_files(names: dict[str, str]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for name in names.values():
        path = RELEASE / name
        if not path.is_file():
            raise RuntimeError(f"release file missing: {path}")
        result[name] = {
            "path": path,
            "bytes": path.stat().st_size,
            "sha256": digest(path, "sha256"),
            "md5": digest(path, "md5"),
        }
    return result


def validate_source_archive_privacy(names: dict[str, str], manifest: dict) -> dict:
    policy = manifest.get("source_archive_privacy") or {}
    if not isinstance(policy, dict):
        raise RuntimeError("release manifest source-archive privacy evidence is malformed")
    manifest_name = policy.get("manifest_path")
    manifest_sha256 = policy.get("manifest_sha256")
    sanitized_count = policy.get("sanitized_entry_count")
    if (
        not isinstance(manifest_name, str)
        or not manifest_name.endswith("/PUBLIC_SANITIZATION_MANIFEST.json")
        or not re.fullmatch(r"[0-9a-f]{64}", str(manifest_sha256 or ""))
        or not isinstance(sanitized_count, int)
        or sanitized_count < 0
        or policy.get("actual_zip_inventory_and_content_scan") != "pass"
    ):
        raise RuntimeError("release manifest lacks passing source-archive privacy evidence")

    archive_path = RELEASE / names["source"]
    if not archive_path.is_file():
        raise RuntimeError(f"source/backend archive is missing: {archive_path}")
    identity_values = {
        Path.home().name,
        os.environ.get("USERNAME", ""),
        os.environ.get("USER", ""),
    }
    generic = {"home", "root", "user", "users", "owner", "admin"}
    identity_tokens = {
        value
        for value in identity_values
        if re.fullmatch(r"[A-Za-z0-9._-]{4,64}", value or "")
        and value.casefold() not in generic
    }
    with zipfile.ZipFile(archive_path, "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError("source/backend archive failed CRC verification")
        names_in_archive = archive.namelist()
        if (
            names_in_archive != sorted(names_in_archive)
            or len(names_in_archive) != len(set(names_in_archive))
        ):
            raise RuntimeError(
                "source/backend archive member order or uniqueness check failed"
            )
        if manifest_name not in names_in_archive:
            raise RuntimeError("source/backend archive omits its sanitization manifest")
        sanitization_data = archive.read(manifest_name)
        if hashlib.sha256(sanitization_data).hexdigest() != manifest_sha256:
            raise RuntimeError("source sanitization manifest SHA-256 mismatch")
        sanitization = json.loads(sanitization_data.decode("utf-8"))
        sanitized_rows = sanitization.get("sanitized_entries")
        if (
            sanitization.get("schema") != "o009.public-source-sanitization.v1"
            or sanitization.get("sanitized_entry_count") != sanitized_count
            or not isinstance(sanitized_rows, list)
            or len(sanitized_rows) != sanitized_count
        ):
            raise RuntimeError("source sanitization manifest content mismatch")
        info_by_name = {info.filename: info for info in archive.infolist()}
        sanitized_paths: list[str] = []
        required_row_fields = {
            "path",
            "original_bytes",
            "original_sha256",
            "public_bytes",
            "public_sha256",
            "replacement_counts",
        }
        for index, row in enumerate(sanitized_rows, start=1):
            if not isinstance(row, dict) or set(row) != required_row_fields:
                raise RuntimeError(
                    f"source sanitization manifest row {index} is malformed"
                )
            path = row.get("path")
            replacements = row.get("replacement_counts")
            if (
                not isinstance(path, str)
                or path == manifest_name
                or path not in info_by_name
                or not isinstance(row.get("original_bytes"), int)
                or row["original_bytes"] < 0
                or not isinstance(row.get("public_bytes"), int)
                or row["public_bytes"] < 0
                or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("original_sha256") or ""))
                or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("public_sha256") or ""))
                or row["original_sha256"] == row["public_sha256"]
                or not isinstance(replacements, dict)
                or not replacements
                or any(
                    not isinstance(key, str)
                    or not isinstance(value, int)
                    or value <= 0
                    for key, value in replacements.items()
                )
            ):
                raise RuntimeError(
                    f"source sanitization manifest row {index} is invalid"
                )
            public_data = archive.read(path)
            if (
                len(public_data) != row["public_bytes"]
                or hashlib.sha256(public_data).hexdigest() != row["public_sha256"]
            ):
                raise RuntimeError(
                    f"source sanitization manifest row does not bind ZIP member: {path}"
                )
            sanitized_paths.append(path)
        if sanitized_paths != sorted(sanitized_paths) or len(sanitized_paths) != len(
            set(sanitized_paths)
        ):
            raise RuntimeError(
                "source sanitization manifest paths are not sorted and unique"
            )
        for info in archive.infolist():
            name = info.filename
            parts = name.split("/")
            if (
                name.startswith("/")
                or "\\" in name
                or re.match(r"(?i)^[A-Z]:", name)
                or any(part in {"", ".", ".."} for part in parts)
            ):
                raise RuntimeError(f"unsafe source/backend ZIP member name: {name!r}")
            data = archive.read(info)
            if PROFILE_RESIDUE_BYTES_RE.search(data):
                raise RuntimeError(
                    f"absolute profile-path residue remains in source/backend ZIP: {name}"
                )
            lowered = data.lower()
            for identity in identity_tokens:
                name_boundary = re.compile(
                    rf"(?<![A-Za-z0-9]){re.escape(identity)}(?![A-Za-z0-9])",
                    re.IGNORECASE,
                )
                if name_boundary.search(name):
                    raise RuntimeError(
                        "private identity residue remains in source/backend ZIP "
                        f"member name: {name}"
                    )
                encoded = identity.encode("utf-8")
                boundary = re.compile(
                    rb"(?<![A-Za-z0-9])"
                    + re.escape(encoded)
                    + rb"(?![A-Za-z0-9])",
                    re.IGNORECASE,
                )
                if (
                    boundary.search(data)
                    or identity.casefold().encode("utf-16le") in lowered
                ):
                    raise RuntimeError(
                        f"private identity residue remains in source/backend ZIP: {name}"
                    )
    return {
        "manifest_path": manifest_name,
        "manifest_sha256": manifest_sha256,
        "sanitized_entry_count": sanitized_count,
        "actual_zip_inventory_and_content_scan": "pass",
    }


def validate_checkpoint_38_archive_evidence(
    names: dict[str, str], completion_evidence: dict
) -> dict:
    prefix = "probabilitas-teoretis-ukuran-proses-stokastik-id/"
    evidence_rows = {
        "build_receipt": completion_evidence.get("build_receipt"),
        "reader_manifest": completion_evidence.get("reader_manifest"),
        "backend_manifest": completion_evidence.get("backend_manifest"),
    }
    for label, row in evidence_rows.items():
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("path"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256") or ""))
        ):
            raise RuntimeError(f"checkpoint-38 {label} evidence is malformed")

    source_archive_path = RELEASE / names["source"]
    with zipfile.ZipFile(source_archive_path, "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError("checkpoint-38 source archive failed CRC verification")
        names_in_archive = set(archive.namelist())
        for label, row in evidence_rows.items():
            member = prefix + row["path"]
            if member not in names_in_archive:
                raise RuntimeError(
                    f"checkpoint-38 source archive omits {label}: {member}"
                )
            if hashlib.sha256(archive.read(member)).hexdigest() != row["sha256"]:
                raise RuntimeError(
                    f"checkpoint-38 source archive {label} hash differs"
                )

    reader_archive_path = RELEASE / names["reader"]
    reader_members = {
        "build_receipt": "reader/BUILD_RECEIPT.json",
        "reader_manifest": "reader/PACKAGE_MANIFEST.csv",
    }
    with zipfile.ZipFile(reader_archive_path, "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError("checkpoint-38 reader archive failed CRC verification")
        names_in_archive = set(archive.namelist())
        for label, member in reader_members.items():
            if member not in names_in_archive:
                raise RuntimeError(
                    f"checkpoint-38 reader archive omits {label}: {member}"
                )
            if (
                hashlib.sha256(archive.read(member)).hexdigest()
                != evidence_rows[label]["sha256"]
            ):
                raise RuntimeError(
                    f"checkpoint-38 reader archive {label} hash differs"
                )

    return {
        "source_archive_evidence": "exact",
        "reader_archive_evidence": "exact",
        "evidence_sha256": hashlib.sha256(
            json.dumps(
                completion_evidence,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
    }


def validate_local_release(checkpoint: int) -> dict:
    names = artifact_names(checkpoint)
    metadata_path = RELEASE / names["metadata"]
    if not metadata_path.is_file():
        raise RuntimeError(f"release metadata missing: {metadata_path}")
    if not LATEST_RECEIPT_PATH.is_file():
        raise RuntimeError(f"latest public-lineage receipt missing: {LATEST_RECEIPT_PATH}")

    metadata_body = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata = metadata_body.get("metadata")
    if not isinstance(metadata, dict):
        raise RuntimeError("Zenodo metadata must contain a metadata object")
    previous_receipt = json.loads(LATEST_RECEIPT_PATH.read_text(encoding="utf-8"))

    target_version = metadata.get("version")
    if not isinstance(target_version, str) or checkpoint_from_version(target_version) != checkpoint:
        raise RuntimeError("metadata version does not match --checkpoint")
    previous_version = previous_receipt.get("version")
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
    if metadata.get("title") != previous_receipt.get("title"):
        raise RuntimeError("metadata title differs from the existing Zenodo lineage")
    if normalized_license(metadata.get("license")) != "other-open":
        raise RuntimeError("mixed-rights edition must use Zenodo license other-open")
    if metadata.get("access_right") != "open":
        raise RuntimeError(
            "Zenodo metadata access_right must be exactly 'open' before publication"
        )

    serialized = json.dumps(metadata_body, ensure_ascii=False)
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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
        pdf_receipt = checkpoint_pdf_receipt(
            checkpoint, RELEASE / artifact_names(checkpoint)["pdf"]
        )
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

    previous_record_id = previous_receipt.get("record_id")
    conceptrecid = str(previous_receipt.get("conceptrecid") or "")
    if not isinstance(previous_record_id, int) or not conceptrecid.isdigit():
        raise RuntimeError("latest receipt lacks a usable record/concept identity")
    if conceptrecid != EXPECTED_CONCEPTRECID:
        raise RuntimeError("latest receipt is not the mandated O009 Zenodo concept")

    expected = desired_files(names)
    manifest = json.loads((RELEASE / names["manifest"]).read_text(encoding="utf-8"))
    if manifest.get("checkpoint") != checkpoint:
        raise RuntimeError("release manifest checkpoint mismatch")
    expected_completion_state = manifest_completion_state(checkpoint)
    if manifest.get("completion_state") != expected_completion_state:
        raise RuntimeError(
            "release manifest completion state mismatch: "
            f"expected {expected_completion_state!r}"
        )
    if checkpoint == 38:
        if manifest.get("scope") != CHECKPOINT_38_SCOPE:
            raise RuntimeError("release manifest checkpoint-38 scope mismatch")
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
        if manifest.get("course_coverage") != derived_course_coverage:
            raise RuntimeError("release manifest checkpoint-38 course coverage mismatch")
        if manifest.get("completion_evidence") != completion_evidence:
            raise RuntimeError("release manifest checkpoint-38 evidence binding mismatch")
    lineage = manifest.get("zenodo_lineage") or {}
    if int(lineage.get("previous_record_id", -1)) != previous_record_id:
        raise RuntimeError("release manifest previous-record identity mismatch")
    if str(lineage.get("conceptrecid") or "") != conceptrecid:
        raise RuntimeError("release manifest concept identity mismatch")
    if lineage.get("skipped_unpublished_checkpoints", []) != skipped_checkpoints:
        raise RuntimeError("release manifest skipped-checkpoint evidence mismatch")
    rights = str(manifest.get("rights") or "")
    if "Mixed component licenses" not in rights or "No blanket license claim" not in rights:
        raise RuntimeError("release manifest mixed-rights statement is incomplete")
    source_archive_privacy = validate_source_archive_privacy(names, manifest)
    completion_archive_evidence: dict | None = None
    if checkpoint == 38:
        completion_archive_evidence = validate_checkpoint_38_archive_evidence(
            names, completion_evidence
        )

    artifact_rows = {
        row.get("filename"): row
        for row in manifest.get("artifacts", [])
        if isinstance(row, dict)
    }
    for key in ("pdf", "reader", "source"):
        name = names[key]
        row = artifact_rows.get(name)
        if row is None:
            raise RuntimeError(f"release manifest omits {name}")
        if int(row.get("bytes", -1)) != expected[name]["bytes"]:
            raise RuntimeError(f"release manifest byte mismatch: {name}")
        if row.get("sha256") != expected[name]["sha256"]:
            raise RuntimeError(f"release manifest SHA-256 mismatch: {name}")

    checksum_rows: dict[str, str] = {}
    for line in (RELEASE / names["checksums"]).read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match or match.group(2) in checksum_rows:
            raise RuntimeError("malformed or duplicate SHA256SUMS row")
        checksum_rows[match.group(2)] = match.group(1)
    checksummed_names = {
        names["pdf"],
        names["reader"],
        names["source"],
        names["manifest"],
        names["metadata"],
    }
    if set(checksum_rows) != checksummed_names:
        raise RuntimeError("SHA256SUMS filename inventory mismatch")
    for name in checksummed_names:
        if checksum_rows[name] != expected[name]["sha256"]:
            raise RuntimeError(f"SHA256SUMS digest mismatch: {name}")

    prior_files: dict[str, dict] = {}
    for row in previous_receipt.get("files", []):
        if not isinstance(row, dict) or not isinstance(row.get("filename"), str):
            raise RuntimeError("latest receipt has a malformed file row")
        prior_files[row["filename"]] = row
    if not prior_files:
        raise RuntimeError("latest receipt has no prior public file inventory")

    return {
        "names": names,
        "metadata_path": metadata_path,
        "metadata_body": metadata_body,
        "previous_receipt": previous_receipt,
        "previous_checkpoint": previous_checkpoint,
        "previous_record_id": previous_record_id,
        "conceptrecid": conceptrecid,
        "skipped_unpublished_checkpoints": skipped_checkpoints,
        "prior_files": prior_files,
        "expected": expected,
        "source_archive_privacy": source_archive_privacy,
        "completion_evidence": completion_evidence,
        "completion_archive_evidence": completion_archive_evidence,
    }


def concept_id(row: dict) -> str:
    metadata = row.get("metadata") or {}
    return str(row.get("conceptrecid") or metadata.get("conceptrecid") or "")


def refresh_draft_metadata(
    session: requests.Session, draft: dict, metadata_body: dict, conceptrecid: str
) -> dict:
    if concept_id(draft) != conceptrecid:
        raise RuntimeError("draft belongs to a different Zenodo concept")
    response = session.put(
        f"{API}/deposit/depositions/{draft['id']}",
        json=metadata_body,
        timeout=CONTROL_TIMEOUT,
    )
    fail_response(response, "draft metadata refresh")
    refreshed = response.json()
    if concept_id(refreshed) != conceptrecid:
        raise RuntimeError("refreshed draft concept identity changed")
    return refreshed


def create_or_reuse_next_version(
    session: requests.Session,
    metadata_body: dict,
    previous_record_id: int,
    conceptrecid: str,
) -> tuple[str, dict]:
    metadata = metadata_body["metadata"]
    matches = exact_depositions(session, metadata["title"])
    exact_version = [
        row
        for row in matches
        if (row.get("metadata") or {}).get("version") == metadata["version"]
    ]
    foreign_exact = [row for row in exact_version if concept_id(row) != conceptrecid]
    if foreign_exact:
        raise RuntimeError(
            "exact title/version exists on another concept; refusing ambiguity: "
            + ", ".join(str(row.get("id")) for row in foreign_exact)
        )
    published = [row for row in exact_version if row.get("submitted")]
    lineage_published = [row for row in published if concept_id(row) == conceptrecid]
    if len(lineage_published) > 1:
        raise RuntimeError("multiple exact published lineage versions found")
    if lineage_published:
        return "already-published", lineage_published[0]

    lineage_drafts = [
        row
        for row in matches
        if not row.get("submitted") and concept_id(row) == conceptrecid
    ]
    if len(lineage_drafts) > 1:
        raise RuntimeError("multiple drafts exist on the target concept")
    if lineage_drafts:
        draft = lineage_drafts[0]
        draft_version = (draft.get("metadata") or {}).get("version")
        if draft_version not in {None, "", metadata["version"]}:
            raise RuntimeError("a different-version draft already occupies the target concept")
        # A timed-out ``newversion`` POST can create the sole same-concept draft
        # before Zenodo applies any version metadata. Reuse that exact draft;
        # never create a second concept or another draft. File synchronization
        # below still fails closed unless every inherited file is byte-identical
        # to the latest public receipt.
        return "draft", refresh_draft_metadata(
            session, draft, metadata_body, conceptrecid
        )

    response = session.post(
        f"{API}/deposit/depositions/{previous_record_id}/actions/newversion",
        timeout=CONTROL_TIMEOUT,
    )
    fail_response(response, "next-version draft creation")
    payload = response.json()
    latest_draft_url = (payload.get("links") or {}).get("latest_draft")
    if latest_draft_url:
        parsed = urlparse(latest_draft_url)
        if (
            parsed.scheme != "https"
            or parsed.netloc != "zenodo.org"
            or not parsed.path.startswith("/api/deposit/depositions/")
            or parsed.query
            or parsed.fragment
        ):
            raise RuntimeError("Zenodo returned an unsafe latest-draft URL")
        response = session.get(latest_draft_url, timeout=CONTROL_TIMEOUT)
        fail_response(response, "next-version draft readback")
        draft = response.json()
    elif payload.get("id") and not payload.get("submitted"):
        draft = payload
    else:
        raise RuntimeError("Zenodo did not return an identifiable next-version draft")
    return "new-draft", refresh_draft_metadata(
        session, draft, metadata_body, conceptrecid
    )


def synchronize_files(
    session: requests.Session,
    deposition_id: int,
    expected: dict[str, dict],
    prior_files: dict[str, dict],
) -> list[dict]:
    response = session.get(
        f"{API}/deposit/depositions/{deposition_id}", timeout=CONTROL_TIMEOUT
    )
    fail_response(response, "draft resource readback")
    bucket_url = ((response.json().get("links") or {}).get("bucket") or "").rstrip("/")
    if not re.fullmatch(r"https://zenodo\.org/api/files/[A-Za-z0-9-]+", bucket_url):
        raise RuntimeError("draft has no valid Zenodo bucket upload link")

    response = session.get(
        f"{API}/deposit/depositions/{deposition_id}/files", timeout=CONTROL_TIMEOUT
    )
    fail_response(response, "draft file inventory")
    remote = response.json()
    remote_by_name = {row["filename"]: row for row in remote}
    unexpected = sorted(set(remote_by_name) - set(expected))
    for name in unexpected:
        current = remote_by_name[name]
        prior = prior_files.get(name)
        inherited_exact = (
            prior is not None
            and int(current.get("filesize", -1)) == int(prior.get("bytes", -2))
            and normalized_md5(current.get("checksum"))
            == normalized_md5(prior.get("zenodo_checksum"))
        )
        if not inherited_exact:
            raise RuntimeError(
                f"unexpected draft file is not an exact inherited prior-version file: {name}"
            )
        response = session.delete(
            f"{API}/deposit/depositions/{deposition_id}/files/{current['id']}",
            timeout=CONTROL_TIMEOUT,
        )
        fail_response(response, f"remove verified inherited file {name}")

    for name, local in expected.items():
        current = remote_by_name.get(name)
        correct = (
            current is not None
            and int(current.get("filesize", -1)) == local["bytes"]
            and normalized_md5(current.get("checksum")) == local["md5"]
        )
        if correct:
            continue
        if current is not None:
            response = session.delete(
                f"{API}/deposit/depositions/{deposition_id}/files/{current['id']}",
                timeout=CONTROL_TIMEOUT,
            )
            fail_response(response, f"replacement deletion for {name}")
        with local["path"].open("rb") as handle:
            response = session.put(
                f"{bucket_url}/{quote(name, safe='')}",
                data=handle,
                headers={"Content-Type": "application/octet-stream"},
                timeout=(30, 1800),
            )
        fail_response(response, f"upload {name}")

    response = session.get(
        f"{API}/deposit/depositions/{deposition_id}/files", timeout=CONTROL_TIMEOUT
    )
    fail_response(response, "post-upload file inventory")
    final_rows = response.json()
    final_by_name = {row["filename"]: row for row in final_rows}
    if set(final_by_name) != set(expected):
        raise RuntimeError("post-upload filename inventory differs")
    for name, local in expected.items():
        row = final_by_name[name]
        if int(row["filesize"]) != local["bytes"]:
            raise RuntimeError(f"post-upload byte mismatch: {name}")
        if normalized_md5(row["checksum"]) != local["md5"]:
            raise RuntimeError(f"post-upload MD5 mismatch: {name}")

    # Zenodo's current bucket-backed legacy-deposition service rejects the
    # documented optional PUT /files sorting call with HTTP 405. File identity,
    # not API list order, is the release invariant; the reader PDF retains its
    # explicit ``00_`` filename for reader-first display in name-sorted clients.
    return [final_by_name[name] for name in expected]


def publish(session: requests.Session, deposition_id: int) -> dict:
    response = session.post(
        f"{API}/deposit/depositions/{deposition_id}/actions/publish",
        timeout=PUBLISH_TIMEOUT,
    )
    fail_response(response, "publication")
    return response.json()


def curl_public_to_temp(url: str, timeout: int) -> tuple[int, Path]:
    """Use Windows Schannel for anonymous HTTPS readback without weakening TLS."""
    if not CURL.is_file():
        raise RuntimeError(
            "Python TLS readback failed and the OS-verified curl fallback is unavailable"
        )
    descriptor, temporary_name = tempfile.mkstemp(prefix="o009-zenodo-readback-")
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        result = subprocess.run(
            [
                str(CURL),
                "--silent",
                "--show-error",
                "--location",
                "--proto",
                "=https",
                "--proto-redir",
                "=https",
                "--tlsv1.2",
                "--max-time",
                str(timeout),
                "--output",
                str(temporary),
                "--write-out",
                "%{http_code}",
                url,
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout + 30,
        )
        status_text = result.stdout.strip()
        if result.returncode != 0 or not re.fullmatch(r"\d{3}", status_text):
            raise RuntimeError(
                "OS-verified anonymous HTTPS fallback failed: "
                f"curl_exit={result.returncode}; http={status_text or 'none'}; "
                f"diagnostic={result.stderr.strip()[:400]}"
            )
        return int(status_text), temporary
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def anonymous_json(url: str, timeout: int) -> tuple[int, dict | None, str]:
    try:
        response = requests.get(url, timeout=timeout)
        body = response.json() if response.status_code == 200 else None
        return response.status_code, body, "python-requests"
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        status, temporary = curl_public_to_temp(url, timeout)
        try:
            body = (
                json.loads(temporary.read_text(encoding="utf-8"))
                if status == 200
                else None
            )
            return status, body, "curl-schannel"
        finally:
            temporary.unlink(missing_ok=True)


def wait_public_record(record_id: int) -> dict:
    last_status = None
    for _ in range(20):
        status, body, _transport = anonymous_json(
            f"{API}/records/{record_id}", CONTROL_TIMEOUT
        )
        last_status = status
        if status == 200 and isinstance(body, dict):
            return body
        if status not in {404, 409, 503}:
            raise RuntimeError(f"anonymous record readback failed with HTTP {status}")
        time.sleep(2)
    raise RuntimeError(f"public record did not become readable; last HTTP {last_status}")


def verify_public_files(record: dict, expected: dict[str, dict]) -> list[dict]:
    public_by_name = {row["key"]: row for row in record.get("files", [])}
    if set(public_by_name) != set(expected):
        raise RuntimeError(
            f"public filename inventory differs: {sorted(public_by_name)}"
        )
    verified: list[dict] = []
    for name, local in expected.items():
        row = public_by_name[name]
        url = row["links"]["self"]
        sha = hashlib.sha256()
        md5 = hashlib.md5()
        byte_count = 0
        transport = "python-requests"
        try:
            response = requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
            fail_response(response, f"anonymous download {name}")
            for chunk in response.iter_content(1024 * 1024):
                if not chunk:
                    continue
                sha.update(chunk)
                md5.update(chunk)
                byte_count += len(chunk)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            status, temporary = curl_public_to_temp(url, DOWNLOAD_TIMEOUT)
            transport = "curl-schannel"
            sha = hashlib.sha256()
            md5 = hashlib.md5()
            byte_count = 0
            try:
                if status != 200:
                    raise RuntimeError(
                        f"anonymous download {name} failed with HTTP {status}"
                    )
                with temporary.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        sha.update(chunk)
                        md5.update(chunk)
                        byte_count += len(chunk)
            finally:
                temporary.unlink(missing_ok=True)
        if byte_count != local["bytes"]:
            raise RuntimeError(f"anonymous byte mismatch: {name}")
        if sha.hexdigest() != local["sha256"]:
            raise RuntimeError(f"anonymous SHA-256 mismatch: {name}")
        if md5.hexdigest() != local["md5"]:
            raise RuntimeError(f"anonymous MD5 mismatch: {name}")
        verified.append(
            {
                "filename": name,
                "bytes": byte_count,
                "sha256": sha.hexdigest(),
                "zenodo_checksum": row.get("checksum"),
                "anonymous_download_url": url,
                "anonymous_transport": transport,
            }
        )
    return verified


def verify_parent_record(local: dict) -> None:
    status, record, _transport = anonymous_json(
        f"{API}/records/{local['previous_record_id']}", CONTROL_TIMEOUT
    )
    if status != 200 or not isinstance(record, dict):
        raise RuntimeError(
            f"anonymous parent-lineage readback failed with HTTP {status}"
        )
    metadata = record.get("metadata") or {}
    receipt = local["previous_receipt"]
    if metadata.get("title") != receipt.get("title"):
        raise RuntimeError("public parent title differs from the lineage receipt")
    if metadata.get("version") != receipt.get("version"):
        raise RuntimeError("public parent version differs from the lineage receipt")
    if metadata.get("access_right") != "open":
        raise RuntimeError("public parent record is not openly accessible")
    if str(record.get("conceptrecid") or "") != local["conceptrecid"]:
        raise RuntimeError("public parent concept differs from the lineage receipt")
    public_files = {row.get("key"): row for row in record.get("files", [])}
    if set(public_files) != set(local["prior_files"]):
        raise RuntimeError("public parent filename inventory differs from the receipt")
    for name, prior in local["prior_files"].items():
        row = public_files[name]
        if int(row.get("size", -1)) != int(prior.get("bytes", -2)):
            raise RuntimeError(f"public parent byte count differs: {name}")
        if normalized_md5(row.get("checksum")) != normalized_md5(
            prior.get("zenodo_checksum")
        ):
            raise RuntimeError(f"public parent checksum differs: {name}")


def write_json_atomic(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise RuntimeError(f"stale temporary receipt requires review: {temporary}")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def persist_receipts(receipt: dict, local: dict, checkpoint: int) -> tuple[Path, str]:
    control = ROOT / "00_control"
    previous_path = control / (
        f"ZENODO_PUBLICATION_RECEIPT_CHECKPOINT_{local['previous_checkpoint']}.json"
    )
    if previous_path.exists():
        existing_previous = json.loads(previous_path.read_text(encoding="utf-8"))
        if existing_previous != local["previous_receipt"]:
            raise RuntimeError("archived previous receipt conflicts with the latest receipt")
    else:
        write_json_atomic(previous_path, local["previous_receipt"])

    versioned_path = control / f"ZENODO_PUBLICATION_RECEIPT_CHECKPOINT_{checkpoint}.json"
    if versioned_path.exists():
        existing = json.loads(versioned_path.read_text(encoding="utf-8"))
        same_publication = (
            existing.get("record_id") == receipt.get("record_id")
            and existing.get("version") == receipt.get("version")
            and existing.get("files") == receipt.get("files")
        )
        if checkpoint == 38:
            same_publication = same_publication and (
                existing.get("completion_state") == COMPLETE_MANIFEST_STATE
                and existing.get("completion_evidence")
                == receipt.get("completion_evidence")
                and existing.get("completion_archive_evidence")
                == receipt.get("completion_archive_evidence")
            )
        if not same_publication:
            raise RuntimeError("target checkpoint receipt conflicts with public readback")
        receipt = existing
    else:
        write_json_atomic(versioned_path, receipt)

    write_json_atomic(LATEST_RECEIPT_PATH, receipt)
    return versioned_path, digest(versioned_path, "sha256")


def main() -> int:
    args = parse_args()
    local = validate_local_release(args.checkpoint)
    if args.validate_only:
        print(
            json.dumps(
                {
                    "status": "LOCAL_RELEASE_VALID",
                    "checkpoint": args.checkpoint,
                    "previous_checkpoint": local["previous_checkpoint"],
                    "previous_record_id": local["previous_record_id"],
                    "conceptrecid": local["conceptrecid"],
                    "skipped_unpublished_checkpoints": local[
                        "skipped_unpublished_checkpoints"
                    ],
                    "file_count": len(local["expected"]),
                    "total_bytes": sum(
                        row["bytes"] for row in local["expected"].values()
                    ),
                    "source_archive_privacy": local[
                        "source_archive_privacy"
                    ],
                    "completion_evidence": local["completion_evidence"],
                    "completion_archive_evidence": local[
                        "completion_archive_evidence"
                    ],
                    "credentials_read": False,
                    "network_used": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    metadata_body = local["metadata_body"]
    expected = local["expected"]
    verify_parent_record(local)
    session = authenticated_session()
    mode, target = create_or_reuse_next_version(
        session,
        metadata_body,
        local["previous_record_id"],
        local["conceptrecid"],
    )
    if mode == "already-published":
        published = target
        deposition_id = int(target.get("id") or target.get("record_id"))
        record_id = int(target.get("record_id") or target.get("id"))
    else:
        deposition_id = int(target["id"])
        synchronize_files(session, deposition_id, expected, local["prior_files"])
        published = publish(session, deposition_id)
        record_id = int(published.get("record_id") or published.get("id"))
    record = wait_public_record(record_id)
    verified_files = verify_public_files(record, expected)

    metadata = record["metadata"]
    public_metadata_verification = compare_public_metadata(
        metadata, metadata_body["metadata"]
    )
    public_license = metadata.get("license") or {}
    public_concept = str(published.get("conceptrecid") or record.get("conceptrecid") or "")
    if public_concept != local["conceptrecid"]:
        raise RuntimeError("public record escaped the existing concept lineage")

    receipt = {
        "schema": "o009.zenodo-publication-receipt.v1",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "authentication": "Bearer header; credential value neither logged nor persisted",
        "deposition_id": deposition_id,
        "record_id": record_id,
        "conceptrecid": public_concept,
        "doi": record.get("doi"),
        "doi_url": record.get("links", {}).get("doi"),
        "record_url": record.get("links", {}).get("self_html")
        or record.get("links", {}).get("html"),
        "title": metadata.get("title"),
        "version": metadata.get("version"),
        "publication_date": metadata.get("publication_date"),
        "completion_state": (
            COMPLETE_MANIFEST_STATE
            if args.checkpoint == 38
            else "explicitly incomplete working edition"
        ),
        "license_metadata": public_license,
        "mixed_license_disclosure": public_metadata_verification[
            "mixed_license_disclosure"
        ],
        "public_metadata_verification": public_metadata_verification,
        "metadata_source": {
            "path": f"release/{local['names']['metadata']}",
            "bytes": local["metadata_path"].stat().st_size,
            "sha256": digest(local["metadata_path"], "sha256"),
        },
        "source_archive_privacy": local["source_archive_privacy"],
        "completion_evidence": local["completion_evidence"],
        "completion_archive_evidence": local[
            "completion_archive_evidence"
        ],
        "files": verified_files,
        "anonymous_inventory_exact": True,
        "all_public_sha256_exact": True,
    }
    receipt_path, receipt_sha256 = persist_receipts(
        receipt, local, args.checkpoint
    )
    print(
        json.dumps(
            {
                "status": (
                    "EXISTING_PUBLIC_VERSION_ANONYMOUSLY_VERIFIED"
                    if mode == "already-published"
                    else "PUBLISHED_AND_ANONYMOUSLY_VERIFIED"
                ),
                "record_id": record_id,
                "conceptrecid": receipt["conceptrecid"],
                "doi": receipt["doi"],
                "record_url": receipt["record_url"],
                "file_count": len(verified_files),
                "total_bytes": sum(row["bytes"] for row in verified_files),
                "receipt_path": str(receipt_path),
                "receipt_sha256": receipt_sha256,
                "latest_receipt_path": str(LATEST_RECEIPT_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
