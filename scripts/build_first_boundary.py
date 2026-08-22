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
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
AUTH_RANDOM = ROOT / "authority" / "random"
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
)
LAB_SOURCE = LAB_SPECS[0]["source"]
SOURCE_INDEX = ROOT / "source" / "index.md"
SOURCE_CSS = ROOT / "source" / "reader.css"
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
<p>Tetapkan \( t \in T \). Keterukuran \( x \mapsto \P(X_t \in A \mid X_0 = x) \) untuk \( A \in \mathscr{S} \) sudah tercakup dalam definisi probabilitas bersyarat. Selain itu, tentu saja, \( A \mapsto \P(X_t \in A \mid X_0 = x) \) merupakan ukuran probabilitas pada \( \mathscr{S} \) untuk \( x \in S \). Secara umum, distribusi bersyarat satu variabel acak, dengan syarat nilai variabel acak lain, mendefinisikan kernel probabilitas.</p>
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
<p class="math">Misalkan \( \bs{X} = \{X_t: t \in T\} \) adalah proses Markov takhomogen dengan ruang keadaan \( (S, \mathscr{S}) \). Misalkan pula bahwa \( \tau \) adalah variabel acak yang mengambil nilai dalam \( T \), independen dari \( \bs{X} \). Misalkan \( \tau_t = \tau + t \) dan \( Y_t = \left(X_{\tau_t}, \tau_t\right) \) untuk \( t \in T \). Maka \( \bs{Y} = \{Y_t: t \in T\} \) adalah proses Markov homogen dengan ruang keadaan \( (S \times T, \mathscr{S} \otimes \mathscr{T}) \). Untuk \( t \in T \), kernel transisi \( P_t \) diberikan oleh
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
        "old": r"Kita hanya perlu menunjukkan bahwa \( \{g_t: t \in [0, \infty)\} \) memenuhi sifat semigrup dan bahwa hasil kontinuitas berlaku. Namun, kita sudah mengetahui bahwa jika \( U, \, V \) adalah variabel independen yang masing-masing berdistribusi normal",
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
)
MATH_SURFACE_RE = re.compile(
    r"\\\(.*?\\\)|\\\[.*?\\\]|"
    r"\\begin\{(?P<environment>[A-Za-z]+\*?)\}.*?\\end\{(?P=environment)\}",
    re.DOTALL,
)
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.I)
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
    source_math = [match.group(0) for match in MATH_SURFACE_RE.finditer(source_text)]
    target_math = [match.group(0) for match in MATH_SURFACE_RE.finditer(target_text)]
    if source_math != target_math:
        raise RuntimeError(f"translated theory TeX surface differs: {unit['rel']}")
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
    for row in rows:
        for key in expected_fields:
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
    output.write_text(str(soup), encoding="utf-8", newline="\n")


def build_theory_unit(stage: Path, unit: dict[str, object]) -> None:
    _, target_path = theory_paths(unit)
    rel = Path(str(unit["rel"]))
    base_url = urllib.parse.urljoin(RANDOM_BASE_URL, rel.as_posix())
    soup = BeautifulSoup(require_file(target_path).decode("utf-8"), "lxml")
    mathjax = soup.find("script", id="MathJax-script")
    if mathjax is None:
        raise RuntimeError("MathJax script marker missing")
    mathjax["src"] = "../MathJax/tex-svg.js"
    extra_css = soup.new_tag("link", rel="stylesheet", href="../reader.css")
    soup.head.append(extra_css)
    local_pages = {
        urllib.parse.urljoin(RANDOM_BASE_URL, Path(str(item["rel"])).as_posix()): Path(str(item["rel"]))
        for item in THEORY_UNITS
    }
    for metadata_link in soup.select("link[href]"):
        rel_values = {str(value).lower() for value in (metadata_link.get("rel") or [])}
        if rel_values & {"stylesheet", "icon"}:
            continue
        href = str(metadata_link.get("href", ""))
        if href and not urllib.parse.urlparse(href).scheme:
            metadata_link["href"] = urllib.parse.urljoin(base_url, href)
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
        if rendered.count(old) != 1:
            raise RuntimeError(
                f"reader correction {correction['id']} matched "
                f"{rendered.count(old)} times in {unit['rel']}"
            )
        rendered = rendered.replace(old, new, 1)
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
        "--from=markdown+fenced_divs+fenced_code_attributes+yaml_metadata_block",
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


