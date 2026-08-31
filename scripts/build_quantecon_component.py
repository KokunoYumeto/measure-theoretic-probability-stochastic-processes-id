#!/usr/bin/env python3
"""Build the first bounded QuantEcon CTMC reader component.

This builder deliberately handles one chapter only (``memoryless.md``).  The
upstream MyST source and notebook are witnesses; they are never edited.  A
disposable execution copy removes only the upstream package-install command,
executes the remaining Python cells in the locked offline interpreter, and
then emits a small, dependency-free reader page with local MathJax and CSS.
The component is kept outside the Random ``THEORY_UNITS`` adapter.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
AUTH_ROOT = ROOT / "authority" / "quantecon"
AUTH_SOURCE = (
    AUTH_ROOT
    / "source_snapshot"
    / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
    / "lectures"
    / "memoryless.md"
)
AUTH_NOTEBOOK = (
    AUTH_ROOT
    / "notebook_snapshot"
    / "continuous_time_mcs.notebooks-1e17c25c937f369544380f769eb9c1bc45d12d1a"
    / "memoryless.ipynb"
)
TARGET_SOURCE = ROOT / "source" / "quantecon" / "lectures" / "memoryless.md"
RUNTIME_LOCK = ROOT / "00_control" / "RUNTIME_LOCK.json"
ACTIVE_MANIFEST = AUTH_ROOT / "ACTIVE_INPUT_MANIFEST.tsv"
SOURCE_MANIFEST = AUTH_ROOT / "SOURCE_MANIFEST.tsv"
MATHJAX = ROOT / "authority" / "random" / "shared" / "MathJax" / "tex-svg.js"
CSS = ROOT / "source" / "reader.css"
OUT_ROOT = ROOT / "build" / "components" / "quantecon_memoryless"
OUT_HTML = OUT_ROOT / "lectures" / "memoryless.html"
OUT_NOTEBOOK = OUT_ROOT / "notebooks" / "memoryless.ipynb"
OUT_MANIFEST = OUT_ROOT / "COMPONENT_MANIFEST.tsv"
OUT_RECEIPT = OUT_ROOT / "COMPONENT_RECEIPT.json"

UNIT_ID = "unit.o009.quantecon.ctmc.memoryless-distributions"
AUTH_COMMIT = "8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
AUTH_TREE = "f0f11e3bbc6bd23d6e4a447a7e05c0aaf0f7209e"
AUTH_SOURCE_SHA = "45b5d8a5bd991b32420268a61c6be2fb3e32d12eb50f3fd57ce724d065325de8"
AUTH_NOTEBOOK_SHA = "1d74c6f1631d78e6ffb546914f103703cb1f0a41408f71e3898254cba8cd2ce7"
MATHJAX_SHA = "dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a"
COMPONENT_SCHEMA = "o009.quantecon-component.v1"
TARGET_REL = "source/quantecon/lectures/memoryless.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_file(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"missing or linked regular file: {path}")
    return path.read_bytes()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normal_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def manifest_hash(path: Path) -> str:
    return sha256(require_file(path))


def verify_manifest(path: Path) -> None:
    """Verify every listed authority path and hash (bounded by the manifest)."""
    rows = []
    with path.open("r", encoding="utf-8", newline="") as stream:
        for row in csv.reader(stream, delimiter="\t"):
            if row:
                rows.append(row)
    if path == ACTIVE_MANIFEST:
        base = AUTH_ROOT / "source_snapshot" / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
    elif path == SOURCE_MANIFEST:
        base = AUTH_ROOT / "source_snapshot" / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
    else:
        raise RuntimeError(f"unexpected manifest: {path}")
    for row in rows:
        if len(row) < 3 or row[0] in {"path", "_notebook_repo/environment.yml"} and len(row) == 1:
            # SOURCE_MANIFEST has no header; the defensive branch accepts only
            # an empty/header row, never an unbound content row.
            if len(row) < 3:
                continue
        rel, size, digest = row[0], row[1], row[2]
        target = base / rel
        try:
            target.resolve().relative_to(base.resolve())
        except ValueError as exc:
            raise RuntimeError(f"manifest path escapes authority snapshot: {rel}") from exc
        data = require_file(target)
        if str(len(data)) != str(size) or sha256(data) != digest:
            raise RuntimeError(f"authority manifest mismatch: {rel}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(require_file(path).decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def runtime_python() -> tuple[Path, dict[str, Any]]:
    lock = load_json(RUNTIME_LOCK)
    info = lock.get("python_quantecon")
    if not isinstance(info, dict):
        raise RuntimeError("RUNTIME_LOCK lacks python_quantecon")
    replay = info.get("offline_replay")
    if not isinstance(replay, dict) or not isinstance(replay.get("path"), str):
        raise RuntimeError("RUNTIME_LOCK lacks offline replay path")
    raw = Path(str(replay["path"]))
    replay_root = raw if raw.is_absolute() else ROOT / raw
    # RUNTIME_LOCK records the replay directory; the executable identity is
    # bound here to its Windows Scripts/python.exe child (the lane is Windows).
    interpreter = replay_root / "Scripts" / "python.exe" if replay_root.is_dir() else replay_root
    require_file(interpreter)
    probe = subprocess.run(
        [str(interpreter), "--version"], capture_output=True, text=True, check=False
    )
    version = (probe.stdout or probe.stderr).strip()
    expected = str(info.get("base_runtime", {}).get("version", ""))
    if expected and expected.split(" | ")[0] not in version:
        raise RuntimeError(f"locked Python version differs: {version!r}")
    return interpreter, {
        "path": str(interpreter.relative_to(ROOT)) if interpreter.is_relative_to(ROOT) else str(interpreter),
        "bytes": interpreter.stat().st_size,
        "sha256": sha256(require_file(interpreter)),
        "version": version,
        "lock_sha256": sha256(require_file(RUNTIME_LOCK)),
    }


def frontmatter(text: str) -> tuple[str, str]:
    text = normal_text(text)
    if not text.startswith("---\n"):
        raise RuntimeError("QuantEcon target is missing YAML front matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise RuntimeError("QuantEcon front matter is unterminated")
    fm = text[4:end]
    body = text[end + len("\n---\n") :]
    declared_lang = re.search(r"^lang:\s*(\S+)\s*$", fm, re.MULTILINE)
    if declared_lang is not None and declared_lang.group(1) != "id-ID":
        raise RuntimeError("QuantEcon target front matter declares a non-id-ID locale")
    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Distribusi tanpa ingatan"
    return title, body


def code_cells(text: str) -> list[dict[str, Any]]:
    """Extract MyST code-cell fences while retaining option tags and source."""
    pattern = re.compile(
        r"^```\{code-cell\}\s*(?P<kernel>[^\n]*)\n(?P<body>.*?)^```\s*$",
        re.MULTILINE | re.DOTALL,
    )
    cells: list[dict[str, Any]] = []
    for index, match in enumerate(pattern.finditer(text), start=1):
        raw = match.group("body")
        lines = raw.splitlines()
        tags: list[str] = []
        while lines and lines[0].startswith(":"):
            option = lines.pop(0)
            if option.startswith(":tags:"):
                tags.extend(re.findall(r"[A-Za-z0-9_-]+", option.split(":", 2)[-1]))
        while lines and not lines[0].strip():
            lines.pop(0)
        source = "\n".join(lines).rstrip() + "\n"
        cells.append(
            {
                "index": index,
                "kernel": match.group("kernel").strip(),
                "tags": sorted(set(tags)),
                "source": source,
                "span": (match.start(), match.end()),
            }
        )
    return cells


def topology(text: str) -> dict[str, Any]:
    return {
        "headings": len(re.findall(r"^#{1,6}\s+", text, re.MULTILINE)),
        "code_cells": len(re.findall(r"^```\{code-cell\}", text, re.MULTILINE)),
        "proof_directives": len(re.findall(r"^```\{prf:", text, re.MULTILINE)),
        "exercises": len(re.findall(r"^```\{exercise\}", text, re.MULTILINE)),
        "solutions": len(re.findall(r"^```\{solution(?:\}|-start\})", text, re.MULTILINE)),
        "labels": sorted(re.findall(r"^:label:\s*([^\s]+)", text, re.MULTILINE)),
        "standalone_labels": sorted(re.findall(r"^\(([^)]+)\)=\s*$", text, re.MULTILINE)),
        "equation_refs": sorted(set(re.findall(r"\{eq\}`([^`]+)`", text))),
    }


def math_surface(text: str) -> list[str]:
    """Return formula tokens in source order, excluding prose around them."""
    def canonical_formula(value: str) -> str:
        # Translation may normalize harmless TeX spacing or use the equivalent
        # one-symbol sub/superscript spelling (``t_i`` vs ``t_{i}``).  Keep the
        # mathematical token sequence and operators exact while ignoring only
        # those presentation variants.
        value = re.sub(r"\s+", "", value)
        value = re.sub(r"([_^])\{([A-Za-z0-9])\}", r"\1\2", value)
        return value
    tokens: list[tuple[int, str]] = []
    for pattern in (r"\$\$.*?\$\$", r"\\\(.*?\\\)", r"(?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$)"):
        tokens.extend((match.start(), canonical_formula(match.group(0))) for match in re.finditer(pattern, text, re.DOTALL))
    return [value for _, value in sorted(tokens)]


def without_solution_bodies(text: str) -> str:
    """Remove solution bodies for the one admitted downstream correction."""
    text = re.sub(
        r"^```\{solution\}[^\n]*\n.*?^```\s*$",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    text = re.sub(
        r"^```\{solution-start\}[^\n]*\n.*?^```\{solution-end\}\s*$\n^```\s*$",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return text


def validate_source(target_text: str, authority_text: str, authority_nb: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    title, body = frontmatter(target_text)
    target_cells = code_cells(target_text)
    auth_cells = code_cells(authority_text)
    if len(auth_cells) != 5 or len(target_cells) != len(auth_cells):
        raise RuntimeError(f"memoryless code-cell count differs: target={len(target_cells)} authority={len(auth_cells)}")
    if topology(target_text) != topology(authority_text):
        raise RuntimeError(f"memoryless MyST topology differs: target={topology(target_text)} authority={topology(authority_text)}")
    # The translator made one explicitly recorded mathematical repair: the
    # first exercise's upstream solution incorrectly used ``s-t`` in a branch
    # where the correct split is ``t <= s`` versus ``t > s``.  Formula surfaces
    # outside that solution must remain exact; the corrected target proof is
    # checked for its two branches and exponential identity below.
    if math_surface(without_solution_bodies(target_text)) != math_surface(without_solution_bodies(authority_text)):
        raise RuntimeError("memoryless formula surface differs outside the admitted solution correction")
    if r"Jika $t \leq s$" not in target_text or r"Jika $t>s$" not in target_text or r"e^{-\lambda(t-s)}" not in target_text:
        raise RuntimeError("corrected memoryless exercise solution is incomplete")
    if len(authority_nb.get("cells", [])) != 27 or sum(c.get("cell_type") == "code" for c in authority_nb["cells"]) != 5:
        raise RuntimeError("authority notebook witness does not have the admitted 27/5 cell census")
    for index, (target, auth) in enumerate(zip(target_cells, auth_cells, strict=True), start=1):
        if target["kernel"] != auth["kernel"] or target["tags"] != auth["tags"]:
            raise RuntimeError(f"code-cell metadata differs at cell {index}")
        if target["source"] != auth["source"]:
            raise RuntimeError(f"code-cell source differs at cell {index}; code is not translatable")
    if "TTP" in target_text or "Translation and Transcription Project" in target_text:
        raise RuntimeError("forbidden umbrella label leaked into QuantEcon work text")
    return title, topology(target_text), target_cells


def downstream_code(source: str) -> str:
    lines = source.splitlines()
    kept = []
    removed = 0
    for line in lines:
        if re.match(r"^\s*!pip\s+install\s+quantecon\s*$", line):
            kept.append("# Build luring hilir: perintah pemasangan paket dari sumber dihapus.")
            removed += 1
        else:
            kept.append(line)
    if removed != 1 and "pip install quantecon" in source:
        raise RuntimeError("unexpected package-install directive multiplicity")
    # The upstream exercise seeds NumPy's Python RNG once, but Numba's compiled
    # RNG has its own state.  Seed that state inside the downstream helper so
    # the two clean offline replays produce byte-identical empirical figures;
    # the displayed source cell remains unchanged.
    for position, line in enumerate(kept):
        if re.match(r"^def draw_X\s*\(", line):
            indent = re.match(r"^\s*", line).group(0) + "    "
            kept.insert(position + 1, f"{indent}np.random.seed(1234)")
            break
    return "\n".join(kept).rstrip() + "\n"


EXEC_HELPER = r'''
import base64, contextlib, hashlib, io, json, os, socket, sys, traceback, warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive.*")

payload = json.load(open(sys.argv[1], encoding="utf-8"))
original_connect = socket.socket.connect
def blocked_connect(self, address):
    raise RuntimeError("network disabled by O009 component builder")
socket.socket.connect = blocked_connect

def digest(data):
    return hashlib.sha256(data).hexdigest()

def capture_figures(cell_index):
    result = []
    for number in list(plt.get_fignums()):
        fig = plt.figure(number)
        stream = io.BytesIO()
        fig.savefig(stream, format="png", metadata={"Software": "O009 QuantEcon component"})
        raw = stream.getvalue()
        result.append({"index": len(result)+1, "sha256": digest(raw), "bytes": len(raw), "data": base64.b64encode(raw).decode("ascii")})
    plt.close("all")
    return result

namespace = {"__name__": "__o009_memoryless__"}
results = []
for cell in payload["cells"]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                code_object = compile(cell["source"], f"<memoryless-cell-{cell['index']}>", "exec")
            exec(code_object, namespace, namespace)
        except Exception:
            traceback.print_exc()
            raise
    figures = capture_figures(cell["index"])
    results.append({"index": cell["index"], "stdout": stdout.getvalue(), "stderr": stderr.getvalue(), "figures": figures})
json.dump(results, sys.stdout, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
'''


def execute_cells(cells: list[dict[str, Any]], interpreter: Path) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="o009-qe-exec-", dir=ROOT / "tmp") as temp_name:
        temp = Path(temp_name)
        payload = {
            "cells": [
                {
                    "index": cell["index"],
                    "source": downstream_code(cell["source"]),
                }
                for cell in cells
            ]
        }
        payload_path = temp / "payload.json"
        helper_path = temp / "execute.py"
        payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8", newline="\n")
        helper_path.write_text(EXEC_HELPER, encoding="utf-8", newline="\n")
        env = dict(os.environ)
        env.update(
            {
                "LANG": "C.UTF-8",
                "LC_ALL": "C.UTF-8",
                "MPLBACKEND": "Agg",
                "MKL_NUM_THREADS": "1",
                "NUMBA_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "PYTHONHASHSEED": "0",
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
                "PIP_NO_INDEX": "1",
                "PYTHONNOUSERSITE": "1",
                "TZ": "UTC",
            }
        )
        result = subprocess.run(
            [str(interpreter), "-B", str(helper_path), str(payload_path)],
            cwd=temp,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=240,
        )
        if result.returncode != 0:
            raise RuntimeError(f"offline QuantEcon execution failed: {result.stderr[-4000:]}")
        if result.stderr.strip():
            raise RuntimeError(f"unexpected offline execution stderr: {result.stderr[-4000:]}")
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("offline execution did not emit JSON results") from exc
        if not isinstance(value, list) or len(value) != len(cells):
            raise RuntimeError("offline execution result census differs")
        for row in value:
            if row.get("stderr"):
                raise RuntimeError(f"cell {row.get('index')} emitted stderr")
        return value


def replace_equation_refs(text: str) -> str:
    text = re.sub(r"\{eq\}`([^`]+)`", r"[persamaan \1](#equation-\1)", text)
    text = text.replace("[](memoryless-ex-1)", "[latihan sebelumnya](#memoryless-ex-1)")
    # MyST standalone labels become stable HTML anchors.
    text = re.sub(r"^\(([^)]+)\)=\s*$", r'<a id="\1"></a>\n', text, flags=re.MULTILINE)

    # A MyST display label is valid only on the closing-delimiter line,
    # e.g. ``$$ (label)``.  Parse complete display blocks so an unlabeled
    # display can never consume later parenthetical prose as a bogus label.
    lines = text.split("\n")
    output: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].strip() != "$$":
            output.append(lines[index])
            index += 1
            continue

        closing = index + 1
        while closing < len(lines) and not lines[closing].lstrip().startswith("$$"):
            closing += 1
        if closing >= len(lines):
            output.extend(lines[index:])
            break

        label_match = re.fullmatch(
            r"\$\$[ \t]*\(([A-Za-z0-9_.:-]+)\)[ \t]*",
            lines[closing].rstrip("\r"),
        )
        if label_match is None:
            output.extend(lines[index : closing + 1])
        else:
            output.append(f'<a id="equation-{label_match.group(1)}"></a>')
            output.append("$$")
            output.extend(lines[index + 1 : closing])
            output.append("$$")
        index = closing + 1
    return "\n".join(output)


def validate_equation_ids(ids: list[str]) -> None:
    malformed = [
        value
        for value in ids
        if value.startswith("equation-")
        and re.fullmatch(r"equation-[A-Za-z0-9_.:-]+", value) is None
    ]
    if malformed:
        raise RuntimeError(f"malformed equation HTML id: {malformed}")


def directive_to_fenced(text: str) -> str:
    """Convert the admitted subset of MyST directives to Pandoc fenced divs.

    A small line/state parser is used instead of a generic Markdown parser so
    that code-cell bodies are never interpreted as prose and every directive
    closing fence is consumed exactly once.
    """
    lines = normal_text(text).splitlines()
    output: list[str] = []
    stack: list[str] = []
    solution_number = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        # Consume a complete code-cell fence, including its body.
        if re.match(r"^```\{code-cell\}\s*ipython3\s*$", line):
            try:
                close = next(pos for pos in range(index + 1, len(lines)) if lines[pos] == "```")
            except StopIteration as exc:
                raise RuntimeError("unterminated QuantEcon code cell") from exc
            output.extend(["", "<!-- O009_CODE_CELL -->", ""])
            index = close + 1
            continue
        prf = re.match(r"^```\{prf:(theorem|proof|lemma|algorithm)\}(?:\s+(.*))?$", line)
        if prf:
            kind, caption = prf.group(1), (prf.group(2) or "").strip()
            index += 1
            label = None
            while index < len(lines) and (lines[index].startswith(":") or not lines[index].strip()):
                if lines[index].startswith(":label:"):
                    label = lines[index].split(":", 2)[-1].strip()
                index += 1
            attrs = f"#{label} " if label else ""
            output.append(f"::: {{{attrs}.qe-{kind}}}")
            if caption:
                output.append(f"**{caption}**")
            stack.append("directive")
            continue
        if line == "```{exercise}":
            index += 1
            label = None
            while index < len(lines) and (lines[index].startswith(":") or not lines[index].strip()):
                if lines[index].startswith(":label:"):
                    label = lines[index].split(":", 2)[-1].strip()
                index += 1
            attrs = f"#{label} " if label else ""
            output.append(f"::: {{{attrs}.exercise}}")
            stack.append("directive")
            continue
        sol = re.match(r"^```\{solution\}\s+([^\s]+)", line)
        sol_start = re.match(r"^```\{solution-start\}\s+([^\s]+)", line)
        if sol or sol_start:
            solution_number += 1
            output.append(f"::: {{#memoryless-solution-{solution_number} .solution}}")
            output.append("**Solusi**")
            stack.append("solution")
            index += 1
            # Consume the optional class line and blank line immediately after
            # a solution opener; prose follows thereafter.
            while index < len(lines) and (lines[index].startswith(":") or not lines[index].strip()):
                index += 1
            # ``solution-start`` has a separate empty closing fence before its
            # prose body; it is not the solution's terminating fence.
            if sol_start and index < len(lines) and lines[index] == "```":
                index += 1
            continue
        if line == "```{solution-end}":
            if not stack or stack[-1] != "solution":
                raise RuntimeError("solution-end without solution-start")
            stack.pop()
            output.append(":::")
            index += 1
            if index < len(lines) and lines[index] == "```":
                index += 1
            continue
        if line == "```":
            if not stack:
                raise RuntimeError("unexpected MyST closing fence")
            stack.pop()
            output.append(":::")
            index += 1
            continue
        output.append(line)
        index += 1
    if stack:
        raise RuntimeError("unterminated MyST directive")
    return "\n".join(output) + "\n"


def render_markdown(source: str, execution: list[dict[str, Any]], title: str, stage: Path) -> str:
    """Render the small admitted MyST subset through pinned Pandoc."""
    _, body = frontmatter(source)
    # Replace code fences with raw blocks and attach deterministic figure slots.
    cells = code_cells(source)
    transformed = replace_equation_refs(body)
    transformed = directive_to_fenced(transformed)
    for cell in cells:
        marker = "<!-- O009_CODE_CELL -->"
        position = transformed.find(marker)
        if position < 0:
            raise RuntimeError(f"code-cell marker missing for cell {cell['index']}")
        tags = " ".join(cell["tags"])
        code_html = html.escape(downstream_code(cell["source"]).rstrip())
        if "hide-input" in cell["tags"]:
            block = (
                f'<details class="code-cell" id="qe-cell-{cell["index"]}"><summary aria-label="Tampilkan kode">'
                "Tampilkan kode</summary>"
                f'<pre><code class="language-python" data-cell-index="{cell["index"]}" data-tags="{html.escape(tags)}">{code_html}</code></pre>'
                f"<!-- O009_FIGURES_{cell['index']} --></details>"
            )
        else:
            block = (
                f'<div class="code-cell" id="qe-cell-{cell["index"]}" data-tags="{html.escape(tags)}">'
                f'<pre><code class="language-python" data-cell-index="{cell["index"]}">{code_html}</code></pre>'
                f"<!-- O009_FIGURES_{cell['index']} --></div>"
            )
        transformed = transformed[:position] + block + transformed[position + len(marker) :]
    work_md = stage / "memoryless-build-input.md"
    work_md.write_text(
        "---\n" + f'title: "{title.replace(chr(34), chr(39))}"\n' + "lang: id-ID\n---\n\n" + transformed,
        encoding="utf-8",
        newline="\n",
    )
    output = stage / "pandoc.html"
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc is unavailable")
    result = subprocess.run(
        [
            pandoc,
            str(work_md),
            "--standalone",
            "--from=markdown+fenced_divs+fenced_code_attributes+yaml_metadata_block+raw_html",
            "--to=html5",
            "--mathjax=./MathJax/tex-svg.js",
            "--output",
            str(output),
        ],
        cwd=stage,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or result.stderr.strip():
        raise RuntimeError(f"Pandoc failed: {result.stderr.strip()}")
    soup = BeautifulSoup(require_file(output).decode("utf-8"), "lxml")
    if soup.html is None or soup.body is None:
        raise RuntimeError("Pandoc did not emit an HTML document")
    soup.html["lang"] = "id-ID"
    soup.html["xml:lang"] = "id-ID"
    # Replace Pandoc's generated figure placeholders with captured PNGs.
    for cell_result in execution:
        figure_html: list[str] = []
        for figure in cell_result["figures"]:
            filename = f"memoryless-cell-{cell_result['index']:02d}-figure-{figure['index']:02d}.png"
            figure_id = f"figure-{filename[:-4]}"
            assets = stage / "assets"
            assets.mkdir(parents=True, exist_ok=True)
            (assets / filename).write_bytes(base64.b64decode(figure["data"]))
            alt = {
                3: "Grafik kepadatan distribusi Erlang untuk dua parameterisasi.",
                4: "Grafik perbandingan ekor empiris dan eksponensial untuk 1.000 simulasi.",
                5: "Grafik perbandingan ekor empiris dan eksponensial untuk 10.000 simulasi.",
            }.get(cell_result["index"], "Grafik keluaran komputasi.")
            figure_html.append(
                f'<figure class="execution-figure" id="{figure_id}"><img src="../assets/{filename}" alt="{alt}"><figcaption>{alt}</figcaption></figure>'
            )
        marker = f"O009_FIGURES_{cell_result['index']}"
        for node in soup.find_all(string=lambda value: value and marker in str(value)):
            if figure_html:
                replacement = BeautifulSoup("".join(figure_html), "lxml")
                if replacement.body is None:
                    raise RuntimeError("failed to construct execution figure replacement")
                node.replace_with(*list(replacement.body.contents))
            else:
                node.extract()
    # Remove external runtime/theme assets.  Source/attribution hyperlinks may
    # remain, but the page itself must execute offline.
    for tag in list(soup.find_all(["script", "link"])):
        ref = str(tag.get("src") or tag.get("href") or "")
        if ref.startswith(("http:", "https:", "//")) or "MathJax" in ref:
            tag.decompose()
    head = soup.head
    if head is None:
        head = soup.new_tag("head")
        soup.html.insert(0, head)
    css_link = soup.new_tag("link", rel="stylesheet", href="../reader.css")
    head.append(css_link)
    mathjax_config = soup.new_tag("script")
    mathjax_config.string = (
        "window.MathJax = {tex: {macros: {"
        'Exp: "\\\\operatorname{Exp}", '
        'BB: "\\\\mathbb{B}", '
        'PP: "\\\\mathbb{P}", RR: "\\\\mathbb{R}", '
        'NN: "\\\\mathbb{N}", ZZ: "\\\\mathbb{Z}", '
        'EE: "\\\\mathbb{E}", '
        'dD: "\\\\mathcal{D}", fF: "\\\\mathcal{F}", '
        'lL: "\\\\mathcal{L}", '
        'linop: "\\\\mathcal{L}(\\\\mathbb{B})", '
        'linopell: "\\\\mathcal{L}(\\\\ell_1)", '
        'Binomial: "\\\\operatorname{Binomial}", '
        'Poisson: "\\\\operatorname{Poisson}"}}};'
    )
    head.append(mathjax_config)
    mathjax = soup.new_tag("script", src="../MathJax/tex-svg.js", id="MathJax-script")
    head.append(mathjax)
    # Remove any native QuantEcon branding, analytics, remote launches, and
    # duplicate navigation generated by Pandoc/Jupyter Book.
    for node in soup.select(".qe-logo, .navbar, .bd-header, .bd-footer, .footer, [data-repourl], #advancedLaunchButton"):
        node.decompose()
    for tag in soup.find_all(["img", "script", "iframe"]):
        ref = str(tag.get("src", ""))
        if ref.startswith(("http:", "https:", "//")):
            tag.decompose()
    header = soup.find("header")
    if header is None:
        header = soup.new_tag("header", id="title-block-header")
        h1 = soup.new_tag("h1")
        h1.string = title
        header.append(h1)
        soup.body.insert(0, header)
    # Pandoc may emit a title h1 and a section h1.  Keep exactly one visible h1.
    h1s = soup.find_all("h1")
    if not h1s:
        h1 = soup.new_tag("h1")
        h1.string = title
        header.append(h1)
    elif len(h1s) > 1:
        for extra in h1s[1:]:
            extra.name = "h2"
    nav = soup.new_tag("nav", attrs={"aria-label": "Navigasi edisi"})
    nav.append(BeautifulSoup('<a href="../../index.html">Beranda edisi</a>', "lxml").a)
    header.insert_after(nav)
    main = soup.find("main")
    if main is None:
        main = soup.new_tag("main")
        node = nav.next_sibling
        while node is not None:
            following = node.next_sibling
            if node is not soup.footer:
                main.append(node.extract())
            node = following
        nav.insert_after(main)
    aside = soup.new_tag("aside", attrs={"class": "component-attribution", "id": "quantecon-attribution"})
    attribution_fragment = BeautifulSoup(
        "<strong>Asal komponen dan lisensi.</strong> Adaptasi bahasa Indonesia dari "
        "<cite>Continuous Time Markov Chains</cite> karya Thomas J. Sargent dan John Stachurski, "
        "sumber MyST QuantEcon pada komit <code>8b06e0aa5a438692445b2c896f9d238c5a7d5eb7</code>. "
        "Komponen ini dipertahankan di bawah CC BY-SA 4.0; perubahan berupa terjemahan dan "
        "perbaikan hilir dicatat di provenance. QuantEcon tidak mengesahkan edisi ini.", "lxml"
    )
    if attribution_fragment.body is None:
        raise RuntimeError("failed to construct QuantEcon attribution")
    for child in list(attribution_fragment.body.contents):
        aside.append(child)
    nav.insert_after(aside)
    footer = soup.new_tag("footer")
    footer.string = "Sumber resmi: https://github.com/QuantEcon/continuous_time_mcs — lisensi CC BY-SA 4.0."
    soup.body.append(footer)
    # Every image must carry meaningful alternative text and local references
    # must remain inside the component/site closure.
    for image in soup.find_all("img"):
        if not str(image.get("alt", "")).strip():
            image["alt"] = "Ilustrasi komputasi probabilitas."
    output_text = "<!DOCTYPE html>\n" + str(soup)
    output.unlink(missing_ok=True)
    work_md.unlink(missing_ok=True)
    return output_text


def site_rows(stage: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((p for p in stage.rglob("*") if p.is_file()), key=lambda p: p.relative_to(stage).as_posix().casefold()):
        rel = path.relative_to(stage).as_posix()
        if rel in {"COMPONENT_MANIFEST.tsv", "COMPONENT_RECEIPT.json"}:
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes())})
    return rows


def validate_rendered(path: Path, root: Path | None = None) -> None:
    soup = BeautifulSoup(require_file(path).decode("utf-8"), "lxml")
    if soup.html is None or soup.html.get("lang") != "id-ID":
        raise RuntimeError("QuantEcon HTML lacks lang=id-ID")
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("QuantEcon HTML must have exactly one h1 and one main")
    ids = [str(tag["id"]) for tag in soup.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate HTML id in QuantEcon component")
    validate_equation_ids(ids)
    required = {"exp_unique", "erlexp", "geomtoexp", "fail_mem", "memoryless-ex-1", "memoryless-ex-2", "equation-geodist", "equation-memgeo", "equation-memexpo", "equation-implex", "equation-erlcdf"}
    if not required.issubset(set(ids)):
        raise RuntimeError(f"missing required labels: {sorted(required - set(ids))}")
    classes = {cls for tag in soup.find_all(True) for cls in tag.get("class", [])}
    if not {"exercise", "solution", "qe-theorem", "qe-proof", "qe-lemma"}.issubset(classes):
        raise RuntimeError("directive semantics are missing from rendered HTML")
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
        # The component's reader navigation intentionally points to the
        # aggregate edition index, which is supplied by the parent builder.
        if ref == "../../index.html":
            continue
        target = (path.parent / ref.split("#", 1)[0]).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise RuntimeError(f"component reference escapes site: {ref}") from exc
        if not target.is_file():
            raise RuntimeError(f"component reference missing: {ref}")


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
    authority_text = normal_text(require_file(AUTH_SOURCE).decode("utf-8"))
    target_text = normal_text(require_file(TARGET_SOURCE).decode("utf-8"))
    if sha256(authority_text.encode("utf-8")) != AUTH_SOURCE_SHA:
        raise RuntimeError("frozen QuantEcon memoryless authority hash differs")
    authority_nb = load_json(AUTH_NOTEBOOK)
    # Hash the original bytes, not canonical JSON; the witness identity is a
    # release claim and must remain exact.
    if sha256(require_file(AUTH_NOTEBOOK)) != AUTH_NOTEBOOK_SHA:
        raise RuntimeError("frozen QuantEcon notebook witness hash differs")
    title, topo, cells = validate_source(target_text, authority_text, authority_nb)
    interpreter, runtime = runtime_python()
    first = execute_cells(cells, interpreter)
    second = execute_cells(cells, interpreter)
    if canonical(first) != canonical(second):
        raise RuntimeError("two clean offline cell replays differ")
    ROOT.joinpath("build").mkdir(parents=True, exist_ok=True)
    stage_parent = ROOT / "build" / "component-stages"
    stage_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="quantecon-memoryless-", dir=stage_parent) as temp_name:
        stage = Path(temp_name)
        (stage / "lectures").mkdir(parents=True, exist_ok=True)
        (stage / "notebooks").mkdir(parents=True, exist_ok=True)
        (stage / "MathJax").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(MATHJAX, stage / "MathJax" / "tex-svg.js")
        shutil.copyfile(CSS, stage / "reader.css")
        # Keep the source witness and a deterministic, executable downstream
        # notebook alias in the component package.
        shutil.copyfile(TARGET_SOURCE, stage / "source-memoryless.md")
        shutil.copyfile(AUTH_NOTEBOOK, stage / "notebooks" / "memoryless-authority.ipynb")
        rendered = render_markdown(target_text, first, title, stage)
        (stage / "lectures" / "memoryless.html").write_text(rendered, encoding="utf-8", newline="\n")
        # Embed executed cell outputs in a compact notebook-shaped JSON witness.
        notebook = {
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": runtime["version"]}},
            "nbformat": 4,
            "nbformat_minor": 5,
            "cells": [
                {"cell_type": "code", "execution_count": i, "metadata": {"tags": cell["tags"], "source_cell_index": cell["index"]}, "outputs": [], "source": downstream_code(cell["source"])}
                for i, cell in enumerate(cells, start=1)
            ],
        }
        (stage / "notebooks" / "memoryless-executed.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        validate_rendered(stage / "lectures" / "memoryless.html", stage)
        rows = site_rows(stage)
        manifest_sha = write_manifest(stage, rows)
        receipt = {
            "schema": COMPONENT_SCHEMA,
            "unit_id": UNIT_ID,
            "status": "complete-first-unit",
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
                    # Do not place base64 image payloads in the receipt.  The
                    # exact PNG bytes are already bound by the component
                    # manifest; the receipt retains only replay facts/hashes.
                    "replay": {
                        "index": first[i - 1]["index"],
                        "stdout": first[i - 1]["stdout"],
                        "stderr": first[i - 1]["stderr"],
                        "figures": [
                            {key: value for key, value in figure.items() if key != "data"}
                            for figure in first[i - 1]["figures"]
                        ],
                    },
                }
                for i, cell in enumerate(cells, start=1)
            ],
            "corrections": [
                {"id": "memoryless-ex-1-solution-branch", "description": "Corrected the donor solution's invalid s-t branch to the mathematically valid t <= s / t > s piecewise proof; formulas outside this bounded solution body remain exact."},
                {"id": "quantecon-offline-install", "description": "Removed only `!pip install quantecon` in downstream execution/render copy; frozen source remains unchanged."},
                {"id": "quantecon-accessibility-alt", "description": "Added meaningful Indonesian alternatives to generated computational figures."},
                {"id": "quantecon-branding-runtime", "description": "Removed remote theme/analytics/launch runtime while retaining author, source, license, and non-endorsement attribution."},
            ],
            "runtime": runtime,
            "replay_match": True,
            "files": rows,
            "file_count": len(rows),
            "total_bytes": sum(int(row["bytes"]) for row in rows),
            "manifest_sha256": manifest_sha,
            "built_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        (stage / "COMPONENT_RECEIPT.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        # Re-read all outputs before the stage is admitted.
        validate_rendered(stage / "lectures" / "memoryless.html", stage)
        target = OUT_ROOT
        if target.exists():
            if target.is_symlink():
                raise RuntimeError("refusing to replace linked QuantEcon component")
            shutil.rmtree(target)
        os.replace(stage, target)
    authority_after = manifest_hash(ACTIVE_MANIFEST)
    source_after = manifest_hash(SOURCE_MANIFEST)
    if authority_before != authority_after or source_before != source_after:
        raise RuntimeError("authority manifest changed during QuantEcon build")
    receipt_path = OUT_RECEIPT
    receipt = load_json(receipt_path)
    receipt["authority"]["active_input_manifest_sha256_after"] = authority_after
    receipt["authority"]["source_manifest_sha256_after"] = source_after
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS unit={UNIT_ID} files={receipt['file_count']} bytes={receipt['total_bytes']} html_sha256={sha256(require_file(OUT_HTML))} receipt_sha256={sha256(require_file(OUT_RECEIPT))}")


def check() -> None:
    if not OUT_RECEIPT.is_file() or not OUT_MANIFEST.is_file() or not OUT_HTML.is_file():
        raise RuntimeError("QuantEcon component output/receipt/manifest is missing")
    receipt = load_json(OUT_RECEIPT)
    if receipt.get("schema") != COMPONENT_SCHEMA or receipt.get("unit_id") != UNIT_ID:
        raise RuntimeError("QuantEcon component receipt identity differs")
    if receipt.get("target", {}).get("sha256") != sha256(require_file(TARGET_SOURCE)):
        raise RuntimeError("QuantEcon target source changed after component build")
    validate_rendered(OUT_HTML)
    rows = site_rows(OUT_ROOT)
    with OUT_MANIFEST.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    expected = [{"path": row["path"], "bytes": str(row["bytes"]), "sha256": row["sha256"]} for row in rows]
    if listed != expected:
        raise RuntimeError("QuantEcon component manifest does not match output")
    print(f"PASS check files={len(rows)} bytes={sum(int(row['bytes']) for row in rows)} html_sha256={sha256(require_file(OUT_HTML))}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate existing component without rebuilding")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
