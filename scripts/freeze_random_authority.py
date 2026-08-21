#!/usr/bin/env python3
"""Freeze the exact bounded Random theory selection and direct asset closure.

This is deliberately not a crawler.  It fetches only the explicit O009 page
selection below, the three authority pages, and files directly required by
those HTML documents or their local CSS.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup


BASE = "https://www.randomservices.org/random/"

AUTHORITY_PAGES = (
    "index.html",
    "Introduction.html",
    "Credits.html",
)

# Dependency-closed teaching selection for D30 after D10, B90, and C140.
# Random chapter 5 (sample/*, including LLN and CLT) belongs to the O006/C140
# lane and is therefore an explicit shared prerequisite, not duplicated here.
THEORY_PAGES = (
    "prob/Convergence.html",
    "prob/Probability2.html",
    "prob/Processes.html",
    "prob/Stop.html",
    "dist/Convergence.html",
    "expect/Conditional2.html",
    "expect/Uniform.html",
    "expect/Kernels.html",
    "martingales/index.html",
    "martingales/Introduction.html",
    "martingales/Properties.html",
    "martingales/Stop.html",
    "martingales/Inequalities.html",
    "martingales/Convergence.html",
    "martingales/Backwards.html",
    "markov/index.html",
    "markov/General.html",
    "markov/Potentials.html",
    "markov/Discrete.html",
    "markov/Recurrence.html",
    "markov/Periodicity.html",
    "markov/Limiting.html",
    "markov/Continuous.html",
    "markov/Transition.html",
    "markov/Potentials2.html",
    "markov/Limiting2.html",
    "poisson/index.html",
    "poisson/Introduction.html",
    "poisson/Exponential.html",
    "poisson/Gamma.html",
    "poisson/Poisson.html",
    "poisson/Splitting.html",
    "poisson/Nonhomogeneous.html",
    "poisson/Compound.html",
    "poisson/General.html",
    "renewal/index.html",
    "renewal/Introduction.html",
    "renewal/Equations.html",
    "renewal/LimitTheorems.html",
    "renewal/Delayed.html",
    "renewal/Alternating.html",
    "renewal/Reward.html",
    "brown/index.html",
    "brown/Standard.html",
    "brown/Drift.html",
    "brown/Bridge.html",
    "brown/Geometric.html",
)

USER_AGENT = "Codex-O009-authority-freeze/1.0"
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.I)
SHARED_MATHJAX_DEPENDENCIES = (
    (
        "https://www.randomservices.org/MathJax/tex-svg.js",
        "shared/MathJax/tex-svg.js",
        "dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a",
    ),
    (
        "https://www.randomservices.org/MathJax/input/tex/extensions/boldsymbol.js",
        "shared/MathJax/input/tex/extensions/boldsymbol.js",
        "716cf8735d00abfb1627f8adbbf4aeb915ac9b5c55d47aeaf276e73dac6a2aa1",
    ),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_rel(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    base = urllib.parse.urlparse(BASE)
    if parsed.scheme != "https" or parsed.netloc != base.netloc:
        raise ValueError(f"outside authority origin: {url}")
    base_path = base.path
    if not parsed.path.startswith(base_path):
        raise ValueError(f"outside authority root: {url}")
    rel = urllib.parse.unquote(parsed.path[len(base_path) :]).lstrip("/")
    parts = Path(rel).parts
    if not rel or any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"unsafe relative authority path: {rel!r}")
    return Path(*parts).as_posix()


def is_local_authority_url(url: str) -> bool:
    """Return true only for files inside Random's bounded publication root."""
    parsed = urllib.parse.urlparse(url)
    base = urllib.parse.urlparse(BASE)
    return (
        parsed.scheme == "https"
        and parsed.netloc == base.netloc
        and parsed.path.startswith(base.path)
    )


