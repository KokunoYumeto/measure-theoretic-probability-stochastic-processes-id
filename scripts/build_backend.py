#!/usr/bin/env python3
"""Build and strictly validate the deterministic O009 modular backend."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
AUTH_RANDOM = ROOT / "authority" / "random"
LAB = ROOT / "source" / "labs" / "01-konvergensi-monte-carlo.Rmd"
TERMS = ROOT / "00_control" / "TERMINOLOGY.csv"
BUILD_SCRIPT = ROOT / "scripts" / "build_first_boundary.py"
EXPORTER = Path(__file__).resolve()
BUILD_MANIFEST = ROOT / "build" / "site" / "PACKAGE_MANIFEST.csv"
BUILD_RECEIPT = ROOT / "build" / "site" / "BUILD_RECEIPT.json"
RANDOM_MANIFEST = AUTH_RANDOM / "RANDOM_AUTHORITY_MANIFEST.csv"
RANDOM_RECEIPT = AUTH_RANDOM / "RANDOM_AUTHORITY_RECEIPT.json"
ZIT_ROOT = (
    ROOT
    / "authority"
    / "zitkovic"
    / "witness"
    / "stochastic-book-e2b35ad91a3689454ae6455e8ffc510a90760c0d"
)
ZIT_ZIP = ROOT / "authority" / "zitkovic" / "stochastic-book-e2b35ad91a3689454ae6455e8ffc510a90760c0d.zip"
ZIT_LICENSE = ZIT_ROOT / "LICENSE"
ZIT_SIMULATION = ZIT_ROOT / "source" / "02-simulation.Rmd"

THEORY_SPECS = (
    {
        "rel": "prob/Convergence.html",
        "slug": "prob.convergence",
        "order": 1,
        "concept_ids": [
            "concept.probability.convergence",
            "concept.probability.almost-sure-convergence",
            "concept.probability.convergence-in-probability",
            "concept.probability.borel-cantelli",
        ],
    },
    {
        "rel": "prob/Probability2.html",
        "slug": "prob.probability-revisited",
        "order": 2,
        "concept_ids": [
            "concept.probability.measure-space",
            "concept.probability.almost-sure-equivalence",
            "concept.probability.exchangeability",
            "concept.probability.tail-events",
            "concept.probability.zero-one-laws",
        ],
    },
    {
        "rel": "prob/Processes.html",
        "slug": "prob.processes",
        "order": 3,
        "concept_ids": [
            "concept.stochastic.process",
            "concept.stochastic.process.measurability",
            "concept.stochastic.process.equivalence",
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.kolmogorov-extension",
        ],
    },
    {
        "rel": "prob/Stop.html",
        "slug": "prob.stop",
        "order": 4,
        "concept_ids": [
            "concept.stochastic.filtration",
            "concept.stochastic.stopping-time",
            "concept.stochastic.stopped-process",
            "concept.stochastic.stopping-time-sigma-algebra",
            "concept.stochastic.right-continuity",
        ],
    },
    {
        "rel": "dist/Convergence.html",
        "slug": "dist.convergence",
        "order": 5,
        "concept_ids": [
            "concept.probability.convergence",
            "concept.probability.convergence-in-probability",
            "concept.probability.convergence-in-distribution",
            "concept.probability.skorohod-representation",
            "concept.probability.scheffe",
        ],
    },
    {
        "rel": "expect/Conditional2.html",
        "slug": "expect.conditional2",
        "order": 6,
        "concept_ids": [
            "concept.conditional.expectation",
            "concept.conditional.probability",
            "concept.conditional.best-predictor",
            "concept.conditional.variance",
            "concept.conditional.covariance",
        ],
    },
    {
        "rel": "expect/Uniform.html",
        "slug": "expect.uniform",
        "order": 7,
        "concept_ids": [
            "concept.expectation.uniform-integrability",
            "concept.probability.lp-convergence",
            "concept.probability.convergence-in-probability",
            "concept.conditional.expectation",
        ],
    },
    {
        "rel": "expect/Kernels.html",
        "slug": "expect.kernels",
        "order": 8,
        "concept_ids": [
            "concept.kernel.measure",
            "concept.kernel.probability",
            "concept.kernel.operator",
            "concept.kernel.composition",
            "concept.kernel.density",
            "concept.kernel.invariant",
            "concept.conditional.regular-distribution",
        ],
    },
    {
        "rel": "martingales/Introduction.html",
        "slug": "martingales.introduction",
        "order": 9,
        "concept_ids": [
            "concept.martingale",
            "concept.martingale.submartingale",
            "concept.martingale.supermartingale",
            "concept.martingale.difference-sequence",
            "concept.stochastic.random-walk",
            "concept.martingale.likelihood-ratio",
            "concept.stochastic.branching-process",
            "concept.martingale.doob",
        ],
    },
    {
        "rel": "martingales/Properties.html",
        "slug": "martingales.properties",
        "order": 10,
        "concept_ids": [
            "concept.function.convex",
            "concept.martingale.transform",
            "concept.martingale.doob-decomposition",
            "concept.martingale.doob-meyer",
            "concept.markov.harmonic-function",
            "concept.stochastic.stationary-independent-increments",
            "concept.martingale",
            "concept.markov.process",
        ],
    },
    {
        "rel": "martingales/Stop.html",
        "slug": "martingales.stop",
        "order": 11,
        "concept_ids": [
            "concept.stochastic.stopping-time",
            "concept.stochastic.stopped-process",
            "concept.martingale.optional-stopping",
            "concept.stochastic.hitting-time",
            "concept.stochastic.random-walk",
            "concept.probability.wald-equation",
            "concept.probability.pattern-waiting-time",
            "concept.stochastic.optimal-stopping",
        ],
    },
    {
        "rel": "martingales/Inequalities.html",
        "slug": "martingales.inequalities",
        "order": 12,
        "concept_ids": [
            "concept.martingale.maximal-process",
            "concept.martingale.doob-maximal-inequality",
            "concept.martingale.lp-maximal-inequality",
            "concept.martingale.upcrossing",
            "concept.probability.kolmogorov-inequality",
            "concept.stochastic.random-walk",
            "concept.stochastic.bold-play",
        ],
    },
    {
        "rel": "martingales/Convergence.html",
        "slug": "martingales.convergence",
        "order": 13,
        "concept_ids": [
            "concept.martingale.convergence-theorem",
            "concept.martingale.terminal-representation",
            "concept.expectation.uniform-integrability",
            "concept.probability.lp-convergence",
            "concept.martingale.lp-convergence",
            "concept.stochastic.random-walk",
            "concept.martingale.doob",
            "concept.probability.zero-one-laws",
            "concept.stochastic.branching-process",
            "concept.stochastic.beta-bernoulli",
            "concept.stochastic.polya-urn",
            "concept.martingale.likelihood-ratio",
            "concept.martingale.partial-product",
            "concept.measure.radon-nikodym-density",
            "concept.martingale.density-process",
        ],
    },
)

SCHEMA = "o009.backend.entity.v2"
MANIFEST_SCHEMA = "o009.backend-manifest.v2"
WORKFLOW = "o009-id-production"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")

RECORD_TYPES = {
    "program",
    "course",
    "resource",
    "edition",
    "rights",
    "concept",
    "outcome",
    "unit",
    "asset",
    "segment",
}
TRANSLATION_STATES = {
    "source_frozen",
    "external_dependency",
    "draft",
    "translated",
    "structurally_verified",
    "authored",
    "built",
}
RELATIONSHIPS = {"translates", "adapts", "authored", "copies", "documents"}
RELATION_TYPES = {
    "contains",
    "depends-on",
    "prerequisite",
    "hints",
    "answers",
    "solves",
    "teaches",
    "assesses",
    "precedes",
    "translates",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def require_file(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"missing or linked regular file: {relative(path)}")
    return path.read_bytes()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(require_file(path).decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {relative(path)}")
    return value


def source_stamp() -> tuple[str, str]:
    """Use the frozen build receipt's timestamp, never the wall clock."""
    receipt = load_json(BUILD_RECEIPT)
    stamp = receipt.get("built_at_utc")
    if not isinstance(stamp, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?\+00:00", stamp
    ):
        raise RuntimeError("build receipt lacks a deterministic UTC source stamp")
    return stamp, sha256(require_file(BUILD_RECEIPT))


STAMP, STAMP_SOURCE_SHA256 = source_stamp()


def record(
    record_type: str,
    stable_id: str,
    *,
    parent_id: str | None = None,
    order: int | None = None,
    path: str | None = None,
    resource_id: str | None = None,
    edition_id: str | None = None,
    source_local_id: str | None = None,
    source_locator: str | None = None,
    source_sha256: str | None = None,
    target_sha256: str | None = None,
    locale: str = "zxx",
    translation_state: str = "source_frozen",
    relationship: str | None = None,
    rights_id: str | None = None,
    concept_ids: list[str] | None = None,
    status: str = "active",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "record_type": record_type,
        "id": stable_id,
        "source_local_id": source_local_id,
        "parent_id": parent_id,
        "order": order,
        "path": path,
        "resource_id": resource_id,
        "edition_id": edition_id,
        "source_locator": source_locator,
        "source_sha256": source_sha256,
        "target_sha256": target_sha256,
        "locale": locale,
        "translation_state": translation_state,
        "source_target_relationship": relationship,
        "concept_ids": concept_ids or [],
        "rights_id": rights_id,
        "status": status,
        "timestamp": STAMP,
        "responsible_workflow": WORKFLOW,
        "supersedes": None,
        "payload": payload or {},
    }


def relation(
    relation_id: str,
    relation_type: str,
    source_id: str,
    target_id: str,
    evidence: str,
) -> dict[str, str]:
    return {
        "relation_id": relation_id,
        "relation_type": relation_type,
        "source_id": source_id,
        "target_id": target_id,
        "evidence": evidence,
        "status": "active",
    }


def rights_witness_hash(parts: Iterable[str]) -> str:
    return sha256(("\n".join(parts) + "\n").encode("utf-8"))


