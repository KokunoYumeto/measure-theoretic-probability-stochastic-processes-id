#!/usr/bin/env python3
"""Anonymously verify every published O009 Pages byte against the local site."""

from __future__ import annotations

import csv
import hashlib
import io
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_BASE = (
    "https://kokunoyumeto.github.io/"
    "measure-theoretic-probability-stochastic-processes-id/"
)
USER_AGENT = "O009-anonymous-pages-verifier/1.0"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_exact(base: str, relative: str, attempts: int = 12) -> bytes:
    url = urllib.parse.urljoin(base, urllib.parse.quote(relative, safe="/"))
    expected = urllib.parse.urlsplit(url)
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=30) as response:
                final = urllib.parse.urlsplit(response.geturl())
                if (
                    final.scheme != "https"
                    or final.hostname != expected.hostname
                    or final.port not in (None, 443)
                    or final.path != expected.path
                    or final.query
                    or final.fragment
                ):
                    raise RuntimeError(f"unexpected public redirect: {url} -> {response.geturl()}")
                if response.status != 200:
                    raise RuntimeError(f"unexpected HTTP {response.status}: {url}")
                return response.read()
        except (OSError, urllib.error.HTTPError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(5)
    raise RuntimeError(f"public fetch failed after {attempts} attempts: {url}: {last_error}")


def verify(site: Path, base: str) -> None:
    site = site.resolve()
    normalized = base.rstrip("/") + "/"
    parsed_base = urllib.parse.urlsplit(normalized)
    if parsed_base.scheme != "https" or not parsed_base.hostname or parsed_base.port not in (None, 443):
        raise RuntimeError("public base must be an ordinary HTTPS origin")
    local_manifest = (site / "PACKAGE_MANIFEST.csv").read_bytes()
    remote_manifest = fetch_exact(normalized, "PACKAGE_MANIFEST.csv")
    if remote_manifest != local_manifest:
        raise RuntimeError("public PACKAGE_MANIFEST.csv differs from local bytes")
    rows = list(csv.DictReader(io.StringIO(local_manifest.decode("utf-8"), newline="")))
    for row in rows:
        relative = row["path"]
        local = (site / relative).read_bytes()
        remote = fetch_exact(normalized, relative)
        expected_size = int(row["bytes"])
        expected_hash = row["sha256"]
        if len(local) != expected_size or sha256(local) != expected_hash:
            raise RuntimeError(f"local manifest mismatch during public check: {relative}")
        if remote != local:
            raise RuntimeError(f"public byte mismatch: {relative}")
    for control in ("BUILD_RECEIPT.json",):
        local = (site / control).read_bytes()
        remote = fetch_exact(normalized, control)
        if remote != local:
            raise RuntimeError(f"public control byte mismatch: {control}")
    print(
        f"ANONYMOUS PASS files={len(rows)} "
        f"bytes={sum(int(row['bytes']) for row in rows)} "
        f"manifest_sha256={sha256(local_manifest)} base={normalized}"
    )


def main() -> int:
    site = Path(sys.argv[1]) if len(sys.argv) >= 2 else Path("build/site")
    base = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_BASE
    verify(site, base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