def fetch(url: str) -> tuple[bytes, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        response_context = urllib.request.urlopen(req, timeout=60)
    except Exception as exc:
        raise RuntimeError(f"authority fetch failed for {url}: {exc}") from exc
    with response_context as response:
        final = response.geturl()
        if urllib.parse.urlparse(final).netloc != urllib.parse.urlparse(BASE).netloc:
            raise RuntimeError(f"unexpected redirect outside authority: {url} -> {final}")
        data = response.read()
        headers = {key.lower(): value for key, value in response.headers.items()}
        headers["status"] = str(response.status)
        headers["final_url"] = final
        return data, headers


def direct_dependencies(url: str, data: bytes) -> tuple[set[str], set[str]]:
    soup = BeautifulSoup(data, "lxml")
    local: set[str] = set()
    external: set[str] = set()
    candidates: list[str] = []
    for tag in soup.select("img[src], script[src]"):
        candidates.append(tag.get("src", ""))
    for tag in soup.select("link[href]"):
        rels = {str(value).lower() for value in tag.get("rel", [])}
        # The legacy rel=copyright target is currently a dead 404; the live,
        # explicit rights grant is frozen separately in Credits.html.
        if rels.intersection({"stylesheet", "icon"}):
            candidates.append(tag.get("href", ""))
    for ref in candidates:
        if not ref or ref.startswith(("data:", "javascript:", "#")):
            continue
        absolute = urllib.parse.urljoin(url, ref)
        parsed = urllib.parse.urlparse(absolute)
        if is_local_authority_url(absolute):
            local.add(urllib.parse.urlunparse(parsed._replace(fragment="", query="")))
        else:
            external.add(absolute)
    return local, external


def css_dependencies(url: str, data: bytes) -> tuple[set[str], set[str]]:
    text = data.decode("utf-8", errors="strict")
    local: set[str] = set()
    external: set[str] = set()
    for _, ref in CSS_URL_RE.findall(text):
        if ref.startswith(("data:", "#")):
            continue
        absolute = urllib.parse.urljoin(url, ref)
        parsed = urllib.parse.urlparse(absolute)
        if is_local_authority_url(absolute):
            local.add(urllib.parse.urlunparse(parsed._replace(fragment="", query="")))
        else:
            external.add(absolute)
    return local, external


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def freeze(root: Path) -> None:
    static = root / "static"
    manifest_rows: list[dict[str, object]] = []
    external_dependencies: set[str] = set()
    seen_urls: set[str] = set()
    pending: list[tuple[str, str]] = []
    for rel in AUTHORITY_PAGES:
        actual = "" if rel == "index.html" else rel
        pending.append((urllib.parse.urljoin(BASE, actual), "authority_html"))
    for rel in THEORY_PAGES:
        pending.append((urllib.parse.urljoin(BASE, rel), "theory_html"))

    while pending:
        url, role = pending.pop(0)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        data, headers = fetch(url)
        if headers["final_url"].rstrip("/") == BASE.rstrip("/"):
            rel = "index.html"
        else:
            rel = normalized_rel(headers["final_url"])
        write_bytes(static / rel, data)
        manifest_rows.append(
            {
                "path": rel,
                "url": url,
                "final_url": headers["final_url"],
                "role": role,
                "bytes": len(data),
                "sha256": sha256(data),
                "content_type": headers.get("content-type", ""),
                "last_modified": headers.get("last-modified", ""),
                "etag": headers.get("etag", ""),
            }
        )
        content_type = headers.get("content-type", "").lower()
        local: set[str] = set()
        external: set[str] = set()
        if "text/html" in content_type or rel.lower().endswith(('.html', '.htm')):
            local, external = direct_dependencies(url, data)
        elif "text/css" in content_type or rel.lower().endswith(".css"):
            local, external = css_dependencies(url, data)
        external_dependencies.update(external)
        for dependency in sorted(local):
            if dependency not in seen_urls:
                pending.append((dependency, "direct_asset"))

    paths = [str(row["path"]) for row in manifest_rows]
    if len(paths) != len(set(paths)):
        raise RuntimeError("duplicate output path")
    if len(paths) != len({path.casefold() for path in paths}):
        raise RuntimeError("case-fold path collision")

    rows = sorted(manifest_rows, key=lambda row: str(row["path"]).casefold())
    csv_path = root / "RANDOM_AUTHORITY_MANIFEST.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    mathjax_url = SHARED_MATHJAX_DEPENDENCIES[0][0]
    if mathjax_url not in external_dependencies:
        raise RuntimeError("the separately frozen Random MathJax dependency is missing")
    shared_build_dependencies: list[dict[str, object]] = []
    for url, relative_path, expected_sha256 in SHARED_MATHJAX_DEPENDENCIES:
        dependency_path = root / relative_path
        if not dependency_path.is_file() or dependency_path.is_symlink():
            raise RuntimeError(f"missing shared MathJax dependency: {relative_path}")
        dependency_data = dependency_path.read_bytes()
        if sha256(dependency_data) != expected_sha256:
            raise RuntimeError(f"shared MathJax dependency hash changed: {relative_path}")
        shared_build_dependencies.append(
            {
                "url": url,
                "path": relative_path,
                "bytes": len(dependency_data),
                "sha256": expected_sha256,
                "license": "Apache-2.0",
                "license_path": "shared/MathJax/LICENSE",
            }
        )
    receipt = {
        "schema": "o009.random-authority-freeze.v3",
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority_base": BASE,
        "license_witnesses": [
            {
                "path": "index.html",
                "license": "CC BY 2.0",
                "license_url": "http://creativecommons.org/licenses/by/2.0/",
            },
            {
                "path": "Credits.html",
                "license": "CC BY 1.0",
                "license_url": "http://creativecommons.org/licenses/by/1.0/",
            },
        ],
        "license_disposition": (
            "The two current official pages conflict on the CC BY version. "
            "Both permit adaptation and commercial redistribution with attribution; "
            "retain both witnesses and do not assert one unqualified version."
        ),
        "shared_prerequisite_exclusions": ["sample/LLN.html", "sample/CLT.html"],
        "authority_pages": list(AUTHORITY_PAGES),
        "theory_pages": list(THEORY_PAGES),
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
        "manifest_sha256": sha256(csv_path.read_bytes()),
        "shared_build_dependencies": shared_build_dependencies,
        "excluded_runtime_dependencies": sorted(
            external_dependencies - {item[0] for item in SHARED_MATHJAX_DEPENDENCIES}
        ),
    }
    (root / "RANDOM_AUTHORITY_RECEIPT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def check(root: Path) -> None:
    csv_path = root / "RANDOM_AUTHORITY_MANIFEST.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    paths = [row["path"] for row in rows]
    if paths != sorted(paths, key=str.casefold):
        raise RuntimeError("manifest is not canonical")
    if len(paths) != len(set(paths)) or len(paths) != len({p.casefold() for p in paths}):
        raise RuntimeError("duplicate or case-colliding path")
    for row in rows:
        path = root / "static" / row["path"]
        data = path.read_bytes()
        if len(data) != int(row["bytes"]) or sha256(data) != row["sha256"]:
            raise RuntimeError(f"authority mismatch: {row['path']}")
    receipt = json.loads((root / "RANDOM_AUTHORITY_RECEIPT.json").read_text("utf-8"))
    if receipt["manifest_sha256"] != sha256(csv_path.read_bytes()):
        raise RuntimeError("receipt does not bind manifest")
    expected_dependencies = {item[1]: item[2] for item in SHARED_MATHJAX_DEPENDENCIES}
    recorded_dependencies = {
        row["path"]: row["sha256"] for row in receipt["shared_build_dependencies"]
    }
    if recorded_dependencies != expected_dependencies:
        raise RuntimeError("receipt shared MathJax dependency set differs")
    for relative_path, expected_sha256 in expected_dependencies.items():
        dependency = root / relative_path
        if not dependency.is_file() or dependency.is_symlink():
            raise RuntimeError(f"missing shared dependency: {relative_path}")
        if sha256(dependency.read_bytes()) != expected_sha256:
            raise RuntimeError(f"shared dependency mismatch: {relative_path}")
    print(
        f"PASS files={len(rows)} bytes={sum(int(row['bytes']) for row in rows)} "
        f"manifest_sha256={receipt['manifest_sha256']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check(args.root.resolve())
    else:
        freeze(args.root.resolve())
        check(args.root.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