def lab_rights_witness(text: str) -> str:
    metadata = re.search(
        r'^  donor_license: "CC0-1\.0"\r?\n  adaptation_license: "CC-BY-4\.0"$',
        text,
        re.MULTILINE,
    )
    notice = re.search(
        r'^> \*\*Asal komponen dan lisensi\.\*\*.*?^> baru dan juga dilepas dengan CC BY 4\.0\.$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    if metadata is None or notice is None:
        raise RuntimeError("lab rights witness text is missing or changed")
    return metadata.group(0) + "\n" + notice.group(0) + "\n"


def fixed_entities(lab_text: str) -> list[dict[str, Any]]:
    random_receipt = load_json(RANDOM_RECEIPT)
    build_receipt = load_json(BUILD_RECEIPT)
    random_manifest_hash = sha256(require_file(RANDOM_MANIFEST))
    if random_receipt.get("manifest_sha256") != random_manifest_hash:
        raise RuntimeError("Random authority receipt does not bind its current manifest")
    adaptation_witness = lab_rights_witness(lab_text)
    random_index = AUTH_RANDOM / "static" / "index.html"
    random_credits = AUTH_RANDOM / "static" / "Credits.html"
    entities = [
        record(
            "program",
            "program.math.id",
            locale="id-ID",
            translation_state="draft",
            payload={"title": "Program Matematika Bahasa Indonesia"},
        ),
        record(
            "course",
            "course.o009.d30",
            parent_id="program.math.id",
            locale="id-ID",
            translation_state="draft",
            concept_ids=[
                "concept.probability.convergence",
                "concept.probability.measure-space",
                "concept.probability.almost-sure-equivalence",
                "concept.probability.exchangeability",
                "concept.probability.tail-events",
                "concept.probability.zero-one-laws",
                "concept.probability.convergence-in-distribution",
                "concept.probability.skorohod-representation",
                "concept.probability.scheffe",
                "concept.stochastic.process",
                "concept.stochastic.process.measurability",
                "concept.stochastic.process.equivalence",
                "concept.stochastic.process.finite-dimensional-distributions",
                "concept.stochastic.process.kolmogorov-extension",
                "concept.stochastic.filtration",
                "concept.stochastic.stopping-time",
                "concept.stochastic.stopped-process",
                "concept.stochastic.stopping-time-sigma-algebra",
                "concept.stochastic.right-continuity",
                "concept.conditional.expectation",
                "concept.conditional.probability",
                "concept.conditional.best-predictor",
                "concept.conditional.variance",
                "concept.conditional.covariance",
                "concept.expectation.uniform-integrability",
                "concept.probability.lp-convergence",
                "concept.kernel.measure",
                "concept.kernel.probability",
                "concept.kernel.operator",
                "concept.kernel.composition",
                "concept.kernel.density",
                "concept.kernel.invariant",
                "concept.conditional.regular-distribution",
                "concept.martingale",
                "concept.martingale.submartingale",
                "concept.martingale.supermartingale",
                "concept.martingale.difference-sequence",
                "concept.stochastic.random-walk",
                "concept.martingale.likelihood-ratio",
                "concept.stochastic.branching-process",
                "concept.martingale.doob",
                "concept.function.convex",
                "concept.martingale.transform",
                "concept.martingale.doob-decomposition",
                "concept.martingale.doob-meyer",
                "concept.markov.harmonic-function",
                "concept.stochastic.stationary-independent-increments",
                "concept.martingale.optional-stopping",
                "concept.stochastic.hitting-time",
                "concept.probability.wald-equation",
                "concept.probability.pattern-waiting-time",
                "concept.stochastic.optimal-stopping",
                "concept.martingale.maximal-process",
                "concept.martingale.doob-maximal-inequality",
                "concept.martingale.lp-maximal-inequality",
                "concept.martingale.upcrossing",
                "concept.probability.kolmogorov-inequality",
                "concept.stochastic.bold-play",
                "concept.martingale.convergence-theorem",
                "concept.martingale.terminal-representation",
                "concept.martingale.lp-convergence",
                "concept.stochastic.beta-bernoulli",
                "concept.stochastic.polya-urn",
                "concept.martingale.partial-product",
                "concept.measure.radon-nikodym-density",
                "concept.martingale.density-process",
                "concept.markov.process",
                "concept.poisson.process",
                "concept.renewal.process",
                "concept.brownian.motion",
            ],
            payload={
                "role_id": "D30",
                "title": "Probabilitas Teoretis-Ukuran dan Proses Stokastik",
                "shared_prerequisite_course": "course.o006.c140",
            },
        ),
        record(
            "resource",
            "resource.random.kyle-siegrist",
            source_locator="https://www.randomservices.org/random/",
            source_sha256=random_manifest_hash,
            payload={"creator": "Kyle Siegrist", "authority_kind": "URL-byte snapshot"},
        ),
        record(
            "edition",
            "edition.random.snapshot.2026-03-13",
            parent_id="resource.random.kyle-siegrist",
            resource_id="resource.random.kyle-siegrist",
            source_locator=relative(RANDOM_MANIFEST),
            source_sha256=random_manifest_hash,
            payload={
                "retrieved": str(random_receipt["fetched_at_utc"]),
                "upstream_deployed": "2026-03-13",
                "receipt_sha256": sha256(require_file(RANDOM_RECEIPT)),
            },
        ),
        record(
            "resource",
            "resource.zitkovic.stochastic-book",
            source_locator="https://github.com/gordanz/stochastic-book",
            source_sha256=sha256(require_file(ZIT_ZIP)),
            payload={"creator": "Gordan Žitković", "donor_rights_id": "rights.zitkovic.donor.cc0-1.0"},
        ),
        record(
            "edition",
            "edition.zitkovic.e2b35ad9",
            parent_id="resource.zitkovic.stochastic-book",
            resource_id="resource.zitkovic.stochastic-book",
            source_locator=relative(ZIT_ZIP),
            source_sha256=sha256(require_file(ZIT_ZIP)),
            payload={
                "commit": "e2b35ad91a3689454ae6455e8ffc510a90760c0d",
                "tree": "9947483e0cafa8dae52b2f6b0592860cf2e59c3d",
            },
        ),
        record(
            "resource",
            "resource.o006.c140.shared",
            source_locator="cross-lane:O006/C140",
            translation_state="external_dependency",
            status="external_dependency",
            payload={"scope": "Random sampling chapter including LLN/CLT"},
        ),
        record(
            "rights",
            "rights.random.cc-by-2.0.witness",
            resource_id="resource.random.kyle-siegrist",
            source_locator=relative(random_index),
            source_sha256=sha256(require_file(random_index)),
            payload={
                "license": "CC-BY-2.0",
                "license_url": "http://creativecommons.org/licenses/by/2.0/",
                "witness_path": relative(random_index),
            },
        ),
        record(
            "rights",
            "rights.random.cc-by-1.0.witness",
            resource_id="resource.random.kyle-siegrist",
            source_locator=relative(random_credits),
            source_sha256=sha256(require_file(random_credits)),
            payload={
                "license": "CC-BY-1.0",
                "license_url": "http://creativecommons.org/licenses/by/1.0/",
                "witness_path": relative(random_credits),
            },
        ),
        record(
            "rights",
            "rights.random.dual-witness",
            resource_id="resource.random.kyle-siegrist",
            source_locator=relative(RANDOM_RECEIPT),
            source_sha256=sha256(require_file(RANDOM_RECEIPT)),
            payload={
                "witness_rights_ids": [
                    "rights.random.cc-by-2.0.witness",
                    "rights.random.cc-by-1.0.witness",
                ],
                "disposition": str(random_receipt["license_disposition"]),
                "attribution_required": True,
            },
        ),
        record(
            "rights",
            "rights.random.martingale-image.cc-by-3.0",
            resource_id="resource.random.kyle-siegrist",
            source_locator="authority/random/static/martingales/Martingale.png",
            source_sha256=sha256(
                require_file(AUTH_RANDOM / "static" / "martingales" / "Martingale.png")
            ),
            payload={
                "license": "CC-BY-3.0",
                "license_url": "http://creativecommons.org/licenses/by/3.0",
                "creator": "Danielle M.",
                "source_url": "https://commons.wikimedia.org/w/index.php?curid=13264705",
                "scope": "martingales/Martingale.png only",
                "attribution_preserved_in": "martingales/Introduction.html#fig1",
            },
        ),
        record(
            "rights",
            "rights.zitkovic.donor.cc0-1.0",
            resource_id="resource.zitkovic.stochastic-book",
            source_locator=relative(ZIT_LICENSE),
            source_sha256=sha256(require_file(ZIT_LICENSE)),
            payload={
                "license": "CC0-1.0",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "scope": "unaltered donor components only",
                "witness_path": relative(ZIT_LICENSE),
            },
        ),
        record(
            "rights",
            "rights.o009.indonesian-adaptation.cc-by-4.0",
            source_locator="source/labs/01-konvergensi-monte-carlo.Rmd#authoring-rights-and-attribution",
            source_sha256=sha256(adaptation_witness.encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": "Indonesian translation and adaptation bytes",
                "donor_component_rights_id": "rights.zitkovic.donor.cc0-1.0",
                "does_not_relicense_donor_bytes": True,
            },
        ),
        record(
            "rights",
            "rights.o009.original.cc-by-4.0",
            source_locator="source/labs/01-konvergensi-monte-carlo.Rmd#authoring-rights-and-attribution",
            source_sha256=sha256(adaptation_witness.encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": "original Indonesian additions",
            },
        ),
        record(
            "rights",
            "rights.mathjax.apache-2.0",
            source_locator="authority/random/shared/MathJax/LICENSE",
            source_sha256=sha256(require_file(AUTH_RANDOM / "shared" / "MathJax" / "LICENSE")),
            payload={"license": "Apache-2.0", "version": "3.1.2"},
        ),
    ]
    concepts = {
        "concept.probability.convergence": "convergence of events and random variables",
        "concept.probability.almost-sure-convergence": "almost sure convergence",
        "concept.probability.convergence-in-probability": "convergence in probability",
        "concept.probability.borel-cantelli": "Borel–Cantelli lemmas",
        "concept.probability.measure-space": "probability spaces as measure spaces",
        "concept.probability.almost-sure-equivalence": "almost-sure equivalence and completion",
        "concept.probability.exchangeability": "exchangeable events and random variables",
        "concept.probability.tail-events": "tail sigma-algebras, events, and variables",
        "concept.probability.zero-one-laws": "zero-one laws",
        "concept.probability.convergence-in-distribution": "convergence in distribution",
        "concept.probability.skorohod-representation": "Skorohod representation",
        "concept.probability.scheffe": "Scheffé's theorem",
        "concept.stochastic.process": "stochastic process",
        "concept.stochastic.process.measurability": "measurable stochastic processes",
        "concept.stochastic.process.equivalence": "versions, equivalence in distribution, and indistinguishability",
        "concept.stochastic.process.finite-dimensional-distributions": "finite-dimensional distributions",
        "concept.stochastic.process.kolmogorov-extension": "Kolmogorov extension construction",
        "concept.stochastic.filtration": "filtration",
        "concept.stochastic.stopping-time": "stopping time",
        "concept.stochastic.stopped-process": "stopped stochastic process",
        "concept.stochastic.stopping-time-sigma-algebra": "sigma-algebra at a stopping time",
        "concept.stochastic.right-continuity": "right-continuous filtration",
        "concept.conditional.expectation": "measure-theoretic conditional expectation",
        "concept.conditional.probability": "conditional probability given a sigma-algebra",
        "concept.conditional.best-predictor": "conditional expectation as best predictor",
        "concept.conditional.variance": "conditional variance",
        "concept.conditional.covariance": "conditional covariance",
        "concept.expectation.uniform-integrability": "uniform integrability",
        "concept.kernel.measure": "measure kernel",
        "concept.kernel.probability": "probability kernel",
        "concept.kernel.operator": "kernel integral operators",
        "concept.kernel.composition": "kernel composition",
        "concept.kernel.density": "kernel density function",
        "concept.kernel.invariant": "invariant measures and functions",
        "concept.conditional.regular-distribution": "regular conditional distribution",
        "concept.probability.lp-convergence": "convergence in Lp",
        "concept.martingale": "martingale",
        "concept.martingale.submartingale": "submartingale",
        "concept.martingale.supermartingale": "supermartingale",
        "concept.martingale.difference-sequence": "martingale difference sequence",
        "concept.stochastic.random-walk": "random walk",
        "concept.martingale.likelihood-ratio": "likelihood-ratio martingale",
        "concept.stochastic.branching-process": "branching process",
        "concept.martingale.doob": "Doob martingale",
        "concept.function.convex": "convex function",
        "concept.martingale.transform": "martingale transform",
        "concept.martingale.doob-decomposition": "Doob decomposition",
        "concept.martingale.doob-meyer": "Doob-Meyer decomposition",
        "concept.markov.harmonic-function": "harmonic function for a Markov process",
        "concept.stochastic.stationary-independent-increments": "stationary independent increments",
        "concept.martingale.optional-stopping": "optional stopping theorem",
        "concept.stochastic.hitting-time": "hitting time",
        "concept.probability.wald-equation": "Wald's equation",
        "concept.probability.pattern-waiting-time": "waiting time for a finite pattern",
        "concept.stochastic.optimal-stopping": "optimal stopping",
        "concept.martingale.maximal-process": "maximal process",
        "concept.martingale.doob-maximal-inequality": "Doob maximal inequality",
        "concept.martingale.lp-maximal-inequality": "Doob Lp maximal inequality",
        "concept.martingale.upcrossing": "upcrossings and Doob upcrossing inequality",
        "concept.probability.kolmogorov-inequality": "Kolmogorov maximal inequality",
        "concept.stochastic.bold-play": "bold-play gambling strategy",
        "concept.martingale.convergence-theorem": "martingale convergence theorem",
        "concept.martingale.terminal-representation": "terminal-variable representation of a uniformly integrable martingale",
        "concept.martingale.lp-convergence": "Lp convergence of martingales",
        "concept.stochastic.beta-bernoulli": "beta-Bernoulli process",
        "concept.stochastic.polya-urn": "Pólya urn process",
        "concept.martingale.partial-product": "partial-product martingale",
        "concept.measure.radon-nikodym-density": "Radon-Nikodym density",
        "concept.martingale.density-process": "density martingale",
        "concept.markov.process": "Markov process",
        "concept.poisson.process": "Poisson process",
        "concept.renewal.process": "renewal process",
        "concept.brownian.motion": "Brownian motion",
        "concept.monte-carlo": "Monte Carlo estimation",
    }
    for stable_id, label in concepts.items():
        entities.append(record("concept", stable_id, payload={"label_en": label}))
    outcomes = {
        "outcome.o009.estimate-expectation-monte-carlo": (
            "Menaksir nilai harapan dengan simulasi Monte Carlo deterministik.",
            "apply",
            ["concept.monte-carlo"],
        ),
        "outcome.o009.explain-lln-monte-carlo": (
            "Menjelaskan hubungan hukum bilangan besar dengan estimasi Monte Carlo.",
            "understand",
            ["concept.monte-carlo", "concept.probability.convergence-in-probability"],
        ),
        "outcome.o009.distinguish-evidence-proof": (
            "Membedakan bukti empiris simulasi dari pembuktian probabilistik.",
            "analyze",
            ["concept.monte-carlo", "concept.probability.convergence-in-probability"],
        ),
        "outcome.o009.prove-convergence-in-probability": (
            "Membuktikan konvergensi dalam probabilitas memakai ketaksamaan Chebyshev.",
            "prove",
            ["concept.probability.convergence-in-probability"],
        ),
        "outcome.o009.check-optional-stopping-conditions": (
            "Memeriksa syarat keterbatasan atau integrabilitas sebelum menerapkan teorema penghentian opsional.",
            "analyze",
            ["concept.stochastic.stopping-time", "concept.martingale.optional-stopping"],
        ),
        "outcome.o009.prove-stopped-martingale": (
            "Membuktikan bahwa penghentian mempertahankan sifat martingal, submartingal, atau supermartingal.",
            "prove",
            ["concept.stochastic.stopped-process", "concept.martingale.optional-stopping"],
        ),
        "outcome.o009.compute-random-time-expectations": (
            "Menghitung probabilitas pencapaian dan nilai harapan pada waktu henti, termasuk Persamaan Wald dan waktu tunggu pola.",
            "apply",
            [
                "concept.stochastic.hitting-time",
                "concept.stochastic.random-walk",
                "concept.probability.wald-equation",
                "concept.probability.pattern-waiting-time",
            ],
        ),
        "outcome.o009.analyze-optimal-stopping": (
            "Menganalisis aturan ambang penghentian optimal pada masalah sekretaris.",
            "analyze",
            ["concept.stochastic.optimal-stopping"],
        ),
        "outcome.o009.apply-martingale-maximal-inequalities": (
            "Menerapkan pertidaksamaan maksimal Doob dan Kolmogorov untuk membatasi probabilitas maksimum lintasan.",
            "apply",
            [
                "concept.martingale.maximal-process",
                "concept.martingale.doob-maximal-inequality",
                "concept.probability.kolmogorov-inequality",
            ],
        ),
        "outcome.o009.use-upcrossings-for-convergence": (
            "Menggunakan pertidaksamaan lintasan-naik untuk mengendalikan osilasi martingal dan menyiapkan teorema konvergensi.",
            "analyze",
            ["concept.martingale.upcrossing"],
        ),
        "outcome.o009.audit-gambling-maximal-bound": (
            "Memeriksa syarat keterprediksian, kenegatifan, dan keterbatasan utang saat menerapkan batas maksimal pada strategi perjudian.",
            "analyze",
            [
                "concept.martingale.supermartingale",
                "concept.stochastic.bold-play",
            ],
        ),
        "outcome.o009.prove-martingale-convergence": (
            "Membuktikan konvergensi hampir pasti martingal dengan pertidaksamaan lintas-naik dan syarat keterbatasan L1.",
            "prove",
            ["concept.martingale.convergence-theorem", "concept.martingale.upcrossing"],
        ),
        "outcome.o009.characterize-ui-martingales": (
            "Mengkarakterisasi martingal terintegralkan seragam melalui representasi peubah terminal dan konvergensi dalam rata-rata.",
            "analyze",
            ["concept.expectation.uniform-integrability", "concept.martingale.terminal-representation"],
        ),
        "outcome.o009.apply-lp-martingale-convergence": (
            "Menerapkan pertidaksamaan maksimal untuk membuktikan konvergensi martingal dalam Lp.",
            "apply",
            ["concept.martingale.lp-convergence", "concept.martingale.lp-maximal-inequality"],
        ),
        "outcome.o009.analyze-martingale-limit-applications": (
            "Menganalisis limit martingal pada gerak acak, proses percabangan, model Bayes, uji rasio kemungkinan, dan hasil kali parsial.",
            "analyze",
            [
                "concept.stochastic.random-walk",
                "concept.stochastic.branching-process",
                "concept.stochastic.beta-bernoulli",
                "concept.stochastic.polya-urn",
                "concept.martingale.likelihood-ratio",
                "concept.martingale.partial-product",
            ],
        ),
        "outcome.o009.recover-density-martingale-limits": (
            "Menentukan limit proses kerapatan melalui teorema Radon-Nikodym dan dekomposisi bagian singular.",
            "analyze",
            ["concept.measure.radon-nikodym-density", "concept.martingale.density-process"],
        ),
    }
    for stable_id, (label, level, concept_ids) in outcomes.items():
        entities.append(
            record(
                "outcome",
                stable_id,
                parent_id="course.o009.d30",
                locale="id-ID",
                translation_state="authored",
                rights_id="rights.o009.original.cc-by-4.0",
                concept_ids=concept_ids,
                payload={"label": label, "cognitive_level": level},
            )
        )
    if build_receipt.get("schema") != "o009.reader-build.v2":
        raise RuntimeError("unsupported reader build receipt schema")
    return entities


def load_build_validator() -> Any:
    spec = importlib.util.spec_from_file_location("o009_build", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load first-boundary build validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def html_entities() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    build_module = load_build_validator()
    builder_rels = [str(item["rel"]) for item in build_module.THEORY_UNITS]
    backend_rels = [str(item["rel"]) for item in THEORY_SPECS]
    if builder_rels != backend_rels:
        raise RuntimeError(
            f"builder/backend theory sequence differs: builder={builder_rels} backend={backend_rels}"
        )
    backend_orders = [int(item["order"]) for item in THEORY_SPECS]
    if backend_orders != list(range(1, len(THEORY_SPECS) + 1)):
        raise RuntimeError(f"backend theory order must be contiguous tuple order: {backend_orders}")
    if len({str(item["slug"]) for item in THEORY_SPECS}) != len(THEORY_SPECS):
        raise RuntimeError("backend theory slugs must be unique")
    build_module.validate_theory_translation()
    entities: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    relations: list[dict[str, str]] = []
    page_ids: list[str] = []
    for spec in THEORY_SPECS:
        rel = str(spec["rel"])
        slug = str(spec["slug"])
        authority = AUTH_RANDOM / "static" / Path(rel)
        target_path = ROOT / "source" / "theory" / Path(rel)
        source_bytes = require_file(authority)
        target_bytes = require_file(target_path)
        source = BeautifulSoup(source_bytes.decode("utf-8"), "lxml")
        target = BeautifulSoup(target_bytes.decode("utf-8"), "lxml")
        left_tags = source.find_all(True)
        right_tags = target.find_all(True)
        page_id = f"unit.o009.random.{slug}"
        page_ids.append(page_id)
        entities.append(
            record(
                "unit",
                page_id,
                parent_id="course.o009.d30",
                order=int(spec["order"]),
                path=rel,
                resource_id="resource.random.kyle-siegrist",
                edition_id="edition.random.snapshot.2026-03-13",
                source_local_id=rel,
                source_locator=f"https://www.randomservices.org/random/{rel}",
                source_sha256=sha256(source_bytes),
                target_sha256=sha256(target_bytes),
                locale="id-ID",
                translation_state="structurally_verified",
                relationship="translates",
                rights_id="rights.random.dual-witness",
                concept_ids=list(spec["concept_ids"]),
                payload={"unit_kind": "section", "source_language": "en", "body_extent": "complete"},
            )
        )
        semantic_indexes: defaultdict[str, int] = defaultdict(int)
        semantic_target_to_id: dict[int, str] = {}
        semantic_names = {"h2", "h3", "h4", "div", "details", "figure"}
        for position, (left, right) in enumerate(zip(left_tags, right_tags, strict=True), start=1):
            qualifies = right.name in semantic_names and (
                right.name != "div" or "unit" in (right.get("class") or [])
            )
            if not qualifies:
                continue
            semantic_indexes[right.name] += 1
            source_local_id = str(right.get("id", "")) or None
            suffix = source_local_id or f"{right.name}-{semantic_indexes[right.name]:03d}"
            stable_id = f"{page_id}.{suffix}"
            parent_id = page_id
            parent = right.find_parent("div", class_="unit")
            if parent is not None and id(parent) in semantic_target_to_id:
                parent_id = semantic_target_to_id[id(parent)]
            semantic_target_to_id[id(right)] = stable_id
            classes = right.get("class") or []
            kind = (
                "details"
                if right.name == "details"
                else "figure"
                if right.name == "figure"
                else "heading"
                if right.name.startswith("h")
                else "definition"
                if right.select_one(":scope > p.dfn")
                else "mathematical_unit"
            )
            entities.append(
                record(
                    "unit",
                    stable_id,
                    parent_id=parent_id,
                    order=position,
                    path=rel,
                    resource_id="resource.random.kyle-siegrist",
                    edition_id="edition.random.snapshot.2026-03-13",
                    source_local_id=source_local_id,
                    source_locator=f"#{source_local_id}" if source_local_id else f"dom-order:{position}",
                    source_sha256=sha256(str(left).encode("utf-8")),
                    target_sha256=sha256(str(right).encode("utf-8")),
                    locale="id-ID",
                    translation_state="structurally_verified",
                    relationship="translates",
                    rights_id="rights.random.dual-witness",
                    payload={"unit_kind": kind, "classes": list(classes), "body_extent": "complete-dom-node"},
                )
            )
            relations.append(
                relation(
                    f"rel.contains.{parent_id}.{stable_id}",
                    "contains",
                    parent_id,
                    stable_id,
                    f"{rel}:dom-order:{position}",
                )
            )
        segment_names = {"h2", "h3", "h4", "p", "li", "figcaption", "summary", "q", "button"}
        segment_order = 0
        for position, (left, right) in enumerate(zip(left_tags, right_tags, strict=True), start=1):
            if right.name not in segment_names:
                continue
            source_text = " ".join(left.stripped_strings)
            target_text = " ".join(right.stripped_strings)
            if not source_text and not target_text:
                continue
            segment_order += 1
            parent_id = page_id
            ancestor = right.find_parent(["div", "details", "figure"])
            while ancestor is not None:
                if id(ancestor) in semantic_target_to_id:
                    parent_id = semantic_target_to_id[id(ancestor)]
                    break
                ancestor = ancestor.find_parent(["div", "details", "figure"])
            segments.append(
                record(
                    "segment",
                    f"segment.o009.random.{slug}.{segment_order:04d}",
                    parent_id=parent_id,
                    order=segment_order,
                    path=rel,
                    resource_id="resource.random.kyle-siegrist",
                    edition_id="edition.random.snapshot.2026-03-13",
                    source_locator=f"dom-order:{position}",
                    source_sha256=sha256(source_text.encode("utf-8")),
                    target_sha256=sha256(target_text.encode("utf-8")),
                    locale="id-ID",
                    translation_state="structurally_verified",
                    relationship="translates",
                    rights_id="rights.random.dual-witness",
                    payload={"source_text": source_text, "target_text": target_text, "tag": right.name},
                )
            )
    kernels_note = tuple(build_module.KERNELS_READER_NOTES)
    if len(kernels_note) != 1:
        raise RuntimeError("expected exactly one original Kernels reader note")
    note = kernels_note[0]
    note_html = str(note["html"])
    note_soup = BeautifulSoup(note_html, "lxml")
    note_text = " ".join(note_soup.stripped_strings)
    note_id = str(note["id"])
    note_record_id = "segment.o009.original.expect.kernels.regular-conditional-note"
    kernels_page_id = "unit.o009.random.expect.kernels"
    segments.append(
        record(
            "segment",
            note_record_id,
            parent_id=kernels_page_id,
            order=10000,
            path="expect/Kernels.html",
            source_local_id=note_id,
            source_locator=f"scripts/build_first_boundary.py#{note_id}",
            source_sha256=sha256(note_html.encode("utf-8")),
            target_sha256=sha256(note_text.encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id="rights.o009.original.cc-by-4.0",
            concept_ids=["concept.conditional.regular-distribution"],
            payload={
                "target_text": note_text,
                "tag": "aside",
                "built_id": note_id,
                "body_extent": "complete-build-addition",
            },
        )
    )
    relations.append(
        relation(
            "rel.contains.unit.o009.random.expect.kernels.regular-conditional-note",
            "contains",
            kernels_page_id,
            note_record_id,
            f"build/site/expect/Kernels.html#{note_id}",
        )
    )
    relations.append(
        relation(
            "rel.depends-on.unit.o009.random.martingales.introduction.fig1.asset.random.martingale-harness",
            "depends-on",
            "unit.o009.random.martingales.introduction.fig1",
            "asset.random.martingale-harness",
            "martingales/Introduction.html#fig1",
        )
    )
    for suffix, asset_id, evidence in (
        (
            "convex-function",
            "asset.random.martingales.convex-function",
            "martingales/Properties.html#fig2",
        ),
        (
            "powers",
            "asset.random.martingales.powers",
            "martingales/Properties.html",
        ),
        (
            "positive-part",
            "asset.random.martingales.positive-part",
            "martingales/Properties.html#fig3",
        ),
    ):
        relations.append(
            relation(
                f"rel.depends-on.unit.o009.random.martingales.properties.{suffix}",
                "depends-on",
                "unit.o009.random.martingales.properties",
                asset_id,
                evidence,
            )
        )
    for left, right in zip(page_ids, page_ids[1:]):
        relations.append(
            relation(
                f"rel.precedes.{left}.{right}",
                "precedes",
                left,
                right,
                "reader source order",
            )
        )
    relations.extend(
        [
            relation(
                "rel.depends-on.martingales-stop.prob-stop",
                "depends-on",
                "unit.o009.random.martingales.stop",
                "unit.o009.random.prob.stop",
                "martingales/Stop.html recalls filtration, stopping-time, and stopped-process definitions",
            ),
            relation(
                "rel.depends-on.martingales-stop.martingales-properties",
                "depends-on",
                "unit.o009.random.martingales.stop",
                "unit.o009.random.martingales.properties",
                "martingales/Stop.html uses martingale transforms and earlier martingale properties",
            ),
            relation(
                "rel.teaches.martingales-stop.optional-stopping",
                "teaches",
                "unit.o009.random.martingales.stop.ost1",
                "outcome.o009.check-optional-stopping-conditions",
                "martingales/Stop.html#ost1; #dis1; #dis2",
            ),
            relation(
                "rel.teaches.martingales-stop.stopped-martingale",
                "teaches",
                "unit.o009.random.martingales.stop.stp2",
                "outcome.o009.prove-stopped-martingale",
                "martingales/Stop.html#stp2",
            ),
            relation(
                "rel.teaches.martingales-stop.wald",
                "teaches",
                "unit.o009.random.martingales.stop.wld1",
                "outcome.o009.compute-random-time-expectations",
                "martingales/Stop.html#wld1",
            ),
            relation(
                "rel.teaches.martingales-stop.pattern-waiting",
                "teaches",
                "unit.o009.random.martingales.stop.pat2",
                "outcome.o009.compute-random-time-expectations",
                "martingales/Stop.html#pat2",
            ),
            relation(
                "rel.assesses.martingales-stop.pattern-waiting",
                "assesses",
                "unit.o009.random.martingales.stop.pat3",
                "outcome.o009.compute-random-time-expectations",
                "martingales/Stop.html#pat3; analogous exercises #pat6 through #pat8",
            ),
            relation(
                "rel.teaches.martingales-stop.optimal-stopping",
                "teaches",
                "unit.o009.random.martingales.stop.sec2",
                "outcome.o009.analyze-optimal-stopping",
                "martingales/Stop.html#sec2",
            ),
            relation(
                "rel.depends-on.martingales-inequalities.martingales-properties",
                "depends-on",
                "unit.o009.random.martingales.inequalities",
                "unit.o009.random.martingales.properties",
                "martingales/Inequalities.html uses convex transforms and predictable martingale transforms",
            ),
            relation(
                "rel.depends-on.martingales-inequalities.martingales-stop",
                "depends-on",
                "unit.o009.random.martingales.inequalities",
                "unit.o009.random.martingales.stop",
                "martingales/Inequalities.html uses stopping times and optional stopping",
            ),
            relation(
                "rel.depends-on.martingales-inequalities.prob-convergence",
                "depends-on",
                "unit.o009.random.martingales.inequalities",
                "unit.o009.random.prob.convergence",
                "martingales/Inequalities.html uses continuity of probability and prepares pathwise convergence",
            ),
            relation(
                "rel.teaches.martingales-inequalities.doob-maximal",
                "teaches",
                "unit.o009.random.martingales.inequalities.max3",
                "outcome.o009.apply-martingale-maximal-inequalities",
                "martingales/Inequalities.html#max3; #max5; #max6; #max7",
            ),
            relation(
                "rel.teaches.martingales-inequalities.upcrossing",
                "teaches",
                "unit.o009.random.martingales.inequalities.upc4",
                "outcome.o009.use-upcrossings-for-convergence",
                "martingales/Inequalities.html#upc1 through #upc8",
            ),
            relation(
                "rel.teaches.martingales-inequalities.kolmogorov",
                "teaches",
                "unit.o009.random.martingales.inequalities",
                "outcome.o009.apply-martingale-maximal-inequalities",
                "martingales/Inequalities.html Kolmogorov inequality application",
            ),
            relation(
                "rel.depends-on.martingales-inequalities.kolmogorov.o006-sampling",
                "depends-on",
                "unit.o009.random.martingales.inequalities.div-016",
                "resource.o006.c140.shared",
                "Kolmogorov's inequality is used here as an application; O006 owns the sampling and independent-sum prerequisite surface",
            ),
            relation(
                "rel.teaches.martingales-inequalities.red-black",
                "teaches",
                "unit.o009.random.martingales.inequalities.red1",
                "outcome.o009.audit-gambling-maximal-bound",
                "martingales/Inequalities.html#red1",
            ),
            relation(
                "rel.depends-on.martingales-convergence.inequalities",
                "depends-on",
                "unit.o009.random.martingales.convergence",
                "unit.o009.random.martingales.inequalities",
                "martingales/Convergence.html uses the upcrossing and Lp maximal inequalities",
            ),
            relation(
                "rel.depends-on.martingales-convergence.uniform-integrability",
                "depends-on",
                "unit.o009.random.martingales.convergence",
                "unit.o009.random.expect.uniform",
                "martingales/Convergence.html uses uniform integrability and mean-convergence results",
            ),
            relation(
                "rel.depends-on.martingales-convergence.probability-convergence",
                "depends-on",
                "unit.o009.random.martingales.convergence",
                "unit.o009.random.prob.convergence",
                "martingales/Convergence.html uses almost-sure convergence and measurability of limits",
            ),
            relation(
                "rel.depends-on.martingales-convergence.introduction",
                "depends-on",
                "unit.o009.random.martingales.convergence",
                "unit.o009.random.martingales.introduction",
                "the application sequence continues the martingale constructions introduced earlier",
            ),
            relation(
                "rel.teaches.martingales-convergence.ae",
                "teaches",
                "unit.o009.random.martingales.convergence.mct1",
                "outcome.o009.prove-martingale-convergence",
                "martingales/Convergence.html#mct1 and #mct2",
            ),
            relation(
                "rel.teaches.martingales-convergence.ui",
                "teaches",
                "unit.o009.random.martingales.convergence.mct3",
                "outcome.o009.characterize-ui-martingales",
                "martingales/Convergence.html#mct3",
            ),
            relation(
                "rel.teaches.martingales-convergence.lp",
                "teaches",
                "unit.o009.random.martingales.convergence.mct4",
                "outcome.o009.apply-lp-martingale-convergence",
                "martingales/Convergence.html#mct4",
            ),
            relation(
                "rel.teaches.martingales-convergence.applications",
                "teaches",
                "unit.o009.random.martingales.convergence",
                "outcome.o009.analyze-martingale-limit-applications",
                "martingales/Convergence.html application sequence from random walk through partial products",
            ),
            relation(
                "rel.depends-on.martingales-convergence.likelihood.o006-lln",
                "depends-on",
                "unit.o009.random.martingales.convergence.lrt1",
                "resource.o006.c140.shared",
                "the likelihood-ratio limit uses the strong law; O006 owns the Random sampling/LLN source surface",
            ),
            relation(
                "rel.depends-on.martingales-convergence.urn.o006-lln",
                "depends-on",
                "unit.o009.random.martingales.convergence.urn1",
                "resource.o006.c140.shared",
                "the no-reinforcement comparison invokes the law of large numbers; O006 owns that Random sampling source surface",
            ),
            relation(
                "rel.teaches.martingales-convergence.density",
                "teaches",
                "unit.o009.random.martingales.convergence.den2",
                "outcome.o009.recover-density-martingale-limits",
                "martingales/Convergence.html#den1 and #den2",
            ),
        ]
    )
    return entities, segments, relations


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    content_start: int
    content_end: int
    classes: tuple[str, ...] = ()


def line_number(text: str, offset: int, base: int = 1) -> int:
    return base + text.count("\n", 0, offset)


def fenced_div_spans(text: str) -> dict[str, Span]:
    opening = re.compile(r"^:::\s+\{#([A-Za-z0-9_.-]+)([^}]*)\}\s*(?:\r?\n|$)")
    closing = re.compile(r"^:::\s*(?:\r?\n|$)")
    stack: list[tuple[str, int, int, tuple[str, ...]]] = []
    result: dict[str, Span] = {}
    for match in re.finditer(r"^.*(?:\r?\n|$)", text, re.MULTILINE):
        raw = match.group(0)
        opened = opening.fullmatch(raw)
        if opened:
            stable_id = opened.group(1)
            classes = tuple(re.findall(r"\.([A-Za-z0-9_.-]+)", opened.group(2)))
            stack.append((stable_id, match.start(), match.end(), classes))
            continue
        if closing.fullmatch(raw):
            if not stack:
                raise RuntimeError(f"unmatched fenced-div close at line {line_number(text, match.start())}")
            stable_id, start, content_start, classes = stack.pop()
            if stable_id in result:
                raise RuntimeError(f"duplicate fenced-div id: {stable_id}")
            result[stable_id] = Span(start, match.end(), content_start, match.start(), classes)
    if stack:
        raise RuntimeError(f"unclosed fenced divs: {[item[0] for item in stack]}")
    return result


def heading_spans(text: str, outer: Span) -> dict[str, Span]:
    header_re = re.compile(
        r"^(#{2,6})\s+.*?\{#([A-Za-z0-9_.-]+)([^}]*)\}\s*(?:\r?\n|$)", re.MULTILINE
    )
    headers = list(header_re.finditer(text, outer.content_start, outer.content_end))
    result: dict[str, Span] = {}
    for index, match in enumerate(headers):
        level = len(match.group(1))
        end = outer.content_end
        for following in headers[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        result[match.group(2)] = Span(
            match.start(),
            end,
            match.end(),
            end,
            tuple(re.findall(r"\.([A-Za-z0-9_.-]+)", match.group(3))),
        )
    return result


def r_chunk_spans(text: str) -> list[tuple[str | None, Span]]:
    result: list[tuple[str | None, Span]] = []
    chunk_re = re.compile(
        r"^```\{r(?:\s+([A-Za-z0-9_.-]+))?[^}]*\}\s*(?:\r?\n)(.*?)^```\s*(?:\r?\n|$)",
        re.MULTILINE | re.DOTALL,
    )
    for match in chunk_re.finditer(text):
        result.append((match.group(1), Span(match.start(), match.end(), match.start(2), match.end(2))))
    return result


def donor_components() -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    whole_text = require_file(ZIT_SIMULATION).decode("utf-8")
    lines = whole_text.splitlines()
    donor_slice = "\n".join(lines[757:832]) + "\n"
    expected_slice_hash = "e95fec79fc93f1239951864901c570b8aaa44e77c6a02be64d48bda4aa5c265f"
    if sha256(donor_slice.encode("utf-8")) != expected_slice_hash:
        raise RuntimeError("Žitković donor slice L758-L832 changed")
    blocks: list[tuple[tuple[str, ...], Span]] = []
    stack: list[tuple[tuple[str, ...], int, int]] = []
    for match in re.finditer(r"^.*(?:\n|$)", donor_slice, re.MULTILINE):
        raw = match.group(0)
        opened = re.fullmatch(r"^:::\s+\{([^}]*)\}\s*(?:\n|$)", raw)
        if opened:
            classes = tuple(re.findall(r"\.([A-Za-z0-9_.-]+)", opened.group(1)))
            stack.append((classes, match.start(), match.end()))
        elif re.fullmatch(r"^:::\s*(?:\n|$)", raw):
            if not stack:
                raise RuntimeError("unmatched donor fenced-div close")
            classes, start, content_start = stack.pop()
            blocks.append((classes, Span(start, match.end(), content_start, match.start(), classes)))
    exercise_span = next(span for classes, span in blocks if "exercise" in classes)
    solution_span = next(span for classes, span in blocks if "solution" in classes)
    chunks = [span for _, span in r_chunk_spans(donor_slice[solution_span.content_start : solution_span.content_end])]
    if len(chunks) != 3:
        raise RuntimeError(f"expected three donor Monte Carlo R chunks, found {len(chunks)}")
    # Convert chunk offsets from the solution substring to donor-slice offsets.
    chunks = [
        Span(
            solution_span.content_start + span.start,
            solution_span.content_start + span.end,
            solution_span.content_start + span.content_start,
            solution_span.content_start + span.content_end,
        )
        for span in chunks
    ]
    entities: list[dict[str, Any]] = []
    aliases: list[dict[str, str]] = []
    hashes: dict[str, str] = {}

    def add_donor(stable_id: str, kind: str, span: Span, parent_id: str | None, order: int) -> None:
        body = donor_slice[span.start : span.end]
        locator = f"source/02-simulation.Rmd#L{line_number(donor_slice, span.start, 758)}-L{line_number(donor_slice, span.end - 1, 758)}"
        digest = sha256(body.encode("utf-8"))
        hashes[stable_id] = digest
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=parent_id,
                order=order,
                path=relative(ZIT_SIMULATION),
                resource_id="resource.zitkovic.stochastic-book",
                edition_id="edition.zitkovic.e2b35ad9",
                source_local_id=locator,
                source_locator=locator,
                source_sha256=digest,
                target_sha256=digest,
                translation_state="source_frozen",
                relationship="copies",
                rights_id="rights.zitkovic.donor.cc0-1.0",
                concept_ids=["concept.monte-carlo"],
                payload={"unit_kind": kind, "body_extent": "complete", "source_language": "en"},
            )
        )
        aliases.append(
            {
                "alias_id": f"alias.{stable_id}",
                "namespace": "zitkovic-source-locator",
                "alias": locator,
                "canonical_id": stable_id,
                "evidence": f"sha256:{digest}",
                "status": "active",
            }
        )

    exercise_id = "unit.donor.zitkovic.monte-carlo-exp.exercise"
    solution_id = "unit.donor.zitkovic.monte-carlo-exp.solution"
    add_donor(exercise_id, "exercise", exercise_span, None, 1)
    add_donor(solution_id, "solution", None if False else solution_span, None, 2)
    program_ids: list[str] = []
    for index, span in enumerate(chunks, start=1):
        program_id = f"unit.donor.zitkovic.monte-carlo-exp.program.{index}"
        program_ids.append(program_id)
        add_donor(program_id, "program", span, solution_id, index)
    relations = [
        relation(
            "rel.solves.donor.zitkovic.monte-carlo-exp",
            "solves",
            solution_id,
            exercise_id,
            "Žitković source/02-simulation.Rmd donor solution block",
        )
    ]
    for index, program_id in enumerate(program_ids, start=1):
        relations.append(
            relation(
                f"rel.contains.donor.solution.program.{index}",
                "contains",
                solution_id,
                program_id,
                f"R chunk {index} inside complete donor solution block",
            )
        )
    return entities, relations, aliases, hashes


def lab_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    data = require_file(LAB)
    text = data.decode("utf-8")
    blocks = fenced_div_spans(text)
    lab_id = "o009-lab-convergence-mc"
    if lab_id not in blocks:
        raise RuntimeError("lab root block is missing")
    headings = heading_spans(text, blocks[lab_id])
    chunks = {name: span for name, span in r_chunk_spans(text) if name}
    if "o009_lab_convergence_mc" not in chunks:
        raise RuntimeError("named target R chunk is missing")
    donor, donor_relations, aliases, donor_hashes = donor_components()
    entities = list(donor)
    relations = list(donor_relations)
    translations: list[dict[str, str]] = []
    corrections: list[dict[str, str]] = []
    lab_path = "labs/01-konvergensi-monte-carlo.Rmd"

    def span_hash(span: Span) -> str:
        return sha256(text[span.start : span.end].encode("utf-8"))

    def add_target(
        stable_id: str,
        span: Span,
        *,
        parent_id: str,
        order: int,
        kind: str,
        original: bool,
        source_id: str | None = None,
        source_hash: str | None = None,
        concepts: list[str] | None = None,
        target_local_id: str | None = "use-stable-id",
        alias_namespace: str = "o009-source-id",
        alias_value: str | None = None,
        alias_evidence: str | None = None,
    ) -> None:
        target_hash = span_hash(span)
        relationship = "authored" if original else "adapts"
        rights_id = (
            "rights.o009.original.cc-by-4.0"
            if original
            else "rights.o009.indonesian-adaptation.cc-by-4.0"
        )
        payload: dict[str, Any] = {
            "unit_kind": kind,
            "body_extent": "complete",
            "line_start": line_number(text, span.start),
            "line_end": line_number(text, span.end - 1),
        }
        if not original:
            payload["component_rights_ids"] = [
                "rights.zitkovic.donor.cc0-1.0",
                "rights.o009.indonesian-adaptation.cc-by-4.0",
            ]
            payload["donor_component_id"] = source_id
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=parent_id,
                order=order,
                path=lab_path,
                resource_id="resource.zitkovic.stochastic-book" if not original else None,
                edition_id="edition.zitkovic.e2b35ad9" if not original else None,
                source_local_id=(stable_id if target_local_id == "use-stable-id" else target_local_id),
                source_locator=(
                    entities_by_id(donor).get(source_id, {}).get("source_locator")
                    if source_id
                    else f"#{stable_id}"
                ),
                source_sha256=source_hash,
                target_sha256=target_hash,
                locale="id-ID",
                translation_state="authored" if original else "translated",
                relationship=relationship,
                rights_id=rights_id,
                concept_ids=concepts or ["concept.probability.convergence-in-probability"],
                payload=payload,
            )
        )
        aliases.append(
            {
                "alias_id": f"alias.target.{stable_id}",
                "namespace": alias_namespace,
                "alias": alias_value or stable_id,
                "canonical_id": stable_id,
                "evidence": alias_evidence or f"{lab_path}#{stable_id}",
                "status": "active",
            }
        )
        relations.append(
            relation(
                f"rel.contains.{parent_id}.{stable_id}",
                "contains",
                parent_id,
                stable_id,
                f"{lab_path}:L{line_number(text, span.start)}-L{line_number(text, span.end - 1)}",
            )
        )
        if source_id:
            translation_id = f"translation.{stable_id}"
            translations.append(
                {
                    "translation_id": translation_id,
                    "source_id": source_id,
                    "target_id": stable_id,
                    "relationship": "adapts",
                    "source_sha256": source_hash or "",
                    "target_sha256": target_hash,
                    "source_rights_id": "rights.zitkovic.donor.cc0-1.0",
                    "target_rights_id": "rights.o009.indonesian-adaptation.cc-by-4.0",
                    "locale": "id-ID",
                    "state": "verified",
                }
            )
            relations.append(
                relation(
                    f"rel.translates.{stable_id}.{source_id}",
                    "translates",
                    stable_id,
                    source_id,
                    translation_id,
                )
            )

    root_span = blocks[lab_id]
    entities.append(
        record(
            "unit",
            lab_id,
            parent_id="course.o009.d30",
            order=2,
            path=lab_path,
            resource_id="resource.zitkovic.stochastic-book",
            edition_id="edition.zitkovic.e2b35ad9",
            source_local_id=lab_id,
            source_locator="source/02-simulation.Rmd#L758-L832",
            source_sha256="e95fec79fc93f1239951864901c570b8aaa44e77c6a02be64d48bda4aa5c265f",
            target_sha256=span_hash(root_span),
            locale="id-ID",
            translation_state="translated",
            relationship="adapts",
            rights_id="rights.o009.indonesian-adaptation.cc-by-4.0",
            concept_ids=["concept.monte-carlo", "concept.probability.convergence-in-probability"],
            payload={
                "unit_kind": "lab",
                "runtime": "R-4.6.1/base",
                "body_extent": "complete",
                "component_rights_ids": [
                    "rights.zitkovic.donor.cc0-1.0",
                    "rights.o009.indonesian-adaptation.cc-by-4.0",
                ],
            },
        )
    )
    aliases.append(
        {
            "alias_id": "alias.target.o009-lab-convergence-mc",
            "namespace": "o009-source-id",
            "alias": lab_id,
            "canonical_id": lab_id,
            "evidence": f"{lab_path}#{lab_id}",
            "status": "active",
        }
    )
    experiment_id = "o009-lab-convergence-mc-experiment"
    concept_id = "o009-concept-monte-carlo-lln"
    mastery_id = "o009-mastery-convergence-mc"
    add_target(
        experiment_id,
        headings[experiment_id],
        parent_id=lab_id,
        order=1,
        kind="section",
        original=False,
        concepts=["concept.monte-carlo"],
    )
    target_exercise = "o009-exercise-convergence-mc-estimation"
    donor_exercise = "unit.donor.zitkovic.monte-carlo-exp.exercise"
    add_target(
        target_exercise,
        blocks[target_exercise],
        parent_id=experiment_id,
        order=1,
        kind="exercise",
        original=False,
        source_id=donor_exercise,
        source_hash=donor_hashes[donor_exercise],
        concepts=["concept.monte-carlo"],
    )
    # The adapted source has no explicit solution fence. Its complete solution is the
    # contiguous body after the exercise and before the next H2.
    solution_span = Span(
        blocks[target_exercise].end,
        headings[concept_id].start,
        blocks[target_exercise].end,
        headings[concept_id].start,
    )
    target_solution = "o009-solution-convergence-mc-estimation"
    donor_solution = "unit.donor.zitkovic.monte-carlo-exp.solution"
    add_target(
        target_solution,
        solution_span,
        parent_id=experiment_id,
        order=2,
        kind="solution",
        original=False,
        source_id=donor_solution,
        source_hash=donor_hashes[donor_solution],
        concepts=["concept.monte-carlo"],
        target_local_id=None,
        alias_namespace="backend-derived-id",
        alias_evidence=(
            f"{lab_path}:L{line_number(text, solution_span.start)}-"
            f"L{line_number(text, solution_span.end - 1)}"
        ),
    )
    target_program = "o009-program-convergence-mc"
    program_span = chunks["o009_lab_convergence_mc"]
    add_target(
        target_program,
        program_span,
        parent_id=target_solution,
        order=1,
        kind="program",
        original=False,
        source_id="unit.donor.zitkovic.monte-carlo-exp.program.1",
        source_hash=donor_hashes["unit.donor.zitkovic.monte-carlo-exp.program.1"],
        concepts=["concept.monte-carlo"],
        target_local_id="o009_lab_convergence_mc",
        alias_namespace="r-chunk-label",
        alias_value="o009_lab_convergence_mc",
        alias_evidence=f"{lab_path}:chunk:o009_lab_convergence_mc",
    )
    # One target program merges and extends all three donor chunks.
    for index in (2, 3):
        source_id = f"unit.donor.zitkovic.monte-carlo-exp.program.{index}"
        relations.append(
            relation(
                f"rel.translates.{target_program}.{source_id}",
                "translates",
                target_program,
                source_id,
                f"translation.{target_program}.donor-{index}",
            )
        )
        translations.append(
            {
                "translation_id": f"translation.{target_program}.donor-{index}",
                "source_id": source_id,
                "target_id": target_program,
                "relationship": "adapts",
                "source_sha256": donor_hashes[source_id],
                "target_sha256": span_hash(program_span),
                "source_rights_id": "rights.zitkovic.donor.cc0-1.0",
                "target_rights_id": "rights.o009.indonesian-adaptation.cc-by-4.0",
                "locale": "id-ID",
                "state": "verified",
            }
        )
    relations.append(
        relation(
            "rel.solves.target.convergence-mc-estimation",
            "solves",
            target_solution,
            target_exercise,
            "complete adapted solution body",
        )
    )
    add_target(
        concept_id,
        headings[concept_id],
        parent_id=lab_id,
        order=2,
        kind="concept-section",
        original=False,
        concepts=["concept.monte-carlo"],
    )
    add_target(
        mastery_id,
        headings[mastery_id],
        parent_id=lab_id,
        order=3,
        kind="original-addition",
        original=True,
        concepts=["concept.probability.convergence-in-probability"],
    )
    nested_original = [
        ("o009-exercise-convergence-mc-mastery", "exercise"),
        ("o009-hint-convergence-mc-mastery-1", "hint"),
        ("o009-hint-convergence-mc-mastery-2", "hint"),
        ("o009-hint-convergence-mc-mastery-3", "hint"),
        ("o009-answer-convergence-mc-mastery", "answer"),
        ("o009-solution-convergence-mc-mastery", "solution"),
    ]
    for order, (stable_id, kind) in enumerate(nested_original, start=1):
        add_target(
            stable_id,
            blocks[stable_id],
            parent_id=mastery_id,
            order=order,
            kind=kind,
            original=True,
            concepts=["concept.probability.convergence-in-probability"],
        )
    relations.extend(
        [
            relation(
                "rel.depends.lab-convergence-mc.theory-convergence",
                "depends-on",
                lab_id,
                "unit.o009.random.prob.convergence",
                "matched_theory_id in Rmd metadata",
            ),
            relation(
                "rel.prerequisite.o009.o006",
                "prerequisite",
                "course.o009.d30",
                "resource.o006.c140.shared",
                "cross-lane ownership boundary; O006 prerequisite retained",
            ),
            relation("rel.hints.mastery.1", "hints", "o009-hint-convergence-mc-mastery-1", "o009-exercise-convergence-mc-mastery", "explicit mastery sequence"),
            relation("rel.hints.mastery.2", "hints", "o009-hint-convergence-mc-mastery-2", "o009-exercise-convergence-mc-mastery", "explicit mastery sequence"),
            relation("rel.hints.mastery.3", "hints", "o009-hint-convergence-mc-mastery-3", "o009-exercise-convergence-mc-mastery", "explicit mastery sequence"),
            relation("rel.answers.mastery", "answers", "o009-answer-convergence-mc-mastery", "o009-exercise-convergence-mc-mastery", "explicit mastery sequence"),
            relation("rel.solves.mastery", "solves", "o009-solution-convergence-mc-mastery", "o009-exercise-convergence-mc-mastery", "explicit mastery sequence"),
            relation("rel.teaches.experiment.estimate", "teaches", experiment_id, "outcome.o009.estimate-expectation-monte-carlo", "Monte Carlo experiment section"),
            relation("rel.teaches.concept.lln", "teaches", concept_id, "outcome.o009.explain-lln-monte-carlo", "mathematical meaning section"),
            relation("rel.teaches.mastery.evidence", "teaches", mastery_id, "outcome.o009.distinguish-evidence-proof", "original mastery section"),
            relation("rel.teaches.mastery.proof", "teaches", mastery_id, "outcome.o009.prove-convergence-in-probability", "original mastery section"),
            relation("rel.assesses.estimation", "assesses", target_exercise, "outcome.o009.estimate-expectation-monte-carlo", "estimation exercise prompt"),
            relation("rel.assesses.mastery.evidence", "assesses", "o009-exercise-convergence-mc-mastery", "outcome.o009.distinguish-evidence-proof", "mastery item 3"),
            relation("rel.assesses.mastery.proof", "assesses", "o009-exercise-convergence-mc-mastery", "outcome.o009.prove-convergence-in-probability", "mastery items 2-3"),
            relation("rel.precedes.theory.lab", "precedes", "unit.o009.random.prob.convergence", lab_id, "theory-to-lab learning sequence"),
            relation("rel.precedes.experiment.concept", "precedes", experiment_id, concept_id, "lab document order"),
            relation("rel.precedes.concept.mastery", "precedes", concept_id, mastery_id, "lab document order"),
        ]
    )
    corrections.extend(
        [
            {
                "correction_id": "correction.o009.program.deterministic-output",
                "change_kind": "deterministic-output",
                "source_id": donor_solution,
                "target_id": target_program,
                "description": "Preserve donor seeds, retain signed error, and emit a canonical CSV result table.",
                "evidence": "source/labs/01-konvergensi-monte-carlo.Rmd#o009_lab_convergence_mc",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.mastery.original-addition",
                "change_kind": "original-addition",
                "source_id": lab_id,
                "target_id": mastery_id,
                "description": "Add a separately licensed mastery sequence connecting simulation to convergence in probability.",
                "evidence": "source/labs/01-konvergensi-monte-carlo.Rmd#o009-mastery-convergence-mc",
                "status": "accepted",
            },
        ]
    )

    # Paragraph-level segments inherit the actual target-component license.
    segments: list[dict[str, Any]] = []
    body = text[root_span.content_start : root_span.content_end]
    body_without_code = re.sub(r"^```.*?^```\s*$", "", body, flags=re.MULTILINE | re.DOTALL)
    original_offset = text.index("## Tambahan asli")
    for order, match in enumerate(re.finditer(r"(?:^|\n\s*\n)(.+?)(?=\n\s*\n|\Z)", body_without_code, re.DOTALL), start=1):
        paragraph = match.group(1).strip()
        if not paragraph or paragraph.startswith(":::"):
            continue
        global_offset = root_span.content_start + body.find(paragraph)
        original = global_offset >= original_offset or "Tambahan asli" in paragraph
        segments.append(
            record(
                "segment",
                f"segment.o009.lab.convergence-mc.{len(segments) + 1:04d}",
                parent_id=mastery_id if original else lab_id,
                order=len(segments) + 1,
                path=lab_path,
                source_locator="local-original" if original else "source/02-simulation.Rmd#L758-L832",
                target_sha256=sha256(paragraph.encode("utf-8")),
                locale="id-ID",
                translation_state="authored" if original else "translated",
                relationship="authored" if original else "adapts",
                rights_id=(
                    "rights.o009.original.cc-by-4.0"
                    if original
                    else "rights.o009.indonesian-adaptation.cc-by-4.0"
                ),
                payload={
                    "target_text": paragraph,
                    "component_rights_ids": (
                        ["rights.o009.original.cc-by-4.0"]
                        if original
                        else [
                            "rights.zitkovic.donor.cc0-1.0",
                            "rights.o009.indonesian-adaptation.cc-by-4.0",
                        ]
                    ),
                },
            )
        )
    return entities, segments, relations, aliases, translations, corrections


