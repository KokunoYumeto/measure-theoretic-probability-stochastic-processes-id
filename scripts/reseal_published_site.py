#!/usr/bin/env python3
"""Reseal the public D30 payload after adding the presentation nav overlay."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

EXCLUDED = {"PACKAGE_MANIFEST.csv", "BUILD_RECEIPT.json"}


def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    site = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("build/site")
    paths = sorted((p for p in site.rglob("*") if p.is_file() and p.name not in EXCLUDED), key=lambda p: p.relative_to(site).as_posix().casefold())
    rows = [{"path": p.relative_to(site).as_posix(), "bytes": str(p.stat().st_size), "sha256": digest(p)} for p in paths]
    manifest = site / "PACKAGE_MANIFEST.csv"
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("path", "bytes", "sha256"), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    receipt_path = site / "BUILD_RECEIPT.json"; receipt = json.loads(receipt_path.read_text("utf-8"))
    receipt["file_count"] = len(rows); receipt["total_bytes"] = sum(int(r["bytes"]) for r in rows); receipt["manifest_sha256"] = digest(manifest)
    receipt["presentation_navigation_overlay"] = {
        "schema": "program-matematika-navigation-v1",
        "course_id": "D30",
        "html_files": len(list(site.rglob("*.html"))),
        "scope_note": "Per-unit target hashes retained elsewhere in this receipt identify the frozen pre-overlay mathematical payload; PACKAGE_MANIFEST.csv identifies the exact final hosted bytes.",
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(rows), "html_files": receipt["presentation_navigation_overlay"]["html_files"], "manifest_sha256": receipt["manifest_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
