#!/usr/bin/env python3
"""Deterministic numerical QA for the UC Markov-semigroup unit."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = (
    ROOT
    / "authority"
    / "quantecon"
    / "source_snapshot"
    / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
    / "lectures"
    / "uc_mc_semigroups.md"
)
TARGET = ROOT / "source" / "quantecon" / "lectures" / "uc_mc_semigroups.md"
RUNTIME_LOCK = ROOT / "00_control" / "RUNTIME_LOCK.json"
OUTPUT = ROOT / "qa" / "QUANTECON_UC_MC_SEMIGROUPS_NUMERICAL_QA.json"

AUTHORITY_SHA = "cb5e67bc9a614a0169ba9b9bee479a0060b88401e0a7442154242af7bffd9b69"
TARGET_SHA = "85dfca4029539025d63721950c74a03dab82c89e0841e3f91b0e7f426fab01f2"
ATOL = 1.0e-12


def sha256(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"missing or linked regular file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError(f"nonfinite QA value: {result}")
    return result


def maximum_abs(value: np.ndarray) -> float:
    return finite(np.max(np.abs(value)))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_decomposition(q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rates = -np.diag(q).copy()
    kernel = np.zeros_like(q)
    for x, rate in enumerate(rates):
        if rate > 0.0:
            kernel[x] = q[x] / rate
            kernel[x, x] += 1.0
        else:
            kernel[x, x] = 1.0
    return rates, kernel


def uniformized(t: float, q: np.ndarray, rate: float, terms: int) -> np.ndarray:
    kernel = np.eye(q.shape[0]) + q / rate
    result = np.zeros_like(q)
    power = np.eye(q.shape[0])
    weight = math.exp(-rate * t)
    result += weight * power
    for n in range(1, terms):
        power = power @ kernel
        weight *= rate * t / n
        result += weight * power
    return result


def main() -> int:
    require(sha256(AUTHORITY) == AUTHORITY_SHA, "authority hash differs")
    require(sha256(TARGET) == TARGET_SHA, "target hash differs")

    runtime_lock = json.loads(RUNTIME_LOCK.read_text(encoding="utf-8"))
    replay_rel = runtime_lock["python_quantecon"]["offline_replay"]["path"]
    runtime = Path(replay_rel)
    if not runtime.is_absolute():
        runtime = ROOT / runtime
    runtime_python = runtime / "Scripts" / "python.exe" if runtime.is_dir() else runtime
    require(runtime_python.resolve() == Path(sys.executable).resolve(), "unpinned interpreter")

    q = np.array(
        [
            [-3.0, 1.0, 2.0, 0.0],
            [0.5, -2.0, 1.5, 0.0],
            [0.0, 0.0, -1.0, 1.0],
            [0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    row_sum_residual = maximum_abs(q.sum(axis=1))
    off_diagonal = q.copy()
    np.fill_diagonal(off_diagonal, 0.0)
    off_diagonal_minimum = finite(off_diagonal.min())
    diagonal_maximum = finite(np.diag(q).max())
    operator_norm = finite(np.max(np.sum(np.abs(q), axis=1)))
    max_exit_rate = finite(np.max(-np.diag(q)))
    operator_norm_identity_residual = abs(operator_norm - 2.0 * max_exit_rate)
    require(row_sum_residual <= ATOL, "fixture row sums differ")
    require(off_diagonal_minimum >= -ATOL, "fixture has negative off-diagonal entry")
    require(diagonal_maximum <= ATOL, "fixture has positive diagonal entry")
    require(operator_norm_identity_residual <= ATOL, "ell_1 operator-norm identity differs")

    rates, kernel = canonical_decomposition(q)
    reconstruction = np.diag(rates) @ (kernel - np.eye(q.shape[0]))
    decomposition_residual = maximum_abs(reconstruction - q)
    kernel_row_sum_residual = maximum_abs(kernel.sum(axis=1) - 1.0)
    kernel_minimum = finite(kernel.min())
    canonical_diagonal_residual = max(
        abs(float(kernel[x, x])) if rates[x] > 0.0 else abs(float(kernel[x, x]) - 1.0)
        for x in range(len(rates))
    )
    require(decomposition_residual <= ATOL, "canonical decomposition differs")
    require(kernel_row_sum_residual <= ATOL, "canonical kernel row sums differ")
    require(kernel_minimum >= -ATOL, "canonical kernel has a negative entry")
    require(canonical_diagonal_residual <= ATOL, "canonical diagonal convention differs")

    q_counterexample = np.array([[-1.0, 1.0], [1.0, -1.0]])
    rates_a = np.array([1.0, 1.0])
    kernel_a = np.array([[0.0, 1.0], [1.0, 0.0]])
    rates_b = np.array([2.0, 2.0])
    kernel_b = np.array([[0.5, 0.5], [0.5, 0.5]])
    counterexample_a_residual = maximum_abs(
        np.diag(rates_a) @ (kernel_a - np.eye(2)) - q_counterexample
    )
    counterexample_b_residual = maximum_abs(
        np.diag(rates_b) @ (kernel_b - np.eye(2)) - q_counterexample
    )
    counterexample_pair_distance = maximum_abs(rates_a - rates_b) + maximum_abs(
        kernel_a - kernel_b
    )
    require(counterexample_a_residual <= ATOL, "first counterexample pair differs")
    require(counterexample_b_residual <= ATOL, "second counterexample pair differs")
    require(counterexample_pair_distance > 0.0, "counterexample pairs are not distinct")

    time_grid = [0.0, 0.001, 0.1, 1.0, 10.0]
    stochasticity: list[dict[str, float]] = []
    transition: dict[float, np.ndarray] = {}
    for t in time_grid:
        p = expm(t * q)
        transition[t] = p
        row_residual = maximum_abs(p.sum(axis=1) - 1.0)
        minimum = finite(p.min())
        require(row_residual <= ATOL, f"P({t}) row sums differ")
        require(minimum >= -ATOL, f"P({t}) has a negative entry")
        stochasticity.append(
            {"t": t, "row_sum_residual": row_residual, "minimum_entry": minimum}
        )

    semigroup_pairs = [(0.001, 0.1), (0.1, 1.0), (1.0, 10.0)]
    semigroup_residuals = []
    for s, t in semigroup_pairs:
        residual = maximum_abs(expm((s + t) * q) - expm(s * q) @ expm(t * q))
        require(residual <= ATOL, f"semigroup composition differs at {s}, {t}")
        semigroup_residuals.append({"s": s, "t": t, "residual": residual})

    difference_steps = [1.0e-3, 1.0e-4, 1.0e-5, 1.0e-6]
    right_difference_residuals = []
    identity = np.eye(q.shape[0])
    for h in difference_steps:
        residual = maximum_abs((expm(h * q) - identity) / h - q)
        right_difference_residuals.append({"h": h, "residual": residual})
    require(
        right_difference_residuals[-1]["residual"] <= 1.0e-5,
        "generator right-difference residual exceeds tolerance",
    )

    uniformization_residuals = []
    for t in time_grid:
        residual = maximum_abs(uniformized(t, q, max_exit_rate, 200) - transition[t])
        require(residual <= ATOL, f"uniformization differs at {t}")
        uniformization_residuals.append({"t": t, "residual": residual})

    q_zero = np.zeros((3, 3))
    zero_rates, zero_kernel = canonical_decomposition(q_zero)
    zero_reconstruction = np.diag(zero_rates) @ (zero_kernel - np.eye(3))
    zero_branch_residual = max(
        maximum_abs(zero_reconstruction - q_zero),
        maximum_abs(expm(q_zero) - np.eye(3)),
    )
    require(zero_branch_residual <= ATOL, "zero-rate branch differs")

    poisson_rate = 1.7
    poisson_size = 12
    poisson_q = np.zeros((poisson_size, poisson_size))
    for j in range(poisson_size - 1):
        poisson_q[j, j] = -poisson_rate
        poisson_q[j, j + 1] = poisson_rate
    poisson_residuals = []
    for t in [0.1, 0.7, 2.0]:
        p = expm(t * poisson_q)
        residual = 0.0
        for j in range(poisson_size - 1):
            for k in range(poisson_size - 1):
                expected = (
                    math.exp(-poisson_rate * t)
                    * (poisson_rate * t) ** (k - j)
                    / math.factorial(k - j)
                    if k >= j
                    else 0.0
                )
                residual = max(residual, abs(float(p[j, k]) - expected))
        require(residual <= ATOL, f"Poisson pre-boundary entries differ at {t}")
        poisson_residuals.append({"t": t, "residual": finite(residual)})

    receipt: dict[str, Any] = {
        "schema": "o009.quantecon-uc-mc-semigroups-numerical-qa.v1",
        "status": "pass",
        "as_of": "2026-08-24",
        "authority": {
            "path": "authority/quantecon/source_snapshot/continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7/lectures/uc_mc_semigroups.md",
            "sha256": AUTHORITY_SHA,
        },
        "target": {
            "path": "source/quantecon/lectures/uc_mc_semigroups.md",
            "sha256": TARGET_SHA,
        },
        "runtime": {
            "path": "tmp/quantecon-offline-replay/Scripts/python.exe",
            "sha256": sha256(runtime_python),
            "runtime_lock_sha256": sha256(RUNTIME_LOCK),
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "tolerances": {
            "matrix_absolute": ATOL,
            "generator_final": 1.0e-5,
            "uniformization_terms": 200,
        },
        "fixture": {
            "Q": q.tolist(),
            "row_sum_residual": row_sum_residual,
            "off_diagonal_minimum": off_diagonal_minimum,
            "diagonal_maximum": diagonal_maximum,
            "ell1_row_action_operator_norm": operator_norm,
            "maximum_exit_rate": max_exit_rate,
            "operator_norm_identity_residual": operator_norm_identity_residual,
        },
        "canonical_decomposition": {
            "rates": rates.tolist(),
            "kernel": kernel.tolist(),
            "reconstruction_residual": decomposition_residual,
            "kernel_row_sum_residual": kernel_row_sum_residual,
            "kernel_minimum": kernel_minimum,
            "canonical_diagonal_residual": finite(canonical_diagonal_residual),
        },
        "noninjective_pair_counterexample": {
            "Q": q_counterexample.tolist(),
            "rates_a": rates_a.tolist(),
            "kernel_a": kernel_a.tolist(),
            "rates_b": rates_b.tolist(),
            "kernel_b": kernel_b.tolist(),
            "pair_a_residual": counterexample_a_residual,
            "pair_b_residual": counterexample_b_residual,
            "distinct_pair_distance": counterexample_pair_distance,
        },
        "transition_stochasticity": stochasticity,
        "semigroup_composition": semigroup_residuals,
        "generator_right_differences": right_difference_residuals,
        "uniformization": uniformization_residuals,
        "zero_rate_branch": {
            "rates": zero_rates.tolist(),
            "kernel": zero_kernel.tolist(),
            "residual": zero_branch_residual,
        },
        "poisson_pre_boundary": {
            "rate": poisson_rate,
            "truncation_size": poisson_size,
            "residuals": poisson_residuals,
        },
    }
    OUTPUT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        "PASS "
        f"target={TARGET_SHA} "
        f"qa_sha256={sha256(OUTPUT)} "
        f"generator_final={right_difference_residuals[-1]['residual']:.3e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