def entities_by_id(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in records}


def asset_entities() -> list[dict[str, Any]]:
    paths = [
        ("asset.random.screen-css", AUTH_RANDOM / "static" / "Screen.css", "rights.random.dual-witness"),
        ("asset.random.basic-js", AUTH_RANDOM / "static" / "Basic.js", "rights.random.dual-witness"),
        ("asset.random.icon", AUTH_RANDOM / "static" / "icons" / "Icon.svg", "rights.random.dual-witness"),
        ("asset.random.plus", AUTH_RANDOM / "static" / "icons" / "Plus.svg", "rights.random.dual-witness"),
        ("asset.random.minus", AUTH_RANDOM / "static" / "icons" / "Minus.svg", "rights.random.dual-witness"),
        ("asset.random.increasing-1", AUTH_RANDOM / "static" / "prob" / "Increasing1.png", "rights.random.dual-witness"),
        ("asset.random.increasing-2", AUTH_RANDOM / "static" / "prob" / "Increasing2.png", "rights.random.dual-witness"),
        ("asset.random.decreasing", AUTH_RANDOM / "static" / "prob" / "Decreasing.png", "rights.random.dual-witness"),
        ("asset.random.inverse-image", AUTH_RANDOM / "static" / "prob" / "InverseImage.png", "rights.random.dual-witness"),
        ("asset.random.convex-function", AUTH_RANDOM / "static" / "expect" / "ConvexFunction.png", "rights.random.dual-witness"),
        (
            "asset.random.martingale-harness",
            AUTH_RANDOM / "static" / "martingales" / "Martingale.png",
            "rights.random.martingale-image.cc-by-3.0",
        ),
        (
            "asset.random.martingales.convex-function",
            AUTH_RANDOM / "static" / "martingales" / "ConvexFunction.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.martingales.powers",
            AUTH_RANDOM / "static" / "martingales" / "Powers.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.martingales.positive-part",
            AUTH_RANDOM / "static" / "martingales" / "PositivePart.png",
            "rights.random.dual-witness",
        ),
        ("asset.mathjax.tex-svg", AUTH_RANDOM / "shared" / "MathJax" / "tex-svg.js", "rights.mathjax.apache-2.0"),
        (
            "asset.mathjax.boldsymbol",
            AUTH_RANDOM / "shared" / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js",
            "rights.mathjax.apache-2.0",
        ),
        ("asset.o009.reader-css", ROOT / "source" / "reader.css", "rights.o009.original.cc-by-4.0"),
    ]
    entities: list[dict[str, Any]] = []
    for stable_id, path, rights_id in paths:
        data = require_file(path)
        entities.append(
            record(
                "asset",
                stable_id,
                path=relative(path),
                source_locator=relative(path),
                source_sha256=sha256(data),
                target_sha256=sha256(data),
                relationship="copies",
                rights_id=rights_id,
                payload={"bytes": len(data)},
            )
        )
    return entities