def copy_assets(stage: Path) -> None:
    mappings = {
        AUTH_RANDOM / "static" / "Screen.css": stage / "Screen.css",
        AUTH_RANDOM / "static" / "Basic.js": stage / "Basic.js",
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
        AUTH_RANDOM / "shared" / "MathJax" / "tex-svg.js": stage / "MathJax" / "tex-svg.js",
        AUTH_RANDOM / "shared" / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js": (
            stage / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js"
        ),
        AUTH_RANDOM / "shared" / "MathJax" / "LICENSE": stage / "licenses" / "MathJax-Apache-2.0.txt",
        SOURCE_CSS: stage / "reader.css",
    }
    if sha256(require_file(AUTH_RANDOM / "shared" / "MathJax" / "tex-svg.js")) != MATHJAX_SHA256:
        raise RuntimeError("MathJax hash changed")
    boldsymbol = AUTH_RANDOM / "shared" / "MathJax" / "input" / "tex" / "extensions" / "boldsymbol.js"
    if sha256(require_file(boldsymbol)) != MATHJAX_BOLDSYMBOL_SHA256:
        raise RuntimeError("MathJax boldsymbol extension hash changed")
    for source, target in mappings.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


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


def write_manifest(site: Path, lab_results: list[dict[str, object]]) -> None:
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
    receipt = {
        "schema": BUILD_RECEIPT_SCHEMA,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_authority_manifest_sha256": RANDOM_MANIFEST_SHA256,
        "theory_units": [
            {
                "path": str(unit["rel"]),
                "authority_sha256": str(unit["authority_sha256"]),
                "target_sha256": sha256(require_file(theory_paths(unit)[1])),
            }
            for unit in THEORY_UNITS
        ],
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


def verify_site(site: Path, execute_r: bool = True) -> None:
    validate_lab_specs()
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
    for path in html_paths:
        data = path.read_bytes()
        text = data.decode("utf-8")
        soup = BeautifulSoup(text, "lxml")
        if soup.html is None or soup.html.get("lang") != "id-ID":
            raise RuntimeError(f"missing lang=id-ID: {path}")
        ids = [str(tag["id"]) for tag in soup.select("[id]")]
        if len(ids) != len(set(ids)):
            raise RuntimeError(f"duplicate id: {path}")
        for tag in soup.select("a[href], img[src], script[src], link[href]"):
            attribute = "href" if tag.has_attr("href") else "src"
            ref = str(tag.get(attribute, ""))
            parsed = urllib.parse.urlparse(ref)
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
    index_soup = BeautifulSoup((site / "index.html").read_text("utf-8"), "lxml")
    index_hrefs = [str(anchor.get("href", "")) for anchor in index_soup.select("a[href]")]
    required_index_links = [str(unit["rel"]) for unit in THEORY_UNITS]
    required_index_links.extend(Path(spec["output"]).as_posix() for spec in LAB_SPECS)
    missing_index_links = [href for href in required_index_links if index_hrefs.count(href) != 1]
    if missing_index_links:
        raise RuntimeError(
            f"reader index must link every admitted unit exactly once: {missing_index_links}"
        )
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
    joined = b"\n".join((site / str(row["path"])).read_bytes() for row in actual)
    forbidden = (b"googletagmanager", b"C:\\Users\\", b"C:/Users/", b"Floris")
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
        run_pandoc(SOURCE_INDEX, stage / "index.html", "reader.css")
        write_manifest(stage, lab_results)
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
            shutil.rmtree(SITE)
        os.replace(stage, SITE)
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
