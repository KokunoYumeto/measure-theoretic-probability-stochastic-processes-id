#!/usr/bin/env python3
"""Verify the exact committed O009 Pages payload with the standard library."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path


CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.I)
EXCLUDED = {"PACKAGE_MANIFEST.csv", "BUILD_RECEIPT.json"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang: str | None = None
        self.ids: list[str] = []
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        if values.get("id"):
            self.ids.append(str(values["id"]))
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.refs.append(str(values[attribute]))


def documents(site: Path) -> dict[Path, Document]:
    parsed: dict[Path, Document] = {}
    for path in sorted(site.rglob("*.html"), key=lambda item: item.as_posix().casefold()):
        parser = Document()
        parser.feed(path.read_text("utf-8"))
        parser.close()
        if parser.lang != "id-ID":
            raise RuntimeError(f"missing lang=id-ID: {path}")
        if len(parser.ids) != len(set(parser.ids)):
            raise RuntimeError(f"duplicate HTML id: {path}")
        parsed[path.resolve()] = parser
    return parsed


def verify(site: Path) -> None:
    site = site.resolve()
    manifest = site / "PACKAGE_MANIFEST.csv"
    receipt_path = site / "BUILD_RECEIPT.json"
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        expected = list(csv.DictReader(stream))
    actual_paths = sorted(
        (
            path
            for path in site.rglob("*")
            if path.is_file() and path.name not in EXCLUDED
        ),
        key=lambda path: path.relative_to(site).as_posix().casefold(),
    )
    actual = [
        {
            "path": path.relative_to(site).as_posix(),
            "bytes": str(path.stat().st_size),
            "sha256": digest(path),
        }
        for path in actual_paths
    ]
    if expected != actual:
        raise RuntimeError("PACKAGE_MANIFEST.csv differs from committed payload")
    receipt = json.loads(receipt_path.read_text("utf-8"))
    if receipt.get("manifest_sha256") != digest(manifest):
        raise RuntimeError("BUILD_RECEIPT.json does not bind the manifest")
    parsed = documents(site)
    for path, document in parsed.items():
        for ref in document.refs:
            parts = urllib.parse.urlparse(ref)
            if not ref or parts.scheme or ref.startswith("//"):
                continue
            fragment = urllib.parse.unquote(parts.fragment)
            target = (path.parent / urllib.parse.unquote(parts.path)).resolve() if parts.path else path
            try:
                target.relative_to(site)
            except ValueError as exc:
                raise RuntimeError(f"reference escapes site: {path} -> {ref}") from exc
            if not target.is_file():
                raise RuntimeError(f"missing local reference: {path} -> {ref}")
            if fragment:
                target_document = parsed.get(target)
                if target_document is None or fragment not in target_document.ids:
                    raise RuntimeError(f"missing fragment target: {path} -> {ref}")
    for css in sorted(site.rglob("*.css"), key=lambda item: item.as_posix().casefold()):
        for _, ref in CSS_URL_RE.findall(css.read_text("utf-8")):
            parts = urllib.parse.urlparse(ref.strip())
            if not parts.path or parts.scheme or ref.startswith("data:"):
                continue
            target = (css.parent / urllib.parse.unquote(parts.path)).resolve()
            try:
                target.relative_to(site)
            except ValueError as exc:
                raise RuntimeError(f"CSS reference escapes site: {css} -> {ref}") from exc
            if not target.is_file():
                raise RuntimeError(f"missing CSS asset: {css} -> {ref}")
    if (site / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js").stat().st_size != 4709:
        raise RuntimeError("MathJax boldsymbol dependency is not the pinned file")
    labs = (
        ("labs/01-konvergensi-monte-carlo.html", "o009_lab_convergence_mc"),
        ("labs/02-simulasi-rantai-markov.html", "o009_lab_markov_gambler_ruin"),
    )
    for rel, chunk_id in labs:
        lab = (site / rel).read_text("utf-8")
        if f'id="{chunk_id}"' not in lab or "set.seed" not in lab or "```{r" in lab:
            raise RuntimeError(f"executable lab block is not correctly rendered: {rel}")
    joined = b"\n".join(path.read_bytes() for path in actual_paths)
    for forbidden in (b"C:\\Users\\", b"C:/Users/", b"/home/Floris", b"googletagmanager"):
        if forbidden in joined:
            raise RuntimeError(f"private or excluded runtime residue: {forbidden!r}")
    print(
        f"PASS files={len(actual)} bytes={sum(int(row['bytes']) for row in actual)} "
        f"manifest_sha256={digest(manifest)}"
    )


def main() -> int:
    site = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("build/site")
    verify(site)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