def artifact_rows() -> list[dict[str, str]]:
    paths = [
        ("artifact.exporter.backend", "exporter", EXPORTER),
        ("artifact.input.first-boundary-builder", "input", BUILD_SCRIPT),
        ("artifact.input.terms", "input", TERMS),
        ("artifact.input.random-manifest", "authority-manifest", RANDOM_MANIFEST),
        ("artifact.input.random-receipt", "authority-receipt", RANDOM_RECEIPT),
        ("artifact.input.zitkovic-zip", "authority-archive", ZIT_ZIP),
        ("artifact.input.zitkovic-license", "rights-witness", ZIT_LICENSE),
        ("artifact.input.zitkovic-simulation", "authority-source", ZIT_SIMULATION),
        ("artifact.input.target-lab", "translation-source", LAB),
        (
            "artifact.input.random-martingale-harness",
            "authority-asset",
            AUTH_RANDOM / "static" / "martingales" / "Martingale.png",
        ),
        (
            "artifact.input.random-martingales-convex-function",
            "authority-asset",
            AUTH_RANDOM / "static" / "martingales" / "ConvexFunction.png",
        ),
        (
            "artifact.input.random-martingales-powers",
            "authority-asset",
            AUTH_RANDOM / "static" / "martingales" / "Powers.png",
        ),
        (
            "artifact.input.random-martingales-positive-part",
            "authority-asset",
            AUTH_RANDOM / "static" / "martingales" / "PositivePart.png",
        ),
        ("artifact.input.site-package-manifest", "build-manifest", BUILD_MANIFEST),
        ("artifact.input.site-build-receipt", "build-receipt", BUILD_RECEIPT),
    ]
    for spec in THEORY_SPECS:
        slug = str(spec["slug"]).replace(".", "-")
        rel = Path(str(spec["rel"]))
        paths.extend(
            [
                (f"artifact.input.random-{slug}", "authority-source", AUTH_RANDOM / "static" / rel),
                (f"artifact.input.target-{slug}", "translation-source", ROOT / "source" / "theory" / rel),
            ]
        )
    rows: list[dict[str, str]] = []
    for artifact_id, kind, path in paths:
        data = require_file(path)
        rows.append(
            {
                "artifact_id": artifact_id,
                "artifact_kind": kind,
                "path": relative(path),
                "bytes": str(len(data)),
                "sha256": sha256(data),
                "media_type": (
                    "application/json"
                    if path.suffix == ".json"
                    else "text/csv"
                    if path.suffix == ".csv"
                    else "application/zip"
                    if path.suffix == ".zip"
                    else "image/png"
                    if path.suffix.lower() == ".png"
                    else "text/html"
                    if path.suffix == ".html"
                    else "text/plain"
                ),
                "status": "bound",
            }
        )
    return rows


