#!/usr/bin/env python3
"""Build and verify the bounded offline O009 theory–lab reader."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
AUTH_RANDOM = ROOT / "authority" / "random"
REPRODUCIBLE_BUILD_TIMESTAMP = (
    ROOT / "00_control" / "REPRODUCIBLE_BUILD_TIMESTAMP_UTC.txt"
)
LAB_SPECS = (
    {
        "source": ROOT / "source" / "labs" / "01-konvergensi-monte-carlo.Rmd",
        "output": Path("labs/01-konvergensi-monte-carlo.html"),
        "chunk_id": "o009_lab_convergence_mc",
        "placeholder": "<!-- O009_EXECUTION_TABLE -->",
        "expected_fields": (
            "n",
            "seed",
            "estimate",
            "exact_value",
            "signed_error",
            "absolute_error",
        ),
        "table_headers": (
            "n",
            "benih",
            "taksiran",
            "nilai eksak",
            "galat bertanda",
            "galat mutlak",
        ),
        "table_id": "o009-results-convergence-mc",
        "required_code": "set.seed(12341)",
        "nav_label": "Laboratorium Monte Carlo",
        "front_matter": {
            "title": "Konvergensi Monte Carlo",
            "lang": "id-ID",
            "course_id": "o009",
            "unit_id": "o009-unit-convergence",
            "lab_id": "o009-lab-convergence-mc",
            "matched_theory_id": "o009-theory-random-prob-convergence",
            "target_locale": "id-ID",
            "source_alias": "zitkovic-stochastic-book:source/02-simulation.Rmd#L758-L832",
            "source_commit": "e2b35ad91a3689454ae6455e8ffc510a90760c0d",
            "source_slice_sha256": "e95fec79fc93f1239951864901c570b8aaa44e77c6a02be64d48bda4aa5c265f",
            "donor_license": "CC0-1.0",
            "adaptation_license": "CC-BY-4.0",
        },
        "golden_rows": (
            {
                "n": "10",
                "seed": "12341",
                "estimate": "0.177976805338",
                "exact_value": "0.250000000000",
                "signed_error": "0.072023194662",
                "absolute_error": "0.072023194662",
            },
            {
                "n": "1000",
                "seed": "12342",
                "estimate": "0.256464342623",
                "exact_value": "0.250000000000",
                "signed_error": "-0.006464342623",
                "absolute_error": "0.006464342623",
            },
            {
                "n": "1000000",
                "seed": "12342",
                "estimate": "0.250381011435",
                "exact_value": "0.250000000000",
                "signed_error": "-0.000381011435",
                "absolute_error": "0.000381011435",
            },
        ),
    },
    {
        "source": ROOT / "source" / "labs" / "02-simulasi-rantai-markov.Rmd",
        "output": Path("labs/02-simulasi-rantai-markov.html"),
        "chunk_id": "o009_lab_markov_gambler_ruin",
        "placeholder": "<!-- O009_MARKOV_EXECUTION_TABLE -->",
        "expected_fields": (
            "seed",
            "simulasi",
            "horizon",
            "keadaan_awal",
            "batas_atas",
            "berhasil",
            "taksiran",
            "eksak_sampai_horizon",
            "peluang_akhir",
            "celah_ekor_eksak",
            "galat_mutlak",
        ),
        "table_headers": (
            "benih",
            "simulasi",
            "horizon",
            "awal",
            "batas atas",
            "berhasil",
            "taksiran",
            "eksak hingga horizon",
            "peluang akhir",
            "celah ekor eksak",
            "galat mutlak",
        ),
        "table_id": "o009-results-markov-gambler-ruin",
        "required_code": "set.seed(seed)",
        "nav_label": "Laboratorium rantai Markov",
        "front_matter": {
            "title": "Simulasi Rantai Markov: Kebangkrutan Penjudi",
            "lang": "id-ID",
            "course_id": "o009",
            "unit_id": "o009-unit-markov-general",
            "lab_id": "o009-lab-markov-gambler-ruin",
            "matched_theory_id": "o009-theory-random-markov-general",
            "target_locale": "id-ID",
            "source_alias": "zitkovic-stochastic-book:source/05-Markov-chains.Rmd#L601-L666",
            "source_commit": "e2b35ad91a3689454ae6455e8ffc510a90760c0d",
            "source_slice_sha256": "dcabe361eaaacaa537966f2bf8809dd8eac52e28392edc78d8e289c8c9be2bd8",
            "donor_license": "CC0-1.0",
            "adaptation_license": "CC-BY-4.0",
        },
        "golden_rows": (
            {
                "seed": "20260822",
                "simulasi": "1000",
                "horizon": "100",
                "keadaan_awal": "1",
                "batas_atas": "3",
                "berhasil": "592",
                "taksiran": "0.592000000000",
                "eksak_sampai_horizon": "0.571428571429",
                "peluang_akhir": "0.571428571429",
                "celah_ekor_eksak": "1.248349703776e-33",
                "galat_mutlak": "0.020571428571",
            },
        ),
    },
    {
        "source": ROOT / "source" / "labs" / "03-konvergensi-mode-dan-lln-clt.Rmd",
        "output": Path("labs/03-konvergensi-mode-dan-lln-clt.html"),
        "chunk_id": "o009_lab_convergence_modes",
        "placeholder": "<!-- O009_CONVERGENCE_MODES_EXECUTION_TABLE -->",
        "expected_fields": (
            "kasus",
            "n",
            "benih",
            "nilai",
            "target",
            "galat_mutlak",
            "skala_teori",
        ),
        "table_headers": (
            "kasus",
            "n",
            "benih",
            "nilai",
            "target",
            "galat mutlak",
            "skala teori",
        ),
        "table_id": "o009-results-convergence-modes",
        "required_code": "set.seed(20260829)",
        "nav_label": "Laboratorium mode konvergensi",
        "front_matter": {
            "title": "Mode konvergensi dan pembanding LLN/CLT",
            "lang": "id-ID",
            "course_id": "o009",
            "unit_id": "o009-unit-convergence-modes",
            "lab_id": "o009-lab-convergence-modes",
            "matched_theory_id": "o009-theory-random-prob-convergence",
            "prerequisite_id": "resource.o006.c140.shared",
            "target_locale": "id-ID",
            "source_alias": "original-synthesis: convergence-modes-and-o006-comparison",
            "source_commit": "local-original-checkpoint-35",
            "source_slice_sha256": "not-applicable-original",
            "donor_license": "none",
            "adaptation_license": "CC-BY-4.0",
            "model": "OpenAI Codex gpt-5.6-sol, Ultra.",
        },
        "golden_rows": (
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
        ),
    },
    {
        "source": (
            ROOT
            / "source"
            / "labs"
            / "04-nilai-harapan-bersyarat-martingal.Rmd"
        ),
        "output": Path("labs/04-nilai-harapan-bersyarat-martingal.html"),
        "chunk_id": "o009_lab_conditional_martingale",
        "placeholder": "<!-- O009_CONDITIONAL_MARTINGALE_EXECUTION_TABLE -->",
        "expected_fields": (
            "seed",
            "ruang_hingga",
            "E_X",
            "galat_bersyarat",
            "galat_menara",
            "galat_martingal",
            "rerata_S_tau_b",
            "target_E_S_tau_b",
            "cap_tau_plus",
            "laju_kena_batas",
            "target_laju",
            "rerata_S_tau_plus_terpotong",
            "target_E_S_tau_plus_terpotong",
            "rerata_S_hanya_yang_kena",
            "target_S_tau_plus",
            "celah_naif",
            "toleransi",
            "status",
        ),
        "nonnumeric_fields": ("ruang_hingga", "status"),
        "table_headers": (
            "benih",
            "ruang hingga",
            "E[X]",
            "galat bersyarat",
            "galat menara",
            "galat martingal",
            "rerata S_tau_b",
            "target E[S_tau_b]",
            "cap tau_+",
            "laju kena batas",
            "target laju",
            "rerata S_(tau_+ terpotong)",
            "target E[S_(tau_+ terpotong)]",
            "rerata S hanya yang kena",
            "target S_tau_+",
            "celah naif",
            "toleransi",
            "status",
        ),
        "table_id": "o009-results-conditional-martingale",
        "required_code": "set.seed(20260829)",
        "nav_label": "Laboratorium martingal dan waktu henti",
        "front_matter": {
            "title": (
                "Nilai harapan bersyarat, filtrasi, dan penghentian opsional"
            ),
            "lang": "id-ID",
            "course_id": "o009",
            "unit_id": "o009-unit-conditional-martingale-lab",
            "lab_id": "o009-lab-conditional-martingale",
            "matched_theory_id": "o009-theory-random-conditional-martingale",
            "target_locale": "id-ID",
            "source_alias": (
                "Random:expect/Conditional2.html;prob/Stop.html;"
                "martingales/Properties.html;martingales/Stop.html"
            ),
            "source_authority": "authority/random/RANDOM_AUTHORITY_RECEIPT.json",
            "source_authority_sha256": (
                "ea3786a05f3a1ccf444818f17516ce85065c76759bfc8071d43fd8a98c643eb4"
            ),
            "source_relation": (
                "original diagnostic informed by the cited theory pages; "
                "no source HTML bytes are copied"
            ),
            "adaptation_license": "CC-BY-4.0",
            "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra.",
            "non_endorsement": (
                "Edisi independen; tidak didukung atau disahkan oleh Kyle "
                "Siegrist, Random, atau penulis sumber."
            ),
        },
        "golden_rows": (
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
            },
        ),
    },
    {
        "source": (
            ROOT
            / "source"
            / "labs"
            / "05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.Rmd"
        ),
        "output": Path(
            "labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
        ),
        "chunk_id": "o009_lab_brownian_diagnostics",
        "placeholder": "<!-- O009_BROWNIAN_EXECUTION_TABLE -->",
        "expected_fields": (
            "n",
            "k_endpoint",
            "ambang_kena",
            "cdf_endpoint_eksak",
            "target_normal",
            "galat_cdf",
            "prob_kena_eksak",
            "target_brown",
            "galat_kena",
            "qv_mesh_alami",
            "qv_refinemen_pralimit",
            "variasi_total",
            "refinemen_r",
            "toleransi",
            "status",
        ),
        "nonnumeric_fields": ("status",),
        "table_headers": (
            "n",
            "k titik akhir",
            "ambang kena",
            "CDF titik akhir eksak",
            "target normal",
            "galat CDF",
            "peluang kena eksak",
            "target Brown",
            "galat kena",
            "QV mesh alami",
            "QV refinemen pralimit",
            "variasi total",
            "refinemen r",
            "toleransi",
            "status",
        ),
        "table_id": "o009-results-brownian-diagnostics",
        "required_code": "ns = c(64L, 256L, 1024L, 4096L)",
        "nav_label": "Laboratorium diagnostik gerak Brown",
        "front_matter": {
            "title": "Gerak Brown: Donsker, variasi kuadratik, dan waktu kena",
            "lang": "id-ID",
            "course_id": "o009",
            "unit_id": "o009-unit-brownian-diagnostics-lab",
            "lab_id": "o009-lab-brownian-diagnostics",
            "matched_theory_id": "o009-theory-random-brown-standard",
            "prerequisite_id": "resource.o006.c140.shared",
            "target_locale": "id-ID",
            "source_alias": "Random:brown/Standard.html",
            "source_authority": "authority/random/RANDOM_AUTHORITY_RECEIPT.json",
            "source_authority_sha256": (
                "ea3786a05f3a1ccf444818f17516ce85065c76759bfc8071d43fd8a98c643eb4"
            ),
            "source_page_sha256": (
                "brown/Standard.html="
                "3693677d4d4c75e7888f806a027fa25020babeb80c720bbb77ad6fd0c639276b"
            ),
            "source_license_witness": (
                "CC-BY-2.0 and CC-BY-1.0 witnesses are retained separately "
                "in RANDOM_AUTHORITY_RECEIPT.json"
            ),
            "source_relation": (
                "wholly original diagnostic informed by the cited Random "
                "theory page and the shared O006/C140 CLT prerequisite; no "
                "Random HTML or O006 bytes are copied"
            ),
            "adaptation_license": "CC-BY-4.0",
            "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra.",
            "non_endorsement": (
                "Edisi independen; tidak didukung atau disahkan oleh Kyle "
                "Siegrist, Random, atau penulis sumber."
            ),
        },
        "required_witnesses": (
            'prerequisite_id: "resource.o006.c140.shared"',
            "Tidak ada byte HTML sumber yang disalin ke",
            "tidak ada byte O006 yang disalin atau diterbitkan",
        ),
        "golden_rows": (
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
        ),
    },
)
LAB_SOURCE = LAB_SPECS[0]["source"]
SOURCE_INDEX = ROOT / "source" / "index.md"
SOURCE_CSS = ROOT / "source" / "reader.css"
SOURCE_TWO_STATE_APP = ROOT / "source" / "apps" / "two-state.html"
SUPPLEMENT_SPECS = (
    ("mastery/01-konvergensi-01-02.md", "mastery/01-konvergensi-01-02.html", "Penguasaan konvergensi 01–02", "mastery"),
    ("mastery/02-konvergensi-03-04.md", "mastery/02-konvergensi-03-04.html", "Penguasaan konvergensi 03–04", "mastery"),
    ("mastery/03-konvergensi-05.md", "mastery/03-konvergensi-05.html", "Penguasaan konvergensi 05", "mastery"),
    ("mastery/04-bersyarat-kernel-01-02.md", "mastery/04-bersyarat-kernel-01-02.html", "Penguasaan nilai harapan bersyarat dan kernel 01–02", "mastery"),
    ("mastery/05-bersyarat-kernel-03.md", "mastery/05-bersyarat-kernel-03.html", "Penguasaan nilai harapan bersyarat dan kernel 03", "mastery"),
    ("mastery/06-martingal-01-02.md", "mastery/06-martingal-01-02.html", "Penguasaan martingal 01–02", "mastery"),
    ("mastery/07-martingal-03-04.md", "mastery/07-martingal-03-04.html", "Penguasaan martingal 03–04", "mastery"),
    ("mastery/08-martingal-05.md", "mastery/08-martingal-05.html", "Penguasaan martingal 05", "mastery"),
    ("mastery/09-poisson-konstruksi-01.md", "mastery/09-poisson-konstruksi-01.html", "Penguasaan konstruksi Poisson", "mastery"),
    ("mastery/10-brown-01.md", "mastery/10-brown-01.html", "Penguasaan gerak Brown 01", "mastery"),
    ("mastery/11-brown-02.md", "mastery/11-brown-02.html", "Penguasaan gerak Brown 02", "mastery"),
    ("mastery/12-brown-03-04.md", "mastery/12-brown-03-04.html", "Penguasaan gerak Brown 03–04", "mastery"),
    ("mastery/13-brown-05-06.md", "mastery/13-brown-05-06.html", "Penguasaan gerak Brown 05–06", "mastery"),
    ("mastery/14-brown-07.md", "mastery/14-brown-07.html", "Penguasaan gerak Brown 07", "mastery"),
    ("assessments/01-formulir-kumulatif-a.md", "assessments/01-formulir-kumulatif-a.html", "Penilaian kumulatif — Formulir A", "assessment"),
    ("assessments/02-formulir-kumulatif-b.md", "assessments/02-formulir-kumulatif-b.html", "Penilaian kumulatif — Formulir B", "assessment"),
)
QUANTECON_COMPONENT_ROOT = ROOT / "build" / "components" / "quantecon_memoryless"
QUANTECON_POISSON_COMPONENT_ROOT = ROOT / "build" / "components" / "quantecon_poisson"
QUANTECON_MARKOV_PROP_COMPONENT_ROOT = ROOT / "build" / "components" / "quantecon_markov_prop"
QUANTECON_KOLMOGOROV_BWD_COMPONENT_ROOT = ROOT / "build" / "components" / "quantecon_kolmogorov_bwd"
QUANTECON_KOLMOGOROV_FWD_COMPONENT_ROOT = ROOT / "build" / "components" / "quantecon_kolmogorov_fwd"
QUANTECON_KOLMOGOROV_FWD_TARGET = (
    ROOT / "source" / "quantecon" / "lectures" / "kolmogorov_fwd.md"
)
QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA = (
    ROOT / "qa" / "QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA.json"
)
QUANTECON_GENERATORS_COMPONENT_ROOT = (
    ROOT / "build" / "components" / "quantecon_generators"
)
QUANTECON_GENERATORS_TARGET = (
    ROOT / "source" / "quantecon" / "lectures" / "generators.md"
)
QUANTECON_UC_MC_SEMIGROUPS_COMPONENT_ROOT = (
    ROOT / "build" / "components" / "quantecon_uc_mc_semigroups"
)
QUANTECON_UC_MC_SEMIGROUPS_TARGET = (
    ROOT / "source" / "quantecon" / "lectures" / "uc_mc_semigroups.md"
)
QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA = (
    ROOT / "qa" / "QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA.json"
)
QUANTECON_ERGODICITY_COMPONENT_ROOT = (
    ROOT / "build" / "components" / "quantecon_ergodicity"
)
QUANTECON_ERGODICITY_TARGET = (
    ROOT / "source" / "quantecon" / "lectures" / "ergodicity.md"
)
QUANTECON_ERGODICITY_NUMERICAL_QA = (
    ROOT / "qa" / "QUANTECON_ERGODICITY_NUMERICAL_QA.json"
)
SITE = ROOT / "build" / "site"
R_SCRIPT = ROOT / "tools" / "R-4.6.1" / "bin" / "Rscript.exe"
PANDOC = "pandoc"

BUILD_RECEIPT_SCHEMA = "o009.reader-build.v2"
R_SCRIPT_SHA256 = "d829bcf7e9fa1d7e3e828c565c3cdbb1ed416f551f4fa6fd4dfcdf231e33e5e8"
R_VERSION = "R version 4.6.1 (2026-06-24 ucrt)"
R_RNG = "Mersenne-Twister / Inversion / Rejection"
PANDOC_VERSION = "pandoc 3.9.0.2"
PANDOC_SHA256 = "24f1593d7ba9f511bc428be3d7177d2a8ddc4bf60457c9f24a888a4790748c5d"

RANDOM_MANIFEST_SHA256 = "2ee154a38b57201457538db8c0e7df592a052eade8dcfda217605810f04f21e4"
MATHJAX_SHA256 = "dba9c7e8646389650c445e0547023942bed229b3fdb9513b1c6c01237af0b81a"
MATHJAX_BOLDSYMBOL_SHA256 = "716cf8735d00abfb1627f8adbbf4aeb915ac9b5c55d47aeaf276e73dac6a2aa1"
RANDOM_BASE_URL = "https://www.randomservices.org/random/"
KERNELS_READER_CORRECTIONS = (
    {
        "id": "sequence-index",
        "old": r"\{A_j: i \in J\}",
        "new": r"\{A_j: j \in J\}",
        "description": "Use j, rather than the unrelated i, as the index of the disjoint family.",
    },
    {
        "id": "kernel-measurability-sigma-algebra",
        "old": r"untuk \( A \in \mathscr S \), serta sifat-sifat dasar integral.",
        "new": r"untuk \( A \in \mathscr T \), serta sifat-sifat dasar integral.",
        "description": "Use the target sigma-algebra in the kernel measurability argument.",
    },
    {
        "id": "operator-norm-bound",
        "old": r"\(\|Kf\| = \|K\| \|f\|\)",
        "new": r"\(\|Kf\| \le \|K\| \|f\|\)",
        "description": "State the valid norm inequality for an arbitrary bounded function.",
    },
    {
        "id": "operator-codomain",
        "old": r"\(Kf \in \mathscr B(T)\)",
        "new": r"\(Kf \in \mathscr B(S)\)",
        "description": "Place Kf in the bounded-function space on its actual domain S.",
    },
    {
        "id": "kernel-product-integrand-variable",
        "old": r"\int_S K(x, dy) L(x, A) =",
        "new": r"\int_S K(x, dy) L(y, A) =",
        "description": "Use the integration variable y in the composed-kernel proof.",
    },
    {
        "id": "right-operator-domain",
        "old": r"\( c K f(x) = c \int_S K(x, dy) f(y) \)",
        "new": r"\( c K f(x) = c \int_T K(x, dy) f(y) \)",
        "description": "Integrate the right action of a kernel over its target space T.",
    },
    {
        "id": "associative-function-domain",
        "old": r"\( K L f(x) = \int_S K(x, dy) \int_T L(y, dz) f(z) \) untuk \( x \in R \), dengan mengandaikan bahwa integralnya ada untuk \( x \in S \).",
        "new": r"\( K L f(x) = \int_S K(x, dy) \int_T L(y, dz) f(z) \) untuk \( x \in R \), dengan mengandaikan bahwa integralnya ada untuk \( x \in R \).",
        "description": "Use R, the domain of the composed operator, in the existence qualification.",
    },
    {
        "id": "distributivity-function-domains",
        "old": r"serta \( f \) dan \( g \) adalah fungsi terukur dari \( T \) ke \( \R \).",
        "new": r"serta \( f \) dan \( g \) adalah fungsi terukur dari \( T \) ke \( \R \), sedangkan \( h \) dan \( j \) adalah fungsi terukur dari \( S \) ke \( \R \).",
        "description": "Introduce correctly typed S-domain functions for the measure identities.",
    },
    {
        "id": "distributivity-measure-sum-function",
        "old": r"\( \mu(f + g) = \mu f + \mu g \)",
        "new": r"\( \mu(h + j) = \mu h + \mu j \)",
        "description": "Use the S-domain functions in the integral additivity identity.",
    },
    {
        "id": "distributivity-measure-addition-function",
        "old": r"\( (\mu + \nu) f = \mu f + \nu f \)",
        "new": r"\( (\mu + \nu) h = \mu h + \nu h \)",
        "description": "Use an S-domain function in the measure-addition identity.",
    },
    {
        "id": "positive-measure-cone-linearity",
        "old": "keduanya merupakan operator <em>linear</em>.",
        "new": "operator pertama aditif dan homogen positif pada kerucut ukuran positif, sedangkan operator kedua linear.",
        "description": "Do not call the positive-measure cone a real vector space.",
    },
    {
        "id": "invariant-kernel-domain",
        "old": r'<p class="dfn">Misalkan \( K \) adalah kernel dari \( (S, \mathscr S) \) ke \( (T, \mathscr T) \).</p>',
        "new": r'<p class="dfn">Misalkan \( K \) adalah kernel pada \( (S, \mathscr S) \).</p>',
        "description": "Require an endokernel so the invariant-measure and invariant-function equalities are typed.",
    },
    {
        "id": "invariant-function-domain",
        "old": r"Fungsi terukur \( f: T \to \R \) yang memenuhi \( K f = f \)",
        "new": r"Fungsi terukur \( f: S \to \R \) yang memenuhi \( K f = f \)",
        "description": "Use S as the domain of an invariant function for an endokernel on S.",
    },
    {
        "id": "probability-product-argument",
        "old": r"\[P Q(T) =",
        "new": r"\[(P Q)(x, T) =",
        "description": "Supply the state argument in the probability-kernel product calculation.",
    },
    {
        "id": "probability-measure-parenthesis",
        "old": r"\( (S, \mathscr S)) \)",
        "new": r"\( (S, \mathscr S) \)",
        "description": "Remove the extra closing parenthesis in the measure-space reference.",
    },
    {
        "id": "kernel-function-right-domain",
        "old": r"\[ K f(x) = \int_S k(x, y) f(y) \mu(dy), \quad x \in S \]",
        "new": r"\[ K f(x) = \int_T k(x, y) f(y) \mu(dy), \quad x \in S \]",
        "description": "Integrate the kernel function over the target space T.",
    },
    {
        "id": "kernel-function-proof-domain",
        "old": r"\[ K f(x) = \int_S K(x, dy) f(y) = \int_S k(x, y) f(y) \mu(dy), \quad x \in S \]",
        "new": r"\[ K f(x) = \int_T K(x, dy) f(y) = \int_T k(x, y) f(y) \mu(dy), \quad x \in S \]",
        "description": "Use T in both integrals of the kernel-function proof.",
    },
    {
        "id": "doubly-stochastic-target",
        "old": r"\( \int_S \lambda(dx) k(x, y) = 1 \) untuk \( y \in S \)",
        "new": r"\( \int_S \lambda(dx) k(x, y) = 1 \) untuk \( y \in T \)",
        "description": "Quantify the second doubly stochastic condition over the target space T.",
    },
    {
        "id": "product-density-reference-measure",
        "old": r"= \int_B k l(x, z) \mu(dz)",
        "new": r"= \int_B k l(x, z) \rho(dz)",
        "description": "Use rho, the target reference measure, in the product-density conclusion.",
    },
    {
        "id": "discrete-operator-sum-domain",
        "old": r"\[K f(x) = \sum_{y \in S} K(x, y) f(y), \quad x \in S \]",
        "new": r"\[K f(x) = \sum_{y \in T} K(x, y) f(y), \quad x \in S \]",
        "description": "Sum the right operator over the target index set T.",
    },
    {
        "id": "discrete-kernel-product",
        "old": r"\[ K L(x, z) = \sum_{y \in T} K(x, y) L(x, z), \quad (x, z) \in S \times L \]",
        "new": r"\[ K L(x, z) = \sum_{y \in T} K(x, y) L(y, z), \quad (x, z) \in S \times U \]",
        "description": "Use y in the second matrix factor and U as the product kernel's target space.",
    },
    {
        "id": "conditional-expectation-integral-domain",
        "old": r"\int_S P(x, dy) f(y)",
        "new": r"\int_T P(x, dy) f(y)",
        "description": "Integrate a T-valued conditional distribution over T.",
    },
    {
        "id": "conditional-second-moment-macro",
        "old": r"\( E\left(Y^2 \bigm| X = x\right) = P g(x)",
        "new": r"\( \E\left(Y^2 \bigm| X = x\right) = P g(x)",
        "description": "Use the defined expectation macro in the conditional second moment.",
    },
    {
        "id": "normal-mixture-equality",
        "old": r"\[ f P(y) \int_{-\infty}^\infty f(x) p(x, y) dx =",
        "new": r"\[ f P(y) = \int_{-\infty}^\infty f(x) p(x, y) dx =",
        "description": "Restore the missing equality sign in the normal-mixture density calculation.",
    },
    {
        "id": "exponential-product-duplicate-integral",
        "old": r"\int_0^\infty p(r, x) p(x, y) \, dx = \int_0^\infty = \int_0^\infty r x",
        "new": r"\int_0^\infty p(r, x) p(x, y) \, dx = \int_0^\infty r x",
        "description": "Remove the duplicated empty integral in the exponential-kernel product.",
    },
    {
        "id": "poisson-left-action-statement",
        "old": r"\( g P = f \)",
        "new": r"\( g P = f + \bs{1} \)",
        "description": "State the correct left action for g(r)=r under the Poisson family.",
    },
    {
        "id": "poisson-left-action-value",
        "old": r"\frac{r^{n+1}}{n!} dr = n \]",
        "new": r"\frac{r^{n+1}}{n!} dr = n + 1 \]",
        "description": "Evaluate the gamma integral as n+1 rather than n.",
    },
    {
        "id": "normal-kernel-positive-power",
        "old": r"Untuk \( n \in \N \), tentukan \( p^n \)",
        "new": r"Untuk \( n \in \N_+ \), tentukan \( p^n \)",
        "description": "Restrict density powers to positive n; the identity kernel at n=0 has no Lebesgue density.",
    },
    {
        "id": "normal-kernel-orientation",
        "old": r"\( x \mapsto p(x, \mu) \) adalah fungsi kepadatan probabilitas normal dengan rata-rata \( \mu \)",
        "new": r"\( x \mapsto p(\mu, x) \) adalah fungsi kepadatan probabilitas normal dengan rata-rata \( \mu \)",
        "description": "Keep the parameter first and observation second in the normal kernel.",
    },
    {
        "id": "normal-kernel-square-variables",
        "old": r"\[ p^2(\mu, x) = \int_{-\infty}^\infty p(\mu, t) p(t, y) \, dt = \frac{1}{\sqrt{4 \pi}} e^{-\frac{1}{4}(x - \mu)^2} \]",
        "new": r"\[ p^2(\mu, x) = \int_{-\infty}^\infty p(\mu, t) p(t, x) \, dt = \frac{1}{\sqrt{4 \pi}} e^{-\frac{1}{4}(x - \mu)^2} \]",
        "description": "Use x consistently as the output variable in the squared normal kernel.",
    },
    {
        "id": "normal-density-half-factor",
        "old": r"\exp\left[-\left(\frac{x - \mu}{\sigma}\right)^2\right]",
        "new": r"\exp\left[-\frac{1}{2}\left(\frac{x - \mu}{\sigma}\right)^2\right]",
        "description": "Restore the one-half factor in the general normal density exponent.",
    },
    {
        "id": "beta-density-second-factor",
        "old": r"x^{a - 1} y^{b - 1}",
        "new": r"x^{a - 1} (1 - x)^{b - 1}",
        "description": "Use the beta density's (1-x) second factor.",
    },
    {
        "id": "negative-binomial-parameter-space",
        "old": r"parameter penghentian \( k \) dan parameter keberhasilan \( \alpha \) mendefinisikan fungsi kernel \( p \) dari \( (0, \infty) \times (0, 1) \) ke \( \N \)",
        "new": r"parameter penghentian \( k \) dan parameter keberhasilan \( \alpha \) mendefinisikan fungsi kernel \( p \) dari \( \N_+ \times (0, 1) \) ke \( \N \)",
        "description": "Use the positive-integer stopping parameter space for the negative binomial family.",
    },
    {
        "id": "negative-binomial-argument-order",
        "old": r"p[(n, \alpha), k] = \binom{n + k - 1}{n} \alpha^k (1 - \alpha)^n",
        "new": r"p[(k, \alpha), n] = \binom{n + k - 1}{n} \alpha^k (1 - \alpha)^n",
        "description": "Put the stopping and success parameters before the observation n.",
    },
)

KERNELS_READER_NOTES = (
    {
        "id": "o009-note-kernels-regular-conditional",
        "after_heading": "Probabilitas Bersyarat",
        "html": r"""<aside class="edition-note" id="o009-note-kernels-regular-conditional">
<strong>Catatan edisi tentang keberadaan.</strong> Kernel probabilitas bersyarat
seperti di bawah ini tidak otomatis ada pada ruang terukur sebarang. Pernyataan
tersebut dibaca dengan asumsi bahwa suatu distribusi bersyarat reguler telah
dipilih; ruang Borel baku memberikan kondisi cukup yang lazim. Versinya hanya
ditentukan hampir di mana-mana terhadap distribusi \(X\), sehingga nilainya pada
himpunan nol dapat dipilih berbeda. Tambahan asli ini berlisensi CC BY 4.0.
</aside>""",
        "description": "Qualify existence and almost-everywhere uniqueness of regular conditional distributions.",
    },
)

DIST_CONVERGENCE_READER_CORRECTIONS = (
    {
        "id": "visible-skorohod-section-reference",
        "old": r'<a class="ref" href="#sko"></a> Skorohod',
        "new": r'<a class="ref" href="#sko">representasi</a> Skorohod',
        "description": "Supply visible Indonesian text for the source's empty reference to the Skorohod-representation section.",
        "change_kind": "source-link-repair",
    },
)

MARTINGALE_INTRO_READER_CORRECTIONS = (
    {
        "id": "expectation-macro-second-moment",
        "old": r"\( E(V_{n+1}^2) - \var(X_{n+1}) = - \var(X_n) \)",
        "new": r"\( \E(V_{n+1}^2) - \var(X_{n+1}) = - \var(X_n) \)",
        "description": "Use the page's expectation macro in the second-moment calculation.",
    },
    {
        "id": "expectation-macro-adapted-difference",
        "old": r"- E(X_k \mid \mathscr{F}_k)",
        "new": r"- \E(X_k \mid \mathscr{F}_k)",
        "description": "Use the expectation macro in the martingale-difference calculation.",
    },
    {
        "id": "expectation-macro-zero-mean",
        "old": r"\( E(V_n) = 0 \)",
        "new": r"\( \E(V_n) = 0 \)",
        "description": "Use the expectation macro in the zero-mean qualification.",
    },
    {
        "id": "expectation-macro-partial-product",
        "old": r"X_n E(V_{n+1} \mid \mathscr{F}_n)",
        "new": r"X_n \E(V_{n+1} \mid \mathscr{F}_n)",
        "description": "Use the expectation macro in the partial-product calculation.",
    },
    {
        "id": "expectation-macro-independent-increments",
        "old": r"\[ E\left(X_t \mid \mathscr{F}_s\right)",
        "new": r"\[ \E\left(X_t \mid \mathscr{F}_s\right)",
        "description": "Use the expectation macro in the independent-increment calculation.",
    },
    {
        "id": "expectation-macro-zero-increment",
        "old": r"\( E(X_t - X_s) = 0 \)",
        "new": r"\( \E(X_t - X_s) = 0 \)",
        "description": "Use the expectation macro for the zero-mean increment.",
    },
    {
        "id": "second-moment-variance-identity",
        "old": r"\[ \var(X_t) = \var[(X_t - X_s) + X_s] = \var(X_s) + \var(X_t - X_s)^2 = \var(X_s) + \E[(X_t - X_s)^2 \]",
        "new": r"\[ \var(X_t) = \var[(X_t - X_s) + X_s] = \var(X_s) + \var(X_t - X_s) = \var(X_s) + \E[(X_t - X_s)^2] \]",
        "description": "Remove the spurious square on the increment variance and close the expected-square bracket.",
    },
    {
        "id": "stationary-increment-variance-rate",
        "old": r"\( b^2 = \E(X_1^2) \lt \infty \)",
        "new": r"\( b^2 = \E[(X_1 - X_0)^2] \lt \infty \)",
        "description": "Define the stationary-increment variance rate from the unit increment rather than the level at time one.",
    },
    {
        "id": "branching-sum-lower-index",
        "old": r"\sum_{i=0}^{X_n} U_i",
        "new": r"\sum_{i=1}^{X_n} U_i",
        "description": "Use the same offspring-sum lower index in the proof as in the branching-process definition.",
    },
    {
        "id": "partial-product-input-sequence",
        "old": r"<dfn>proses hasil kali parsial</dfn> yang terkait dengan \( \bs X \)",
        "new": r"<dfn>proses hasil kali parsial</dfn> yang terkait dengan \( \bs V \)",
        "description": "Associate the partial-product process with its input sequence V rather than with itself.",
    },
    {
        "id": "branching-offspring-mean-symbol",
        "old": r"rata-rata \( \mu \) serta fungsi pembangkit probabilitas",
        "new": r"rata-rata \( m \) serta fungsi pembangkit probabilitas",
        "description": "Use the previously defined offspring-mean symbol m in the branching-process proof.",
    },
    {
        "id": "density-index-domain",
        "old": r"pada \(\mathscr{F}_n\) untuk setiap \( n \in \N_+ \). Fungsi kepadatan suatu ukuran",
        "new": r"pada \(\mathscr{F}_n\) untuk setiap \( n \in \N \). Fungsi kepadatan suatu ukuran",
        "description": "Include n=0 in the density construction, consistently with the process and proof.",
    },
    {
        "id": "stationary-increment-time-order",
        "old": r"<dfn>Inkremen stasioner</dfn> jika \( X_t - X_s \) memiliki distribusi yang sama dengan \( X_{t-s} - X_0 \) untuk semua \( s, \, t \in T \).",
        "new": r"<dfn>Inkremen stasioner</dfn> jika \( X_t - X_s \) memiliki distribusi yang sama dengan \( X_{t-s} - X_0 \) untuk semua \( s, \, t \in T \) dengan \( s \le t \).",
        "description": "Restrict stationary-increment comparisons to ordered times so that t-s is in the time domain.",
    },
    {
        "id": "visible-basic-assumptions-reference-definition",
        "old": r'memenuhi asumsi dasar pada <a class="ref" href="#asm"></a> di atas.</p>',
        "new": r'memenuhi asumsi dasar pada <a class="ref" href="#asm">bagian Asumsi Dasar</a> di atas.</p>',
        "description": "Supply visible Indonesian text for the empty basic-assumptions reference in the definition.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-independent-increments-reference",
        "old": r'inkremen independen pada <a class="ref" href="#inc"></a>.</p>',
        "new": r'inkremen independen pada <a class="ref" href="#inc">bagian Proses dengan Inkremen Independen</a>.</p>',
        "description": "Supply visible Indonesian text for the empty independent-increments section reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-partial-sums-reference-random-walk",
        "old": r'lebih umum pada <a class="ref" href="#sum"></a>. Proses',
        "new": r'lebih umum pada <a class="ref" href="#sum">bagian Jumlah Parsial</a>. Proses',
        "description": "Supply visible Indonesian text for the empty partial-sums reference in the random-walk discussion.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-partial-sums-reference-products",
        "old": r'proses jumlah parsial pada <a class="ref" href="#sum"></a>, tetapi',
        "new": r'proses jumlah parsial pada <a class="ref" href="#sum">bagian Jumlah Parsial</a>, tetapi',
        "description": "Supply visible Indonesian text for the empty partial-sums reference in the partial-product discussion.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-random-walk-reference-simple",
        "old": r'lebih umum pada <a class="ref" href="#wlk"></a>. Dalam konteks',
        "new": r'lebih umum pada <a class="ref" href="#wlk">bagian Gerak Acak Waktu Diskret</a>. Dalam konteks',
        "description": "Supply visible Indonesian text for the empty discrete-time-random-walk section reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-partial-sums-reference-increments",
        "old": r'proses jumlah parsial \( \bs{X} \) pada <a class="ref" href="#sum"></a> yang terkait',
        "new": r'proses jumlah parsial \( \bs{X} \) pada <a class="ref" href="#sum">bagian Jumlah Parsial</a> yang terkait',
        "description": "Supply visible Indonesian text for the empty partial-sums reference in the increments discussion.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-random-walk-reference-increments",
        "old": r'Gerak acak pada <a class="ref" href="#wlk"></a> memiliki',
        "new": r'Gerak acak pada <a class="ref" href="#wlk">bagian Gerak Acak Waktu Diskret</a> memiliki',
        "description": "Supply visible Indonesian text for the empty random-walk reference in the increments discussion.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-basic-assumptions-reference-increments",
        "old": r'memenuhi asumsi dasar pada <a class="ref" href="#asm"></a> di atas relatif',
        "new": r'memenuhi asumsi dasar pada <a class="ref" href="#asm">bagian Asumsi Dasar</a> di atas relatif',
        "description": "Supply visible Indonesian text for the empty basic-assumptions reference in the increments discussion.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-partial-products-reference",
        "old": r'mengikuti <a class="ref" href="#prd"></a> tentang hasil kali parsial',
        "new": r'mengikuti <a class="ref" href="#prd">pembahasan Hasil Kali Parsial</a> tentang hasil kali parsial',
        "description": "Supply visible Indonesian text for the empty partial-products reference in the likelihood-ratio proof.",
        "change_kind": "source-link-repair",
    },
)

MARTINGALE_PROPERTIES_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "filtration-command",
        "old": r"""<ol class="sub">
<li>Jika \( \bs{X} \) merupakan martingal terhadap \( \frak{F} \), maka \( \E(X_s) = \E(X_t) \).</li>
<li>Jika \( \bs{X} \) merupakan submartingal terhadap \( \frak{F} \), maka \( \E(X_s) \le \E(X_t) \).</li>
<li>Jika \( \bs{X} \) merupakan supermartingal terhadap \( \frak{F} \), maka \( \E(X_s) \ge \E(X_t) \).</li>
</ol>""",
        "new": r"""<ol class="sub">
<li>Jika \( \bs{X} \) merupakan martingal terhadap \( \mathfrak{F} \), maka \( \E(X_s) = \E(X_t) \).</li>
<li>Jika \( \bs{X} \) merupakan submartingal terhadap \( \mathfrak{F} \), maka \( \E(X_s) \le \E(X_t) \).</li>
<li>Jika \( \bs{X} \) merupakan supermartingal terhadap \( \mathfrak{F} \), maka \( \E(X_s) \ge \E(X_t) \).</li>
</ol>""",
        "description": "Use the page's defined mathfrak command for the filtration in all three expectation relations.",
    },
    {
        "id": "preliminaries-reference-sampling",
        "old": r'memenuhi asumsi dasar dalam <a class="ref" href="#pre"></a>. Andaikan pula',
        "new": r'memenuhi asumsi dasar dalam <a class="ref" href="#pre">bagian Pendahuluan</a>. Andaikan pula',
        "description": "Supply visible text for the empty reference whose target is a heading rather than a unit.",
    },
    {
        "id": "doob-normalization-and-reference",
        "old": r'memenuhi asumsi dasar dalam <a class="ref" href="#pre"></a> di atas terhadap filtrasi \( \mathfrak F = \{\mathscr{F}_n: n \in \N\} \). Maka \( X_n = Y_n + Z_n \) untuk \( n \in \N \), dengan \( \bs Y = \{Y_n: n \in \N\} \) merupakan martingal terhadap \( \mathfrak F \) dan \( \bs Z = \{Z_n: n \in \N\} \) terprediksi terhadap \( \mathfrak F \). Dekomposisi tersebut unik.',
        "new": r'memenuhi asumsi dasar dalam <a class="ref" href="#pre">bagian Pendahuluan</a> di atas terhadap filtrasi \( \mathfrak F = \{\mathscr{F}_n: n \in \N\} \). Maka \( X_n = Y_n + Z_n \) untuk \( n \in \N \), dengan \( \bs Y = \{Y_n: n \in \N\} \) merupakan martingal terhadap \( \mathfrak F \), sedangkan \( \bs Z = \{Z_n: n \in \N\} \) terprediksi terhadap \( \mathfrak F \) dan memenuhi \( Z_0 = 0 \). Dengan normalisasi ini, dekomposisi tersebut unik.',
        "description": "State the zero-at-origin normalization required for uniqueness and expose the heading reference.",
    },
    {
        "id": "doob-meyer-hypotheses",
        "old": r'<p>Dekomposisi berbentuk demikian lebih rumit dalam waktu kontinu, antara lain karena definisi proses terprediksi lebih halus dan kompleks. Teorema dekomposisi berlaku dalam waktu kontinu dengan asumsi dasar kita dan asumsi tambahan bahwa koleksi peubah acak \( \{X_\tau: \tau \text{ is a finite-valued stopping time}\} \) <a href="../expect/Uniform.html">terintegralkan seragam</a>. Hasil tersebut dikenal sebagai <dfn>teorema dekomposisi Doob–Meyer</dfn>, yang juga dinamai menurut Paul Meyer.</p>',
        "new": r'<p>Dalam waktu kontinu, <dfn>teorema dekomposisi Doob–Meyer</dfn> menyatakan bahwa submartingal càdlàg \( \bs X \) kelas D memiliki dekomposisi unik \( X = M + A \), dengan \( M \) suatu martingal dan \( A \) terprediksi, menaik, serta dinormalisasi oleh \( A_0 = 0 \). Untuk supermartingal, dekomposisinya dapat ditulis \( X = M + A \) dengan \( A \) terprediksi, menurun, dan \( A_0 = 0 \). Hasil ini dinamai menurut Joseph Doob dan Paul Meyer.</p>',
        "description": "State the cadlag sub/supermartingale and class-D hypotheses, predictable monotonicity, and normalization required by Doob-Meyer.",
    },
    {
        "id": "harmonic-every-start-scope",
        "old": r'<p class="math">Misalkan \( h: S \to \R \) dan \( \E[\left|h(X_t)\right|] \lt \infty \) untuk \( t \in T \). Definisikan \( h(\bs X) = \{h(X_t): t \in T\} \).</p>',
        "new": r'<p class="math">Misalkan \( h: S \to \R \) dan \( \E_x[\left|h(X_t)\right|] \lt \infty \) untuk setiap \( x \in S \) dan \( t \in T \). Definisikan \( h(\bs X) = \{h(X_t): t \in T\} \). Semua pernyataan martingal, submartingal, dan supermartingal berikut dipahami berlaku di bawah hukum \( \P_x \) untuk setiap keadaan awal \( x \in S \).</p>',
        "description": "Require the martingale assertions under every initial-state law so the harmonic converse is global on the state space.",
    },
    {
        "id": "harmonic-converse-every-start",
        "old": r'Sebaliknya, jika \( \{h(X_t): t \in T\} \) merupakan martingal, maka \( P_{t-s}h(X_s) = h(X_s) \). Dengan mengambil \( s = 0 \) dan \( X_0 = x \), kita memperoleh \( P_t h(x) = h(x) \), sehingga \( h \) harmonik. Bukti untuk submartingal dan supermartingal serupa, dengan pertidaksamaan menggantikan kesamaan.',
        "new": r'Sebaliknya, andaikan sifat martingal berlaku di bawah \( \P_x \) untuk setiap \( x \in S \). Dengan mengambil \( s = 0 \) di bawah \( \P_x \), kita memperoleh \( P_t h(x) = h(x) \), sehingga \( h \) harmonik. Argumen yang sama, dengan pertidaksamaan menggantikan kesamaan, berlaku untuk submartingal dan supermartingal.',
        "description": "Derive the harmonic converse from the explicitly quantified every-start martingale property.",
    },
    {
        "id": "simple-walk-transform-reference",
        "old": r'<p>Hasil-hasil ini langsung mengikuti transformasi martingal dalam <a class="ref" href="#wlk1"></a>.</p>',
        "new": r'<p>Hasil-hasil ini mengikuti perhitungan yang sama seperti dalam <a class="ref" href="#trn2">hasil transformasi martingal</a>; keterintegralan berlaku karena \( |V_k| = 1 \) dan \( \E(Y_k) \lt \infty \).</p>',
        "description": "Point to the transform result rather than the random-walk proposition and close the unbounded-bet integrability condition.",
    },
    {
        "id": "de-moivre-alignment-equality",
        "old": r'&amp; \frac{(1 - p)^{x + 1}}{p^x}',
        "new": r'&amp; = \frac{(1 - p)^{x + 1}}{p^x}',
        "description": "Restore the missing equality sign in the harmonic-function calculation.",
    },
    {
        "id": "branching-state-function-exception",
        "old": r'Namun, kita tidak dapat menulis \( Y_n = h(X_n) \) untuk fungsi \( h \) yang didefinisikan pada ruang keadaan, sehingga martingal ini tidak dapat ditafsirkan melalui fungsi harmonik.',
        "new": r'Kecuali jika \( m = 1 \), representasi \( Y_n = X_n / m^n \) bergantung pada waktu dan secara umum tidak dapat ditulis sebagai \( Y_n = h(X_n) \) untuk satu fungsi keadaan yang tidak bergantung pada \( n \); representasi ruang–waktunya adalah \( H(n, x) = x / m^n \).',
        "description": "Qualify the state-only representation claim by its m=1 exception and give the correct space-time function.",
    },
    {
        "id": "independent-increments-preliminaries-reference",
        "old": r'Misalkan \( \bs X = \{X_t: t \in T\} \) merupakan proses stokastik yang memenuhi asumsi dasar dalam <a class="ref" href="#pre"></a> di atas',
        "new": r'Misalkan \( \bs X = \{X_t: t \in T\} \) merupakan proses stokastik yang memenuhi asumsi dasar dalam <a class="ref" href="#pre">bagian Pendahuluan</a> di atas',
        "description": "Supply visible text for the independent-increments section's heading reference.",
    },
    {
        "id": "random-walk-heading-reference",
        "old": r'Dalam waktu diskret, proses dengan inkremen stasioner dan independen hanyalah gerak acak seperti dalam <a class="ref" href="#wlk"></a> yang dibahas di atas.',
        "new": r'Dalam waktu diskret, proses dengan inkremen stasioner dan independen hanyalah gerak acak seperti dalam <a class="ref" href="#wlk">bagian Gerak Acak</a> yang dibahas di atas.',
        "description": "Supply visible text for the random-walk heading reference.",
    },
    {
        "id": "identity-function-introduction",
        "old": r'<p class="math">Fungsi identitas \( I \) bersifat .</p>',
        "new": r'<p class="math">Fungsi identitas \( I \) memiliki sifat berikut:</p>',
        "description": "Complete the truncated sentence introducing the harmonicity classification.",
    },
)

MARTINGALE_STOP_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "optional-stopping-missing-variables",
        "old": r'<p class="math">Misalkan bahwa  merupakan waktu henti terbatas terhadap \( \mathfrak F \) dengan \( \rho \le \tau \). </p>',
        "new": r'<p class="math">Misalkan \( \rho \) dan \( \tau \) merupakan waktu henti terbatas terhadap \( \mathfrak F \) dengan \( \rho \le \tau \). </p>',
        "description": "Restore the two stopping-time variables omitted from the optional-stopping theorem premise.",
    },
    {
        "id": "continuous-proof-time-word",
        "old": r"\text{ as } n \to \infty",
        "new": r"\text{ saat } n \to \infty",
        "description": "Translate the remaining prose word inside the continuous-time limit display.",
    },
    {
        "id": "stopping-time-sigma-algebra-quantifier",
        "old": r"\text{ for all } t \in T",
        "new": r"\text{ untuk setiap } t \in T",
        "description": "Translate the prose quantifier inside the stopping-time sigma-algebra display.",
    },
    {
        "id": "restricted-expectation-separator",
        "old": r"\E\left(X_{\rho_n}: A\right)",
        "new": r"\E\left(X_{\rho_n}; A\right)",
        "description": "Use the page's semicolon notation consistently for expectation restricted to an event.",
    },
    {
        "id": "unbounded-counterexample-reference",
        "old": r'ketika asumsi ini tidak berlaku diberikan dalam <a class="ref" href="#srw2"></a>. Berikut dua akibat sederhana:',
        "new": r'ketika asumsi ini tidak berlaku diberikan dalam <a class="ref" href="#srw3"></a>. Berikut dua akibat sederhana:',
        "description": "Point to the example that actually violates the bounded-stopping-time identity.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "stopped-process-time-domain",
        "old": r"""<p class="math">Misalkan \( \bs X \) memenuhi asumsi di atas dan \( \tau \) merupakan waktu henti terhadap filtrasi \( \mathfrak F \). <dfn>Proses yang dihentikan</dfn> \( X^\tau = \{X^\tau_t: t \in [0, \infty)\} \) didefinisikan oleh
	\[ X^\tau_t = X_{t \wedge \tau}, \quad t \in [0, \infty) \]</p>""",
        "new": r"""<p class="math">Misalkan \( \bs X \) memenuhi asumsi di atas dan \( \tau \) merupakan waktu henti terhadap filtrasi \( \mathfrak F \). <dfn>Proses yang dihentikan</dfn> \( \bs X^\tau = \{X^\tau_t: t \in T\} \) didefinisikan oleh
	\[ X^\tau_t = X_{t \wedge \tau}, \quad t \in T \]</p>""",
        "description": "Define the stopped process on the page's actual discrete-or-continuous time set T.",
    },
    {
        "id": "remove-empty-summary",
        "old": "<summary></summary>\n",
        "new": "",
        "description": "Remove the stray second empty summary from the stopped-martingale proof panel.",
    },
    {
        "id": "stopped-process-notation",
        "old": r"\bs Y \cdot \bs X = \bs{X}_\tau",
        "new": r"\bs Y \cdot \bs X = \bs{X}^\tau",
        "description": "Use superscript stopping notation for the stopped process rather than a subscripted process.",
    },
    {
        "id": "stopped-process-expectation-macros",
        "old": r"""<ol class="sub">
<li>Jika \( \bs X \) merupakan martingal terhadap \( \mathfrak F \), maka \( \E(X_{t \wedge \tau}) = E(X_0) \)</li>
<li>Jika \( \bs X \) merupakan submartingal terhadap \( \mathfrak F \), maka \( \E(X_{t \wedge \tau}) \ge E(X_0) \)</li>
<li>Jika \( \bs X \) merupakan supermartingal terhadap \( \mathfrak F \), maka \( \E(X_{t \wedge \tau}) \le E(X_0) \)</li>
</ol>""",
        "new": r"""<ol class="sub">
<li>Jika \( \bs X \) merupakan martingal terhadap \( \mathfrak F \), maka \( \E(X_{t \wedge \tau}) = \E(X_0) \)</li>
<li>Jika \( \bs X \) merupakan submartingal terhadap \( \mathfrak F \), maka \( \E(X_{t \wedge \tau}) \ge \E(X_0) \)</li>
<li>Jika \( \bs X \) merupakan supermartingal terhadap \( \mathfrak F \), maka \( \E(X_{t \wedge \tau}) \le \E(X_0) \)</li>
</ol>""",
        "description": "Use the page's defined expectation macro in all three stopped-process expectation relations.",
    },
    {
        "id": "exit-time-optional-stopping-reference",
        "old": r'<li>Teorema pencuplikan opsional <a class="ref" href="#ost1"></a> berlaku, sehingga \( \E(X_\tau) = \E(X_0) = 0 \).</li>',
        "new": r'<li>Teorema penghentian opsional waktu diskret <a class="ref" href="#dis2"></a> berlaku, sehingga \( \E(X_\tau) = \E(X_0) = 0 \).</li>',
        "description": "Cite the unbounded-time discrete theorem whose finite-mean and bounded-increment hypotheses were established.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "optional-stopping-canonical-term",
        "old": r"versi pertama teorema pencuplikan opsional dapat gagal",
        "new": r"versi pertama teorema penghentian opsional dapat gagal",
        "description": "Use the edition's canonical Indonesian term for optional stopping consistently.",
    },
    {
        "id": "wald-integrability-hypothesis",
        "old": r"merupakan barisan peubah independen dan berdistribusi identik dengan rata-rata bersama \( \mu \in \R \).",
        "new": r"merupakan barisan peubah independen dan berdistribusi identik dengan \( \E(|X_1|) \lt \infty \) dan \( \E(X_1) = \mu \in \R \).",
        "description": "State the integrability hypothesis used by Wald's equation explicitly.",
    },
    {
        "id": "wald-valid-martingale-proof",
        "old": r"""<p>Misalkan \( \mathfrak F \) menyatakan filtrasi alami yang terkait dengan \( \bs X \). Tetapkan \( c = \E(|X_n|)\), sehingga berdasarkan asumsi, \( c \lt \infty \). Terakhir, tetapkan 
		\[ Y_n = \sum_{k=1}^n (X_k - \mu) \, \quad n \in \N_+ \]
		Maka \( \bs Y = (Y_n: n \in \N_+) \) merupakan martingal terhadap \( \mathfrak F \), dengan rata-rata 0. Perhatikan bahwa
		\[ \E(|Y_{n+1} - Y_n|) = \E(|X_{n+1} - \mu|) \le c + |\mu|, \quad n \in \N_+ \]
		Oleh karena itu, versi diskret teorema penghentian opsional dalam <a class="ref" href="#dis2"></a> berlaku, dan kita memperoleh \( \E(Y_N) = 0 \). Dengan demikian,
		\[ 0 = \E(Y_N) = \E\left[\sum_{k=1}^N (X_k - \mu)\right] = \E\left(\sum_{k=1}^N X_k - N \mu\right) = \E\left(\sum_{k=1}^N X_k\right) - \E(N) \mu \]</p>""",
        "new": r"""<p>Misalkan \( \mathfrak F \) merupakan filtrasi alami \( \bs X \), lalu tetapkan \( Y_0=0 \) dan
		\[ Y_n = \sum_{k=1}^n (X_k - \mu), \quad n \in \N_+. \]
		Maka \( \bs Y=\{Y_n:n\in\N\} \) merupakan martingal. Untuk setiap \(n\), waktu henti \(N\wedge n\) terbatas, sehingga <a class="ref" href="#ost3"></a> memberikan \(\E(Y_{N\wedge n})=0\). Untuk \(k\ge1\), kejadian \(\{N\ge k\}=\{N\gt k-1\}\) berada dalam \(\mathscr F_{k-1}\) dan karena itu independen dari \(X_k\). Maka
		\[ \begin{aligned}
\E\left(|Y_N-Y_{N\wedge n}|\right)
&amp;\le \sum_{k=n+1}^{\infty}\E\left[|X_k-\mu|\bs{1}(N\ge k)\right] \\
&amp;= \E(|X_1-\mu|)\sum_{k=n+1}^{\infty}\P(N\ge k) \\
&amp;\longrightarrow 0.
\end{aligned} \]
		karena \(\E(N)=\sum_{k=1}^{\infty}\P(N\ge k)\lt\infty\). Jadi \(Y_{N\wedge n}\to Y_N\) dalam \(L^1\) dan \(\E(Y_N)=0\). Dengan demikian,
		\[ \begin{aligned}
0 &amp;= \E(Y_N) \\
  &amp;= \E\left[\sum_{k=1}^N (X_k - \mu)\right] \\
  &amp;= \E\left(\sum_{k=1}^N X_k\right) - \mu\E(N).
\end{aligned} \]</p>""",
        "description": "Replace an invalid bounded-increment invocation with bounded stopping followed by an explicit L1 convergence argument.",
    },
    {
        "id": "pattern-terminal-wealth-statement",
        "old": r'<p class="math">Untuk kata berhingga \( \bs a \) dari alfabet \( S \), \( \nu(\bs a) \) merupakan total kemenangan semua pemain pada waktu \( N_{\bs a} \).</p>',
        "new": r'<p class="math">Untuk kata berhingga \( \bs a \), misalkan \( W_{N_{\bs a}} \) menyatakan total kekayaan semua penjudi ketika permainan dihentikan pada \( N_{\bs a} \). Maka \( W_{N_{\bs a}} \) deterministik dan \( \nu(\bs a)=W_{N_{\bs a}} \).</p>',
        "description": "State the deterministic terminal-wealth identity proved by the fair-game accounting argument.",
    },
    {
        "id": "pattern-valid-net-gain-proof",
        "old": r"""<p>Misalkan \( X_n \) menyatakan total kekayaan semua penjudi setelah percobaan \( n \in \N_+ \). Karena semua taruhan adil, \( \bs X = \{X_n: n \in \N_+\} \) merupakan martingal dengan rata-rata 0. Kita akan menunjukkan bahwa syarat dalam versi diskret teorema pencuplikan opsional <a class="ref" href="#dis2"></a> berlaku. Pertama, tinjau blok-blok percobaan saling lepas sepanjang \( k \), yakni
		\[ \left((L_1, L_2, \ldots, L_k), (L_{k+1}, L_{k+2}, \ldots, L_{2 k}), \ldots\right) \]
		Misalkan \( M_{\bs a} \) menyatakan indeks blok pertama semacam itu yang membentuk kata \( \bs a \). Peubah ini memiliki <a href="https://www.randomservices.org/random/bernoulli/Geometric.html">distribusi geometrik</a> pada \( \N_+ \) dengan parameter keberhasilan \( f(\bs a) \), sehingga khususnya \( \E(M_\bs{a}) = 1 / f(\bs a) \). Jelas bahwa \( N_{\bs a} \le k M_{\bs a} \), sehingga \( \nu(\bs a) \lt k / f(\bs a) \lt \infty \). Selanjutnya, perhatikan bahwa semua penjudi telah berhenti bermain pada waktu \( N \), sehingga jelas \( |X_{n+1} - X_n| \le 1 / f(a) \) untuk \( n \in \N_+ \). Jadi, teorema penghentian opsional berlaku, dan karenanya \( \E\left(X_{N_a}\right) = 0 \). Namun, \( \nu(\bs a) \) juga dapat ditafsirkan sebagai jumlah uang yang diharapkan telah ditanamkan oleh para penjudi (1 unit pada setiap waktu hingga permainan berakhir pada waktu \( N_{\bs a} \)); karena itu, nilai tersebut juga harus sama dengan total kemenangan pada waktu \( N_{\bs a} \) (yang deterministik).</p>""",
        "new": r"""<p>Tuliskan \( N=N_{\bs a} \). Misalkan \( W_n \) menyatakan total kekayaan semua penjudi setelah percobaan \( n \), dengan \( W_0=0 \), dan definisikan \( X_n=W_n-n \). Pengurangan \(n\) mencatat satu unit modal baru yang ditanamkan pada setiap percobaan. Karena setiap taruhan adil, \( \bs X=\{X_n:n\in\N\} \) merupakan martingal dengan rata-rata 0.

Misalkan \( M_{\bs a} \) merupakan indeks blok saling lepas pertama sepanjang \( k \) yang membentuk \( \bs a \). Maka
\[ \E(N)\le k\E(M_{\bs a})=\frac{k}{f(\bs a)}\lt\infty. \]
Pada setiap saat paling banyak \( k \) penjudi masih aktif dan kekayaan setiap penjudi aktif paling besar \(1/f(\bs a)\). Karena itu, misalnya,
\[ |X_{n+1}-X_n|\le 1+\frac{2k}{f(\bs a)}, \]
sehingga <a class="ref" href="#dis2"></a> berlaku dan \( \E(X_N)=0 \). Karena \(X_N=W_N-N\), diperoleh \( \E(W_N)=\E(N)=\nu(\bs a)\). Pada waktu \(N\), penjudi yang masih memiliki kekayaan tepat bersesuaian dengan prefiks \( \bs a \) yang juga merupakan sufiksnya; akibatnya \(W_N\) deterministik. Jadi \(W_N=\nu(\bs a)\).</p>""",
        "description": "Use net gain rather than injected total wealth as the martingale and justify integrability and bounded increments correctly.",
    },
    {
        "id": "pattern-example-gambler-index",
        "old": r"Penjudi \( N - 2 \) memasang dua taruhan, memenangkan yang pertama tetapi kalah pada yang kedua.",
        "new": r"Penjudi \( N - 1 \) memasang dua taruhan, memenangkan yang pertama tetapi kalah pada yang kedua.",
        "description": "Correct the repeated gambler index in the 001 pattern accounting example.",
    },
    {
        "id": "secretary-sequence-count",
        "old": r"Aproksimasi 10 suku pertamanya adalah",
        "new": r"Aproksimasi suku \(a_0\) sampai \(a_{10}\) adalah",
        "description": "Describe the eleven displayed sequence terms without calling them ten terms.",
    },
    {
        "id": "secretary-filtration-and-initialization",
        "old": r'<p>Misalkan \( \mathfrak F = \{\mathscr{F}_k: k \in \N_n^+\} \) merupakan filtrasi alami \( \bs X \), dan misalkan \( \rho \) merupakan waktu henti bagi \( \mathfrak F \). Definisikan \( \bs Y = \{Y_k: k \in \N_n\} \) dengan \( Y_0 = 0 \) dan \( Y_k = X_{\rho \wedge k} \vee a_{n-k} \) untuk \( k \in \N_n^+ \). Kita akan menunjukkan bahwa \( \bs Y \) merupakan supermartingal terhadap \( \mathfrak F \). Pertama, pada kejadian \( \rho \le k - 1 \),',
        "new": r'<p>Misalkan \( \mathfrak F=\{\mathscr F_k:k\in\N_n\} \) merupakan filtrasi alami \( \bs X \), dengan \( \mathscr F_0=\{\emptyset,\Omega\} \) dan \( \mathscr F_k=\sigma(X_1,\ldots,X_k) \). Misalkan \( \rho \) merupakan waktu henti bernilai dalam \( \N_n^+ \). Definisikan \( \bs Y=\{Y_k:k\in\N_n\} \) dengan \( Y_0=a_n \) dan \( Y_k=X_{\rho\wedge k}\vee a_{n-k} \) untuk \( k\in\N_n^+ \). Kita akan menunjukkan bahwa \( \bs Y \) merupakan supermartingal terhadap \( \mathfrak F \). Pertama, pada kejadian \( \rho \le k - 1 \),',
        "description": "Include the time-zero sigma-algebra and initialize the comparison process at a_n so the supermartingale proof also works at k=1.",
    },
    {
        "id": "secretary-expectation-macro",
        "old": r"\E(Y_\rho) \le E(Y_0) = a_n",
        "new": r"\E(Y_\rho) \le \E(Y_0) = a_n",
        "description": "Use the page's defined expectation macro in the secretary upper-bound calculation.",
    },
)

MARTINGALE_INEQUALITIES_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "discrete-maximal-index-first",
        "old": r"= x \P(U_t \ge x) + \E(X_n; \tau_x \gt n)",
        "new": r"= x \P(U_n \ge x) + \E(X_n; \tau_x \gt n)",
        "description": "Use the fixed discrete index n in the first-passage identity.",
    },
    {
        "id": "discrete-maximal-index-second",
        "old": r"= \E(X_n; U_t \ge x) + \E(X_n; \tau_x \gt n)",
        "new": r"= \E(X_n; U_n \ge x) + \E(X_n; \tau_x \gt n)",
        "description": "Use the fixed discrete index n in the expectation decomposition.",
    },
    {
        "id": "discrete-maximal-index-conclusion",
        "old": r"\[ x \P(U_t \ge x) + \E(X_n; \tau_x \gt n) \le  \E(X_n; U_t \ge x) + \E(X_n; \tau_x \gt n)\]",
        "new": r"\[ x \P(U_n \ge x) + \E(X_n; \tau_x \gt n) \le  \E(X_n; U_n \ge x) + \E(X_n; \tau_x \gt n)\]",
        "description": "Use U_n throughout the discrete maximal-inequality conclusion.",
    },
    {
        "id": "continuous-maximal-threshold-proof",
        "old": r"""Himpunan \( \D^+ \) dari <em>semua</em> bilangan rasional diadik nonnegatif rapat dalam \( [0, \infty) \), dan karena \( \bs X \) kontinu kanan serta memiliki limit kiri, jika \( U_t \ge x \), maka \( U^k_t \ge x \) untuk suatu \( k \in \N \). Dengan kata lain,
		\[ \{U_t \ge x\} = \bigcup_{k=0}^\infty \left\{U^k_t \ge x\right\} \]
		Pertidaksamaan maksimal berlaku untuk submartingal waktu diskret \( \bs{X}^k \), sehingga
		\[ P(U^k_t \ge x) \le \frac{1}{x} \E(X_t; U^k_t \ge x) \]
		untuk setiap \( k \in \N \). Berdasarkan <a href="https://www.randomservices.org/random/expect/Integral.html">teorema konvergensi monoton</a>, ruas kiri konvergen ke \( \P(U_t \ge x) \) ketika \( k \to \infty \), dan ruas kanan konvergen ke \( \E(X; U_t \ge x) \) ketika \( k \to \infty \).""",
        "new": r"""Kerapatan \( \D^+ \), kekontinuan kanan, dan penyertaan \(t\) memberikan \(U_t^k \uparrow U_t\), tetapi kejadian ambang tertutupnya tidak harus sama pada suatu kisi berhingga. Ambil \(y \in (0,x)\), dan tetapkan
		\[ A_y = \bigcup_{k=0}^{\infty}\{U_t^k \ge y\}. \]
		Untuk setiap \(k\in\N\), pertidaksamaan waktu diskret memberikan
		\[ \P(U_t^k \ge y) \le \frac{1}{y}\E(X_t;U_t^k\ge y). \]
		Kejadian-kejadian tersebut menaik menuju \(A_y\). Karena \(X_t\) terintegralkan, kekontinuan probabilitas dari bawah dan teorema konvergensi terdominasi memberikan
		\[ \P(A_y) \le \frac{1}{y}\E(X_t;A_y). \]
		Jika \(y_m\uparrow x\), maka \(A_{y_m}\downarrow\{U_t\ge x\}\). Kekontinuan probabilitas dari atas dan konvergensi terdominasi kemudian memberikan
		\[ \P(U_t\ge x) \le \frac{1}{x}\E(X_t;U_t\ge x). \]""",
        "description": "Replace the false closed-threshold grid identity and signed monotone-convergence step with a relaxed threshold and dominated convergence.",
    },
    {
        "id": "lp-maximal-missing-factor",
        "old": r"\frac{1}{x} \E(|X_t|; W_t \ge x) = \E(|X_t|; W_t \wedge c \ge x)",
        "new": r"\frac{1}{x} \E(|X_t|; W_t \ge x) = \frac{1}{x}\E(|X_t|; W_t \wedge c \ge x)",
        "description": "Retain the factor 1/x when replacing the event by its truncated equivalent.",
    },
    {
        "id": "nonnegative-supermartingale-maximal-proof",
        "old": r"""<p>Tetapkan \( Y_t = -X_t \) untuk \( t \in T \). Karena \( \bs X \) merupakan supermartingal, \( \bs Y \) merupakan submartingal. Dan karena \( \bs X \) nonnegatif, \( Y_t^+ = X_t \) untuk \( t \in T \). Tetapkan \( U_t = \sup\{X_s: s \in T_t\} = \sup\{Y_s^+: s \in T_t\} \) untuk \( t \in T \). Berdasarkan pertidaksamaan maksimal untuk submartingal, dan karena \( \bs X \) merupakan supermartingal, untuk \( t \in T \) kita memperoleh
		\[ \P(U_t \ge x) \le \frac{1}{x} \E(Y_t^+) = \frac{1}{x} \E(X_t) \le \frac{1}{x} \E(X_0), \quad x \in (0, \infty) \]
		Selanjutnya,""",
        "new": r"""<p>Untuk \(t\in T\), tetapkan \(U_t=\sup\{X_s:s\in T_t\}\), lalu ambil \(x\in(0,\infty)\). Dalam waktu diskret, tetapkan \(\tau_x=\inf\{s\in T_t:X_s\ge x\}\), dengan \(\inf(\emptyset)=\infty\). Kenonnegatifan dan teorema penghentian opsional memberikan
		\[ x\P(U_t\ge x) \le \E(X_{\tau_x\wedge t}) \le \E(X_0). \]
		Dalam waktu kontinu, gunakan kisi diadik berhingga \(T_t^k\) di atas. Untuk \(0\lt y\lt x\),
		\[ \{U_t\ge x\}\subseteq\bigcup_{k=0}^{\infty}\left\{\sup_{s\in T_t^k}X_s\ge y\right\}. \]
		Argumen waktu diskret pada setiap kisi membatasi probabilitas di ruas kanan dengan \(\E(X_0)/y\). Kekontinuan probabilitas dari bawah, diikuti limit \(y\uparrow x\), menghasilkan
		\[ \P(U_t\ge x)\le\frac{1}{x}\E(X_0). \]
		Selanjutnya,""",
        "description": "Replace the sign-reversed Y=-X argument with valid stopped-process and dyadic-grid proofs.",
    },
    {
        "id": "total-upcrossing-prose-notation",
        "old": r"\( u(a, b, \bs x) \) menyatakan berapa kali seluruh barisan",
        "new": r"\( u_\infty(a, b, \bs x) \) menyatakan berapa kali seluruh barisan",
        "description": "Use the defined u_infinity notation for the total number of upcrossings.",
    },
    {
        "id": "total-upcrossing-limit-notation",
        "old": r"\( u_n(a, b, \bs x) \to u(a, b, \bs x) \)",
        "new": r"\( u_n(a, b, \bs x) \to u_\infty(a, b, \bs x) \)",
        "description": "Use the defined total-upcrossing notation in the convergence statement.",
    },
    {
        "id": "total-upcrossing-monotonicity-notation",
        "old": r"\( u(c, d, \bs x) \ge u(a, b, \bs x) \)",
        "new": r"\( u_\infty(c, d, \bs x) \ge u_\infty(a, b, \bs x) \)",
        "description": "Use the defined total-upcrossing notation in the interval comparison.",
    },
    {
        "id": "finite-upcrossing-index-set",
        "old": r"\{k \in \N: t_k(\bs x) \le \infty\}",
        "new": r"\{k \in \N: t_k(\bs x) \lt \infty\}",
        "description": "Exclude failed crossings whose terminal time is infinity.",
    },
    {
        "id": "discrete-supermartingale-upcrossing-reflow",
        "old": r"""\[ \E(U_n) \le \frac{1}{b - a} \E[(X_n - a)^-] \le \frac{1}{b - a}\left[\E(X_n^-) + |a|\right] \le \frac{1}{b - a} \left[\E(|X_n|) + |a|\right], \quad n \in \N \]""",
        "new": r"""\[ \begin{aligned}
\E(U_n)&amp;\le \frac{1}{b-a}\E[(X_n-a)^-]\\
&amp;\le \frac{\E(X_n^-)+|a|}{b-a}\\
&amp;\le \frac{\E(|X_n|)+|a|}{b-a},\qquad n\in\N.
\end{aligned} \]""",
        "description": "Reflow the discrete supermartingale bound into readable mobile lines without changing its mathematics.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "discrete-submartingale-upcrossing-reflow",
        "old": r"""\[ \E(U_n) \le \frac{1}{b - a} \E[(X_n - a)^+] \le \frac{1}{b - a}\left[\E(X_n^+) + |a|\right] \le \frac{1}{b - a}\left[\E(|X_n|) + |a|\right], \quad n \in \N \]""",
        "new": r"""\[ \begin{aligned}
\E(U_n)&amp;\le \frac{1}{b-a}\E[(X_n-a)^+]\\
&amp;\le \frac{\E(X_n^+)+|a|}{b-a}\\
&amp;\le \frac{\E(|X_n|)+|a|}{b-a},\qquad n\in\N.
\end{aligned} \]""",
        "description": "Reflow the discrete submartingale bound into readable mobile lines without changing its mathematics.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "continuous-supermartingale-upcrossing-reflow",
        "old": r"""\[ \E(U_t) \le \frac{1}{b - a} \E[(X_t - a)^-] \le \frac{1}{b - a}\left[\E(X_t^-) + |a|\right] \le \frac{1}{b - a}\left[\E(|X_t|) + |a|\right], \quad t \in [0, \infty) \]""",
        "new": r"""\[ \begin{aligned}
\E(U_t)&amp;\le \frac{1}{b-a}\E[(X_t-a)^-]\\
&amp;\le \frac{\E(X_t^-)+|a|}{b-a}\\
&amp;\le \frac{\E(|X_t|)+|a|}{b-a},\qquad t\in[0,\infty).
\end{aligned} \]""",
        "description": "Reflow the continuous supermartingale bound into readable mobile lines without changing its mathematics.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "continuous-submartingale-upcrossing-reflow",
        "old": r"""\[ \E(U_t) \le \frac{1}{b - a} \E[(X_t - a)^+] \le \frac{1}{b - a} \left[\E(X_t^+) + |a|\right] \le \frac{1}{b - a} \left[\E(|X_t|) + |a|\right], \quad t \in [0, \infty) \]""",
        "new": r"""\[ \begin{aligned}
\E(U_t)&amp;\le \frac{1}{b-a}\E[(X_t-a)^+]\\
&amp;\le \frac{\E(X_t^+)+|a|}{b-a}\\
&amp;\le \frac{\E(|X_t|)+|a|}{b-a},\qquad t\in[0,\infty).
\end{aligned} \]""",
        "description": "Reflow the continuous submartingale bound into readable mobile lines without changing its mathematics.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "submartingale-upcrossing-proof",
        "old": r"""Rantai pertidaksamaan selebihnya mengikuti karena \( (x - a)^- \le x^- + |a| \le |x| + |a| \) untuk \( x \in \R \).</li>
</ol>
<p>Proses""",
        "new": r"""Rantai pertidaksamaan selebihnya mengikuti karena \( (x - a)^- \le x^- + |a| \le |x| + |a| \) untuk \( x \in \R \).</li>
<li>Jika \(\bs X\) merupakan submartingal, tetapkan \(V_j=a+(X_j-a)^+\). Karena fungsi \(x\mapsto a+(x-a)^+\) menaik dan cembung, \(\bs V\) juga merupakan submartingal. Definisikan proses terprediksi
\[ H_j=\bs{1}\{\sigma_k\lt j\le\tau_k\text{ untuk suatu }k\in\N_+\},\qquad J_j=1-H_j,\quad j\in\N_+, \]
dan keuntungan masing-masing strategi
\[ G_n^H=\sum_{j=1}^nH_j(V_j-V_{j-1}),\qquad G_n^J=\sum_{j=1}^nJ_j(V_j-V_{j-1}). \]
Setiap lintas-naik lengkap menyumbang sekurang-kurangnya \(b-a\) pada \(G_n^H\), sedangkan sumbangan lintas-naik yang belum lengkap tidak negatif. Jadi \(G_n^H\ge(b-a)U_n\). Karena \(\bs J\) nonnegatif dan terprediksi, transformasi \(V_0+G_n^J\) merupakan submartingal, sehingga \(\E(G_n^J)\ge0\). Selain itu, \(V_n-V_0=G_n^H+G_n^J\). Oleh karena itu,
\[ \begin{aligned}
(b-a)\E(U_n)&amp;\le\E(G_n^H)\\
&amp;=\E(V_n-V_0)-\E(G_n^J)\\
&amp;\le\E[(X_n-a)^+]-\E[(X_0-a)^+]\\
&amp;\le\E[(X_n-a)^+].
\end{aligned} \]
Ini membuktikan pernyataan kedua.</li>
</ol>
<p>Proses""",
        "description": "Supply the omitted submartingale half using the truncated process and complementary predictable transforms.",
    },
    {
        "id": "upcrossing-transform-convention",
        "old": r"""<p>Proses \( \bs Z = \{Z_n: n \in \N\} \) dalam bukti dapat dipandang sebagai <a href="Properties.html#trn">transformasi</a> \( \bs X = \{X_n: n \in \N\} \) oleh suatu proses terprediksi. Secara khusus, untuk \( n \in \N_+ \), tetapkan \( I_n = 1 \) jika \( \sigma_k \lt n \le \tau_k \) untuk suatu \( k \in \N \), dan tetapkan \( I_n = 0 \) jika tidak. Karena \( \sigma_k \) dan \( \tau_k \) merupakan waktu henti, perhatikan bahwa \( \{I_n = 1\} \in \mathscr{F}_{n-1} \) untuk \( n \in \N_+ \). Dengan demikian, proses \( \bs I = \{I_n: n \in \N_+\} \) terprediksi terhadap \( \mathfrak F \). Selain itu, transformasi \( \bs X \) oleh \( \bs I \) adalah
		\[ (\bs I \cdot \bs X)_n = \sum_{j=1}^n I_j (X_j - X_{j-1}) = \sum_{k=1}^n \left(X_{\tau_k \wedge n} - X_{\sigma_k \wedge n}\right) = Z_n, \quad n \in \N \]
		Karena \( \bs I \) merupakan proses nonnegatif, jika \( \bs X \) merupakan martingal (submartingal, supermartingal), maka \( \bs I \cdot \bs X \) juga merupakan martingal (submartingal, supermartingal).</p>""",
        "new": r"""<p>Proses keuntungan \( \bs Z = \{Z_n: n \in \N\} \) dalam bukti dapat dipandang sebagai keuntungan dari <a href="Properties.html#trn">transformasi</a> \( \bs X = \{X_n: n \in \N\} \) oleh suatu proses terprediksi. Secara khusus, untuk \( n \in \N_+ \), tetapkan \( I_n = 1 \) jika \( \sigma_k \lt n \le \tau_k \) untuk suatu \( k \in \N_+ \), dan tetapkan \( I_n = 0 \) jika tidak. Karena \( \sigma_k \) dan \( \tau_k \) merupakan waktu henti, \( \{I_n = 1\} \in \mathscr{F}_{n-1} \), sehingga \( \bs I = \{I_n: n \in \N_+\} \) terprediksi terhadap \( \mathfrak F \). Dengan konvensi transformasi edisi ini,
		\[ (\bs I \cdot \bs X)_n-X_0 = \sum_{j=1}^n I_j (X_j - X_{j-1}) = \sum_{k=1}^n \left(X_{\tau_k \wedge n} - X_{\sigma_k \wedge n}\right) = Z_n, \quad n \in \N. \]
		Karena \( \bs I \) nonnegatif, jika \( \bs X \) merupakan martingal (submartingal, supermartingal), maka \( \bs I \cdot \bs X \) juga merupakan martingal (submartingal, supermartingal); secara ekuivalen, keuntungan \(\bs Z\) bermula dari 0 dan memiliki arah nilai harapan yang sama.</p>""",
        "description": "Respect the edition's transform convention, which includes X_0, and exclude the undefined crossing index zero.",
    },
    {
        "id": "translate-iff-in-math",
        "old": r"\text{ if and only if }",
        "new": r"\text{ jika dan hanya jika }",
        "description": "Translate the remaining prose connector inside the discrete duality display.",
    },
    {
        "id": "translate-finite-subset-definition",
        "old": r"\sup\{u_J(a, b, \bs x): J \text{ is finite and } J \subset I\}",
        "new": r"\sup\{u_J(a, b, \bs x): J \text{ berhingga dan } J \subset I\}",
        "description": "Translate the finite-subset condition inside the continuous upcrossing definition.",
    },
    {
        "id": "translate-finite-subset-comparison",
        "old": r"""\{u_K(a, b, \bs x): K \text{ is finite and } K \subseteq I\} \subseteq \{u_K(a, b, \bs x): K \text{ is finite and } K \subseteq J\}""",
        "new": r"""\{u_K(a, b, \bs x): K \text{ berhingga dan } K \subseteq I\} \subseteq \{u_K(a, b, \bs x): K \text{ berhingga dan } K \subseteq J\}""",
        "description": "Translate both finite-subset conditions in the monotonicity proof.",
    },
    {
        "id": "continuous-upcrossing-alternation",
        "old": r"""<li>Terdapat \( a, \, b \in \Q \) dengan \( a \lt b \), serta terdapat \( s_n, \, t_n \in [0, \infty) \) dengan \( x_{s_n} \le a \) untuk \( n \in \N \) dan \( x_{t_n} \ge b \) untuk \( n \in \N \).</li>""",
        "new": r"""<li>Terdapat \(a,\,b\in\Q\) dengan \(a\lt b\), serta barisan \((s_n:n\in\N)\) dan \((t_n:n\in\N)\) dalam \([0,\infty)\) sedemikian sehingga
\[ s_n\lt t_n\lt s_{n+1},\qquad x_{s_n}\le a,\qquad x_{t_n}\ge b,\quad n\in\N. \]</li>""",
        "description": "Require alternating times tending to infinity rather than permitting two fixed repeated times.",
    },
    {
        "id": "continuous-upcrossing-measurability-proof",
        "old": r"""<p>Misalkan \( \bs X \) merupakan submartingal; bukti untuk supermartingal serupa. Tetapkan \( t \in [0, \infty) \) dan \( a, \, b \in \R \) dengan \( a \lt b \). Untuk \( I \subseteq [0, \infty) \), tetapkan \( U_I = u_I(a, b, \bs X) \), yaitu jumlah lintas-naik \( [a, b] \) oleh restriksi \( \bs X \) pada \( I \). Andaikan bahwa \( I \) berhingga dan bahwa \( t \in I \) merupakan maksimum dari \( I \). Karena restriksi \( \bs X \) pada \( I \) juga merupakan submartingal, teorema lintas-naik waktu diskret berlaku, sehingga
		\[ \E(U_I) \le \frac{1}{b - a} \E[(X_t - a)^+] \]
		Karena \( U_t = \sup\{U_I: I \text{ is finite and } I \subset [0, t]\} \), terdapat himpunan berhingga \( I_n \) untuk \( n \in \N \) dengan \( U_{I_n} \uparrow U_t \) ketika \( n \to \infty \). Secara khusus, \( U_t \) terukur. Berdasarkan sifat (a) dalam <a class="ref" href="#upc6"></a>, terdapat barisan semacam itu dengan \( I_n \) menaik dalam \( n \) dan \( t \in I_n \) untuk setiap \( n \in \N \). Berdasarkan teorema konvergensi monoton, \( \E\left(U_{I_n}\right) \to \E(U_t) \) ketika \( n \to \infty \). Jadi, berdasarkan persamaan yang ditampilkan di atas,
		\[ \E(U_t) \le \frac{1}{b - a} \E[(X_t - a)^+] \]</p>""",
        "new": r"""<p>Definisikan secara rekursif waktu masuk \(\sigma_k\) ke \(( -\infty,a]\) dan \(\tau_k\) ke \([b,\infty)\), seperti dalam kasus diskret. Untuk proses teradaptasi càdlàg di bawah asumsi biasa, waktu-waktu tersebut merupakan waktu henti. Karena itu,
\[ U_t=\sup\{k\in\N:\tau_k\le t\} \]
terukur. Ambil \(0\lt\epsilon\lt(b-a)/2\), dan tetapkan
\[ D_m=(\D_m^+\cap[0,t])\cup\{t\}. \]
Kekontinuan kanan memberikan batas lintasan
\[ U_t\le\lim_{m\to\infty}u_{D_m}(a+\epsilon,b-\epsilon,\bs X). \]
Jika \(\bs X\) merupakan submartingal, pertidaksamaan waktu diskret pada \(D_m\), diikuti teorema konvergensi monoton, memberikan
\[ \E(U_t)\le\frac{\E[(X_t-a-\epsilon)^+]}{b-a-2\epsilon}. \]
Dengan membiarkan \(\epsilon\downarrow0\), diperoleh
\[ \E(U_t)\le\frac{1}{b-a}\E[(X_t-a)^+]. \]
Untuk supermartingal, argumen yang sama menggunakan bagian negatif dan menghasilkan
\[ \E(U_t)\le\frac{1}{b-a}\E[(X_t-a)^-]. \]</p>""",
        "description": "Use measurable entrance times and deterministic relaxed dyadic grids instead of an unjustified path-dependent cofinal family.",
    },
    {
        "id": "red-black-fair-case-introduction",
        "old": "Kita dapat menggunakan pertidaksamaan maksimal untuk supermartingal guna menunjukkan bahwa memang tidak ada strategi yang dapat memberikan hasil lebih baik.",
        "new": "Dalam kasus adil ini, pertidaksamaan maksimal untuk supermartingal menunjukkan bahwa tidak ada strategi yang dapat memberikan hasil lebih baik.",
        "description": "Scope the displayed x/a optimality argument to the fair case it actually proves.",
    },
    {
        "id": "red-black-nonnegative-bets",
        "old": r"kita harus memiliki \( Z_n \le W_{n-1} \)",
        "new": r"kita harus memiliki \( 0 \le Z_n \le W_{n-1} \)",
        "description": "State the nonnegative-stake condition needed to preserve the supermartingale direction and prevent debt.",
    },
    {
        "id": "red-black-valid-supermartingale-proof",
        "old": r"""<p>Karena \( \bs Y \) merupakan supermartingal dan \( \bs Z \) nonnegatif, <a href="Properties.html#trn">transformasi</a> \( \bs W = \bs Z \cdot \bs Y \) juga merupakan supermartingal. Berdasarkan <a class="ref" href="#max5"></a>:
		\[ \P(U_\infty \ge a) \le \frac{1}{a} \E(W_0) = \frac{x}{a} \]</p>""",
        "new": r"""<p>Kendala \(0\le Z_n\le W_{n-1}\) memastikan \(W_n\ge0\). Karena \(Z_n\) terukur terhadap informasi sebelum permainan ke-\(n\),
\[ \E(W_n\mid\mathscr F_{n-1})=W_{n-1}+Z_n(2p-1)\le W_{n-1}. \]
Jadi \(\bs W\) merupakan supermartingal nonnegatif. Berdasarkan <a class="ref" href="#max7"></a>,
		\[ \P(U_\infty \ge a) \le \frac{1}{a} \E(W_0) = \frac{x}{a}. \]</p>""",
        "description": "Prove the fortune process is a nonnegative supermartingale directly and invoke the correct all-time maximal inequality.",
    },
    {
        "id": "red-black-optimality-scope",
        "old": r"""Berdasarkan asumsi-asumsi dasar ini, tidak ada strategi yang dapat memberikan hasil lebih baik daripada permainan berani. Namun, <em>ada</em> strategi yang sama baiknya dengan permainan berani; strategi-strategi tersebut merupakan <a href="https://www.randomservices.org/random/games/Optimal.html">variasi permainan berani</a>.""",
        "new": r"""Ketika \(p=\frac12\), tidak ada strategi yang dapat memberikan hasil lebih baik daripada permainan berani karena strategi itu mencapai batas \(x/a\). Untuk \(p\lt\frac12\), batas \(x/a\) di atas saja tidak membuktikan optimalitas; hasil terpisah tentang <a href="https://www.randomservices.org/random/games/Optimal.html">variasi permainan berani</a> menangani kasus tersebut.""",
        "description": "Distinguish the fair-case proof from the separate subfair bold-play optimality theorem.",
    },
)

MARTINGALE_CONVERGENCE_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "submartingale-expectation-macro",
        "old": r"\( E(X_t \mid \mathscr{F}_s) \ge X_s\)",
        "new": r"\( \E(X_t \mid \mathscr{F}_s) \ge X_s\)",
        "description": "Use the page's defined expectation macro in the introductory submartingale relation.",
    },
    {
        "id": "upcrossing-time-domain",
        "old": r"\[ \E[U_t(a, b)] \le \frac{1}{b - a}[|a| + \E(|X_t|)]  \le \frac{|a| + c}{b - a}, \quad n \in \N\]",
        "new": r"\[ \E[U_t(a, b)] \le \frac{1}{b-a}[|a|+\E(|X_t|)] \le \frac{|a|+c}{b-a}, \quad t \in T \]",
        "description": "Use the general time index t in the first martingale-convergence proof.",
    },
    {
        "id": "upcrossing-limit-bound",
        "old": r"\[ \E[U_\infty(a, b)] \lt \frac{|a| + c}{b - a} \lt \infty  \]",
        "new": r"\[ \E[U_\infty(a,b)] \le \frac{|a|+c}{b-a} \lt \infty \]",
        "description": "Use the non-strict bound justified after passing to the increasing limit.",
    },
    {
        "id": "upcrossing-discrete-continuous-references",
        "old": r'<a href="Inequalities.html#upc3">karakterisasi</a> konvergensi kita dalam hal lintas-naik',
        "new": r'<a href="Inequalities.html#upc3">karakterisasi waktu diskret</a> dan <a href="Inequalities.html#upc7">karakterisasi waktu kontinu</a> dalam hal lintas-naik',
        "description": "Cite the separate discrete- and continuous-time upcrossing characterizations used by the theorem.",
    },
    {
        "id": "limit-variable-measurability",
        "old": r"Perhatikan bahwa \( X \) terukur terhadap \( \mathscr{F}_\infty \).",
        "new": r"Perhatikan bahwa \( X_\infty \) terukur terhadap \( \mathscr{F}_\infty \).",
        "description": "Name the limiting random variable in the measurability conclusion.",
    },
    {
        "id": "uniform-integrability-valid-terminal-proof",
        "old": r'''<p>Karena \( \bs X = \{X_t: t \in T\} \) terintegralkan seragam, \( \E(|X_t|) \) terbatas dalam \( t \in T \). Oleh karena itu, berdasarkan teorema konvergensi martingal <a class="ref" href="https://www.randomservices.org/random/martingales/mct1"></a>, terdapat \( X_\infty \) yang terukur terhadap \( \mathscr{F}_\infty \), sedemikian sehingga \( \E(|X_\infty|) \lt \infty \) dan \( X_t \to X_\infty \) ketika \( t \to \infty \) dengan probabilitas 1. Berdasarkan <a href="../expect/Uniform.html#con2">teorema keterintegralan seragam</a>, konvergensi tersebut juga berlaku dalam rata-rata, sehingga \( \E(|X_t - X|) \to 0 \) ketika \( t \to \infty \). Sekarang andaikan bahwa \( \bs X \) merupakan martingal terhadap \( \mathfrak F \). Untuk \( s \in T \) tetap, kita mengetahui bahwa \( \E(X_t \mid \mathscr{F}_s) \to \E(X_\infty \mid \mathscr{F}_s) \) ketika \( t \to \infty \) (dengan probabilitas 1). Namun, \( \E(X_t \mid \mathscr{F}_s) = X_s \) untuk \( t \ge s \), sehingga diperoleh \( X_s = \E(X_\infty \mid \mathscr{F}_s) \).</p>''',
        "new": r'''<p>Karena \(\bs X=\{X_t:t\in T\}\) terintegralkan seragam, \(\E(|X_t|)\) terbatas dalam \(t\in T\). Berdasarkan teorema konvergensi martingal <a class="ref" href="#mct1"></a>, terdapat peubah acak \(X_\infty\) yang terukur terhadap \(\mathscr F_\infty\), terintegralkan, dan memenuhi \(X_t\to X_\infty\) dengan probabilitas 1. Teorema <a href="../expect/Uniform.html#con2">keterintegralan seragam</a> juga memberikan konvergensi dalam rata-rata:
\[ \E(|X_t-X_\infty|)\to0. \]
Sekarang andaikan bahwa \(\bs X\) merupakan martingal. Untuk \(s\in T\) tetap, sifat kontraksi nilai harapan bersyarat dalam \(\mathscr L_1\) memberikan
\[ \E\!\left(\left|\E(X_t-X_\infty\mid\mathscr F_s)\right|\right) \le \E(|X_t-X_\infty|)\to0. \]
Karena \(\E(X_t\mid\mathscr F_s)=X_s\) untuk \(t\ge s\), limit ini menghasilkan \(X_s=\E(X_\infty\mid\mathscr F_s)\).</p>''',
        "description": "Repair the broken theorem link, use X_infinity in mean convergence, and justify the terminal representation through L1 contraction.",
    },
    {
        "id": "lp-theorem-martingale-hypothesis",
        "old": r"Misalkan kembali bahwa \( \bs X = \{X_t: t \in T\} \) merupakan submartingal atau supermartingal terhadap",
        "new": r"Misalkan kembali bahwa \( \bs X = \{X_t: t \in T\} \) merupakan martingal terhadap",
        "description": "Restrict the false general submartingale/supermartingale Lp claim to martingales, for which the cited maximal inequality applies.",
    },
    {
        "id": "lp-maximal-norm-subscript",
        "old": r"\[ \|W_t\|_k \le \frac{k}{k-1}\|X_t\| \le \frac{k c}{k - 1}, \quad t \in T \]",
        "new": r"\[ \|W_t\|_k \le \frac{k}{k-1}\|X_t\|_k \le \frac{k c}{k-1}, \quad t \in T \]",
        "description": "Restore the missing k-norm subscript in the Lp maximal estimate.",
    },
    {
        "id": "translate-as-in-limit-display",
        "old": r"\text{ as }",
        "new": r"\text{ ketika }",
        "description": "Translate the remaining prose connector inside the Lp convergence display.",
    },
    {
        "id": "simple-walk-increment-domain",
        "old": r"\( \bs{V} = \{V_n: n \in \N\} \)",
        "new": r"\( \bs{V} = \{V_n: n \in \N_+\} \)",
        "description": "Index the random-walk increments on the positive integers, where their laws are defined.",
    },
    {
        "id": "simple-walk-partial-sum-index",
        "old": r"\[ X_n = \sum_{i=0}^n V_i, \quad n \in \N \]",
        "new": r"\[ X_0=0, \qquad X_n=\sum_{i=1}^n V_i, \quad n\in\N_+. \]",
        "description": "Make the partial-sum definition consistent with the increment domain and stated mean.",
    },
    {
        "id": "simple-walk-state-space",
        "old": r"mengunjungi setiap keadaan dalam \( \N \) tak berhingga kali",
        "new": r"mengunjungi setiap keadaan dalam \( \mathbb Z \) tak berhingga kali",
        "description": "Use the integer state space of the simple symmetric random walk.",
    },
    {
        "id": "simple-walk-convergence-hypothesis-diagnosis",
        "old": r"Namun, tentu saja \( \E(X_n) = n (2 p - 1) \) untuk \( n \in \N \), sehingga teorema konvergensi martingal tidak berlaku.",
        "new": r"Dalam setiap kasus, \(\sup_n\E(|X_n|)=\infty\), sehingga syarat keterbatasan teorema konvergensi martingal gagal. Untuk \(p\ne\frac12\), hal ini mengikuti dari \(\E|X_n|\ge|\E X_n|=n|2p-1|\); untuk \(p=\frac12\), \(\E|X_n|\) bertumbuh seorde \(\sqrt n\).",
        "description": "Explain the failed L1-boundedness hypothesis in both biased and symmetric cases.",
    },
    {
        "id": "branching-limit-claim",
        "old": r"<li>Jika \( m \gt 1 \), maka \( q \in (0, 1) \). Berlaku \( X_n \to 0 \) ketika \( n \to \infty \) atau \( X_n \to \infty \) ketika \( n \to \infty \) dengan laju eksponensial.</li>",
        "new": r'''<li>Jika \(m\gt1\), maka \(q\in(0,1)\). Berlaku \(X_n\to0\) atau \(X_n\to\infty\). Selain itu, terdapat peubah acak nonnegatif berhingga \(W\), sedemikian sehingga
\[ \frac{X_n}{m^n}\to W \]
dengan probabilitas 1.</li>''',
        "description": "State the normalized branching-process limit actually supplied by martingale convergence.",
    },
    {
        "id": "branching-new-information-statement",
        "old": r"Informasi yang baru adalah laju divergensi menuju \( \infty \) pada (b).",
        "new": r"Informasi yang baru pada (b) adalah kekonvergenan martingal ternormalisasi \(X_n/m^n\).",
        "description": "Describe the normalized martingale convergence actually established, not an unsupported divergence rate.",
    },
    {
        "id": "branching-limit-rate-scope",
        "old": r"Jadi, jika \( m \gt 1 \) dan \( X_n \to \infty \) ketika \( n \to \infty \), maka divergensi menuju \( \infty \) pada dasarnya harus memiliki laju yang sama dengan \( m^n. \)",
        "new": r"Jadi, \(X_n/m^n\) konvergen dengan probabilitas 1 menuju limit nonnegatif berhingga. Argumen ini saja tidak menyiratkan bahwa limit tersebut positif pada kejadian tidak punah; kesimpulan demikian memerlukan syarat momen keturunan tambahan.",
        "description": "Remove the unsupported assertion that the normalized branching limit is positive on nonextinction.",
    },
    {
        "id": "beta-bernoulli-sample-mean-proof",
        "old": r'''Oleh karena itu, teorema konvergensi martingal <a class="ref" href="#mct3"></a> berlaku, dan konvergensi tersebut juga berlaku dalam rata-rata.</p>''',
        "new": r'''Oleh karena itu, teorema konvergensi martingal <a class="ref" href="#mct3"></a> berlaku, dan konvergensi \(Z_n\) juga berlaku dalam rata-rata. Selain itu,
\[ Z_n-M_n=\frac{a n-(a+b)Y_n}{n(a+b+n)}. \]
Karena \(0\le Y_n\le n\),
\[ |Z_n-M_n|\le\frac{\max(a,b)}{a+b+n}\to0. \]
Jadi, \(M_n\to P\) dengan probabilitas 1 dan
\[ \E(|M_n-P|)\le\E(|Z_n-P|)+\frac{\max(a,b)}{a+b+n}\to0. \]</p>''',
        "description": "Complete the omitted proof that the beta-Bernoulli sample mean shares the martingale limit in both modes.",
    },
    {
        "id": "polya-urn-variable-interpretation",
        "old": r'''Karena \( Y_n \) merupakan banyaknya bola merah dalam urna pada waktu \( n \in \N_+ \), banyaknya bola <em>rata-rata</em> pada waktu \( n \) adalah \( M_n = Y_n / n \). Di sisi lain, jumlah seluruh bola dalam urna pada waktu \( n \in \N \) adalah \( a + b + c n \), sehingga <em>proporsi</em> bola merah dalam urna pada waktu \( n \) adalah''',
        "new": r'''Peubah \(Y_n\) menyatakan banyaknya pemilihan bola merah dalam \(n\) pengambilan pertama. Untuk \(n\in\N_+\), \(M_n=Y_n/n\) merupakan proporsi sampel pemilihan merah. Banyaknya bola merah dalam urna pada waktu \(n\) adalah \(a+cY_n\), sedangkan jumlah seluruh bolanya \(a+b+cn\). Jadi, proporsi bola merah dalam urna adalah''',
        "description": "Correct the meanings of the Pólya-urn draw count and sample proportion.",
    },
    {
        "id": "likelihood-ratio-infinite-mean-proof",
        "old": r'''Peubah-peubah \( \ln[g_0(X_i) / g_1(X_i)] \) untuk \( i \in \N_+ \) juga independen dan berdistribusi identik, jadi misalkan \( m \) menyatakan rata-rata bersamanya. Logaritma alami bersifat cekung dan martingal \( \bs L \) memiliki rata-rata 1, sehingga berdasarkan <a href="https://www.randomservices.org/random/expect/Properties2.html#jen">pertidaksamaan Jensen</a>,
		\[ m = \E\left(\ln\left[\frac{g_0(X)}{g_1(X)}\right]\right) \lt \ln\left(\E\left[\frac{g_0(X)}{g_1(X)}\right]\right) = \ln(1) = 0  \]
		Oleh karena itu, \( m \in [-\infty, 0) \). Berdasarkan <a href="https://www.randomservices.org/random/sample/LLN.html">hukum kuat bilangan besar</a>, \( \frac{1}{n} \ln(L_n) \to m \) ketika \( n \to \infty \) dengan probabilitas 1. Dengan demikian, harus berlaku \( \ln(L_n) \to -\infty \) ketika \( n \to \infty \) dengan probabilitas 1. Namun, berdasarkan kekontinuan, \( \ln(L_n) \to \ln(L_\infty) \) ketika \( n \to \infty \) dengan probabilitas 1, sehingga \( L_\infty = 0 \) dengan probabilitas 1.</p>''',
        "new": r'''Tetapkan
\[ \xi_i=\ln\left[\frac{g_0(X_i)}{g_1(X_i)}\right], \quad i\in\N_+. \]
Peubah-peubah \(\xi_i\) independen dan berdistribusi identik. Karena \(\xi_i^+\le g_0(X_i)/g_1(X_i)\), bagian positifnya terintegralkan. Pertidaksamaan Jensen tegas memberikan
\[ m=\E(\xi_1)\in[-\infty,0). \]
Jika \(m\gt-\infty\), <a href="https://www.randomservices.org/random/sample/LLN.html">hukum kuat bilangan besar</a> memberikan
\[ \frac1n\ln L_n=\frac1n\sum_{i=1}^n\xi_i\to m\lt0. \]
Jika \(m=-\infty\), tetapkan \(\xi_i^{(r)}=\xi_i\vee(-r)\) untuk \(r\in\N_+\). Hukum kuat dan \(\xi_i\le\xi_i^{(r)}\) memberikan
\[ \limsup_{n\to\infty}\frac1n\ln L_n\le\E(\xi_1^{(r)}). \]
Ketika \(r\to\infty\), ruas kanan menuju \(-\infty\). Jadi, dalam kedua kasus, \(\ln L_n\to-\infty\). Pada kejadian \(\{L_\infty\gt0\}\), kekontinuan justru akan memberikan \(\ln L_n\to\ln L_\infty\in\R\), suatu kontradiksi. Oleh karena itu, \(L_\infty=0\) dengan probabilitas 1.</p>''',
        "description": "Handle an infinite logarithmic mean by truncation and avoid applying logarithmic continuity at zero.",
    },
    {
        "id": "partial-product-normalized-domain",
        "old": r"\( \{\sqrt{X_n} / a_n: n \in \N\} \)",
        "new": r"\( \{\sqrt{X_n} / a_n: n \in \N_+\} \)",
        "description": "Exclude the undefined X_0/a_0 term from the normalized product sequence.",
    },
    {
        "id": "partial-product-ratio-scope",
        "old": r"\(Z_n = \prod_{i=1}^n \sqrt{X_i} / a_i\)",
        "new": r"\(Z_n = \prod_{i=1}^n \frac{\sqrt{X_i}}{a_i}\)",
        "description": "Place the normalization inside the product so the index is bound and the later squared identity follows.",
    },
    {
        "id": "density-restriction-total-variation-bound",
        "old": r"Selain itu, \( \E(|X_n|) = \|\mu\| \) (variasi total dari \( \mu \)) untuk setiap \( n \in \N \). Karena \( \mu \) merupakan ukuran berhingga, \( \|\mu\| \lt \infty \), sehingga teorema konvergensi martingal",
        "new": r"Selain itu, \(\E(|X_n|)=|\mu\!\restriction_{\mathscr F_n}|(\Omega)\le |\mu|(\Omega)\lt\infty\) untuk setiap \(n\in\N\), sehingga teorema konvergensi martingal",
        "description": "Bound the variation of each restricted signed measure by the ambient total variation instead of asserting equality.",
    },
    {
        "id": "density-expectation-notation",
        "old": r"\( E(X_n: A) = \E(Y_\infty; A) \)",
        "new": r"\( \E(X_n; A) = \E(Y_\infty; A) \)",
        "description": "Use the defined expectation macro and event separator in the density-martingale proof.",
    },
    {
        "id": "density-defined-measures",
        "old": r"\( \mu_\infty(B) = 0 \) dan \( \P_\infty(B^c) = 0 \)",
        "new": r"\( \mu(B) = 0 \) dan \( \P(B^c) = 0 \)",
        "description": "Use the measures actually defined on the terminal sigma-algebra.",
    },
    {
        "id": "density-signed-measure-proof",
        "old": r'''Jika \( \mu \) merupakan ukuran berhingga umum, maka berdasarkan <a href="https://www.randomservices.org/random/foundations/General.html#jor">teorema dekomposisi Jordan</a>, \( \mu \) dapat ditulis secara unik dalam bentuk \( \mu = \mu^+ - \mu^- \), dengan \( \mu^+ \) dan \( \mu^- \) merupakan ukuran positif berhingga. Selain itu, \( X_n^+ \) merupakan fungsi kepadatan \( \mu^+ \) pada \(\mathscr{F}_n\), dan \( X_n^- \) merupakan fungsi kepadatan \( \mu^- \) pada \( \mathscr{F}_n \). Berdasarkan bagian pertama bukti, \( X^+ = 0 \), \( X^- = 0 \), dan juga \( X = 0 \), semuanya dengan probabilitas 1.''',
        "new": r'''Untuk ukuran bertanda berhingga, kesingularan \(\mu\) dan \(\P\) berarti \(|\mu|\perp\P\) pada \(\mathscr F_\infty\). Ulangi argumen di atas dengan \(|X_\infty|\) dan \(|\mu|\). Jika \(A\in\mathscr F_k\) dan \(n\ge k\), maka
\[ \E(|X_n|;A)=|\mu\!\restriction_{\mathscr F_n}|(A)\le|\mu|(A). \]
Lema Fatou memberikan \(\E(|X_\infty|;A)\le|\mu|(A)\). Dengan argumen kelas monoton yang sama, pertidaksamaan ini berlaku untuk setiap \(A\in\mathscr F_\infty\). Kesingularan menyediakan \(B\in\mathscr F_\infty\) dengan \(|\mu|(B)=0\) dan \(\P(B^c)=0\). Karena itu,
\[ \E(|X_\infty|)=\E(|X_\infty|;B)\le|\mu|(B)=0, \]
sehingga \(X_\infty=0\) dengan probabilitas 1.''',
        "description": "Use total variation of each restricted signed measure; ambient Jordan parts need not remain absolutely continuous on coarse sigma-algebras.",
    },
    {
        "id": "density-sum-mobile-reflow",
        "change_kind": "deterministic-output",
        "old": r"\[ \E(X_n; A) = \sum_{j \in J} \E(X_n; A^n_j) = \sum_{j \in J} \frac{\mu(A^n_j)}{\P(A^n_j)} \P(A^n_j) = \sum_{j \in J} \mu(A^n_j) = \mu(A)\]",
        "new": r'''\[
\begin{aligned}
\E(X_n;A)
&amp;=\sum_{j\in J}\E(X_n;A_j^n) \\
&amp;=\sum_{j\in J}\frac{\mu(A_j^n)}{\P(A_j^n)}\P(A_j^n) \\
&amp;=\sum_{j\in J}\mu(A_j^n)=\mu(A).
\end{aligned}
\]''',
        "description": "Reflow the density equality chain into readable mobile lines without changing its mathematics.",
    },
    {
        "id": "dyadic-partition-mobile-reflow",
        "change_kind": "deterministic-output",
        "old": r"\[ \mathscr{A}_n = \left\{\left[\frac{j}{2^n}, \frac{j + 1}{2^n}\right): j \in \{0, 1, \ldots, 2^n - 1\}\right\} \]",
        "new": r'''\[
\mathscr A_n=
\left\{
\left[\frac{j}{2^n},\frac{j+1}{2^n}\right)
:j\in\{0,1,\ldots,2^n-1\}
\right\}.
\]''',
        "description": "Reflow the dyadic-partition set builder for phone readability without changing the set.",
    },
    {
        "id": "measure-interval-argument",
        "old": r"\(2^n \mu[j / 2^n, (j + 1) / 2^n) \)",
        "new": r"\(2^n \mu\!\left([j / 2^n, (j + 1) / 2^n)\right) \)",
        "description": "Write the dyadic interval as the argument of the measure.",
    },
    {
        "id": "doob-heading-visible-reference",
        "change_kind": "source-link-repair",
        "old": r'<a class="ref" href="#doo"></a> yang terkait',
        "new": r'<a class="ref" href="#doo">pembahasan Martingal Doob</a> yang terkait',
        "description": "Supply visible Indonesian text for the heading reference that Basic.js cannot populate.",
    },
)

MARTINGALE_BACKWARDS_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "negative-time-filtration-mathscr",
        "old": r"koleksi \( \mathfrak F \) merupakan keluarga menaik subaljabar-\( \sigma \) dari \( \scr F \)",
        "new": r"koleksi \( \mathfrak F \) merupakan keluarga menaik subaljabar-\( \sigma \) dari \( \mathscr F \)",
        "description": "Replace the undefined scr command in the negative-time filtration proof.",
    },
    {
        "id": "finite-reversal-filtration-mathscr",
        "old": r"koleksi \( \mathfrak{F}^t \) merupakan keluarga menaik subaljabar-\( \sigma \) dari \( \scr F \)",
        "new": r"koleksi \( \mathfrak{F}^t \) merupakan keluarga menaik subaljabar-\( \sigma \) dari \( \mathscr F \)",
        "description": "Replace the undefined scr command in the finite-horizon reversal proof.",
    },
    {
        "id": "continuous-time-path-regularity",
        "old": r"Berikut <dfn>teorema konvergensi martingal mundur</dfn> yang utama:",
        "new": r"Untuk \(T=[0,\infty)\), hasil konvergensi di bawah ini juga mensyaratkan suatu versi \(\bs Y\) dengan lintasan kontinu kiri dan limit kanan. Untuk \(T=\N\), tidak diperlukan asumsi lintasan tambahan. Inilah <dfn>teorema konvergensi martingal mundur</dfn> yang utama:",
        "description": "Add the path regularity needed for an all-real-time reverse-martingale limit; fixed-time versions alone do not control continuous-time paths.",
    },
    {
        "id": "finite-horizon-upcrossing-terminal-variable",
        "old": r"\[\E[U_t(a, b)] \le \frac{1}{b - a}[\E(|X_t|) + |a|] = \frac{1}{b - a} [\E(|Y_0|) + |a|] \]",
        "new": r"\[ \E[U_t(a,b)] \le \frac{1}{b-a}\big[\E(|X^t_t|)+|a|\big] = \frac{1}{b-a}\big[\E(|Y_0|)+|a|\big] \]",
        "description": "Use the defined finite-horizon process X^t at its terminal time.",
    },
    {
        "id": "downcrossing-limit-direction",
        "old": r"Karena \( U_t \uparrow U_\infty \) ketika \( t \to -\infty \), berdasarkan teorema konvergensi monoton diperoleh",
        "new": r"Karena \(U_t\uparrow U_\infty\) ketika \(t\to\infty\), berdasarkan teorema konvergensi monoton diperoleh",
        "description": "Send the expanding positive-time horizon to positive infinity, not negative infinity.",
    },
    {
        "id": "downcrossing-expectation-macro",
        "old": r"\[ E[U_\infty(a, b)] \le \frac{1}{b - a} [\E(|Y_0|) + |a|]\]",
        "new": r"\[ \E[U_\infty(a,b)] \le \frac{1}{b-a}\big[\E(|Y_0|)+|a|\big] \]",
        "description": "Use the page's defined expectation macro in the downcrossing bound.",
    },
    {
        "id": "terminal-limit-identification-and-markup",
        "old": r'''</p><p>
</p><p>Masih perlu ditunjukkan bahwa \( Y_\infty = \E(Y_0 \mid \mathscr{G}_\infty) \).  Misalkan \( A \in \mathscr{G}_\infty \). Maka \( A \in \mathscr{G}_t \) untuk setiap \( t \in T \). Karena \( Y_t = \E(Y_0 \mid \mathscr{G}_t) \), berdasarkan definisi diperoleh bahwa \( \E(Y_t; A) = \E(Y_0; A) \) untuk setiap \( t \in T \). Dengan mengambil \( t \to \infty \) dan menggunakan teorema konvergensi terdominasi, diperoleh \( \E(Y_\infty ; A) = \E(Y_0; A) \). Oleh karena itu, \( Y_\infty = \E(Y_0 \mid \mathscr{G}_\infty) \).</p>''',
        "new": r'''</p>
<p>Masih perlu mengidentifikasi limit tersebut. Tetapkan \(Y_\infty\) sebagai limit di sepanjang indeks bilangan bulat; limit di sepanjang indeks \(T\) yang diperoleh di atas harus sama. Untuk setiap \(s\in T\), peubah \(Y_n\) terukur terhadap \(\mathscr G_s\) untuk setiap bilangan bulat \(n\ge s\). Jadi, \(Y_\infty\) terukur terhadap setiap \(\mathscr G_s\), dan karena itu terhadap \(\mathscr G_\infty\). Jika \(A\in\mathscr G_\infty\), maka \(\E(Y_t;A)=\E(Y_0;A)\) untuk setiap \(t\in T\). Karena \(Y_t\to Y_\infty\) dalam \(\mathscr L_1\),
\[ \left|\E(Y_t;A)-\E(Y_\infty;A)\right|\le \E(|Y_t-Y_\infty|)\to0. \]
Dengan demikian, \(\E(Y_\infty;A)=\E(Y_0;A)\) untuk setiap \(A\in\mathscr G_\infty\), yang membuktikan \(Y_\infty=\E(Y_0\mid\mathscr G_\infty)\).</p>''',
        "description": "Remove the parser-created empty paragraph, prove terminal measurability, and use established L1 convergence instead of an unavailable dominator.",
    },
    {
        "id": "lp-jensen-parenthesis",
        "old": r"\E[\E(|Y_0|^k \mid \mathscr{G}_t]",
        "new": r"\E[\E(|Y_0|^k \mid \mathscr{G}_t)]",
        "description": "Close the inner conditional expectation before closing the outer expectation.",
    },
    {
        "id": "slln-decreasing-family-positive-index",
        "old": r"Sekarang, untuk \( n \in \N \), tetapkan",
        "new": r"Sekarang, untuk \(n\in\N_+\), tetapkan",
        "description": "Define the decreasing family on the same positive index set as the sample-mean process.",
    },
    {
        "id": "slln-filtration-positive-index",
        "old": r"\( \mathfrak G = \{\mathscr{G}_n: n \in \N\} \) merupakan keluarga menurun",
        "new": r"\(\mathfrak G=\{\mathscr G_n:n\in\N_+\}\) merupakan keluarga menurun",
        "description": "Keep the SLLN reverse filtration and sample means on a common positive-integer index set.",
    },
    {
        "id": "slln-sum-expectation-macro",
        "old": r"\sum_{j=1}^n E(X_j \mid \mathscr{G}_n)",
        "new": r"\sum_{j=1}^n \E(X_j \mid \mathscr{G}_n)",
        "description": "Use the defined expectation macro in the exchangeability calculation.",
    },
    {
        "id": "slln-positive-index-shift",
        "old": r"Dengan membagi oleh \( n \), diperoleh \( \E(M_n \mid \mathscr{G}_{n+1}) = M_{n+1} \), sehingga \( \bs M \) merupakan martingal mundur terhadap \( \mathfrak G \). Berdasarkan teorema konvergensi martingal mundur, terdapat \( M_\infty \), sedemikian sehingga",
        "new": r"Dengan membagi oleh \(n\), diperoleh \(\E(M_n\mid\mathscr G_{n+1})=M_{n+1}\), sehingga \(\{M_n:n\in\N_+\}\) merupakan martingal mundur terhadap \(\{\mathscr G_n:n\in\N_+\}\). Setelah pergeseran indeks \(Z_r=M_{r+1}\) dan \(\mathscr H_r=\mathscr G_{r+1}\), teorema konvergensi martingal mundur memberikan \(M_\infty\), sedemikian sehingga",
        "description": "Make the positive-index reverse martingale an explicit index shift before invoking the theorem stated on N.",
    },
    {
        "id": "de-finetti-bit-string-index",
        "old": r"\sum_{i=0}^n x_i = k",
        "new": r"\sum_{i=1}^n x_i = k",
        "description": "Sum the defined bit-string coordinates x_1 through x_n, not an undefined x_0.",
    },
    {
        "id": "de-finetti-tail-field-index",
        "old": r"\( \mathscr{G}_\infty = \bigcap_{n=0}^\infty \mathscr{G}_n \)",
        "new": r"\(\mathscr G_\infty=\bigcap_{n=1}^\infty\mathscr G_n\)",
        "description": "Start the intersection where the de Finetti proof actually defines G_n.",
    },
    {
        "id": "de-finetti-positive-probability-conditioning",
        "old": r"Misalkan \( m \in \N_+ \) dan \( k \in \{0, 1, \ldots m\} \). Gagasan kuncinya adalah bahwa karena peubah-peubahnya dapat dipertukarkan, jika diberikan \( Y_m = k \),",
        "new": r"Misalkan \(m\in\N_+\) dan \(k\in\{0,1,\ldots,m\}\) dengan \(\P(Y_m=k)\gt0\). Karena peubah-peubahnya dapat dipertukarkan, jika diberikan \(Y_m=k\),",
        "description": "Condition only on totals with positive probability in the elementary finite calculation.",
    },
    {
        "id": "de-finetti-first-doob-conditioning-field",
        "old": r'''Jika \( Y_m \) diberikan, peubah-peubah \( (Y_{m+1}, Y_{m+2}, \ldots) \) tidak memberikan informasi tambahan tentang distribusi \( (X_1, X_2, \ldots, X_n) \), sehingga
		\[ \P(X_1 = x_1, X_2 = x_2, \ldots, X_n = x_n \mid \mathscr{G}_m) =\E[\bs{1}(X_1 = x_1, X_2 = x_2, \ldots, X_n = x_n) \mid \mathscr{G}_n] = \frac{Y_m^{(j)} (m - Y_m)^{(n - j)}}{m^{(n)}} \]''',
        "new": r'''Jika \(Y_m\) diberikan, peubah-peubah \((Y_{m+1},Y_{m+2},\ldots)\) tidak memberikan informasi tambahan tentang susunan \((X_1,\ldots,X_n)\). Tetapkan \(A_{\bs x}=\{X_1=x_1,\ldots,X_n=x_n\}\). Maka
\[
\P(A_{\bs x}\mid\mathscr G_m)
=\E[\bs 1(A_{\bs x})\mid\mathscr G_m]
=\frac{Y_m^{(j)}(m-Y_m)^{(n-j)}}{m^{(n)}}.
\]''',
        "description": "Condition the indicator on G_m, the field that varies with m, and abbreviate the event for a readable display.",
    },
    {
        "id": "de-finetti-doob-construction-reference",
        "old": r'martingal mundur Doob <a class="ref" href="#prp1"></a>',
        "new": r'martingal mundur Doob <a class="ref" href="#prp2"></a>',
        "description": "Cite the result that constructs conditional-expectation reverse martingales.",
    },
    {
        "id": "de-finetti-integrability-index",
        "old": r"\( \E(M_n) \le 1 \) untuk setiap \( n \in \N \)",
        "new": r"\(\E(|M_n|)\le1\) untuk setiap \(n\in\N_+\)",
        "description": "State integrability explicitly on the positive index set where M_n is defined.",
    },
    {
        "id": "de-finetti-hypergeometric-null-events",
        "old": r"distribusi bersyarat \( Y_n \) jika diberikan \( Y_m = k \) adalah distribusi hipergeometrik dengan parameter \( m \), \( k \), dan \( n \):",
        "new": r"untuk setiap \(k\in\{0,1,\ldots,m\}\) dengan \(\P(Y_m=k)\gt0\), distribusi bersyarat \(Y_n\) jika diberikan \(Y_m=k\) adalah distribusi hipergeometrik dengan parameter \(m\), \(k\), dan \(n\):",
        "description": "Qualify the elementary conditional hypergeometric law on non-null totals.",
    },
    {
        "id": "de-finetti-conditional-mean-scale",
        "old": r'''Atau secara ekuivalen, \( \E(M_n \mid Y_m) = Y_m / m = M_m \).  Sekali lagi, jika \( Y_m \) diberikan, peubah-peubah \( Y_{m+1}, Y_{m+2} \) tidak memberikan informasi tambahan, sehingga \( \E(Y_n \mid \mathscr{G}_m) = Y_m \). Oleh karena itu, \( \bs M \) merupakan martingal mundur terhadap \( \mathfrak G \). Berdasarkan teorema konvergensi martingal mundur <a class="ref" href="#prp3"></a>, terdapat peubah acak \( P \), sedemikian sehingga''',
        "new": r'''Atau secara ekuivalen, \(\E(M_n\mid Y_m)=Y_m/m=M_m\). Sekali lagi, jika \(Y_m\) diberikan, peubah-peubah \(Y_{m+1},Y_{m+2},\ldots\) tidak memberikan informasi tambahan tentang \(Y_n\). Jadi, \(\E(Y_n\mid\mathscr G_m)=\frac{n}{m}Y_m\), atau secara ekuivalen \(\E(M_n\mid\mathscr G_m)=M_m\). Dengan demikian, \(\{M_n:n\in\N_+\}\) merupakan martingal mundur terhadap \(\mathfrak G\). Setelah menggeser indeks, teorema konvergensi martingal mundur <a class="ref" href="#prp3"></a> memberikan peubah acak \(P\), sedemikian sehingga''',
        "description": "Restore the n/m conditional-mean scale and make the positive-index theorem invocation explicit.",
    },
    {
        "id": "de-finetti-final-index-set-comma",
        "old": r"\( j \in \{0, 1, \ldots n\} \), serta",
        "new": r"\(j\in\{0,1,\ldots,n\}\), serta",
        "description": "Restore the missing separator before the final index in the finite-dimensional argument.",
    },
    {
        "id": "hypergeometric-limit-localization",
        "change_kind": "deterministic-output",
        "old": r"\[ \frac{k_m^{(j)} (m - k_m)^{(n - j)}}{m^{(n)}} \to p^j (1 - p)^{n - j} \text{ as } m \to \infty \]",
        "new": r"\[ \frac{k_m^{(j)}(m-k_m)^{(n-j)}}{m^{(n)}} \to p^j(1-p)^{n-j} \text{ ketika } m\to\infty \]",
        "description": "Translate the prose connector retained inside the source TeX and tighten the display without changing its mathematics.",
    },
    {
        "id": "de-finetti-final-conditioning-tower",
        "old": r'''Peubah acak \( P \) terukur terhadap \( \mathscr{G}_\infty \), sehingga
		\[ \P(X_1 = x_1, X_2 = x_2, \ldots, X_n = x_n \mid P) = P^j (1 - P)^{n - j} \text{ as } m \to \infty \]''',
        "new": r'''Karena \(P\) terukur terhadap \(\mathscr G_\infty\), sifat menara dan identitas sebelumnya memberikan
\[
\begin{aligned}
\P(A_{\bs x}\mid P)
&amp;=\E\!\left[\P(A_{\bs x}\mid\mathscr G_\infty)\mid P\right] \\
&amp;=P^j(1-P)^{n-j}.
\end{aligned}
\]''',
        "description": "Use the tower property to pass from conditioning on G_infinity to conditioning on P and remove the stale limit phrase.",
    },
    {
        "id": "general-de-finetti-scope",
        "old": r"Pada dasarnya, jika \( \bs X = (X_1, X_2, \ldots) \) merupakan barisan peubah acak yang dapat dipertukarkan, dengan masing-masing bernilai dalam ruang terukur \( (S, \mathscr{S}) \) yang cukup baik, maka terdapat peubah acak \( \Theta \), sedemikian sehingga \( \bs X \) independen dan berdistribusi identik jika diberikan \( \Theta \). Dalam bukti tersebut, hasil bahwa \( M_n \to P \) ketika \( n \to \infty \) dengan probabilitas 1, dengan \( M_n = \frac{1}{n} \sum_{i=1}^n X_i \), dikenal sebagai <dfn>hukum kuat bilangan besar de Finetti</dfn>.",
        "new": r"Pada dasarnya, jika \(\bs X=(X_1,X_2,\ldots)\) merupakan barisan peubah acak yang dapat dipertukarkan dan bernilai dalam ruang Borel standar \((S,\mathscr S)\), maka terdapat ukuran probabilitas acak \(\Theta\) pada \((S,\mathscr S)\), sedemikian sehingga, jika diberikan \(\Theta\), peubah-peubah dalam \(\bs X\) independen dan masing-masing berdistribusi \(\Theta\). Untuk barisan dapat dipertukarkan bernilai riil dan terintegralkan, konvergensi hampir pasti dari rata-rata sampel \(M_n=\frac1n\sum_{i=1}^nX_i\) dikenal sebagai <dfn>hukum kuat bilangan besar de Finetti</dfn>.",
        "description": "State the standard-Borel scope of the general representation and restrict arithmetic sample means to integrable real-valued variables.",
    },
    {
        "id": "mixture-product-space-comma",
        "old": r"\( (S^n \mathscr{S}^n) \)",
        "new": r"\((S^n,\mathscr S^n)\)",
        "description": "Separate the carrier space from its product sigma-algebra.",
    },
)

MARKOV_GENERAL_READER_CORRECTIONS = (
    {
        "id": "state-space-dimension-index",
        "old": r"\( S = \R^k \) untuk suatu \( k \in S \)",
        "new": r"\(S=\R^k\) untuk suatu \(k\in\N_+\)",
        "description": "Use a positive integer, rather than a state-space element, for the Euclidean dimension.",
    },
    {
        "id": "filtration-completeness-event-sigma-algebra",
        "old": r"jika \( A \in \mathscr{S} \) dengan \( \P(A) = 0 \)",
        "new": r"jika \(A\in\mathscr F\) dengan \(\P(A)=0\)",
        "description": "Place null events in the event sigma-algebra rather than the state sigma-algebra.",
    },
    {
        "id": "full-information-filtration-name",
        "old": r"filtrasi tersebut adalah filtrasi trivial dengan \( \mathscr{F}_t = \mathscr{F} \) untuk semua \( t \in T \)",
        "new": r"filtrasi tersebut adalah filtrasi informasi penuh yang konstan dengan \(\mathscr F_t=\mathscr F\) untuk semua \(t\in T\)",
        "description": "Distinguish the full-information filtration from the usual trivial filtration {empty set, Omega}.",
    },
    {
        "id": "full-information-filtration-tail-name",
        "old": "Namun, tentu saja filtrasi trivial ini biasanya tidak masuk akal.",
        "new": "Namun, tentu saja filtrasi informasi penuh yang konstan ini biasanya tidak masuk akal.",
        "description": "Use the corrected full-information name consistently through the end of the paragraph.",
    },
    {
        "id": "homogeneity-consistent-transition-kernels",
        "old": r'''<div class="unit" id="dfn3">
<p class="dfn">Proses Markov \( \bs{X} \) <dfn>homogen terhadap waktu</dfn> jika 
	\[ \P(X_{s+t} \in A \mid X_s = x) = \P(X_t \in A \mid X_0 = x) \]
	untuk setiap \( s, \, t \in T \), \( x \in S \), dan \( A \in \mathscr{S} \).</p>
</div>''',
        "new": r'''<div class="unit" id="dfn3">
<p class="dfn">Proses Markov \(\bs X\) <dfn>homogen terhadap waktu</dfn> jika terdapat keluarga kernel probabilitas \(\{P_t:t\in T\}\) pada \((S,\mathscr S)\) sedemikian sehingga
\[
\P(X_{s+t}\in A\mid\mathscr F_s)=P_t(X_s,A)\quad\text{hampir pasti}
\]
untuk setiap \(s,t\in T\) dan \(A\in\mathscr S\). Rumus untuk setiap keadaan \(x\) menggunakan keluarga Markov \((\P_x)_{x\in S}\), atau versi kernel transisi yang dipilih secara konsisten.</p>
</div>''',
        "description": "Define homogeneity through consistent all-state kernels instead of pointwise conditioning on possibly null events.",
    },
    {
        "id": "feller-semigroup-definition",
        "old": r'''<div class="unit" id="fel1">
<p class="dfn">Proses Markov \( \bs{X} = \{X_t: t \in T\} \) adalah <dfn>proses Feller</dfn> jika syarat-syarat berikut terpenuhi.</p>
<ol class="sub">
<li><dfn>Kontinuitas dalam ruang</dfn>: Untuk \( t \in T \) dan \( y \in S \), distribusi \( X_t \) dengan syarat \( X_0 = x \) <a href="../dist/Convergence.html">konvergen</a> ke distribusi \( X_t \) dengan syarat \( X_0 = y \) ketika \( x \to y \).</li>
<li><dfn>Kontinuitas dalam waktu</dfn>: Dengan \(X_0 = x \) untuk \( x \in S \), \( X_t \) <a href="../prob/Convergence.html">konvergen dalam probabilitas</a> ke \( x \) ketika \( t \downarrow 0 \).</li>
</ol>
<details>
<summary>Rincian:</summary>
<ol class="sub">
<li>Ini berarti bahwa \( \E[f(X_t) \mid X_0 = x] \to \E[f(X_t) \mid X_0 = y] \) ketika \( x \to y \) untuk setiap \( f \in \mathscr{C} \).</li>
<li>Ini berarti bahwa \( \P[X_t \in U \mid X_0 = x] \to 1 \) ketika \( t \downarrow 0 \) untuk setiap lingkungan \( U \) dari \( x \).</li>
</ol>
</details>
</div>''',
        "new": r'''<div class="unit" id="fel1">
<p class="dfn">Proses Markov homogen \(\bs X=\{X_t:t\in T\}\) dengan semigrup transisi \(\{P_t:t\in T\}\) adalah <dfn>proses Feller</dfn> jika:</p>
<ol class="sub">
<li><dfn>Kontinuitas dalam ruang</dfn>: \(P_t f\in\mathscr C_0\) untuk setiap \(t\in T\) dan \(f\in\mathscr C_0\).</li>
<li><dfn>Kontinuitas pada waktu nol</dfn>: jika \(T=[0,\infty)\), maka \(P_t f(x)\to f(x)\) ketika \(t\downarrow0\), untuk setiap \(f\in\mathscr C_0\) dan \(x\in S\). Syarat waktu ini otomatis dalam waktu diskret.</li>
</ol>
<details>
<summary>Rincian:</summary>
<p>Syarat pertama memuat ketentuan lenyap di tak hingga, bukan hanya kekontinuan lemah terhadap keadaan awal. Bersama syarat kedua, kondisi ini memberikan semigrup Feller yang kuat kontinu pada \(\mathscr C_0\).</p>
</details>
</div>''',
        "description": "Use the standard C0-preserving Feller definition that is needed by the later semigroup results.",
    },
    {
        "id": "feller-discrete-state-qualification",
        "old": r"Perhatikan bahwa jika \( S \) diskret, (a) terpenuhi secara otomatis, dan jika \( T \) diskret, (b) terpenuhi secara otomatis. Secara khusus, setiap rantai Markov waktu diskret merupakan proses Markov Feller.",
        "new": r"Syarat waktu otomatis jika \(T\) diskret. Syarat ruang otomatis pada ruang keadaan diskret berhingga, tetapi tetap harus diperiksa pada ruang diskret tak berhingga; karena itu, tidak setiap rantai waktu diskret pada ruang tak berhingga bersifat Feller.",
        "description": "Do not claim that every infinite-state discrete-time chain preserves C0.",
    },
    {
        "id": "feller-cadlag-version-scope",
        "old": r'''<div class="unit" id="fel2">
<p class="math">Jika \( \bs{X} = \{X_t: t \in T\} \) merupakan proses Feller, maka terdapat <a href="../prob/Processes.html">versi</a> dari \( \bs{X} \) sedemikian sehingga \( t \mapsto X_t(\omega) \) kontinu dari kanan dan memiliki limit kiri untuk setiap \( \omega \in \Omega \).</p>
</div>''',
        "new": r'''<div class="unit" id="fel2">
<p class="math">Dalam waktu kontinu, realisasi Markov dari semigrup Feller pada ruang keadaan LCCB memiliki <a href="../prob/Processes.html">versi</a> càdlàg: \(t\mapsto X_t(\omega)\) kontinu dari kanan dan memiliki limit kiri. Pernyataan ini dipakai bersama keluarga Markov dan penyempurnaan filtrasi yang lazim.</p>
</div>''',
        "description": "State the path-regularity conclusion with its continuous-time Markov-family scope.",
    },
    {
        "id": "strong-markov-feller-version",
        "old": r'''<div class="unit">
<p class="math">Jika \( \bs{X} = \{X_t: t \in [0, \infty) \) adalah proses Markov Feller, maka \( \bs{X} \) merupakan proses Markov kuat relatif terhadap filtrasi \( \mathfrak{F}^0_+ \), yaitu penyempurnaan kontinu kanan dari filtrasi alami.</p>
</div>''',
        "new": r'''<div class="unit">
<p class="math">Misalkan \(\bs X=\{X_t:t\in[0,\infty)\}\) adalah versi càdlàg dari proses Feller dengan keluarga Markovnya. Terhadap penyempurnaan lengkap dan kontinu kanan yang lazim dari filtrasi alami, \(\bs X\) memiliki sifat Markov kuat.</p>
</div>''',
        "description": "Close the malformed set and state the path and filtration hypotheses for the strong Markov conclusion.",
    },
    {
        "id": "transition-kernel-version-scope",
        "old": r'''<div class="unit" id="trn1">
<p class="math">Untuk \( t \in T \), misalkan
	\[ P_t(x, A) = \P(X_t \in A \mid X_0 = x), \quad x \in S, \, A \in \mathscr{S} \]
	Maka \( P_t \) adalah kernel probabilitas pada \( (S, \mathscr{S}) \), yang dikenal sebagai <dfn>kernel transisi</dfn> dari \( \bs{X} \) untuk waktu \( t \).</p>
<details>
<summary>Rincian:</summary>
<p>Tetapkan \( t \in T \). Keterukuran \( x \mapsto \P(X_t \in A \mid X_0 = x) \) untuk \( A \in \mathscr{S} \) sudah tercakup dalam definisi probabilitas bersyarat. Selain itu, tentu saja, \( A \mapsto \P(X_t \in A \mid X_0 = x) \) merupakan ukuran probabilitas pada \( \mathscr{S} \) untuk \( x \in S \). Secara umum, distribusi bersyarat satu peubah acak, dengan syarat nilai peubah acak lain, mendefinisikan kernel probabilitas.</p>
</details>
</div>''',
        "new": r'''<div class="unit" id="trn1">
<p class="math">Untuk \(t\in T\), kernel \(P_t\) dalam definisi homogenitas disebut <dfn>kernel transisi</dfn>. Dalam keluarga Markov,
\[
P_t(x,A)=\P_x(X_t\in A),\qquad x\in S,\ A\in\mathscr S.
\]</p>
<details>
<summary>Rincian:</summary>
<p>Pada ruang Borel standar, hukum bersyarat reguler dari \(X_t\) jika \(X_0\) diketahui dapat dipilih sebagai kernel terukur. Di bawah satu distribusi awal \(\mu_0\), versi itu hanya ditentukan untuk \(\mu_0\)-hampir setiap \(x\). Rumus untuk semua \(x\), beserta identitas semigrup untuk semua \(x\), memerlukan keluarga Markov \((\P_x)_{x\in S}\) atau versi yang dipilih secara konsisten.</p>
</details>
</div>''',
        "description": "Separate almost-everywhere regular conditional laws from an all-state Markov transition function.",
    },
    {
        "id": "chapman-kolmogorov-kernel-proof",
        "old": r'''<div class="unit" id="trn2">
<p class="math">Misalkan kembali bahwa \( \bs{X} = \{X_t: t \in T\} \) adalah proses Markov pada \( S \) dengan kernel transisi \( \bs{P} = \{P_t: t \in T\} \). Jika \( s, \, s \in T \), maka \( P_s P_t = P_{s + t} \). Artinya,
	\[ P_{s+t}(x, A) = \int_S P_s(x, dy) P_t(y, A), \quad x \in S, \, A \in \mathscr{S} \]</p>
<details>
<summary>Rincian:</summary>
<p>Sifat Markov dan argumen pengondisian merupakan perangkat mendasar. Ingat kembali bahwa \( P_s(x, \cdot) \) adalah distribusi bersyarat dari \( X_s \) dengan syarat \( X_0 = x \), untuk \( x \in S \). Misalkan \( A \in \mathscr{S} \). Pengondisian pada \( X_s \) memberikan
		\[ P_{s+t}(x, A) = \P(X_{s+t} \in A \mid X_0 = x) = \int_S P_s(x, dy) \P(X_{s+t} \in A \mid X_s = y, X_0 = x) \]
		Namun, berdasarkan sifat Markov dan sifat homogen terhadap waktu, 
		\[ \P(X_{s+t} \in A \mid X_s = y, X_0 = x) = \P(X_t \in A \mid X_0 = y) = P_t(y, A) \] Dengan menyubstitusikannya, kita memperoleh
		\[ P_{s+t}(x, A) = \int_S P_s(x, dy) P_t(y, A) = (P_s P_t)(x, A) \]</p>
</details>
</div>''',
        "new": r'''<div class="unit" id="trn2">
<p class="math">Misalkan \(\bs X=\{X_t:t\in T\}\) adalah proses Markov homogen pada \(S\) dengan fungsi transisi \(\bs P=\{P_t:t\in T\}\). Jika \(s,t\in T\), maka \(P_sP_t=P_{s+t}\). Artinya,
\[
P_{s+t}(x,A)=\int_S P_s(x,dy)P_t(y,A),\qquad x\in S,\ A\in\mathscr S.
\]</p>
<details>
<summary>Rincian:</summary>
<p>Di bawah hukum \(\P_x\), sifat Markov dan sifat menara memberikan
\[
P_{s+t}(x,A)=\E_x\!\left[P_t(X_s,A)\right]
=\int_S P_s(x,dy)P_t(y,A).
\]
Penggunaan keluarga \((\P_x)_{x\in S}\) menghindari pengondisian titik demi titik pada kejadian yang mungkin berprobabilitas nol.</p>
</details>
</div>''',
        "description": "Correct the duplicated time variable and prove Chapman-Kolmogorov with the all-state Markov family.",
    },
    {
        "id": "transition-density-positive-time-scope",
        "old": r"Dalam hal ini, kernel transisi \( P_t \) sering memiliki <dfn>kepadatan transisi</dfn> \( p_t \) terhadap \( \lambda \) untuk \( t \in T \). Artinya,",
        "new": r"Untuk waktu \(t\) ketika \(P_t(x,\cdot)\ll\lambda\) bagi setiap \(x\), kernel transisi memiliki <dfn>kepadatan transisi</dfn> \(p_t\) terhadap \(\lambda\). Pada ruang tak-atom, ini biasanya hanya berlaku untuk \(t&gt;0\), sebab \(P_0=I\) tidak mutlak kontinu terhadap \(\lambda\). Artinya,",
        "description": "Do not assume a reference-measure density at time zero or at every time without absolute continuity.",
    },
    {
        "id": "transition-density-composition-scope",
        "old": r"Misalkan \( \lambda \) adalah ukuran acuan pada \( (S, \mathscr{S}) \), dan \( \bs{X} = \{X_t: t \in T\} \) adalah proses Markov pada \( S \) dengan kepadatan transisi \( \{p_t: t \in T\} \). Jika \( s, \, t \in T \), maka \( p_s p_t = p_{s+t} \). Artinya,",
        "new": r"Misalkan \(D\subseteq T\) dan, untuk setiap \(u\in D\), kernel \(P_u\) memiliki kepadatan \(p_u\) terhadap ukuran acuan \(\lambda\). Jika \(s,t,s+t\in D\), maka \(p_s p_t=p_{s+t}\) sebagai kelas kesetaraan hampir di mana-mana. Artinya,",
        "description": "State Chapman-Kolmogorov for exactly the times whose kernels possess reference-measure densities.",
    },
    {
        "id": "transition-density-consequence-scope",
        "old": r"Sebagai akibat langsung, jika \( S \) memiliki ukuran acuan, hubungan dasar yang sama berlaku untuk kepadatan transisi.",
        "new": r"Jika ketiga kernel yang terlibat mutlak kontinu terhadap ukuran acuan, hubungan dasar yang sama berlaku bagi kelas kepadatan transisinya.",
        "description": "Require absolute continuity rather than merely the existence of a reference measure.",
    },
    {
        "id": "transition-density-chapman-kolmogorov",
        "old": r"\[ p_t(x, z) = \int_S p_s(x, y) p_t(y, z) \lambda(dy), \quad x, \, z \in S \]",
        "new": r"\[p_{s+t}(x,z)=\int_Sp_s(x,y)p_t(y,z)\lambda(dy),\quad x,z\in S\] Kesamaan ini berlaku untuk \(\lambda\)-hampir setiap \(z\), kecuali telah dipilih versi kepadatan titik demi titik yang kompatibel.",
        "description": "Put s+t on the left and state the almost-everywhere scope of density identities.",
    },
    {
        "id": "bounded-measurable-function-space",
        "old": r"ruang vektor fungsi linear terbatas \( f: S \to \R \)",
        "new": r"ruang vektor fungsi terbatas dan terukur \(f:S\to\R\)",
        "description": "Describe B as bounded measurable functions, not bounded linear functions.",
    },
    {
        "id": "harmonic-function-domain",
        "old": r"Fungsi terukur \( f: S \to \R \) bersifat <dfn>harmonik</dfn>",
        "new": r"Fungsi \(f\in\mathscr B\) bersifat <dfn>harmonik</dfn>",
        "description": "Keep harmonic functions inside the bounded-function domain of the transition operators.",
    },
    {
        "id": "transition-result-label",
        "old": "Latihan <a class=\"ref\" href=\"#trn4\"></a>",
        "new": "Hasil <a class=\"ref\" href=\"#trn4\"></a>",
        "description": "Refer to the preceding result rather than calling it an exercise.",
    },
    {
        "id": "finite-dimensional-initial-measure",
        "old": r"\int_A P_t(x, B) \mu(dx)",
        "new": r"\int_A P_t(x,B)\mu_0(dx)",
        "description": "Use the declared initial law in the two-time distribution.",
    },
    {
        "id": "finite-dimensional-differential-law",
        "old": r"\( \mu(dx) P_t(x, dy)\)",
        "new": r"\(\mu_0(dx)P_t(x,dy)\)",
        "description": "Use the declared initial law in differential notation.",
    },
    {
        "id": "kolmogorov-construction-standard-borel-scope",
        "old": "Berdasarkan <a href=\"../prob/Processes.html#kol\">teorema konstruksi Kolmogorov</a>, kita mengetahui bahwa <em>terdapat</em> proses stokastik",
        "new": r'''Jika \((S,\mathscr S)\) merupakan ruang Borel standar, <a href="../prob/Processes.html#kol">teorema konstruksi Kolmogorov</a> menjamin bahwa <em>terdapat</em> proses stokastik''',
        "description": "State a standard-Borel hypothesis for Kolmogorov extension.",
    },
    {
        "id": "feller-characterization-time-index",
        "old": r"\( \bs{X} = \{X_t: t \in T\} \) merupakan proses Markov pada ruang keadaan LCCB",
        "new": r"\(\bs X=\{X_t:t\in[0,\infty)\}\) merupakan proses Markov pada ruang keadaan LCCB",
        "description": "Make the process time index agree with its continuous-time semigroup.",
    },
    {
        "id": "feller-semigroup-prose",
        "old": r"<em>semigrup transisi dari transisi</em> \( \bs{P} \) bersifat Feller. Seperti sebelumnya, (a) terpenuhi secara otomatis jika \( S \) diskret, dan (b) terpenuhi secara otomatis jika \( T \) diskret.",
        "new": r"<em>semigrup transisi</em> \(\bs P\) bersifat Feller. Syarat waktu otomatis dalam waktu diskret; syarat pemetaan \(\mathscr C_0\) otomatis hanya pada ruang diskret berhingga dan harus diperiksa pada ruang diskret tak berhingga.",
        "description": "Remove duplicated prose and retain the infinite-discrete C0 qualification.",
    },
    {
        "id": "random-clock-kernel-and-markov-proof",
        "old": r'''<div class="unit" id="enl1">
<p class="math">Misalkan \( \bs{X} = \{X_t: t \in T\} \) adalah proses Markov takhomogen dengan ruang keadaan \( (S, \mathscr{S}) \). Misalkan pula bahwa \( \tau \) adalah peubah acak yang mengambil nilai dalam \( T \), independen dari \( \bs{X} \). Misalkan \( \tau_t = \tau + t \) dan \( Y_t = \left(X_{\tau_t}, \tau_t\right) \) untuk \( t \in T \). Maka \( \bs{Y} = \{Y_t: t \in T\} \) adalah proses Markov homogen dengan ruang keadaan \( (S \times T, \mathscr{S} \otimes \mathscr{T}) \). Untuk \( t \in T \), kernel transisi \( P_t \) diberikan oleh
	\[ P_t[(x, r), A \times B] = \P(X_{r+t} \in A \mid X_r = x) \bs{1}(r + t \in B), \quad (x, r) \in S \times T, \, A \times B \in \mathscr{S} \otimes \mathscr{T} \]</p>
<details>
<summary>Rincian:</summary>
<p>Berdasarkan definisi dan kaidah substitusi,
		\begin{align*}
			\P[Y_{s + t} \in A \times B \mid Y_s = (x, r)] &amp; = \P\left(X_{\tau_{s + t}} \in A, \tau_{s + t} \in B \mid X_{\tau_s} = x, \tau_s = r\right) \\
			&amp; = \P \left(X_{\tau + s + t} \in A, \tau + s + t \in B \mid X_{\tau + s} = x, \tau + s = r\right) \\
			&amp; = \P(X_{r + t} \in A, r + t \in B \mid X_r = x, \tau + s = r)
		\end{align*}
		Namun, \( \tau \) independen dari \( \bs{X} \), sehingga suku terakhir adalah
		\[ \P(X_{r + t} \in A, r + t \in B \mid X_r = x) = \P(X_{r+t} \in A \mid X_r = x) \bs{1}(r + t \in B) \]
		Hal yang penting adalah bahwa ekspresi terakhir tidak bergantung pada \( s \), sehingga \( \bs{Y} \) homogen.</p>
</details>
</div>''',
        "new": r'''<div class="unit" id="enl1">
<p class="math">Misalkan \(\bs X=\{X_t:t\in T\}\) terukur bersama dan merupakan proses Markov takhomogen dengan kernel transisi terukur bersama \(K_{r,u}(x,dy)\), \(r\le u\). Misalkan \(\tau\) bernilai dalam \(T\) dan independen dari \(\bs X\), lalu definisikan \(Y_t=(X_{\tau+t},\tau+t)\). Maka \(\bs Y\) merupakan proses Markov homogen pada \((S\times T,\mathscr S\otimes\mathscr T)\), dengan
\[
P_t((x,r),C)=\int_S\bs1_C(y,r+t)K_{r,r+t}(x,dy),\qquad C\in\mathscr S\otimes\mathscr T.
\]</p>
<details>
<summary>Rincian:</summary>
<p>Untuk \(\mathscr H_s=\sigma(Y_u:u\le s)\), sifat Markov takhomogen dan independensi jam memberi
\[
\E[\bs1_C(Y_{s+t})\mid\mathscr H_s]=P_t(Y_s,C)\quad\text{hampir pasti}.
\]
Ruas kanan hanya bergantung pada keadaan diperluas \(Y_s\), sehingga membuktikan sifat Markov; ketergantungan kernel hanya pada inkremen \(t\) membuktikan homogenitas. Keterukuran bersama menjamin bahwa \(X_{\tau+t}\) dan kernel di atas terukur.</p>
</details>
</div>''',
        "description": "Add joint measurability and kernel hypotheses and prove the Markov property for the random-clock enlargement.",
    },
    {
        "id": "two-step-kernel-hypothesis",
        "old": "Misalkan pula bahwa proses tersebut homogen terhadap waktu dalam arti bahwa",
        "new": r"Misalkan pula bahwa \(Q\) adalah kernel probabilitas yang terukur dalam \((x,y)\), dan proses tersebut homogen terhadap waktu dalam arti bahwa",
        "description": "Require the two-state conditional rule to be a measurable probability kernel.",
    },
    {
        "id": "product-state-space-parenthesis",
        "old": r"\( (S \times S, \mathscr{S} \otimes \mathscr{S} \).",
        "new": r"\((S\times S,\mathscr S\otimes\mathscr S)\).",
        "description": "Close the product measurable-space pair correctly.",
    },
    {
        "id": "product-sigma-algebra-parenthesis",
        "old": r"\( C \in \mathscr{S} \otimes \mathscr{S}) \)",
        "new": r"\(C\in\mathscr S\otimes\mathscr S\)",
        "description": "Remove the extra parenthesis in the product sigma-algebra condition.",
    },
    {
        "id": "finite-memory-positive-length",
        "old": r"untuk suatu \( k \in \N \) tetap",
        "new": r"untuk suatu \(k\in\N_+\) tetap",
        "description": "Require a positive number of remembered states.",
    },
    {
        "id": "deterministic-recurrence-operator",
        "old": r"\( P f(x) = \E[g(X_1) \mid X_0 = x] = f[g(x)] \)",
        "new": r"\(Pf(x)=\E[f(X_1)\mid X_0=x]=f(g(x))\)",
        "description": "Apply the transition operator to f, not to the recurrence map g.",
    },
    {
        "id": "ode-state-domain",
        "old": r"untuk \( s, \, t \in [0, \infty) \) dan \( x \in S \)",
        "new": r"untuk \(s,t\in[0,\infty)\) dan \(x\in\R\)",
        "description": "Use the declared real state space in the deterministic flow example.",
    },
    {
        "id": "ode-feller-c0-argument",
        "old": r"Sifat-sifat Feller merupakan konsekuensi dari kontinuitas \( t \mapsto X_t(x) \) dan kontinuitas \( x \mapsto X_t(x) \). Kontinuitas yang terakhir adalah <em>ketergantungan kontinu pada nilai awal</em>, yang sekali lagi dijamin oleh asumsi pada \( g \).",
        "new": r"Sifat Lipschitz global menghasilkan aliran kontinu \(\phi_t(x)=X_t(x)\) yang proper. Karena itu, \(f\circ\phi_t\in\mathscr C_0\) untuk \(f\in\mathscr C_0\), dan ketergantungan kontinu pada waktu serta nilai awal memberikan kekontinuan kuat di waktu nol.",
        "description": "Justify the C0-preserving Feller property rather than inferring it from pointwise continuity alone.",
    },
    {
        "id": "ode-transition-operator-real-domain",
        "old": r"\( P_t f(x) = f[X_t(x)] \) untuk fungsi terukur \( f: S \to \R \) dan \( x \in S \)",
        "new": r"\(P_t f(x)=f[X_t(x)]\) untuk fungsi terukur \(f:\R\to\R\) dan \(x\in\R\)",
        "description": "Use the real state space declared by the ODE example in the transition-operator formula.",
    },
    {
        "id": "stationary-increments-additive-state-scope",
        "old": r'''<p>Untuk pembahasan berikutnya, kita mempertimbangkan kelas umum proses stokastik yang merupakan proses Markov. Misalkan \( \bs{X} = \{X_t: t \in T\} \) adalah proses acak dengan \( S \subseteq \R\) sebagai himpunan keadaan. Ruang keadaan dapat bersifat diskret (terhitung) atau <q>kontinu</q>. Biasanya, \( S \) adalah \( \N \) atau \( \Z \) dalam kasus diskret, dan \( [0, \infty) \) atau \( \R \) dalam kasus kontinu. Dalam setiap kasus, \( S \) dilengkapi dengan \( \sigma \)-aljabar biasa \( \mathscr{S} \) yang terdiri atas himpunan bagian Borel dari \( S \) (yang merupakan himpunan kuasa dalam kasus diskret). Ruang keadaan \( (S, \mathscr{S}) \) juga memiliki ukuran acuan alami \( \lambda \), yaitu ukuran pencacahan dalam kasus diskret dan ukuran Lebesgue dalam kasus kontinu. Misalkan \( \mathfrak{F} = \{\mathscr{F}_t: t \in T\} \) menyatakan filtrasi alami, sehingga \( \mathscr{F}_t = \sigma\{X_s: s \in T, s \le t\} \) untuk \( t \in T \).</p>''',
        "new": r'''<p>Untuk pembahasan berikutnya, misalkan \(\bs X=\{X_t:t\in T\}\) bernilai dalam himpunan Borel \(S\subseteq\R\) yang tertutup terhadap penjumlahan, dan misalkan setiap inkremen \(X_{s+t}-X_s\) juga bernilai dalam \(S\) hampir pasti. Untuk \(S=\N\) atau \([0,\infty)\), ini merupakan asumsi tambahan bahwa inkremen tidak negatif; untuk \(S=\Z\) atau \(\R\), struktur grup aditif sudah memadai. Gunakan \(\sigma\)-aljabar Borel \(\mathscr S\), ukuran pencacahan atau Lebesgue yang sesuai, dan filtrasi alami \(\mathscr F_t=\sigma\{X_s:s\le t\}\). Asumsi aditif ini membuat ekspresi \(x+y\) dan hukum inkremen di bawah terdefinisi pada ruang keadaan.</p>''',
        "description": "State the additive closure and increment-support assumptions required by the convolution formulas.",
    },
    {
        "id": "increment-density-reference-scope",
        "old": r"Misalkan untuk \( t \in T \) positif, distribusi \( Q_t \) memiliki fungsi kepadatan probabilitas \( g_t \) terhadap ukuran acuan \( \lambda \).",
        "new": r"Misalkan untuk \(t\in T\) positif, \(Q_t\) memiliki kepadatan \(g_t\) terhadap ukuran acuan yang kompatibel dengan translasi; bila perlu, perluas \(g_t\) dengan nol di luar dukungan inkremen.",
        "description": "State the reference-measure and support conditions behind translated densities.",
    },
    {
        "id": "increment-density-semigroup-time-zero-scope",
        "old": r'''Tentu saja, dari <a class="ref" href="#inc4"></a> diperoleh bahwa \( g_s * g_t = g_{s+t} \) untuk \( s, \, t \in T \), dengan \( * \) di sini menyatakan operasi konvolusi pada fungsi kepadatan probabilitas.''',
        "new": r'''Dari <a class="ref" href="#inc2"></a> diperoleh \(Q_s*Q_t=Q_{s+t}\) untuk semua \(s,t\in T\). Jika ketiga ukuran tersebut memiliki kepadatan terhadap ukuran acuan, maka \(g_s*g_t=g_{s+t}\) hampir di mana-mana, dengan \(*\) menyatakan konvolusi.''',
        "description": "State the all-time convolution identity for measures and only assert a density identity when all densities exist.",
    },
    {
        "id": "levy-weak-continuity",
        "old": r'''<div class="unit" id="inc5">
<p class="math">Jika \( Q_t \to Q_0 \) ketika \( t \downarrow 0 \), maka \( \bs{X} \) merupakan proses Markov Feller. </p>
</div>''',
        "new": r'''<div class="unit" id="inc5">
<p class="math">Jika \(T=[0,\infty)\) dan \(Q_t\Rightarrow\delta_0\) secara lemah ketika \(t\downarrow0\), maka semigrup konvolusi yang bersesuaian merupakan semigrup Feller.</p>
</div>''',
        "description": "Specify continuous time and weak convergence to the point mass at zero.",
    },
    {
        "id": "levy-process-convention",
        "old": r"Dengan demikian, berdasarkan teori umum yang diuraikan di atas, \( \bs{X} \) merupakan proses Markov kuat, dan terdapat versi dari \( \bs{X} \) yang kontinu kanan serta memiliki limit kiri. Proses semacam itu dikenal sebagai <dfn>proses Lévy</dfn>, untuk menghormati",
        "new": r"Dalam waktu kontinu, proses yang kontinu secara stokastik, berawal dari \(0\), dan memiliki inkremen stasioner serta independen mempunyai versi càdlàg; versi itu disebut <dfn>proses Lévy</dfn>. Jika \(X_0\) acak dan independen, proses terpusat \(\{X_t-X_0\}\) adalah proses Lévy, sedangkan \(\bs X\) merupakan pergeseran awal independennya. Penamaan ini tidak diterapkan pada gerak acak waktu diskret. Istilah ini menghormati",
        "description": "Use the standard continuous-time, stochastic-continuity, and initial-state convention for Lévy processes.",
    },
    {
        "id": "stationary-increment-moment-regularity",
        "old": r'''<p class="math">Misalkan kembali bahwa \( \bs X \) memiliki inkremen stasioner dan independen.</p>''',
        "new": r'''<p class="math">Misalkan kembali bahwa \(\bs X\) memiliki inkremen stasioner dan independen. Dalam waktu kontinu, asumsikan pula bahwa fungsi rerata atau varians inkremen yang digunakan di bawah kontinu di waktu nol.</p>''',
        "description": "Add the regularity needed to turn continuous-time Cauchy equations into linear functions.",
    },
    {
        "id": "stationary-increment-variance-range",
        "old": r"\( \sigma_0^2 = \var(X_0) \in (0, \infty) \) dan \( \sigma_1^2 = \var(X_1) \in (0, \infty) \)",
        "new": r"\(\sigma_0^2=\var(X_0)\in[0,\infty)\) dan \(\sigma_1^2=\var(X_1)\in[0,\infty)\)",
        "description": "Allow deterministic initial states and increments with zero variance.",
    },
    {
        "id": "stationary-increment-variance-slope",
        "old": r"\( b^2 \in (0, \infty) \)",
        "new": r"\(b^2\in[0,\infty)\)",
        "description": "Allow the zero-variance increment case.",
    },
    {
        "id": "stationary-increment-continuity-explanation",
        "old": r"Hal yang sama berlaku dalam waktu kontinu, dengan asumsi kontinuitas yang telah kita berlakukan pada proses \( \bs X \).",
        "new": r"Hal yang sama berlaku dalam waktu kontinu karena kekontinuan \(m_0\) dan \(v_0\) di waktu nol menyingkirkan solusi aditif Cauchy yang patologis.",
        "description": "Name the precise moment-function regularity used in the continuous-time Cauchy argument.",
    },
    {
        "id": "random-walk-real-state-space",
        "old": r"\[ P(x, A) = Q(A - x), \quad x \in S, \, A \in \mathscr{S} \]",
        "new": r"\[P(x,A)=Q(A-x),\quad x\in\R,\ A\in\mathscr R\]",
        "description": "Use the real state space declared by the partial-sum construction.",
    },
    {
        "id": "random-walk-real-density-domain",
        "old": r"\[ p(x, y) = g(y - x), \quad x, \, y \in S \]",
        "new": r"\[p(x,y)=g(y-x),\quad x,y\in\R\]",
        "description": "Use the real domain for the partial-sum transition density.",
    },
    {
        "id": "random-walk-real-n-step-domain",
        "old": r"\( P^n(x, A) = Q^{*n}(A - x) \) untuk \( x \in S \) dan \( A \in \mathscr{S} \)",
        "new": r"\(P^n(x,A)=Q^{*n}(A-x)\) untuk \(x\in\R\) dan \(A\in\mathscr R\)",
        "description": "Use the real state space consistently in the n-step random-walk kernel.",
    },
    {
        "id": "poisson-transition-support",
        "old": r''' dengan parameter \( t \), dan misalkan \( p_t(x, y) = g_t(y - x) \) untuk \( x, \, y \in \N \). Maka \( \{p_t: t \in [0, \infty)\} \) adalah koleksi kepadatan transisi untuk semigrup Feller pada \( \N \)''',
        "new": r''' dengan parameter \(t\). Definisikan \(g_t(n)=0\) untuk bilangan bulat \(n&lt;0\), dan \(g_0=\delta_0\). Maka \(p_t(x,y)=g_t(y-x)\), \(x,y\in\N\), merupakan keluarga kepadatan transisi semigrup Feller pada \(\N\).''',
        "description": "Define the Poisson mass for negative differences and at time zero.",
    },
    {
        "id": "gaussian-kernel-at-time-zero",
        "old": r''' dengan rerata 0 dan varians \( t \), dan misalkan \( p_t(x, y) = g_t(y - x) \) untuk \( x, \, y \in \R \). Maka \(\{p_t: t \in [0, \infty)\} \) adalah koleksi kepadatan transisi dari semigrup Feller pada \( \R \).''',
        "new": r''' dengan rerata \(0\) dan varians \(t\). Untuk \(t&gt;0\), tetapkan \(P_t(x,dy)=g_t(y-x)\,dy\), serta tetapkan \(P_0=I\). Maka \(\{P_t:t\in[0,\infty)\}\) merupakan semigrup Feller pada \(\R\); kernel identitas \(P_0(x,\cdot)=\delta_x\) tidak memiliki kepadatan terhadap ukuran Lebesgue.''',
        "description": "Represent time zero by the identity kernel rather than a nonexistent Lebesgue density.",
    },
    {
        "id": "gaussian-semigroup-kernel-notation",
        "old": r"Kita hanya perlu menunjukkan bahwa \( \{g_t: t \in [0, \infty)\} \) memenuhi sifat semigrup dan bahwa hasil kontinuitas berlaku. Namun, kita sudah mengetahui bahwa jika \( U, \, V \) adalah peubah independen yang masing-masing berdistribusi normal",
        "new": r"Kita hanya perlu menunjukkan bahwa \(\{P_t:t\in[0,\infty)\}\) memenuhi sifat semigrup dan kontinuitas Feller. Untuk bagian kepadatan pada waktu positif, jika \(U,V\) independen dan masing-masing berdistribusi normal",
        "description": "State the time-zero semigroup in terms of kernels; only positive-time Gaussian members have Lebesgue densities.",
    },
    {
        "id": "stopping-sigma-algebra-localization",
        "old": r"\text{ for all }",
        "new": r"\text{ untuk setiap }",
        "description": "Localize the remaining English quantifier inside the stopping-time sigma-algebra display.",
    },
    {
        "id": "feller-norm-limit-localization",
        "old": r"\text{ as }",
        "new": r"\text{ ketika }",
        "description": "Localize the remaining English limit connector inside the Feller display.",
    },
    {
        "id": "coarser-filtration-arbitrary-stopping-time",
        "old": r"Misalkan \( \tau \) merupakan waktu henti berhingga untuk \( \mathfrak{F} \), serta \( t \in T \) dan \( f \in \mathscr{B} \).",
        "new": r"Misalkan \(\tau\) merupakan waktu henti untuk \(\mathfrak F\), serta \(t\in T\) dan \(f\in\mathscr B\). Pada kejadian \(\{\tau=\infty\}\), gunakan konvensi keadaan kematian dan \(f(\delta)=0\) yang ditetapkan di atas.",
        "description": "Make the proof cover the same possibly infinite stopping times as the stated strong Markov property.",
    },
    {
        "id": "continuous-chain-holding-time-scope",
        "old": "Sifat Markov juga menyiratkan bahwa waktu tinggal dalam suatu keadaan memiliki sifat tanpa memori sehingga harus ber",
        "new": "Untuk rantai homogen waktu kontinu yang reguler, waktu tinggal pada keadaan dengan laju positif memiliki sifat tanpa memori sehingga ber",
        "description": "Qualify the exponential holding-time claim by homogeneity and regularity.",
    },
    {
        "id": "stopping-time-symbol",
        "old": r"maka ( \tau ) juga merupakan waktu henti",
        "new": r"maka \(\tau\) juga merupakan waktu henti",
        "description": "Remove stray parentheses around the stopping time.",
    },
    {
        "id": "stopped-state-notation",
        "old": r"\( \bs{X_\tau} \) terukur terhadap \( \mathscr{F}_\tau \)",
        "new": r"\(X_\tau\) terukur terhadap \(\mathscr F_\tau\)",
        "description": "Use the stopped state rather than the process-vector macro.",
    },
)

MARKOV_DISCRETE_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "positive-probability-history-condition",
        "old": r'''<div class="unit" id="dfn4">
<p class="math">\( \bs{X} = (X_0, X_1, X_2, \ldots) \) adalah rantai Markov jika untuk setiap \( n \in \N \) dan setiap barisan keadaan \( (x_0, x_1, \ldots, x_{n-1}, x,  y) \),
	\[ \P(X_{n+1} = y \mid X_0 = x_0, X_1 = x_1, \ldots, X_{n-1} = x_{n-1}, X_n = x) = \P(X_{n+1} = y \mid X_n = x) \]</p>
</div>''',
        "new": r'''<div class="unit" id="dfn4">
<p class="math">\(\bs X=(X_0,X_1,X_2,\ldots)\) adalah rantai Markov jika, untuk setiap \(n\in\N\), \(y\in S\), dan \((x_0,\ldots,x_n)\in S^{n+1}\) dengan
\[
\P(X_0=x_0,\ldots,X_n=x_n)&gt;0,
\]
berlaku
\[
\P(X_{n+1}=y\mid X_0=x_0,\ldots,X_n=x_n)
=\P(X_{n+1}=y\mid X_n=x_n).
\]</p>
</div>''',
        "description": "Restrict point conditioning to positive-probability histories and make the indexing valid at n=0.",
    },
    {
        "id": "homogeneous-all-state-transition-version",
        "old": r'''<div class="unit" id="dfn5">
<p class="math">Rantai Markov \( \bs{X} = (X_0, X_1, X_2, \ldots) \) <dfn>homogen terhadap waktu</dfn> jika
	\[ \P(X_{n+k} = y \mid X_k = x) = \P(X_n = y \mid X_0 = x) \]
	untuk setiap \( k, \, n \in \N \) dan setiap \( x, \, y \in S \).</p>
</div>''',
        "new": r'''<div class="unit" id="dfn5">
<p class="math">Rantai Markov \(\bs X=(X_0,X_1,X_2,\ldots)\) <dfn>homogen terhadap waktu</dfn> jika terdapat keluarga matriks stokastik \(\{P_n:n\in\N\}\) sedemikian sehingga, untuk setiap \(k,n\in\N\) dan \(y\in S\),
\[
\P(X_{k+n}=y\mid\mathscr F_k)=P_n(X_k,y)\quad\text{hampir pasti},
\qquad P_n(x,y)=\P_x(X_n=y).
\]
Rumus kedua memakai keluarga ukuran peluang Markov \((\P_x)_{x\in S}\), atau versi peluang transisi yang dipilih secara konsisten untuk semua keadaan.</p>
</div>''',
        "description": "Define time homogeneity through a consistent all-state transition family rather than null-event point conditioning.",
    },
    {
        "id": "homogeneous-all-state-process-law-prose",
        "old": r"Artinya, distribusi bersyarat dari \( X_{n+k} \) jika \( X_k = x \) diketahui hanya bergantung pada \( n \). Jadi, jika \( \bs{X} \) homogen (biasanya kata sifat <em>terhadap waktu</em> tidak kita sebutkan), rantai \( \{X_{k+n}: n \in \N\} \) dengan syarat \( X_k = x \) ekuivalen (dalam distribusi) dengan rantai \( \{X_n: n \in \N\} \) dengan syarat \( X_0 = x \).",
        "new": r"Artinya, di bawah keluarga ukuran peluang Markov \((\P_x)_{x\in S}\), hukum rantai setelah waktu \(k\) hanya bergantung pada keadaan saat ini dan selang waktu berikutnya. Jadi, hukum masa depan dari keadaan \(x\) diberikan secara konsisten oleh \(\P_x\), tanpa bergantung pada cara rantai mencapai \(x\).",
        "description": "Explain time homogeneity through the admitted all-state Markov family rather than null-event point conditioning.",
    },
    {
        "id": "homogeneous-all-state-expectation",
        "old": r'''Untuk rantai Markov homogen, jika \( k, \, n \in \N \), \( x \in S \), dan \( f \in \mathscr{B}\), maka
\[ \E[f(X_{k+n}) \mid X_k = x] = \E[f(X_n) \mid X_0 = x] \]''',
        "new": r'''Untuk rantai Markov homogen, jika \(k,n\in\N\) dan \(f\in\mathscr B\), maka, dengan \(P_nf(x)=\E_x[f(X_n)]\),
\[
\E[f(X_{k+n})\mid\mathscr F_k]=P_nf(X_k)\quad\text{hampir pasti}.
\]''',
        "description": "State the homogeneous expectation identity almost surely through the all-state transition operator.",
    },
    {
        "id": "stationary-versus-time-homogeneous-terminology",
        "old": "Istilah <dfn>stasioner</dfn> kadang-kadang digunakan sebagai pengganti homogen.",
        "new": "Sebagian sumber lama memakai istilah <dfn>stasioner</dfn> untuk sifat ini; di sini istilah <em>homogen terhadap waktu</em> dipertahankan agar tidak tertukar dengan stasioneritas distribusi proses.",
        "description": "Distinguish time-homogeneous transitions from stationarity of the process law.",
    },
    {
        "id": "nonhomogeneous-enlargement-cardinality",
        "old": "tetapi dengan konsekuensi terciptanya ruang keadaan yang tak terhitung.",
        "new": r"tetapi dengan konsekuensi memperbesar ruang keadaan menjadi \(S\times\N\), yang tetap terhitung jika \(S\) terhitung.",
        "description": "The product of two countable discrete state spaces remains countable.",
    },
    {
        "id": "hitting-time-proof-domains",
        "old": r'''<p>Untuk \( n \in \N \)</p>
<ol class="sub">
<li>\(\{\rho_A = n\} = \{X_0 \notin A, X_1 \notin A, \ldots, X_{n-1} \notin A, X_n \in A\} \in \mathscr{F}_n\)</li>
<li>\(\{\tau_A = n\} = \{X_1 \notin A, X_2 \notin A, \ldots, X_{n-1} \notin A, X_n \in A\} \in \mathscr{F}_n\)</li>
</ol>''',
        "new": r'''<p>Dengan konvensi bahwa irisan kosong sama dengan \(\Omega\),</p>
<ol class="sub">
<li>\(\{\rho_A=n\}=\bigcap_{j=0}^{n-1}\{X_j\notin A\}\cap\{X_n\in A\}\in\mathscr F_n\) untuk \(n\in\N\).</li>
<li>\(\{\tau_A=n\}=\bigcap_{j=1}^{n-1}\{X_j\notin A\}\cap\{X_n\in A\}\in\mathscr F_n\) untuk \(n\in\N_+\).</li>
</ol>''',
        "description": "State both entrance-time events without an invalid X_{-1} term and exclude n=0 from first-positive hitting.",
    },
    {
        "id": "last-visit-supremum-and-infinity",
        "old": r'''\[ \zeta_A = \max\{n \in \N_+: X_n \in A\} \]
Kita tidak dapat menentukan apakah \( \zeta_A = n \) tanpa melihat ke masa depan: \( \{ \zeta_A = n\} = \{X_n \in A, X_{n+1} \notin A, X_{n+2} \notin A, \ldots\} \) untuk \( n \in \N \).''',
        "new": r'''\[\zeta_A=\sup\bigl(\{n\in\N_+:X_n\in A\}\cup\{0\}\bigr)\in\N\cup\{\infty\}.\]
Kita tidak dapat menentukan \(\zeta_A\) tanpa melihat ke masa depan. Untuk \(n\in\N_+\),
\[\{\zeta_A=n\}=\{X_n\in A,X_{n+1}\notin A,X_{n+2}\notin A,\ldots\},\]
sedangkan \(\{\zeta_A=0\}=\{X_1\notin A,X_2\notin A,\ldots\}\).''',
        "description": "Define the last visit for zero or infinitely many positive visits and state its events on the correct domains.",
    },
    {
        "id": "stopping-sigma-field-display-language",
        "old": r"\[ \mathscr{F}_\tau = \{A \in \mathscr{F}: A \cap \{\tau = n\} \in \mathscr{F}_n \text{ for all } n \in \N\} \]",
        "new": r"\[\mathscr F_\tau=\{A\in\mathscr F:A\cap\{\tau=n\}\in\mathscr F_n\ \text{untuk semua }n\in\N\}.\]",
        "description": "Localize the prose retained inside the source formula.",
    },
    {
        "id": "strong-markov-homogeneous-introduction",
        "old": "Untuk rantai Markov waktu diskret, sifat Markov biasa menyiratkan sifat Markov kuat.",
        "new": "Untuk rantai Markov waktu diskret yang homogen, sifat Markov biasa menyiratkan sifat Markov kuat.",
        "description": "State the time-homogeneity hypothesis needed for a future law depending only on the stopped state.",
    },
    {
        "id": "strong-markov-homogeneous-kernel-form",
        "old": r'''<div class="unit" id="str2">
<p class="math">Jika \( \bs{X} = (X_0, X_1, X_2, \ldots) \) adalah rantai Markov waktu diskret, maka \( \bs{X} \) memiliki sifat Markov kuat. Artinya, jika \( \tau \) adalah waktu henti berhingga bagi \( \bs{X} \), maka</p>
<ol class="sub">
<li>\( \P(X_{\tau+k} = x \mid \mathscr{F}_\tau) = \P(X_{\tau+k} = x \mid X_\tau) \) untuk setiap \(  k \in \N \) dan \( x \in S \).</li>
<li>\( \E[f(X_{\tau+k}) \mid \mathscr{F}_\tau] = \E[f(X_{\tau+k}) \mid X_\tau] \) untuk setiap \( k \in \N \) dan \( f \in \mathscr{B} \).</li>
</ol>
</div>''',
        "new": r'''<div class="unit" id="str2">
<p class="math">Jika \(\bs X=(X_0,X_1,X_2,\ldots)\) adalah rantai Markov waktu diskret homogen dengan matriks transisi \(k\)-langkah \(P_k\), maka \(\bs X\) memiliki sifat Markov kuat. Jika \(\tau\) adalah waktu henti berhingga bagi \(\bs X\), maka</p>
<ol class="sub">
<li>\(\P(X_{\tau+k}=x\mid\mathscr F_\tau)=P_k(X_\tau,x)\) untuk setiap \(k\in\N\) dan \(x\in S\).</li>
<li>\(\E[f(X_{\tau+k})\mid\mathscr F_\tau]=P_kf(X_\tau)\) untuk setiap \(k\in\N\) dan \(f\in\mathscr B\).</li>
</ol>
</div>''',
        "description": "State the strong Markov property for homogeneous chains using the consistent transition family.",
    },
    {
        "id": "strong-markov-all-state-future-law-prose",
        "old": r"Dengan mengasumsikan homogenitas seperti biasa, rantai Markov \( \{X_{\tau + n}: n \in \N\} \) dengan syarat \( X_\tau = x \) ekuivalen dalam distribusi dengan rantai \( \{X_n: n \in \N\} \) dengan syarat \( X_0 = x \).",
        "new": r"Dengan mengasumsikan homogenitas seperti biasa, untuk setiap \(x\in S\), hukum masa depan rantai setelah \(\tau\), ketika \(X_\tau=x\), diberikan oleh hukum semua-keadaan \(\P_x\) dari \((X_n)_{n\in\N}\). Di bawah hukum semula, identitas bersyarat sebagai fungsi dari \(X_\tau\) berlaku hampir pasti; keluarga \((\P_x)_{x\in S}\) menetapkan versinya secara konsisten untuk semua \(x\).",
        "description": "Carry the all-state Markov family through the post-stopping-time explanatory prose.",
    },
    {
        "id": "transition-matrix-all-state-definition",
        "old": r'''<div class="unit" id="trn1">
<p class="math">Untuk \( n \in \N \), misalkan
	\[ P_n(x, y) = \P(X_n = y \mid X_0 = x), \quad (x, y) \in S \times S \]
	Matriks \( P_n \) adalah <dfn>matriks probabilitas transisi</dfn> \( n \) langkah bagi \( \bs{X} \). </p>
</div>''',
        "new": r'''<div class="unit" id="trn1">
<p class="math">Untuk \(n\in\N\), misalkan
\[
P_n(x,y)=\P_x(X_n=y),\qquad(x,y)\in S\times S.
\]
Matriks \(P_n\) adalah <dfn>matriks probabilitas transisi</dfn> \(n\) langkah bagi \(\bs X\).</p>
</div>''',
        "description": "Define every transition row through the admitted all-state Markov family.",
    },
    {
        "id": "transition-matrix-all-state-kernel-prose",
        "old": r'''<p>Dengan demikian, \( y \mapsto P_n(x, y) \) adalah fungsi kepadatan probabilitas dari \( X_n \) jika \( X_0 = x \) diketahui. Secara khusus, \( P_n \) adalah <dfn>matriks probabilitas</dfn> (atau <dfn>matriks stokastik</dfn>) karena \( P_n(x, y) \ge 0 \) untuk \( (x, y) \in S^2 \) dan \( \sum_{y \in S} P(x, y) = 1 \) untuk \( x \in S \). Seperti setiap matriks nonnegatif pada \( S \), \( P_n \) mendefinisikan kernel pada \( S \) untuk \( n \in \N \):
\[ P_n(x, A) = \sum_{y \in A} P_n(x, y) = \P(X_n \in A \mid X_0 = x), \quad x \in S, \, A \subseteq S \]
Jadi, \( A \mapsto P_n(x, A) \) adalah distribusi probabilitas dari \( X_n \) jika \( X_0 = x \) diketahui.''',
        "new": r'''<p>Dengan demikian, \(y\mapsto P_n(x,y)\) adalah fungsi kepadatan probabilitas \(X_n\) di bawah \(\P_x\). Secara khusus, \(P_n\) adalah <dfn>matriks probabilitas</dfn> (atau <dfn>matriks stokastik</dfn>) karena \(P_n(x,y)\ge0\) untuk \((x,y)\in S^2\) dan \(\sum_{y\in S}P_n(x,y)=1\) untuk \(x\in S\). Seperti setiap matriks nonnegatif pada \(S\), \(P_n\) mendefinisikan kernel pada \(S\) untuk \(n\in\N\):
\[
P_n(x,A)=\sum_{y\in A}P_n(x,y)=\P_x(X_n\in A),
\qquad x\in S,\ A\subseteq S.
\]
Jadi, \(A\mapsto P_n(x,A)\) adalah distribusi probabilitas \(X_n\) di bawah \(\P_x\).''',
        "description": "Carry the all-state convention through transition rows, row sums, and kernel notation.",
    },
    {
        "id": "transition-distribution-proof-reference",
        "old": r'dari definisi <a class="ref" href="#trn4"></a> dan argumen pengondisian.',
        "new": r'dari <a class="ref" href="#trn3">identitas operator transisi</a> dan hukum probabilitas total.',
        "description": "Cite the P_n=P^n operator identity used by the distribution-propagation proof.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "chapman-kolmogorov-all-state-proof",
        "old": r'''<details>
<summary>Rincian:</summary>
<p>Hal ini mengikuti dari sifat Markov dan sifat homogen terhadap waktu serta argumen pengondisian dasar. Jika \( x, \, z \in S \), maka
		\[ P_{m+n}(x, z) = \P(X_{m+n} = z \mid X_0 = x) = \sum_{y \in S} \P(X_{m+n} = z \mid X_0 = x, X_m = y) \P(X_m = y \mid X_0 = x) \]
		Namun, berdasarkan sifat Markov dan sifat homogen terhadap waktu,
		\[ \P(X_{m+n} = z \mid X_0 = x, X_m = y) = \P(X_n = z \mid X_0 = y) = P_n(y, z) \]
		Tentu saja, \( \P(X_m = y \mid X_0 = x) = P_m(x, y) \) juga berlaku.
		Karena itu,
		\[ P_{m+n}(x, z) = \sum_{y \in S} P_m(x, y) P_n(y, z) \]
		Ruas kanan, berdasarkan definisi, adalah \( P_m P_n(x, z) \).</p>
</details>''',
        "new": r'''<details>
<summary>Rincian:</summary>
<p>Ambil \(x,z\in S\). Di bawah \(\P_x\), sifat Markov dan homogenitas waktu memberikan
\[
\P_x(X_{m+n}=z\mid\mathscr F_m)=P_n(X_m,z)
\quad\text{hampir pasti}.
\]
Karena itu, sifat menara menghasilkan
\[
\begin{aligned}
P_{m+n}(x,z)
&amp;=\E_x\!\left[P_n(X_m,z)\right]\\
&amp;=\sum_{y\in S}P_m(x,y)P_n(y,z)
=(P_mP_n)(x,z).
\end{aligned}
\]</p>
</details>''',
        "description": "Prove Chapman-Kolmogorov under P_x without conditioning on zero-probability state events.",
    },
    {
        "id": "transition-operator-all-state-expectation",
        "old": r'''<div class="unit" id="trn3">
<p class="math">Misalkan \( n \in \N \) dan \( f: S \to \R \). Maka, dengan mengasumsikan bahwa nilai harapannya ada,
	\[ P^n f(x) = \sum_{y \in S} P^n(x, y) f(y) = \E[f(X_n) \mid X_0 = x], \quad x \in S \]</p>
<details>
<summary>Rincian:</summary>
<p>Hal ini langsung mengikuti dari definisi:
		\[ P^nf(x) = \sum_{y \in S} P^n(x, y) f(y) = \sum_{y \in S} \P(X_n = y \mid X_0 = x) f(y) = \E[f(X_n) \mid X_0 = x], \quad x \in S\]</p>
</details>
</div>''',
        "new": r'''<div class="unit" id="trn3">
<p class="math">Misalkan \(n\in\N\) dan \(f:S\to\R\). Jika nilai harapannya ada, maka
\[
P^nf(x)=\sum_{y\in S}P^n(x,y)f(y)=\E_x[f(X_n)],
\qquad x\in S.
\]</p>
<details>
<summary>Rincian:</summary>
<p>Hal ini langsung mengikuti dari definisi:
\[
P^nf(x)=\sum_{y\in S}\P_x(X_n=y)f(y)=\E_x[f(X_n)],
\qquad x\in S.
\]</p>
</details>
</div>''',
        "description": "Express the n-step transition operator through expectations under the all-state laws P_x.",
    },
    {
        "id": "transition-result-label-and-fragment",
        "old": r'dari latihan <a class="ref" href="https://www.randomservices.org/random/markov/trn5"></a> diperoleh',
        "new": r'dari <a class="ref" href="#trn5">hasil sebelumnya</a> diperoleh',
        "description": "Label the statement as a result and repair the missing hash in its fragment link.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "transition-distribution-all-state-mixture",
        "old": r'''\[ \P(X_n = y) = \sum_{x \in S} \P(X_0 = x) \P(X_n = y \mid X_0 = x) = \sum_{x \in S} f(x) P^n(x, y) = f P^n(y), \quad y \in S \]''',
        "new": r'''\[
\P(X_n=y)=\sum_{x\in S}f(x)P^n(x,y)=fP^n(y),
\qquad y\in S.
\]''',
        "description": "Propagate the initial distribution by its mixture of all-state transition laws, without null-event conditioning.",
    },
    {
        "id": "finite-dimensional-state-tuple-power",
        "old": r"\( (x_0, x_1, \ldots, x_n) \in S^n, \)",
        "new": r"\((x_0,x_1,\ldots,x_n)\in S^{n+1}\)",
        "description": "Place an (n+1)-tuple in the correct Cartesian power and remove the stray comma.",
    },
    {
        "id": "finite-dimensional-chain-reflow",
        "old": r"""\[ \P(X_0 = x_0, X_1 = x_1, \ldots, X_n = x_n) = f_0(x_0) P(x_0, x_1) P(x_1, x_2) \cdots P(x_{n-1},x_n) \]""",
        "new": r"""\[
\begin{aligned}
&amp;\P(X_0=x_0,X_1=x_1,\ldots,X_n=x_n)\\
&amp;\qquad=f_0(x_0)P(x_0,x_1)P(x_1,x_2)\cdots P(x_{n-1},x_n).
\end{aligned}
\]""",
        "description": "Reflow the finite-dimensional product law for readable narrow-screen rendering.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "finite-dimensional-tower-proof",
        "old": (r'''		\[ \P(X_0 = x_0, X_1 = x_1, \ldots, X_n = x_n) = \P(X_0 = x_0) \P(X_1 = x_1 \mid X_0 = x_0) \P(X_2 = x_2 \mid X_0 = x_0, X_1 = x_1) \cdots \P(X_n = x_n \mid X_0 = x_0, \ldots, X_{n-1} = x_{n-1}) \]
		Namun, berdasarkan sifat Markov, pernyataan ini menyederhana menjadi
		\begin{align*}
			\P(X_0 = x_0, X_1 = x_1, \ldots, X_n = x_n) &amp; = \P(X_0 = x_0) \P(X_1 = x_1 \mid X_0 = x_0) \P(X_2 = x_2 \mid X_1 = x_1) \cdots \P(X_n = x_n \mid X_{n-1} = x_{n-1}) \\
			&amp; = f_0(x_0) P(x_0, x_1) P(x_1, x_2) \cdots P(x_{n-1}, x_n)''' + " \n" + r'''		\end{align*}'''),
        "new": r'''Kasus \(n=0\) langsung. Untuk \(n\in\N_+\), tetapkan \(A_j=\{X_j=x_j\}\). Sifat menara dan sifat Markov memberikan
\[
\begin{aligned}
\P(A_0\cap\cdots\cap A_n)
&amp;=\E\!\left[\bs1_{A_0\cap\cdots\cap A_{n-1}}
\E(\bs1_{A_n}\mid\mathscr F_{n-1})\right]\\
&amp;=\E\!\left[\bs1_{A_0\cap\cdots\cap A_{n-1}}
P(X_{n-1},x_n)\right].
\end{aligned}
\]
Dengan mengulangi langkah ini diperoleh
\[
\P(A_0\cap\cdots\cap A_n)
=f_0(x_0)\prod_{j=1}^{n}P(x_{j-1},x_j).
\]''',
        "description": "Prove the finite-dimensional law by tower recursion rather than a chain rule over potentially null histories.",
    },
    {
        "id": "potential-definition-entries",
        "old": r"\[ R_\alpha = \sum_{n=0}^\infty \alpha^n P^n, \quad (x, y) \in S^2 \]",
        "new": r"\[R_\alpha(x,y)=\sum_{n=0}^\infty\alpha^nP^n(x,y),\qquad(x,y)\in S^2.\]",
        "description": "Attach the entrywise state domain to an entrywise potential-matrix definition.",
    },
    {
        "id": "potential-visit-count-reflow",
        "old": r"""\[ R(x, y) = \sum_{n=0}^\infty P^n(x, y) = \sum_{n=0}^\infty \E[\bs{1}(X_n = y) \mid X_0 = x] = \E\left( \sum_{n=0}^\infty \bs{1}(X_n = y) \biggm| X_0 = x\right) = \E[\#\{n \in \N: X_n = y\} \mid X_0 = x] \]""",
        "new": r"""\[
\begin{aligned}
R(x,y)
&amp;=\sum_{n=0}^\infty P^n(x,y)
=\sum_{n=0}^\infty\E_x[\bs1(X_n=y)]\\
&amp;=\E_x\!\left[\sum_{n=0}^\infty\bs1(X_n=y)\right]
=\E_x[\#\{n\in\N:X_n=y\}].
\end{aligned}
\]""",
        "description": "Reflow the visit-count identity and express it under the all-state law P_x.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "potential-set-visits-conditioning",
        "old": r"\E\left[\sum_{n=0}^\infty \bs{1}(X_n \in A)\right]",
        "new": r"\E_x\left[\sum_{n=0}^\infty\bs{1}(X_n\in A)\right]",
        "description": "Take the expected number of visits under the all-state law P_x.",
    },
    {
        "id": "random-time-all-state-geometric-mixture",
        "old": r'''<div class="unit" id="pot3">
<p class="math">Jika \( \alpha \in (0, 1) \), maka \( (1 - \alpha) R_\alpha(x, y) = \P(X_N = y \mid X_0 = x) \) untuk \( (x, y) \in S^2 \), dengan \( N \) independen dari \( \bs{X} \) dan memiliki distribusi geometrik pada \( \N \) dengan parameter \( 1 - \alpha \).</p>
<details>
<summary>Rincian:</summary>
<p>Misalkan \( (x, y) \in S^2 \). Pengondisian terhadap \( N \) memberikan
		\[ \P(X_N = y \mid X_0 = x) = \sum_{n=0}^\infty \P(N = n) \P(X_N = y \mid X_0 = x, N = n) \]
		Namun, berdasarkan aturan substitusi dan asumsi independensi,
		\[ \P(X_N = y \mid N = n, X_0 = x) = \E(X_n = y \mid N = n, X_0 = x) = \P(X_n = y \mid X_0 = x) = P^n (x, y) \]
		Karena \( N \) memiliki distribusi geometrik pada \( N \) dengan parameter \( 1 - \alpha \), kita memperoleh \( \P(N = n) = (1 - \alpha) \alpha^n \). Karena itu,
		\[ \P(X_N = y \mid X_0 = x) = \sum_{n=0}^\infty (1 - \alpha) \alpha^n P^n(x, y) = (1 - \alpha) R_\alpha(x, y) \]</p>
</details>
</div>''',
        "new": r'''<div class="unit" id="pot3">
<p class="math">Jika \(\alpha\in(0,1)\), maka
\[
(1-\alpha)R_\alpha(x,y)=\P_x(X_N=y),\qquad(x,y)\in S^2,
\]
dengan \(N\) independen dari \(\bs X\) di bawah setiap \(\P_x\) dan berdistribusi geometrik pada \(\N\) dengan parameter \(1-\alpha\).</p>
<details>
<summary>Rincian:</summary>
<p>Ambil \((x,y)\in S^2\). Dengan mengondisikan pada \(N\) dan memakai independensi,
\[
\P_x(X_N=y)=\sum_{n=0}^\infty\P(N=n)\P_x(X_N=y\mid N=n)
=\sum_{n=0}^\infty\P(N=n)\P_x(X_n=y).
\]
Karena \(\P(N=n)=(1-\alpha)\alpha^n\), diperoleh
\[
\P_x(X_N=y)=\sum_{n=0}^\infty(1-\alpha)\alpha^nP^n(x,y)
=(1-\alpha)R_\alpha(x,y).
\]</p>
</details>
</div>''',
        "description": "State the geometric-time mixture under each P_x and remove null-event and event-expectation notation.",
    },
    {
        "id": "discount-factor-name",
        "old": r"sehingga \( \alpha \) adalah <dfn>faktor inflasi</dfn> (kadang-kadang juga disebut <dfn>faktor diskonto</dfn>)",
        "new": r"sehingga \(\alpha\) adalah <dfn>faktor diskonto</dfn>",
        "description": "Use the standard economic name for a present-value multiplier below one.",
    },
    {
        "id": "potential-product-reflow",
        "old": r"""\[R_\alpha R_\beta = \sum_{m=0}^\infty \alpha^m P^m R_\beta = \sum_{m=0}^\infty \alpha^m P^m \left(\sum_{n=0}^\infty \beta^n P^n\right) = \sum_{m=0}^\infty \sum_{n=0}^\infty \alpha^m \beta^n P^m P^n = \sum_{m=0}^\infty \sum_{n=0}^\infty \alpha^m \beta^n P^{m+n}\]""",
        "new": r"""\[
\begin{aligned}
R_\alpha R_\beta
&amp;=\sum_{m=0}^\infty\alpha^mP^mR_\beta
=\sum_{m=0}^\infty\alpha^mP^m\!\left(\sum_{n=0}^\infty\beta^nP^n\right)\\
&amp;=\sum_{m=0}^\infty\sum_{n=0}^\infty\alpha^m\beta^nP^mP^n
=\sum_{m=0}^\infty\sum_{n=0}^\infty\alpha^m\beta^nP^{m+n}.
\end{aligned}
\]""",
        "description": "Reflow the double-series product for readable narrow-screen rendering.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "resolvent-beta-symbol",
        "old": r"\alpha^j q^k P^{j+k}",
        "new": r"\alpha^j\beta^kP^{j+k}",
        "description": "Replace the undefined q by the declared parameter beta.",
    },
    {
        "id": "resolvent-geometric-reflow",
        "old": r"""\[ R_\alpha R_\beta = \sum_{n=0}^\infty \sum_{k=0}^n \alpha^{n-k} \beta^k P^n = \sum_{n=0}^\infty  \sum_{k=0}^n \left(\frac{\beta}{\alpha}\right)^k \alpha^n P^n = \sum_{n=0}^\infty \frac{1 - \left(\frac{\beta}{\alpha}\right)^{n+1}}{1 - \frac{\beta}{\alpha}} \alpha^n P^n \]""",
        "new": r"""\[
\begin{aligned}
R_\alpha R_\beta
&amp;=\sum_{n=0}^\infty\sum_{k=0}^n\alpha^{n-k}\beta^kP^n\\
&amp;=\sum_{n=0}^\infty\sum_{k=0}^n
\left(\frac{\beta}{\alpha}\right)^k\alpha^nP^n\\
&amp;=\sum_{n=0}^\infty
\frac{1-(\beta/\alpha)^{n+1}}{1-\beta/\alpha}\alpha^nP^n.
\end{aligned}
\]""",
        "description": "Reflow the finite geometric-sum reduction for readable narrow-screen rendering.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "potential-shift-reference",
        "old": r'Dari <a class="ref" href="#pot6"></a>,',
        "new": r'Dari <a class="ref" href="#pot1">definisi matriks potensial</a>,',
        "description": "Cite the defining series used by the shift identity.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "potential-result-label",
        "old": r'Latihan <a class="ref" href="#pot8"></a> sekali lagi menunjukkan',
        "new": r'<a class="ref" href="#pot8">Hasil sebelumnya</a> sekali lagi menunjukkan',
        "description": "Label the proved inverse relation as a result and supply visible reference text.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "sampling-index-origin",
        "old": r"\( 0 \lt n_1 \lt n_2 \lt \cdots \) dalam \( \N \)",
        "new": r"\(0=n_0\lt n_1\lt n_2\lt\cdots\) dalam \(\N\)",
        "description": "Define n_0 before using Y_0=X_{n_0}.",
    },
    {
        "id": "restricted-matrix-positive-time",
        "old": r'''<p class="math">Jika \( A \) adalah himpunan bagian tak kosong dari \( S \), maka untuk \( n \in \N \),
	\[ P_A^n(x, y) = \P(X_1 \in A, X_2 \in A, \ldots, X_{n-1} \in A, X_n = y \mid X_0 = x), \quad (x, y) \in A \times A \]</p>''',
        "new": r'''<p class="math">Jika \(A\) adalah himpunan bagian tak kosong dari \(S\), maka \(P_A^0=I_A\), dan untuk \(n\in\N_+\), dengan irisan kosong ditafsirkan sebagai \(\Omega\),
\[
P_A^n(x,y)=\P_x\!\left(\bigcap_{j=1}^{n-1}\{X_j\in A\}\cap\{X_n=y\}\right),
\qquad(x,y)\in A\times A.
\]</p>''',
        "description": "Separate zero time and express the positive-time restricted law under P_x with an empty-intersection convention at n=1.",
    },
    {
        "id": "finite-chain-exercise-all-state-probability",
        "old": r"\( \P(X_1 = a, X_2 = b, X_3 = c \mid X_0 = a) \)",
        "new": r"\(\P_a(X_1=a,X_2=b,X_3=c)\)",
        "description": "State the finite-chain path probability under the all-state law starting at a.",
    },
    {
        "id": "finite-chain-exercise-all-state-expectation",
        "old": r"\( \E[g(X_2) \mid X_0 = x] \)",
        "new": r"\(\E_x[g(X_2)]\)",
        "description": "State the finite-chain expectation under the all-state law P_x.",
    },
    {
        "id": "random-walk-all-state-kernel-proof",
        "old": r'''<p>Sekali lagi, misalkan \( \mathscr{F}_n = \sigma\{X_0, X_1, \ldots, X_n\} \) untuk \( n \in \N \). Maka \( \mathscr{F}_n = \sigma\{Y_0, Y_1, \ldots, Y_n\} \) juga berlaku untuk \( n \in \N \). Karena itu,
		\[ \P(Y_{n+1} = y \mid \mathscr{F}_n) = \P(Y_n + X_{n+1} = y \mid \mathscr{F}_n) = \P(Y_n + X_{n+1} = y \mid Y_n), \quad y \in \Z \]
		karena barisan \( \bs{X} \) independen. Secara khusus,
		\[ \P(Y_{n+1} = y \mid Y_n = x) = \P(x + X_{n+1} = y \mid Y_n = x) = \P(X_{n+1} = y - x) = f(y - x), \quad (x, y) \in \Z^2 \]</p>''',
        "new": r'''<p>Sekali lagi, misalkan \(\mathscr F_n=\sigma\{X_0,X_1,\ldots,X_n\}=\sigma\{Y_0,Y_1,\ldots,Y_n\}\). Karena \(X_{n+1}\) independen dari \(\mathscr F_n\), untuk \(y\in\Z\),
\[
\P(Y_{n+1}=y\mid\mathscr F_n)
=\P(X_{n+1}=y-Y_n\mid\mathscr F_n)
=f(y-Y_n)=Q(Y_n,y)
\quad\text{hampir pasti},
\]
dengan kernel yang dipilih untuk semua \((x,y)\in\Z^2\) oleh \(Q(x,y)=f(y-x)\).</p>''',
        "description": "Prove the random-walk kernel almost surely and define every row without null-event point conditioning.",
    },
    {
        "id": "visible-doubly-stochastic-reference",
        "old": r'<a class="ref" href="#dbl4"></a>',
        "new": r'<a class="ref" href="#dbl4">latihan sebelumnya</a>',
        "description": "Supply visible, accessible fallback text for the doubly stochastic example reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "two-state-potential-matrix",
        "old": r"""\[ R_\alpha = \frac{1}{(p + q)(1 - \alpha)} \left[\begin{matrix} q &amp; p \\ q &amp; p \\ \end{matrix}\right] + \frac{1}{(p + q)^2 (1 - \alpha)} \left[\begin{matrix} p &amp; -p \\ -q &amp; q \end{matrix}\right] \]""",
        "new": r"""\[
R_\alpha=
\frac{1}{(p+q)(1-\alpha)}
\begin{bmatrix}q&amp;p\\q&amp;p\end{bmatrix}
+
\frac{1}{(p+q)\,[1-\alpha(1-p-q)]}
\begin{bmatrix}p&amp;-p\\-q&amp;q\end{bmatrix}.
\]""",
        "description": "Replace the incorrect resolvent; the corrected spectral decomposition equals (I-alpha P)^(-1) and satisfies R_0=I.",
    },
    {
        "id": "limiting-link-case",
        "old": r'href="https://www.randomservices.org/random/markov/limiting.html"',
        "new": r'href="https://www.randomservices.org/random/markov/Limiting.html"',
        "description": "Repair the case-sensitive selected-page URL.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "random-walk-integer-symbol",
        "old": r"\( x \in Z \)",
        "new": r"\(x\in\Z\)",
        "description": "Use the declared integer-set macro.",
    },
    {
        "id": "doubly-stochastic-state-symbol",
        "old": r"\sum_{u \in s} P(u, y)",
        "new": r"\sum_{u\in S}P(u,y)",
        "description": "Use the declared state-space symbol in the column-sum condition.",
    },
    {
        "id": "doubly-stochastic-potential-alpha-symbol",
        "old": r"""\left[\begin{matrix} 4 - 4 a + a^2 &amp; 2 a - a^2 &amp; a^2 \\ a^2 &amp; 4 - 4 a + a^2 &amp; 2 a - a^2 \\ 2 a - a^2 &amp; a^2 &amp; 4 - 4 a + a^2 \end{matrix}\right]""",
        "new": r"""\left[\begin{matrix} 4-4\alpha+\alpha^2 &amp; 2\alpha-\alpha^2 &amp; \alpha^2 \\ \alpha^2 &amp; 4-4\alpha+\alpha^2 &amp; 2\alpha-\alpha^2 \\ 2\alpha-\alpha^2 &amp; \alpha^2 &amp; 4-4\alpha+\alpha^2 \end{matrix}\right]""",
        "description": "Replace the undefined scalar a by alpha throughout the verified potential matrix.",
    },
)

MARKOV_RECURRENCE_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "all-state-markov-family",
        "old": r"""Jadi, berdasarkan definisi,""" + " \n" + r"""\[ P(x, y) = \P(X_{n+1} = y \mid X_n = x) \]
untuk \( x, \, y \in S \) dan \( n \in \N \).""",
        "new": r"""Untuk membahas semua keadaan—termasuk keadaan yang mungkin berpeluang nol di bawah \(\P\)—pilih keluarga hukum Markov \((\P_x)_{x\in S}\) dengan \(\P_x(X_0=x)=1\), dan tulis \(\E_x\) untuk nilai harapannya. Tetapkan
\[
P(x,y)=\P_x(X_1=y),\qquad
P^n(x,y)=\P_x(X_n=y),\qquad x,y\in S,\ n\in\N.
\]
Pada halaman ini, ungkapan \(\P(\,cdot\mid X_0=x)\) dan \(\E(\,cdot\mid X_0=x)\) selanjutnya merupakan notasi singkat untuk \(\P_x\) dan \(\E_x\).""",
        "description": "Bind every state, including null states under an ambient law, to a consistent all-state Markov family.",
    },
    {
        "id": "hitting-event-empty-intersection",
        "old": r"""\[ \{\tau_A = n\} = \{X_1 \notin A, \ldots, X_{n-1} \notin A, X_n \in A\} \]""",
        "new": r"""\[
\{\tau_A=n\}
=\bigcap_{j=1}^{n-1}\{X_j\notin A\}\cap\{X_n\in A\},
\qquad n\in\N_+,
\]
dengan konvensi bahwa irisan kosong sama dengan \(\Omega\).""",
        "description": "State the first-positive hitting event for n=1 without a nonexistent list of prior coordinates.",
    },
    {
        "id": "first-hit-convolution-proof",
        "old": r"""<p>Hasil ini diperoleh dengan mengondisikan pada \( \tau_y \). Jika rantai dimulai pada keadaan \( x \), rantai berada pada keadaan \( y \) pada waktu \( n \) jika dan hanya jika rantai mencapai \( y \) untuk pertama kalinya pada suatu waktu sebelumnya \( k \), lalu kembali ke \( y \) dalam \( n - k \) langkah sisanya. Secara lebih formal,
		\[ P^n(x, y) = \P(X_n = y \mid X_0 = x) = \sum_{k=0}^\infty \P(X_n = y \mid \tau_y = k, X_0 = x) \P(\tau_y = k \mid X_0 = x) \]
		Namun, kejadian \( \tau_y = k \) menyiratkan \( X_k = y \) dan termasuk dalam \( \mathscr{F}_k \). Karena itu, berdasarkan sifat Markov,
		\[ \P(X_n = y \mid \tau_y = k, X_0 = x) = \P(X_n = y \mid X_k = y, \tau_y = k, X_0 = x) = \P(X_n = y \mid X_k = y) = P^k(x, y) \]
		Tentu saja, berdasarkan definisi, \( \P(\tau_y = k \mid X_0 = x) = H_k(x, y) \), sehingga hasilnya diperoleh melalui substitusi.</p>""",
        "new": r"""<p>Untuk \(n\in\N_+\), kejadian-kejadian \(\{\tau_y=k,X_n=y\}\), \(1\le k\le n\), mempartisi \(\{X_n=y\}\). Karena \(\tau_y\) adalah waktu henti dan \(X_{\tau_y}=y\) pada \(\{\tau_y&lt;\infty\}\), sifat Markov kuat pada \(\tau_y\) memberikan
\[
\begin{aligned}
P^n(x,y)
&amp;=\P_x(X_n=y)\\
&amp;=\sum_{k=1}^{n}\P_x(X_n=y,\tau_y=k)\\
&amp;=\sum_{k=1}^{n}
   \E_x\!\left[\bs{1}_{\{\tau_y=k\}}
   P^{n-k}(X_{\tau_y},y)\right]\\
&amp;=\sum_{k=1}^{n}H_k(x,y)P^{n-k}(y,y).
\end{aligned}
\]
Inilah identitas yang dinyatakan di atas.</p>""",
        "description": "Use the finite first-hit partition and the strong Markov factor P^(n-k)(y,y), replacing the source's wrong range and transition term.",
    },
    {
        "id": "first-hit-convolution-statement-reflow",
        "old": r"""\[ P^n(x, y) = \sum_{k=1}^n H_k(x, y) P^{n-k}(y, y),  \quad n \in \N_+ \]""",
        "new": r"""\[
\begin{gathered}
P^n(x,y)=\sum_{k=1}^{n}H_k(x,y)P^{n-k}(y,y),\\
n\in\N_+.
\end{gathered}
\]""",
        "description": "Reflow the first-hit convolution statement into two readable narrow-screen lines.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "hitting-set-nonempty-domain",
        "old": r"""<p class="math">Misalkan \( x \in S \) dan \( A \subseteq S \). Maka</p>""",
        "new": r"""<p class="math">Misalkan \(x\in S\) dan \(A\subseteq S\) tak kosong. Maka</p>""",
        "description": "Keep the hitting-set domain consistent with the preceding definition.",
    },
    {
        "id": "hitting-first-step-proof",
        "old": r"""<ol class="sub">
<li>Jika rantai dimulai pada keadaan \( x \), rantai pertama kali mencapai \( A \) pada waktu \( n + 1 \) jika dan hanya jika rantai berpindah ke suatu keadaan \( y \notin A \) pada waktu 1, lalu dari keadaan \( y \) pertama kali mencapai \( A \) dalam \( n \) langkah.
			\[ H_{n+1}(x, A) = \P(\tau_A = n + 1 \mid X_0 = x) = \sum_{y \in S} \P(\tau_A = n + 1 \mid X_0 = x, X_1 = y) \P(X_1 = y \mid X_0 = x) \]
			Namun, \( \P(\tau_A = n + 1 \mid X_0 = x, X_1 = y) = 0 \) untuk \( y \in A \). Berdasarkan sifat Markov dan sifat homogen terhadap waktu, \( \P(\tau_A = n + 1 \mid X_0 = x,  X_1 = y) = \P(\tau_A = n \mid X_0 = y) = H_n(x, A) \) untuk \( y \notin A \). Tentu saja, \( \P(X_1 = y \mid X_0 = x) = P(x, y) \). Jadi, hasilnya diperoleh melalui substitusi.</li>
<li>Jika rantai dimulai pada keadaan \( x \), rantai pada akhirnya mencapai \( A \) jika dan hanya jika rantai mencapai \( A \) pada langkah pertama, atau berpindah ke suatu keadaan lain \( y \notin A \) pada langkah pertama, lalu pada akhirnya mencapai \( A \) dari \( y \).
			\[ H(x, A) = \P(\tau_A \lt \infty \mid X_0 = x) = \sum_{y \in S} \P(\tau_A \lt \infty \mid X_1 =y, X_0 = x) \P(X_1 = y \mid X_0 = x)\]
			Namun, \( \P(\tau_A \lt \infty \mid X_1 = y, X_0 = x) = 1\) untuk \( y \in A \). Berdasarkan sifat Markov dan sifat homogen terhadap waktu, \(\P(\tau_A \lt \infty \mid X_1 = y, X_0 = x) =  \P(\tau_A \lt \infty \mid X_0 = y) = H(y, A) \) untuk \( y \notin A \). Dengan melakukan substitusi, diperoleh
			\[ H(x, A) = \sum_{y \in A} P(x, y) + \sum_{y \notin A} P(x, y) H(y, A) = P(x, A) + \sum_{y \notin A} P(x, y) H(y, A) \]</li>
</ol>""",
        "new": r"""<ol class="sub">
<li>Untuk \(n\in\N_+\), dekomposisi menurut keadaan pada waktu 1 dan sifat Markov memberikan
\[
\begin{aligned}
H_{n+1}(x,A)
&amp;=\sum_{y\notin A}\P_x(\tau_A=n+1,X_1=y)\\
&amp;=\sum_{y\notin A}P(x,y)\P_y(\tau_A=n)\\
&amp;=\sum_{y\notin A}P(x,y)H_n(y,A).
\end{aligned}
\]
Argumen ini berlaku untuk setiap keadaan karena memakai keluarga \((\P_x)_{x\in S}\), bukan pengondisian pada kejadian nol.</li>
<li>Pisahkan kemungkinan \(X_1\in A\) dari kemungkinan \(X_1=y\notin A\). Sifat Markov memberikan
\[
\begin{aligned}
H(x,A)
&amp;=\P_x(X_1\in A)
 +\sum_{y\notin A}\P_x(X_1=y)\P_y(\tau_A&lt;\infty)\\
&amp;=P(x,A)+\sum_{y\notin A}P(x,y)H(y,A).
\end{aligned}
\]</li>
</ol>""",
        "description": "Replace null-event conditioning and the erroneous H_n(x,A) substitution by the all-state first-step identities.",
    },
    {
        "id": "green-kernel-all-state-reflow",
        "old": r"""\[ G(x, A) = \E \left(\sum_{n=1}^\infty \bs{1}(X_n \in A) \biggm| X_0 = x\right) = \sum_{n=1}^\infty \P(X_n \in A \mid X_0 = x) = \sum_{n=1}^\infty P^n(x, A) \]""",
        "new": r"""\[
\begin{aligned}
G(x,A)
&amp;=\E_x\!\left[\sum_{n=1}^{\infty}\bs1(X_n\in A)\right]\\
&amp;=\sum_{n=1}^{\infty}\P_x(X_n\in A)
=\sum_{n=1}^{\infty}P^n(x,A).
\end{aligned}
\]""",
        "description": "Express the Green kernel under the all-state law and reflow its monotone-sum identity.",
    },
    {
        "id": "transient-visit-distribution-reference",
        "old": r"""dengan menggunakan <a class="ref" href="#pot2"></a> dan deret geometri""",
        "new": r"""dengan menggunakan <a class="ref" href="#pot2">distribusi banyaknya kunjungan</a> dan deret geometri""",
        "description": "Supply visible text for the transient visit-distribution reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "transient-geometric-sum-reflow",
        "old": r"""\[\P(N_y \in \N_+ \mid X_0 = x) = \sum_{n=1}^\infty \P(N_y = n \mid X_0 = x) = H(x, y) [1 - H(y, y)] \sum_{n=1}^\infty [H(y, y)]^{n-1} = H(x, y)\]""",
        "new": r"""\[
\begin{aligned}
\P_x(N_y\in\N_+)
&amp;=\sum_{n=1}^{\infty}\P_x(N_y=n)\\
&amp;=H(x,y)[1-H(y,y)]
  \sum_{n=1}^{\infty}[H(y,y)]^{n-1}\\
&amp;=H(x,y).
\end{aligned}
\]""",
        "description": "Reflow the geometric-series calculation and use the all-state law.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "recurrent-visit-mass",
        "old": r"""<li>Jika \( y \) rekuren, \( H(y, y) = 1 \), sehingga dari <a class="ref" href="#pot2"></a>, \( \P(N_y = n \mid X_0 = x) = 0 \) untuk semua \( n \in \N_+ \). Karena itu, \( \P(N_y = \infty \mid X_0 = x) = 1 - \P(N_y = 0 \mid X_0 = x) = 1 - H(x, y) \).</li>""",
        "new": r"""<li>Jika \(y\) rekuren, \(H(y,y)=1\), sehingga dari <a class="ref" href="#pot2">distribusi banyaknya kunjungan</a>, \(\P_x(N_y=n)=0\) untuk semua \(n\in\N_+\). Karena itu,
\[
\P_x(N_y=\infty)=1-\P_x(N_y=0)=H(x,y).
\]</li>""",
        "description": "Correct the recurrent-state mass at infinity from 1-H(x,y) to H(x,y), and expose its supporting reference.",
    },
    {
        "id": "recurrent-self-visit-reference",
        "old": r"""<li>Dari <a class="ref" href="#pot4"></a>, \( \P(N_y = n \mid X_0 = y) = 0 \) untuk semua \( n \in \N \), sehingga \( \P(N_y = \infty \mid X_0 = y) = 1 \).</li>""",
        "new": r"""<li>Dari <a class="ref" href="#pot2">distribusi banyaknya kunjungan</a>, \(\P_y(N_y=n)=0\) untuk semua \(n\in\N\), sehingga \(\P_y(N_y=\infty)=1\).</li>""",
        "description": "Cite the visit-distribution result rather than the transient-state theorem, and use the all-state law.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "hitting-accessibility-reference",
        "old": r"""<a class="ref" href="#hit2"></a> diperoleh bahwa""",
        "new": r"""<a class="ref" href="#hit2">kriteria pencapaian melalui pangkat transisi</a> diperoleh bahwa""",
        "description": "Supply visible text for the accessibility criterion reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "transitivity-natural-number-symbol",
        "old": r"""\( j, \, k \in N \)""",
        "new": r"""\(j,k\in\N\)""",
        "description": "Use the declared natural-number macro in the transitivity proof.",
    },
    {
        "id": "restricted-path-edge-cases",
        "old": r"""\[ P_A^n(x, y) = \P(X_1 \in A, \ldots, X_{n-1} \in A, X_n = y \mid X_0 = x) \]
besaran tersebut adalah probabilitas berpindah dari \( x \) ke \( y \) dalam \( n \) langkah sambil tetap berada di \( A \) sepanjang waktu.""",
        "new": r"""\[
P_A^0(x,y)=\bs1(x=y),
\]
sedangkan, untuk \(n\in\N_+\),
\[
P_A^n(x,y)
=\P_x\!\left(
\bigcap_{j=1}^{n-1}\{X_j\in A\}\cap\{X_n=y\}
\right),
\]
dengan irisan kosong sama dengan \(\Omega\). Besaran kedua adalah probabilitas berpindah dari \(x\) ke \(y\) dalam \(n\) langkah sambil tetap berada di \(A\) sepanjang waktu.""",
        "description": "Separate the n=0 identity and state the restricted-path event for n>=1 with the empty-intersection convention.",
    },
    {
        "id": "irreducible-singleton-closures",
        "old": r"""\( \cl(y) = A \) untuk setiap \( y \in A \), dan khususnya \( \cl(x) = A \)""",
        "new": r"""\(\cl(\{y\})=A\) untuk setiap \(y\in A\), dan khususnya \(\cl(\{x\})=A\)""",
        "description": "Apply the closure operator to singleton sets rather than bare states.",
    },
    {
        "id": "recurrent-class-property-reference",
        "old": r"""Dari <a class="ref" href="#cls1"></a>, perhatikan bahwa""",
        "new": r"""Dari <a class="ref" href="#cls1">teorema ketercapaian dari keadaan rekuren</a>, perhatikan bahwa""",
        "description": "Supply visible text for the recurrent class-property reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "finite-irreducible-class-references",
        "old": r"""Perhatikan bahwa \( A \) adalah kelas komunikasi berdasarkan <a class="ref" href="#rel10"></a>, dan \( A \) memiliki keadaan rekuren berdasarkan <a class="ref" href="#cls3"></a>.""",
        "new": r"""Perhatikan bahwa \(A\) adalah kelas komunikasi berdasarkan <a class="ref" href="#rel10">teorema himpunan tak tereduksi</a>, dan \(A\) memiliki keadaan rekuren berdasarkan <a class="ref" href="#cls3">teorema himpunan berhingga tertutup</a>.""",
        "description": "Supply visible text for both references in the finite irreducible-class proof.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "finite-staying-event-domain",
        "old": r"""<p class="math">Misalkan \( A \) adalah himpunan bagian sejati dari \( S \). Maka</p>
<ol class="sub">
<li>\(P_A^n(x, A) = \P(X_1 \in A, X_2 \in A, \ldots, X_n \in A \mid X_0 = x) \) untuk \( x \in A \)</li>
<li>\( \lim_{n \to \infty} P_A^n(x, A) = \P(X_1 \in A, X_2 \in A \ldots \mid X_0 = x) \) untuk \( x \in A \)</li>
</ol>""",
        "new": r"""<p class="math">Misalkan \(A\) adalah himpunan bagian sejati dari \(S\). Maka</p>
<ol class="sub">
<li>\(P_A^n(x,A)=\P_x(X_1\in A,\ldots,X_n\in A)\) untuk \(x\in A\) dan \(n\in\N_+\).</li>
<li>\(\displaystyle\lim_{n\to\infty}P_A^n(x,A)=\P_x(X_1\in A,X_2\in A,\ldots)\) untuk \(x\in A\).</li>
</ol>""",
        "description": "Give the finite staying formula its positive-time domain, restore the missing comma, and use the all-state law.",
    },
    {
        "id": "zero-one-reference",
        "old": r"""Pencirian dalam <a class="ref" href="#tst2"></a> menyiratkan""",
        "new": r"""Pencirian dalam <a class="ref" href="#tst2">teorema fungsi bertahan terbesar</a> menyiratkan""",
        "description": "Supply visible text for the zero-one characterization reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "classification-reference",
        "old": r"""rekuren berdasarkan <a class="ref" href="#tst4"></a>.""",
        "new": r"""rekuren berdasarkan <a class="ref" href="#tst4">uji klasifikasi melalui fungsi bertahan</a>.""",
        "description": "Supply visible text for the recurrence-classification reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "green-to-hitting-reference",
        "old": r"""menghitung \( H_B \) menggunakan <a class="ref" href="#pot4"></a>.""",
        "new": r"""menghitung \(H_B\) menggunakan <a class="ref" href="#pot4">hubungan Green–pencapaian bagi keadaan transien</a>.""",
        "description": "Supply visible text for the Green-to-hitting conversion reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "hitting-computation-references",
        "old": r"""Latihan <a class="ref" href="#com3"></a> memadai jika kita telah menghitung \( G_B \) (misalnya dengan menggunakan latihan <a class="ref" href="#com1"></a>).""",
        "new": r"""Rumus <a class="ref" href="#com3">pencapaian kelas rekuren</a> memadai jika kita telah menghitung \(G_B\) (misalnya dengan menggunakan <a class="ref" href="#com1">persamaan matriks Green transien</a>).""",
        "description": "Supply visible, semantically accurate text for both computational cross-references.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "finite-hitting-solution-reference",
        "old": r"""diperoleh dari latihan <a class="ref" href="#com1"></a>.""",
        "new": r"""diperoleh dari <a class="ref" href="#com1">persamaan matriks Green transien</a>.""",
        "description": "Supply visible text for the finite hitting-system reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "hitting-event-tex-localization",
        "old": r"""\{\tau_y \lt \infty\} = \{X_k = y \text{ for some } k \in \N_+\}""",
        "new": r"""\{\tau_y&lt;\infty\}=\{X_k=y\text{ untuk suatu }k\in\N_+\}""",
        "description": "Localize the English prose retained inside the source TeX.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "closure-tex-localization",
        "old": r"""\cl(A) = \{y \in S: x \to y \text{ for some } x \in A\}""",
        "new": r"""\cl(A)=\{y\in S:x\to y\text{ untuk suatu }x\in A\}""",
        "description": "Localize the English prose retained inside the closure formula.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "finite-example-transition-row",
        "old": r"""\frac{1}{2} &amp; \frac{2}{3} &amp; 0 &amp; 0 \\""",
        "new": r"""\frac{1}{3} &amp; \frac{2}{3} &amp; 0 &amp; 0 \\""",
        "description": "Restore the stochastic first row (1/3,2/3,0,0), witnessed by the July 2009 official UAH print capture; the current 1/2 entry makes the row sum 7/6.",
    },
    {
        "id": "finite-example-1-green-matrix-reflow",
        "old": r"""\( G = \left[ \begin{matrix}
				\infty &amp; \infty &amp; 0 &amp; 0 \\
				\infty &amp; \infty &amp; 0 &amp; 0 \\
				0 &amp; 0 &amp; \infty &amp; 0 \\
				\infty &amp; \infty &amp; \infty &amp; \frac{1}{3}
			\end{matrix} \right] \)""",
        "new": r"""\[
G=\begin{bmatrix}
\infty&amp;\infty&amp;0&amp;0\\
\infty&amp;\infty&amp;0&amp;0\\
0&amp;0&amp;\infty&amp;0\\
\infty&amp;\infty&amp;\infty&amp;\frac13
\end{bmatrix}.
\]""",
        "description": "Promote the first worked Green matrix to a readable, bounded display.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "finite-example-1-hitting-matrix-reflow",
        "old": r"""\( H = \left[ \begin{matrix}
				1 &amp; 1 &amp; 0 &amp; 0 \\
				1 &amp; 1 &amp; 0 &amp; 0 \\
				0 &amp; 0 &amp; 1 &amp; 0 \\
				\frac{2}{3} &amp; \frac{2}{3} &amp; \frac{1}{3} &amp; \frac{1}{4}
			\end{matrix} \right] \)""",
        "new": r"""\[
H=\begin{bmatrix}
1&amp;1&amp;0&amp;0\\
1&amp;1&amp;0&amp;0\\
0&amp;0&amp;1&amp;0\\
\frac23&amp;\frac23&amp;\frac13&amp;\frac14
\end{bmatrix}.
\]""",
        "description": "Promote the first worked hitting matrix to a readable, bounded display.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "finite-example-2-green-matrix-reflow",
        "old": r"""\( G = \left[ \begin{matrix}
				\infty &amp; 0 &amp; \infty &amp; 0 &amp; \infty &amp; 0 \\
				\infty &amp; \frac{1}{2} &amp; \infty &amp; \infty &amp; \infty &amp; 2 \\
				\infty &amp; 0 &amp; \infty &amp; 0 &amp; \infty &amp; 0 \\
				0 &amp; 0 &amp; 0 &amp; \infty &amp; 0 &amp; 0 \\
				\infty &amp; 0 &amp; \infty &amp; 0 &amp; \infty &amp; 0 \\
""" + "\t\t\t\t" + r"""\infty &amp; \frac{1}{2} &amp; \infty &amp; \infty &amp; \infty &amp; 1""" + " \n\t\t\t" + r"""\end{matrix} \right] \)""",
        "new": r"""\[
G=\begin{bmatrix}
\infty&amp;0&amp;\infty&amp;0&amp;\infty&amp;0\\
\infty&amp;\frac12&amp;\infty&amp;\infty&amp;\infty&amp;2\\
\infty&amp;0&amp;\infty&amp;0&amp;\infty&amp;0\\
0&amp;0&amp;0&amp;\infty&amp;0&amp;0\\
\infty&amp;0&amp;\infty&amp;0&amp;\infty&amp;0\\
\infty&amp;\frac12&amp;\infty&amp;\infty&amp;\infty&amp;1
\end{bmatrix}.
\]""",
        "description": "Promote the second worked Green matrix to a readable, bounded display.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "finite-example-2-hitting-matrix-reflow",
        "old": r"""\( H = \left[ \begin{matrix}
				1 &amp; 0 &amp; 1 &amp; 0 &amp; 1 &amp; 0 \\
				\frac{1}{2} &amp; \frac{1}{3} &amp; \frac{1}{2} &amp; \frac{1}{2} &amp; \frac{1}{2} &amp; 1 \\
				1 &amp; 0 &amp; 1 &amp; 0 &amp; 1 &amp; 0 \\
				0 &amp; 0 &amp; 0 &amp; 1 &amp; 0 &amp; 0 \\
				1 &amp; 0 &amp; 1 &amp; 0 &amp; 1 &amp; 0 \\
""" + "\t\t\t\t" + r"""\frac{1}{2} &amp; \frac{1}{3} &amp; \frac{1}{2} &amp; \frac{1}{2} &amp; \frac{1}{2} &amp; \frac{1}{2}""" + " \n\t\t\t" + r"""\end{matrix} \right] \)""",
        "new": r"""\[
H=\begin{bmatrix}
1&amp;0&amp;1&amp;0&amp;1&amp;0\\
\frac12&amp;\frac13&amp;\frac12&amp;\frac12&amp;\frac12&amp;1\\
1&amp;0&amp;1&amp;0&amp;1&amp;0\\
0&amp;0&amp;0&amp;1&amp;0&amp;0\\
1&amp;0&amp;1&amp;0&amp;1&amp;0\\
\frac12&amp;\frac13&amp;\frac12&amp;\frac12&amp;\frac12&amp;\frac12
\end{bmatrix}.
\]""",
        "description": "Promote the second worked hitting matrix to a readable, bounded display.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "finite-example-3-green-matrix-reflow",
        "old": r"""\( G = \left[ \begin{matrix}
				\infty &amp; \infty &amp; 0 &amp; 0 &amp; 0 &amp; 0 \\
				\infty &amp; \infty &amp; 0 &amp; 0 &amp; 0 &amp; 0 \\
				\infty &amp; \infty &amp; \frac{7}{5} &amp; \frac{4}{5} &amp; \infty &amp; \infty \\
				\infty &amp; \infty &amp; \frac{4}{5} &amp; \frac{3}{5} &amp; \infty &amp; \infty \\
				0 &amp; 0 &amp; 0 &amp; 0 &amp; \infty &amp; \infty \\
""" + "\t\t\t\t" + r"""0 &amp; 0 &amp; 0 &amp; 0 &amp; \infty &amp; \infty""" + " \n\t\t\t" + r"""\end{matrix} \right] \)""",
        "new": r"""\[
G=\begin{bmatrix}
\infty&amp;\infty&amp;0&amp;0&amp;0&amp;0\\
\infty&amp;\infty&amp;0&amp;0&amp;0&amp;0\\
\infty&amp;\infty&amp;\frac75&amp;\frac45&amp;\infty&amp;\infty\\
\infty&amp;\infty&amp;\frac45&amp;\frac35&amp;\infty&amp;\infty\\
0&amp;0&amp;0&amp;0&amp;\infty&amp;\infty\\
0&amp;0&amp;0&amp;0&amp;\infty&amp;\infty
\end{bmatrix}.
\]""",
        "description": "Promote the third worked Green matrix to a readable, bounded display.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "finite-example-3-hitting-matrix-reflow",
        "old": r"""\( H = \left[ \begin{matrix}
				1 &amp; 1 &amp; 0 &amp; 0 &amp; 0 &amp; 0 \\
				1 &amp; 1 &amp; 0 &amp; 0 &amp; 0 &amp; 0 \\
				\frac{4}{5} &amp; \frac{4}{5} &amp; \frac{7}{12} &amp; \frac{1}{2} &amp; \frac{1}{5} &amp; \frac{1}{5} \\
				\frac{3}{5} &amp; \frac{3}{5} &amp; \frac{1}{3} &amp; \frac{3}{8} &amp; \frac{2}{5} &amp; \frac{2}{5} \\
				0 &amp; 0 &amp; 0 &amp; 0 &amp; 1 &amp; 1 \\
""" + "\t\t\t\t" + r"""0 &amp; 0 &amp; 0 &amp; 0 &amp; 1 &amp; 1""" + " \n\t\t\t" + r"""\end{matrix} \right] \)""",
        "new": r"""\[
H=\begin{bmatrix}
1&amp;1&amp;0&amp;0&amp;0&amp;0\\
1&amp;1&amp;0&amp;0&amp;0&amp;0\\
\frac45&amp;\frac45&amp;\frac7{12}&amp;\frac12&amp;\frac15&amp;\frac15\\
\frac35&amp;\frac35&amp;\frac13&amp;\frac38&amp;\frac25&amp;\frac25\\
0&amp;0&amp;0&amp;0&amp;1&amp;1\\
0&amp;0&amp;0&amp;0&amp;1&amp;1
\end{bmatrix}.
\]""",
        "description": "Promote the third worked hitting matrix to a readable, bounded display.",
        "change_kind": "deterministic-output",
    },
)

MARKOV_PERIODICITY_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "periodicity-opening-nonempty-return-set",
        "old": r"Suatu keadaan dalam rantai Markov waktu diskret bersifat periodik jika rantai hanya dapat kembali ke keadaan tersebut pada kelipatan suatu bilangan bulat yang lebih besar dari 1.",
        "new": r"Suatu keadaan dalam rantai Markov waktu diskret bersifat periodik jika himpunan waktu kembali positifnya tidak kosong dan mempunyai faktor persekutuan terbesar yang lebih besar dari 1.",
        "description": "Avoid classifying a state with no possible positive return as periodic by vacuous divisibility.",
    },
    {
        "id": "empty-return-set-period-convention",
        "old": r"""<p class="dfn"><dfn>Periode</dfn> keadaan \( x \in S \) adalah
	\[ d(x) = \gcd\{n \in \N_+: P^n(x, x) \gt 0 \} \]
	Keadaan \( x \) bersifat <dfn>aperiodik</dfn> jika \( d(x) = 1 \) dan <dfn>periodik</dfn> jika \( d(x) \gt 1 \).</p>""",
        "new": r"""<p class="dfn"><dfn>Periode</dfn> keadaan \( x \in S \) adalah
	\[ d(x) = \gcd\{n \in \N_+: P^n(x, x) \gt 0 \} \]
	dengan konvensi \(\gcd\varnothing=0\). Keadaan \(x\) dengan \(d(x)=0\) bukan keadaan periodik maupun aperiodik. Keadaan \( x \) bersifat <dfn>aperiodik</dfn> jika \( d(x) = 1 \) dan <dfn>periodik</dfn> jika \( d(x) \gt 1 \).</p>""",
        "description": "Define the empty-return-set case instead of leaving the period undefined for a legitimate transient state.",
    },
    {
        "id": "period-class-proof-divisibility-direction",
        "old": r"Berdasarkan definisi periode, \( d(y) \mid d(x) \). Dengan menukar peran \( x \) dan \( y \), kita juga memperoleh \( d(x) \mid d(y) \).",
        "new": r"Berdasarkan definisi periode, \( d(x) \mid d(y) \). Dengan menukar peran \( x \) dan \( y \), kita juga memperoleh \( d(y) \mid d(x) \).",
        "description": "Repair both reversed divisibility conclusions in the class-property proof.",
    },
    {
        "id": "period-explanation-empty-return-case",
        "old": r"Jadi, jika dimulai dari \( x \), rantai hanya dapat kembali ke \( x \) pada kelipatan periode \( d \), dan \( d \) adalah bilangan bulat terbesar dengan sifat tersebut.",
        "new": r"Jika \(d(x)\ge 1\), setiap waktu kembali positif ke \(x\) habis dibagi \(d(x)\), dan \(d(x)\) adalah faktor persekutuan terbesar semua waktu tersebut. Jika \(d(x)=0\), tidak ada waktu kembali positif ke \(x\).",
        "description": "State the gcd property only for nonempty return-time sets and handle d=0 separately.",
    },
    {
        "id": "closed-class-restriction-scope",
        "old": r"Kita tidak kehilangan keumuman dengan mengasumsikan bahwa rantai tak tereduksi, sebab jika tidak demikian, kita cukup membatasi perhatian pada salah satu kelas komunikasi yang tak tereduksi.",
        "new": r"Pembahasan berikut berlaku untuk rantai tak tereduksi. Untuk rantai tereduksi, argumen yang sama dapat diterapkan secara terpisah pada setiap kelas komunikasi tertutup yang tak tereduksi; pembatasan pada kelas yang tidak tertutup umumnya hanya menghasilkan matriks substokastik.",
        "description": "Limit the restriction claim to closed irreducible classes, whose restrictions remain Markov chains.",
    },
    {
        "id": "explicit-cyclic-introduction-paragraph-close",
        "old": r"""m - p \equiv_d n - q \).

</p><p>Sekarang""",
        "new": r"""m - p \equiv_d n - q \).</p>
<p>Sekarang""",
        "description": "Repair the omitted paragraph close before parser-dependent downstream transformations.",
    },
    {
        "id": "cyclic-definition-quantifier-localization",
        "old": r"\text{ for some } n \in \N",
        "new": r"\text{ untuk suatu } n \in \N",
        "description": "Localize reader-facing prose embedded in the cyclic-class display.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "cyclic-residue-set-punctuation",
        "old": r"\{0, 1, \ldots d - 1\}",
        "new": r"\{0, 1, \ldots, d - 1\}",
        "description": "Restore the missing separator in the finite residue set.",
    },
    {
        "id": "cyclic-partition-index",
        "old": r"\( (A_0, A_1, \ldots, A_{k-1}) \) mempartisi \( S \)",
        "new": r"\( (A_0, A_1, \ldots, A_{d-1}) \) mempartisi \( S \)",
        "description": "Use the chain period d, not the preceding local index k, in the cyclic partition.",
    },
    {
        "id": "cyclic-forward-step-domain-and-punctuation",
        "old": r"maka \( P^n(x, y) \gt 0 \) untuk suatu \( n \equiv_d k - j \)</li>",
        "new": r"maka \( P^n(x, y) \gt 0 \) untuk suatu \( n \in \N \) dengan \( n \equiv_d k - j \).</li>",
        "description": "State the step-count domain explicitly and complete the first cyclic-class assertion.",
    },
    {
        "id": "cyclic-proof-finite-residue-bound",
        "old": r"\(j, \, k \in \{0, 1, \ldots\}\)",
        "new": r"\(j, \, k \in \{0, 1, \ldots, d - 1\}\)",
        "description": "Bound both cyclic-class indices by the complete residue system modulo d.",
    },
    {
        "id": "cyclic-proof-congruence-punctuation",
        "old": r"sehingga \( n \equiv_d k - j \)</p>",
        "new": r"sehingga \( n \equiv_d k - j \).</p>",
        "description": "Complete the cyclic-class proof sentence.",
    },
    {
        "id": "visible-finite-example-reference",
        "old": r'<a class="ref" href="#fin1"></a>',
        "new": r'<a class="ref" href="#fin1">contoh rantai tiga keadaan</a>',
        "description": "Supply visible Indonesian text for the JavaScript-generated empty reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "cyclic-classes-image-description",
        "old": r'alt="Kelas-kelas siklik suatu rantai periodik" src="CyclicClasses.png"',
        "new": r'alt="Diagram siklus berarah A_0 ke A_1 hingga A_{d-1}, lalu kembali ke A_0" src="CyclicClasses.png"',
        "description": "Describe the information carried by the cyclic-class diagram rather than repeat its caption.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "finite-seven-state-graph-text-alternative",
        "old": r"""<img alt="Graf keadaan untuk rantai tujuh keadaan" src="State4.png" title="Diagram keadaan"/>
</figure>
</li>""",
        "new": r"""<img alt="Graf tiga lapis: 1 menuju 3, 4, dan 5; 2 menuju 3 dan 5; 3, 4, dan 5 masing-masing menuju 6 dan 7; 6 dan 7 masing-masing menuju 1 dan 2" src="State4.png" title="Diagram keadaan"/>
</figure>
<p>Graf menunjukkan busur langsung 1 ke 3, 4, dan 5; 2 ke 3 dan 5; masing-masing dari 3, 4, dan 5 ke 6 dan 7; serta masing-masing dari 6 dan 7 ke 1 dan 2. Melalui lapisan-lapisan itu, setiap keadaan dapat mencapai setiap keadaan lain, sehingga rantai ini tak tereduksi.</p>
</li>""",
        "description": "Add a complete textual alternative and explicit irreducibility argument for the state graph.",
        "change_kind": "original-addition",
    },
    {
        "id": "finite-seven-state-cube-repair-and-reflow",
        "old": r"""<li>\( P^3 = \left[ \begin{matrix}
				\frac{71}{192} &amp; \frac{121}{192} &amp; 0 &amp; 0 &amp; 0 &amp; 0 &amp; 0 \\
				\frac{29}{72} &amp; \frac{43}{72} &amp; 0 &amp; 0 &amp; 0 &amp; 0 &amp; 0 \\
				0 &amp; 0 &amp; \frac{7}{18} &amp; \frac{1}{12} &amp; \frac{19}{36} &amp; 0 &amp; 0 \\
				0 &amp; 0 &amp; \frac{19}{48} &amp; \frac{3}{32} &amp; \frac{49}{96} &amp; 0 &amp; 0 \\
				0 &amp; 0 &amp; \frac{13}{32} &amp; \frac{7}{64} &amp; \frac{31}{64} &amp; 0 &amp; 0 \\
				0 &amp; 0 &amp; 0 &amp; 0 &amp; 0 &amp; \frac{157}{299} &amp; \frac{131}{288} \\
				0 &amp; 0 &amp; 0 &amp; 0 &amp; 0 &amp; \frac{37}{64} &amp; \frac{27}{64}
			\end{matrix} \right] \)</li>""",
        "new": r"""<li>\[
P^3=\begin{bmatrix}
\frac{71}{192}&amp;\frac{121}{192}&amp;0&amp;0&amp;0&amp;0&amp;0\\
\frac{29}{72}&amp;\frac{43}{72}&amp;0&amp;0&amp;0&amp;0&amp;0\\
0&amp;0&amp;\frac7{18}&amp;\frac1{12}&amp;\frac{19}{36}&amp;0&amp;0\\
0&amp;0&amp;\frac{19}{48}&amp;\frac3{32}&amp;\frac{49}{96}&amp;0&amp;0\\
0&amp;0&amp;\frac{13}{32}&amp;\frac7{64}&amp;\frac{31}{64}&amp;0&amp;0\\
0&amp;0&amp;0&amp;0&amp;0&amp;\frac{157}{288}&amp;\frac{131}{288}\\
0&amp;0&amp;0&amp;0&amp;0&amp;\frac{37}{64}&amp;\frac{27}{64}
\end{bmatrix}.
\]</li>""",
        "description": "Correct 157/299 to 157/288 and promote the seven-state cube to a bounded display for mobile reflow.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "simple-random-walk-dimension-domain",
        "old": r'<li><a href="https://www.randomservices.org/random/markov/WalkGraph.html">Gerak acak sederhana pada \( \Z^k \)</a> bersifat periodik dengan periode 2,</li>',
        "new": r'<li><a href="https://www.randomservices.org/random/markov/WalkGraph.html">Gerak acak sederhana pada \( \Z^k \), dengan \(k\in\N_+\)</a>, bersifat periodik dengan periode 2.</li>',
        "description": "State the positive-integer dimension domain and finish the sentence.",
    },
)

MARKOV_LIMITING_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "localize-limit-tex-prose",
        "old": r"\text{ as }",
        "new": r"\text{ saat }",
        "matches": 9,
        "description": "Localize all nine serialized reader-facing limit qualifiers embedded in preserved TeX.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "localize-universal-state-tex-prose",
        "old": r"\text{ for every }",
        "new": r"\text{ untuk setiap }",
        "description": "Localize the reader-facing universal quantifier embedded in preserved TeX.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "proper-delayed-renewal-assumption",
        "old": r"""<li>Jika \( x \ne y \), tetapi \( x \to y \), kunjungan-kunjungan berturut-turut ke \( y \) membentuk <a href="https://www.randomservices.org/random/renewal/Delayed.html">proses pembaruan tertunda</a>.</li>""",
        "new": r"""<li>Jika \( x \ne y \) dan \( H(x,y)=1 \), kunjungan-kunjungan berturut-turut ke \( y \) membentuk <a href="https://www.randomservices.org/random/renewal/Delayed.html">proses pembaruan tertunda</a>. Jika hanya \(x\to y\), pernyataan tersebut berlaku setelah pengondisian pada \(\{\tau_y\lt\infty\}\).</li>""",
        "description": "Require an almost-sure first hit for a proper delayed renewal process, or condition explicitly on the first hit.",
    },
    {
        "id": "proper-delayed-renewal-proof",
        "old": r"""<li>Jika \( x \ne y \), tetapi \( x \to y \), maka jika \( X_0 = x \) diketahui, barisan \( \left(\tau_{y,1}, \tau_{y,2}, \ldots\right) \) adalah barisan waktu kedatangan suatu proses pembaruan tertunda. Berdasarkan argumen yang sama seperti pada (a), waktu antarkedatangan \( \tau_{y,n+1} - \tau_{y,n} \) untuk \( n \in \N \) independen secara bersyarat jika \( X_0 = x \) diketahui, dan semuanya kecuali \( \tau_{y,1} \) memiliki distribusi yang sama.</li>""",
        "new": r"""<li>Jika \( x \ne y \) dan \(H(x,y)=1\), maka jika \( X_0 = x \) diketahui, barisan \( \left(\tau_{y,1}, \tau_{y,2}, \ldots\right) \) adalah barisan waktu kedatangan suatu proses pembaruan tertunda. Berdasarkan argumen yang sama seperti pada (a), waktu antarkedatangan \( \tau_{y,n+1} - \tau_{y,n} \) untuk \( n \in \N \) independen secara bersyarat jika \( X_0 = x \) diketahui, dan semuanya kecuali \( \tau_{y,1} \) memiliki distribusi yang sama. Jika hanya \(x\to y\), klaim ini berlaku bersyarat pada \(\tau_y\lt\infty\); tanpa pengondisian, \(\tau_{y,1}=\infty\) dengan probabilitas \(1-H(x,y)\).</li>""",
        "description": "Close the defective-first-delay gap in the embedded-renewal proof.",
    },
    {
        "id": "visit-frequency-null-recurrence-theorem",
        "old": r"""<p class="math">Jika \( x, \, y \in S \) dan \( y \) rekuren, maka
	\[ \P\left( \frac{1}{n} N_{n,y} \to \frac{1}{\mu(y)} \text{ saat } n \to \infty \biggm| X_0 = x \right) = H(x, y) \]</p>""",
        "new": r"""<p class="math">Jika \( x, \, y \in S \) dan \( y \) rekuren, maka, dengan konvensi \(1/\infty=0\),
	\[ \P\left( \frac{N_{y,n}}{n} \to \frac{\bs{1}(\tau_y \lt \infty)}{\mu(y)} \text{ saat } n \to \infty \biggm| X_0 = x \right) = 1 \]
	Jadi, jika \(\mu(y)\lt\infty\), probabilitas bahwa \(N_{y,n}/n\to1/\mu(y)\) adalah \(H(x,y)\); jika \(\mu(y)=\infty\), probabilitas limit tersebut adalah 1.</p>""",
        "description": "Repair the reversed visit-count indices and the false null-recurrent probability claim.",
    },
    {
        "id": "cesaro-renewal-proof-conditioning",
        "old": r"""<p>Hasil ini mengikuti <a href="https://www.randomservices.org/random/renewal/LimitTheorems.html#ele">teorema pembaruan elementer</a> untuk proses pembaruan.</p>""",
        "new": r"""<p>Jika \(H(x,y)=0\), kedua ruas limit bernilai 0. Jika \(H(x,y)\gt0\), kondisikan pada \(\tau_y\lt\infty\), gunakan sifat Markov kuat pada \(\tau_y\), lalu terapkan <a href="https://www.randomservices.org/random/renewal/LimitTheorems.html#ele">teorema pembaruan elementer</a> pada proses pembaruan setelah kunjungan pertama. Mengalikan limit bersyarat itu dengan \(H(x,y)\) memberi hasil yang dinyatakan.</p>""",
        "description": "Justify the Cesaro limit when the first hitting delay is defective.",
    },
    {
        "id": "aperiodic-renewal-proof-conditioning",
        "old": r"""<p>Hasil ini mengikuti <a href="https://www.randomservices.org/random/renewal/LimitTheorems.html#ren">teorema pembaruan</a> untuk proses pembaruan.</p>""",
        "new": r"""<p>Jika \(H(x,y)=0\), kedua ruas limit bernilai 0. Jika \(H(x,y)\gt0\), kondisikan pada \(\tau_y\lt\infty\), gunakan sifat Markov kuat pada \(\tau_y\), lalu terapkan <a href="https://www.randomservices.org/random/renewal/LimitTheorems.html#ren">teorema pembaruan</a> pada proses pembaruan setelah kunjungan pertama. Aperiodisitas \(y\) meniadakan osilasi kisi, dan faktor \(H(x,y)\) berasal dari peluang kunjungan pertama.</p>""",
        "description": "Justify the pointwise renewal limit when the first hitting delay is defective.",
    },
    {
        "id": "positive-recurrence-averaged-index",
        "old": r"""\[ \frac{G_n(y, y)}{n } - \frac{G_{i+j}(y, y)}{n} \ge P^j(y, x) \frac{G_n(x, x)}{n} P^i(x, y)\]""",
        "new": r"""\[ \frac{G_{n+i+j}(y, y)-G_{i+j}(y, y)}{n} \ge P^j(y, x) \frac{G_n(x, x)}{n} P^i(x, y) \]""",
        "description": "Use the correctly shifted Green-function numerator after averaging the transition inequality.",
    },
    {
        "id": "invariant-density-cesaro-reference",
        "old": r"""Dengan mengambil \( n \to \infty \) dan menggunakan <a class="ref" href="#lim3"></a>, diperoleh \( \sum_{y \in A} f(y) \le 1 \).""",
        "new": r"""Dengan mengambil \( n \to \infty \) dan menggunakan <a class="ref" href="#lim2">hasil limit Cesàro</a>, diperoleh \( \sum_{y \in A} f(y) \le 1 \).""",
        "description": "Cite the Cesaro transition limit, which does not require aperiodicity, instead of the pointwise limit.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "zero-mixture-weight-case",
        "old": r"""Misalkan \( p_i = \sum_{x \in A_i} f(x) \), yaitu konstanta normalisasi bagi \( f \) yang dibatasi pada \( A_i \). Berdasarkan ketunggalan, pembatasan \( f / p_i \) pada \( A_i \) harus sama dengan \( f_i \), sehingga \( f \) berbentuk seperti yang diberikan dalam teorema.""",
        "new": r"""Misalkan \( p_i = \sum_{x \in A_i} f(x) \). Jika \(p_i=0\), karena \(f\ge0\), maka \(f(x)=0\) untuk setiap \(x\in A_i\). Jika \(p_i\gt0\), \(p_i\) adalah konstanta normalisasi bagi \( f \) yang dibatasi pada \( A_i \), dan berdasarkan ketunggalan pembatasan \( f / p_i \) pada \( A_i \) sama dengan \( f_i \). Jadi, dalam kedua kasus, \(f(x)=p_i f_i(x)\) pada \(A_i\), sehingga \( f \) berbentuk seperti yang diberikan dalam teorema.""",
        "description": "Handle zero class weights before dividing by the normalization constant.",
    },
    {
        "id": "green-matrix-subscript-spacing",
        "old": r"\( g G_ n / n = g \)",
        "new": r"\( g G_n / n = g \)",
        "description": "Repair the broken Green-matrix subscript.",
    },
    {
        "id": "finite-example-3-return-time",
        "old": r"\( \mu = \left(\frac{19}{2}, \infty, \frac{19}{8}, 1, \frac{19}{8}, \infty\right) \)",
        "new": r"\( \mu = \left(\frac{19}{2}, \infty, \frac{19}{8}, 1, \frac{19}{9}, \infty\right) \)",
        "description": "Use the reciprocal of f(5)=9/19 for the fifth state's mean return time.",
    },
    {
        "id": "finite-example-4-missing-absorption-mass",
        "old": r"""\frac{4}{15} &amp; \frac{8}{15} &amp; 0 &amp; 0 &amp; 0 &amp; 0 \\""",
        "new": r"""\frac{4}{15} &amp; \frac{8}{15} &amp; 0 &amp; 0 &amp; \frac{1}{10} &amp; \frac{1}{10} \\""",
        "description": "Restore the omitted absorption probabilities into states 5 and 6 in the third limiting row.",
    },
    {
        "id": "finite-example-5-return-vector-comma",
        "old": r"\frac{1}{300} \frac{1}{333}",
        "new": r"\frac{1}{300}, \frac{1}{333}",
        "description": "Restore the missing separator between the fifth and sixth mean return times.",
    },
    {
        "id": "finite-example-5-limit-3n-normalizer",
        "old": r"\( P^{3 n} \to \frac{1}{585}",
        "new": r"\( P^{3 n} \to \frac{1}{595}",
        "description": "Normalize the 3n subsequential limit by the verified cyclic-class numerator sum 595.",
    },
    {
        "id": "finite-example-5-limit-3n-plus-1-normalizer",
        "old": r"\( P^{3 n + 1} \to \frac{1}{585}",
        "new": r"\( P^{3 n + 1} \to \frac{1}{595}",
        "description": "Normalize the 3n+1 subsequential limit by the verified cyclic-class numerator sum 595.",
    },
    {
        "id": "finite-example-5-limit-3n-plus-2-normalizer",
        "old": r"\( P^{3 n + 2} \to \frac{1}{585}",
        "new": r"\( P^{3 n + 2} \to \frac{1}{595}",
        "description": "Normalize the 3n+2 subsequential limit by the verified cyclic-class numerator sum 595.",
    },
    {
        "id": "cyclic-classes-image-description",
        "old": r'alt="Kelas-kelas siklik suatu rantai periodik" src="CyclicClasses.png"',
        "new": r'alt="Diagram siklus berarah A_0 ke A_1 hingga A_{d-1}, lalu kembali ke A_0" src="CyclicClasses.png"',
        "description": "Describe the cyclic transition pattern instead of repeating the caption.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "finite-example-2-state-graph-and-loop-note",
        "old": r"""<img alt="Graf keadaan untuk contoh berhingga pertama" src="State1.png"/>
</figure>
</li>""",
        "new": r"""<img alt="Graf berarah: a menuju a dengan bobot 1/3 dan b dengan 2/3; b menuju a dengan 1; c menyerap; d menuju a, b, c, dan d masing-masing dengan 1/4" src="State1.png"/>
</figure>
<p class="reader-correction"><strong>Catatan koreksi diagram:</strong> matriks \(P\) juga memuat gelang \(d\to d\) berbobot \(1/4\); gelang tersebut tidak tergambar pada berkas sumber.</p>
</li>""",
        "description": "Supply a complete text alternative and disclose the source figure's omitted d-to-d self-loop.",
        "change_kind": "original-addition",
    },
    {
        "id": "finite-example-3-state-graph-description",
        "old": r'alt="Graf keadaan untuk contoh berhingga kedua" src="State2.png"',
        "new": r'alt="Graf berarah: 1 menuju 3 dan 5; 2 menuju 6; 3 menuju 1, 3, dan 5; 4 menyerap; 5 menuju 3 dan 5; 6 menuju 2, 3, 4, dan 6, dengan bobot sesuai matriks P" src="State2.png"',
        "description": "Replace the generic graph alternative with its edge structure.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "finite-example-4-state-graph-description",
        "old": r'alt="Graf keadaan untuk contoh berhingga ketiga" src="State3.png"',
        "new": r'alt="Graf berarah: kelas tertutup 1–2 dan 5–6; keadaan 3 menuju 1, 3, dan 4; keadaan 4 menuju 1, 3, 4, dan 6, dengan bobot sesuai matriks P" src="State3.png"',
        "description": "Replace the generic graph alternative with its closed classes and transient edges.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "finite-example-5-state-graph-description",
        "old": r'alt="Graf keadaan untuk contoh berhingga keempat" src="State4.png"',
        "new": r'alt="Graf tiga lapis: 1 menuju 3, 4, dan 5; 2 menuju 3 dan 5; 3, 4, dan 5 masing-masing menuju 6 dan 7; 6 dan 7 masing-masing menuju 1 dan 2" src="State4.png"',
        "description": "Replace the generic graph alternative with the complete directed edge structure.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-reference-lim1",
        "old": r'<a class="ref" href="#lim1"></a>',
        "new": r'<a class="ref" href="#lim1">hasil frekuensi kunjungan</a>',
        "description": "Supply static visible text for the first JavaScript-generated reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-references-lim2",
        "old": r'<a class="ref" href="#lim2"></a>',
        "new": r'<a class="ref" href="#lim2">hasil limit Cesàro</a>',
        "matches": 3,
        "description": "Supply static visible text for all three remaining Cesaro-limit references.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-reference-lim3",
        "old": r'<a class="ref" href="#lim3"></a>',
        "new": r'<a class="ref" href="#lim3">hasil limit aperiodik</a>',
        "description": "Supply static visible text for the remaining pointwise-limit reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-reference-pos4",
        "old": r'<a class="ref" href="#pos4"></a>',
        "new": r'<a class="ref" href="#pos4">hasil kelas tertutup berhingga</a>',
        "description": "Supply static visible text for the positive-recurrence reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-reference-pos5",
        "old": r'<a class="ref" href="#pos5"></a>',
        "new": r'<a class="ref" href="#pos5">hasil kelas rekuren</a>',
        "description": "Supply static visible text for the recurrent-class reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-reference-lim5",
        "old": r'<a class="ref" href="#lim5"></a>',
        "new": r'<a class="ref" href="#lim5">klasifikasi limit sebelumnya</a>',
        "description": "Supply static visible text for the limiting-classification reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "visible-reference-rev2",
        "old": r'<a class="ref" href="#rev2"></a>',
        "new": r'<a class="ref" href="#rev2">hasil limit periodik</a>',
        "description": "Supply static visible text for the periodic-limit reference.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "offline-two-state-simulator-link",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/TwoState.html">rantai dua-keadaan</a>',
        "new": r'<a class="ancillary" href="../apps/two-state.html">rantai dua-keadaan</a>',
        "description": "Route the exercise to the deterministic, accessible, offline Indonesian simulator.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "post-ergodic-definition-paragraph",
        "old": r"""</div>

Dalam kasus ergodik, seperti akan kita lihat, \( X_n \) memiliki distribusi limit ketika \( n \to \infty \) yang tidak bergantung pada distribusi awal.

""",
        "new": r"""</div>
<p>Dalam kasus ergodik, seperti akan kita lihat, \( X_n \) memiliki distribusi limit ketika \( n \to \infty \) yang tidak bergantung pada distribusi awal.</p>
""",
        "description": "Wrap the orphan post-definition sentence in a semantic paragraph.",
        "change_kind": "deterministic-output",
    },
    {
        "id": "special-model-list-close",
        "old": r"</ol></div>",
        "new": "</ol>\n</div>",
        "description": "Make the source parser's repair of the missing special-model list close explicit in output.",
        "change_kind": "deterministic-output",
    },
)

POISSON_GENERAL_READER_NOTES = (
    {
        "after_heading": "Teori Dasar",
        "html": r"""<aside class="reader-note reader-correction" id="poisson-general-downstream-corrections">
<strong>Catatan koreksi hilir.</strong> Pembaca ini memperbaiki simbol domain
yang tidak terdefinisi, nomor bagian, hipotesis ukuran hingga untuk momen dan
distribusi bersyarat, urutan parameter pada penipisan, kejadian pengondisian,
domain perhitungan, argumen penandaan berdimensi hingga, dan indeks pada bukti
superposisi, sifat inkremen proses tak homogen, serta simbol ruang dan rumus
norma Euklides. Istilah massa probabilitas diskret, normalisasi ukuran proses
tak homogen, dan asumsi geometri satu latihan juga diperjelas. Terjemahan
sumber tetap mempertahankan permukaan matematika beku; setiap perubahan
pembaca dicatat terpisah dalam backend dan manifes QA.
</aside>""",
    },
)

POISSON_GENERAL_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "poisson-general-set-domain",
        "old": r"\(A \subseteq D\)",
        "new": r"\(A \in \mathscr{S},\ \mu(A) \lt \infty\)",
        "description": "Replace the undefined set D by the finite-measure condition required for finite moments of N(A).",
    },
    {
        "id": "poisson-general-heading-number",
        "old": r"<h2>6. Proses Poisson pada Ruang Umum</h2>",
        "new": r"<h2>8. Proses Poisson pada Ruang Umum</h2>",
        "description": "Align the copied source heading number with current navigation item 8.",
    },
    {
        "id": "poisson-general-single-point-finite-measure",
        "old": r"""<p class="math">Jika diketahui bahwa \(A \in \mathscr{S}\) memuat tepat satu titik acak, maka posisi \(X\) dari titik tersebut berdistribusi seragam pada \(A\).</p>""",
        "new": r"""<p class="math">Misalkan \(A \in \mathscr{S}\) dan \(0 \lt \mu(A) \lt \infty\). Jika diketahui bahwa \(A\) memuat tepat satu titik acak, maka posisi \(X\) dari titik tersebut berdistribusi seragam pada \(A\), yaitu menurut ukuran probabilitas \(\mu(\,\cdot\,\cap A)/\mu(A)\).</p>""",
        "description": "State the finite-positive-measure hypothesis required by the conditional uniform law.",
    },
    {
        "id": "poisson-general-binomial-finite-measure",
        "old": r"""<p class="math">Misalkan \(A, \, B \in \mathscr{S}\) dan \(B \subseteq A\). Untuk \( n \in \N_+ \), distribusi bersyarat \(N(B)\) jika \(N(A) = n\) diketahui adalah <a href="https://www.randomservices.org/random/bernoulli/Binomial.html">distribusi binomial</a> dengan parameter banyak percobaan \(n\) dan parameter sukses \(p = \mu(B) \big/ \mu(A)\).</p>""",
        "new": r"""<p class="math">Misalkan \(A, \, B \in \mathscr{S}\), \(B \subseteq A\), dan \(0 \lt \mu(A) \lt \infty\). Untuk \( n \in \N_+ \), distribusi bersyarat \(N(B)\) jika \(N(A) = n\) diketahui adalah <a href="https://www.randomservices.org/random/bernoulli/Binomial.html">distribusi binomial</a> dengan parameter banyak percobaan \(n\) dan parameter sukses \(p = \mu(B) \big/ \mu(A)\).</p>""",
        "description": "State the finite-positive-measure hypothesis needed to define the conditional binomial parameter.",
    },
    {
        "id": "poisson-general-multinomial-finite-measure",
        "old": r"""<p class="math">Secara lebih umum, misalkan \(A \in \mathscr{S}\) dan \(A\) dipartisi menjadi \(k\) himpunan bagian \((B_1, B_2, \ldots, B_k)\) dalam \( \mathscr{S} \). Maka, distribusi bersyarat \(\left(N(B_1), N(B_2), \ldots, N(B_k)\right)\) jika \(N(A) = n\) diketahui adalah <a href="https://www.randomservices.org/random/bernoulli/Multinomial.html">distribusi multinomial</a> dengan parameter \(n\) dan \((p_1, p_2, \ldots p_k)\), dengan \(p_i = \mu(B_i) \big/ \mu(A)\) untuk \(i \in \{1, 2, \ldots, k\}\).</p>""",
        "new": r"""<p class="math">Secara lebih umum, misalkan \(A \in \mathscr{S}\), \(0 \lt \mu(A) \lt \infty\), dan \(A\) dipartisi menjadi \(k \in \N_+\) himpunan bagian \((B_1, B_2, \ldots, B_k)\) dalam \( \mathscr{S} \). Untuk \(n \in \N_+\), distribusi bersyarat \(\left(N(B_1), N(B_2), \ldots, N(B_k)\right)\) jika \(N(A) = n\) diketahui adalah <a href="https://www.randomservices.org/random/bernoulli/Multinomial.html">distribusi multinomial</a> dengan parameter \(n\) dan \((p_1, p_2, \ldots p_k)\), dengan \(p_i = \mu(B_i) \big/ \mu(A)\) untuk \(i \in \{1, 2, \ldots, k\}\).</p>""",
        "description": "State the finite-positive-measure and integer-domain hypotheses for the conditional multinomial law.",
    },
    {
        "id": "poisson-count-pmf-terminology",
        "old": r"""Perhatikan lokasi dan bentuk fungsi kepadatan probabilitas \(N\). Untuk nilai parameter yang dipilih, jalankan simulasi 1000 kali dan bandingkan fungsi kepadatan empiris dengan fungsi kepadatan probabilitas yang sebenarnya.""",
        "new": r"""Perhatikan lokasi dan bentuk fungsi massa probabilitas \(N\). Untuk nilai parameter yang dipilih, jalankan simulasi 1000 kali dan bandingkan frekuensi relatif empiris dengan fungsi massa probabilitas teoretis.""",
        "description": "Use probability-mass terminology for the discrete Poisson count shown by the simulator.",
    },
    {
        "id": "thinning-rate-order",
        "old": r"""dengan parameter kerapatan masing-masing \( p r \) dan \( (1 - p) r \)""",
        "new": r"""dengan parameter kerapatan masing-masing \( (1 - p) r \) dan \( p r \)""",
        "description": "Assign rate (1-p)r to type 0 and pr to type 1.",
    },
    {
        "id": "thinning-conditioning-event",
        "old": r"\mid N_0(A) = j + k",
        "new": r"\mid N(A) = j + k",
        "description": "Condition the binomial split on the total count rather than the type-0 count.",
    },
    {
        "id": "thinning-finite-measure-proof-domain",
        "old": r"""Buktinya serupa dengan bukti bagi proses Poisson pada \( [0, \infty) \). Untuk \(j, \; k \in \N\),""",
        "new": r"""Buktinya serupa dengan bukti bagi proses Poisson pada \( [0, \infty) \). Tetapkan \(A \in \mathscr{S}\) dengan \(\mu(A) \lt \infty\). Untuk \(j, \; k \in \N\),""",
        "description": "Restrict the displayed finite-parameter Poisson factorization to a finite-measure set.",
    },
    {
        "id": "thinning-proof-rate-labels",
        "old": r"""\( N_0(A) \) mempunyai distribusi Poisson dengan parameter \( p \mu(A) \), \( N_1(A) \) mempunyai distribusi Poisson dengan parameter \( (1 - p) \mu(A) \)""",
        "new": r"""\( N_0(A) \) mempunyai distribusi Poisson dengan parameter \( (1 - p) r \mu(A) \), \( N_1(A) \) mempunyai distribusi Poisson dengan parameter \( p r \mu(A) \)""",
        "description": "Restore the density factor r and associate each marked process with the correct rate.",
    },
    {
        "id": "thinning-process-independence-argument",
        "old": r"""Maka, \( \{N_0(A_i): i \in I\} \) dan \( \{N_1(A_i): i \in I\} \) masing-masing merupakan himpunan peubah acak independen, dan kedua himpunan itu saling independen.""",
        "new": r"""Untuk membuktikan independensi kedua ukuran acak, terapkan perhitungan penandaan yang sama secara bersama pada setiap keluarga berhingga himpunan dengan ukuran \(\mu\) berhingga, setelah keluarga itu diuraikan menjadi atom-atom saling lepas. Fungsi massa gabungannya memfaktor menurut tipe dan atom; karena itu \( \{N_0(A_i): i \in I\} \) dan \( \{N_1(A_i): i \in I\} \) masing-masing merupakan himpunan peubah acak independen, dan kedua proses itu saling independen. Himpunan \(A\) dengan \(\mu(A)=\infty\) mengikuti konvensi cacah degenerat pada halaman ini.""",
        "description": "Upgrade the single-set calculation to the finite-dimensional marking argument required for process independence.",
    },
    {
        "id": "superposition-process-index",
        "old": r"\( N = N_1 + N_2 \)",
        "new": r"\( N = N_0 + N_1 \)",
        "description": "Use the two processes introduced in the superposition theorem.",
    },
    {
        "id": "superposition-count-index",
        "old": r"\( N(A) = N_1(A) + N_2(A) \)",
        "new": r"\( N(A) = N_0(A) + N_1(A) \)",
        "description": "Use the introduced process indices in the setwise count identity.",
    },
    {
        "id": "superposition-index-set",
        "old": r"\( i \in \{1, 2\} \)",
        "new": r"\( i \in \{0, 1\} \)",
        "description": "Quantify over the introduced process indices 0 and 1.",
    },
    {
        "id": "superposition-finite-infinite-measure-proof",
        "old": r"""Jadi, untuk \( A \in \mathscr{S} \), \( N(A) = N_0(A) + N_1(A) \). Namun, \( N_i(A) \) mempunyai distribusi Poisson dengan parameter \( r_i \mu(A) \) untuk \( i \in \{0, 1\} \), dan peubah-peubah tersebut independen, sehingga \( N(A) \) mempunyai distribusi Poisson dengan parameter \( r_0 \mu(A) + r_1 \mu(A) = (r_0 + r_1)\mu(A) \).""",
        "new": r"""Jika \( A \in \mathscr{S} \) dan \(\mu(A) \lt \infty\), maka \( N(A) = N_0(A) + N_1(A) \). Karena \( N_i(A) \) mempunyai distribusi Poisson dengan parameter \( r_i \mu(A) \) untuk \( i \in \{0, 1\} \), dan peubah-peubah tersebut independen, konvolusi Poisson memberi distribusi Poisson bagi \( N(A) \) dengan parameter \( r_0 \mu(A) + r_1 \mu(A) = (r_0 + r_1)\mu(A) \). Jika \(\mu(A)=\infty\), kesimpulan cacah mengikuti konvensi degenerat pada halaman ini; independensi inkremen untuk keluarga himpunan saling lepas mengikuti dengan menerapkan argumen ini pada setiap subkeluarga berhingga yang semua himpunannya mempunyai ukuran \(\mu\) berhingga.""",
        "description": "Separate the finite-parameter Poisson convolution from the page's infinite-measure convention.",
    },
    {
        "id": "nonhomogeneous-independent-increments",
        "old": r"""\( N \) mempunyai inkremen stasioner, dan""",
        "new": r"""\( N \) mempunyai inkremen independen, dan""",
        "description": "A non-homogeneous Poisson process has independent but generally non-stationary increments.",
    },
    {
        "id": "nonhomogeneous-unit-density",
        "old": r"""<p class="math">Proses Poisson tak homogen pada \( [0, \infty) \) dengan fungsi laju \( r \) adalah proses Poisson pada \( [0, \infty) \) terhadap ukuran \( m \).</p>""",
        "new": r"""<p class="math">Proses Poisson tak homogen pada \( [0, \infty) \) dengan fungsi laju \( r \) adalah proses Poisson pada \( [0, \infty) \) dengan parameter kerapatan 1 terhadap ukuran \( m \).</p>""",
        "description": "State the unit density relative to the mean measure m, avoiding a second unstated intensity factor.",
    },
    {
        "id": "euclidean-space-symbol",
        "old": r"\( \R_d \)",
        "new": r"\( \R^d \)",
        "description": "Use the declared d-dimensional Euclidean-space symbol.",
    },
    {
        "id": "euclidean-norm-definition",
        "old": r"""\[ \|\bs{x}\|_d = \left(x_1^d + x_2^d \cdots + x_d^d\right)^{1/d}, \quad \bs{x} = (x_1, x_2, \ldots, x_d) \in \R^d \]""",
        "new": r"""\[ \|\bs{x}\|_2 = \left(x_1^2 + x_2^2 + \cdots + x_d^2\right)^{1/2}, \quad \bs{x} = (x_1, x_2, \ldots, x_d) \in \R^d \]""",
        "description": "Replace the malformed dimension-dependent expression by the Euclidean 2-norm.",
    },
    {
        "id": "euclidean-ball-norm",
        "old": r"\|\bs{x}\|_d \le t",
        "new": r"\|\bs{x}\|_2 \le t",
        "description": "Use the corrected Euclidean norm in the ball definition.",
    },
    {
        "id": "poisson2d-explicit-online-source",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/Poisson2D.html">proses Poisson dua dimensi</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/Poisson2D.html">aplikasi resmi daring proses Poisson dua dimensi</a>',
        "matches": 2,
        "description": "Make both retained external interactive surfaces explicit instead of implying offline inclusion.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "exercise4-contained-circle-assumption",
        "old": r"""Tentukan probabilitas bahwa cacat tersebut berada dalam daerah lingkaran pada bahan itu dengan jari-jari \(\frac{1}{4}\) meter.""",
        "new": r"""Tentukan probabilitas bahwa cacat tersebut berada dalam daerah lingkaran berjari-jari \(\frac{1}{4}\) meter yang seluruhnya terletak di dalam lembaran bahan itu.""",
        "description": "State the containment assumption required for the displayed area-ratio answer.",
    },
)

BROWN_STANDARD_READER_NOTES = (
    {
        "after_heading": "Teori Dasar",
        "html": r"""<aside class="reader-note reader-correction" id="brown-standard-downstream-corrections">
<strong>Catatan koreksi hilir.</strong> Terjemahan sumber mempertahankan struktur
dan permukaan matematika halaman beku. Lapisan pembaca ini memperbaiki salah
cetak simbol dan rujukan, melengkapi bukti yang terpotong, menyatakan domain
dan syarat filtrasi yang diperlukan, memperbaiki pembuktian kontinuitas dan
kesempurnaan himpunan nol, serta memberi lingkup hampir pasti pada hasil
regularitas. Hasil ketakterdiferensialan, dimensi Hausdorff, dan hukum
logaritma berulang tetap ditandai sebagai hasil lanjut yang dinyatakan tanpa
bukti lengkap pada sumber. Satu simulator gerak Brown pada halaman ini bekerja
secara luring; dua belas tautan simulator Random lainnya diberi label jelas
sebagai aplikasi resmi daring.
</aside>""",
    },
    {
        "after_heading": "Latihan Komputasi",
        "html": r"""<aside class="reader-original-solution" id="brown-standard-exercise-solution">
<details>
<summary>Jawaban dan solusi</summary>
<p><strong>Status.</strong> Halaman sumber tidak menyediakan jawaban untuk latihan
ini. Penutupan berikut merupakan solusi asli edisi ini, dilisensikan CC BY 4.0,
dan bukan bagian dari halaman Random.</p>
<p>Vektor inkremen
\[ \left(X_{0.5},\;X_1-X_{0.5},\;X_{2.3}-X_1\right) \]
terdiri atas peubah normal yang saling bebas dengan varians berturut-turut
\(\frac12,\frac12,\frac{13}{10}\). Jadi, untuk
\(x=(x_1,x_2,x_3)\in\R^3\), fungsi kepadatannya ialah
\[ f(x)=\frac{1}{(2\pi)^{3/2}\sqrt{13/40}}
\exp\!\left[-\frac12\left(\frac{x_1^2}{1/2}
+\frac{(x_2-x_1)^2}{1/2}
+\frac{(x_3-x_2)^2}{13/10}\right)\right]. \]</p>
<p>Karena \(\cov(X_s,X_t)=\min\{s,t\}\), matriks kovarians dan
korelasinya adalah
\[ \Sigma=\begin{pmatrix}
1/2 &amp; 1/2 &amp; 1/2\\
1/2 &amp; 1 &amp; 1\\
1/2 &amp; 1 &amp; 23/10
\end{pmatrix},\qquad
R=\begin{pmatrix}
1 &amp; 1/\sqrt2 &amp; \sqrt{5/23}\\
1/\sqrt2 &amp; 1 &amp; \sqrt{10/23}\\
\sqrt{5/23} &amp; \sqrt{10/23} &amp; 1
\end{pmatrix}. \]</p>
</details>
</aside>""",
    },
)

BROWN_STANDARD_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "offline-simulator-accessible-controls",
        "old": r"""const runButton = new RunButton(this.toolbar, this.name);
				const stopButton = new StopButton(this.toolbar, this.name);
				const resetButton = new ResetButton(this.toolbar, this.name);
				this.graph = new Canvas(this.graphs, 200, 200, "Lintasan sampel");""",
        "new": r"""const runButton = new RunButton(this.toolbar, this.name);
				const stopButton = new StopButton(this.toolbar, this.name);
				const resetButton = new ResetButton(this.toolbar, this.name);
				for (const [control, label] of [[runButton, "Jalankan"], [stopButton, "Hentikan"], [resetButton, "Atur ulang"]]) {
					control.button.title = label;
					control.button.setAttribute("aria-label", label);
					const icon = control.button.querySelector("svg");
					if (icon) icon.setAttribute("aria-hidden", "true");
				}
				this.graph = new Canvas(this.graphs, 200, 200, "Lintasan sampel");
				this.graph.svg.setAttribute("role", "img");
				this.graph.svg.setAttribute("aria-label", "Lintasan sampel gerak Brown yang disimulasikan");""",
        "description": "Localize the offline simulator controls and expose the generated SVG graph to assistive technology.",
        "change_kind": "accessibility-localization",
    },
    {
        "id": "continuous-version-proof",
        "old": r"""<p>Asumsi-asumsi dalam definisi <a class="ref" href="#def1"></a> menghasilkan sekumpulan distribusi berdimensi hingga yang konsisten (yang diberikan dalam <a class="ref" href="#dis1"></a>). Karena itu, menurut <a href="../prob/Processes.html">teorema eksistensi Kolmogorov</a>, terdapat proses stokastik \( \bs{U} = \{U_t: t \in [0, \infty)\} \) yang mempunyai distribusi-distribusi berdimensi hingga tersebut. Akan tetapi, \( \bs{U} \) tidak mempunyai lintasan sampel kontinu; dari \( \bs{U} \), kita dapat mengonstruksi proses ekuivalen yang mempunyai lintasan sampel kontinu.</p>
<p>Pertama, <a href="https://www.randomservices.org/random/foundations/Sets.html#dyr">ingatlah</a> bahwa <dfn>rasional biner</dfn> (atau <dfn>rasional diadik</dfn>) dalam \( [0, \infty) \) adalah bilangan berbentuk \( k / 2^n \), dengan \( k, \, n \in \N \). Misalkan \( \D_+ \) menyatakan himpunan semua rasional biner dalam \( [0, \infty) \), dan ingat bahwa \( \D_+ \) terhitung tetapi juga <dfn>rapat</dfn> dalam \( [0, \infty) \) (artinya, jika \( t \in [0, \infty) \setminus \D_+ \), maka terdapat \( t_n \in \D_+ \) untuk \( n \in \N_+ \) sedemikian sehingga \( t_n \to t \) ketika \( n \to \infty \)).</p>
<p>Sekarang, untuk \( n \in \N_+ \), tetapkan \( X_n(t) = U_t \) apabila \( t \) adalah rasional biner berbentuk \( k \big/ 2^n \) untuk suatu \( k \in \N \). Jika \( t \) bukan rasional biner semacam itu, definisikan \( X_n(t) \) melalui interpolasi linear di antara dua rasional biner terdekat yang berbentuk demikian, masing-masing di satu sisi \( t \). Maka \( X_n(t) \to U(t) \) ketika \( n \to \infty \) untuk setiap \( t \in \D_+\), dan dengan probabilitas 1, konvergensinya seragam pada \( \D_+ \cap [0, T] \) untuk setiap \( T \gt 0 \). Selanjutnya diperoleh bahwa \( \bs{U} \) kontinu pada \( \D_+ \) dengan probabilitas 1.</p>
<p>Untuk langkah terakhir, tetapkan \( X_t = \lim_{s \to t, \; s \in \D_+} U_s \) untuk \( t \in [0, \infty) \). Limit tersebut ada karena \( \bs{U} \) kontinu pada \( \D_+ \) dengan probabilitas 1. Proses \( \bs{X} = \{X_t: t \in [0, \infty)\} \) kontinu pada \( [0, \infty) \) dengan probabilitas 1 dan mempunyai distribusi berdimensi hingga yang sama dengan \( \bs{U} \).</p>""",
        "new": r"""<p>Asumsi-asumsi dalam definisi <a class="ref" href="#def1"></a> menentukan keluarga distribusi berdimensi hingga yang konsisten, sebagaimana diberikan dalam <a class="ref" href="#dis1"></a>. Teorema ekstensi Kolmogorov karena itu menghasilkan proses stokastik \(\bs{U}=\{U_t:t\in[0,\infty)\}\) dengan distribusi berdimensi hingga tersebut. Teorema ekstensi itu sendiri belum menjamin kontinuitas lintasan sampel; yang diperlukan ialah modifikasi kontinu dari \(\bs{U}\).</p>
<p>Untuk \(0\le s\lt t\), inkremen \(U_t-U_s\) berdistribusi normal dengan rataan 0 dan varians \(t-s\), sehingga
\[ \E\!\left(\lvert U_t-U_s\rvert^4\right)=3(t-s)^2. \]
Kriteria kontinuitas Kolmogorov kemudian memberikan modifikasi \(\bs{X}\) yang lintasan sampelnya kontinu—bahkan kontinu Hölder lokal dengan setiap eksponen \(\alpha\lt\tfrac14\)—pada setiap selang terbatas \([0,T]\), dengan probabilitas 1. Dengan mengambil irisan atas \(T\in\N_+\), lintasan \(\bs{X}\) kontinu pada seluruh \([0,\infty)\) dengan probabilitas 1. Karena modifikasi mempunyai distribusi berdimensi hingga yang sama dengan \(\bs{U}\), proses \(\bs{X}\) memenuhi semua syarat dalam definisi <a class="ref" href="#def1"></a>.</p>""",
        "description": "Replace the unsupported claim about the canonical version and the incomplete dyadic sketch by the standard fourth-moment continuity argument.",
    },
    {
        "id": "finite-dimensional-time-order",
        "old": r"0 \lt t_1 \lt t_2 \cdots \lt t_n",
        "new": r"0 \lt t_1 \lt t_2 \lt \cdots \lt t_n",
        "description": "Restore the missing inequality sign in the ordered time tuple.",
    },
    {
        "id": "gaussian-process-time-domain",
        "old": r"\(t \in T\)",
        "new": r"\(t \in [0, \infty)\)",
        "description": "Replace the undefined time set T by this page's declared index set.",
    },
    {
        "id": "brownian-correlation-max-domain",
        "old": r"""\[ \cor(X_s, X_t) = \frac{\min\{s, t\}}{\sqrt{s t}} = \sqrt{\frac{\min\{s, t\}}{\5\{s, t\}}}  ,\quad (s, t) \in [0, \infty)^2 \]""",
        "new": r"""\[ \cor(X_s, X_t) = \frac{\min\{s, t\}}{\sqrt{s t}} = \sqrt{\frac{\min\{s, t\}}{\max\{s, t\}}}, \quad (s, t) \in (0, \infty)^2 \]""",
        "description": "Restore max and exclude zero times, where correlation is undefined.",
    },
    {
        "id": "normal-mgf-square",
        "old": r"e^{t u / 2}",
        "new": r"e^{t u^2 / 2}",
        "description": "Restore the square in the centered normal moment-generating function.",
    },
    {
        "id": "time-reversal-covariance",
        "old": r"""\cov(X_{T - s} - X_T, X_{T-t} - X_t) = \cov(X_{T-s}, X_{T-t}) - \cov(X_{T-s}, X_T) - \cov(X_T, X_{T-t}) + \cov(X_T, X_t)""",
        "new": r"""\cov(X_{T - s} - X_T, X_{T-t} - X_T) = \cov(X_{T-s}, X_{T-t}) - \cov(X_{T-s}, X_T) - \cov(X_T, X_{T-t}) + \cov(X_T, X_T)""",
        "description": "Use X_T in both centered variables and in the final covariance term.",
    },
    {
        "id": "brownian-scaling-mean",
        "old": r"\( \E(Y_t) = a \E(X_{a^2 t}) = 0 \)",
        "new": r"\( \E(Y_t) = a^{-1} \E(X_{a^2 t}) = 0 \)",
        "description": "Use the reciprocal spatial scale in the transformed mean.",
    },
    {
        "id": "self-similarity-law-not-path",
        "old": r"""Karena grafik tidak berubah oleh transformasi ini, gerak Brown memiliki sifat fraktal yang serupa diri.""",
        "new": r"""Karena hukum proses—bukan setiap grafik individual—tetap sama di bawah transformasi ini, gerak Brown memiliki sifat fraktal yang serupa diri secara distribusional.""",
        "description": "State scaling invariance in distribution rather than pathwise invariance.",
    },
    {
        "id": "holder-exponent-scope-endpoint",
        "old": r"""<p class="math">Gerak Brown standar \( \bs{X} \) mempunyai <a href="https://www.randomservices.org/random/foundations/Metric.html#hol">eksponen Hölder</a> \( \frac{1}{2} \). Artinya, \( \bs{X} \) kontinu Hölder dengan eksponen \( \alpha \) untuk setiap \( \alpha \lt \frac{1}{2} \), tetapi tidak kontinu Hölder dengan eksponen \( \alpha \) untuk \( \alpha \gt \frac{1}{2} \) mana pun.</p>""",
        "new": r"""<p class="math">Dengan probabilitas 1, pada setiap selang waktu terbatas, lintasan gerak Brown standar \(\bs{X}\) kontinu Hölder dengan setiap eksponen \(\alpha\) yang memenuhi \(0\lt\alpha\lt\frac12\), tetapi tidak kontinu Hölder dengan eksponen \(\alpha\ge\frac12\) pada selang mana pun yang panjangnya positif. Jadi, eksponen Hölder—sebagai supremum eksponen yang berlaku—adalah \(\frac12\), meskipun nilai batas itu tidak tercapai.</p>""",
        "description": "Add the almost-sure local scope and exclude the unattained alpha=1/2 endpoint.",
    },
    {
        "id": "brownian-graph-dimension-scope",
        "old": r"""<p class="math">Grafik gerak Brown standar mempunyai dimensi Hausdorff \( \frac{3}{2} \).</p>""",
        "new": r"""<p class="math">Dengan probabilitas 1, grafik gerak Brown standar mempunyai dimensi Hausdorff \(\frac32\).</p>""",
        "description": "State the almost-sure scope of the Hausdorff-dimension theorem.",
    },
    {
        "id": "brownian-total-variation-domain-scope",
        "old": r"""<p class="math">Misalkan \( a, \, b \in \R \) dengan \( a \lt b \). Maka variasi total \( \bs{X} \) pada \( [a, b] \) adalah \( \infty \).</p>""",
        "new": r"""<p class="math">Dengan probabilitas 1, untuk setiap \(0\le a\lt b\lt\infty\), variasi total \(\bs{X}\) pada \([a,b]\) adalah \(\infty\).</p>""",
        "description": "Restrict the theorem to the process time domain and state its almost-sure scope.",
    },
    {
        "id": "markov-proof-truncated-filtration",
        "old": r"""<p>Tetapkan \( s \in [0, \infty) \). Teorema ini mengikuti fakta bahwa proses \( \{X_{s+t} - X_s: t \in [0, \infty)\} \) merupakan gerak Brown standar lain, seperti ditunjukkan dalam <a class="ref" href="#trn2"></a>, dan saling bebas dengan \( \mathscr{F}
	</p>""",
        "new": r"""<p>Tetapkan \(s\in[0,\infty)\). Teorema ini mengikuti fakta bahwa proses \(\{X_{s+t}-X_s:t\in[0,\infty)\}\) merupakan gerak Brown standar lain, seperti ditunjukkan dalam <a class="ref" href="#trn2"></a>, dan saling bebas dengan \(\mathscr F_s\).</p>""",
        "description": "Complete the source-truncated Markov proof and close its TeX surface.",
    },
    {
        "id": "strong-markov-filtration-scope",
        "old": r"""<p><dfn>Sifat Markov kuat</dfn> adalah sifat Markov yang diperumum untuk waktu henti. Gerak Brown standar \( \bs{X} \) juga merupakan proses Markov kuat. Cara terbaik untuk menyatakannya adalah melalui perumuman <a class="ref" href="#trn2"></a>.</p>""",
        "new": r"""<p><dfn>Sifat Markov kuat</dfn> adalah sifat Markov yang diperumum untuk waktu henti. Mulai dari sini, \(\mathfrak F=\{\mathscr F_t:t\ge0\}\) menyatakan filtrasi alami gerak Brown yang telah dilengkapi dan dibuat kontinu dari kanan, yaitu filtrasi Brown biasa. Dengan konvensi ini, sifat Markov kuat dapat dinyatakan sebagai perumuman <a class="ref" href="#trn2"></a>.</p>""",
        "description": "State the usual augmented right-continuous Brownian filtration required by the strong Markov theorem.",
    },
    {
        "id": "strong-markov-finite-stopping-time",
        "old": r"""<p class="math">Misalkan \( \tau \) adalah waktu henti dan definisikan \( Y_t = X_{\tau + t} - X_\tau \) untuk \( t \in [0, \infty) \). Maka \( \bs{Y} = \{Y_t: t \in [0, \infty)\} \) merupakan gerak Brown standar dan saling bebas dengan \( \mathscr{F}_\tau \).</p>""",
        "new": r"""<p class="math">Misalkan \(\tau\) adalah waktu henti terhadap \(\mathfrak F\) dan \(\P(\tau\lt\infty)=1\). Definisikan \(Y_t=X_{\tau+t}-X_\tau\) untuk \(t\in[0,\infty)\). Maka \(\bs Y=\{Y_t:t\in[0,\infty)\}\) merupakan gerak Brown standar dan saling bebas dengan \(\mathscr F_\tau\).</p>""",
        "description": "Require an almost-surely finite stopping time so X_tau is defined.",
    },
    {
        "id": "conditional-second-moment-square",
        "old": r"\E\left[(X_t - X_s)\right]^2",
        "new": r"\E\left[(X_t - X_s)^2\right]",
        "description": "Put the square inside the conditional second-moment expectation.",
    },
    {
        "id": "hitting-time-and-running-maximum-definition",
        "old": r"""Untuk \( y \in [0, \infty) \), ingat bahwa \( \tau_y = \min\{t \ge 0: X_t = y\} \) adalah waktu pertama proses mencapai keadaan \( y \). Tentu saja, \( \tau_0 = 0 \). Untuk \( t \in [0, \infty) \), misalkan \( Y_t = \5\{X_s: 0 \le s \le t\} \), yaitu nilai maksimum \( \bs{X} \) pada selang \( [0, t] \).""",
        "new": r"""Untuk \(y\in[0,\infty)\), ingat bahwa \(\tau_y=\inf\{t\ge0:X_t=y\}\), dengan konvensi \(\inf\varnothing=\infty\), adalah waktu pertama proses mencapai keadaan \(y\). Tentu saja, \(\tau_0=0\). Untuk \(t\in[0,\infty)\), misalkan \(Y_t=\max\{X_s:0\le s\le t\}\), yaitu nilai maksimum \(\bs{X}\) pada selang \([0,t]\).""",
        "description": "Use an extended hitting-time definition and restore the maximum operator.",
    },
    {
        "id": "recurrence-proof-reference",
        "old": r'<a class="ref" href="#max3"></a>',
        "new": r'<a class="ref" href="#max2"></a>',
        "description": "Point the recurrence proof to the hitting-time distribution theorem rather than an app prompt.",
    },
    {
        "id": "hitting-filtration-subscript",
        "old": r"\( \mathscr{F}(\tau_x) \)",
        "new": r"\( \mathscr{F}_{\tau_x} \)",
        "matches": 2,
        "description": "Use the stopped sigma-algebra notation defined earlier on the page.",
    },
    {
        "id": "half-normal-scale-parameter",
        "old": r"distribusi setengah-normal</dfn> dengan parameter skala \( t \)",
        "new": r"distribusi setengah-normal</dfn> dengan parameter skala \( \sqrt{t} \)",
        "description": "Use the standard-deviation scale parameter rather than the variance.",
    },
    {
        "id": "half-normal-scale-proof",
        "old": r"\( \left|X_t\right| \) berdistribusi setengah-normal dengan parameter \( t \)",
        "new": r"\( \left|X_t\right| \) berdistribusi setengah-normal dengan parameter skala \( \sqrt{t} \)",
        "description": "Keep the half-normal parameterization consistent in the proof.",
    },
    {
        "id": "hitting-reflection-finite-stopping-scope",
        "old": r"""Namun, berdasarkan sifat Markov kuat <a class="ref" href="#mar3"></a>, \( s \mapsto X(\tau_y + s) - y \) merupakan gerak Brown standar lain. Jadi, \( \P(X_t \ge y \mid \tau_y \le t) = \frac{1}{2} \). Oleh karena itu,""",
        "new": r"""Terapkan sifat Markov kuat <a class="ref" href="#mar3"></a> pada waktu henti terbatas \(\sigma=\tau_y\wedge t\). Pada kejadian \(\{\tau_y\lt t\}\), proses setelah \(\tau_y\) bermula dari \(y\), saling bebas dengan masa lalu, dan mempunyai inkremen normal yang simetris. Selain itu, \(\P(\tau_y=t)\le\P(X_t=y)=0\). Karena itu, \(\P(X_t\ge y\mid\tau_y\le t)=\frac12\). Oleh karena itu,""",
        "description": "Avoid circularly assuming that tau_y is finite before recurrence has been proved by stopping at tau_y wedge t.",
    },
    {
        "id": "arcsine-zero-event-proof",
        "old": r"""<p class="math">Untuk \( s, \; t \in [0, \infty) \) dengan \( s \lt t \), misalkan \( E(s, t) \) adalah kejadian bahwa \( \bs{X} \) mempunyai nol dalam selang waktu \( (s, t) \). Artinya, \( \E(s, t) = \{X_u = 0 \text{ untuk suatu } u \in (s, t)\} \). Maka
	\[ \P\left[E(s, t)\right] = 1 - \frac{2}{\pi} \arcsin\left(\sqrt{\frac{s}{t}}\right) \]</p>
<details>
<summary>Rincian:</summary>
<p>Pengondisian pada \( X_s \) dan penggunaan simetri memberikan
		\[ \P\left[E(s, t)\right] = \int_{-\infty}^\infty \P\left[E(s, t) \mid X_s = x\right] f_s(x) \, dx = 2 \int_{-\infty}^0 \P\left[E(s, t) \mid X_s = x\right] f_s(x) \, dx \]
		Namun, berdasarkan homogenitas waktu dan ruang \( \bs{X} \), perhatikan bahwa untuk \( x \gt 0 \), \( \P\left[E(s, t) \mid X_s = -x\right] = \P(\tau_x \lt t - s) \). Artinya, proses yang berada pada keadaan \( -x \) pada waktu \( s \) dan mencapai 0 sebelum waktu \( t \) sama dengan proses yang berada pada keadaan 0 pada waktu 0 dan mencapai keadaan \( x \) sebelum waktu \( t - s \). Karena itu,
		\[ \P\left[E(s, t)\right] = \int_0^\infty \int_0^{t-s} g_x(u) f_s(-x) \, du \, dx \]
		dengan \( g_x \) fungsi kepadatan probabilitas \( \tau_x \) dari <a class="ref" href="#max2"></a>. Substitusi memberikan
		\[ \P\left[E(s, t)\right] = \frac{1}{\pi \sqrt{s}} \int_0^{t-s} u^{-3/2} \int_0^\infty x \exp\left[-\frac{1}{2} x^2 \left(\frac{u + s}{u s} \right) \right] \, dx \, du = \frac{\sqrt{s}}{\pi} \int_0^{t-s} \frac{1}{(u + s) \sqrt{u}} \, du\]
		Terakhir, substitusi \( v = \sqrt{u / s} \) pada integral terakhir memberikan
		\[ \P\left[E(s, t)\right] = \frac{2}{\pi} \int_0^{\sqrt{t/s - 1}} \frac{1}{v^2 + 1} \, dv = \frac{2}{\pi} \arctan \left(\sqrt{\frac{t}{s} - 1}\right) = 1 - \frac{2}{\pi} \arcsin\left(\sqrt{\frac{s}{t}} \right) \]</p>
</details>""",
        "new": r"""<p class="math">Untuk \(0\le s\lt t\), misalkan \(E(s,t)\) adalah kejadian bahwa \(\bs X\) mempunyai nol dalam selang waktu \((s,t)\), yaitu
\[ E(s,t)=\{X_u=0\text{ untuk suatu }u\in(s,t)\}. \]
Maka
\[ \P[E(s,t)]=1-\frac{2}{\pi}\arcsin\!\left(\sqrt{\frac{s}{t}}\right). \]</p>
<details>
<summary>Rincian:</summary>
<p>Anggap terlebih dahulu \(0\lt s\lt t\). Dengan mengondisikan pada \(X_s\) dan menggunakan simetri,
\[ \P[E(s,t)]=2\int_{-\infty}^{0}\P[E(s,t)\mid X_s=x]f_s(x)\,dx. \]
Berdasarkan homogenitas waktu dan ruang, untuk \(x\gt0\),
\[ \P[E(s,t)\mid X_s=-x]=\P(\tau_x\lt t-s). \]
Karena itu,
\[ \P[E(s,t)]=2\int_0^\infty\int_0^{t-s}g_x(u)f_s(-x)\,du\,dx. \]
Dengan menyubstitusikan kepadatan \(g_x\) dan \(f_s\), diperoleh
\[ \P[E(s,t)]=\frac{1}{\pi\sqrt{s}}\int_0^{t-s}u^{-3/2}\int_0^\infty x\exp\!\left[-\frac{x^2}{2}\left(\frac{u+s}{us}\right)\right]dx\,du
=\frac{\sqrt{s}}{\pi}\int_0^{t-s}\frac{du}{(u+s)\sqrt{u}}. \]
Substitusi \(v=\sqrt{u/s}\) memberikan
\[ \P[E(s,t)]=\frac{2}{\pi}\arctan\!\sqrt{\frac{t}{s}-1}
=1-\frac{2}{\pi}\arcsin\!\sqrt{\frac{s}{t}}. \]
Untuk \(s=0\), ambil \(s_n\downarrow0\). Karena \(E(s_n,t)\uparrow E(0,t)\), kontinuitas probabilitas dari bawah memberikan \(\P[E(0,t)]=1\), sesuai dengan rumus yang sama.</p>
</details>""",
        "description": "Use the event symbol E, restore the factor two, keep f_0 out of the proof, and handle s=0 by monotone continuity.",
    },
    {
        "id": "arcsine-complement-delimiter",
        "old": r"\( \lef[E(s, t)\right]^c \)",
        "new": r"\( \left[E(s, t)\right]^c \)",
        "description": "Repair the malformed left delimiter in the complement event.",
    },
    {
        "id": "last-zero-event-endpoint",
        "old": r"""<p>Untuk \( 0 \le s \lt t \), kejadian \( Z_t \le s \) sama dengan \( \left[E(s, t)\right]^c \), yaitu tidak adanya nol dalam selang \( (s, t) \). Karena itu, rumus untuk \( H_t \) mengikuti <a class="ref" href="#arc1"></a>. Menurunkan \( H_t \) dan menyederhanakannya menghasilkan rumus untuk \( h_t \).</p>""",
        "new": r"""<p>Untuk \(0\le s\lt t\), kejadian \(\{Z_t\le s\}\) berarti tidak ada nol dalam \((s,t]\). Karena \(\P(X_t=0)=0\), probabilitas kejadian ini sama dengan \(\P\!\left(\left[E(s,t)\right]^c\right)\). Karena itu, rumus untuk \(H_t\) mengikuti <a class="ref" href="#arc1"></a>. Menurunkan \(H_t\) dan menyederhanakannya menghasilkan rumus untuk \(h_t\).</p>""",
        "description": "Use the exact half-open last-zero event and only identify its probability with the open-interval complement.",
    },
    {
        "id": "arcsine-variance-label",
        "old": r"\( \E(Z_t) = t^2 / 8 \)",
        "new": r"\( \var(Z_t) = t^2 / 8 \)",
        "description": "Label the second arcsine moment as variance.",
    },
    {
        "id": "zero-set-perfect-proof",
        "old": r"""<li>Misalkan \( s \in Z \). Maka, berdasarkan <a class="ref" href="#trn1"></a>, \( t \mapsto X_{s + t} \) juga merupakan gerak Brown standar. Namun, menurut <a class="ref" href="#arc2"></a>, dengan probabilitas 1, \( \bs{X} \) mempunyai nol dalam selang \( (s, s + 1 / n) \) untuk setiap \( n \in \N_+ \). Jadi, \( s \) bukan titik terisolasi dari \( Z \).</li>""",
        "new": r"""<li>Untuk setiap \(q\in\mathbb Q\cap[0,\infty)\), definisikan waktu henti \(\sigma_q=\inf\{t\ge q:X_t=0\}\). Menurut <a class="ref" href="#arc1"></a>, dengan membiarkan \(t\to\infty\), diperoleh \(\P(\sigma_q\lt\infty)=1\). Karena itu sifat Markov kuat dapat diterapkan pada \(\sigma_q\), dan \(u\mapsto X_{\sigma_q+u}-X_{\sigma_q}\) merupakan gerak Brown standar. Menurut <a class="ref" href="#arc2"></a>, proses ini mempunyai nol dalam \((0,1/n)\) untuk setiap \(n\in\N_+\), dengan probabilitas 1. Karena pasangan \((q,n)\) yang digunakan terhitung, pernyataan tersebut berlaku serentak untuk semuanya di luar satu himpunan nol. Jika suatu \(s\gt0\) merupakan titik nol terisolasi, pilih rasional \(q\lt s\) sedemikian sehingga tidak ada nol dalam \([q,s)\); maka \(\sigma_q=s\), bertentangan dengan adanya nol segera di sebelah kanan \(s\). Titik 0 juga bukan titik terisolasi menurut <a class="ref" href="#arc2"></a>. Jadi \(Z\) tidak mempunyai titik terisolasi; bersama ketertutupannya, hal ini membuktikan bahwa \(Z\) sempurna dengan probabilitas 1.</li>""",
        "description": "Replace the invalid random-time shift argument by a countable stopping-time/strong-Markov proof.",
    },
    {
        "id": "zero-set-dimension-scope",
        "old": r"""<p class="math">\( Z \) mempunyai dimensi Hausdorff \(\frac{1}{2}\).</p>""",
        "new": r"""<p class="math">Dengan probabilitas 1, \(Z\) mempunyai dimensi Hausdorff \(\frac12\).</p>""",
        "description": "State the almost-sure scope of the zero-set dimension theorem.",
    },
    {
        "id": "iterated-logarithm-two-sided",
        "old": r"""<p class="math">Dengan probabilitas 1,
	\[ \limsup_{t \to \infty} \frac{X_t}{\sqrt{2 t \ln \ln t}} = 1 \]</p>""",
        "new": r"""<p class="math">Dengan probabilitas 1,
\begin{align}
\limsup_{t\to\infty}\frac{X_t}{\sqrt{2t\ln\ln t}} &amp;=1,\\
\liminf_{t\to\infty}\frac{X_t}{\sqrt{2t\ln\ln t}} &amp;=-1.
\end{align}</p>
<details id="lil1-consequence">
<summary>Konsekuensi</summary>
<p>Kedua batas tersebut khususnya menyiratkan \(X_t/t\to0\) ketika \(t\to\infty\). Inilah batas dua sisi yang digunakan untuk membuktikan kontinuitas transformasi inversi waktu pada \(t=0\).</p>
</details>""",
        "description": "Give the two-sided LIL and make explicit the consequence used earlier by time inversion.",
    },
    {
        "id": "brownian-motion-apps-explicit-online",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/BrownianMotion.html">proses gerak Brown standar</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/BrownianMotion.html">simulator resmi daring gerak Brown standar</a>',
        "matches": 3,
        "description": "Label all three retained process prompts as official online simulators.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "random-walk-app-explicit-online",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/RandomWalk.html">proses gerak acak</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/RandomWalk.html">simulator resmi daring gerak acak</a>',
        "description": "Label the retained random-walk prompt as an official online simulator.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "reflected-brownian-apps-explicit-online",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/ReflectedBrownianMotion.html">gerak Brown tercermin</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/ReflectedBrownianMotion.html">simulator resmi daring gerak Brown tercermin</a>',
        "matches": 2,
        "description": "Label both retained reflected-Brownian prompts as official online simulators.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "reflected-brownian-process-app-explicit-online",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/ReflectedBrownianMotion.html">proses gerak Brown tercermin</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/ReflectedBrownianMotion.html">simulator resmi daring gerak Brown tercermin</a>',
        "description": "Label the retained reflected-process prompt as an official online simulator.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "special-distribution-apps-explicit-online",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/SpecialSimulator.html">simulator distribusi khusus</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/SpecialSimulator.html">simulator resmi daring distribusi khusus</a>',
        "matches": 3,
        "description": "Label all three retained special-distribution prompts as official online simulators.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "brownian-simulation-app-explicit-online",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/BrownianMotion.html">simulasi gerak Brown standar</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/BrownianMotion.html">simulator resmi daring gerak Brown standar</a>',
        "description": "Label the retained running-maximum prompt as an official online simulator.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "brownian-zero-app-explicit-online",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/BrownianMotion.html">gerak Brown standar</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/BrownianMotion.html">simulator resmi daring gerak Brown standar</a>',
        "description": "Label the retained last-zero prompt as an official online simulator.",
        "change_kind": "source-link-repair",
    },
)

BROWN_DRIFT_READER_NOTES = (
    {
        "after_heading": "Definisi",
        "html": r"""<section class="reader-original-lab" id="brown-drift-offline-lab">
<style>
#brown-drift-offline-lab fieldset { border: 1px solid #777; margin: 1rem 0; padding: 1rem; }
#brown-drift-offline-lab .brown-drift-fields { display: grid; gap: .65rem; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); }
#brown-drift-offline-lab label { display: grid; gap: .2rem; height: auto; margin-left: 0; }
#brown-drift-offline-lab input { box-sizing: border-box; font: inherit; height: 2.4rem; margin-left: 0; max-width: none; padding: .25rem; width: 100%; }
#brown-drift-offline-lab .brown-drift-actions { align-items: center; display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .75rem; }
#brown-drift-offline-lab button { font: inherit; height: auto; margin-left: 0; padding: .45rem .75rem; }
#brown-drift-chart { background: #fff; border: 1px solid #777; display: block; height: auto; max-width: 100%; }
#brown-drift-offline-lab .brown-drift-frame { fill: #fff; stroke: #777; }
#brown-drift-offline-lab .brown-drift-axis { stroke: #999; stroke-width: 1; }
#brown-drift-offline-lab .brown-drift-path { fill: none; stroke: #2457a7; stroke-width: 2; }
#brown-drift-offline-lab .brown-drift-bar { fill: #8baee5; stroke: #31598d; stroke-width: .5; }
#brown-drift-offline-lab .brown-drift-density { fill: none; stroke: #9a2e65; stroke-width: 2; }
#brown-drift-offline-lab .brown-drift-title { font-size: 14px; font-weight: 700; }
#brown-drift-offline-lab table { border-collapse: collapse; margin: 1rem 0; width: 100%; }
#brown-drift-offline-lab th, #brown-drift-offline-lab td { border: 1px solid #777; padding: .4rem; text-align: right; }
#brown-drift-offline-lab th:first-child { text-align: left; }
@media print { #brown-drift-offline-lab fieldset, #brown-drift-offline-lab .brown-drift-actions { display: none; } }
</style>
<p class="reader-note-title"><strong>Laboratorium luring: pengaruh hanyutan dan skala</strong></p>
<p><strong>Status dan lisensi.</strong> Laboratorium deterministik ini merupakan
karya asli edisi, berfungsi tanpa jaringan, dan dilisensikan CC BY 4.0. Ia
melengkapi—bukan menggantikan—<a href="https://www.randomservices.org/random/apps/DriftBrownianMotion.html">aplikasi resmi daring Random</a>.</p>
<p>Ubah parameter, jalankan simulasi, lalu bandingkan histogram nilai akhir
dengan kepadatan normal teoretis serta rataan dan varians empiris dengan
\( \E(X_T)=\mu T \) dan \( \var(X_T)=\sigma^2T \). Benih yang sama selalu
menghasilkan keluaran yang sama.</p>
<fieldset>
<legend>Parameter simulasi</legend>
<div class="brown-drift-fields">
<label for="brown-drift-mu">Hanyutan μ<input id="brown-drift-mu" max="20" min="-20" step="0.1" type="number" value="0.4"/></label>
<label for="brown-drift-sigma">Skala σ<input id="brown-drift-sigma" max="20" min="0.1" step="0.1" type="number" value="1.2"/></label>
<label for="brown-drift-horizon">Horizon T<input id="brown-drift-horizon" max="20" min="0.1" step="0.1" type="number" value="1"/></label>
<label for="brown-drift-steps">Banyak langkah<input id="brown-drift-steps" max="2000" min="20" step="1" type="number" value="200"/></label>
<label for="brown-drift-repetitions">Banyak replikasi<input id="brown-drift-repetitions" max="5000" min="10" step="10" type="number" value="1000"/></label>
<label for="brown-drift-seed">Benih deterministik<input id="brown-drift-seed" max="4294967295" min="1" step="1" type="number" value="20260825"/></label>
</div>
<div class="brown-drift-actions"><button id="brown-drift-run" type="button">Jalankan simulasi</button><button id="brown-drift-reset" type="button">Pulihkan parameter</button></div>
</fieldset>
<p aria-live="polite" id="brown-drift-status">Simulator sedang disiapkan.</p>
<svg aria-labelledby="brown-drift-chart-title brown-drift-chart-description" id="brown-drift-chart" role="img" viewBox="0 0 750 350">
<title id="brown-drift-chart-title">Lintasan dan distribusi akhir gerak Brown dengan hanyutan</title>
<desc id="brown-drift-chart-description">Grafik akan diperbarui setelah simulasi dijalankan.</desc>
</svg>
<table>
<caption>Perbandingan momen nilai akhir \(X_T\)</caption>
<thead><tr><th scope="col">Momen</th><th scope="col">Teoretis</th><th scope="col">Empiris</th></tr></thead>
<tbody>
<tr><th scope="row">Rataan</th><td id="brown-drift-theoretical-mean">—</td><td id="brown-drift-empirical-mean">—</td></tr>
<tr><th scope="row">Varians</th><td id="brown-drift-theoretical-variance">—</td><td id="brown-drift-empirical-variance">—</td></tr>
</tbody>
</table>
<noscript>JavaScript diperlukan untuk menjalankan simulasi. Rumus teoretis dan latihan bersolusi di bawah tetap dapat dibaca tanpa JavaScript.</noscript>
<script src="../apps/brown-drift-offline.js"></script>
</section>""",
        "id": "brown-drift-offline-lab",
        "description": "Add a deterministic, accessible, offline simulation and nonvisual moment table for Brownian motion with drift.",
    },
    {
        "after_heading": "Teori Dasar",
        "html": r"""<aside class="reader-note reader-correction" id="brown-drift-downstream-corrections">
<strong>Catatan koreksi hilir.</strong> Terjemahan sumber mempertahankan struktur
dan permukaan matematika halaman beku. Lapisan pembaca ini menyatakan domain
kepadatan, memperbaiki urutan waktu dan rumus korelasi, membatasi klaim
penskalaan nontrivial, membedakan proses yang dimulai ulang dari gerak Brown
standar, serta melengkapi ruang probabilitas, filtrasi, keterhinggaan waktu
henti, dan sketsa bukti sifat Markov kuat. Laboratorium luring dan rangkaian
latihan bersolusi diberi tanda terpisah sebagai karya asli edisi CC BY 4.0.
</aside>""",
        "id": "brown-drift-downstream-corrections",
        "description": "Disclose the guarded mathematical repairs and separately licensed reader additions.",
    },
    {
        "after_heading": "Distribusi Berdimensi Hingga",
        "html": r"""<aside class="reader-original-solution" id="brown-drift-mastery">
<p class="reader-note-title"><strong>Latihan penguasaan asli edisi</strong></p>
<p><strong>Status dan lisensi.</strong> Soal, petunjuk, dan solusi berikut merupakan
karya asli edisi ini, dilisensikan CC BY 4.0, dan bukan bagian dari halaman Random.</p>
<p id="brown-drift-mastery-exercise"><strong>Soal.</strong> Untuk gerak Brown dengan
hanyutan \(\mu\) dan skala \(\sigma\), tentukan vektor rataan, fungsi kepadatan
gabungan, matriks kovarians, dan matriks korelasi
\((X_{1/2},X_1,X_{5/2})\). Tentukan pula distribusi bersyarat
\(X_{5/2}\mid X_1=x_2\).</p>
<details id="brown-drift-mastery-hint">
<summary>Petunjuk</summary>
<p>Gunakan inkremen independen pada selang dengan panjang
\(1/2,1/2,3/2\), lalu gunakan \(\cov(X_s,X_t)=\sigma^2\min\{s,t\}\).</p>
</details>
<details id="brown-drift-mastery-solution">
<summary>Jawaban dan solusi</summary>
<p>Vektor rataannya adalah
\[ \mu\left(\frac12,1,\frac52\right). \]
Dengan \(x=(x_1,x_2,x_3)\in\R^3\), kepadatan gabungannya ialah
\[ f_{1/2}(x_1)f_{1/2}(x_2-x_1)f_{3/2}(x_3-x_2) \]
atau, secara eksplisit,
\[ \frac{1}{(2\pi)^{3/2}\sigma^3\sqrt{3/8}}
\exp\!\left[-\frac{1}{2\sigma^2}\left(
\frac{(x_1-\mu/2)^2}{1/2}
+\frac{(x_2-x_1-\mu/2)^2}{1/2}
+\frac{(x_3-x_2-3\mu/2)^2}{3/2}
\right)\right]. \]</p>
<p>Matriks kovarians dan korelasinya adalah
\[ \Sigma=\sigma^2\begin{pmatrix}
1/2&amp;1/2&amp;1/2\\
1/2&amp;1&amp;1\\
1/2&amp;1&amp;5/2
\end{pmatrix},\qquad
R=\begin{pmatrix}
1&amp;1/\sqrt2&amp;1/\sqrt5\\
1/\sqrt2&amp;1&amp;\sqrt{2/5}\\
1/\sqrt5&amp;\sqrt{2/5}&amp;1
\end{pmatrix}. \]</p>
<p>Karena inkremen setelah waktu 1 saling bebas dengan masa lalu,
\[ X_{5/2}\mid X_1=x_2\sim
N\!\left(x_2+\frac32\mu,\frac32\sigma^2\right). \]</p>
</details>
</aside>""",
        "id": "brown-drift-mastery",
        "description": "Add a complete CC BY 4.0 mastery exercise, hint, and solution for the joint Gaussian laws.",
    },
)

BROWN_DRIFT_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "explicit-online-app",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/DriftBrownianMotion.html">gerak Brown dengan hanyutan dan penskalaan</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/DriftBrownianMotion.html">aplikasi resmi daring gerak Brown dengan hanyutan dan penskalaan</a>',
        "description": "Label the retained Random simulation link as an official online surface.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "marginal-density-and-fdd-scope",
        "old": r"""<p>Misalkan \( \bs{X} = \{X_t: t \in [0, \infty)\} \) adalah gerak Brown dengan parameter hanyutan \(\mu \in \R\) dan parameter skala \(\sigma \in (0, \infty)\). Dari bagian (d) definisi <a class="ref" href="#def1"></a>, \( X_t \) mempunyai fungsi kepadatan probabilitas \( f_t \) yang diberikan oleh
\[ f_t(x) = \frac{1}{\sigma \sqrt{2 \pi t}} \exp\left[-\frac{1}{2  \sigma^2 t} (x - \mu t)^2\right], \quad x \in \R \]
Keluarga fungsi kepadatan ini menentukan distribusi berdimensi hingga dari \( \bs{X} \).</p>""",
        "new": r"""<p>Misalkan \( \bs{X} = \{X_t: t \in [0, \infty)\} \) adalah gerak Brown dengan parameter hanyutan \(\mu \in \R\) dan parameter skala \(\sigma \in (0, \infty)\). Dari bagian (d) definisi <a class="ref" href="#def1"></a>, untuk \(t \in (0,\infty)\), \( X_t \) mempunyai fungsi kepadatan probabilitas \( f_t \) yang diberikan oleh
\[ f_t(x) = \frac{1}{\sigma \sqrt{2 \pi t}} \exp\left[-\frac{1}{2  \sigma^2 t} (x - \mu t)^2\right], \quad x \in \R \]
Pada \(t=0\), distribusinya adalah massa titik di 0. Keluarga kepadatan satu-waktu tersebut, bersama sifat inkremen stasioner dan independen, menentukan distribusi berdimensi hingga dari \( \bs{X} \).</p>""",
        "description": "Restrict the displayed density to positive time and state the increment assumption needed for finite-dimensional laws.",
    },
    {
        "id": "finite-dimensional-time-order",
        "old": r"\( 0 \lt t_1 \lt t_2 \cdots \lt t_n \)",
        "new": r"\( 0 \lt t_1 \lt t_2 \lt \cdots \lt t_n \)",
        "description": "Restore the missing comparison sign in the ordered time sequence.",
    },
    {
        "id": "brown-drift-correlation",
        "old": r"""<p>Fungsi korelasi tidak bergantung pada parameter-parameter tersebut sehingga sama dengan fungsi korelasi gerak Brown standar. Hal ini tidak mengherankan karena korelasi merupakan ukuran keterkaitan yang dibakukan.
\[ \cor(X_s, X_t) \frac{\sigma^2 \min\{s, t\}}{\sigma s \sigma t} = \frac{\min\{s, t\}}{s t} = \sqrt{\frac{\min\{s, t\}}{\max\{s, t\}}}, \quad (s, t) \in [0, \infty)^2 \]</p>""",
        "new": r"""<p>Fungsi korelasi tidak bergantung pada parameter-parameter tersebut sehingga sama dengan fungsi korelasi gerak Brown standar. Hal ini tidak mengherankan karena korelasi merupakan ukuran keterkaitan yang dibakukan.
\[ \cor(X_s, X_t) = \frac{\sigma^2 \min\{s, t\}}{\sigma\sqrt{s}\,\sigma\sqrt{t}} = \frac{\min\{s, t\}}{\sqrt{s t}} = \sqrt{\frac{\min\{s, t\}}{\max\{s, t\}}}, \quad (s, t) \in (0, \infty)^2 \]</p>""",
        "description": "Repair the missing equality, standard-deviation denominator, intermediate expression, and positive-time domain.",
    },
    {
        "id": "nontrivial-scaling-qualification",
        "old": r"""Kedua syarat tersebut tidak dapat dipenuhi sekaligus kecuali jika \(\mu = 0\), yang menghasilkan sedikit perumuman atas salah satu hasil kita untuk gerak Brown standar:""",
        "new": r"""Jika \(\mu \ne 0\), kedua syarat tersebut memaksa \(a=b=1\), sehingga tidak ada penskalaan nontrivial yang mempertahankan kedua parameter. Jika \(\mu = 0\), kita memperoleh keluarga penskalaan nontrivial berikut, yang sedikit memperumum salah satu hasil untuk gerak Brown standar:""",
        "description": "Exclude the identity transformation from the claimed impossibility and state the intended nontrivial result.",
    },
    {
        "id": "markov-initial-law-clarification",
        "old": r"""Sebagai catatan kecil, untuk memandang \( \bs{X} \) sebagai proses Markov, terkadang kita perlu melonggarkan Asumsi 1 dan membolehkan \( X_0 \) mempunyai nilai sembarang dalam \( \R \).""",
        "new": r"""Proses dengan \(X_0=0\) sudah bersifat Markov. Untuk membentuk keluarga hukum Markov yang diindeks oleh keadaan awal, kita juga mempertimbangkan versi dengan \(X_0=x\in\R\); bila keadaan awal diacak, hukum awalnya ditetapkan dan diambil independen dari inkremen berikutnya.""",
        "description": "Distinguish the Markov property from the optional family of laws indexed by initial state.",
    },
    {
        "id": "restarted-process-parameters",
        "old": r"""merupakan gerak Brown standar lain, seperti ditunjukkan dalam""",
        "new": r"""merupakan gerak Brown lain dengan parameter hanyutan dan skala yang sama, seperti ditunjukkan dalam""",
        "description": "Do not call the restarted drifted and scaled process standard Brownian motion.",
    },
    {
        "id": "stopping-sigma-algebra-and-finiteness",
        "old": r"""<p>Ingat kembali bahwa waktu acak \( \tau \) yang bernilai dalam \( [0, \infty] \) merupakan <dfn>waktu henti</dfn> terhadap proses \( \bs{X} \) apabila \( \{\tau \le t\} \in \mathscr{F}_t \) untuk setiap \( t \in [0, \infty) \). Aljabar-\( \sigma \) yang berkaitan dengan \( \tau \) adalah
\[ \mathscr{F}_\tau = \left\{B \in \mathscr{F}:  B \cap \{\tau \le t\} \in \mathscr{F}_t \text{ for all } t \ge 0\right\} \]
Lihat bagian tentang <a href="../prob/Stop.html">Filtrasi dan Waktu Henti</a> untuk informasi lebih lanjut mengenai filtrasi, waktu henti, dan aljabar-\(\sigma\) yang berkaitan dengan suatu waktu henti. Gerak Brown \( \bs{X} \) juga merupakan proses Markov kuat.</p>""",
        "new": r"""<p>Ingat kembali bahwa waktu acak \( \tau \) yang bernilai dalam \( [0, \infty] \) merupakan <dfn>waktu henti</dfn> terhadap proses \( \bs{X} \) apabila \( \{\tau \le t\} \in \mathscr{F}_t \) untuk setiap \( t \in [0, \infty) \). Dengan aljabar-\(\sigma\) ambien \(\mathscr F_\infty=\sigma(\bigcup_{t\ge0}\mathscr F_t)\), aljabar-\( \sigma \) yang berkaitan dengan \( \tau \) adalah
\[ \mathscr{F}_\tau = \left\{B \in \mathscr{F}_\infty: B \cap \{\tau \le t\} \in \mathscr{F}_t \text{ untuk setiap } t \ge 0\right\}. \]
Lihat bagian tentang <a href="../prob/Stop.html">Filtrasi dan Waktu Henti</a> untuk informasi lebih lanjut. Pernyataan yang melibatkan \(X_\tau\) di bawah mensyaratkan \(\P(\tau\lt\infty)=1\). Dengan filtrasi natural yang telah dilengkapi dan dibuat kontinu kanan, gerak Brown \( \bs{X} \) juga merupakan proses Markov kuat.</p>""",
        "description": "Define the ambient sigma-algebra, localize the quantified text, require finite stopped values, and state the usual filtration conditions.",
    },
    {
        "id": "strong-markov-filtration-proof",
        "old": r"""<p class="math">Misalkan \( \tau \) adalah waktu henti dan definisikan \( Y_t = X_{\tau + t} - X_\tau \) untuk \( t \in [0, \infty) \). Maka \( \bs{Y} = \{Y_t: t \in [0, \infty)\} \) merupakan gerak Brown dengan parameter hanyutan dan skala yang sama, serta saling bebas dengan \( \mathscr{F}_\tau \).</p>""",
        "new": r"""<p class="math">Pada ruang probabilitas terfilter dengan filtrasi natural yang telah dilengkapi dan dibuat kontinu kanan, misalkan \( \tau \) adalah waktu henti dengan \(\P(\tau\lt\infty)=1\), dan definisikan \( Y_t = X_{\tau + t} - X_\tau \) untuk \( t \in [0, \infty) \). Maka \( \bs{Y} = \{Y_t: t \in [0, \infty)\} \) merupakan gerak Brown dengan parameter hanyutan dan skala yang sama, serta saling bebas dengan \( \mathscr{F}_\tau \).</p>
<details id="brown-drift-strong-markov-proof"><summary>Sketsa bukti yang dilengkapi:</summary><p>Untuk waktu henti yang mengambil berhingga banyak nilai pada kisi, kondisikan pada setiap kejadian \(\{\tau=t_k\}\) dan gunakan inkremen stasioner serta independen. Untuk waktu henti umum yang hingga hampir pasti, gunakan pendekatan kisi dari atas \(\tau_n=2^{-n}\lceil2^n\tau\rceil\downarrow\tau\). Kekontinuan lintasan memberi konvergensi proses yang dimulai ulang, sedangkan kekontinuan kanan dan kelengkapan filtrasi memindahkan sifat kebebasan dari \(\mathscr F_{\tau_n}\) ke \(\mathscr F_\tau\). Distribusi berdimensi hingga hasil limit dan kekontinuan lintasannya kemudian memberi gerak Brown dengan parameter yang sama.</p></details>""",
        "description": "State the strong Markov theorem under the usual filtration and finite-stopping assumptions and supply the missing proof route.",
    },
)

BROWN_BRIDGE_READER_NOTES = (
    {
        "after_heading": "Definisi dan Konstruksi",
        "html": r"""<section class="reader-original-lab" id="brown-bridge-offline-lab">
<style>
#brown-bridge-offline-lab fieldset { border: 1px solid #777; margin: 1rem 0; padding: 1rem; }
#brown-bridge-offline-lab .brown-bridge-fields { display: grid; gap: .65rem; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); }
#brown-bridge-offline-lab label { display: grid; gap: .2rem; height: auto; margin-left: 0; }
#brown-bridge-offline-lab input { box-sizing: border-box; font: inherit; height: 2.4rem; margin-left: 0; max-width: none; padding: .25rem; width: 100%; }
#brown-bridge-offline-lab .brown-bridge-actions { align-items: center; display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .75rem; }
#brown-bridge-offline-lab button { font: inherit; height: auto; margin-left: 0; padding: .45rem .75rem; }
#brown-bridge-chart { background: #fff; border: 1px solid #777; display: block; height: auto; max-width: 100%; }
#brown-bridge-offline-lab .brown-bridge-frame { fill: #fff; stroke: #777; }
#brown-bridge-offline-lab .brown-bridge-axis { stroke: #999; stroke-width: 1; }
#brown-bridge-offline-lab .brown-bridge-observation { stroke: #b56b00; stroke-dasharray: 5 4; stroke-width: 1.5; }
#brown-bridge-offline-lab .brown-bridge-path { fill: none; stroke: #2457a7; stroke-width: 2; }
#brown-bridge-offline-lab .brown-bridge-bar { fill: #8baee5; stroke: #31598d; stroke-width: .5; }
#brown-bridge-offline-lab .brown-bridge-density { fill: none; stroke: #9a2e65; stroke-width: 2; }
#brown-bridge-offline-lab .brown-bridge-title { font-size: 14px; font-weight: 700; }
#brown-bridge-offline-lab table { border-collapse: collapse; margin: 1rem 0; width: 100%; }
#brown-bridge-offline-lab th, #brown-bridge-offline-lab td { border: 1px solid #777; padding: .4rem; text-align: right; }
#brown-bridge-offline-lab th:first-child { text-align: left; }
@media print { #brown-bridge-offline-lab fieldset, #brown-bridge-offline-lab .brown-bridge-actions { display: none; } }
</style>
<p class="reader-note-title"><strong>Laboratorium luring: lintasan dan distribusi jembatan Brown</strong></p>
<p><strong>Status dan lisensi.</strong> Laboratorium deterministik ini merupakan
karya asli edisi, berfungsi tanpa jaringan, dan dilisensikan CC BY 4.0. Ia
melengkapi—bukan menggantikan—<a href="https://www.randomservices.org/random/apps/BrownianBridge.html">aplikasi resmi daring Random</a>.</p>
<p>Ubah waktu pengamatan \(t\), lalu bandingkan histogram simulasi dengan
\(N(0,t(1-t))\). Benih yang sama selalu menghasilkan keluaran yang sama;
grafik, deskripsi nonvisual, dan tabel momen diperbarui bersama.</p>
<fieldset>
<legend>Parameter simulasi</legend>
<div class="brown-bridge-fields">
<label for="brown-bridge-observation">Waktu pengamatan t<input id="brown-bridge-observation" max="0.99" min="0.01" step="0.01" type="number" value="0.5"/></label>
<label for="brown-bridge-steps">Banyak langkah lintasan<input id="brown-bridge-steps" max="2000" min="20" step="1" type="number" value="200"/></label>
<label for="brown-bridge-repetitions">Banyak replikasi<input id="brown-bridge-repetitions" max="5000" min="10" step="10" type="number" value="1000"/></label>
<label for="brown-bridge-seed">Benih deterministik<input id="brown-bridge-seed" max="4294967295" min="1" step="1" type="number" value="20260825"/></label>
</div>
<div class="brown-bridge-actions"><button id="brown-bridge-run" type="button">Jalankan simulasi</button><button id="brown-bridge-reset" type="button">Pulihkan parameter</button></div>
</fieldset>
<p aria-live="polite" id="brown-bridge-status">Simulator sedang disiapkan.</p>
<svg aria-labelledby="brown-bridge-chart-title brown-bridge-chart-description" id="brown-bridge-chart" role="img" viewBox="0 0 750 350">
<title id="brown-bridge-chart-title">Lintasan dan distribusi jembatan Brown</title>
<desc id="brown-bridge-chart-description">Grafik akan diperbarui setelah simulasi dijalankan.</desc>
</svg>
<table>
<caption>Perbandingan momen (X_t)</caption>
<thead><tr><th scope="col">Momen</th><th scope="col">Teoretis</th><th scope="col">Empiris</th></tr></thead>
<tbody>
<tr><th scope="row">Rataan</th><td id="brown-bridge-theoretical-mean">—</td><td id="brown-bridge-empirical-mean">—</td></tr>
<tr><th scope="row">Varians</th><td id="brown-bridge-theoretical-variance">—</td><td id="brown-bridge-empirical-variance">—</td></tr>
</tbody>
</table>
<noscript>JavaScript diperlukan untuk menjalankan simulasi. Rumus teoretis dan latihan bersolusi di bawah tetap dapat dibaca tanpa JavaScript.</noscript>
<script src="../apps/brown-bridge-offline.js"></script>
</section>""",
        "id": "brown-bridge-offline-lab",
        "description": "Add a deterministic, accessible, offline Brownian-bridge path and marginal-distribution laboratory.",
    },
    {
        "after_heading": "Teori Dasar",
        "html": r"""<aside class="reader-note reader-correction" id="brown-bridge-downstream-corrections">
<strong>Catatan koreksi hilir.</strong> Terjemahan sumber mempertahankan struktur,
ID, dan permukaan matematika halaman beku. Lapisan pembaca ini memperbaiki
nomor judul lokal, notasi nilai harapan, dua domain waktu, penafsiran
pengondisian pada kejadian nol, domain integral stokastik, tanda drift dalam
SDE, jenis konsistensi fungsi distribusi empiris, dan satu koma kovarians.
Laboratorium luring dan latihan bersolusi diberi tanda terpisah sebagai karya
asli edisi CC BY 4.0.
</aside>""",
        "id": "brown-bridge-downstream-corrections",
        "description": "Disclose guarded mathematical repairs and separately licensed reader additions.",
    },
    {
        "after_heading": "Fungsi Distribusi Empiris",
        "html": r"""<aside class="reader-original-solution" id="brown-bridge-mastery">
<p class="reader-note-title"><strong>Jembatan proses dan latihan penguasaan asli edisi</strong></p>
<p><strong>Status dan lisensi.</strong> Catatan, soal, petunjuk, dan solusi berikut
merupakan karya asli edisi ini, dilisensikan CC BY 4.0, dan bukan bagian dari
halaman Random.</p>
<p id="brown-bridge-process-limit-warning"><strong>Batas klaim.</strong> Kesamaan
fungsi kovarians saja belum membuktikan konvergensi proses empiris ke jembatan
Brown. Teorema Donsker memerlukan konvergensi berdimensi hingga dan keketatan
dalam ruang fungsi yang ditentukan. Hasil titik-demi-titik pada halaman sumber
tidak diam-diam dinaikkan menjadi teorema limit fungsional.</p>
<p id="brown-bridge-mastery-exercise"><strong>Soal.</strong> Misalkan
\(\bs X\) adalah jembatan Brown standar dan \(0\lt s\lt t\lt1\). Tentukan
distribusi bersyarat \(X_t\mid X_s=x\), lalu tafsirkan rataan bersyaratnya.</p>
<details id="brown-bridge-mastery-hint"><summary>Petunjuk</summary><p>Gunakan
normalitas bersama, \(\var(X_u)=u(1-u)\), dan
\(\cov(X_s,X_t)=s(1-t)\) untuk \(s\lt t\).</p></details>
<details id="brown-bridge-mastery-solution"><summary>Solusi lengkap</summary><p>
Untuk pasangan normal bersama, rataan bersyarat adalah
\[\frac{\cov(X_t,X_s)}{\var(X_s)}x
=\frac{s(1-t)}{s(1-s)}x=\frac{1-t}{1-s}x,\]
sedangkan varians bersyaratnya adalah
\[t(1-t)-\frac{s^2(1-t)^2}{s(1-s)}
=\frac{(t-s)(1-t)}{1-s}.\]
Jadi
\[X_t\mid X_s=x\sim N\!\left(\frac{1-t}{1-s}x,
\frac{(t-s)(1-t)}{1-s}\right).\]
Rataannya menginterpolasi secara linear dari nilai \(x\) pada waktu \(s\)
menuju tambatan 0 pada waktu 1.</p></details>
</aside>""",
        "id": "brown-bridge-mastery",
        "description": "Add an explicit process-level convergence boundary and a fully solved conditional-law mastery problem.",
    },
)

BROWN_BRIDGE_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "local-section-number",
        "old": r"<h2>5. Jembatan Brown</h2>",
        "new": r"<h2>3. Jembatan Brown</h2>",
        "description": "Align the page heading with the source navigation position three.",
    },
    {
        "id": "explicit-online-apps",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/BrownianBridge.html">proses jembatan Brown</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/BrownianBridge.html">aplikasi resmi daring proses jembatan Brown</a>',
        "matches": 2,
        "description": "Label both retained Random simulation links as official online surfaces.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "expectation-macro",
        "old": r"\( E(X_t) = \E(Z_t) - t \E(Z_1) = 0 \)",
        "new": r"\( \E(X_t) = \E(Z_t) - t \E(Z_1) = 0 \)",
        "description": "Restore the edition's expectation macro in the first construction proof.",
    },
    {
        "id": "time-change-expectation-domain",
        "old": r"Untuk \( t \in [0, 1] \),",
        "new": r"Untuk \( t \in [0, 1) \),",
        "description": "Exclude the endpoint where the displayed time change is undefined.",
    },
    {
        "id": "time-change-endpoint-mean",
        "old": r"\[ \E(X_t) = (1 - t) \E\left[Z\left(\frac{t}{1 - t}\right)\right] = 0 \]",
        "new": r"\[ \E(X_t) = (1 - t) \E\left[Z\left(\frac{t}{1 - t}\right)\right] = 0 \]<br/>Untuk \(t=1\), \(\E(X_1)=0\) berdasarkan definisi.",
        "description": "Handle the endpoint mean separately through the defined value X_1=0.",
    },
    {
        "id": "time-change-tab-normalization",
        "old": "\\frac{t}{1 - \tt}",
        "new": r"\frac{t}{1 - t}",
        "description": "Normalize a frozen source tab inside the TeX denominator only in the reader layer.",
    },
    {
        "id": "inverse-time-change-domain",
        "old": r"Jika \( s, \, t \in [0, 1] \) dengan \( s \lt t \), maka \( s \big/ (1 + s) \lt t \big/ (1 + t) \)",
        "new": r"Jika \( s, \, t \in [0, \infty) \) dengan \( s \lt t \), maka \( s \big/ (1 + s) \lt t \big/ (1 + t) \)",
        "description": "Use the full nonnegative-time domain of the constructed Brownian motion.",
    },
    {
        "id": "regular-conditional-law",
        "old": r"Maka, jika dikondisikan pada \( X_1 = 0 \), proses \( \{X_t: t \in [0, 1]\} \) adalah proses jembatan Brown.",
        "new": r"Maka, dalam arti hukum kondisional reguler jika diketahui \( X_1 = 0 \), proses \( \{X_t: t \in [0, 1]\} \) mempunyai hukum jembatan Brown. Penafsiran ini diperlukan karena \(\P(X_1=0)=0\); versi kontinu hukum tersebut dapat direalisasikan melalui konstruksi pada Teorema 2.",
        "description": "Interpret conditioning on the probability-zero endpoint through a regular conditional law.",
    },
    {
        "id": "stochastic-integral-domain",
        "old": r"Misalkan \( s, \, t \in [0, 1] \) dengan \( s \le t \). Maka",
        "new": r"Misalkan \( s, \, t \in [0, 1) \) dengan \( s \le t \). Maka",
        "description": "Keep the displayed stochastic integrals away from their singular endpoint; the endpoint follows by continuous extension.",
    },
    {
        "id": "stochastic-integral-endpoint-covariance",
        "old": r"= (1 - t)s \]</li>",
        "new": r"= (1 - t)s \]<br/>Untuk \(t=1\), kovarians bernilai 0 karena \(X_1=0\) menurut definisi.</li>",
        "description": "Handle the endpoint separately after the open-domain stochastic-integral calculation.",
    },
    {
        "id": "stochastic-differential-sign",
        "old": r"\[ d X_t = \frac{X_t}{1 - t} \, dt  + dZ_t, \; X_0 = 0 \]",
        "new": r"\[ d X_t = -\frac{X_t}{1 - t} \, dt + dZ_t, \quad t \in [0,1), \; X_0 = 0. \]",
        "description": "Apply the product rule to restore the negative bridge drift and its open endpoint domain.",
    },
    {
        "id": "edf-consistency-mode",
        "old": r"\( \var\left[F_n(t)\right] = F(t)\left[1 - F(t)\right] \big/ n \), sehingga \( F_n(t) \) adalah penduga konsisten bagi \( F(t) \).",
        "new": r"\( \var\left[F_n(t)\right] = F(t)\left[1 - F(t)\right] \big/ n \); bersama ketakbiasan, hal ini memberi konsistensi kuadrat-rataan, dan karenanya konsistensi dalam probabilitas, bagi \( F(t) \).",
        "description": "State the mode of consistency actually implied by the displayed variance and unbiasedness.",
    },
    {
        "id": "edf-covariance-comma",
        "old": r"\cov\left[\bs{1}(T_i \le s) \bs{1}(T_j \le t)\right]",
        "new": r"\cov\left[\bs{1}(T_i \le s), \bs{1}(T_j \le t)\right]",
        "description": "Restore the missing separator between the two covariance arguments.",
    },
)

BROWN_GEOMETRIC_READER_NOTES = (
    {
        "after_heading": "Definisi",
        "html": r"""<section class="reader-original-lab" id="geometric-brownian-offline-lab">
<style>
#geometric-brownian-offline-lab fieldset { border: 1px solid #777; margin: 1rem 0; padding: 1rem; }
#geometric-brownian-offline-lab .geometric-brownian-fields { display: grid; gap: .65rem; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); }
#geometric-brownian-offline-lab label { display: grid; gap: .2rem; height: auto; margin-left: 0; }
#geometric-brownian-offline-lab input { box-sizing: border-box; font: inherit; height: 2.4rem; margin-left: 0; max-width: none; padding: .25rem; width: 100%; }
#geometric-brownian-offline-lab .geometric-brownian-actions { align-items: center; display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .75rem; }
#geometric-brownian-offline-lab button { font: inherit; height: auto; margin-left: 0; padding: .45rem .75rem; }
#geometric-brownian-chart { background: #fff; border: 1px solid #777; display: block; height: auto; max-width: 100%; }
#geometric-brownian-offline-lab .geometric-brownian-frame { fill: #fff; stroke: #777; }
#geometric-brownian-offline-lab .geometric-brownian-initial { stroke: #b56b00; stroke-dasharray: 1 3; stroke-width: 1.5; }
#geometric-brownian-offline-lab .geometric-brownian-path { fill: none; stroke: #2457a7; stroke-width: 2; }
#geometric-brownian-offline-lab .geometric-brownian-mean { fill: none; stroke: #137333; stroke-dasharray: 10 4; stroke-width: 1.8; }
#geometric-brownian-offline-lab .geometric-brownian-median { fill: none; stroke: #8a4d00; stroke-dasharray: 3 3; stroke-width: 1.6; }
#geometric-brownian-offline-lab .geometric-brownian-bar { fill: #8baee5; stroke: #31598d; stroke-width: .5; }
#geometric-brownian-offline-lab .geometric-brownian-density { fill: none; stroke: #9a2e65; stroke-width: 2; }
#geometric-brownian-offline-lab .geometric-brownian-title { font-size: 14px; font-weight: 700; }
#geometric-brownian-offline-lab .geometric-brownian-legend { font-size: 11px; }
#geometric-brownian-offline-lab table { border-collapse: collapse; margin: 1rem 0; width: 100%; }
#geometric-brownian-offline-lab th, #geometric-brownian-offline-lab td { border: 1px solid #777; padding: .4rem; text-align: right; }
#geometric-brownian-offline-lab th:first-child { text-align: left; }
@media print { #geometric-brownian-offline-lab fieldset, #geometric-brownian-offline-lab .geometric-brownian-actions { display: none; } }
</style>
<p class="reader-note-title"><strong>Laboratorium luring: lintasan dan distribusi gerak Brown geometrik</strong></p>
<p><strong>Status dan lisensi.</strong> Laboratorium deterministik ini merupakan
karya asli edisi, berfungsi tanpa jaringan, dan dilisensikan CC BY 4.0. Ia
melengkapi—bukan menggantikan—<a href="https://www.randomservices.org/random/apps/GeometricBrownianMotion.html">aplikasi resmi daring Random</a>.</p>
<p>Ubah nilai awal \(x_0\), hanyutan \(\mu\), volatilitas \(\sigma\), dan horizon
\(T\). Simulator menggunakan solusi eksak pada kisi waktu, lalu membandingkan
histogram \(X_T\) dengan kepadatan lognormal teoretis. Benih yang sama selalu
menghasilkan keluaran yang sama.</p>
<fieldset>
<legend>Parameter simulasi</legend>
<div class="geometric-brownian-fields">
<label for="geometric-brownian-x0">Nilai awal x₀<input id="geometric-brownian-x0" max="1000000" min="0.0001" step="0.1" type="number" value="1"/></label>
<label for="geometric-brownian-mu">Hanyutan μ<input id="geometric-brownian-mu" max="2" min="-2" step="0.05" type="number" value="0.1"/></label>
<label for="geometric-brownian-sigma">Volatilitas σ<input id="geometric-brownian-sigma" max="2" min="0.01" step="0.05" type="number" value="0.4"/></label>
<label for="geometric-brownian-horizon">Horizon T<input id="geometric-brownian-horizon" max="4" min="0.01" step="0.1" type="number" value="1"/></label>
<label for="geometric-brownian-steps">Banyak langkah<input id="geometric-brownian-steps" max="1000" min="20" step="1" type="number" value="200"/></label>
<label for="geometric-brownian-repetitions">Banyak replikasi<input id="geometric-brownian-repetitions" max="2000" min="10" step="10" type="number" value="1000"/></label>
<label for="geometric-brownian-seed">Benih deterministik<input id="geometric-brownian-seed" max="4294967295" min="1" step="1" type="number" value="20260826"/></label>
</div>
<div class="geometric-brownian-actions"><button id="geometric-brownian-run" type="button">Jalankan simulasi</button><button id="geometric-brownian-reset" type="button">Pulihkan parameter</button></div>
</fieldset>
<p aria-live="polite" id="geometric-brownian-status">Simulator sedang disiapkan.</p>
<svg aria-labelledby="geometric-brownian-chart-title geometric-brownian-chart-description" id="geometric-brownian-chart" role="img" viewBox="0 0 750 350">
<title id="geometric-brownian-chart-title">Lintasan dan distribusi akhir gerak Brown geometrik</title>
<desc id="geometric-brownian-chart-description">Grafik akan diperbarui setelah simulasi dijalankan.</desc>
</svg>
<table>
<caption>Perbandingan ringkasan distribusi nilai akhir \(X_T\)</caption>
<thead><tr><th scope="col">Ringkasan</th><th scope="col">Teoretis</th><th scope="col">Empiris</th></tr></thead>
<tbody>
<tr><th scope="row">Rataan</th><td id="geometric-brownian-theoretical-mean">—</td><td id="geometric-brownian-empirical-mean">—</td></tr>
<tr><th scope="row">Median</th><td id="geometric-brownian-theoretical-median">—</td><td id="geometric-brownian-empirical-median">—</td></tr>
<tr><th scope="row">Varians</th><td id="geometric-brownian-theoretical-variance">—</td><td id="geometric-brownian-empirical-variance">—</td></tr>
<tr><th scope="row">Peluang \(X_T\gt x_0\)</th><td id="geometric-brownian-theoretical-probability">—</td><td id="geometric-brownian-empirical-probability">—</td></tr>
</tbody>
</table>
<noscript>JavaScript diperlukan untuk menjalankan simulasi. Rumus teoretis dan latihan bersolusi di bawah tetap dapat dibaca tanpa JavaScript.</noscript>
<script src="../apps/geometric-brownian-offline.js"></script>
</section>""",
        "id": "geometric-brownian-offline-lab",
        "description": "Add a deterministic, accessible, offline exact-solution path and lognormal-distribution laboratory.",
    },
    {
        "after_heading": "Teori Dasar",
        "html": r"""<aside class="reader-note reader-correction" id="geometric-brownian-downstream-corrections">
<strong>Catatan koreksi hilir.</strong> Terjemahan sumber mempertahankan struktur,
ID, dan permukaan matematika halaman beku. Lapisan pembaca ini memperbaiki
penomoran judul ke urutan pembaca lokal, tipe media ikon, label aplikasi daring, notasi kepadatan,
titik belok lognormal, domain fungsi distribusi, syarat orde momen positif,
bukti kasus batas asimtotik, urutan ID, dan syarat keterintegralan dalam bukti
martingal. Laboratorium luring dan latihan bersolusi diberi tanda terpisah
sebagai karya asli edisi CC BY 4.0.
</aside>""",
        "id": "geometric-brownian-downstream-corrections",
        "description": "Disclose guarded mathematical repairs and separately licensed reader additions.",
    },
    {
        "after_heading": "Sifat",
        "html": r"""<aside class="reader-original-solution" id="geometric-brownian-mastery">
<p class="reader-note-title"><strong>Latihan penguasaan asli edisi</strong></p>
<p><strong>Status dan lisensi.</strong> Soal, petunjuk, dan solusi berikut merupakan
karya asli edisi ini, dilisensikan CC BY 4.0, dan bukan bagian dari halaman Random.</p>
<p id="geometric-brownian-mastery-exercise"><strong>Soal.</strong> Misalkan
\(\bs X\) adalah gerak Brown geometrik dengan parameter \(\mu,\sigma\), dimulai
dari \(x_0\gt0\), dan \(0\le s\lt t\). Dengan
\(\mathscr F_s=\sigma\{Z_u:0\le u\le s\}\), tentukan hukum bersyarat \(X_t\)
jika \(\mathscr F_s\) diketahui, lalu hitung rataan dan varians bersyaratnya. Tunjukkan
bahwa proses terdiskonto \(M_t=e^{-\mu t}X_t\) merupakan martingal.</p>
<details id="geometric-brownian-mastery-hint"><summary>Petunjuk</summary><p>Tulis
\(X_t=X_s\exp[(\mu-\sigma^2/2)(t-s)+\sigma(Z_t-Z_s)]\) dan gunakan kebebasan
inkremen \(Z_t-Z_s\) dari \(\mathscr F_s\).</p></details>
<details id="geometric-brownian-mastery-solution"><summary>Solusi lengkap</summary><p>
Dengan \(\Delta=t-s\), rasio \(X_t/X_s\), jika \(\mathscr F_s\) diketahui,
berdistribusi lognormal dengan parameter lokasi log
\((\mu-\sigma^2/2)\Delta\) dan parameter skala log \(\sigma\sqrt{\Delta}\).
Karena itu
\[\E(X_t\mid\mathscr F_s)=X_s e^{\mu\Delta},\qquad
\var(X_t\mid\mathscr F_s)=X_s^2e^{2\mu\Delta}\bigl(e^{\sigma^2\Delta}-1\bigr).\]
Selanjutnya,
\[\E(M_t\mid\mathscr F_s)=e^{-\mu t}\E(X_t\mid\mathscr F_s)
=e^{-\mu s}X_s=M_s.\]
Setiap \(M_t\) terintegralkan karena \(\E(M_t)=x_0\), sehingga identitas
bersyarat tersebut membuktikan sifat martingal.</p></details>
</aside>""",
        "id": "geometric-brownian-mastery",
        "description": "Add a complete conditional-law and discounted-martingale mastery exercise, hint, and solution.",
    },
)

BROWN_GEOMETRIC_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
    {
        "id": "local-section-number",
        "old": r"<h2>6. Gerak Brown Geometrik</h2>",
        "new": r"<h2>4. Gerak Brown Geometrik</h2>",
        "description": "Align the page heading with the source navigation position four.",
    },
    {
        "id": "explicit-online-apps",
        "old": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/GeometricBrownianMotion.html">gerak Brown geometrik</a>',
        "new": r'<a class="ancillary" href="https://www.randomservices.org/random/apps/GeometricBrownianMotion.html">aplikasi resmi daring gerak Brown geometrik</a>',
        "matches": 4,
        "description": "Label all four retained Random simulation links as official online surfaces.",
        "change_kind": "source-link-repair",
    },
    {
        "id": "density-mode-subscript",
        "old": r"<li>\( f \) meningkat lalu menurun,",
        "new": r"<li>\( f_t \) meningkat lalu menurun,",
        "description": "Use the defined time-indexed density in the mode statement.",
    },
    {
        "id": "density-inflection-subscript",
        "old": r"<li>\( f \) mula-mula cekung ke atas,",
        "new": r"<li>\( f_t \) mula-mula cekung ke atas,",
        "description": "Use the defined time-indexed density in the inflection statement.",
    },
    {
        "id": "lognormal-inflection-center",
        "old": r"\exp\left[(\mu - \sigma^2) t \pm \frac{1}{2} \sigma \sqrt{\sigma^2 t^2 + 4 t}\right]",
        "new": r"\exp\left[(\mu - 2\sigma^2) t \pm \frac{1}{2} \sigma \sqrt{\sigma^2 t^2 + 4 t}\right]",
        "description": "Restore the correct center of the two lognormal density inflection points.",
    },
    {
        "id": "cdf-nonpositive-domain",
        "old": r"dengan \( \Phi \) adalah fungsi distribusi normal standar.</p>",
        "new": r"dengan \( \Phi \) adalah fungsi distribusi normal standar; untuk \(x \le 0\), \(F_t(x)=0\).</p>",
        "description": "Complete the lognormal CDF on the nonpositive half-line.",
    },
    {
        "id": "quantile-unit-id",
        "old": r'<div class="unit" id="dist4">',
        "new": r'<div class="unit" id="dst4">',
        "description": "Repair the distribution-unit ID sequence.",
    },
    {
        "id": "positive-moment-order",
        "old": r"<p>Ditinjau dari orde momen \( n \), suku dominan di dalam eksponensial adalah \( \sigma^2 n^2 / 2 \). Jika \( n \gt 1 - 2 \mu / \sigma^2 \), maka \( n \mu + \frac{\sigma^2}{2}(n^2 - n) \gt 0 \), sehingga \( \E(X_t^n) \to \infty \) ketika \( t \to \infty \). Rataan dan varians mudah diperoleh dari hasil momen umum tersebut.</p>",
        "new": r"<p>Untuk orde momen positif \(n\in\N_+\), suku dominan di dalam tanda kurung siku pada eksponen adalah \( \sigma^2 n^2 / 2 \). Jika \( n \gt 1 - 2 \mu / \sigma^2 \), maka \( n \mu + \frac{\sigma^2}{2}(n^2 - n) \gt 0 \), sehingga \( \E(X_t^n) \to \infty \) ketika \( t \to \infty \). Pembatasan \(n\gt0\) diperlukan karena momen orde nol selalu bernilai 1. Rataan dan varians mudah diperoleh dari hasil momen umum tersebut.</p>",
        "description": "Exclude the zero-order moment from the divergence implication.",
    },
    {
        "id": "asymptotic-equality-case",
        "old": r"""<p>Hasil-hasil ini mengikuti <a href="Standard.html#lil">hukum logaritma berulang</a>. Secara asimtotik, suku \( \left(\mu - \sigma^2 / 2\right) t \) mendominasi suku \( \sigma Z_t \) ketika \( t \to \infty \).</p>""",
        "new": r"""<p>Jika \(\mu\ne\sigma^2/2\), hasilnya mengikuti fakta bahwa \(\log(X_t)/t=\mu-\sigma^2/2+\sigma Z_t/t\to\mu-\sigma^2/2\) hampir pasti. Pada kasus batas \(\mu=\sigma^2/2\), <a href="Standard.html#lil">hukum logaritma berulang</a> memberi \(\limsup_{t\to\infty}Z_t=\infty\) dan \(\liminf_{t\to\infty}Z_t=-\infty\) hampir pasti; jadi \(\limsup_{t\to\infty}X_t=\infty\), \(\liminf_{t\to\infty}X_t=0\), dan \(X_t\) tidak mempunyai limit.</p>""",
        "description": "Prove the equality case separately instead of invoking linear dominance where the linear term vanishes.",
    },
    {
        "id": "mean-standard-deviation-spacing",
        "old": r"rataan\( \pm \)simpangan baku",
        "new": r"rataan \( \pm \) simpangan baku",
        "description": "Restore spaces around the inline plus-or-minus expression.",
    },
    {
        "id": "final-property-id",
        "old": r"""<div class="unit">
<p class="math">Jika \( \mu = 0 \),""",
        "new": r"""<div class="unit" id="prp2">
<p class="math">Jika \( \mu = 0 \),""",
        "description": "Give the final property unit a stable local ID.",
    },
    {
        "id": "stochastic-integral-square-integrability",
        "old": r"Proses yang berkaitan dengan integral stokastik selalu merupakan martingal, dengan asumsi-asumsi lazim pada proses integrannya (yang dipenuhi di sini).</p>",
        "new": r"Selain itu, \(\E(X_s^2)=e^{\sigma^2s}\), sehingga untuk setiap \(t\lt\infty\), \[\E\!\left(\int_0^t \sigma^2X_s^2\,ds\right)=\sigma^2\int_0^t e^{\sigma^2s}\,ds\lt\infty.\] Karena integrannya teradaptasi dan terintegralkan kuadrat pada setiap horizon hingga, integral stokastik tersebut merupakan martingal kuadrat-terintegralkan.</p>",
        "description": "Replace a vague appeal to usual assumptions with the exact square-integrability check.",
    },
)

MARTINGALES_INDEX_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
)

MARKOV_INDEX_READER_NOTES = (
    {
        "after_selector": "#sum + p",
        "html": r'''<aside class="scope-note" id="markov-index-edition-scope">
<strong>Batas edisi.</strong> Ikhtisar sumber mencantumkan seluruh bab Markov
di situs Random. Edisi D30 ini memuat secara lokal halaman teori Markov umum,
rantai waktu diskret, rekurensi, periodisitas, dan distribusi invarian/limit.
Blok waktu kontinu, Poisson, generator, semigrup, dan ergodisitas disediakan
oleh komponen QuantEcon yang lengkap; halaman Random lain pada daftar di bawah
tetap berupa rujukan daring dan tidak dinyatakan telah diterjemahkan.
</aside>''',
    },
)

MARKOV_INDEX_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
)

BROWN_INDEX_READER_NOTES = (
    {
        "after_selector": "#sum + p",
        "html": r'''<aside class="scope-note" id="brown-index-edition-scope">
<strong>Batas edisi.</strong> Pembaca ini memuat empat halaman sumber yang
tersedia: gerak Brown standar, gerak Brown dengan hanyutan dan penskalaan,
jembatan Brown, dan gerak Brown geometrik. Judul integral stokastik, rumus Itô,
dan teorema representasi yang hanya muncul sebagai komentar pada ikhtisar
sumber bukan halaman tersedia dan tidak dinyatakan sebagai unit terjemahan.
</aside>''',
    },
)

BROWN_INDEX_READER_CORRECTIONS = (
    {
        "id": "favicon-svg-mime",
        "old": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg"/>',
        "new": r'<link href="../icons/Icon.svg" rel="icon" type="image/svg+xml"/>',
        "description": "Use the registered SVG media type for the local favicon.",
    },
)

THEORY_UNITS = (
    {
        "rel": "prob/Convergence.html",
        "authority_sha256": "749de69aba8c7b54e5944ddbe4b342fec8695b32ff46e34409f7b6040241e34f",
        "source_title": "Convergence",
        "nav_label": "Konvergensi",
        "rights_id": "o009-rights-random-convergence",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Basic Theory",
            "Sequences of events",
            "The Continuity Theorems",
            "Convergence with Probability 1",
            "Convergence in Probability",
        ),
    },
    {
        "rel": "prob/Probability2.html",
        "authority_sha256": "ba442c5fac2cb1608965f974b3f346cec9515e894428accb83521465492b2d10",
        "source_title": "Probability Revisited",
        "nav_label": "Probabilitas ditinjau kembali",
        "rights_id": "o009-rights-random-probability-revisited",
        # Upstream links #tai1, but its intended limsup/liminf result is #tai12.
        "fragment_corrections": {"#tai1": "#tai12"},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Probability Revisited",
            "Measure Theory",
            "Probability Theory",
            "Equivalent Random Variables",
            "Completion",
        ),
    },
    {
        "rel": "prob/Processes.html",
        "authority_sha256": "d4a65b124face6115950e212af2acb5dccf33e1065c77fb3d6aecb727d39e6bc",
        "source_title": "Stochastic Processes",
        "nav_label": "Proses stokastik",
        "rights_id": "o009-rights-random-stochastic-processes",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Stochastic Processes",
            "Introduction",
            "Equivalent Processes",
            "The Kolmogorov Construction",
            "Applications",
        ),
    },
    {
        "rel": "prob/Stop.html",
        "authority_sha256": "9d26e78a8ee2a5a14ade3708838298ef0ba51cf9cd9658602a4f26e73b68524d",
        "source_title": "Filtrations and Stopping Times",
        "nav_label": "Filtrasi dan waktu henti",
        "rights_id": "o009-rights-random-filtrations-stopping-times",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Filtrations and Stopping Times",
            "Introduction",
            "Basic Definitions",
            "Right Continuity",
            "Stopping Times",
            "Basic Properties",
            "Basic Constructions",
            "The Sigma-Algebra of a Stopping Time",
        ),
    },
    {
        "rel": "dist/Convergence.html",
        "authority_sha256": "dc6a536ca3359f3952e1ae487a445377de1c1e73491bb56f3baa8862630dcc3d",
        "source_title": "Convergence in Distribution",
        "nav_label": "Konvergensi dalam distribusi",
        "rights_id": "o009-rights-random-convergence-in-distribution",
        "fragment_corrections": {},
        "reader_corrections": DIST_CONVERGENCE_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Convergence in Distribution",
            "Distributions on",
            "Preliminary Examples",
            "Probability Density Functions",
            "The Skorohod Representation",
            "Examples and Applications",
            "Fundamental Theorems",
            "General Spaces",
            "Skorohod's Representation Theorem",
            "Expected Value",
        ),
    },
    {
        "rel": "expect/Conditional2.html",
        "authority_sha256": "98307993d76941808cc87b7d28dfd8b2e24325913471b07c3a350a52a54c87c2",
        "source_title": "Conditional Expected Value Revisited",
        "nav_label": "Nilai harapan bersyarat",
        "rights_id": "o009-rights-random-conditional-expectation",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Conditional Expected Value Revisited",
            "Basic Theory",
            "Definition",
            "Properties",
            "Conditional Probability",
            "Basic Examples",
            "Best Predictor",
            "Conditional Variance",
            "Conditional Covariance",
        ),
    },
    {
        "rel": "expect/Uniform.html",
        "authority_sha256": "66f610030094a063be69408d3112c74353941849fe36353f4c5365380f03df2d",
        "source_title": "Uniformly Integrable Variables",
        "nav_label": "Peubah terintegralkan seragam",
        "rights_id": "o009-rights-random-uniform-integrability",
        "fragment_corrections": {},
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Uniformly Integrable Variables",
            "Basic Theory",
            "Definition",
            "Properties",
            "Convergence",
            "Examples",
        ),
    },
    {
        "rel": "expect/Kernels.html",
        "authority_sha256": "9dd2a5474f284fcb11c9e9f9e81099a1c4fe1708094bfcd64b08ccb9f82c5b8d",
        "source_title": "Kernels and Operators",
        "nav_label": "Kernel dan operator",
        "rights_id": "o009-rights-random-kernels-operators",
        "fragment_corrections": {},
        "reader_corrections": KERNELS_READER_CORRECTIONS,
        "reader_notes": KERNELS_READER_NOTES,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Kernels and Operators",
            "Basic Theory",
            "Definition",
            "Constructions",
            "Kernel Functions",
            "Examples and Special Cases",
            "Discrete Spaces",
            "Conditional Probability",
            "Parametric Distributions",
        ),
    },
    {
        "rel": "martingales/Introduction.html",
        "authority_sha256": "ff102fd4f54926d89c47b92885176e587f342378e442f1f38e4a69199a02375a",
        "source_title": "Introduction",
        "nav_label": "Pendahuluan martingal",
        "rights_id": "o009-rights-random-martingale-introduction",
        "fragment_corrections": {},
        "reader_corrections": MARTINGALE_INTRO_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Introduction",
            "Basic Theory",
            "Basic Assumptions",
            "Definitions",
            "Examples",
            "Constant Sequence",
            "Partial Sums",
            "Martingale Difference Sequences",
            "Discrete-Time Random Walks",
            "Partial Products",
            "The Simple Random Walk",
            "The Beta-Bernoulli Process",
            "Urn Process",
            "Processes with Independent Increments",
            "Likelihood Ratio Tests",
            "Branching Processes",
            "Doob's Martingale",
            "Density Functions",
            "Details:",
        ),
    },
    {
        "rel": "martingales/Properties.html",
        "authority_sha256": "0f8bc07eb5eda38e8d4f78e94ba71a7dae8e9b788278f9b6ed250b0f66dc3850",
        "source_title": "Properties and Constructions",
        "nav_label": "Sifat dan konstruksi martingal",
        "rights_id": "o009-rights-random-martingale-properties",
        "fragment_corrections": {},
        "reader_corrections": MARTINGALE_PROPERTIES_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Properties and Constructions",
            "Basic Theory",
            "Preliminaries",
            "Basic Properties",
            "Martingale Transforms",
            "Doob Decomposition",
            "Markov Processes",
            "Examples",
            "Random Walks",
            "Simple Random Walk",
            "Branching Processes",
            "Processes with Independent Increments",
            "Details:",
        ),
    },
    {
        "rel": "martingales/Stop.html",
        "authority_sha256": "8d4c674bec0d19a253405dfe8c06e4b4062d6ef82330f945d50e2c494955a5af",
        "source_title": "Stopping Times",
        "nav_label": "Waktu henti martingal",
        "rights_id": "o009-rights-random-martingale-stopping",
        "fragment_corrections": {},
        "reader_corrections": MARTINGALE_STOP_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Stopping Times",
            "Basic Theory",
            "Optional Stopping",
            "Stopped Martingales",
            "Optional Stopping in Discrete Time",
            "Examples and Applications",
            "Simple Random Walk",
            "Wald's Equation",
            "Patterns in Multinomial Trials",
            "Secretary Problem",
            "Details:",
        ),
    },
    {
        "rel": "martingales/Inequalities.html",
        "authority_sha256": "9e03259e83a9e8ac67c9a43a2df1aa8a85d65944f86b82653e46869f4ab451f3",
        "source_title": "Inequalities",
        "nav_label": "Pertidaksamaan martingal",
        "rights_id": "o009-rights-random-martingale-inequalities",
        "fragment_corrections": {},
        "reader_corrections": MARTINGALE_INEQUALITIES_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Inequalities",
            "Basic Theory",
            "Basic Assumptions",
            "Maximal Inequalities",
            "The Up-Crossing Inequality",
            "Examples and Applications",
            "Kolmogorov's Inequality",
            "Red and Black",
            "Details:",
        ),
    },
    {
        "rel": "martingales/Convergence.html",
        "authority_sha256": "c5ef4134737d39992647bc1bf7ab4c9b16814f11450e53e7f54642ec64bdea0f",
        "source_title": "Convergence",
        "nav_label": "Konvergensi martingal",
        "rights_id": "o009-rights-random-martingale-convergence",
        "fragment_corrections": {},
        "reader_corrections": MARTINGALE_CONVERGENCE_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Convergence",
            "Basic Theory",
            "Basic Assumptions",
            "The Martingale Convergence Theorems",
            "Example and Applications",
            "Simple Random Walk",
            "Doob's Martingale",
            "Kolmogorov Zero-One Law",
            "Branching Processes",
            "The Beta-Bernoulli Process",
            "Pólya's Urn Process",
            "Likelihood Ratio Tests",
            "Partial Products",
            "Density Functions",
            "Details:",
        ),
    },
    {
        "rel": "martingales/Backwards.html",
        "authority_sha256": "adae3d5409d9f698129b8b21dfe9f1cd8d3045e2bd3f79e42cbc70751b7b28ba",
        "source_title": "Backwards Martingales",
        "nav_label": "Martingal mundur",
        "rights_id": "o009-rights-random-martingale-backwards",
        "fragment_corrections": {},
        "reader_corrections": MARTINGALE_BACKWARDS_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Backwards Martingales",
            "Basic Theory",
            "Definitions",
            "Properties",
            "Applications",
            "The Strong Law of Large Numbers",
            "Exchangeable Variables",
            "Details:",
        ),
    },
    {
        "rel": "markov/General.html",
        "authority_sha256": "69b4f54fd8c976d8a7093b3bfb9e0b3e836aa60794d1ad262e55c9b4b27f043c",
        "source_title": "General Markov Processes",
        "nav_label": "Proses Markov umum",
        "rights_id": "o009-rights-random-markov-general",
        "fragment_corrections": {},
        "reader_corrections": MARKOV_GENERAL_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "General Markov Processes",
            "Basic Theory",
            "Preliminaries",
            "Definitions",
            "Feller Processes",
            "Stopping Times and the Strong Markov Property",
            "Transition Kernels of Markov Processes",
            "Sampling in Time",
            "Enlarging the State Space",
            "Examples and Applications",
            "Recurrence Relations and Differential Equations",
            "Processes with Stationary, Independent Increments",
            "Additional details:",
            "Details:",
        ),
    },
    {
        "rel": "markov/Discrete.html",
        "authority_sha256": "808118b103e17cd5e31115b953663b0d8ff94da21f432e6fe7c104e9300380f0",
        "source_title": "Discrete-Time Markov Chains",
        "nav_label": "Rantai Markov waktu diskret",
        "rights_id": "o009-rights-random-markov-discrete",
        "fragment_corrections": {},
        "reader_corrections": MARKOV_DISCRETE_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Discrete-Time Markov Chains",
            "Basic Theory",
            "Review",
            "Definitions",
            "Stopping Times and the Strong Markov Property",
            "Transition Matrices",
            "Potential Matrices",
            "Sampling in Time",
            "Examples and Applications",
            "Computational Exercises",
            "Two-State Chain",
            "Independent Variables and Random Walks",
            "Doubly Stochastic Matrices",
            "Special Models",
            "Details:",
        ),
    },
    {
        "rel": "markov/Recurrence.html",
        "authority_sha256": "24edb8bd0237b0e3abd7beeae48596f35421c9aa35653c6845cfaebb223c5535",
        "source_title": "Transience and Recurrence",
        "nav_label": "Keadaan transien dan rekuren",
        "rights_id": "o009-rights-random-markov-recurrence",
        "fragment_corrections": {},
        "reader_corrections": MARKOV_RECURRENCE_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Transience and Recurrence",
            "Basic Theory",
            "Hitting Times and Probabilities",
            "Counting Variables and Potentials",
            "Relations",
            "Transient and Recurrent Classes",
            "Staying Probabilities and a Classification Test",
            "Computing Hitting Probabilities and Potentials",
            "Examples and Applications",
            "Finite Chains",
            "Special Models",
            "Details:",
            "Example:",
        ),
    },
    {
        "rel": "markov/Periodicity.html",
        "authority_sha256": "6311c165cff1538b2b8da7ff2f5b6d243b86cb6f1e7cb423a2712c3a7689f9b3",
        "source_title": "Periodicity",
        "nav_label": "Periodisitas",
        "rights_id": "o009-rights-random-markov-periodicity",
        "fragment_corrections": {},
        "reader_corrections": MARKOV_PERIODICITY_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Periodicity",
            "Basic Theory",
            "Definitions and Basic Results",
            "The Cyclic Classes",
            "Examples and Special Cases",
            "Finite Chains",
            "Special Models",
            "Details:",
        ),
    },
    {
        "rel": "markov/Limiting.html",
        "authority_sha256": "d4719c5e1cb9ad3be4fbf84c8dd849390f7d1ad15ced112f6312be83e5545680",
        "source_title": "Stationary and Limiting Distributions",
        "nav_label": "Distribusi invarian dan limit",
        "rights_id": "o009-rights-random-markov-limiting",
        "fragment_corrections": {},
        "reader_corrections": MARKOV_LIMITING_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Stationary and Limiting Distributions",
            "Basic Theory",
            "The Embedded Renewal Process",
            "Limiting Behavior",
            "Positive and Null Recurrence",
            "Limiting  Behavior, Revisited",
            "Invariant Distributions",
            "Invariant Measures",
            "Examples and Applications",
            "Finite Chains",
            "Special Models",
            "State graph",
            "Details:",
            "Open the simulation",
            "Markov Processes",
            "Data Sets",
            "Biographies",
        ),
    },
    {
        "rel": "poisson/General.html",
        "authority_sha256": "cdc957a1fb433c343ee4654af5350259baf15fcc37acbb4acf2c5a50077b6567",
        "source_title": "General Poisson Processes",
        "nav_label": "Proses Poisson pada ruang umum",
        "rights_id": "o009-rights-random-poisson-general",
        "fragment_corrections": {},
        "reader_notes": POISSON_GENERAL_READER_NOTES,
        "reader_corrections": POISSON_GENERAL_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "General Poisson Processes",
            "Basic Theory",
            "The Process",
            "The Distribution of the Random Points",
            "Thinning and Combining",
            "Applications and Special Cases",
            "Non-homogeneous Poisson Processes",
            "Nearest Points",
            "Computational Exercises",
            "Details:",
            "Data Sets",
            "Biographies",
        ),
    },
    {
        "rel": "brown/Standard.html",
        "authority_sha256": "442b4dacc55ce0ffc49fff5093ee2ad5adb75d337d45908e5e0df1448d84ebd8",
        "source_title": "Standard Brownian Motion",
        "nav_label": "Gerak Brown standar",
        "rights_id": "o009-rights-random-brown-standard",
        "fragment_corrections": {},
        "reader_notes": BROWN_STANDARD_READER_NOTES,
        "reader_corrections": BROWN_STANDARD_READER_CORRECTIONS,
        "tex_validation": "delimiter-token-stream-with-authority-unclosed-inline-witness",
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Standard Brownian Motion",
            "Basic Theory",
            "History",
            "Definition",
            "Brownian Motion as a Limit of Random Walks",
            "Finite Dimensional Distributions",
            "Simple Transformations",
            "Irregularity",
            "The Markov Property and Stopping Times",
            "The Reflection Principle",
            "Martingales",
            "Maximums and Hitting Times",
            "Zeros and Arcsine Laws",
            "The Law of the Iterated Logarithm",
            "Computational Exercises",
            "Details:",
            "Data Sets",
            "Biographies",
        ),
    },
    {
        "rel": "brown/Drift.html",
        "authority_sha256": "f1603646520d3c83fa986e6b0be7bcac6862d7443e57d0a28264534da3dc70d5",
        "source_title": "Brownian Motion with Drift",
        "nav_label": "Gerak Brown dengan hanyutan",
        "rights_id": "o009-rights-random-brown-drift",
        "fragment_corrections": {},
        "reader_notes": BROWN_DRIFT_READER_NOTES,
        "reader_corrections": BROWN_DRIFT_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Brownian Motion with Drift",
            "Basic Theory",
            "Definition",
            "Finite Dimensional Distributions",
            "Transformations",
            "The Markov Property and Stopping Times",
            "Computational Exercises",
            "Details:",
            "Data Sets",
            "Biographies",
        ),
    },
    {
        "rel": "brown/Bridge.html",
        "authority_sha256": "62e8b18c32f191f801e4cb9be3ee0db3fb658329d937b0807c6d8b8d7b37410e",
        "source_title": "The Brownian Bridge",
        "nav_label": "Jembatan Brown",
        "rights_id": "o009-rights-random-brown-bridge",
        "fragment_corrections": {},
        "reader_notes": BROWN_BRIDGE_READER_NOTES,
        "reader_corrections": BROWN_BRIDGE_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "The Brownian Bridge",
            "Basic Theory",
            "Definition and Constructions",
            "The General Brownian Bridge",
            "Applications",
            "The Empirical Distribution Function",
            "Details:",
            "Data Sets",
            "Biographies",
        ),
    },
    {
        "rel": "brown/Geometric.html",
        "authority_sha256": "4a6c1fa4c4d1cd7d646f700d438201af2b75fead1f094ecb4720d2831343f6ce",
        "source_title": "Geometric Brownian Motion",
        "nav_label": "Gerak Brown geometrik",
        "rights_id": "o009-rights-random-brown-geometric",
        "fragment_corrections": {},
        "reader_notes": BROWN_GEOMETRIC_READER_NOTES,
        "reader_corrections": BROWN_GEOMETRIC_READER_CORRECTIONS,
        "forbidden": (
            "Expand Details",
            "Contract Details",
            "Geometric Brownian Motion",
            "Basic Theory",
            "Definition",
            "Distributions",
            "Moments",
            "Properties",
            "Details:",
            "Data Sets",
            "Biographies",
        ),
    },
    {
        "rel": "martingales/index.html",
        "authority_sha256": "92b98c9e04ad843647041974d54ba6557aedf51d393ff540af4f27a868aa791e",
        "source_title": "Martingales",
        "nav_label": "Ikhtisar martingal",
        "rights_id": "o009-rights-random-martingales-index",
        "unit_kind": "overview",
        "fragment_corrections": {},
        "metadata_href_corrections": {
            "../renewal/index.html": "../markov/index.html",
            "../markov/index.html": "../brown/index.html",
        },
        "reader_corrections": MARTINGALES_INDEX_READER_CORRECTIONS,
        "forbidden": (
            "Summary",
            "Topics",
            "Properties and Constructions",
            "Stopping Times",
            "Backwards Martingales",
            "Data Sets",
            "Biographies",
        ),
    },
    {
        "rel": "markov/index.html",
        "authority_sha256": "18dfcf15b97a2af7d90404e879376234865bfb40985deb4d6e50b9778f5f7660",
        "source_title": "Markov Processes",
        "nav_label": "Ikhtisar proses Markov",
        "rights_id": "o009-rights-random-markov-index",
        "unit_kind": "overview",
        "fragment_corrections": {},
        "metadata_href_corrections": {
            "../brown/index.html": "../martingales/index.html",
        },
        "reader_notes": MARKOV_INDEX_READER_NOTES,
        "reader_corrections": MARKOV_INDEX_READER_CORRECTIONS,
        "forbidden": (
            "Summary",
            "Special Discrete-Time Chains",
            "Special Continuous-Time Chains",
            "Two-State, Discrete-Time Chain",
            "Success-Runs Chain",
            "Remaining-Life Chain",
            "Data Sets",
            "Biographies",
        ),
    },
    {
        "rel": "brown/index.html",
        "authority_sha256": "c471c5a1b2bd85731eded48e1ba7a0337c1b752b56fcadde87e213eacf2a7b4a",
        "source_title": "Brownian Motion",
        "nav_label": "Ikhtisar gerak Brown",
        "rights_id": "o009-rights-random-brown-index",
        "unit_kind": "overview",
        "fragment_corrections": {
            "JavaScript:openAncillary('../apps/.html../apps/AbsoluteBrownianMotion.html')": "https://www.randomservices.org/random/apps/AbsoluteBrownianMotion.html",
        },
        "metadata_href_corrections": {
            "../Markov/index.html": "../martingales/index.html",
        },
        "reader_notes": BROWN_INDEX_READER_NOTES,
        "reader_corrections": BROWN_INDEX_READER_CORRECTIONS,
        "forbidden": (
            "Summary",
            "Basic Topics",
            "Special Processes",
            "Absolute Brownian Motion",
            "Reflected Brownian Motion",
            "Integrated Brownian Motion",
            "Two-Dimensional Brownian Motion",
            "Hitting Time Experiment",
            "Data Sets",
            "Biographies",
        ),
    },
)
ORIGINAL_BRIDGE_SPECS = (
    {
        "source": ROOT / "source" / "original" / "01-konstruksi-kolmogorov.md",
        "output": Path("original/01-konstruksi-kolmogorov.html"),
        "title": "Konstruksi Kolmogorov dan proses kanonik",
        "unit_id": "unit.o009.original.bridge.kolmogorov-canonical-process",
        "rights_id": "rights.o009.original.bridge.kolmogorov.cc-by-4.0",
        "previous_output": Path("brown/Geometric.html"),
        "previous_label": "Unit Random sebelumnya",
        "source_bytes": 34418,
        "source_sha256": "bf37d6b746e617b5010a96be0c105e7f4ecd33e39a22b6a0f0528cd6b48cd164",
        "required_witnesses": (
            'title: "Konstruksi Kolmogorov dan proses kanonik"',
            "lang: id-ID",
            'unit_id: "unit.o009.original.bridge.kolmogorov-canonical-process"',
            'rights_id: "rights.o009.original.bridge.kolmogorov.cc-by-4.0"',
            'license: "CC-BY-4.0"',
            'model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."',
            "ruang Borel standar",
            "konsisten secara proyektif",
            r"\mathcal S^{\otimes T}",
            "Keunikan pada sigma-aljabar produk",
            "../prob/Probability2.html",
            "../prob/Processes.html",
            "../quantecon/lectures/markov_prop.html",
            "../brown/Standard.html",
            "tidak mengubah lisensi apa pun",
            "tidak mendukung, mengesahkan, atau",
            "OpenAI Codex gpt-5.6-sol, Ultra.",
        ),
        "expected_class_counts": {
            "original-bridge": 1,
            "bridge-section": 11,
            "mastery-sequence": 3,
            "exercise": 3,
            "hint": 6,
            "answer": 3,
            "solution": 3,
        },
        "disclosure_count": 9,
        "mastery_counts": {
            "exercises": 3,
            "hints": 6,
            "answers": 3,
            "solutions": 3,
        },
        "built_rights_witnesses": (
            "rights.o009.original.bridge.kolmogorov.cc-by-4.0",
            "Creative Commons Attribution 4.0 International",
            "OpenAI Codex gpt-5.6-sol, Ultra.",
            "tidak mengubah lisensi apa pun",
            "tidak mendukung, mengesahkan, atau mensponsori",
        ),
        "word_bounds": (3000, 4500),
        "stable_ids": (
            "unit.o009.original.bridge.kolmogorov-canonical-process",
            "tujuan-dan-prasyarat",
            "ruang-lintasan-produk",
            "konsistensi-proyektif",
            "teorema-perluasan-kolmogorov",
            "lingkup-bukti",
            "proses-koordinat-kanonik",
            "contoh-keluarga-markov",
            "contoh-keluarga-gaussian",
            "audit-hipotesis-dan-bukan-klaim",
            "latihan-penguasaan",
            "unit.o009.original.mastery.process-construction.01",
            "unit.o009.original.mastery.process-construction.01.exercise",
            "unit.o009.original.mastery.process-construction.01.hint.01",
            "unit.o009.original.mastery.process-construction.01.hint.02",
            "unit.o009.original.mastery.process-construction.01.answer",
            "unit.o009.original.mastery.process-construction.01.solution",
            "unit.o009.original.mastery.process-construction.02",
            "unit.o009.original.mastery.process-construction.02.exercise",
            "unit.o009.original.mastery.process-construction.02.hint.01",
            "unit.o009.original.mastery.process-construction.02.hint.02",
            "unit.o009.original.mastery.process-construction.02.answer",
            "unit.o009.original.mastery.process-construction.02.solution",
            "unit.o009.original.mastery.process-construction.03",
            "unit.o009.original.mastery.process-construction.03.exercise",
            "unit.o009.original.mastery.process-construction.03.hint.01",
            "unit.o009.original.mastery.process-construction.03.hint.02",
            "unit.o009.original.mastery.process-construction.03.answer",
            "unit.o009.original.mastery.process-construction.03.solution",
            "hak-dan-provenans",
        ),
        "disclosures": (
            (
                "unit.o009.original.mastery.process-construction.01.hint.01",
                "Petunjuk 1 untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.process-construction.01.hint.02",
                "Petunjuk 2 untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.process-construction.01.solution",
                "Penyelesaian lengkap untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.process-construction.02.hint.01",
                "Petunjuk 1 untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.process-construction.02.hint.02",
                "Petunjuk 2 untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.process-construction.02.solution",
                "Penyelesaian lengkap untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.process-construction.03.hint.01",
                "Petunjuk 1 untuk Latihan 3",
            ),
            (
                "unit.o009.original.mastery.process-construction.03.hint.02",
                "Petunjuk 2 untuk Latihan 3",
            ),
            (
                "unit.o009.original.mastery.process-construction.03.solution",
                "Penyelesaian lengkap untuk Latihan 3",
            ),
        ),
    },
    {
        "source": (
            ROOT
            / "source"
            / "original"
            / "02-keterukuran-proses-dan-hukum-lintasan.md"
        ),
        "output": Path("original/02-keterukuran-proses-dan-hukum-lintasan.html"),
        "title": "Keterukuran proses dan hukum lintasan",
        "unit_id": "unit.o009.original.bridge.process-measurability-path-law",
        "rights_id": (
            "rights.o009.original.bridge.process-measurability-path-law.cc-by-4.0"
        ),
        "previous_output": Path("original/01-konstruksi-kolmogorov.html"),
        "previous_label": "Jembatan asli sebelumnya",
        "source_bytes": 29971,
        "source_sha256": "f14bd9e7ad6a80079eb40609dd97f9768e08fae5bc638e9d5939666f53ad0acb",
        "required_witnesses": (
            'title: "Keterukuran proses dan hukum lintasan"',
            "lang: id-ID",
            'unit_id: "unit.o009.original.bridge.process-measurability-path-law"',
            (
                'rights_id: "rights.o009.original.bridge.'
                'process-measurability-path-law.cc-by-4.0"'
            ),
            'license: "CC-BY-4.0"',
            'model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."',
            "keterukuran bersama",
            "distribusi berdimensi hingga",
            "hukum lintasan mentah",
            r"\mathcal T\otimes\mathcal A",
            r"Setiap $E\in\mathcal S^{\otimes T}$ bergantung pada paling banyak terhitung",
            "01-konstruksi-kolmogorov.html",
            "../prob/Probability2.html",
            "../prob/Processes.html",
            "melisensikan ulang komponen mereka",
            "tidak didukung atau disahkan",
            "OpenAI Codex gpt-5.6-sol, Ultra.",
        ),
        "expected_class_counts": {
            "original-bridge": 1,
            "bridge-section": 10,
            "mastery-sequence": 3,
            "exercise": 3,
            "hint": 6,
            "answer": 3,
            "solution": 3,
        },
        "disclosure_count": 9,
        "mastery_counts": {
            "exercises": 3,
            "hints": 6,
            "answers": 3,
            "solutions": 3,
        },
        "built_rights_witnesses": (
            (
                "rights.o009.original.bridge."
                "process-measurability-path-law.cc-by-4.0"
            ),
            "CC BY 4.0",
            "OpenAI Codex gpt-5.6-sol, Ultra.",
            "melisensikan ulang komponen mereka",
            "tidak didukung atau disahkan",
        ),
        "word_bounds": (2500, 4000),
        "stable_ids": (
            "unit.o009.original.bridge.process-measurability-path-law",
            "tujuan-dan-empat-lapis-objek",
            "peta-lintasan-mentah",
            "keterukuran-bersama",
            "fdd-dan-hukum-lintasan-mentah",
            "sifat-lintasan-di-ruang-mentah",
            "hukum-pada-ruang-lintasan-kontinu",
            "modifikasi-dan-ketakterbedaan",
            "audit-klaim-lintasan",
            "latihan-penguasaan-keterukuran",
            "unit.o009.original.mastery.measurability-path-law.01",
            "unit.o009.original.mastery.measurability-path-law.01.exercise",
            "unit.o009.original.mastery.measurability-path-law.01.hint.01",
            "unit.o009.original.mastery.measurability-path-law.01.hint.02",
            "unit.o009.original.mastery.measurability-path-law.01.answer",
            "unit.o009.original.mastery.measurability-path-law.01.solution",
            "unit.o009.original.mastery.measurability-path-law.02",
            "unit.o009.original.mastery.measurability-path-law.02.exercise",
            "unit.o009.original.mastery.measurability-path-law.02.hint.01",
            "unit.o009.original.mastery.measurability-path-law.02.hint.02",
            "unit.o009.original.mastery.measurability-path-law.02.answer",
            "unit.o009.original.mastery.measurability-path-law.02.solution",
            "unit.o009.original.mastery.measurability-path-law.03",
            "unit.o009.original.mastery.measurability-path-law.03.exercise",
            "unit.o009.original.mastery.measurability-path-law.03.hint.01",
            "unit.o009.original.mastery.measurability-path-law.03.hint.02",
            "unit.o009.original.mastery.measurability-path-law.03.answer",
            "unit.o009.original.mastery.measurability-path-law.03.solution",
            "hak-dan-provenans-keterukuran",
        ),
        "disclosures": (
            (
                "unit.o009.original.mastery.measurability-path-law.01.hint.01",
                "Petunjuk 1 untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.measurability-path-law.01.hint.02",
                "Petunjuk 2 untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.measurability-path-law.01.solution",
                "Penyelesaian lengkap untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.measurability-path-law.02.hint.01",
                "Petunjuk 1 untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.measurability-path-law.02.hint.02",
                "Petunjuk 2 untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.measurability-path-law.02.solution",
                "Penyelesaian lengkap untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.measurability-path-law.03.hint.01",
                "Petunjuk 1 untuk Latihan 3",
            ),
            (
                "unit.o009.original.mastery.measurability-path-law.03.hint.02",
                "Petunjuk 2 untuk Latihan 3",
            ),
            (
                "unit.o009.original.mastery.measurability-path-law.03.solution",
                "Penyelesaian lengkap untuk Latihan 3",
            ),
        ),
    },
    {
        "source": (
            ROOT
            / "source"
            / "original"
            / "03-probabilitas-bersyarat-reguler.md"
        ),
        "output": Path("original/03-probabilitas-bersyarat-reguler.html"),
        "title": "Distribusi bersyarat reguler dan disiplin versi",
        "unit_id": "unit.o009.original.bridge.regular-conditional-probability",
        "rights_id": (
            "rights.o009.original.bridge.regular-conditional-probability.cc-by-4.0"
        ),
        "previous_output": Path(
            "original/02-keterukuran-proses-dan-hukum-lintasan.html"
        ),
        "previous_label": "Jembatan asli sebelumnya",
        "source_bytes": 34016,
        "source_sha256": "d24d06e9c5e60c2d0a70ee0ff00fd0e2e7687e12a12404b6f7e903af76ccbe44",
        "required_witnesses": (
            'title: "Distribusi bersyarat reguler dan disiplin versi"',
            "lang: id-ID",
            (
                'unit_id: "unit.o009.original.bridge.'
                'regular-conditional-probability"'
            ),
            (
                'rights_id: "rights.o009.original.bridge.'
                'regular-conditional-probability.cc-by-4.0"'
            ),
            'license: "CC-BY-4.0"',
            'model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."',
            "ruang Borel standar",
            "kelas penentu terhitung",
            "disintegrasi",
            "nilai pengondisian yang bermassa nol",
            "../expect/Conditional2.html",
            "../expect/Kernels.html",
            "01-konstruksi-kolmogorov.html",
            "02-keterukuran-proses-dan-hukum-lintasan.html",
            "tidak melisensikan ulang Random Services",
            "tidak didukung atau disahkan",
            "OpenAI Codex gpt-5.6-sol, Ultra.",
        ),
        "expected_class_counts": {
            "original-bridge": 1,
            "bridge-section": 11,
            "mastery-sequence": 3,
            "exercise": 3,
            "hint": 6,
            "answer": 3,
            "solution": 3,
        },
        "disclosure_count": 9,
        "mastery_counts": {
            "exercises": 3,
            "hints": 6,
            "answers": 3,
            "solutions": 3,
        },
        "built_rights_witnesses": (
            (
                "rights.o009.original.bridge."
                "regular-conditional-probability.cc-by-4.0"
            ),
            "CC BY 4.0",
            "OpenAI Codex gpt-5.6-sol, Ultra.",
            "tidak melisensikan ulang Random Services",
            "tidak didukung atau disahkan",
        ),
        "word_bounds": (2800, 3800),
        "stable_ids": (
            "unit.o009.original.bridge.regular-conditional-probability",
            "tujuan-dan-kesenjangan-versi",
            "dari-nilai-harapan-ke-kernel",
            "keberadaan-pada-sasaran-borel-standar",
            "kelas-penentu-dan-versi-serentak",
            "pengondisian-pada-peubah-acak",
            "rumus-disintegrasi-dan-kepadatan",
            "nilai-pada-titik-pengondisian-nol",
            "probabilitas-bersyarat-seluruh-eksperimen",
            "audit-klaim-probabilitas-bersyarat",
            "latihan-penguasaan-probabilitas-bersyarat-reguler",
            "unit.o009.original.mastery.regular-conditional-probability.01",
            "unit.o009.original.mastery.regular-conditional-probability.01.exercise",
            "unit.o009.original.mastery.regular-conditional-probability.01.hint.01",
            "unit.o009.original.mastery.regular-conditional-probability.01.hint.02",
            "unit.o009.original.mastery.regular-conditional-probability.01.answer",
            "unit.o009.original.mastery.regular-conditional-probability.01.solution",
            "unit.o009.original.mastery.regular-conditional-probability.02",
            "unit.o009.original.mastery.regular-conditional-probability.02.exercise",
            "unit.o009.original.mastery.regular-conditional-probability.02.hint.01",
            "unit.o009.original.mastery.regular-conditional-probability.02.hint.02",
            "unit.o009.original.mastery.regular-conditional-probability.02.answer",
            "unit.o009.original.mastery.regular-conditional-probability.02.solution",
            "unit.o009.original.mastery.regular-conditional-probability.03",
            "unit.o009.original.mastery.regular-conditional-probability.03.exercise",
            "unit.o009.original.mastery.regular-conditional-probability.03.hint.01",
            "unit.o009.original.mastery.regular-conditional-probability.03.hint.02",
            "unit.o009.original.mastery.regular-conditional-probability.03.answer",
            "unit.o009.original.mastery.regular-conditional-probability.03.solution",
            "hak-dan-provenans-probabilitas-bersyarat",
        ),
        "disclosures": (
            (
                "unit.o009.original.mastery.regular-conditional-probability.01.hint.01",
                "Petunjuk 1 untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.regular-conditional-probability.01.hint.02",
                "Petunjuk 2 untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.regular-conditional-probability.01.solution",
                "Penyelesaian lengkap untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.regular-conditional-probability.02.hint.01",
                "Petunjuk 1 untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.regular-conditional-probability.02.hint.02",
                "Petunjuk 2 untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.regular-conditional-probability.02.solution",
                "Penyelesaian lengkap untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.regular-conditional-probability.03.hint.01",
                "Petunjuk 1 untuk Latihan 3",
            ),
            (
                "unit.o009.original.mastery.regular-conditional-probability.03.hint.02",
                "Petunjuk 2 untuk Latihan 3",
            ),
            (
                "unit.o009.original.mastery.regular-conditional-probability.03.solution",
                "Penyelesaian lengkap untuk Latihan 3",
            ),
        ),
    },
    {
        "source": (
            ROOT
            / "source"
            / "original"
            / "04-audit-hipotesis-proses-stokastik.md"
        ),
        "output": Path("original/04-audit-hipotesis-proses-stokastik.html"),
        "title": "Audit hipotesis untuk proses stokastik",
        "unit_id": "unit.o009.original.bridge.hypothesis-audits",
        "rights_id": (
            "rights.o009.original.bridge.hypothesis-audits.cc-by-4.0"
        ),
        "previous_output": Path(
            "original/03-probabilitas-bersyarat-reguler.html"
        ),
        "previous_label": "Jembatan asli sebelumnya",
        "source_bytes": 39925,
        "source_sha256": "be6de4f7b2fc63bbfee8be51b3dd8ac733edff5d58374c7a71891d0ab20d4bfd",
        "required_witnesses": (
            'title: "Audit hipotesis untuk proses stokastik"',
            "lang: id-ID",
            'unit_id: "unit.o009.original.bridge.hypothesis-audits"',
            (
                'rights_id: "rights.o009.original.bridge.'
                'hypothesis-audits.cc-by-4.0"'
            ),
            'license: "CC-BY-4.0"',
            'model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."',
            "lima kotak",
            "Klaim uji",
            "keterintegralan seragam",
            "waktu henti berhingga hampir pasti belum cukup",
            "M_t=2N_t",
            "keketatan",
            "../expect/Uniform.html#con",
            "../expect/Conditional2.html#bay",
            "../martingales/Stop.html#stp3",
            "../quantecon/lectures/ergodicity.html#uniirr",
            "../quantecon/lectures/poisson.html#keunikan",
            "../brown/Standard.html#wlk",
            (
                "correction.o009.random.martingales.stop."
                "optional-stopping-missing-variables"
            ),
            "tidak mereproduksi prosa donor secara",
            "tidak didukung atau disahkan",
            "OpenAI Codex gpt-5.6-sol, Ultra.",
        ),
        "expected_class_counts": {
            "original-bridge": 1,
            "bridge-section": 10,
            "mastery-sequence": 3,
            "exercise": 3,
            "hint": 6,
            "answer": 3,
            "solution": 3,
        },
        "disclosure_count": 9,
        "mastery_counts": {
            "exercises": 3,
            "hints": 6,
            "answers": 3,
            "solutions": 3,
        },
        "built_rights_witnesses": (
            "rights.o009.original.bridge.hypothesis-audits.cc-by-4.0",
            "CC BY 4.0",
            "OpenAI Codex gpt-5.6-sol, Ultra.",
            "tidak mereproduksi prosa donor secara",
            "tidak didukung atau disahkan",
        ),
        "word_bounds": (3500, 4300),
        "stable_ids": (
            "unit.o009.original.bridge.hypothesis-audits",
            "tujuan-dan-protokol-audit-hipotesis",
            "audit-konvergensi-dan-integrabilitas",
            "audit-pengondisian-dan-kernel",
            "audit-martingal-dan-waktu-henti",
            "audit-markov-dan-ctmc",
            "audit-poisson-dan-konstruksi-proses",
            "audit-brown-dan-hukum-lintasan",
            "matriks-perbaikan-klaim",
            "latihan-penguasaan-audit-hipotesis",
            "unit.o009.original.mastery.hypothesis-audits.01",
            "unit.o009.original.mastery.hypothesis-audits.01.exercise",
            "unit.o009.original.mastery.hypothesis-audits.01.hint.01",
            "unit.o009.original.mastery.hypothesis-audits.01.hint.02",
            "unit.o009.original.mastery.hypothesis-audits.01.answer",
            "unit.o009.original.mastery.hypothesis-audits.01.solution",
            "unit.o009.original.mastery.hypothesis-audits.02",
            "unit.o009.original.mastery.hypothesis-audits.02.exercise",
            "unit.o009.original.mastery.hypothesis-audits.02.hint.01",
            "unit.o009.original.mastery.hypothesis-audits.02.hint.02",
            "unit.o009.original.mastery.hypothesis-audits.02.answer",
            "unit.o009.original.mastery.hypothesis-audits.02.solution",
            "unit.o009.original.mastery.hypothesis-audits.03",
            "unit.o009.original.mastery.hypothesis-audits.03.exercise",
            "unit.o009.original.mastery.hypothesis-audits.03.hint.01",
            "unit.o009.original.mastery.hypothesis-audits.03.hint.02",
            "unit.o009.original.mastery.hypothesis-audits.03.answer",
            "unit.o009.original.mastery.hypothesis-audits.03.solution",
            "hak-dan-provenans-audit-hipotesis",
        ),
        "disclosures": (
            (
                "unit.o009.original.mastery.hypothesis-audits.01.hint.01",
                "Petunjuk 1 untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.hypothesis-audits.01.hint.02",
                "Petunjuk 2 untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.hypothesis-audits.01.solution",
                "Penyelesaian lengkap untuk Latihan 1",
            ),
            (
                "unit.o009.original.mastery.hypothesis-audits.02.hint.01",
                "Petunjuk 1 untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.hypothesis-audits.02.hint.02",
                "Petunjuk 2 untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.hypothesis-audits.02.solution",
                "Penyelesaian lengkap untuk Latihan 2",
            ),
            (
                "unit.o009.original.mastery.hypothesis-audits.03.hint.01",
                "Petunjuk 1 untuk Latihan 3",
            ),
            (
                "unit.o009.original.mastery.hypothesis-audits.03.hint.02",
                "Petunjuk 2 untuk Latihan 3",
            ),
            (
                "unit.o009.original.mastery.hypothesis-audits.03.solution",
                "Penyelesaian lengkap untuk Latihan 3",
            ),
        ),
    },
)
MATH_SURFACE_RE = re.compile(
    r"\\\(.*?\\\)|\\\[.*?\\\]|"
    r"\\begin\{(?P<environment>[A-Za-z]+\*?)\}.*?\\end\{(?P=environment)\}",
    re.DOTALL,
)
TEX_DELIMITER_TOKEN_RE = re.compile(
    r"\\\(|\\\)|\\\[|\\\]|\\begin\{[A-Za-z]+\*?\}|\\end\{[A-Za-z]+\*?\}"
)
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.I)
FENCED_DIV_OPEN_RE = re.compile(
    r"^::: \{#(?P<id>\S+)(?P<classes>(?:\s+\.[A-Za-z0-9_-]+)+)\}\s*$",
    re.MULTILINE,
)
PLACEHOLDER = str(LAB_SPECS[0]["placeholder"])


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_file(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"missing or linked regular file: {path}")
    return path.read_bytes()


def validate_lab_specs() -> None:
    """Reject ambiguous, escaping, or incompletely bound lab declarations."""
    seen: dict[str, set[str]] = {
        "source": set(),
        "output": set(),
        "chunk_id": set(),
        "placeholder": set(),
        "table_id": set(),
    }
    lab_root = (ROOT / "source" / "labs").resolve()
    for spec in LAB_SPECS:
        source = Path(spec["source"])
        require_file(source)
        try:
            source.resolve().relative_to(lab_root)
        except ValueError as exc:
            raise RuntimeError(f"lab source escapes source/labs: {source}") from exc
        output = Path(spec["output"])
        if (
            output.is_absolute()
            or output.suffix != ".html"
            or not output.parts
            or output.parts[0] != "labs"
            or any(part in {"", ".", ".."} for part in output.parts)
        ):
            raise RuntimeError(f"unsafe lab output path: {output}")
        identifiers = (str(spec["chunk_id"]), str(spec["table_id"]))
        if any(re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", value) is None for value in identifiers):
            raise RuntimeError(f"unsafe lab identifier declaration: {identifiers}")
        fields = tuple(str(value) for value in spec["expected_fields"])
        headers = tuple(str(value) for value in spec["table_headers"])
        if not fields or len(fields) != len(set(fields)) or len(fields) != len(headers):
            raise RuntimeError(f"invalid lab result schema: {spec['chunk_id']}")
        golden_rows = [dict(row) for row in spec["golden_rows"]]
        if not golden_rows or any(tuple(row) != fields for row in golden_rows):
            raise RuntimeError(f"golden lab rows do not match declared schema: {spec['chunk_id']}")

        text = require_file(source).decode("utf-8")
        if "\r" in text:
            raise RuntimeError(f"lab source must use LF line endings: {source}")
        front = re.match(r"\A---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
        if front is None:
            raise RuntimeError(f"lab source lacks a bounded YAML metadata block: {source}")
        metadata: dict[str, list[str]] = {}
        for line in front.group("body").splitlines():
            item = re.match(r"^\s{0,2}([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", line)
            if item is None or not item.group(2):
                continue
            raw_value = item.group(2)
            try:
                value = json.loads(raw_value) if raw_value.startswith('"') else raw_value
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"invalid quoted YAML scalar in {source}: {line}") from exc
            metadata.setdefault(item.group(1), []).append(str(value))
        for key, expected in dict(spec["front_matter"]).items():
            if metadata.get(str(key)) != [str(expected)]:
                raise RuntimeError(
                    f"lab front matter differs for {spec['chunk_id']}:{key}: "
                    f"{metadata.get(str(key))!r}"
                )
        missing_witnesses = [
            str(witness)
            for witness in spec.get("required_witnesses", ())
            if str(witness) not in text
        ]
        if missing_witnesses:
            raise RuntimeError(
                f"lab rights/dependency disclosure differs for "
                f"{spec['chunk_id']}: {missing_witnesses!r}"
            )
        if text.count(str(spec["placeholder"])) != 1:
            raise RuntimeError(f"lab placeholder is not exact-once: {spec['chunk_id']}")
        if len(lab_chunk_re(spec).findall(text)) != 1:
            raise RuntimeError(f"lab executable chunk is not exact-once: {spec['chunk_id']}")

        values = {
            "source": source.resolve().as_posix().casefold(),
            "output": output.as_posix().casefold(),
            "chunk_id": str(spec["chunk_id"]),
            "placeholder": str(spec["placeholder"]),
            "table_id": str(spec["table_id"]),
        }
        for kind, value in values.items():
            if value in seen[kind]:
                raise RuntimeError(f"duplicate lab {kind}: {value}")
            seen[kind].add(value)


@lru_cache(maxsize=1)
def runtime_evidence() -> dict[str, object]:
    """Probe and hash the exact executables used by the deterministic build."""
    if sha256(require_file(R_SCRIPT)) != R_SCRIPT_SHA256:
        raise RuntimeError("Rscript executable hash changed")
    with tempfile.TemporaryDirectory(prefix="o009-runtime-") as temp:
        env = dict(os.environ)
        env["LC_ALL"] = "C"
        env["R_USER"] = temp
        probe = subprocess.run(
            [
                str(R_SCRIPT),
                "--vanilla",
                "-e",
                'cat(R.version.string, "\\n", paste(RNGkind(), collapse=" / "), "\\n", sep="")',
            ],
            cwd=temp,
            env=env,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
    if probe.returncode != 0 or probe.stderr.strip():
        raise RuntimeError(f"R runtime probe failed: {probe.stderr.strip()}")
    r_lines = probe.stdout.splitlines()
    if r_lines != [R_VERSION, R_RNG]:
        raise RuntimeError(f"R runtime identity differs: {r_lines!r}")

    pandoc_command = shutil.which(PANDOC)
    if not pandoc_command:
        raise RuntimeError("pinned Pandoc command is unavailable")
    pandoc_path = Path(pandoc_command)
    if sha256(require_file(pandoc_path)) != PANDOC_SHA256:
        raise RuntimeError("Pandoc executable hash changed")
    pandoc_probe = subprocess.run(
        [str(pandoc_path), "--version"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if pandoc_probe.returncode != 0 or pandoc_probe.stderr.strip():
        raise RuntimeError(f"Pandoc runtime probe failed: {pandoc_probe.stderr.strip()}")
    pandoc_lines = pandoc_probe.stdout.splitlines()
    if not pandoc_lines or pandoc_lines[0] != PANDOC_VERSION:
        raise RuntimeError(f"Pandoc runtime identity differs: {pandoc_lines[:1]!r}")
    return {
        "r": {
            "command": "tools/R-4.6.1/bin/Rscript.exe",
            "sha256": R_SCRIPT_SHA256,
            "version": R_VERSION,
            "rng": R_RNG,
        },
        "pandoc": {
            "command": PANDOC,
            "sha256": PANDOC_SHA256,
            "version": PANDOC_VERSION,
        },
    }


def theory_paths(unit: dict[str, object]) -> tuple[Path, Path]:
    rel = Path(str(unit["rel"]))
    return AUTH_RANDOM / "static" / rel, ROOT / "source" / "theory" / rel


def validate_theory_unit(unit: dict[str, object]) -> None:
    authority, target_path = theory_paths(unit)
    source_bytes = require_file(authority)
    target_bytes = require_file(target_path)
    if sha256(source_bytes) != unit["authority_sha256"]:
        raise RuntimeError(f"Random authority hash changed: {unit['rel']}")
    source_text = source_bytes.decode("utf-8")
    target_text = target_bytes.decode("utf-8")
    source = BeautifulSoup(source_text, "lxml")
    target = BeautifulSoup(target_text, "lxml")
    source_tags = source.find_all(True)
    target_tags = target.find_all(True)
    if [tag.name for tag in source_tags] != [tag.name for tag in target_tags]:
        raise RuntimeError(f"translated theory element topology differs: {unit['rel']}")
    if len(source_tags) != len(target_tags):
        raise RuntimeError(f"translated theory element count differs: {unit['rel']}")
    for index, (left, right) in enumerate(zip(source_tags, target_tags, strict=True)):
        left_attrs = deepcopy(left.attrs)
        right_attrs = deepcopy(right.attrs)
        if left.name == "html":
            left_attrs.pop("lang", None)
            right_attrs.pop("lang", None)
        if left.name == "meta" and left.get("name") == "keywords":
            left_attrs.pop("content", None)
            right_attrs.pop("content", None)
        for permitted in ("alt", "title"):
            left_attrs.pop(permitted, None)
            right_attrs.pop(permitted, None)
        if left_attrs != right_attrs:
            raise RuntimeError(
                f"translated theory attribute drift in {unit['rel']} at tag {index}: "
                f"{left.name} {left_attrs!r} != {right_attrs!r}"
            )
    if target.html is None or target.html.get("lang") != "id-ID":
        raise RuntimeError(f"translated theory must declare lang=id-ID: {unit['rel']}")
    tex_validation = str(unit.get("tex_validation", "complete-surface-sequence"))
    if tex_validation == "complete-surface-sequence":
        source_math = [match.group(0) for match in MATH_SURFACE_RE.finditer(source_text)]
        target_math = [match.group(0) for match in MATH_SURFACE_RE.finditer(target_text)]
        if source_math != target_math:
            raise RuntimeError(f"translated theory TeX surface differs: {unit['rel']}")
    elif tex_validation == "delimiter-token-stream-with-authority-unclosed-inline-witness":
        source_tokens = TEX_DELIMITER_TOKEN_RE.findall(source_text)
        target_tokens = TEX_DELIMITER_TOKEN_RE.findall(target_text)
        if source_tokens != target_tokens or len(source_tokens) != 1157:
            raise RuntimeError(
                f"translated theory TeX delimiter stream differs: {unit['rel']}"
            )
        if (
            source_text.count(r"\(") - source_text.count(r"\)") != 1
            or target_text.count(r"\(") - target_text.count(r"\)") != 1
            or source_text.count(r"\( \mathscr{F}" + "\n\t</details>") != 1
            or target_text.count(r"\( \mathscr{F}" + "\n\t</details>") != 1
        ):
            raise RuntimeError(
                "translated theory no longer preserves the frozen unclosed-TeX "
                f"witness: {unit['rel']}"
            )
    else:
        raise RuntimeError(f"unknown TeX validation mode: {tex_validation}")
    ids = [str(tag["id"]) for tag in target.select("[id]")]
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"duplicate id in translated theory: {unit['rel']}")
    if any(not str(tag.get("alt", "")).strip() for tag in target.select("img")):
        raise RuntimeError(f"empty image alt in translated theory: {unit['rel']}")
    visible = " ".join(target.stripped_strings)
    forbidden = tuple(str(item) for item in unit["forbidden"])
    hits = [item for item in forbidden if item in visible]
    if hits:
        raise RuntimeError(f"active English theory residue in {unit['rel']}: {hits}")


def validate_theory_translation() -> None:
    for unit in THEORY_UNITS:
        validate_theory_unit(unit)


def original_bridge_word_count(text: str) -> int:
    """Count Indonesian prose while excluding front matter and TeX surfaces."""
    prose = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.DOTALL)
    prose = re.sub(r"\$\$.*?\$\$", " ", prose, flags=re.DOTALL)
    prose = re.sub(r"\$[^$\n]*\$", " ", prose)
    prose = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", prose)
    return len(
        re.findall(
            r"\b[^\W\d_][^\W_]*(?:[-’'][^\W\d_][^\W_]*)*\b",
            prose,
        )
    )


def validate_original_bridge_specs() -> None:
    """Bind each original bridge to its admitted bytes, IDs, scope, and rights."""
    if len(THEORY_UNITS) != 27:
        raise RuntimeError("the canonical Random theory tuple must remain exactly 27 pages")
    if len(ORIGINAL_BRIDGE_SPECS) != 4:
        raise RuntimeError("the current reader boundary must declare exactly four original bridges")
    source_root = (ROOT / "source" / "original").resolve()
    seen_outputs: set[str] = set()
    for spec in ORIGINAL_BRIDGE_SPECS:
        source = Path(spec["source"])
        data = require_file(source)
        try:
            source.resolve().relative_to(source_root)
        except ValueError as exc:
            raise RuntimeError(f"original bridge source escapes source/original: {source}") from exc
        output = Path(spec["output"])
        output_key = output.as_posix()
        if (
            output.is_absolute()
            or ".." in output.parts
            or output.suffix != ".html"
            or output.parts[:1] != ("original",)
        ):
            raise RuntimeError(f"unsafe original bridge output path: {output}")
        if output_key in seen_outputs:
            raise RuntimeError(f"duplicate original bridge output: {output}")
        seen_outputs.add(output_key)
        if len(data) != int(spec["source_bytes"]):
            raise RuntimeError(f"original bridge source byte count differs: {source}")
        if sha256(data) != str(spec["source_sha256"]):
            raise RuntimeError(f"original bridge source SHA-256 differs: {source}")
        if b"\r" in data or not data.endswith(b"\n"):
            raise RuntimeError(f"original bridge source must use LF with a final LF: {source}")
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"original bridge source is not strict UTF-8: {source}") from exc
        required_witnesses = tuple(str(item) for item in spec["required_witnesses"])
        missing = [witness for witness in required_witnesses if witness not in text]
        if missing:
            raise RuntimeError(f"original bridge source witnesses missing: {missing}")
        opening_matches = list(FENCED_DIV_OPEN_RE.finditer(text))
        stable_ids = tuple(match.group("id") for match in opening_matches)
        expected_ids = tuple(str(item) for item in spec["stable_ids"])
        if stable_ids != expected_ids or len(stable_ids) != len(set(stable_ids)):
            raise RuntimeError("original bridge stable fenced-div ID order differs")
        class_counts: dict[str, int] = {}
        for match in opening_matches:
            for token in match.group("classes").split():
                class_name = token.removeprefix(".")
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
        expected_class_counts = {
            str(key): int(value)
            for key, value in dict(spec["expected_class_counts"]).items()
        }
        if class_counts != expected_class_counts:
            raise RuntimeError(
                f"original bridge fenced-div class census differs: {class_counts}"
            )
        disclosure_ids = tuple(str(item[0]) for item in spec["disclosures"])
        disclosure_count = int(spec["disclosure_count"])
        if (
            len(disclosure_ids) != disclosure_count
            or len(disclosure_ids) != len(set(disclosure_ids))
        ):
            raise RuntimeError(
                "original bridge disclosure declarations differ from the exact "
                f"per-spec count: expected={disclosure_count} actual={len(disclosure_ids)}"
            )
        expected_disclosure_ids = tuple(
            stable_id
            for stable_id in expected_ids
            if stable_id.endswith((".hint.01", ".hint.02", ".solution"))
        )
        if disclosure_ids != expected_disclosure_ids:
            raise RuntimeError("original bridge disclosure order differs from stable source order")
        if len(re.findall(r"^#\s+", text, flags=re.MULTILINE)) != 1:
            raise RuntimeError("original bridge source must contain exactly one authored H1")
        word_count = original_bridge_word_count(text)
        word_min, word_max = (int(value) for value in spec["word_bounds"])
        if not word_min <= word_count <= word_max:
            raise RuntimeError(
                "original bridge prose extent is outside its per-spec bounds "
                f"{word_min:,}–{word_max:,}: {word_count}"
            )


def lab_chunk_re(spec: dict[str, object]) -> re.Pattern[str]:
    return re.compile(
        rf"^```\{{r\s+{re.escape(str(spec['chunk_id']))}\b[^}}]*\}}\s*$\n(.*?)^```\s*$",
        re.MULTILINE | re.DOTALL,
    )


def extract_and_run_lab(
    work: Path, spec: dict[str, object] | None = None
) -> tuple[str, list[dict[str, str]]]:
    spec = LAB_SPECS[0] if spec is None else spec
    source = Path(spec["source"])
    text = require_file(source).decode("utf-8")
    chunk_re = lab_chunk_re(spec)
    match = chunk_re.search(text)
    if not match:
        raise RuntimeError(f"labelled executable R chunk missing: {spec['chunk_id']}")
    if len(chunk_re.findall(text)) != 1:
        raise RuntimeError(f"labelled executable R chunk is not unique: {spec['chunk_id']}")
    placeholder = str(spec["placeholder"])
    if text.count(placeholder) != 1:
        raise RuntimeError(f"execution-table placeholder is not unique: {placeholder}")
    r_bytes = match.group(1).encode("utf-8")
    script = work / f"{spec['chunk_id']}.R"
    guard = (
        f'if (!identical(R.version.string, "{R_VERSION}")) stop("R version drift")\n'
        'if (!identical(RNGkind(), c("Mersenne-Twister", "Inversion", "Rejection"))) '
        'stop("R RNG drift")\n'
    ).encode("utf-8")
    script.write_bytes(guard + r_bytes)
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env["R_USER"] = str(work)
    result = subprocess.run(
        [str(R_SCRIPT), "--vanilla", str(script)],
        cwd=work,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"R execution failed: {result.stderr.strip()}")
    if result.stderr.strip():
        raise RuntimeError(f"unexpected R stderr: {result.stderr.strip()}")
    rows = list(csv.DictReader(result.stdout.splitlines()))
    expected_fields = list(spec["expected_fields"])
    if not rows or list(rows[0]) != expected_fields:
        raise RuntimeError(f"R CSV header mismatch: {spec['chunk_id']}")
    golden_rows = [dict(row) for row in spec["golden_rows"]]
    if rows != golden_rows:
        raise RuntimeError(
            f"R deterministic result differs for {spec['chunk_id']}: "
            f"expected={golden_rows!r} actual={rows!r}"
        )
    nonnumeric_fields = set(spec.get("nonnumeric_fields", ()))
    for row in rows:
        for key in expected_fields:
            if key in nonnumeric_fields:
                continue
            try:
                value = float(row[key])
            except ValueError as exc:
                raise RuntimeError(f"non-numeric lab result: {spec['chunk_id']}:{key}") from exc
            if not math.isfinite(value):
                raise RuntimeError(f"non-finite lab result: {spec['chunk_id']}:{key}")
    if spec["chunk_id"] == "o009_lab_convergence_mc":
        if [row["n"] for row in rows] != ["10", "1000", "1000000"]:
            raise RuntimeError("R CSV n sequence mismatch")
        if [row["seed"] for row in rows] != ["12341", "12342", "12342"]:
            raise RuntimeError("R CSV seed sequence mismatch")
        for row in rows:
            if row["exact_value"] != "0.250000000000":
                raise RuntimeError("R CSV exact value mismatch")
            for key in ("estimate", "signed_error", "absolute_error"):
                float(row[key])
            estimate = float(row["estimate"])
            signed_error = float(row["signed_error"])
            absolute_error = float(row["absolute_error"])
            if not math.isclose(signed_error, 0.25 - estimate, abs_tol=5e-12):
                raise RuntimeError("Monte Carlo signed error is inconsistent")
            if not math.isclose(absolute_error, abs(signed_error), abs_tol=5e-12):
                raise RuntimeError("Monte Carlo absolute error is inconsistent")
    elif spec["chunk_id"] == "o009_lab_markov_gambler_ruin":
        if len(rows) != 1:
            raise RuntimeError("Markov lab must emit exactly one result row")
        row = rows[0]
        if not 0 <= int(row["berhasil"]) <= int(row["simulasi"]):
            raise RuntimeError("Markov lab success count is outside its simulation range")
        estimate = float(row["taksiran"])
        exact_horizon = float(row["eksak_sampai_horizon"])
        final_probability = float(row["peluang_akhir"])
        exact_tail = float(row["celah_ekor_eksak"])
        absolute_error = float(row["galat_mutlak"])
        if not math.isclose(estimate, int(row["berhasil"]) / int(row["simulasi"]), abs_tol=5e-13):
            raise RuntimeError("Markov estimate is inconsistent with its success count")
        if not math.isclose(final_probability, 4 / 7, abs_tol=5e-13):
            raise RuntimeError("Markov eventual probability is inconsistent")
        if not math.isclose(exact_tail, (4 / 7) * (2 / 9) ** 50, rel_tol=5e-13):
            raise RuntimeError("Markov exact tail gap is inconsistent")
        if exact_tail <= 0 or exact_horizon > final_probability + 5e-13:
            raise RuntimeError("Markov finite-horizon ordering is inconsistent")
        if not math.isclose(absolute_error, abs(estimate - exact_horizon), abs_tol=5e-13):
            raise RuntimeError("Markov absolute error is inconsistent")
    elif spec["chunk_id"] == "o009_lab_convergence_modes":
        if [row["kasus"] for row in rows] != ["1", "2", "3", "4", "5"]:
            raise RuntimeError("convergence-mode lab case sequence mismatch")
        if [row["benih"] for row in rows] != [
            "20260829",
            "20260829",
            "20260829",
            "20260830",
            "20260830",
        ]:
            raise RuntimeError("convergence-mode lab seed sequence mismatch")
        values = [float(row["nilai"]) for row in rows]
        targets = [float(row["target"]) for row in rows]
        errors = [float(row["galat_mutlak"]) for row in rows]
        scales = [float(row["skala_teori"]) for row in rows]
        if values[0] != 0 or targets[0] != 0 or errors[0] != 0:
            raise RuntimeError("fixed-path almost-sure indicator witness differs")
        if not math.isclose(targets[1], 0.001, abs_tol=5e-13):
            raise RuntimeError("rare-event probability target differs")
        if abs(values[1] - targets[1]) > 2e-4:
            raise RuntimeError("rare-event probability tolerance failed")
        if abs(values[2] - 1.0) > 0.08 or not math.isclose(scales[2], 1.0):
            raise RuntimeError("rare-spike L1 failure witness tolerance failed")
        if not math.isclose(targets[3], 0.3, abs_tol=5e-13):
            raise RuntimeError("LLN analytic target differs")
        if abs(values[3] - targets[3]) > 0.01:
            raise RuntimeError("LLN numerical tolerance failed")
        if abs(values[4]) > 3.0 or not math.isclose(scales[4], 1.0):
            raise RuntimeError("CLT standardized-scale diagnostic failed")
        if any(
            not math.isclose(error, abs(value - target), abs_tol=5e-13)
            for value, target, error in zip(values, targets, errors, strict=True)
        ):
            raise RuntimeError("convergence-mode absolute-error column differs")
    elif spec["chunk_id"] == "o009_lab_conditional_martingale":
        if len(rows) != 1:
            raise RuntimeError(
                "conditional-martingale lab must emit exactly one result row"
            )
        row = rows[0]
        if (
            row["seed"] != "20260829"
            or row["ruang_hingga"] != "Omega_3 dan Omega_12"
            or row["cap_tau_plus"] != "12"
            or row["status"] != "PASS"
        ):
            raise RuntimeError(
                "conditional-martingale execution identity differs"
            )
        tolerance = float(row["toleransi"])
        if not math.isclose(tolerance, 1e-12, rel_tol=0, abs_tol=1e-24):
            raise RuntimeError("conditional-martingale tolerance differs")
        zero_fields = (
            "galat_bersyarat",
            "galat_menara",
            "galat_martingal",
            "rerata_S_tau_b",
            "target_E_S_tau_b",
            "rerata_S_tau_plus_terpotong",
            "target_E_S_tau_plus_terpotong",
        )
        if any(abs(float(row[key])) > tolerance for key in zero_fields):
            raise RuntimeError(
                "conditional/martingale/bounded-stop exact-enumeration gate failed"
            )
        if not math.isclose(float(row["E_X"]), 3.0, abs_tol=tolerance):
            raise RuntimeError("conditional-martingale E[X] target differs")
        exact_hit_rate = 3172 / 4096
        if not math.isclose(
            float(row["laju_kena_batas"]), exact_hit_rate, abs_tol=5e-13
        ) or not math.isclose(
            float(row["target_laju"]), exact_hit_rate, abs_tol=5e-13
        ):
            raise RuntimeError("optional-stopping finite-cap hit rate differs")
        if (
            not math.isclose(
                float(row["rerata_S_hanya_yang_kena"]), 1.0, abs_tol=tolerance
            )
            or not math.isclose(
                float(row["target_S_tau_plus"]), 1.0, abs_tol=tolerance
            )
            or not math.isclose(
                float(row["celah_naif"]), 1.0, abs_tol=tolerance
            )
        ):
            raise RuntimeError(
                "optional-stopping censoring diagnostic differs"
            )
    elif spec["chunk_id"] == "o009_lab_brownian_diagnostics":
        if len(rows) != 4 or any(len(row) != 15 for row in rows):
            raise RuntimeError(
                "Brownian diagnostic table must have dimensions 4 by 15"
            )
        if [row["n"] for row in rows] != ["64", "256", "1024", "4096"]:
            raise RuntimeError("Brownian diagnostic n sequence differs")
        if [row["k_endpoint"] for row in rows] != ["36", "136", "528", "2080"]:
            raise RuntimeError("Brownian endpoint lattice sequence differs")
        if [row["ambang_kena"] for row in rows] != ["8", "16", "32", "64"]:
            raise RuntimeError("Brownian hitting-threshold sequence differs")
        if any(row["refinemen_r"] != "8" for row in rows):
            raise RuntimeError("Brownian fixed-refinement factor differs")
        if any(row["status"] != "PASS" for row in rows):
            raise RuntimeError("Brownian diagnostic status differs")
        tolerances = [float(row["toleransi"]) for row in rows]
        if any(
            not math.isclose(value, 1e-12, rel_tol=0, abs_tol=1e-24)
            for value in tolerances
        ):
            raise RuntimeError("Brownian diagnostic tolerance differs")
        for row in rows:
            n = int(row["n"])
            cdf = float(row["cdf_endpoint_eksak"])
            normal_target = float(row["target_normal"])
            hit = float(row["prob_kena_eksak"])
            brown_target = float(row["target_brown"])
            if not math.isclose(
                float(row["galat_cdf"]), abs(cdf - normal_target), abs_tol=5e-13
            ):
                raise RuntimeError("Brownian endpoint-CDF error identity differs")
            if not math.isclose(
                float(row["galat_kena"]), abs(hit - brown_target), abs_tol=5e-13
            ):
                raise RuntimeError("Brownian hitting-probability error identity differs")
            if not math.isclose(float(row["qv_mesh_alami"]), 1.0, abs_tol=5e-13):
                raise RuntimeError("Brownian natural-mesh quadratic variation differs")
            if not math.isclose(
                float(row["qv_refinemen_pralimit"]), 1 / 8, abs_tol=5e-13
            ):
                raise RuntimeError("Brownian prelimit-refinement quadratic variation differs")
            if not math.isclose(
                float(row["variasi_total"]), math.sqrt(n), abs_tol=5e-13
            ):
                raise RuntimeError("Brownian natural-mesh total variation differs")
    else:
        raise RuntimeError(f"no result validator for lab: {spec['chunk_id']}")
    return text, rows


def markdown_table(rows: list[dict[str, str]], spec: dict[str, object] | None = None) -> str:
    spec = LAB_SPECS[0] if spec is None else spec
    fields = list(spec["expected_fields"])
    headers = list(spec["table_headers"])
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---:" for _ in fields) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[field] for field in fields) + " |")
    return "\n".join(lines)


def pandoc_lab_text(text: str, spec: dict[str, object] | None = None) -> str:
    """Convert one admitted R Markdown fence to Pandoc attributes."""
    spec = LAB_SPECS[0] if spec is None else spec
    chunk_id = str(spec["chunk_id"])
    opening = f"```{{r {chunk_id}, echo=TRUE}}"
    replacement = f"``` {{#{chunk_id} .r}}"
    if text.count(opening) != 1:
        raise RuntimeError(f"expected exactly one admitted R Markdown fence: {chunk_id}")
    return text.replace(opening, replacement, 1)


def lab_navigation(spec: dict[str, object]) -> list[tuple[str, str]]:
    """Return the complete edition navigation, relative to one lab page."""
    current = Path(spec["output"])
    links = [
        (
            os.path.relpath(Path("index.html"), current.parent).replace(os.sep, "/"),
            "Beranda edisi",
        )
    ]
    links.extend(
        (
            os.path.relpath(Path(str(unit["rel"])), current.parent).replace(os.sep, "/"),
            str(unit["nav_label"]),
        )
        for unit in THEORY_UNITS
    )
    links.append(
        (
            os.path.relpath(Path("quantecon/lectures/memoryless.html"), current.parent).replace(os.sep, "/"),
            "QuantEcon: distribusi tanpa ingatan",
        )
    )
    links.extend(
        (
            os.path.relpath(Path(other["output"]), current.parent).replace(os.sep, "/"),
            str(other["nav_label"]),
        )
        for other in LAB_SPECS
        if other is not spec
    )
    return links


def decorate_lab_output(output: Path, spec: dict[str, object]) -> None:
    """Bind the executed table and complete reader navigation into Pandoc HTML."""
    soup = BeautifulSoup(require_file(output).decode("utf-8"), "lxml")
    if soup.body is None:
        raise RuntimeError(f"Pandoc lab has no body: {spec['chunk_id']}")
    tables = soup.find_all("table")
    if len(tables) != 1:
        raise RuntimeError(
            f"expected exactly one executed result table for {spec['chunk_id']}, found {len(tables)}"
        )
    tables[0]["id"] = str(spec["table_id"])
    nav_links = " · ".join(
        f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        for href, label in lab_navigation(spec)
    )
    nav_soup = BeautifulSoup(
        f'<nav aria-label="Navigasi edisi">{nav_links}</nav>',
        "lxml",
    )
    nav = nav_soup.find("nav")
    if nav is None:
        raise RuntimeError("failed to construct lab navigation")
    header = soup.find("header", id="title-block-header")
    if header is not None:
        header.insert_after(nav)
    else:
        soup.body.insert(0, nav)
    main = soup.new_tag("main")
    node = nav.next_sibling
    while node is not None:
        following = node.next_sibling
        main.append(node.extract())
        node = following
    nav.insert_after(main)
    output.write_text(str(soup), encoding="utf-8", newline="\n")


def decorate_index_output(output: Path) -> None:
    """Give the generated course landing page one title and one main landmark."""
    soup = BeautifulSoup(require_file(output).decode("utf-8"), "lxml")
    if soup.body is None:
        raise RuntimeError("Pandoc reader index has no body")
    header = soup.find("header", id="title-block-header")
    if header is None or len(header.find_all("h1")) != 1:
        raise RuntimeError("Pandoc reader index title is not exact-once")
    toc = soup.find("nav", id="TOC")
    if toc is not None:
        toc["aria-label"] = "Daftar isi"
    main = soup.new_tag("main")
    node = header.next_sibling
    while node is not None:
        following = node.next_sibling
        main.append(node.extract())
        node = following
    header.insert_after(main)
    output.write_text(str(soup), encoding="utf-8", newline="\n")


def build_theory_unit(stage: Path, unit: dict[str, object]) -> None:
    _, target_path = theory_paths(unit)
    rel = Path(str(unit["rel"]))
    base_url = urllib.parse.urljoin(RANDOM_BASE_URL, rel.as_posix())
    soup = BeautifulSoup(require_file(target_path).decode("utf-8"), "lxml")
    mathjax = soup.find("script", id="MathJax-script")
    if mathjax is None:
        if MATH_SURFACE_RE.search(require_file(target_path).decode("utf-8")):
            raise RuntimeError("MathJax script marker missing on a mathematical page")
    else:
        mathjax["src"] = "../MathJax/tex-svg.js"
    extra_css = soup.new_tag("link", rel="stylesheet", href="../reader.css")
    soup.head.append(extra_css)
    local_pages = {
        urllib.parse.urljoin(RANDOM_BASE_URL, Path(str(item["rel"])).as_posix()): Path(str(item["rel"]))
        for item in THEORY_UNITS
    }
    metadata_href_corrections = {
        str(old): str(new)
        for old, new in dict(unit.get("metadata_href_corrections", {})).items()
    }
    for metadata_link in soup.select("link[href]"):
        rel_values = {str(value).lower() for value in (metadata_link.get("rel") or [])}
        if rel_values & {"stylesheet", "icon"}:
            continue
        href = str(metadata_link.get("href", ""))
        if not href or urllib.parse.urlparse(href).scheme:
            continue
        href = metadata_href_corrections.get(href, href)
        resolved = urllib.parse.urljoin(base_url, href)
        resolved_page = urllib.parse.urlunparse(
            urllib.parse.urlparse(resolved)._replace(fragment="")
        )
        if resolved_page in local_pages:
            local_target = local_pages[resolved_page]
            metadata_link["href"] = os.path.relpath(
                local_target, rel.parent
            ).replace(os.sep, "/")
        else:
            metadata_link["href"] = resolved
    for anchor in soup.select("a[href]"):
        href = str(anchor.get("href", ""))
        corrections = dict(unit["fragment_corrections"])
        if href in corrections:
            anchor["href"] = corrections[href]
            continue
        match = re.fullmatch(r"JavaScript:openAncillary\(['\"]([^'\"]+)['\"]\)", href)
        if match:
            anchor["href"] = urllib.parse.urljoin(base_url, match.group(1))
            continue
        parsed = urllib.parse.urlparse(href)
        if href.startswith("#") or parsed.scheme or not href:
            continue
        resolved = urllib.parse.urljoin(base_url, href)
        resolved_page = urllib.parse.urlunparse(urllib.parse.urlparse(resolved)._replace(fragment=""))
        if resolved_page in local_pages:
            local_target = local_pages[resolved_page]
            relative_target = os.path.relpath(local_target, rel.parent).replace(os.sep, "/")
            anchor["href"] = relative_target + (f"#{parsed.fragment}" if parsed.fragment else "")
        else:
            anchor["href"] = resolved
    for note in tuple(unit.get("reader_notes", ())):
        if "after_selector" in note:
            selector = str(note["after_selector"])
            anchors = soup.select(selector)
            if len(anchors) != 1:
                raise RuntimeError(
                    f"reader-note selector mismatch in {unit['rel']}: {selector!r}"
                )
            anchor_unit = anchors[0]
        else:
            heading_text = str(note["after_heading"])
            headings = [
                heading
                for heading in soup.find_all(("h3", "h4"))
                if heading.get_text(" ", strip=True) == heading_text
            ]
            if len(headings) != 1:
                raise RuntimeError(
                    f"reader-note heading mismatch in {unit['rel']}: {heading_text!r}"
                )
            anchor_unit = headings[0].find_next("div", class_="unit")
            if anchor_unit is None:
                raise RuntimeError(f"reader-note insertion unit missing in {unit['rel']}")
        note_soup = BeautifulSoup(str(note["html"]), "lxml")
        if note_soup.body is None or len(note_soup.body.contents) != 1:
            raise RuntimeError(f"reader-note payload is not one element in {unit['rel']}")
        anchor_unit.insert_after(note_soup.body.contents[0])
    official_url = urllib.parse.urljoin(RANDOM_BASE_URL, rel.as_posix())
    source_title = str(unit["source_title"])
    rights_id = str(unit["rights_id"])
    edition_links = []
    for item in THEORY_UNITS:
        local_target = Path(str(item["rel"]))
        relative_target = os.path.relpath(local_target, rel.parent).replace(os.sep, "/")
        edition_links.append(f'<a href="{relative_target}">{item["nav_label"]}</a>')
    for lab_spec in LAB_SPECS:
        edition_links.append(
            f'<a href="{os.path.relpath(Path(lab_spec["output"]), rel.parent).replace(os.sep, "/")}">'
            f'{lab_spec["nav_label"]}</a>'
        )
    edition_links.append(
        f'<a href="{os.path.relpath(Path("quantecon/lectures/memoryless.html"), rel.parent).replace(os.sep, "/")}">'
        "QuantEcon: distribusi tanpa ingatan</a>"
    )
    index_href = os.path.relpath(Path("index.html"), rel.parent).replace(os.sep, "/")
    attribution = BeautifulSoup(
        f"""<aside class="component-attribution" id="{rights_id}">
<strong>Asal komponen.</strong> Terjemahan halaman <cite>{source_title}</cite>
karya Kyle Siegrist berdasarkan cuplikan situs Random bertanggal 13 Maret 2026.
Halaman resmi Random saat ini mencantumkan keterangan lisensi CC BY 2.0 pada
beranda dan CC BY 1.0 pada halaman Credits; keduanya mengizinkan adaptasi dengan
atribusi. <a href="{official_url}">Baca sumber resmi</a>.
</aside><nav aria-label="Navigasi edisi"><a href="{index_href}">Beranda edisi</a> ·
{' · '.join(edition_links)}</nav>""",
        "lxml",
    )
    header = soup.find("header")
    if header is None:
        raise RuntimeError("theory header missing")
    insertion_point = header
    for node in list(attribution.body.contents):
        insertion_point.insert_after(node)
        insertion_point = node
    output = stage / rel
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = str(soup)
    for correction in tuple(unit.get("reader_corrections", ())):
        old = str(correction["old"])
        new = str(correction["new"])
        expected_matches = int(correction.get("matches", 1))
        actual_matches = rendered.count(old)
        if expected_matches < 1:
            raise RuntimeError(
                f"reader correction {correction['id']} has an invalid expected match count"
            )
        if actual_matches != expected_matches:
            raise RuntimeError(
                f"reader correction {correction['id']} matched "
                f"{actual_matches} times rather than {expected_matches} in {unit['rel']}"
            )
        rendered = rendered.replace(old, new, expected_matches)
    reader_soup = BeautifulSoup(rendered, "lxml")
    reader_header = reader_soup.find("header")
    page_heading = (
        reader_header.find(("h1", "h2")) if reader_header is not None else None
    )
    if page_heading is None:
        raise RuntimeError(f"theory page heading missing in {unit['rel']}")
    page_heading.name = "h1"
    page_topic = re.sub(
        r"^\s*\d+\.\s*", "", page_heading.get_text(" ", strip=True)
    )
    previous_level = 1
    for content_heading in reader_soup.find_all(("h3", "h4")):
        candidate_level = int(content_heading.name[1]) - 1
        level = min(candidate_level, previous_level + 1)
        content_heading.name = f"h{level}"
        existing_classes = [
            value
            for value in content_heading.get("class", [])
            if not str(value).startswith("reader-level-")
        ]
        content_heading["class"] = [*existing_classes, f"reader-level-{level}"]
        previous_level = level
    for section_anchor in reader_soup.select("ol.map a[title]"):
        section_number = section_anchor.get_text(" ", strip=True)
        section_title = str(section_anchor.get("title", "")).strip()
        if section_number and section_title:
            section_anchor["aria-label"] = f"Bagian {section_number}: {section_title}"
    for current_item in reader_soup.select("ol.map li.current"):
        section_number = current_item.get_text(" ", strip=True)
        current_item["aria-current"] = "page"
        current_item["aria-label"] = (
            f"Bagian {section_number}: {page_topic} (halaman saat ini)"
        )
    for details_button in reader_soup.select('button[onclick="expandDetails(true);"]'):
        details_button["aria-label"] = "Buka semua rincian"
    for details_button in reader_soup.select('button[onclick="expandDetails(false);"]'):
        details_button["aria-label"] = "Tutup semua rincian"
    summary_contexts: list[tuple[object, str]] = []
    context_totals: dict[str, int] = {}
    for summary in reader_soup.find_all("summary"):
        previous_heading = summary.find_previous(("h2", "h3"))
        context = (
            previous_heading.get_text(" ", strip=True)
            if previous_heading is not None
            else page_topic
        )
        summary_contexts.append((summary, context))
        context_totals[context] = context_totals.get(context, 0) + 1
    context_positions: dict[str, int] = {}
    for summary, context in summary_contexts:
        context_positions[context] = context_positions.get(context, 0) + 1
        suffix = (
            f", butir {context_positions[context]}"
            if context_totals[context] > 1
            else ""
        )
        visible_label = summary.get_text(" ", strip=True).rstrip(":")
        if not visible_label:
            visible_label = "Rincian"
        summary["aria-label"] = f"{visible_label}: {context}{suffix}"
    edition_nav = reader_soup.find("nav", attrs={"aria-label": "Navigasi edisi"})
    footer = reader_soup.find("footer")
    if edition_nav is None or footer is None:
        raise RuntimeError(f"reader landmarks missing in {unit['rel']}")
    main = reader_soup.new_tag("main")
    node = edition_nav.next_sibling
    while node is not None and node is not footer:
        following = node.next_sibling
        main.append(node.extract())
        node = following
    footer.insert_before(main)
    rendered = str(reader_soup)
    output.write_text(rendered, encoding="utf-8", newline="\n")


def build_theory(stage: Path) -> None:
    for unit in THEORY_UNITS:
        build_theory_unit(stage, unit)


def run_pandoc(source: Path, output: Path, css: str, mathjax: str | None = None) -> None:
    runtime_evidence()
    pandoc_command = shutil.which(PANDOC)
    if not pandoc_command:
        raise RuntimeError("pinned Pandoc command is unavailable")
    command = [
        pandoc_command,
        str(source),
        "--standalone",
        "--from=markdown+fenced_divs+fenced_code_attributes+yaml_metadata_block+tex_math_single_backslash",
        "--to=html5",
        f"--css={css}",
        "--toc",
        "--output",
        str(output),
    ]
    if mathjax:
        command.append(f"--mathjax={mathjax}")
    result = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc failed: {result.stderr.strip()}")
    rendered = output.read_text(encoding="utf-8").replace("\r\n", "\n")
    if rendered.count("</head>") != 1:
        raise RuntimeError(f"Pandoc output has an unexpected head boundary: {output}")
    favicon = "../icons/Icon.svg" if css.startswith("../") else "icons/Icon.svg"
    rendered = rendered.replace(
        "</head>",
        f'<link href="{favicon}" rel="icon" type="image/svg+xml" />\n</head>',
        1,
    )
    output.write_text(rendered, encoding="utf-8", newline="\n")


def decorate_original_bridge_output(output: Path, spec: dict[str, object]) -> None:
    """Expose original hints/solutions as native disclosures and bind landmarks."""
    soup = BeautifulSoup(require_file(output).decode("utf-8"), "lxml")
    if soup.head is None or soup.body is None:
        raise RuntimeError(f"Pandoc original bridge lacks document landmarks: {output}")
    generated_header = soup.find("header", id="title-block-header")
    if generated_header is None or len(generated_header.find_all("h1")) != 1:
        raise RuntimeError("Pandoc original bridge generated title is not exact-once")
    generated_header.decompose()
    root = soup.find(id=str(spec["unit_id"]))
    if root is None or root.name != "div" or "original-bridge" not in root.get("class", []):
        raise RuntimeError("original bridge root div is missing or malformed")
    root.name = "main"
    toc = soup.find("nav", id="TOC")
    if toc is not None:
        toc["aria-label"] = "Daftar isi"
    output_rel = Path(spec["output"])
    home_href = os.path.relpath(Path("index.html"), output_rel.parent).replace(os.sep, "/")
    previous_href = os.path.relpath(
        Path(spec["previous_output"]), output_rel.parent
    ).replace(os.sep, "/")
    previous_label = str(spec["previous_label"])
    nav_fragment = BeautifulSoup(
        '<nav aria-label="Navigasi edisi">'
        f'<a href="{html.escape(home_href, quote=True)}">Beranda edisi</a> · '
        f'<a href="{html.escape(previous_href, quote=True)}">'
        f'{html.escape(previous_label)}</a>'
        "</nav>",
        "lxml",
    )
    edition_nav = nav_fragment.find("nav")
    if edition_nav is None:
        raise RuntimeError("failed to construct original bridge navigation")
    soup.body.insert(0, edition_nav)
    previous_link = soup.new_tag(
        "link", attrs={"rel": "prev", "href": previous_href}
    )
    soup.head.append(previous_link)
    for disclosure_id, label in spec["disclosures"]:
        disclosure = soup.find(id=str(disclosure_id))
        if disclosure is None or disclosure.name != "div":
            raise RuntimeError(f"original bridge disclosure div missing: {disclosure_id}")
        details = soup.new_tag("details")
        details.attrs = deepcopy(disclosure.attrs)
        summary = soup.new_tag("summary")
        summary["aria-label"] = str(label)
        summary.string = str(label)
        details.append(summary)
        for child in list(disclosure.contents):
            details.append(child.extract())
        disclosure.replace_with(details)
    if len(soup.find_all("h1")) != 1 or len(soup.find_all("main")) != 1:
        raise RuntimeError("original bridge must render with exactly one H1 and one main")
    disclosure_count = int(spec["disclosure_count"])
    if len(soup.find_all("details")) != disclosure_count:
        raise RuntimeError(
            "original bridge disclosure render count differs: "
            f"expected={disclosure_count} actual={len(soup.find_all('details'))}"
        )
    output.write_text(str(soup), encoding="utf-8", newline="\n")


def build_original_bridges(stage: Path) -> None:
    for spec in ORIGINAL_BRIDGE_SPECS:
        output = stage / Path(spec["output"])
        output.parent.mkdir(parents=True, exist_ok=True)
        run_pandoc(
            Path(spec["source"]),
            output,
            "../reader.css",
            "../MathJax/tex-svg.js",
        )
        decorate_original_bridge_output(output, spec)


def supplement_receipt_units(site: Path) -> list[dict[str, object]]:
    """Bind every authored mastery and assessment source to its reader page."""
    units: list[dict[str, object]] = []
    for source_rel, output_rel, label, kind in SUPPLEMENT_SPECS:
        source = ROOT / "source" / source_rel
        output = site / output_rel
        units.append(
            {
                "source": f"source/{source_rel}",
                "output": output_rel,
                "label": label,
                "kind": kind,
                "source_sha256": sha256(require_file(source)),
                "target_sha256": sha256(require_file(output)),
            }
        )
    return units


def _disclose_heading_section(soup: BeautifulSoup, heading: object) -> None:
    """Turn one heading-led hint/solution section into a native disclosure."""
    stable_id = str(heading.get("id", ""))
    details = soup.new_tag("details", id=stable_id)
    hint_id = any(token in stable_id for token in (".hint.", "-hint-", "-petunjuk-"))
    details["class"] = ["hint" if hint_id else "solution"]
    summary = soup.new_tag("summary")
    label = heading.get_text(" ", strip=True)
    summary.string = label
    summary["aria-label"] = f"{label}: {stable_id}" if stable_id else label
    details.append(summary)
    node = heading.next_sibling
    while node is not None:
        following = node.next_sibling
        if getattr(node, "name", None) in {"h1", "h2", "h3", "h4"}:
            break
        details.append(node.extract())
        node = following
    heading.replace_with(details)


def decorate_supplement_output(
    output: Path, previous_output: str, kind: str
) -> None:
    """Give authored mastery/assessment pages one consistent accessible shell."""
    soup = BeautifulSoup(require_file(output).decode("utf-8"), "lxml")
    if soup.head is None or soup.body is None:
        raise RuntimeError(f"Pandoc supplement lacks document landmarks: {output}")
    if soup.html is None:
        raise RuntimeError(f"Pandoc supplement lacks html root: {output}")
    soup.html["lang"] = "id-ID"
    generated_header = soup.find("header", id="title-block-header")
    generated_title = None
    if generated_header is not None:
        generated_heading = generated_header.find("h1")
        if generated_heading is not None:
            generated_title = generated_heading.get_text(" ", strip=True)
        generated_header.decompose()
    headings = soup.find_all("h1")
    if not headings and generated_title:
        synthesized_heading = soup.new_tag("h1")
        synthesized_heading.string = generated_title
        soup.body.insert(0, synthesized_heading)
        headings = [synthesized_heading]
    if len(headings) != 1:
        raise RuntimeError(f"supplement must contain exactly one H1: {output}")

    for disclosure in list(
        soup.select("div.hint, div.solution, div.mastery-hint, div.mastery-solution")
    ):
        details = soup.new_tag("details")
        details.attrs = deepcopy(disclosure.attrs)
        classes = set(str(value) for value in details.get("class", []))
        is_hint = bool(classes & {"hint", "mastery-hint"})
        details["class"] = ["hint" if is_hint else "solution"]
        label = "Petunjuk" if is_hint else "Penyelesaian lengkap"
        summary = soup.new_tag("summary")
        summary.string = label
        disclosure_key = str(details.get("id", "")).strip()
        if not disclosure_key:
            disclosure_key = f"{kind}-{len(soup.find_all('details')) + 1}"
        summary["aria-label"] = f"{label}: {disclosure_key}"
        details.append(summary)
        for child in list(disclosure.contents):
            details.append(child.extract())
        disclosure.replace_with(details)

    heading_disclosures = [
        heading
        for heading in soup.find_all(("h2", "h3", "h4"))
        if any(
            token in str(heading.get("id", ""))
            for token in (".hint.", "-hint-", "-petunjuk-")
        )
        or str(heading.get("id", "")).endswith((".solution", "-solution", "-solusi"))
    ]
    for heading in heading_disclosures:
        _disclose_heading_section(soup, heading)

    for anchor in list(soup.find_all("a", id=True)):
        stable_id = str(anchor.get("id", ""))
        if not (
            any(token in stable_id for token in ("-hint-", "-petunjuk-"))
            or stable_id.endswith(("-solution", "-solusi"))
        ):
            continue
        marker = anchor
        if (
            anchor.parent is not None
            and anchor.parent.name == "p"
            and not anchor.parent.get_text(" ", strip=True)
        ):
            marker = anchor.parent
        heading = marker.find_next_sibling(("h2", "h3", "h4"))
        if heading is None or heading.find_previous_sibling() is not marker:
            continue
        generated_id = str(heading.get("id", ""))
        if generated_id and generated_id != stable_id:
            for link in soup.select(f'a[href="#{generated_id}"]'):
                link["href"] = f"#{stable_id}"
        heading["id"] = stable_id
        marker.decompose()
        _disclose_heading_section(soup, heading)

    for anchor in soup.select("a[href]"):
        href = str(anchor.get("href", ""))
        if href.startswith("../theory/"):
            anchor["href"] = "../" + href[len("../theory/") :]

    main = soup.new_tag("main")
    main["class"] = ["mastery-reader" if kind == "mastery" else "assessment-reader"]
    for child in list(soup.body.contents):
        main.append(child.extract())
    provenance = soup.new_tag("aside")
    provenance["class"] = ["component-attribution", "model-provenance"]
    provenance.string = (
        "Materi asli pada halaman ini berlisensi CC BY 4.0 dan disusun dengan OpenAI Codex "
        "gpt-5.6-sol, Ultra. Kredit sumber dan kontributor lain tetap "
        "dipertahankan pada unit masing-masing."
    )
    main.append(provenance)
    soup.body.append(main)

    output_rel = output.relative_to(output.parents[1])
    home_href = os.path.relpath(Path("index.html"), output_rel.parent).replace(os.sep, "/")
    previous_href = os.path.relpath(Path(previous_output), output_rel.parent).replace(os.sep, "/")
    nav_fragment = BeautifulSoup(
        '<nav aria-label="Navigasi edisi">'
        f'<a href="{html.escape(home_href, quote=True)}">Beranda edisi</a> · '
        f'<a href="{html.escape(previous_href, quote=True)}">Unit sebelumnya</a>'
        "</nav>",
        "lxml",
    )
    soup.body.insert(0, nav_fragment.find("nav"))
    soup.head.append(
        soup.new_tag("link", attrs={"rel": "prev", "href": previous_href})
    )
    output.write_text(str(soup), encoding="utf-8", newline="\n")


def build_supplements(stage: Path) -> None:
    previous_output = "labs/05-gerak-brown-donsker-variasi-kuadratik-dan-waktu-kena.html"
    for source_rel, output_rel, _label, kind in SUPPLEMENT_SPECS:
        source = ROOT / "source" / source_rel
        output = stage / output_rel
        output.parent.mkdir(parents=True, exist_ok=True)
        run_pandoc(source, output, "../reader.css", "../MathJax/tex-svg.js")
        decorate_supplement_output(output, previous_output, kind)
        previous_output = output_rel


def verify_supplement_outputs(site: Path) -> None:
    seen_ids: set[str] = set()
    for source_rel, output_rel, _label, kind in SUPPLEMENT_SPECS:
        source = ROOT / "source" / source_rel
        output = site / output_rel
        source_text = require_file(source).decode("utf-8")
        soup = BeautifulSoup(require_file(output).decode("utf-8"), "lxml")
        if len(soup.find_all("main")) != 1 or len(soup.find_all("h1")) != 1:
            raise RuntimeError(f"supplement landmarks differ: {output_rel}")
        expected_class = "mastery-reader" if kind == "mastery" else "assessment-reader"
        if soup.find("main", class_=expected_class) is None:
            raise RuntimeError(f"supplement reader class differs: {output_rel}")
        if soup.find("header", id="title-block-header") is not None:
            raise RuntimeError(f"supplement retained duplicate title: {output_rel}")
        ids = [str(node["id"]) for node in soup.select("[id]")]
        if len(ids) != len(set(ids)):
            raise RuntimeError(f"duplicate stable IDs in supplement: {output_rel}")
        explicit_source_ids = set(
            re.findall(r"\{#([A-Za-z0-9][A-Za-z0-9._:-]*)", source_text)
        ) | set(
            re.findall(
                r'<a\s+id=["\']([A-Za-z0-9][A-Za-z0-9._:-]*)["\']',
                source_text,
                re.IGNORECASE,
            )
        )
        missing_explicit = sorted(item for item in explicit_source_ids if ids.count(item) != 1)
        if missing_explicit:
            raise RuntimeError(
                f"supplement explicit stable-ID preservation differs: {output_rel}: {missing_explicit}"
            )
        collisions = sorted(seen_ids.intersection(explicit_source_ids))
        if collisions:
            raise RuntimeError(f"cross-supplement stable-ID collision: {collisions}")
        seen_ids.update(explicit_source_ids)
        if soup.select("div.hint, div.solution, div.mastery-hint, div.mastery-solution"):
            raise RuntimeError(f"supplement left hint/solution divs undisclosed: {output_rel}")
        if not soup.find_all("details"):
            raise RuntimeError(f"supplement has no accessible disclosures: {output_rel}")
        if soup.select('a[href^="../theory/"]'):
            raise RuntimeError(f"supplement retained unresolved theory prefix: {output_rel}")
        visible = re.sub(r"\s+", " ", " ".join(soup.stripped_strings)).strip()
        if "CC BY 4.0" not in visible or "OpenAI Codex gpt-5.6-sol, Ultra." not in visible:
            raise RuntimeError(f"supplement rights/model witness missing: {output_rel}")
        if "TTP" in source_text or "Translation and Transcription Project" in source_text:
            raise RuntimeError(f"forbidden umbrella prose in supplement: {source_rel}")


def copy_assets(stage: Path) -> None:
    mappings = {
        AUTH_RANDOM / "static" / "Screen.css": stage / "Screen.css",
        AUTH_RANDOM / "static" / "Basic.js": stage / "Basic.js",
        AUTH_RANDOM / "static" / "apps" / "Apps.js": stage / "apps" / "Apps.js",
        AUTH_RANDOM / "static" / "apps" / "Distributions.js": (
            stage / "apps" / "Distributions.js"
        ),
        ROOT / "source" / "original" / "brown-drift-offline.js": (
            stage / "apps" / "brown-drift-offline.js"
        ),
        ROOT / "source" / "original" / "brown-bridge-offline.js": (
            stage / "apps" / "brown-bridge-offline.js"
        ),
        ROOT / "source" / "original" / "geometric-brownian-offline.js": (
            stage / "apps" / "geometric-brownian-offline.js"
        ),
        AUTH_RANDOM / "static" / "icons" / "Icon.svg": stage / "icons" / "Icon.svg",
        AUTH_RANDOM / "static" / "icons" / "DieBlue5.svg": stage / "icons" / "DieBlue5.svg",
        AUTH_RANDOM / "static" / "icons" / "DieGreen5.svg": stage / "icons" / "DieGreen5.svg",
        AUTH_RANDOM / "static" / "icons" / "DieRed5.svg": stage / "icons" / "DieRed5.svg",
        AUTH_RANDOM / "static" / "icons" / "Plus.svg": stage / "icons" / "Plus.svg",
        AUTH_RANDOM / "static" / "icons" / "Minus.svg": stage / "icons" / "Minus.svg",
        AUTH_RANDOM / "static" / "icons" / "Step.svg": stage / "icons" / "Step.svg",
        AUTH_RANDOM / "static" / "icons" / "Stop.svg": stage / "icons" / "Stop.svg",
        AUTH_RANDOM / "static" / "icons" / "Run.svg": stage / "icons" / "Run.svg",
        AUTH_RANDOM / "static" / "icons" / "Reset.svg": stage / "icons" / "Reset.svg",
        AUTH_RANDOM / "static" / "prob" / "Increasing1.png": stage / "prob" / "Increasing1.png",
        AUTH_RANDOM / "static" / "prob" / "Increasing2.png": stage / "prob" / "Increasing2.png",
        AUTH_RANDOM / "static" / "prob" / "Decreasing.png": stage / "prob" / "Decreasing.png",
        AUTH_RANDOM / "static" / "prob" / "InverseImage.png": stage / "prob" / "InverseImage.png",
        AUTH_RANDOM / "static" / "expect" / "ConvexFunction.png": stage / "expect" / "ConvexFunction.png",
        AUTH_RANDOM / "static" / "martingales" / "Martingale.png": (
            stage / "martingales" / "Martingale.png"
        ),
        AUTH_RANDOM / "static" / "martingales" / "ConvexFunction.png": (
            stage / "martingales" / "ConvexFunction.png"
        ),
        AUTH_RANDOM / "static" / "martingales" / "Powers.png": (
            stage / "martingales" / "Powers.png"
        ),
        AUTH_RANDOM / "static" / "martingales" / "PositivePart.png": (
            stage / "martingales" / "PositivePart.png"
        ),
        AUTH_RANDOM / "static" / "markov" / "Visits.png": (
            stage / "markov" / "Visits.png"
        ),
        AUTH_RANDOM / "static" / "markov" / "Partition.png": (
            stage / "markov" / "Partition.png"
        ),
        AUTH_RANDOM / "static" / "markov" / "Classes.png": (
            stage / "markov" / "Classes.png"
        ),
        AUTH_RANDOM / "static" / "markov" / "State1.png": (
            stage / "markov" / "State1.png"
        ),
        AUTH_RANDOM / "static" / "markov" / "State2.png": (
            stage / "markov" / "State2.png"
        ),
        AUTH_RANDOM / "static" / "markov" / "State3.png": (
            stage / "markov" / "State3.png"
        ),
        AUTH_RANDOM / "static" / "markov" / "CyclicClasses.png": (
            stage / "markov" / "CyclicClasses.png"
        ),
        AUTH_RANDOM / "static" / "markov" / "State4.png": (
            stage / "markov" / "State4.png"
        ),
        AUTH_RANDOM / "shared" / "MathJax" / "tex-svg.js": stage / "MathJax" / "tex-svg.js",
        AUTH_RANDOM / "shared" / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js": (
            stage / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js"
        ),
        AUTH_RANDOM / "shared" / "MathJax" / "LICENSE": stage / "licenses" / "MathJax-Apache-2.0.txt",
        SOURCE_CSS: stage / "reader.css",
        SOURCE_TWO_STATE_APP: stage / "apps" / "two-state.html",
    }
    if sha256(require_file(AUTH_RANDOM / "shared" / "MathJax" / "tex-svg.js")) != MATHJAX_SHA256:
        raise RuntimeError("MathJax hash changed")
    boldsymbol = AUTH_RANDOM / "shared" / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js"
    if sha256(require_file(boldsymbol)) != MATHJAX_BOLDSYMBOL_SHA256:
        raise RuntimeError("MathJax boldsymbol extension hash changed")
    for source, target in mappings.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def copy_quantecon_component(stage: Path) -> dict[str, object]:
    """Admit the separately verified first QuantEcon unit into the aggregate site.

    QuantEcon remains outside ``THEORY_UNITS``.  Its self-contained component
    closure is copied only after the component receipt/manifest has been
    checked, so the aggregate build cannot silently consume a partial page.
    """
    root = QUANTECON_COMPONENT_ROOT
    receipt_path = root / "COMPONENT_RECEIPT.json"
    manifest_path = root / "COMPONENT_MANIFEST.tsv"
    receipt = json.loads(require_file(receipt_path).decode("utf-8"))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon component receipt schema differs")
    if receipt.get("unit_id") != "unit.o009.quantecon.ctmc.memoryless-distributions":
        raise RuntimeError("QuantEcon component unit identity differs")
    listed: list[dict[str, str]] = []
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    for row in listed:
        relative = Path(str(row["path"]))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise RuntimeError(f"unsafe QuantEcon component manifest path: {relative}")
        source = root / relative
        data = require_file(source)
        if int(row["bytes"]) != len(data) or str(row["sha256"]) != sha256(data):
            raise RuntimeError(f"QuantEcon component manifest mismatch: {relative}")
    if receipt.get("manifest_sha256") != sha256(require_file(manifest_path)):
        raise RuntimeError("QuantEcon component receipt does not bind its manifest")
    target = stage / "quantecon"
    if target.exists():
        if target.is_symlink():
            raise RuntimeError("refusing to replace linked aggregate QuantEcon directory")
        shutil.rmtree(target)
    # ``components/`` is reserved for namespaced companion controls (such as
    # the separately built Poisson unit) and may remain from a prior failed
    # aggregate staging attempt; the memoryless component does not own it.
    shutil.copytree(root, target, symlinks=False, ignore=shutil.ignore_patterns("components"))
    return {
        "unit_id": str(receipt["unit_id"]),
        "source_path": str(receipt["target"]["path"]),
        "target_sha256": str(receipt["target"]["sha256"]),
        "component_manifest_sha256": sha256(require_file(manifest_path)),
        "component_receipt_sha256": sha256(require_file(receipt_path)),
        "file_count": int(receipt["file_count"]),
        "total_bytes": int(receipt["total_bytes"]),
    }


def copy_quantecon_poisson_component(stage: Path) -> dict[str, object]:
    """Merge the separately verified Poisson unit into the QuantEcon closure.

    The component manifest and receipt are retained under a namespaced control
    directory because the memoryless component already owns the root-level
    control filenames.  Content files are merged only when any shared CSS or
    MathJax bytes are identical; a differing collision is a hard failure.
    """
    root = QUANTECON_POISSON_COMPONENT_ROOT
    receipt_path = root / "COMPONENT_RECEIPT.json"
    manifest_path = root / "COMPONENT_MANIFEST.tsv"
    receipt = json.loads(require_file(receipt_path).decode("utf-8"))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon Poisson component receipt schema differs")
    if receipt.get("unit_id") != "unit.o009.quantecon.ctmc.poisson-processes":
        raise RuntimeError("QuantEcon Poisson component unit identity differs")
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    for row in listed:
        relative = Path(str(row["path"]))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise RuntimeError(f"unsafe QuantEcon Poisson manifest path: {relative}")
        source = root / relative
        data = require_file(source)
        if int(row["bytes"]) != len(data) or str(row["sha256"]) != sha256(data):
            raise RuntimeError(f"QuantEcon Poisson component manifest mismatch: {relative}")
    if receipt.get("manifest_sha256") != sha256(require_file(manifest_path)):
        raise RuntimeError("QuantEcon Poisson component receipt does not bind its manifest")
    target = stage / "quantecon"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: path.relative_to(root).as_posix().casefold()):
        relative = source.relative_to(root)
        if relative.name in {"COMPONENT_MANIFEST.tsv", "COMPONENT_RECEIPT.json"}:
            destination = target / "components" / "poisson" / relative.name
        else:
            destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = require_file(source)
        if destination.exists():
            if destination.is_symlink() or require_file(destination) != data:
                raise RuntimeError(f"conflicting QuantEcon component collision: {destination}")
        else:
            destination.write_bytes(data)
    return {
        "unit_id": str(receipt["unit_id"]),
        "source_path": str(receipt["target"]["path"]),
        "target_sha256": str(receipt["target"]["sha256"]),
        "component_manifest_sha256": sha256(require_file(manifest_path)),
        "component_receipt_sha256": sha256(require_file(receipt_path)),
        "file_count": int(receipt["file_count"]),
        "total_bytes": int(receipt["total_bytes"]),
    }


def copy_quantecon_markov_prop_component(stage: Path) -> dict[str, object]:
    """Merge the verified Markov-property unit into the QuantEcon closure.

    The lecture remains beside the preceding QuantEcon lectures.  Component-
    local assets, notebooks, source, and controls are namespaced under
    ``components/markov_prop``; only the shared CSS and MathJax runtime may
    collide, and then only when their bytes are identical.
    """
    root = QUANTECON_MARKOV_PROP_COMPONENT_ROOT
    receipt_path = root / "COMPONENT_RECEIPT.json"
    manifest_path = root / "COMPONENT_MANIFEST.tsv"
    receipt = json.loads(require_file(receipt_path).decode("utf-8"))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon Markov-property component receipt schema differs")
    if receipt.get("unit_id") != "unit.o009.quantecon.ctmc.markov-property":
        raise RuntimeError("QuantEcon Markov-property component unit identity differs")
    if receipt.get("target", {}).get("path") != "source/quantecon/lectures/markov_prop.md":
        raise RuntimeError("QuantEcon Markov-property component target path differs")
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    manifest_paths: set[Path] = set()
    for row in listed:
        relative = Path(str(row["path"]))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise RuntimeError(f"unsafe QuantEcon Markov-property manifest path: {relative}")
        if relative in manifest_paths:
            raise RuntimeError(f"duplicate QuantEcon Markov-property manifest path: {relative}")
        manifest_paths.add(relative)
        source = root / relative
        data = require_file(source)
        if int(row["bytes"]) != len(data) or str(row["sha256"]) != sha256(data):
            raise RuntimeError(f"QuantEcon Markov-property component manifest mismatch: {relative}")
    lecture_relative = Path("lectures/markov_prop.html")
    if lecture_relative not in manifest_paths:
        raise RuntimeError("QuantEcon Markov-property lecture is absent from its manifest")
    if receipt.get("manifest_sha256") != sha256(require_file(manifest_path)):
        raise RuntimeError("QuantEcon Markov-property component receipt does not bind its manifest")
    if int(receipt.get("file_count", -1)) != len(listed):
        raise RuntimeError("QuantEcon Markov-property component file count differs")
    if int(receipt.get("total_bytes", -1)) != sum(int(row["bytes"]) for row in listed):
        raise RuntimeError("QuantEcon Markov-property component byte count differs")
    actual_paths = {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    }
    expected_paths = manifest_paths | {
        Path("COMPONENT_MANIFEST.tsv"),
        Path("COMPONENT_RECEIPT.json"),
    }
    if actual_paths != expected_paths:
        raise RuntimeError(
            "QuantEcon Markov-property component inventory differs: "
            f"missing={sorted(str(path) for path in expected_paths - actual_paths)}; "
            f"unexpected={sorted(str(path) for path in actual_paths - expected_paths)}"
        )

    target = stage / "quantecon"
    lane = target / "components" / "markov_prop"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    ):
        relative = source.relative_to(root)
        if relative == lecture_relative:
            destination = target / relative
        elif relative == Path("reader.css") or relative.parts[0] == "MathJax":
            destination = target / relative
        else:
            destination = lane / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = require_file(source)
        if destination.exists():
            if destination.is_symlink() or require_file(destination) != data:
                raise RuntimeError(f"conflicting QuantEcon component collision: {destination}")
        else:
            destination.write_bytes(data)

    lecture_path = target / lecture_relative
    lecture_text = require_file(lecture_path).decode("utf-8")
    local_lane_ref = re.compile(
        r'(?P<prefix>\b(?:href|src)=["\'])\.\./(?P<directory>assets|notebooks)/'
    )
    lecture_text, rewritten = local_lane_ref.subn(
        r'\g<prefix>../components/markov_prop/\g<directory>/',
        lecture_text,
    )
    if rewritten == 0:
        raise RuntimeError("QuantEcon Markov-property lecture has no component-local references")
    if local_lane_ref.search(lecture_text):
        raise RuntimeError("QuantEcon Markov-property component-local reference rewrite failed")
    lecture_path.write_text(lecture_text, encoding="utf-8", newline="\n")
    return {
        "unit_id": str(receipt["unit_id"]),
        "source_path": str(receipt["target"]["path"]),
        "target_sha256": str(receipt["target"]["sha256"]),
        "component_manifest_sha256": sha256(require_file(manifest_path)),
        "component_receipt_sha256": sha256(require_file(receipt_path)),
        "file_count": int(receipt["file_count"]),
        "total_bytes": int(receipt["total_bytes"]),
    }


def copy_quantecon_kolmogorov_bwd_component(stage: Path) -> dict[str, object]:
    """Merge the verified backward-equation unit into the QuantEcon closure."""
    root = QUANTECON_KOLMOGOROV_BWD_COMPONENT_ROOT
    receipt_path = root / "COMPONENT_RECEIPT.json"
    manifest_path = root / "COMPONENT_MANIFEST.tsv"
    receipt = json.loads(require_file(receipt_path).decode("utf-8"))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon backward-equation component receipt schema differs")
    if receipt.get("unit_id") != "unit.o009.quantecon.ctmc.kolmogorov-backward":
        raise RuntimeError("QuantEcon backward-equation component unit identity differs")
    if receipt.get("target", {}).get("path") != "source/quantecon/lectures/kolmogorov_bwd.md":
        raise RuntimeError("QuantEcon backward-equation component target path differs")
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    manifest_paths: set[Path] = set()
    for row in listed:
        relative = Path(str(row["path"]))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise RuntimeError(f"unsafe QuantEcon backward-equation manifest path: {relative}")
        if relative in manifest_paths:
            raise RuntimeError(f"duplicate QuantEcon backward-equation manifest path: {relative}")
        manifest_paths.add(relative)
        data = require_file(root / relative)
        if int(row["bytes"]) != len(data) or str(row["sha256"]) != sha256(data):
            raise RuntimeError(f"QuantEcon backward-equation component manifest mismatch: {relative}")
    lecture_relative = Path("lectures/kolmogorov_bwd.html")
    if lecture_relative not in manifest_paths:
        raise RuntimeError("QuantEcon backward-equation lecture is absent from its manifest")
    if receipt.get("manifest_sha256") != sha256(require_file(manifest_path)):
        raise RuntimeError("QuantEcon backward-equation component receipt does not bind its manifest")
    if int(receipt.get("file_count", -1)) != len(listed):
        raise RuntimeError("QuantEcon backward-equation component file count differs")
    if int(receipt.get("total_bytes", -1)) != sum(int(row["bytes"]) for row in listed):
        raise RuntimeError("QuantEcon backward-equation component byte count differs")
    actual_paths = {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    }
    expected_paths = manifest_paths | {
        Path("COMPONENT_MANIFEST.tsv"),
        Path("COMPONENT_RECEIPT.json"),
    }
    if actual_paths != expected_paths:
        raise RuntimeError(
            "QuantEcon backward-equation component inventory differs: "
            f"missing={sorted(str(path) for path in expected_paths - actual_paths)}; "
            f"unexpected={sorted(str(path) for path in actual_paths - expected_paths)}"
        )

    target = stage / "quantecon"
    lane = target / "components" / "kolmogorov_bwd"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    ):
        relative = source.relative_to(root)
        if relative == lecture_relative:
            destination = target / relative
        elif relative == Path("reader.css") or relative.parts[0] == "MathJax":
            destination = target / relative
        else:
            destination = lane / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = require_file(source)
        if destination.exists():
            if destination.is_symlink() or require_file(destination) != data:
                raise RuntimeError(f"conflicting QuantEcon component collision: {destination}")
        else:
            destination.write_bytes(data)

    lecture_path = target / lecture_relative
    lecture_text = require_file(lecture_path).decode("utf-8")
    local_lane_ref = re.compile(
        r'(?P<prefix>\b(?:href|src)=["\'])\.\./(?P<directory>assets|notebooks)/'
    )
    lecture_text, rewritten = local_lane_ref.subn(
        r'\g<prefix>../components/kolmogorov_bwd/\g<directory>/',
        lecture_text,
    )
    if rewritten == 0:
        raise RuntimeError("QuantEcon backward-equation lecture has no component-local references")
    if local_lane_ref.search(lecture_text):
        raise RuntimeError("QuantEcon backward-equation component-local reference rewrite failed")
    lecture_path.write_text(lecture_text, encoding="utf-8", newline="\n")
    return {
        "unit_id": str(receipt["unit_id"]),
        "source_path": str(receipt["target"]["path"]),
        "target_sha256": str(receipt["target"]["sha256"]),
        "component_manifest_sha256": sha256(require_file(manifest_path)),
        "component_receipt_sha256": sha256(require_file(receipt_path)),
        "file_count": int(receipt["file_count"]),
        "total_bytes": int(receipt["total_bytes"]),
    }


def validate_quantecon_kolmogorov_fwd_live_bindings(
    receipt: dict[str, object],
) -> tuple[str, str]:
    target_sha = sha256(require_file(QUANTECON_KOLMOGOROV_FWD_TARGET))
    target = receipt.get("target")
    if not isinstance(target, dict) or target.get("path") != (
        "source/quantecon/lectures/kolmogorov_fwd.md"
    ):
        raise RuntimeError("QuantEcon forward-equation component target path differs")
    if target.get("sha256") != target_sha:
        raise RuntimeError(
            "QuantEcon forward-equation component is stale against the live target: "
            f"receipt={target.get('sha256')} current={target_sha}"
        )

    numerical_bytes = require_file(QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA)
    numerical_sha = sha256(numerical_bytes)
    try:
        numerical = json.loads(numerical_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("QuantEcon forward-equation numerical QA is invalid") from exc
    if not isinstance(numerical, dict) or numerical.get("status") != "pass":
        raise RuntimeError("QuantEcon forward-equation numerical QA has not passed")
    numerical_target = numerical.get("target")
    if not isinstance(numerical_target, dict) or numerical_target != {
        "path": "source/quantecon/lectures/kolmogorov_fwd.md",
        "bytes": len(require_file(QUANTECON_KOLMOGOROV_FWD_TARGET)),
        "sha256": target_sha,
    }:
        raise RuntimeError(
            "QuantEcon forward-equation numerical QA is stale against the live target"
        )
    expected_numerical = {
        "path": "qa/QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA.json",
        "status": "pass",
        "sha256": numerical_sha,
    }
    if receipt.get("numerical_qa") != expected_numerical:
        raise RuntimeError(
            "QuantEcon forward-equation component receipt is stale against the live numerical QA"
        )
    return target_sha, numerical_sha


def copy_quantecon_kolmogorov_fwd_component(stage: Path) -> dict[str, object]:
    """Merge the verified forward-equation unit into the QuantEcon closure."""
    root = QUANTECON_KOLMOGOROV_FWD_COMPONENT_ROOT
    receipt_path = root / "COMPONENT_RECEIPT.json"
    manifest_path = root / "COMPONENT_MANIFEST.tsv"
    receipt = json.loads(require_file(receipt_path).decode("utf-8"))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon forward-equation component receipt schema differs")
    if receipt.get("unit_id") != "unit.o009.quantecon.ctmc.kolmogorov-forward":
        raise RuntimeError("QuantEcon forward-equation component unit identity differs")
    target_sha, numerical_qa_sha = validate_quantecon_kolmogorov_fwd_live_bindings(
        receipt
    )
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    manifest_paths: set[Path] = set()
    for row in listed:
        relative = Path(str(row["path"]))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise RuntimeError(f"unsafe QuantEcon forward-equation manifest path: {relative}")
        if relative in manifest_paths:
            raise RuntimeError(f"duplicate QuantEcon forward-equation manifest path: {relative}")
        manifest_paths.add(relative)
        data = require_file(root / relative)
        if int(row["bytes"]) != len(data) or str(row["sha256"]) != sha256(data):
            raise RuntimeError(f"QuantEcon forward-equation component manifest mismatch: {relative}")
    lecture_relative = Path("lectures/kolmogorov_fwd.html")
    if lecture_relative not in manifest_paths:
        raise RuntimeError("QuantEcon forward-equation lecture is absent from its manifest")
    required_component_assets = {
        Path("assets/kolmogorov_fwd-source-flow.png"),
        Path("assets/kolmogorov_fwd-cell-04-data.csv"),
        Path("assets/kolmogorov_fwd-cell-06-data.csv"),
    }
    if not required_component_assets.issubset(manifest_paths):
        raise RuntimeError(
            "QuantEcon forward-equation accessibility closure is incomplete: "
            f"{sorted(str(path) for path in required_component_assets - manifest_paths)}"
        )
    if receipt.get("manifest_sha256") != sha256(require_file(manifest_path)):
        raise RuntimeError("QuantEcon forward-equation component receipt does not bind its manifest")
    if int(receipt.get("file_count", -1)) != len(listed):
        raise RuntimeError("QuantEcon forward-equation component file count differs")
    if int(receipt.get("total_bytes", -1)) != sum(int(row["bytes"]) for row in listed):
        raise RuntimeError("QuantEcon forward-equation component byte count differs")
    actual_paths = {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    }
    expected_paths = manifest_paths | {
        Path("COMPONENT_MANIFEST.tsv"),
        Path("COMPONENT_RECEIPT.json"),
    }
    if actual_paths != expected_paths:
        raise RuntimeError(
            "QuantEcon forward-equation component inventory differs: "
            f"missing={sorted(str(path) for path in expected_paths - actual_paths)}; "
            f"unexpected={sorted(str(path) for path in actual_paths - expected_paths)}"
        )

    target = stage / "quantecon"
    lane = target / "components" / "kolmogorov_fwd"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    ):
        relative = source.relative_to(root)
        if relative == lecture_relative:
            destination = target / relative
        elif relative == Path("reader.css") or relative.parts[0] == "MathJax":
            destination = target / relative
        else:
            destination = lane / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = require_file(source)
        if destination.exists():
            if destination.is_symlink() or require_file(destination) != data:
                raise RuntimeError(f"conflicting QuantEcon component collision: {destination}")
        else:
            destination.write_bytes(data)

    lecture_path = target / lecture_relative
    lecture_text = require_file(lecture_path).decode("utf-8")
    local_lane_ref = re.compile(
        r'(?P<prefix>\b(?:href|src)=["\'])\.\./(?P<directory>assets|notebooks)/'
    )
    lecture_text, rewritten = local_lane_ref.subn(
        r'\g<prefix>../components/kolmogorov_fwd/\g<directory>/',
        lecture_text,
    )
    if rewritten < 5:
        raise RuntimeError(
            "QuantEcon forward-equation lecture lost component-local source, "
            "notebook, figure, or CSV references"
        )
    if local_lane_ref.search(lecture_text):
        raise RuntimeError("QuantEcon forward-equation component-local reference rewrite failed")
    lecture_path.write_text(lecture_text, encoding="utf-8", newline="\n")
    return {
        "unit_id": str(receipt["unit_id"]),
        "source_path": str(receipt["target"]["path"]),
        "target_sha256": target_sha,
        "numerical_qa_sha256": numerical_qa_sha,
        "component_manifest_sha256": sha256(require_file(manifest_path)),
        "component_receipt_sha256": sha256(require_file(receipt_path)),
        "file_count": int(receipt["file_count"]),
        "total_bytes": int(receipt["total_bytes"]),
    }


def validate_quantecon_generators_live_binding(
    receipt: dict[str, object],
) -> str:
    """Bind the zero-code generators component to the exact live translation."""
    target_sha = sha256(require_file(QUANTECON_GENERATORS_TARGET))
    target = receipt.get("target")
    if not isinstance(target, dict) or target.get("path") != (
        "source/quantecon/lectures/generators.md"
    ):
        raise RuntimeError("QuantEcon generators component target path differs")
    if target.get("sha256") != target_sha:
        raise RuntimeError(
            "QuantEcon generators component is stale against the live target: "
            f"receipt={target.get('sha256')} current={target_sha}"
        )
    topology = receipt.get("topology")
    if not isinstance(topology, dict) or {
        key: int(topology.get(key, -1))
        for key in ("exercises", "solutions", "code_cells")
    } != {"exercises": 3, "solutions": 3, "code_cells": 0}:
        raise RuntimeError("QuantEcon generators topology differs")
    closure = receipt.get("unit_closure")
    if not isinstance(closure, dict) or any(
        int(closure.get(key, -1)) != expected
        for key, expected in {
            "target_markdown_bytes": len(require_file(QUANTECON_GENERATORS_TARGET)),
            "target_code_cells": 0,
            "unit_source_assets": 0,
            "unit_generated_media": 0,
        }.items()
    ):
        raise RuntimeError("QuantEcon generators zero-code/source closure differs")
    if closure.get("target_markdown_sha256") != target_sha:
        raise RuntimeError("QuantEcon generators unit closure is stale")
    authority = receipt.get("authority")
    if not isinstance(authority, dict) or not authority.get("notebook_sha256"):
        raise RuntimeError("QuantEcon generators authority notebook witness is absent")
    return target_sha


def copy_quantecon_generators_component(stage: Path) -> dict[str, object]:
    """Merge the verified semigroups/generators unit into the reader closure."""
    root = QUANTECON_GENERATORS_COMPONENT_ROOT
    receipt_path = root / "COMPONENT_RECEIPT.json"
    manifest_path = root / "COMPONENT_MANIFEST.tsv"
    receipt = json.loads(require_file(receipt_path).decode("utf-8"))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon generators component receipt schema differs")
    if receipt.get("unit_id") != "unit.o009.quantecon.ctmc.generators":
        raise RuntimeError("QuantEcon generators component unit identity differs")
    target_sha = validate_quantecon_generators_live_binding(receipt)
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    manifest_paths: set[Path] = set()
    for row in listed:
        relative = Path(str(row["path"]))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise RuntimeError(f"unsafe QuantEcon generators manifest path: {relative}")
        if relative in manifest_paths:
            raise RuntimeError(f"duplicate QuantEcon generators manifest path: {relative}")
        manifest_paths.add(relative)
        data = require_file(root / relative)
        if int(row["bytes"]) != len(data) or str(row["sha256"]) != sha256(data):
            raise RuntimeError(f"QuantEcon generators component manifest mismatch: {relative}")
    lecture_relative = Path("lectures/generators.html")
    required_closure = {
        lecture_relative,
        Path("notebooks/generators-authority.ipynb"),
        Path("notebooks/generators-executed.ipynb"),
        Path("source-generators.md"),
        Path("reader.css"),
        Path("MathJax/tex-svg.js"),
    }
    if manifest_paths != required_closure:
        raise RuntimeError(
            "QuantEcon generators component closure differs: "
            f"missing={sorted(str(path) for path in required_closure - manifest_paths)}; "
            f"unexpected={sorted(str(path) for path in manifest_paths - required_closure)}"
        )
    if receipt.get("manifest_sha256") != sha256(require_file(manifest_path)):
        raise RuntimeError("QuantEcon generators component receipt does not bind its manifest")
    if int(receipt.get("file_count", -1)) != len(listed):
        raise RuntimeError("QuantEcon generators component file count differs")
    if int(receipt.get("total_bytes", -1)) != sum(int(row["bytes"]) for row in listed):
        raise RuntimeError("QuantEcon generators component byte count differs")
    actual_paths = {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    }
    expected_paths = manifest_paths | {
        Path("COMPONENT_MANIFEST.tsv"),
        Path("COMPONENT_RECEIPT.json"),
    }
    if actual_paths != expected_paths:
        raise RuntimeError(
            "QuantEcon generators component inventory differs: "
            f"missing={sorted(str(path) for path in expected_paths - actual_paths)}; "
            f"unexpected={sorted(str(path) for path in actual_paths - expected_paths)}"
        )

    target = stage / "quantecon"
    lane = target / "components" / "generators"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    ):
        relative = source.relative_to(root)
        if relative == lecture_relative:
            destination = target / relative
        elif relative == Path("reader.css") or relative.parts[0] == "MathJax":
            destination = target / relative
        else:
            destination = lane / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = require_file(source)
        if destination.exists():
            if destination.is_symlink() or require_file(destination) != data:
                raise RuntimeError(f"conflicting QuantEcon component collision: {destination}")
        else:
            destination.write_bytes(data)

    lecture_text = require_file(target / lecture_relative).decode("utf-8")
    forbidden_component_local = re.compile(
        r'\b(?:href|src)=["\']\.\./(?:assets|notebooks)/'
    )
    if forbidden_component_local.search(lecture_text):
        raise RuntimeError(
            "zero-code QuantEcon generators lecture unexpectedly links component-local files"
        )
    return {
        "unit_id": str(receipt["unit_id"]),
        "source_path": str(receipt["target"]["path"]),
        "target_sha256": target_sha,
        "component_manifest_sha256": sha256(require_file(manifest_path)),
        "component_receipt_sha256": sha256(require_file(receipt_path)),
        "file_count": int(receipt["file_count"]),
        "total_bytes": int(receipt["total_bytes"]),
    }


def validate_quantecon_uc_mc_semigroups_live_bindings(
    receipt: dict[str, object],
) -> tuple[str, str]:
    """Bind the zero-code UC Markov unit and its numerical QA to live bytes."""
    target_sha = sha256(require_file(QUANTECON_UC_MC_SEMIGROUPS_TARGET))
    target = receipt.get("target")
    if not isinstance(target, dict) or target.get("path") != (
        "source/quantecon/lectures/uc_mc_semigroups.md"
    ):
        raise RuntimeError("QuantEcon UC Markov component target path differs")
    if target.get("sha256") != target_sha:
        raise RuntimeError(
            "QuantEcon UC Markov component is stale against the live target: "
            f"receipt={target.get('sha256')} current={target_sha}"
        )
    topology = receipt.get("topology")
    if not isinstance(topology, dict) or {
        key: int(topology.get(key, -1))
        for key in ("headings", "exercises", "solutions", "code_cells")
    } != {"headings": 13, "exercises": 5, "solutions": 5, "code_cells": 0}:
        raise RuntimeError("QuantEcon UC Markov topology differs")
    closure = receipt.get("unit_closure")
    if not isinstance(closure, dict) or any(
        int(closure.get(key, -1)) != expected
        for key, expected in {
            "authority_markdown_bytes": 18_234,
            "authority_notebook_bytes": 29_169,
            "authority_notebook_cells": 34,
            "authority_code_cells": 0,
            "target_markdown_bytes": len(require_file(QUANTECON_UC_MC_SEMIGROUPS_TARGET)),
            "target_code_cells": 0,
            "unit_source_assets": 0,
            "unit_generated_media": 0,
        }.items()
    ):
        raise RuntimeError("QuantEcon UC Markov zero-code/source closure differs")
    if closure.get("target_markdown_sha256") != target_sha:
        raise RuntimeError("QuantEcon UC Markov unit closure is stale")
    authority = receipt.get("authority")
    if (
        not isinstance(authority, dict)
        or authority.get("source_sha256")
        != "cb5e67bc9a614a0169ba9b9bee479a0060b88401e0a7442154242af7bffd9b69"
        or authority.get("notebook_sha256")
        != "fd772f3a052aa9bba611bc5d419858256f1f390459e5c6cd681b6b9ebb58f9ef"
    ):
        raise RuntimeError("QuantEcon UC Markov authority binding differs")
    numerical = receipt.get("numerical_qa")
    if not isinstance(numerical, dict) or numerical.get("path") != (
        "qa/QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA.json"
    ) or numerical.get("status") != "pass":
        raise RuntimeError("QuantEcon UC Markov numerical-QA receipt differs")
    numerical_sha = sha256(require_file(QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA))
    if numerical.get("sha256") != numerical_sha:
        raise RuntimeError("QuantEcon UC Markov numerical-QA hash differs")
    numerical_receipt = json.loads(
        require_file(QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA).decode("utf-8")
    )
    if (
        numerical_receipt.get("status") != "pass"
        or numerical_receipt.get("target", {}).get("sha256") != target_sha
        or numerical_receipt.get("authority", {}).get("sha256")
        != authority.get("source_sha256")
    ):
        raise RuntimeError("QuantEcon UC Markov numerical-QA live binding differs")
    return target_sha, numerical_sha


def copy_quantecon_uc_mc_semigroups_component(stage: Path) -> dict[str, object]:
    """Merge the verified UC Markov semigroup unit into the reader closure."""
    root = QUANTECON_UC_MC_SEMIGROUPS_COMPONENT_ROOT
    receipt_path = root / "COMPONENT_RECEIPT.json"
    manifest_path = root / "COMPONENT_MANIFEST.tsv"
    receipt = json.loads(require_file(receipt_path).decode("utf-8"))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon UC Markov component receipt schema differs")
    if receipt.get("unit_id") != (
        "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups"
    ):
        raise RuntimeError("QuantEcon UC Markov component unit identity differs")
    target_sha, numerical_qa_sha = validate_quantecon_uc_mc_semigroups_live_bindings(
        receipt
    )
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    manifest_paths: set[Path] = set()
    for row in listed:
        relative = Path(str(row["path"]))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise RuntimeError(f"unsafe QuantEcon UC Markov manifest path: {relative}")
        if relative in manifest_paths:
            raise RuntimeError(f"duplicate QuantEcon UC Markov manifest path: {relative}")
        manifest_paths.add(relative)
        data = require_file(root / relative)
        if int(row["bytes"]) != len(data) or str(row["sha256"]) != sha256(data):
            raise RuntimeError(f"QuantEcon UC Markov component manifest mismatch: {relative}")
    lecture_relative = Path("lectures/uc_mc_semigroups.html")
    required_closure = {
        lecture_relative,
        Path("notebooks/uc_mc_semigroups-authority.ipynb"),
        Path("notebooks/uc_mc_semigroups-executed.ipynb"),
        Path("source-uc_mc_semigroups.md"),
        Path("reader.css"),
        Path("MathJax/tex-svg.js"),
    }
    if manifest_paths != required_closure:
        raise RuntimeError(
            "QuantEcon UC Markov component closure differs: "
            f"missing={sorted(str(path) for path in required_closure - manifest_paths)}; "
            f"unexpected={sorted(str(path) for path in manifest_paths - required_closure)}"
        )
    if receipt.get("manifest_sha256") != sha256(require_file(manifest_path)):
        raise RuntimeError("QuantEcon UC Markov receipt does not bind its manifest")
    if int(receipt.get("file_count", -1)) != len(listed):
        raise RuntimeError("QuantEcon UC Markov component file count differs")
    if int(receipt.get("total_bytes", -1)) != sum(int(row["bytes"]) for row in listed):
        raise RuntimeError("QuantEcon UC Markov component byte count differs")
    actual_paths = {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    }
    expected_paths = manifest_paths | {
        Path("COMPONENT_MANIFEST.tsv"),
        Path("COMPONENT_RECEIPT.json"),
    }
    if actual_paths != expected_paths:
        raise RuntimeError(
            "QuantEcon UC Markov component inventory differs: "
            f"missing={sorted(str(path) for path in expected_paths - actual_paths)}; "
            f"unexpected={sorted(str(path) for path in actual_paths - expected_paths)}"
        )

    target = stage / "quantecon"
    lane = target / "components" / "uc_mc_semigroups"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    ):
        relative = source.relative_to(root)
        if relative == lecture_relative:
            destination = target / relative
        elif relative == Path("reader.css") or relative.parts[0] == "MathJax":
            destination = target / relative
        else:
            destination = lane / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = require_file(source)
        if destination.exists():
            if destination.is_symlink() or require_file(destination) != data:
                raise RuntimeError(f"conflicting QuantEcon component collision: {destination}")
        else:
            destination.write_bytes(data)

    lecture_text = require_file(target / lecture_relative).decode("utf-8")
    forbidden_component_local = re.compile(
        r'\b(?:href|src)=["\']\.\./(?:assets|notebooks)/'
    )
    if forbidden_component_local.search(lecture_text):
        raise RuntimeError(
            "zero-code QuantEcon UC Markov lecture unexpectedly links component-local files"
        )
    return {
        "unit_id": str(receipt["unit_id"]),
        "source_path": str(receipt["target"]["path"]),
        "target_sha256": target_sha,
        "numerical_qa_sha256": numerical_qa_sha,
        "component_manifest_sha256": sha256(require_file(manifest_path)),
        "component_receipt_sha256": sha256(require_file(receipt_path)),
        "file_count": int(receipt["file_count"]),
        "total_bytes": int(receipt["total_bytes"]),
    }


def validate_quantecon_ergodicity_live_bindings(
    receipt: dict[str, object],
) -> tuple[str, str]:
    """Bind the final executable QuantEcon unit and numerical QA to live bytes."""
    target_bytes = require_file(QUANTECON_ERGODICITY_TARGET)
    target_sha = sha256(target_bytes)
    target = receipt.get("target")
    if not isinstance(target, dict) or target.get("path") != (
        "source/quantecon/lectures/ergodicity.md"
    ):
        raise RuntimeError("QuantEcon ergodicity component target path differs")
    if target.get("sha256") != target_sha:
        raise RuntimeError(
            "QuantEcon ergodicity component is stale against the live target: "
            f"receipt={target.get('sha256')} current={target_sha}"
        )
    topology = receipt.get("topology")
    if not isinstance(topology, dict) or {
        key: int(topology.get(key, -1))
        for key in ("exercises", "solutions", "code_cells")
    } != {"exercises": 3, "solutions": 3, "code_cells": 4}:
        raise RuntimeError("QuantEcon ergodicity topology differs")
    authority = receipt.get("authority")
    if (
        not isinstance(authority, dict)
        or authority.get("source_sha256")
        != "01c8f94e8016119107d6a3c14e688a0c1ed71690f678a2ae252703f7abccba84"
        or authority.get("notebook_sha256")
        != "e9daac187c07d8ba4d63cb43df2bb1874afa69a6095f91dd9f14a27c674fa881"
    ):
        raise RuntimeError("QuantEcon ergodicity authority binding differs")
    numerical_bytes = require_file(QUANTECON_ERGODICITY_NUMERICAL_QA)
    numerical_sha = sha256(numerical_bytes)
    numerical = json.loads(numerical_bytes.decode("utf-8"))
    if (
        not isinstance(numerical, dict)
        or numerical.get("status") != "pass"
        or numerical.get("target", {}).get("sha256") != target_sha
    ):
        raise RuntimeError("QuantEcon ergodicity numerical QA is stale or failed")
    numerical_binding = receipt.get("numerical_qa")
    if (
        not isinstance(numerical_binding, dict)
        or numerical_binding.get("path") != "qa/QUANTECON_ERGODICITY_NUMERICAL_QA.json"
        or numerical_binding.get("status") != "pass"
        or numerical_binding.get("sha256") != numerical_sha
    ):
        raise RuntimeError("QuantEcon ergodicity numerical-QA receipt differs")
    if receipt.get("replay_match") is not True:
        raise RuntimeError("QuantEcon ergodicity two-pass replay is not exact")
    return target_sha, numerical_sha


def copy_quantecon_ergodicity_component(stage: Path) -> dict[str, object]:
    """Merge the verified stationarity/ergodicity unit into the reader closure."""
    root = QUANTECON_ERGODICITY_COMPONENT_ROOT
    receipt_path = root / "COMPONENT_RECEIPT.json"
    manifest_path = root / "COMPONENT_MANIFEST.tsv"
    receipt = json.loads(require_file(receipt_path).decode("utf-8"))
    if receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon ergodicity component receipt schema differs")
    if receipt.get("unit_id") != "unit.o009.quantecon.ctmc.stationarity-ergodicity":
        raise RuntimeError("QuantEcon ergodicity component unit identity differs")
    target_sha, numerical_qa_sha = validate_quantecon_ergodicity_live_bindings(receipt)
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        listed = list(csv.DictReader(stream, delimiter="\t"))
    manifest_paths: set[Path] = set()
    for row in listed:
        relative = Path(str(row["path"]))
        if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise RuntimeError(f"unsafe QuantEcon ergodicity manifest path: {relative}")
        if relative in manifest_paths:
            raise RuntimeError(f"duplicate QuantEcon ergodicity manifest path: {relative}")
        manifest_paths.add(relative)
        data = require_file(root / relative)
        if int(row["bytes"]) != len(data) or str(row["sha256"]) != sha256(data):
            raise RuntimeError(f"QuantEcon ergodicity manifest mismatch: {relative}")
    lecture_relative = Path("lectures/ergodicity.html")
    required_closure = {
        lecture_relative,
        Path("notebooks/ergodicity-authority.ipynb"),
        Path("notebooks/ergodicity-executed.ipynb"),
        Path("source-ergodicity.md"),
        Path("assets/ergodicity-cell-04-figure-01.png"),
        Path("reader.css"),
        Path("MathJax/tex-svg.js"),
    }
    if manifest_paths != required_closure:
        raise RuntimeError(
            "QuantEcon ergodicity component closure differs: "
            f"missing={sorted(str(path) for path in required_closure - manifest_paths)}; "
            f"unexpected={sorted(str(path) for path in manifest_paths - required_closure)}"
        )
    if receipt.get("manifest_sha256") != sha256(require_file(manifest_path)):
        raise RuntimeError("QuantEcon ergodicity receipt does not bind its manifest")
    if int(receipt.get("file_count", -1)) != len(listed):
        raise RuntimeError("QuantEcon ergodicity component file count differs")
    if int(receipt.get("total_bytes", -1)) != sum(int(row["bytes"]) for row in listed):
        raise RuntimeError("QuantEcon ergodicity component byte count differs")
    actual_paths = {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    }
    expected_paths = manifest_paths | {
        Path("COMPONENT_MANIFEST.tsv"),
        Path("COMPONENT_RECEIPT.json"),
    }
    if actual_paths != expected_paths:
        raise RuntimeError(
            "QuantEcon ergodicity component inventory differs: "
            f"missing={sorted(str(path) for path in expected_paths - actual_paths)}; "
            f"unexpected={sorted(str(path) for path in actual_paths - expected_paths)}"
        )

    target = stage / "quantecon"
    lane = target / "components" / "ergodicity"
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    ):
        relative = source.relative_to(root)
        if relative == lecture_relative:
            destination = target / relative
        elif relative == Path("reader.css") or relative.parts[0] == "MathJax":
            destination = target / relative
        else:
            destination = lane / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = require_file(source)
        if destination.exists():
            if destination.is_symlink() or require_file(destination) != data:
                raise RuntimeError(f"conflicting QuantEcon component collision: {destination}")
        else:
            destination.write_bytes(data)

    lecture_path = target / lecture_relative
    lecture_text = require_file(lecture_path).decode("utf-8")
    local_lane_ref = re.compile(
        r'(?P<prefix>\b(?:href|src)=["\'])\.\./(?P<directory>assets|notebooks)/'
    )
    lecture_text, rewritten = local_lane_ref.subn(
        r'\g<prefix>../components/ergodicity/\g<directory>/',
        lecture_text,
    )
    if rewritten == 0 or local_lane_ref.search(lecture_text):
        raise RuntimeError("QuantEcon ergodicity component-local reference rewrite failed")
    lecture_path.write_text(lecture_text, encoding="utf-8", newline="\n")
    return {
        "unit_id": str(receipt["unit_id"]),
        "source_path": str(receipt["target"]["path"]),
        "target_sha256": target_sha,
        "numerical_qa_sha256": numerical_qa_sha,
        "component_manifest_sha256": sha256(require_file(manifest_path)),
        "component_receipt_sha256": sha256(require_file(receipt_path)),
        "file_count": int(receipt["file_count"]),
        "total_bytes": int(receipt["total_bytes"]),
    }


def site_rows(site: Path) -> list[dict[str, object]]:
    if not site.is_dir() or site.is_symlink():
        raise RuntimeError(f"site root is missing or linked: {site}")
    excluded = {"PACKAGE_MANIFEST.csv", "BUILD_RECEIPT.json"}
    entries = list(site.rglob("*"))
    linked = [path.relative_to(site).as_posix() for path in entries if path.is_symlink()]
    if linked:
        raise RuntimeError(f"site contains symbolic links: {linked}")
    paths = [path for path in entries if path.is_file()]
    paths = [path for path in paths if path.relative_to(site).as_posix() not in excluded]
    paths.sort(key=lambda path: path.relative_to(site).as_posix().casefold())
    rows: list[dict[str, object]] = []
    for path in paths:
        data = path.read_bytes()
        rows.append(
            {
                "path": path.relative_to(site).as_posix(),
                "bytes": len(data),
                "sha256": sha256(data),
            }
        )
    return rows


def shared_reader_stylesheet(site: Path) -> bytes:
    root_css = require_file(site / "reader.css")
    quantecon_css = require_file(site / "quantecon" / "reader.css")
    if quantecon_css != root_css:
        raise RuntimeError(
            "root and QuantEcon reader.css bytes differ; one shared cache key is unsafe"
        )
    return root_css


def synchronize_shared_reader_stylesheet(site: Path) -> None:
    """Apply the edition's validated shared CSS after donor-component admission."""
    root_css = require_file(site / "reader.css")
    quantecon_css = site / "quantecon" / "reader.css"
    if not quantecon_css.is_file() or quantecon_css.is_symlink():
        raise RuntimeError("QuantEcon shared reader stylesheet target is missing or unsafe")
    quantecon_css.write_bytes(root_css)


def version_reader_stylesheet_links(site: Path) -> None:
    """Cache-bust the shared stylesheet after every staged HTML build."""
    digest = sha256(shared_reader_stylesheet(site))[:12]
    pattern = re.compile(
        r'(?P<prefix>href=["\'])(?P<path>[^"\']*reader\.css)(?P<suffix>["\'])'
    )
    rewritten_total = 0
    for path in sorted(site.rglob("*.html"), key=lambda item: item.as_posix().casefold()):
        text = require_file(path).decode("utf-8")
        updated, rewritten = pattern.subn(
            lambda match: (
                f"{match.group('prefix')}{match.group('path')}?v={digest}"
                f"{match.group('suffix')}"
            ),
            text,
        )
        if rewritten:
            path.write_text(updated, encoding="utf-8", newline="\n")
            rewritten_total += rewritten
    if rewritten_total == 0:
        raise RuntimeError("reader stylesheet cache-buster found no HTML links")


def original_bridge_receipt_units(site: Path) -> list[dict[str, object]]:
    units: list[dict[str, object]] = []
    for spec in ORIGINAL_BRIDGE_SPECS:
        source = Path(spec["source"])
        output = Path(spec["output"])
        source_data = require_file(source)
        output_data = require_file(site / output)
        units.append(
            {
                "unit_id": str(spec["unit_id"]),
                "source": source.relative_to(ROOT).as_posix(),
                "output": output.as_posix(),
                "previous_output": Path(spec["previous_output"]).as_posix(),
                "rights_id": str(spec["rights_id"]),
                "source_bytes": len(source_data),
                "source_sha256": sha256(source_data),
                "output_sha256": sha256(output_data),
                "stable_ids": [str(item) for item in spec["stable_ids"]],
                "disclosures": [
                    {"id": str(disclosure_id), "aria_label": str(label)}
                    for disclosure_id, label in spec["disclosures"]
                ],
                "mastery_counts": {
                    str(key): int(value)
                    for key, value in dict(spec["mastery_counts"]).items()
                },
            }
        )
    return units


def write_manifest(
    site: Path,
    lab_results: list[dict[str, object]],
    quantecon_component: dict[str, object],
    quantecon_poisson_component: dict[str, object],
    quantecon_markov_prop_component: dict[str, object],
    quantecon_kolmogorov_bwd_component: dict[str, object],
    quantecon_kolmogorov_fwd_component: dict[str, object],
    quantecon_generators_component: dict[str, object],
    quantecon_uc_mc_semigroups_component: dict[str, object],
    quantecon_ergodicity_component: dict[str, object],
) -> None:
    rows = site_rows(site)
    manifest = site / "PACKAGE_MANIFEST.csv"
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["path", "bytes", "sha256"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    build_timestamp = require_file(REPRODUCIBLE_BUILD_TIMESTAMP).decode(
        "utf-8"
    ).strip()
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?\+00:00",
        build_timestamp,
    ):
        raise RuntimeError(
            "reproducible build timestamp must be an explicit UTC ISO-8601 value"
        )
    receipt = {
        "schema": BUILD_RECEIPT_SCHEMA,
        "built_at_utc": build_timestamp,
        "timestamp_policy": (
            "pinned by 00_control/REPRODUCIBLE_BUILD_TIMESTAMP_UTC.txt for "
            "byte-reproducible reader and backend builds"
        ),
        "random_authority_manifest_sha256": RANDOM_MANIFEST_SHA256,
        "theory_units": [
            {
                "path": str(unit["rel"]),
                "authority_sha256": str(unit["authority_sha256"]),
                "target_sha256": sha256(require_file(theory_paths(unit)[1])),
            }
            for unit in THEORY_UNITS
        ],
        "original_bridge_units": original_bridge_receipt_units(site),
        "supplement_units": supplement_receipt_units(site),
        "lab_source_sha256": sha256(require_file(Path(LAB_SPECS[0]["source"]))),
        "lab_sources": [
            {
                "source": Path(spec["source"]).relative_to(ROOT).as_posix(),
                "output": Path(spec["output"]).as_posix(),
                "chunk_id": str(spec["chunk_id"]),
                "source_sha256": sha256(require_file(Path(spec["source"]))),
                "r_result_rows": result["rows"],
            }
            for spec, result in zip(LAB_SPECS, lab_results, strict=True)
        ],
        "quantecon_component": quantecon_component,
        "quantecon_poisson_component": quantecon_poisson_component,
        "quantecon_markov_prop_component": quantecon_markov_prop_component,
        "quantecon_kolmogorov_bwd_component": quantecon_kolmogorov_bwd_component,
        "quantecon_kolmogorov_fwd_component": quantecon_kolmogorov_fwd_component,
        "quantecon_generators_component": quantecon_generators_component,
        "quantecon_uc_mc_semigroups_component": quantecon_uc_mc_semigroups_component,
        "quantecon_ergodicity_component": quantecon_ergodicity_component,
        "runtime": runtime_evidence(),
        "r_version": R_VERSION,
        "r_rng": R_RNG,
        "r_result_rows": lab_results[0]["rows"],
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
        "manifest_sha256": sha256(manifest.read_bytes()),
    }
    (site / "BUILD_RECEIPT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify_original_bridge_outputs(site: Path) -> None:
    for spec in ORIGINAL_BRIDGE_SPECS:
        output = site / Path(spec["output"])
        soup = BeautifulSoup(require_file(output).decode("utf-8"), "lxml")
        root = soup.find(id=str(spec["unit_id"]))
        if root is None or root.name != "main" or "original-bridge" not in root.get(
            "class", []
        ):
            raise RuntimeError("built original bridge root/main binding differs")
        headings = soup.find_all("h1")
        heading_text = re.sub(
            r"\s+", " ", headings[0].get_text(" ", strip=True)
        ).strip() if len(headings) == 1 else ""
        if len(headings) != 1 or heading_text != str(spec["title"]):
            raise RuntimeError("built original bridge H1 differs")
        if soup.find("header", id="title-block-header") is not None:
            raise RuntimeError("built original bridge retained the duplicate generated title")
        expected_ids = tuple(str(item) for item in spec["stable_ids"])
        expected_set = set(expected_ids)
        all_ids = [str(node["id"]) for node in soup.select("[id]")]
        observed_ids = tuple(item for item in all_ids if item in expected_set)
        if observed_ids != expected_ids or any(all_ids.count(item) != 1 for item in expected_ids):
            raise RuntimeError("built original bridge stable ID order or uniqueness differs")
        expected_disclosures = tuple(
            (str(disclosure_id), str(label))
            for disclosure_id, label in spec["disclosures"]
        )
        details = soup.find_all("details")
        if tuple(str(node.get("id", "")) for node in details) != tuple(
            disclosure_id for disclosure_id, _ in expected_disclosures
        ):
            raise RuntimeError("built original bridge disclosure order differs")
        for disclosure_id, label in expected_disclosures:
            disclosure = soup.find("details", id=disclosure_id)
            summary = (
                disclosure.find("summary", recursive=False)
                if disclosure is not None
                else None
            )
            if (
                summary is None
                or summary.get_text(" ", strip=True) != label
                or str(summary.get("aria-label", "")) != label
            ):
                raise RuntimeError(
                    f"built original bridge disclosure label differs: {disclosure_id}"
                )
        if soup.select("div.hint, div.solution"):
            raise RuntimeError("built original bridge left hint/solution divs undisclosed")
        answer_ids = tuple(item for item in expected_ids if item.endswith(".answer"))
        if any(soup.find("div", id=answer_id) is None for answer_id in answer_ids):
            raise RuntimeError("built original bridge concise answers must remain visible divs")
        output_rel = Path(spec["output"])
        home_href = os.path.relpath(Path("index.html"), output_rel.parent).replace(os.sep, "/")
        previous_href = os.path.relpath(
            Path(spec["previous_output"]), output_rel.parent
        ).replace(os.sep, "/")
        edition_navs = soup.find_all("nav", attrs={"aria-label": "Navigasi edisi"})
        if len(edition_navs) != 1 or [
            str(anchor.get("href", "")) for anchor in edition_navs[0].select("a[href]")
        ] != [home_href, previous_href]:
            raise RuntimeError("built original bridge navigation differs")
        previous_links = soup.select('head link[rel~="prev"]')
        if len(previous_links) != 1 or str(previous_links[0].get("href", "")) != previous_href:
            raise RuntimeError("built original bridge previous-unit metadata differs")
        mathjax = soup.select('script[src="../MathJax/tex-svg.js"]')
        if len(mathjax) != 1:
            raise RuntimeError("built original bridge local MathJax binding differs")
        visible = re.sub(r"\s+", " ", " ".join(soup.stripped_strings)).strip()
        for witness in tuple(str(item) for item in spec["built_rights_witnesses"]):
            if witness not in visible:
                raise RuntimeError(f"built original bridge rights witness missing: {witness}")


def verify_site(site: Path, execute_r: bool = True) -> None:
    validate_lab_specs()
    validate_original_bridge_specs()
    runtime = runtime_evidence()
    manifest = site / "PACKAGE_MANIFEST.csv"
    receipt_path = site / "BUILD_RECEIPT.json"
    if (
        not manifest.is_file()
        or manifest.is_symlink()
        or not receipt_path.is_file()
        or receipt_path.is_symlink()
    ):
        raise RuntimeError("site manifest or build receipt missing")
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        expected = list(csv.DictReader(stream))
    actual = site_rows(site)
    if expected != [{key: str(value) for key, value in row.items()} for row in actual]:
        raise RuntimeError("site manifest does not match current files")
    receipt = json.loads(receipt_path.read_text("utf-8"))
    if receipt.get("schema") != BUILD_RECEIPT_SCHEMA:
        raise RuntimeError("build receipt schema differs")
    if receipt.get("random_authority_manifest_sha256") != RANDOM_MANIFEST_SHA256:
        raise RuntimeError("build receipt does not bind the Random authority manifest")
    if receipt["manifest_sha256"] != sha256(manifest.read_bytes()):
        raise RuntimeError("build receipt does not bind manifest")
    if receipt.get("file_count") != len(actual):
        raise RuntimeError("build receipt file count differs from the current site")
    if receipt.get("total_bytes") != sum(int(row["bytes"]) for row in actual):
        raise RuntimeError("build receipt byte count differs from the current site")
    expected_theory = [
        {
            "path": str(unit["rel"]),
            "authority_sha256": str(unit["authority_sha256"]),
            "target_sha256": sha256(require_file(theory_paths(unit)[1])),
        }
        for unit in THEORY_UNITS
    ]
    if receipt.get("theory_units") != expected_theory:
        raise RuntimeError("build receipt theory inputs differ from the current ordered units")
    expected_original_bridges = original_bridge_receipt_units(site)
    if receipt.get("original_bridge_units") != expected_original_bridges:
        raise RuntimeError("build receipt original bridge inputs/outputs differ")
    expected_supplements = supplement_receipt_units(site)
    if receipt.get("supplement_units") != expected_supplements:
        raise RuntimeError("build receipt authored supplement inputs/outputs differ")
    expected_labs = [
        {
            "source": Path(spec["source"]).relative_to(ROOT).as_posix(),
            "output": Path(spec["output"]).as_posix(),
            "chunk_id": str(spec["chunk_id"]),
            "source_sha256": sha256(require_file(Path(spec["source"]))),
            "r_result_rows": [dict(row) for row in spec["golden_rows"]],
        }
        for spec in LAB_SPECS
    ]
    if receipt.get("lab_sources") != expected_labs:
        raise RuntimeError("build receipt lab inputs/results differ from the current ordered specs")
    component_root = QUANTECON_COMPONENT_ROOT
    component_receipt_path = component_root / "COMPONENT_RECEIPT.json"
    component_manifest_path = component_root / "COMPONENT_MANIFEST.tsv"
    if not component_receipt_path.is_file() or not component_manifest_path.is_file():
        raise RuntimeError("verified QuantEcon component receipt/manifest is missing")
    component_receipt = json.loads(require_file(component_receipt_path).decode("utf-8"))
    expected_component = {
        "unit_id": str(component_receipt["unit_id"]),
        "source_path": str(component_receipt["target"]["path"]),
        "target_sha256": str(component_receipt["target"]["sha256"]),
        "component_manifest_sha256": sha256(require_file(component_manifest_path)),
        "component_receipt_sha256": sha256(require_file(component_receipt_path)),
        "file_count": int(component_receipt["file_count"]),
        "total_bytes": int(component_receipt["total_bytes"]),
    }
    if receipt.get("quantecon_component") != expected_component:
        raise RuntimeError("build receipt QuantEcon component binding differs")
    poisson_root = QUANTECON_POISSON_COMPONENT_ROOT
    poisson_receipt_path = poisson_root / "COMPONENT_RECEIPT.json"
    poisson_manifest_path = poisson_root / "COMPONENT_MANIFEST.tsv"
    if not poisson_receipt_path.is_file() or not poisson_manifest_path.is_file():
        raise RuntimeError("verified QuantEcon Poisson component receipt/manifest is missing")
    poisson_receipt = json.loads(require_file(poisson_receipt_path).decode("utf-8"))
    expected_poisson_component = {
        "unit_id": str(poisson_receipt["unit_id"]),
        "source_path": str(poisson_receipt["target"]["path"]),
        "target_sha256": str(poisson_receipt["target"]["sha256"]),
        "component_manifest_sha256": sha256(require_file(poisson_manifest_path)),
        "component_receipt_sha256": sha256(require_file(poisson_receipt_path)),
        "file_count": int(poisson_receipt["file_count"]),
        "total_bytes": int(poisson_receipt["total_bytes"]),
    }
    if receipt.get("quantecon_poisson_component") != expected_poisson_component:
        raise RuntimeError("build receipt QuantEcon Poisson component binding differs")
    markov_prop_root = QUANTECON_MARKOV_PROP_COMPONENT_ROOT
    markov_prop_receipt_path = markov_prop_root / "COMPONENT_RECEIPT.json"
    markov_prop_manifest_path = markov_prop_root / "COMPONENT_MANIFEST.tsv"
    if not markov_prop_receipt_path.is_file() or not markov_prop_manifest_path.is_file():
        raise RuntimeError("verified QuantEcon Markov-property component receipt/manifest is missing")
    markov_prop_receipt = json.loads(require_file(markov_prop_receipt_path).decode("utf-8"))
    if markov_prop_receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon Markov-property component receipt schema differs")
    if markov_prop_receipt.get("unit_id") != "unit.o009.quantecon.ctmc.markov-property":
        raise RuntimeError("QuantEcon Markov-property component unit identity differs")
    if markov_prop_receipt.get("target", {}).get("path") != "source/quantecon/lectures/markov_prop.md":
        raise RuntimeError("QuantEcon Markov-property component target path differs")
    expected_markov_prop_component = {
        "unit_id": str(markov_prop_receipt["unit_id"]),
        "source_path": str(markov_prop_receipt["target"]["path"]),
        "target_sha256": str(markov_prop_receipt["target"]["sha256"]),
        "component_manifest_sha256": sha256(require_file(markov_prop_manifest_path)),
        "component_receipt_sha256": sha256(require_file(markov_prop_receipt_path)),
        "file_count": int(markov_prop_receipt["file_count"]),
        "total_bytes": int(markov_prop_receipt["total_bytes"]),
    }
    if receipt.get("quantecon_markov_prop_component") != expected_markov_prop_component:
        raise RuntimeError("build receipt QuantEcon Markov-property component binding differs")
    kolmogorov_bwd_root = QUANTECON_KOLMOGOROV_BWD_COMPONENT_ROOT
    kolmogorov_bwd_receipt_path = kolmogorov_bwd_root / "COMPONENT_RECEIPT.json"
    kolmogorov_bwd_manifest_path = kolmogorov_bwd_root / "COMPONENT_MANIFEST.tsv"
    if not kolmogorov_bwd_receipt_path.is_file() or not kolmogorov_bwd_manifest_path.is_file():
        raise RuntimeError("verified QuantEcon backward-equation component receipt/manifest is missing")
    kolmogorov_bwd_receipt = json.loads(require_file(kolmogorov_bwd_receipt_path).decode("utf-8"))
    if kolmogorov_bwd_receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon backward-equation component receipt schema differs")
    if kolmogorov_bwd_receipt.get("unit_id") != "unit.o009.quantecon.ctmc.kolmogorov-backward":
        raise RuntimeError("QuantEcon backward-equation component unit identity differs")
    if kolmogorov_bwd_receipt.get("target", {}).get("path") != "source/quantecon/lectures/kolmogorov_bwd.md":
        raise RuntimeError("QuantEcon backward-equation component target path differs")
    expected_kolmogorov_bwd_component = {
        "unit_id": str(kolmogorov_bwd_receipt["unit_id"]),
        "source_path": str(kolmogorov_bwd_receipt["target"]["path"]),
        "target_sha256": str(kolmogorov_bwd_receipt["target"]["sha256"]),
        "component_manifest_sha256": sha256(require_file(kolmogorov_bwd_manifest_path)),
        "component_receipt_sha256": sha256(require_file(kolmogorov_bwd_receipt_path)),
        "file_count": int(kolmogorov_bwd_receipt["file_count"]),
        "total_bytes": int(kolmogorov_bwd_receipt["total_bytes"]),
    }
    if receipt.get("quantecon_kolmogorov_bwd_component") != expected_kolmogorov_bwd_component:
        raise RuntimeError("build receipt QuantEcon backward-equation component binding differs")
    kolmogorov_fwd_root = QUANTECON_KOLMOGOROV_FWD_COMPONENT_ROOT
    kolmogorov_fwd_receipt_path = kolmogorov_fwd_root / "COMPONENT_RECEIPT.json"
    kolmogorov_fwd_manifest_path = kolmogorov_fwd_root / "COMPONENT_MANIFEST.tsv"
    if not kolmogorov_fwd_receipt_path.is_file() or not kolmogorov_fwd_manifest_path.is_file():
        raise RuntimeError("verified QuantEcon forward-equation component receipt/manifest is missing")
    kolmogorov_fwd_receipt = json.loads(require_file(kolmogorov_fwd_receipt_path).decode("utf-8"))
    if kolmogorov_fwd_receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon forward-equation component receipt schema differs")
    if kolmogorov_fwd_receipt.get("unit_id") != "unit.o009.quantecon.ctmc.kolmogorov-forward":
        raise RuntimeError("QuantEcon forward-equation component unit identity differs")
    target_sha, numerical_qa_sha = validate_quantecon_kolmogorov_fwd_live_bindings(
        kolmogorov_fwd_receipt
    )
    expected_kolmogorov_fwd_component = {
        "unit_id": str(kolmogorov_fwd_receipt["unit_id"]),
        "source_path": str(kolmogorov_fwd_receipt["target"]["path"]),
        "target_sha256": target_sha,
        "numerical_qa_sha256": numerical_qa_sha,
        "component_manifest_sha256": sha256(require_file(kolmogorov_fwd_manifest_path)),
        "component_receipt_sha256": sha256(require_file(kolmogorov_fwd_receipt_path)),
        "file_count": int(kolmogorov_fwd_receipt["file_count"]),
        "total_bytes": int(kolmogorov_fwd_receipt["total_bytes"]),
    }
    if receipt.get("quantecon_kolmogorov_fwd_component") != expected_kolmogorov_fwd_component:
        raise RuntimeError("build receipt QuantEcon forward-equation component binding differs")
    generators_root = QUANTECON_GENERATORS_COMPONENT_ROOT
    generators_receipt_path = generators_root / "COMPONENT_RECEIPT.json"
    generators_manifest_path = generators_root / "COMPONENT_MANIFEST.tsv"
    if not generators_receipt_path.is_file() or not generators_manifest_path.is_file():
        raise RuntimeError("verified QuantEcon generators component receipt/manifest is missing")
    generators_receipt = json.loads(require_file(generators_receipt_path).decode("utf-8"))
    if generators_receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon generators component receipt schema differs")
    if generators_receipt.get("unit_id") != "unit.o009.quantecon.ctmc.generators":
        raise RuntimeError("QuantEcon generators component unit identity differs")
    generators_target_sha = validate_quantecon_generators_live_binding(
        generators_receipt
    )
    expected_generators_component = {
        "unit_id": str(generators_receipt["unit_id"]),
        "source_path": str(generators_receipt["target"]["path"]),
        "target_sha256": generators_target_sha,
        "component_manifest_sha256": sha256(require_file(generators_manifest_path)),
        "component_receipt_sha256": sha256(require_file(generators_receipt_path)),
        "file_count": int(generators_receipt["file_count"]),
        "total_bytes": int(generators_receipt["total_bytes"]),
    }
    if receipt.get("quantecon_generators_component") != expected_generators_component:
        raise RuntimeError("build receipt QuantEcon generators component binding differs")
    uc_root = QUANTECON_UC_MC_SEMIGROUPS_COMPONENT_ROOT
    uc_receipt_path = uc_root / "COMPONENT_RECEIPT.json"
    uc_manifest_path = uc_root / "COMPONENT_MANIFEST.tsv"
    if not uc_receipt_path.is_file() or not uc_manifest_path.is_file():
        raise RuntimeError("verified QuantEcon UC Markov component receipt/manifest is missing")
    uc_receipt = json.loads(require_file(uc_receipt_path).decode("utf-8"))
    if uc_receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon UC Markov component receipt schema differs")
    if uc_receipt.get("unit_id") != (
        "unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups"
    ):
        raise RuntimeError("QuantEcon UC Markov component unit identity differs")
    uc_target_sha, uc_numerical_qa_sha = (
        validate_quantecon_uc_mc_semigroups_live_bindings(uc_receipt)
    )
    expected_uc_component = {
        "unit_id": str(uc_receipt["unit_id"]),
        "source_path": str(uc_receipt["target"]["path"]),
        "target_sha256": uc_target_sha,
        "numerical_qa_sha256": uc_numerical_qa_sha,
        "component_manifest_sha256": sha256(require_file(uc_manifest_path)),
        "component_receipt_sha256": sha256(require_file(uc_receipt_path)),
        "file_count": int(uc_receipt["file_count"]),
        "total_bytes": int(uc_receipt["total_bytes"]),
    }
    if receipt.get("quantecon_uc_mc_semigroups_component") != expected_uc_component:
        raise RuntimeError("build receipt QuantEcon UC Markov component binding differs")
    ergodicity_root = QUANTECON_ERGODICITY_COMPONENT_ROOT
    ergodicity_receipt_path = ergodicity_root / "COMPONENT_RECEIPT.json"
    ergodicity_manifest_path = ergodicity_root / "COMPONENT_MANIFEST.tsv"
    if not ergodicity_receipt_path.is_file() or not ergodicity_manifest_path.is_file():
        raise RuntimeError("verified QuantEcon ergodicity component receipt/manifest is missing")
    ergodicity_receipt = json.loads(require_file(ergodicity_receipt_path).decode("utf-8"))
    if ergodicity_receipt.get("schema") != "o009.quantecon-component.v1":
        raise RuntimeError("QuantEcon ergodicity component receipt schema differs")
    if ergodicity_receipt.get("unit_id") != "unit.o009.quantecon.ctmc.stationarity-ergodicity":
        raise RuntimeError("QuantEcon ergodicity component unit identity differs")
    ergodicity_target_sha, ergodicity_numerical_qa_sha = (
        validate_quantecon_ergodicity_live_bindings(ergodicity_receipt)
    )
    expected_ergodicity_component = {
        "unit_id": str(ergodicity_receipt["unit_id"]),
        "source_path": str(ergodicity_receipt["target"]["path"]),
        "target_sha256": ergodicity_target_sha,
        "numerical_qa_sha256": ergodicity_numerical_qa_sha,
        "component_manifest_sha256": sha256(require_file(ergodicity_manifest_path)),
        "component_receipt_sha256": sha256(require_file(ergodicity_receipt_path)),
        "file_count": int(ergodicity_receipt["file_count"]),
        "total_bytes": int(ergodicity_receipt["total_bytes"]),
    }
    if receipt.get("quantecon_ergodicity_component") != expected_ergodicity_component:
        raise RuntimeError("build receipt QuantEcon ergodicity component binding differs")
    if receipt.get("lab_source_sha256") != expected_labs[0]["source_sha256"]:
        raise RuntimeError("legacy first-lab source binding differs")
    if receipt.get("r_result_rows") != expected_labs[0]["r_result_rows"]:
        raise RuntimeError("legacy first-lab result binding differs")
    if receipt.get("r_version") != R_VERSION or receipt.get("r_rng") != R_RNG:
        raise RuntimeError("legacy R runtime binding differs")
    if receipt.get("runtime") != runtime:
        raise RuntimeError("build receipt executable/runtime evidence differs")
    html_paths = sorted(
        (site / str(row["path"]) for row in actual if str(row["path"]).endswith(".html")),
        key=lambda path: path.as_posix().casefold(),
    )
    expected_css_query = f"v={sha256(shared_reader_stylesheet(site))[:12]}"
    for path in html_paths:
        data = path.read_bytes()
        text = data.decode("utf-8")
        soup = BeautifulSoup(text, "lxml")
        if soup.html is None or soup.html.get("lang") != "id-ID":
            raise RuntimeError(f"missing lang=id-ID: {path}")
        if len(soup.find_all("h1")) != 1:
            raise RuntimeError(f"reader page must have exactly one h1: {path}")
        if len(soup.find_all("main")) != 1:
            raise RuntimeError(f"reader page must have exactly one main landmark: {path}")
        heading_levels = [
            int(heading.name[1])
            for heading in soup.find_all(("h1", "h2", "h3", "h4", "h5", "h6"))
        ]
        if any(
            following - current > 1
            for current, following in zip(heading_levels, heading_levels[1:])
        ):
            raise RuntimeError(f"reader heading hierarchy skips a level: {path}")
        summary_labels = [
            str(summary.get("aria-label", "")).strip()
            for summary in soup.find_all("summary")
        ]
        if any(not label for label in summary_labels) or len(summary_labels) != len(
            set(summary_labels)
        ):
            raise RuntimeError(f"reader disclosure labels are missing or duplicated: {path}")
        ids = [str(tag["id"]) for tag in soup.select("[id]")]
        if len(ids) != len(set(ids)):
            raise RuntimeError(f"duplicate id: {path}")
        for tag in soup.select("a[href], img[src], script[src], link[href]"):
            attribute = "href" if tag.has_attr("href") else "src"
            ref = str(tag.get(attribute, ""))
            parsed = urllib.parse.urlparse(ref)
            if parsed.path.endswith("reader.css") and parsed.query != expected_css_query:
                raise RuntimeError(
                    f"reader stylesheet link lacks the current cache-buster: {path} -> {ref}"
                )
            if not ref or parsed.scheme:
                continue
            if not parsed.path and parsed.fragment:
                fragment = urllib.parse.unquote(parsed.fragment)
                if soup.find(id=fragment) is None:
                    raise RuntimeError(f"missing same-page fragment: {path} -> {ref}")
                continue
            target = (path.parent / urllib.parse.unquote(parsed.path)).resolve()
            try:
                target.relative_to(site.resolve())
            except ValueError as exc:
                raise RuntimeError(f"local reference escapes site: {path} -> {ref}") from exc
            if not target.is_file():
                raise RuntimeError(f"missing local reference: {path} -> {ref}")
            if target.is_symlink():
                raise RuntimeError(f"linked local reference: {path} -> {ref}")
            if parsed.fragment:
                target_soup = BeautifulSoup(target.read_text("utf-8"), "lxml")
                if target_soup.find(id=parsed.fragment) is None:
                    raise RuntimeError(f"missing local fragment: {path} -> {ref}")
    verify_original_bridge_outputs(site)
    verify_supplement_outputs(site)
    index_soup = BeautifulSoup((site / "index.html").read_text("utf-8"), "lxml")
    index_hrefs = [str(anchor.get("href", "")) for anchor in index_soup.select("a[href]")]
    required_index_links = [str(unit["rel"]) for unit in THEORY_UNITS]
    required_index_links.append("apps/two-state.html")
    required_index_links.extend(Path(spec["output"]).as_posix() for spec in LAB_SPECS)
    required_index_links.extend(
        Path(spec["output"]).as_posix() for spec in ORIGINAL_BRIDGE_SPECS
    )
    required_index_links.append("quantecon/lectures/memoryless.html")
    required_index_links.append("quantecon/lectures/poisson.html")
    required_index_links.append("quantecon/lectures/markov_prop.html")
    required_index_links.append("quantecon/lectures/kolmogorov_bwd.html")
    required_index_links.append("quantecon/lectures/kolmogorov_fwd.html")
    required_index_links.append("quantecon/lectures/generators.html")
    required_index_links.append("quantecon/lectures/uc_mc_semigroups.html")
    required_index_links.append("quantecon/lectures/ergodicity.html")
    missing_index_links = [href for href in required_index_links if index_hrefs.count(href) != 1]
    if missing_index_links:
        raise RuntimeError(
            f"reader index must link every admitted unit exactly once: {missing_index_links}"
        )
    overview_expectations = {
        "martingales/index.html": {
            "ids": {"Summary", "External"},
            "metadata": {
                "previous": "../markov/index.html",
                "next": "../brown/index.html",
            },
            "scope_note": None,
        },
        "markov/index.html": {
            "ids": {"sum", "cha", "spe", "con", "spe2", "Apps", "External"},
            "metadata": {"next": "../martingales/index.html"},
            "scope_note": "markov-index-edition-scope",
        },
        "brown/index.html": {
            "ids": {"sum", "apps", "ext", "Grimmett2"},
            "metadata": {"previous": "../martingales/index.html"},
            "scope_note": "brown-index-edition-scope",
        },
    }
    for relative, expected in overview_expectations.items():
        overview_path = site / relative
        overview_soup = BeautifulSoup(overview_path.read_text("utf-8"), "lxml")
        observed_ids = {
            str(node.get("id")) for node in overview_soup.select("[id]")
        }
        if not expected["ids"].issubset(observed_ids):
            raise RuntimeError(
                f"overview page lost selected source ids: {relative}: "
                f"{sorted(expected['ids'] - observed_ids)}"
            )
        for relation, href in expected["metadata"].items():
            links = overview_soup.select(f'head link[rel~="{relation}"]')
            if len(links) != 1 or str(links[0].get("href", "")) != href:
                raise RuntimeError(
                    f"overview sequential metadata mismatch: {relative} {relation}"
                )
        scope_note = expected["scope_note"]
        if scope_note is not None and len(overview_soup.select(f"#{scope_note}")) != 1:
            raise RuntimeError(f"overview scope note missing or duplicated: {relative}")
    brown_index_soup = BeautifulSoup(
        (site / "brown" / "index.html").read_text("utf-8"), "lxml"
    )
    absolute_brownian_href = (
        "https://www.randomservices.org/random/apps/AbsoluteBrownianMotion.html"
    )
    if len(
        brown_index_soup.select(
            f'a[href="{absolute_brownian_href}"]'
        )
    ) != 1:
        raise RuntimeError("Brown overview absolute-motion application link was not repaired")
    css_paths = sorted(
        (site / str(row["path"]) for row in actual if str(row["path"]).endswith(".css")),
        key=lambda path: path.as_posix().casefold(),
    )
    for css_path in css_paths:
        css_text = css_path.read_text("utf-8")
        for _, ref in CSS_URL_RE.findall(css_text):
            parsed = urllib.parse.urlparse(ref.strip())
            if not parsed.path or parsed.scheme or ref.startswith("data:"):
                continue
            target = (css_path.parent / urllib.parse.unquote(parsed.path)).resolve()
            try:
                target.relative_to(site.resolve())
            except ValueError as exc:
                raise RuntimeError(f"CSS reference escapes site: {css_path} -> {ref}") from exc
            if not target.is_file():
                raise RuntimeError(f"missing CSS asset: {css_path} -> {ref}")
            if target.is_symlink():
                raise RuntimeError(f"linked CSS asset: {css_path} -> {ref}")
    receipt_labs = {str(item["chunk_id"]): item for item in receipt["lab_sources"]}
    for spec in LAB_SPECS:
        lab_html = site / Path(spec["output"])
        lab_text = lab_html.read_text("utf-8")
        lab_soup = BeautifulSoup(lab_text, "lxml")
        executable = lab_soup.find(id=str(spec["chunk_id"]))
        if executable is None or executable.name not in {"div", "pre", "code"}:
            raise RuntimeError(f"rendered lab lacks stable code-block id: {spec['chunk_id']}")
        code = executable.find("code") if executable.name != "code" else executable
        if code is None or str(spec["required_code"]) not in code.get_text():
            raise RuntimeError(f"rendered lab R code is not copyable: {spec['chunk_id']}")
        if (
            "```{r" in lab_text
            or ">true<" in lab_text
            or str(spec["placeholder"]) in lab_text
        ):
            raise RuntimeError(f"raw R fence or malformed metadata leaked: {spec['chunk_id']}")
        table = lab_soup.find("table", id=str(spec["table_id"]))
        if table is None:
            raise RuntimeError(f"rendered lab result table lacks its stable id: {spec['chunk_id']}")
        headers = [cell.get_text(" ", strip=True) for cell in table.select("thead th")]
        if headers != list(spec["table_headers"]):
            raise RuntimeError(f"rendered lab table headers differ: {spec['chunk_id']}")
        rendered_rows = [
            [cell.get_text(" ", strip=True) for cell in row.select("td")]
            for row in table.select("tbody tr")
        ]
        expected_rows = [
            [row[field] for field in spec["expected_fields"]]
            for row in receipt_labs[str(spec["chunk_id"])]["r_result_rows"]
        ]
        if rendered_rows != expected_rows:
            raise RuntimeError(f"rendered lab table rows differ: {spec['chunk_id']}")
        navs = lab_soup.select('nav[aria-label="Navigasi edisi"]')
        if len(navs) != 1:
            raise RuntimeError(f"rendered lab navigation is not exact-once: {spec['chunk_id']}")
        nav_hrefs = [str(anchor.get("href", "")) for anchor in navs[0].select("a[href]")]
        expected_nav = [href for href, _ in lab_navigation(spec)]
        if nav_hrefs != expected_nav:
            raise RuntimeError(f"rendered lab navigation differs: {spec['chunk_id']}")
    theory_text = "\n".join((site / str(unit["rel"])).read_text("utf-8") for unit in THEORY_UNITS)
    boldsymbol_target = site / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js"
    if "\\boldsymbol" in theory_text and not boldsymbol_target.is_file():
        raise RuntimeError("required MathJax boldsymbol autoload extension is missing")
    brown_path = site / "brown" / "Standard.html"
    brown_text = brown_path.read_text("utf-8")
    brown_soup = BeautifulSoup(brown_text, "lxml")
    if len(brown_soup.select("div.unit")) != 50:
        raise RuntimeError("Brown Standard reader must preserve all 50 source units")
    if len(brown_soup.find_all("details")) != 30 or len(brown_soup.find_all("summary")) != 30:
        raise RuntimeError("Brown Standard reader must contain 28 source disclosures and two additive disclosures")
    for required_id in (
        "app",
        "brown-standard-downstream-corrections",
        "brown-standard-exercise-solution",
        "lil1-consequence",
    ):
        if brown_soup.find(id=required_id) is None:
            raise RuntimeError(f"Brown Standard reader closure missing: {required_id}")
    if len(brown_soup.select("#brown-standard-exercise-solution details")) != 1:
        raise RuntimeError("Brown Standard original exercise solution is not structurally complete")
    brown_app_links = brown_soup.select(
        'p.app a[href^="https://www.randomservices.org/random/apps/"]'
    )
    if len(brown_app_links) != 12 or any(
        "resmi daring" not in anchor.get_text(" ", strip=True)
        for anchor in brown_app_links
    ):
        raise RuntimeError("Brown Standard external app prompts are not all explicitly online")
    if [str(script.get("src", "")) for script in brown_soup.select("script[src]")].count(
        "../apps/Apps.js"
    ) != 1 or [
        str(script.get("src", "")) for script in brown_soup.select("script[src]")
    ].count("../apps/Distributions.js") != 1:
        raise RuntimeError("Brown Standard offline simulator scripts are not exact-once")
    for asset, expected_hash in (
        (site / "apps" / "Apps.js", "a983fd231b3e5924ca46a80ef25ad614d84c70f5da933f90c698bd342ddf9d22"),
        (site / "apps" / "Distributions.js", "bcf0e7266ff22890e23e577bdb37328233c1df9410ac2dc77a4075f0a3beeb0a"),
    ):
        if sha256(require_file(asset)) != expected_hash:
            raise RuntimeError(f"Brown Standard offline simulator asset drift: {asset.name}")
    required_brown_witnesses = (
        'control.button.setAttribute("aria-label", label)',
        'this.graph.svg.setAttribute("role", "img")',
        r"e^{t u^2 / 2}",
        r"\max\{X_s:0\le s\le t\}",
        r"\var(Z_t) = t^2 / 8",
        r"\liminf_{t\to\infty}",
        r"\inf\varnothing=\infty",
        r"\P(\tau\lt\infty)=1",
        r"\mathscr F_s\)",
        r"\sigma=\tau_y\wedge t",
        r"\P(\sigma_q\lt\infty)=1",
        r"tidak ada nol dalam \((s,t]\)",
        r"Dengan probabilitas 1, \(Z\) mempunyai dimensi Hausdorff",
        "solusi asli edisi ini",
    )
    missing_brown_witnesses = [
        witness for witness in required_brown_witnesses if witness not in brown_text
    ]
    if missing_brown_witnesses:
        raise RuntimeError(
            f"Brown Standard corrected reader witnesses missing: {missing_brown_witnesses}"
        )
    forbidden_brown_witnesses = (
        r"\5",
        r"\lef[",
        r"\text{ for all }",
        r"\text{ for some }",
        r"e^{t u / 2}",
        r'href="#max3"',
        "proses Markov homogen-waktu",
        "inkremen stasioner dan saling bebas",
        "jalan acak",
        r"parameter skala \( t \)",
        r"\E(Z_t) = t^2 / 8",
        r"s \mapsto X(\tau_y + s) - y",
        r"kejadian \( Z_t \le s \) sama dengan",
    )
    brown_hits = [value for value in forbidden_brown_witnesses if value in brown_text]
    if brown_hits:
        raise RuntimeError(f"Brown Standard stale authority defects remain: {brown_hits}")
    if brown_text.count(r"\(") != brown_text.count(r"\)"):
        raise RuntimeError("Brown Standard inline TeX delimiters are unbalanced downstream")
    if brown_text.count(r"\[") != brown_text.count(r"\]"):
        raise RuntimeError("Brown Standard display TeX delimiters are unbalanced downstream")
    if brown_text.count(r"\begin{align}") != brown_text.count(r"\end{align}"):
        raise RuntimeError("Brown Standard align environments are unbalanced downstream")
    drift_path = site / "brown" / "Drift.html"
    drift_text = drift_path.read_text("utf-8")
    drift_soup = BeautifulSoup(drift_text, "lxml")
    if len(drift_soup.select("div.unit")) != 11:
        raise RuntimeError("Brown Drift reader must preserve all 11 active source units")
    if len(drift_soup.find_all("details")) != 10 or len(drift_soup.find_all("summary")) != 10:
        raise RuntimeError(
            "Brown Drift reader must contain seven source disclosures and three additive disclosures"
        )
    for required_id in (
        "brown-drift-downstream-corrections",
        "brown-drift-offline-lab",
        "brown-drift-chart",
        "brown-drift-status",
        "brown-drift-mastery",
        "brown-drift-mastery-exercise",
        "brown-drift-mastery-hint",
        "brown-drift-mastery-solution",
        "brown-drift-strong-markov-proof",
    ):
        if drift_soup.find(id=required_id) is None:
            raise RuntimeError(f"Brown Drift reader closure missing: {required_id}")
    drift_app_links = drift_soup.select(
        'p.app a[href="https://www.randomservices.org/random/apps/DriftBrownianMotion.html"]'
    )
    if len(drift_app_links) != 1 or "resmi daring" not in drift_app_links[0].get_text(
        " ", strip=True
    ):
        raise RuntimeError("Brown Drift retained Random app is not explicit and exact-once")
    if [str(script.get("src", "")) for script in drift_soup.select("script[src]")].count(
        "../apps/brown-drift-offline.js"
    ) != 1:
        raise RuntimeError("Brown Drift offline simulator script is not exact-once")
    drift_app_asset = site / "apps" / "brown-drift-offline.js"
    if sha256(require_file(drift_app_asset)) != (
        "e4d64c98b1fa3fc7d1511c00a6b4385beb4079615c1217d74c0a0221ca310a1f"
    ):
        raise RuntimeError("Brown Drift offline simulator asset drift")
    if len(drift_soup.select("#brown-drift-offline-lab input")) != 6:
        raise RuntimeError("Brown Drift offline simulator parameter closure differs")
    if len(drift_soup.select("#brown-drift-offline-lab button")) != 2:
        raise RuntimeError("Brown Drift offline simulator action closure differs")
    required_drift_witnesses = (
        r"t_2 \lt \cdots \lt t_n",
        r"\sigma\sqrt{s}\,\sigma\sqrt{t}",
        r"(s, t) \in (0, \infty)^2",
        r"\mathscr F_\infty=\sigma(\bigcup_{t\ge0}\mathscr F_t)",
        r"\P(\tau\lt\infty)=1",
        r"\tau_n=2^{-n}\lceil2^n\tau\rceil\downarrow\tau",
        "tidak ada penskalaan nontrivial",
        "parameter hanyutan dan skala yang sama",
        "karya asli edisi ini, dilisensikan CC BY 4.0",
        r"X_{5/2}\mid X_1=x_2",
        "brown-drift-offline.js",
    )
    missing_drift_witnesses = [
        witness for witness in required_drift_witnesses if witness not in drift_text
    ]
    if missing_drift_witnesses:
        raise RuntimeError(
            f"Brown Drift corrected reader witnesses missing: {missing_drift_witnesses}"
        )
    forbidden_drift_witnesses = (
        r"t_2 \cdots \lt t_n",
        r"\sigma s \sigma t",
        r"\frac{\min\{s, t\}}{s t}",
        r"(s, t) \in [0, \infty)^2 \]</p>",
        "Kedua syarat tersebut tidak dapat dipenuhi sekaligus",
        "merupakan gerak Brown standar lain",
        r"B \in \mathscr{F}:",
        r"\text{ for all }",
    )
    drift_hits = [value for value in forbidden_drift_witnesses if value in drift_text]
    if drift_hits:
        raise RuntimeError(f"Brown Drift stale authority defects remain: {drift_hits}")
    if drift_text.count(r"\(") != drift_text.count(r"\)"):
        raise RuntimeError("Brown Drift inline TeX delimiters are unbalanced downstream")
    if drift_text.count(r"\[") != drift_text.count(r"\]"):
        raise RuntimeError("Brown Drift display TeX delimiters are unbalanced downstream")
    if drift_text.count(r"\begin{align}") != drift_text.count(r"\end{align}"):
        raise RuntimeError("Brown Drift align environments are unbalanced downstream")
    bridge_path = site / "brown" / "Bridge.html"
    bridge_text = bridge_path.read_text("utf-8")
    bridge_soup = BeautifulSoup(bridge_text, "lxml")
    if len(bridge_soup.select("div.unit")) != 13:
        raise RuntimeError("Brown Bridge reader must preserve all 13 source units")
    if len(bridge_soup.find_all("details")) != 9 or len(bridge_soup.find_all("summary")) != 9:
        raise RuntimeError(
            "Brown Bridge reader must contain seven source disclosures and two additive disclosures"
        )
    for required_id in (
        "brown-bridge-downstream-corrections",
        "brown-bridge-offline-lab",
        "brown-bridge-chart",
        "brown-bridge-status",
        "brown-bridge-mastery",
        "brown-bridge-process-limit-warning",
        "brown-bridge-mastery-exercise",
        "brown-bridge-mastery-hint",
        "brown-bridge-mastery-solution",
    ):
        if bridge_soup.find(id=required_id) is None:
            raise RuntimeError(f"Brown Bridge reader closure missing: {required_id}")
    bridge_app_links = bridge_soup.select(
        'p.app a[href="https://www.randomservices.org/random/apps/BrownianBridge.html"]'
    )
    if len(bridge_app_links) != 2 or any(
        "resmi daring" not in anchor.get_text(" ", strip=True)
        for anchor in bridge_app_links
    ):
        raise RuntimeError("Brown Bridge retained Random apps are not explicit and exact-twice")
    if [str(script.get("src", "")) for script in bridge_soup.select("script[src]")].count(
        "../apps/brown-bridge-offline.js"
    ) != 1:
        raise RuntimeError("Brown Bridge offline simulator script is not exact-once")
    bridge_app_asset = site / "apps" / "brown-bridge-offline.js"
    if sha256(require_file(bridge_app_asset)) != (
        "2c3a29ab169b538a54dd77e1813f95c06a68face108eb386723a84a514387f2b"
    ):
        raise RuntimeError("Brown Bridge offline simulator asset drift")
    if len(bridge_soup.select("#brown-bridge-offline-lab input")) != 4:
        raise RuntimeError("Brown Bridge offline simulator parameter closure differs")
    if len(bridge_soup.select("#brown-bridge-offline-lab button")) != 2:
        raise RuntimeError("Brown Bridge offline simulator action closure differs")
    required_bridge_witnesses = (
        "3. Jembatan Brown",
        r"\E(X_t) = \E(Z_t) - t \E(Z_1)",
        r"t \in [0, 1)",
        r"s, \, t \in [0, \infty)",
        r"\P(X_1=0)=0",
        "hukum kondisional reguler",
        r"d X_t = -\frac{X_t}{1 - t}",
        "konsistensi kuadrat-rataan",
        r"\cov\left[\bs{1}(T_i \le s), \bs{1}(T_j \le t)\right]",
        "Teorema Donsker",
        r"X_t\mid X_s=x\sim N",
        "karya asli edisi ini, dilisensikan CC BY 4.0",
        "brown-bridge-offline.js",
    )
    missing_bridge_witnesses = [
        witness for witness in required_bridge_witnesses if witness not in bridge_text
    ]
    if missing_bridge_witnesses:
        raise RuntimeError(
            f"Brown Bridge corrected reader witnesses missing: {missing_bridge_witnesses}"
        )
    forbidden_bridge_witnesses = (
        "5. Jembatan Brown",
        r"\( E(X_t) = \E(Z_t)",
        "1 - \tt",
        r"d X_t = \frac{X_t}{1 - t}",
        r"\cov\left[\bs{1}(T_i \le s) \bs{1}(T_j \le t)\right]",
    )
    bridge_hits = [value for value in forbidden_bridge_witnesses if value in bridge_text]
    if bridge_hits:
        raise RuntimeError(f"Brown Bridge stale authority defects remain: {bridge_hits}")
    if bridge_text.count(r"\(") != bridge_text.count(r"\)"):
        raise RuntimeError("Brown Bridge inline TeX delimiters are unbalanced downstream")
    if bridge_text.count(r"\[") != bridge_text.count(r"\]"):
        raise RuntimeError("Brown Bridge display TeX delimiters are unbalanced downstream")
    geometric_path = site / "brown" / "Geometric.html"
    geometric_text = geometric_path.read_text("utf-8")
    geometric_soup = BeautifulSoup(geometric_text, "lxml")
    if len(geometric_soup.select("div.unit")) != 14:
        raise RuntimeError("Brown Geometric reader must preserve all 14 source units")
    if (
        len(geometric_soup.find_all("details")) != 8
        or len(geometric_soup.find_all("summary")) != 8
    ):
        raise RuntimeError(
            "Brown Geometric reader must contain six source disclosures and two additive disclosures"
        )
    for required_id in (
        "geometric-brownian-downstream-corrections",
        "geometric-brownian-offline-lab",
        "geometric-brownian-chart",
        "geometric-brownian-status",
        "geometric-brownian-theoretical-mean",
        "geometric-brownian-empirical-mean",
        "geometric-brownian-theoretical-median",
        "geometric-brownian-empirical-median",
        "geometric-brownian-theoretical-variance",
        "geometric-brownian-empirical-variance",
        "geometric-brownian-theoretical-probability",
        "geometric-brownian-empirical-probability",
        "geometric-brownian-mastery",
        "geometric-brownian-mastery-exercise",
        "geometric-brownian-mastery-hint",
        "geometric-brownian-mastery-solution",
        "dst4",
        "prp2",
    ):
        if geometric_soup.find(id=required_id) is None:
            raise RuntimeError(f"Brown Geometric reader closure missing: {required_id}")
    geometric_app_links = geometric_soup.select(
        'p.app a[href="https://www.randomservices.org/random/apps/GeometricBrownianMotion.html"]'
    )
    if len(geometric_app_links) != 4 or any(
        "resmi daring" not in anchor.get_text(" ", strip=True)
        for anchor in geometric_app_links
    ):
        raise RuntimeError(
            "Brown Geometric retained Random apps are not explicit and exact-four"
        )
    if [
        str(script.get("src", "")) for script in geometric_soup.select("script[src]")
    ].count("../apps/geometric-brownian-offline.js") != 1:
        raise RuntimeError("Brown Geometric offline simulator script is not exact-once")
    geometric_app_asset = site / "apps" / "geometric-brownian-offline.js"
    if sha256(require_file(geometric_app_asset)) != (
        "5b18869f5582f354c40fbf6a9987a191450e09d93b21891d9838251b4a3ed8a8"
    ):
        raise RuntimeError("Brown Geometric offline simulator asset drift")
    if len(geometric_soup.select("#geometric-brownian-offline-lab input")) != 7:
        raise RuntimeError("Brown Geometric offline simulator parameter closure differs")
    if len(geometric_soup.select("#geometric-brownian-offline-lab button")) != 2:
        raise RuntimeError("Brown Geometric offline simulator action closure differs")
    if len(geometric_soup.select("#geometric-brownian-offline-lab tbody tr")) != 4:
        raise RuntimeError("Brown Geometric accessible output table closure differs")
    geometric_js_text = geometric_app_asset.read_text("utf-8")
    required_geometric_js_witnesses = (
        "function seededRandom(seed)",
        "function normalCdf(x)",
        "value *= Math.exp(logDrift + logScale * standardNormal(random));",
        "geometric-brownian-theoretical-median",
        "geometric-brownian-theoretical-probability",
        "meanPoints",
        "medianPoints",
        "Selesai:",
    )
    missing_geometric_js_witnesses = [
        witness
        for witness in required_geometric_js_witnesses
        if witness not in geometric_js_text
    ]
    if missing_geometric_js_witnesses:
        raise RuntimeError(
            "Brown Geometric offline simulator witnesses missing: "
            f"{missing_geometric_js_witnesses}"
        )
    if any(value in geometric_js_text for value in ("fetch(", "XMLHttpRequest", "WebSocket")):
        raise RuntimeError("Brown Geometric offline simulator has a network dependency")
    required_geometric_witnesses = (
        "4. Gerak Brown Geometrik",
        r"(\mu - 2\sigma^2) t",
        r"\(F_t(x)=0\)",
        r"n\in\N_+",
        r"\log(X_t)/t",
        r"\limsup_{t\to\infty}X_t=\infty",
        r"\E\!\left(\int_0^t \sigma^2X_s^2\,ds\right)",
        r"\E(X_t\mid\mathscr F_s)=X_s e^{\mu\Delta}",
        r"M_t=e^{-\mu t}X_t",
        "karya asli edisi ini, dilisensikan CC BY 4.0",
        "geometric-brownian-offline.js",
    )
    missing_geometric_witnesses = [
        witness
        for witness in required_geometric_witnesses
        if witness not in geometric_text
    ]
    if missing_geometric_witnesses:
        raise RuntimeError(
            f"Brown Geometric corrected reader witnesses missing: {missing_geometric_witnesses}"
        )
    forbidden_geometric_witnesses = (
        "6. Gerak Brown Geometrik",
        r"(\mu - \sigma^2) t \pm",
        'id="dist4"',
        r"\( f \) meningkat lalu menurun",
        r"\( f \) mula-mula cekung ke atas",
        "Ditinjau dari orde momen",
        "mendominasi suku",
        "dengan asumsi-asumsi lazim",
    )
    geometric_hits = [
        value for value in forbidden_geometric_witnesses if value in geometric_text
    ]
    if geometric_hits:
        raise RuntimeError(
            f"Brown Geometric stale authority defects remain: {geometric_hits}"
        )
    if geometric_text.count(r"\(") != geometric_text.count(r"\)"):
        raise RuntimeError("Brown Geometric inline TeX delimiters are unbalanced downstream")
    if geometric_text.count(r"\[") != geometric_text.count(r"\]"):
        raise RuntimeError("Brown Geometric display TeX delimiters are unbalanced downstream")
    joined = b"\n".join((site / str(row["path"])).read_bytes() for row in actual)
    forbidden = (b"googletagmanager", b"C:\\Users\\", b"C:/Users/")
    profile_leaf = Path.home().name.encode("utf-8")
    if profile_leaf:
        forbidden += (profile_leaf,)
    hits = [value.decode("ascii") for value in forbidden if value in joined]
    if hits:
        raise RuntimeError(f"privacy/runtime residue in site: {hits}")
    if execute_r:
        for spec in LAB_SPECS:
            with tempfile.TemporaryDirectory(prefix="o009-check-") as temp:
                _, rows = extract_and_run_lab(Path(temp), spec)
            recorded = receipt_labs.get(str(spec["chunk_id"]), {}).get("r_result_rows")
            if rows != recorded:
                raise RuntimeError(f"fresh R execution differs: {spec['chunk_id']}")


def build() -> None:
    validate_lab_specs()
    runtime_evidence()
    validate_theory_translation()
    validate_original_bridge_specs()
    ROOT.joinpath("build").mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="o009-first-boundary-", dir=ROOT / "build"))
    try:
        lab_results: list[dict[str, object]] = []
        with tempfile.TemporaryDirectory(prefix="o009-r-") as temp:
            for spec in LAB_SPECS:
                lab_text, rows = extract_and_run_lab(Path(temp), spec)
                lab_results.append({"text": lab_text, "rows": rows})
        copy_assets(stage)
        build_theory(stage)
        build_original_bridges(stage)
        build_supplements(stage)
        for index, (spec, result) in enumerate(zip(LAB_SPECS, lab_results, strict=True), start=1):
            processed_lab = stage / f"lab-build-input-{index:02d}.md"
            source_text = str(result["text"])
            rows = result["rows"]
            processed_lab.write_text(
                pandoc_lab_text(
                    source_text.replace(str(spec["placeholder"]), markdown_table(rows, spec)),
                    spec,
                ),
                encoding="utf-8",
                newline="\n",
            )
            lab_output = stage / Path(spec["output"])
            lab_output.parent.mkdir(parents=True, exist_ok=True)
            run_pandoc(processed_lab, lab_output, "../reader.css", "../MathJax/tex-svg.js")
            decorate_lab_output(lab_output, spec)
            processed_lab.unlink()
        quantecon_component = copy_quantecon_component(stage)
        quantecon_poisson_component = copy_quantecon_poisson_component(stage)
        quantecon_markov_prop_component = copy_quantecon_markov_prop_component(stage)
        quantecon_kolmogorov_bwd_component = copy_quantecon_kolmogorov_bwd_component(stage)
        quantecon_kolmogorov_fwd_component = copy_quantecon_kolmogorov_fwd_component(stage)
        quantecon_generators_component = copy_quantecon_generators_component(stage)
        quantecon_uc_mc_semigroups_component = (
            copy_quantecon_uc_mc_semigroups_component(stage)
        )
        quantecon_ergodicity_component = copy_quantecon_ergodicity_component(stage)
        run_pandoc(SOURCE_INDEX, stage / "index.html", "reader.css")
        decorate_index_output(stage / "index.html")
        synchronize_shared_reader_stylesheet(stage)
        version_reader_stylesheet_links(stage)
        write_manifest(
            stage,
            lab_results,
            quantecon_component,
            quantecon_poisson_component,
            quantecon_markov_prop_component,
            quantecon_kolmogorov_bwd_component,
            quantecon_kolmogorov_fwd_component,
            quantecon_generators_component,
            quantecon_uc_mc_semigroups_component,
            quantecon_ergodicity_component,
        )
        verify_site(stage)
        site_resolved = SITE.resolve()
        build_resolved = (ROOT / "build").resolve()
        try:
            site_resolved.relative_to(build_resolved)
        except ValueError as exc:
            raise RuntimeError("site target escapes build directory") from exc
        if SITE.exists():
            if SITE.is_symlink():
                raise RuntimeError("refusing to replace linked site directory")
            try:
                shutil.rmtree(SITE)
            except PermissionError:
                # Windows can keep the directory handle open briefly after the
                # bounded preview server exits even though every child was
                # removed.  The already verified stage can still be copied
                # losslessly into that exact, demonstrably empty directory.
                if any(SITE.iterdir()):
                    raise
                shutil.copytree(stage, SITE, dirs_exist_ok=True)
                shutil.rmtree(stage)
            else:
                os.replace(stage, SITE)
        else:
            os.replace(stage, SITE)
        verify_site(SITE)
        receipt = json.loads((SITE / "BUILD_RECEIPT.json").read_text("utf-8"))
        print(
            f"PASS files={receipt['file_count']} bytes={receipt['total_bytes']} "
            f"manifest_sha256={receipt['manifest_sha256']}"
        )
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate_lab_specs()
        runtime_evidence()
        validate_theory_translation()
        validate_original_bridge_specs()
        verify_site(SITE)
        receipt = json.loads((SITE / "BUILD_RECEIPT.json").read_text("utf-8"))
        print(
            f"PASS files={receipt['file_count']} bytes={receipt['total_bytes']} "
            f"manifest_sha256={receipt['manifest_sha256']}"
        )
    else:
        build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
