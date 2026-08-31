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
from yaml import safe_load


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
AUTHORED_MASTERY_INPUTS = tuple(
    ROOT / "source" / "mastery" / name
    for name in (
        "01-konvergensi-01-02.md",
        "02-konvergensi-03-04.md",
        "03-konvergensi-05.md",
        "04-bersyarat-kernel-01-02.md",
        "05-bersyarat-kernel-03.md",
        "06-martingal-01-02.md",
        "07-martingal-03-04.md",
        "08-martingal-05.md",
        "09-poisson-konstruksi-01.md",
        "10-brown-01.md",
        "11-brown-02.md",
        "12-brown-03-04.md",
        "13-brown-05-06.md",
        "14-brown-07.md",
    )
)
AUTHORED_ASSESSMENT_INPUTS = tuple(
    ROOT / "source" / "assessments" / name
    for name in (
        "01-formulir-kumulatif-a.md",
        "02-formulir-kumulatif-b.md",
    )
)
AUTHORED_MARKDOWN_INPUTS = AUTHORED_MASTERY_INPUTS + AUTHORED_ASSESSMENT_INPUTS
AUTHORED_MARKDOWN_INGESTION = "authored-markdown-v1"
AUTHORED_MASTERY_ITEM_COUNTS = (2, 2, 1, 2, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1)
AUTHORED_FALLBACK_RIGHTS = {
    "source/mastery/03-konvergensi-05.md": "rights.o009.mastery.convergence.05.cc-by-4.0",
    "source/mastery/07-martingal-03-04.md": "rights.o009.mastery.martingales.03-04.cc-by-4.0",
    "source/mastery/08-martingal-05.md": "rights.o009.mastery.martingales.05.cc-by-4.0",
    "source/mastery/10-brown-01.md": "rights.o009.mastery.brown.01.cc-by-4.0",
    "source/mastery/12-brown-03-04.md": "rights.o009.mastery.brown.03-04.cc-by-4.0",
}
AUTHORED_REFERENCE_TARGETS = {
    "o009-theory-random-prob-convergence": "unit.o009.random.prob.convergence",
    "prerequisite.o009.probability.borel-cantelli.first": "unit.o009.random.prob.convergence",
    "prerequisite.o009.probability.convergence.modes": "unit.o009.random.prob.convergence",
    "theory.o009.prob.convergence.random-variables": "unit.o009.random.prob.convergence",
    "prerequisite.o009.convergence.characteristic-functions": "unit.o009.random.dist.convergence",
    "prerequisite.o009.convergence.poisson-generating-functions": "unit.o009.random.dist.convergence",
    "prerequisite.o009.convergence.slutsky-continuous-mapping": "unit.o009.random.dist.convergence",
    "prerequisite.o009.distribution.skorohod-continuous-mapping": "unit.o009.random.dist.convergence",
    "prerequisite.o009.distribution.weak-convergence": "unit.o009.random.dist.convergence",
    "theory.o009.dist.convergence.fundamental-limit-theorems": "unit.o009.random.dist.convergence",
    "theory.o009.expect.uniform-integrability.convergence": "unit.o009.random.expect.uniform",
    "prerequisite.o009.conditional-expectation": "unit.o009.random.expect.conditional2",
    "prerequisite.o009.martingales.definition": "unit.o009.random.martingales.introduction",
    "prerequisite.o009.martingales.optional-stopping": "unit.o009.random.martingales.stop",
    "prerequisite.o009.ctmc.generator": "unit.o009.quantecon.ctmc.generators",
    "o009-theory-brown-standard": "unit.o009.random.brown.standard",
    "o009-theory-random-brown-standard": "unit.o009.random.brown.standard",
    "unit.o009.original.bridge.regular-conditional-probability": "unit.o009.original.bridge.regular-conditional-probability",
}
AUTHORED_OUTCOME_SPECS = {
    "outcome.o009.convergence.03.second-order-delta-method": ("Membuktikan metode delta orde kedua pada limit bersama", "prove"),
    "outcome.o009.convergence.04.rare-spike-phase-diagram": ("Menganalisis diagram fase lonjakan langka", "analyze"),
    "outcome.o009.convergence.asymptotic-independence": ("Membuktikan ketakbergantungan asimtotik", "prove"),
    "outcome.o009.convergence.audit-discontinuous-transform": ("Mengaudit transformasi diskontinu pada limit", "analyze"),
    "outcome.o009.convergence.map-outside-null-discontinuities": ("Menerapkan pemetaan kontinu di luar himpunan diskontinuitas nol", "prove"),
    "outcome.o009.convergence.random-sum-joint-limit": ("Membuktikan limit gabungan jumlah acak", "prove"),
    "outcome.o009.convergence.random-versus-deterministic-centering": ("Membandingkan pemusatan acak dan deterministik", "analyze"),
    "outcome.o009.convergence.separate-probability-almost-sure": ("Membedakan konvergensi dalam probabilitas dan hampir pasti", "analyze"),
    "outcome.o009.convergence.subsequence-characterization": ("Membuktikan karakterisasi konvergensi melalui subbarisan", "prove"),
    "outcome.o009.mastery.conditional-kernel.bayes-tilt": ("Membuktikan perubahan ukuran Bayes melalui kernel", "prove"),
    "outcome.o009.mastery.conditional-kernel.gaussian-bridge": ("Membangun kernel jembatan Gaussian", "prove"),
    "outcome.o009.mastery.martingales.01.compensator": ("Membangun kompensator dan menghentikannya secara sah", "prove"),
    "outcome.o009.mastery.martingales.01.harmonic-stopping": ("Membangun martingal harmonik untuk absorpsi", "prove"),
    "outcome.o009.mastery.martingales.02.counting-compensator": ("Menurunkan kompensator proses hitung dari generator", "prove"),
    "outcome.o009.mastery.martingales.02.laplace-stopping": ("Menghitung transformasi Laplace dengan martingal ruang-waktu", "prove"),
}
AUTH_RANDOM = ROOT / "authority" / "random"
LAB = ROOT / "source" / "labs" / "01-konvergensi-monte-carlo.Rmd"
LAB_MARKOV = ROOT / "source" / "labs" / "02-simulasi-rantai-markov.Rmd"
LAB_CONVERGENCE_MODES = (
    ROOT / "source" / "labs" / "03-konvergensi-mode-dan-lln-clt.Rmd"
)
LAB_CONDITIONAL_MARTINGALE = (
    ROOT / "source" / "labs" / "04-nilai-harapan-bersyarat-martingal.Rmd"
)
LAB_BROWNIAN_DIAGNOSTICS = (
    ROOT
    / "source"
    / "labs"
    / "05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.Rmd"
)
TWO_STATE_APP = ROOT / "source" / "apps" / "two-state.html"
BUILT_TWO_STATE_APP = ROOT / "build" / "site" / "apps" / "two-state.html"
BROWN_DRIFT_OFFLINE_APP = ROOT / "source" / "original" / "brown-drift-offline.js"
BUILT_BROWN_DRIFT_OFFLINE_APP = (
    ROOT / "build" / "site" / "apps" / "brown-drift-offline.js"
)
BROWN_BRIDGE_OFFLINE_APP = ROOT / "source" / "original" / "brown-bridge-offline.js"
BUILT_BROWN_BRIDGE_OFFLINE_APP = (
    ROOT / "build" / "site" / "apps" / "brown-bridge-offline.js"
)
BROWN_GEOMETRIC_OFFLINE_APP = (
    ROOT / "source" / "original" / "geometric-brownian-offline.js"
)
BUILT_BROWN_GEOMETRIC_OFFLINE_APP = (
    ROOT / "build" / "site" / "apps" / "geometric-brownian-offline.js"
)
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
ZIT_MARKOV = ZIT_ROOT / "source" / "05-Markov-chains.Rmd"
QUANTECON_ROOT = ROOT / "authority" / "quantecon"
QUANTECON_SOURCE_ROOT = QUANTECON_ROOT / "source_snapshot" / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
QUANTECON_NOTEBOOK_ROOT = QUANTECON_ROOT / "notebook_snapshot" / "continuous_time_mcs.notebooks-1e17c25c937f369544380f769eb9c1bc45d12d1a"
QUANTECON_SOURCE = QUANTECON_SOURCE_ROOT / "lectures" / "memoryless.md"
QUANTECON_NOTEBOOK = QUANTECON_NOTEBOOK_ROOT / "memoryless.ipynb"
QUANTECON_LICENSE = QUANTECON_ROOT / "evidence" / "quantecon-ctmc-intro-license-witness.html"
QUANTECON_COMPONENT = ROOT / "build" / "components" / "quantecon_memoryless"
QUANTECON_HTML = QUANTECON_COMPONENT / "lectures" / "memoryless.html"
QUANTECON_MANIFEST = QUANTECON_COMPONENT / "COMPONENT_MANIFEST.tsv"
QUANTECON_RECEIPT = QUANTECON_COMPONENT / "COMPONENT_RECEIPT.json"
QUANTECON_POISSON_COMPONENT = ROOT / "build" / "components" / "quantecon_poisson"
QUANTECON_POISSON_SOURCE = QUANTECON_SOURCE_ROOT / "lectures" / "poisson.md"
QUANTECON_POISSON_NOTEBOOK = QUANTECON_NOTEBOOK_ROOT / "poisson.ipynb"
QUANTECON_POISSON_HTML = QUANTECON_POISSON_COMPONENT / "lectures" / "poisson.html"
QUANTECON_POISSON_MANIFEST = QUANTECON_POISSON_COMPONENT / "COMPONENT_MANIFEST.tsv"
QUANTECON_POISSON_RECEIPT = QUANTECON_POISSON_COMPONENT / "COMPONENT_RECEIPT.json"
QUANTECON_MARKOV_PROP_COMPONENT = ROOT / "build" / "components" / "quantecon_markov_prop"
QUANTECON_MARKOV_PROP_SOURCE = QUANTECON_SOURCE_ROOT / "lectures" / "markov_prop.md"
QUANTECON_MARKOV_PROP_NOTEBOOK = QUANTECON_NOTEBOOK_ROOT / "markov_prop.ipynb"
QUANTECON_MARKOV_PROP_HTML = QUANTECON_MARKOV_PROP_COMPONENT / "lectures" / "markov_prop.html"
QUANTECON_MARKOV_PROP_MANIFEST = QUANTECON_MARKOV_PROP_COMPONENT / "COMPONENT_MANIFEST.tsv"
QUANTECON_MARKOV_PROP_RECEIPT = QUANTECON_MARKOV_PROP_COMPONENT / "COMPONENT_RECEIPT.json"
QUANTECON_KOLMOGOROV_BWD_COMPONENT = ROOT / "build" / "components" / "quantecon_kolmogorov_bwd"
QUANTECON_KOLMOGOROV_BWD_SOURCE = QUANTECON_SOURCE_ROOT / "lectures" / "kolmogorov_bwd.md"
QUANTECON_KOLMOGOROV_BWD_NOTEBOOK = QUANTECON_NOTEBOOK_ROOT / "kolmogorov_bwd.ipynb"
QUANTECON_KOLMOGOROV_BWD_HTML = QUANTECON_KOLMOGOROV_BWD_COMPONENT / "lectures" / "kolmogorov_bwd.html"
QUANTECON_KOLMOGOROV_BWD_MANIFEST = QUANTECON_KOLMOGOROV_BWD_COMPONENT / "COMPONENT_MANIFEST.tsv"
QUANTECON_KOLMOGOROV_BWD_RECEIPT = QUANTECON_KOLMOGOROV_BWD_COMPONENT / "COMPONENT_RECEIPT.json"
QUANTECON_KOLMOGOROV_FWD_COMPONENT = ROOT / "build" / "components" / "quantecon_kolmogorov_fwd"
QUANTECON_KOLMOGOROV_FWD_SOURCE = QUANTECON_SOURCE_ROOT / "lectures" / "kolmogorov_fwd.md"
QUANTECON_KOLMOGOROV_FWD_NOTEBOOK = QUANTECON_NOTEBOOK_ROOT / "kolmogorov_fwd.ipynb"
QUANTECON_KOLMOGOROV_FWD_STATIC_ASSET = (
    QUANTECON_SOURCE_ROOT
    / "lectures"
    / "_static"
    / "lecture_specific"
    / "markov_prop"
    / "flow_fig.png"
)
QUANTECON_KOLMOGOROV_FWD_HTML = QUANTECON_KOLMOGOROV_FWD_COMPONENT / "lectures" / "kolmogorov_fwd.html"
QUANTECON_KOLMOGOROV_FWD_MANIFEST = QUANTECON_KOLMOGOROV_FWD_COMPONENT / "COMPONENT_MANIFEST.tsv"
QUANTECON_KOLMOGOROV_FWD_RECEIPT = QUANTECON_KOLMOGOROV_FWD_COMPONENT / "COMPONENT_RECEIPT.json"
QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA = ROOT / "qa" / "QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA.json"
QUANTECON_GENERATORS_COMPONENT = ROOT / "build" / "components" / "quantecon_generators"
QUANTECON_GENERATORS_SOURCE = QUANTECON_SOURCE_ROOT / "lectures" / "generators.md"
QUANTECON_GENERATORS_NOTEBOOK = QUANTECON_NOTEBOOK_ROOT / "generators.ipynb"
QUANTECON_GENERATORS_HTML = QUANTECON_GENERATORS_COMPONENT / "lectures" / "generators.html"
QUANTECON_GENERATORS_MANIFEST = QUANTECON_GENERATORS_COMPONENT / "COMPONENT_MANIFEST.tsv"
QUANTECON_GENERATORS_RECEIPT = QUANTECON_GENERATORS_COMPONENT / "COMPONENT_RECEIPT.json"
QUANTECON_GENERATORS_TRANSLATION_AUDIT = ROOT / "qa" / "QUANTECON_GENERATORS_TRANSLATION_AUDIT_20260824.md"
QUANTECON_GENERATORS_MATH_AUDIT = ROOT / "qa" / "QUANTECON_GENERATORS_MATH_AUDIT_20260824.md"
QUANTECON_UC_MC_SEMIGROUPS_COMPONENT = ROOT / "build" / "components" / "quantecon_uc_mc_semigroups"
QUANTECON_UC_MC_SEMIGROUPS_SOURCE = QUANTECON_SOURCE_ROOT / "lectures" / "uc_mc_semigroups.md"
QUANTECON_UC_MC_SEMIGROUPS_NOTEBOOK = QUANTECON_NOTEBOOK_ROOT / "uc_mc_semigroups.ipynb"
QUANTECON_UC_MC_SEMIGROUPS_HTML = QUANTECON_UC_MC_SEMIGROUPS_COMPONENT / "lectures" / "uc_mc_semigroups.html"
QUANTECON_UC_MC_SEMIGROUPS_MANIFEST = QUANTECON_UC_MC_SEMIGROUPS_COMPONENT / "COMPONENT_MANIFEST.tsv"
QUANTECON_UC_MC_SEMIGROUPS_RECEIPT = QUANTECON_UC_MC_SEMIGROUPS_COMPONENT / "COMPONENT_RECEIPT.json"
QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA = ROOT / "qa" / "QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA.json"
QUANTECON_UC_MC_SEMIGROUPS_TRANSLATION_AUDIT = ROOT / "qa" / "QUANTECON_UC_MC_SEMIGROUPS_TRANSLATION_AUDIT_20260824.md"
QUANTECON_UC_MC_SEMIGROUPS_MATH_AUDIT = ROOT / "qa" / "QUANTECON_UC_MC_SEMIGROUPS_MATH_AUDIT_20260824.md"
QUANTECON_ERGODICITY_COMPONENT = ROOT / "build" / "components" / "quantecon_ergodicity"
QUANTECON_ERGODICITY_SOURCE = QUANTECON_SOURCE_ROOT / "lectures" / "ergodicity.md"
QUANTECON_ERGODICITY_NOTEBOOK = QUANTECON_NOTEBOOK_ROOT / "ergodicity.ipynb"
QUANTECON_ERGODICITY_HTML = QUANTECON_ERGODICITY_COMPONENT / "lectures" / "ergodicity.html"
QUANTECON_ERGODICITY_MANIFEST = QUANTECON_ERGODICITY_COMPONENT / "COMPONENT_MANIFEST.tsv"
QUANTECON_ERGODICITY_RECEIPT = QUANTECON_ERGODICITY_COMPONENT / "COMPONENT_RECEIPT.json"
QUANTECON_ERGODICITY_NUMERICAL_QA = ROOT / "qa" / "QUANTECON_ERGODICITY_NUMERICAL_QA.json"
QUANTECON_ERGODICITY_TRANSLATION_AUDIT = ROOT / "qa" / "QUANTECON_ERGODICITY_TRANSLATION_AUDIT_20260824.md"
QUANTECON_ERGODICITY_MATH_AUDIT = ROOT / "qa" / "QUANTECON_ERGODICITY_MATH_AUDIT_20260824.md"

ORIGINAL_BRIDGE_SOURCE = (
    ROOT / "source" / "original" / "01-konstruksi-kolmogorov.md"
)
ORIGINAL_BRIDGE_READER = (
    ROOT / "build" / "site" / "original" / "01-konstruksi-kolmogorov.html"
)
ORIGINAL_BRIDGE_MASTERY_LEDGER = (
    ROOT / "qa" / "ORIGINAL_BRIDGE_01_MASTERY_LEDGER.json"
)
ORIGINAL_BRIDGE_SOURCE_BYTES = 34418
ORIGINAL_BRIDGE_SOURCE_SHA256 = (
    "bf37d6b746e617b5010a96be0c105e7f4ecd33e39a22b6a0f0528cd6b48cd164"
)
ORIGINAL_BRIDGE_UNIT_ID = (
    "unit.o009.original.bridge.kolmogorov-canonical-process"
)
ORIGINAL_BRIDGE_RIGHTS_ID = (
    "rights.o009.original.bridge.kolmogorov.cc-by-4.0"
)
ORIGINAL_BRIDGE_PATH = "original/01-konstruksi-kolmogorov.html"
ORIGINAL_BRIDGE_SECTION_SPECS = (
    (
        "tujuan-dan-prasyarat",
        "Tujuan dan prasyarat",
        (
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.kolmogorov-extension",
        ),
    ),
    (
        "ruang-lintasan-produk",
        "Ruang lintasan produk",
        (
            "concept.measure.product-sigma-algebra",
            "concept.measure.cylinder-set",
            "concept.stochastic.process.path-space",
        ),
    ),
    (
        "konsistensi-proyektif",
        "Konsistensi proyektif",
        (
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.projective-consistency",
        ),
    ),
    (
        "teorema-perluasan-kolmogorov",
        "Teorema perluasan Kolmogorov",
        (
            "concept.measurable-space.standard-borel",
            "concept.stochastic.process.kolmogorov-extension",
            "concept.stochastic.process.projective-consistency",
        ),
    ),
    (
        "lingkup-bukti",
        "Lingkup bukti",
        (
            "concept.measure.product-sigma-algebra",
            "concept.measure.cylinder-set",
            "concept.stochastic.process.kolmogorov-extension",
        ),
    ),
    (
        "proses-koordinat-kanonik",
        "Proses koordinat kanonik",
        (
            "concept.stochastic.process.path-space",
            "concept.stochastic.process.canonical-process",
        ),
    ),
    (
        "contoh-keluarga-markov",
        "Contoh keluarga Markov",
        (
            "concept.stochastic.process.projective-consistency",
            "concept.stochastic.process.canonical-process",
            "concept.markov.chapman-kolmogorov",
        ),
    ),
    (
        "contoh-keluarga-gaussian",
        "Contoh keluarga Gaussian",
        (
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.projective-consistency",
            "concept.stochastic.process.canonical-process",
        ),
    ),
    (
        "audit-hipotesis-dan-bukan-klaim",
        "Audit hipotesis dan bukan klaim",
        (
            "concept.measure.product-sigma-algebra",
            "concept.measurable-space.standard-borel",
            "concept.stochastic.process.path-space",
            "concept.stochastic.process.kolmogorov-extension",
        ),
    ),
    (
        "latihan-penguasaan",
        "Latihan penguasaan",
        (
            "concept.measure.cylinder-set",
            "concept.stochastic.process.projective-consistency",
            "concept.stochastic.process.canonical-process",
        ),
    ),
    ("hak-dan-provenans", "Hak dan provenans", ()),
)
ORIGINAL_BRIDGE_NEW_CONCEPTS = {
    "concept.measure.product-sigma-algebra": "product sigma-algebra",
    "concept.measure.cylinder-set": "measurable cylinder set",
    "concept.measurable-space.standard-borel": "standard Borel measurable space",
    "concept.stochastic.process.projective-consistency": (
        "projective consistency of finite-dimensional laws"
    ),
    "concept.stochastic.process.path-space": "raw product path space",
    "concept.stochastic.process.canonical-process": "canonical coordinate process",
}
ORIGINAL_BRIDGE_OUTCOMES = {
    "outcome.o009.audit-kolmogorov-extension-hypotheses": (
        "Mengaudit hipotesis perluasan Kolmogorov dan membatasi kesimpulannya "
        "pada sigma-aljabar produk serta ruang lintasan mentah.",
        "analyze",
        [
            "concept.measurable-space.standard-borel",
            "concept.measure.product-sigma-algebra",
            "concept.stochastic.process.kolmogorov-extension",
            "concept.stochastic.process.path-space",
        ],
    ),
    "outcome.o009.construct-canonical-process-from-fdds": (
        "Membangun proses koordinat kanonik dari keluarga hukum berdimensi "
        "hingga yang konsisten secara proyektif.",
        "prove",
        [
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.projective-consistency",
            "concept.stochastic.process.canonical-process",
        ],
    ),
}
ORIGINAL_BRIDGE_MASTERY_BASE_IDS = tuple(
    f"unit.o009.original.mastery.process-construction.{index:02d}"
    for index in range(1, 4)
)
ORIGINAL_BRIDGE_MASTERY_SUFFIXES = (
    "exercise",
    "hint.01",
    "hint.02",
    "answer",
    "solution",
)

ORIGINAL_BRIDGE_02_SOURCE = (
    ROOT / "source" / "original" / "02-keterukuran-proses-dan-hukum-lintasan.md"
)
ORIGINAL_BRIDGE_02_READER = (
    ROOT
    / "build"
    / "site"
    / "original"
    / "02-keterukuran-proses-dan-hukum-lintasan.html"
)
ORIGINAL_BRIDGE_02_MASTERY_LEDGER = (
    ROOT / "qa" / "ORIGINAL_BRIDGE_02_MASTERY_LEDGER.json"
)
ORIGINAL_BRIDGE_02_SOURCE_BYTES = 29971
ORIGINAL_BRIDGE_02_SOURCE_SHA256 = (
    "f14bd9e7ad6a80079eb40609dd97f9768e08fae5bc638e9d5939666f53ad0acb"
)
ORIGINAL_BRIDGE_02_UNIT_ID = (
    "unit.o009.original.bridge.process-measurability-path-law"
)
ORIGINAL_BRIDGE_02_RIGHTS_ID = (
    "rights.o009.original.bridge.process-measurability-path-law.cc-by-4.0"
)
ORIGINAL_BRIDGE_02_PATH = (
    "original/02-keterukuran-proses-dan-hukum-lintasan.html"
)
ORIGINAL_BRIDGE_02_SECTION_SPECS = (
    (
        "tujuan-dan-empat-lapis-objek",
        "Tujuan dan empat lapis objek",
        (
            "concept.stochastic.process.coordinatewise-measurability",
            "concept.stochastic.process.path-map-measurability",
            "concept.stochastic.process.joint-measurability",
            "concept.stochastic.process.regular-path-space-law",
        ),
    ),
    (
        "peta-lintasan-mentah",
        "Peta lintasan mentah dan keterukuran tiap waktu",
        (
            "concept.measure.product-sigma-algebra",
            "concept.stochastic.process.coordinatewise-measurability",
            "concept.stochastic.process.path-map-measurability",
            "concept.stochastic.process.raw-path-law",
        ),
    ),
    (
        "keterukuran-bersama",
        "Keterukuran bersama dan evaluasi kanonik",
        (
            "concept.stochastic.process.coordinatewise-measurability",
            "concept.stochastic.process.joint-measurability",
            "concept.stochastic.process.countable-coordinate-dependence",
            "concept.stochastic.process.canonical-process",
        ),
    ),
    (
        "fdd-dan-hukum-lintasan-mentah",
        "Distribusi berdimensi hingga dan hukum lintasan mentah",
        (
            "concept.measure.product-sigma-algebra",
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.raw-path-law",
        ),
    ),
    (
        "sifat-lintasan-di-ruang-mentah",
        "Mengapa sifat lintasan belum menjadi kejadian mentah",
        (
            "concept.stochastic.process.path-space",
            "concept.stochastic.process.raw-path-law",
            "concept.stochastic.process.countable-coordinate-dependence",
        ),
    ),
    (
        "hukum-pada-ruang-lintasan-kontinu",
        "Hukum pada ruang lintasan kontinu",
        (
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.regular-path-space-law",
        ),
    ),
    (
        "modifikasi-dan-ketakterbedaan",
        "Modifikasi, FDD yang sama, dan ketakterbedaan",
        (
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.modification",
            "concept.stochastic.process.indistinguishability",
        ),
    ),
    (
        "audit-klaim-lintasan",
        "Audit klaim lintasan",
        (
            "concept.stochastic.process.joint-measurability",
            "concept.stochastic.process.raw-path-law",
            "concept.stochastic.process.regular-path-space-law",
            "concept.stochastic.process.modification",
            "concept.stochastic.process.indistinguishability",
        ),
    ),
    (
        "latihan-penguasaan-keterukuran",
        "Latihan penguasaan",
        (
            "concept.stochastic.process.joint-measurability",
            "concept.stochastic.process.regular-path-space-law",
            "concept.stochastic.process.modification",
            "concept.stochastic.process.indistinguishability",
        ),
    ),
    (
        "hak-dan-provenans-keterukuran",
        "Hak dan provenans",
        (),
    ),
)
ORIGINAL_BRIDGE_02_NEW_CONCEPTS = {
    "concept.stochastic.process.coordinatewise-measurability": (
        "coordinatewise measurability of a stochastic process"
    ),
    "concept.stochastic.process.path-map-measurability": (
        "measurability of the raw path map"
    ),
    "concept.stochastic.process.joint-measurability": (
        "joint measurability of a stochastic process"
    ),
    "concept.stochastic.process.raw-path-law": "law on a raw product path space",
    "concept.stochastic.process.regular-path-space-law": (
        "Borel law on a regular path space"
    ),
    "concept.stochastic.process.countable-coordinate-dependence": (
        "countable-coordinate dependence in a product sigma-algebra"
    ),
    "concept.stochastic.process.modification": "modification of a stochastic process",
    "concept.stochastic.process.indistinguishability": (
        "indistinguishability of stochastic processes"
    ),
}
ORIGINAL_BRIDGE_02_OUTCOMES = {
    "outcome.o009.distinguish-process-measurability-levels": (
        "Membedakan keterukuran tiap koordinat, peta lintasan mentah, evaluasi "
        "proses bersama, dan peubah acak bernilai ruang lintasan teratur.",
        "analyze",
        [
            "concept.stochastic.process.coordinatewise-measurability",
            "concept.stochastic.process.path-map-measurability",
            "concept.stochastic.process.joint-measurability",
            "concept.stochastic.process.regular-path-space-law",
        ],
    ),
    "outcome.o009.audit-fdd-versus-regular-path-law": (
        "Mengaudit tepat apa yang ditentukan oleh distribusi berdimensi hingga "
        "pada ruang produk mentah dan apa yang masih memerlukan ruang lintasan teratur.",
        "analyze",
        [
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.raw-path-law",
            "concept.stochastic.process.regular-path-space-law",
            "concept.stochastic.process.countable-coordinate-dependence",
        ],
    ),
    "outcome.o009.distinguish-modification-and-indistinguishability": (
        "Membedakan kesamaan FDD, modifikasi, dan ketakterbedaan serta membuktikan "
        "kapan keteraturan lintasan menguatkan kesamaan tiap waktu.",
        "prove",
        [
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.modification",
            "concept.stochastic.process.indistinguishability",
        ],
    ),
}
ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS = tuple(
    f"unit.o009.original.mastery.measurability-path-law.{index:02d}"
    for index in range(1, 4)
)
ORIGINAL_BRIDGE_02_MASTERY_SUFFIXES = ORIGINAL_BRIDGE_MASTERY_SUFFIXES

ORIGINAL_BRIDGE_03_SOURCE = (
    ROOT / "source" / "original" / "03-probabilitas-bersyarat-reguler.md"
)
ORIGINAL_BRIDGE_03_READER = (
    ROOT
    / "build"
    / "site"
    / "original"
    / "03-probabilitas-bersyarat-reguler.html"
)
ORIGINAL_BRIDGE_03_MASTERY_LEDGER = (
    ROOT / "qa" / "ORIGINAL_BRIDGE_03_MASTERY_LEDGER.json"
)
ORIGINAL_BRIDGE_03_SOURCE_BYTES = 34016
ORIGINAL_BRIDGE_03_SOURCE_SHA256 = (
    "d24d06e9c5e60c2d0a70ee0ff00fd0e2e7687e12a12404b6f7e903af76ccbe44"
)
ORIGINAL_BRIDGE_03_UNIT_ID = (
    "unit.o009.original.bridge.regular-conditional-probability"
)
ORIGINAL_BRIDGE_03_RIGHTS_ID = (
    "rights.o009.original.bridge.regular-conditional-probability.cc-by-4.0"
)
ORIGINAL_BRIDGE_03_PATH = (
    "original/03-probabilitas-bersyarat-reguler.html"
)
ORIGINAL_BRIDGE_03_SECTION_SPECS = (
    (
        "tujuan-dan-kesenjangan-versi",
        "Tujuan dan kesenjangan versi",
        (
            "concept.conditional.expectation",
            "concept.conditional.probability",
            "concept.kernel.probability",
            "concept.conditional.regular-distribution",
            "concept.conditional.version",
            "concept.conditional.null-conditioning-value",
        ),
    ),
    (
        "dari-nilai-harapan-ke-kernel",
        "Dari nilai harapan bersyarat ke kernel",
        (
            "concept.conditional.expectation",
            "concept.conditional.probability",
            "concept.kernel.probability",
            "concept.conditional.regular-distribution",
            "concept.conditional.version",
        ),
    ),
    (
        "keberadaan-pada-sasaran-borel-standar",
        "Keberadaan pada sasaran Borel standar",
        (
            "concept.measurable-space.standard-borel",
            "concept.kernel.probability",
            "concept.conditional.regular-distribution",
            "concept.conditional.determining-class",
        ),
    ),
    (
        "kelas-penentu-dan-versi-serentak",
        "Kelas penentu dan versi serentak",
        (
            "concept.conditional.version",
            "concept.conditional.determining-class",
            "concept.conditional.regular-distribution",
        ),
    ),
    (
        "pengondisian-pada-peubah-acak",
        "Pengondisian pada peubah acak",
        (
            "concept.kernel.probability",
            "concept.conditional.regular-distribution",
            "concept.conditional.disintegration",
            "concept.conditional.null-conditioning-value",
        ),
    ),
    (
        "rumus-disintegrasi-dan-kepadatan",
        "Rumus disintegrasi dan kepadatan",
        (
            "concept.kernel.density",
            "concept.conditional.regular-distribution",
            "concept.conditional.disintegration",
        ),
    ),
    (
        "nilai-pada-titik-pengondisian-nol",
        "Nilai pada titik pengondisian bermassa nol",
        (
            "concept.conditional.version",
            "concept.conditional.regular-distribution",
            "concept.conditional.null-conditioning-value",
        ),
    ),
    (
        "probabilitas-bersyarat-seluruh-eksperimen",
        "Probabilitas bersyarat seluruh eksperimen",
        (
            "concept.measurable-space.standard-borel",
            "concept.conditional.version",
            "concept.conditional.regular-distribution",
        ),
    ),
    (
        "audit-klaim-probabilitas-bersyarat",
        "Audit klaim probabilitas bersyarat",
        (
            "concept.measurable-space.standard-borel",
            "concept.kernel.probability",
            "concept.conditional.regular-distribution",
            "concept.conditional.version",
            "concept.conditional.disintegration",
            "concept.conditional.null-conditioning-value",
        ),
    ),
    (
        "latihan-penguasaan-probabilitas-bersyarat-reguler",
        "Latihan penguasaan probabilitas bersyarat reguler",
        (
            "concept.kernel.probability",
            "concept.conditional.regular-distribution",
            "concept.conditional.version",
            "concept.conditional.disintegration",
            "concept.conditional.null-conditioning-value",
        ),
    ),
    (
        "hak-dan-provenans-probabilitas-bersyarat",
        "Hak dan provenans",
        (),
    ),
)
ORIGINAL_BRIDGE_03_NEW_CONCEPTS = {
    "concept.conditional.version": (
        "version of a conditional expectation, probability, or law"
    ),
    "concept.conditional.determining-class": (
        "countable determining class for probability measures"
    ),
    "concept.conditional.disintegration": "disintegration of a joint law",
    "concept.conditional.null-conditioning-value": (
        "version choice at a null conditioning value"
    ),
}
ORIGINAL_BRIDGE_03_OUTCOMES = {
    "outcome.o009.construct-regular-conditional-distribution": (
        "Membangun distribusi bersyarat reguler pada sasaran Borel standar "
        "dan menunjukkan tepat letak hipotesis keberadaannya.",
        "prove",
        [
            "concept.measurable-space.standard-borel",
            "concept.kernel.probability",
            "concept.conditional.regular-distribution",
            "concept.conditional.determining-class",
        ],
    ),
    "outcome.o009.audit-conditional-version-uniqueness": (
        "Membedakan keunikan untuk satu kejadian, keunikan kernel di luar "
        "satu himpunan nol, dan pilihan versi pada nilai pengondisian nol.",
        "analyze",
        [
            "concept.conditional.version",
            "concept.conditional.determining-class",
            "concept.conditional.null-conditioning-value",
        ],
    ),
    "outcome.o009.derive-disintegration-and-null-value-versions": (
        "Menurunkan kernel dari hukum gabungan atau kepadatan, memverifikasi "
        "rumus disintegrasi, dan menangani nilai pengondisian bermassa nol.",
        "apply",
        [
            "concept.kernel.density",
            "concept.conditional.regular-distribution",
            "concept.conditional.disintegration",
            "concept.conditional.null-conditioning-value",
        ],
    ),
}
ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS = tuple(
    f"unit.o009.original.mastery.regular-conditional-probability.{index:02d}"
    for index in range(1, 4)
)
ORIGINAL_BRIDGE_03_MASTERY_SUFFIXES = ORIGINAL_BRIDGE_MASTERY_SUFFIXES

ORIGINAL_BRIDGE_04_SOURCE = (
    ROOT / "source" / "original" / "04-audit-hipotesis-proses-stokastik.md"
)
ORIGINAL_BRIDGE_04_READER = (
    ROOT
    / "build"
    / "site"
    / "original"
    / "04-audit-hipotesis-proses-stokastik.html"
)
ORIGINAL_BRIDGE_04_MASTERY_LEDGER = (
    ROOT / "qa" / "ORIGINAL_BRIDGE_04_MASTERY_LEDGER.json"
)
ORIGINAL_BRIDGE_04_SOURCE_BYTES = 39925
ORIGINAL_BRIDGE_04_SOURCE_SHA256 = (
    "be6de4f7b2fc63bbfee8be51b3dd8ac733edff5d58374c7a71891d0ab20d4bfd"
)
ORIGINAL_BRIDGE_04_UNIT_ID = "unit.o009.original.bridge.hypothesis-audits"
ORIGINAL_BRIDGE_04_RIGHTS_ID = (
    "rights.o009.original.bridge.hypothesis-audits.cc-by-4.0"
)
ORIGINAL_BRIDGE_04_PATH = "original/04-audit-hipotesis-proses-stokastik.html"
ORIGINAL_BRIDGE_04_SECTION_SPECS = (
    (
        "tujuan-dan-protokol-audit-hipotesis",
        "Tujuan dan protokol audit hipotesis",
        ("concept.probability.hypothesis-audit",),
    ),
    (
        "audit-konvergensi-dan-integrabilitas",
        "Audit konvergensi dan keterintegralan",
        (
            "concept.probability.hypothesis-audit",
            "concept.probability.almost-sure-convergence",
            "concept.probability.convergence-in-probability",
            "concept.probability.convergence-in-distribution",
            "concept.probability.lp-convergence",
            "concept.expectation.uniform-integrability",
        ),
    ),
    (
        "audit-pengondisian-dan-kernel",
        "Audit pengondisian dan kernel",
        (
            "concept.probability.hypothesis-audit",
            "concept.conditional.expectation",
            "concept.conditional.probability",
            "concept.kernel.probability",
            "concept.conditional.regular-distribution",
            "concept.conditional.version",
        ),
    ),
    (
        "audit-martingal-dan-waktu-henti",
        "Audit martingal dan waktu henti",
        (
            "concept.probability.hypothesis-audit",
            "concept.martingale.optional-stopping",
            "concept.stochastic.stopping-time",
            "concept.stochastic.stopped-process",
            "concept.expectation.uniform-integrability",
        ),
    ),
    (
        "audit-markov-dan-ctmc",
        "Audit rantai Markov waktu diskret dan waktu kontinu (CTMC)",
        (
            "concept.probability.hypothesis-audit",
            "concept.markov.irreducibility",
            "concept.markov.aperiodic-state",
            "concept.markov.stationary-distribution",
            "concept.markov.intensity-matrix",
            "concept.markov.nonexplosion",
            "concept.markov.transition-semigroup",
            "concept.semigroup.generator",
        ),
    ),
    (
        "audit-poisson-dan-konstruksi-proses",
        "Audit objek Poisson dan konstruksi proses",
        (
            "concept.probability.hypothesis-audit",
            "concept.poisson.process",
            "concept.poisson.random-measure",
            "concept.poisson.intensity-measure",
            "concept.stochastic.process.kolmogorov-extension",
        ),
    ),
    (
        "audit-brown-dan-hukum-lintasan",
        "Audit gerak Brown dan hukum lintasan",
        (
            "concept.probability.hypothesis-audit",
            "concept.brownian.gaussian-finite-dimensional-laws",
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.regular-path-space-law",
            "concept.stochastic.process.path-law-tightness",
            "concept.probability.continuous-mapping-theorem",
        ),
    ),
    (
        "matriks-perbaikan-klaim",
        "Matriks perbaikan klaim",
        ("concept.probability.hypothesis-audit",),
    ),
    (
        "latihan-penguasaan-audit-hipotesis",
        "Latihan penguasaan audit hipotesis",
        (
            "concept.probability.hypothesis-audit",
            "concept.expectation.uniform-integrability",
            "concept.martingale.optional-stopping",
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.regular-path-space-law",
            "concept.stochastic.process.path-law-tightness",
            "concept.probability.continuous-mapping-theorem",
        ),
    ),
    (
        "hak-dan-provenans-audit-hipotesis",
        "Hak dan provenans",
        (),
    ),
)
ORIGINAL_BRIDGE_04_NEW_CONCEPTS = {
    "concept.probability.hypothesis-audit": (
        "five-field hypothesis audit for a probability or stochastic-process claim"
    ),
    "concept.stochastic.process.path-law-tightness": (
        "tightness of probability laws on a stochastic-process path space"
    ),
    "concept.probability.continuous-mapping-theorem": (
        "continuous mapping theorem for weak convergence"
    ),
}
ORIGINAL_BRIDGE_04_OUTCOMES = {
    "outcome.o009.audit-and-repair-stochastic-process-claims": (
        "Mengaudit objek, latar, hipotesis, kesimpulan, dan saksi kegagalan "
        "suatu klaim proses stokastik, lalu menyatakan satu perbaikan cukup "
        "yang eksplisit.",
        "analyze",
        ["concept.probability.hypothesis-audit"],
    ),
    "outcome.o009.audit-fdd-versus-path-law-convergence": (
        "Membedakan konvergensi distribusi berdimensi hingga dari konvergensi "
        "lemah hukum lintasan dengan memeriksa keketatan dan gerbang teorema "
        "pemetaan kontinu.",
        "analyze",
        [
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.regular-path-space-law",
            "concept.stochastic.process.path-law-tightness",
            "concept.probability.continuous-mapping-theorem",
        ],
    ),
}
ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS = tuple(
    f"unit.o009.original.mastery.hypothesis-audits.{index:02d}"
    for index in range(1, 4)
)
ORIGINAL_BRIDGE_04_MASTERY_SUFFIXES = ORIGINAL_BRIDGE_MASTERY_SUFFIXES

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
    {
        "rel": "martingales/Backwards.html",
        "slug": "martingales.backwards",
        "order": 14,
        "concept_ids": [
            "concept.martingale.reverse",
            "concept.stochastic.decreasing-filtration",
            "concept.martingale.reverse-time-transform",
            "concept.martingale.doob-reverse",
            "concept.martingale.reverse-convergence",
            "concept.martingale.reverse-lp-convergence",
            "concept.probability.strong-law",
            "concept.probability.exchangeability",
            "concept.probability.conditional-iid",
            "concept.probability.de-finetti",
            "concept.probability.mixture-model",
            "concept.probability.hypergeometric",
        ],
    },
    {
        "rel": "markov/General.html",
        "slug": "markov.general",
        "order": 15,
        "concept_ids": [
            "concept.markov.process",
            "concept.markov.transition-kernel",
            "concept.markov.transition-semigroup",
            "concept.markov.feller-process",
            "concept.markov.strong-property",
            "concept.markov.chapman-kolmogorov",
            "concept.stochastic.stationary-independent-increments",
            "concept.stochastic.levy-process",
            "concept.poisson.process",
            "concept.brownian.motion",
        ],
    },
    {
        "rel": "markov/Discrete.html",
        "slug": "markov.discrete",
        "order": 16,
        "concept_ids": [
            "concept.markov.chain.discrete-time",
            "concept.markov.chain.time-homogeneous",
            "concept.stochastic.stopping-time",
            "concept.stochastic.entrance-time",
            "concept.markov.strong-property",
            "concept.markov.transition-matrix",
            "concept.markov.chapman-kolmogorov",
            "concept.markov.invariant-distribution",
            "concept.markov.state-graph",
            "concept.markov.potential-matrix",
            "concept.markov.sampled-chain",
            "concept.markov.restricted-transition-matrix",
            "concept.stochastic.random-walk",
            "concept.markov.doubly-stochastic-matrix",
        ],
    },
    {
        "rel": "markov/Recurrence.html",
        "slug": "markov.recurrence",
        "order": 17,
        "concept_ids": [
            "concept.stochastic.hitting-time",
            "concept.markov.hitting-probability",
            "concept.markov.hitting-matrix",
            "concept.markov.recurrence",
            "concept.markov.transience",
            "concept.markov.visit-count",
            "concept.markov.green-matrix",
            "concept.markov.accessibility",
            "concept.markov.communicating-class",
            "concept.markov.irreducibility",
            "concept.markov.canonical-decomposition",
            "concept.markov.staying-probability",
        ],
    },
    {
        "rel": "markov/Periodicity.html",
        "slug": "markov.periodicity",
        "order": 18,
        "concept_ids": [
            "concept.markov.period",
            "concept.markov.periodic-state",
            "concept.markov.aperiodic-state",
            "concept.markov.cyclic-class",
            "concept.number-theory.modular-congruence",
            "concept.markov.communicating-class",
            "concept.markov.irreducibility",
            "concept.markov.sampled-chain",
            "concept.markov.transition-matrix",
            "concept.markov.state-graph",
            "concept.stochastic.random-walk",
        ],
    },
    {
        "rel": "markov/Limiting.html",
        "slug": "markov.limiting",
        "order": 19,
        "concept_ids": [
            "concept.renewal.process",
            "concept.markov.visit-count",
            "concept.markov.green-matrix",
            "concept.markov.hitting-probability",
            "concept.markov.mean-return-time",
            "concept.markov.occupation-frequency",
            "concept.markov.cesaro-transition-limit",
            "concept.markov.limiting-distribution",
            "concept.markov.positive-recurrence",
            "concept.markov.null-recurrence",
            "concept.markov.ergodic-chain",
            "concept.markov.invariant-distribution",
            "concept.markov.invariant-measure",
            "concept.markov.period",
            "concept.markov.cyclic-class",
            "concept.markov.irreducibility",
        ],
    },
    {
        "rel": "poisson/General.html",
        "slug": "poisson.general",
        "order": 28,
        "authority_sha256": "cdc957a1fb433c343ee4654af5350259baf15fcc37acbb4acf2c5a50077b6567",
        "concept_ids": [
            "concept.poisson.process",
            "concept.poisson.random-measure",
            "concept.poisson.intensity-measure",
            "concept.poisson.conditional-point-law",
            "concept.probability.multinomial-distribution",
            "concept.poisson.thinning",
            "concept.poisson.superposition",
            "concept.poisson.nonhomogeneous-mean-measure",
            "concept.poisson.nearest-neighbor-distance",
        ],
        "required_correction_ids": [
            "poisson-general-set-domain",
            "poisson-general-heading-number",
            "poisson-general-single-point-finite-measure",
            "poisson-general-binomial-finite-measure",
            "poisson-general-multinomial-finite-measure",
            "poisson-count-pmf-terminology",
            "thinning-rate-order",
            "thinning-conditioning-event",
            "thinning-finite-measure-proof-domain",
            "thinning-proof-rate-labels",
            "thinning-process-independence-argument",
            "superposition-process-index",
            "superposition-count-index",
            "superposition-index-set",
            "superposition-finite-infinite-measure-proof",
            "nonhomogeneous-independent-increments",
            "nonhomogeneous-unit-density",
            "euclidean-space-symbol",
            "euclidean-norm-definition",
            "euclidean-ball-norm",
            "exercise4-contained-circle-assumption",
        ],
    },
    {
        "rel": "brown/Standard.html",
        "slug": "brown.standard",
        "order": 29,
        "authority_sha256": "442b4dacc55ce0ffc49fff5093ee2ad5adb75d337d45908e5e0df1448d84ebd8",
        "concept_ids": [
            "concept.brownian.motion",
            "concept.brownian.standard-motion",
            "concept.brownian.gaussian-finite-dimensional-laws",
            "concept.brownian.self-similarity",
            "concept.brownian.path-irregularity",
            "concept.brownian.reflection-principle",
            "concept.brownian.running-maximum",
            "concept.brownian.hitting-time-law",
            "concept.brownian.zero-set",
            "concept.brownian.arcsine-law",
            "concept.brownian.iterated-logarithm",
            "concept.markov.strong-property",
            "concept.martingale",
            "concept.stochastic.hitting-time",
        ],
        "required_correction_ids": [
            "favicon-svg-mime",
            "offline-simulator-accessible-controls",
            "continuous-version-proof",
            "finite-dimensional-time-order",
            "gaussian-process-time-domain",
            "brownian-correlation-max-domain",
            "normal-mgf-square",
            "time-reversal-covariance",
            "brownian-scaling-mean",
            "self-similarity-law-not-path",
            "holder-exponent-scope-endpoint",
            "brownian-graph-dimension-scope",
            "brownian-total-variation-domain-scope",
            "markov-proof-truncated-filtration",
            "strong-markov-filtration-scope",
            "strong-markov-finite-stopping-time",
            "conditional-second-moment-square",
            "hitting-time-and-running-maximum-definition",
            "recurrence-proof-reference",
            "hitting-filtration-subscript",
            "half-normal-scale-parameter",
            "half-normal-scale-proof",
            "hitting-reflection-finite-stopping-scope",
            "arcsine-zero-event-proof",
            "arcsine-complement-delimiter",
            "last-zero-event-endpoint",
            "arcsine-variance-label",
            "zero-set-perfect-proof",
            "zero-set-dimension-scope",
            "iterated-logarithm-two-sided",
            "brownian-motion-apps-explicit-online",
            "random-walk-app-explicit-online",
            "reflected-brownian-apps-explicit-online",
            "reflected-brownian-process-app-explicit-online",
            "special-distribution-apps-explicit-online",
            "brownian-simulation-app-explicit-online",
            "brownian-zero-app-explicit-online",
        ],
    },
    {
        "rel": "brown/Drift.html",
        "slug": "brown.drift",
        "order": 30,
        "authority_sha256": "f1603646520d3c83fa986e6b0be7bcac6862d7443e57d0a28264534da3dc70d5",
        "target_sha256": "7957d796d47ae31d74e1f0ae9733eac7df22f2ccd3311d5195c4cf948dcb9936",
        "concept_ids": [
            "concept.brownian.motion",
            "concept.brownian.standard-motion",
            "concept.brownian.drift-and-scale",
            "concept.brownian.gaussian-finite-dimensional-laws",
            "concept.brownian.affine-scaling",
            "concept.brownian.transition-density",
            "concept.brownian.diffusion-equations",
            "concept.markov.strong-property",
            "concept.stochastic.stopping-time",
        ],
        "required_correction_ids": [
            "favicon-svg-mime",
            "explicit-online-app",
            "marginal-density-and-fdd-scope",
            "finite-dimensional-time-order",
            "brown-drift-correlation",
            "nontrivial-scaling-qualification",
            "markov-initial-law-clarification",
            "restarted-process-parameters",
            "stopping-sigma-algebra-and-finiteness",
            "strong-markov-filtration-proof",
        ],
    },
    {
        "rel": "brown/Bridge.html",
        "slug": "brown.bridge",
        "order": 31,
        "authority_sha256": "62e8b18c32f191f801e4cb9be3ee0db3fb658329d937b0807c6d8b8d7b37410e",
        "target_sha256": "8af8c9da98203455a19181a4609cd52fe39787bcc7c21e607c92bf1b4235cc1a",
        "concept_ids": [
            "concept.brownian.motion",
            "concept.brownian.standard-motion",
            "concept.brownian.bridge",
            "concept.brownian.bridge-time-change",
            "concept.brownian.gaussian-finite-dimensional-laws",
            "concept.brownian.regular-conditioning",
            "concept.brownian.empirical-process",
            "concept.statistics.empirical-distribution-function",
            "concept.conditional.regular-distribution",
            "concept.stochastic.process.finite-dimensional-distributions",
        ],
        "required_correction_ids": [
            "favicon-svg-mime",
            "local-section-number",
            "explicit-online-apps",
            "expectation-macro",
            "time-change-expectation-domain",
            "time-change-endpoint-mean",
            "time-change-tab-normalization",
            "inverse-time-change-domain",
            "regular-conditional-law",
            "stochastic-integral-domain",
            "stochastic-integral-endpoint-covariance",
            "stochastic-differential-sign",
            "edf-consistency-mode",
            "edf-covariance-comma",
        ],
    },
    {
        "rel": "brown/Geometric.html",
        "slug": "brown.geometric",
        "order": 32,
        "authority_sha256": "4a6c1fa4c4d1cd7d646f700d438201af2b75fead1f094ecb4720d2831343f6ce",
        "target_sha256": "8404e8ac8caaa41699d8f2e623a890f991cc208d63200bfdef6c636640fecf0e",
        "concept_ids": [
            "concept.brownian.motion",
            "concept.brownian.standard-motion",
            "concept.brownian.geometric-motion",
            "concept.brownian.geometric-sde",
            "concept.probability.lognormal-distribution",
            "concept.brownian.geometric-moments",
            "concept.brownian.geometric-asymptotics",
            "concept.brownian.exponential-martingale",
        ],
        "required_correction_ids": [
            "favicon-svg-mime",
            "local-section-number",
            "explicit-online-apps",
            "density-mode-subscript",
            "density-inflection-subscript",
            "lognormal-inflection-center",
            "cdf-nonpositive-domain",
            "quantile-unit-id",
            "positive-moment-order",
            "asymptotic-equality-case",
            "mean-standard-deviation-spacing",
            "final-property-id",
            "stochastic-integral-square-integrability",
        ],
    },
    {
        "rel": "martingales/index.html",
        "slug": "martingales.index",
        "order": 33,
        "authority_sha256": "92b98c9e04ad843647041974d54ba6557aedf51d393ff540af4f27a868aa791e",
        "target_sha256": "61a0cf06004de06d9afb5869426c8319cca9f3cbacbf6ed6832691dadabcfa33",
        "unit_kind": "overview",
        "concept_ids": [
            "concept.martingale",
            "concept.martingale.submartingale",
            "concept.martingale.supermartingale",
            "concept.stochastic.stopping-time",
        ],
    },
    {
        "rel": "markov/index.html",
        "slug": "markov.index",
        "order": 34,
        "authority_sha256": "18dfcf15b97a2af7d90404e879376234865bfb40985deb4d6e50b9778f5f7660",
        "target_sha256": "b2948f92824eebb77f05bd0ebf2117d476fc4ae4f2c9cbbc3ad4ab37f73e0e7f",
        "unit_kind": "overview",
        "concept_ids": [
            "concept.markov.process",
            "concept.markov.chain.discrete-time",
            "concept.markov.transition-kernel",
            "concept.markov.invariant-distribution",
            "concept.markov.recurrence",
        ],
    },
    {
        "rel": "brown/index.html",
        "slug": "brown.index",
        "order": 35,
        "authority_sha256": "c471c5a1b2bd85731eded48e1ba7a0337c1b752b56fcadde87e213eacf2a7b4a",
        "target_sha256": "3f16a19194aeffe6cf6e5e6d98765f4aacbe743933fcf5365b0012438c8804a0",
        "unit_kind": "overview",
        "concept_ids": [
            "concept.brownian.motion",
            "concept.brownian.standard-motion",
            "concept.brownian.bridge",
            "concept.brownian.geometric-motion",
        ],
    },
)

OVERVIEW_CHILDREN = {
    "martingales.index": (
        ("martingales.introduction", "Introduction.html"),
        ("martingales.properties", "Properties.html"),
        ("martingales.stop", "Stop.html"),
        ("martingales.inequalities", "Inequalities.html"),
        ("martingales.convergence", "Convergence.html"),
        ("martingales.backwards", "Backwards.html"),
    ),
    "markov.index": (
        ("markov.general", "General.html"),
        ("markov.discrete", "Discrete.html"),
        ("markov.recurrence", "Recurrence.html"),
        ("markov.periodicity", "Periodicity.html"),
        ("markov.limiting", "Limiting.html"),
    ),
    "brown.index": (
        ("brown.standard", "Standard.html"),
        ("brown.drift", "Drift.html"),
        ("brown.bridge", "Bridge.html"),
        ("brown.geometric", "Geometric.html"),
    ),
}

SEMANTIC_KIND_OVERRIDES = {
    ("markov.discrete", unit_id): "exercise"
    for unit_id in ("com1", "com2", "com3", "com4", "ind3", "dbl4", "dbl6")
}
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("markov.discrete", details_id): "solution"
        for details_id in (
            "details-015",
            "details-016",
            "details-017",
            "details-018",
            "details-025",
            "details-028",
            "details-030",
        )
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("brown.bridge", "def1"): "definition",
        ("brown.bridge", "def2"): "construction-theorem",
        ("brown.bridge", "def3"): "application",
        ("brown.bridge", "def4"): "application",
        ("brown.bridge", "def5"): "inverse-construction-theorem",
        ("brown.bridge", "def7"): "time-change-construction-theorem",
        ("brown.bridge", "def8"): "inverse-time-change-theorem",
        ("brown.bridge", "def6"): "regular-conditioning-theorem",
        ("brown.bridge", "div-009"): "stochastic-integral-construction-theorem",
        ("brown.bridge", "gen1"): "construction-theorem",
        ("brown.bridge", "gen2"): "characterization",
        ("brown.bridge", "edf1"): "estimation-theorem",
        ("brown.bridge", "edf2"): "covariance-theorem",
        **{
            ("brown.bridge", f"details-{index:03d}"): "proof"
            for index in range(1, 8)
        },
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("brown.geometric", "def1"): "definition",
        ("brown.geometric", "def2"): "stochastic-differential-equation",
        ("brown.geometric", "def3"): "application",
        ("brown.geometric", "dst1"): "distribution-theorem",
        ("brown.geometric", "dst2"): "application",
        ("brown.geometric", "dst3"): "distribution-function-theorem",
        ("brown.geometric", "dist4"): "quantile-theorem",
        ("brown.geometric", "mom1"): "moment-theorem",
        ("brown.geometric", "mom2"): "moment-corollary",
        ("brown.geometric", "mom3"): "mean-asymptotics",
        ("brown.geometric", "mom4"): "application",
        ("brown.geometric", "mom5"): "application",
        ("brown.geometric", "prp1"): "path-asymptotics",
        ("brown.geometric", "div-014"): "martingale-theorem",
        **{
            ("brown.geometric", f"details-{index:03d}"): "proof"
            for index in range(1, 7)
        },
    }
)
SEMANTIC_KIND_OVERRIDES[("brown.standard", "div-050")] = "exercise"
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("brown.drift", "def1"): "definition",
        ("brown.drift", "def2"): "application",
        ("brown.drift", "def3"): "characterization",
        ("brown.drift", "dis1"): "theorem",
        ("brown.drift", "dis2"): "theorem",
        ("brown.drift", "trn1"): "transformation-rule",
        ("brown.drift", "trn2"): "scaling-law",
        ("brown.drift", "trn3"): "stationary-increment-theorem",
        ("brown.drift", "mar1"): "transition-density-theorem",
        ("brown.drift", "mar2"): "diffusion-equation-theorem",
        ("brown.drift", "mar3"): "strong-markov-theorem",
        **{
            ("brown.drift", f"details-{index:03d}"): "proof"
            for index in range(1, 8)
        },
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("markov.recurrence", unit_id): "exercise"
        for unit_id in ("fin1", "fin2", "fin3")
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("markov.recurrence", details_id): "solution"
        for details_id in ("details-025", "details-026", "details-027")
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("markov.periodicity", unit_id): "exercise"
        for unit_id in ("fin1", "fin3")
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("markov.periodicity", details_id): "solution"
        for details_id in ("details-004", "details-005")
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("markov.limiting", unit_id): "exercise"
        for unit_id in ("div-023", "fin1", "fin2", "fin3", "fin4", "fin5")
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("markov.limiting", details_id): "solution"
        for details_id in (
            "details-018",
            "details-019",
            "details-020",
            "details-021",
            "details-022",
        )
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("poisson.general", exercise_id): "exercise"
        for exercise_id in ("exe1", "exe2", "exe3", "exe4", "exe5", "exe6")
    }
)
SEMANTIC_KIND_OVERRIDES.update(
    {
        ("poisson.general", details_id): "solution"
        for details_id in (
            "details-008",
            "details-009",
            "details-010",
            "details-011",
            "details-012",
            "details-013",
        )
    }
)

SCHEMA = "o009.backend.entity.v2"
MANIFEST_SCHEMA = "o009.backend-manifest.v2"
WORKFLOW = "o009-id-production"
CSV_LINE_TERMINATOR = "\n"
CSV_LINE_ENDING_NAME = "LF"
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
    "alternate-form",
    "contains",
    "depends-on",
    "prerequisite",
    "hints",
    "answers",
    "solves",
    "executes",
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


def validate_site_manifest_inventory() -> dict[str, str]:
    site = BUILD_MANIFEST.parent
    if not site.is_dir() or site.is_symlink():
        raise RuntimeError("build/site is missing or linked")
    manifest_bytes = require_file(BUILD_MANIFEST)
    receipt = load_json(BUILD_RECEIPT)
    manifest_sha = sha256(manifest_bytes)
    if receipt.get("manifest_sha256") != manifest_sha:
        raise RuntimeError("site build receipt does not bind the live package manifest")
    text = manifest_bytes.decode("utf-8")
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames != ["path", "bytes", "sha256"]:
        raise RuntimeError("site package manifest columns differ")
    listed = list(reader)
    listed_paths: set[str] = set()
    for row in listed:
        raw_path = str(row.get("path", ""))
        path = Path(raw_path)
        if (
            not raw_path
            or path.is_absolute()
            or path.drive
            or path.as_posix() != raw_path
            or any(part in {"", ".", ".."} for part in path.parts)
            or raw_path in listed_paths
        ):
            raise RuntimeError(f"unsafe or duplicate site manifest path: {raw_path!r}")
        listed_paths.add(raw_path)
        try:
            byte_count = int(str(row.get("bytes", "")))
        except ValueError as exc:
            raise RuntimeError(f"invalid site manifest byte count: {raw_path}") from exc
        if byte_count < 0 or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", ""))):
            raise RuntimeError(f"invalid site manifest identity: {raw_path}")

    entries = list(site.rglob("*"))
    linked = [path.relative_to(site).as_posix() for path in entries if path.is_symlink()]
    if linked:
        raise RuntimeError(f"site contains symbolic links: {linked}")
    excluded = {"PACKAGE_MANIFEST.csv", "BUILD_RECEIPT.json"}
    paths = [
        path
        for path in entries
        if path.is_file() and path.relative_to(site).as_posix() not in excluded
    ]
    paths.sort(key=lambda path: path.relative_to(site).as_posix().casefold())
    actual = []
    for path in paths:
        data = path.read_bytes()
        actual.append(
            {
                "path": path.relative_to(site).as_posix(),
                "bytes": str(len(data)),
                "sha256": sha256(data),
            }
        )
    if listed != actual:
        listed_by_path = {row["path"]: row for row in listed}
        actual_by_path = {row["path"]: row for row in actual}
        raise RuntimeError(
            "site package manifest does not match live site bytes: "
            f"missing={sorted(set(listed_by_path) - set(actual_by_path))}; "
            f"unexpected={sorted(set(actual_by_path) - set(listed_by_path))}; "
            f"changed={sorted(path for path in set(listed_by_path) & set(actual_by_path) if listed_by_path[path] != actual_by_path[path])}"
        )
    if receipt.get("file_count") != len(actual) or receipt.get("total_bytes") != sum(
        int(row["bytes"]) for row in actual
    ):
        raise RuntimeError("site build receipt inventory totals differ from live site bytes")
    return {row["path"]: row["sha256"] for row in actual}


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
        r'^> \*\*Asal komponen dan lisensi\.\*\*.*?^> .*CC BY 4\.0\.$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    if metadata is None or notice is None:
        raise RuntimeError("lab rights witness text is missing or changed")
    return metadata.group(0) + "\n" + notice.group(0) + "\n"


def original_lab_rights_witness(text: str) -> str:
    """Bind one wholly original lab to its local rights/model notice."""
    metadata = re.search(
        r'^  donor_license: "none"\r?\n'
        r'  adaptation_license: "CC-BY-4\.0"\r?\n'
        r'  model: "OpenAI Codex gpt-5\.6-sol, Ultra\."$',
        text,
        re.MULTILINE,
    )
    notice = re.search(
        r'^> \*\*Asal dan lisensi\.\*\*.*?'
        r'^> \*\*OpenAI Codex gpt-5\.6-sol, Ultra\.\*\*$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    if metadata is None or notice is None:
        raise RuntimeError("original lab rights/model witness text is missing or changed")
    return metadata.group(0) + "\n" + notice.group(0) + "\n"


def conditional_martingale_lab_rights_witness(text: str) -> str:
    """Bind Lab 04 to its exact authority, rights, model, and visible notice."""
    metadata = re.search(
        r'^  source_authority: "authority/random/RANDOM_AUTHORITY_RECEIPT\.json"\r?\n'
        r'^  source_authority_sha256: "ea3786a05f3a1ccf444818f17516ce85065c76759bfc8071d43fd8a98c643eb4"\r?\n'
        r'^  source_page_sha256: ".*"\r?\n'
        r'^  source_license_witness: ".*"\r?\n'
        r'^  source_relation: "original diagnostic informed by the cited theory pages; no source HTML bytes are copied"\r?\n'
        r'^  adaptation_license: "CC-BY-4\.0"\r?\n'
        r'^  model_provenance: "OpenAI Codex gpt-5\.6-sol, Ultra\."\r?\n'
        r'^  non_endorsement: ".*"$',
        text,
        re.MULTILINE,
    )
    notice = re.search(
        r'^> \*\*Asal konsep, hak, dan batasan\.\*\*.*?'
        r'^> Kyle Siegrist, Random, ataupun penulis sumber\.$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    if metadata is None or notice is None:
        raise RuntimeError(
            "conditional-martingale lab authority/rights/model witness is missing or changed"
        )
    exact_sources = {
        "expect/Conditional2.html": "98307993d76941808cc87b7d28dfd8b2e24325913471b07c3a350a52a54c87c2",
        "prob/Stop.html": "9d26e78a8ee2a5a14ade3708838298ef0ba51cf9cd9658602a4f26e73b68524d",
        "martingales/Properties.html": "0f8bc07eb5eda38e8d4f78e94ba71a7dae8e9b788278f9b6ed250b0f66dc3850",
        "martingales/Stop.html": "8d4c674bec0d19a253405dfe8c06e4b4062d6ef82330f945d50e2c494955a5af",
    }
    for rel, expected in exact_sources.items():
        if sha256(require_file(AUTH_RANDOM / "static" / Path(rel))) != expected:
            raise RuntimeError(
                f"conditional-martingale frozen Random authority differs: {rel}"
            )
        if f"{rel}={expected}" not in metadata.group(0):
            raise RuntimeError(
                f"conditional-martingale source-page metadata differs: {rel}"
            )
    return metadata.group(0) + "\n" + notice.group(0) + "\n"


def brownian_diagnostics_lab_rights_witness(text: str) -> str:
    """Bind Lab 05 to its exact authority, rights, model, and no-copy notice."""
    metadata = re.search(
        r'^  source_authority: "authority/random/RANDOM_AUTHORITY_RECEIPT\.json"\r?\n'
        r'^  source_authority_sha256: "ea3786a05f3a1ccf444818f17516ce85065c76759bfc8071d43fd8a98c643eb4"\r?\n'
        r'^  source_page_sha256: "brown/Standard\.html=3693677d4d4c75e7888f806a027fa25020babeb80c720bbb77ad6fd0c639276b"\r?\n'
        r'^  source_license_witness: "CC-BY-2\.0 and CC-BY-1\.0 witnesses are retained separately in RANDOM_AUTHORITY_RECEIPT\.json"\r?\n'
        r'^  source_relation: "wholly original diagnostic informed by the cited Random theory page and the shared O006/C140 CLT prerequisite; no Random HTML or O006 bytes are copied"\r?\n'
        r'^  adaptation_license: "CC-BY-4\.0"\r?\n'
        r'^  model_provenance: "OpenAI Codex gpt-5\.6-sol, Ultra\."\r?\n'
        r'^  non_endorsement: ".*"$',
        text,
        re.MULTILINE,
    )
    notice = re.search(
        r'^> \*\*Asal konsep, hak, dan batasan\.\*\*.*?'
        r'^> penulis sumber\.$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    prerequisite_notice = re.search(
        r'^> \*\*Prasyarat bersama\.\*\*.*?'
        r'^> ulang di sini\.$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    if metadata is None or notice is None or prerequisite_notice is None:
        raise RuntimeError(
            "Brownian-diagnostics lab authority/rights/model/no-copy witness is missing or changed"
        )
    if sha256(require_file(RANDOM_RECEIPT)) != (
        "ea3786a05f3a1ccf444818f17516ce85065c76759bfc8071d43fd8a98c643eb4"
    ):
        raise RuntimeError("Brownian-diagnostics Random authority receipt differs")
    if sha256(require_file(AUTH_RANDOM / "static" / "brown" / "Standard.html")) != (
        "442b4dacc55ce0ffc49fff5093ee2ad5adb75d337d45908e5e0df1448d84ebd8"
    ):
        raise RuntimeError("Brownian-diagnostics frozen Random authority page differs")
    if sha256(require_file(ROOT / "source" / "theory" / "brown" / "Standard.html")) != (
        "3693677d4d4c75e7888f806a027fa25020babeb80c720bbb77ad6fd0c639276b"
    ):
        raise RuntimeError("Brownian-diagnostics admitted Indonesian theory page differs")
    return (
        metadata.group(0)
        + "\n"
        + notice.group(0)
        + "\n"
        + prerequisite_notice.group(0)
        + "\n"
    )


def brown_drift_original_rights_witness() -> str:
    """Bind every authored Drift surface to its local CC BY 4.0 witness bytes."""
    build_module = load_build_validator()
    notes = {
        str(item["id"]): str(item["html"])
        for item in tuple(build_module.BROWN_DRIFT_READER_NOTES)
    }
    expected_notes = {
        "brown-drift-downstream-corrections",
        "brown-drift-offline-lab",
        "brown-drift-mastery",
    }
    if set(notes) != expected_notes:
        raise RuntimeError(
            "Brown Drift authored reader-note registry differs from the rights witness"
        )
    if "CC BY 4.0" not in notes["brown-drift-offline-lab"] or "CC BY 4.0" not in notes[
        "brown-drift-mastery"
    ]:
        raise RuntimeError("Brown Drift lab or mastery surface lacks its CC BY 4.0 notice")
    corrections = {
        str(item["id"]): item
        for item in tuple(build_module.BROWN_DRIFT_READER_CORRECTIONS)
    }
    strong_markov = corrections.get("strong-markov-filtration-proof")
    if strong_markov is None or 'id="brown-drift-strong-markov-proof"' not in str(
        strong_markov["new"]
    ):
        raise RuntimeError("Brown Drift strong-Markov correction lacks its authored proof")
    app_text = require_file(BROWN_DRIFT_OFFLINE_APP).decode("utf-8")
    if "Karya asli edisi O009/D30; CC BY 4.0." not in app_text:
        raise RuntimeError("Brown Drift offline app lacks its exact CC BY 4.0 header")
    parts = [
        *(f"reader-note:{stable_id}:{sha256(notes[stable_id].encode('utf-8'))}" for stable_id in sorted(notes)),
        f"strong-markov-proof:{sha256(str(strong_markov['new']).encode('utf-8'))}",
        f"offline-app:{sha256(app_text.encode('utf-8'))}",
    ]
    return "\n".join(parts) + "\n"


def brown_bridge_original_rights_witness() -> str:
    """Bind every authored Bridge surface to its local CC BY 4.0 witness bytes."""
    build_module = load_build_validator()
    notes = {
        str(item["id"]): str(item["html"])
        for item in tuple(build_module.BROWN_BRIDGE_READER_NOTES)
    }
    expected_notes = {
        "brown-bridge-downstream-corrections",
        "brown-bridge-offline-lab",
        "brown-bridge-mastery",
    }
    if set(notes) != expected_notes:
        raise RuntimeError(
            "Brown Bridge authored reader-note registry differs from the rights witness"
        )
    if any("CC BY 4.0" not in notes[stable_id] for stable_id in expected_notes):
        raise RuntimeError("Brown Bridge authored reader note lacks its CC BY 4.0 notice")
    app_text = require_file(BROWN_BRIDGE_OFFLINE_APP).decode("utf-8")
    expected_header = [
        "/*",
        " * Laboratorium luring jembatan Brown.",
        " * Karya asli edisi O009/D30; CC BY 4.0.",
        " */",
    ]
    if app_text.splitlines()[:4] != expected_header:
        raise RuntimeError("Brown Bridge offline app lacks its exact CC BY 4.0 header")
    parts = [
        *(
            f"reader-note:{stable_id}:{sha256(notes[stable_id].encode('utf-8'))}"
            for stable_id in sorted(notes)
        ),
        f"offline-app:{sha256(app_text.encode('utf-8'))}",
    ]
    return "\n".join(parts) + "\n"


def brown_geometric_original_rights_witness() -> str:
    """Bind every authored Geometric surface to its local CC BY 4.0 witness bytes."""
    build_module = load_build_validator()
    notes = {
        str(item["id"]): str(item["html"])
        for item in tuple(build_module.BROWN_GEOMETRIC_READER_NOTES)
    }
    expected_notes = {
        "geometric-brownian-downstream-corrections",
        "geometric-brownian-offline-lab",
        "geometric-brownian-mastery",
    }
    if set(notes) != expected_notes:
        raise RuntimeError(
            "Brown Geometric authored reader-note registry differs from the rights witness"
        )
    if any("CC BY 4.0" not in notes[stable_id] for stable_id in expected_notes):
        raise RuntimeError(
            "Brown Geometric authored reader note lacks its CC BY 4.0 notice"
        )
    app_text = require_file(BROWN_GEOMETRIC_OFFLINE_APP).decode("utf-8")
    expected_header = [
        "/*",
        " * Laboratorium luring gerak Brown geometrik.",
        " * Karya asli edisi O009/D30; CC BY 4.0.",
        " */",
    ]
    if app_text.splitlines()[:4] != expected_header:
        raise RuntimeError(
            "Brown Geometric offline app lacks its exact CC BY 4.0 header"
        )
    parts = [
        *(
            f"reader-note:{stable_id}:{sha256(notes[stable_id].encode('utf-8'))}"
            for stable_id in sorted(notes)
        ),
        f"offline-app:{sha256(app_text.encode('utf-8'))}",
    ]
    return "\n".join(parts) + "\n"


def fixed_entities(
    lab_text: str,
    markov_lab_text: str,
    convergence_modes_lab_text: str,
    conditional_martingale_lab_text: str,
    brownian_diagnostics_lab_text: str,
) -> list[dict[str, Any]]:
    random_receipt = load_json(RANDOM_RECEIPT)
    build_receipt = load_json(BUILD_RECEIPT)
    random_manifest_hash = sha256(require_file(RANDOM_MANIFEST))
    if random_receipt.get("manifest_sha256") != random_manifest_hash:
        raise RuntimeError("Random authority receipt does not bind its current manifest")
    adaptation_witness = lab_rights_witness(lab_text)
    markov_adaptation_witness = lab_rights_witness(markov_lab_text)
    convergence_modes_rights_witness = original_lab_rights_witness(
        convergence_modes_lab_text
    )
    conditional_martingale_rights_witness = (
        conditional_martingale_lab_rights_witness(
            conditional_martingale_lab_text
        )
    )
    brownian_diagnostics_rights_witness = brownian_diagnostics_lab_rights_witness(
        brownian_diagnostics_lab_text
    )
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
                "concept.probability.weak-law",
                "concept.probability.central-limit-theorem",
                "concept.probability.skorohod-representation",
                "concept.probability.scheffe",
                "concept.stochastic.process",
                "concept.stochastic.process.measurability",
                "concept.stochastic.process.equivalence",
                "concept.stochastic.process.finite-dimensional-distributions",
                "concept.stochastic.process.kolmogorov-extension",
                "concept.measure.product-sigma-algebra",
                "concept.measure.cylinder-set",
                "concept.measurable-space.standard-borel",
                "concept.stochastic.process.projective-consistency",
                "concept.stochastic.process.path-space",
                "concept.stochastic.process.canonical-process",
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
                "concept.martingale.reverse",
                "concept.stochastic.decreasing-filtration",
                "concept.martingale.reverse-time-transform",
                "concept.martingale.doob-reverse",
                "concept.martingale.reverse-convergence",
                "concept.martingale.reverse-lp-convergence",
                "concept.probability.strong-law",
                "concept.probability.conditional-iid",
                "concept.probability.de-finetti",
                "concept.probability.mixture-model",
                "concept.probability.hypergeometric",
                "concept.markov.process",
                "concept.markov.transition-kernel",
                "concept.markov.transition-semigroup",
                "concept.markov.feller-process",
                "concept.markov.strong-property",
                "concept.markov.chapman-kolmogorov",
                "concept.markov.chain.discrete-time",
                "concept.markov.chain.time-homogeneous",
                "concept.stochastic.entrance-time",
                "concept.markov.transition-matrix",
                "concept.markov.invariant-distribution",
                "concept.markov.state-graph",
                "concept.markov.potential-matrix",
                "concept.markov.sampled-chain",
                "concept.markov.restricted-transition-matrix",
                "concept.markov.doubly-stochastic-matrix",
                "concept.markov.mean-return-time",
                "concept.markov.occupation-frequency",
                "concept.markov.cesaro-transition-limit",
                "concept.markov.limiting-distribution",
                "concept.markov.positive-recurrence",
                "concept.markov.null-recurrence",
                "concept.markov.ergodic-chain",
                "concept.markov.invariant-measure",
                "concept.markov.period",
                "concept.markov.periodic-state",
                "concept.markov.aperiodic-state",
                "concept.markov.cyclic-class",
                "concept.number-theory.modular-congruence",
                "concept.stochastic.levy-process",
                "concept.poisson.process",
                "concept.poisson.random-measure",
                "concept.poisson.intensity-measure",
                "concept.poisson.conditional-point-law",
                "concept.probability.multinomial-distribution",
                "concept.poisson.thinning",
                "concept.poisson.superposition",
                "concept.poisson.nonhomogeneous-mean-measure",
                "concept.poisson.nearest-neighbor-distance",
                "concept.renewal.process",
                "concept.brownian.motion",
                "concept.brownian.standard-motion",
                "concept.brownian.drift-and-scale",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.brownian.affine-scaling",
                "concept.brownian.transition-density",
                "concept.brownian.diffusion-equations",
                "concept.brownian.self-similarity",
                "concept.brownian.path-irregularity",
                "concept.brownian.reflection-principle",
                "concept.brownian.running-maximum",
                "concept.brownian.hitting-time-law",
                "concept.brownian.zero-set",
                "concept.brownian.arcsine-law",
                "concept.brownian.iterated-logarithm",
                "concept.brownian.bridge",
                "concept.brownian.bridge-time-change",
                "concept.brownian.regular-conditioning",
                "concept.brownian.empirical-process",
                "concept.statistics.empirical-distribution-function",
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
            "rights.o009.lab.convergence-modes.cc-by-4.0",
            source_locator=(
                "source/labs/03-konvergensi-mode-dan-lln-clt.Rmd"
                "#o009-lab-convergence-modes"
            ),
            source_sha256=sha256(convergence_modes_rights_witness.encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "OpenAI Codex gpt-5.6-sol, Ultra., at the user's direction",
                "scope": "complete original convergence-modes/O006-comparison laboratory",
                "does_not_relicense_o006_bytes": True,
            },
        ),
        record(
            "rights",
            "rights.o009.lab.conditional-martingale.cc-by-4.0",
            source_locator=(
                "source/labs/04-nilai-harapan-bersyarat-martingal.Rmd"
                "#o009-lab-conditional-martingale"
            ),
            source_sha256=sha256(
                conditional_martingale_rights_witness.encode("utf-8")
            ),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "OpenAI Codex gpt-5.6-sol, Ultra., at the user's direction",
                "scope": (
                    "complete original conditional-expectation, martingale, and "
                    "optional-stopping diagnostic laboratory"
                ),
                "random_witness_rights_ids": [
                    "rights.random.cc-by-2.0.witness",
                    "rights.random.cc-by-1.0.witness",
                ],
                "does_not_relicense_random_source_bytes": True,
            },
        ),
        record(
            "rights",
            "rights.o009.lab.brownian-diagnostics.cc-by-4.0",
            source_locator=(
                "source/labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.Rmd"
                "#o009-lab-brownian-diagnostics"
            ),
            source_sha256=sha256(
                brownian_diagnostics_rights_witness.encode("utf-8")
            ),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "OpenAI Codex gpt-5.6-sol, Ultra., at the user's direction",
                "scope": (
                    "complete original Donsker, quadratic-variation, total-variation, "
                    "reflection, and Brownian hitting-time diagnostic laboratory"
                ),
                "random_witness_rights_ids": [
                    "rights.random.cc-by-2.0.witness",
                    "rights.random.cc-by-1.0.witness",
                ],
                "o006_dependency_only": True,
                "does_not_relicense_random_or_o006_source_bytes": True,
            },
        ),
        record(
            "rights",
            "rights.o009.brown-drift-original.cc-by-4.0",
            source_locator=(
                "scripts/build_first_boundary.py#BROWN_DRIFT_READER_NOTES;"
                "scripts/build_first_boundary.py#strong-markov-filtration-proof;"
                "source/original/brown-drift-offline.js"
            ),
            source_sha256=sha256(
                brown_drift_original_rights_witness().encode("utf-8")
            ),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": (
                    "original Brown Drift downstream note, offline lab and JavaScript, "
                    "mastery exercise/hint/solution, and strong-Markov proof addition"
                ),
                "does_not_relicense_random_source_bytes": True,
            },
        ),
        record(
            "rights",
            "rights.o009.brown-bridge-original.cc-by-4.0",
            source_locator=(
                "scripts/build_first_boundary.py#BROWN_BRIDGE_READER_NOTES;"
                "source/original/brown-bridge-offline.js"
            ),
            source_sha256=sha256(
                brown_bridge_original_rights_witness().encode("utf-8")
            ),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": (
                    "original Brown Bridge downstream note, offline lab and JavaScript, "
                    "process-limit warning, and mastery exercise/hint/solution"
                ),
                "does_not_relicense_random_source_bytes": True,
            },
        ),
        record(
            "rights",
            "rights.o009.brown-geometric-original.cc-by-4.0",
            source_locator=(
                "scripts/build_first_boundary.py#BROWN_GEOMETRIC_READER_NOTES;"
                "source/original/geometric-brownian-offline.js"
            ),
            source_sha256=sha256(
                brown_geometric_original_rights_witness().encode("utf-8")
            ),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": (
                    "original Brown Geometric downstream note, offline lab and "
                    "JavaScript, and mastery exercise/hint/solution"
                ),
                "does_not_relicense_random_source_bytes": True,
            },
        ),
        record(
            "rights",
            "rights.o009.markov.indonesian-adaptation.cc-by-4.0",
            source_locator="source/labs/02-simulasi-rantai-markov.Rmd#authoring-rights-and-attribution",
            source_sha256=sha256(markov_adaptation_witness.encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": "Indonesian translation and adaptation bytes in the Markov-chain lab",
                "donor_component_rights_id": "rights.zitkovic.donor.cc0-1.0",
                "does_not_relicense_donor_bytes": True,
            },
        ),
        record(
            "rights",
            "rights.o009.markov.original.cc-by-4.0",
            source_locator="source/labs/02-simulasi-rantai-markov.Rmd#authoring-rights-and-attribution",
            source_sha256=sha256(markov_adaptation_witness.encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": "original Indonesian additions in the Markov-chain lab",
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
        "concept.probability.weak-law": "weak law of large numbers",
        "concept.probability.central-limit-theorem": "central limit theorem",
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
        "concept.martingale.reverse": "reverse martingale",
        "concept.stochastic.decreasing-filtration": "decreasing family of sigma-algebras",
        "concept.martingale.reverse-time-transform": "reverse-time martingale transform",
        "concept.martingale.doob-reverse": "Doob reverse martingale",
        "concept.martingale.reverse-convergence": "reverse martingale convergence theorem",
        "concept.martingale.reverse-lp-convergence": "Lp convergence of reverse martingales",
        "concept.probability.strong-law": "strong law of large numbers",
        "concept.probability.conditional-iid": "conditionally independent and identically distributed sequence",
        "concept.probability.de-finetti": "de Finetti representation theorem",
        "concept.probability.mixture-model": "mixture of product measures",
        "concept.probability.hypergeometric": "hypergeometric sampling law",
        "concept.markov.process": "Markov process",
        "concept.markov.transition-kernel": "transition kernel of a Markov process",
        "concept.markov.transition-semigroup": "transition semigroup",
        "concept.markov.feller-process": "Feller process",
        "concept.markov.strong-property": "strong Markov property",
        "concept.markov.chapman-kolmogorov": "Chapman-Kolmogorov equation",
        "concept.markov.chain.discrete-time": "discrete-time Markov chain",
        "concept.markov.chain.time-homogeneous": "time-homogeneous Markov chain",
        "concept.stochastic.entrance-time": "entrance and first-positive hitting times",
        "concept.markov.transition-matrix": "transition matrix and its powers",
        "concept.markov.invariant-distribution": "invariant distribution of a Markov chain",
        "concept.markov.state-graph": "state graph of a Markov chain",
        "concept.markov.potential-matrix": "discounted potential matrix and resolvent",
        "concept.markov.sampled-chain": "chain sampled at deterministic times",
        "concept.markov.restricted-transition-matrix": "restricted substochastic transition matrix",
        "concept.markov.doubly-stochastic-matrix": "doubly stochastic transition matrix",
        "concept.markov.hitting-probability": "hitting probability",
        "concept.markov.hitting-matrix": "hitting matrix",
        "concept.markov.recurrence": "recurrence of a Markov-chain state",
        "concept.markov.transience": "transience of a Markov-chain state",
        "concept.markov.visit-count": "number of positive-time visits",
        "concept.markov.green-matrix": "Green matrix of expected positive-time visits",
        "concept.markov.accessibility": "accessibility relation on states",
        "concept.markov.communicating-class": "communicating equivalence class",
        "concept.markov.irreducibility": "irreducible closed class",
        "concept.markov.canonical-decomposition": "canonical transient-recurrent decomposition",
        "concept.markov.staying-probability": "probability of staying in a state subset forever",
        "concept.markov.mean-return-time": "mean return time to a Markov-chain state",
        "concept.markov.occupation-frequency": "long-run occupation frequency of a Markov-chain state",
        "concept.markov.cesaro-transition-limit": "Cesaro limit of transition probabilities",
        "concept.markov.limiting-distribution": "limiting distribution of a Markov chain",
        "concept.markov.positive-recurrence": "positive recurrence of a Markov-chain state or class",
        "concept.markov.null-recurrence": "null recurrence of a Markov-chain state or class",
        "concept.markov.ergodic-chain": "irreducible positive recurrent aperiodic Markov chain",
        "concept.markov.invariant-measure": "nonnegative invariant measure of a Markov chain",
        "concept.markov.period": "period of a Markov-chain state or communicating class",
        "concept.markov.periodic-state": "periodic state or irreducible Markov chain",
        "concept.markov.aperiodic-state": "aperiodic state or irreducible Markov chain",
        "concept.markov.cyclic-class": "cyclic class of a periodic irreducible Markov chain",
        "concept.number-theory.modular-congruence": "congruence modulo a positive integer",
        "concept.stochastic.levy-process": "Lévy process",
        "concept.poisson.process": "Poisson process",
        "concept.poisson.random-measure": "Poisson random measure on a measure space",
        "concept.poisson.intensity-measure": "intensity measure of a Poisson random measure",
        "concept.poisson.conditional-point-law": "conditional uniform, binomial, and multinomial point laws",
        "concept.probability.multinomial-distribution": "multinomial distribution",
        "concept.poisson.thinning": "independent thinning of a Poisson process",
        "concept.poisson.superposition": "superposition of independent Poisson processes",
        "concept.poisson.nonhomogeneous-mean-measure": "nonhomogeneous Poisson process represented by its mean measure",
        "concept.poisson.nearest-neighbor-distance": "nearest-neighbor distance laws for a spatial Poisson process",
        "concept.renewal.process": "renewal process",
        "concept.brownian.motion": "Brownian motion",
        "concept.brownian.standard-motion": "standard Brownian motion",
        "concept.brownian.drift-and-scale": "Brownian motion with drift and scale parameters",
        "concept.brownian.gaussian-finite-dimensional-laws": "Gaussian finite-dimensional laws of Brownian motion",
        "concept.brownian.affine-scaling": "space-time transformations of Brownian drift and scale",
        "concept.brownian.transition-density": "transition density of Brownian motion with drift",
        "concept.brownian.diffusion-equations": "forward and backward diffusion equations for Brownian motion with drift",
        "concept.brownian.self-similarity": "Brownian scaling and self-similarity in distribution",
        "concept.brownian.path-irregularity": "almost-sure path irregularity of Brownian motion",
        "concept.brownian.reflection-principle": "Brownian reflection principle",
        "concept.brownian.running-maximum": "running maximum of Brownian motion",
        "concept.brownian.hitting-time-law": "Brownian first-hitting-time law",
        "concept.brownian.zero-set": "zero set of Brownian motion",
        "concept.brownian.arcsine-law": "Brownian arcsine laws",
        "concept.brownian.iterated-logarithm": "law of the iterated logarithm for Brownian motion",
        "concept.brownian.bridge": "standard and endpoint-general Brownian bridge",
        "concept.brownian.bridge-time-change": "Brownian-bridge time-change and stochastic-integral constructions",
        "concept.brownian.regular-conditioning": "Brownian bridge as a regular conditional path law",
        "concept.brownian.empirical-process": "Brownian-bridge covariance structure of the empirical process",
        "concept.statistics.empirical-distribution-function": "empirical distribution function",
        "concept.brownian.geometric-motion": "geometric Brownian motion",
        "concept.brownian.geometric-sde": "stochastic differential equation for geometric Brownian motion",
        "concept.probability.lognormal-distribution": "lognormal distribution",
        "concept.brownian.geometric-moments": "moments of geometric Brownian motion",
        "concept.brownian.geometric-asymptotics": "almost-sure asymptotics of geometric Brownian motion",
        "concept.brownian.exponential-martingale": "discounted geometric-Brownian exponential martingale",
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
        "outcome.o009.distinguish-convergence-modes": (
            "Membedakan konvergensi hampir pasti, dalam probabilitas, dalam distribusi, dan dalam Lp melalui bukti serta diagnostik deterministik.",
            "analyze",
            [
                "concept.probability.almost-sure-convergence",
                "concept.probability.convergence-in-probability",
                "concept.probability.convergence-in-distribution",
                "concept.probability.lp-convergence",
                "concept.probability.weak-law",
                "concept.probability.central-limit-theorem",
            ],
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
        "outcome.o009.construct-reverse-martingales": (
            "Membangun martingal mundur dari keluarga aljabar-σ menurun dan mengubahnya menjadi martingal waktu maju.",
            "apply",
            [
                "concept.martingale.reverse",
                "concept.stochastic.decreasing-filtration",
                "concept.martingale.reverse-time-transform",
                "concept.martingale.doob-reverse",
            ],
        ),
        "outcome.o009.prove-reverse-martingale-convergence": (
            "Membuktikan konvergensi martingal mundur waktu diskret hampir pasti, dalam rata-rata, dan dalam Lp dengan syarat yang tepat.",
            "prove",
            [
                "concept.martingale.reverse-convergence",
                "concept.martingale.reverse-lp-convergence",
                "concept.expectation.uniform-integrability",
            ],
        ),
        "outcome.o009.derive-strong-law-reverse-martingale": (
            "Menurunkan hukum kuat bilangan besar dari struktur martingal mundur sambil menggunakan modul sampling bersama sebagai prasyarat.",
            "prove",
            [
                "concept.martingale.reverse",
                "concept.probability.strong-law",
            ],
        ),
        "outcome.o009.analyze-exchangeability-conditional-iid": (
            "Menganalisis pertukaran, keindependenan bersyarat, dan hukum hipergeometrik pada awalan barisan.",
            "analyze",
            [
                "concept.probability.exchangeability",
                "concept.probability.conditional-iid",
                "concept.probability.hypergeometric",
            ],
        ),
        "outcome.o009.prove-binary-de-finetti": (
            "Membuktikan representasi de Finetti biner sebagai campuran hukum Bernoulli dengan pengondisian yang sah.",
            "prove",
            [
                "concept.probability.de-finetti",
                "concept.probability.mixture-model",
                "concept.martingale.reverse-convergence",
            ],
        ),
        "outcome.o009.construct-markov-kernels": (
            "Menyusun kernel transisi, semigrup transisi, dan persamaan Chapman–Kolmogorov pada ruang keadaan yang sesuai.",
            "apply",
            [
                "concept.markov.transition-kernel",
                "concept.markov.transition-semigroup",
                "concept.markov.chapman-kolmogorov",
            ],
        ),
        "outcome.o009.audit-strong-markov-hypotheses": (
            "Memeriksa hipotesis ruang keadaan, sifat Feller, regularitas lintasan, dan filtrasi sebelum memakai sifat Markov kuat.",
            "analyze",
            [
                "concept.markov.feller-process",
                "concept.markov.strong-property",
            ],
        ),
        "outcome.o009.simulate-absorbing-markov-chain": (
            "Mensimulasikan rantai Markov menyerap secara deterministik dan membandingkan taksiran dengan peluang horizon serta peluang harmonik eksak.",
            "apply",
            [
                "concept.markov.process",
                "concept.markov.transition-kernel",
                "concept.monte-carlo",
            ],
        ),
        "outcome.o009.characterize-discrete-markov-chains": (
            "Mengkarakterisasi rantai Markov waktu diskret homogen melalui riwayat berprobabilitas positif dan keluarga matriks transisi yang konsisten.",
            "analyze",
            [
                "concept.markov.chain.discrete-time",
                "concept.markov.chain.time-homogeneous",
                "concept.markov.strong-property",
            ],
        ),
        "outcome.o009.compute-discrete-transition-laws": (
            "Menghitung matriks transisi beberapa langkah dan hukum berdimensi hingga dengan persamaan Chapman–Kolmogorov.",
            "apply",
            [
                "concept.markov.transition-matrix",
                "concept.markov.chapman-kolmogorov",
                "concept.markov.invariant-distribution",
            ],
        ),
        "outcome.o009.analyze-discrete-potential-and-restriction": (
            "Menganalisis matriks potensial, pengambilan sampel waktu, dan pembatasan substokastik suatu rantai diskret.",
            "analyze",
            [
                "concept.markov.potential-matrix",
                "concept.markov.sampled-chain",
                "concept.markov.restricted-transition-matrix",
            ],
        ),
        "outcome.o009.solve-finite-discrete-chain-models": (
            "Menyelesaikan model rantai hingga memakai graf keadaan, distribusi invarian, dan struktur stokastik ganda.",
            "apply",
            [
                "concept.markov.state-graph",
                "concept.markov.invariant-distribution",
                "concept.markov.doubly-stochastic-matrix",
            ],
        ),
        "outcome.o009.compute-markov-hitting-and-green-quantities": (
            "Menghitung probabilitas pencapaian, banyaknya kunjungan, serta matriks Green pada rantai Markov waktu diskret.",
            "apply",
            [
                "concept.stochastic.hitting-time",
                "concept.markov.hitting-probability",
                "concept.markov.hitting-matrix",
                "concept.markov.visit-count",
                "concept.markov.green-matrix",
            ],
        ),
        "outcome.o009.classify-markov-states-and-classes": (
            "Mengklasifikasikan keadaan dan kelas komunikasi sebagai transien atau rekuren serta menyusun dekomposisi kanonik.",
            "analyze",
            [
                "concept.markov.recurrence",
                "concept.markov.transience",
                "concept.markov.accessibility",
                "concept.markov.communicating-class",
                "concept.markov.irreducibility",
                "concept.markov.canonical-decomposition",
            ],
        ),
        "outcome.o009.analyze-markov-staying-probabilities": (
            "Menganalisis peluang bertahan sebagai solusi tetap matriks pembatasan dan menggunakannya untuk menguji rekurensi.",
            "analyze",
            [
                "concept.markov.staying-probability",
                "concept.markov.irreducibility",
                "concept.markov.recurrence",
            ],
        ),
        "outcome.o009.solve-finite-recurrence-models": (
            "Menyelesaikan model rantai berhingga melalui graf keadaan, kelas komunikasi, matriks pencapaian, dan matriks Green.",
            "apply",
            [
                "concept.markov.state-graph",
                "concept.markov.communicating-class",
                "concept.markov.hitting-matrix",
                "concept.markov.green-matrix",
            ],
        ),
        "outcome.o009.characterize-markov-periodicity": (
            "Mengkarakterisasi periode suatu keadaan dan membuktikan bahwa periodisitas merupakan sifat kelas komunikasi.",
            "analyze",
            [
                "concept.markov.period",
                "concept.markov.periodic-state",
                "concept.markov.aperiodic-state",
                "concept.markov.communicating-class",
            ],
        ),
        "outcome.o009.construct-markov-cyclic-decomposition": (
            "Menyusun kelas-kelas siklik suatu rantai irreduksibel periodik dan menghubungkannya dengan rantai langkah-d.",
            "prove",
            [
                "concept.markov.cyclic-class",
                "concept.number-theory.modular-congruence",
                "concept.markov.sampled-chain",
                "concept.markov.irreducibility",
            ],
        ),
        "outcome.o009.solve-finite-periodicity-models": (
            "Menentukan periode, pangkat matriks transisi, dan kelas siklik pada rantai Markov berhingga.",
            "apply",
            [
                "concept.markov.period",
                "concept.markov.transition-matrix",
                "concept.markov.state-graph",
                "concept.markov.cyclic-class",
            ],
        ),
        "outcome.o009.derive-markov-renewal-limits": (
            "Menurunkan frekuensi okupasi, rata-rata Cesàro probabilitas transisi, dan limit transisi aperiodik dari proses pembaruan yang tertanam.",
            "prove",
            [
                "concept.renewal.process",
                "concept.markov.visit-count",
                "concept.markov.green-matrix",
                "concept.markov.mean-return-time",
                "concept.markov.occupation-frequency",
                "concept.markov.cesaro-transition-limit",
                "concept.markov.limiting-distribution",
            ],
        ),
        "outcome.o009.classify-positive-null-recurrence": (
            "Mengklasifikasikan keadaan dan kelas sebagai rekuren positif, rekuren nol, atau transien melalui waktu kembali rata-rata.",
            "analyze",
            [
                "concept.markov.recurrence",
                "concept.markov.transience",
                "concept.markov.mean-return-time",
                "concept.markov.positive-recurrence",
                "concept.markov.null-recurrence",
            ],
        ),
        "outcome.o009.analyze-markov-ergodic-periodic-limits": (
            "Menganalisis distribusi limit rantai ergodik dan limit subsekuens rantai periodik melalui kelas-kelas siklik.",
            "analyze",
            [
                "concept.markov.ergodic-chain",
                "concept.markov.limiting-distribution",
                "concept.markov.period",
                "concept.markov.cyclic-class",
            ],
        ),
        "outcome.o009.characterize-markov-invariant-measures": (
            "Mengkarakterisasi distribusi dan ukuran invarian pada rantai rekuren, termasuk eksistensi, ketunggalan, dan campuran antarkelas.",
            "prove",
            [
                "concept.markov.invariant-distribution",
                "concept.markov.invariant-measure",
                "concept.markov.positive-recurrence",
                "concept.markov.null-recurrence",
            ],
        ),
        "outcome.o009.solve-finite-limiting-models": (
            "Menghitung distribusi invarian, waktu kembali rata-rata, dan matriks limit atau limit subsekuens pada rantai Markov berhingga.",
            "apply",
            [
                "concept.markov.transition-matrix",
                "concept.markov.invariant-distribution",
                "concept.markov.mean-return-time",
                "concept.markov.limiting-distribution",
                "concept.markov.state-graph",
                "concept.markov.cyclic-class",
            ],
        ),
        "outcome.o009.formulate-poisson-random-measures": (
            "Merumuskan ukuran acak Poisson pada ruang ukuran dan menghitung momen cacahannya dari ukuran intensitas.",
            "apply",
            [
                "concept.poisson.random-measure",
                "concept.poisson.intensity-measure",
                "concept.poisson.process",
            ],
        ),
        "outcome.o009.derive-conditional-poisson-point-laws": (
            "Menurunkan hukum seragam, binomial, dan multinomial bersyarat untuk lokasi titik-titik proses Poisson.",
            "prove",
            [
                "concept.poisson.conditional-point-law",
                "concept.probability.multinomial-distribution",
            ],
        ),
        "outcome.o009.analyze-poisson-thinning-superposition": (
            "Membuktikan hukum penipisan dan superposisi proses Poisson beserta parameter intensitas yang tepat.",
            "prove",
            [
                "concept.poisson.thinning",
                "concept.poisson.superposition",
                "concept.poisson.intensity-measure",
            ],
        ),
        "outcome.o009.analyze-spatial-poisson-models": (
            "Menganalisis proses Poisson takhomogen dan spasial, termasuk distribusi jarak titik terdekat, lalu menyelesaikan model cacahan ruang.",
            "analyze",
            [
                "concept.poisson.nonhomogeneous-mean-measure",
                "concept.poisson.nearest-neighbor-distance",
                "concept.poisson.process",
            ],
        ),
        "outcome.o009.characterize-standard-brownian-motion": (
            "Mengkarakterisasi gerak Brown standar melalui inkremen, kontinuitas, dan hukum Gaussian berdimensi hingga.",
            "analyze",
            [
                "concept.brownian.standard-motion",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.stochastic.process.finite-dimensional-distributions",
            ],
        ),
        "outcome.o009.analyze-brownian-scaling-irregularity": (
            "Menganalisis penskalaan distribusional dan regularitas lintasan gerak Brown.",
            "analyze",
            [
                "concept.brownian.self-similarity",
                "concept.brownian.path-irregularity",
            ],
        ),
        "outcome.o009.apply-brownian-strong-markov-reflection": (
            "Menerapkan sifat Markov kuat dan prinsip refleksi pada gerak Brown.",
            "apply",
            [
                "concept.brownian.reflection-principle",
                "concept.markov.strong-property",
                "concept.stochastic.stopping-time",
            ],
        ),
        "outcome.o009.derive-brownian-hitting-maximum-laws": (
            "Menurunkan hukum waktu pencapaian, maksimum berjalan, dan rekurensi gerak Brown.",
            "prove",
            [
                "concept.brownian.hitting-time-law",
                "concept.brownian.running-maximum",
                "concept.stochastic.hitting-time",
            ],
        ),
        "outcome.o009.analyze-brownian-zero-arcsine-lil": (
            "Menganalisis himpunan nol, hukum arksinus, dan hukum logaritma berulang untuk gerak Brown.",
            "analyze",
            [
                "concept.brownian.zero-set",
                "concept.brownian.arcsine-law",
                "concept.brownian.iterated-logarithm",
            ],
        ),
        "outcome.o009.solve-brownian-joint-gaussian": (
            "Menghitung kepadatan bersama, matriks kovarians, dan matriks korelasi vektor gerak Brown.",
            "apply",
            [
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.brownian.motion",
            ],
        ),
        "outcome.o009.characterize-brownian-drift-scaling": (
            "Mengkarakterisasi gerak Brown dengan parameter hanyutan dan skala melalui representasi standar, hukum Gaussian, dan transformasi ruang-waktu.",
            "analyze",
            [
                "concept.brownian.drift-and-scale",
                "concept.brownian.standard-motion",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.brownian.affine-scaling",
            ],
        ),
        "outcome.o009.derive-brownian-drift-transition-laws": (
            "Menurunkan kepadatan transisi serta persamaan difusi maju dan mundur untuk gerak Brown dengan hanyutan.",
            "prove",
            [
                "concept.brownian.transition-density",
                "concept.brownian.diffusion-equations",
                "concept.markov.transition-kernel",
            ],
        ),
        "outcome.o009.verify-brownian-drift-strong-markov": (
            "Memeriksa dan menerapkan sifat Markov kuat gerak Brown dengan hanyutan di bawah hipotesis filtrasi dan keterhinggaan waktu henti yang tepat.",
            "analyze",
            [
                "concept.brownian.drift-and-scale",
                "concept.markov.strong-property",
                "concept.stochastic.stopping-time",
            ],
        ),
        "outcome.o009.simulate-brownian-drift-terminal-law": (
            "Mensimulasikan secara deterministik gerak Brown dengan hanyutan dan membandingkan momen serta distribusi terminal empiris dengan hukum teoretis.",
            "apply",
            [
                "concept.brownian.drift-and-scale",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.monte-carlo",
            ],
        ),
        "outcome.o009.solve-brownian-drift-joint-conditional-law": (
            "Menghitung hukum Gaussian bersama dan bersyarat gerak Brown dengan hanyutan, termasuk vektor rataan, kovarians, dan korelasi.",
            "apply",
            [
                "concept.brownian.drift-and-scale",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.conditional.probability",
            ],
        ),
        "outcome.o009.construct-brownian-bridges": (
            "Membangun jembatan Brown melalui pengurangan tambatan, perubahan waktu, integral stokastik, dan pengondisian reguler.",
            "analyze",
            [
                "concept.brownian.bridge",
                "concept.brownian.bridge-time-change",
                "concept.brownian.regular-conditioning",
                "concept.conditional.regular-distribution",
            ],
        ),
        "outcome.o009.analyze-brownian-bridge-empirical-process": (
            "Menganalisis struktur kovarians jembatan Brown dalam proses empiris tanpa menyamakan hasil titik-demi-titik dengan teorema limit fungsional.",
            "analyze",
            [
                "concept.brownian.empirical-process",
                "concept.statistics.empirical-distribution-function",
                "concept.stochastic.process.finite-dimensional-distributions",
            ],
        ),
        "outcome.o009.simulate-brownian-bridge-marginal-law": (
            "Mensimulasikan jembatan Brown secara deterministik dan membandingkan distribusi marginal empiris dengan hukum Gaussian teoretis.",
            "apply",
            [
                "concept.brownian.bridge",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.monte-carlo",
            ],
        ),
        "outcome.o009.solve-brownian-bridge-conditional-law": (
            "Menghitung dan menafsirkan hukum Gaussian bersyarat jembatan Brown pada dua waktu interior.",
            "apply",
            [
                "concept.brownian.bridge",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.conditional.probability",
            ],
        ),
        "outcome.o009.characterize-geometric-brownian-motion": (
            "Mengkarakterisasi gerak Brown geometrik melalui representasi eksponensial dan persamaan diferensial stokastiknya.",
            "analyze",
            [
                "concept.brownian.geometric-motion",
                "concept.brownian.geometric-sde",
                "concept.brownian.drift-and-scale",
            ],
        ),
        "outcome.o009.derive-geometric-brownian-laws": (
            "Menurunkan distribusi lognormal, fungsi distribusi, kuantil, dan momen gerak Brown geometrik.",
            "prove",
            [
                "concept.brownian.geometric-motion",
                "concept.probability.lognormal-distribution",
                "concept.brownian.geometric-moments",
            ],
        ),
        "outcome.o009.analyze-geometric-brownian-asymptotics": (
            "Menganalisis perilaku hampir pasti gerak Brown geometrik dan syarat martingal eksponensialnya.",
            "analyze",
            [
                "concept.brownian.geometric-asymptotics",
                "concept.brownian.exponential-martingale",
            ],
        ),
        "outcome.o009.simulate-geometric-brownian-terminal-law": (
            "Mensimulasikan lintasan gerak Brown geometrik secara deterministik dan membandingkan hukum terminal empiris dengan hukum lognormal teoretis.",
            "apply",
            [
                "concept.brownian.geometric-motion",
                "concept.probability.lognormal-distribution",
                "concept.monte-carlo",
            ],
        ),
        "outcome.o009.solve-geometric-brownian-conditional-law": (
            "Menurunkan hukum, rataan, dan varians bersyarat gerak Brown geometrik serta membuktikan sifat martingal proses terdiskonto.",
            "apply",
            [
                "concept.brownian.geometric-motion",
                "concept.probability.lognormal-distribution",
                "concept.brownian.exponential-martingale",
                "concept.conditional.probability",
            ],
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
    builder_units_by_rel = {
        str(item["rel"]): item for item in build_module.THEORY_UNITS
    }
    builder_rels = list(builder_units_by_rel)
    backend_rels = [str(item["rel"]) for item in THEORY_SPECS]
    if builder_rels != backend_rels:
        raise RuntimeError(
            f"builder/backend theory sequence differs: builder={builder_rels} backend={backend_rels}"
        )
    backend_orders = [int(item["order"]) for item in THEORY_SPECS]
    expected_random_orders = [*range(1, 20), *range(28, 28 + max(0, len(THEORY_SPECS) - 19))]
    if backend_orders != expected_random_orders:
        raise RuntimeError(
            "backend Random theory order must preserve the QuantEcon 20--27 gap: "
            f"expected={expected_random_orders} actual={backend_orders}"
        )
    if len({str(item["slug"]) for item in THEORY_SPECS}) != len(THEORY_SPECS):
        raise RuntimeError("backend theory slugs must be unique")
    for spec in THEORY_SPECS:
        required_corrections = {
            str(item) for item in spec.get("required_correction_ids", ())
        }
        if not required_corrections:
            continue
        builder_corrections = {
            str(item.get("id"))
            for item in builder_units_by_rel[str(spec["rel"])].get(
                "reader_corrections", ()
            )
        }
        missing_corrections = required_corrections - builder_corrections
        if missing_corrections:
            raise RuntimeError(
                f"{spec['rel']}: required guarded reader corrections are missing: "
                f"{sorted(missing_corrections)}"
            )
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
        expected_authority_sha256 = spec.get("authority_sha256")
        if (
            expected_authority_sha256 is not None
            and sha256(source_bytes) != str(expected_authority_sha256)
        ):
            raise RuntimeError(
                f"{rel}: frozen authority hash differs: "
                f"expected={expected_authority_sha256} actual={sha256(source_bytes)}"
            )
        expected_target_sha256 = spec.get("target_sha256")
        if (
            expected_target_sha256 is not None
            and sha256(target_bytes) != str(expected_target_sha256)
        ):
            raise RuntimeError(
                f"{rel}: frozen translated-source hash differs: "
                f"expected={expected_target_sha256} actual={sha256(target_bytes)}"
            )
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
                payload={
                    "unit_kind": str(spec.get("unit_kind", "section")),
                    "source_language": "en",
                    "body_extent": "complete",
                },
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
            kind = SEMANTIC_KIND_OVERRIDES.get((slug, suffix), kind)
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
    brown_rel = "brown/Standard.html"
    brown_page_id = "unit.o009.random.brown.standard"
    brown_exercise_id = f"{brown_page_id}.div-050"
    brown_target = BeautifulSoup(
        require_file(ROOT / "source" / "theory" / "brown" / "Standard.html").decode(
            "utf-8"
        ),
        "lxml",
    )
    brown_reader_path = ROOT / "build" / "site" / "brown" / "Standard.html"
    brown_reader = BeautifulSoup(require_file(brown_reader_path).decode("utf-8"), "lxml")
    brown_generic_segments = [
        item for item in segments if item.get("path") == brown_rel
    ]
    if (
        len(brown_target.select("div.unit")) != 50
        or len(brown_target.find_all("details")) != 28
        or len(brown_generic_segments) != 207
    ):
        raise RuntimeError(
            "Brown source topology differs from 50 unit divs, 28 disclosures, and 207 segments"
        )
    if (
        len(brown_reader.select("div.unit")) != 50
        or len(brown_reader.find_all("details")) != 30
    ):
        raise RuntimeError(
            "Brown built reader differs from 50 unit divs and 30 disclosures"
        )
    source_exercise = brown_target.select("div.unit")[-1]
    if source_exercise.get("id") or source_exercise.find("details") is not None:
        raise RuntimeError(
            "Brown computational exercise must remain the anonymous unsolved source div-050"
        )

    brown_notes_by_id: dict[str, tuple[str, object]] = {}
    for reader_note in tuple(build_module.BROWN_STANDARD_READER_NOTES):
        reader_note_html = str(reader_note["html"])
        reader_note_soup = BeautifulSoup(reader_note_html, "lxml")
        reader_note_root = reader_note_soup.body.find(True, recursive=False)
        if reader_note_root is None or not reader_note_root.get("id"):
            raise RuntimeError("Brown reader note lacks one stable root id")
        brown_notes_by_id[str(reader_note_root["id"])] = (
            reader_note_html,
            reader_note_root,
        )
    if set(brown_notes_by_id) != {
        "brown-standard-downstream-corrections",
        "brown-standard-exercise-solution",
    }:
        raise RuntimeError("Brown reader-note identities differ")

    brown_correction_note = brown_reader.find(
        "aside", id="brown-standard-downstream-corrections"
    )
    brown_solution_aside = brown_reader.find(
        "aside", id="brown-standard-exercise-solution"
    )
    brown_lil_consequence = brown_reader.find("details", id="lil1-consequence")
    if (
        brown_correction_note is None
        or brown_solution_aside is None
        or brown_lil_consequence is None
        or len(brown_solution_aside.find_all("details")) != 1
    ):
        raise RuntimeError("Brown built-reader additions are incomplete")

    correction_note_html = brown_notes_by_id[
        "brown-standard-downstream-corrections"
    ][0]
    correction_note_text = " ".join(brown_correction_note.stripped_strings)
    correction_note_id = (
        "segment.o009.original.brown.standard.downstream-correction-note"
    )
    segments.append(
        record(
            "segment",
            correction_note_id,
            parent_id=brown_page_id,
            order=10000,
            path=brown_rel,
            source_local_id="brown-standard-downstream-corrections",
            source_locator=(
                "scripts/build_first_boundary.py#brown-standard-downstream-corrections"
            ),
            source_sha256=sha256(correction_note_html.encode("utf-8")),
            target_sha256=sha256(correction_note_text.encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id="rights.o009.original.cc-by-4.0",
            concept_ids=["concept.brownian.motion"],
            payload={
                "target_text": correction_note_text,
                "tag": "aside",
                "built_id": "brown-standard-downstream-corrections",
                "body_extent": "complete-build-addition",
            },
        )
    )
    relations.append(
        relation(
            "rel.contains.unit.o009.random.brown.standard.downstream-correction-note",
            "contains",
            brown_page_id,
            correction_note_id,
            "build/site/brown/Standard.html#brown-standard-downstream-corrections",
        )
    )

    brown_corrections = {
        str(item["id"]): item
        for item in tuple(build_module.BROWN_STANDARD_READER_CORRECTIONS)
    }
    lil_correction = brown_corrections.get("iterated-logarithm-two-sided")
    if lil_correction is None or 'id="lil1-consequence"' not in str(
        lil_correction["new"]
    ):
        raise RuntimeError("Brown two-sided LIL correction lacks its consequence disclosure")
    lil_unit_id = "unit.o009.original.brown.standard.lil1-consequence"
    entities.append(
        record(
            "unit",
            lil_unit_id,
            parent_id=f"{brown_page_id}.lil1",
            order=10000,
            path=brown_rel,
            source_local_id="lil1-consequence",
            source_locator=(
                "scripts/build_first_boundary.py#iterated-logarithm-two-sided"
            ),
            source_sha256=sha256(str(lil_correction["new"]).encode("utf-8")),
            target_sha256=sha256(str(brown_lil_consequence).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id="rights.o009.original.cc-by-4.0",
            concept_ids=["concept.brownian.iterated-logarithm"],
            payload={
                "unit_kind": "consequence",
                "tag": "details",
                "built_id": "lil1-consequence",
                "body_extent": "complete-build-addition",
            },
        )
    )
    relations.append(
        relation(
            "rel.contains.unit.o009.random.brown.standard.lil1.lil1-consequence",
            "contains",
            f"{brown_page_id}.lil1",
            lil_unit_id,
            "build/site/brown/Standard.html#lil1-consequence",
        )
    )

    solution_note_html = brown_notes_by_id["brown-standard-exercise-solution"][0]
    solution_unit_id = "unit.o009.original.brown.standard.exercise-solution"
    entities.append(
        record(
            "unit",
            solution_unit_id,
            parent_id=brown_exercise_id,
            order=10000,
            path=brown_rel,
            source_local_id="brown-standard-exercise-solution",
            source_locator=(
                "scripts/build_first_boundary.py#brown-standard-exercise-solution"
            ),
            source_sha256=sha256(solution_note_html.encode("utf-8")),
            target_sha256=sha256(str(brown_solution_aside).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id="rights.o009.original.cc-by-4.0",
            concept_ids=["concept.brownian.gaussian-finite-dimensional-laws"],
            payload={
                "unit_kind": "solution",
                "tag": "details",
                "built_id": "brown-standard-exercise-solution",
                "body_extent": "complete-build-addition",
                "source_supplied": False,
            },
        )
    )
    relations.extend(
        [
            relation(
                "rel.contains.unit.o009.random.brown.standard.div-050.exercise-solution",
                "contains",
                brown_exercise_id,
                solution_unit_id,
                "build/site/brown/Standard.html#brown-standard-exercise-solution",
            ),
            relation(
                "rel.solves.brown-standard.div-050",
                "solves",
                solution_unit_id,
                brown_exercise_id,
                "original CC BY 4.0 solution for the source-unsolved computational exercise",
            ),
        ]
    )

    def append_brown_addition_segments(
        parent_id: str,
        root: object,
        stable_prefix: str,
        locator: str,
    ) -> None:
        segment_nodes = root.find_all(("summary", "p"))
        if not segment_nodes:
            raise RuntimeError(f"Brown reader addition has no segments: {stable_prefix}")
        for index, node in enumerate(segment_nodes, start=1):
            target_text = " ".join(node.stripped_strings)
            if not target_text:
                raise RuntimeError(
                    f"Brown reader addition has an empty segment: {stable_prefix}.{index}"
                )
            digest = sha256(target_text.encode("utf-8"))
            segments.append(
                record(
                    "segment",
                    f"{stable_prefix}.{index:04d}",
                    parent_id=parent_id,
                    order=index,
                    path=brown_rel,
                    source_locator=f"{locator}:segment-{index:04d}",
                    source_sha256=digest,
                    target_sha256=digest,
                    locale="id-ID",
                    translation_state="authored",
                    relationship="authored",
                    rights_id="rights.o009.original.cc-by-4.0",
                    concept_ids=["concept.brownian.motion"],
                    payload={
                        "target_text": target_text,
                        "tag": node.name,
                        "body_extent": "complete-build-addition-segment",
                    },
                )
            )

    append_brown_addition_segments(
        lil_unit_id,
        brown_lil_consequence,
        "segment.o009.original.brown.standard.lil1-consequence",
        "scripts/build_first_boundary.py#iterated-logarithm-two-sided",
    )
    append_brown_addition_segments(
        solution_unit_id,
        brown_solution_aside,
        "segment.o009.original.brown.standard.exercise-solution",
        "scripts/build_first_boundary.py#brown-standard-exercise-solution",
    )

    drift_rel = "brown/Drift.html"
    drift_page_id = "unit.o009.random.brown.drift"
    drift_target_path = ROOT / "source" / "theory" / "brown" / "Drift.html"
    drift_reader_path = ROOT / "build" / "site" / "brown" / "Drift.html"
    drift_target = BeautifulSoup(require_file(drift_target_path).decode("utf-8"), "lxml")
    drift_reader = BeautifulSoup(require_file(drift_reader_path).decode("utf-8"), "lxml")
    drift_generic_segments = [item for item in segments if item.get("path") == drift_rel]
    expected_drift_unit_ids = {
        "def1",
        "def2",
        "def3",
        "dis1",
        "dis2",
        "trn1",
        "trn2",
        "trn3",
        "mar1",
        "mar2",
        "mar3",
    }
    if (
        {str(item.get("id")) for item in drift_target.select("div.unit")}
        != expected_drift_unit_ids
        or len(drift_target.find_all("details")) != 7
        or len(drift_generic_segments) != 68
    ):
        raise RuntimeError(
            "Brown Drift source topology differs from 11 exact unit divs, 7 disclosures, and 68 segments"
        )
    if (
        {str(item.get("id")) for item in drift_reader.select("div.unit")}
        != expected_drift_unit_ids
        or len(drift_reader.find_all("details")) != 10
    ):
        raise RuntimeError(
            "Brown Drift reader topology differs from 11 source unit divs and 10 total disclosures"
        )

    drift_notes_by_id: dict[str, tuple[str, object]] = {}
    for reader_note in tuple(build_module.BROWN_DRIFT_READER_NOTES):
        reader_note_html = str(reader_note["html"])
        reader_note_soup = BeautifulSoup(reader_note_html, "lxml")
        reader_note_root = reader_note_soup.body.find(True, recursive=False)
        if reader_note_root is None or not reader_note_root.get("id"):
            raise RuntimeError("Brown Drift reader note lacks one stable root id")
        drift_notes_by_id[str(reader_note_root["id"])] = (
            reader_note_html,
            reader_note_root,
        )
    if set(drift_notes_by_id) != {
        "brown-drift-downstream-corrections",
        "brown-drift-offline-lab",
        "brown-drift-mastery",
    }:
        raise RuntimeError("Brown Drift reader-note identities differ")

    drift_correction_note = drift_reader.find(
        "aside", id="brown-drift-downstream-corrections"
    )
    drift_offline_lab = drift_reader.find("section", id="brown-drift-offline-lab")
    drift_mastery = drift_reader.find("aside", id="brown-drift-mastery")
    drift_mastery_exercise = drift_reader.find(id="brown-drift-mastery-exercise")
    drift_mastery_hint = drift_reader.find("details", id="brown-drift-mastery-hint")
    drift_mastery_solution = drift_reader.find(
        "details", id="brown-drift-mastery-solution"
    )
    drift_strong_markov_proof = drift_reader.find(
        "details", id="brown-drift-strong-markov-proof"
    )
    if any(
        item is None
        for item in (
            drift_correction_note,
            drift_offline_lab,
            drift_mastery,
            drift_mastery_exercise,
            drift_mastery_hint,
            drift_mastery_solution,
            drift_strong_markov_proof,
        )
    ):
        raise RuntimeError("Brown Drift explicit reader additions are incomplete")
    if (
        drift_mastery_exercise.find_parent(id="brown-drift-mastery") is None
        or drift_mastery_hint.find_parent(id="brown-drift-mastery") is None
        or drift_mastery_solution.find_parent(id="brown-drift-mastery") is None
        or drift_strong_markov_proof.find_parent(id="mar3") is None
    ):
        raise RuntimeError("Brown Drift reader additions are attached to the wrong source units")

    drift_corrections = {
        str(item["id"]): item
        for item in tuple(build_module.BROWN_DRIFT_READER_CORRECTIONS)
    }
    drift_strong_markov_correction = drift_corrections.get(
        "strong-markov-filtration-proof"
    )
    if drift_strong_markov_correction is None:
        raise RuntimeError("Brown Drift strong-Markov guarded correction is absent")
    drift_strong_markov_source = BeautifulSoup(
        str(drift_strong_markov_correction["new"]), "lxml"
    ).find("details", id="brown-drift-strong-markov-proof")
    if drift_strong_markov_source is None:
        raise RuntimeError("Brown Drift strong-Markov correction lacks its proof disclosure")

    drift_rights_id = "rights.o009.brown-drift-original.cc-by-4.0"
    drift_correction_note_html = drift_notes_by_id[
        "brown-drift-downstream-corrections"
    ][0]
    drift_correction_note_id = (
        "segment.o009.original.brown.drift.downstream-correction-note"
    )
    segments.append(
        record(
            "segment",
            drift_correction_note_id,
            parent_id=drift_page_id,
            order=10000,
            path=drift_rel,
            source_local_id="brown-drift-downstream-corrections",
            source_locator=(
                "scripts/build_first_boundary.py#brown-drift-downstream-corrections"
            ),
            source_sha256=sha256(drift_correction_note_html.encode("utf-8")),
            target_sha256=sha256(str(drift_correction_note).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=drift_rights_id,
            concept_ids=["concept.brownian.drift-and-scale"],
            payload={
                "target_text": " ".join(drift_correction_note.stripped_strings),
                "tag": "aside",
                "built_id": "brown-drift-downstream-corrections",
                "body_extent": "complete-build-addition",
            },
        )
    )

    drift_offline_lab_id = "unit.o009.original.brown.drift.offline-lab"
    drift_offline_lab_html = drift_notes_by_id["brown-drift-offline-lab"][0]
    entities.append(
        record(
            "unit",
            drift_offline_lab_id,
            parent_id=drift_page_id,
            order=10010,
            path=drift_rel,
            source_local_id="brown-drift-offline-lab",
            source_locator="scripts/build_first_boundary.py#brown-drift-offline-lab",
            source_sha256=sha256(drift_offline_lab_html.encode("utf-8")),
            target_sha256=sha256(str(drift_offline_lab).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=drift_rights_id,
            concept_ids=[
                "concept.brownian.drift-and-scale",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.monte-carlo",
            ],
            payload={
                "unit_kind": "computational-lab",
                "tool_kind": "interactive-simulator",
                "runtime": "offline-browser/JavaScript",
                "offline_capable": True,
                "deterministic_seeded": True,
                "built_id": "brown-drift-offline-lab",
                "body_extent": "complete-build-addition",
                "source_supplied": False,
            },
        )
    )
    drift_app_source = require_file(BROWN_DRIFT_OFFLINE_APP)
    drift_app_target = require_file(BUILT_BROWN_DRIFT_OFFLINE_APP)
    if drift_app_source != drift_app_target:
        raise RuntimeError("Brown Drift built offline app differs from its authored source")
    drift_app_id = "asset.o009.brown-drift-offline-js"
    entities.append(
        record(
            "asset",
            drift_app_id,
            parent_id=drift_offline_lab_id,
            path=relative(BROWN_DRIFT_OFFLINE_APP),
            source_locator=relative(BROWN_DRIFT_OFFLINE_APP),
            source_sha256=sha256(drift_app_source),
            target_sha256=sha256(drift_app_target),
            locale="id-ID",
            translation_state="authored",
            relationship="copies",
            rights_id=drift_rights_id,
            concept_ids=["concept.brownian.drift-and-scale", "concept.monte-carlo"],
            payload={
                "bytes": len(drift_app_source),
                "built_path": relative(BUILT_BROWN_DRIFT_OFFLINE_APP),
                "runtime": "offline-browser/JavaScript",
                "deterministic_seeded": True,
            },
        )
    )

    drift_mastery_id = "unit.o009.original.brown.drift.mastery"
    drift_mastery_html = drift_notes_by_id["brown-drift-mastery"][0]
    entities.append(
        record(
            "unit",
            drift_mastery_id,
            parent_id=drift_page_id,
            order=10020,
            path=drift_rel,
            source_local_id="brown-drift-mastery",
            source_locator="scripts/build_first_boundary.py#brown-drift-mastery",
            source_sha256=sha256(drift_mastery_html.encode("utf-8")),
            target_sha256=sha256(str(drift_mastery).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=drift_rights_id,
            concept_ids=[
                "concept.brownian.drift-and-scale",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.conditional.probability",
            ],
            payload={
                "unit_kind": "mastery-sequence",
                "built_id": "brown-drift-mastery",
                "body_extent": "complete-build-addition",
                "source_supplied": False,
            },
        )
    )
    drift_mastery_source = drift_notes_by_id["brown-drift-mastery"][1]
    mastery_parts = (
        (
            "exercise",
            drift_mastery_source.find(id="brown-drift-mastery-exercise"),
            drift_mastery_exercise,
            "exercise",
            1,
        ),
        (
            "hint",
            drift_mastery_source.find("details", id="brown-drift-mastery-hint"),
            drift_mastery_hint,
            "hint",
            2,
        ),
        (
            "solution",
            drift_mastery_source.find("details", id="brown-drift-mastery-solution"),
            drift_mastery_solution,
            "solution",
            3,
        ),
    )
    drift_mastery_part_ids: dict[str, str] = {}
    for suffix, source_part, target_part, unit_kind, order in mastery_parts:
        if source_part is None or target_part is None:
            raise RuntimeError(f"Brown Drift mastery {suffix} source/target surface is absent")
        stable_id = f"{drift_mastery_id}.{suffix}"
        drift_mastery_part_ids[suffix] = stable_id
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=drift_mastery_id,
                order=order,
                path=drift_rel,
                source_local_id=str(target_part.get("id")),
                source_locator=f"scripts/build_first_boundary.py#brown-drift-mastery-{suffix}",
                source_sha256=sha256(str(source_part).encode("utf-8")),
                target_sha256=sha256(str(target_part).encode("utf-8")),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=drift_rights_id,
                concept_ids=[
                    "concept.brownian.drift-and-scale",
                    "concept.brownian.gaussian-finite-dimensional-laws",
                    "concept.conditional.probability",
                ],
                payload={
                    "unit_kind": unit_kind,
                    "tag": target_part.name,
                    "built_id": str(target_part.get("id")),
                    "body_extent": "complete-build-addition",
                    "source_supplied": False,
                },
            )
        )

    drift_strong_markov_id = (
        "unit.o009.original.brown.drift.strong-markov-proof"
    )
    entities.append(
        record(
            "unit",
            drift_strong_markov_id,
            parent_id=f"{drift_page_id}.mar3",
            order=10000,
            path=drift_rel,
            source_local_id="brown-drift-strong-markov-proof",
            source_locator=(
                "scripts/build_first_boundary.py#strong-markov-filtration-proof"
            ),
            source_sha256=sha256(str(drift_strong_markov_source).encode("utf-8")),
            target_sha256=sha256(str(drift_strong_markov_proof).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=drift_rights_id,
            concept_ids=[
                "concept.brownian.drift-and-scale",
                "concept.markov.strong-property",
                "concept.stochastic.stopping-time",
            ],
            payload={
                "unit_kind": "proof",
                "tag": "details",
                "built_id": "brown-drift-strong-markov-proof",
                "body_extent": "complete-correction-addition",
                "source_supplied": False,
            },
        )
    )

    def append_drift_addition_segments(
        parent_id: str,
        nodes: Iterable[object],
        stable_prefix: str,
        locator: str,
        concept_ids: list[str],
    ) -> None:
        added = 0
        for node in nodes:
            target_text = " ".join(node.stripped_strings)
            if not target_text:
                continue
            added += 1
            digest = sha256(target_text.encode("utf-8"))
            segments.append(
                record(
                    "segment",
                    f"{stable_prefix}.{added:04d}",
                    parent_id=parent_id,
                    order=added,
                    path=drift_rel,
                    source_locator=f"{locator}:segment-{added:04d}",
                    source_sha256=digest,
                    target_sha256=digest,
                    locale="id-ID",
                    translation_state="authored",
                    relationship="authored",
                    rights_id=drift_rights_id,
                    concept_ids=concept_ids,
                    payload={
                        "target_text": target_text,
                        "tag": node.name,
                        "body_extent": "complete-build-addition-segment",
                    },
                )
            )
        if added == 0:
            raise RuntimeError(f"Brown Drift reader addition has no segments: {stable_prefix}")

    drift_lab_nodes = drift_offline_lab.find_all(
        (
            "p",
            "legend",
            "label",
            "button",
            "title",
            "desc",
            "caption",
            "th",
            "td",
            "noscript",
        )
    )
    append_drift_addition_segments(
        drift_offline_lab_id,
        drift_lab_nodes,
        "segment.o009.original.brown.drift.offline-lab",
        "scripts/build_first_boundary.py#brown-drift-offline-lab",
        ["concept.brownian.drift-and-scale", "concept.monte-carlo"],
    )
    mastery_intro_nodes = drift_mastery.find_all("p", recursive=False)[:2]
    append_drift_addition_segments(
        drift_mastery_id,
        mastery_intro_nodes,
        "segment.o009.original.brown.drift.mastery",
        "scripts/build_first_boundary.py#brown-drift-mastery",
        ["concept.brownian.drift-and-scale"],
    )
    append_drift_addition_segments(
        drift_mastery_part_ids["exercise"],
        [drift_mastery_exercise],
        "segment.o009.original.brown.drift.mastery.exercise",
        "scripts/build_first_boundary.py#brown-drift-mastery-exercise",
        ["concept.brownian.gaussian-finite-dimensional-laws"],
    )
    append_drift_addition_segments(
        drift_mastery_part_ids["hint"],
        drift_mastery_hint.find_all(("summary", "p")),
        "segment.o009.original.brown.drift.mastery.hint",
        "scripts/build_first_boundary.py#brown-drift-mastery-hint",
        ["concept.brownian.gaussian-finite-dimensional-laws"],
    )
    append_drift_addition_segments(
        drift_mastery_part_ids["solution"],
        drift_mastery_solution.find_all(("summary", "p")),
        "segment.o009.original.brown.drift.mastery.solution",
        "scripts/build_first_boundary.py#brown-drift-mastery-solution",
        [
            "concept.brownian.gaussian-finite-dimensional-laws",
            "concept.conditional.probability",
        ],
    )
    append_drift_addition_segments(
        drift_strong_markov_id,
        drift_strong_markov_proof.find_all(("summary", "p")),
        "segment.o009.original.brown.drift.strong-markov-proof",
        "scripts/build_first_boundary.py#strong-markov-filtration-proof",
        ["concept.markov.strong-property", "concept.stochastic.stopping-time"],
    )

    relations.extend(
        [
            relation(
                "rel.contains.unit.o009.random.brown.drift.downstream-correction-note",
                "contains",
                drift_page_id,
                drift_correction_note_id,
                "build/site/brown/Drift.html#brown-drift-downstream-corrections",
            ),
            relation(
                "rel.contains.unit.o009.random.brown.drift.offline-lab",
                "contains",
                drift_page_id,
                drift_offline_lab_id,
                "build/site/brown/Drift.html#brown-drift-offline-lab",
            ),
            relation(
                "rel.depends-on.brown-drift-offline-lab.javascript",
                "depends-on",
                drift_offline_lab_id,
                drift_app_id,
                "build/site/brown/Drift.html#brown-drift-offline-lab script[src='../apps/brown-drift-offline.js']",
            ),
            relation(
                "rel.executes.brown-drift-offline-lab.javascript",
                "executes",
                drift_offline_lab_id,
                drift_app_id,
                "source/original/brown-drift-offline.js is copied byte-for-byte into the offline reader",
            ),
            relation(
                "rel.assesses.brown-drift-offline-lab.terminal-law",
                "assesses",
                drift_offline_lab_id,
                "outcome.o009.simulate-brownian-drift-terminal-law",
                "seeded path and terminal-law simulation with theoretical/empirical moment comparison",
            ),
            relation(
                "rel.contains.unit.o009.random.brown.drift.mastery",
                "contains",
                drift_page_id,
                drift_mastery_id,
                "build/site/brown/Drift.html#brown-drift-mastery",
            ),
            *(
                relation(
                    f"rel.contains.brown-drift-mastery.{suffix}",
                    "contains",
                    drift_mastery_id,
                    stable_id,
                    f"build/site/brown/Drift.html#brown-drift-mastery-{suffix}",
                )
                for suffix, stable_id in drift_mastery_part_ids.items()
            ),
            relation(
                "rel.hints.brown-drift-mastery",
                "hints",
                drift_mastery_part_ids["hint"],
                drift_mastery_part_ids["exercise"],
                "build/site/brown/Drift.html#brown-drift-mastery-hint",
            ),
            relation(
                "rel.solves.brown-drift-mastery",
                "solves",
                drift_mastery_part_ids["solution"],
                drift_mastery_part_ids["exercise"],
                "build/site/brown/Drift.html#brown-drift-mastery-solution",
            ),
            relation(
                "rel.assesses.brown-drift-mastery",
                "assesses",
                drift_mastery_part_ids["exercise"],
                "outcome.o009.solve-brownian-drift-joint-conditional-law",
                "original complete joint/conditional Gaussian mastery exercise",
            ),
            relation(
                "rel.contains.brown-drift-mar3.strong-markov-proof",
                "contains",
                f"{drift_page_id}.mar3",
                drift_strong_markov_id,
                "build/site/brown/Drift.html#brown-drift-strong-markov-proof",
            ),
            relation(
                "rel.teaches.brown-drift.strong-markov-proof",
                "teaches",
                drift_strong_markov_id,
                "outcome.o009.verify-brownian-drift-strong-markov",
                "authored proof route via dyadic stopping-time approximation",
            ),
        ]
    )

    bridge_rel = "brown/Bridge.html"
    bridge_page_id = "unit.o009.random.brown.bridge"
    bridge_target_path = ROOT / "source" / "theory" / "brown" / "Bridge.html"
    bridge_reader_path = ROOT / "build" / "site" / "brown" / "Bridge.html"
    bridge_target = BeautifulSoup(
        require_file(bridge_target_path).decode("utf-8"), "lxml"
    )
    bridge_reader = BeautifulSoup(
        require_file(bridge_reader_path).decode("utf-8"), "lxml"
    )
    bridge_generic_segments = [
        item for item in segments if item.get("path") == bridge_rel
    ]
    expected_bridge_named_unit_ids = {
        "def1",
        "def2",
        "def3",
        "def4",
        "def5",
        "def7",
        "def8",
        "def6",
        "gen1",
        "gen2",
        "edf1",
        "edf2",
    }
    bridge_target_unit_ids = [
        item.get("id") for item in bridge_target.select("div.unit")
    ]
    if (
        len(bridge_target_unit_ids) != 13
        or set(item for item in bridge_target_unit_ids if item)
        != expected_bridge_named_unit_ids
        or bridge_target_unit_ids.count(None) != 1
        or len(bridge_target.find_all("details")) != 7
        or len(bridge_generic_segments) != 99
    ):
        raise RuntimeError(
            "Brown Bridge source topology differs from 13 exact unit divs, "
            "7 disclosures, and 99 segments"
        )
    bridge_reader_unit_ids = [
        item.get("id") for item in bridge_reader.select("div.unit")
    ]
    if (
        bridge_reader_unit_ids != bridge_target_unit_ids
        or len(bridge_reader.find_all("details")) != 9
    ):
        raise RuntimeError(
            "Brown Bridge reader topology differs from 13 source unit divs and "
            "9 total disclosures"
        )

    bridge_notes_by_id: dict[str, tuple[str, object]] = {}
    for reader_note in tuple(build_module.BROWN_BRIDGE_READER_NOTES):
        reader_note_html = str(reader_note["html"])
        reader_note_soup = BeautifulSoup(reader_note_html, "lxml")
        reader_note_root = reader_note_soup.body.find(True, recursive=False)
        if reader_note_root is None or not reader_note_root.get("id"):
            raise RuntimeError("Brown Bridge reader note lacks one stable root id")
        bridge_notes_by_id[str(reader_note_root["id"])] = (
            reader_note_html,
            reader_note_root,
        )
    if set(bridge_notes_by_id) != {
        "brown-bridge-downstream-corrections",
        "brown-bridge-offline-lab",
        "brown-bridge-mastery",
    }:
        raise RuntimeError("Brown Bridge reader-note identities differ")

    bridge_correction_note = bridge_reader.find(
        "aside", id="brown-bridge-downstream-corrections"
    )
    bridge_offline_lab = bridge_reader.find(
        "section", id="brown-bridge-offline-lab"
    )
    bridge_mastery = bridge_reader.find("aside", id="brown-bridge-mastery")
    bridge_process_limit_warning = bridge_reader.find(
        "p", id="brown-bridge-process-limit-warning"
    )
    bridge_mastery_exercise = bridge_reader.find(
        "p", id="brown-bridge-mastery-exercise"
    )
    bridge_mastery_hint = bridge_reader.find(
        "details", id="brown-bridge-mastery-hint"
    )
    bridge_mastery_solution = bridge_reader.find(
        "details", id="brown-bridge-mastery-solution"
    )
    if any(
        item is None
        for item in (
            bridge_correction_note,
            bridge_offline_lab,
            bridge_mastery,
            bridge_process_limit_warning,
            bridge_mastery_exercise,
            bridge_mastery_hint,
            bridge_mastery_solution,
        )
    ):
        raise RuntimeError("Brown Bridge explicit reader additions are incomplete")
    if any(
        item.find_parent(id="brown-bridge-mastery") is None
        for item in (
            bridge_process_limit_warning,
            bridge_mastery_exercise,
            bridge_mastery_hint,
            bridge_mastery_solution,
        )
    ):
        raise RuntimeError("Brown Bridge mastery additions are attached to the wrong parent")

    bridge_rights_id = "rights.o009.brown-bridge-original.cc-by-4.0"
    bridge_correction_note_html = bridge_notes_by_id[
        "brown-bridge-downstream-corrections"
    ][0]
    bridge_correction_note_id = (
        "segment.o009.original.brown.bridge.downstream-correction-note"
    )
    segments.append(
        record(
            "segment",
            bridge_correction_note_id,
            parent_id=bridge_page_id,
            order=10000,
            path=bridge_rel,
            source_local_id="brown-bridge-downstream-corrections",
            source_locator=(
                "scripts/build_first_boundary.py#brown-bridge-downstream-corrections"
            ),
            source_sha256=sha256(bridge_correction_note_html.encode("utf-8")),
            target_sha256=sha256(str(bridge_correction_note).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=bridge_rights_id,
            concept_ids=["concept.brownian.bridge"],
            payload={
                "target_text": " ".join(bridge_correction_note.stripped_strings),
                "tag": "aside",
                "built_id": "brown-bridge-downstream-corrections",
                "body_extent": "complete-build-addition",
            },
        )
    )

    bridge_offline_lab_id = "unit.o009.original.brown.bridge.offline-lab"
    bridge_offline_lab_html = bridge_notes_by_id["brown-bridge-offline-lab"][0]
    entities.append(
        record(
            "unit",
            bridge_offline_lab_id,
            parent_id=bridge_page_id,
            order=10010,
            path=bridge_rel,
            source_local_id="brown-bridge-offline-lab",
            source_locator=(
                "scripts/build_first_boundary.py#brown-bridge-offline-lab"
            ),
            source_sha256=sha256(bridge_offline_lab_html.encode("utf-8")),
            target_sha256=sha256(str(bridge_offline_lab).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=bridge_rights_id,
            concept_ids=[
                "concept.brownian.bridge",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.monte-carlo",
            ],
            payload={
                "unit_kind": "computational-lab",
                "tool_kind": "interactive-simulator",
                "runtime": "offline-browser/JavaScript",
                "offline_capable": True,
                "deterministic_seeded": True,
                "built_id": "brown-bridge-offline-lab",
                "body_extent": "complete-build-addition",
                "source_supplied": False,
            },
        )
    )
    bridge_app_source = require_file(BROWN_BRIDGE_OFFLINE_APP)
    bridge_app_target = require_file(BUILT_BROWN_BRIDGE_OFFLINE_APP)
    if bridge_app_source != bridge_app_target:
        raise RuntimeError("Brown Bridge built offline app differs from its authored source")
    bridge_app_id = "asset.o009.brown-bridge-offline-js"
    entities.append(
        record(
            "asset",
            bridge_app_id,
            parent_id=bridge_offline_lab_id,
            path=relative(BROWN_BRIDGE_OFFLINE_APP),
            source_locator=relative(BROWN_BRIDGE_OFFLINE_APP),
            source_sha256=sha256(bridge_app_source),
            target_sha256=sha256(bridge_app_target),
            locale="id-ID",
            translation_state="authored",
            relationship="copies",
            rights_id=bridge_rights_id,
            concept_ids=["concept.brownian.bridge", "concept.monte-carlo"],
            payload={
                "bytes": len(bridge_app_source),
                "built_path": relative(BUILT_BROWN_BRIDGE_OFFLINE_APP),
                "runtime": "offline-browser/JavaScript",
                "deterministic_seeded": True,
            },
        )
    )

    bridge_mastery_id = "unit.o009.original.brown.bridge.mastery"
    bridge_mastery_html = bridge_notes_by_id["brown-bridge-mastery"][0]
    entities.append(
        record(
            "unit",
            bridge_mastery_id,
            parent_id=bridge_page_id,
            order=10020,
            path=bridge_rel,
            source_local_id="brown-bridge-mastery",
            source_locator="scripts/build_first_boundary.py#brown-bridge-mastery",
            source_sha256=sha256(bridge_mastery_html.encode("utf-8")),
            target_sha256=sha256(str(bridge_mastery).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=bridge_rights_id,
            concept_ids=[
                "concept.brownian.bridge",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.brownian.empirical-process",
                "concept.conditional.probability",
            ],
            payload={
                "unit_kind": "mastery-sequence",
                "built_id": "brown-bridge-mastery",
                "body_extent": "complete-build-addition",
                "source_supplied": False,
            },
        )
    )
    bridge_mastery_source = bridge_notes_by_id["brown-bridge-mastery"][1]
    bridge_mastery_parts = (
        (
            "process-limit-warning",
            bridge_mastery_source.find(
                "p", id="brown-bridge-process-limit-warning"
            ),
            bridge_process_limit_warning,
            "process-limit-warning",
            1,
            [
                "concept.brownian.empirical-process",
                "concept.stochastic.process.finite-dimensional-distributions",
            ],
        ),
        (
            "exercise",
            bridge_mastery_source.find("p", id="brown-bridge-mastery-exercise"),
            bridge_mastery_exercise,
            "exercise",
            2,
            [
                "concept.brownian.bridge",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.conditional.probability",
            ],
        ),
        (
            "hint",
            bridge_mastery_source.find(
                "details", id="brown-bridge-mastery-hint"
            ),
            bridge_mastery_hint,
            "hint",
            3,
            [
                "concept.brownian.bridge",
                "concept.brownian.gaussian-finite-dimensional-laws",
            ],
        ),
        (
            "solution",
            bridge_mastery_source.find(
                "details", id="brown-bridge-mastery-solution"
            ),
            bridge_mastery_solution,
            "solution",
            4,
            [
                "concept.brownian.bridge",
                "concept.brownian.gaussian-finite-dimensional-laws",
                "concept.conditional.probability",
            ],
        ),
    )
    bridge_mastery_part_ids: dict[str, str] = {}
    for (
        suffix,
        source_part,
        target_part,
        unit_kind,
        order,
        concept_ids,
    ) in bridge_mastery_parts:
        if source_part is None or target_part is None:
            raise RuntimeError(
                f"Brown Bridge mastery {suffix} source/target surface is absent"
            )
        stable_id = f"{bridge_mastery_id}.{suffix}"
        bridge_mastery_part_ids[suffix] = stable_id
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=bridge_mastery_id,
                order=order,
                path=bridge_rel,
                source_local_id=str(target_part.get("id")),
                source_locator=(
                    f"scripts/build_first_boundary.py#brown-bridge-{suffix}"
                ),
                source_sha256=sha256(str(source_part).encode("utf-8")),
                target_sha256=sha256(str(target_part).encode("utf-8")),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=bridge_rights_id,
                concept_ids=concept_ids,
                payload={
                    "unit_kind": unit_kind,
                    "tag": target_part.name,
                    "built_id": str(target_part.get("id")),
                    "body_extent": "complete-build-addition",
                    "source_supplied": False,
                },
            )
        )

    def append_bridge_addition_segments(
        parent_id: str,
        nodes: Iterable[object],
        stable_prefix: str,
        locator: str,
        concept_ids: list[str],
    ) -> None:
        added = 0
        for node in nodes:
            target_text = " ".join(node.stripped_strings)
            if not target_text:
                continue
            added += 1
            digest = sha256(target_text.encode("utf-8"))
            segments.append(
                record(
                    "segment",
                    f"{stable_prefix}.{added:04d}",
                    parent_id=parent_id,
                    order=added,
                    path=bridge_rel,
                    source_locator=f"{locator}:segment-{added:04d}",
                    source_sha256=digest,
                    target_sha256=digest,
                    locale="id-ID",
                    translation_state="authored",
                    relationship="authored",
                    rights_id=bridge_rights_id,
                    concept_ids=concept_ids,
                    payload={
                        "target_text": target_text,
                        "tag": node.name,
                        "body_extent": "complete-build-addition-segment",
                    },
                )
            )
        if added == 0:
            raise RuntimeError(
                f"Brown Bridge reader addition has no segments: {stable_prefix}"
            )

    bridge_lab_nodes = bridge_offline_lab.find_all(
        (
            "p",
            "legend",
            "label",
            "button",
            "title",
            "desc",
            "caption",
            "th",
            "td",
            "noscript",
        )
    )
    append_bridge_addition_segments(
        bridge_offline_lab_id,
        bridge_lab_nodes,
        "segment.o009.original.brown.bridge.offline-lab",
        "scripts/build_first_boundary.py#brown-bridge-offline-lab",
        ["concept.brownian.bridge", "concept.monte-carlo"],
    )
    bridge_mastery_intro_nodes = bridge_mastery.find_all("p", recursive=False)[:2]
    append_bridge_addition_segments(
        bridge_mastery_id,
        bridge_mastery_intro_nodes,
        "segment.o009.original.brown.bridge.mastery",
        "scripts/build_first_boundary.py#brown-bridge-mastery",
        ["concept.brownian.bridge"],
    )
    append_bridge_addition_segments(
        bridge_mastery_part_ids["process-limit-warning"],
        [bridge_process_limit_warning],
        "segment.o009.original.brown.bridge.mastery.process-limit-warning",
        "scripts/build_first_boundary.py#brown-bridge-process-limit-warning",
        [
            "concept.brownian.empirical-process",
            "concept.stochastic.process.finite-dimensional-distributions",
        ],
    )
    append_bridge_addition_segments(
        bridge_mastery_part_ids["exercise"],
        [bridge_mastery_exercise],
        "segment.o009.original.brown.bridge.mastery.exercise",
        "scripts/build_first_boundary.py#brown-bridge-mastery-exercise",
        ["concept.brownian.bridge", "concept.conditional.probability"],
    )
    append_bridge_addition_segments(
        bridge_mastery_part_ids["hint"],
        bridge_mastery_hint.find_all(("summary", "p")),
        "segment.o009.original.brown.bridge.mastery.hint",
        "scripts/build_first_boundary.py#brown-bridge-mastery-hint",
        ["concept.brownian.bridge"],
    )
    append_bridge_addition_segments(
        bridge_mastery_part_ids["solution"],
        bridge_mastery_solution.find_all(("summary", "p")),
        "segment.o009.original.brown.bridge.mastery.solution",
        "scripts/build_first_boundary.py#brown-bridge-mastery-solution",
        [
            "concept.brownian.bridge",
            "concept.brownian.gaussian-finite-dimensional-laws",
            "concept.conditional.probability",
        ],
    )

    relations.extend(
        [
            relation(
                "rel.contains.unit.o009.random.brown.bridge.downstream-correction-note",
                "contains",
                bridge_page_id,
                bridge_correction_note_id,
                "build/site/brown/Bridge.html#brown-bridge-downstream-corrections",
            ),
            relation(
                "rel.contains.unit.o009.random.brown.bridge.offline-lab",
                "contains",
                bridge_page_id,
                bridge_offline_lab_id,
                "build/site/brown/Bridge.html#brown-bridge-offline-lab",
            ),
            relation(
                "rel.depends-on.brown-bridge-offline-lab.definition",
                "depends-on",
                bridge_offline_lab_id,
                f"{bridge_page_id}.def1",
                "the simulator instantiates the standard Brownian-bridge definition",
            ),
            relation(
                "rel.depends-on.brown-bridge-offline-lab.javascript",
                "depends-on",
                bridge_offline_lab_id,
                bridge_app_id,
                "build/site/brown/Bridge.html#brown-bridge-offline-lab script[src='../apps/brown-bridge-offline.js']",
            ),
            relation(
                "rel.executes.brown-bridge-offline-lab.javascript",
                "executes",
                bridge_offline_lab_id,
                bridge_app_id,
                "source/original/brown-bridge-offline.js is copied byte-for-byte into the offline reader",
            ),
            relation(
                "rel.assesses.brown-bridge-offline-lab.marginal-law",
                "assesses",
                bridge_offline_lab_id,
                "outcome.o009.simulate-brownian-bridge-marginal-law",
                "seeded bridge-path and marginal-law simulation with theoretical/empirical moment comparison",
            ),
            relation(
                "rel.contains.unit.o009.random.brown.bridge.mastery",
                "contains",
                bridge_page_id,
                bridge_mastery_id,
                "build/site/brown/Bridge.html#brown-bridge-mastery",
            ),
            relation(
                "rel.depends-on.brown-bridge-mastery.definition",
                "depends-on",
                bridge_mastery_id,
                f"{bridge_page_id}.def1",
                "the process-limit warning and conditional-law exercise use the standard bridge definition",
            ),
            *(
                relation(
                    f"rel.contains.brown-bridge-mastery.{suffix}",
                    "contains",
                    bridge_mastery_id,
                    stable_id,
                    f"build/site/brown/Bridge.html#brown-bridge-{suffix}",
                )
                for suffix, stable_id in bridge_mastery_part_ids.items()
            ),
            relation(
                "rel.precedes.brown-bridge-mastery.process-limit-warning.exercise",
                "precedes",
                bridge_mastery_part_ids["process-limit-warning"],
                bridge_mastery_part_ids["exercise"],
                "authored mastery sequence in reader DOM order",
            ),
            relation(
                "rel.precedes.brown-bridge-mastery.exercise.hint",
                "precedes",
                bridge_mastery_part_ids["exercise"],
                bridge_mastery_part_ids["hint"],
                "authored mastery sequence in reader DOM order",
            ),
            relation(
                "rel.precedes.brown-bridge-mastery.hint.solution",
                "precedes",
                bridge_mastery_part_ids["hint"],
                bridge_mastery_part_ids["solution"],
                "authored mastery sequence in reader DOM order",
            ),
            relation(
                "rel.hints.brown-bridge-mastery",
                "hints",
                bridge_mastery_part_ids["hint"],
                bridge_mastery_part_ids["exercise"],
                "build/site/brown/Bridge.html#brown-bridge-mastery-hint",
            ),
            relation(
                "rel.solves.brown-bridge-mastery",
                "solves",
                bridge_mastery_part_ids["solution"],
                bridge_mastery_part_ids["exercise"],
                "build/site/brown/Bridge.html#brown-bridge-mastery-solution",
            ),
            relation(
                "rel.teaches.brown-bridge.process-limit-warning",
                "teaches",
                bridge_mastery_part_ids["process-limit-warning"],
                "outcome.o009.analyze-brownian-bridge-empirical-process",
                "authored boundary between covariance calculations and a functional limit theorem",
            ),
            relation(
                "rel.assesses.brown-bridge-mastery",
                "assesses",
                bridge_mastery_part_ids["exercise"],
                "outcome.o009.solve-brownian-bridge-conditional-law",
                "original complete conditional Gaussian mastery exercise",
            ),
        ]
    )

    geometric_rel = "brown/Geometric.html"
    geometric_page_id = "unit.o009.random.brown.geometric"
    geometric_target_path = ROOT / "source" / "theory" / "brown" / "Geometric.html"
    geometric_reader_path = ROOT / "build" / "site" / "brown" / "Geometric.html"
    geometric_target = BeautifulSoup(
        require_file(geometric_target_path).decode("utf-8"), "lxml"
    )
    geometric_reader = BeautifulSoup(
        require_file(geometric_reader_path).decode("utf-8"), "lxml"
    )
    geometric_generic_segments = [
        item for item in segments if item.get("path") == geometric_rel
    ]
    expected_geometric_named_unit_ids = {
        "def1",
        "def2",
        "def3",
        "dst1",
        "dst2",
        "dst3",
        "dist4",
        "mom1",
        "mom2",
        "mom3",
        "mom4",
        "mom5",
        "prp1",
    }
    geometric_target_unit_ids = [
        item.get("id") for item in geometric_target.select("div.unit")
    ]
    if (
        len(geometric_target_unit_ids) != 14
        or set(item for item in geometric_target_unit_ids if item)
        != expected_geometric_named_unit_ids
        or geometric_target_unit_ids.count(None) != 1
        or len(geometric_target.find_all("details")) != 6
        or len(geometric_generic_segments) != 67
    ):
        raise RuntimeError(
            "Brown Geometric source topology differs from 14 exact unit divs, "
            "6 disclosures, and 67 segments"
        )
    geometric_reader_unit_ids = [
        item.get("id") for item in geometric_reader.select("div.unit")
    ]
    expected_geometric_reader_unit_ids = [
        "dst4" if item == "dist4" else "prp2" if item is None else item
        for item in geometric_target_unit_ids
    ]
    if (
        geometric_reader_unit_ids != expected_geometric_reader_unit_ids
        or len(geometric_reader.find_all("details")) != 8
    ):
        raise RuntimeError(
            "Brown Geometric reader topology differs from 14 corrected source "
            "unit divs and 8 total disclosures"
        )

    geometric_notes_by_id: dict[str, tuple[str, object]] = {}
    for reader_note in tuple(build_module.BROWN_GEOMETRIC_READER_NOTES):
        reader_note_html = str(reader_note["html"])
        reader_note_soup = BeautifulSoup(reader_note_html, "lxml")
        reader_note_root = reader_note_soup.body.find(True, recursive=False)
        if reader_note_root is None or not reader_note_root.get("id"):
            raise RuntimeError("Brown Geometric reader note lacks one stable root id")
        geometric_notes_by_id[str(reader_note_root["id"])] = (
            reader_note_html,
            reader_note_root,
        )
    if set(geometric_notes_by_id) != {
        "geometric-brownian-downstream-corrections",
        "geometric-brownian-offline-lab",
        "geometric-brownian-mastery",
    }:
        raise RuntimeError("Brown Geometric reader-note identities differ")

    geometric_correction_note = geometric_reader.find(
        "aside", id="geometric-brownian-downstream-corrections"
    )
    geometric_offline_lab = geometric_reader.find(
        "section", id="geometric-brownian-offline-lab"
    )
    geometric_mastery = geometric_reader.find(
        "aside", id="geometric-brownian-mastery"
    )
    geometric_mastery_exercise = geometric_reader.find(
        "p", id="geometric-brownian-mastery-exercise"
    )
    geometric_mastery_hint = geometric_reader.find(
        "details", id="geometric-brownian-mastery-hint"
    )
    geometric_mastery_solution = geometric_reader.find(
        "details", id="geometric-brownian-mastery-solution"
    )
    if any(
        item is None
        for item in (
            geometric_correction_note,
            geometric_offline_lab,
            geometric_mastery,
            geometric_mastery_exercise,
            geometric_mastery_hint,
            geometric_mastery_solution,
        )
    ):
        raise RuntimeError("Brown Geometric explicit reader additions are incomplete")
    if any(
        item.find_parent(id="geometric-brownian-mastery") is None
        for item in (
            geometric_mastery_exercise,
            geometric_mastery_hint,
            geometric_mastery_solution,
        )
    ):
        raise RuntimeError(
            "Brown Geometric mastery additions are attached to the wrong parent"
        )

    geometric_rights_id = "rights.o009.brown-geometric-original.cc-by-4.0"
    geometric_correction_note_html = geometric_notes_by_id[
        "geometric-brownian-downstream-corrections"
    ][0]
    geometric_correction_note_id = (
        "segment.o009.original.brown.geometric.downstream-correction-note"
    )
    segments.append(
        record(
            "segment",
            geometric_correction_note_id,
            parent_id=geometric_page_id,
            order=10000,
            path=geometric_rel,
            source_local_id="geometric-brownian-downstream-corrections",
            source_locator=(
                "scripts/build_first_boundary.py#geometric-brownian-downstream-corrections"
            ),
            source_sha256=sha256(geometric_correction_note_html.encode("utf-8")),
            target_sha256=sha256(str(geometric_correction_note).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=geometric_rights_id,
            concept_ids=["concept.brownian.geometric-motion"],
            payload={
                "target_text": " ".join(geometric_correction_note.stripped_strings),
                "tag": "aside",
                "built_id": "geometric-brownian-downstream-corrections",
                "body_extent": "complete-build-addition",
            },
        )
    )

    geometric_offline_lab_id = "unit.o009.original.brown.geometric.offline-lab"
    geometric_offline_lab_html = geometric_notes_by_id[
        "geometric-brownian-offline-lab"
    ][0]
    entities.append(
        record(
            "unit",
            geometric_offline_lab_id,
            parent_id=geometric_page_id,
            order=10010,
            path=geometric_rel,
            source_local_id="geometric-brownian-offline-lab",
            source_locator=(
                "scripts/build_first_boundary.py#geometric-brownian-offline-lab"
            ),
            source_sha256=sha256(geometric_offline_lab_html.encode("utf-8")),
            target_sha256=sha256(str(geometric_offline_lab).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=geometric_rights_id,
            concept_ids=[
                "concept.brownian.geometric-motion",
                "concept.probability.lognormal-distribution",
                "concept.brownian.geometric-moments",
                "concept.monte-carlo",
            ],
            payload={
                "unit_kind": "computational-lab",
                "tool_kind": "interactive-simulator",
                "runtime": "offline-browser/JavaScript",
                "offline_capable": True,
                "deterministic_seeded": True,
                "built_id": "geometric-brownian-offline-lab",
                "body_extent": "complete-build-addition",
                "source_supplied": False,
            },
        )
    )
    geometric_app_source = require_file(BROWN_GEOMETRIC_OFFLINE_APP)
    geometric_app_target = require_file(BUILT_BROWN_GEOMETRIC_OFFLINE_APP)
    if geometric_app_source != geometric_app_target:
        raise RuntimeError(
            "Brown Geometric built offline app differs from its authored source"
        )
    geometric_app_id = "asset.o009.geometric-brownian-offline-js"
    entities.append(
        record(
            "asset",
            geometric_app_id,
            parent_id=geometric_offline_lab_id,
            path=relative(BROWN_GEOMETRIC_OFFLINE_APP),
            source_locator=relative(BROWN_GEOMETRIC_OFFLINE_APP),
            source_sha256=sha256(geometric_app_source),
            target_sha256=sha256(geometric_app_target),
            locale="id-ID",
            translation_state="authored",
            relationship="copies",
            rights_id=geometric_rights_id,
            concept_ids=[
                "concept.brownian.geometric-motion",
                "concept.probability.lognormal-distribution",
                "concept.monte-carlo",
            ],
            payload={
                "bytes": len(geometric_app_source),
                "built_path": relative(BUILT_BROWN_GEOMETRIC_OFFLINE_APP),
                "runtime": "offline-browser/JavaScript",
                "deterministic_seeded": True,
            },
        )
    )

    geometric_mastery_id = "unit.o009.original.brown.geometric.mastery"
    geometric_mastery_html = geometric_notes_by_id["geometric-brownian-mastery"][0]
    entities.append(
        record(
            "unit",
            geometric_mastery_id,
            parent_id=geometric_page_id,
            order=10020,
            path=geometric_rel,
            source_local_id="geometric-brownian-mastery",
            source_locator=(
                "scripts/build_first_boundary.py#geometric-brownian-mastery"
            ),
            source_sha256=sha256(geometric_mastery_html.encode("utf-8")),
            target_sha256=sha256(str(geometric_mastery).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=geometric_rights_id,
            concept_ids=[
                "concept.brownian.geometric-motion",
                "concept.probability.lognormal-distribution",
                "concept.brownian.geometric-moments",
                "concept.brownian.exponential-martingale",
                "concept.conditional.probability",
            ],
            payload={
                "unit_kind": "mastery-sequence",
                "built_id": "geometric-brownian-mastery",
                "body_extent": "complete-build-addition",
                "source_supplied": False,
            },
        )
    )
    geometric_mastery_source = geometric_notes_by_id[
        "geometric-brownian-mastery"
    ][1]
    geometric_mastery_parts = (
        (
            "exercise",
            geometric_mastery_source.find(
                "p", id="geometric-brownian-mastery-exercise"
            ),
            geometric_mastery_exercise,
            "exercise",
            1,
        ),
        (
            "hint",
            geometric_mastery_source.find(
                "details", id="geometric-brownian-mastery-hint"
            ),
            geometric_mastery_hint,
            "hint",
            2,
        ),
        (
            "solution",
            geometric_mastery_source.find(
                "details", id="geometric-brownian-mastery-solution"
            ),
            geometric_mastery_solution,
            "solution",
            3,
        ),
    )
    geometric_mastery_part_ids: dict[str, str] = {}
    for suffix, source_part, target_part, unit_kind, order in geometric_mastery_parts:
        if source_part is None or target_part is None:
            raise RuntimeError(
                f"Brown Geometric mastery {suffix} source/target surface is absent"
            )
        stable_id = f"{geometric_mastery_id}.{suffix}"
        geometric_mastery_part_ids[suffix] = stable_id
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=geometric_mastery_id,
                order=order,
                path=geometric_rel,
                source_local_id=str(target_part.get("id")),
                source_locator=(
                    f"scripts/build_first_boundary.py#geometric-brownian-mastery-{suffix}"
                ),
                source_sha256=sha256(str(source_part).encode("utf-8")),
                target_sha256=sha256(str(target_part).encode("utf-8")),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=geometric_rights_id,
                concept_ids=[
                    "concept.brownian.geometric-motion",
                    "concept.probability.lognormal-distribution",
                    "concept.brownian.exponential-martingale",
                    "concept.conditional.probability",
                ],
                payload={
                    "unit_kind": unit_kind,
                    "tag": target_part.name,
                    "built_id": str(target_part.get("id")),
                    "body_extent": "complete-build-addition",
                    "source_supplied": False,
                },
            )
        )

    def append_geometric_addition_segments(
        parent_id: str,
        nodes: Iterable[object],
        stable_prefix: str,
        locator: str,
        concept_ids: list[str],
    ) -> None:
        added = 0
        for node in nodes:
            target_text = " ".join(node.stripped_strings)
            if not target_text:
                continue
            added += 1
            digest = sha256(target_text.encode("utf-8"))
            segments.append(
                record(
                    "segment",
                    f"{stable_prefix}.{added:04d}",
                    parent_id=parent_id,
                    order=added,
                    path=geometric_rel,
                    source_locator=f"{locator}:segment-{added:04d}",
                    source_sha256=digest,
                    target_sha256=digest,
                    locale="id-ID",
                    translation_state="authored",
                    relationship="authored",
                    rights_id=geometric_rights_id,
                    concept_ids=concept_ids,
                    payload={
                        "target_text": target_text,
                        "tag": node.name,
                        "body_extent": "complete-build-addition-segment",
                    },
                )
            )
        if added == 0:
            raise RuntimeError(
                f"Brown Geometric reader addition has no segments: {stable_prefix}"
            )

    geometric_lab_nodes = geometric_offline_lab.find_all(
        (
            "p",
            "legend",
            "label",
            "button",
            "title",
            "desc",
            "caption",
            "th",
            "td",
            "noscript",
        )
    )
    append_geometric_addition_segments(
        geometric_offline_lab_id,
        geometric_lab_nodes,
        "segment.o009.original.brown.geometric.offline-lab",
        "scripts/build_first_boundary.py#geometric-brownian-offline-lab",
        [
            "concept.brownian.geometric-motion",
            "concept.probability.lognormal-distribution",
            "concept.monte-carlo",
        ],
    )
    geometric_mastery_intro_nodes = geometric_mastery.find_all(
        "p", recursive=False
    )[:2]
    append_geometric_addition_segments(
        geometric_mastery_id,
        geometric_mastery_intro_nodes,
        "segment.o009.original.brown.geometric.mastery",
        "scripts/build_first_boundary.py#geometric-brownian-mastery",
        ["concept.brownian.geometric-motion"],
    )
    append_geometric_addition_segments(
        geometric_mastery_part_ids["exercise"],
        [geometric_mastery_exercise],
        "segment.o009.original.brown.geometric.mastery.exercise",
        "scripts/build_first_boundary.py#geometric-brownian-mastery-exercise",
        [
            "concept.brownian.geometric-motion",
            "concept.conditional.probability",
            "concept.brownian.exponential-martingale",
        ],
    )
    append_geometric_addition_segments(
        geometric_mastery_part_ids["hint"],
        geometric_mastery_hint.find_all(("summary", "p")),
        "segment.o009.original.brown.geometric.mastery.hint",
        "scripts/build_first_boundary.py#geometric-brownian-mastery-hint",
        [
            "concept.brownian.geometric-motion",
            "concept.conditional.probability",
        ],
    )
    append_geometric_addition_segments(
        geometric_mastery_part_ids["solution"],
        geometric_mastery_solution.find_all(("summary", "p")),
        "segment.o009.original.brown.geometric.mastery.solution",
        "scripts/build_first_boundary.py#geometric-brownian-mastery-solution",
        [
            "concept.brownian.geometric-motion",
            "concept.probability.lognormal-distribution",
            "concept.brownian.exponential-martingale",
            "concept.conditional.probability",
        ],
    )

    relations.extend(
        [
            relation(
                "rel.contains.unit.o009.random.brown.geometric.downstream-correction-note",
                "contains",
                geometric_page_id,
                geometric_correction_note_id,
                "build/site/brown/Geometric.html#geometric-brownian-downstream-corrections",
            ),
            relation(
                "rel.contains.unit.o009.random.brown.geometric.offline-lab",
                "contains",
                geometric_page_id,
                geometric_offline_lab_id,
                "build/site/brown/Geometric.html#geometric-brownian-offline-lab",
            ),
            relation(
                "rel.depends-on.brown-geometric-offline-lab.definition",
                "depends-on",
                geometric_offline_lab_id,
                f"{geometric_page_id}.def1",
                "the simulator instantiates the geometric-Brownian definition",
            ),
            relation(
                "rel.depends-on.brown-geometric-offline-lab.javascript",
                "depends-on",
                geometric_offline_lab_id,
                geometric_app_id,
                "build/site/brown/Geometric.html#geometric-brownian-offline-lab script[src='../apps/geometric-brownian-offline.js']",
            ),
            relation(
                "rel.executes.brown-geometric-offline-lab.javascript",
                "executes",
                geometric_offline_lab_id,
                geometric_app_id,
                "source/original/geometric-brownian-offline.js is copied byte-for-byte into the offline reader",
            ),
            relation(
                "rel.assesses.brown-geometric-offline-lab.terminal-law",
                "assesses",
                geometric_offline_lab_id,
                "outcome.o009.simulate-geometric-brownian-terminal-law",
                "seeded exact-solution path and terminal-law simulation with theoretical/empirical moment comparison",
            ),
            relation(
                "rel.contains.unit.o009.random.brown.geometric.mastery",
                "contains",
                geometric_page_id,
                geometric_mastery_id,
                "build/site/brown/Geometric.html#geometric-brownian-mastery",
            ),
            relation(
                "rel.depends-on.brown-geometric-mastery.definition",
                "depends-on",
                geometric_mastery_id,
                f"{geometric_page_id}.def1",
                "the conditional-law exercise starts from the geometric-Brownian definition",
            ),
            relation(
                "rel.depends-on.brown-geometric-mastery.moments",
                "depends-on",
                geometric_mastery_id,
                f"{geometric_page_id}.mom1",
                "the conditional moments use the source lognormal moment formula",
            ),
            *(
                relation(
                    f"rel.contains.brown-geometric-mastery.{suffix}",
                    "contains",
                    geometric_mastery_id,
                    stable_id,
                    f"build/site/brown/Geometric.html#geometric-brownian-mastery-{suffix}",
                )
                for suffix, stable_id in geometric_mastery_part_ids.items()
            ),
            relation(
                "rel.precedes.brown-geometric-mastery.exercise.hint",
                "precedes",
                geometric_mastery_part_ids["exercise"],
                geometric_mastery_part_ids["hint"],
                "authored mastery sequence in reader DOM order",
            ),
            relation(
                "rel.precedes.brown-geometric-mastery.hint.solution",
                "precedes",
                geometric_mastery_part_ids["hint"],
                geometric_mastery_part_ids["solution"],
                "authored mastery sequence in reader DOM order",
            ),
            relation(
                "rel.hints.brown-geometric-mastery",
                "hints",
                geometric_mastery_part_ids["hint"],
                geometric_mastery_part_ids["exercise"],
                "build/site/brown/Geometric.html#geometric-brownian-mastery-hint",
            ),
            relation(
                "rel.solves.brown-geometric-mastery",
                "solves",
                geometric_mastery_part_ids["solution"],
                geometric_mastery_part_ids["exercise"],
                "build/site/brown/Geometric.html#geometric-brownian-mastery-solution",
            ),
            relation(
                "rel.assesses.brown-geometric-mastery",
                "assesses",
                geometric_mastery_part_ids["exercise"],
                "outcome.o009.solve-geometric-brownian-conditional-law",
                "original complete conditional-lognormal and discounted-martingale mastery exercise",
            ),
        ]
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
    for suffix, asset_id, evidence in (
        (
            "pot3",
            "asset.random.markov.recurrence.visits",
            "markov/Recurrence.html#pot3",
        ),
        (
            "rel8",
            "asset.random.markov.recurrence.partition",
            "markov/Recurrence.html#rel8",
        ),
        (
            "figure-003",
            "asset.random.markov.recurrence.classes",
            "markov/Recurrence.html canonical-decomposition figure",
        ),
        (
            "figure-004",
            "asset.random.markov.recurrence.state-1",
            "markov/Recurrence.html#fin1 state graph",
        ),
        (
            "figure-005",
            "asset.random.markov.recurrence.state-2",
            "markov/Recurrence.html#fin2 state graph",
        ),
        (
            "figure-006",
            "asset.random.markov.recurrence.state-3",
            "markov/Recurrence.html#fin3 state graph",
        ),
    ):
        relations.append(
            relation(
                f"rel.depends-on.unit.o009.random.markov.recurrence.{suffix}",
                "depends-on",
                f"unit.o009.random.markov.recurrence.{suffix}",
                asset_id,
                evidence,
            )
        )
    for suffix, asset_id, evidence in (
        (
            "cyc3",
            "asset.random.markov.periodicity.cyclic-classes",
            "markov/Periodicity.html#cyc3 cyclic-class diagram",
        ),
        (
            "figure-002",
            "asset.random.markov.periodicity.state-4",
            "markov/Periodicity.html#fin3 state graph",
        ),
    ):
        relations.append(
            relation(
                f"rel.depends-on.unit.o009.random.markov.periodicity.{suffix}",
                "depends-on",
                f"unit.o009.random.markov.periodicity.{suffix}",
                asset_id,
                evidence,
            )
        )
    for suffix, asset_id, evidence in (
        (
            "figure-001",
            "asset.random.markov.periodicity.cyclic-classes",
            "markov/Limiting.html periodic-chain cyclic-class diagram",
        ),
        (
            "figure-002",
            "asset.random.markov.recurrence.state-1",
            "markov/Limiting.html#fin2 state graph",
        ),
        (
            "figure-003",
            "asset.random.markov.recurrence.state-2",
            "markov/Limiting.html#fin3 state graph",
        ),
        (
            "figure-004",
            "asset.random.markov.recurrence.state-3",
            "markov/Limiting.html#fin4 state graph",
        ),
        (
            "figure-005",
            "asset.random.markov.periodicity.state-4",
            "markov/Limiting.html#fin5 state graph",
        ),
    ):
        relations.append(
            relation(
                f"rel.depends-on.unit.o009.random.markov.limiting.{suffix}",
                "depends-on",
                f"unit.o009.random.markov.limiting.{suffix}",
                asset_id,
                evidence,
            )
        )
    known_page_ids = set(page_ids)
    overview_relation_ids: set[str] = set()
    for overview_slug, children in OVERVIEW_CHILDREN.items():
        overview_id = f"unit.o009.random.{overview_slug}"
        if overview_id not in known_page_ids:
            raise RuntimeError(f"overview unit is absent from the backend: {overview_id}")
        overview_rel = str(
            next(spec["rel"] for spec in THEORY_SPECS if spec["slug"] == overview_slug)
        )
        overview_source = BeautifulSoup(
            require_file(AUTH_RANDOM / "static" / Path(overview_rel)).decode("utf-8"),
            "lxml",
        )
        source_hrefs = {
            str(anchor.get("href"))
            for anchor in overview_source.find_all("a", href=True)
        }
        for child_slug, child_href in children:
            child_id = f"unit.o009.random.{child_slug}"
            if child_id not in known_page_ids:
                raise RuntimeError(
                    f"selected overview child is absent from the backend: {child_id}"
                )
            if child_href not in source_hrefs:
                raise RuntimeError(
                    f"{overview_rel}: selected child link is absent: {child_href}"
                )
            relation_id = f"rel.contains.{overview_id}.{child_id}"
            overview_relation_ids.add(relation_id)
            relations.append(
                relation(
                    relation_id,
                    "contains",
                    overview_id,
                    child_id,
                    f"{overview_rel} overview link {child_href}",
                )
            )
    expected_overview_relation_count = sum(
        len(children) for children in OVERVIEW_CHILDREN.values()
    )
    if len(overview_relation_ids) != expected_overview_relation_count:
        raise RuntimeError(
            "overview/child containment relation identities are not one-to-one"
        )

    for left_spec, right_spec, left, right in zip(
        THEORY_SPECS, THEORY_SPECS[1:], page_ids, page_ids[1:]
    ):
        if int(right_spec["order"]) != int(left_spec["order"]) + 1:
            continue
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
            relation(
                "rel.depends-on.martingales-backwards.convergence",
                "depends-on",
                "unit.o009.random.martingales.backwards",
                "unit.o009.random.martingales.convergence",
                "martingales/Backwards.html uses ordinary martingale convergence and upcrossing results after reversing time",
            ),
            relation(
                "rel.depends-on.martingales-backwards.conditional-expectation",
                "depends-on",
                "unit.o009.random.martingales.backwards",
                "unit.o009.random.expect.conditional2",
                "martingales/Backwards.html constructs Doob reverse martingales with conditional expectation and the tower property",
            ),
            relation(
                "rel.depends-on.martingales-backwards.exchangeability",
                "depends-on",
                "unit.o009.random.martingales.backwards",
                "unit.o009.random.prob.probability-revisited",
                "martingales/Backwards.html applies the earlier exchangeability and tail-event concepts",
            ),
            relation(
                "rel.teaches.martingales-backwards.definition",
                "teaches",
                "unit.o009.random.martingales.backwards.dfn1",
                "outcome.o009.construct-reverse-martingales",
                "martingales/Backwards.html#dfn1 through #dfn3",
            ),
            relation(
                "rel.teaches.martingales-backwards.convergence",
                "teaches",
                "unit.o009.random.martingales.backwards.prp3",
                "outcome.o009.prove-reverse-martingale-convergence",
                "martingales/Backwards.html#prp3 and the following Lp extension",
            ),
            relation(
                "rel.teaches.martingales-backwards.lp-convergence",
                "teaches",
                "unit.o009.random.martingales.backwards.div-007",
                "outcome.o009.prove-reverse-martingale-convergence",
                "martingales/Backwards.html anonymous unit immediately after #prp3",
            ),
            relation(
                "rel.teaches.martingales-backwards.strong-law",
                "teaches",
                "unit.o009.random.martingales.backwards.div-008",
                "outcome.o009.derive-strong-law-reverse-martingale",
                "martingales/Backwards.html#lln",
            ),
            relation(
                "rel.depends-on.martingales-backwards.strong-law.o006-sampling",
                "depends-on",
                "unit.o009.random.martingales.backwards.div-008",
                "resource.o006.c140.shared",
                "the reverse-martingale application proves the strong law using sampling concepts; O006 owns the Random chapter-5 sampling source bytes",
            ),
            relation(
                "rel.teaches.martingales-backwards.exchangeability",
                "teaches",
                "unit.o009.random.martingales.backwards.exc1",
                "outcome.o009.analyze-exchangeability-conditional-iid",
                "martingales/Backwards.html#exc1",
            ),
            relation(
                "rel.teaches.martingales-backwards.de-finetti",
                "teaches",
                "unit.o009.random.martingales.backwards.exc2",
                "outcome.o009.prove-binary-de-finetti",
                "martingales/Backwards.html#exc2",
            ),
            relation(
                "rel.depends-on.markov-discrete.markov-general",
                "depends-on",
                "unit.o009.random.markov.discrete",
                "unit.o009.random.markov.general",
                "Discrete.html specializes the all-state Markov family, transition kernels, and strong-property conventions from General.html",
            ),
            relation(
                "rel.depends-on.markov-discrete.processes",
                "depends-on",
                "unit.o009.random.markov.discrete",
                "unit.o009.random.prob.processes",
                "Discrete.html uses stochastic-process and finite-dimensional-distribution foundations",
            ),
            relation(
                "rel.depends-on.markov-discrete.stopping-times",
                "depends-on",
                "unit.o009.random.markov.discrete",
                "unit.o009.random.prob.stop",
                "Discrete.html uses filtrations, entrance times, and sigma-algebras at stopping times",
            ),
            relation(
                "rel.depends-on.markov-discrete.kernels",
                "depends-on",
                "unit.o009.random.markov.discrete",
                "unit.o009.random.expect.kernels",
                "Discrete transition matrices are countable-state probability kernels and operators",
            ),
            relation(
                "rel.depends-on.markov-discrete.random-walk.o006-sampling",
                "depends-on",
                "unit.o009.random.markov.discrete.ind2",
                "resource.o006.c140.shared",
                "the independent-increment random-walk subsection uses the shared i.i.d. sampling prerequisite without importing O006 chapter-5 bytes",
            ),
            relation(
                "rel.teaches.markov-discrete.definition",
                "teaches",
                "unit.o009.random.markov.discrete.dfn1",
                "outcome.o009.characterize-discrete-markov-chains",
                "markov/Discrete.html#dfn1 through #dfn5",
            ),
            relation(
                "rel.teaches.markov-discrete.transition-laws",
                "teaches",
                "unit.o009.random.markov.discrete.trn2",
                "outcome.o009.compute-discrete-transition-laws",
                "markov/Discrete.html#trn1 through #trn6",
            ),
            relation(
                "rel.teaches.markov-discrete.potential",
                "teaches",
                "unit.o009.random.markov.discrete.pot8",
                "outcome.o009.analyze-discrete-potential-and-restriction",
                "markov/Discrete.html#pot1 through #pot8",
            ),
            relation(
                "rel.teaches.markov-discrete.restriction",
                "teaches",
                "unit.o009.random.markov.discrete.smp2",
                "outcome.o009.analyze-discrete-potential-and-restriction",
                "markov/Discrete.html#smp2",
            ),
            relation(
                "rel.teaches.markov-discrete.finite-models",
                "teaches",
                "unit.o009.random.markov.discrete.two1",
                "outcome.o009.solve-finite-discrete-chain-models",
                "markov/Discrete.html#two1 through #dbl6",
            ),
            relation(
                "rel.assesses.markov-discrete.com1",
                "assesses",
                "unit.o009.random.markov.discrete.com1",
                "outcome.o009.solve-finite-discrete-chain-models",
                "markov/Discrete.html#com1",
            ),
            relation(
                "rel.assesses.markov-discrete.com2",
                "assesses",
                "unit.o009.random.markov.discrete.com2",
                "outcome.o009.analyze-discrete-potential-and-restriction",
                "markov/Discrete.html#com2",
            ),
            relation(
                "rel.assesses.markov-discrete.com3",
                "assesses",
                "unit.o009.random.markov.discrete.com3",
                "outcome.o009.solve-finite-discrete-chain-models",
                "markov/Discrete.html#com3",
            ),
            relation(
                "rel.assesses.markov-discrete.com4",
                "assesses",
                "unit.o009.random.markov.discrete.com4",
                "outcome.o009.analyze-discrete-potential-and-restriction",
                "markov/Discrete.html#com4",
            ),
            relation(
                "rel.assesses.markov-discrete.dbl4",
                "assesses",
                "unit.o009.random.markov.discrete.dbl4",
                "outcome.o009.solve-finite-discrete-chain-models",
                "markov/Discrete.html#dbl4",
            ),
            relation(
                "rel.assesses.markov-discrete.ind3",
                "assesses",
                "unit.o009.random.markov.discrete.ind3",
                "outcome.o009.compute-discrete-transition-laws",
                "markov/Discrete.html#ind3",
            ),
            relation(
                "rel.assesses.markov-discrete.dbl6",
                "assesses",
                "unit.o009.random.markov.discrete.dbl6",
                "outcome.o009.solve-finite-discrete-chain-models",
                "markov/Discrete.html#dbl6",
            ),
            relation(
                "rel.solves.markov-discrete.com1",
                "solves",
                "unit.o009.random.markov.discrete.details-015",
                "unit.o009.random.markov.discrete.com1",
                "markov/Discrete.html#com1 worked disclosure",
            ),
            relation(
                "rel.solves.markov-discrete.com2",
                "solves",
                "unit.o009.random.markov.discrete.details-016",
                "unit.o009.random.markov.discrete.com2",
                "markov/Discrete.html#com2 worked disclosure",
            ),
            relation(
                "rel.solves.markov-discrete.com3",
                "solves",
                "unit.o009.random.markov.discrete.details-017",
                "unit.o009.random.markov.discrete.com3",
                "markov/Discrete.html#com3 worked disclosure",
            ),
            relation(
                "rel.solves.markov-discrete.com4",
                "solves",
                "unit.o009.random.markov.discrete.details-018",
                "unit.o009.random.markov.discrete.com4",
                "markov/Discrete.html#com4 worked disclosure",
            ),
            relation(
                "rel.solves.markov-discrete.ind3",
                "solves",
                "unit.o009.random.markov.discrete.details-025",
                "unit.o009.random.markov.discrete.ind3",
                "markov/Discrete.html#ind3 worked disclosure",
            ),
            relation(
                "rel.solves.markov-discrete.dbl4",
                "solves",
                "unit.o009.random.markov.discrete.details-028",
                "unit.o009.random.markov.discrete.dbl4",
                "markov/Discrete.html#dbl4 worked disclosure",
            ),
            relation(
                "rel.solves.markov-discrete.dbl6",
                "solves",
                "unit.o009.random.markov.discrete.details-030",
                "unit.o009.random.markov.discrete.dbl6",
                "markov/Discrete.html#dbl6 worked disclosure",
            ),
            relation(
                "rel.depends-on.markov-recurrence.markov-discrete",
                "depends-on",
                "unit.o009.random.markov.recurrence",
                "unit.o009.random.markov.discrete",
                "Recurrence.html uses first-positive hitting times, transition powers, restricted matrices, and all-state chain laws from Discrete.html",
            ),
            relation(
                "rel.depends-on.markov-recurrence.stopping-times",
                "depends-on",
                "unit.o009.random.markov.recurrence",
                "unit.o009.random.prob.stop",
                "Recurrence.html treats first-positive hitting times as stopping times for the natural filtration",
            ),
            relation(
                "rel.depends-on.markov-recurrence.kernels",
                "depends-on",
                "unit.o009.random.markov.recurrence",
                "unit.o009.random.expect.kernels",
                "Recurrence.html uses positive kernels, restricted kernel operators, and monotone or bounded convergence",
            ),
            relation(
                "rel.teaches.markov-recurrence.hitting",
                "teaches",
                "unit.o009.random.markov.recurrence.hit1",
                "outcome.o009.compute-markov-hitting-and-green-quantities",
                "markov/Recurrence.html#hit1 through #hit5",
            ),
            relation(
                "rel.teaches.markov-recurrence.green",
                "teaches",
                "unit.o009.random.markov.recurrence.pot6",
                "outcome.o009.compute-markov-hitting-and-green-quantities",
                "markov/Recurrence.html#pot1 through #pot6",
            ),
            relation(
                "rel.teaches.markov-recurrence.classes",
                "teaches",
                "unit.o009.random.markov.recurrence.rel10",
                "outcome.o009.classify-markov-states-and-classes",
                "markov/Recurrence.html#rel1 through #cls4",
            ),
            relation(
                "rel.teaches.markov-recurrence.canonical-decomposition",
                "teaches",
                "unit.o009.random.markov.recurrence.cls4",
                "outcome.o009.classify-markov-states-and-classes",
                "markov/Recurrence.html canonical-decomposition paragraph and figure",
            ),
            relation(
                "rel.teaches.markov-recurrence.staying-test",
                "teaches",
                "unit.o009.random.markov.recurrence.tst4",
                "outcome.o009.analyze-markov-staying-probabilities",
                "markov/Recurrence.html#tst1 through #tst4",
            ),
            relation(
                "rel.teaches.markov-recurrence.computation",
                "teaches",
                "unit.o009.random.markov.recurrence.com4",
                "outcome.o009.compute-markov-hitting-and-green-quantities",
                "markov/Recurrence.html#com1 through #com4",
            ),
            relation(
                "rel.assesses.markov-recurrence.fin1",
                "assesses",
                "unit.o009.random.markov.recurrence.fin1",
                "outcome.o009.solve-finite-recurrence-models",
                "markov/Recurrence.html#fin1",
            ),
            relation(
                "rel.assesses.markov-recurrence.fin2",
                "assesses",
                "unit.o009.random.markov.recurrence.fin2",
                "outcome.o009.solve-finite-recurrence-models",
                "markov/Recurrence.html#fin2",
            ),
            relation(
                "rel.assesses.markov-recurrence.fin3",
                "assesses",
                "unit.o009.random.markov.recurrence.fin3",
                "outcome.o009.solve-finite-recurrence-models",
                "markov/Recurrence.html#fin3",
            ),
            relation(
                "rel.solves.markov-recurrence.fin1",
                "solves",
                "unit.o009.random.markov.recurrence.details-025",
                "unit.o009.random.markov.recurrence.fin1",
                "markov/Recurrence.html#fin1 worked disclosure",
            ),
            relation(
                "rel.solves.markov-recurrence.fin2",
                "solves",
                "unit.o009.random.markov.recurrence.details-026",
                "unit.o009.random.markov.recurrence.fin2",
                "markov/Recurrence.html#fin2 worked disclosure",
            ),
            relation(
                "rel.solves.markov-recurrence.fin3",
                "solves",
                "unit.o009.random.markov.recurrence.details-027",
                "unit.o009.random.markov.recurrence.fin3",
                "markov/Recurrence.html#fin3 worked disclosure",
            ),
            relation(
                "rel.depends-on.markov-periodicity.markov-discrete",
                "depends-on",
                "unit.o009.random.markov.periodicity",
                "unit.o009.random.markov.discrete",
                "Periodicity.html uses transition powers, irreducibility, state graphs, and deterministic-time sampled chains from Discrete.html",
            ),
            relation(
                "rel.depends-on.markov-periodicity.markov-recurrence",
                "depends-on",
                "unit.o009.random.markov.periodicity",
                "unit.o009.random.markov.recurrence",
                "Periodicity.html uses accessibility, communication classes, and class properties from Recurrence.html",
            ),
            relation(
                "rel.teaches.markov-periodicity.period",
                "teaches",
                "unit.o009.random.markov.periodicity.dfn1",
                "outcome.o009.characterize-markov-periodicity",
                "markov/Periodicity.html#dfn1 through #dfn3",
            ),
            relation(
                "rel.teaches.markov-periodicity.cyclic-decomposition",
                "teaches",
                "unit.o009.random.markov.periodicity.cyc1",
                "outcome.o009.construct-markov-cyclic-decomposition",
                "markov/Periodicity.html#cyc1 through #cyc3",
            ),
            relation(
                "rel.assesses.markov-periodicity.fin1",
                "assesses",
                "unit.o009.random.markov.periodicity.fin1",
                "outcome.o009.solve-finite-periodicity-models",
                "markov/Periodicity.html#fin1",
            ),
            relation(
                "rel.assesses.markov-periodicity.fin3",
                "assesses",
                "unit.o009.random.markov.periodicity.fin3",
                "outcome.o009.solve-finite-periodicity-models",
                "markov/Periodicity.html#fin3",
            ),
            relation(
                "rel.solves.markov-periodicity.fin1",
                "solves",
                "unit.o009.random.markov.periodicity.details-004",
                "unit.o009.random.markov.periodicity.fin1",
                "markov/Periodicity.html#fin1 worked disclosure",
            ),
            relation(
                "rel.solves.markov-periodicity.fin3",
                "solves",
                "unit.o009.random.markov.periodicity.details-005",
                "unit.o009.random.markov.periodicity.fin3",
                "markov/Periodicity.html#fin3 worked disclosure",
            ),
            relation(
                "rel.depends-on.markov-limiting.markov-discrete",
                "depends-on",
                "unit.o009.random.markov.limiting",
                "unit.o009.random.markov.discrete",
                "Limiting.html uses transition matrices, invariant distributions, and deterministic-time sampled chains from Discrete.html",
            ),
            relation(
                "rel.depends-on.markov-limiting.markov-recurrence",
                "depends-on",
                "unit.o009.random.markov.limiting",
                "unit.o009.random.markov.recurrence",
                "Limiting.html uses hitting probabilities, visit counts, Green matrices, and recurrent/transient classes from Recurrence.html",
            ),
            relation(
                "rel.depends-on.markov-limiting.markov-periodicity",
                "depends-on",
                "unit.o009.random.markov.limiting",
                "unit.o009.random.markov.periodicity",
                "Limiting.html uses periods, cyclic classes, and the aperiodic d-step chain from Periodicity.html",
            ),
            relation(
                "rel.teaches.markov-limiting.embedded-renewal",
                "teaches",
                "unit.o009.random.markov.limiting.ren1",
                "outcome.o009.derive-markov-renewal-limits",
                "markov/Limiting.html#ren1",
            ),
            relation(
                "rel.teaches.markov-limiting.renewal-limits",
                "teaches",
                "unit.o009.random.markov.limiting.lim5",
                "outcome.o009.derive-markov-renewal-limits",
                "markov/Limiting.html#lim1 through #lim5",
            ),
            relation(
                "rel.teaches.markov-limiting.positive-null-recurrence",
                "teaches",
                "unit.o009.random.markov.limiting.pos1",
                "outcome.o009.classify-positive-null-recurrence",
                "markov/Limiting.html#pos1 through #pos6",
            ),
            relation(
                "rel.teaches.markov-limiting.ergodic-definition",
                "teaches",
                "unit.o009.random.markov.limiting.rev1",
                "outcome.o009.analyze-markov-ergodic-periodic-limits",
                "markov/Limiting.html#rev1",
            ),
            relation(
                "rel.teaches.markov-limiting.periodic-subsequence-limits",
                "teaches",
                "unit.o009.random.markov.limiting.rev3",
                "outcome.o009.analyze-markov-ergodic-periodic-limits",
                "markov/Limiting.html#rev2 through #rev4",
            ),
            relation(
                "rel.teaches.markov-limiting.invariant-existence",
                "teaches",
                "unit.o009.random.markov.limiting.inv2",
                "outcome.o009.characterize-markov-invariant-measures",
                "markov/Limiting.html#inv1 through #inv2",
            ),
            relation(
                "rel.teaches.markov-limiting.invariant-mixtures",
                "teaches",
                "unit.o009.random.markov.limiting.inv3",
                "outcome.o009.characterize-markov-invariant-measures",
                "markov/Limiting.html#inv3",
            ),
            relation(
                "rel.teaches.markov-limiting.invariant-measure-uniqueness",
                "teaches",
                "unit.o009.random.markov.limiting.mea2",
                "outcome.o009.characterize-markov-invariant-measures",
                "markov/Limiting.html#mea1 through #mea2",
            ),
            relation(
                "rel.assesses.markov-limiting.div-023",
                "assesses",
                "unit.o009.random.markov.limiting.div-023",
                "outcome.o009.analyze-markov-ergodic-periodic-limits",
                "markov/Limiting.html two-state simulation exercise after #fin1",
            ),
            *(
                relation(
                    f"rel.assesses.markov-limiting.{exercise_id}",
                    "assesses",
                    f"unit.o009.random.markov.limiting.{exercise_id}",
                    "outcome.o009.solve-finite-limiting-models",
                    f"markov/Limiting.html#{exercise_id}",
                )
                for exercise_id in ("fin1", "fin2", "fin3", "fin4", "fin5")
            ),
            *(
                relation(
                    f"rel.solves.markov-limiting.{exercise_id}",
                    "solves",
                    f"unit.o009.random.markov.limiting.{details_id}",
                    f"unit.o009.random.markov.limiting.{exercise_id}",
                    f"markov/Limiting.html#{exercise_id} worked disclosure",
                )
                for exercise_id, details_id in (
                    ("fin1", "details-018"),
                    ("fin2", "details-019"),
                    ("fin3", "details-020"),
                    ("fin4", "details-021"),
                    ("fin5", "details-022"),
                )
            ),
            relation(
                "rel.contains.course.o009.unit.o009.random.poisson.general",
                "contains",
                "course.o009.d30",
                "unit.o009.random.poisson.general",
                "backend curriculum order 28; Random general-space Poisson bridge",
            ),
            relation(
                "rel.precedes.unit.o009.quantecon.ctmc.stationarity-ergodicity.unit.o009.random.poisson.general",
                "precedes",
                "unit.o009.quantecon.ctmc.stationarity-ergodicity",
                "unit.o009.random.poisson.general",
                "curriculum order 27 to 28; QuantEcon block remains between the Random theory blocks",
            ),
            relation(
                "rel.depends-on.poisson-general.quantecon-poisson",
                "depends-on",
                "unit.o009.random.poisson.general",
                "unit.o009.quantecon.ctmc.poisson-processes",
                "poisson/General.html extends the one-dimensional counting-process treatment to general measure spaces",
            ),
            relation(
                "rel.depends-on.poisson-general.probability-measure-space",
                "depends-on",
                "unit.o009.random.poisson.general",
                "unit.o009.random.prob.probability-revisited",
                "poisson/General.html assumes probability and measure-space language from Probability2.html",
            ),
            relation(
                "rel.teaches.poisson-general.random-measure",
                "teaches",
                "unit.o009.random.poisson.general.pro1",
                "outcome.o009.formulate-poisson-random-measures",
                "poisson/General.html#pro1",
            ),
            relation(
                "rel.teaches.poisson-general.moments",
                "teaches",
                "unit.o009.random.poisson.general.pro3",
                "outcome.o009.formulate-poisson-random-measures",
                "poisson/General.html#pro3",
            ),
            *(
                relation(
                    f"rel.teaches.poisson-general.conditional-law.{local_id}",
                    "teaches",
                    f"unit.o009.random.poisson.general.{local_id}",
                    "outcome.o009.derive-conditional-poisson-point-laws",
                    f"poisson/General.html#{local_id}",
                )
                for local_id in ("dst1", "dst2", "dst3")
            ),
            *(
                relation(
                    f"rel.teaches.poisson-general.thinning-superposition.{local_id}",
                    "teaches",
                    f"unit.o009.random.poisson.general.{local_id}",
                    "outcome.o009.analyze-poisson-thinning-superposition",
                    f"poisson/General.html#{local_id}",
                )
                for local_id in ("spl1", "spl2")
            ),
            relation(
                "rel.teaches.poisson-general.nonhomogeneous",
                "teaches",
                "unit.o009.random.poisson.general.div-010",
                "outcome.o009.analyze-spatial-poisson-models",
                "poisson/General.html anonymous nonhomogeneous-process theorem at DOM unit 10",
            ),
            *(
                relation(
                    f"rel.teaches.poisson-general.nearest-neighbor.{local_id}",
                    "teaches",
                    f"unit.o009.random.poisson.general.{local_id}",
                    "outcome.o009.analyze-spatial-poisson-models",
                    f"poisson/General.html#{local_id}",
                )
                for local_id in ("nea1", "nea2")
            ),
            *(
                relation(
                    f"rel.assesses.poisson-general.{exercise_id}",
                    "assesses",
                    f"unit.o009.random.poisson.general.{exercise_id}",
                    outcome_id,
                    f"poisson/General.html#{exercise_id}",
                )
                for exercise_id, outcome_id in (
                    ("exe1", "outcome.o009.analyze-spatial-poisson-models"),
                    ("exe2", "outcome.o009.analyze-spatial-poisson-models"),
                    ("exe3", "outcome.o009.analyze-spatial-poisson-models"),
                    ("exe4", "outcome.o009.derive-conditional-poisson-point-laws"),
                    ("exe5", "outcome.o009.derive-conditional-poisson-point-laws"),
                    ("exe6", "outcome.o009.analyze-poisson-thinning-superposition"),
                )
            ),
            *(
                relation(
                    f"rel.solves.poisson-general.{exercise_id}",
                    "solves",
                    f"unit.o009.random.poisson.general.{details_id}",
                    f"unit.o009.random.poisson.general.{exercise_id}",
                    f"poisson/General.html#{exercise_id} answer disclosure",
                )
                for exercise_id, details_id in (
                    ("exe1", "details-008"),
                    ("exe2", "details-009"),
                    ("exe3", "details-010"),
                    ("exe4", "details-011"),
                    ("exe5", "details-012"),
                    ("exe6", "details-013"),
                )
            ),
            relation(
                "rel.contains.course.o009.unit.o009.random.brown.standard",
                "contains",
                "course.o009.d30",
                "unit.o009.random.brown.standard",
                "backend curriculum order 29; Standard Brownian Motion reader",
            ),
            relation(
                "rel.depends-on.brown-standard.prob-processes",
                "depends-on",
                "unit.o009.random.brown.standard",
                "unit.o009.random.prob.processes",
                "Brownian motion is introduced as a continuous-time stochastic process",
            ),
            relation(
                "rel.depends-on.brown-standard.prob-stop",
                "depends-on",
                "unit.o009.random.brown.standard",
                "unit.o009.random.prob.stop",
                "hitting-time and strong-Markov arguments use stopping times",
            ),
            relation(
                "rel.depends-on.brown-standard.markov-general",
                "depends-on",
                "unit.o009.random.brown.standard",
                "unit.o009.random.markov.general",
                "the Markov and strong Markov properties depend on the general Markov-process unit",
            ),
            relation(
                "rel.depends-on.brown-standard.martingales-introduction",
                "depends-on",
                "unit.o009.random.brown.standard",
                "unit.o009.random.martingales.introduction",
                "the standard process and its quadratic compensation are martingales",
            ),
            relation(
                "rel.depends-on.brown-standard.o006",
                "depends-on",
                "unit.o009.random.brown.standard",
                "resource.o006.c140.shared",
                "Gaussian and random-walk approximation language reuses the frozen O006 sampling prerequisite",
            ),
            relation(
                "rel.depends-on.brown-standard.apps-js",
                "depends-on",
                "unit.o009.random.brown.standard",
                "asset.random.apps.core",
                "brown/Standard.html launches simulations through apps/Apps.js",
            ),
            relation(
                "rel.depends-on.brown-standard.distributions-js",
                "depends-on",
                "unit.o009.random.brown.standard",
                "asset.random.apps.distributions",
                "Brownian simulators use the shared distribution library",
            ),
            relation(
                "rel.teaches.brown-standard.definition",
                "teaches",
                "unit.o009.random.brown.standard.def1",
                "outcome.o009.characterize-standard-brownian-motion",
                "brown/Standard.html#def1",
            ),
            relation(
                "rel.teaches.brown-standard.gaussian-laws",
                "teaches",
                "unit.o009.random.brown.standard.dis1",
                "outcome.o009.characterize-standard-brownian-motion",
                "brown/Standard.html#dis1",
            ),
            relation(
                "rel.teaches.brown-standard.scaling-irregularity",
                "teaches",
                "unit.o009.random.brown.standard.irr2",
                "outcome.o009.analyze-brownian-scaling-irregularity",
                "brown/Standard.html#irr2",
            ),
            relation(
                "rel.teaches.brown-standard.strong-markov-reflection",
                "teaches",
                "unit.o009.random.brown.standard.ref1",
                "outcome.o009.apply-brownian-strong-markov-reflection",
                "brown/Standard.html#ref1",
            ),
            relation(
                "rel.teaches.brown-standard.hitting-maximum",
                "teaches",
                "unit.o009.random.brown.standard.max1",
                "outcome.o009.derive-brownian-hitting-maximum-laws",
                "brown/Standard.html#max1",
            ),
            relation(
                "rel.teaches.brown-standard.arcsine-law",
                "teaches",
                "unit.o009.random.brown.standard.arc1",
                "outcome.o009.analyze-brownian-zero-arcsine-lil",
                "brown/Standard.html#arc1",
            ),
            relation(
                "rel.teaches.brown-standard.iterated-logarithm",
                "teaches",
                "unit.o009.random.brown.standard.lil1",
                "outcome.o009.analyze-brownian-zero-arcsine-lil",
                "brown/Standard.html#lil1 and the explicit two-sided consequence",
            ),
            relation(
                "rel.assesses.brown-standard.div-050",
                "assesses",
                "unit.o009.random.brown.standard.div-050",
                "outcome.o009.solve-brownian-joint-gaussian",
                "brown/Standard.html anonymous computational exercise at DOM unit 50",
            ),
            relation(
                "rel.contains.course.o009.unit.o009.random.brown.drift",
                "contains",
                "course.o009.d30",
                "unit.o009.random.brown.drift",
                "backend curriculum order 30; Brownian Motion with Drift reader",
            ),
            relation(
                "rel.depends-on.brown-drift.brown-standard",
                "depends-on",
                "unit.o009.random.brown.drift",
                "unit.o009.random.brown.standard",
                "the drifted/scaled process is constructed from and compared with standard Brownian motion",
            ),
            relation(
                "rel.depends-on.brown-drift.prob-processes",
                "depends-on",
                "unit.o009.random.brown.drift",
                "unit.o009.random.prob.processes",
                "finite-dimensional laws and process equivalence use the stochastic-process foundation",
            ),
            relation(
                "rel.depends-on.brown-drift.prob-stop",
                "depends-on",
                "unit.o009.random.brown.drift",
                "unit.o009.random.prob.stop",
                "the strong-Markov statement uses stopping times and stopped sigma-algebras",
            ),
            relation(
                "rel.depends-on.brown-drift.markov-general",
                "depends-on",
                "unit.o009.random.brown.drift",
                "unit.o009.random.markov.general",
                "the transition density and strong property instantiate the general Markov-process unit",
            ),
            *(
                relation(
                    f"rel.teaches.brown-drift.characterization.{local_id}",
                    "teaches",
                    f"unit.o009.random.brown.drift.{local_id}",
                    "outcome.o009.characterize-brownian-drift-scaling",
                    f"brown/Drift.html#{local_id}",
                )
                for local_id in ("def1", "def3", "dis1", "dis2", "trn1", "trn2", "trn3")
            ),
            relation(
                "rel.assesses.brown-drift.def2",
                "assesses",
                "unit.o009.random.brown.drift.def2",
                "outcome.o009.simulate-brownian-drift-terminal-law",
                "brown/Drift.html#def2 official online simulation activity",
            ),
            relation(
                "rel.teaches.brown-drift.transition-density.mar1",
                "teaches",
                "unit.o009.random.brown.drift.mar1",
                "outcome.o009.derive-brownian-drift-transition-laws",
                "brown/Drift.html#mar1",
            ),
            relation(
                "rel.teaches.brown-drift.diffusion-equations.mar2",
                "teaches",
                "unit.o009.random.brown.drift.mar2",
                "outcome.o009.derive-brownian-drift-transition-laws",
                "brown/Drift.html#mar2",
            ),
            relation(
                "rel.teaches.brown-drift.strong-markov.mar3",
                "teaches",
                "unit.o009.random.brown.drift.mar3",
                "outcome.o009.verify-brownian-drift-strong-markov",
                "brown/Drift.html#mar3",
            ),
            relation(
                "rel.contains.course.o009.unit.o009.random.brown.bridge",
                "contains",
                "course.o009.d30",
                "unit.o009.random.brown.bridge",
                "backend curriculum order 31; Brownian Bridge reader",
            ),
            relation(
                "rel.depends-on.brown-bridge.brown-standard",
                "depends-on",
                "unit.o009.random.brown.bridge",
                "unit.o009.random.brown.standard",
                "the bridge constructions start from standard Brownian motion",
            ),
            relation(
                "rel.depends-on.brown-bridge.prob-processes",
                "depends-on",
                "unit.o009.random.brown.bridge",
                "unit.o009.random.prob.processes",
                "finite-dimensional laws and process-level convergence use the stochastic-process foundation",
            ),
            relation(
                "rel.depends-on.brown-bridge.expect-kernels",
                "depends-on",
                "unit.o009.random.brown.bridge",
                "unit.o009.random.expect.kernels",
                "the bridge conditioning theorem uses regular conditional distributions",
            ),
            *(
                relation(
                    f"rel.teaches.brown-bridge.constructions.{local_id}",
                    "teaches",
                    f"unit.o009.random.brown.bridge.{local_id}",
                    "outcome.o009.construct-brownian-bridges",
                    f"brown/Bridge.html#{local_id}",
                )
                for local_id in (
                    "def1",
                    "def2",
                    "def5",
                    "def7",
                    "def8",
                    "def6",
                    "div-009",
                    "gen1",
                    "gen2",
                )
            ),
            *(
                relation(
                    f"rel.assesses.brown-bridge.online-app.{local_id}",
                    "assesses",
                    f"unit.o009.random.brown.bridge.{local_id}",
                    "outcome.o009.simulate-brownian-bridge-marginal-law",
                    f"brown/Bridge.html#{local_id} official online simulation activity",
                )
                for local_id in ("def3", "def4")
            ),
            *(
                relation(
                    f"rel.teaches.brown-bridge.empirical-process.{local_id}",
                    "teaches",
                    f"unit.o009.random.brown.bridge.{local_id}",
                    "outcome.o009.analyze-brownian-bridge-empirical-process",
                    f"brown/Bridge.html#{local_id}",
                )
                for local_id in ("edf1", "edf2")
            ),
            relation(
                "rel.contains.course.o009.unit.o009.random.brown.geometric",
                "contains",
                "course.o009.d30",
                "unit.o009.random.brown.geometric",
                "backend curriculum order 32; Geometric Brownian Motion reader",
            ),
            relation(
                "rel.depends-on.brown-geometric.brown-standard",
                "depends-on",
                "unit.o009.random.brown.geometric",
                "unit.o009.random.brown.standard",
                "the exponential construction starts from standard Brownian motion",
            ),
            relation(
                "rel.depends-on.brown-geometric.brown-drift",
                "depends-on",
                "unit.o009.random.brown.geometric",
                "unit.o009.random.brown.drift",
                "the logarithm of the process is Brownian motion with drift and scale",
            ),
            relation(
                "rel.depends-on.brown-geometric.prob-processes",
                "depends-on",
                "unit.o009.random.brown.geometric",
                "unit.o009.random.prob.processes",
                "finite-dimensional distributions and adapted processes use the stochastic-process foundation",
            ),
            relation(
                "rel.depends-on.brown-geometric.martingales-introduction",
                "depends-on",
                "unit.o009.random.brown.geometric",
                "unit.o009.random.martingales.introduction",
                "the discounted-process conclusion uses the martingale definition",
            ),
            *(
                relation(
                    f"rel.teaches.brown-geometric.characterization.{local_id}",
                    "teaches",
                    f"unit.o009.random.brown.geometric.{local_id}",
                    "outcome.o009.characterize-geometric-brownian-motion",
                    f"brown/Geometric.html#{local_id}",
                )
                for local_id in ("def1", "def2")
            ),
            *(
                relation(
                    f"rel.teaches.brown-geometric.laws.{local_id}",
                    "teaches",
                    f"unit.o009.random.brown.geometric.{local_id}",
                    "outcome.o009.derive-geometric-brownian-laws",
                    f"brown/Geometric.html#{local_id}",
                )
                for local_id in ("dst1", "dst3", "dist4", "mom1", "mom2")
            ),
            *(
                relation(
                    f"rel.teaches.brown-geometric.asymptotics.{local_id}",
                    "teaches",
                    f"unit.o009.random.brown.geometric.{local_id}",
                    "outcome.o009.analyze-geometric-brownian-asymptotics",
                    f"brown/Geometric.html#{local_id}",
                )
                for local_id in ("mom3", "prp1", "div-014")
            ),
            *(
                relation(
                    f"rel.assesses.brown-geometric.online-app.{local_id}",
                    "assesses",
                    f"unit.o009.random.brown.geometric.{local_id}",
                    "outcome.o009.simulate-geometric-brownian-terminal-law",
                    f"brown/Geometric.html#{local_id} official online simulation activity",
                )
                for local_id in ("def3", "dst2", "mom4", "mom5")
            ),
        ]
    )
    return entities, segments, relations


def quantecon_entities(component: str = "memoryless") -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    """Export one admitted QuantEcon CTMC unit as a separate component lane."""
    if component == "memoryless":
        component_root = QUANTECON_COMPONENT
        component_source = QUANTECON_SOURCE
        component_notebook = QUANTECON_NOTEBOOK
        component_html = QUANTECON_HTML
        component_manifest = QUANTECON_MANIFEST
        component_receipt = QUANTECON_RECEIPT
        target_source = ROOT / "source" / "quantecon" / "lectures" / "memoryless.md"
        html_rel = "lectures/memoryless.html"
        unit_id = "unit.o009.quantecon.ctmc.memoryless-distributions"
        unit_order = 20
        unit_slug = "memoryless"
        contains_item = 23
        precedes_source = "unit.o009.random.markov.limiting"
        body_extent = "complete-first-unit"
        inherited_concept_ids: tuple[str, ...] = ()
        expected_topology = {"exercises": 2, "solutions": 2, "code_cells": 5}
        concept_labels = {
            "concept.markov.continuous-time": "continuous-time Markov chain",
            "concept.probability.memoryless": "memoryless property",
            "concept.probability.geometric-distribution": "geometric distribution",
            "concept.probability.exponential-distribution": "exponential distribution",
            "concept.probability.erlang-distribution": "Erlang distribution",
            "concept.stochastic.holding-time": "holding time between jumps",
        }
    elif component == "poisson":
        component_root = QUANTECON_POISSON_COMPONENT
        component_source = QUANTECON_POISSON_SOURCE
        component_notebook = QUANTECON_POISSON_NOTEBOOK
        component_html = QUANTECON_POISSON_HTML
        component_manifest = QUANTECON_POISSON_MANIFEST
        component_receipt = QUANTECON_POISSON_RECEIPT
        target_source = ROOT / "source" / "quantecon" / "lectures" / "poisson.md"
        html_rel = "lectures/poisson.html"
        unit_id = "unit.o009.quantecon.ctmc.poisson-processes"
        unit_order = 21
        unit_slug = "poisson"
        contains_item = 24
        precedes_source = "unit.o009.quantecon.ctmc.memoryless-distributions"
        body_extent = "complete-unit-local"
        inherited_concept_ids = ()
        expected_topology = {"exercises": 2, "solutions": 2, "code_cells": 7}
        concept_labels = {
            "concept.markov.continuous-time": "continuous-time Markov chain",
            "concept.probability.poisson-process": "Poisson process",
            "concept.probability.counting-process": "counting process",
            "concept.probability.stationary-independent-increments": "stationary independent increments",
            "concept.stochastic.holding-time": "holding time between jumps",
        }
    elif component == "markov_prop":
        component_root = QUANTECON_MARKOV_PROP_COMPONENT
        component_source = QUANTECON_MARKOV_PROP_SOURCE
        component_notebook = QUANTECON_MARKOV_PROP_NOTEBOOK
        component_html = QUANTECON_MARKOV_PROP_HTML
        component_manifest = QUANTECON_MARKOV_PROP_MANIFEST
        component_receipt = QUANTECON_MARKOV_PROP_RECEIPT
        target_source = ROOT / "source" / "quantecon" / "lectures" / "markov_prop.md"
        html_rel = "lectures/markov_prop.html"
        unit_id = "unit.o009.quantecon.ctmc.markov-property"
        unit_order = 22
        unit_slug = "markov_prop"
        contains_item = 25
        precedes_source = "unit.o009.quantecon.ctmc.poisson-processes"
        body_extent = "complete-unit-local"
        inherited_concept_ids = (
            "concept.markov.continuous-time",
            "concept.markov.transition-semigroup",
        )
        expected_topology = {"exercises": 4, "solutions": 4, "code_cells": 5}
        concept_labels = {
            "concept.markov.property": "Markov property",
            "concept.markov.embedded-jump-chain": "embedded jump chain",
            "concept.linear-algebra.matrix-exponential": "matrix exponential",
            "concept.markov.distribution-flow": "distribution flow",
        }
    elif component == "kolmogorov_bwd":
        component_root = QUANTECON_KOLMOGOROV_BWD_COMPONENT
        component_source = QUANTECON_KOLMOGOROV_BWD_SOURCE
        component_notebook = QUANTECON_KOLMOGOROV_BWD_NOTEBOOK
        component_html = QUANTECON_KOLMOGOROV_BWD_HTML
        component_manifest = QUANTECON_KOLMOGOROV_BWD_MANIFEST
        component_receipt = QUANTECON_KOLMOGOROV_BWD_RECEIPT
        target_source = ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_bwd.md"
        html_rel = "lectures/kolmogorov_bwd.html"
        unit_id = "unit.o009.quantecon.ctmc.kolmogorov-backward"
        unit_order = 23
        unit_slug = "kolmogorov_bwd"
        contains_item = 26
        precedes_source = "unit.o009.quantecon.ctmc.markov-property"
        body_extent = "complete-unit-local"
        inherited_concept_ids = (
            "concept.markov.continuous-time",
            "concept.markov.transition-semigroup",
            "concept.markov.embedded-jump-chain",
            "concept.linear-algebra.matrix-exponential",
        )
        expected_topology = {"exercises": 3, "solutions": 3, "code_cells": 6}
        concept_labels = {
            "concept.markov.kolmogorov-backward-equation": "Kolmogorov backward equation",
            "concept.markov.state-dependent-jump-intensity": "state-dependent jump intensity",
            "concept.markov.uniformization": "uniformization of a finite-state generator",
            "concept.markov.inventory-ctmc": "continuous-time inventory Markov chain",
        }
    elif component == "kolmogorov_fwd":
        component_root = QUANTECON_KOLMOGOROV_FWD_COMPONENT
        component_source = QUANTECON_KOLMOGOROV_FWD_SOURCE
        component_notebook = QUANTECON_KOLMOGOROV_FWD_NOTEBOOK
        component_html = QUANTECON_KOLMOGOROV_FWD_HTML
        component_manifest = QUANTECON_KOLMOGOROV_FWD_MANIFEST
        component_receipt = QUANTECON_KOLMOGOROV_FWD_RECEIPT
        target_source = ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_fwd.md"
        html_rel = "lectures/kolmogorov_fwd.html"
        unit_id = "unit.o009.quantecon.ctmc.kolmogorov-forward"
        unit_order = 24
        unit_slug = "kolmogorov_fwd"
        contains_item = 27
        precedes_source = "unit.o009.quantecon.ctmc.kolmogorov-backward"
        body_extent = "complete-unit-local"
        inherited_concept_ids = (
            "concept.markov.continuous-time",
            "concept.markov.transition-semigroup",
            "concept.markov.embedded-jump-chain",
            "concept.linear-algebra.matrix-exponential",
            "concept.markov.distribution-flow",
            "concept.markov.state-dependent-jump-intensity",
        )
        expected_topology = {"exercises": 3, "solutions": 3, "code_cells": 6}
        concept_labels = {
            "concept.markov.kolmogorov-forward-equation": "Kolmogorov forward equation",
            "concept.markov.intensity-matrix": "intensity matrix",
            "concept.markov.fokker-planck-equation": "Fokker--Planck equation",
            "concept.differential-equations.linear-vector-ode": "linear vector-valued ordinary differential equation",
        }
    elif component == "generators":
        component_root = QUANTECON_GENERATORS_COMPONENT
        component_source = QUANTECON_GENERATORS_SOURCE
        component_notebook = QUANTECON_GENERATORS_NOTEBOOK
        component_html = QUANTECON_GENERATORS_HTML
        component_manifest = QUANTECON_GENERATORS_MANIFEST
        component_receipt = QUANTECON_GENERATORS_RECEIPT
        target_source = ROOT / "source" / "quantecon" / "lectures" / "generators.md"
        html_rel = "lectures/generators.html"
        unit_id = "unit.o009.quantecon.ctmc.generators"
        unit_order = 25
        unit_slug = "generators"
        contains_item = 28
        precedes_source = "unit.o009.quantecon.ctmc.kolmogorov-forward"
        body_extent = "complete-unit-local"
        inherited_concept_ids = (
            "concept.markov.continuous-time",
            "concept.markov.transition-semigroup",
            "concept.linear-algebra.matrix-exponential",
            "concept.markov.intensity-matrix",
            "concept.differential-equations.linear-vector-ode",
        )
        expected_topology = {"exercises": 3, "solutions": 3, "code_cells": 0}
        concept_labels = {
            "concept.functional-analysis.banach-space": "Banach space",
            "concept.functional-analysis.bounded-linear-operator": "bounded linear operator",
            "concept.functional-analysis.operator-norm": "operator norm",
            "concept.semigroup.evolution": "evolution semigroup",
            "concept.semigroup.c0": "C0 semigroup",
            "concept.semigroup.uniformly-continuous": "uniformly continuous semigroup",
            "concept.semigroup.generator": "generator of an operator semigroup",
            "concept.differential-equations.abstract-cauchy-problem": "abstract Cauchy problem",
        }
    elif component == "uc_mc_semigroups":
        component_root = QUANTECON_UC_MC_SEMIGROUPS_COMPONENT
        component_source = QUANTECON_UC_MC_SEMIGROUPS_SOURCE
        component_notebook = QUANTECON_UC_MC_SEMIGROUPS_NOTEBOOK
        component_html = QUANTECON_UC_MC_SEMIGROUPS_HTML
        component_manifest = QUANTECON_UC_MC_SEMIGROUPS_MANIFEST
        component_receipt = QUANTECON_UC_MC_SEMIGROUPS_RECEIPT
        target_source = ROOT / "source" / "quantecon" / "lectures" / "uc_mc_semigroups.md"
        html_rel = "lectures/uc_mc_semigroups.html"
        unit_id = "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups"
        unit_order = 26
        unit_slug = "uc_mc_semigroups"
        contains_item = 29
        precedes_source = "unit.o009.quantecon.ctmc.generators"
        body_extent = "complete-unit-local"
        inherited_concept_ids = (
            "concept.markov.continuous-time",
            "concept.markov.transition-semigroup",
            "concept.linear-algebra.matrix-exponential",
            "concept.markov.intensity-matrix",
            "concept.functional-analysis.bounded-linear-operator",
            "concept.semigroup.uniformly-continuous",
            "concept.semigroup.generator",
        )
        expected_topology = {"exercises": 5, "solutions": 5, "code_cells": 0}
        concept_labels = {
            "concept.markov.conservative-intensity-matrix": "conservative intensity matrix in the source-local bounded-operator sense",
            "concept.markov.canonical-jump-chain-decomposition": "canonical jump-chain decomposition",
            "concept.markov.nonexplosion": "nonexplosion",
            "concept.markov.explosion": "explosion",
            "concept.markov.sub-markov-semigroup": "sub-Markov semigroup",
            "concept.markov.absorbing-state": "absorbing state",
        }
    elif component == "ergodicity":
        component_root = QUANTECON_ERGODICITY_COMPONENT
        component_source = QUANTECON_ERGODICITY_SOURCE
        component_notebook = QUANTECON_ERGODICITY_NOTEBOOK
        component_html = QUANTECON_ERGODICITY_HTML
        component_manifest = QUANTECON_ERGODICITY_MANIFEST
        component_receipt = QUANTECON_ERGODICITY_RECEIPT
        target_source = ROOT / "source" / "quantecon" / "lectures" / "ergodicity.md"
        html_rel = "lectures/ergodicity.html"
        unit_id = "unit.o009.quantecon.ctmc.stationarity-ergodicity"
        unit_order = 27
        unit_slug = "ergodicity"
        contains_item = 30
        precedes_source = "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups"
        body_extent = "complete-unit-local"
        inherited_concept_ids = (
            "concept.markov.continuous-time",
            "concept.markov.transition-semigroup",
            "concept.markov.intensity-matrix",
            "concept.markov.conservative-intensity-matrix",
            "concept.markov.accessibility",
            "concept.markov.irreducibility",
            "concept.semigroup.uniformly-continuous",
            "concept.semigroup.generator",
        )
        expected_topology = {"exercises": 3, "solutions": 3, "code_cells": 4}
        concept_labels = {
            "concept.markov.stationary-distribution": "stationary distribution",
            "concept.markov.asymptotic-stability": "asymptotic stability",
            "concept.markov.strict-contractivity": "strict l1 contractivity",
            "concept.markov.skeleton-chain": "fixed-step skeleton chain",
            "concept.markov.drift-criterion": "Foster--Lyapunov drift criterion",
            "concept.markov.mm1-queue": "M/M/1 queue",
        }
    else:
        raise RuntimeError(f"unknown QuantEcon component: {component}")
    receipt = load_json(component_receipt)
    manifest_hash = sha256(require_file(component_manifest))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon component receipt schema differs")
    if receipt.get("manifest_sha256") != manifest_hash:
        raise RuntimeError("QuantEcon component receipt does not bind its manifest")
    receipt_topology = receipt.get("topology", {})
    if any(int(receipt_topology.get(key, -1)) != value for key, value in expected_topology.items()):
        raise RuntimeError(
            f"QuantEcon {component} topology differs: "
            f"expected={expected_topology} receipt={receipt_topology}"
        )
    source_bytes = require_file(component_source)
    target_bytes = require_file(target_source)
    notebook_bytes = (
        require_file(component_notebook) if component_notebook is not None else None
    )
    html_bytes = require_file(component_html)
    if receipt.get("authority", {}).get("source_sha256") != sha256(source_bytes):
        raise RuntimeError("QuantEcon authority source hash differs")
    if component_notebook is None:
        if receipt.get("authority", {}).get("notebook_status") != "not_present_in_authority":
            raise RuntimeError("QuantEcon no-notebook authority status differs")
        if receipt.get("authority", {}).get("notebook_sha256") not in {None, ""}:
            raise RuntimeError("QuantEcon no-notebook component claims notebook bytes")
    elif notebook_bytes is None or receipt.get("authority", {}).get("notebook_sha256") != sha256(notebook_bytes):
        raise RuntimeError("QuantEcon authority notebook hash differs")
    if receipt.get("target", {}).get("sha256") != sha256(target_bytes):
        raise RuntimeError("QuantEcon target hash differs")
    manifest_rows = {}
    for line in require_file(component_manifest).decode("utf-8").splitlines()[1:]:
        path, bytes_text, digest = line.split("\t")
        manifest_rows[path] = (int(bytes_text), digest)
    if manifest_rows.get(html_rel, (None, None))[1] != sha256(html_bytes):
        raise RuntimeError("QuantEcon component manifest does not bind HTML")

    resource_id = "resource.quantecon.continuous-time-mcs"
    edition_id = "edition.quantecon.8b06e0aa"
    rights_id = "rights.quantecon.cc-by-sa-4.0"
    source_manifest_sha = str(receipt["authority"]["source_manifest_sha256_after"])
    tree = str(receipt["authority"]["tree"])
    commit = str(receipt["authority"]["commit"])
    source_locator = "https://github.com/QuantEcon/continuous_time_mcs"
    entities: list[dict[str, Any]] = [
        record(
            "resource",
            resource_id,
            source_locator=source_locator,
            source_sha256=sha256(require_file(QUANTECON_ROOT / "evidence" / "continuous_time_mcs-8b06e0a.zip")),
            payload={"creator": "Thomas J. Sargent; John Stachurski", "component": "Continuous Time Markov Chains"},
        ),
        record(
            "edition",
            edition_id,
            parent_id=resource_id,
            resource_id=resource_id,
            source_locator=relative(component_manifest),
            source_sha256=source_manifest_sha,
            payload={"commit": commit, "tree": tree, "source_manifest_sha256": source_manifest_sha},
        ),
        record(
            "rights",
            rights_id,
            resource_id=resource_id,
            source_locator=relative(QUANTECON_LICENSE),
            source_sha256=sha256(require_file(QUANTECON_LICENSE)),
            payload={
                "license": "CC-BY-SA-4.0",
                "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
                "scope": "QuantEcon component bytes; Indonesian adaptations retain attribution and ShareAlike",
                "authors": ["Thomas J. Sargent", "John Stachurski"],
            },
        ),
    ]
    entities.extend(record("concept", key, payload={"label_en": value}) for key, value in concept_labels.items())
    unit_concept_ids = list(dict.fromkeys((*inherited_concept_ids, *concept_labels)))
    entities.append(
        record(
            "unit",
            unit_id,
            parent_id="course.o009.d30",
            order=unit_order,
            path=f"quantecon/lectures/{unit_slug}.html",
            resource_id=resource_id,
            edition_id=edition_id,
            source_local_id=f"lectures/{unit_slug}.md",
            source_locator=f"{source_locator}/blob/{commit}/lectures/{unit_slug}.md",
            source_sha256=sha256(source_bytes),
            target_sha256=sha256(target_bytes),
            locale="id-ID",
            translation_state="structurally_verified",
            relationship="translates",
            rights_id=rights_id,
            concept_ids=unit_concept_ids,
            payload={
                "unit_kind": "section",
                "component": "quantecon-ctmc",
                "source_language": "en",
                "body_extent": body_extent,
                "exercise_count": int(receipt["topology"]["exercises"]),
                "solution_count": int(receipt["topology"]["solutions"]),
                "code_cell_count": int(receipt["topology"]["code_cells"]),
                "runtime_status": (
                    "not-applicable-no-code-cells"
                    if int(receipt["topology"]["code_cells"]) == 0
                    else "two-pass-offline-replay"
                ),
            },
        )
    )

    site_inventory: dict[str, str] | None = None
    if component in {"kolmogorov_fwd", "generators", "uc_mc_semigroups", "ergodicity"}:
        site_inventory = validate_site_manifest_inventory()
    site_root = (ROOT / "build" / "site").resolve()
    site_html = site_root / "quantecon" / "lectures" / f"{unit_slug}.html"
    site_html_bytes = require_file(site_html)
    site_html_rel = site_html.relative_to(site_root).as_posix()
    if site_inventory is not None and site_inventory.get(site_html_rel) != sha256(
        site_html_bytes
    ):
        raise RuntimeError(
            f"aggregate QuantEcon {component} HTML is not bound by the live site manifest"
        )
    soup = BeautifulSoup(site_html_bytes.decode("utf-8"), "lxml")
    semantic: dict[int, str] = {}
    counters: defaultdict[str, int] = defaultdict(int)
    execution_figure_links: list[tuple[str, str]] = []
    semantic_nodes = []
    for node in soup.find_all(True):
        classes = set(node.get("class") or [])
        kind: str | None = None
        if node.name in {"h2", "h3", "h4"}:
            kind = "heading"
        elif "exercise" in classes:
            kind = "exercise"
        elif "solution" in classes:
            kind = "solution"
        elif "qe-theorem" in classes:
            kind = "theorem"
        elif "qe-corollary" in classes:
            kind = "corollary"
        elif "qe-lemma" in classes:
            kind = "lemma"
        elif "qe-proof" in classes:
            kind = "proof"
        elif "qe-algorithm" in classes:
            kind = "algorithm"
        elif "qe-example" in classes:
            kind = "example"
        elif "qe-note" in classes:
            kind = "note"
        elif node.name in {"div", "details"} and "code-cell" in classes:
            kind = "code"
        elif node.name == "figure" and {"execution-figure", "source-figure"}.intersection(classes):
            kind = "figure"
        if kind is None:
            continue
        counters[kind] += 1
        local_id = str(node.get("id") or f"{kind}-{counters[kind]:03d}")
        stable_id = f"{unit_id}.{local_id}"
        semantic[id(node)] = stable_id
        semantic_nodes.append((node, stable_id, kind, local_id))
        target_hash = sha256(str(node).encode("utf-8"))
        payload = {
            "unit_kind": kind,
            "component": "quantecon-ctmc",
            "body_extent": "complete-dom-node",
            "classes": sorted(classes),
        }
        if kind == "code":
            cell_index = node.find("code").get("data-cell-index") if node.find("code") else None
            payload.update({"execution_index": int(cell_index) if cell_index else counters[kind], "execution_status": "replayed-offline"})
        if kind == "figure":
            image = node.find("img")
            if image is not None and image.get("src"):
                asset_path = (site_html.parent / Path(str(image["src"]))).resolve()
                if not asset_path.is_relative_to(site_root) or not asset_path.is_file():
                    raise RuntimeError(
                        f"QuantEcon backend figure asset escapes or is missing: {image['src']}"
                    )
                rel_asset = asset_path.relative_to(site_root).as_posix()
                payload.update({"asset_path": f"build/site/{rel_asset}", "alt": str(image.get("alt") or "")})
            if "execution-figure" in classes:
                code_ancestor = node.parent
                while code_ancestor is not None:
                    if "code-cell" in set(code_ancestor.get("class") or []):
                        break
                    code_ancestor = code_ancestor.parent
                if code_ancestor is None or id(code_ancestor) not in semantic:
                    raise RuntimeError(
                        f"QuantEcon execution figure has no exported code-cell ancestor: {local_id}"
                    )
                execution_figure_links.append((semantic[id(code_ancestor)], stable_id))
        parent_id = unit_id
        ancestor = node.parent
        while ancestor is not None:
            if id(ancestor) in semantic:
                parent_id = semantic[id(ancestor)]
                break
            ancestor = ancestor.parent
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=parent_id,
                order=len(semantic_nodes),
                path=f"quantecon/lectures/{unit_slug}.html",
                resource_id=resource_id,
                edition_id=edition_id,
                source_local_id=local_id,
                source_locator=f"quantecon/lectures/{unit_slug}.html#{local_id}",
                target_sha256=target_hash,
                locale="id-ID",
                translation_state="built",
                relationship="documents",
                rights_id=rights_id,
                concept_ids=unit_concept_ids if kind in {"heading", "theorem", "corollary", "lemma", "proof", "example"} else [],
                payload=payload,
            )
        )

    segments: list[dict[str, Any]] = []
    segment_order = 0
    for node in soup.find_all(["p", "li", "summary", "figcaption"]):
        text = " ".join(node.stripped_strings)
        if not text:
            continue
        segment_order += 1
        parent_id = unit_id
        ancestor = node.parent
        while ancestor is not None:
            if id(ancestor) in semantic:
                parent_id = semantic[id(ancestor)]
                break
            ancestor = ancestor.parent
        segments.append(
            record(
                "segment",
                f"segment.o009.quantecon.{unit_slug}.{segment_order:04d}",
                parent_id=parent_id,
                order=segment_order,
                path=f"quantecon/lectures/{unit_slug}.html",
                resource_id=resource_id,
                edition_id=edition_id,
                source_locator=f"quantecon/lectures/{unit_slug}.html:segment-{segment_order}",
                target_sha256=sha256(text.encode("utf-8")),
                locale="id-ID",
                translation_state="built",
                relationship="documents",
                rights_id=rights_id,
                payload={"target_text": text, "tag": node.name, "component": "quantecon-ctmc"},
            )
        )

    relations: list[dict[str, str]] = [
        relation(
            f"rel.contains.course.o009.{unit_id}",
            "contains",
            "course.o009.d30",
            unit_id,
            f"source/index.md item {contains_item}; QuantEcon component boundary",
        ),
        relation(
            f"rel.precedes.{precedes_source}.{unit_id}",
            "precedes",
            precedes_source,
            unit_id,
            "reader source order; QuantEcon component boundary",
        ),
    ]
    for node, stable_id, kind, local_id in semantic_nodes:
        parent_id = unit_id
        ancestor = node.parent
        while ancestor is not None:
            if id(ancestor) in semantic:
                parent_id = semantic[id(ancestor)]
                break
            ancestor = ancestor.parent
        relations.append(
            relation(
                f"rel.contains.{parent_id}.{stable_id}",
                "contains",
                parent_id,
                stable_id,
                f"quantecon/lectures/{unit_slug}.html#{local_id}",
            )
        )
    exercise_pairs = {
        "memoryless": (
            ("memoryless-ex-1", "memoryless-solution-1"),
            ("memoryless-ex-2", "memoryless-solution-2"),
        ),
        "poisson": (
            ("poisson-ex-1", "poisson-solution-1"),
            ("poisson-ex-2", "poisson-solution-2"),
        ),
        "markov_prop": tuple(
            (f"markov-prop-{index}", f"markov_prop-solution-{index}")
            for index in range(1, 5)
        ),
        "kolmogorov_bwd": tuple(
            (f"kolmogorov-bwd-{index}", f"kolmogorov_bwd-solution-{index}")
            for index in range(1, 4)
        ),
        "kolmogorov_fwd": tuple(
            (f"kolmogorov-fwd-{index}", f"kolmogorov_fwd-solution-{index}")
            for index in range(1, 4)
        ),
        "generators": tuple(
            (f"generators-ex-{index}", f"generators-solution-{index}")
            for index in range(1, 4)
        ),
        "uc_mc_semigroups": tuple(
            (f"uc-mc-semigroups-ex-{index}", f"uc_mc_semigroups-solution-{index}")
            for index in range(1, 6)
        ),
        "ergodicity": tuple(
            (f"ergodicity-ex-{index}", f"ergodicity-solution-{index}")
            for index in range(1, 4)
        ),
    }[unit_slug]
    for index, (exercise, solution) in enumerate(exercise_pairs, start=1):
        relations.append(relation(f"rel.solves.quantecon.{unit_slug}.{index}", "solves", f"{unit_id}.{solution}", f"{unit_id}.{exercise}", f"{unit_slug}.html#{solution} solves #{exercise}"))
    for index, (code_id, figure_id) in enumerate(execution_figure_links, start=1):
        relations.append(
            relation(
                f"rel.executes.quantecon.{unit_slug}.figure-{index}",
                "executes",
                code_id,
                figure_id,
                f"{unit_slug}.html execution figure {index}; nearest code-cell ancestor; deterministic offline replay",
            )
        )
    relations.append(relation(f"rel.depends-on.quantecon.{unit_slug}.o006", "depends-on", unit_id, "resource.o006.c140.shared", "O006/C140 sampling and LLN/CLT surface is a shared prerequisite; no chapter-5 bytes duplicated"))
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


@dataclass(frozen=True)
class AuthoredMarkdownNode:
    stable_id: str
    start: int
    end: int
    content_start: int
    content_end: int
    dialect: str
    title: str
    classes: tuple[str, ...] = ()
    attributes: tuple[tuple[str, str], ...] = ()


def authored_artifact_id(path: Path) -> str:
    family = "mastery" if path.parent.name == "mastery" else "assessment"
    return f"artifact.input.authored-{family}-{path.stem}"


def normalized_yaml(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): normalized_yaml(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalized_yaml(item) for item in value]
    return str(value)


def authored_front_matter(text: str, path: Path) -> tuple[dict[str, Any], int]:
    if not text.startswith("---\n"):
        return {}, 0
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise RuntimeError(f"unterminated YAML front matter: {relative(path)}")
    loaded = safe_load(text[4:closing])
    if not isinstance(loaded, dict):
        raise RuntimeError(f"front matter must be a mapping: {relative(path)}")
    return normalized_yaml(loaded), closing + 5


def authored_markdown_nodes(text: str, path: Path) -> list[AuthoredMarkdownNode]:
    heading_re = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*(?:\r?\n|$)", re.MULTILINE)
    headings = list(heading_re.finditer(text))
    result: list[AuthoredMarkdownNode] = []

    explicit_heading_re = re.compile(
        r"^(#{1,6})[ \t]+(.+?)[ \t]+\{#([A-Za-z0-9_.:-]+)([^}]*)\}[ \t]*(?:\r?\n|$)",
        re.MULTILINE,
    )
    for match in explicit_heading_re.finditer(text):
        level = len(match.group(1))
        end = len(text)
        for following in headings:
            if following.start() > match.start() and len(following.group(1)) <= level:
                end = following.start()
                break
        tail = match.group(4)
        result.append(
            AuthoredMarkdownNode(
                match.group(3), match.start(), end, match.end(), end, "heading",
                match.group(2).strip(),
                tuple(re.findall(r"\.([A-Za-z0-9_.-]+)", tail)),
                tuple(re.findall(r'([A-Za-z][A-Za-z0-9_.:-]*)="([^"]*)"', tail)),
            )
        )

    raw_anchor_re = re.compile(
        r'^<a[ \t]+id="([A-Za-z0-9_.:-]+)"[ \t]*></a>[ \t]*(?:\r?\n)'
        r'(?:[ \t]*(?:\r?\n))*'
        r'^(#{1,6})[ \t]+(.+?)[ \t]*(?:\r?\n|$)',
        re.MULTILINE,
    )
    raw_anchor_matches = list(raw_anchor_re.finditer(text))
    anchor_start_by_heading = {
        match.start(2): match.start() for match in raw_anchor_matches
    }
    for match in raw_anchor_matches:
        level = len(match.group(2))
        end = len(text)
        for following in headings:
            if following.start() >= match.end() and len(following.group(1)) <= level:
                end = anchor_start_by_heading.get(following.start(), following.start())
                break
        result.append(
            AuthoredMarkdownNode(
                match.group(1), match.start(), end, match.end(), end, "raw-anchor",
                match.group(3).strip(),
            )
        )

    opening = re.compile(r"^:::\s+\{#([A-Za-z0-9_.:-]+)([^}]*)\}\s*(?:\r?\n|$)")
    closing = re.compile(r"^:::\s*(?:\r?\n|$)")
    stack: list[tuple[str, int, int, str]] = []
    for line in re.finditer(r"^.*(?:\r?\n|$)", text, re.MULTILINE):
        opened = opening.fullmatch(line.group(0))
        if opened:
            stack.append((opened.group(1), line.start(), line.end(), opened.group(2)))
        elif closing.fullmatch(line.group(0)):
            if not stack:
                raise RuntimeError(
                    f"unmatched fenced-div close: {relative(path)}:L{line_number(text, line.start())}"
                )
            stable_id, start, content_start, tail = stack.pop()
            content = text[content_start:line.start()]
            title_match = heading_re.search(content)
            result.append(
                AuthoredMarkdownNode(
                    stable_id, start, line.end(), content_start, line.start(), "fenced-div",
                    title_match.group(2).strip() if title_match else stable_id,
                    tuple(re.findall(r"\.([A-Za-z0-9_.-]+)", tail)),
                    tuple(re.findall(r'([A-Za-z][A-Za-z0-9_.:-]*)="([^"]*)"', tail)),
                )
            )
    if stack:
        raise RuntimeError(f"unclosed fenced divs in {relative(path)}: {[item[0] for item in stack]}")

    ids = [node.stable_id for node in result]
    if len(ids) != len(set(ids)):
        duplicates = sorted({stable_id for stable_id in ids if ids.count(stable_id) > 1})
        raise RuntimeError(f"duplicate authored Markdown ids in {relative(path)}: {duplicates}")
    result.sort(key=lambda node: (node.start, -node.end, node.stable_id))
    for index, left in enumerate(result):
        for right in result[index + 1:]:
            if right.start >= left.end:
                break
            if not (left.start <= right.start and right.end <= left.end):
                raise RuntimeError(
                    f"crossing authored Markdown spans in {relative(path)}: "
                    f"{left.stable_id}, {right.stable_id}"
                )
    return result


def authored_unit_kind(node: AuthoredMarkdownNode, assessment_root: str | None) -> str:
    stable_id = node.stable_id.lower()
    tokens = " ".join((stable_id, *node.classes, node.title.lower()))
    if stable_id.startswith("rights."):
        return "rights"
    if assessment_root == node.stable_id:
        return "assessment"
    if re.search(r"\.problem\.\d+$", stable_id):
        return "assessment-problem"
    if "rubric" in tokens or "rubrik" in tokens:
        return "rubric"
    if "hint" in tokens or "petunjuk" in tokens:
        return "hint"
    if "answer" in tokens or "jawaban" in tokens:
        return "answer"
    if "solution" in tokens or "solusi" in tokens or "penyelesaian" in tokens:
        return "solution"
    if "exercise" in tokens or "latihan" in tokens or "soal" in node.classes:
        return "exercise"
    if "prerequisite" in tokens or "prasyarat" in tokens:
        return "prerequisites"
    if "outcome" in tokens or "capaian" in tokens:
        return "outcomes"
    if "binding" in tokens or "ikatan" in tokens:
        return "bindings"
    if "rights" in tokens or "hak-provenans" in tokens:
        return "rights-provenance"
    if "section" in stable_id:
        return "section"
    if any(token in tokens for token in ("mastery", "masteri", "penguasaan", "masalah")):
        return "mastery"
    return "section"


def authored_parent_map(
    nodes: list[AuthoredMarkdownNode], document_parent: str | None
) -> dict[str, str]:
    parents: dict[str, str] = {}
    for node in nodes:
        candidates = [
            candidate
            for candidate in nodes
            if candidate.stable_id != node.stable_id
            and candidate.start <= node.start
            and node.end <= candidate.end
            and (candidate.start < node.start or node.end < candidate.end)
        ]
        if candidates:
            parent = min(candidates, key=lambda candidate: (candidate.end - candidate.start, candidate.stable_id))
            parents[node.stable_id] = parent.stable_id
        else:
            parents[node.stable_id] = document_parent or "course.o009.d30"
    return parents


def authored_relation(
    relation_type: str, source_id: str, target_id: str, evidence: str
) -> dict[str, str]:
    digest = sha256(f"{relation_type}\t{source_id}\t{target_id}\t{evidence}".encode("utf-8"))[:24]
    return relation(
        f"rel.authored.{relation_type}.{digest}", relation_type, source_id, target_id, evidence
    )


def authored_alias(alias: str, canonical_id: str, evidence: str) -> dict[str, str]:
    digest = sha256(f"{alias}\t{canonical_id}\t{evidence}".encode("utf-8"))[:24]
    return {
        "alias_id": f"alias.authored.{digest}",
        "namespace": "o009-source-id",
        "alias": alias,
        "canonical_id": canonical_id,
        "evidence": evidence,
        "status": "active",
    }


def authored_metadata_bindings(metadata: dict[str, Any]) -> dict[str, dict[str, list[str]]]:
    result: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: {"outcomes": [], "prerequisites": []}
    )

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            root_id = value.get("root_id") or value.get("mastery_id")
            if isinstance(root_id, str):
                for key, bucket in (("outcome_ids", "outcomes"), ("prerequisite_ids", "prerequisites")):
                    items = value.get(key, [])
                    if isinstance(items, str):
                        items = [items]
                    if isinstance(items, list):
                        result[root_id][bucket].extend(str(item) for item in items)
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(metadata)
    authoring = metadata.get("authoring", {})
    if isinstance(authoring, dict):
        roots: list[str] = []
        for key in ("mastery_id", "mastery_ids"):
            value = authoring.get(key)
            if isinstance(value, str):
                roots.append(value)
            elif isinstance(value, list):
                roots.extend(str(item) for item in value)
        for root_id in roots:
            for key, bucket in (("outcome_ids", "outcomes"), ("prerequisite_ids", "prerequisites")):
                values = authoring.get(key, [])
                if isinstance(values, str):
                    values = [values]
                if isinstance(values, list):
                    result[root_id][bucket].extend(str(item) for item in values)
    return result


def authored_derived_outcome_id(root_id: str) -> str:
    if root_id.startswith("unit."):
        return "outcome." + root_id[len("unit."):]
    match = re.fullmatch(r"o009-mastery-(.+)", root_id)
    if match:
        return "outcome.o009.mastery." + match.group(1).replace("-", ".")
    match = re.search(r"martingal-(\d+)(?:-root)?$", root_id)
    if match:
        return f"outcome.o009.mastery.martingales.{int(match.group(1)):02d}"
    return f"outcome.o009.authored.{sha256(root_id.encode('utf-8'))[:24]}"


def authored_markdown_bundle(
    existing_records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]], list[dict[str, str]]]:
    actual_mastery = tuple(sorted((ROOT / "source" / "mastery").glob("*.md"), key=lambda path: path.name))
    actual_assessments = tuple(sorted((ROOT / "source" / "assessments").glob("*.md"), key=lambda path: path.name))
    if actual_mastery != AUTHORED_MASTERY_INPUTS or actual_assessments != AUTHORED_ASSESSMENT_INPUTS:
        raise RuntimeError(
            "authored Markdown inventory differs from the admitted 14+2 closure: "
            f"mastery={[path.name for path in actual_mastery]} "
            f"assessments={[path.name for path in actual_assessments]}"
        )

    known = {item["id"] for item in existing_records}
    entities: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    relations: list[dict[str, str]] = []
    aliases: list[dict[str, str]] = []
    relation_keys: set[tuple[str, str, str]] = set()
    alias_keys: set[tuple[str, str]] = set()
    corpus_anchor_ids: set[str] = set()

    def add_relation_once(kind: str, source_id: str, target_id: str, evidence: str) -> None:
        key = (kind, source_id, target_id)
        if key not in relation_keys:
            relation_keys.add(key)
            relations.append(authored_relation(kind, source_id, target_id, evidence))

    def add_alias_once(alias_value: str, canonical_id: str, evidence: str) -> None:
        key = (alias_value, canonical_id)
        if alias_value != canonical_id and key not in alias_keys:
            alias_keys.add(key)
            aliases.append(authored_alias(alias_value, canonical_id, evidence))

    for file_index, path in enumerate(AUTHORED_MARKDOWN_INPUTS, start=1):
        data = require_file(path)
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data or not data.endswith(b"\n"):
            raise RuntimeError(f"authored Markdown must be UTF-8 without BOM, LF-only, with final LF: {relative(path)}")
        text = data.decode("utf-8")
        metadata, front_matter_end = authored_front_matter(text, path)
        rel_path = relative(path)
        if metadata and metadata.get("lang") != "id-ID":
            raise RuntimeError(f"authored Markdown locale must be id-ID: {rel_path}")
        if "CC BY 4.0" not in text and "CC-BY-4.0" not in text:
            raise RuntimeError(f"authored Markdown lacks a CC BY 4.0 declaration: {rel_path}")
        if "OpenAI Codex" not in text:
            raise RuntimeError(f"authored Markdown lacks model provenance: {rel_path}")

        nodes = authored_markdown_nodes(text, path)
        if not nodes:
            raise RuntimeError(f"authored Markdown has no explicit stable anchors: {rel_path}")
        duplicate_corpus = corpus_anchor_ids & {node.stable_id for node in nodes}
        if duplicate_corpus:
            raise RuntimeError(f"duplicate authored Markdown ids across files: {sorted(duplicate_corpus)}")
        corpus_anchor_ids.update(node.stable_id for node in nodes)

        section = metadata.get("assessment") or metadata.get("authoring") or {}
        if not isinstance(section, dict):
            raise RuntimeError(f"authored metadata section must be a mapping: {rel_path}")
        assessment_root = section.get("assessment_id") if path in AUTHORED_ASSESSMENT_INPUTS else None
        if assessment_root is not None and assessment_root not in {node.stable_id for node in nodes}:
            raise RuntimeError(f"assessment_id lacks a matching explicit anchor: {rel_path}#{assessment_root}")
        unit_id = section.get("unit_id")
        document_parent: str | None = None
        if (
            isinstance(unit_id, str)
            and unit_id.startswith("unit.")
            and unit_id not in {node.stable_id for node in nodes}
        ):
            document_parent = unit_id

        explicit_rights = sorted(set(re.findall(r"rights\.[A-Za-z0-9._:-]+", text)))
        explicit_rights = [item.rstrip(".:") for item in explicit_rights]
        fallback = AUTHORED_FALLBACK_RIGHTS.get(rel_path)
        if fallback:
            explicit_rights.append(fallback)
        rights_ids = sorted(set(explicit_rights))
        if not rights_ids:
            raise RuntimeError(f"authored Markdown has no stable rights binding: {rel_path}")

        file_hash = sha256(data)
        artifact_id = authored_artifact_id(path)
        anchor_by_id = {node.stable_id: node for node in nodes}
        for rights_id in rights_ids:
            if rights_id in anchor_by_id:
                continue
            if rights_id in known:
                continue
            first = text.find(rights_id)
            locator = f"{rel_path}:L{line_number(text, max(first, 0))}"
            entities.append(
                record(
                    "rights", rights_id, parent_id="course.o009.d30", path=rel_path,
                    source_local_id=rights_id, source_locator=locator,
                    source_sha256=file_hash, target_sha256=file_hash, locale="id-ID",
                    translation_state="authored", relationship="authored",
                    payload={
                        "ingestion": AUTHORED_MARKDOWN_INGESTION,
                        "license": "CC-BY-4.0",
                        "license_url": "https://creativecommons.org/licenses/by/4.0/",
                        "source_artifact_id": artifact_id,
                        "source_file_sha256": file_hash,
                        "provenance": metadata.get("provenance") or metadata.get("provenans") or section.get("provenance"),
                    },
                )
            )
            known.add(rights_id)

        def node_rights(node: AuthoredMarkdownNode) -> str:
            attributes = dict(node.attributes)
            if attributes.get("data-rights-id") in rights_ids:
                return attributes["data-rights-id"]
            # A terminal role ordinal (for example ``.hint.02``) identifies
            # the second hint, not the second mastery problem.  Remove that
            # suffix before matching a per-problem rights identifier.
            rights_subject_id = re.sub(
                r"(?i)(?:[.-](?:hint|answer|solution|exercise|latihan|jawaban|solusi)(?:[.-]\d+)?)$",
                "",
                node.stable_id,
            )
            numbers = re.findall(
                r"(?:^|[.-])(0[1-9]|[1-9][0-9]?)(?=$|[.-])",
                rights_subject_id,
            )
            for number in reversed(numbers):
                candidates = [item for item in rights_ids if re.search(rf"[.-]{re.escape(number)}(?:[.-]|$)", item)]
                if len(candidates) == 1:
                    return candidates[0]
            return rights_ids[0]

        if document_parent:
            if document_parent in known:
                raise RuntimeError(f"authored document unit collides with an existing id: {document_parent}")
            entities.append(
                record(
                    "unit", document_parent, parent_id="course.o009.d30", order=file_index,
                    path=rel_path, source_local_id=document_parent,
                    source_locator=f"{rel_path}:L1-L{line_number(text, len(text) - 1)}",
                    source_sha256=file_hash, target_sha256=file_hash, locale="id-ID",
                    translation_state="authored", relationship="authored", rights_id=rights_ids[0],
                    payload={
                        "ingestion": AUTHORED_MARKDOWN_INGESTION,
                        "unit_kind": "mastery-collection",
                        "body_extent": "complete-source-file",
                        "front_matter": metadata,
                        "source_artifact_id": artifact_id,
                        "source_file_sha256": file_hash,
                        "rights_ids": rights_ids,
                    },
                )
            )
            known.add(document_parent)
            add_relation_once("contains", "course.o009.d30", document_parent, rel_path)

        parents = authored_parent_map(nodes, document_parent)
        sibling_orders: dict[str, int] = defaultdict(int)
        previous_sibling: dict[str, str] = {}
        kinds = {node.stable_id: authored_unit_kind(node, assessment_root) for node in nodes}
        for node in nodes:
            stable_id = node.stable_id
            if stable_id in known:
                raise RuntimeError(f"authored anchor collides with an existing backend id: {stable_id}")
            parent_id = parents[stable_id]
            sibling_orders[parent_id] += 1
            span_text = text[node.start:node.end]
            kind = kinds[stable_id]
            record_type = "rights" if kind == "rights" else "unit"
            payload = {
                "ingestion": AUTHORED_MARKDOWN_INGESTION,
                "unit_kind": kind,
                "body_extent": "complete-authored-anchor",
                "anchor_dialect": node.dialect,
                "anchor_classes": list(node.classes),
                "anchor_attributes": dict(node.attributes),
                "title": node.title,
                "line_start": line_number(text, node.start),
                "line_end": line_number(text, max(node.end - 1, node.start)),
                "source_artifact_id": artifact_id,
                "source_file_sha256": file_hash,
                "rights_ids": rights_ids,
            }
            if record_type == "rights":
                payload.update(
                    {
                        "license": "CC-BY-4.0",
                        "license_url": "https://creativecommons.org/licenses/by/4.0/",
                        "provenance": metadata.get("provenance") or metadata.get("provenans") or section.get("provenance"),
                    }
                )
            if stable_id in {assessment_root, unit_id} or (not document_parent and parent_id == "course.o009.d30" and sibling_orders[parent_id] == 1):
                payload["front_matter"] = metadata
            entities.append(
                record(
                    record_type, stable_id, parent_id=parent_id,
                    order=sibling_orders[parent_id], path=rel_path,
                    source_local_id=stable_id, source_locator=f"{rel_path}#{stable_id}",
                    source_sha256=sha256(span_text.encode("utf-8")),
                    target_sha256=sha256(span_text.encode("utf-8")), locale="id-ID",
                    translation_state="authored", relationship="authored",
                    rights_id=None if record_type == "rights" else node_rights(node), payload=payload,
                )
            )
            known.add(stable_id)
            add_relation_once("contains", parent_id, stable_id, f"{rel_path}#{stable_id}")
            if parent_id in previous_sibling:
                add_relation_once("precedes", previous_sibling[parent_id], stable_id, f"source order in {rel_path}")
            previous_sibling[parent_id] = stable_id

            segment_id = f"segment.o009.authored.anchor.{sha256((rel_path + '#' + stable_id).encode('utf-8'))[:24]}"
            segments.append(
                record(
                    "segment", segment_id, parent_id=stable_id, order=1, path=rel_path,
                    source_local_id=stable_id, source_locator=f"{rel_path}#{stable_id}",
                    source_sha256=sha256(span_text.encode("utf-8")),
                    target_sha256=sha256(span_text.encode("utf-8")), locale="id-ID",
                    translation_state="authored", relationship="authored", rights_id=(None if record_type == "rights" else node_rights(node)),
                    payload={
                        "ingestion": AUTHORED_MARKDOWN_INGESTION,
                        "segment_kind": "authored-markdown-anchor",
                        "body_extent": "complete",
                        "source_text": span_text,
                        "source_artifact_id": artifact_id,
                    },
                )
            )

        top_roots = [node.stable_id for node in nodes if parents[node.stable_id] in {document_parent, "course.o009.d30"}]
        file_parent = document_parent or top_roots[0]
        file_segment_id = f"segment.o009.authored.file.{sha256(rel_path.encode('utf-8'))[:24]}"
        segments.append(
            record(
                "segment", file_segment_id, parent_id=file_parent, order=0, path=rel_path,
                source_local_id=None, source_locator=f"{rel_path}:L1-L{line_number(text, len(text) - 1)}",
                source_sha256=file_hash, target_sha256=file_hash, locale="id-ID",
                translation_state="authored", relationship="authored", rights_id=rights_ids[0],
                payload={
                    "ingestion": AUTHORED_MARKDOWN_INGESTION,
                    "segment_kind": "authored-markdown-source-file",
                    "body_extent": "complete-source-file",
                    "source_text": text,
                    "front_matter_extent": front_matter_end,
                    "source_artifact_id": artifact_id,
                },
            )
        )

        bindings = authored_metadata_bindings(metadata)
        exercise_nodes = [node for node in nodes if kinds[node.stable_id] == "exercise"]
        assessment_problems = [node for node in nodes if kinds[node.stable_id] == "assessment-problem"]
        if path in AUTHORED_MASTERY_INPUTS:
            expected = AUTHORED_MASTERY_ITEM_COUNTS[AUTHORED_MASTERY_INPUTS.index(path)]
            if len(exercise_nodes) != expected:
                raise RuntimeError(f"{rel_path}: expected {expected} mastery exercises, found {len(exercise_nodes)}")
        else:
            if len(assessment_problems) != 8:
                raise RuntimeError(f"{rel_path}: expected 8 cumulative-assessment problems, found {len(assessment_problems)}")

        assessment_outcomes: dict[int, list[str]] = defaultdict(list)
        for match in re.finditer(r"^\|\s*([1-8])\s*\|.*?\|(.+?)\|\s*$", text, re.MULTILINE):
            assessment_outcomes[int(match.group(1))].extend(
                item.rstrip(".:") for item in re.findall(r"outcome\.[A-Za-z0-9._:-]+", match.group(2))
            )

        targets = [(node, node) for node in assessment_problems]
        for exercise in exercise_nodes:
            parent_id = parents[exercise.stable_id]
            group = anchor_by_id.get(parent_id, exercise)
            targets.append((exercise, group))
        for exercise, group in targets:
            components = [node for node in nodes if group.start <= node.start and node.end <= group.end]
            hints = [node for node in components if kinds[node.stable_id] == "hint"]
            answers = [node for node in components if kinds[node.stable_id] == "answer"]
            solutions = [node for node in components if kinds[node.stable_id] == "solution"]
            if len(hints) < 2 or len(answers) != 1 or len(solutions) != 1:
                raise RuntimeError(
                    f"{rel_path}#{group.stable_id}: requires >=2 hints, one answer, and one solution; "
                    f"found {len(hints)}/{len(answers)}/{len(solutions)}"
                )
            for node in hints:
                add_relation_once("hints", node.stable_id, exercise.stable_id, f"{rel_path}#{node.stable_id}")
            add_relation_once("answers", answers[0].stable_id, exercise.stable_id, f"{rel_path}#{answers[0].stable_id}")
            add_relation_once("solves", solutions[0].stable_id, exercise.stable_id, f"{rel_path}#{solutions[0].stable_id}")

            group_text = text[group.start:group.end]
            outcome_ids = [item.rstrip(".:") for item in re.findall(r"outcome\.[A-Za-z0-9._:-]+", group_text)]
            outcome_ids.extend(bindings.get(group.stable_id, {}).get("outcomes", []))
            problem_match = re.search(r"\.problem\.(\d+)$", group.stable_id)
            if problem_match:
                outcome_ids.extend(assessment_outcomes[int(problem_match.group(1))])
            outcome_ids = sorted(set(outcome_ids))
            if not outcome_ids and path in AUTHORED_MASTERY_INPUTS:
                outcome_ids = [authored_derived_outcome_id(group.stable_id)]
            for outcome_id in outcome_ids:
                if outcome_id not in known:
                    label, level = AUTHORED_OUTCOME_SPECS.get(
                        outcome_id, (f"Membuktikan capaian penguasaan: {group.title}", "prove")
                    )
                    entities.append(
                        record(
                            "outcome", outcome_id, parent_id="course.o009.d30", path=rel_path,
                            source_local_id=outcome_id, source_locator=f"{rel_path}#{group.stable_id}",
                            source_sha256=sha256(group_text.encode("utf-8")),
                            target_sha256=sha256(group_text.encode("utf-8")), locale="id-ID",
                            translation_state="authored", relationship="authored", rights_id=node_rights(group),
                            payload={
                                "ingestion": AUTHORED_MARKDOWN_INGESTION,
                                "label": label,
                                "cognitive_level": level,
                                "derived_from_mastery_root": outcome_id not in AUTHORED_OUTCOME_SPECS,
                                "source_artifact_id": artifact_id,
                            },
                        )
                    )
                    known.add(outcome_id)
                add_relation_once("assesses", exercise.stable_id, outcome_id, f"{rel_path}#{group.stable_id}")

            reference_ids = [item.rstrip(".:") for item in re.findall(
                r"(?:prerequisite|theory)\.[A-Za-z0-9._:-]+|o009-theory-[A-Za-z0-9_.:-]+|unit\.o009\.original\.bridge\.regular-conditional-probability",
                group_text,
            )]
            reference_ids.extend(bindings.get(group.stable_id, {}).get("prerequisites", []))
            authoring = metadata.get("authoring", {})
            authored_roots: list[str] = []
            if isinstance(authoring, dict):
                for key in ("mastery_id", "mastery_ids"):
                    value = authoring.get(key)
                    if isinstance(value, str):
                        authored_roots.append(value)
                    elif isinstance(value, list):
                        authored_roots.extend(str(item) for item in value)
            if isinstance(authoring, dict) and group.stable_id in authored_roots:
                matched = authoring.get("matched_theory_id")
                if isinstance(matched, str):
                    reference_ids.append(matched)
            for source_reference in sorted(set(reference_ids)):
                target_id = AUTHORED_REFERENCE_TARGETS.get(source_reference)
                if target_id is None:
                    raise RuntimeError(f"unmapped authored prerequisite/theory id: {source_reference}")
                if target_id not in known:
                    raise RuntimeError(f"authored prerequisite target is absent: {source_reference} -> {target_id}")
                add_relation_once("depends-on", group.stable_id, target_id, f"{rel_path}: source id {source_reference}")
                add_alias_once(source_reference, target_id, f"{rel_path}: prerequisite/theory binding")

        authoring = metadata.get("authoring", {})
        if isinstance(authoring, dict):
            root_for_alias = document_parent or top_roots[0]
            for key in ("source_alias", "source_aliases"):
                values = authoring.get(key, [])
                if isinstance(values, str):
                    values = [values]
                if isinstance(values, list):
                    for value in values:
                        add_alias_once(str(value), root_for_alias, f"{rel_path}: front matter {key}")

    assessment_metadata: dict[str, str] = {}
    for path in AUTHORED_ASSESSMENT_INPUTS:
        text = require_file(path).decode("utf-8")
        metadata, _ = authored_front_matter(text, path)
        assessment = metadata.get("assessment", {})
        if not isinstance(assessment, dict):
            raise RuntimeError(f"assessment front matter is absent: {relative(path)}")
        root_id = assessment.get("assessment_id")
        alternate = assessment.get("alternate_of")
        if not isinstance(root_id, str) or not isinstance(alternate, str):
            raise RuntimeError(f"assessment alternate-form ids are absent: {relative(path)}")
        assessment_metadata[root_id] = alternate
    expected_alternates = {
        "assessment.o009.d30.cumulative.form-a": "assessment.o009.d30.cumulative.form-b",
        "assessment.o009.d30.cumulative.form-b": "assessment.o009.d30.cumulative.form-a",
    }
    if assessment_metadata != expected_alternates:
        raise RuntimeError(f"assessment alternate-form declarations differ: {assessment_metadata}")
    for source_id, target_id in sorted(assessment_metadata.items()):
        add_relation_once("alternate-form", source_id, target_id, "reciprocal assessment front-matter alternate_of")

    return entities, segments, relations, aliases


def validate_authored_markdown_contract(
    records: list[dict[str, Any]],
    relations: list[dict[str, str]],
    aliases: list[dict[str, str]],
    artifacts: dict[str, dict[str, str]],
) -> None:
    base_records = [
        item for item in records
        if item.get("payload", {}).get("ingestion") != AUTHORED_MARKDOWN_INGESTION
    ]
    expected_entities, expected_segments, expected_relations, expected_aliases = (
        authored_markdown_bundle(base_records)
    )
    expected_records = {item["id"]: item for item in expected_entities + expected_segments}
    actual_records = {
        item["id"]: item for item in records
        if item.get("payload", {}).get("ingestion") == AUTHORED_MARKDOWN_INGESTION
    }
    if actual_records != expected_records:
        raise RuntimeError(
            "generated authored Markdown record closure differs: "
            f"missing={sorted(set(expected_records) - set(actual_records))} "
            f"extra={sorted(set(actual_records) - set(expected_records))}"
        )
    actual_relations = {
        item["relation_id"]: item for item in relations
        if item["relation_id"].startswith("rel.authored.")
    }
    if actual_relations != {item["relation_id"]: item for item in expected_relations}:
        raise RuntimeError("generated authored Markdown relation closure differs")
    actual_aliases = {
        item["alias_id"]: item for item in aliases
        if item["alias_id"].startswith("alias.authored.")
    }
    if actual_aliases != {item["alias_id"]: item for item in expected_aliases}:
        raise RuntimeError("generated authored Markdown alias closure differs")
    expected_artifacts = {authored_artifact_id(path): path for path in AUTHORED_MARKDOWN_INPUTS}
    for artifact_id, path in expected_artifacts.items():
        data = require_file(path)
        if artifacts.get(artifact_id) != {
            "artifact_id": artifact_id,
            "artifact_kind": "input",
            "path": relative(path),
            "bytes": str(len(data)),
            "sha256": sha256(data),
            "media_type": "text/markdown",
            "status": "bound",
        }:
            raise RuntimeError(f"authored Markdown artifact binding differs: {artifact_id}")


def original_bridge_section_id(local_id: str) -> str:
    return f"{ORIGINAL_BRIDGE_UNIT_ID}.section.{local_id}"


def original_bridge_source_contract() -> tuple[bytes, str, dict[str, Span]]:
    data = require_file(ORIGINAL_BRIDGE_SOURCE)
    if (
        len(data) != ORIGINAL_BRIDGE_SOURCE_BYTES
        or sha256(data) != ORIGINAL_BRIDGE_SOURCE_SHA256
    ):
        raise RuntimeError(
            "original bridge 01 source differs from the admitted 34,418-byte freeze"
        )
    if b"\r" in data or not data.endswith(b"\n"):
        raise RuntimeError("original bridge 01 source must be UTF-8 LF with final LF")
    text = data.decode("utf-8")
    spans = fenced_div_spans(text)
    expected_ids = {
        ORIGINAL_BRIDGE_UNIT_ID,
        *(local_id for local_id, _, _ in ORIGINAL_BRIDGE_SECTION_SPECS),
        *ORIGINAL_BRIDGE_MASTERY_BASE_IDS,
        *(
            f"{base_id}.{suffix}"
            for base_id in ORIGINAL_BRIDGE_MASTERY_BASE_IDS
            for suffix in ORIGINAL_BRIDGE_MASTERY_SUFFIXES
        ),
    }
    if set(spans) != expected_ids or len(expected_ids) != 30:
        raise RuntimeError(
            "original bridge 01 explicit-ID closure differs: "
            f"missing={sorted(expected_ids - set(spans))} "
            f"extra={sorted(set(spans) - expected_ids)}"
        )
    if "original-bridge" not in spans[ORIGINAL_BRIDGE_UNIT_ID].classes:
        raise RuntimeError("original bridge root lacks its original-bridge class")
    for local_id, _, _ in ORIGINAL_BRIDGE_SECTION_SPECS:
        if "bridge-section" not in spans[local_id].classes:
            raise RuntimeError(f"original bridge section class differs: {local_id}")
    expected_child_classes = {
        "exercise": "exercise",
        "hint.01": "hint",
        "hint.02": "hint",
        "answer": "answer",
        "solution": "solution",
    }
    for base_id in ORIGINAL_BRIDGE_MASTERY_BASE_IDS:
        if "mastery-sequence" not in spans[base_id].classes:
            raise RuntimeError(f"mastery wrapper class differs: {base_id}")
        for suffix, expected_class in expected_child_classes.items():
            stable_id = f"{base_id}.{suffix}"
            if expected_class not in spans[stable_id].classes:
                raise RuntimeError(f"mastery child class differs: {stable_id}")
    return data, text, spans


def original_bridge_reader_contract() -> tuple[bytes, BeautifulSoup, dict[str, Any]]:
    data = require_file(ORIGINAL_BRIDGE_READER)
    soup = BeautifulSoup(data.decode("utf-8"), "lxml")
    expected_ids = {
        ORIGINAL_BRIDGE_UNIT_ID,
        *(local_id for local_id, _, _ in ORIGINAL_BRIDGE_SECTION_SPECS),
        *ORIGINAL_BRIDGE_MASTERY_BASE_IDS,
        *(
            f"{base_id}.{suffix}"
            for base_id in ORIGINAL_BRIDGE_MASTERY_BASE_IDS
            for suffix in ORIGINAL_BRIDGE_MASTERY_SUFFIXES
        ),
    }
    nodes: dict[str, Any] = {}
    for stable_id in sorted(expected_ids):
        matches = soup.find_all(id=stable_id)
        if len(matches) != 1:
            raise RuntimeError(
                f"original bridge reader ID must occur exactly once: {stable_id}"
            )
        node = matches[0]
        if not " ".join(node.stripped_strings):
            raise RuntimeError(f"original bridge reader node is empty: {stable_id}")
        nodes[stable_id] = node
    return data, soup, nodes


def original_bridge_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    source_data, source_text, source_spans = original_bridge_source_contract()
    reader_data, _, reader_nodes = original_bridge_reader_contract()

    def source_extent_sha(stable_id: str) -> str:
        span = source_spans[stable_id]
        return sha256(source_text[span.start : span.end].encode("utf-8"))

    def reader_node_sha(stable_id: str) -> str:
        return sha256(str(reader_nodes[stable_id]).encode("utf-8"))

    all_bridge_concepts = [
        "concept.stochastic.process.finite-dimensional-distributions",
        "concept.stochastic.process.kolmogorov-extension",
        *ORIGINAL_BRIDGE_NEW_CONCEPTS,
    ]
    entities: list[dict[str, Any]] = [
        *(
            record("concept", stable_id, payload={"label_en": label})
            for stable_id, label in ORIGINAL_BRIDGE_NEW_CONCEPTS.items()
        ),
        record(
            "rights",
            ORIGINAL_BRIDGE_RIGHTS_ID,
            source_local_id="hak-dan-provenans",
            source_locator=(
                "source/original/01-konstruksi-kolmogorov.md#hak-dan-provenans"
            ),
            source_sha256=source_extent_sha("hak-dan-provenans"),
            target_sha256=reader_node_sha("hak-dan-provenans"),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": (
                    "source/original/01-konstruksi-kolmogorov.md and its built "
                    "reader rendering only"
                ),
                "model_disclosure": "OpenAI Codex gpt-5.6-sol, Ultra.",
                "does_not_relicense_random_or_quantecon": True,
                "non_endorsement": True,
            },
        ),
        *(
            record(
                "outcome",
                stable_id,
                parent_id="course.o009.d30",
                locale="id-ID",
                translation_state="authored",
                rights_id=ORIGINAL_BRIDGE_RIGHTS_ID,
                concept_ids=concept_ids,
                payload={"label": label, "cognitive_level": level},
            )
            for stable_id, (label, level, concept_ids) in ORIGINAL_BRIDGE_OUTCOMES.items()
        ),
        record(
            "unit",
            ORIGINAL_BRIDGE_UNIT_ID,
            parent_id="course.o009.d30",
            order=36,
            path=ORIGINAL_BRIDGE_PATH,
            source_local_id=ORIGINAL_BRIDGE_UNIT_ID,
            source_locator=relative(ORIGINAL_BRIDGE_SOURCE),
            source_sha256=sha256(source_data),
            target_sha256=sha256(reader_data),
            locale="id-ID",
            translation_state="built",
            relationship="authored",
            rights_id=ORIGINAL_BRIDGE_RIGHTS_ID,
            concept_ids=all_bridge_concepts,
            payload={
                "title": "Konstruksi Kolmogorov dan proses kanonik",
                "unit_kind": "original-bridge",
                "body_extent": "complete-source-and-reader-page",
                "source_type": "original",
                "source_bytes": len(source_data),
                "reader_bytes": len(reader_data),
                "section_count": len(ORIGINAL_BRIDGE_SECTION_SPECS),
                "mastery_sequence_count": len(ORIGINAL_BRIDGE_MASTERY_BASE_IDS),
                "mastery_child_count": (
                    len(ORIGINAL_BRIDGE_MASTERY_BASE_IDS)
                    * len(ORIGINAL_BRIDGE_MASTERY_SUFFIXES)
                ),
                "model_disclosure": "OpenAI Codex gpt-5.6-sol, Ultra.",
                "excluded_from_random_page_count": True,
                "excluded_from_quantecon_chapter_count": True,
            },
        ),
    ]

    section_ids: dict[str, str] = {}
    for order, (local_id, title, concept_ids) in enumerate(
        ORIGINAL_BRIDGE_SECTION_SPECS, start=1
    ):
        stable_id = original_bridge_section_id(local_id)
        section_ids[local_id] = stable_id
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=ORIGINAL_BRIDGE_UNIT_ID,
                order=order,
                path=ORIGINAL_BRIDGE_PATH,
                source_local_id=local_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_SOURCE)}#{local_id}",
                source_sha256=source_extent_sha(local_id),
                target_sha256=reader_node_sha(local_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_RIGHTS_ID,
                concept_ids=list(concept_ids),
                payload={
                    "title": title,
                    "unit_kind": "section",
                    "body_extent": "complete-fenced-div",
                    "built_id": local_id,
                },
            )
        )

    mastery_concepts = {
        1: [
            "concept.measure.product-sigma-algebra",
            "concept.measure.cylinder-set",
            "concept.stochastic.process.projective-consistency",
            "concept.stochastic.process.canonical-process",
        ],
        2: [
            "concept.stochastic.process.projective-consistency",
            "concept.stochastic.process.canonical-process",
            "concept.markov.chapman-kolmogorov",
        ],
        3: [
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.projective-consistency",
            "concept.stochastic.process.canonical-process",
        ],
    }
    child_kinds = {
        "exercise": "exercise",
        "hint.01": "hint",
        "hint.02": "hint",
        "answer": "answer",
        "solution": "solution",
    }
    for mastery_order, base_id in enumerate(
        ORIGINAL_BRIDGE_MASTERY_BASE_IDS, start=1
    ):
        entities.append(
            record(
                "unit",
                base_id,
                parent_id=section_ids["latihan-penguasaan"],
                order=mastery_order,
                path=ORIGINAL_BRIDGE_PATH,
                source_local_id=base_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_SOURCE)}#{base_id}",
                source_sha256=source_extent_sha(base_id),
                target_sha256=reader_node_sha(base_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_RIGHTS_ID,
                concept_ids=mastery_concepts[mastery_order],
                payload={
                    "unit_kind": "mastery-sequence",
                    "body_extent": "complete-fenced-div",
                    "built_id": base_id,
                    "quota_category": (
                        "general-space-poisson-process-construction"
                    ),
                },
            )
        )
        for child_order, suffix in enumerate(
            ORIGINAL_BRIDGE_MASTERY_SUFFIXES, start=1
        ):
            stable_id = f"{base_id}.{suffix}"
            entities.append(
                record(
                    "unit",
                    stable_id,
                    parent_id=base_id,
                    order=child_order,
                    path=ORIGINAL_BRIDGE_PATH,
                    source_local_id=stable_id,
                    source_locator=(
                        f"{relative(ORIGINAL_BRIDGE_SOURCE)}#{stable_id}"
                    ),
                    source_sha256=source_extent_sha(stable_id),
                    target_sha256=reader_node_sha(stable_id),
                    locale="id-ID",
                    translation_state="built",
                    relationship="authored",
                    rights_id=ORIGINAL_BRIDGE_RIGHTS_ID,
                    concept_ids=mastery_concepts[mastery_order],
                    payload={
                        "unit_kind": child_kinds[suffix],
                        "body_extent": "complete-fenced-div",
                        "built_id": stable_id,
                        "mastery_sequence": mastery_order,
                    },
                )
            )

    relation_prefix = "rel.o009.original.bridge.kolmogorov"
    relations: list[dict[str, str]] = [
        relation(
            f"{relation_prefix}.contains.course",
            "contains",
            "course.o009.d30",
            ORIGINAL_BRIDGE_UNIT_ID,
            "complete original bridge source and reader page",
        ),
        relation(
            f"{relation_prefix}.precedes.random-overview",
            "precedes",
            "unit.o009.random.brown.index",
            ORIGINAL_BRIDGE_UNIT_ID,
            "curriculum order 35 to 36; all 27 selected Random pages remain separate",
        ),
        relation(
            f"{relation_prefix}.depends.random-probability-revisited",
            "depends-on",
            ORIGINAL_BRIDGE_UNIT_ID,
            "unit.o009.random.prob.probability-revisited",
            "source prerequisite link to Random product probability spaces",
        ),
        relation(
            f"{relation_prefix}.depends.random-processes",
            "depends-on",
            ORIGINAL_BRIDGE_UNIT_ID,
            "unit.o009.random.prob.processes",
            "source prerequisite link to finite-dimensional distributions",
        ),
        relation(
            f"{relation_prefix}.depends.quantecon-markov-property",
            "depends-on",
            ORIGINAL_BRIDGE_UNIT_ID,
            "unit.o009.quantecon.ctmc.markov-property",
            "source prerequisite link to transition kernels and Markov construction",
        ),
        *(
            relation(
                f"{relation_prefix}.teaches.{index:02d}",
                "teaches",
                ORIGINAL_BRIDGE_UNIT_ID,
                outcome_id,
                "two explicit reader outcomes in tujuan-dan-prasyarat",
            )
            for index, outcome_id in enumerate(ORIGINAL_BRIDGE_OUTCOMES, start=1)
        ),
        *(
            relation(
                f"{relation_prefix}.contains.section.{index:02d}",
                "contains",
                ORIGINAL_BRIDGE_UNIT_ID,
                section_ids[local_id],
                f"{ORIGINAL_BRIDGE_PATH}#{local_id}",
            )
            for index, (local_id, _, _) in enumerate(
                ORIGINAL_BRIDGE_SECTION_SPECS, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.precedes.section.{index:02d}.{index + 1:02d}",
                "precedes",
                section_ids[ORIGINAL_BRIDGE_SECTION_SPECS[index - 1][0]],
                section_ids[ORIGINAL_BRIDGE_SECTION_SPECS[index][0]],
                "original bridge source and reader DOM order",
            )
            for index in range(1, len(ORIGINAL_BRIDGE_SECTION_SPECS))
        ),
    ]
    for mastery_order, base_id in enumerate(
        ORIGINAL_BRIDGE_MASTERY_BASE_IDS, start=1
    ):
        relations.append(
            relation(
                f"{relation_prefix}.contains.mastery.{mastery_order:02d}",
                "contains",
                section_ids["latihan-penguasaan"],
                base_id,
                f"{ORIGINAL_BRIDGE_PATH}#{base_id}",
            )
        )
        if mastery_order > 1:
            relations.append(
                relation(
                    f"{relation_prefix}.precedes.mastery.{mastery_order - 1:02d}.{mastery_order:02d}",
                    "precedes",
                    ORIGINAL_BRIDGE_MASTERY_BASE_IDS[mastery_order - 2],
                    base_id,
                    "original bridge mastery sequence order",
                )
            )
        child_ids = [
            f"{base_id}.{suffix}" for suffix in ORIGINAL_BRIDGE_MASTERY_SUFFIXES
        ]
        for child_order, (suffix, child_id) in enumerate(
            zip(ORIGINAL_BRIDGE_MASTERY_SUFFIXES, child_ids), start=1
        ):
            relations.append(
                relation(
                    f"{relation_prefix}.contains.mastery.{mastery_order:02d}.{suffix.replace('.', '-')}",
                    "contains",
                    base_id,
                    child_id,
                    f"{ORIGINAL_BRIDGE_PATH}#{child_id}",
                )
            )
            if child_order > 1:
                previous = child_ids[child_order - 2]
                relations.append(
                    relation(
                        f"{relation_prefix}.precedes.mastery.{mastery_order:02d}.{child_order - 1:02d}.{child_order:02d}",
                        "precedes",
                        previous,
                        child_id,
                        "exercise, two hints, answer, and solution DOM order",
                    )
                )
        exercise_id, hint_01_id, hint_02_id, answer_id, solution_id = child_ids
        for hint_order, hint_id in enumerate((hint_01_id, hint_02_id), start=1):
            relations.append(
                relation(
                    f"{relation_prefix}.hints.mastery.{mastery_order:02d}.{hint_order:02d}",
                    "hints",
                    hint_id,
                    exercise_id,
                    "progressive hint bound to its complete exercise",
                )
            )
        relations.extend(
            [
                relation(
                    f"{relation_prefix}.answers.mastery.{mastery_order:02d}",
                    "answers",
                    answer_id,
                    exercise_id,
                    "concise answer bound to its complete exercise",
                ),
                relation(
                    f"{relation_prefix}.solves.mastery.{mastery_order:02d}",
                    "solves",
                    solution_id,
                    exercise_id,
                    "worked solution bound to its complete exercise",
                ),
            ]
        )
        assessed_outcomes = [
            "outcome.o009.construct-canonical-process-from-fdds"
        ]
        if mastery_order == 3:
            assessed_outcomes.append(
                "outcome.o009.audit-kolmogorov-extension-hypotheses"
            )
        for outcome_id in assessed_outcomes:
            outcome_suffix = "audit" if ".audit-" in outcome_id else "construct"
            relations.append(
                relation(
                    f"{relation_prefix}.assesses.mastery.{mastery_order:02d}.{outcome_suffix}",
                    "assesses",
                    exercise_id,
                    outcome_id,
                    "complete original mastery prompt and worked solution",
                )
            )

    allowed_relation_types = {
        "contains",
        "depends-on",
        "precedes",
        "prerequisite",
        "teaches",
        "assesses",
        "hints",
        "answers",
        "solves",
    }
    if any(item["relation_type"] not in allowed_relation_types for item in relations):
        raise RuntimeError("original bridge emitted a relation type outside its contract")

    corrections = [
        {
            "correction_id": (
                "correction.o009.original.bridge.kolmogorov.random-state-space-hypothesis"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.random.prob.processes",
            "target_id": section_ids["teorema-perluasan-kolmogorov"],
            "description": (
                "State standard Borel as an explicit sufficient state-space hypothesis; "
                "retain the Random donor bytes unchanged."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_PATH}#teorema-perluasan-kolmogorov"
            ),
            "status": "accepted",
        },
        {
            "correction_id": (
                "correction.o009.original.bridge.kolmogorov.random-existence-proof-scope"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.random.prob.processes",
            "target_id": section_ids["lingkup-bukti"],
            "description": (
                "Separate the finite-consistency argument from the countable-additivity "
                "existence theorem; retain the Random donor bytes unchanged."
            ),
            "evidence": f"{ORIGINAL_BRIDGE_PATH}#lingkup-bukti",
            "status": "accepted",
        },
        {
            "correction_id": (
                "correction.o009.original.bridge.kolmogorov.quantecon-raw-path-right-continuity"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.quantecon.ctmc.markov-property",
            "target_id": section_ids["audit-hipotesis-dan-bukan-klaim"],
            "description": (
                "Distinguish the canonical raw product-path law from concentration on a "
                "right-continuous path class; retain the QuantEcon donor bytes unchanged."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_PATH}#audit-hipotesis-dan-bukan-klaim"
            ),
            "status": "accepted",
        },
    ]
    return entities, [], relations, corrections


def original_bridge_mastery_ledger(*, admitted: bool) -> dict[str, Any]:
    source_data, _, _ = original_bridge_source_contract()
    reader_sha256 = None
    reader_bytes = None
    if admitted:
        reader_data, _, _ = original_bridge_reader_contract()
        reader_sha256 = sha256(reader_data)
        reader_bytes = len(reader_data)
    sequences = []
    for order, base_id in enumerate(ORIGINAL_BRIDGE_MASTERY_BASE_IDS, start=1):
        assesses = ["outcome.o009.construct-canonical-process-from-fdds"]
        if order == 3:
            assesses.append("outcome.o009.audit-kolmogorov-extension-hypotheses")
        sequences.append(
            {
                "id": base_id,
                "exercise_id": f"{base_id}.exercise",
                "hint_ids": [f"{base_id}.hint.01", f"{base_id}.hint.02"],
                "answer_id": f"{base_id}.answer",
                "solution_id": f"{base_id}.solution",
                "assesses": assesses,
                "rights_id": ORIGINAL_BRIDGE_RIGHTS_ID,
            }
        )
    return {
        "schema": "o009.original-bridge-01-mastery-ledger.v1",
        "generated": STAMP,
        "course_id": "course.o009.d30",
        "unit_id": ORIGINAL_BRIDGE_UNIT_ID,
        "status": "admitted" if admitted else "reader-build-pending",
        "source": {
            "path": relative(ORIGINAL_BRIDGE_SOURCE),
            "bytes": len(source_data),
            "sha256": sha256(source_data),
        },
        "built_reader": {
            "path": ORIGINAL_BRIDGE_PATH,
            "bytes": reader_bytes,
            "sha256": reader_sha256,
            "status": "bound" if admitted else "pending-no-hash-fabricated",
        },
        "rights_id": ORIGINAL_BRIDGE_RIGHTS_ID,
        "quota": {
            "category_id": "general-space-poisson-process-construction",
            "required": 4,
            "credited_before_bridge": 0,
            "bridge_increment_after_all_gates": 3,
            "credited_currently": 3 if admitted else 0,
            "credited_after_bridge_admission": 3,
            "remaining_after_bridge_admission": 1,
            "remaining_scope": "later general-space Poisson boundary",
        },
        "counts": {
            "mastery_sequences": 3,
            "exercise_records": 3,
            "hint_records": 6,
            "answer_records": 3,
            "solution_records": 3,
            "mastery_child_records": 15,
        },
        "validation": {
            "all_source_extents_complete": True,
            "all_reader_extents_complete": admitted,
            "all_relation_endpoints_validated": admitted,
            "all_rights_bindings_validated": admitted,
            "credit_admitted": admitted,
        },
        "sequences": sequences,
    }


def write_original_bridge_mastery_ledger() -> None:
    ORIGINAL_BRIDGE_MASTERY_LEDGER.write_text(
        json.dumps(
            original_bridge_mastery_ledger(admitted=True),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def original_bridge_02_section_id(local_id: str) -> str:
    return f"{ORIGINAL_BRIDGE_02_UNIT_ID}.section.{local_id}"


def original_bridge_02_source_contract() -> tuple[bytes, str, dict[str, Span]]:
    data = require_file(ORIGINAL_BRIDGE_02_SOURCE)
    if (
        len(data) != ORIGINAL_BRIDGE_02_SOURCE_BYTES
        or sha256(data) != ORIGINAL_BRIDGE_02_SOURCE_SHA256
    ):
        raise RuntimeError(
            "original bridge 02 source differs from the admitted "
            "29,971-byte freeze"
        )
    if b"\r" in data or not data.endswith(b"\n"):
        raise RuntimeError("original bridge 02 source must be UTF-8 LF with final LF")
    text = data.decode("utf-8")
    spans = fenced_div_spans(text)
    expected_ids = {
        ORIGINAL_BRIDGE_02_UNIT_ID,
        *(local_id for local_id, _, _ in ORIGINAL_BRIDGE_02_SECTION_SPECS),
        *ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS,
        *(
            f"{base_id}.{suffix}"
            for base_id in ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS
            for suffix in ORIGINAL_BRIDGE_02_MASTERY_SUFFIXES
        ),
    }
    if set(spans) != expected_ids or len(expected_ids) != 29:
        raise RuntimeError(
            "original bridge 02 explicit-ID closure differs: "
            f"missing={sorted(expected_ids - set(spans))} "
            f"extra={sorted(set(spans) - expected_ids)}"
        )
    if "original-bridge" not in spans[ORIGINAL_BRIDGE_02_UNIT_ID].classes:
        raise RuntimeError("original bridge 02 root lacks its original-bridge class")
    for local_id, _, _ in ORIGINAL_BRIDGE_02_SECTION_SPECS:
        if "bridge-section" not in spans[local_id].classes:
            raise RuntimeError(
                f"original bridge 02 section class differs: {local_id}"
            )
    expected_child_classes = {
        "exercise": "exercise",
        "hint.01": "hint",
        "hint.02": "hint",
        "answer": "answer",
        "solution": "solution",
    }
    for base_id in ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS:
        if "mastery-sequence" not in spans[base_id].classes:
            raise RuntimeError(f"bridge 02 mastery wrapper class differs: {base_id}")
        for suffix, expected_class in expected_child_classes.items():
            stable_id = f"{base_id}.{suffix}"
            if expected_class not in spans[stable_id].classes:
                raise RuntimeError(
                    f"bridge 02 mastery child class differs: {stable_id}"
                )
    return data, text, spans


def original_bridge_02_reader_contract() -> tuple[
    bytes, BeautifulSoup, dict[str, Any]
]:
    data = require_file(ORIGINAL_BRIDGE_02_READER)
    soup = BeautifulSoup(data.decode("utf-8"), "lxml")
    expected_ids = {
        ORIGINAL_BRIDGE_02_UNIT_ID,
        *(local_id for local_id, _, _ in ORIGINAL_BRIDGE_02_SECTION_SPECS),
        *ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS,
        *(
            f"{base_id}.{suffix}"
            for base_id in ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS
            for suffix in ORIGINAL_BRIDGE_02_MASTERY_SUFFIXES
        ),
    }
    nodes: dict[str, Any] = {}
    for stable_id in sorted(expected_ids):
        matches = soup.find_all(id=stable_id)
        if len(matches) != 1:
            raise RuntimeError(
                "original bridge 02 reader ID must occur exactly once: "
                f"{stable_id}"
            )
        node = matches[0]
        if not " ".join(node.stripped_strings):
            raise RuntimeError(
                f"original bridge 02 reader node is empty: {stable_id}"
            )
        nodes[stable_id] = node
    duplicate_ids = sorted(
        stable_id
        for stable_id in {
            str(node.get("id"))
            for node in soup.find_all(id=True)
            if node.get("id")
        }
        if len(soup.find_all(id=stable_id)) != 1
    )
    if duplicate_ids:
        raise RuntimeError(
            f"original bridge 02 reader contains duplicate IDs: {duplicate_ids}"
        )
    return data, soup, nodes


def original_bridge_02_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    source_data, source_text, source_spans = original_bridge_02_source_contract()
    reader_data, _, reader_nodes = original_bridge_02_reader_contract()

    def source_extent_sha(stable_id: str) -> str:
        span = source_spans[stable_id]
        return sha256(source_text[span.start : span.end].encode("utf-8"))

    def reader_node_sha(stable_id: str) -> str:
        return sha256(str(reader_nodes[stable_id]).encode("utf-8"))

    all_bridge_concepts = [
        "concept.measure.product-sigma-algebra",
        "concept.stochastic.process.finite-dimensional-distributions",
        "concept.stochastic.process.path-space",
        "concept.stochastic.process.canonical-process",
        *ORIGINAL_BRIDGE_02_NEW_CONCEPTS,
    ]
    entities: list[dict[str, Any]] = [
        *(
            record("concept", stable_id, payload={"label_en": label})
            for stable_id, label in ORIGINAL_BRIDGE_02_NEW_CONCEPTS.items()
        ),
        record(
            "rights",
            ORIGINAL_BRIDGE_02_RIGHTS_ID,
            source_local_id="hak-dan-provenans-keterukuran",
            source_locator=(
                "source/original/02-keterukuran-proses-dan-hukum-lintasan.md"
                "#hak-dan-provenans-keterukuran"
            ),
            source_sha256=source_extent_sha("hak-dan-provenans-keterukuran"),
            target_sha256=reader_node_sha("hak-dan-provenans-keterukuran"),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": (
                    "source/original/02-keterukuran-proses-dan-hukum-lintasan.md "
                    "and its built reader rendering only"
                ),
                "model_disclosure": "OpenAI Codex gpt-5.6-sol, Ultra.",
                "does_not_relicense_random_quantecon_or_bridge_01": True,
                "non_endorsement": True,
            },
        ),
        *(
            record(
                "outcome",
                stable_id,
                parent_id="course.o009.d30",
                locale="id-ID",
                translation_state="authored",
                rights_id=ORIGINAL_BRIDGE_02_RIGHTS_ID,
                concept_ids=concept_ids,
                payload={"label": label, "cognitive_level": level},
            )
            for stable_id, (label, level, concept_ids) in ORIGINAL_BRIDGE_02_OUTCOMES.items()
        ),
        record(
            "unit",
            ORIGINAL_BRIDGE_02_UNIT_ID,
            parent_id="course.o009.d30",
            order=37,
            path=ORIGINAL_BRIDGE_02_PATH,
            source_local_id=ORIGINAL_BRIDGE_02_UNIT_ID,
            source_locator=relative(ORIGINAL_BRIDGE_02_SOURCE),
            source_sha256=sha256(source_data),
            target_sha256=sha256(reader_data),
            locale="id-ID",
            translation_state="built",
            relationship="authored",
            rights_id=ORIGINAL_BRIDGE_02_RIGHTS_ID,
            concept_ids=all_bridge_concepts,
            payload={
                "title": "Keterukuran proses dan hukum lintasan",
                "unit_kind": "original-bridge",
                "body_extent": "complete-source-and-reader-page",
                "source_type": "original",
                "source_bytes": len(source_data),
                "reader_bytes": len(reader_data),
                "section_count": len(ORIGINAL_BRIDGE_02_SECTION_SPECS),
                "mastery_sequence_count": len(ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS),
                "mastery_child_count": (
                    len(ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS)
                    * len(ORIGINAL_BRIDGE_02_MASTERY_SUFFIXES)
                ),
                "model_disclosure": "OpenAI Codex gpt-5.6-sol, Ultra.",
                "excluded_from_random_page_count": True,
                "excluded_from_quantecon_chapter_count": True,
                "executable_lab_count": 0,
            },
        ),
    ]

    section_ids: dict[str, str] = {}
    for order, (local_id, title, concept_ids) in enumerate(
        ORIGINAL_BRIDGE_02_SECTION_SPECS, start=1
    ):
        stable_id = original_bridge_02_section_id(local_id)
        section_ids[local_id] = stable_id
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=ORIGINAL_BRIDGE_02_UNIT_ID,
                order=order,
                path=ORIGINAL_BRIDGE_02_PATH,
                source_local_id=local_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_02_SOURCE)}#{local_id}",
                source_sha256=source_extent_sha(local_id),
                target_sha256=reader_node_sha(local_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_02_RIGHTS_ID,
                concept_ids=list(concept_ids),
                payload={
                    "title": title,
                    "unit_kind": "section",
                    "body_extent": "complete-fenced-div",
                    "built_id": local_id,
                },
            )
        )

    mastery_concepts = {
        1: [
            "concept.stochastic.process.coordinatewise-measurability",
            "concept.stochastic.process.joint-measurability",
            "concept.stochastic.process.countable-coordinate-dependence",
            "concept.stochastic.process.canonical-process",
        ],
        2: [
            "concept.stochastic.process.joint-measurability",
            "concept.stochastic.process.raw-path-law",
            "concept.stochastic.process.modification",
            "concept.stochastic.process.indistinguishability",
        ],
        3: [
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.regular-path-space-law",
            "concept.stochastic.process.modification",
            "concept.stochastic.process.indistinguishability",
        ],
    }
    child_kinds = {
        "exercise": "exercise",
        "hint.01": "hint",
        "hint.02": "hint",
        "answer": "answer",
        "solution": "solution",
    }
    for mastery_order, base_id in enumerate(
        ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS, start=1
    ):
        entities.append(
            record(
                "unit",
                base_id,
                parent_id=section_ids["latihan-penguasaan-keterukuran"],
                order=mastery_order,
                path=ORIGINAL_BRIDGE_02_PATH,
                source_local_id=base_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_02_SOURCE)}#{base_id}",
                source_sha256=source_extent_sha(base_id),
                target_sha256=reader_node_sha(base_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_02_RIGHTS_ID,
                concept_ids=mastery_concepts[mastery_order],
                payload={
                    "unit_kind": "mastery-sequence",
                    "body_extent": "complete-fenced-div",
                    "built_id": base_id,
                    "quota_category": (
                        "integrative-counterexample-literature-reading"
                    ),
                },
            )
        )
        for child_order, suffix in enumerate(
            ORIGINAL_BRIDGE_02_MASTERY_SUFFIXES, start=1
        ):
            stable_id = f"{base_id}.{suffix}"
            entities.append(
                record(
                    "unit",
                    stable_id,
                    parent_id=base_id,
                    order=child_order,
                    path=ORIGINAL_BRIDGE_02_PATH,
                    source_local_id=stable_id,
                    source_locator=(
                        f"{relative(ORIGINAL_BRIDGE_02_SOURCE)}#{stable_id}"
                    ),
                    source_sha256=source_extent_sha(stable_id),
                    target_sha256=reader_node_sha(stable_id),
                    locale="id-ID",
                    translation_state="built",
                    relationship="authored",
                    rights_id=ORIGINAL_BRIDGE_02_RIGHTS_ID,
                    concept_ids=mastery_concepts[mastery_order],
                    payload={
                        "unit_kind": child_kinds[suffix],
                        "body_extent": "complete-fenced-div",
                        "built_id": stable_id,
                        "mastery_sequence": mastery_order,
                    },
                )
            )

    relation_prefix = "rel.o009.original.bridge.process-measurability-path-law"
    relations: list[dict[str, str]] = [
        relation(
            f"{relation_prefix}.contains.course",
            "contains",
            "course.o009.d30",
            ORIGINAL_BRIDGE_02_UNIT_ID,
            "complete original bridge 02 source and reader page",
        ),
        relation(
            f"{relation_prefix}.precedes.bridge-01",
            "precedes",
            ORIGINAL_BRIDGE_UNIT_ID,
            ORIGINAL_BRIDGE_02_UNIT_ID,
            "curriculum order 36 to 37; bridge 02 follows the admitted Kolmogorov bridge",
        ),
        relation(
            f"{relation_prefix}.depends.bridge-01",
            "depends-on",
            ORIGINAL_BRIDGE_02_UNIT_ID,
            ORIGINAL_BRIDGE_UNIT_ID,
            "source prerequisite link to raw product path-space construction",
        ),
        relation(
            f"{relation_prefix}.depends.random-probability-revisited",
            "depends-on",
            ORIGINAL_BRIDGE_02_UNIT_ID,
            "unit.o009.random.prob.probability-revisited",
            "source prerequisite link to product probability spaces",
        ),
        relation(
            f"{relation_prefix}.depends.random-processes",
            "depends-on",
            ORIGINAL_BRIDGE_02_UNIT_ID,
            "unit.o009.random.prob.processes",
            "source prerequisite link to processes and finite-dimensional distributions",
        ),
        *(
            relation(
                f"{relation_prefix}.teaches.{index:02d}",
                "teaches",
                ORIGINAL_BRIDGE_02_UNIT_ID,
                outcome_id,
                "three explicit reader outcomes in tujuan-dan-empat-lapis-objek",
            )
            for index, outcome_id in enumerate(
                ORIGINAL_BRIDGE_02_OUTCOMES, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.contains.section.{index:02d}",
                "contains",
                ORIGINAL_BRIDGE_02_UNIT_ID,
                section_ids[local_id],
                f"{ORIGINAL_BRIDGE_02_PATH}#{local_id}",
            )
            for index, (local_id, _, _) in enumerate(
                ORIGINAL_BRIDGE_02_SECTION_SPECS, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.precedes.section.{index:02d}.{index + 1:02d}",
                "precedes",
                section_ids[ORIGINAL_BRIDGE_02_SECTION_SPECS[index - 1][0]],
                section_ids[ORIGINAL_BRIDGE_02_SECTION_SPECS[index][0]],
                "original bridge 02 source and reader DOM order",
            )
            for index in range(1, len(ORIGINAL_BRIDGE_02_SECTION_SPECS))
        ),
    ]
    mastery_outcomes = {
        1: ["outcome.o009.distinguish-process-measurability-levels"],
        2: [
            "outcome.o009.audit-fdd-versus-regular-path-law",
            "outcome.o009.distinguish-modification-and-indistinguishability",
        ],
        3: [
            "outcome.o009.audit-fdd-versus-regular-path-law",
            "outcome.o009.distinguish-modification-and-indistinguishability",
        ],
    }
    for mastery_order, base_id in enumerate(
        ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS, start=1
    ):
        relations.append(
            relation(
                f"{relation_prefix}.contains.mastery.{mastery_order:02d}",
                "contains",
                section_ids["latihan-penguasaan-keterukuran"],
                base_id,
                f"{ORIGINAL_BRIDGE_02_PATH}#{base_id}",
            )
        )
        if mastery_order > 1:
            relations.append(
                relation(
                    f"{relation_prefix}.precedes.mastery.{mastery_order - 1:02d}.{mastery_order:02d}",
                    "precedes",
                    ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS[mastery_order - 2],
                    base_id,
                    "original bridge 02 mastery sequence order",
                )
            )
        child_ids = [
            f"{base_id}.{suffix}" for suffix in ORIGINAL_BRIDGE_02_MASTERY_SUFFIXES
        ]
        for child_order, (suffix, child_id) in enumerate(
            zip(ORIGINAL_BRIDGE_02_MASTERY_SUFFIXES, child_ids), start=1
        ):
            relations.append(
                relation(
                    f"{relation_prefix}.contains.mastery.{mastery_order:02d}.{suffix.replace('.', '-')}",
                    "contains",
                    base_id,
                    child_id,
                    f"{ORIGINAL_BRIDGE_02_PATH}#{child_id}",
                )
            )
            if child_order > 1:
                relations.append(
                    relation(
                        f"{relation_prefix}.precedes.mastery.{mastery_order:02d}.{child_order - 1:02d}.{child_order:02d}",
                        "precedes",
                        child_ids[child_order - 2],
                        child_id,
                        "exercise, two hints, answer, and solution DOM order",
                    )
                )
        exercise_id, hint_01_id, hint_02_id, answer_id, solution_id = child_ids
        for hint_order, hint_id in enumerate((hint_01_id, hint_02_id), start=1):
            relations.append(
                relation(
                    f"{relation_prefix}.hints.mastery.{mastery_order:02d}.{hint_order:02d}",
                    "hints",
                    hint_id,
                    exercise_id,
                    "progressive hint bound to its complete exercise",
                )
            )
        relations.extend(
            [
                relation(
                    f"{relation_prefix}.answers.mastery.{mastery_order:02d}",
                    "answers",
                    answer_id,
                    exercise_id,
                    "concise answer bound to its complete exercise",
                ),
                relation(
                    f"{relation_prefix}.solves.mastery.{mastery_order:02d}",
                    "solves",
                    solution_id,
                    exercise_id,
                    "worked solution bound to its complete exercise",
                ),
            ]
        )
        for outcome_order, outcome_id in enumerate(
            mastery_outcomes[mastery_order], start=1
        ):
            relations.append(
                relation(
                    f"{relation_prefix}.assesses.mastery.{mastery_order:02d}.{outcome_order:02d}",
                    "assesses",
                    exercise_id,
                    outcome_id,
                    "complete original mastery prompt and worked solution",
                )
            )

    allowed_relation_types = {
        "contains",
        "depends-on",
        "precedes",
        "teaches",
        "assesses",
        "hints",
        "answers",
        "solves",
    }
    if any(item["relation_type"] not in allowed_relation_types for item in relations):
        raise RuntimeError(
            "original bridge 02 emitted a relation type outside its contract"
        )

    corrections = [
        {
            "correction_id": (
                "correction.o009.original.bridge.process-measurability-path-law."
                "coordinatewise-versus-joint"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.random.prob.processes",
            "target_id": section_ids["keterukuran-bersama"],
            "description": (
                "Separate coordinatewise process measurability from joint "
                "time-sample measurability; retain the Random donor bytes unchanged."
            ),
            "evidence": f"{ORIGINAL_BRIDGE_02_PATH}#keterukuran-bersama",
            "status": "accepted",
        },
        {
            "correction_id": (
                "correction.o009.original.bridge.process-measurability-path-law."
                "raw-versus-regular-path-law"
            ),
            "change_kind": "original-addition",
            "source_id": ORIGINAL_BRIDGE_UNIT_ID,
            "target_id": section_ids["sifat-lintasan-di-ruang-mentah"],
            "description": (
                "Separate the law on the raw product sigma-algebra from a Borel "
                "law on a regular path space; retain bridge 01 unchanged."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_02_PATH}#sifat-lintasan-di-ruang-mentah"
            ),
            "status": "accepted",
        },
        {
            "correction_id": (
                "correction.o009.original.bridge.process-measurability-path-law."
                "modification-versus-indistinguishability"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.random.prob.processes",
            "target_id": section_ids["modifikasi-dan-ketakterbedaan"],
            "description": (
                "Distinguish equality of finite-dimensional laws, modification, "
                "and indistinguishability without changing donor bytes."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_02_PATH}#modifikasi-dan-ketakterbedaan"
            ),
            "status": "accepted",
        },
    ]
    return entities, [], relations, corrections


def original_bridge_02_mastery_ledger(*, admitted: bool) -> dict[str, Any]:
    source_data, _, _ = original_bridge_02_source_contract()
    reader_sha256 = None
    reader_bytes = None
    if admitted:
        reader_data, _, _ = original_bridge_02_reader_contract()
        reader_sha256 = sha256(reader_data)
        reader_bytes = len(reader_data)
    mastery_outcomes = {
        1: ["outcome.o009.distinguish-process-measurability-levels"],
        2: [
            "outcome.o009.audit-fdd-versus-regular-path-law",
            "outcome.o009.distinguish-modification-and-indistinguishability",
        ],
        3: [
            "outcome.o009.audit-fdd-versus-regular-path-law",
            "outcome.o009.distinguish-modification-and-indistinguishability",
        ],
    }
    sequences = []
    for order, base_id in enumerate(ORIGINAL_BRIDGE_02_MASTERY_BASE_IDS, start=1):
        sequences.append(
            {
                "id": base_id,
                "exercise_id": f"{base_id}.exercise",
                "hint_ids": [f"{base_id}.hint.01", f"{base_id}.hint.02"],
                "answer_id": f"{base_id}.answer",
                "solution_id": f"{base_id}.solution",
                "assesses": mastery_outcomes[order],
                "rights_id": ORIGINAL_BRIDGE_02_RIGHTS_ID,
            }
        )
    return {
        "schema": "o009.original-bridge-02-mastery-ledger.v1",
        "generated": STAMP,
        "course_id": "course.o009.d30",
        "unit_id": ORIGINAL_BRIDGE_02_UNIT_ID,
        "status": "admitted" if admitted else "reader-build-pending",
        "source": {
            "path": relative(ORIGINAL_BRIDGE_02_SOURCE),
            "bytes": len(source_data),
            "sha256": sha256(source_data),
        },
        "built_reader": {
            "path": ORIGINAL_BRIDGE_02_PATH,
            "bytes": reader_bytes,
            "sha256": reader_sha256,
            "status": "bound" if admitted else "pending-no-hash-fabricated",
        },
        "rights_id": ORIGINAL_BRIDGE_02_RIGHTS_ID,
        "quota": {
            "category_id": "integrative-counterexample-literature-reading",
            "required": 6,
            "credited_before_bridge": 0,
            "bridge_increment_after_all_gates": 3,
            "credited_currently": 3 if admitted else 0,
            "credited_after_bridge_admission": 3,
            "remaining_after_bridge_admission": 3,
            "remaining_scope": (
                "three later integrative counterexample or literature-reading items"
            ),
            "does_not_consume_general_space_poisson_slot": True,
        },
        "counts": {
            "mastery_sequences": 3,
            "exercise_records": 3,
            "hint_records": 6,
            "answer_records": 3,
            "solution_records": 3,
            "mastery_child_records": 15,
        },
        "validation": {
            "all_source_extents_complete": True,
            "all_reader_extents_complete": admitted,
            "all_relation_endpoints_validated": admitted,
            "all_rights_bindings_validated": admitted,
            "credit_admitted": admitted,
        },
        "sequences": sequences,
    }


def write_original_bridge_02_mastery_ledger() -> None:
    reader_data, _, _ = original_bridge_02_reader_contract()
    site_inventory = validate_site_manifest_inventory()
    if site_inventory.get(ORIGINAL_BRIDGE_02_PATH) != sha256(reader_data):
        raise RuntimeError(
            "site manifest does not bind original bridge 02; mastery remains unadmitted"
        )
    ORIGINAL_BRIDGE_02_MASTERY_LEDGER.write_text(
        json.dumps(
            original_bridge_02_mastery_ledger(admitted=True),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def original_bridge_03_section_id(local_id: str) -> str:
    return f"{ORIGINAL_BRIDGE_03_UNIT_ID}.section.{local_id}"


def original_bridge_03_segment_id(local_id: str) -> str:
    return (
        "segment.o009.original.bridge.regular-conditional-probability."
        f"section.{local_id}"
    )


def original_bridge_03_source_contract() -> tuple[bytes, str, dict[str, Span]]:
    data = require_file(ORIGINAL_BRIDGE_03_SOURCE)
    if (
        len(data) != ORIGINAL_BRIDGE_03_SOURCE_BYTES
        or sha256(data) != ORIGINAL_BRIDGE_03_SOURCE_SHA256
    ):
        raise RuntimeError(
            "original bridge 03 source differs from the admitted "
            "34,016-byte freeze"
        )
    if b"\r" in data or not data.endswith(b"\n"):
        raise RuntimeError("original bridge 03 source must be UTF-8 LF with final LF")
    text = data.decode("utf-8")
    spans = fenced_div_spans(text)
    expected_ids = {
        ORIGINAL_BRIDGE_03_UNIT_ID,
        *(local_id for local_id, _, _ in ORIGINAL_BRIDGE_03_SECTION_SPECS),
        *ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS,
        *(
            f"{base_id}.{suffix}"
            for base_id in ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS
            for suffix in ORIGINAL_BRIDGE_03_MASTERY_SUFFIXES
        ),
    }
    if set(spans) != expected_ids or len(expected_ids) != 30:
        raise RuntimeError(
            "original bridge 03 explicit-ID closure differs: "
            f"missing={sorted(expected_ids - set(spans))} "
            f"extra={sorted(set(spans) - expected_ids)}"
        )
    if "original-bridge" not in spans[ORIGINAL_BRIDGE_03_UNIT_ID].classes:
        raise RuntimeError("original bridge 03 root lacks its original-bridge class")
    for local_id, _, _ in ORIGINAL_BRIDGE_03_SECTION_SPECS:
        if "bridge-section" not in spans[local_id].classes:
            raise RuntimeError(
                f"original bridge 03 section class differs: {local_id}"
            )
    expected_child_classes = {
        "exercise": "exercise",
        "hint.01": "hint",
        "hint.02": "hint",
        "answer": "answer",
        "solution": "solution",
    }
    for base_id in ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS:
        if "mastery-sequence" not in spans[base_id].classes:
            raise RuntimeError(f"bridge 03 mastery wrapper class differs: {base_id}")
        for suffix, expected_class in expected_child_classes.items():
            stable_id = f"{base_id}.{suffix}"
            if expected_class not in spans[stable_id].classes:
                raise RuntimeError(
                    f"bridge 03 mastery child class differs: {stable_id}"
                )
    return data, text, spans


def original_bridge_03_reader_contract() -> tuple[
    bytes, BeautifulSoup, dict[str, Any]
]:
    data = require_file(ORIGINAL_BRIDGE_03_READER)
    soup = BeautifulSoup(data.decode("utf-8"), "lxml")
    expected_ids = {
        ORIGINAL_BRIDGE_03_UNIT_ID,
        *(local_id for local_id, _, _ in ORIGINAL_BRIDGE_03_SECTION_SPECS),
        *ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS,
        *(
            f"{base_id}.{suffix}"
            for base_id in ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS
            for suffix in ORIGINAL_BRIDGE_03_MASTERY_SUFFIXES
        ),
    }
    nodes: dict[str, Any] = {}
    for stable_id in sorted(expected_ids):
        matches = soup.find_all(id=stable_id)
        if len(matches) != 1:
            raise RuntimeError(
                "original bridge 03 reader ID must occur exactly once: "
                f"{stable_id}"
            )
        node = matches[0]
        if not " ".join(node.stripped_strings):
            raise RuntimeError(
                f"original bridge 03 reader node is empty: {stable_id}"
            )
        nodes[stable_id] = node
    duplicate_ids = sorted(
        stable_id
        for stable_id in {
            str(node.get("id"))
            for node in soup.find_all(id=True)
            if node.get("id")
        }
        if len(soup.find_all(id=stable_id)) != 1
    )
    if duplicate_ids:
        raise RuntimeError(
            f"original bridge 03 reader contains duplicate IDs: {duplicate_ids}"
        )
    return data, soup, nodes


def original_bridge_03_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    source_data, source_text, source_spans = original_bridge_03_source_contract()
    reader_data, _, reader_nodes = original_bridge_03_reader_contract()

    def source_extent(stable_id: str) -> str:
        span = source_spans[stable_id]
        return source_text[span.start : span.end]

    def source_extent_sha(stable_id: str) -> str:
        return sha256(source_extent(stable_id).encode("utf-8"))

    def reader_node_sha(stable_id: str) -> str:
        return sha256(str(reader_nodes[stable_id]).encode("utf-8"))

    all_bridge_concepts = [
        "concept.measurable-space.standard-borel",
        "concept.conditional.expectation",
        "concept.conditional.probability",
        "concept.kernel.probability",
        "concept.kernel.density",
        "concept.conditional.regular-distribution",
        *ORIGINAL_BRIDGE_03_NEW_CONCEPTS,
    ]
    entities: list[dict[str, Any]] = [
        *(
            record("concept", stable_id, payload={"label_en": label})
            for stable_id, label in ORIGINAL_BRIDGE_03_NEW_CONCEPTS.items()
        ),
        record(
            "rights",
            ORIGINAL_BRIDGE_03_RIGHTS_ID,
            source_local_id="hak-dan-provenans-probabilitas-bersyarat",
            source_locator=(
                "source/original/03-probabilitas-bersyarat-reguler.md"
                "#hak-dan-provenans-probabilitas-bersyarat"
            ),
            source_sha256=source_extent_sha(
                "hak-dan-provenans-probabilitas-bersyarat"
            ),
            target_sha256=reader_node_sha(
                "hak-dan-provenans-probabilitas-bersyarat"
            ),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": (
                    "source/original/03-probabilitas-bersyarat-reguler.md "
                    "and its built reader rendering only"
                ),
                "model_disclosure": "OpenAI Codex gpt-5.6-sol, Ultra.",
                "does_not_relicense_random_quantecon_or_prior_bridges": True,
                "non_endorsement": True,
            },
        ),
        *(
            record(
                "outcome",
                stable_id,
                parent_id="course.o009.d30",
                locale="id-ID",
                translation_state="authored",
                rights_id=ORIGINAL_BRIDGE_03_RIGHTS_ID,
                concept_ids=concept_ids,
                payload={"label": label, "cognitive_level": level},
            )
            for stable_id, (label, level, concept_ids) in ORIGINAL_BRIDGE_03_OUTCOMES.items()
        ),
        record(
            "unit",
            ORIGINAL_BRIDGE_03_UNIT_ID,
            parent_id="course.o009.d30",
            order=38,
            path=ORIGINAL_BRIDGE_03_PATH,
            source_local_id=ORIGINAL_BRIDGE_03_UNIT_ID,
            source_locator=relative(ORIGINAL_BRIDGE_03_SOURCE),
            source_sha256=sha256(source_data),
            target_sha256=sha256(reader_data),
            locale="id-ID",
            translation_state="built",
            relationship="authored",
            rights_id=ORIGINAL_BRIDGE_03_RIGHTS_ID,
            concept_ids=all_bridge_concepts,
            payload={
                "title": "Distribusi bersyarat reguler dan disiplin versi",
                "unit_kind": "original-bridge",
                "body_extent": "complete-source-and-reader-page",
                "source_type": "original",
                "source_bytes": len(source_data),
                "reader_bytes": len(reader_data),
                "section_count": len(ORIGINAL_BRIDGE_03_SECTION_SPECS),
                "section_segment_count": len(ORIGINAL_BRIDGE_03_SECTION_SPECS),
                "mastery_sequence_count": len(ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS),
                "mastery_child_count": (
                    len(ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS)
                    * len(ORIGINAL_BRIDGE_03_MASTERY_SUFFIXES)
                ),
                "model_disclosure": "OpenAI Codex gpt-5.6-sol, Ultra.",
                "excluded_from_random_page_count": True,
                "excluded_from_quantecon_chapter_count": True,
                "executable_lab_count": 0,
            },
        ),
    ]

    section_ids: dict[str, str] = {}
    segments: list[dict[str, Any]] = []
    for order, (local_id, title, concept_ids) in enumerate(
        ORIGINAL_BRIDGE_03_SECTION_SPECS, start=1
    ):
        stable_id = original_bridge_03_section_id(local_id)
        section_ids[local_id] = stable_id
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=ORIGINAL_BRIDGE_03_UNIT_ID,
                order=order,
                path=ORIGINAL_BRIDGE_03_PATH,
                source_local_id=local_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_03_SOURCE)}#{local_id}",
                source_sha256=source_extent_sha(local_id),
                target_sha256=reader_node_sha(local_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_03_RIGHTS_ID,
                concept_ids=list(concept_ids),
                payload={
                    "title": title,
                    "unit_kind": "section",
                    "body_extent": "complete-fenced-div",
                    "built_id": local_id,
                },
            )
        )
        segments.append(
            record(
                "segment",
                original_bridge_03_segment_id(local_id),
                parent_id=stable_id,
                order=1,
                path=ORIGINAL_BRIDGE_03_PATH,
                source_local_id=local_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_03_SOURCE)}#{local_id}",
                source_sha256=source_extent_sha(local_id),
                target_sha256=reader_node_sha(local_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_03_RIGHTS_ID,
                concept_ids=list(concept_ids),
                payload={
                    "source_markdown": source_extent(local_id),
                    "reader_text": " ".join(reader_nodes[local_id].stripped_strings),
                    "source_extent": "complete-fenced-div",
                    "reader_extent": "complete-id-node",
                    "tag": str(reader_nodes[local_id].name),
                },
            )
        )

    mastery_concepts = {
        1: [
            "concept.conditional.probability",
            "concept.kernel.probability",
            "concept.conditional.version",
            "concept.conditional.null-conditioning-value",
        ],
        2: [
            "concept.kernel.density",
            "concept.conditional.regular-distribution",
            "concept.conditional.disintegration",
            "concept.conditional.null-conditioning-value",
        ],
        3: [
            "concept.conditional.regular-distribution",
            "concept.conditional.version",
            "concept.conditional.determining-class",
            "concept.conditional.null-conditioning-value",
        ],
    }
    child_kinds = {
        "exercise": "exercise",
        "hint.01": "hint",
        "hint.02": "hint",
        "answer": "answer",
        "solution": "solution",
    }
    mastery_parent = section_ids[
        "latihan-penguasaan-probabilitas-bersyarat-reguler"
    ]
    for mastery_order, base_id in enumerate(
        ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS, start=1
    ):
        entities.append(
            record(
                "unit",
                base_id,
                parent_id=mastery_parent,
                order=mastery_order,
                path=ORIGINAL_BRIDGE_03_PATH,
                source_local_id=base_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_03_SOURCE)}#{base_id}",
                source_sha256=source_extent_sha(base_id),
                target_sha256=reader_node_sha(base_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_03_RIGHTS_ID,
                concept_ids=mastery_concepts[mastery_order],
                payload={
                    "unit_kind": "mastery-sequence",
                    "body_extent": "complete-fenced-div",
                    "built_id": base_id,
                    "quota_category": "regular-conditional-probability",
                },
            )
        )
        for child_order, suffix in enumerate(
            ORIGINAL_BRIDGE_03_MASTERY_SUFFIXES, start=1
        ):
            stable_id = f"{base_id}.{suffix}"
            entities.append(
                record(
                    "unit",
                    stable_id,
                    parent_id=base_id,
                    order=child_order,
                    path=ORIGINAL_BRIDGE_03_PATH,
                    source_local_id=stable_id,
                    source_locator=(
                        f"{relative(ORIGINAL_BRIDGE_03_SOURCE)}#{stable_id}"
                    ),
                    source_sha256=source_extent_sha(stable_id),
                    target_sha256=reader_node_sha(stable_id),
                    locale="id-ID",
                    translation_state="built",
                    relationship="authored",
                    rights_id=ORIGINAL_BRIDGE_03_RIGHTS_ID,
                    concept_ids=mastery_concepts[mastery_order],
                    payload={
                        "unit_kind": child_kinds[suffix],
                        "body_extent": "complete-fenced-div",
                        "built_id": stable_id,
                        "mastery_sequence": mastery_order,
                    },
                )
            )

    relation_prefix = "rel.o009.original.bridge.regular-conditional-probability"
    relations: list[dict[str, str]] = [
        relation(
            f"{relation_prefix}.contains.course",
            "contains",
            "course.o009.d30",
            ORIGINAL_BRIDGE_03_UNIT_ID,
            "complete original bridge 03 source and reader page",
        ),
        relation(
            f"{relation_prefix}.precedes.bridge-02",
            "precedes",
            ORIGINAL_BRIDGE_02_UNIT_ID,
            ORIGINAL_BRIDGE_03_UNIT_ID,
            "curriculum order 37 to 38; bridge 03 follows the admitted path-law bridge",
        ),
        relation(
            f"{relation_prefix}.depends.bridge-01",
            "depends-on",
            ORIGINAL_BRIDGE_03_UNIT_ID,
            ORIGINAL_BRIDGE_UNIT_ID,
            "standard-Borel and canonical-space vocabulary from bridge 01",
        ),
        relation(
            f"{relation_prefix}.depends.bridge-02",
            "depends-on",
            ORIGINAL_BRIDGE_03_UNIT_ID,
            ORIGINAL_BRIDGE_02_UNIT_ID,
            "measurable path-map and regular path-law distinctions from bridge 02",
        ),
        relation(
            f"{relation_prefix}.depends.random-conditional2",
            "depends-on",
            ORIGINAL_BRIDGE_03_UNIT_ID,
            "unit.o009.random.expect.conditional2",
            "source prerequisite link to measure-theoretic conditional expectation",
        ),
        relation(
            f"{relation_prefix}.depends.random-kernels",
            "depends-on",
            ORIGINAL_BRIDGE_03_UNIT_ID,
            "unit.o009.random.expect.kernels",
            "source prerequisite link to probability-kernel calculus",
        ),
        *(
            relation(
                f"{relation_prefix}.teaches.outcome.{index:02d}",
                "teaches",
                ORIGINAL_BRIDGE_03_UNIT_ID,
                outcome_id,
                "three explicit reader outcomes in tujuan-dan-kesenjangan-versi",
            )
            for index, outcome_id in enumerate(
                ORIGINAL_BRIDGE_03_OUTCOMES, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.contains.section.{index:02d}",
                "contains",
                ORIGINAL_BRIDGE_03_UNIT_ID,
                section_ids[local_id],
                f"{ORIGINAL_BRIDGE_03_PATH}#{local_id}",
            )
            for index, (local_id, _, _) in enumerate(
                ORIGINAL_BRIDGE_03_SECTION_SPECS, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.contains.section-segment.{index:02d}",
                "contains",
                section_ids[local_id],
                original_bridge_03_segment_id(local_id),
                f"complete source/reader extent at {ORIGINAL_BRIDGE_03_PATH}#{local_id}",
            )
            for index, (local_id, _, _) in enumerate(
                ORIGINAL_BRIDGE_03_SECTION_SPECS, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.precedes.section.{index:02d}.{index + 1:02d}",
                "precedes",
                section_ids[ORIGINAL_BRIDGE_03_SECTION_SPECS[index - 1][0]],
                section_ids[ORIGINAL_BRIDGE_03_SECTION_SPECS[index][0]],
                "original bridge 03 source and reader DOM order",
            )
            for index in range(1, len(ORIGINAL_BRIDGE_03_SECTION_SPECS))
        ),
    ]
    mastery_outcomes = {
        1: ["outcome.o009.audit-conditional-version-uniqueness"],
        2: ["outcome.o009.derive-disintegration-and-null-value-versions"],
        3: [
            "outcome.o009.construct-regular-conditional-distribution",
            "outcome.o009.audit-conditional-version-uniqueness",
        ],
    }
    for mastery_order, base_id in enumerate(
        ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS, start=1
    ):
        relations.append(
            relation(
                f"{relation_prefix}.contains.mastery.{mastery_order:02d}",
                "contains",
                mastery_parent,
                base_id,
                f"{ORIGINAL_BRIDGE_03_PATH}#{base_id}",
            )
        )
        if mastery_order > 1:
            relations.append(
                relation(
                    f"{relation_prefix}.precedes.mastery.{mastery_order - 1:02d}.{mastery_order:02d}",
                    "precedes",
                    ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS[mastery_order - 2],
                    base_id,
                    "original bridge 03 mastery sequence order",
                )
            )
        child_ids = [
            f"{base_id}.{suffix}" for suffix in ORIGINAL_BRIDGE_03_MASTERY_SUFFIXES
        ]
        for child_order, (suffix, child_id) in enumerate(
            zip(ORIGINAL_BRIDGE_03_MASTERY_SUFFIXES, child_ids), start=1
        ):
            relations.append(
                relation(
                    f"{relation_prefix}.contains.mastery.{mastery_order:02d}.{suffix.replace('.', '-')}",
                    "contains",
                    base_id,
                    child_id,
                    f"{ORIGINAL_BRIDGE_03_PATH}#{child_id}",
                )
            )
            if child_order > 1:
                relations.append(
                    relation(
                        f"{relation_prefix}.precedes.mastery.{mastery_order:02d}.{child_order - 1:02d}.{child_order:02d}",
                        "precedes",
                        child_ids[child_order - 2],
                        child_id,
                        "exercise, two hints, answer, and solution DOM order",
                    )
                )
        exercise_id, hint_01_id, hint_02_id, answer_id, solution_id = child_ids
        for hint_order, hint_id in enumerate((hint_01_id, hint_02_id), start=1):
            relations.append(
                relation(
                    f"{relation_prefix}.hints.mastery.{mastery_order:02d}.{hint_order:02d}",
                    "hints",
                    hint_id,
                    exercise_id,
                    "progressive hint bound to its complete exercise",
                )
            )
        relations.extend(
            [
                relation(
                    f"{relation_prefix}.answers.mastery.{mastery_order:02d}",
                    "answers",
                    answer_id,
                    exercise_id,
                    "concise answer bound to its complete exercise",
                ),
                relation(
                    f"{relation_prefix}.solves.mastery.{mastery_order:02d}",
                    "solves",
                    solution_id,
                    exercise_id,
                    "worked solution bound to its complete exercise",
                ),
            ]
        )
        for outcome_order, outcome_id in enumerate(
            mastery_outcomes[mastery_order], start=1
        ):
            relations.append(
                relation(
                    f"{relation_prefix}.assesses.mastery.{mastery_order:02d}.{outcome_order:02d}",
                    "assesses",
                    exercise_id,
                    outcome_id,
                    "complete original mastery prompt and worked solution",
                )
            )

    allowed_relation_types = {
        "contains",
        "depends-on",
        "precedes",
        "teaches",
        "assesses",
        "hints",
        "answers",
        "solves",
    }
    if any(item["relation_type"] not in allowed_relation_types for item in relations):
        raise RuntimeError(
            "original bridge 03 emitted a relation type outside its contract"
        )

    corrections = [
        {
            "correction_id": (
                "correction.o009.original.bridge.regular-conditional-probability."
                "conditional2-version-coherence"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.random.expect.conditional2",
            "target_id": section_ids["dari-nilai-harapan-ke-kernel"],
            "description": (
                "Clarify that eventwise almost-sure versions need not jointly form "
                "a probability kernel; retain the Conditional2 donor bytes unchanged."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_03_PATH}#dari-nilai-harapan-ke-kernel"
            ),
            "status": "accepted",
        },
        {
            "correction_id": (
                "correction.o009.original.bridge.regular-conditional-probability."
                "kernels-standard-borel-existence"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.random.expect.kernels",
            "target_id": section_ids["keberadaan-pada-sasaran-borel-standar"],
            "description": (
                "State the exact standard-Borel target hypothesis, simultaneous "
                "version construction, and almost-everywhere uniqueness level; "
                "retain the Kernels donor bytes unchanged."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_03_PATH}#keberadaan-pada-sasaran-borel-standar"
            ),
            "status": "accepted",
        },
    ]
    return entities, segments, relations, corrections


def original_bridge_03_mastery_ledger(*, admitted: bool) -> dict[str, Any]:
    source_data, _, _ = original_bridge_03_source_contract()
    reader_sha256 = None
    reader_bytes = None
    if admitted:
        reader_data, _, _ = original_bridge_03_reader_contract()
        reader_sha256 = sha256(reader_data)
        reader_bytes = len(reader_data)
    mastery_outcomes = {
        1: ["outcome.o009.audit-conditional-version-uniqueness"],
        2: ["outcome.o009.derive-disintegration-and-null-value-versions"],
        3: [
            "outcome.o009.construct-regular-conditional-distribution",
            "outcome.o009.audit-conditional-version-uniqueness",
        ],
    }
    sequences = []
    for order, base_id in enumerate(ORIGINAL_BRIDGE_03_MASTERY_BASE_IDS, start=1):
        sequences.append(
            {
                "id": base_id,
                "exercise_id": f"{base_id}.exercise",
                "hint_ids": [f"{base_id}.hint.01", f"{base_id}.hint.02"],
                "answer_id": f"{base_id}.answer",
                "solution_id": f"{base_id}.solution",
                "assesses": mastery_outcomes[order],
                "rights_id": ORIGINAL_BRIDGE_03_RIGHTS_ID,
            }
        )
    return {
        "schema": "o009.original-bridge-03-mastery-ledger.v1",
        "generated": STAMP,
        "course_id": "course.o009.d30",
        "unit_id": ORIGINAL_BRIDGE_03_UNIT_ID,
        "status": "admitted" if admitted else "reader-build-pending",
        "source": {
            "path": relative(ORIGINAL_BRIDGE_03_SOURCE),
            "bytes": len(source_data),
            "sha256": sha256(source_data),
        },
        "built_reader": {
            "path": ORIGINAL_BRIDGE_03_PATH,
            "bytes": reader_bytes,
            "sha256": reader_sha256,
            "status": "bound" if admitted else "pending-no-hash-fabricated",
        },
        "rights_id": ORIGINAL_BRIDGE_03_RIGHTS_ID,
        "quota": {
            "category_id": "regular-conditional-probability",
            "required": 3,
            "credited_before_bridge": 0,
            "bridge_increment_after_all_gates": 3,
            "credited_currently": 3 if admitted else 0,
            "credited_after_bridge_admission": 3,
            "remaining_after_bridge_admission": 0,
            "course_original_mastery_credited_before_bridge": 6,
            "course_original_mastery_credited_after_bridge_admission": (
                9 if admitted else 6
            ),
            "course_original_mastery_remaining_after_bridge_admission": (
                27 if admitted else 30
            ),
            "does_not_recredit_prior_bridges": True,
        },
        "counts": {
            "mastery_sequences": 3,
            "exercise_records": 3,
            "hint_records": 6,
            "answer_records": 3,
            "solution_records": 3,
            "mastery_child_records": 15,
        },
        "validation": {
            "all_source_extents_complete": True,
            "all_reader_extents_complete": admitted,
            "all_relation_endpoints_validated": admitted,
            "all_rights_bindings_validated": admitted,
            "credit_admitted": admitted,
        },
        "sequences": sequences,
    }


def write_original_bridge_03_mastery_ledger() -> None:
    reader_data, _, _ = original_bridge_03_reader_contract()
    site_inventory = validate_site_manifest_inventory()
    if site_inventory.get(ORIGINAL_BRIDGE_03_PATH) != sha256(reader_data):
        raise RuntimeError(
            "site manifest does not bind original bridge 03; mastery remains unadmitted"
        )
    ORIGINAL_BRIDGE_03_MASTERY_LEDGER.write_text(
        json.dumps(
            original_bridge_03_mastery_ledger(admitted=True),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def validate_original_bridge_03_contract(
    records: list[dict[str, Any]],
    relations: list[dict[str, str]],
    corrections: list[dict[str, str]],
    artifacts: dict[str, dict[str, str]],
) -> None:
    expected_entities, expected_segments, expected_relations, expected_corrections = (
        original_bridge_03_entities()
    )
    by_id = entities_by_id(records)
    expected_by_id = entities_by_id(expected_entities + expected_segments)
    for stable_id, expected in expected_by_id.items():
        if by_id.get(stable_id) != expected:
            raise RuntimeError(
                "original bridge 03 backend record differs from exact contract: "
                f"{stable_id}"
            )
    segment_prefix = (
        "segment.o009.original.bridge.regular-conditional-probability.section."
    )
    bridge_record_ids = {
        stable_id
        for stable_id in by_id
        if stable_id == ORIGINAL_BRIDGE_03_UNIT_ID
        or stable_id == ORIGINAL_BRIDGE_03_RIGHTS_ID
        or stable_id in ORIGINAL_BRIDGE_03_NEW_CONCEPTS
        or stable_id in ORIGINAL_BRIDGE_03_OUTCOMES
        or stable_id.startswith(f"{ORIGINAL_BRIDGE_03_UNIT_ID}.section.")
        or stable_id.startswith(
            "unit.o009.original.mastery.regular-conditional-probability."
        )
        or stable_id.startswith(segment_prefix)
    }
    if bridge_record_ids != set(expected_by_id):
        raise RuntimeError(
            "original bridge 03 stable-ID closure differs: "
            f"missing={sorted(set(expected_by_id) - bridge_record_ids)} "
            f"extra={sorted(bridge_record_ids - set(expected_by_id))}"
        )
    expected_segment_ids = {
        original_bridge_03_segment_id(local_id)
        for local_id, _, _ in ORIGINAL_BRIDGE_03_SECTION_SPECS
    }
    actual_segment_ids = {
        item["id"]
        for item in records
        if item["record_type"] == "segment" and item["id"].startswith(segment_prefix)
    }
    if actual_segment_ids != expected_segment_ids or len(actual_segment_ids) != 11:
        raise RuntimeError("original bridge 03 section-segment closure differs")
    relation_prefix = "rel.o009.original.bridge.regular-conditional-probability."
    expected_relation_map = {
        item["relation_id"]: item for item in expected_relations
    }
    actual_relation_map = {
        item["relation_id"]: item
        for item in relations
        if item["relation_id"].startswith(relation_prefix)
    }
    if actual_relation_map != expected_relation_map:
        raise RuntimeError(
            "original bridge 03 relation closure differs from exact contract"
        )
    correction_prefix = (
        "correction.o009.original.bridge.regular-conditional-probability."
    )
    expected_correction_map = {
        item["correction_id"]: item for item in expected_corrections
    }
    actual_correction_map = {
        item["correction_id"]: item
        for item in corrections
        if item["correction_id"].startswith(correction_prefix)
    }
    if actual_correction_map != expected_correction_map:
        raise RuntimeError(
            "original bridge 03 clarification-correction closure differs"
        )
    if len(actual_correction_map) != 2:
        raise RuntimeError("original bridge 03 must expose exactly two donor clarifications")
    expected_artifacts = {
        "artifact.input.original-bridge-03-source": ORIGINAL_BRIDGE_03_SOURCE,
        "artifact.input.original-bridge-03-reader": ORIGINAL_BRIDGE_03_READER,
        "artifact.input.original-bridge-03-mastery-ledger": (
            ORIGINAL_BRIDGE_03_MASTERY_LEDGER
        ),
    }
    for artifact_id, path in expected_artifacts.items():
        artifact = artifacts.get(artifact_id)
        data = require_file(path)
        if (
            artifact is None
            or artifact["path"] != relative(path)
            or artifact["bytes"] != str(len(data))
            or artifact["sha256"] != sha256(data)
        ):
            raise RuntimeError(
                f"original bridge 03 artifact binding differs: {artifact_id}"
            )
    ledger = load_json(ORIGINAL_BRIDGE_03_MASTERY_LEDGER)
    if ledger != original_bridge_03_mastery_ledger(admitted=True):
        raise RuntimeError(
            "original bridge 03 mastery ledger differs from exact +3 contract"
        )
    site_inventory = validate_site_manifest_inventory()
    if site_inventory.get(ORIGINAL_BRIDGE_03_PATH) != sha256(
        require_file(ORIGINAL_BRIDGE_03_READER)
    ):
        raise RuntimeError("site manifest does not bind original bridge 03 reader")
    validate_preserved_corpus_counts(records)


def original_bridge_04_section_id(local_id: str) -> str:
    return f"{ORIGINAL_BRIDGE_04_UNIT_ID}.section.{local_id}"


def original_bridge_04_segment_id(local_id: str) -> str:
    return f"segment.o009.original.bridge.hypothesis-audits.section.{local_id}"


def original_bridge_04_source_contract() -> tuple[bytes, str, dict[str, Span]]:
    data = require_file(ORIGINAL_BRIDGE_04_SOURCE)
    if (
        len(data) != ORIGINAL_BRIDGE_04_SOURCE_BYTES
        or sha256(data) != ORIGINAL_BRIDGE_04_SOURCE_SHA256
    ):
        raise RuntimeError(
            "original bridge 04 source differs from the admitted "
            f"{ORIGINAL_BRIDGE_04_SOURCE_BYTES:,}-byte freeze"
        )
    if b"\r" in data or not data.endswith(b"\n"):
        raise RuntimeError("original bridge 04 source must be UTF-8 LF with final LF")
    text = data.decode("utf-8")
    spans = fenced_div_spans(text)
    expected_ids = {
        ORIGINAL_BRIDGE_04_UNIT_ID,
        *(local_id for local_id, _, _ in ORIGINAL_BRIDGE_04_SECTION_SPECS),
        *ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS,
        *(
            f"{base_id}.{suffix}"
            for base_id in ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS
            for suffix in ORIGINAL_BRIDGE_04_MASTERY_SUFFIXES
        ),
    }
    if set(spans) != expected_ids or len(expected_ids) != 29:
        raise RuntimeError(
            "original bridge 04 explicit-ID closure differs: "
            f"missing={sorted(expected_ids - set(spans))} "
            f"extra={sorted(set(spans) - expected_ids)}"
        )
    if "original-bridge" not in spans[ORIGINAL_BRIDGE_04_UNIT_ID].classes:
        raise RuntimeError("original bridge 04 root lacks its original-bridge class")
    for local_id, _, _ in ORIGINAL_BRIDGE_04_SECTION_SPECS:
        if "bridge-section" not in spans[local_id].classes:
            raise RuntimeError(
                f"original bridge 04 section class differs: {local_id}"
            )
    expected_child_classes = {
        "exercise": "exercise",
        "hint.01": "hint",
        "hint.02": "hint",
        "answer": "answer",
        "solution": "solution",
    }
    for base_id in ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS:
        if "mastery-sequence" not in spans[base_id].classes:
            raise RuntimeError(f"bridge 04 mastery wrapper class differs: {base_id}")
        for suffix, expected_class in expected_child_classes.items():
            stable_id = f"{base_id}.{suffix}"
            if expected_class not in spans[stable_id].classes:
                raise RuntimeError(
                    f"bridge 04 mastery child class differs: {stable_id}"
                )
    return data, text, spans


def original_bridge_04_reader_contract() -> tuple[
    bytes, BeautifulSoup, dict[str, Any]
]:
    data = require_file(ORIGINAL_BRIDGE_04_READER)
    soup = BeautifulSoup(data.decode("utf-8"), "lxml")
    expected_ids = {
        ORIGINAL_BRIDGE_04_UNIT_ID,
        *(local_id for local_id, _, _ in ORIGINAL_BRIDGE_04_SECTION_SPECS),
        *ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS,
        *(
            f"{base_id}.{suffix}"
            for base_id in ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS
            for suffix in ORIGINAL_BRIDGE_04_MASTERY_SUFFIXES
        ),
    }
    nodes: dict[str, Any] = {}
    for stable_id in sorted(expected_ids):
        matches = soup.find_all(id=stable_id)
        if len(matches) != 1:
            raise RuntimeError(
                "original bridge 04 reader ID must occur exactly once: "
                f"{stable_id}"
            )
        node = matches[0]
        if not " ".join(node.stripped_strings):
            raise RuntimeError(
                f"original bridge 04 reader node is empty: {stable_id}"
            )
        nodes[stable_id] = node
    duplicate_ids = sorted(
        stable_id
        for stable_id in {
            str(node.get("id"))
            for node in soup.find_all(id=True)
            if node.get("id")
        }
        if len(soup.find_all(id=stable_id)) != 1
    )
    if duplicate_ids:
        raise RuntimeError(
            f"original bridge 04 reader contains duplicate IDs: {duplicate_ids}"
        )
    return data, soup, nodes


def original_bridge_04_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    source_data, source_text, source_spans = original_bridge_04_source_contract()
    reader_data, _, reader_nodes = original_bridge_04_reader_contract()

    def source_extent(stable_id: str) -> str:
        span = source_spans[stable_id]
        return source_text[span.start : span.end]

    def source_extent_sha(stable_id: str) -> str:
        return sha256(source_extent(stable_id).encode("utf-8"))

    def reader_node_sha(stable_id: str) -> str:
        return sha256(str(reader_nodes[stable_id]).encode("utf-8"))

    all_bridge_concepts = list(
        dict.fromkeys(
            concept_id
            for _, _, concept_ids in ORIGINAL_BRIDGE_04_SECTION_SPECS
            for concept_id in concept_ids
        )
    )
    entities: list[dict[str, Any]] = [
        *(
            record("concept", stable_id, payload={"label_en": label})
            for stable_id, label in ORIGINAL_BRIDGE_04_NEW_CONCEPTS.items()
        ),
        record(
            "rights",
            ORIGINAL_BRIDGE_04_RIGHTS_ID,
            source_local_id="hak-dan-provenans-audit-hipotesis",
            source_locator=(
                "source/original/04-audit-hipotesis-proses-stokastik.md"
                "#hak-dan-provenans-audit-hipotesis"
            ),
            source_sha256=source_extent_sha("hak-dan-provenans-audit-hipotesis"),
            target_sha256=reader_node_sha("hak-dan-provenans-audit-hipotesis"),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": (
                    "source/original/04-audit-hipotesis-proses-stokastik.md "
                    "and its built reader rendering only"
                ),
                "model_disclosure": "OpenAI Codex gpt-5.6-sol, Ultra.",
                "does_not_relicense_random_quantecon_or_prior_bridges": True,
                "non_endorsement": True,
            },
        ),
        *(
            record(
                "outcome",
                stable_id,
                parent_id="course.o009.d30",
                locale="id-ID",
                translation_state="authored",
                rights_id=ORIGINAL_BRIDGE_04_RIGHTS_ID,
                concept_ids=concept_ids,
                payload={"label": label, "cognitive_level": level},
            )
            for stable_id, (label, level, concept_ids) in ORIGINAL_BRIDGE_04_OUTCOMES.items()
        ),
        record(
            "unit",
            ORIGINAL_BRIDGE_04_UNIT_ID,
            parent_id="course.o009.d30",
            order=39,
            path=ORIGINAL_BRIDGE_04_PATH,
            source_local_id=ORIGINAL_BRIDGE_04_UNIT_ID,
            source_locator=relative(ORIGINAL_BRIDGE_04_SOURCE),
            source_sha256=sha256(source_data),
            target_sha256=sha256(reader_data),
            locale="id-ID",
            translation_state="built",
            relationship="authored",
            rights_id=ORIGINAL_BRIDGE_04_RIGHTS_ID,
            concept_ids=all_bridge_concepts,
            payload={
                "title": "Audit hipotesis untuk proses stokastik",
                "unit_kind": "original-bridge",
                "body_extent": "complete-source-and-reader-page",
                "source_type": "original",
                "source_bytes": len(source_data),
                "reader_bytes": len(reader_data),
                "section_count": len(ORIGINAL_BRIDGE_04_SECTION_SPECS),
                "section_segment_count": len(ORIGINAL_BRIDGE_04_SECTION_SPECS),
                "mastery_sequence_count": len(ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS),
                "mastery_child_count": (
                    len(ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS)
                    * len(ORIGINAL_BRIDGE_04_MASTERY_SUFFIXES)
                ),
                "model_disclosure": "OpenAI Codex gpt-5.6-sol, Ultra.",
                "excluded_from_random_page_count": True,
                "excluded_from_quantecon_chapter_count": True,
                "executable_lab_count": 0,
            },
        ),
    ]

    section_ids: dict[str, str] = {}
    segments: list[dict[str, Any]] = []
    for order, (local_id, title, concept_ids) in enumerate(
        ORIGINAL_BRIDGE_04_SECTION_SPECS, start=1
    ):
        stable_id = original_bridge_04_section_id(local_id)
        section_ids[local_id] = stable_id
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=ORIGINAL_BRIDGE_04_UNIT_ID,
                order=order,
                path=ORIGINAL_BRIDGE_04_PATH,
                source_local_id=local_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_04_SOURCE)}#{local_id}",
                source_sha256=source_extent_sha(local_id),
                target_sha256=reader_node_sha(local_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_04_RIGHTS_ID,
                concept_ids=list(concept_ids),
                payload={
                    "title": title,
                    "unit_kind": "section",
                    "body_extent": "complete-fenced-div",
                    "built_id": local_id,
                },
            )
        )
        segments.append(
            record(
                "segment",
                original_bridge_04_segment_id(local_id),
                parent_id=stable_id,
                order=1,
                path=ORIGINAL_BRIDGE_04_PATH,
                source_local_id=local_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_04_SOURCE)}#{local_id}",
                source_sha256=source_extent_sha(local_id),
                target_sha256=reader_node_sha(local_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_04_RIGHTS_ID,
                concept_ids=list(concept_ids),
                payload={
                    "source_markdown": source_extent(local_id),
                    "reader_text": " ".join(reader_nodes[local_id].stripped_strings),
                    "source_extent": "complete-fenced-div",
                    "reader_extent": "complete-id-node",
                    "tag": str(reader_nodes[local_id].name),
                },
            )
        )

    mastery_concepts = {
        1: [
            "concept.probability.hypothesis-audit",
            "concept.probability.almost-sure-convergence",
            "concept.probability.convergence-in-probability",
            "concept.probability.lp-convergence",
            "concept.expectation.uniform-integrability",
        ],
        2: [
            "concept.probability.hypothesis-audit",
            "concept.martingale.optional-stopping",
            "concept.stochastic.stopping-time",
            "concept.stochastic.stopped-process",
            "concept.expectation.uniform-integrability",
        ],
        3: [
            "concept.probability.hypothesis-audit",
            "concept.stochastic.process.finite-dimensional-distributions",
            "concept.stochastic.process.regular-path-space-law",
            "concept.stochastic.process.path-law-tightness",
            "concept.probability.continuous-mapping-theorem",
        ],
    }
    child_kinds = {
        "exercise": "exercise",
        "hint.01": "hint",
        "hint.02": "hint",
        "answer": "answer",
        "solution": "solution",
    }
    mastery_parent = section_ids["latihan-penguasaan-audit-hipotesis"]
    for mastery_order, base_id in enumerate(
        ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS, start=1
    ):
        entities.append(
            record(
                "unit",
                base_id,
                parent_id=mastery_parent,
                order=mastery_order,
                path=ORIGINAL_BRIDGE_04_PATH,
                source_local_id=base_id,
                source_locator=f"{relative(ORIGINAL_BRIDGE_04_SOURCE)}#{base_id}",
                source_sha256=source_extent_sha(base_id),
                target_sha256=reader_node_sha(base_id),
                locale="id-ID",
                translation_state="built",
                relationship="authored",
                rights_id=ORIGINAL_BRIDGE_04_RIGHTS_ID,
                concept_ids=mastery_concepts[mastery_order],
                payload={
                    "unit_kind": "mastery-sequence",
                    "body_extent": "complete-fenced-div",
                    "built_id": base_id,
                    "quota_category": "integrative-counterexample-literature-reading",
                },
            )
        )
        for child_order, suffix in enumerate(
            ORIGINAL_BRIDGE_04_MASTERY_SUFFIXES, start=1
        ):
            stable_id = f"{base_id}.{suffix}"
            entities.append(
                record(
                    "unit",
                    stable_id,
                    parent_id=base_id,
                    order=child_order,
                    path=ORIGINAL_BRIDGE_04_PATH,
                    source_local_id=stable_id,
                    source_locator=(
                        f"{relative(ORIGINAL_BRIDGE_04_SOURCE)}#{stable_id}"
                    ),
                    source_sha256=source_extent_sha(stable_id),
                    target_sha256=reader_node_sha(stable_id),
                    locale="id-ID",
                    translation_state="built",
                    relationship="authored",
                    rights_id=ORIGINAL_BRIDGE_04_RIGHTS_ID,
                    concept_ids=mastery_concepts[mastery_order],
                    payload={
                        "unit_kind": child_kinds[suffix],
                        "body_extent": "complete-fenced-div",
                        "built_id": stable_id,
                        "mastery_sequence": mastery_order,
                    },
                )
            )

    relation_prefix = "rel.o009.original.bridge.hypothesis-audits"
    relations: list[dict[str, str]] = [
        relation(
            f"{relation_prefix}.contains.course",
            "contains",
            "course.o009.d30",
            ORIGINAL_BRIDGE_04_UNIT_ID,
            "complete original bridge 04 source and reader page",
        ),
        relation(
            f"{relation_prefix}.precedes.bridge-03",
            "precedes",
            ORIGINAL_BRIDGE_03_UNIT_ID,
            ORIGINAL_BRIDGE_04_UNIT_ID,
            "curriculum order 38 to 39; bridge 04 follows the admitted conditional-law bridge",
        ),
        *(
            relation(
                f"{relation_prefix}.depends.{suffix}",
                "depends-on",
                ORIGINAL_BRIDGE_04_UNIT_ID,
                target_id,
                evidence,
            )
            for suffix, target_id, evidence in (
                (
                    "bridge-01",
                    ORIGINAL_BRIDGE_UNIT_ID,
                    "canonical process and Kolmogorov-extension distinctions from bridge 01",
                ),
                (
                    "bridge-02",
                    ORIGINAL_BRIDGE_02_UNIT_ID,
                    "finite-dimensional versus regular path-law distinctions from bridge 02",
                ),
                (
                    "bridge-03",
                    ORIGINAL_BRIDGE_03_UNIT_ID,
                    "conditional-version and coherent-kernel distinctions from bridge 03",
                ),
                (
                    "random-prob-convergence",
                    "unit.o009.random.prob.convergence",
                    "source link for modes of convergence of random variables",
                ),
                (
                    "random-dist-convergence",
                    "unit.o009.random.dist.convergence",
                    "source link for convergence in distribution",
                ),
                (
                    "random-uniform-integrability",
                    "unit.o009.random.expect.uniform",
                    "source link for uniform-integrability convergence conditions",
                ),
                (
                    "random-conditional2",
                    "unit.o009.random.expect.conditional2",
                    "source link for conditional expectation and Bayes scope",
                ),
                (
                    "random-kernels",
                    "unit.o009.random.expect.kernels",
                    "source link for probability kernels",
                ),
                (
                    "random-martingale-stop",
                    "unit.o009.random.martingales.stop",
                    "source link for optional stopping",
                ),
                (
                    "random-martingale-convergence",
                    "unit.o009.random.martingales.convergence",
                    "source link for martingale convergence conditions",
                ),
                (
                    "random-markov-limiting",
                    "unit.o009.random.markov.limiting",
                    "source link for irreducibility, periodicity, and limiting laws",
                ),
                (
                    "quantecon-generators",
                    "unit.o009.quantecon.ctmc.generators",
                    "source link for generators and continuous-time semigroups",
                ),
                (
                    "quantecon-ergodicity",
                    "unit.o009.quantecon.ctmc.stationarity-ergodicity",
                    "source link for stationary-distribution uniqueness and stability",
                ),
                (
                    "random-poisson-general",
                    "unit.o009.random.poisson.general",
                    "source link for Poisson random measures",
                ),
                (
                    "quantecon-poisson",
                    "unit.o009.quantecon.ctmc.poisson-processes",
                    "source link for counting-process characterization",
                ),
                (
                    "random-brown-standard",
                    "unit.o009.random.brown.standard",
                    "source link for Brownian finite-dimensional and path-law claims",
                ),
            )
        ),
        *(
            relation(
                f"{relation_prefix}.teaches.outcome.{index:02d}",
                "teaches",
                ORIGINAL_BRIDGE_04_UNIT_ID,
                outcome_id,
                "two explicit reader outcomes in tujuan-dan-protokol-audit-hipotesis",
            )
            for index, outcome_id in enumerate(
                ORIGINAL_BRIDGE_04_OUTCOMES, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.contains.section.{index:02d}",
                "contains",
                ORIGINAL_BRIDGE_04_UNIT_ID,
                section_ids[local_id],
                f"{ORIGINAL_BRIDGE_04_PATH}#{local_id}",
            )
            for index, (local_id, _, _) in enumerate(
                ORIGINAL_BRIDGE_04_SECTION_SPECS, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.contains.section-segment.{index:02d}",
                "contains",
                section_ids[local_id],
                original_bridge_04_segment_id(local_id),
                f"complete source/reader extent at {ORIGINAL_BRIDGE_04_PATH}#{local_id}",
            )
            for index, (local_id, _, _) in enumerate(
                ORIGINAL_BRIDGE_04_SECTION_SPECS, start=1
            )
        ),
        *(
            relation(
                f"{relation_prefix}.precedes.section.{index:02d}.{index + 1:02d}",
                "precedes",
                section_ids[ORIGINAL_BRIDGE_04_SECTION_SPECS[index - 1][0]],
                section_ids[ORIGINAL_BRIDGE_04_SECTION_SPECS[index][0]],
                "original bridge 04 source and reader DOM order",
            )
            for index in range(1, len(ORIGINAL_BRIDGE_04_SECTION_SPECS))
        ),
    ]
    mastery_outcomes = {
        1: ["outcome.o009.audit-and-repair-stochastic-process-claims"],
        2: [
            "outcome.o009.audit-and-repair-stochastic-process-claims",
            "outcome.o009.check-optional-stopping-conditions",
        ],
        3: [
            "outcome.o009.audit-and-repair-stochastic-process-claims",
            "outcome.o009.audit-fdd-versus-path-law-convergence",
            "outcome.o009.audit-fdd-versus-regular-path-law",
        ],
    }
    for mastery_order, base_id in enumerate(
        ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS, start=1
    ):
        relations.append(
            relation(
                f"{relation_prefix}.contains.mastery.{mastery_order:02d}",
                "contains",
                mastery_parent,
                base_id,
                f"{ORIGINAL_BRIDGE_04_PATH}#{base_id}",
            )
        )
        if mastery_order > 1:
            relations.append(
                relation(
                    f"{relation_prefix}.precedes.mastery.{mastery_order - 1:02d}.{mastery_order:02d}",
                    "precedes",
                    ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS[mastery_order - 2],
                    base_id,
                    "original bridge 04 mastery sequence order",
                )
            )
        child_ids = [
            f"{base_id}.{suffix}" for suffix in ORIGINAL_BRIDGE_04_MASTERY_SUFFIXES
        ]
        for child_order, (suffix, child_id) in enumerate(
            zip(ORIGINAL_BRIDGE_04_MASTERY_SUFFIXES, child_ids), start=1
        ):
            relations.append(
                relation(
                    f"{relation_prefix}.contains.mastery.{mastery_order:02d}.{suffix.replace('.', '-')}",
                    "contains",
                    base_id,
                    child_id,
                    f"{ORIGINAL_BRIDGE_04_PATH}#{child_id}",
                )
            )
            if child_order > 1:
                relations.append(
                    relation(
                        f"{relation_prefix}.precedes.mastery.{mastery_order:02d}.{child_order - 1:02d}.{child_order:02d}",
                        "precedes",
                        child_ids[child_order - 2],
                        child_id,
                        "exercise, two hints, answer, and solution DOM order",
                    )
                )
        exercise_id, hint_01_id, hint_02_id, answer_id, solution_id = child_ids
        for hint_order, hint_id in enumerate((hint_01_id, hint_02_id), start=1):
            relations.append(
                relation(
                    f"{relation_prefix}.hints.mastery.{mastery_order:02d}.{hint_order:02d}",
                    "hints",
                    hint_id,
                    exercise_id,
                    "progressive hint bound to its complete exercise",
                )
            )
        relations.extend(
            [
                relation(
                    f"{relation_prefix}.answers.mastery.{mastery_order:02d}",
                    "answers",
                    answer_id,
                    exercise_id,
                    "concise answer bound to its complete exercise",
                ),
                relation(
                    f"{relation_prefix}.solves.mastery.{mastery_order:02d}",
                    "solves",
                    solution_id,
                    exercise_id,
                    "worked solution bound to its complete exercise",
                ),
            ]
        )
        for outcome_order, outcome_id in enumerate(
            mastery_outcomes[mastery_order], start=1
        ):
            relations.append(
                relation(
                    f"{relation_prefix}.assesses.mastery.{mastery_order:02d}.{outcome_order:02d}",
                    "assesses",
                    exercise_id,
                    outcome_id,
                    "complete original mastery prompt and worked solution",
                )
            )

    allowed_relation_types = {
        "contains",
        "depends-on",
        "precedes",
        "teaches",
        "assesses",
        "hints",
        "answers",
        "solves",
    }
    if any(item["relation_type"] not in allowed_relation_types for item in relations):
        raise RuntimeError(
            "original bridge 04 emitted a relation type outside its contract"
        )

    corrections = [
        {
            "correction_id": (
                "correction.o009.original.bridge.hypothesis-audits."
                "uniform-convergence-premise-scope"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.random.expect.uniform",
            "target_id": section_ids["audit-konvergensi-dan-integrabilitas"],
            "description": (
                "Clarify that the concluding mean-convergence consequence retains "
                "the immediately preceding almost-sure or in-probability convergence "
                "premise; uniform integrability alone is insufficient; retain the "
                "Random donor bytes unchanged."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_04_PATH}#audit-konvergensi-dan-integrabilitas"
            ),
            "status": "accepted",
        },
        {
            "correction_id": (
                "correction.o009.original.bridge.hypothesis-audits."
                "conditional2-bayes-positive-denominator"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.random.expect.conditional2",
            "target_id": section_ids["audit-pengondisian-dan-kernel"],
            "description": (
                "Retain P(B)>0 for ratio-form Bayes conditional probability and state "
                "that a null conditioning event does not select a canonical value; "
                "retain the Conditional2 donor bytes unchanged."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_04_PATH}#audit-pengondisian-dan-kernel"
            ),
            "status": "accepted",
        },
        {
            "correction_id": (
                "correction.o009.original.bridge.hypothesis-audits."
                "ergodicity-uniqueness-without-existence"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.quantecon.ctmc.stationarity-ergodicity",
            "target_id": section_ids["audit-markov-dan-ctmc"],
            "description": (
                "Clarify that irreducibility gives at most one stationary distribution "
                "and does not by itself prove existence or asymptotic stability; retain "
                "the QuantEcon donor bytes unchanged."
            ),
            "evidence": f"{ORIGINAL_BRIDGE_04_PATH}#audit-markov-dan-ctmc",
            "status": "accepted",
        },
        {
            "correction_id": (
                "correction.o009.original.bridge.hypothesis-audits."
                "poisson-characterization-counting-process-context"
            ),
            "change_kind": "original-addition",
            "source_id": "unit.o009.quantecon.ctmc.poisson-processes",
            "target_id": section_ids["audit-poisson-dan-konstruksi-proses"],
            "description": (
                "Retain the established counting-process path, unit-jump, and "
                "nonexplosion context in the Poisson characterization; stationary "
                "independent increments and integer-valued start alone admit "
                "compound-Poisson counterexamples; retain the QuantEcon donor bytes "
                "unchanged."
            ),
            "evidence": (
                f"{ORIGINAL_BRIDGE_04_PATH}#audit-poisson-dan-konstruksi-proses"
            ),
            "status": "accepted",
        },
    ]
    return entities, segments, relations, corrections


def original_bridge_04_mastery_ledger(*, admitted: bool) -> dict[str, Any]:
    source_data, _, _ = original_bridge_04_source_contract()
    reader_sha256 = None
    reader_bytes = None
    if admitted:
        reader_data, _, _ = original_bridge_04_reader_contract()
        reader_sha256 = sha256(reader_data)
        reader_bytes = len(reader_data)
    mastery_outcomes = {
        1: ["outcome.o009.audit-and-repair-stochastic-process-claims"],
        2: [
            "outcome.o009.audit-and-repair-stochastic-process-claims",
            "outcome.o009.check-optional-stopping-conditions",
        ],
        3: [
            "outcome.o009.audit-and-repair-stochastic-process-claims",
            "outcome.o009.audit-fdd-versus-path-law-convergence",
            "outcome.o009.audit-fdd-versus-regular-path-law",
        ],
    }
    sequences = []
    for order, base_id in enumerate(ORIGINAL_BRIDGE_04_MASTERY_BASE_IDS, start=1):
        sequences.append(
            {
                "id": base_id,
                "exercise_id": f"{base_id}.exercise",
                "hint_ids": [f"{base_id}.hint.01", f"{base_id}.hint.02"],
                "answer_id": f"{base_id}.answer",
                "solution_id": f"{base_id}.solution",
                "assesses": mastery_outcomes[order],
                "rights_id": ORIGINAL_BRIDGE_04_RIGHTS_ID,
            }
        )
    return {
        "schema": "o009.original-bridge-04-mastery-ledger.v1",
        "generated": STAMP,
        "course_id": "course.o009.d30",
        "unit_id": ORIGINAL_BRIDGE_04_UNIT_ID,
        "status": "admitted" if admitted else "reader-build-pending",
        "source": {
            "path": relative(ORIGINAL_BRIDGE_04_SOURCE),
            "bytes": len(source_data),
            "sha256": sha256(source_data),
        },
        "built_reader": {
            "path": ORIGINAL_BRIDGE_04_PATH,
            "bytes": reader_bytes,
            "sha256": reader_sha256,
            "status": "bound" if admitted else "pending-no-hash-fabricated",
        },
        "rights_id": ORIGINAL_BRIDGE_04_RIGHTS_ID,
        "quota": {
            "category_id": "integrative-counterexample-literature-reading",
            "required": 6,
            "credited_before_bridge": 3,
            "bridge_increment_after_all_gates": 3,
            "credited_currently": 3 if admitted else 0,
            "credited_after_bridge_admission": 6,
            "remaining_after_bridge_admission": 0,
            "course_original_mastery_credited_before_bridge": 9,
            "course_original_mastery_credited_after_bridge_admission": (
                12 if admitted else 9
            ),
            "course_original_mastery_remaining_after_bridge_admission": (
                24 if admitted else 27
            ),
            "does_not_recredit_prior_bridges": True,
        },
        "counts": {
            "mastery_sequences": 3,
            "exercise_records": 3,
            "hint_records": 6,
            "answer_records": 3,
            "solution_records": 3,
            "mastery_child_records": 15,
        },
        "validation": {
            "all_source_extents_complete": True,
            "all_reader_extents_complete": admitted,
            "all_relation_endpoints_validated": admitted,
            "all_rights_bindings_validated": admitted,
            "credit_admitted": admitted,
        },
        "sequences": sequences,
    }


def write_original_bridge_04_mastery_ledger() -> None:
    reader_data, _, _ = original_bridge_04_reader_contract()
    site_inventory = validate_site_manifest_inventory()
    if site_inventory.get(ORIGINAL_BRIDGE_04_PATH) != sha256(reader_data):
        raise RuntimeError(
            "site manifest does not bind original bridge 04; mastery remains unadmitted"
        )
    ORIGINAL_BRIDGE_04_MASTERY_LEDGER.write_text(
        json.dumps(
            original_bridge_04_mastery_ledger(admitted=True),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def validate_original_bridge_04_contract(
    records: list[dict[str, Any]],
    relations: list[dict[str, str]],
    corrections: list[dict[str, str]],
    artifacts: dict[str, dict[str, str]],
) -> None:
    expected_entities, expected_segments, expected_relations, expected_corrections = (
        original_bridge_04_entities()
    )
    by_id = entities_by_id(records)
    expected_by_id = entities_by_id(expected_entities + expected_segments)
    for stable_id, expected in expected_by_id.items():
        if by_id.get(stable_id) != expected:
            raise RuntimeError(
                "original bridge 04 backend record differs from exact contract: "
                f"{stable_id}"
            )
    segment_prefix = "segment.o009.original.bridge.hypothesis-audits.section."
    bridge_record_ids = {
        stable_id
        for stable_id in by_id
        if stable_id == ORIGINAL_BRIDGE_04_UNIT_ID
        or stable_id == ORIGINAL_BRIDGE_04_RIGHTS_ID
        or stable_id in ORIGINAL_BRIDGE_04_NEW_CONCEPTS
        or stable_id in ORIGINAL_BRIDGE_04_OUTCOMES
        or stable_id.startswith(f"{ORIGINAL_BRIDGE_04_UNIT_ID}.section.")
        or stable_id.startswith("unit.o009.original.mastery.hypothesis-audits.")
        or stable_id.startswith(segment_prefix)
    }
    if bridge_record_ids != set(expected_by_id):
        raise RuntimeError(
            "original bridge 04 stable-ID closure differs: "
            f"missing={sorted(set(expected_by_id) - bridge_record_ids)} "
            f"extra={sorted(bridge_record_ids - set(expected_by_id))}"
        )
    expected_segment_ids = {
        original_bridge_04_segment_id(local_id)
        for local_id, _, _ in ORIGINAL_BRIDGE_04_SECTION_SPECS
    }
    actual_segment_ids = {
        item["id"]
        for item in records
        if item["record_type"] == "segment" and item["id"].startswith(segment_prefix)
    }
    if actual_segment_ids != expected_segment_ids or len(actual_segment_ids) != 10:
        raise RuntimeError("original bridge 04 section-segment closure differs")
    relation_prefix = "rel.o009.original.bridge.hypothesis-audits."
    expected_relation_map = {
        item["relation_id"]: item for item in expected_relations
    }
    actual_relation_map = {
        item["relation_id"]: item
        for item in relations
        if item["relation_id"].startswith(relation_prefix)
    }
    if actual_relation_map != expected_relation_map:
        raise RuntimeError(
            "original bridge 04 relation closure differs from exact contract"
        )
    correction_prefix = "correction.o009.original.bridge.hypothesis-audits."
    expected_correction_map = {
        item["correction_id"]: item for item in expected_corrections
    }
    actual_correction_map = {
        item["correction_id"]: item
        for item in corrections
        if item["correction_id"].startswith(correction_prefix)
    }
    if actual_correction_map != expected_correction_map:
        raise RuntimeError(
            "original bridge 04 clarification-correction closure differs"
        )
    if len(actual_correction_map) != 4:
        raise RuntimeError("original bridge 04 must expose exactly four donor clarifications")
    expected_artifacts = {
        "artifact.input.original-bridge-04-source": ORIGINAL_BRIDGE_04_SOURCE,
        "artifact.input.original-bridge-04-reader": ORIGINAL_BRIDGE_04_READER,
        "artifact.input.original-bridge-04-mastery-ledger": (
            ORIGINAL_BRIDGE_04_MASTERY_LEDGER
        ),
    }
    for artifact_id, path in expected_artifacts.items():
        artifact = artifacts.get(artifact_id)
        data = require_file(path)
        if (
            artifact is None
            or artifact["path"] != relative(path)
            or artifact["bytes"] != str(len(data))
            or artifact["sha256"] != sha256(data)
        ):
            raise RuntimeError(
                f"original bridge 04 artifact binding differs: {artifact_id}"
            )
    ledger = load_json(ORIGINAL_BRIDGE_04_MASTERY_LEDGER)
    if ledger != original_bridge_04_mastery_ledger(admitted=True):
        raise RuntimeError(
            "original bridge 04 mastery ledger differs from exact +3 contract"
        )
    site_inventory = validate_site_manifest_inventory()
    if site_inventory.get(ORIGINAL_BRIDGE_04_PATH) != sha256(
        require_file(ORIGINAL_BRIDGE_04_READER)
    ):
        raise RuntimeError("site manifest does not bind original bridge 04 reader")
    validate_preserved_corpus_counts(records)


def validate_preserved_corpus_counts(records: list[dict[str, Any]]) -> None:
    expected_random_ids = {
        f"unit.o009.random.{spec['slug']}" for spec in THEORY_SPECS
    }
    actual_random_ids = {
        item["id"]
        for item in records
        if item["record_type"] == "unit"
        and item["parent_id"] == "course.o009.d30"
        and item["id"].startswith("unit.o009.random.")
    }
    if len(THEORY_SPECS) != 27 or actual_random_ids != expected_random_ids:
        raise RuntimeError(
            "Random page closure must remain exactly 27: "
            f"missing={sorted(expected_random_ids - actual_random_ids)} "
            f"extra={sorted(actual_random_ids - expected_random_ids)}"
        )
    expected_quantecon_ids = {
        "unit.o009.quantecon.ctmc.memoryless-distributions",
        "unit.o009.quantecon.ctmc.poisson-processes",
        "unit.o009.quantecon.ctmc.markov-property",
        "unit.o009.quantecon.ctmc.kolmogorov-backward",
        "unit.o009.quantecon.ctmc.kolmogorov-forward",
        "unit.o009.quantecon.ctmc.generators",
        "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups",
        "unit.o009.quantecon.ctmc.stationarity-ergodicity",
    }
    actual_quantecon_ids = {
        item["id"]
        for item in records
        if item["record_type"] == "unit"
        and item["parent_id"] == "course.o009.d30"
        and item["id"].startswith("unit.o009.quantecon.ctmc.")
    }
    if actual_quantecon_ids != expected_quantecon_ids:
        raise RuntimeError(
            "QuantEcon chapter closure must remain exactly 8: "
            f"missing={sorted(expected_quantecon_ids - actual_quantecon_ids)} "
            f"extra={sorted(actual_quantecon_ids - expected_quantecon_ids)}"
        )
    quantecon_records = [
        item
        for item in records
        if item["id"].startswith("unit.o009.quantecon.ctmc.")
    ]
    exercise_count = sum(
        item["payload"].get("unit_kind") == "exercise"
        for item in quantecon_records
    )
    solution_count = sum(
        item["payload"].get("unit_kind") == "solution"
        for item in quantecon_records
    )
    if (exercise_count, solution_count) != (25, 25):
        raise RuntimeError(
            "QuantEcon exercise/solution closure must remain 25/25: "
            f"actual={exercise_count}/{solution_count}"
        )
    expected_labs = {
        "o009-lab-convergence-mc",
        "o009-lab-markov-gambler-ruin",
        "o009-lab-convergence-modes",
        "o009-lab-conditional-martingale",
        "o009-lab-brownian-diagnostics",
    }
    actual_labs = {
        item["id"]
        for item in records
        if item["record_type"] == "unit"
        and item["parent_id"] == "course.o009.d30"
        and item["payload"].get("unit_kind") == "lab"
    }
    if actual_labs != expected_labs:
        raise RuntimeError(
            "admitted executable lab closure must match the current boundary: "
            f"missing={sorted(expected_labs - actual_labs)} "
            f"extra={sorted(actual_labs - expected_labs)}"
        )


def validate_original_bridge_contract(
    records: list[dict[str, Any]],
    relations: list[dict[str, str]],
    corrections: list[dict[str, str]],
    artifacts: dict[str, dict[str, str]],
) -> None:
    expected_entities, expected_segments, expected_relations, expected_corrections = (
        original_bridge_entities()
    )
    if expected_segments:
        raise RuntimeError("original bridge contract unexpectedly emitted segments")
    by_id = entities_by_id(records)
    expected_by_id = entities_by_id(expected_entities)
    for stable_id, expected in expected_by_id.items():
        if by_id.get(stable_id) != expected:
            raise RuntimeError(
                f"original bridge backend record differs from exact contract: {stable_id}"
            )
    bridge_record_ids = {
        stable_id
        for stable_id in by_id
        if stable_id == ORIGINAL_BRIDGE_UNIT_ID
        or stable_id == ORIGINAL_BRIDGE_RIGHTS_ID
        or stable_id in ORIGINAL_BRIDGE_NEW_CONCEPTS
        or stable_id in ORIGINAL_BRIDGE_OUTCOMES
        or stable_id.startswith(f"{ORIGINAL_BRIDGE_UNIT_ID}.section.")
        or stable_id.startswith("unit.o009.original.mastery.process-construction.")
    }
    if bridge_record_ids != set(expected_by_id):
        raise RuntimeError(
            "original bridge stable-ID closure differs: "
            f"missing={sorted(set(expected_by_id) - bridge_record_ids)} "
            f"extra={sorted(bridge_record_ids - set(expected_by_id))}"
        )
    relation_prefix = "rel.o009.original.bridge.kolmogorov."
    expected_relation_map = {
        item["relation_id"]: item for item in expected_relations
    }
    actual_relation_map = {
        item["relation_id"]: item
        for item in relations
        if item["relation_id"].startswith(relation_prefix)
    }
    if actual_relation_map != expected_relation_map:
        raise RuntimeError("original bridge relation closure differs from exact contract")
    correction_prefix = "correction.o009.original.bridge.kolmogorov."
    expected_correction_map = {
        item["correction_id"]: item for item in expected_corrections
    }
    actual_correction_map = {
        item["correction_id"]: item
        for item in corrections
        if item["correction_id"].startswith(correction_prefix)
    }
    if actual_correction_map != expected_correction_map:
        raise RuntimeError("original bridge correction closure differs from exact contract")
    expected_artifacts = {
        "artifact.input.original-bridge-01-source": ORIGINAL_BRIDGE_SOURCE,
        "artifact.input.original-bridge-01-reader": ORIGINAL_BRIDGE_READER,
        "artifact.input.original-bridge-01-mastery-ledger": (
            ORIGINAL_BRIDGE_MASTERY_LEDGER
        ),
    }
    for artifact_id, path in expected_artifacts.items():
        artifact = artifacts.get(artifact_id)
        data = require_file(path)
        if (
            artifact is None
            or artifact["path"] != relative(path)
            or artifact["bytes"] != str(len(data))
            or artifact["sha256"] != sha256(data)
        ):
            raise RuntimeError(
                f"original bridge artifact binding differs: {artifact_id}"
            )
    ledger = load_json(ORIGINAL_BRIDGE_MASTERY_LEDGER)
    if ledger != original_bridge_mastery_ledger(admitted=True):
        raise RuntimeError("original bridge mastery ledger differs from exact +3/1 contract")
    site_inventory = validate_site_manifest_inventory()
    if site_inventory.get(ORIGINAL_BRIDGE_PATH) != sha256(
        require_file(ORIGINAL_BRIDGE_READER)
    ):
        raise RuntimeError("site manifest does not bind the original bridge reader")
    validate_preserved_corpus_counts(records)


def validate_original_bridge_02_contract(
    records: list[dict[str, Any]],
    relations: list[dict[str, str]],
    corrections: list[dict[str, str]],
    artifacts: dict[str, dict[str, str]],
) -> None:
    expected_entities, expected_segments, expected_relations, expected_corrections = (
        original_bridge_02_entities()
    )
    if expected_segments:
        raise RuntimeError("original bridge 02 contract unexpectedly emitted segments")
    by_id = entities_by_id(records)
    expected_by_id = entities_by_id(expected_entities)
    for stable_id, expected in expected_by_id.items():
        if by_id.get(stable_id) != expected:
            raise RuntimeError(
                "original bridge 02 backend record differs from exact contract: "
                f"{stable_id}"
            )
    bridge_record_ids = {
        stable_id
        for stable_id in by_id
        if stable_id == ORIGINAL_BRIDGE_02_UNIT_ID
        or stable_id == ORIGINAL_BRIDGE_02_RIGHTS_ID
        or stable_id in ORIGINAL_BRIDGE_02_NEW_CONCEPTS
        or stable_id in ORIGINAL_BRIDGE_02_OUTCOMES
        or stable_id.startswith(f"{ORIGINAL_BRIDGE_02_UNIT_ID}.section.")
        or stable_id.startswith(
            "unit.o009.original.mastery.measurability-path-law."
        )
    }
    if bridge_record_ids != set(expected_by_id):
        raise RuntimeError(
            "original bridge 02 stable-ID closure differs: "
            f"missing={sorted(set(expected_by_id) - bridge_record_ids)} "
            f"extra={sorted(bridge_record_ids - set(expected_by_id))}"
        )
    relation_prefix = "rel.o009.original.bridge.process-measurability-path-law."
    expected_relation_map = {
        item["relation_id"]: item for item in expected_relations
    }
    actual_relation_map = {
        item["relation_id"]: item
        for item in relations
        if item["relation_id"].startswith(relation_prefix)
    }
    if actual_relation_map != expected_relation_map:
        raise RuntimeError(
            "original bridge 02 relation closure differs from exact contract"
        )
    correction_prefix = (
        "correction.o009.original.bridge.process-measurability-path-law."
    )
    expected_correction_map = {
        item["correction_id"]: item for item in expected_corrections
    }
    actual_correction_map = {
        item["correction_id"]: item
        for item in corrections
        if item["correction_id"].startswith(correction_prefix)
    }
    if actual_correction_map != expected_correction_map:
        raise RuntimeError(
            "original bridge 02 correction closure differs from exact contract"
        )
    expected_artifacts = {
        "artifact.input.original-bridge-02-source": ORIGINAL_BRIDGE_02_SOURCE,
        "artifact.input.original-bridge-02-reader": ORIGINAL_BRIDGE_02_READER,
        "artifact.input.original-bridge-02-mastery-ledger": (
            ORIGINAL_BRIDGE_02_MASTERY_LEDGER
        ),
    }
    for artifact_id, path in expected_artifacts.items():
        artifact = artifacts.get(artifact_id)
        data = require_file(path)
        if (
            artifact is None
            or artifact["path"] != relative(path)
            or artifact["bytes"] != str(len(data))
            or artifact["sha256"] != sha256(data)
        ):
            raise RuntimeError(
                f"original bridge 02 artifact binding differs: {artifact_id}"
            )
    ledger = load_json(ORIGINAL_BRIDGE_02_MASTERY_LEDGER)
    if ledger != original_bridge_02_mastery_ledger(admitted=True):
        raise RuntimeError(
            "original bridge 02 mastery ledger differs from exact +3/3 contract"
        )
    site_inventory = validate_site_manifest_inventory()
    if site_inventory.get(ORIGINAL_BRIDGE_02_PATH) != sha256(
        require_file(ORIGINAL_BRIDGE_02_READER)
    ):
        raise RuntimeError("site manifest does not bind original bridge 02 reader")
    if any(
        item["source_id"].startswith(ORIGINAL_BRIDGE_02_UNIT_ID)
        and item["target_id"].startswith("unit.o009.original.bridge.")
        and item["target_id"] not in by_id
        for item in relations
    ):
        raise RuntimeError("original bridge 02 has a relation to a future seam endpoint")
    validate_preserved_corpus_counts(records)


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


def markov_donor_components() -> tuple[
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
    dict[str, str],
]:
    """Close the exact Žitković Markov-chain donor slice under stable IDs."""
    whole_text = require_file(ZIT_MARKOV).decode("utf-8")
    lines = whole_text.splitlines()
    donor_slice = "\n".join(lines[600:666]) + "\n"
    expected_slice_hash = "dcabe361eaaacaa537966f2bf8809dd8eac52e28392edc78d8e289c8c9be2bd8"
    if sha256(donor_slice.encode("utf-8")) != expected_slice_hash:
        raise RuntimeError("Žitković donor slice source/05-Markov-chains.Rmd L601-L666 changed")

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
                raise RuntimeError("unmatched Markov donor fenced-div close")
            classes, start, content_start = stack.pop()
            blocks.append((classes, Span(start, match.end(), content_start, match.start(), classes)))
    if stack:
        raise RuntimeError("unclosed Markov donor fenced div")
    exercise_spans = [span for classes, span in blocks if "exercise" in classes]
    solution_spans = [span for classes, span in blocks if "solution" in classes]
    if len(exercise_spans) != 1 or len(solution_spans) != 1:
        raise RuntimeError(
            "expected exactly one exercise and one solution in the Markov donor slice"
        )
    exercise_span = exercise_spans[0]
    solution_span = solution_spans[0]
    chunks = [
        span
        for _, span in r_chunk_spans(
            donor_slice[solution_span.content_start : solution_span.content_end]
        )
    ]
    if len(chunks) != 1:
        raise RuntimeError(f"expected one donor Markov R chunk, found {len(chunks)}")
    program_span = Span(
        solution_span.content_start + chunks[0].start,
        solution_span.content_start + chunks[0].end,
        solution_span.content_start + chunks[0].content_start,
        solution_span.content_start + chunks[0].content_end,
    )
    section_span = Span(0, len(donor_slice), 0, len(donor_slice))

    entities: list[dict[str, Any]] = []
    aliases: list[dict[str, str]] = []
    hashes: dict[str, str] = {}

    def add_donor(
        stable_id: str,
        kind: str,
        span: Span,
        parent_id: str | None,
        order: int,
        concepts: list[str],
    ) -> None:
        body = donor_slice[span.start : span.end]
        locator = (
            "source/05-Markov-chains.Rmd"
            f"#L{line_number(donor_slice, span.start, 601)}-"
            f"L{line_number(donor_slice, span.end - 1, 601)}"
        )
        digest = sha256(body.encode("utf-8"))
        hashes[stable_id] = digest
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=parent_id,
                order=order,
                path=relative(ZIT_MARKOV),
                resource_id="resource.zitkovic.stochastic-book",
                edition_id="edition.zitkovic.e2b35ad9",
                source_local_id=locator,
                source_locator=locator,
                source_sha256=digest,
                target_sha256=digest,
                translation_state="source_frozen",
                relationship="copies",
                rights_id="rights.zitkovic.donor.cc0-1.0",
                concept_ids=concepts,
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

    section_id = "unit.donor.zitkovic.markov-chain-simulation.section"
    exercise_id = "unit.donor.zitkovic.markov-gambler-ruin.exercise"
    solution_id = "unit.donor.zitkovic.markov-gambler-ruin.solution"
    program_id = "unit.donor.zitkovic.markov-gambler-ruin.program.1"
    common_concepts = [
        "concept.markov.process",
        "concept.markov.transition-kernel",
        "concept.monte-carlo",
    ]
    add_donor(section_id, "section", section_span, None, 1, common_concepts)
    add_donor(exercise_id, "exercise", exercise_span, section_id, 1, common_concepts)
    add_donor(solution_id, "solution", solution_span, section_id, 2, common_concepts)
    add_donor(program_id, "program", program_span, solution_id, 1, common_concepts)
    relations = [
        relation(
            "rel.contains.donor.markov-section.exercise",
            "contains",
            section_id,
            exercise_id,
            "complete exercise inside source/05-Markov-chains.Rmd L601-L666",
        ),
        relation(
            "rel.contains.donor.markov-section.solution",
            "contains",
            section_id,
            solution_id,
            "complete solution inside source/05-Markov-chains.Rmd L601-L666",
        ),
        relation(
            "rel.solves.donor.zitkovic.markov-gambler-ruin",
            "solves",
            solution_id,
            exercise_id,
            "Žitković source/05-Markov-chains.Rmd donor solution block",
        ),
        relation(
            "rel.contains.donor.markov-solution.program.1",
            "contains",
            solution_id,
            program_id,
            "R chunk inside the complete donor Markov solution block",
        ),
    ]
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


def markov_lab_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    data = require_file(LAB_MARKOV)
    text = data.decode("utf-8")
    expected_slice_hash = "dcabe361eaaacaa537966f2bf8809dd8eac52e28392edc78d8e289c8c9be2bd8"
    required_metadata = (
        'source_alias: "zitkovic-stochastic-book:source/05-Markov-chains.Rmd#L601-L666"',
        f'source_slice_sha256: "{expected_slice_hash}"',
        'donor_license: "CC0-1.0"',
        'adaptation_license: "CC-BY-4.0"',
    )
    if any(item not in text for item in required_metadata):
        raise RuntimeError("Markov lab donor metadata is missing or changed")
    blocks = fenced_div_spans(text)
    lab_id = "o009-lab-markov-gambler-ruin"
    if lab_id not in blocks:
        raise RuntimeError("Markov lab root block is missing")
    headings = heading_spans(text, blocks[lab_id])
    chunks = {name: span for name, span in r_chunk_spans(text) if name}
    chunk_label = "o009_lab_markov_gambler_ruin"
    if chunk_label not in chunks:
        raise RuntimeError("named target Markov R chunk is missing")
    donor, donor_relations, aliases, donor_hashes = markov_donor_components()
    entities = list(donor)
    relations = list(donor_relations)
    translations: list[dict[str, str]] = []
    corrections: list[dict[str, str]] = []
    lab_path = "labs/02-simulasi-rantai-markov.Rmd"
    adaptation_rights = "rights.o009.markov.indonesian-adaptation.cc-by-4.0"
    original_rights = "rights.o009.markov.original.cc-by-4.0"

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
        rights_id = original_rights if original else adaptation_rights
        payload: dict[str, Any] = {
            "unit_kind": kind,
            "body_extent": "complete",
            "line_start": line_number(text, span.start),
            "line_end": line_number(text, span.end - 1),
        }
        if not original:
            payload["component_rights_ids"] = [
                "rights.zitkovic.donor.cc0-1.0",
                adaptation_rights,
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
                source_local_id=(
                    stable_id if target_local_id == "use-stable-id" else target_local_id
                ),
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
                concept_ids=concepts
                or ["concept.markov.process", "concept.markov.transition-kernel"],
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
                    "target_rights_id": adaptation_rights,
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
            order=3,
            path=lab_path,
            resource_id="resource.zitkovic.stochastic-book",
            edition_id="edition.zitkovic.e2b35ad9",
            source_local_id=lab_id,
            source_locator="source/05-Markov-chains.Rmd#L601-L666",
            source_sha256=expected_slice_hash,
            target_sha256=span_hash(root_span),
            locale="id-ID",
            translation_state="translated",
            relationship="adapts",
            rights_id=adaptation_rights,
            concept_ids=[
                "concept.markov.process",
                "concept.markov.transition-kernel",
                "concept.markov.harmonic-function",
                "concept.monte-carlo",
            ],
            payload={
                "unit_kind": "lab",
                "runtime": "R-4.6.1/base",
                "body_extent": "complete",
                "component_rights_ids": [
                    "rights.zitkovic.donor.cc0-1.0",
                    adaptation_rights,
                    original_rights,
                ],
            },
        )
    )
    aliases.append(
        {
            "alias_id": "alias.target.o009-lab-markov-gambler-ruin",
            "namespace": "o009-source-id",
            "alias": lab_id,
            "canonical_id": lab_id,
            "evidence": f"{lab_path}#{lab_id}",
            "status": "active",
        }
    )

    experiment_id = "o009-lab-markov-gambler-ruin-experiment"
    mastery_id = "o009-mastery-markov-gambler-ruin"
    donor_section = "unit.donor.zitkovic.markov-chain-simulation.section"
    common_concepts = [
        "concept.markov.process",
        "concept.markov.transition-kernel",
        "concept.monte-carlo",
    ]
    add_target(
        experiment_id,
        headings[experiment_id],
        parent_id=lab_id,
        order=1,
        kind="section",
        original=False,
        source_id=donor_section,
        source_hash=donor_hashes[donor_section],
        concepts=common_concepts,
    )
    target_exercise = "o009-exercise-markov-gambler-ruin-estimation"
    donor_exercise = "unit.donor.zitkovic.markov-gambler-ruin.exercise"
    add_target(
        target_exercise,
        blocks[target_exercise],
        parent_id=experiment_id,
        order=1,
        kind="exercise",
        original=False,
        source_id=donor_exercise,
        source_hash=donor_hashes[donor_exercise],
        concepts=common_concepts,
    )
    solution_span = Span(
        blocks[target_exercise].end,
        headings[mastery_id].start,
        blocks[target_exercise].end,
        headings[mastery_id].start,
    )
    target_solution = "o009-solution-markov-gambler-ruin-estimation"
    donor_solution = "unit.donor.zitkovic.markov-gambler-ruin.solution"
    add_target(
        target_solution,
        solution_span,
        parent_id=experiment_id,
        order=2,
        kind="solution",
        original=False,
        source_id=donor_solution,
        source_hash=donor_hashes[donor_solution],
        concepts=common_concepts,
        target_local_id=None,
        alias_namespace="backend-derived-id",
        alias_evidence=(
            f"{lab_path}:L{line_number(text, solution_span.start)}-"
            f"L{line_number(text, solution_span.end - 1)}"
        ),
    )
    target_program = "o009-program-markov-gambler-ruin"
    donor_program = "unit.donor.zitkovic.markov-gambler-ruin.program.1"
    program_span = chunks[chunk_label]
    add_target(
        target_program,
        program_span,
        parent_id=target_solution,
        order=1,
        kind="program",
        original=False,
        source_id=donor_program,
        source_hash=donor_hashes[donor_program],
        concepts=common_concepts,
        target_local_id=chunk_label,
        alias_namespace="r-chunk-label",
        alias_value=chunk_label,
        alias_evidence=f"{lab_path}:chunk:{chunk_label}",
    )
    relations.append(
        relation(
            "rel.solves.target.markov-gambler-ruin-estimation",
            "solves",
            target_solution,
            target_exercise,
            "complete adapted Markov-chain solution body",
        )
    )

    add_target(
        mastery_id,
        headings[mastery_id],
        parent_id=lab_id,
        order=2,
        kind="original-addition",
        original=True,
        concepts=["concept.markov.harmonic-function", "concept.markov.transition-kernel"],
    )
    nested_original = [
        ("o009-exercise-markov-gambler-ruin-mastery", "exercise"),
        ("o009-hint-markov-gambler-ruin-mastery-1", "hint"),
        ("o009-hint-markov-gambler-ruin-mastery-2", "hint"),
        ("o009-hint-markov-gambler-ruin-mastery-3", "hint"),
        ("o009-answer-markov-gambler-ruin-mastery", "answer"),
        ("o009-solution-markov-gambler-ruin-mastery", "solution"),
    ]
    for order, (stable_id, kind) in enumerate(nested_original, start=1):
        add_target(
            stable_id,
            blocks[stable_id],
            parent_id=mastery_id,
            order=order,
            kind=kind,
            original=True,
            concepts=["concept.markov.harmonic-function", "concept.markov.transition-kernel"],
        )

    mastery_exercise = "o009-exercise-markov-gambler-ruin-mastery"
    relations.extend(
        [
            relation(
                "rel.depends.lab-markov-gambler-ruin.theory-markov-general",
                "depends-on",
                lab_id,
                "unit.o009.random.markov.general",
                "matched_theory_id in Rmd metadata",
            ),
            relation(
                "rel.hints.markov-mastery.1",
                "hints",
                "o009-hint-markov-gambler-ruin-mastery-1",
                mastery_exercise,
                "explicit Markov mastery sequence",
            ),
            relation(
                "rel.hints.markov-mastery.2",
                "hints",
                "o009-hint-markov-gambler-ruin-mastery-2",
                mastery_exercise,
                "explicit Markov mastery sequence",
            ),
            relation(
                "rel.hints.markov-mastery.3",
                "hints",
                "o009-hint-markov-gambler-ruin-mastery-3",
                mastery_exercise,
                "explicit Markov mastery sequence",
            ),
            relation(
                "rel.answers.markov-mastery",
                "answers",
                "o009-answer-markov-gambler-ruin-mastery",
                mastery_exercise,
                "explicit Markov mastery sequence",
            ),
            relation(
                "rel.solves.markov-mastery",
                "solves",
                "o009-solution-markov-gambler-ruin-mastery",
                mastery_exercise,
                "explicit Markov mastery sequence",
            ),
            relation(
                "rel.teaches.markov-experiment.simulation",
                "teaches",
                experiment_id,
                "outcome.o009.simulate-absorbing-markov-chain",
                "absorbing-chain Monte Carlo experiment",
            ),
            relation(
                "rel.teaches.markov-experiment.kernels",
                "teaches",
                experiment_id,
                "outcome.o009.construct-markov-kernels",
                "transition-matrix construction and propagation",
            ),
            relation(
                "rel.teaches.markov-mastery.harmonic",
                "teaches",
                mastery_id,
                "outcome.o009.simulate-absorbing-markov-chain",
                "harmonic exact comparator for the simulation",
            ),
            relation(
                "rel.assesses.markov-estimation",
                "assesses",
                target_exercise,
                "outcome.o009.simulate-absorbing-markov-chain",
                "absorbing-chain estimation prompt",
            ),
            relation(
                "rel.assesses.markov-mastery.kernels",
                "assesses",
                mastery_exercise,
                "outcome.o009.construct-markov-kernels",
                "first-step harmonic system",
            ),
            relation(
                "rel.precedes.markov-theory.lab",
                "precedes",
                "unit.o009.random.markov.general",
                lab_id,
                "theory-to-lab learning sequence",
            ),
            relation(
                "rel.precedes.markov-experiment.mastery",
                "precedes",
                experiment_id,
                mastery_id,
                "Markov lab document order",
            ),
        ]
    )
    corrections.extend(
        [
            {
                "correction_id": "correction.o009.markov.program.deterministic-output",
                "change_kind": "deterministic-output",
                "source_id": donor_program,
                "target_id": target_program,
                "description": (
                    "Add an explicit seed, preserve the absorbing-chain simulation, "
                    "and emit a canonical CSV table with finite-horizon and harmonic exact comparators."
                ),
                "evidence": (
                    "source/labs/02-simulasi-rantai-markov.Rmd"
                    "#o009_lab_markov_gambler_ruin"
                ),
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.markov.mastery.original-addition",
                "change_kind": "original-addition",
                "source_id": lab_id,
                "target_id": mastery_id,
                "description": (
                    "Add a separately licensed mastery sequence deriving the exact "
                    "gambler's-ruin probability from harmonic first-step equations."
                ),
                "evidence": (
                    "source/labs/02-simulasi-rantai-markov.Rmd"
                    "#o009-mastery-markov-gambler-ruin"
                ),
                "status": "accepted",
            },
        ]
    )

    segments: list[dict[str, Any]] = []
    body = text[root_span.content_start : root_span.content_end]
    body_without_code = re.sub(
        r"^```.*?^```\s*$", "", body, flags=re.MULTILINE | re.DOTALL
    )
    original_offset = text.index("## Tambahan asli", root_span.content_start)
    for match in re.finditer(
        r"(?:^|\n\s*\n)(.+?)(?=\n\s*\n|\Z)", body_without_code, re.DOTALL
    ):
        paragraph = match.group(1).strip()
        if not paragraph or paragraph.startswith(":::"):
            continue
        global_offset = root_span.content_start + body.find(paragraph)
        original = global_offset >= original_offset or "Tambahan asli" in paragraph
        segments.append(
            record(
                "segment",
                f"segment.o009.lab.markov-gambler-ruin.{len(segments) + 1:04d}",
                parent_id=mastery_id if original else lab_id,
                order=len(segments) + 1,
                path=lab_path,
                source_locator=(
                    "local-original"
                    if original
                    else "source/05-Markov-chains.Rmd#L601-L666"
                ),
                target_sha256=sha256(paragraph.encode("utf-8")),
                locale="id-ID",
                translation_state="authored" if original else "translated",
                relationship="authored" if original else "adapts",
                rights_id=original_rights if original else adaptation_rights,
                concept_ids=(
                    ["concept.markov.harmonic-function"]
                    if original
                    else ["concept.markov.process", "concept.markov.transition-kernel"]
                ),
                payload={
                    "target_text": paragraph,
                    "component_rights_ids": (
                        [original_rights]
                        if original
                        else ["rights.zitkovic.donor.cc0-1.0", adaptation_rights]
                    ),
                },
            )
        )
    return entities, segments, relations, aliases, translations, corrections


def convergence_modes_lab_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    """Export the first wholly original deterministic domain lab."""
    data = require_file(LAB_CONVERGENCE_MODES)
    text = data.decode("utf-8")
    required_metadata = (
        'lab_id: "o009-lab-convergence-modes"',
        'prerequisite_id: "resource.o006.c140.shared"',
        'source_alias: "original-synthesis: convergence-modes-and-o006-comparison"',
        'source_slice_sha256: "not-applicable-original"',
        'donor_license: "none"',
        'adaptation_license: "CC-BY-4.0"',
        'model: "OpenAI Codex gpt-5.6-sol, Ultra."',
    )
    if any(witness not in text for witness in required_metadata):
        raise RuntimeError("convergence-modes lab metadata is missing or changed")
    original_lab_rights_witness(text)
    blocks = fenced_div_spans(text)
    lab_id = "o009-lab-convergence-modes"
    if lab_id not in blocks:
        raise RuntimeError("convergence-modes lab root block is missing")
    headings = heading_spans(text, blocks[lab_id])
    chunks = {name: span for name, span in r_chunk_spans(text) if name}
    chunk_label = "o009_lab_convergence_modes"
    if chunk_label not in chunks:
        raise RuntimeError("convergence-modes executable R chunk is missing")

    lab_path = "labs/03-konvergensi-mode-dan-lln-clt.Rmd"
    rights_id = "rights.o009.lab.convergence-modes.cc-by-4.0"
    common_concepts = [
        "concept.probability.almost-sure-convergence",
        "concept.probability.convergence-in-probability",
        "concept.probability.convergence-in-distribution",
        "concept.probability.lp-convergence",
        "concept.probability.weak-law",
        "concept.probability.central-limit-theorem",
    ]
    entities: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    relations: list[dict[str, str]] = []
    aliases: list[dict[str, str]] = []
    translations: list[dict[str, str]] = []
    corrections: list[dict[str, str]] = []

    def span_hash(span: Span) -> str:
        return sha256(text[span.start : span.end].encode("utf-8"))

    def add_unit(
        stable_id: str,
        span: Span,
        *,
        parent_id: str,
        order: int,
        kind: str,
        concepts: list[str] | None = None,
        source_local_id: str | None = "use-stable-id",
        alias_namespace: str = "o009-source-id",
        alias_value: str | None = None,
    ) -> None:
        line_locator = (
            "source/labs/03-konvergensi-mode-dan-lln-clt.Rmd:"
            f"L{line_number(text, span.start)}-L{line_number(text, span.end - 1)}"
        )
        if source_local_id is None:
            source_locator = line_locator
        elif alias_namespace == "r-chunk-label":
            source_locator = (
                f"source/{lab_path}:chunk:{alias_value or source_local_id}"
            )
        else:
            source_locator = f"source/{lab_path}#{stable_id}"
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=parent_id,
                order=order,
                path=lab_path,
                source_local_id=(
                    stable_id if source_local_id == "use-stable-id" else source_local_id
                ),
                source_locator=source_locator,
                source_sha256=span_hash(span),
                target_sha256=span_hash(span),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=rights_id,
                concept_ids=concepts or common_concepts,
                payload={
                    "unit_kind": kind,
                    "body_extent": "complete",
                    "line_start": line_number(text, span.start),
                    "line_end": line_number(text, span.end - 1),
                    "runtime": "R-4.6.1/base" if kind in {"lab", "program"} else None,
                },
            )
        )
        aliases.append(
            {
                "alias_id": f"alias.target.{stable_id}",
                "namespace": alias_namespace,
                "alias": alias_value or stable_id,
                "canonical_id": stable_id,
                "evidence": (
                    f"source/{lab_path}:chunk:{alias_value}"
                    if alias_namespace == "r-chunk-label"
                    else line_locator
                    if source_local_id is None
                    else f"source/{lab_path}#{stable_id}"
                ),
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

    root_span = blocks[lab_id]
    add_unit(
        lab_id,
        root_span,
        parent_id="course.o009.d30",
        order=4,
        kind="lab",
    )
    experiment_id = "o009-lab-convergence-modes-experiment"
    add_unit(
        experiment_id,
        headings[experiment_id],
        parent_id=lab_id,
        order=1,
        kind="section",
    )
    estimation_exercise = "o009-exercise-convergence-modes-estimation"
    add_unit(
        estimation_exercise,
        blocks[estimation_exercise],
        parent_id=experiment_id,
        order=1,
        kind="exercise",
    )
    mastery_heading = "o009-mastery-convergence-modes"
    estimation_solution_span = Span(
        blocks[estimation_exercise].end,
        headings[mastery_heading].start,
        blocks[estimation_exercise].end,
        headings[mastery_heading].start,
    )
    estimation_solution = "o009-solution-convergence-modes-estimation"
    add_unit(
        estimation_solution,
        estimation_solution_span,
        parent_id=experiment_id,
        order=2,
        kind="solution",
        source_local_id=None,
        alias_namespace="backend-derived-id",
    )
    program_id = "o009-program-convergence-modes"
    add_unit(
        program_id,
        chunks[chunk_label],
        parent_id=estimation_solution,
        order=1,
        kind="program",
        source_local_id=chunk_label,
        alias_namespace="r-chunk-label",
        alias_value=chunk_label,
    )
    result_id = "o009-results-convergence-modes"
    reader_path = ROOT / "build" / "site" / "labs" / (
        "03-konvergensi-mode-dan-lln-clt.html"
    )
    reader_soup = BeautifulSoup(require_file(reader_path).decode("utf-8"), "lxml")
    result_table = reader_soup.find("table", id=result_id)
    if result_table is None or len(result_table.find_all("tr")) != 6:
        raise RuntimeError("convergence-modes reader result table is missing or incomplete")
    entities.append(
        record(
            "unit",
            result_id,
            parent_id=program_id,
            order=1,
            path="labs/03-konvergensi-mode-dan-lln-clt.html",
            source_local_id=chunk_label,
            source_locator=f"source/{lab_path}:chunk:{chunk_label}",
            source_sha256=span_hash(chunks[chunk_label]),
            target_sha256=sha256(str(result_table).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=rights_id,
            concept_ids=common_concepts,
            payload={
                "unit_kind": "result-table",
                "body_extent": "complete-reader-table",
                "generated_from": chunk_label,
                "row_count_including_header": 6,
                "runtime": "R-4.6.1/base",
            },
        )
    )
    aliases.extend(
        [
            {
                "alias_id": "alias.reader.o009-results-convergence-modes",
                "namespace": "o009-source-id",
                "alias": result_id,
                "canonical_id": result_id,
                "evidence": (
                    "build/site/labs/03-konvergensi-mode-dan-lln-clt.html"
                    f"#{result_id}"
                ),
                "status": "active",
            },
            {
                "alias_id": "alias.frontmatter.o009-unit-convergence-modes",
                "namespace": "o009-source-id",
                "alias": "o009-unit-convergence-modes",
                "canonical_id": lab_id,
                "evidence": f"source/{lab_path}:authoring.unit_id",
                "status": "active",
            },
            {
                "alias_id": "alias.frontmatter.o009-theory-random-prob-convergence",
                "namespace": "o009-source-id",
                "alias": "o009-theory-random-prob-convergence",
                "canonical_id": "unit.o009.random.prob.convergence",
                "evidence": f"source/{lab_path}:authoring.matched_theory_id",
                "status": "active",
            },
        ]
    )
    relations.append(
        relation(
            "rel.contains.convergence-modes.program.result-table",
            "contains",
            program_id,
            result_id,
            "the deterministic R chunk emits the exact five-row reader table",
        )
    )
    add_unit(
        mastery_heading,
        headings[mastery_heading],
        parent_id=lab_id,
        order=2,
        kind="mastery-section",
    )
    mastery_sequence = "o009-mastery-convergence-modes-sequence"
    add_unit(
        mastery_sequence,
        blocks[mastery_sequence],
        parent_id=mastery_heading,
        order=1,
        kind="mastery-sequence",
    )
    mastery_children = (
        ("o009-exercise-convergence-modes-mastery", "exercise"),
        ("o009-hint-convergence-modes-1", "hint"),
        ("o009-hint-convergence-modes-2", "hint"),
        ("o009-answer-convergence-modes", "answer"),
        ("o009-solution-convergence-modes", "solution"),
    )
    for order, (stable_id, kind) in enumerate(mastery_children, start=1):
        add_unit(
            stable_id,
            blocks[stable_id],
            parent_id=mastery_sequence,
            order=order,
            kind=kind,
        )

    relations.extend(
        [
            relation(
                "rel.depends-on.convergence-modes.prob-convergence",
                "depends-on",
                lab_id,
                "unit.o009.random.prob.convergence",
                "matched measure-theoretic convergence theory",
            ),
            relation(
                "rel.depends-on.convergence-modes.dist-convergence",
                "depends-on",
                lab_id,
                "unit.o009.random.dist.convergence",
                "matched distributional-convergence theory",
            ),
            relation(
                "rel.depends-on.convergence-modes.uniform-integrability",
                "depends-on",
                lab_id,
                "unit.o009.random.expect.uniform",
                "rare-spike failure case distinguishes probability and L1 convergence",
            ),
            relation(
                "rel.depends-on.convergence-modes.o006",
                "depends-on",
                lab_id,
                "resource.o006.c140.shared",
                "LLN/CLT comparison uses the external O006 prerequisite without copying its bytes",
            ),
            relation(
                "rel.executes.convergence-modes.program",
                "executes",
                lab_id,
                program_id,
                "the pinned base-R program emits the canonical five-row diagnostic table",
            ),
            relation(
                "rel.solves.convergence-modes.estimation",
                "solves",
                estimation_solution,
                estimation_exercise,
                "complete code, table, tolerance, and interpretation body",
            ),
            relation(
                "rel.hints.convergence-modes.1",
                "hints",
                "o009-hint-convergence-modes-1",
                "o009-exercise-convergence-modes-mastery",
                "first progressive hint",
            ),
            relation(
                "rel.hints.convergence-modes.2",
                "hints",
                "o009-hint-convergence-modes-2",
                "o009-exercise-convergence-modes-mastery",
                "second progressive hint",
            ),
            relation(
                "rel.answers.convergence-modes",
                "answers",
                "o009-answer-convergence-modes",
                "o009-exercise-convergence-modes-mastery",
                "concise answer",
            ),
            relation(
                "rel.solves.convergence-modes",
                "solves",
                "o009-solution-convergence-modes",
                "o009-exercise-convergence-modes-mastery",
                "complete worked solution",
            ),
            relation(
                "rel.teaches.convergence-modes",
                "teaches",
                lab_id,
                "outcome.o009.distinguish-convergence-modes",
                "proof and deterministic diagnostics across convergence modes",
            ),
            relation(
                "rel.assesses.convergence-modes",
                "assesses",
                "o009-exercise-convergence-modes-mastery",
                "outcome.o009.distinguish-convergence-modes",
                "rare-spike counterexample mastery sequence",
            ),
            relation(
                "rel.precedes.convergence-theory.convergence-modes-lab",
                "precedes",
                "unit.o009.random.prob.convergence",
                lab_id,
                "theory before domain-specific lab",
            ),
        ]
    )
    corrections.append(
        {
            "correction_id": "correction.o009.original.lab.convergence-modes",
            "change_kind": "original-addition",
            "source_id": "course.o009.d30",
            "target_id": lab_id,
            "description": (
                "Add the bounded deterministic convergence-mode/O006 comparison lab "
                "with a rare-spike failure case and one complete mastery sequence."
            ),
            "evidence": (
                "source/labs/03-konvergensi-mode-dan-lln-clt.Rmd; "
                "build/site/labs/03-konvergensi-mode-dan-lln-clt.html"
            ),
            "status": "accepted",
        }
    )

    body = text[root_span.content_start : root_span.content_end]
    body_without_code = re.sub(
        r"^```.*?^```\s*$", "", body, flags=re.MULTILINE | re.DOTALL
    )
    for match in re.finditer(
        r"(?:^|\n\s*\n)(.+?)(?=\n\s*\n|\Z)",
        body_without_code,
        re.DOTALL,
    ):
        paragraph = match.group(1).strip()
        if not paragraph or paragraph.startswith(":::"):
            continue
        segments.append(
            record(
                "segment",
                f"segment.o009.lab.convergence-modes.{len(segments) + 1:04d}",
                parent_id=lab_id,
                order=len(segments) + 1,
                path=lab_path,
                source_locator="local-original",
                source_sha256=sha256(paragraph.encode("utf-8")),
                target_sha256=sha256(paragraph.encode("utf-8")),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=rights_id,
                concept_ids=common_concepts,
                payload={
                    "target_text": paragraph,
                    "component_rights_ids": [rights_id],
                },
            )
        )
    return entities, segments, relations, aliases, translations, corrections


def conditional_martingale_lab_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    """Export the wholly original conditional-expectation/martingale lab."""
    data = require_file(LAB_CONDITIONAL_MARTINGALE)
    text = data.decode("utf-8")
    required_metadata = (
        'unit_id: "o009-unit-conditional-martingale-lab"',
        'lab_id: "o009-lab-conditional-martingale"',
        'matched_theory_id: "o009-theory-random-conditional-martingale"',
        (
            'source_alias: "Random:expect/Conditional2.html;prob/Stop.html;'
            'martingales/Properties.html;martingales/Stop.html"'
        ),
        (
            'source_relation: "original diagnostic informed by the cited theory '
            'pages; no source HTML bytes are copied"'
        ),
        'adaptation_license: "CC-BY-4.0"',
        'model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."',
    )
    if any(witness not in text for witness in required_metadata):
        raise RuntimeError(
            "conditional-martingale lab metadata is missing or changed"
        )
    conditional_martingale_lab_rights_witness(text)
    blocks = fenced_div_spans(text)
    lab_id = "o009-lab-conditional-martingale"
    if lab_id not in blocks:
        raise RuntimeError("conditional-martingale lab root block is missing")
    root_span = blocks[lab_id]
    headings = heading_spans(text, root_span)
    chunks = {name: span for name, span in r_chunk_spans(text) if name}
    chunk_label = "o009_lab_conditional_martingale"
    if chunk_label not in chunks:
        raise RuntimeError(
            "conditional-martingale executable R chunk is missing"
        )

    lab_path = "labs/04-nilai-harapan-bersyarat-martingal.Rmd"
    rights_id = "rights.o009.lab.conditional-martingale.cc-by-4.0"
    common_concepts = [
        "concept.conditional.expectation",
        "concept.stochastic.filtration",
        "concept.martingale",
        "concept.stochastic.stopping-time",
        "concept.stochastic.stopped-process",
        "concept.martingale.optional-stopping",
        "concept.expectation.uniform-integrability",
        "concept.stochastic.random-walk",
    ]
    entities: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    relations: list[dict[str, str]] = []
    aliases: list[dict[str, str]] = []
    translations: list[dict[str, str]] = []
    corrections: list[dict[str, str]] = []

    def span_hash(span: Span) -> str:
        return sha256(text[span.start : span.end].encode("utf-8"))

    def add_unit(
        stable_id: str,
        span: Span,
        *,
        parent_id: str,
        order: int,
        kind: str,
        source_local_id: str | None = "use-stable-id",
        alias_namespace: str = "o009-source-id",
        alias_value: str | None = None,
    ) -> None:
        line_locator = (
            "source/labs/04-nilai-harapan-bersyarat-martingal.Rmd:"
            f"L{line_number(text, span.start)}-L{line_number(text, span.end - 1)}"
        )
        if source_local_id is None:
            source_locator = line_locator
        elif alias_namespace == "r-chunk-label":
            source_locator = (
                f"source/{lab_path}:chunk:{alias_value or source_local_id}"
            )
        else:
            source_locator = f"source/{lab_path}#{stable_id}"
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=parent_id,
                order=order,
                path=lab_path,
                source_local_id=(
                    stable_id
                    if source_local_id == "use-stable-id"
                    else source_local_id
                ),
                source_locator=source_locator,
                source_sha256=span_hash(span),
                target_sha256=span_hash(span),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=rights_id,
                concept_ids=common_concepts,
                payload={
                    "unit_kind": kind,
                    "body_extent": "complete",
                    "line_start": line_number(text, span.start),
                    "line_end": line_number(text, span.end - 1),
                    "runtime": (
                        "R-4.6.1/base"
                        if kind in {"lab", "program"}
                        else None
                    ),
                },
            )
        )
        aliases.append(
            {
                "alias_id": f"alias.target.{stable_id}",
                "namespace": alias_namespace,
                "alias": alias_value or stable_id,
                "canonical_id": stable_id,
                "evidence": (
                    f"source/{lab_path}:chunk:{alias_value}"
                    if alias_namespace == "r-chunk-label"
                    else line_locator
                    if source_local_id is None
                    else f"source/{lab_path}#{stable_id}"
                ),
                "status": "active",
            }
        )
        relations.append(
            relation(
                f"rel.contains.{parent_id}.{stable_id}",
                "contains",
                parent_id,
                stable_id,
                (
                    f"{lab_path}:L{line_number(text, span.start)}-"
                    f"L{line_number(text, span.end - 1)}"
                ),
            )
        )

    add_unit(
        lab_id,
        root_span,
        parent_id="course.o009.d30",
        order=5,
        kind="lab",
    )
    goals_id = "o009-conditional-martingale-goals"
    audit_id = "o009-conditional-expectation-audit"
    optional_id = "o009-optional-stopping-diagnostic"
    add_unit(
        goals_id,
        headings[goals_id],
        parent_id=lab_id,
        order=1,
        kind="section",
    )
    add_unit(
        audit_id,
        headings[audit_id],
        parent_id=lab_id,
        order=2,
        kind="section",
    )
    exercise_id = "o009-exercise-conditional-martingale-audit"
    add_unit(
        exercise_id,
        blocks[exercise_id],
        parent_id=audit_id,
        order=1,
        kind="exercise",
    )
    program_id = "o009-program-conditional-martingale"
    add_unit(
        program_id,
        chunks[chunk_label],
        parent_id=audit_id,
        order=2,
        kind="program",
        source_local_id=chunk_label,
        alias_namespace="r-chunk-label",
        alias_value=chunk_label,
    )
    result_id = "o009-results-conditional-martingale"
    reader_path = (
        ROOT
        / "build"
        / "site"
        / "labs"
        / "04-nilai-harapan-bersyarat-martingal.html"
    )
    reader_soup = BeautifulSoup(
        require_file(reader_path).decode("utf-8"), "lxml"
    )
    result_table = reader_soup.find("table", id=result_id)
    if result_table is None or len(result_table.find_all("tr")) != 2:
        raise RuntimeError(
            "conditional-martingale reader result table is missing or incomplete"
        )
    entities.append(
        record(
            "unit",
            result_id,
            parent_id=program_id,
            order=1,
            path="labs/04-nilai-harapan-bersyarat-martingal.html",
            source_local_id=chunk_label,
            source_locator=f"source/{lab_path}:chunk:{chunk_label}",
            source_sha256=span_hash(chunks[chunk_label]),
            target_sha256=sha256(str(result_table).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=rights_id,
            concept_ids=common_concepts,
            payload={
                "unit_kind": "result-table",
                "body_extent": "complete-reader-table",
                "generated_from": chunk_label,
                "row_count_including_header": 2,
                "column_count": 18,
                "runtime": "R-4.6.1/base",
            },
        )
    )
    aliases.extend(
        [
            {
                "alias_id": "alias.reader.o009-results-conditional-martingale",
                "namespace": "o009-source-id",
                "alias": result_id,
                "canonical_id": result_id,
                "evidence": (
                    "build/site/labs/04-nilai-harapan-bersyarat-martingal.html"
                    f"#{result_id}"
                ),
                "status": "active",
            },
            {
                "alias_id": (
                    "alias.frontmatter.o009-unit-conditional-martingale-lab"
                ),
                "namespace": "o009-source-id",
                "alias": "o009-unit-conditional-martingale-lab",
                "canonical_id": lab_id,
                "evidence": f"source/{lab_path}:authoring.unit_id",
                "status": "active",
            },
            {
                "alias_id": (
                    "alias.frontmatter.o009-theory-random-conditional-martingale"
                ),
                "namespace": "o009-source-id",
                "alias": "o009-theory-random-conditional-martingale",
                "canonical_id": "unit.o009.random.expect.conditional2",
                "evidence": f"source/{lab_path}:authoring.matched_theory_id",
                "status": "active",
            },
        ]
    )
    relations.append(
        relation(
            "rel.contains.conditional-martingale.program.result-table",
            "contains",
            program_id,
            result_id,
            "the deterministic R chunk emits the exact one-row reader table",
        )
    )
    add_unit(
        optional_id,
        headings[optional_id],
        parent_id=lab_id,
        order=3,
        kind="section",
    )
    optional_children = (
        ("o009-hint-conditional-martingale-audit-1", "hint"),
        ("o009-hint-conditional-martingale-audit-2", "hint"),
        ("o009-hint-conditional-martingale-audit-3", "hint"),
        ("o009-answer-conditional-martingale-audit", "answer"),
        ("o009-solution-conditional-martingale-audit", "solution"),
    )
    for order, (stable_id, kind) in enumerate(optional_children, start=1):
        add_unit(
            stable_id,
            blocks[stable_id],
            parent_id=optional_id,
            order=order,
            kind=kind,
        )

    theory_dependencies = (
        (
            "expect-conditional2",
            "unit.o009.random.expect.conditional2",
            "conditional expectation on finite filtration atoms",
        ),
        (
            "prob-stop",
            "unit.o009.random.prob.stop",
            "filtrations, stopping times, and stopped processes",
        ),
        (
            "martingales-properties",
            "unit.o009.random.martingales.properties",
            "martingale tower identities and stopped-process properties",
        ),
        (
            "martingales-stop",
            "unit.o009.random.martingales.stop",
            "optional-stopping hypotheses and counterexample boundary",
        ),
    )
    for slug, target_id, evidence in theory_dependencies:
        relations.append(
            relation(
                f"rel.depends-on.conditional-martingale.{slug}",
                "depends-on",
                lab_id,
                target_id,
                evidence,
            )
        )
    relations.extend(
        [
            relation(
                "rel.executes.conditional-martingale.program",
                "executes",
                lab_id,
                program_id,
                "the pinned base-R program emits the canonical exact-enumeration table",
            ),
            *(
                relation(
                    f"rel.hints.conditional-martingale.{index}",
                    "hints",
                    f"o009-hint-conditional-martingale-audit-{index}",
                    exercise_id,
                    f"progressive hint {index}",
                )
                for index in (1, 2, 3)
            ),
            relation(
                "rel.answers.conditional-martingale",
                "answers",
                "o009-answer-conditional-martingale-audit",
                exercise_id,
                "concise answer",
            ),
            relation(
                "rel.solves.conditional-martingale",
                "solves",
                "o009-solution-conditional-martingale-audit",
                exercise_id,
                "complete worked solution",
            ),
            relation(
                "rel.teaches.conditional-martingale.optional-stopping",
                "teaches",
                lab_id,
                "outcome.o009.check-optional-stopping-conditions",
                "finite filtration audit and bounded/unbounded stopping contrast",
            ),
            relation(
                "rel.assesses.conditional-martingale.optional-stopping",
                "assesses",
                exercise_id,
                "outcome.o009.check-optional-stopping-conditions",
                "the exercise requires explicit hypothesis and censoring checks",
            ),
        ]
    )
    corrections.append(
        {
            "correction_id": "correction.o009.original.lab.conditional-martingale",
            "change_kind": "original-addition",
            "source_id": "course.o009.d30",
            "target_id": lab_id,
            "description": (
                "Add the deterministic finite-space conditional-expectation, "
                "martingale, and optional-stopping diagnostic with a complete "
                "exercise/hint/answer/solution sequence."
            ),
            "evidence": (
                "source/labs/04-nilai-harapan-bersyarat-martingal.Rmd; "
                "build/site/labs/04-nilai-harapan-bersyarat-martingal.html"
            ),
            "status": "accepted",
        }
    )

    body = text[root_span.content_start : root_span.content_end]
    body_without_code = re.sub(
        r"^```.*?^```\s*$", "", body, flags=re.MULTILINE | re.DOTALL
    )
    for match in re.finditer(
        r"(?:^|\n\s*\n)(.+?)(?=\n\s*\n|\Z)",
        body_without_code,
        re.DOTALL,
    ):
        paragraph = match.group(1).strip()
        if not paragraph or paragraph.startswith(":::"):
            continue
        segments.append(
            record(
                "segment",
                (
                    "segment.o009.lab.conditional-martingale."
                    f"{len(segments) + 1:04d}"
                ),
                parent_id=lab_id,
                order=len(segments) + 1,
                path=lab_path,
                source_locator="local-original",
                source_sha256=sha256(paragraph.encode("utf-8")),
                target_sha256=sha256(paragraph.encode("utf-8")),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=rights_id,
                concept_ids=common_concepts,
                payload={
                    "target_text": paragraph,
                    "component_rights_ids": [rights_id],
                },
            )
        )
    return entities, segments, relations, aliases, translations, corrections


def brownian_diagnostics_lab_entities() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    """Export the wholly original Brownian/Donsker diagnostic laboratory."""
    data = require_file(LAB_BROWNIAN_DIAGNOSTICS)
    text = data.decode("utf-8")
    required_metadata = (
        'unit_id: "o009-unit-brownian-diagnostics-lab"',
        'lab_id: "o009-lab-brownian-diagnostics"',
        'matched_theory_id: "o009-theory-random-brown-standard"',
        'prerequisite_id: "resource.o006.c140.shared"',
        'source_alias: "Random:brown/Standard.html"',
        (
            'source_relation: "wholly original diagnostic informed by the cited '
            'Random theory page and the shared O006/C140 CLT prerequisite; no '
            'Random HTML or O006 bytes are copied"'
        ),
        'adaptation_license: "CC-BY-4.0"',
        'model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."',
    )
    if any(witness not in text for witness in required_metadata):
        raise RuntimeError("Brownian-diagnostics lab metadata is missing or changed")
    brownian_diagnostics_lab_rights_witness(text)
    blocks = fenced_div_spans(text)
    lab_id = "o009-lab-brownian-diagnostics"
    if lab_id not in blocks:
        raise RuntimeError("Brownian-diagnostics lab root block is missing")
    root_span = blocks[lab_id]
    headings = heading_spans(text, root_span)
    chunks = {name: span for name, span in r_chunk_spans(text) if name}
    chunk_label = "o009_lab_brownian_diagnostics"
    if chunk_label not in chunks:
        raise RuntimeError("Brownian-diagnostics executable R chunk is missing")

    lab_path = "labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.Rmd"
    rights_id = "rights.o009.lab.brownian-diagnostics.cc-by-4.0"
    common_concepts = [
        "concept.probability.central-limit-theorem",
        "concept.stochastic.random-walk",
        "concept.brownian.motion",
        "concept.brownian.standard-motion",
        "concept.brownian.gaussian-finite-dimensional-laws",
        "concept.brownian.self-similarity",
        "concept.brownian.path-irregularity",
        "concept.brownian.reflection-principle",
        "concept.brownian.running-maximum",
        "concept.brownian.hitting-time-law",
        "concept.stochastic.hitting-time",
    ]
    entities: list[dict[str, Any]] = []
    segments: list[dict[str, Any]] = []
    relations: list[dict[str, str]] = []
    aliases: list[dict[str, str]] = []
    translations: list[dict[str, str]] = []
    corrections: list[dict[str, str]] = []

    def span_hash(span: Span) -> str:
        return sha256(text[span.start : span.end].encode("utf-8"))

    def add_unit(
        stable_id: str,
        span: Span,
        *,
        parent_id: str,
        order: int,
        kind: str,
        source_local_id: str | None = "use-stable-id",
        alias_namespace: str = "o009-source-id",
        alias_value: str | None = None,
    ) -> None:
        line_locator = (
            "source/labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.Rmd:"
            f"L{line_number(text, span.start)}-L{line_number(text, span.end - 1)}"
        )
        if source_local_id is None:
            source_locator = line_locator
        elif alias_namespace == "r-chunk-label":
            source_locator = f"source/{lab_path}:chunk:{alias_value or source_local_id}"
        else:
            source_locator = f"source/{lab_path}#{stable_id}"
        entities.append(
            record(
                "unit",
                stable_id,
                parent_id=parent_id,
                order=order,
                path=lab_path,
                source_local_id=(
                    stable_id
                    if source_local_id == "use-stable-id"
                    else source_local_id
                ),
                source_locator=source_locator,
                source_sha256=span_hash(span),
                target_sha256=span_hash(span),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=rights_id,
                concept_ids=common_concepts,
                payload={
                    "unit_kind": kind,
                    "body_extent": "complete",
                    "line_start": line_number(text, span.start),
                    "line_end": line_number(text, span.end - 1),
                    "runtime": (
                        "R-4.6.1/base" if kind in {"lab", "program"} else None
                    ),
                },
            )
        )
        aliases.append(
            {
                "alias_id": f"alias.target.{stable_id}",
                "namespace": alias_namespace,
                "alias": alias_value or stable_id,
                "canonical_id": stable_id,
                "evidence": (
                    f"source/{lab_path}:chunk:{alias_value}"
                    if alias_namespace == "r-chunk-label"
                    else line_locator
                    if source_local_id is None
                    else f"source/{lab_path}#{stable_id}"
                ),
                "status": "active",
            }
        )
        relations.append(
            relation(
                f"rel.contains.{parent_id}.{stable_id}",
                "contains",
                parent_id,
                stable_id,
                (
                    f"{lab_path}:L{line_number(text, span.start)}-"
                    f"L{line_number(text, span.end - 1)}"
                ),
            )
        )

    add_unit(
        lab_id,
        root_span,
        parent_id="course.o009.d30",
        order=6,
        kind="lab",
    )
    goals_id = "o009-brownian-diagnostics-goals"
    partitions_id = "o009-brownian-partition-order"
    audit_id = "o009-brownian-exact-audit"
    for order, stable_id in enumerate(
        (goals_id, partitions_id, audit_id), start=1
    ):
        add_unit(
            stable_id,
            headings[stable_id],
            parent_id=lab_id,
            order=order,
            kind="section",
        )

    exercise_id = "o009-exercise-brownian-diagnostics"
    add_unit(
        exercise_id,
        blocks[exercise_id],
        parent_id=audit_id,
        order=1,
        kind="exercise",
    )
    program_id = "o009-program-brownian-diagnostics"
    add_unit(
        program_id,
        chunks[chunk_label],
        parent_id=audit_id,
        order=2,
        kind="program",
        source_local_id=chunk_label,
        alias_namespace="r-chunk-label",
        alias_value=chunk_label,
    )
    result_id = "o009-results-brownian-diagnostics"
    reader_path = (
        ROOT
        / "build"
        / "site"
        / "labs"
        / "05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
    )
    reader_soup = BeautifulSoup(require_file(reader_path).decode("utf-8"), "lxml")
    result_table = reader_soup.find("table", id=result_id)
    if (
        result_table is None
        or len(result_table.find_all("tr")) != 5
        or len(result_table.find_all("th")) != 15
    ):
        raise RuntimeError(
            "Brownian-diagnostics reader result table must be exactly 5 rows by 15 columns"
        )
    entities.append(
        record(
            "unit",
            result_id,
            parent_id=program_id,
            order=1,
            path=(
                "labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
            ),
            source_local_id=chunk_label,
            source_locator=f"source/{lab_path}:chunk:{chunk_label}",
            source_sha256=span_hash(chunks[chunk_label]),
            target_sha256=sha256(str(result_table).encode("utf-8")),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=rights_id,
            concept_ids=common_concepts,
            payload={
                "unit_kind": "result-table",
                "body_extent": "complete-reader-table",
                "generated_from": chunk_label,
                "row_count_including_header": 5,
                "column_count": 15,
                "runtime": "R-4.6.1/base",
            },
        )
    )
    aliases.extend(
        [
            {
                "alias_id": "alias.reader.o009-results-brownian-diagnostics",
                "namespace": "o009-source-id",
                "alias": result_id,
                "canonical_id": result_id,
                "evidence": (
                    "build/site/labs/"
                    "05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
                    f"#{result_id}"
                ),
                "status": "active",
            },
            {
                "alias_id": "alias.frontmatter.o009-unit-brownian-diagnostics-lab",
                "namespace": "o009-source-id",
                "alias": "o009-unit-brownian-diagnostics-lab",
                "canonical_id": lab_id,
                "evidence": f"source/{lab_path}:authoring.unit_id",
                "status": "active",
            },
            {
                "alias_id": "alias.frontmatter.o009-theory-random-brown-standard",
                "namespace": "o009-source-id",
                "alias": "o009-theory-random-brown-standard",
                "canonical_id": "unit.o009.random.brown.standard",
                "evidence": f"source/{lab_path}:authoring.matched_theory_id",
                "status": "active",
            },
        ]
    )
    relations.append(
        relation(
            "rel.contains.brownian-diagnostics.program.result-table",
            "contains",
            program_id,
            result_id,
            "the deterministic base-R chunk emits the exact four-row reader table",
        )
    )
    for order, (stable_id, kind) in enumerate(
        (
            ("o009-hint-brownian-diagnostics-1", "hint"),
            ("o009-hint-brownian-diagnostics-2", "hint"),
            ("o009-hint-brownian-diagnostics-3", "hint"),
            ("o009-answer-brownian-diagnostics", "answer"),
            ("o009-solution-brownian-diagnostics", "solution"),
        ),
        start=3,
    ):
        add_unit(
            stable_id,
            blocks[stable_id],
            parent_id=audit_id,
            order=order,
            kind=kind,
        )

    relations.extend(
        [
            relation(
                "rel.depends-on.brownian-diagnostics.random-standard",
                "depends-on",
                lab_id,
                "unit.o009.random.brown.standard",
                "the exact admitted Random Brownian theory page",
            ),
            relation(
                "rel.depends-on.brownian-diagnostics.o006",
                "depends-on",
                lab_id,
                "resource.o006.c140.shared",
                "the O006/C140 CLT is linked as a shared prerequisite without copied bytes",
            ),
            relation(
                "rel.executes.brownian-diagnostics.program",
                "executes",
                lab_id,
                program_id,
                "the pinned base-R program emits the exact endpoint, reflection, and variation audit",
            ),
            *(
                relation(
                    f"rel.hints.brownian-diagnostics.{index}",
                    "hints",
                    f"o009-hint-brownian-diagnostics-{index}",
                    exercise_id,
                    f"progressive hint {index}",
                )
                for index in (1, 2, 3)
            ),
            relation(
                "rel.answers.brownian-diagnostics",
                "answers",
                "o009-answer-brownian-diagnostics",
                exercise_id,
                "concise answer",
            ),
            relation(
                "rel.solves.brownian-diagnostics",
                "solves",
                "o009-solution-brownian-diagnostics",
                exercise_id,
                "complete worked solution",
            ),
            relation(
                "rel.teaches.brownian-diagnostics.fdd-path-law",
                "teaches",
                lab_id,
                "outcome.o009.audit-fdd-versus-path-law-convergence",
                "Donsker convergence is separated from finite-dimensional and pathwise claims",
            ),
            relation(
                "rel.teaches.brownian-diagnostics.scaling-irregularity",
                "teaches",
                partitions_id,
                "outcome.o009.analyze-brownian-scaling-irregularity",
                "natural-mesh and fixed-prelimit-refinement limits are explicitly distinguished",
            ),
            relation(
                "rel.teaches.brownian-diagnostics.reflection",
                "teaches",
                goals_id,
                "outcome.o009.apply-brownian-strong-markov-reflection",
                "the discrete reflection bijection is connected to the Brownian reflection limit",
            ),
            relation(
                "rel.teaches.brownian-diagnostics.hitting-maximum",
                "teaches",
                audit_id,
                "outcome.o009.derive-brownian-hitting-maximum-laws",
                "the exact random-walk maximum probability is compared with its Brownian limit",
            ),
            *(
                relation(
                    f"rel.assesses.brownian-diagnostics.{slug}",
                    "assesses",
                    exercise_id,
                    outcome_id,
                    "the four-part exercise directly audits this outcome",
                )
                for slug, outcome_id in (
                    (
                        "fdd-path-law",
                        "outcome.o009.audit-fdd-versus-path-law-convergence",
                    ),
                    (
                        "scaling-irregularity",
                        "outcome.o009.analyze-brownian-scaling-irregularity",
                    ),
                    (
                        "reflection",
                        "outcome.o009.apply-brownian-strong-markov-reflection",
                    ),
                    (
                        "hitting-maximum",
                        "outcome.o009.derive-brownian-hitting-maximum-laws",
                    ),
                )
            ),
        ]
    )
    corrections.append(
        {
            "correction_id": "correction.o009.original.lab.brownian-diagnostics",
            "change_kind": "original-addition",
            "source_id": "course.o009.d30",
            "target_id": lab_id,
            "description": (
                "Add the deterministic Brownian/Donsker diagnostic with exact "
                "endpoint and reflection probabilities, a quadratic/total-variation "
                "limit-order audit, and a complete exercise/hint/answer/solution sequence."
            ),
            "evidence": (
                "source/labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.Rmd; "
                "build/site/labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
            ),
            "status": "accepted",
        }
    )

    body = text[root_span.content_start : root_span.content_end]
    body_without_code = re.sub(
        r"^```.*?^```\s*$", "", body, flags=re.MULTILINE | re.DOTALL
    )
    for match in re.finditer(
        r"(?:^|\n\s*\n)(.+?)(?=\n\s*\n|\Z)",
        body_without_code,
        re.DOTALL,
    ):
        paragraph = match.group(1).strip()
        if (
            not paragraph
            or paragraph.startswith(":::")
            or paragraph.startswith("<!--")
        ):
            continue
        segments.append(
            record(
                "segment",
                f"segment.o009.lab.brownian-diagnostics.{len(segments) + 1:04d}",
                parent_id=lab_id,
                order=len(segments) + 1,
                path=lab_path,
                source_locator="local-original",
                source_sha256=sha256(paragraph.encode("utf-8")),
                target_sha256=sha256(paragraph.encode("utf-8")),
                locale="id-ID",
                translation_state="authored",
                relationship="authored",
                rights_id=rights_id,
                concept_ids=common_concepts,
                payload={
                    "target_text": paragraph,
                    "component_rights_ids": [rights_id],
                },
            )
        )
    if (
        len(entities),
        len(segments),
        len(relations),
        len(aliases),
        len(translations),
        len(corrections),
    ) != (12, 33, 28, 14, 0, 1):
        raise RuntimeError(
            "Brownian-diagnostics backend delta differs from the exact "
            "12/33/28/14/0/1 contract: "
            f"actual={len(entities)}/{len(segments)}/{len(relations)}/"
            f"{len(aliases)}/{len(translations)}/{len(corrections)}"
        )
    return entities, segments, relations, aliases, translations, corrections


def entities_by_id(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in records}


def two_state_app_entities() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    source_data = require_file(TWO_STATE_APP)
    target_data = require_file(BUILT_TWO_STATE_APP)
    if target_data != source_data:
        raise RuntimeError("built two-state app is not an exact copy of its authored source")
    document = BeautifulSoup(source_data.decode("utf-8"), "lxml")
    if document.html is None or document.html.get("lang") != "id-ID":
        raise RuntimeError("two-state app must declare Indonesian document language")
    if document.title is None or document.title.get_text(" ", strip=True) != "Simulator Rantai Markov Dua Keadaan":
        raise RuntimeError("two-state app title is missing or changed")
    provenance = document.find(id="two-state-provenance")
    license_link = provenance.find("a", rel=lambda value: value and "license" in value) if provenance else None
    if license_link is None or license_link.get("href") != "https://creativecommons.org/licenses/by/4.0/":
        raise RuntimeError("two-state app lacks its exact CC BY 4.0 self-witness")
    required_surface_ids = {
        "two-state-main",
        "two-state-controls",
        "two-state-run",
        "two-state-results",
        "two-state-copy-text",
        "two-state-provenance",
    }
    missing_surface_ids = sorted(
        surface_id for surface_id in required_surface_ids if document.find(id=surface_id) is None
    )
    if missing_surface_ids:
        raise RuntimeError(f"two-state app surface is incomplete: {missing_surface_ids}")

    app_id = "unit.o009.original.markov.two-state-simulator"
    rights_id = "rights.o009.two-state-app.cc-by-4.0"
    digest = sha256(source_data)
    entities = [
        record(
            "rights",
            rights_id,
            source_locator="source/apps/two-state.html#two-state-provenance",
            source_sha256=digest,
            locale="id-ID",
            translation_state="authored",
            payload={
                "license": "CC-BY-4.0",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "creator": "Codex at the user's direction",
                "scope": "complete original Indonesian two-state Markov-chain simulator",
                "witness_path": "source/apps/two-state.html#two-state-provenance",
            },
        ),
        record(
            "unit",
            app_id,
            parent_id="course.o009.d30",
            order=20,
            path="apps/two-state.html",
            source_local_id="two-state-main",
            source_locator="source/apps/two-state.html",
            source_sha256=digest,
            target_sha256=sha256(target_data),
            locale="id-ID",
            translation_state="authored",
            relationship="authored",
            rights_id=rights_id,
            concept_ids=[
                "concept.markov.transition-matrix",
                "concept.markov.invariant-distribution",
                "concept.markov.occupation-frequency",
                "concept.markov.limiting-distribution",
                "concept.markov.positive-recurrence",
                "concept.markov.period",
                "concept.markov.ergodic-chain",
            ],
            payload={
                "unit_kind": "program",
                "tool_kind": "interactive-simulator",
                "runtime": "offline-browser/JavaScript",
                "body_extent": "complete-file",
                "offline_capable": True,
                "deterministic_seeded": True,
                "title": "Simulator Rantai Markov Dua Keadaan",
            },
        ),
    ]
    relations = [
        relation(
            "rel.contains.course.o009.two-state-simulator",
            "contains",
            "course.o009.d30",
            app_id,
            "source/apps/two-state.html is an original course companion",
        ),
        relation(
            "rel.depends-on.two-state-simulator.markov-limiting",
            "depends-on",
            app_id,
            "unit.o009.random.markov.limiting",
            "the simulator operationalizes the two-state limiting-distribution analysis",
        ),
        relation(
            "rel.executes.markov-limiting.div-023.two-state-simulator",
            "executes",
            "unit.o009.random.markov.limiting.div-023",
            app_id,
            "markov/Limiting.html#div-023 launches apps/two-state.html",
        ),
        relation(
            "rel.assesses.two-state-simulator.markov-ergodic-periodic-limits",
            "assesses",
            app_id,
            "outcome.o009.analyze-markov-ergodic-periodic-limits",
            "the seeded simulation compares long-run occupation with the invariant distribution and exposes the period-two exception",
        ),
    ]
    return entities, relations


def asset_entities() -> list[dict[str, Any]]:
    paths = [
        ("asset.random.screen-css", AUTH_RANDOM / "static" / "Screen.css", "rights.random.dual-witness"),
        ("asset.random.basic-js", AUTH_RANDOM / "static" / "Basic.js", "rights.random.dual-witness"),
        (
            "asset.random.apps.core",
            AUTH_RANDOM / "static" / "apps" / "Apps.js",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.apps.distributions",
            AUTH_RANDOM / "static" / "apps" / "Distributions.js",
            "rights.random.dual-witness",
        ),
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
        (
            "asset.random.markov.recurrence.visits",
            AUTH_RANDOM / "static" / "markov" / "Visits.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.markov.recurrence.partition",
            AUTH_RANDOM / "static" / "markov" / "Partition.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.markov.recurrence.classes",
            AUTH_RANDOM / "static" / "markov" / "Classes.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.markov.recurrence.state-1",
            AUTH_RANDOM / "static" / "markov" / "State1.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.markov.recurrence.state-2",
            AUTH_RANDOM / "static" / "markov" / "State2.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.markov.recurrence.state-3",
            AUTH_RANDOM / "static" / "markov" / "State3.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.markov.periodicity.cyclic-classes",
            AUTH_RANDOM / "static" / "markov" / "CyclicClasses.png",
            "rights.random.dual-witness",
        ),
        (
            "asset.random.markov.periodicity.state-4",
            AUTH_RANDOM / "static" / "markov" / "State4.png",
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
        (
            "artifact.input.reproducible-build-timestamp",
            "input",
            ROOT / "00_control" / "REPRODUCIBLE_BUILD_TIMESTAMP_UTC.txt",
        ),
        ("artifact.input.terms", "input", TERMS),
        ("artifact.input.random-manifest", "authority-manifest", RANDOM_MANIFEST),
        ("artifact.input.random-receipt", "authority-receipt", RANDOM_RECEIPT),
        ("artifact.input.zitkovic-zip", "authority-archive", ZIT_ZIP),
        ("artifact.input.zitkovic-license", "rights-witness", ZIT_LICENSE),
        ("artifact.input.zitkovic-simulation", "authority-source", ZIT_SIMULATION),
        ("artifact.input.zitkovic-markov", "authority-source", ZIT_MARKOV),
        ("artifact.input.target-lab", "translation-source", LAB),
        ("artifact.input.target-lab-markov", "translation-source", LAB_MARKOV),
        (
            "artifact.input.target-lab-convergence-modes",
            "input",
            LAB_CONVERGENCE_MODES,
        ),
        (
            "artifact.input.target-lab-conditional-martingale",
            "input",
            LAB_CONDITIONAL_MARTINGALE,
        ),
        (
            "artifact.input.target-lab-brownian-diagnostics",
            "input",
            LAB_BROWNIAN_DIAGNOSTICS,
        ),
        (
            "artifact.input.original-bridge-01-source",
            "input",
            ORIGINAL_BRIDGE_SOURCE,
        ),
        (
            "artifact.input.original-bridge-01-reader",
            "input",
            ORIGINAL_BRIDGE_READER,
        ),
        (
            "artifact.input.original-bridge-01-mastery-ledger",
            "input",
            ORIGINAL_BRIDGE_MASTERY_LEDGER,
        ),
        (
            "artifact.input.original-bridge-02-source",
            "input",
            ORIGINAL_BRIDGE_02_SOURCE,
        ),
        (
            "artifact.input.original-bridge-02-reader",
            "input",
            ORIGINAL_BRIDGE_02_READER,
        ),
        (
            "artifact.input.original-bridge-02-mastery-ledger",
            "input",
            ORIGINAL_BRIDGE_02_MASTERY_LEDGER,
        ),
        (
            "artifact.input.original-bridge-03-source",
            "input",
            ORIGINAL_BRIDGE_03_SOURCE,
        ),
        (
            "artifact.input.original-bridge-03-reader",
            "input",
            ORIGINAL_BRIDGE_03_READER,
        ),
        (
            "artifact.input.original-bridge-03-mastery-ledger",
            "input",
            ORIGINAL_BRIDGE_03_MASTERY_LEDGER,
        ),
        (
            "artifact.input.original-bridge-04-source",
            "input",
            ORIGINAL_BRIDGE_04_SOURCE,
        ),
        (
            "artifact.input.original-bridge-04-reader",
            "input",
            ORIGINAL_BRIDGE_04_READER,
        ),
        (
            "artifact.input.original-bridge-04-mastery-ledger",
            "input",
            ORIGINAL_BRIDGE_04_MASTERY_LEDGER,
        ),
        ("artifact.input.original-two-state-app", "input", TWO_STATE_APP),
        (
            "artifact.input.original-brown-drift-offline-js",
            "input",
            BROWN_DRIFT_OFFLINE_APP,
        ),
        (
            "artifact.input.reader-brown-drift-offline-js",
            "input",
            BUILT_BROWN_DRIFT_OFFLINE_APP,
        ),
        (
            "artifact.input.original-brown-bridge-offline-js",
            "input",
            BROWN_BRIDGE_OFFLINE_APP,
        ),
        (
            "artifact.input.reader-brown-bridge-offline-js",
            "input",
            BUILT_BROWN_BRIDGE_OFFLINE_APP,
        ),
        (
            "artifact.input.original-brown-geometric-offline-js",
            "input",
            BROWN_GEOMETRIC_OFFLINE_APP,
        ),
        (
            "artifact.input.reader-brown-geometric-offline-js",
            "input",
            BUILT_BROWN_GEOMETRIC_OFFLINE_APP,
        ),
        ("artifact.input.quantecon-source-manifest", "authority-manifest", QUANTECON_ROOT / "SOURCE_MANIFEST.tsv"),
        ("artifact.input.quantecon-notebook-manifest", "authority-manifest", QUANTECON_ROOT / "NOTEBOOK_MANIFEST.tsv"),
        ("artifact.input.quantecon-source", "authority-source", QUANTECON_SOURCE),
        ("artifact.input.quantecon-notebook", "authority-source", QUANTECON_NOTEBOOK),
        ("artifact.input.quantecon-license", "rights-witness", QUANTECON_LICENSE),
        ("artifact.input.quantecon-component-manifest", "build-manifest", QUANTECON_MANIFEST),
        ("artifact.input.quantecon-component-receipt", "build-receipt", QUANTECON_RECEIPT),
        ("artifact.input.quantecon-target", "translation-source", ROOT / "source" / "quantecon" / "lectures" / "memoryless.md"),
        ("artifact.input.quantecon-html", "input", QUANTECON_HTML),
        ("artifact.input.quantecon-executed-notebook", "input", QUANTECON_COMPONENT / "notebooks" / "memoryless-executed.ipynb"),
        ("artifact.input.quantecon-figure-01", "authority-asset", QUANTECON_COMPONENT / "assets" / "memoryless-cell-03-figure-01.png"),
        ("artifact.input.quantecon-figure-02", "authority-asset", QUANTECON_COMPONENT / "assets" / "memoryless-cell-04-figure-01.png"),
        ("artifact.input.quantecon-figure-03", "authority-asset", QUANTECON_COMPONENT / "assets" / "memoryless-cell-05-figure-01.png"),
        ("artifact.input.quantecon-poisson-source", "authority-source", QUANTECON_POISSON_SOURCE),
        ("artifact.input.quantecon-poisson-notebook", "authority-source", QUANTECON_POISSON_NOTEBOOK),
        ("artifact.input.quantecon-poisson-component-manifest", "build-manifest", QUANTECON_POISSON_MANIFEST),
        ("artifact.input.quantecon-poisson-component-receipt", "build-receipt", QUANTECON_POISSON_RECEIPT),
        ("artifact.input.quantecon-poisson-target", "translation-source", ROOT / "source" / "quantecon" / "lectures" / "poisson.md"),
        ("artifact.input.quantecon-poisson-html", "input", QUANTECON_POISSON_HTML),
        ("artifact.input.quantecon-poisson-executed-notebook", "input", QUANTECON_POISSON_COMPONENT / "notebooks" / "poisson-executed.ipynb"),
        ("artifact.input.quantecon-poisson-figure-01", "authority-asset", QUANTECON_POISSON_COMPONENT / "assets" / "poisson-cell-03-figure-01.png"),
        ("artifact.input.quantecon-poisson-figure-02", "authority-asset", QUANTECON_POISSON_COMPONENT / "assets" / "poisson-cell-04-figure-01.png"),
        ("artifact.input.quantecon-poisson-figure-03", "authority-asset", QUANTECON_POISSON_COMPONENT / "assets" / "poisson-cell-05-figure-01.png"),
        ("artifact.input.quantecon-poisson-figure-04", "authority-asset", QUANTECON_POISSON_COMPONENT / "assets" / "poisson-cell-06-figure-01.png"),
        ("artifact.input.quantecon-poisson-figure-05", "authority-asset", QUANTECON_POISSON_COMPONENT / "assets" / "poisson-cell-07-figure-01.png"),
        ("artifact.input.quantecon-markov-prop-source", "authority-source", QUANTECON_MARKOV_PROP_SOURCE),
        ("artifact.input.quantecon-markov-prop-notebook", "authority-source", QUANTECON_MARKOV_PROP_NOTEBOOK),
        ("artifact.input.quantecon-markov-prop-component-manifest", "build-manifest", QUANTECON_MARKOV_PROP_MANIFEST),
        ("artifact.input.quantecon-markov-prop-component-receipt", "build-receipt", QUANTECON_MARKOV_PROP_RECEIPT),
        ("artifact.input.quantecon-markov-prop-target", "translation-source", ROOT / "source" / "quantecon" / "lectures" / "markov_prop.md"),
        ("artifact.input.quantecon-markov-prop-html", "input", QUANTECON_MARKOV_PROP_HTML),
        ("artifact.input.quantecon-markov-prop-executed-notebook", "input", QUANTECON_MARKOV_PROP_COMPONENT / "notebooks" / "markov_prop-executed.ipynb"),
        ("artifact.input.quantecon-markov-prop-figure-01", "authority-asset", QUANTECON_MARKOV_PROP_COMPONENT / "assets" / "markov_prop-cell-04-figure-01.png"),
        ("artifact.input.quantecon-markov-prop-figure-02", "authority-asset", QUANTECON_MARKOV_PROP_COMPONENT / "assets" / "markov_prop-cell-05-figure-01.png"),
        ("artifact.input.quantecon-kolmogorov-bwd-source", "authority-source", QUANTECON_KOLMOGOROV_BWD_SOURCE),
        ("artifact.input.quantecon-kolmogorov-bwd-notebook", "authority-source", QUANTECON_KOLMOGOROV_BWD_NOTEBOOK),
        ("artifact.input.quantecon-kolmogorov-bwd-component-manifest", "build-manifest", QUANTECON_KOLMOGOROV_BWD_MANIFEST),
        ("artifact.input.quantecon-kolmogorov-bwd-component-receipt", "build-receipt", QUANTECON_KOLMOGOROV_BWD_RECEIPT),
        ("artifact.input.quantecon-kolmogorov-bwd-target", "translation-source", ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_bwd.md"),
        ("artifact.input.quantecon-kolmogorov-bwd-html", "input", QUANTECON_KOLMOGOROV_BWD_HTML),
        ("artifact.input.quantecon-kolmogorov-bwd-executed-notebook", "input", QUANTECON_KOLMOGOROV_BWD_COMPONENT / "notebooks" / "kolmogorov_bwd-executed.ipynb"),
        ("artifact.input.quantecon-kolmogorov-bwd-figure-01", "authority-asset", QUANTECON_KOLMOGOROV_BWD_COMPONENT / "assets" / "kolmogorov_bwd-cell-05-figure-01.png"),
        ("artifact.input.quantecon-kolmogorov-bwd-figure-02", "authority-asset", QUANTECON_KOLMOGOROV_BWD_COMPONENT / "assets" / "kolmogorov_bwd-cell-06-figure-01.png"),
        ("artifact.input.quantecon-kolmogorov-fwd-source", "authority-source", QUANTECON_KOLMOGOROV_FWD_SOURCE),
        ("artifact.input.quantecon-kolmogorov-fwd-notebook", "authority-source", QUANTECON_KOLMOGOROV_FWD_NOTEBOOK),
        ("artifact.input.quantecon-kolmogorov-fwd-static-flow", "authority-asset", QUANTECON_KOLMOGOROV_FWD_STATIC_ASSET),
        ("artifact.input.quantecon-kolmogorov-fwd-component-manifest", "build-manifest", QUANTECON_KOLMOGOROV_FWD_MANIFEST),
        ("artifact.input.quantecon-kolmogorov-fwd-component-receipt", "build-receipt", QUANTECON_KOLMOGOROV_FWD_RECEIPT),
        ("artifact.input.quantecon-kolmogorov-fwd-numerical-qa", "input", QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA),
        ("artifact.input.quantecon-kolmogorov-fwd-target", "translation-source", ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_fwd.md"),
        ("artifact.input.quantecon-kolmogorov-fwd-html", "input", QUANTECON_KOLMOGOROV_FWD_HTML),
        ("artifact.input.quantecon-kolmogorov-fwd-executed-notebook", "input", QUANTECON_KOLMOGOROV_FWD_COMPONENT / "notebooks" / "kolmogorov_fwd-executed.ipynb"),
        ("artifact.input.quantecon-kolmogorov-fwd-source-figure", "input", QUANTECON_KOLMOGOROV_FWD_COMPONENT / "assets" / "kolmogorov_fwd-source-flow.png"),
        ("artifact.input.quantecon-kolmogorov-fwd-figure-01", "input", QUANTECON_KOLMOGOROV_FWD_COMPONENT / "assets" / "kolmogorov_fwd-cell-04-figure-01.png"),
        ("artifact.input.quantecon-kolmogorov-fwd-figure-02", "input", QUANTECON_KOLMOGOROV_FWD_COMPONENT / "assets" / "kolmogorov_fwd-cell-06-figure-01.png"),
        ("artifact.input.quantecon-kolmogorov-fwd-cell-04-data", "input", QUANTECON_KOLMOGOROV_FWD_COMPONENT / "assets" / "kolmogorov_fwd-cell-04-data.csv"),
        ("artifact.input.quantecon-kolmogorov-fwd-cell-06-data", "input", QUANTECON_KOLMOGOROV_FWD_COMPONENT / "assets" / "kolmogorov_fwd-cell-06-data.csv"),
        ("artifact.input.quantecon-generators-source", "authority-source", QUANTECON_GENERATORS_SOURCE),
        ("artifact.input.quantecon-generators-notebook", "authority-source", QUANTECON_GENERATORS_NOTEBOOK),
        ("artifact.input.quantecon-generators-component-manifest", "build-manifest", QUANTECON_GENERATORS_MANIFEST),
        ("artifact.input.quantecon-generators-component-receipt", "build-receipt", QUANTECON_GENERATORS_RECEIPT),
        ("artifact.input.quantecon-generators-target", "translation-source", ROOT / "source" / "quantecon" / "lectures" / "generators.md"),
        ("artifact.input.quantecon-generators-html", "input", QUANTECON_GENERATORS_HTML),
        ("artifact.input.quantecon-generators-executed-notebook", "input", QUANTECON_GENERATORS_COMPONENT / "notebooks" / "generators-executed.ipynb"),
        ("artifact.input.quantecon-generators-translation-audit", "input", QUANTECON_GENERATORS_TRANSLATION_AUDIT),
        ("artifact.input.quantecon-generators-math-audit", "input", QUANTECON_GENERATORS_MATH_AUDIT),
        ("artifact.input.quantecon-uc-mc-semigroups-source", "authority-source", QUANTECON_UC_MC_SEMIGROUPS_SOURCE),
        ("artifact.input.quantecon-uc-mc-semigroups-notebook", "authority-source", QUANTECON_UC_MC_SEMIGROUPS_NOTEBOOK),
        ("artifact.input.quantecon-uc-mc-semigroups-component-manifest", "build-manifest", QUANTECON_UC_MC_SEMIGROUPS_MANIFEST),
        ("artifact.input.quantecon-uc-mc-semigroups-component-receipt", "build-receipt", QUANTECON_UC_MC_SEMIGROUPS_RECEIPT),
        ("artifact.input.quantecon-uc-mc-semigroups-target", "translation-source", ROOT / "source" / "quantecon" / "lectures" / "uc_mc_semigroups.md"),
        ("artifact.input.quantecon-uc-mc-semigroups-html", "input", QUANTECON_UC_MC_SEMIGROUPS_HTML),
        ("artifact.input.quantecon-uc-mc-semigroups-executed-notebook", "input", QUANTECON_UC_MC_SEMIGROUPS_COMPONENT / "notebooks" / "uc_mc_semigroups-executed.ipynb"),
        ("artifact.input.quantecon-uc-mc-semigroups-translation-audit", "input", QUANTECON_UC_MC_SEMIGROUPS_TRANSLATION_AUDIT),
        ("artifact.input.quantecon-uc-mc-semigroups-math-audit", "input", QUANTECON_UC_MC_SEMIGROUPS_MATH_AUDIT),
        ("artifact.input.quantecon-uc-mc-semigroups-numerical-qa", "input", QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA),
        ("artifact.input.quantecon-ergodicity-source", "authority-source", QUANTECON_ERGODICITY_SOURCE),
        ("artifact.input.quantecon-ergodicity-notebook", "authority-source", QUANTECON_ERGODICITY_NOTEBOOK),
        ("artifact.input.quantecon-ergodicity-component-manifest", "build-manifest", QUANTECON_ERGODICITY_MANIFEST),
        ("artifact.input.quantecon-ergodicity-component-receipt", "build-receipt", QUANTECON_ERGODICITY_RECEIPT),
        ("artifact.input.quantecon-ergodicity-target", "translation-source", ROOT / "source" / "quantecon" / "lectures" / "ergodicity.md"),
        ("artifact.input.quantecon-ergodicity-html", "input", QUANTECON_ERGODICITY_HTML),
        ("artifact.input.quantecon-ergodicity-executed-notebook", "input", QUANTECON_ERGODICITY_COMPONENT / "notebooks" / "ergodicity-executed.ipynb"),
        ("artifact.input.quantecon-ergodicity-figure-01", "input", QUANTECON_ERGODICITY_COMPONENT / "assets" / "ergodicity-cell-04-figure-01.png"),
        ("artifact.input.quantecon-ergodicity-translation-audit", "input", QUANTECON_ERGODICITY_TRANSLATION_AUDIT),
        ("artifact.input.quantecon-ergodicity-math-audit", "input", QUANTECON_ERGODICITY_MATH_AUDIT),
        ("artifact.input.quantecon-ergodicity-numerical-qa", "input", QUANTECON_ERGODICITY_NUMERICAL_QA),
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
        *[
            (
                f"artifact.input.random-markov-recurrence-{path.stem.lower()}",
                "authority-asset",
                path,
            )
            for path in (
                AUTH_RANDOM / "static" / "markov" / "Visits.png",
                AUTH_RANDOM / "static" / "markov" / "Partition.png",
                AUTH_RANDOM / "static" / "markov" / "Classes.png",
                AUTH_RANDOM / "static" / "markov" / "State1.png",
                AUTH_RANDOM / "static" / "markov" / "State2.png",
                AUTH_RANDOM / "static" / "markov" / "State3.png",
            )
        ],
        *[
            (
                f"artifact.input.random-markov-periodicity-{path.stem.lower()}",
                "authority-asset",
                path,
            )
            for path in (
                AUTH_RANDOM / "static" / "markov" / "CyclicClasses.png",
                AUTH_RANDOM / "static" / "markov" / "State4.png",
            )
        ],
        (
            "artifact.input.random-brown-apps-js",
            "authority-asset",
            AUTH_RANDOM / "static" / "apps" / "Apps.js",
        ),
        (
            "artifact.input.reader-brown-apps-js",
            "input",
            ROOT / "build" / "site" / "apps" / "Apps.js",
        ),
        (
            "artifact.input.random-brown-distributions-js",
            "authority-asset",
            AUTH_RANDOM / "static" / "apps" / "Distributions.js",
        ),
        (
            "artifact.input.reader-brown-distributions-js",
            "input",
            ROOT / "build" / "site" / "apps" / "Distributions.js",
        ),
        *[
            (authored_artifact_id(path), "input", path)
            for path in AUTHORED_MARKDOWN_INPUTS
        ],
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
        if str(spec["rel"]) in {
            "poisson/General.html",
            "brown/Standard.html",
            "brown/Drift.html",
            "brown/Bridge.html",
            "brown/Geometric.html",
        }:
            paths.append(
                (
                    f"artifact.input.reader-{slug}",
                    "input",
                    ROOT / "build" / "site" / rel,
                )
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
                    else "text/javascript"
                    if path.suffix == ".js"
                    else "text/markdown"
                    if path in AUTHORED_MARKDOWN_INPUTS
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
    receipt_lab_sources = {
        str(item.get("source")): item
        for item in receipt.get("lab_sources", [])
        if isinstance(item, dict)
    }
    current_lab_sources = {
        relative(LAB): sha256(require_file(LAB)),
        relative(LAB_MARKOV): sha256(require_file(LAB_MARKOV)),
        relative(LAB_CONVERGENCE_MODES): sha256(
            require_file(LAB_CONVERGENCE_MODES)
        ),
        relative(LAB_CONDITIONAL_MARTINGALE): sha256(
            require_file(LAB_CONDITIONAL_MARTINGALE)
        ),
        relative(LAB_BROWNIAN_DIAGNOSTICS): sha256(
            require_file(LAB_BROWNIAN_DIAGNOSTICS)
        ),
    }
    lab_sources_bound = set(receipt_lab_sources) == set(current_lab_sources) and all(
        receipt_lab_sources[path].get("source_sha256") == digest
        for path, digest in current_lab_sources.items()
    )
    quantecon_receipt = load_json(QUANTECON_RECEIPT)
    quantecon_target_bound = (
        quantecon_receipt.get("target", {}).get("sha256")
        == sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "memoryless.md"))
        and quantecon_receipt.get("manifest_sha256") == sha256(require_file(QUANTECON_MANIFEST))
    )
    quantecon_poisson_receipt = load_json(QUANTECON_POISSON_RECEIPT)
    quantecon_poisson_target_bound = (
        quantecon_poisson_receipt.get("target", {}).get("sha256")
        == sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "poisson.md"))
        and quantecon_poisson_receipt.get("manifest_sha256") == sha256(require_file(QUANTECON_POISSON_MANIFEST))
    )
    quantecon_markov_prop_receipt = load_json(QUANTECON_MARKOV_PROP_RECEIPT)
    quantecon_markov_prop_target_bound = (
        quantecon_markov_prop_receipt.get("target", {}).get("sha256")
        == sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "markov_prop.md"))
        and quantecon_markov_prop_receipt.get("manifest_sha256")
        == sha256(require_file(QUANTECON_MARKOV_PROP_MANIFEST))
    )
    quantecon_kolmogorov_bwd_receipt = load_json(QUANTECON_KOLMOGOROV_BWD_RECEIPT)
    quantecon_kolmogorov_bwd_target_bound = (
        quantecon_kolmogorov_bwd_receipt.get("target", {}).get("sha256")
        == sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_bwd.md"))
        and quantecon_kolmogorov_bwd_receipt.get("manifest_sha256")
        == sha256(require_file(QUANTECON_KOLMOGOROV_BWD_MANIFEST))
    )
    quantecon_kolmogorov_fwd_receipt = load_json(QUANTECON_KOLMOGOROV_FWD_RECEIPT)
    quantecon_kolmogorov_fwd_target_bound = (
        quantecon_kolmogorov_fwd_receipt.get("target", {}).get("sha256")
        == sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_fwd.md"))
        and quantecon_kolmogorov_fwd_receipt.get("manifest_sha256")
        == sha256(require_file(QUANTECON_KOLMOGOROV_FWD_MANIFEST))
        and (
            quantecon_kolmogorov_fwd_receipt.get("authority", {}).get("static_assets")
            or [{}]
        )[0].get("sha256")
        == sha256(require_file(QUANTECON_KOLMOGOROV_FWD_STATIC_ASSET))
        and quantecon_kolmogorov_fwd_receipt.get("numerical_qa", {}).get("status")
        == "pass"
        and quantecon_kolmogorov_fwd_receipt.get("numerical_qa", {}).get("sha256")
        == sha256(require_file(QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA))
    )
    quantecon_generators_receipt = load_json(QUANTECON_GENERATORS_RECEIPT)
    quantecon_generators_target = ROOT / "source" / "quantecon" / "lectures" / "generators.md"
    quantecon_generators_target_bound = (
        quantecon_generators_receipt.get("schema") == "o009.quantecon-component.v1"
        and quantecon_generators_receipt.get("unit_id")
        == "unit.o009.quantecon.ctmc.generators"
        and quantecon_generators_receipt.get("target", {}).get("sha256")
        == sha256(require_file(quantecon_generators_target))
        and quantecon_generators_receipt.get("manifest_sha256")
        == sha256(require_file(QUANTECON_GENERATORS_MANIFEST))
        and quantecon_generators_receipt.get("authority", {}).get("source_sha256")
        == sha256(require_file(QUANTECON_GENERATORS_SOURCE))
        and quantecon_generators_receipt.get("authority", {}).get("notebook_sha256")
        == sha256(require_file(QUANTECON_GENERATORS_NOTEBOOK))
        and quantecon_generators_receipt.get("topology", {}).get("code_cells") == 0
        and quantecon_generators_receipt.get("code_cells") == []
        and quantecon_generators_receipt.get("replay_match") is True
    )
    quantecon_uc_mc_semigroups_receipt = load_json(QUANTECON_UC_MC_SEMIGROUPS_RECEIPT)
    quantecon_uc_mc_semigroups_target = (
        ROOT / "source" / "quantecon" / "lectures" / "uc_mc_semigroups.md"
    )
    quantecon_uc_mc_semigroups_target_bound = (
        quantecon_uc_mc_semigroups_receipt.get("schema")
        == "o009.quantecon-component.v1"
        and quantecon_uc_mc_semigroups_receipt.get("unit_id")
        == "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups"
        and quantecon_uc_mc_semigroups_receipt.get("target", {}).get("sha256")
        == sha256(require_file(quantecon_uc_mc_semigroups_target))
        and quantecon_uc_mc_semigroups_receipt.get("manifest_sha256")
        == sha256(require_file(QUANTECON_UC_MC_SEMIGROUPS_MANIFEST))
        and quantecon_uc_mc_semigroups_receipt.get("authority", {}).get("source_sha256")
        == sha256(require_file(QUANTECON_UC_MC_SEMIGROUPS_SOURCE))
        and quantecon_uc_mc_semigroups_receipt.get("authority", {}).get("notebook_sha256")
        == sha256(require_file(QUANTECON_UC_MC_SEMIGROUPS_NOTEBOOK))
        and quantecon_uc_mc_semigroups_receipt.get("topology", {}).get("exercises") == 5
        and quantecon_uc_mc_semigroups_receipt.get("topology", {}).get("solutions") == 5
        and quantecon_uc_mc_semigroups_receipt.get("topology", {}).get("code_cells") == 0
        and quantecon_uc_mc_semigroups_receipt.get("code_cells") == []
        and quantecon_uc_mc_semigroups_receipt.get("replay_match") is True
        and quantecon_uc_mc_semigroups_receipt.get("numerical_qa", {}).get("status")
        == "pass"
        and quantecon_uc_mc_semigroups_receipt.get("numerical_qa", {}).get("sha256")
        == sha256(require_file(QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA))
    )
    quantecon_ergodicity_receipt = load_json(QUANTECON_ERGODICITY_RECEIPT)
    quantecon_ergodicity_target = (
        ROOT / "source" / "quantecon" / "lectures" / "ergodicity.md"
    )
    quantecon_ergodicity_target_bound = (
        quantecon_ergodicity_receipt.get("schema")
        == "o009.quantecon-component.v1"
        and quantecon_ergodicity_receipt.get("unit_id")
        == "unit.o009.quantecon.ctmc.stationarity-ergodicity"
        and quantecon_ergodicity_receipt.get("target", {}).get("sha256")
        == sha256(require_file(quantecon_ergodicity_target))
        and quantecon_ergodicity_receipt.get("manifest_sha256")
        == sha256(require_file(QUANTECON_ERGODICITY_MANIFEST))
        and quantecon_ergodicity_receipt.get("authority", {}).get("source_sha256")
        == sha256(require_file(QUANTECON_ERGODICITY_SOURCE))
        and quantecon_ergodicity_receipt.get("authority", {}).get("notebook_sha256")
        == sha256(require_file(QUANTECON_ERGODICITY_NOTEBOOK))
        and quantecon_ergodicity_receipt.get("topology", {}).get("exercises") == 3
        and quantecon_ergodicity_receipt.get("topology", {}).get("solutions") == 3
        and quantecon_ergodicity_receipt.get("topology", {}).get("code_cells") == 4
        and len(quantecon_ergodicity_receipt.get("code_cells", [])) == 4
        and quantecon_ergodicity_receipt.get("replay_match") is True
        and quantecon_ergodicity_receipt.get("numerical_qa", {}).get("status")
        == "pass"
        and quantecon_ergodicity_receipt.get("numerical_qa", {}).get("sha256")
        == sha256(require_file(QUANTECON_ERGODICITY_NUMERICAL_QA))
    )
    brown_source_soup = BeautifulSoup(
        require_file(ROOT / "source" / "theory" / "brown" / "Standard.html").decode(
            "utf-8"
        ),
        "lxml",
    )
    brown_reader_soup = BeautifulSoup(
        require_file(ROOT / "build" / "site" / "brown" / "Standard.html").decode(
            "utf-8"
        ),
        "lxml",
    )
    records_by_id = {item["id"]: item for item in records}
    brown_solution = records_by_id.get(
        "unit.o009.original.brown.standard.exercise-solution"
    )
    brown_reader_bound = (
        len(brown_source_soup.select("div.unit")) == 50
        and len(brown_source_soup.find_all("details")) == 28
        and len(brown_reader_soup.select("div.unit")) == 50
        and len(brown_reader_soup.find_all("details")) == 30
        and brown_solution is not None
        and brown_solution["rights_id"] == "rights.o009.original.cc-by-4.0"
        and brown_solution["source_target_relationship"] == "authored"
    )
    drift_source_soup = BeautifulSoup(
        require_file(ROOT / "source" / "theory" / "brown" / "Drift.html").decode(
            "utf-8"
        ),
        "lxml",
    )
    drift_reader_soup = BeautifulSoup(
        require_file(ROOT / "build" / "site" / "brown" / "Drift.html").decode(
            "utf-8"
        ),
        "lxml",
    )
    drift_rights_id = "rights.o009.brown-drift-original.cc-by-4.0"
    drift_original_ids = {
        "unit.o009.original.brown.drift.offline-lab",
        "unit.o009.original.brown.drift.mastery",
        "unit.o009.original.brown.drift.mastery.exercise",
        "unit.o009.original.brown.drift.mastery.hint",
        "unit.o009.original.brown.drift.mastery.solution",
        "unit.o009.original.brown.drift.strong-markov-proof",
        "asset.o009.brown-drift-offline-js",
        "segment.o009.original.brown.drift.downstream-correction-note",
    }
    drift_reader_bound = (
        len(drift_source_soup.select("div.unit")) == 11
        and len(drift_source_soup.find_all("details")) == 7
        and len(drift_reader_soup.select("div.unit")) == 11
        and len(drift_reader_soup.find_all("details")) == 10
        and all(
            records_by_id.get(stable_id, {}).get("rights_id") == drift_rights_id
            for stable_id in drift_original_ids
        )
        and require_file(BROWN_DRIFT_OFFLINE_APP)
        == require_file(BUILT_BROWN_DRIFT_OFFLINE_APP)
    )
    bridge_source_soup = BeautifulSoup(
        require_file(ROOT / "source" / "theory" / "brown" / "Bridge.html").decode(
            "utf-8"
        ),
        "lxml",
    )
    bridge_reader_soup = BeautifulSoup(
        require_file(ROOT / "build" / "site" / "brown" / "Bridge.html").decode(
            "utf-8"
        ),
        "lxml",
    )
    bridge_rights_id = "rights.o009.brown-bridge-original.cc-by-4.0"
    bridge_original_ids = {
        "unit.o009.original.brown.bridge.offline-lab",
        "unit.o009.original.brown.bridge.mastery",
        "unit.o009.original.brown.bridge.mastery.process-limit-warning",
        "unit.o009.original.brown.bridge.mastery.exercise",
        "unit.o009.original.brown.bridge.mastery.hint",
        "unit.o009.original.brown.bridge.mastery.solution",
        "asset.o009.brown-bridge-offline-js",
        "segment.o009.original.brown.bridge.downstream-correction-note",
    }
    bridge_reader_bound = (
        len(bridge_source_soup.select("div.unit")) == 13
        and len(bridge_source_soup.find_all("details")) == 7
        and len(bridge_reader_soup.select("div.unit")) == 13
        and len(bridge_reader_soup.find_all("details")) == 9
        and all(
            records_by_id.get(stable_id, {}).get("rights_id") == bridge_rights_id
            for stable_id in bridge_original_ids
        )
        and require_file(BROWN_BRIDGE_OFFLINE_APP)
        == require_file(BUILT_BROWN_BRIDGE_OFFLINE_APP)
    )
    geometric_source_soup = BeautifulSoup(
        require_file(
            ROOT / "source" / "theory" / "brown" / "Geometric.html"
        ).decode("utf-8"),
        "lxml",
    )
    geometric_reader_soup = BeautifulSoup(
        require_file(ROOT / "build" / "site" / "brown" / "Geometric.html").decode(
            "utf-8"
        ),
        "lxml",
    )
    geometric_rights_id = "rights.o009.brown-geometric-original.cc-by-4.0"
    geometric_original_ids = {
        "unit.o009.original.brown.geometric.offline-lab",
        "unit.o009.original.brown.geometric.mastery",
        "unit.o009.original.brown.geometric.mastery.exercise",
        "unit.o009.original.brown.geometric.mastery.hint",
        "unit.o009.original.brown.geometric.mastery.solution",
        "asset.o009.geometric-brownian-offline-js",
        "segment.o009.original.brown.geometric.downstream-correction-note",
    }
    geometric_reader_bound = (
        len(geometric_source_soup.select("div.unit")) == 14
        and len(geometric_source_soup.find_all("details")) == 6
        and len(geometric_reader_soup.select("div.unit")) == 14
        and len(geometric_reader_soup.find_all("details")) == 8
        and all(
            records_by_id.get(stable_id, {}).get("rights_id")
            == geometric_rights_id
            for stable_id in geometric_original_ids
        )
        and require_file(BROWN_GEOMETRIC_OFFLINE_APP)
        == require_file(BUILT_BROWN_GEOMETRIC_OFFLINE_APP)
    )
    original_bridge_source_bound = (
        len(require_file(ORIGINAL_BRIDGE_SOURCE)) == ORIGINAL_BRIDGE_SOURCE_BYTES
        and sha256(require_file(ORIGINAL_BRIDGE_SOURCE))
        == ORIGINAL_BRIDGE_SOURCE_SHA256
    )
    site_inventory = validate_site_manifest_inventory()
    original_bridge_reader_bound = site_inventory.get(ORIGINAL_BRIDGE_PATH) == sha256(
        require_file(ORIGINAL_BRIDGE_READER)
    )
    original_bridge_mastery_bound = (
        load_json(ORIGINAL_BRIDGE_MASTERY_LEDGER)
        == original_bridge_mastery_ledger(admitted=True)
    )
    original_bridge_02_source_bound = (
        len(require_file(ORIGINAL_BRIDGE_02_SOURCE))
        == ORIGINAL_BRIDGE_02_SOURCE_BYTES
        and sha256(require_file(ORIGINAL_BRIDGE_02_SOURCE))
        == ORIGINAL_BRIDGE_02_SOURCE_SHA256
    )
    original_bridge_02_reader_bound = site_inventory.get(
        ORIGINAL_BRIDGE_02_PATH
    ) == sha256(require_file(ORIGINAL_BRIDGE_02_READER))
    original_bridge_02_mastery_bound = (
        load_json(ORIGINAL_BRIDGE_02_MASTERY_LEDGER)
        == original_bridge_02_mastery_ledger(admitted=True)
    )
    original_bridge_03_source_bound = (
        len(require_file(ORIGINAL_BRIDGE_03_SOURCE))
        == ORIGINAL_BRIDGE_03_SOURCE_BYTES
        and sha256(require_file(ORIGINAL_BRIDGE_03_SOURCE))
        == ORIGINAL_BRIDGE_03_SOURCE_SHA256
    )
    original_bridge_03_reader_bound = site_inventory.get(
        ORIGINAL_BRIDGE_03_PATH
    ) == sha256(require_file(ORIGINAL_BRIDGE_03_READER))
    original_bridge_03_mastery_bound = (
        load_json(ORIGINAL_BRIDGE_03_MASTERY_LEDGER)
        == original_bridge_03_mastery_ledger(admitted=True)
    )
    original_bridge_04_source_bound = (
        len(require_file(ORIGINAL_BRIDGE_04_SOURCE))
        == ORIGINAL_BRIDGE_04_SOURCE_BYTES
        and sha256(require_file(ORIGINAL_BRIDGE_04_SOURCE))
        == ORIGINAL_BRIDGE_04_SOURCE_SHA256
    )
    original_bridge_04_reader_bound = site_inventory.get(
        ORIGINAL_BRIDGE_04_PATH
    ) == sha256(require_file(ORIGINAL_BRIDGE_04_READER))
    original_bridge_04_mastery_bound = (
        load_json(ORIGINAL_BRIDGE_04_MASTERY_LEDGER)
        == original_bridge_04_mastery_ledger(admitted=True)
    )
    convergence_lab_rel = relative(LAB_CONVERGENCE_MODES)
    convergence_lab_receipt = receipt_lab_sources.get(convergence_lab_rel, {})
    convergence_reader_path = (
        ROOT / "build" / "site" / "labs" / "03-konvergensi-mode-dan-lln-clt.html"
    )
    convergence_reader_soup = BeautifulSoup(
        require_file(convergence_reader_path).decode("utf-8"), "lxml"
    )
    convergence_table = convergence_reader_soup.find(
        "table", id="o009-results-convergence-modes"
    )
    convergence_expected_rows = [
        {
            "kasus": "1",
            "n": "1000",
            "benih": "20260829",
            "nilai": "0.000000000000",
            "target": "0.000000000000",
            "galat_mutlak": "0.000000000000",
            "skala_teori": "0.001000000000",
        },
        {
            "kasus": "2",
            "n": "1000",
            "benih": "20260829",
            "nilai": "0.001040000000",
            "target": "0.001000000000",
            "galat_mutlak": "0.000040000000",
            "skala_teori": "0.001000000000",
        },
        {
            "kasus": "3",
            "n": "1000",
            "benih": "20260829",
            "nilai": "1.040000000000",
            "target": "0.000000000000",
            "galat_mutlak": "1.040000000000",
            "skala_teori": "1.000000000000",
        },
        {
            "kasus": "4",
            "n": "10000",
            "benih": "20260830",
            "nilai": "0.297000000000",
            "target": "0.300000000000",
            "galat_mutlak": "0.003000000000",
            "skala_teori": "0.004582575695",
        },
        {
            "kasus": "5",
            "n": "10000",
            "benih": "20260830",
            "nilai": "-0.654653670708",
            "target": "0.000000000000",
            "galat_mutlak": "0.654653670708",
            "skala_teori": "1.000000000000",
        },
    ]
    convergence_entity_ids = {
        "o009-lab-convergence-modes",
        "o009-lab-convergence-modes-experiment",
        "o009-exercise-convergence-modes-estimation",
        "o009-solution-convergence-modes-estimation",
        "o009-program-convergence-modes",
        "o009-results-convergence-modes",
        "o009-mastery-convergence-modes",
        "o009-mastery-convergence-modes-sequence",
        "o009-exercise-convergence-modes-mastery",
        "o009-hint-convergence-modes-1",
        "o009-hint-convergence-modes-2",
        "o009-answer-convergence-modes",
        "o009-solution-convergence-modes",
    }
    convergence_o006_edges = [
        item
        for item in relations
        if item["source_id"] == "o009-lab-convergence-modes"
        and item["target_id"] == "resource.o006.c140.shared"
    ]
    convergence_lab_bound = (
        convergence_lab_receipt.get("chunk_id")
        == "o009_lab_convergence_modes"
        and convergence_lab_receipt.get("source_sha256")
        == sha256(require_file(LAB_CONVERGENCE_MODES))
        and convergence_lab_receipt.get("r_result_rows")
        == convergence_expected_rows
        and site_inventory.get("labs/03-konvergensi-mode-dan-lln-clt.html")
        == sha256(require_file(convergence_reader_path))
        and convergence_table is not None
        and len(convergence_table.find_all("tr")) == 6
        and all(
            records_by_id.get(stable_id, {}).get("rights_id")
            == "rights.o009.lab.convergence-modes.cc-by-4.0"
            for stable_id in convergence_entity_ids
        )
        and len(convergence_o006_edges) == 1
        and convergence_o006_edges[0]["relation_type"] == "depends-on"
        and "tidak ada byte"
        in require_file(LAB_CONVERGENCE_MODES).decode("utf-8")
        and "donor O006 yang disalin"
        in require_file(LAB_CONVERGENCE_MODES).decode("utf-8")
    )
    conditional_lab_rel = relative(LAB_CONDITIONAL_MARTINGALE)
    conditional_lab_receipt = receipt_lab_sources.get(conditional_lab_rel, {})
    conditional_reader_path = (
        ROOT
        / "build"
        / "site"
        / "labs"
        / "04-nilai-harapan-bersyarat-martingal.html"
    )
    conditional_reader_text = require_file(conditional_reader_path).decode("utf-8")
    conditional_reader_soup = BeautifulSoup(conditional_reader_text, "lxml")
    conditional_reader_visible_text = " ".join(
        conditional_reader_soup.get_text(" ", strip=True).split()
    )
    conditional_table = conditional_reader_soup.find(
        "table", id="o009-results-conditional-martingale"
    )
    conditional_expected_rows = [
        {
            "seed": "20260829",
            "ruang_hingga": "Omega_3 dan Omega_12",
            "E_X": "3.000000000000",
            "galat_bersyarat": "0.000000000000",
            "galat_menara": "0.000000000000",
            "galat_martingal": "0.000000000000",
            "rerata_S_tau_b": "0.000000000000",
            "target_E_S_tau_b": "0.000000000000",
            "cap_tau_plus": "12",
            "laju_kena_batas": "0.774414062500",
            "target_laju": "0.774414062500",
            "rerata_S_tau_plus_terpotong": "0.000000000000",
            "target_E_S_tau_plus_terpotong": "0.000000000000",
            "rerata_S_hanya_yang_kena": "1.000000000000",
            "target_S_tau_plus": "1.000000000000",
            "celah_naif": "1.000000000000",
            "toleransi": "1.000000000000e-12",
            "status": "PASS",
        }
    ]
    conditional_entity_ids = {
        "o009-lab-conditional-martingale",
        "o009-conditional-martingale-goals",
        "o009-conditional-expectation-audit",
        "o009-exercise-conditional-martingale-audit",
        "o009-program-conditional-martingale",
        "o009-results-conditional-martingale",
        "o009-optional-stopping-diagnostic",
        "o009-hint-conditional-martingale-audit-1",
        "o009-hint-conditional-martingale-audit-2",
        "o009-hint-conditional-martingale-audit-3",
        "o009-answer-conditional-martingale-audit",
        "o009-solution-conditional-martingale-audit",
    }
    conditional_expected_dependencies = {
        "unit.o009.random.expect.conditional2",
        "unit.o009.random.prob.stop",
        "unit.o009.random.martingales.properties",
        "unit.o009.random.martingales.stop",
    }
    conditional_dependency_edges = [
        item
        for item in relations
        if item["source_id"] == "o009-lab-conditional-martingale"
        and item["relation_type"] == "depends-on"
    ]
    conditional_source_text = require_file(
        LAB_CONDITIONAL_MARTINGALE
    ).decode("utf-8")
    conditional_lab_bound = (
        conditional_lab_receipt.get("chunk_id")
        == "o009_lab_conditional_martingale"
        and conditional_lab_receipt.get("source_sha256")
        == sha256(require_file(LAB_CONDITIONAL_MARTINGALE))
        and conditional_lab_receipt.get("r_result_rows")
        == conditional_expected_rows
        and site_inventory.get(
            "labs/04-nilai-harapan-bersyarat-martingal.html"
        )
        == sha256(require_file(conditional_reader_path))
        and conditional_table is not None
        and len(conditional_table.find_all("tr")) == 2
        and len(conditional_table.find_all("th")) == 18
        and all(
            records_by_id.get(stable_id, {}).get("rights_id")
            == "rights.o009.lab.conditional-martingale.cc-by-4.0"
            for stable_id in conditional_entity_ids
        )
        and {item["target_id"] for item in conditional_dependency_edges}
        == conditional_expected_dependencies
        and len(conditional_dependency_edges) == 4
        and "no source HTML bytes are copied" in conditional_source_text
        and "OpenAI Codex gpt-5.6-sol, Ultra." in conditional_reader_visible_text
        and "tidak didukung atau disahkan" in conditional_reader_visible_text
        and len(
            [
                item
                for item in relations
                if item["relation_type"] == "hints"
                and item["target_id"]
                == "o009-exercise-conditional-martingale-audit"
            ]
        )
        == 3
        and len(
            [
                item
                for item in relations
                if item["relation_type"] == "answers"
                and item["target_id"]
                == "o009-exercise-conditional-martingale-audit"
            ]
        )
        == 1
        and len(
            [
                item
                for item in relations
                if item["relation_type"] == "solves"
                and item["target_id"]
                == "o009-exercise-conditional-martingale-audit"
            ]
        )
        == 1
    )
    brownian_lab_rel = relative(LAB_BROWNIAN_DIAGNOSTICS)
    brownian_lab_receipt = receipt_lab_sources.get(brownian_lab_rel, {})
    brownian_reader_path = (
        ROOT
        / "build"
        / "site"
        / "labs"
        / "05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
    )
    brownian_reader_text = require_file(brownian_reader_path).decode("utf-8")
    brownian_reader_soup = BeautifulSoup(brownian_reader_text, "lxml")
    brownian_reader_visible_text = " ".join(
        brownian_reader_soup.get_text(" ", strip=True).split()
    )
    brownian_table = brownian_reader_soup.find(
        "table", id="o009-results-brownian-diagnostics"
    )
    brownian_expected_rows = [
        {
            "n": "64",
            "k_endpoint": "36",
            "ambang_kena": "8",
            "cdf_endpoint_eksak": "0.869782261712",
            "target_normal": "0.841344746069",
            "galat_cdf": "0.028437515643",
            "prob_kena_eksak": "0.321084135685",
            "target_brown": "0.317310507863",
            "galat_kena": "0.003773627822",
            "qv_mesh_alami": "1.000000000000",
            "qv_refinemen_pralimit": "0.125000000000",
            "variasi_total": "8.000000000000",
            "refinemen_r": "8",
            "toleransi": "1.000000000000e-12",
            "status": "PASS",
        },
        {
            "n": "256",
            "k_endpoint": "136",
            "ambang_kena": "16",
            "cdf_endpoint_eksak": "0.856005356734",
            "target_normal": "0.841344746069",
            "galat_cdf": "0.014660610666",
            "prob_kena_eksak": "0.318255270999",
            "target_brown": "0.317310507863",
            "galat_kena": "0.000944763136",
            "qv_mesh_alami": "1.000000000000",
            "qv_refinemen_pralimit": "0.125000000000",
            "variasi_total": "16.000000000000",
            "refinemen_r": "8",
            "toleransi": "1.000000000000e-12",
            "status": "PASS",
        },
        {
            "n": "1024",
            "k_endpoint": "528",
            "ambang_kena": "32",
            "cdf_endpoint_eksak": "0.848789424921",
            "target_normal": "0.841344746069",
            "galat_cdf": "0.007444678852",
            "prob_kena_eksak": "0.317546780410",
            "target_brown": "0.317310507863",
            "galat_kena": "0.000236272547",
            "qv_mesh_alami": "1.000000000000",
            "qv_refinemen_pralimit": "0.125000000000",
            "variasi_total": "32.000000000000",
            "refinemen_r": "8",
            "toleransi": "1.000000000000e-12",
            "status": "PASS",
        },
        {
            "n": "4096",
            "k_endpoint": "2080",
            "ambang_kena": "64",
            "cdf_endpoint_eksak": "0.845096155857",
            "target_normal": "0.841344746069",
            "galat_cdf": "0.003751409788",
            "prob_kena_eksak": "0.317369581063",
            "target_brown": "0.317310507863",
            "galat_kena": "0.000059073200",
            "qv_mesh_alami": "1.000000000000",
            "qv_refinemen_pralimit": "0.125000000000",
            "variasi_total": "64.000000000000",
            "refinemen_r": "8",
            "toleransi": "1.000000000000e-12",
            "status": "PASS",
        },
    ]
    brownian_entity_ids = {
        "o009-lab-brownian-diagnostics",
        "o009-brownian-diagnostics-goals",
        "o009-brownian-partition-order",
        "o009-brownian-exact-audit",
        "o009-exercise-brownian-diagnostics",
        "o009-program-brownian-diagnostics",
        "o009-results-brownian-diagnostics",
        "o009-hint-brownian-diagnostics-1",
        "o009-hint-brownian-diagnostics-2",
        "o009-hint-brownian-diagnostics-3",
        "o009-answer-brownian-diagnostics",
        "o009-solution-brownian-diagnostics",
    }
    brownian_expected_dependencies = {
        "unit.o009.random.brown.standard",
        "resource.o006.c140.shared",
    }
    brownian_dependency_edges = [
        item
        for item in relations
        if item["source_id"] == "o009-lab-brownian-diagnostics"
        and item["relation_type"] == "depends-on"
    ]
    brownian_source_text = require_file(LAB_BROWNIAN_DIAGNOSTICS).decode("utf-8")
    brownian_lab_bound = (
        brownian_lab_receipt.get("chunk_id")
        == "o009_lab_brownian_diagnostics"
        and brownian_lab_receipt.get("source_sha256")
        == sha256(require_file(LAB_BROWNIAN_DIAGNOSTICS))
        and brownian_lab_receipt.get("output")
        == "labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
        and brownian_lab_receipt.get("r_result_rows") == brownian_expected_rows
        and site_inventory.get(
            "labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
        )
        == sha256(require_file(brownian_reader_path))
        and brownian_table is not None
        and len(brownian_table.find_all("tr")) == 5
        and len(brownian_table.find_all("th")) == 15
        and all(
            records_by_id.get(stable_id, {}).get("rights_id")
            == "rights.o009.lab.brownian-diagnostics.cc-by-4.0"
            for stable_id in brownian_entity_ids
        )
        and {item["target_id"] for item in brownian_dependency_edges}
        == brownian_expected_dependencies
        and len(brownian_dependency_edges) == 2
        and "no Random HTML or O006 bytes are copied" in brownian_source_text
        and "tidak ada byte O006 yang disalin" in brownian_source_text
        and "OpenAI Codex gpt-5.6-sol, Ultra." in brownian_reader_visible_text
        and "tidak didukung atau disahkan" in brownian_reader_visible_text
        and (
            'source_page_sha256: "brown/Standard.html='
            + sha256(
                require_file(
                    ROOT / "source" / "theory" / "brown" / "Standard.html"
                )
            )
            + '"'
        )
        in brownian_source_text
        and len(
            [
                item
                for item in relations
                if item["relation_type"] == "hints"
                and item["target_id"] == "o009-exercise-brownian-diagnostics"
            ]
        )
        == 3
        and len(
            [
                item
                for item in relations
                if item["relation_type"] == "answers"
                and item["target_id"] == "o009-exercise-brownian-diagnostics"
            ]
        )
        == 1
        and len(
            [
                item
                for item in relations
                if item["relation_type"] == "solves"
                and item["target_id"] == "o009-exercise-brownian-diagnostics"
            ]
        )
        == 1
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
            "qa.o009.brown-standard-reader-binding",
            "structural-translation",
            "artifact.input.reader-brown-standard",
            "pass" if brown_reader_bound else "fail",
            "source=50 unit divs/28 disclosures; reader=50 unit divs/30 disclosures; original solution is separately licensed",
        ),
        (
            "qa.o009.brown-drift-reader-binding",
            "structural-translation",
            "artifact.input.reader-brown-drift",
            "pass" if drift_reader_bound else "fail",
            "source=11 unit divs/7 disclosures; reader=11 unit divs/10 disclosures; note, offline lab/app, mastery sequence, and strong-Markov proof are separately bound CC BY 4.0 additions",
        ),
        (
            "qa.o009.brown-bridge-reader-binding",
            "structural-translation",
            "artifact.input.reader-brown-bridge",
            "pass" if bridge_reader_bound else "fail",
            "source=13 unit divs/7 disclosures; reader=13 unit divs/9 disclosures; note, offline lab/app, process-limit warning, and mastery exercise/hint/solution are separately bound CC BY 4.0 additions",
        ),
        (
            "qa.o009.brown-geometric-reader-binding",
            "structural-translation",
            "artifact.input.reader-brown-geometric",
            "pass" if geometric_reader_bound else "fail",
            "source=14 unit divs/6 disclosures; reader=14 unit divs/8 disclosures; note, offline lab/app, and conditional-law mastery exercise/hint/solution are separately bound CC BY 4.0 additions",
        ),
        (
            "qa.o009.original-bridge-01-source-binding",
            "input-binding",
            "artifact.input.original-bridge-01-source",
            "pass" if original_bridge_source_bound else "fail",
            (
                f"bytes={ORIGINAL_BRIDGE_SOURCE_BYTES} "
                f"sha256={ORIGINAL_BRIDGE_SOURCE_SHA256}"
            ),
        ),
        (
            "qa.o009.original-bridge-01-reader-binding",
            "build-binding",
            "artifact.input.original-bridge-01-reader",
            "pass" if original_bridge_reader_bound else "fail",
            "reader byte hash is bound by the complete site package manifest",
        ),
        (
            "qa.o009.original-bridge-01-mastery-binding",
            "graph-validation",
            "artifact.input.original-bridge-01-mastery-ledger",
            "pass" if original_bridge_mastery_bound else "fail",
            (
                "3 exercises, 6 hints, 3 answers, 3 worked solutions; "
                "process-construction quota +3 with 1 remaining"
            ),
        ),
        (
            "qa.o009.original-bridge-02-source-binding",
            "input-binding",
            "artifact.input.original-bridge-02-source",
            "pass" if original_bridge_02_source_bound else "fail",
            (
                f"bytes={ORIGINAL_BRIDGE_02_SOURCE_BYTES} "
                f"sha256={ORIGINAL_BRIDGE_02_SOURCE_SHA256}"
            ),
        ),
        (
            "qa.o009.original-bridge-02-reader-binding",
            "build-binding",
            "artifact.input.original-bridge-02-reader",
            "pass" if original_bridge_02_reader_bound else "fail",
            "reader byte hash is bound by the complete site package manifest",
        ),
        (
            "qa.o009.original-bridge-02-mastery-binding",
            "graph-validation",
            "artifact.input.original-bridge-02-mastery-ledger",
            "pass" if original_bridge_02_mastery_bound else "fail",
            (
                "3 exercises, 6 hints, 3 answers, 3 worked solutions; "
                "integrative counterexample/literature-reading quota +3 with 3 remaining"
            ),
        ),
        (
            "qa.o009.original-bridge-03-source-binding",
            "input-binding",
            "artifact.input.original-bridge-03-source",
            "pass" if original_bridge_03_source_bound else "fail",
            (
                f"bytes={ORIGINAL_BRIDGE_03_SOURCE_BYTES} "
                f"sha256={ORIGINAL_BRIDGE_03_SOURCE_SHA256}"
            ),
        ),
        (
            "qa.o009.original-bridge-03-reader-binding",
            "build-binding",
            "artifact.input.original-bridge-03-reader",
            "pass" if original_bridge_03_reader_bound else "fail",
            "reader byte hash is bound by the complete site package manifest",
        ),
        (
            "qa.o009.original-bridge-03-mastery-binding",
            "graph-validation",
            "artifact.input.original-bridge-03-mastery-ledger",
            "pass" if original_bridge_03_mastery_bound else "fail",
            (
                "3 exercises, 6 hints, 3 answers, 3 worked solutions; "
                "regular-conditional-probability quota +3; course original "
                "mastery count 9 with 27 remaining"
            ),
        ),
        (
            "qa.o009.original-bridge-04-source-binding",
            "input-binding",
            "artifact.input.original-bridge-04-source",
            "pass" if original_bridge_04_source_bound else "fail",
            (
                f"bytes={ORIGINAL_BRIDGE_04_SOURCE_BYTES} "
                f"sha256={ORIGINAL_BRIDGE_04_SOURCE_SHA256}"
            ),
        ),
        (
            "qa.o009.original-bridge-04-reader-binding",
            "build-binding",
            "artifact.input.original-bridge-04-reader",
            "pass" if original_bridge_04_reader_bound else "fail",
            "reader byte hash is bound by the complete site package manifest",
        ),
        (
            "qa.o009.original-bridge-04-mastery-binding",
            "graph-validation",
            "artifact.input.original-bridge-04-mastery-ledger",
            "pass" if original_bridge_04_mastery_bound else "fail",
            (
                "3 exercises, 6 hints, 3 answers, 3 worked solutions; "
                "integrative counterexample/literature-reading quota +3 and complete; "
                "course original mastery count 12 with 24 remaining"
            ),
        ),
        (
            "qa.o009.original-lab-03-convergence-binding",
            "graph-validation",
            "artifact.input.target-lab-convergence-modes",
            "pass" if convergence_lab_bound else "fail",
            (
                "source and reader hashes, one five-row deterministic R result, "
                "13 stable-ID units, 2 exercises/2 hints/1 answer/2 solutions, "
                "separate CC BY 4.0 rights, and the dependency-only O006 boundary "
                "are bound"
            ),
        ),
        (
            "qa.o009.original-lab-04-conditional-martingale-binding",
            "graph-validation",
            "artifact.input.target-lab-conditional-martingale",
            "pass" if conditional_lab_bound else "fail",
            (
                "source and reader hashes, one exact 18-column R result, 12 "
                "stable-ID units, 1 exercise/3 hints/1 answer/1 worked solution, "
                "four dependency-only Random theory edges, visible exact model and "
                "non-endorsement, and separate CC BY 4.0 rights are bound"
            ),
        ),
        (
            "qa.o009.original-lab-05-brownian-diagnostics-binding",
            "graph-validation",
            "artifact.input.target-lab-brownian-diagnostics",
            "pass" if brownian_lab_bound else "fail",
            (
                "source and reader hashes, one exact 5-row by 15-column R result, "
                "12 stable-ID units, 1 exercise/3 hints/1 answer/1 worked solution, "
                "two dependency-only Random/O006 edges, four existing outcome pairs, "
                "visible exact model/non-endorsement/no-copy notices, and separate "
                "CC BY 4.0 rights are bound"
            ),
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
            "qa.o009.build-lab-sources-input-binding",
            "input-binding",
            "artifact.input.site-build-receipt",
            "pass" if lab_sources_bound else "fail",
            f"receipt_paths={sorted(receipt_lab_sources)} current={current_lab_sources}",
        ),
        (
            "qa.o009.quantecon-component-binding",
            "build-binding",
            "artifact.input.quantecon-component-receipt",
            "pass" if quantecon_target_bound else "fail",
            f"target={quantecon_receipt.get('target', {}).get('sha256')} manifest={quantecon_receipt.get('manifest_sha256')}",
        ),
        (
            "qa.o009.quantecon-rights-witness",
            "rights-binding",
            "artifact.input.quantecon-license",
            "pass" if "Attribution-ShareAlike 4.0 International" in require_file(QUANTECON_LICENSE).decode("utf-8") else "fail",
            "QuantEcon component retains CC BY-SA 4.0 and attribution/non-endorsement notice",
        ),
        (
            "qa.o009.quantecon-poisson-component-binding",
            "build-binding",
            "artifact.input.quantecon-poisson-component-receipt",
            "pass" if quantecon_poisson_target_bound else "fail",
            f"target={quantecon_poisson_receipt.get('target', {}).get('sha256')} manifest={quantecon_poisson_receipt.get('manifest_sha256')}",
        ),
        (
            "qa.o009.quantecon-markov-prop-component-binding",
            "build-binding",
            "artifact.input.quantecon-markov-prop-component-receipt",
            "pass" if quantecon_markov_prop_target_bound else "fail",
            f"target={quantecon_markov_prop_receipt.get('target', {}).get('sha256')} manifest={quantecon_markov_prop_receipt.get('manifest_sha256')}",
        ),
        (
            "qa.o009.quantecon-kolmogorov-bwd-component-binding",
            "build-binding",
            "artifact.input.quantecon-kolmogorov-bwd-component-receipt",
            "pass" if quantecon_kolmogorov_bwd_target_bound else "fail",
            f"target={quantecon_kolmogorov_bwd_receipt.get('target', {}).get('sha256')} manifest={quantecon_kolmogorov_bwd_receipt.get('manifest_sha256')}",
        ),
        (
            "qa.o009.quantecon-kolmogorov-fwd-component-binding",
            "build-binding",
            "artifact.input.quantecon-kolmogorov-fwd-component-receipt",
            "pass" if quantecon_kolmogorov_fwd_target_bound else "fail",
            (
                f"target={quantecon_kolmogorov_fwd_receipt.get('target', {}).get('sha256')} "
                f"manifest={quantecon_kolmogorov_fwd_receipt.get('manifest_sha256')} "
                f"source_figure={quantecon_kolmogorov_fwd_receipt.get('authority', {}).get('static_assets', [])} "
                f"numerical_qa={quantecon_kolmogorov_fwd_receipt.get('numerical_qa', {})}"
            ),
        ),
        (
            "qa.o009.quantecon-generators-component-binding",
            "build-binding",
            "artifact.input.quantecon-generators-component-receipt",
            "pass" if quantecon_generators_target_bound else "fail",
            (
                f"target={quantecon_generators_receipt.get('target', {}).get('sha256')} "
                f"manifest={quantecon_generators_receipt.get('manifest_sha256')} "
                f"source={quantecon_generators_receipt.get('authority', {}).get('source_sha256')} "
                f"notebook={quantecon_generators_receipt.get('authority', {}).get('notebook_sha256')} "
                f"topology={quantecon_generators_receipt.get('topology', {})}"
            ),
        ),
        (
            "qa.o009.quantecon-uc-mc-semigroups-component-binding",
            "build-binding",
            "artifact.input.quantecon-uc-mc-semigroups-component-receipt",
            "pass" if quantecon_uc_mc_semigroups_target_bound else "fail",
            (
                f"target={quantecon_uc_mc_semigroups_receipt.get('target', {}).get('sha256')} "
                f"manifest={quantecon_uc_mc_semigroups_receipt.get('manifest_sha256')} "
                f"source={quantecon_uc_mc_semigroups_receipt.get('authority', {}).get('source_sha256')} "
                f"notebook={quantecon_uc_mc_semigroups_receipt.get('authority', {}).get('notebook_sha256')} "
                f"topology={quantecon_uc_mc_semigroups_receipt.get('topology', {})} "
                f"numerical_qa={quantecon_uc_mc_semigroups_receipt.get('numerical_qa', {})}"
            ),
        ),
        (
            "qa.o009.quantecon-ergodicity-component-binding",
            "build-binding",
            "artifact.input.quantecon-ergodicity-component-receipt",
            "pass" if quantecon_ergodicity_target_bound else "fail",
            (
                f"target={quantecon_ergodicity_receipt.get('target', {}).get('sha256')} "
                f"manifest={quantecon_ergodicity_receipt.get('manifest_sha256')} "
                f"source={quantecon_ergodicity_receipt.get('authority', {}).get('source_sha256')} "
                f"notebook={quantecon_ergodicity_receipt.get('authority', {}).get('notebook_sha256')} "
                f"topology={quantecon_ergodicity_receipt.get('topology', {})} "
                f"numerical_qa={quantecon_ergodicity_receipt.get('numerical_qa', {})}"
            ),
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
                "accessibility-localization",
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
        "x-csv": {
            "header": definition["fields"],
            "encoding": "utf-8",
            "line_ending": CSV_LINE_ENDING_NAME,
        },
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
        "rel.translates.o009-lab-markov-gambler-ruin-experiment.unit.donor.zitkovic.markov-chain-simulation.section",
        "rel.translates.o009-exercise-markov-gambler-ruin-estimation.unit.donor.zitkovic.markov-gambler-ruin.exercise",
        "rel.translates.o009-solution-markov-gambler-ruin-estimation.unit.donor.zitkovic.markov-gambler-ruin.solution",
        "rel.translates.o009-program-markov-gambler-ruin.unit.donor.zitkovic.markov-gambler-ruin.program.1",
        "rel.solves.donor.zitkovic.markov-gambler-ruin",
        "rel.solves.target.markov-gambler-ruin-estimation",
        "rel.contains.donor.markov-section.exercise",
        "rel.contains.donor.markov-section.solution",
        "rel.contains.donor.markov-solution.program.1",
        "rel.contains.o009-solution-markov-gambler-ruin-estimation.o009-program-markov-gambler-ruin",
        "rel.depends.lab-markov-gambler-ruin.theory-markov-general",
        "rel.teaches.markov-experiment.simulation",
        "rel.assesses.markov-estimation",
        "rel.precedes.markov-theory.lab",
        "rel.depends-on.martingales-stop.prob-stop",
        "rel.depends-on.martingales-stop.martingales-properties",
        "rel.teaches.martingales-stop.optional-stopping",
        "rel.teaches.martingales-stop.stopped-martingale",
        "rel.teaches.martingales-stop.wald",
        "rel.teaches.martingales-stop.pattern-waiting",
        "rel.assesses.martingales-stop.pattern-waiting",
        "rel.teaches.martingales-stop.optimal-stopping",
        "rel.depends-on.markov-discrete.markov-general",
        "rel.depends-on.markov-discrete.processes",
        "rel.depends-on.markov-discrete.stopping-times",
        "rel.depends-on.markov-discrete.kernels",
        "rel.depends-on.markov-discrete.random-walk.o006-sampling",
        "rel.teaches.markov-discrete.definition",
        "rel.teaches.markov-discrete.transition-laws",
        "rel.teaches.markov-discrete.potential",
        "rel.teaches.markov-discrete.restriction",
        "rel.teaches.markov-discrete.finite-models",
        "rel.assesses.markov-discrete.com1",
        "rel.assesses.markov-discrete.com2",
        "rel.assesses.markov-discrete.com3",
        "rel.assesses.markov-discrete.com4",
        "rel.assesses.markov-discrete.ind3",
        "rel.assesses.markov-discrete.dbl4",
        "rel.assesses.markov-discrete.dbl6",
        "rel.solves.markov-discrete.com1",
        "rel.solves.markov-discrete.com2",
        "rel.solves.markov-discrete.com3",
        "rel.solves.markov-discrete.com4",
        "rel.solves.markov-discrete.ind3",
        "rel.solves.markov-discrete.dbl4",
        "rel.solves.markov-discrete.dbl6",
        "rel.depends-on.markov-recurrence.markov-discrete",
        "rel.depends-on.markov-recurrence.stopping-times",
        "rel.depends-on.markov-recurrence.kernels",
        "rel.teaches.markov-recurrence.hitting",
        "rel.teaches.markov-recurrence.green",
        "rel.teaches.markov-recurrence.classes",
        "rel.teaches.markov-recurrence.canonical-decomposition",
        "rel.teaches.markov-recurrence.staying-test",
        "rel.teaches.markov-recurrence.computation",
        "rel.assesses.markov-recurrence.fin1",
        "rel.assesses.markov-recurrence.fin2",
        "rel.assesses.markov-recurrence.fin3",
        "rel.solves.markov-recurrence.fin1",
        "rel.solves.markov-recurrence.fin2",
        "rel.solves.markov-recurrence.fin3",
        "rel.depends-on.markov-periodicity.markov-discrete",
        "rel.depends-on.markov-periodicity.markov-recurrence",
        "rel.teaches.markov-periodicity.period",
        "rel.teaches.markov-periodicity.cyclic-decomposition",
        "rel.assesses.markov-periodicity.fin1",
        "rel.assesses.markov-periodicity.fin3",
        "rel.solves.markov-periodicity.fin1",
        "rel.solves.markov-periodicity.fin3",
        "rel.depends-on.markov-limiting.markov-discrete",
        "rel.depends-on.markov-limiting.markov-recurrence",
        "rel.depends-on.markov-limiting.markov-periodicity",
        "rel.teaches.markov-limiting.embedded-renewal",
        "rel.teaches.markov-limiting.renewal-limits",
        "rel.teaches.markov-limiting.positive-null-recurrence",
        "rel.teaches.markov-limiting.ergodic-definition",
        "rel.teaches.markov-limiting.periodic-subsequence-limits",
        "rel.teaches.markov-limiting.invariant-existence",
        "rel.teaches.markov-limiting.invariant-mixtures",
        "rel.teaches.markov-limiting.invariant-measure-uniqueness",
        "rel.assesses.markov-limiting.div-023",
        "rel.assesses.markov-limiting.fin1",
        "rel.assesses.markov-limiting.fin2",
        "rel.assesses.markov-limiting.fin3",
        "rel.assesses.markov-limiting.fin4",
        "rel.assesses.markov-limiting.fin5",
        "rel.solves.markov-limiting.fin1",
        "rel.solves.markov-limiting.fin2",
        "rel.solves.markov-limiting.fin3",
        "rel.solves.markov-limiting.fin4",
        "rel.solves.markov-limiting.fin5",
        "rel.depends-on.unit.o009.random.markov.limiting.figure-001",
        "rel.depends-on.unit.o009.random.markov.limiting.figure-002",
        "rel.depends-on.unit.o009.random.markov.limiting.figure-003",
        "rel.depends-on.unit.o009.random.markov.limiting.figure-004",
        "rel.depends-on.unit.o009.random.markov.limiting.figure-005",
        "rel.precedes.unit.o009.random.markov.periodicity.unit.o009.random.markov.limiting",
        "rel.contains.course.o009.two-state-simulator",
        "rel.depends-on.two-state-simulator.markov-limiting",
        "rel.executes.markov-limiting.div-023.two-state-simulator",
        "rel.assesses.two-state-simulator.markov-ergodic-periodic-limits",
        "rel.contains.course.o009.unit.o009.quantecon.ctmc.markov-property",
        "rel.precedes.unit.o009.quantecon.ctmc.poisson-processes.unit.o009.quantecon.ctmc.markov-property",
        "rel.solves.quantecon.markov_prop.1",
        "rel.solves.quantecon.markov_prop.2",
        "rel.solves.quantecon.markov_prop.3",
        "rel.solves.quantecon.markov_prop.4",
        "rel.depends-on.quantecon.markov_prop.o006",
        "rel.contains.course.o009.unit.o009.quantecon.ctmc.kolmogorov-backward",
        "rel.precedes.unit.o009.quantecon.ctmc.markov-property.unit.o009.quantecon.ctmc.kolmogorov-backward",
        "rel.solves.quantecon.kolmogorov_bwd.1",
        "rel.solves.quantecon.kolmogorov_bwd.2",
        "rel.solves.quantecon.kolmogorov_bwd.3",
        "rel.depends-on.quantecon.kolmogorov_bwd.o006",
        "rel.contains.course.o009.unit.o009.quantecon.ctmc.kolmogorov-forward",
        "rel.precedes.unit.o009.quantecon.ctmc.kolmogorov-backward.unit.o009.quantecon.ctmc.kolmogorov-forward",
        "rel.solves.quantecon.kolmogorov_fwd.1",
        "rel.solves.quantecon.kolmogorov_fwd.2",
        "rel.solves.quantecon.kolmogorov_fwd.3",
        "rel.depends-on.quantecon.kolmogorov_fwd.o006",
        "rel.contains.course.o009.unit.o009.quantecon.ctmc.generators",
        "rel.precedes.unit.o009.quantecon.ctmc.kolmogorov-forward.unit.o009.quantecon.ctmc.generators",
        "rel.solves.quantecon.generators.1",
        "rel.solves.quantecon.generators.2",
        "rel.solves.quantecon.generators.3",
        "rel.depends-on.quantecon.generators.o006",
        "rel.contains.course.o009.unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups",
        "rel.precedes.unit.o009.quantecon.ctmc.generators.unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups",
        "rel.solves.quantecon.uc_mc_semigroups.1",
        "rel.solves.quantecon.uc_mc_semigroups.2",
        "rel.solves.quantecon.uc_mc_semigroups.3",
        "rel.solves.quantecon.uc_mc_semigroups.4",
        "rel.solves.quantecon.uc_mc_semigroups.5",
        "rel.depends-on.quantecon.uc_mc_semigroups.o006",
        "rel.contains.course.o009.unit.o009.quantecon.ctmc.stationarity-ergodicity",
        "rel.precedes.unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups.unit.o009.quantecon.ctmc.stationarity-ergodicity",
        "rel.solves.quantecon.ergodicity.1",
        "rel.solves.quantecon.ergodicity.2",
        "rel.solves.quantecon.ergodicity.3",
        "rel.depends-on.quantecon.ergodicity.o006",
    }
    required_relations.update(
        {
            "rel.contains.course.o009.unit.o009.random.poisson.general",
            "rel.precedes.unit.o009.quantecon.ctmc.stationarity-ergodicity.unit.o009.random.poisson.general",
            "rel.depends-on.poisson-general.quantecon-poisson",
            "rel.depends-on.poisson-general.probability-measure-space",
            "rel.teaches.poisson-general.random-measure",
            "rel.teaches.poisson-general.moments",
            "rel.teaches.poisson-general.conditional-law.dst1",
            "rel.teaches.poisson-general.conditional-law.dst2",
            "rel.teaches.poisson-general.conditional-law.dst3",
            "rel.teaches.poisson-general.thinning-superposition.spl1",
            "rel.teaches.poisson-general.thinning-superposition.spl2",
            "rel.teaches.poisson-general.nonhomogeneous",
            "rel.teaches.poisson-general.nearest-neighbor.nea1",
            "rel.teaches.poisson-general.nearest-neighbor.nea2",
            *(
                f"rel.assesses.poisson-general.exe{index}"
                for index in range(1, 7)
            ),
            *(
                f"rel.solves.poisson-general.exe{index}"
                for index in range(1, 7)
            ),
        }
    )
    required_relations.update(
        {
            "rel.contains.course.o009.unit.o009.random.brown.standard",
            "rel.precedes.unit.o009.random.poisson.general.unit.o009.random.brown.standard",
            "rel.depends-on.brown-standard.prob-processes",
            "rel.depends-on.brown-standard.prob-stop",
            "rel.depends-on.brown-standard.markov-general",
            "rel.depends-on.brown-standard.martingales-introduction",
            "rel.depends-on.brown-standard.o006",
            "rel.depends-on.brown-standard.apps-js",
            "rel.depends-on.brown-standard.distributions-js",
            "rel.teaches.brown-standard.definition",
            "rel.teaches.brown-standard.gaussian-laws",
            "rel.teaches.brown-standard.scaling-irregularity",
            "rel.teaches.brown-standard.strong-markov-reflection",
            "rel.teaches.brown-standard.hitting-maximum",
            "rel.teaches.brown-standard.arcsine-law",
            "rel.teaches.brown-standard.iterated-logarithm",
            "rel.assesses.brown-standard.div-050",
            "rel.contains.unit.o009.random.brown.standard.downstream-correction-note",
            "rel.contains.unit.o009.random.brown.standard.lil1.lil1-consequence",
            "rel.contains.unit.o009.random.brown.standard.div-050.exercise-solution",
            "rel.solves.brown-standard.div-050",
        }
    )
    required_relations.update(
        {
            "rel.contains.course.o009.unit.o009.random.brown.drift",
            "rel.precedes.unit.o009.random.brown.standard.unit.o009.random.brown.drift",
            "rel.depends-on.brown-drift.brown-standard",
            "rel.depends-on.brown-drift.prob-processes",
            "rel.depends-on.brown-drift.prob-stop",
            "rel.depends-on.brown-drift.markov-general",
            *(
                f"rel.teaches.brown-drift.characterization.{local_id}"
                for local_id in ("def1", "def3", "dis1", "dis2", "trn1", "trn2", "trn3")
            ),
            "rel.assesses.brown-drift.def2",
            "rel.teaches.brown-drift.transition-density.mar1",
            "rel.teaches.brown-drift.diffusion-equations.mar2",
            "rel.teaches.brown-drift.strong-markov.mar3",
            "rel.contains.unit.o009.random.brown.drift.downstream-correction-note",
            "rel.contains.unit.o009.random.brown.drift.offline-lab",
            "rel.depends-on.brown-drift-offline-lab.javascript",
            "rel.executes.brown-drift-offline-lab.javascript",
            "rel.assesses.brown-drift-offline-lab.terminal-law",
            "rel.contains.unit.o009.random.brown.drift.mastery",
            "rel.contains.brown-drift-mastery.exercise",
            "rel.contains.brown-drift-mastery.hint",
            "rel.contains.brown-drift-mastery.solution",
            "rel.hints.brown-drift-mastery",
            "rel.solves.brown-drift-mastery",
            "rel.assesses.brown-drift-mastery",
            "rel.contains.brown-drift-mar3.strong-markov-proof",
            "rel.teaches.brown-drift.strong-markov-proof",
        }
    )
    required_relations.update(
        {
            "rel.contains.course.o009.unit.o009.random.brown.bridge",
            "rel.precedes.unit.o009.random.brown.drift.unit.o009.random.brown.bridge",
            "rel.depends-on.brown-bridge.brown-standard",
            "rel.depends-on.brown-bridge.prob-processes",
            "rel.depends-on.brown-bridge.expect-kernels",
            *(
                f"rel.teaches.brown-bridge.constructions.{local_id}"
                for local_id in (
                    "def1",
                    "def2",
                    "def5",
                    "def7",
                    "def8",
                    "def6",
                    "div-009",
                    "gen1",
                    "gen2",
                )
            ),
            *(
                f"rel.assesses.brown-bridge.online-app.{local_id}"
                for local_id in ("def3", "def4")
            ),
            *(
                f"rel.teaches.brown-bridge.empirical-process.{local_id}"
                for local_id in ("edf1", "edf2")
            ),
            "rel.contains.unit.o009.random.brown.bridge.downstream-correction-note",
            "rel.contains.unit.o009.random.brown.bridge.offline-lab",
            "rel.depends-on.brown-bridge-offline-lab.definition",
            "rel.depends-on.brown-bridge-offline-lab.javascript",
            "rel.executes.brown-bridge-offline-lab.javascript",
            "rel.assesses.brown-bridge-offline-lab.marginal-law",
            "rel.contains.unit.o009.random.brown.bridge.mastery",
            "rel.depends-on.brown-bridge-mastery.definition",
            "rel.contains.brown-bridge-mastery.process-limit-warning",
            "rel.contains.brown-bridge-mastery.exercise",
            "rel.contains.brown-bridge-mastery.hint",
            "rel.contains.brown-bridge-mastery.solution",
            "rel.precedes.brown-bridge-mastery.process-limit-warning.exercise",
            "rel.precedes.brown-bridge-mastery.exercise.hint",
            "rel.precedes.brown-bridge-mastery.hint.solution",
            "rel.hints.brown-bridge-mastery",
            "rel.solves.brown-bridge-mastery",
            "rel.teaches.brown-bridge.process-limit-warning",
            "rel.assesses.brown-bridge-mastery",
        }
    )
    required_relations.update(
        {
            "rel.contains.course.o009.unit.o009.random.brown.geometric",
            "rel.precedes.unit.o009.random.brown.bridge.unit.o009.random.brown.geometric",
            "rel.depends-on.brown-geometric.brown-standard",
            "rel.depends-on.brown-geometric.brown-drift",
            "rel.depends-on.brown-geometric.prob-processes",
            "rel.depends-on.brown-geometric.martingales-introduction",
            *(
                f"rel.teaches.brown-geometric.characterization.{local_id}"
                for local_id in ("def1", "def2")
            ),
            *(
                f"rel.teaches.brown-geometric.laws.{local_id}"
                for local_id in ("dst1", "dst3", "dist4", "mom1", "mom2")
            ),
            *(
                f"rel.teaches.brown-geometric.asymptotics.{local_id}"
                for local_id in ("mom3", "prp1", "div-014")
            ),
            *(
                f"rel.assesses.brown-geometric.online-app.{local_id}"
                for local_id in ("def3", "dst2", "mom4", "mom5")
            ),
            "rel.contains.unit.o009.random.brown.geometric.downstream-correction-note",
            "rel.contains.unit.o009.random.brown.geometric.offline-lab",
            "rel.depends-on.brown-geometric-offline-lab.definition",
            "rel.depends-on.brown-geometric-offline-lab.javascript",
            "rel.executes.brown-geometric-offline-lab.javascript",
            "rel.assesses.brown-geometric-offline-lab.terminal-law",
            "rel.contains.unit.o009.random.brown.geometric.mastery",
            "rel.depends-on.brown-geometric-mastery.definition",
            "rel.depends-on.brown-geometric-mastery.moments",
            "rel.contains.brown-geometric-mastery.exercise",
            "rel.contains.brown-geometric-mastery.hint",
            "rel.contains.brown-geometric-mastery.solution",
            "rel.precedes.brown-geometric-mastery.exercise.hint",
            "rel.precedes.brown-geometric-mastery.hint.solution",
            "rel.hints.brown-geometric-mastery",
            "rel.solves.brown-geometric-mastery",
            "rel.assesses.brown-geometric-mastery",
        }
    )
    missing = required_relations - relation_ids
    if missing:
        raise RuntimeError(f"missing required graph relations: {sorted(missing)}")
    records_by_id = {item["id"]: item for item in records}
    for exercise_id in ("com1", "com2", "com3", "com4", "ind3", "dbl4", "dbl6"):
        stable_id = f"unit.o009.random.markov.discrete.{exercise_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "exercise":
            raise RuntimeError(f"Discrete exercise role missing: {stable_id}")
    for details_id in (
        "details-015",
        "details-016",
        "details-017",
        "details-018",
        "details-025",
        "details-028",
        "details-030",
    ):
        stable_id = f"unit.o009.random.markov.discrete.{details_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "solution":
            raise RuntimeError(f"Discrete solution role missing: {stable_id}")
    for exercise_id in ("fin1", "fin2", "fin3"):
        stable_id = f"unit.o009.random.markov.recurrence.{exercise_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "exercise":
            raise RuntimeError(f"Recurrence exercise role missing: {stable_id}")
    for details_id in ("details-025", "details-026", "details-027"):
        stable_id = f"unit.o009.random.markov.recurrence.{details_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "solution":
            raise RuntimeError(f"Recurrence solution role missing: {stable_id}")
    for exercise_id in ("fin1", "fin3"):
        stable_id = f"unit.o009.random.markov.periodicity.{exercise_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "exercise":
            raise RuntimeError(f"Periodicity exercise role missing: {stable_id}")
    for details_id in ("details-004", "details-005"):
        stable_id = f"unit.o009.random.markov.periodicity.{details_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "solution":
            raise RuntimeError(f"Periodicity solution role missing: {stable_id}")
    for exercise_id in ("div-023", "fin1", "fin2", "fin3", "fin4", "fin5"):
        stable_id = f"unit.o009.random.markov.limiting.{exercise_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "exercise":
            raise RuntimeError(f"Limiting exercise role missing: {stable_id}")
    for details_id in ("details-018", "details-019", "details-020", "details-021", "details-022"):
        stable_id = f"unit.o009.random.markov.limiting.{details_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "solution":
            raise RuntimeError(f"Limiting solution role missing: {stable_id}")
    for exercise_id in ("exe1", "exe2", "exe3", "exe4", "exe5", "exe6"):
        stable_id = f"unit.o009.random.poisson.general.{exercise_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "exercise":
            raise RuntimeError(f"General-space Poisson exercise role missing: {stable_id}")
    for details_id in (
        "details-008",
        "details-009",
        "details-010",
        "details-011",
        "details-012",
        "details-013",
    ):
        stable_id = f"unit.o009.random.poisson.general.{details_id}"
        if records_by_id[stable_id]["payload"].get("unit_kind") != "solution":
            raise RuntimeError(f"General-space Poisson solution role missing: {stable_id}")
    if "unit.o009.random.poisson.general.exe7" in records_by_id:
        raise RuntimeError(
            "nested ol#exe7 must not be exported as a seventh top-level Poisson exercise"
        )
    brown_page_id = "unit.o009.random.brown.standard"
    brown_exercise_id = f"{brown_page_id}.div-050"
    brown_solution_id = "unit.o009.original.brown.standard.exercise-solution"
    brown_lil_addition_id = "unit.o009.original.brown.standard.lil1-consequence"
    brown_exercise = records_by_id.get(brown_exercise_id)
    brown_solution = records_by_id.get(brown_solution_id)
    brown_lil_addition = records_by_id.get(brown_lil_addition_id)
    if brown_exercise is None or brown_exercise["payload"].get("unit_kind") != "exercise":
        raise RuntimeError("Brown final computational div lacks its exercise role")
    if (
        brown_solution is None
        or brown_solution["parent_id"] != brown_exercise_id
        or brown_solution["payload"].get("unit_kind") != "solution"
        or brown_solution["payload"].get("source_supplied") is not False
        or brown_solution["source_target_relationship"] != "authored"
        or brown_solution["rights_id"] != "rights.o009.original.cc-by-4.0"
    ):
        raise RuntimeError(
            "Brown additive solution is not explicitly separated as authored CC BY 4.0 material"
        )
    if (
        brown_lil_addition is None
        or brown_lil_addition["parent_id"] != f"{brown_page_id}.lil1"
        or brown_lil_addition["source_target_relationship"] != "authored"
        or brown_lil_addition["rights_id"] != "rights.o009.original.cc-by-4.0"
    ):
        raise RuntimeError("Brown two-sided LIL consequence lacks its original-material binding")
    brown_generic_unit_divs = [
        item
        for item in records
        if item["record_type"] == "unit"
        and item["id"].startswith(f"{brown_page_id}.")
        and "unit" in item["payload"].get("classes", [])
    ]
    brown_generic_disclosures = [
        item
        for item in records
        if item["record_type"] == "unit"
        and item["id"].startswith(f"{brown_page_id}.details-")
    ]
    brown_generic_segments = [
        item
        for item in records
        if item["record_type"] == "segment"
        and item["id"].startswith("segment.o009.random.brown.standard.")
    ]
    brown_original_segments = [
        item
        for item in records
        if item["record_type"] == "segment"
        and item["id"].startswith("segment.o009.original.brown.standard.")
    ]
    if (
        len(brown_generic_unit_divs) != 50
        or len(brown_generic_disclosures) != 28
        or len(brown_generic_segments) != 207
        or len(brown_original_segments) != 7
    ):
        raise RuntimeError(
            "Brown backend topology differs from 50 source unit divs, 28 source disclosures, 207 source segments, and 7 explicit addition segments"
        )
    if any(
        forbidden_id in records_by_id
        for forbidden_id in (
            f"{brown_page_id}.details-029",
            f"{brown_page_id}.details-030",
        )
    ):
        raise RuntimeError(
            "Brown reader-only disclosures were incorrectly represented as Random source content"
        )
    drift_page_id = "unit.o009.random.brown.drift"
    expected_drift_roles = {
        "def1": "definition",
        "def2": "application",
        "def3": "characterization",
        "dis1": "theorem",
        "dis2": "theorem",
        "trn1": "transformation-rule",
        "trn2": "scaling-law",
        "trn3": "stationary-increment-theorem",
        "mar1": "transition-density-theorem",
        "mar2": "diffusion-equation-theorem",
        "mar3": "strong-markov-theorem",
    }
    for local_id, expected_role in expected_drift_roles.items():
        stable_id = f"{drift_page_id}.{local_id}"
        if records_by_id.get(stable_id, {}).get("payload", {}).get(
            "unit_kind"
        ) != expected_role:
            raise RuntimeError(
                f"Brown Drift source unit lacks its exact semantic role: {stable_id}"
            )
    for index in range(1, 8):
        stable_id = f"{drift_page_id}.details-{index:03d}"
        if records_by_id.get(stable_id, {}).get("payload", {}).get(
            "unit_kind"
        ) != "proof":
            raise RuntimeError(
                f"Brown Drift source disclosure lacks its proof role: {stable_id}"
            )
    drift_generic_unit_divs = [
        item
        for item in records
        if item["record_type"] == "unit"
        and item["id"].startswith(f"{drift_page_id}.")
        and "unit" in item["payload"].get("classes", [])
    ]
    drift_generic_disclosures = [
        item
        for item in records
        if item["record_type"] == "unit"
        and item["id"].startswith(f"{drift_page_id}.details-")
    ]
    drift_generic_segments = [
        item
        for item in records
        if item["record_type"] == "segment"
        and item["id"].startswith("segment.o009.random.brown.drift.")
    ]
    drift_original_segments = [
        item
        for item in records
        if item["record_type"] == "segment"
        and item["id"].startswith("segment.o009.original.brown.drift.")
    ]
    if (
        len(drift_generic_unit_divs) != 11
        or len(drift_generic_disclosures) != 7
        or len(drift_generic_segments) != 68
        or len(drift_original_segments) != 38
    ):
        raise RuntimeError(
            "Brown Drift backend topology differs from 11 source unit divs, 7 source disclosures, 68 source segments, and 38 explicit addition segments"
        )
    if any(
        f"{drift_page_id}.details-{index:03d}" in records_by_id
        for index in range(8, 11)
    ):
        raise RuntimeError(
            "Brown Drift reader-only disclosures were incorrectly represented as Random source content"
        )
    drift_rights_id = "rights.o009.brown-drift-original.cc-by-4.0"
    expected_drift_original_roles = {
        "unit.o009.original.brown.drift.offline-lab": "computational-lab",
        "unit.o009.original.brown.drift.mastery": "mastery-sequence",
        "unit.o009.original.brown.drift.mastery.exercise": "exercise",
        "unit.o009.original.brown.drift.mastery.hint": "hint",
        "unit.o009.original.brown.drift.mastery.solution": "solution",
        "unit.o009.original.brown.drift.strong-markov-proof": "proof",
    }
    for stable_id, expected_role in expected_drift_original_roles.items():
        item = records_by_id.get(stable_id)
        if (
            item is None
            or item["payload"].get("unit_kind") != expected_role
            or item["source_target_relationship"] != "authored"
            or item["rights_id"] != drift_rights_id
            or item["payload"].get("source_supplied") is not False
        ):
            raise RuntimeError(
                f"Brown Drift original unit lacks its authored role/rights boundary: {stable_id}"
            )
    drift_app = records_by_id.get("asset.o009.brown-drift-offline-js")
    if (
        drift_app is None
        or drift_app["record_type"] != "asset"
        or drift_app["parent_id"]
        != "unit.o009.original.brown.drift.offline-lab"
        or drift_app["rights_id"] != drift_rights_id
        or drift_app["source_target_relationship"] != "copies"
        or drift_app["payload"].get("deterministic_seeded") is not True
    ):
        raise RuntimeError("Brown Drift offline app lacks its authored asset binding")
    drift_note = records_by_id.get(
        "segment.o009.original.brown.drift.downstream-correction-note"
    )
    if (
        drift_note is None
        or drift_note["parent_id"] != drift_page_id
        or drift_note["source_target_relationship"] != "authored"
        or drift_note["rights_id"] != drift_rights_id
    ):
        raise RuntimeError("Brown Drift downstream note lacks its original-material binding")
    bridge_page_id = "unit.o009.random.brown.bridge"
    expected_bridge_roles = {
        "def1": "definition",
        "def2": "construction-theorem",
        "def3": "application",
        "def4": "application",
        "def5": "inverse-construction-theorem",
        "def7": "time-change-construction-theorem",
        "def8": "inverse-time-change-theorem",
        "def6": "regular-conditioning-theorem",
        "div-009": "stochastic-integral-construction-theorem",
        "gen1": "construction-theorem",
        "gen2": "characterization",
        "edf1": "estimation-theorem",
        "edf2": "covariance-theorem",
    }
    for local_id, expected_role in expected_bridge_roles.items():
        stable_id = f"{bridge_page_id}.{local_id}"
        if records_by_id.get(stable_id, {}).get("payload", {}).get(
            "unit_kind"
        ) != expected_role:
            raise RuntimeError(
                f"Brown Bridge source unit lacks its exact semantic role: {stable_id}"
            )
    for index in range(1, 8):
        stable_id = f"{bridge_page_id}.details-{index:03d}"
        if records_by_id.get(stable_id, {}).get("payload", {}).get(
            "unit_kind"
        ) != "proof":
            raise RuntimeError(
                f"Brown Bridge source disclosure lacks its proof role: {stable_id}"
            )
    bridge_generic_unit_divs = [
        item
        for item in records
        if item["record_type"] == "unit"
        and item["id"].startswith(f"{bridge_page_id}.")
        and "unit" in item["payload"].get("classes", [])
    ]
    bridge_generic_disclosures = [
        item
        for item in records
        if item["record_type"] == "unit"
        and item["id"].startswith(f"{bridge_page_id}.details-")
    ]
    bridge_generic_segments = [
        item
        for item in records
        if item["record_type"] == "segment"
        and item["id"].startswith("segment.o009.random.brown.bridge.")
    ]
    bridge_original_segments = [
        item
        for item in records
        if item["record_type"] == "segment"
        and item["id"].startswith("segment.o009.original.brown.bridge.")
    ]
    if (
        len(bridge_generic_unit_divs) != 13
        or len(bridge_generic_disclosures) != 7
        or len(bridge_generic_segments) != 99
        or len(bridge_original_segments) != 33
    ):
        raise RuntimeError(
            "Brown Bridge backend topology differs from 13 source unit divs, "
            "7 source disclosures, 99 source segments, and 33 explicit "
            "addition segments"
        )
    if any(
        f"{bridge_page_id}.details-{index:03d}" in records_by_id
        for index in range(8, 10)
    ):
        raise RuntimeError(
            "Brown Bridge reader-only disclosures were incorrectly represented "
            "as Random source content"
        )
    bridge_rights_id = "rights.o009.brown-bridge-original.cc-by-4.0"
    expected_bridge_original_roles = {
        "unit.o009.original.brown.bridge.offline-lab": "computational-lab",
        "unit.o009.original.brown.bridge.mastery": "mastery-sequence",
        "unit.o009.original.brown.bridge.mastery.process-limit-warning": (
            "process-limit-warning"
        ),
        "unit.o009.original.brown.bridge.mastery.exercise": "exercise",
        "unit.o009.original.brown.bridge.mastery.hint": "hint",
        "unit.o009.original.brown.bridge.mastery.solution": "solution",
    }
    for stable_id, expected_role in expected_bridge_original_roles.items():
        item = records_by_id.get(stable_id)
        if (
            item is None
            or item["payload"].get("unit_kind") != expected_role
            or item["source_target_relationship"] != "authored"
            or item["rights_id"] != bridge_rights_id
            or item["payload"].get("source_supplied") is not False
        ):
            raise RuntimeError(
                "Brown Bridge original unit lacks its authored role/rights "
                f"boundary: {stable_id}"
            )
    bridge_app = records_by_id.get("asset.o009.brown-bridge-offline-js")
    if (
        bridge_app is None
        or bridge_app["record_type"] != "asset"
        or bridge_app["parent_id"]
        != "unit.o009.original.brown.bridge.offline-lab"
        or bridge_app["rights_id"] != bridge_rights_id
        or bridge_app["source_target_relationship"] != "copies"
        or bridge_app["payload"].get("deterministic_seeded") is not True
    ):
        raise RuntimeError("Brown Bridge offline app lacks its authored asset binding")
    bridge_note = records_by_id.get(
        "segment.o009.original.brown.bridge.downstream-correction-note"
    )
    if (
        bridge_note is None
        or bridge_note["parent_id"] != bridge_page_id
        or bridge_note["source_target_relationship"] != "authored"
        or bridge_note["rights_id"] != bridge_rights_id
        or any(
            item["rights_id"] != bridge_rights_id
            or item["source_target_relationship"] != "authored"
            for item in bridge_original_segments
        )
    ):
        raise RuntimeError(
            "Brown Bridge authored segments lack their original-material binding"
        )
    geometric_page_id = "unit.o009.random.brown.geometric"
    expected_geometric_roles = {
        "def1": "definition",
        "def2": "stochastic-differential-equation",
        "def3": "application",
        "dst1": "distribution-theorem",
        "dst2": "application",
        "dst3": "distribution-function-theorem",
        "dist4": "quantile-theorem",
        "mom1": "moment-theorem",
        "mom2": "moment-corollary",
        "mom3": "mean-asymptotics",
        "mom4": "application",
        "mom5": "application",
        "prp1": "path-asymptotics",
        "div-014": "martingale-theorem",
    }
    for local_id, expected_role in expected_geometric_roles.items():
        stable_id = f"{geometric_page_id}.{local_id}"
        if records_by_id.get(stable_id, {}).get("payload", {}).get(
            "unit_kind"
        ) != expected_role:
            raise RuntimeError(
                f"Brown Geometric source unit lacks its exact semantic role: {stable_id}"
            )
    for index in range(1, 7):
        stable_id = f"{geometric_page_id}.details-{index:03d}"
        if records_by_id.get(stable_id, {}).get("payload", {}).get(
            "unit_kind"
        ) != "proof":
            raise RuntimeError(
                f"Brown Geometric source disclosure lacks its proof role: {stable_id}"
            )
    geometric_generic_unit_divs = [
        item
        for item in records
        if item["record_type"] == "unit"
        and item["id"].startswith(f"{geometric_page_id}.")
        and "unit" in item["payload"].get("classes", [])
    ]
    geometric_generic_disclosures = [
        item
        for item in records
        if item["record_type"] == "unit"
        and item["id"].startswith(f"{geometric_page_id}.details-")
    ]
    geometric_generic_segments = [
        item
        for item in records
        if item["record_type"] == "segment"
        and item["id"].startswith("segment.o009.random.brown.geometric.")
    ]
    geometric_original_segments = [
        item
        for item in records
        if item["record_type"] == "segment"
        and item["id"].startswith("segment.o009.original.brown.geometric.")
    ]
    if (
        len(geometric_generic_unit_divs) != 14
        or len(geometric_generic_disclosures) != 6
        or len(geometric_generic_segments) != 67
        or len(geometric_original_segments) != 41
    ):
        raise RuntimeError(
            "Brown Geometric backend topology differs from 14 source unit divs, "
            "6 source disclosures, 67 source segments, and 41 explicit "
            "addition segments"
        )
    if any(
        f"{geometric_page_id}.details-{index:03d}" in records_by_id
        for index in range(7, 9)
    ):
        raise RuntimeError(
            "Brown Geometric reader-only disclosures were incorrectly represented "
            "as Random source content"
        )
    geometric_rights_id = "rights.o009.brown-geometric-original.cc-by-4.0"
    expected_geometric_original_roles = {
        "unit.o009.original.brown.geometric.offline-lab": "computational-lab",
        "unit.o009.original.brown.geometric.mastery": "mastery-sequence",
        "unit.o009.original.brown.geometric.mastery.exercise": "exercise",
        "unit.o009.original.brown.geometric.mastery.hint": "hint",
        "unit.o009.original.brown.geometric.mastery.solution": "solution",
    }
    for stable_id, expected_role in expected_geometric_original_roles.items():
        item = records_by_id.get(stable_id)
        if (
            item is None
            or item["payload"].get("unit_kind") != expected_role
            or item["source_target_relationship"] != "authored"
            or item["rights_id"] != geometric_rights_id
            or item["payload"].get("source_supplied") is not False
        ):
            raise RuntimeError(
                "Brown Geometric original unit lacks its authored role/rights "
                f"boundary: {stable_id}"
            )
    geometric_app = records_by_id.get("asset.o009.geometric-brownian-offline-js")
    if (
        geometric_app is None
        or geometric_app["record_type"] != "asset"
        or geometric_app["parent_id"]
        != "unit.o009.original.brown.geometric.offline-lab"
        or geometric_app["rights_id"] != geometric_rights_id
        or geometric_app["source_target_relationship"] != "copies"
        or geometric_app["payload"].get("deterministic_seeded") is not True
    ):
        raise RuntimeError(
            "Brown Geometric offline app lacks its authored asset binding"
        )
    geometric_note = records_by_id.get(
        "segment.o009.original.brown.geometric.downstream-correction-note"
    )
    if (
        geometric_note is None
        or geometric_note["parent_id"] != geometric_page_id
        or geometric_note["source_target_relationship"] != "authored"
        or geometric_note["rights_id"] != geometric_rights_id
        or any(
            item["rights_id"] != geometric_rights_id
            or item["source_target_relationship"] != "authored"
            for item in geometric_original_segments
        )
    ):
        raise RuntimeError(
            "Brown Geometric authored segments lack their original-material binding"
        )
    two_state_app = records_by_id["unit.o009.original.markov.two-state-simulator"]
    if (
        two_state_app["payload"].get("unit_kind") != "program"
        or two_state_app["payload"].get("tool_kind") != "interactive-simulator"
        or two_state_app["rights_id"] != "rights.o009.two-state-app.cc-by-4.0"
        or two_state_app["source_target_relationship"] != "authored"
    ):
        raise RuntimeError("two-state app lacks its authored program/tool role and rights binding")
    for item in records:
        if item["record_type"] in {"unit", "segment"} and item.get("path") == "labs/01-konvergensi-monte-carlo.Rmd":
            if item["source_target_relationship"] == "adapts" and item["rights_id"] != "rights.o009.indonesian-adaptation.cc-by-4.0":
                raise RuntimeError(f"adapted Indonesian bytes mislabeled: {item['id']}")
        if item["record_type"] in {"unit", "segment"} and item.get("path") == "labs/02-simulasi-rantai-markov.Rmd":
            expected_rights = (
                "rights.o009.markov.original.cc-by-4.0"
                if item["source_target_relationship"] == "authored"
                else "rights.o009.markov.indonesian-adaptation.cc-by-4.0"
            )
            if item["rights_id"] != expected_rights:
                raise RuntimeError(f"Markov lab bytes mislabeled: {item['id']}")
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
        writer = csv.DictWriter(
            stream, fieldnames=fields, lineterminator=CSV_LINE_TERMINATOR
        )
        writer.writeheader()
        writer.writerows(rows)


def build() -> None:
    lab_text = require_file(LAB).decode("utf-8")
    markov_lab_text = require_file(LAB_MARKOV).decode("utf-8")
    convergence_modes_lab_text = require_file(LAB_CONVERGENCE_MODES).decode("utf-8")
    conditional_martingale_lab_text = require_file(
        LAB_CONDITIONAL_MARTINGALE
    ).decode("utf-8")
    brownian_diagnostics_lab_text = require_file(
        LAB_BROWNIAN_DIAGNOSTICS
    ).decode("utf-8")
    entities = fixed_entities(
        lab_text,
        markov_lab_text,
        convergence_modes_lab_text,
        conditional_martingale_lab_text,
        brownian_diagnostics_lab_text,
    )
    html, html_segments, html_relations = html_entities()
    quantecon, quantecon_segments, quantecon_relations = quantecon_entities("memoryless")
    quantecon_poisson, quantecon_poisson_segments, quantecon_poisson_relations = quantecon_entities("poisson")
    existing_ids = {item["id"] for item in quantecon}
    quantecon.extend(item for item in quantecon_poisson if item["id"] not in existing_ids)
    existing_segment_ids = {item["id"] for item in quantecon_segments}
    quantecon_segments.extend(item for item in quantecon_poisson_segments if item["id"] not in existing_segment_ids)
    existing_relation_ids = {item["relation_id"] for item in quantecon_relations}
    quantecon_relations.extend(item for item in quantecon_poisson_relations if item["relation_id"] not in existing_relation_ids)
    (
        quantecon_markov_prop,
        quantecon_markov_prop_segments,
        quantecon_markov_prop_relations,
    ) = quantecon_entities("markov_prop")
    existing_ids = {item["id"] for item in quantecon}
    quantecon.extend(
        item for item in quantecon_markov_prop if item["id"] not in existing_ids
    )
    existing_segment_ids = {item["id"] for item in quantecon_segments}
    quantecon_segments.extend(
        item
        for item in quantecon_markov_prop_segments
        if item["id"] not in existing_segment_ids
    )
    existing_relation_ids = {item["relation_id"] for item in quantecon_relations}
    quantecon_relations.extend(
        item
        for item in quantecon_markov_prop_relations
        if item["relation_id"] not in existing_relation_ids
    )
    (
        quantecon_kolmogorov_bwd,
        quantecon_kolmogorov_bwd_segments,
        quantecon_kolmogorov_bwd_relations,
    ) = quantecon_entities("kolmogorov_bwd")
    existing_ids = {item["id"] for item in quantecon}
    quantecon.extend(
        item for item in quantecon_kolmogorov_bwd if item["id"] not in existing_ids
    )
    existing_segment_ids = {item["id"] for item in quantecon_segments}
    quantecon_segments.extend(
        item
        for item in quantecon_kolmogorov_bwd_segments
        if item["id"] not in existing_segment_ids
    )
    existing_relation_ids = {item["relation_id"] for item in quantecon_relations}
    quantecon_relations.extend(
        item
        for item in quantecon_kolmogorov_bwd_relations
        if item["relation_id"] not in existing_relation_ids
    )
    (
        quantecon_kolmogorov_fwd,
        quantecon_kolmogorov_fwd_segments,
        quantecon_kolmogorov_fwd_relations,
    ) = quantecon_entities("kolmogorov_fwd")
    existing_ids = {item["id"] for item in quantecon}
    quantecon.extend(
        item for item in quantecon_kolmogorov_fwd if item["id"] not in existing_ids
    )
    existing_segment_ids = {item["id"] for item in quantecon_segments}
    quantecon_segments.extend(
        item
        for item in quantecon_kolmogorov_fwd_segments
        if item["id"] not in existing_segment_ids
    )
    existing_relation_ids = {item["relation_id"] for item in quantecon_relations}
    quantecon_relations.extend(
        item
        for item in quantecon_kolmogorov_fwd_relations
        if item["relation_id"] not in existing_relation_ids
    )
    (
        quantecon_generators,
        quantecon_generators_segments,
        quantecon_generators_relations,
    ) = quantecon_entities("generators")
    existing_ids = {item["id"] for item in quantecon}
    quantecon.extend(
        item for item in quantecon_generators if item["id"] not in existing_ids
    )
    existing_segment_ids = {item["id"] for item in quantecon_segments}
    quantecon_segments.extend(
        item
        for item in quantecon_generators_segments
        if item["id"] not in existing_segment_ids
    )
    existing_relation_ids = {item["relation_id"] for item in quantecon_relations}
    quantecon_relations.extend(
        item
        for item in quantecon_generators_relations
        if item["relation_id"] not in existing_relation_ids
    )
    (
        quantecon_uc_mc_semigroups,
        quantecon_uc_mc_semigroups_segments,
        quantecon_uc_mc_semigroups_relations,
    ) = quantecon_entities("uc_mc_semigroups")
    existing_ids = {item["id"] for item in quantecon}
    quantecon.extend(
        item
        for item in quantecon_uc_mc_semigroups
        if item["id"] not in existing_ids
    )
    existing_segment_ids = {item["id"] for item in quantecon_segments}
    quantecon_segments.extend(
        item
        for item in quantecon_uc_mc_semigroups_segments
        if item["id"] not in existing_segment_ids
    )
    existing_relation_ids = {item["relation_id"] for item in quantecon_relations}
    quantecon_relations.extend(
        item
        for item in quantecon_uc_mc_semigroups_relations
        if item["relation_id"] not in existing_relation_ids
    )
    (
        quantecon_ergodicity,
        quantecon_ergodicity_segments,
        quantecon_ergodicity_relations,
    ) = quantecon_entities("ergodicity")
    existing_ids = {item["id"] for item in quantecon}
    quantecon.extend(
        item for item in quantecon_ergodicity if item["id"] not in existing_ids
    )
    existing_segment_ids = {item["id"] for item in quantecon_segments}
    quantecon_segments.extend(
        item
        for item in quantecon_ergodicity_segments
        if item["id"] not in existing_segment_ids
    )
    existing_relation_ids = {item["relation_id"] for item in quantecon_relations}
    quantecon_relations.extend(
        item
        for item in quantecon_ergodicity_relations
        if item["relation_id"] not in existing_relation_ids
    )
    (
        original_bridge,
        original_bridge_segments,
        original_bridge_relations,
        original_bridge_corrections,
    ) = original_bridge_entities()
    (
        original_bridge_02,
        original_bridge_02_segments,
        original_bridge_02_relations,
        original_bridge_02_corrections,
    ) = original_bridge_02_entities()
    (
        original_bridge_03,
        original_bridge_03_segments,
        original_bridge_03_relations,
        original_bridge_03_corrections,
    ) = original_bridge_03_entities()
    (
        original_bridge_04,
        original_bridge_04_segments,
        original_bridge_04_relations,
        original_bridge_04_corrections,
    ) = original_bridge_04_entities()
    lab, lab_segments, lab_relations, aliases, translations, corrections = lab_entities()
    (
        markov_lab,
        markov_lab_segments,
        markov_lab_relations,
        markov_aliases,
        markov_translations,
        markov_corrections,
    ) = markov_lab_entities()
    (
        convergence_modes_lab,
        convergence_modes_lab_segments,
        convergence_modes_lab_relations,
        convergence_modes_aliases,
        convergence_modes_translations,
        convergence_modes_corrections,
    ) = convergence_modes_lab_entities()
    (
        conditional_martingale_lab,
        conditional_martingale_lab_segments,
        conditional_martingale_lab_relations,
        conditional_martingale_aliases,
        conditional_martingale_translations,
        conditional_martingale_corrections,
    ) = conditional_martingale_lab_entities()
    (
        brownian_diagnostics_lab,
        brownian_diagnostics_lab_segments,
        brownian_diagnostics_lab_relations,
        brownian_diagnostics_aliases,
        brownian_diagnostics_translations,
        brownian_diagnostics_corrections,
    ) = brownian_diagnostics_lab_entities()
    aliases.extend(markov_aliases)
    aliases.extend(convergence_modes_aliases)
    aliases.extend(conditional_martingale_aliases)
    aliases.extend(brownian_diagnostics_aliases)
    translations.extend(markov_translations)
    translations.extend(convergence_modes_translations)
    translations.extend(conditional_martingale_translations)
    translations.extend(brownian_diagnostics_translations)
    corrections.extend(markov_corrections)
    corrections.extend(convergence_modes_corrections)
    corrections.extend(conditional_martingale_corrections)
    corrections.extend(brownian_diagnostics_corrections)
    corrections.extend(original_bridge_corrections)
    corrections.extend(original_bridge_02_corrections)
    corrections.extend(original_bridge_03_corrections)
    corrections.extend(original_bridge_04_corrections)
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
    corrections.extend(
        [
            {
                "correction_id": "correction.o009.original.brown.standard.downstream-correction-note",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.standard",
                "target_id": "segment.o009.original.brown.standard.downstream-correction-note",
                "description": "Add a compact reader note identifying the guarded mathematical and accessibility repairs applied downstream.",
                "evidence": "build/site/brown/Standard.html#brown-standard-downstream-corrections",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.standard.exercise-solution",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.standard.div-050",
                "target_id": "unit.o009.original.brown.standard.exercise-solution",
                "description": "Add an independently authored CC BY 4.0 worked solution to the source-unsolved final Gaussian-process exercise.",
                "evidence": "build/site/brown/Standard.html#brown-standard-exercise-solution",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.drift.downstream-correction-note",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.drift",
                "target_id": "segment.o009.original.brown.drift.downstream-correction-note",
                "description": "Add a compact note disclosing the guarded Drift mathematical repairs and separately licensed reader additions.",
                "evidence": "build/site/brown/Drift.html#brown-drift-downstream-corrections",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.drift.offline-lab",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.drift.def2",
                "target_id": "unit.o009.original.brown.drift.offline-lab",
                "description": "Add a deterministic accessible offline simulation with a nonvisual theoretical/empirical moment comparison.",
                "evidence": "build/site/brown/Drift.html#brown-drift-offline-lab",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.drift.offline-app",
                "change_kind": "original-addition",
                "source_id": "unit.o009.original.brown.drift.offline-lab",
                "target_id": "asset.o009.brown-drift-offline-js",
                "description": "Bind the offline Drift laboratory to its byte-identical authored JavaScript runtime.",
                "evidence": "source/original/brown-drift-offline.js; build/site/apps/brown-drift-offline.js",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.drift.mastery",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.drift.dis1",
                "target_id": "unit.o009.original.brown.drift.mastery",
                "description": "Add a complete CC BY 4.0 exercise, hint, and worked solution for joint and conditional Gaussian laws with drift.",
                "evidence": "build/site/brown/Drift.html#brown-drift-mastery",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.drift.strong-markov-proof",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.drift.mar3",
                "target_id": "unit.o009.original.brown.drift.strong-markov-proof",
                "description": "Add the missing proof route for the strong-Markov statement via finite-valued stopping times and dyadic approximation.",
                "evidence": "build/site/brown/Drift.html#brown-drift-strong-markov-proof",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.bridge.downstream-correction-note",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.bridge",
                "target_id": "segment.o009.original.brown.bridge.downstream-correction-note",
                "description": "Add a compact note disclosing the guarded Bridge mathematical repairs and separately licensed reader additions.",
                "evidence": "build/site/brown/Bridge.html#brown-bridge-downstream-corrections",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.bridge.offline-lab",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.bridge.def3",
                "target_id": "unit.o009.original.brown.bridge.offline-lab",
                "description": "Add a deterministic accessible offline bridge-path and marginal-law simulation with a nonvisual moment comparison.",
                "evidence": "build/site/brown/Bridge.html#brown-bridge-offline-lab",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.bridge.offline-app",
                "change_kind": "original-addition",
                "source_id": "unit.o009.original.brown.bridge.offline-lab",
                "target_id": "asset.o009.brown-bridge-offline-js",
                "description": "Bind the offline Bridge laboratory to its byte-identical authored JavaScript runtime.",
                "evidence": "source/original/brown-bridge-offline.js; build/site/apps/brown-bridge-offline.js",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.bridge.mastery",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.bridge.edf2",
                "target_id": "unit.o009.original.brown.bridge.mastery",
                "description": "Add a process-limit warning and a complete CC BY 4.0 conditional-law exercise, hint, and worked solution.",
                "evidence": "build/site/brown/Bridge.html#brown-bridge-mastery",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.geometric.downstream-correction-note",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.geometric",
                "target_id": "segment.o009.original.brown.geometric.downstream-correction-note",
                "description": "Add a compact note disclosing the guarded Geometric mathematical repairs and separately licensed reader additions.",
                "evidence": "build/site/brown/Geometric.html#geometric-brownian-downstream-corrections",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.geometric.offline-lab",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.geometric.def1",
                "target_id": "unit.o009.original.brown.geometric.offline-lab",
                "description": "Add a deterministic accessible offline exact-solution path and terminal lognormal simulation with a nonvisual moment comparison.",
                "evidence": "build/site/brown/Geometric.html#geometric-brownian-offline-lab",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.geometric.offline-app",
                "change_kind": "original-addition",
                "source_id": "unit.o009.original.brown.geometric.offline-lab",
                "target_id": "asset.o009.geometric-brownian-offline-js",
                "description": "Bind the offline Geometric laboratory to its byte-identical authored JavaScript runtime.",
                "evidence": "source/original/geometric-brownian-offline.js; build/site/apps/geometric-brownian-offline.js",
                "status": "accepted",
            },
            {
                "correction_id": "correction.o009.original.brown.geometric.mastery",
                "change_kind": "original-addition",
                "source_id": "unit.o009.random.brown.geometric.mom1",
                "target_id": "unit.o009.original.brown.geometric.mastery",
                "description": "Add a complete CC BY 4.0 conditional-lognormal and discounted-martingale exercise, hint, and worked solution.",
                "evidence": "build/site/brown/Geometric.html#geometric-brownian-mastery",
                "status": "accepted",
            },
        ]
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
    entities.extend(quantecon)
    entities.extend(original_bridge)
    entities.extend(original_bridge_02)
    entities.extend(original_bridge_03)
    entities.extend(original_bridge_04)
    entities.extend(lab)
    entities.extend(markov_lab)
    entities.extend(convergence_modes_lab)
    entities.extend(conditional_martingale_lab)
    entities.extend(brownian_diagnostics_lab)
    two_state_app, two_state_app_relations = two_state_app_entities()
    entities.extend(two_state_app)
    entities.extend(asset_entities())
    segments = (
        html_segments
        + quantecon_segments
        + original_bridge_segments
        + original_bridge_02_segments
        + original_bridge_03_segments
        + original_bridge_04_segments
        + lab_segments
        + markov_lab_segments
        + convergence_modes_lab_segments
        + conditional_martingale_lab_segments
        + brownian_diagnostics_lab_segments
    )
    relations = (
        html_relations
        + quantecon_relations
        + original_bridge_relations
        + original_bridge_02_relations
        + original_bridge_03_relations
        + original_bridge_04_relations
        + lab_relations
        + markov_lab_relations
        + convergence_modes_lab_relations
        + conditional_martingale_lab_relations
        + brownian_diagnostics_lab_relations
        + two_state_app_relations
    )
    (
        authored_entities,
        authored_segments,
        authored_relations,
        authored_aliases,
    ) = authored_markdown_bundle(entities + segments)
    entities.extend(authored_entities)
    segments.extend(authored_segments)
    relations.extend(authored_relations)
    aliases.extend(authored_aliases)
    all_records = entities + segments
    validate_record_envelopes(all_records, relations)
    validate_preserved_corpus_counts(all_records)
    write_original_bridge_mastery_ledger()
    write_original_bridge_02_mastery_ledger()
    write_original_bridge_03_mastery_ledger()
    write_original_bridge_04_mastery_ledger()

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
    validate_authored_markdown_contract(
        all_records,
        relations,
        aliases,
        {item["artifact_id"]: item for item in artifacts},
    )
    validate_original_bridge_contract(
        all_records,
        relations,
        corrections,
        {item["artifact_id"]: item for item in artifacts},
    )
    validate_original_bridge_02_contract(
        all_records,
        relations,
        corrections,
        {item["artifact_id"]: item for item in artifacts},
    )
    validate_original_bridge_03_contract(
        all_records,
        relations,
        corrections,
        {item["artifact_id"]: item for item in artifacts},
    )
    validate_original_bridge_04_contract(
        all_records,
        relations,
        corrections,
        {item["artifact_id"]: item for item in artifacts},
    )
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
    raw = require_file(BACKEND / filename)
    if b"\r" in raw or (raw and not raw.endswith(b"\n")):
        raise RuntimeError(f"{filename}: bytes violate the strict LF line-ending contract")
    with (BACKEND / filename).open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != CSV_DEFINITIONS[filename]["fields"]:
            raise RuntimeError(f"{filename}: header differs from strict schema")
        rows = list(reader)
    validate_csv_rows(filename, rows)
    return rows


def validate_backend() -> None:
    validate_site_manifest_inventory()
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
    aliases_by_id = {row["alias_id"]: row for row in alias_rows}
    for row in alias_rows:
        if row["canonical_id"] not in known:
            raise RuntimeError(f"alias references unknown canonical id: {row['alias_id']}")
    validate_authored_markdown_contract(
        entities + segments,
        relations,
        alias_rows,
        artifacts,
    )
    by_id = entities_by_id(entities + segments)
    if (
        manifest.get("entity_count") != len(entities)
        or manifest.get("segment_count") != len(segments)
        or manifest.get("relation_count") != len(relations)
    ):
        raise RuntimeError("backend manifest record totals differ from generated rows")
    validate_original_bridge_contract(
        entities + segments,
        relations,
        read_csv("corrections.csv"),
        artifacts,
    )
    validate_original_bridge_02_contract(
        entities + segments,
        relations,
        read_csv("corrections.csv"),
        artifacts,
    )
    validate_original_bridge_03_contract(
        entities + segments,
        relations,
        read_csv("corrections.csv"),
        artifacts,
    )
    validate_original_bridge_04_contract(
        entities + segments,
        relations,
        read_csv("corrections.csv"),
        artifacts,
    )

    relations_by_id = {row["relation_id"]: row for row in relations}
    for overview_slug, children in OVERVIEW_CHILDREN.items():
        overview_spec = next(
            spec for spec in THEORY_SPECS if str(spec["slug"]) == overview_slug
        )
        overview_id = f"unit.o009.random.{overview_slug}"
        overview = by_id.get(overview_id)
        authority = AUTH_RANDOM / "static" / Path(str(overview_spec["rel"]))
        target = ROOT / "source" / "theory" / Path(str(overview_spec["rel"]))
        if (
            overview is None
            or overview["record_type"] != "unit"
            or overview["parent_id"] != "course.o009.d30"
            or overview["order"] != int(overview_spec["order"])
            or overview["path"] != str(overview_spec["rel"])
            or overview["payload"].get("unit_kind") != "overview"
            or overview["source_sha256"] != sha256(require_file(authority))
            or overview["target_sha256"] != sha256(require_file(target))
            or overview["source_sha256"] != str(overview_spec["authority_sha256"])
            or overview["target_sha256"] != str(overview_spec["target_sha256"])
        ):
            raise RuntimeError(
                f"Random overview lacks its exact stable-ID/hash/kind binding: {overview_id}"
            )
        for child_slug, child_href in children:
            child_id = f"unit.o009.random.{child_slug}"
            relation_id = f"rel.contains.{overview_id}.{child_id}"
            if relations_by_id.get(relation_id) != {
                "relation_id": relation_id,
                "relation_type": "contains",
                "source_id": overview_id,
                "target_id": child_id,
                "evidence": f"{overview_spec['rel']} overview link {child_href}",
                "status": "active",
            }:
                raise RuntimeError(
                    f"Random overview lacks exact selected-child containment: {relation_id}"
                )

    # Prove that each replayed QuantEcon figure is linked to the code cell that
    # actually contains it in the public DOM.  Positional matching is invalid
    # because hidden and visible cells use different HTML containers, and a
    # source figure can occur between execution figures.
    quantecon_units = {
        "memoryless": "unit.o009.quantecon.ctmc.memoryless-distributions",
        "poisson": "unit.o009.quantecon.ctmc.poisson-processes",
        "markov_prop": "unit.o009.quantecon.ctmc.markov-property",
        "kolmogorov_bwd": "unit.o009.quantecon.ctmc.kolmogorov-backward",
        "kolmogorov_fwd": "unit.o009.quantecon.ctmc.kolmogorov-forward",
        "generators": "unit.o009.quantecon.ctmc.generators",
        "uc_mc_semigroups": "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups",
        "ergodicity": "unit.o009.quantecon.ctmc.stationarity-ergodicity",
    }
    expected_execution_links: set[tuple[str, str]] = set()
    for slug, quantecon_unit_id in quantecon_units.items():
        page = BeautifulSoup(
            require_file(ROOT / "build" / "site" / "quantecon" / "lectures" / f"{slug}.html").decode("utf-8"),
            "lxml",
        )
        for figure in page.select("figure.execution-figure"):
            code_ancestor = figure.parent
            while code_ancestor is not None:
                if "code-cell" in set(code_ancestor.get("class") or []):
                    break
                code_ancestor = code_ancestor.parent
            code_local_id = None if code_ancestor is None else code_ancestor.get("id")
            figure_local_id = figure.get("id")
            if not code_local_id or not figure_local_id:
                raise RuntimeError(
                    f"QuantEcon execution figure lacks stable DOM ancestry: {slug}"
                )
            expected_execution_links.add(
                (
                    f"{quantecon_unit_id}.{code_local_id}",
                    f"{quantecon_unit_id}.{figure_local_id}",
                )
            )
    actual_execution_links = {
        (row["source_id"], row["target_id"])
        for row in relations
        if row["relation_id"].startswith("rel.executes.quantecon.")
    }
    if actual_execution_links != expected_execution_links:
        raise RuntimeError(
            "QuantEcon execution relations differ from nearest code-cell DOM ancestry: "
            f"missing={sorted(expected_execution_links - actual_execution_links)} "
            f"extra={sorted(actual_execution_links - expected_execution_links)}"
        )
    if any(source_id not in by_id or target_id not in by_id for source_id, target_id in expected_execution_links):
        raise RuntimeError("QuantEcon execution relation references an unexported code or figure entity")

    required_alias_targets = {
        "unit.donor.zitkovic.monte-carlo-exp.exercise",
        "unit.donor.zitkovic.monte-carlo-exp.solution",
        "unit.donor.zitkovic.monte-carlo-exp.program.1",
        "unit.donor.zitkovic.monte-carlo-exp.program.2",
        "unit.donor.zitkovic.monte-carlo-exp.program.3",
        "o009-exercise-convergence-mc-estimation",
        "o009-solution-convergence-mc-estimation",
        "o009-program-convergence-mc",
        "unit.donor.zitkovic.markov-chain-simulation.section",
        "unit.donor.zitkovic.markov-gambler-ruin.exercise",
        "unit.donor.zitkovic.markov-gambler-ruin.solution",
        "unit.donor.zitkovic.markov-gambler-ruin.program.1",
        "o009-lab-markov-gambler-ruin-experiment",
        "o009-exercise-markov-gambler-ruin-estimation",
        "o009-solution-markov-gambler-ruin-estimation",
        "o009-program-markov-gambler-ruin",
        "o009-lab-convergence-modes",
        "o009-lab-convergence-modes-experiment",
        "o009-exercise-convergence-modes-estimation",
        "o009-solution-convergence-modes-estimation",
        "o009-program-convergence-modes",
        "o009-mastery-convergence-modes",
        "o009-mastery-convergence-modes-sequence",
        "o009-exercise-convergence-modes-mastery",
        "o009-hint-convergence-modes-1",
        "o009-hint-convergence-modes-2",
        "o009-answer-convergence-modes",
        "o009-solution-convergence-modes",
        "o009-lab-conditional-martingale",
        "o009-conditional-martingale-goals",
        "o009-conditional-expectation-audit",
        "o009-exercise-conditional-martingale-audit",
        "o009-program-conditional-martingale",
        "o009-results-conditional-martingale",
        "o009-optional-stopping-diagnostic",
        "o009-hint-conditional-martingale-audit-1",
        "o009-hint-conditional-martingale-audit-2",
        "o009-hint-conditional-martingale-audit-3",
        "o009-answer-conditional-martingale-audit",
        "o009-solution-conditional-martingale-audit",
        "o009-lab-brownian-diagnostics",
        "o009-brownian-diagnostics-goals",
        "o009-brownian-partition-order",
        "o009-brownian-exact-audit",
        "o009-exercise-brownian-diagnostics",
        "o009-program-brownian-diagnostics",
        "o009-results-brownian-diagnostics",
        "o009-hint-brownian-diagnostics-1",
        "o009-hint-brownian-diagnostics-2",
        "o009-hint-brownian-diagnostics-3",
        "o009-answer-brownian-diagnostics",
        "o009-solution-brownian-diagnostics",
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
        "rights.quantecon.cc-by-sa-4.0": sha256(require_file(QUANTECON_LICENSE)),
    }
    witness_hash = sha256(lab_rights_witness(require_file(LAB).decode("utf-8")).encode("utf-8"))
    rights_expectations["rights.o009.indonesian-adaptation.cc-by-4.0"] = witness_hash
    rights_expectations["rights.o009.original.cc-by-4.0"] = witness_hash
    rights_expectations[
        "rights.o009.lab.convergence-modes.cc-by-4.0"
    ] = sha256(
        original_lab_rights_witness(
            require_file(LAB_CONVERGENCE_MODES).decode("utf-8")
        ).encode("utf-8")
    )
    rights_expectations[
        "rights.o009.lab.conditional-martingale.cc-by-4.0"
    ] = sha256(
        conditional_martingale_lab_rights_witness(
            require_file(LAB_CONDITIONAL_MARTINGALE).decode("utf-8")
        ).encode("utf-8")
    )
    rights_expectations[
        "rights.o009.lab.brownian-diagnostics.cc-by-4.0"
    ] = sha256(
        brownian_diagnostics_lab_rights_witness(
            require_file(LAB_BROWNIAN_DIAGNOSTICS).decode("utf-8")
        ).encode("utf-8")
    )
    rights_expectations["rights.o009.brown-drift-original.cc-by-4.0"] = sha256(
        brown_drift_original_rights_witness().encode("utf-8")
    )
    rights_expectations["rights.o009.brown-bridge-original.cc-by-4.0"] = sha256(
        brown_bridge_original_rights_witness().encode("utf-8")
    )
    rights_expectations["rights.o009.brown-geometric-original.cc-by-4.0"] = sha256(
        brown_geometric_original_rights_witness().encode("utf-8")
    )
    _, original_bridge_text, original_bridge_spans = original_bridge_source_contract()
    original_bridge_rights_span = original_bridge_spans["hak-dan-provenans"]
    rights_expectations[ORIGINAL_BRIDGE_RIGHTS_ID] = sha256(
        original_bridge_text[
            original_bridge_rights_span.start : original_bridge_rights_span.end
        ].encode("utf-8")
    )
    (
        _,
        original_bridge_02_text,
        original_bridge_02_spans,
    ) = original_bridge_02_source_contract()
    original_bridge_02_rights_span = original_bridge_02_spans[
        "hak-dan-provenans-keterukuran"
    ]
    rights_expectations[ORIGINAL_BRIDGE_02_RIGHTS_ID] = sha256(
        original_bridge_02_text[
            original_bridge_02_rights_span.start : original_bridge_02_rights_span.end
        ].encode("utf-8")
    )
    (
        _,
        original_bridge_03_text,
        original_bridge_03_spans,
    ) = original_bridge_03_source_contract()
    original_bridge_03_rights_span = original_bridge_03_spans[
        "hak-dan-provenans-probabilitas-bersyarat"
    ]
    rights_expectations[ORIGINAL_BRIDGE_03_RIGHTS_ID] = sha256(
        original_bridge_03_text[
            original_bridge_03_rights_span.start : original_bridge_03_rights_span.end
        ].encode("utf-8")
    )
    (
        _,
        original_bridge_04_text,
        original_bridge_04_spans,
    ) = original_bridge_04_source_contract()
    original_bridge_04_rights_span = original_bridge_04_spans[
        "hak-dan-provenans-audit-hipotesis"
    ]
    rights_expectations[ORIGINAL_BRIDGE_04_RIGHTS_ID] = sha256(
        original_bridge_04_text[
            original_bridge_04_rights_span.start : original_bridge_04_rights_span.end
        ].encode("utf-8")
    )
    markov_witness_hash = sha256(
        lab_rights_witness(require_file(LAB_MARKOV).decode("utf-8")).encode("utf-8")
    )
    rights_expectations[
        "rights.o009.markov.indonesian-adaptation.cc-by-4.0"
    ] = markov_witness_hash
    rights_expectations["rights.o009.markov.original.cc-by-4.0"] = markov_witness_hash
    rights_expectations["rights.o009.two-state-app.cc-by-4.0"] = sha256(
        require_file(TWO_STATE_APP)
    )
    for rights_id, expected_hash in rights_expectations.items():
        if by_id[rights_id]["source_sha256"] != expected_hash:
            raise RuntimeError(f"rights witness hash differs: {rights_id}")

    quantecon_unit = by_id.get("unit.o009.quantecon.ctmc.memoryless-distributions")
    if quantecon_unit is None or quantecon_unit["rights_id"] != "rights.quantecon.cc-by-sa-4.0":
        raise RuntimeError("QuantEcon first-unit rights binding is missing")
    if quantecon_unit["target_sha256"] != sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "memoryless.md")):
        raise RuntimeError("QuantEcon first-unit target binding differs")
    quantecon_poisson_unit = by_id.get("unit.o009.quantecon.ctmc.poisson-processes")
    if quantecon_poisson_unit is None or quantecon_poisson_unit["rights_id"] != "rights.quantecon.cc-by-sa-4.0":
        raise RuntimeError("QuantEcon Poisson-unit rights binding is missing")
    if quantecon_poisson_unit["target_sha256"] != sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "poisson.md")):
        raise RuntimeError("QuantEcon Poisson-unit target binding differs")
    quantecon_markov_prop_unit = by_id.get("unit.o009.quantecon.ctmc.markov-property")
    if quantecon_markov_prop_unit is None or quantecon_markov_prop_unit["rights_id"] != "rights.quantecon.cc-by-sa-4.0":
        raise RuntimeError("QuantEcon Markov-property unit rights binding is missing")
    if quantecon_markov_prop_unit["target_sha256"] != sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "markov_prop.md")):
        raise RuntimeError("QuantEcon Markov-property unit target binding differs")
    quantecon_kolmogorov_bwd_unit = by_id.get("unit.o009.quantecon.ctmc.kolmogorov-backward")
    if quantecon_kolmogorov_bwd_unit is None or quantecon_kolmogorov_bwd_unit["rights_id"] != "rights.quantecon.cc-by-sa-4.0":
        raise RuntimeError("QuantEcon backward-equation unit rights binding is missing")
    if quantecon_kolmogorov_bwd_unit["target_sha256"] != sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_bwd.md")):
        raise RuntimeError("QuantEcon backward-equation unit target binding differs")
    quantecon_kolmogorov_fwd_unit = by_id.get("unit.o009.quantecon.ctmc.kolmogorov-forward")
    if quantecon_kolmogorov_fwd_unit is None or quantecon_kolmogorov_fwd_unit["rights_id"] != "rights.quantecon.cc-by-sa-4.0":
        raise RuntimeError("QuantEcon forward-equation unit rights binding is missing")
    if quantecon_kolmogorov_fwd_unit["target_sha256"] != sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_fwd.md")):
        raise RuntimeError("QuantEcon forward-equation unit target binding differs")
    quantecon_generators_unit = by_id.get("unit.o009.quantecon.ctmc.generators")
    if quantecon_generators_unit is None or quantecon_generators_unit["rights_id"] != "rights.quantecon.cc-by-sa-4.0":
        raise RuntimeError("QuantEcon generators unit rights binding is missing")
    if quantecon_generators_unit["target_sha256"] != sha256(require_file(ROOT / "source" / "quantecon" / "lectures" / "generators.md")):
        raise RuntimeError("QuantEcon generators unit target binding differs")
    if (
        quantecon_generators_unit["payload"].get("code_cell_count") != 0
        or quantecon_generators_unit["payload"].get("runtime_status")
        != "not-applicable-no-code-cells"
    ):
        raise RuntimeError("QuantEcon generators zero-code runtime binding differs")
    quantecon_uc_mc_semigroups_unit = by_id.get(
        "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups"
    )
    if (
        quantecon_uc_mc_semigroups_unit is None
        or quantecon_uc_mc_semigroups_unit["rights_id"]
        != "rights.quantecon.cc-by-sa-4.0"
    ):
        raise RuntimeError(
            "QuantEcon uniformly-continuous-semigroup unit rights binding is missing"
        )
    if quantecon_uc_mc_semigroups_unit["target_sha256"] != sha256(
        require_file(
            ROOT / "source" / "quantecon" / "lectures" / "uc_mc_semigroups.md"
        )
    ):
        raise RuntimeError(
            "QuantEcon uniformly-continuous-semigroup unit target binding differs"
        )
    if (
        quantecon_uc_mc_semigroups_unit["payload"].get("code_cell_count") != 0
        or quantecon_uc_mc_semigroups_unit["payload"].get("runtime_status")
        != "not-applicable-no-code-cells"
    ):
        raise RuntimeError(
            "QuantEcon uniformly-continuous-semigroup zero-code runtime binding differs"
        )
    quantecon_ergodicity_unit = by_id.get(
        "unit.o009.quantecon.ctmc.stationarity-ergodicity"
    )
    if (
        quantecon_ergodicity_unit is None
        or quantecon_ergodicity_unit["rights_id"]
        != "rights.quantecon.cc-by-sa-4.0"
    ):
        raise RuntimeError("QuantEcon ergodicity unit rights binding is missing")
    if quantecon_ergodicity_unit["target_sha256"] != sha256(
        require_file(
            ROOT / "source" / "quantecon" / "lectures" / "ergodicity.md"
        )
    ):
        raise RuntimeError("QuantEcon ergodicity unit target binding differs")
    if (
        quantecon_ergodicity_unit["payload"].get("code_cell_count") != 4
        or quantecon_ergodicity_unit["payload"].get("runtime_status")
        != "two-pass-offline-replay"
    ):
        raise RuntimeError("QuantEcon ergodicity runtime binding differs")

    poisson_general_authority = AUTH_RANDOM / "static" / "poisson" / "General.html"
    poisson_general_target = ROOT / "source" / "theory" / "poisson" / "General.html"
    poisson_general_reader = ROOT / "build" / "site" / "poisson" / "General.html"
    poisson_general_authority_sha256 = (
        "cdc957a1fb433c343ee4654af5350259baf15fcc37acbb4acf2c5a50077b6567"
    )
    poisson_general_unit = by_id.get("unit.o009.random.poisson.general")
    if (
        poisson_general_unit is None
        or poisson_general_unit["order"] != 28
        or poisson_general_unit["rights_id"] != "rights.random.dual-witness"
        or poisson_general_unit["path"] != "poisson/General.html"
        or poisson_general_unit["source_sha256"]
        != poisson_general_authority_sha256
        or poisson_general_unit["target_sha256"]
        != sha256(require_file(poisson_general_target))
    ):
        raise RuntimeError(
            "general-space Poisson unit lacks its order, rights, path, or byte binding"
        )
    if sha256(require_file(poisson_general_authority)) != poisson_general_authority_sha256:
        raise RuntimeError("general-space Poisson frozen authority hash differs")
    expected_poisson_artifacts = {
        "artifact.input.random-poisson-general": poisson_general_authority,
        "artifact.input.target-poisson-general": poisson_general_target,
        "artifact.input.reader-poisson-general": poisson_general_reader,
    }
    for artifact_id, path in expected_poisson_artifacts.items():
        artifact = artifacts.get(artifact_id)
        if artifact is None or artifact["sha256"] != sha256(require_file(path)):
            raise RuntimeError(f"general-space Poisson artifact binding differs: {artifact_id}")
    required_poisson_corrections = {
        f"correction.o009.random.poisson.general.{correction_id}"
        for correction_id in (
            "poisson-general-set-domain",
            "poisson-general-heading-number",
            "poisson-general-single-point-finite-measure",
            "poisson-general-binomial-finite-measure",
            "poisson-general-multinomial-finite-measure",
            "poisson-count-pmf-terminology",
            "thinning-rate-order",
            "thinning-conditioning-event",
            "thinning-finite-measure-proof-domain",
            "thinning-proof-rate-labels",
            "thinning-process-independence-argument",
            "superposition-process-index",
            "superposition-count-index",
            "superposition-index-set",
            "superposition-finite-infinite-measure-proof",
            "nonhomogeneous-independent-increments",
            "nonhomogeneous-unit-density",
            "euclidean-space-symbol",
            "euclidean-norm-definition",
            "euclidean-ball-norm",
            "exercise4-contained-circle-assumption",
        )
    }
    correction_ids = {
        row["correction_id"] for row in read_csv("corrections.csv")
    }
    missing_poisson_corrections = required_poisson_corrections - correction_ids
    if missing_poisson_corrections:
        raise RuntimeError(
            "general-space Poisson guarded corrections are absent from the ledger: "
            f"{sorted(missing_poisson_corrections)}"
        )
    if (
        "rel.precedes.unit.o009.random.markov.limiting.unit.o009.random.poisson.general"
        in {row["relation_id"] for row in relations}
    ):
        raise RuntimeError(
            "general-space Poisson ordering bypasses the QuantEcon 20--27 block"
        )

    brown_authority = AUTH_RANDOM / "static" / "brown" / "Standard.html"
    brown_target = ROOT / "source" / "theory" / "brown" / "Standard.html"
    brown_reader = ROOT / "build" / "site" / "brown" / "Standard.html"
    brown_authority_sha256 = (
        "442b4dacc55ce0ffc49fff5093ee2ad5adb75d337d45908e5e0df1448d84ebd8"
    )
    brown_unit = by_id.get("unit.o009.random.brown.standard")
    if (
        brown_unit is None
        or brown_unit["order"] != 29
        or brown_unit["rights_id"] != "rights.random.dual-witness"
        or brown_unit["path"] != "brown/Standard.html"
        or brown_unit["source_sha256"] != brown_authority_sha256
        or brown_unit["target_sha256"] != sha256(require_file(brown_target))
    ):
        raise RuntimeError(
            "Brown Standard unit lacks its order, rights, path, or authority/target byte binding"
        )
    if sha256(require_file(brown_authority)) != brown_authority_sha256:
        raise RuntimeError("Brown Standard frozen authority hash differs")
    expected_brown_artifacts = {
        "artifact.input.random-brown-standard": brown_authority,
        "artifact.input.target-brown-standard": brown_target,
        "artifact.input.reader-brown-standard": brown_reader,
        "artifact.input.random-brown-apps-js": AUTH_RANDOM
        / "static"
        / "apps"
        / "Apps.js",
        "artifact.input.reader-brown-apps-js": ROOT
        / "build"
        / "site"
        / "apps"
        / "Apps.js",
        "artifact.input.random-brown-distributions-js": AUTH_RANDOM
        / "static"
        / "apps"
        / "Distributions.js",
        "artifact.input.reader-brown-distributions-js": ROOT
        / "build"
        / "site"
        / "apps"
        / "Distributions.js",
    }
    for artifact_id, path in expected_brown_artifacts.items():
        artifact = artifacts.get(artifact_id)
        if artifact is None or artifact["sha256"] != sha256(require_file(path)):
            raise RuntimeError(f"Brown artifact binding differs: {artifact_id}")

    apps_sha256 = "a983fd231b3e5924ca46a80ef25ad614d84c70f5da933f90c698bd342ddf9d22"
    distributions_sha256 = (
        "bcf0e7266ff22890e23e577bdb37328233c1df9410ac2dc77a4075f0a3beeb0a"
    )
    for asset_id, expected_sha256 in (
        ("asset.random.apps.core", apps_sha256),
        ("asset.random.apps.distributions", distributions_sha256),
    ):
        asset = by_id.get(asset_id)
        if (
            asset is None
            or asset["record_type"] != "asset"
            or asset["rights_id"] != "rights.random.dual-witness"
            or asset["source_sha256"] != expected_sha256
            or asset["target_sha256"] != expected_sha256
        ):
            raise RuntimeError(f"Brown app asset binding differs: {asset_id}")
    if (
        sha256(require_file(expected_brown_artifacts["artifact.input.random-brown-apps-js"]))
        != apps_sha256
        or sha256(require_file(expected_brown_artifacts["artifact.input.reader-brown-apps-js"]))
        != apps_sha256
        or sha256(
            require_file(
                expected_brown_artifacts[
                    "artifact.input.random-brown-distributions-js"
                ]
            )
        )
        != distributions_sha256
        or sha256(
            require_file(
                expected_brown_artifacts[
                    "artifact.input.reader-brown-distributions-js"
                ]
            )
        )
        != distributions_sha256
    ):
        raise RuntimeError("Brown reader app bytes differ from the frozen authority assets")

    brown_build_module = load_build_validator()
    brown_spec = next(
        spec for spec in THEORY_SPECS if str(spec["rel"]) == "brown/Standard.html"
    )
    required_brown_builder_ids = {
        str(item) for item in brown_spec.get("required_correction_ids", ())
    }
    actual_brown_builder_ids = {
        str(item["id"])
        for item in tuple(brown_build_module.BROWN_STANDARD_READER_CORRECTIONS)
    }
    if (
        len(actual_brown_builder_ids)
        != len(tuple(brown_build_module.BROWN_STANDARD_READER_CORRECTIONS))
        or actual_brown_builder_ids != required_brown_builder_ids
        or len(required_brown_builder_ids) != 37
    ):
        raise RuntimeError(
            "Brown guarded correction registry differs from the exact 37-ID backend contract"
        )
    expected_brown_correction_ids = {
        f"correction.o009.random.brown.standard.{item}"
        for item in required_brown_builder_ids
    }
    actual_brown_correction_ids = {
        item
        for item in correction_ids
        if item.startswith("correction.o009.random.brown.standard.")
    }
    if actual_brown_correction_ids != expected_brown_correction_ids:
        raise RuntimeError(
            "Brown correction ledger differs from the exact guarded builder set: "
            f"missing={sorted(expected_brown_correction_ids - actual_brown_correction_ids)} "
            f"extra={sorted(actual_brown_correction_ids - expected_brown_correction_ids)}"
        )
    for original_correction_id in (
        "correction.o009.original.brown.standard.downstream-correction-note",
        "correction.o009.original.brown.standard.exercise-solution",
    ):
        if original_correction_id not in correction_ids:
            raise RuntimeError(
                f"Brown original-addition ledger row is missing: {original_correction_id}"
            )

    brown_source_soup = BeautifulSoup(require_file(brown_target).decode("utf-8"), "lxml")
    brown_reader_soup = BeautifulSoup(require_file(brown_reader).decode("utf-8"), "lxml")
    brown_solution_aside = brown_reader_soup.find(
        "aside", id="brown-standard-exercise-solution"
    )
    brown_correction_aside = brown_reader_soup.find(
        "aside", id="brown-standard-downstream-corrections"
    )
    brown_lil_consequence = brown_reader_soup.find("details", id="lil1-consequence")
    if (
        len(brown_source_soup.select("div.unit")) != 50
        or len(brown_source_soup.find_all("details")) != 28
        or len(brown_reader_soup.select("div.unit")) != 50
        or len(brown_reader_soup.find_all("details")) != 30
        or brown_solution_aside is None
        or len(brown_solution_aside.find_all("details")) != 1
        or brown_correction_aside is None
        or brown_lil_consequence is None
    ):
        raise RuntimeError("Brown source/reader topology or explicit addition surfaces differ")
    brown_solution = by_id.get(
        "unit.o009.original.brown.standard.exercise-solution"
    )
    brown_correction_note = by_id.get(
        "segment.o009.original.brown.standard.downstream-correction-note"
    )
    brown_lil_addition = by_id.get(
        "unit.o009.original.brown.standard.lil1-consequence"
    )
    if (
        brown_solution is None
        or brown_solution["target_sha256"]
        != sha256(str(brown_solution_aside).encode("utf-8"))
        or brown_solution["rights_id"] != "rights.o009.original.cc-by-4.0"
        or brown_solution["source_target_relationship"] != "authored"
        or brown_solution["payload"].get("source_supplied") is not False
        or brown_correction_note is None
        or brown_correction_note["target_sha256"]
        != sha256(" ".join(brown_correction_aside.stripped_strings).encode("utf-8"))
        or brown_correction_note["rights_id"] != "rights.o009.original.cc-by-4.0"
        or brown_lil_addition is None
        or brown_lil_addition["target_sha256"]
        != sha256(str(brown_lil_consequence).encode("utf-8"))
        or brown_lil_addition["rights_id"] != "rights.o009.original.cc-by-4.0"
    ):
        raise RuntimeError("Brown explicit reader additions lack exact byte or rights binding")
    incoming_brown_predecessors = {
        (item["source_id"], item["target_id"])
        for item in relations
        if item["relation_type"] == "precedes"
        and item["target_id"] == "unit.o009.random.brown.standard"
    }
    if incoming_brown_predecessors != {
        (
            "unit.o009.random.poisson.general",
            "unit.o009.random.brown.standard",
        )
    }:
        raise RuntimeError(
            "Brown Standard must have exactly general-space Poisson as its predecessor"
        )

    drift_authority = AUTH_RANDOM / "static" / "brown" / "Drift.html"
    drift_target = ROOT / "source" / "theory" / "brown" / "Drift.html"
    drift_reader = ROOT / "build" / "site" / "brown" / "Drift.html"
    drift_authority_sha256 = (
        "f1603646520d3c83fa986e6b0be7bcac6862d7443e57d0a28264534da3dc70d5"
    )
    drift_target_sha256 = (
        "7957d796d47ae31d74e1f0ae9733eac7df22f2ccd3311d5195c4cf948dcb9936"
    )
    drift_page_id = "unit.o009.random.brown.drift"
    drift_unit = by_id.get(drift_page_id)
    if (
        drift_unit is None
        or drift_unit["order"] != 30
        or drift_unit["rights_id"] != "rights.random.dual-witness"
        or drift_unit["path"] != "brown/Drift.html"
        or drift_unit["source_sha256"] != drift_authority_sha256
        or drift_unit["target_sha256"] != drift_target_sha256
    ):
        raise RuntimeError(
            "Brown Drift unit lacks its order, rights, path, or frozen authority/target byte binding"
        )
    if sha256(require_file(drift_authority)) != drift_authority_sha256:
        raise RuntimeError("Brown Drift frozen authority hash differs")
    if sha256(require_file(drift_target)) != drift_target_sha256:
        raise RuntimeError("Brown Drift frozen translated-source hash differs")
    expected_drift_artifacts = {
        "artifact.input.random-brown-drift": drift_authority,
        "artifact.input.target-brown-drift": drift_target,
        "artifact.input.reader-brown-drift": drift_reader,
        "artifact.input.original-brown-drift-offline-js": BROWN_DRIFT_OFFLINE_APP,
        "artifact.input.reader-brown-drift-offline-js": BUILT_BROWN_DRIFT_OFFLINE_APP,
    }
    for artifact_id, path in expected_drift_artifacts.items():
        artifact = artifacts.get(artifact_id)
        if artifact is None or artifact["sha256"] != sha256(require_file(path)):
            raise RuntimeError(f"Brown Drift artifact binding differs: {artifact_id}")

    drift_build_module = load_build_validator()
    drift_spec = next(
        spec for spec in THEORY_SPECS if str(spec["rel"]) == "brown/Drift.html"
    )
    required_drift_builder_ids = {
        str(item) for item in drift_spec.get("required_correction_ids", ())
    }
    actual_drift_builder_ids = {
        str(item["id"])
        for item in tuple(drift_build_module.BROWN_DRIFT_READER_CORRECTIONS)
    }
    if (
        len(actual_drift_builder_ids)
        != len(tuple(drift_build_module.BROWN_DRIFT_READER_CORRECTIONS))
        or actual_drift_builder_ids != required_drift_builder_ids
        or len(required_drift_builder_ids) != 10
    ):
        raise RuntimeError(
            "Brown Drift guarded correction registry differs from the exact 10-ID backend contract"
        )
    expected_drift_correction_ids = {
        f"correction.o009.random.brown.drift.{item}"
        for item in required_drift_builder_ids
    }
    actual_drift_correction_ids = {
        item
        for item in correction_ids
        if item.startswith("correction.o009.random.brown.drift.")
    }
    if actual_drift_correction_ids != expected_drift_correction_ids:
        raise RuntimeError(
            "Brown Drift correction ledger differs from the exact guarded builder set: "
            f"missing={sorted(expected_drift_correction_ids - actual_drift_correction_ids)} "
            f"extra={sorted(actual_drift_correction_ids - expected_drift_correction_ids)}"
        )
    expected_drift_original_corrections = {
        "correction.o009.original.brown.drift.downstream-correction-note",
        "correction.o009.original.brown.drift.offline-lab",
        "correction.o009.original.brown.drift.offline-app",
        "correction.o009.original.brown.drift.mastery",
        "correction.o009.original.brown.drift.strong-markov-proof",
    }
    actual_drift_original_corrections = {
        item
        for item in correction_ids
        if item.startswith("correction.o009.original.brown.drift.")
    }
    if actual_drift_original_corrections != expected_drift_original_corrections:
        raise RuntimeError(
            "Brown Drift original-addition ledger differs: "
            f"missing={sorted(expected_drift_original_corrections - actual_drift_original_corrections)} "
            f"extra={sorted(actual_drift_original_corrections - expected_drift_original_corrections)}"
        )

    drift_source_soup = BeautifulSoup(require_file(drift_target).decode("utf-8"), "lxml")
    drift_reader_soup = BeautifulSoup(require_file(drift_reader).decode("utf-8"), "lxml")
    drift_correction_aside = drift_reader_soup.find(
        "aside", id="brown-drift-downstream-corrections"
    )
    drift_lab_section = drift_reader_soup.find("section", id="brown-drift-offline-lab")
    drift_mastery_aside = drift_reader_soup.find("aside", id="brown-drift-mastery")
    drift_mastery_exercise = drift_reader_soup.find(
        id="brown-drift-mastery-exercise"
    )
    drift_mastery_hint = drift_reader_soup.find(
        "details", id="brown-drift-mastery-hint"
    )
    drift_mastery_solution = drift_reader_soup.find(
        "details", id="brown-drift-mastery-solution"
    )
    drift_strong_markov_proof = drift_reader_soup.find(
        "details", id="brown-drift-strong-markov-proof"
    )
    if (
        len(drift_source_soup.select("div.unit")) != 11
        or len(drift_source_soup.find_all("details")) != 7
        or len(drift_reader_soup.select("div.unit")) != 11
        or len(drift_reader_soup.find_all("details")) != 10
        or any(
            item is None
            for item in (
                drift_correction_aside,
                drift_lab_section,
                drift_mastery_aside,
                drift_mastery_exercise,
                drift_mastery_hint,
                drift_mastery_solution,
                drift_strong_markov_proof,
            )
        )
    ):
        raise RuntimeError(
            "Brown Drift source/reader topology or explicit addition surfaces differ"
        )
    drift_rights_id = "rights.o009.brown-drift-original.cc-by-4.0"
    exact_drift_bindings = {
        "segment.o009.original.brown.drift.downstream-correction-note": drift_correction_aside,
        "unit.o009.original.brown.drift.offline-lab": drift_lab_section,
        "unit.o009.original.brown.drift.mastery": drift_mastery_aside,
        "unit.o009.original.brown.drift.mastery.exercise": drift_mastery_exercise,
        "unit.o009.original.brown.drift.mastery.hint": drift_mastery_hint,
        "unit.o009.original.brown.drift.mastery.solution": drift_mastery_solution,
        "unit.o009.original.brown.drift.strong-markov-proof": drift_strong_markov_proof,
    }
    for stable_id, node in exact_drift_bindings.items():
        item = by_id.get(stable_id)
        if (
            item is None
            or item["target_sha256"] != sha256(str(node).encode("utf-8"))
            or item["rights_id"] != drift_rights_id
            or item["source_target_relationship"] != "authored"
        ):
            raise RuntimeError(
                f"Brown Drift explicit reader addition lacks exact byte or rights binding: {stable_id}"
            )
    drift_app = by_id.get("asset.o009.brown-drift-offline-js")
    drift_app_sha256 = sha256(require_file(BROWN_DRIFT_OFFLINE_APP))
    if (
        drift_app is None
        or drift_app["source_sha256"] != drift_app_sha256
        or drift_app["target_sha256"] != drift_app_sha256
        or drift_app["rights_id"] != drift_rights_id
        or require_file(BROWN_DRIFT_OFFLINE_APP)
        != require_file(BUILT_BROWN_DRIFT_OFFLINE_APP)
    ):
        raise RuntimeError("Brown Drift offline JavaScript lacks exact byte or rights binding")
    incoming_drift_predecessors = {
        (item["source_id"], item["target_id"])
        for item in relations
        if item["relation_type"] == "precedes"
        and item["target_id"] == drift_page_id
    }
    if incoming_drift_predecessors != {
        ("unit.o009.random.brown.standard", drift_page_id)
    }:
        raise RuntimeError("Brown Drift must have exactly Brown Standard as its predecessor")

    bridge_authority = AUTH_RANDOM / "static" / "brown" / "Bridge.html"
    bridge_target = ROOT / "source" / "theory" / "brown" / "Bridge.html"
    bridge_reader = ROOT / "build" / "site" / "brown" / "Bridge.html"
    bridge_authority_sha256 = (
        "62e8b18c32f191f801e4cb9be3ee0db3fb658329d937b0807c6d8b8d7b37410e"
    )
    bridge_target_sha256 = (
        "8af8c9da98203455a19181a4609cd52fe39787bcc7c21e607c92bf1b4235cc1a"
    )
    bridge_page_id = "unit.o009.random.brown.bridge"
    bridge_unit = by_id.get(bridge_page_id)
    if (
        bridge_unit is None
        or bridge_unit["order"] != 31
        or bridge_unit["rights_id"] != "rights.random.dual-witness"
        or bridge_unit["path"] != "brown/Bridge.html"
        or bridge_unit["source_sha256"] != bridge_authority_sha256
        or bridge_unit["target_sha256"] != bridge_target_sha256
    ):
        raise RuntimeError(
            "Brown Bridge unit lacks its order, rights, path, or frozen "
            "authority/target byte binding"
        )
    if sha256(require_file(bridge_authority)) != bridge_authority_sha256:
        raise RuntimeError("Brown Bridge frozen authority hash differs")
    if sha256(require_file(bridge_target)) != bridge_target_sha256:
        raise RuntimeError("Brown Bridge frozen translated-source hash differs")
    expected_bridge_artifacts = {
        "artifact.input.random-brown-bridge": bridge_authority,
        "artifact.input.target-brown-bridge": bridge_target,
        "artifact.input.reader-brown-bridge": bridge_reader,
        "artifact.input.original-brown-bridge-offline-js": (
            BROWN_BRIDGE_OFFLINE_APP
        ),
        "artifact.input.reader-brown-bridge-offline-js": (
            BUILT_BROWN_BRIDGE_OFFLINE_APP
        ),
    }
    for artifact_id, path in expected_bridge_artifacts.items():
        artifact = artifacts.get(artifact_id)
        if artifact is None or artifact["sha256"] != sha256(require_file(path)):
            raise RuntimeError(f"Brown Bridge artifact binding differs: {artifact_id}")

    bridge_build_module = load_build_validator()
    bridge_spec = next(
        spec for spec in THEORY_SPECS if str(spec["rel"]) == "brown/Bridge.html"
    )
    required_bridge_builder_ids = {
        str(item) for item in bridge_spec.get("required_correction_ids", ())
    }
    actual_bridge_builder_ids = {
        str(item["id"])
        for item in tuple(bridge_build_module.BROWN_BRIDGE_READER_CORRECTIONS)
    }
    if (
        len(actual_bridge_builder_ids)
        != len(tuple(bridge_build_module.BROWN_BRIDGE_READER_CORRECTIONS))
        or actual_bridge_builder_ids != required_bridge_builder_ids
        or len(required_bridge_builder_ids) != 14
    ):
        raise RuntimeError(
            "Brown Bridge guarded correction registry differs from the exact "
            "14-ID backend contract"
        )
    expected_bridge_correction_ids = {
        f"correction.o009.random.brown.bridge.{item}"
        for item in required_bridge_builder_ids
    }
    actual_bridge_correction_ids = {
        item
        for item in correction_ids
        if item.startswith("correction.o009.random.brown.bridge.")
    }
    if actual_bridge_correction_ids != expected_bridge_correction_ids:
        raise RuntimeError(
            "Brown Bridge correction ledger differs from the exact guarded builder "
            f"set: missing={sorted(expected_bridge_correction_ids - actual_bridge_correction_ids)} "
            f"extra={sorted(actual_bridge_correction_ids - expected_bridge_correction_ids)}"
        )
    expected_bridge_original_corrections = {
        "correction.o009.original.brown.bridge.downstream-correction-note",
        "correction.o009.original.brown.bridge.offline-lab",
        "correction.o009.original.brown.bridge.offline-app",
        "correction.o009.original.brown.bridge.mastery",
    }
    actual_bridge_original_corrections = {
        item
        for item in correction_ids
        if item.startswith("correction.o009.original.brown.bridge.")
    }
    if actual_bridge_original_corrections != expected_bridge_original_corrections:
        raise RuntimeError(
            "Brown Bridge original-addition ledger differs: "
            f"missing={sorted(expected_bridge_original_corrections - actual_bridge_original_corrections)} "
            f"extra={sorted(actual_bridge_original_corrections - expected_bridge_original_corrections)}"
        )

    bridge_source_soup = BeautifulSoup(
        require_file(bridge_target).decode("utf-8"), "lxml"
    )
    bridge_reader_soup = BeautifulSoup(
        require_file(bridge_reader).decode("utf-8"), "lxml"
    )
    bridge_correction_aside = bridge_reader_soup.find(
        "aside", id="brown-bridge-downstream-corrections"
    )
    bridge_lab_section = bridge_reader_soup.find(
        "section", id="brown-bridge-offline-lab"
    )
    bridge_mastery_aside = bridge_reader_soup.find(
        "aside", id="brown-bridge-mastery"
    )
    bridge_process_limit_warning = bridge_reader_soup.find(
        "p", id="brown-bridge-process-limit-warning"
    )
    bridge_mastery_exercise = bridge_reader_soup.find(
        "p", id="brown-bridge-mastery-exercise"
    )
    bridge_mastery_hint = bridge_reader_soup.find(
        "details", id="brown-bridge-mastery-hint"
    )
    bridge_mastery_solution = bridge_reader_soup.find(
        "details", id="brown-bridge-mastery-solution"
    )
    if (
        len(bridge_source_soup.select("div.unit")) != 13
        or len(bridge_source_soup.find_all("details")) != 7
        or len(bridge_reader_soup.select("div.unit")) != 13
        or len(bridge_reader_soup.find_all("details")) != 9
        or any(
            item is None
            for item in (
                bridge_correction_aside,
                bridge_lab_section,
                bridge_mastery_aside,
                bridge_process_limit_warning,
                bridge_mastery_exercise,
                bridge_mastery_hint,
                bridge_mastery_solution,
            )
        )
    ):
        raise RuntimeError(
            "Brown Bridge source/reader topology or explicit addition surfaces differ"
        )
    bridge_rights_id = "rights.o009.brown-bridge-original.cc-by-4.0"
    exact_bridge_bindings = {
        "segment.o009.original.brown.bridge.downstream-correction-note": (
            bridge_correction_aside
        ),
        "unit.o009.original.brown.bridge.offline-lab": bridge_lab_section,
        "unit.o009.original.brown.bridge.mastery": bridge_mastery_aside,
        "unit.o009.original.brown.bridge.mastery.process-limit-warning": (
            bridge_process_limit_warning
        ),
        "unit.o009.original.brown.bridge.mastery.exercise": (
            bridge_mastery_exercise
        ),
        "unit.o009.original.brown.bridge.mastery.hint": bridge_mastery_hint,
        "unit.o009.original.brown.bridge.mastery.solution": (
            bridge_mastery_solution
        ),
    }
    for stable_id, node in exact_bridge_bindings.items():
        item = by_id.get(stable_id)
        if (
            item is None
            or item["target_sha256"] != sha256(str(node).encode("utf-8"))
            or item["rights_id"] != bridge_rights_id
            or item["source_target_relationship"] != "authored"
        ):
            raise RuntimeError(
                "Brown Bridge explicit reader addition lacks exact byte or rights "
                f"binding: {stable_id}"
            )
    bridge_app = by_id.get("asset.o009.brown-bridge-offline-js")
    bridge_app_sha256 = sha256(require_file(BROWN_BRIDGE_OFFLINE_APP))
    if (
        bridge_app is None
        or bridge_app["source_sha256"] != bridge_app_sha256
        or bridge_app["target_sha256"] != bridge_app_sha256
        or bridge_app["rights_id"] != bridge_rights_id
        or require_file(BROWN_BRIDGE_OFFLINE_APP)
        != require_file(BUILT_BROWN_BRIDGE_OFFLINE_APP)
    ):
        raise RuntimeError(
            "Brown Bridge offline JavaScript lacks exact byte or rights binding"
        )

    bridge_segment_groups = (
        (
            "segment.o009.original.brown.bridge.offline-lab",
            "unit.o009.original.brown.bridge.offline-lab",
            bridge_lab_section.find_all(
                (
                    "p",
                    "legend",
                    "label",
                    "button",
                    "title",
                    "desc",
                    "caption",
                    "th",
                    "td",
                    "noscript",
                )
            ),
        ),
        (
            "segment.o009.original.brown.bridge.mastery",
            "unit.o009.original.brown.bridge.mastery",
            bridge_mastery_aside.find_all("p", recursive=False)[:2],
        ),
        (
            "segment.o009.original.brown.bridge.mastery.process-limit-warning",
            "unit.o009.original.brown.bridge.mastery.process-limit-warning",
            [bridge_process_limit_warning],
        ),
        (
            "segment.o009.original.brown.bridge.mastery.exercise",
            "unit.o009.original.brown.bridge.mastery.exercise",
            [bridge_mastery_exercise],
        ),
        (
            "segment.o009.original.brown.bridge.mastery.hint",
            "unit.o009.original.brown.bridge.mastery.hint",
            bridge_mastery_hint.find_all(("summary", "p")),
        ),
        (
            "segment.o009.original.brown.bridge.mastery.solution",
            "unit.o009.original.brown.bridge.mastery.solution",
            bridge_mastery_solution.find_all(("summary", "p")),
        ),
    )
    expected_bridge_segment_ids = {
        "segment.o009.original.brown.bridge.downstream-correction-note"
    }
    for stable_prefix, parent_id, nodes in bridge_segment_groups:
        nonempty_nodes = [node for node in nodes if " ".join(node.stripped_strings)]
        for index, node in enumerate(nonempty_nodes, start=1):
            stable_id = f"{stable_prefix}.{index:04d}"
            expected_bridge_segment_ids.add(stable_id)
            target_text = " ".join(node.stripped_strings)
            digest = sha256(target_text.encode("utf-8"))
            item = by_id.get(stable_id)
            if (
                item is None
                or item["parent_id"] != parent_id
                or item["order"] != index
                or item["source_sha256"] != digest
                or item["target_sha256"] != digest
                or item["rights_id"] != bridge_rights_id
                or item["source_target_relationship"] != "authored"
                or item["payload"].get("target_text") != target_text
            ):
                raise RuntimeError(
                    "Brown Bridge authored text segment lacks exact stable-ID, "
                    f"text, or rights binding: {stable_id}"
                )
    actual_bridge_segment_ids = {
        stable_id
        for stable_id in by_id
        if stable_id.startswith("segment.o009.original.brown.bridge.")
    }
    if (
        actual_bridge_segment_ids != expected_bridge_segment_ids
        or len(expected_bridge_segment_ids) != 33
    ):
        raise RuntimeError(
            "Brown Bridge authored text-segment inventory differs: "
            f"missing={sorted(expected_bridge_segment_ids - actual_bridge_segment_ids)} "
            f"extra={sorted(actual_bridge_segment_ids - expected_bridge_segment_ids)}"
        )
    incoming_bridge_predecessors = {
        (item["source_id"], item["target_id"])
        for item in relations
        if item["relation_type"] == "precedes"
        and item["target_id"] == bridge_page_id
    }
    if incoming_bridge_predecessors != {
        ("unit.o009.random.brown.drift", bridge_page_id)
    }:
        raise RuntimeError("Brown Bridge must have exactly Brown Drift as its predecessor")

    geometric_authority = AUTH_RANDOM / "static" / "brown" / "Geometric.html"
    geometric_target = ROOT / "source" / "theory" / "brown" / "Geometric.html"
    geometric_reader = ROOT / "build" / "site" / "brown" / "Geometric.html"
    geometric_authority_sha256 = (
        "4a6c1fa4c4d1cd7d646f700d438201af2b75fead1f094ecb4720d2831343f6ce"
    )
    geometric_target_sha256 = (
        "8404e8ac8caaa41699d8f2e623a890f991cc208d63200bfdef6c636640fecf0e"
    )
    geometric_app_sha256 = (
        "5b18869f5582f354c40fbf6a9987a191450e09d93b21891d9838251b4a3ed8a8"
    )
    geometric_page_id = "unit.o009.random.brown.geometric"
    geometric_unit = by_id.get(geometric_page_id)
    if (
        geometric_unit is None
        or geometric_unit["order"] != 32
        or geometric_unit["rights_id"] != "rights.random.dual-witness"
        or geometric_unit["path"] != "brown/Geometric.html"
        or geometric_unit["source_sha256"] != geometric_authority_sha256
        or geometric_unit["target_sha256"] != geometric_target_sha256
    ):
        raise RuntimeError(
            "Brown Geometric unit lacks its order, rights, path, or frozen "
            "authority/target byte binding"
        )
    if sha256(require_file(geometric_authority)) != geometric_authority_sha256:
        raise RuntimeError("Brown Geometric frozen authority hash differs")
    if sha256(require_file(geometric_target)) != geometric_target_sha256:
        raise RuntimeError("Brown Geometric frozen translated-source hash differs")
    if sha256(require_file(BROWN_GEOMETRIC_OFFLINE_APP)) != geometric_app_sha256:
        raise RuntimeError("Brown Geometric frozen offline JavaScript hash differs")
    expected_geometric_artifacts = {
        "artifact.input.random-brown-geometric": geometric_authority,
        "artifact.input.target-brown-geometric": geometric_target,
        "artifact.input.reader-brown-geometric": geometric_reader,
        "artifact.input.original-brown-geometric-offline-js": (
            BROWN_GEOMETRIC_OFFLINE_APP
        ),
        "artifact.input.reader-brown-geometric-offline-js": (
            BUILT_BROWN_GEOMETRIC_OFFLINE_APP
        ),
    }
    for artifact_id, path in expected_geometric_artifacts.items():
        artifact = artifacts.get(artifact_id)
        if artifact is None or artifact["sha256"] != sha256(require_file(path)):
            raise RuntimeError(
                f"Brown Geometric artifact binding differs: {artifact_id}"
            )

    geometric_build_module = load_build_validator()
    geometric_spec = next(
        spec for spec in THEORY_SPECS if str(spec["rel"]) == "brown/Geometric.html"
    )
    required_geometric_builder_ids = {
        str(item) for item in geometric_spec.get("required_correction_ids", ())
    }
    actual_geometric_builder_ids = {
        str(item["id"])
        for item in tuple(geometric_build_module.BROWN_GEOMETRIC_READER_CORRECTIONS)
    }
    if (
        len(actual_geometric_builder_ids)
        != len(tuple(geometric_build_module.BROWN_GEOMETRIC_READER_CORRECTIONS))
        or actual_geometric_builder_ids != required_geometric_builder_ids
        or len(required_geometric_builder_ids) != 13
    ):
        raise RuntimeError(
            "Brown Geometric guarded correction registry differs from the exact "
            "13-ID backend contract"
        )
    expected_geometric_correction_ids = {
        f"correction.o009.random.brown.geometric.{item}"
        for item in required_geometric_builder_ids
    }
    actual_geometric_correction_ids = {
        item
        for item in correction_ids
        if item.startswith("correction.o009.random.brown.geometric.")
    }
    if actual_geometric_correction_ids != expected_geometric_correction_ids:
        raise RuntimeError(
            "Brown Geometric correction ledger differs from the exact guarded "
            f"builder set: missing={sorted(expected_geometric_correction_ids - actual_geometric_correction_ids)} "
            f"extra={sorted(actual_geometric_correction_ids - expected_geometric_correction_ids)}"
        )
    expected_geometric_original_corrections = {
        "correction.o009.original.brown.geometric.downstream-correction-note",
        "correction.o009.original.brown.geometric.offline-lab",
        "correction.o009.original.brown.geometric.offline-app",
        "correction.o009.original.brown.geometric.mastery",
    }
    actual_geometric_original_corrections = {
        item
        for item in correction_ids
        if item.startswith("correction.o009.original.brown.geometric.")
    }
    if (
        actual_geometric_original_corrections
        != expected_geometric_original_corrections
    ):
        raise RuntimeError(
            "Brown Geometric original-addition ledger differs: "
            f"missing={sorted(expected_geometric_original_corrections - actual_geometric_original_corrections)} "
            f"extra={sorted(actual_geometric_original_corrections - expected_geometric_original_corrections)}"
        )

    geometric_source_soup = BeautifulSoup(
        require_file(geometric_target).decode("utf-8"), "lxml"
    )
    geometric_reader_soup = BeautifulSoup(
        require_file(geometric_reader).decode("utf-8"), "lxml"
    )
    geometric_correction_aside = geometric_reader_soup.find(
        "aside", id="geometric-brownian-downstream-corrections"
    )
    geometric_lab_section = geometric_reader_soup.find(
        "section", id="geometric-brownian-offline-lab"
    )
    geometric_mastery_aside = geometric_reader_soup.find(
        "aside", id="geometric-brownian-mastery"
    )
    geometric_mastery_exercise = geometric_reader_soup.find(
        "p", id="geometric-brownian-mastery-exercise"
    )
    geometric_mastery_hint = geometric_reader_soup.find(
        "details", id="geometric-brownian-mastery-hint"
    )
    geometric_mastery_solution = geometric_reader_soup.find(
        "details", id="geometric-brownian-mastery-solution"
    )
    geometric_source_unit_ids = [
        item.get("id") for item in geometric_source_soup.select("div.unit")
    ]
    geometric_reader_unit_ids = [
        item.get("id") for item in geometric_reader_soup.select("div.unit")
    ]
    expected_geometric_reader_unit_ids = [
        "dst4" if item == "dist4" else "prp2" if item is None else item
        for item in geometric_source_unit_ids
    ]
    if (
        len(geometric_source_unit_ids) != 14
        or len(geometric_source_soup.find_all("details")) != 6
        or geometric_reader_unit_ids != expected_geometric_reader_unit_ids
        or len(geometric_reader_soup.find_all("details")) != 8
        or any(
            item is None
            for item in (
                geometric_correction_aside,
                geometric_lab_section,
                geometric_mastery_aside,
                geometric_mastery_exercise,
                geometric_mastery_hint,
                geometric_mastery_solution,
            )
        )
    ):
        raise RuntimeError(
            "Brown Geometric source/reader topology or explicit addition surfaces differ"
        )
    geometric_rights_id = "rights.o009.brown-geometric-original.cc-by-4.0"
    exact_geometric_bindings = {
        "segment.o009.original.brown.geometric.downstream-correction-note": (
            geometric_correction_aside
        ),
        "unit.o009.original.brown.geometric.offline-lab": geometric_lab_section,
        "unit.o009.original.brown.geometric.mastery": geometric_mastery_aside,
        "unit.o009.original.brown.geometric.mastery.exercise": (
            geometric_mastery_exercise
        ),
        "unit.o009.original.brown.geometric.mastery.hint": geometric_mastery_hint,
        "unit.o009.original.brown.geometric.mastery.solution": (
            geometric_mastery_solution
        ),
    }
    for stable_id, node in exact_geometric_bindings.items():
        item = by_id.get(stable_id)
        if (
            item is None
            or item["target_sha256"] != sha256(str(node).encode("utf-8"))
            or item["rights_id"] != geometric_rights_id
            or item["source_target_relationship"] != "authored"
        ):
            raise RuntimeError(
                "Brown Geometric explicit reader addition lacks exact byte or "
                f"rights binding: {stable_id}"
            )
    geometric_app = by_id.get("asset.o009.geometric-brownian-offline-js")
    if (
        geometric_app is None
        or geometric_app["source_sha256"] != geometric_app_sha256
        or geometric_app["target_sha256"] != geometric_app_sha256
        or geometric_app["rights_id"] != geometric_rights_id
        or require_file(BROWN_GEOMETRIC_OFFLINE_APP)
        != require_file(BUILT_BROWN_GEOMETRIC_OFFLINE_APP)
    ):
        raise RuntimeError(
            "Brown Geometric offline JavaScript lacks exact byte or rights binding"
        )

    geometric_segment_groups = (
        (
            "segment.o009.original.brown.geometric.offline-lab",
            "unit.o009.original.brown.geometric.offline-lab",
            geometric_lab_section.find_all(
                (
                    "p",
                    "legend",
                    "label",
                    "button",
                    "title",
                    "desc",
                    "caption",
                    "th",
                    "td",
                    "noscript",
                )
            ),
        ),
        (
            "segment.o009.original.brown.geometric.mastery",
            "unit.o009.original.brown.geometric.mastery",
            geometric_mastery_aside.find_all("p", recursive=False)[:2],
        ),
        (
            "segment.o009.original.brown.geometric.mastery.exercise",
            "unit.o009.original.brown.geometric.mastery.exercise",
            [geometric_mastery_exercise],
        ),
        (
            "segment.o009.original.brown.geometric.mastery.hint",
            "unit.o009.original.brown.geometric.mastery.hint",
            geometric_mastery_hint.find_all(("summary", "p")),
        ),
        (
            "segment.o009.original.brown.geometric.mastery.solution",
            "unit.o009.original.brown.geometric.mastery.solution",
            geometric_mastery_solution.find_all(("summary", "p")),
        ),
    )
    expected_geometric_segment_ids = {
        "segment.o009.original.brown.geometric.downstream-correction-note"
    }
    for stable_prefix, parent_id, nodes in geometric_segment_groups:
        nonempty_nodes = [node for node in nodes if " ".join(node.stripped_strings)]
        for index, node in enumerate(nonempty_nodes, start=1):
            stable_id = f"{stable_prefix}.{index:04d}"
            expected_geometric_segment_ids.add(stable_id)
            target_text = " ".join(node.stripped_strings)
            digest = sha256(target_text.encode("utf-8"))
            item = by_id.get(stable_id)
            if (
                item is None
                or item["parent_id"] != parent_id
                or item["order"] != index
                or item["source_sha256"] != digest
                or item["target_sha256"] != digest
                or item["rights_id"] != geometric_rights_id
                or item["source_target_relationship"] != "authored"
                or item["payload"].get("target_text") != target_text
            ):
                raise RuntimeError(
                    "Brown Geometric authored text segment lacks exact stable-ID, "
                    f"text, or rights binding: {stable_id}"
                )
    actual_geometric_segment_ids = {
        stable_id
        for stable_id in by_id
        if stable_id.startswith("segment.o009.original.brown.geometric.")
    }
    if (
        actual_geometric_segment_ids != expected_geometric_segment_ids
        or len(expected_geometric_segment_ids) != 41
    ):
        raise RuntimeError(
            "Brown Geometric authored text-segment inventory differs: "
            f"missing={sorted(expected_geometric_segment_ids - actual_geometric_segment_ids)} "
            f"extra={sorted(actual_geometric_segment_ids - expected_geometric_segment_ids)}"
        )
    incoming_geometric_predecessors = {
        (item["source_id"], item["target_id"])
        for item in relations
        if item["relation_type"] == "precedes"
        and item["target_id"] == geometric_page_id
    }
    if incoming_geometric_predecessors != {
        ("unit.o009.random.brown.bridge", geometric_page_id)
    }:
        raise RuntimeError(
            "Brown Geometric must have exactly Brown Bridge as its predecessor"
        )

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

    markov_lab_text = require_file(LAB_MARKOV).decode("utf-8")
    markov_blocks = fenced_div_spans(markov_lab_text)
    markov_root_id = "o009-lab-markov-gambler-ruin"
    markov_headings = heading_spans(markov_lab_text, markov_blocks[markov_root_id])
    markov_chunks = {
        name: span for name, span in r_chunk_spans(markov_lab_text) if name
    }
    markov_exercise = "o009-exercise-markov-gambler-ruin-estimation"
    markov_mastery = "o009-mastery-markov-gambler-ruin"
    markov_body_spans = {
        markov_root_id: markov_blocks[markov_root_id],
        "o009-lab-markov-gambler-ruin-experiment": markov_headings[
            "o009-lab-markov-gambler-ruin-experiment"
        ],
        markov_exercise: markov_blocks[markov_exercise],
        "o009-solution-markov-gambler-ruin-estimation": Span(
            markov_blocks[markov_exercise].end,
            markov_headings[markov_mastery].start,
            markov_blocks[markov_exercise].end,
            markov_headings[markov_mastery].start,
        ),
        "o009-program-markov-gambler-ruin": markov_chunks[
            "o009_lab_markov_gambler_ruin"
        ],
        markov_mastery: markov_headings[markov_mastery],
        "o009-exercise-markov-gambler-ruin-mastery": markov_blocks[
            "o009-exercise-markov-gambler-ruin-mastery"
        ],
        "o009-hint-markov-gambler-ruin-mastery-1": markov_blocks[
            "o009-hint-markov-gambler-ruin-mastery-1"
        ],
        "o009-hint-markov-gambler-ruin-mastery-2": markov_blocks[
            "o009-hint-markov-gambler-ruin-mastery-2"
        ],
        "o009-hint-markov-gambler-ruin-mastery-3": markov_blocks[
            "o009-hint-markov-gambler-ruin-mastery-3"
        ],
        "o009-answer-markov-gambler-ruin-mastery": markov_blocks[
            "o009-answer-markov-gambler-ruin-mastery"
        ],
        "o009-solution-markov-gambler-ruin-mastery": markov_blocks[
            "o009-solution-markov-gambler-ruin-mastery"
        ],
    }
    for stable_id, span in markov_body_spans.items():
        expected_hash = sha256(markov_lab_text[span.start : span.end].encode("utf-8"))
        if by_id[stable_id]["target_sha256"] != expected_hash:
            raise RuntimeError(f"complete Markov lab body hash differs: {stable_id}")
        if by_id[stable_id]["payload"].get("body_extent") != "complete":
            raise RuntimeError(f"Markov lab unit is not a complete body: {stable_id}")

    convergence_modes_text = require_file(LAB_CONVERGENCE_MODES).decode("utf-8")
    convergence_modes_blocks = fenced_div_spans(convergence_modes_text)
    convergence_modes_root = "o009-lab-convergence-modes"
    convergence_modes_headings = heading_spans(
        convergence_modes_text, convergence_modes_blocks[convergence_modes_root]
    )
    convergence_modes_chunks = {
        name: span
        for name, span in r_chunk_spans(convergence_modes_text)
        if name
    }
    convergence_modes_exercise = "o009-exercise-convergence-modes-estimation"
    convergence_modes_mastery = "o009-mastery-convergence-modes"
    convergence_modes_body_spans = {
        convergence_modes_root: convergence_modes_blocks[convergence_modes_root],
        "o009-lab-convergence-modes-experiment": convergence_modes_headings[
            "o009-lab-convergence-modes-experiment"
        ],
        convergence_modes_exercise: convergence_modes_blocks[
            convergence_modes_exercise
        ],
        "o009-solution-convergence-modes-estimation": Span(
            convergence_modes_blocks[convergence_modes_exercise].end,
            convergence_modes_headings[convergence_modes_mastery].start,
            convergence_modes_blocks[convergence_modes_exercise].end,
            convergence_modes_headings[convergence_modes_mastery].start,
        ),
        "o009-program-convergence-modes": convergence_modes_chunks[
            "o009_lab_convergence_modes"
        ],
        convergence_modes_mastery: convergence_modes_headings[
            convergence_modes_mastery
        ],
        "o009-mastery-convergence-modes-sequence": convergence_modes_blocks[
            "o009-mastery-convergence-modes-sequence"
        ],
        "o009-exercise-convergence-modes-mastery": convergence_modes_blocks[
            "o009-exercise-convergence-modes-mastery"
        ],
        "o009-hint-convergence-modes-1": convergence_modes_blocks[
            "o009-hint-convergence-modes-1"
        ],
        "o009-hint-convergence-modes-2": convergence_modes_blocks[
            "o009-hint-convergence-modes-2"
        ],
        "o009-answer-convergence-modes": convergence_modes_blocks[
            "o009-answer-convergence-modes"
        ],
        "o009-solution-convergence-modes": convergence_modes_blocks[
            "o009-solution-convergence-modes"
        ],
    }
    for stable_id, span in convergence_modes_body_spans.items():
        expected_hash = sha256(
            convergence_modes_text[span.start : span.end].encode("utf-8")
        )
        if by_id[stable_id]["target_sha256"] != expected_hash:
            raise RuntimeError(
                f"complete convergence-modes lab body hash differs: {stable_id}"
            )
        if by_id[stable_id]["payload"].get("body_extent") != "complete":
            raise RuntimeError(
                f"convergence-modes lab unit is not a complete body: {stable_id}"
            )
        if by_id[stable_id]["rights_id"] != (
            "rights.o009.lab.convergence-modes.cc-by-4.0"
        ):
            raise RuntimeError(
                f"convergence-modes lab rights binding differs: {stable_id}"
            )

    convergence_program = by_id["o009-program-convergence-modes"]
    if (
        convergence_program["source_local_id"] != "o009_lab_convergence_modes"
        or convergence_program["source_locator"]
        != (
            "source/labs/03-konvergensi-mode-dan-lln-clt.Rmd:"
            "chunk:o009_lab_convergence_modes"
        )
    ):
        raise RuntimeError("convergence-modes program lacks its exact R-chunk locator")
    convergence_estimation_solution = by_id[
        "o009-solution-convergence-modes-estimation"
    ]
    if (
        convergence_estimation_solution["source_local_id"] is not None
        or not convergence_estimation_solution["source_locator"].startswith(
            "source/labs/03-konvergensi-mode-dan-lln-clt.Rmd:L"
        )
    ):
        raise RuntimeError(
            "derived convergence-modes solution lacks its real line-range locator"
        )
    convergence_result = by_id["o009-results-convergence-modes"]
    convergence_reader_soup = BeautifulSoup(
        require_file(
            ROOT
            / "build"
            / "site"
            / "labs"
            / "03-konvergensi-mode-dan-lln-clt.html"
        ).decode("utf-8"),
        "lxml",
    )
    convergence_result_table = convergence_reader_soup.find(
        "table", id="o009-results-convergence-modes"
    )
    if (
        convergence_result_table is None
        or convergence_result["parent_id"] != "o009-program-convergence-modes"
        or convergence_result["payload"].get("unit_kind") != "result-table"
        or convergence_result["target_sha256"]
        != sha256(str(convergence_result_table).encode("utf-8"))
    ):
        raise RuntimeError(
            "convergence-modes result table lacks its exact reader/backend binding"
        )
    required_convergence_aliases = {
        "alias.frontmatter.o009-unit-convergence-modes": (
            "o009-unit-convergence-modes",
            "o009-lab-convergence-modes",
        ),
        "alias.frontmatter.o009-theory-random-prob-convergence": (
            "o009-theory-random-prob-convergence",
            "unit.o009.random.prob.convergence",
        ),
        "alias.reader.o009-results-convergence-modes": (
            "o009-results-convergence-modes",
            "o009-results-convergence-modes",
        ),
    }
    for alias_id, (alias_value, canonical_id) in required_convergence_aliases.items():
        row = aliases_by_id.get(alias_id)
        if (
            row is None
            or row["alias"] != alias_value
            or row["canonical_id"] != canonical_id
        ):
            raise RuntimeError(
                f"convergence-modes frontmatter/reader alias differs: {alias_id}"
            )

    conditional_text = require_file(LAB_CONDITIONAL_MARTINGALE).decode("utf-8")
    conditional_blocks = fenced_div_spans(conditional_text)
    conditional_root = "o009-lab-conditional-martingale"
    conditional_headings = heading_spans(
        conditional_text, conditional_blocks[conditional_root]
    )
    conditional_chunks = {
        name: span
        for name, span in r_chunk_spans(conditional_text)
        if name
    }
    conditional_body_spans = {
        conditional_root: conditional_blocks[conditional_root],
        "o009-conditional-martingale-goals": conditional_headings[
            "o009-conditional-martingale-goals"
        ],
        "o009-conditional-expectation-audit": conditional_headings[
            "o009-conditional-expectation-audit"
        ],
        "o009-exercise-conditional-martingale-audit": conditional_blocks[
            "o009-exercise-conditional-martingale-audit"
        ],
        "o009-program-conditional-martingale": conditional_chunks[
            "o009_lab_conditional_martingale"
        ],
        "o009-optional-stopping-diagnostic": conditional_headings[
            "o009-optional-stopping-diagnostic"
        ],
        "o009-hint-conditional-martingale-audit-1": conditional_blocks[
            "o009-hint-conditional-martingale-audit-1"
        ],
        "o009-hint-conditional-martingale-audit-2": conditional_blocks[
            "o009-hint-conditional-martingale-audit-2"
        ],
        "o009-hint-conditional-martingale-audit-3": conditional_blocks[
            "o009-hint-conditional-martingale-audit-3"
        ],
        "o009-answer-conditional-martingale-audit": conditional_blocks[
            "o009-answer-conditional-martingale-audit"
        ],
        "o009-solution-conditional-martingale-audit": conditional_blocks[
            "o009-solution-conditional-martingale-audit"
        ],
    }
    conditional_rights_id = (
        "rights.o009.lab.conditional-martingale.cc-by-4.0"
    )
    for stable_id, span in conditional_body_spans.items():
        expected_hash = sha256(
            conditional_text[span.start : span.end].encode("utf-8")
        )
        if by_id[stable_id]["target_sha256"] != expected_hash:
            raise RuntimeError(
                f"complete conditional-martingale lab body hash differs: {stable_id}"
            )
        if by_id[stable_id]["payload"].get("body_extent") != "complete":
            raise RuntimeError(
                f"conditional-martingale lab unit is not a complete body: {stable_id}"
            )
        if by_id[stable_id]["rights_id"] != conditional_rights_id:
            raise RuntimeError(
                f"conditional-martingale lab rights binding differs: {stable_id}"
            )
    conditional_program = by_id["o009-program-conditional-martingale"]
    if (
        conditional_program["source_local_id"]
        != "o009_lab_conditional_martingale"
        or conditional_program["source_locator"]
        != (
            "source/labs/04-nilai-harapan-bersyarat-martingal.Rmd:"
            "chunk:o009_lab_conditional_martingale"
        )
    ):
        raise RuntimeError(
            "conditional-martingale program lacks its exact R-chunk locator"
        )
    conditional_reader_soup = BeautifulSoup(
        require_file(
            ROOT
            / "build"
            / "site"
            / "labs"
            / "04-nilai-harapan-bersyarat-martingal.html"
        ).decode("utf-8"),
        "lxml",
    )
    conditional_result_table = conditional_reader_soup.find(
        "table", id="o009-results-conditional-martingale"
    )
    conditional_result = by_id["o009-results-conditional-martingale"]
    if (
        conditional_result_table is None
        or len(conditional_result_table.find_all("tr")) != 2
        or len(conditional_result_table.find_all("th")) != 18
        or conditional_result["parent_id"]
        != "o009-program-conditional-martingale"
        or conditional_result["payload"].get("unit_kind") != "result-table"
        or conditional_result["target_sha256"]
        != sha256(str(conditional_result_table).encode("utf-8"))
        or conditional_result["rights_id"] != conditional_rights_id
    ):
        raise RuntimeError(
            "conditional-martingale result table lacks its exact reader/backend binding"
        )
    required_conditional_aliases = {
        "alias.frontmatter.o009-unit-conditional-martingale-lab": (
            "o009-unit-conditional-martingale-lab",
            conditional_root,
        ),
        "alias.frontmatter.o009-theory-random-conditional-martingale": (
            "o009-theory-random-conditional-martingale",
            "unit.o009.random.expect.conditional2",
        ),
        "alias.reader.o009-results-conditional-martingale": (
            "o009-results-conditional-martingale",
            "o009-results-conditional-martingale",
        ),
    }
    for alias_id, (alias_value, canonical_id) in required_conditional_aliases.items():
        row = aliases_by_id.get(alias_id)
        if (
            row is None
            or row["alias"] != alias_value
            or row["canonical_id"] != canonical_id
        ):
            raise RuntimeError(
                f"conditional-martingale frontmatter/reader alias differs: {alias_id}"
            )
    expected_conditional_dependencies = {
        "unit.o009.random.expect.conditional2",
        "unit.o009.random.prob.stop",
        "unit.o009.random.martingales.properties",
        "unit.o009.random.martingales.stop",
    }
    actual_conditional_dependencies = {
        row["target_id"]
        for row in relations
        if row["source_id"] == conditional_root
        and row["relation_type"] == "depends-on"
    }
    if actual_conditional_dependencies != expected_conditional_dependencies:
        raise RuntimeError(
            "conditional-martingale dependency boundary differs: "
            f"actual={sorted(actual_conditional_dependencies)}"
        )
    conditional_record_ids = set(conditional_body_spans) | {
        "o009-results-conditional-martingale"
    }
    if any(
        row["source_id"] in conditional_record_ids
        or row["target_id"] in conditional_record_ids
        for row in read_csv("translations.csv")
    ):
        raise RuntimeError(
            "wholly original conditional-martingale lab claims a translation row"
        )

    (
        expected_brownian_entities,
        expected_brownian_segments,
        expected_brownian_relations,
        expected_brownian_aliases,
        expected_brownian_translations,
        expected_brownian_corrections,
    ) = brownian_diagnostics_lab_entities()
    if (
        len(expected_brownian_entities),
        len(expected_brownian_segments),
        len(expected_brownian_relations),
        len(expected_brownian_aliases),
        len(expected_brownian_translations),
        len(expected_brownian_corrections),
    ) != (12, 33, 28, 14, 0, 1):
        raise RuntimeError("Brownian-diagnostics expected backend delta changed")
    for expected in expected_brownian_entities:
        if by_id.get(expected["id"]) != expected:
            raise RuntimeError(
                f"Brownian-diagnostics entity differs: {expected['id']}"
            )
    actual_brownian_segments = sorted(
        (
            item
            for item in segments
            if item["id"].startswith("segment.o009.lab.brownian-diagnostics.")
        ),
        key=lambda item: item["id"],
    )
    if actual_brownian_segments != sorted(
        expected_brownian_segments, key=lambda item: item["id"]
    ):
        raise RuntimeError(
            "Brownian-diagnostics 33-segment source/hash/rights closure differs"
        )
    relations_by_id = {row["relation_id"]: row for row in relations}
    for expected in expected_brownian_relations:
        if relations_by_id.get(expected["relation_id"]) != expected:
            raise RuntimeError(
                f"Brownian-diagnostics relation differs: {expected['relation_id']}"
            )
    expected_brownian_relation_ids = {
        row["relation_id"] for row in expected_brownian_relations
    }
    brownian_record_ids = {row["id"] for row in expected_brownian_entities}
    actual_brownian_relation_ids = {
        row["relation_id"]
        for row in relations
        if row["source_id"] in brownian_record_ids
        or row["target_id"] in brownian_record_ids
    }
    if actual_brownian_relation_ids != expected_brownian_relation_ids:
        raise RuntimeError(
            "Brownian-diagnostics relation closure is not exactly 28 rows"
        )
    for expected in expected_brownian_aliases:
        if aliases_by_id.get(expected["alias_id"]) != expected:
            raise RuntimeError(
                f"Brownian-diagnostics alias differs: {expected['alias_id']}"
            )
    correction_rows_by_id = {
        row["correction_id"]: row for row in read_csv("corrections.csv")
    }
    for expected in expected_brownian_corrections:
        if correction_rows_by_id.get(expected["correction_id"]) != expected:
            raise RuntimeError(
                f"Brownian-diagnostics correction differs: {expected['correction_id']}"
            )
    brownian_translation_rows = [
        row
        for row in read_csv("translations.csv")
        if row["source_id"] in brownian_record_ids
        or row["target_id"] in brownian_record_ids
    ]
    if brownian_translation_rows or expected_brownian_translations:
        raise RuntimeError(
            "wholly original Brownian-diagnostics lab claims a translation row"
        )
    expected_brownian_outcomes = {
        "outcome.o009.audit-fdd-versus-path-law-convergence",
        "outcome.o009.analyze-brownian-scaling-irregularity",
        "outcome.o009.apply-brownian-strong-markov-reflection",
        "outcome.o009.derive-brownian-hitting-maximum-laws",
    }
    if {
        row["target_id"]
        for row in expected_brownian_relations
        if row["relation_type"] == "teaches"
    } != expected_brownian_outcomes or {
        row["target_id"]
        for row in expected_brownian_relations
        if row["relation_type"] == "assesses"
    } != expected_brownian_outcomes:
        raise RuntimeError(
            "Brownian-diagnostics teaches/assesses pairs differ from the four existing outcomes"
        )
    brownian_artifact = artifacts.get(
        "artifact.input.target-lab-brownian-diagnostics"
    )
    if (
        brownian_artifact is None
        or brownian_artifact["path"] != relative(LAB_BROWNIAN_DIAGNOSTICS)
        or brownian_artifact["sha256"]
        != sha256(require_file(LAB_BROWNIAN_DIAGNOSTICS))
    ):
        raise RuntimeError("Brownian-diagnostics source artifact binding differs")
    brownian_qa = {
        row["event_id"]: row for row in read_csv("qa_events.csv")
    }.get("qa.o009.original-lab-05-brownian-diagnostics-binding")
    if brownian_qa is None or brownian_qa["result"] != "pass":
        raise RuntimeError("Brownian-diagnostics QA event is absent or failing")

    current_donor, _, _, _ = donor_components()
    current_markov_donor, _, _, _ = markov_donor_components()
    for donor in current_donor + current_markov_donor:
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