def qa_rows(artifacts: list[dict[str, str]], records: list[dict[str, Any]], relations: list[dict[str, str]]) -> list[dict[str, str]]:
    receipt = load_json(BUILD_RECEIPT)
    manifest_hash = sha256(require_file(BUILD_MANIFEST))
    receipt_units = {
        str(item.get("path")): item
        for item in receipt.get("theory_units", [])
        if isinstance(item, dict)
    }
    current_unit_hashes = {
        str(spec["rel"]): sha256(require_file(ROOT / "source" / "theory" / Path(str(spec["rel"]))))
        for spec in THEORY_SPECS
    }
    theory_inputs_bound = set(receipt_units) == set(current_unit_hashes) and all(
        receipt_units[path].get("target_sha256") == digest for path, digest in current_unit_hashes.items()
    )
    checks = [
        (
            "qa.o009.theory-structure",
            "structural-translation",
            "artifact.input.first-boundary-builder",
            "pass",
            f"reader validator accepted topology, TeX, ids, and locale for {len(THEORY_SPECS)} theory units",
        ),
        (
            "qa.o009.build-manifest-binding",
            "build-binding",
            "artifact.input.site-build-receipt",
            "pass" if receipt.get("manifest_sha256") == manifest_hash else "fail",
            f"receipt={receipt.get('manifest_sha256')} current={manifest_hash}",
        ),
        (
            "qa.o009.build-theory-input-binding",
            "input-binding",
            "artifact.input.site-build-receipt",
            "pass" if theory_inputs_bound else "fail",
            f"receipt_paths={sorted(receipt_units)} current={current_unit_hashes}",
        ),
        (
            "qa.o009.build-lab-input-binding",
            "input-binding",
            "artifact.input.site-build-receipt",
            "pass" if receipt.get("lab_source_sha256") == sha256(require_file(LAB)) else "fail",
            f"receipt={receipt.get('lab_source_sha256')} current={sha256(require_file(LAB))}",
        ),
        (
            "qa.o009.rights-component-separation",
            "rights-binding",
            "artifact.input.zitkovic-license",
            "pass",
            "donor units use witnessed CC0; Indonesian adaptation units use CC-BY-4.0",
        ),
        (
            "qa.o009.o006-prerequisite",
            "prerequisite-boundary",
            "artifact.exporter.backend",
            "pass" if any(item["relation_id"] == "rel.prerequisite.o009.o006" for item in relations) else "fail",
            "O006/C140 prerequisite relation is present",
        ),
        (
            "qa.o009.graph-completeness",
            "graph-validation",
            "artifact.exporter.backend",
            "pass",
            f"records={len(records)} relations={len(relations)}",
        ),
    ]
    artifact_ids = {item["artifact_id"] for item in artifacts}
    rows = []
    for event_id, event_type, artifact_id, result, detail in checks:
        if artifact_id not in artifact_ids:
            raise RuntimeError(f"QA event references unknown artifact: {artifact_id}")
        rows.append(
            {
                "event_id": event_id,
                "event_type": event_type,
                "artifact_id": artifact_id,
                "result": result,
                "detail": detail,
                "timestamp": STAMP,
                "status": "recorded",
            }
        )
    return rows


CSV_DEFINITIONS: dict[str, dict[str, Any]] = {
    "relations.csv": {
        "fields": ["relation_id", "relation_type", "source_id", "target_id", "evidence", "status"],
        "enums": {"relation_type": sorted(RELATION_TYPES), "status": ["active"]},
        "patterns": {"relation_id": r"^rel\.[A-Za-z0-9._:-]+$"},
    },
    "unit_map.csv": {
        "fields": ["id", "parent_id", "order", "path", "source_local_id", "translation_state", "rights_id"],
        "enums": {"translation_state": sorted(TRANSLATION_STATES)},
        "patterns": {"id": r"^[A-Za-z0-9][A-Za-z0-9._:-]+$", "rights_id": r"^rights\.[A-Za-z0-9._:-]+$"},
    },
    "terms.csv": {
        "fields": ["term_id", "en", "id_ID", "status", "scope", "note"],
        "enums": {"status": ["admitted", "provisional"], "scope": ["course", "lab"]},
        "patterns": {"term_id": r"^O009-T\d{4}$"},
    },
    "artifacts.csv": {
        "fields": ["artifact_id", "artifact_kind", "path", "bytes", "sha256", "media_type", "status"],
        "enums": {
            "artifact_kind": ["exporter", "input", "authority-manifest", "authority-receipt", "authority-source", "authority-asset", "authority-archive", "rights-witness", "translation-source", "build-manifest", "build-receipt"],
            "status": ["bound"],
        },
        "patterns": {"artifact_id": r"^artifact\.[A-Za-z0-9._:-]+$", "bytes": r"^[0-9]+$", "sha256": r"^[0-9a-f]{64}$"},
    },
    "qa_events.csv": {
        "fields": ["event_id", "event_type", "artifact_id", "result", "detail", "timestamp", "status"],
        "enums": {
            "event_type": ["structural-translation", "build-binding", "input-binding", "rights-binding", "prerequisite-boundary", "graph-validation"],
            "result": ["pass", "fail"],
            "status": ["recorded"],
        },
        "patterns": {"event_id": r"^qa\.[A-Za-z0-9._:-]+$", "artifact_id": r"^artifact\.[A-Za-z0-9._:-]+$"},
    },
    "corrections.csv": {
        "fields": ["correction_id", "change_kind", "source_id", "target_id", "description", "evidence", "status"],
        "enums": {
            "change_kind": [
                "deterministic-output",
                "original-addition",
                "source-content-repair",
                "source-link-repair",
            ],
            "status": ["accepted"],
        },
        "patterns": {"correction_id": r"^correction\.[A-Za-z0-9._:-]+$"},
    },
    "translations.csv": {
        "fields": ["translation_id", "source_id", "target_id", "relationship", "source_sha256", "target_sha256", "source_rights_id", "target_rights_id", "locale", "state"],
        "enums": {"relationship": ["adapts", "translates"], "locale": ["id-ID"], "state": ["verified"]},
        "patterns": {"translation_id": r"^translation\.[A-Za-z0-9._:-]+$", "source_sha256": r"^[0-9a-f]{64}$", "target_sha256": r"^[0-9a-f]{64}$"},
    },
    "outcomes.csv": {
        "fields": ["outcome_id", "course_id", "label", "locale", "cognitive_level", "status"],
        "enums": {"locale": ["id-ID"], "cognitive_level": ["understand", "apply", "analyze", "prove"], "status": ["active"]},
        "patterns": {"outcome_id": r"^outcome\.[A-Za-z0-9._:-]+$", "course_id": r"^course\.[A-Za-z0-9._:-]+$"},
    },
    "aliases.csv": {
        "fields": ["alias_id", "namespace", "alias", "canonical_id", "evidence", "status"],
        "enums": {"namespace": ["zitkovic-source-locator", "o009-source-id", "backend-derived-id", "r-chunk-label"], "status": ["active"]},
        "patterns": {"alias_id": r"^alias\.[A-Za-z0-9._:-]+$"},
    },
}


def csv_schema(filename: str, definition: dict[str, Any]) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    for field in definition["fields"]:
        spec: dict[str, Any] = {"type": "string"}
        if field in definition.get("enums", {}):
            spec["enum"] = definition["enums"][field]
        if field in definition.get("patterns", {}):
            spec["pattern"] = definition["patterns"][field]
        properties[field] = spec
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://example.invalid/o009/backend/{filename}.schema.json",
        "title": f"Strict row schema for {filename}",
        "type": "object",
        "additionalProperties": False,
        "required": definition["fields"],
        "properties": properties,
        "x-csv": {"header": definition["fields"], "encoding": "utf-8", "line_ending": "CRLF"},
    }


def entity_schema() -> dict[str, Any]:
    fields = list(record("concept", "concept.example").keys())
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://example.invalid/o009/backend/entity-v2.schema.json",
        "title": "O009 modular backend entity envelope v2",
        "type": "object",
        "additionalProperties": False,
        "required": fields,
        "properties": {
            "schema": {"const": SCHEMA},
            "record_type": {"enum": sorted(RECORD_TYPES)},
            "id": {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9._:-]+$"},
            "source_local_id": {"type": ["string", "null"]},
            "parent_id": {"type": ["string", "null"]},
            "order": {"type": ["integer", "null"], "minimum": 0},
            "path": {"type": ["string", "null"]},
            "resource_id": {"type": ["string", "null"]},
            "edition_id": {"type": ["string", "null"]},
            "source_locator": {"type": ["string", "null"]},
            "source_sha256": {"anyOf": [{"type": "null"}, {"type": "string", "pattern": r"^[0-9a-f]{64}$"}]},
            "target_sha256": {"anyOf": [{"type": "null"}, {"type": "string", "pattern": r"^[0-9a-f]{64}$"}]},
            "locale": {"enum": ["zxx", "id-ID"]},
            "translation_state": {"enum": sorted(TRANSLATION_STATES)},
            "source_target_relationship": {"anyOf": [{"type": "null"}, {"enum": sorted(RELATIONSHIPS)}]},
            "concept_ids": {"type": "array", "uniqueItems": True, "items": {"type": "string", "pattern": r"^concept\."}},
            "rights_id": {"type": ["string", "null"]},
            "status": {"enum": ["active", "external_dependency"]},
            "timestamp": {"const": STAMP},
            "responsible_workflow": {"const": WORKFLOW},
            "supersedes": {"type": ["string", "null"]},
            "payload": {"type": "object"},
        },
    }


def validate_record_envelopes(records: list[dict[str, Any]], relations: list[dict[str, str]]) -> None:
    required = set(record("concept", "concept.example"))
    ids = [item["id"] for item in records]
    if len(ids) != len(set(ids)):
        duplicates = sorted({value for value in ids if ids.count(value) > 1})
        raise RuntimeError(f"duplicate backend ids: {duplicates}")
    known = set(ids)
    for item in records:
        if set(item) != required or item["schema"] != SCHEMA:
            raise RuntimeError(f"invalid backend record envelope: {item.get('id')}")
        if item["record_type"] not in RECORD_TYPES:
            raise RuntimeError(f"unknown record type: {item['record_type']}")
        if not ID_RE.fullmatch(item["id"]):
            raise RuntimeError(f"invalid backend id: {item['id']}")
        if item["translation_state"] not in TRANSLATION_STATES:
            raise RuntimeError(f"unknown translation state: {item['id']}")
        if item["source_target_relationship"] not in RELATIONSHIPS | {None}:
            raise RuntimeError(f"unknown source-target relationship: {item['id']}")
        for key in ("source_sha256", "target_sha256"):
            if item[key] is not None and not HASH_RE.fullmatch(item[key]):
                raise RuntimeError(f"invalid {key}: {item['id']}")
        if item["parent_id"] is not None and item["parent_id"] not in known:
            raise RuntimeError(f"unknown parent_id: {item['id']} -> {item['parent_id']}")
        if item["resource_id"] is not None and item["resource_id"] not in known:
            raise RuntimeError(f"unknown resource_id: {item['id']}")
        if item["edition_id"] is not None and item["edition_id"] not in known:
            raise RuntimeError(f"unknown edition_id: {item['id']}")
        if item["rights_id"] is not None and item["rights_id"] not in known:
            raise RuntimeError(f"unknown rights_id: {item['id']} -> {item['rights_id']}")
        if any(concept_id not in known for concept_id in item["concept_ids"]):
            raise RuntimeError(f"unknown concept id: {item['id']}")
        canonical_json(item).encode("utf-8")
    relation_ids: set[str] = set()
    for item in relations:
        if list(item) != CSV_DEFINITIONS["relations.csv"]["fields"]:
            raise RuntimeError(f"invalid relation fields: {item}")
        if item["relation_id"] in relation_ids:
            raise RuntimeError(f"duplicate relation id: {item['relation_id']}")
        relation_ids.add(item["relation_id"])
        if item["relation_type"] not in RELATION_TYPES:
            raise RuntimeError(f"unknown relation type: {item['relation_type']}")
        if item["source_id"] not in known or item["target_id"] not in known:
            raise RuntimeError(f"relation has unknown endpoint: {item}")
    required_relations = {
        "rel.prerequisite.o009.o006",
        "rel.teaches.experiment.estimate",
        "rel.assesses.estimation",
        "rel.precedes.theory.lab",
        "rel.translates.o009-exercise-convergence-mc-estimation.unit.donor.zitkovic.monte-carlo-exp.exercise",
        "rel.translates.o009-solution-convergence-mc-estimation.unit.donor.zitkovic.monte-carlo-exp.solution",
        "rel.translates.o009-program-convergence-mc.unit.donor.zitkovic.monte-carlo-exp.program.1",
        "rel.translates.o009-program-convergence-mc.unit.donor.zitkovic.monte-carlo-exp.program.2",
        "rel.translates.o009-program-convergence-mc.unit.donor.zitkovic.monte-carlo-exp.program.3",
        "rel.solves.donor.zitkovic.monte-carlo-exp",
        "rel.solves.target.convergence-mc-estimation",
        "rel.contains.donor.solution.program.1",
        "rel.contains.donor.solution.program.2",
        "rel.contains.donor.solution.program.3",
        "rel.contains.o009-solution-convergence-mc-estimation.o009-program-convergence-mc",
        "rel.depends-on.martingales-stop.prob-stop",
        "rel.depends-on.martingales-stop.martingales-properties",
        "rel.teaches.martingales-stop.optional-stopping",
        "rel.teaches.martingales-stop.stopped-martingale",
        "rel.teaches.martingales-stop.wald",
        "rel.teaches.martingales-stop.pattern-waiting",
        "rel.assesses.martingales-stop.pattern-waiting",
        "rel.teaches.martingales-stop.optimal-stopping",
    }
    missing = required_relations - relation_ids
    if missing:
        raise RuntimeError(f"missing required graph relations: {sorted(missing)}")
    for item in records:
        if item["record_type"] in {"unit", "segment"} and item.get("path") == "labs/01-konvergensi-monte-carlo.Rmd":
            if item["source_target_relationship"] == "adapts" and item["rights_id"] != "rights.o009.indonesian-adaptation.cc-by-4.0":
                raise RuntimeError(f"adapted Indonesian bytes mislabeled: {item['id']}")
    donor_units = [item for item in records if item["id"].startswith("unit.donor.zitkovic.")]
    if not donor_units or any(item["rights_id"] != "rights.zitkovic.donor.cc0-1.0" for item in donor_units):
        raise RuntimeError("donor unit rights are not consistently CC0")


def validate_csv_rows(filename: str, rows: list[dict[str, str]]) -> None:
    definition = CSV_DEFINITIONS[filename]
    fields = definition["fields"]
    for row_number, row in enumerate(rows, start=2):
        if list(row) != fields:
            raise RuntimeError(f"{filename}:{row_number}: header/field order differs from schema")
        for field in fields:
            if field not in row or row[field] is None:
                raise RuntimeError(f"{filename}:{row_number}: missing {field}")
            value = row[field]
            allowed = definition.get("enums", {}).get(field)
            if allowed is not None and value not in allowed:
                raise RuntimeError(f"{filename}:{row_number}: {field}={value!r} outside vocabulary")
            pattern = definition.get("patterns", {}).get(field)
            if pattern is not None and not re.fullmatch(pattern, value):
                raise RuntimeError(f"{filename}:{row_number}: invalid {field}={value!r}")


def write_csv(filename: str, rows: list[dict[str, str]]) -> None:
    validate_csv_rows(filename, rows)
    fields = CSV_DEFINITIONS[filename]["fields"]
    with (BACKEND / filename).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build() -> None:
    lab_text = require_file(LAB).decode("utf-8")
    entities = fixed_entities(lab_text)
    html, html_segments, html_relations = html_entities()
    lab, lab_segments, lab_relations, aliases, translations, corrections = lab_entities()
    corrections.append(
        {
            "correction_id": "correction.o009.random.probability-revisited.fragment-tai1",
            "change_kind": "source-link-repair",
            "source_id": "unit.o009.random.prob.probability-revisited",
            "target_id": "unit.o009.random.prob.probability-revisited",
            "description": "Rewrite the upstream broken #tai1 reference to its intended limsup/liminf result #tai12 in the built reader only.",
            "evidence": "authority/random/static/prob/Probability2.html:486; built prob/Probability2.html",
            "status": "accepted",
        }
    )
    build_module = load_build_validator()
    build_units_by_rel = {
        str(unit["rel"]): unit for unit in build_module.THEORY_UNITS
    }
    for spec in THEORY_SPECS:
        rel = str(spec["rel"])
        slug = str(spec["slug"])
        page_id = f"unit.o009.random.{slug}"
        build_unit = build_units_by_rel[rel]
        for correction in tuple(build_unit.get("reader_corrections", ())):
            corrections.append(
                {
                    "correction_id": f"correction.o009.random.{slug}.{correction['id']}",
                    "change_kind": str(
                        correction.get("change_kind", "source-content-repair")
                    ),
                    "source_id": page_id,
                    "target_id": page_id,
                    "description": str(correction["description"]),
                    "evidence": (
                        f"authority/random/static/{rel}; build/site/{rel}; "
                        "00_control/UPSTREAM_FINDINGS.md"
                    ),
                    "status": "accepted",
                }
            )
    kernels_unit = build_units_by_rel["expect/Kernels.html"]
    for note in tuple(kernels_unit.get("reader_notes", ())):
        corrections.append(
            {
                "correction_id": f"correction.o009.original.expect.kernels.{note['id']}",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.expect.kernels",
                "target_id": "segment.o009.original.expect.kernels.regular-conditional-note",
                "description": str(note["description"]),
                "evidence": f"build/site/expect/Kernels.html#{note['id']}",
                "status": "accepted",
            }
        )
    entities.extend(html)
    entities.extend(lab)
    entities.extend(asset_entities())
    segments = html_segments + lab_segments
    relations = html_relations + lab_relations
    all_records = entities + segments
    validate_record_envelopes(all_records, relations)

    BACKEND.mkdir(parents=True, exist_ok=True)
    expected_names = {
        "entities.jsonl",
        "segments.jsonl",
        "relations.csv",
        "unit_map.csv",
        "terms.csv",
        "artifacts.csv",
        "qa_events.csv",
        "corrections.csv",
        "translations.csv",
        "outcomes.csv",
        "aliases.csv",
        "entity.schema.json",
        *(f"{name}.schema.json" for name in CSV_DEFINITIONS),
        "BACKEND_MANIFEST.json",
    }
    for existing in BACKEND.iterdir():
        if existing.is_file() and existing.name not in expected_names:
            raise RuntimeError(f"unexpected backend file; refusing to overwrite/delete: {existing.name}")

    (BACKEND / "entities.jsonl").write_text(
        "".join(canonical_json(item) + "\n" for item in sorted(entities, key=lambda item: item["id"])),
        encoding="utf-8",
        newline="\n",
    )
    (BACKEND / "segments.jsonl").write_text(
        "".join(canonical_json(item) + "\n" for item in sorted(segments, key=lambda item: item["id"])),
        encoding="utf-8",
        newline="\n",
    )
    write_csv("relations.csv", sorted(relations, key=lambda item: item["relation_id"]))
    unit_rows = [item for item in entities if item["record_type"] == "unit"]
    unit_fields = CSV_DEFINITIONS["unit_map.csv"]["fields"]
    write_csv(
        "unit_map.csv",
        [
            {field: "" if item[field] is None else str(item[field]) for field in unit_fields}
            for item in sorted(unit_rows, key=lambda value: value["id"])
        ],
    )
    shutil.copyfile(TERMS, BACKEND / "terms.csv")
    with (BACKEND / "terms.csv").open("r", encoding="utf-8", newline="") as stream:
        validate_csv_rows("terms.csv", list(csv.DictReader(stream)))

    artifacts = sorted(artifact_rows(), key=lambda item: item["artifact_id"])
    write_csv("artifacts.csv", artifacts)
    qa = sorted(qa_rows(artifacts, all_records, relations), key=lambda item: item["event_id"])
    qa_failures = [item["event_id"] for item in qa if item["result"] == "fail"]
    if qa_failures:
        raise RuntimeError(f"backend QA failures: {qa_failures}")
    write_csv("qa_events.csv", qa)
    write_csv("corrections.csv", sorted(corrections, key=lambda item: item["correction_id"]))
    write_csv("translations.csv", sorted(translations, key=lambda item: item["translation_id"]))
    outcome_records = [item for item in entities if item["record_type"] == "outcome"]
    outcomes = [
        {
            "outcome_id": item["id"],
            "course_id": str(item["parent_id"]),
            "label": str(item["payload"]["label"]),
            "locale": item["locale"],
            "cognitive_level": str(item["payload"]["cognitive_level"]),
            "status": item["status"],
        }
        for item in sorted(outcome_records, key=lambda value: value["id"])
    ]
    write_csv("outcomes.csv", outcomes)
    write_csv("aliases.csv", sorted(aliases, key=lambda item: item["alias_id"]))

    (BACKEND / "entity.schema.json").write_text(
        json.dumps(entity_schema(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    for filename, definition in CSV_DEFINITIONS.items():
        (BACKEND / f"{filename}.schema.json").write_text(
            json.dumps(csv_schema(filename, definition), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    files = sorted(
        [path for path in BACKEND.iterdir() if path.is_file() and path.name != "BACKEND_MANIFEST.json"],
        key=lambda path: path.name.casefold(),
    )
    artifact_binding = {item["artifact_id"]: item["sha256"] for item in artifacts}
    input_set_sha = sha256(
        ("\n".join(f"{item['artifact_id']}\t{item['sha256']}" for item in artifacts) + "\n").encode("utf-8")
    )
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "generated": STAMP,
        "timestamp_source": {
            "artifact_id": "artifact.input.site-build-receipt",
            "sha256": STAMP_SOURCE_SHA256,
            "field": "built_at_utc",
        },
        "exporter_sha256": artifact_binding["artifact.exporter.backend"],
        "input_set_sha256": input_set_sha,
        "build_manifest_sha256": artifact_binding["artifact.input.site-package-manifest"],
        "build_receipt_sha256": artifact_binding["artifact.input.site-build-receipt"],
        "entity_count": len(entities),
        "segment_count": len(segments),
        "relation_count": len(relations),
        "qa_failures": qa_failures,
        "files": [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes())}
            for path in files
        ],
    }
    (BACKEND / "BACKEND_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    validate_backend()
    print(
        f"PASS entities={len(entities)} segments={len(segments)} relations={len(relations)} "
        f"qa_failures={len(manifest['qa_failures'])} "
        f"manifest_sha256={sha256(require_file(BACKEND / 'BACKEND_MANIFEST.json'))}"
    )


def read_csv(filename: str) -> list[dict[str, str]]:
    with (BACKEND / filename).open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != CSV_DEFINITIONS[filename]["fields"]:
            raise RuntimeError(f"{filename}: header differs from strict schema")
        rows = list(reader)
    validate_csv_rows(filename, rows)
    return rows


def validate_backend() -> None:
    manifest = load_json(BACKEND / "BACKEND_MANIFEST.json")
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("generated") != STAMP:
        raise RuntimeError("backend manifest schema or deterministic source stamp differs")
    listed = manifest.get("files")
    if not isinstance(listed, list):
        raise RuntimeError("backend manifest files must be an array")
    expected_files = sorted(
        [path for path in BACKEND.iterdir() if path.is_file() and path.name != "BACKEND_MANIFEST.json"],
        key=lambda path: path.name.casefold(),
    )
    actual_rows = [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes())}
        for path in expected_files
    ]
    if listed != actual_rows:
        raise RuntimeError("backend manifest does not exactly bind generated files")
    if manifest.get("timestamp_source") != {
        "artifact_id": "artifact.input.site-build-receipt",
        "sha256": sha256(require_file(BUILD_RECEIPT)),
        "field": "built_at_utc",
    }:
        raise RuntimeError("backend manifest timestamp is not bound to the current build receipt")
    entities = [json.loads(line) for line in require_file(BACKEND / "entities.jsonl").decode("utf-8").splitlines()]
    segments = [json.loads(line) for line in require_file(BACKEND / "segments.jsonl").decode("utf-8").splitlines()]
    relations = read_csv("relations.csv")
    validate_record_envelopes(entities + segments, relations)
    for filename in CSV_DEFINITIONS:
        rows = read_csv(filename)
        schema_path = BACKEND / f"{filename}.schema.json"
        schema = load_json(schema_path)
        if schema != csv_schema(filename, CSV_DEFINITIONS[filename]):
            raise RuntimeError(f"generated strict schema differs: {schema_path.name}")
        if filename == "artifacts.csv":
            for row in rows:
                path = ROOT / Path(row["path"])
                data = require_file(path)
                if row["bytes"] != str(len(data)) or row["sha256"] != sha256(data):
                    raise RuntimeError(f"artifact binding differs: {row['artifact_id']}")
    if load_json(BACKEND / "entity.schema.json") != entity_schema():
        raise RuntimeError("generated entity schema differs")
    artifacts = {row["artifact_id"]: row for row in read_csv("artifacts.csv")}
    current_qa_failures = sorted(
        row["event_id"] for row in read_csv("qa_events.csv") if row["result"] == "fail"
    )
    if manifest.get("qa_failures") != current_qa_failures:
        raise RuntimeError("backend manifest QA-failure list differs from qa_events.csv")
    if current_qa_failures:
        raise RuntimeError(f"backend contains QA failures: {current_qa_failures}")
    if manifest.get("exporter_sha256") != artifacts["artifact.exporter.backend"]["sha256"]:
        raise RuntimeError("backend manifest does not bind exporter")
    if manifest.get("build_manifest_sha256") != artifacts["artifact.input.site-package-manifest"]["sha256"]:
        raise RuntimeError("backend manifest does not bind site package manifest")
    if manifest.get("build_receipt_sha256") != artifacts["artifact.input.site-build-receipt"]["sha256"]:
        raise RuntimeError("backend manifest does not bind site build receipt")
    artifact_list = sorted(artifacts.values(), key=lambda item: item["artifact_id"])
    input_set_sha = sha256(
        ("\n".join(f"{item['artifact_id']}\t{item['sha256']}" for item in artifact_list) + "\n").encode("utf-8")
    )
    if manifest.get("input_set_sha256") != input_set_sha:
        raise RuntimeError("backend manifest input-set binding differs")
    known = {item["id"] for item in entities + segments}
    alias_rows = read_csv("aliases.csv")
    for row in alias_rows:
        if row["canonical_id"] not in known:
            raise RuntimeError(f"alias references unknown canonical id: {row['alias_id']}")
    by_id = entities_by_id(entities + segments)
    required_alias_targets = {
        "unit.donor.zitkovic.monte-carlo-exp.exercise",
        "unit.donor.zitkovic.monte-carlo-exp.solution",
        "unit.donor.zitkovic.monte-carlo-exp.program.1",
        "unit.donor.zitkovic.monte-carlo-exp.program.2",
        "unit.donor.zitkovic.monte-carlo-exp.program.3",
        "o009-exercise-convergence-mc-estimation",
        "o009-solution-convergence-mc-estimation",
        "o009-program-convergence-mc",
    }
    missing_aliases = required_alias_targets - {row["canonical_id"] for row in alias_rows}
    if missing_aliases:
        raise RuntimeError(f"alias surface does not cover donor/target graph: {sorted(missing_aliases)}")
    for row in read_csv("translations.csv"):
        if row["source_id"] not in by_id or row["target_id"] not in by_id:
            raise RuntimeError(f"translation references unknown endpoint: {row['translation_id']}")
        source = by_id[row["source_id"]]
        target = by_id[row["target_id"]]
        if row["source_sha256"] not in {source["source_sha256"], source["target_sha256"]}:
            raise RuntimeError(f"translation source hash differs: {row['translation_id']}")
        if row["target_sha256"] != target["target_sha256"]:
            raise RuntimeError(f"translation target hash differs: {row['translation_id']}")
        if row["source_rights_id"] != source["rights_id"] or row["target_rights_id"] != target["rights_id"]:
            raise RuntimeError(f"translation rights binding differs: {row['translation_id']}")
    if require_file(BACKEND / "terms.csv") != require_file(TERMS):
        raise RuntimeError("backend terms surface is not an exact controlled-vocabulary copy")
    rights_expectations = {
        "rights.random.cc-by-2.0.witness": sha256(require_file(AUTH_RANDOM / "static" / "index.html")),
        "rights.random.cc-by-1.0.witness": sha256(require_file(AUTH_RANDOM / "static" / "Credits.html")),
        "rights.random.dual-witness": sha256(require_file(RANDOM_RECEIPT)),
        "rights.random.martingale-image.cc-by-3.0": sha256(
            require_file(AUTH_RANDOM / "static" / "martingales" / "Martingale.png")
        ),
        "rights.zitkovic.donor.cc0-1.0": sha256(require_file(ZIT_LICENSE)),
        "rights.mathjax.apache-2.0": sha256(require_file(AUTH_RANDOM / "shared" / "MathJax" / "LICENSE")),
    }
    witness_hash = sha256(lab_rights_witness(require_file(LAB).decode("utf-8")).encode("utf-8"))
    rights_expectations["rights.o009.indonesian-adaptation.cc-by-4.0"] = witness_hash
    rights_expectations["rights.o009.original.cc-by-4.0"] = witness_hash
    for rights_id, expected_hash in rights_expectations.items():
        if by_id[rights_id]["source_sha256"] != expected_hash:
            raise RuntimeError(f"rights witness hash differs: {rights_id}")

    # Re-extract complete target bodies independently from the exported hashes.
    lab_text = require_file(LAB).decode("utf-8")
    blocks = fenced_div_spans(lab_text)
    headings = heading_spans(lab_text, blocks["o009-lab-convergence-mc"])
    chunks = {name: span for name, span in r_chunk_spans(lab_text) if name}
    body_spans = {
        "o009-lab-convergence-mc": blocks["o009-lab-convergence-mc"],
        "o009-lab-convergence-mc-experiment": headings["o009-lab-convergence-mc-experiment"],
        "o009-exercise-convergence-mc-estimation": blocks["o009-exercise-convergence-mc-estimation"],
        "o009-concept-monte-carlo-lln": headings["o009-concept-monte-carlo-lln"],
        "o009-mastery-convergence-mc": headings["o009-mastery-convergence-mc"],
        "o009-exercise-convergence-mc-mastery": blocks["o009-exercise-convergence-mc-mastery"],
        "o009-hint-convergence-mc-mastery-1": blocks["o009-hint-convergence-mc-mastery-1"],
        "o009-hint-convergence-mc-mastery-2": blocks["o009-hint-convergence-mc-mastery-2"],
        "o009-hint-convergence-mc-mastery-3": blocks["o009-hint-convergence-mc-mastery-3"],
        "o009-answer-convergence-mc-mastery": blocks["o009-answer-convergence-mc-mastery"],
        "o009-solution-convergence-mc-mastery": blocks["o009-solution-convergence-mc-mastery"],
        "o009-program-convergence-mc": chunks["o009_lab_convergence_mc"],
        "o009-solution-convergence-mc-estimation": Span(
            blocks["o009-exercise-convergence-mc-estimation"].end,
            headings["o009-concept-monte-carlo-lln"].start,
            blocks["o009-exercise-convergence-mc-estimation"].end,
            headings["o009-concept-monte-carlo-lln"].start,
        ),
    }
    for stable_id, span in body_spans.items():
        expected_hash = sha256(lab_text[span.start : span.end].encode("utf-8"))
        if by_id[stable_id]["target_sha256"] != expected_hash:
            raise RuntimeError(f"complete lab body hash differs: {stable_id}")
        if by_id[stable_id]["payload"].get("body_extent") != "complete":
            raise RuntimeError(f"lab unit is not declared as a complete body: {stable_id}")

    current_donor, _, _, _ = donor_components()
    for donor in current_donor:
        exported = by_id[donor["id"]]
        if exported["source_sha256"] != donor["source_sha256"] or exported["target_sha256"] != donor["target_sha256"]:
            raise RuntimeError(f"donor component hash differs: {donor['id']}")
    # Validate the already-built site without mutating it or re-running R.
    load_build_validator().verify_site(ROOT / "build" / "site", execute_r=False)
    print(
        f"STRICT PASS files={len(listed)} records={len(entities) + len(segments)} "
        f"manifest_sha256={sha256(require_file(BACKEND / 'BACKEND_MANIFEST.json'))}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true", help="strictly validate current backend without writing")
    args = parser.parse_args()
    if args.validate_only:
        validate_backend()
    else:
        build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
