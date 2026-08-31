#!/usr/bin/env python3
"""Deterministic numerical QA for the QuantEcon ergodicity unit."""

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
    / "ergodicity.md"
)
TARGET = ROOT / "source" / "quantecon" / "lectures" / "ergodicity.md"
RUNTIME_LOCK = ROOT / "00_control" / "RUNTIME_LOCK.json"
OUTPUT = ROOT / "qa" / "QUANTECON_ERGODICITY_NUMERICAL_QA.json"

AUTHORITY_SHA = "01c8f94e8016119107d6a3c14e688a0c1ed71690f678a2ae252703f7abccba84"
TARGET_SHA = "5ae7f5f06befc5c71727da6c33678af5aac3fed523e9d547fb7a0577a1af61ad"
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


def shortest_positive_paths(kernel: np.ndarray) -> np.ndarray:
    size = kernel.shape[0]
    distance = np.full((size, size), -1, dtype=int)
    for origin in range(size):
        distance[origin, origin] = 0
        frontier = [origin]
        while frontier:
            current = frontier.pop(0)
            for destination in np.flatnonzero(kernel[current] > 0.0):
                if distance[origin, destination] < 0:
                    distance[origin, destination] = distance[origin, current] + 1
                    frontier.append(int(destination))
    return distance


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
            [-3.0, 2.0, 1.0],
            [3.0, -5.0, 2.0],
            [4.0, 6.0, -10.0],
        ],
        dtype=float,
    )
    row_sum_residual = maximum_abs(q.sum(axis=1))
    off_diagonal = q.copy()
    np.fill_diagonal(off_diagonal, 0.0)
    off_diagonal_minimum = finite(off_diagonal.min())
    diagonal_maximum = finite(np.diag(q).max())
    require(row_sum_residual <= ATOL, "fixture row sums differ")
    require(off_diagonal_minimum >= -ATOL, "fixture has a negative off-diagonal entry")
    require(diagonal_maximum <= ATOL, "fixture has a positive diagonal entry")

    stationary_exact = np.array([38.0, 26.0, 9.0]) / 73.0
    stationary_sum_residual = abs(finite(stationary_exact.sum()) - 1.0)
    stationary_generator_residual = maximum_abs(stationary_exact @ q)
    system = np.vstack((q.T[:2], np.ones(3)))
    solved_stationary = np.linalg.solve(system, np.array([0.0, 0.0, 1.0]))
    stationary_solve_residual = maximum_abs(solved_stationary - stationary_exact)
    accessible_rounding_residual = maximum_abs(
        np.round(stationary_exact, 6) - np.array([0.520548, 0.356164, 0.123288])
    )
    require(stationary_sum_residual <= ATOL, "stationary law does not sum to one")
    require(stationary_generator_residual <= ATOL, "stationary law does not annihilate Q")
    require(stationary_solve_residual <= ATOL, "solved stationary law differs")
    require(accessible_rounding_residual <= 5.0e-7, "accessible figure value differs")

    eigenvalues = np.linalg.eigvals(q)
    zero_eigenvalue_residual = finite(np.min(np.abs(eigenvalues)))
    nonzero_decay_rates = sorted(
        finite(-value.real) for value in eigenvalues if abs(value) > 1.0e-10
    )
    require(zero_eigenvalue_residual <= ATOL, "Q lacks its zero eigenvalue")
    require(min(nonzero_decay_rates) > 0.0, "Q lacks a positive spectral gap")

    max_exit_rate = finite(np.max(-np.diag(q)))
    uniformized = np.eye(3) + q / max_exit_rate
    uniformized_row_residual = maximum_abs(uniformized.sum(axis=1) - 1.0)
    uniformized_minimum = finite(uniformized.min())
    path_lengths = shortest_positive_paths(uniformized)
    require(uniformized_row_residual <= ATOL, "uniformized kernel row sums differ")
    require(uniformized_minimum >= -ATOL, "uniformized kernel is not nonnegative")
    require(np.all(path_lengths >= 0), "uniformized kernel is not irreducible")

    lower_bound_time = 0.5
    lower_bound_residuals: list[dict[str, Any]] = []
    p_lower_time = expm(lower_bound_time * q)
    for origin in range(3):
        for destination in range(3):
            power = int(path_lengths[origin, destination])
            kernel_power = np.linalg.matrix_power(uniformized, power)
            lower_bound = (
                math.exp(-max_exit_rate * lower_bound_time)
                * (max_exit_rate * lower_bound_time) ** power
                / math.factorial(power)
                * float(kernel_power[origin, destination])
            )
            slack = finite(p_lower_time[origin, destination] - lower_bound)
            require(lower_bound > 0.0, "uniformization path lower bound is not positive")
            require(slack >= -ATOL, "uniformization lower bound exceeds transition entry")
            lower_bound_residuals.append(
                {
                    "origin": origin,
                    "destination": destination,
                    "path_length": power,
                    "lower_bound": finite(lower_bound),
                    "slack": slack,
                }
            )

    time_grid = [0.001, 0.1, 1.0, 5.0, 20.0]
    transition: dict[float, np.ndarray] = {}
    transition_checks: list[dict[str, float]] = []
    for time in time_grid:
        p = expm(time * q)
        transition[time] = p
        row_residual = maximum_abs(p.sum(axis=1) - 1.0)
        minimum = finite(p.min())
        invariant_residual = maximum_abs(stationary_exact @ p - stationary_exact)
        require(row_residual <= ATOL, f"P({time}) row sums differ")
        require(minimum > 0.0, f"P({time}) is not everywhere positive")
        require(invariant_residual <= ATOL, f"stationary law changes under P({time})")
        transition_checks.append(
            {
                "t": time,
                "row_sum_residual": row_residual,
                "minimum_entry": minimum,
                "stationary_residual": invariant_residual,
            }
        )

    semigroup_checks: list[dict[str, float]] = []
    for first, second in [(0.001, 0.1), (0.1, 1.0), (1.0, 5.0)]:
        residual = maximum_abs(
            expm((first + second) * q) - expm(first * q) @ expm(second * q)
        )
        require(residual <= ATOL, f"semigroup composition differs at {first}, {second}")
        semigroup_checks.append({"s": first, "t": second, "residual": residual})

    initial_distributions = [
        np.array([0.01, 0.01, 0.98]),
        np.array([0.01, 0.98, 0.01]),
        np.array([0.98, 0.01, 0.01]),
    ]
    convergence_grid = [0.0, 0.1, 1.0, 5.0, 20.0]
    convergence: list[dict[str, Any]] = []
    for index, initial in enumerate(initial_distributions, start=1):
        distances = [
            finite(np.linalg.norm(initial @ expm(time * q) - stationary_exact, ord=1))
            for time in convergence_grid
        ]
        require(
            all(later <= earlier + ATOL for earlier, later in zip(distances, distances[1:])),
            f"trajectory {index} is not contractive toward stationarity",
        )
        require(distances[-1] <= ATOL, f"trajectory {index} did not converge")
        convergence.append(
            {
                "initial": initial.tolist(),
                "times": convergence_grid,
                "l1_distances": distances,
            }
        )

    p_one = transition[1.0]
    strict_contractions: list[dict[str, float | int]] = []
    for left in range(len(initial_distributions)):
        for right in range(left + 1, len(initial_distributions)):
            before = finite(
                np.linalg.norm(initial_distributions[left] - initial_distributions[right], ord=1)
            )
            after = finite(
                np.linalg.norm(
                    initial_distributions[left] @ p_one
                    - initial_distributions[right] @ p_one,
                    ord=1,
                )
            )
            require(after < before, "strict contraction fixture did not contract")
            strict_contractions.append(
                {
                    "left": left + 1,
                    "right": right + 1,
                    "before": before,
                    "after": after,
                    "ratio": finite(after / before),
                }
            )

    skeleton_checks: list[dict[str, float | int]] = []
    for power in [1, 2, 5, 10, 20]:
        residual = maximum_abs(np.linalg.matrix_power(p_one, power) - expm(power * q))
        convergence_residual = max(
            finite(np.linalg.norm(initial @ np.linalg.matrix_power(p_one, power) - stationary_exact, ord=1))
            for initial in initial_distributions
        )
        require(residual <= ATOL, f"skeleton identity differs at power {power}")
        skeleton_checks.append(
            {
                "power": power,
                "semigroup_residual": residual,
                "maximum_l1_distance": convergence_residual,
            }
        )
    require(
        float(skeleton_checks[-1]["maximum_l1_distance"]) <= ATOL,
        "skeleton did not converge to stationarity",
    )

    arrival_rate = 2.0
    service_rate = 3.0
    drift_interior = np.array(
        [
            (state - 1) * service_rate
            - state * (service_rate + arrival_rate)
            + (state + 1) * arrival_rate
            for state in range(1, 11)
        ]
    )
    epsilon = service_rate - arrival_rate
    boundary_drift = arrival_rate
    drift_interior_residual = maximum_abs(drift_interior + epsilon)
    require(drift_interior_residual <= ATOL, "M/M/1 interior drift differs")
    require(boundary_drift > 0.0, "M/M/1 finite-set bound is not positive")

    finite_q = q
    constant_value = 2.0
    finite_drift_residual = maximum_abs(finite_q @ np.full(3, constant_value))
    require(finite_drift_residual <= ATOL, "finite-state constant drift differs")

    birth_size = 16
    birth_rates = np.array([4.0 / (index + 1) for index in range(birth_size)])
    birth_equations = np.zeros((birth_size, birth_size))
    for coordinate in range(birth_size):
        birth_equations[coordinate, coordinate] = -birth_rates[coordinate]
        if coordinate > 0:
            birth_equations[coordinate, coordinate - 1] = birth_rates[coordinate - 1]
    birth_rank = int(np.linalg.matrix_rank(birth_equations))
    birth_zero_solution = np.linalg.solve(birth_equations, np.zeros(birth_size))
    birth_zero_residual = maximum_abs(birth_zero_solution)
    require(np.all(np.diff(birth_rates) <= 0.0), "birth rates are not non-increasing")
    require(np.all(birth_rates > 0.0), "birth rates are not positive")
    require(birth_rank == birth_size, "pure-birth coordinate induction matrix is singular")
    require(birth_zero_residual <= ATOL, "pure-birth zero-coordinate induction differs")

    receipt: dict[str, Any] = {
        "schema": "o009.quantecon-ergodicity-numerical-qa.v1",
        "status": "pass",
        "as_of": "2026-08-24",
        "authority": {
            "path": "authority/quantecon/source_snapshot/continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7/lectures/ergodicity.md",
            "sha256": AUTHORITY_SHA,
        },
        "target": {
            "path": "source/quantecon/lectures/ergodicity.md",
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
        "tolerances": {"matrix_absolute": ATOL, "accessible_rounding": 5.0e-7},
        "lecture_fixture": {
            "Q": q.tolist(),
            "row_sum_residual": row_sum_residual,
            "off_diagonal_minimum": off_diagonal_minimum,
            "diagonal_maximum": diagonal_maximum,
            "eigenvalues": [[finite(value.real), finite(value.imag)] for value in eigenvalues],
            "zero_eigenvalue_residual": zero_eigenvalue_residual,
            "nonzero_decay_rates": nonzero_decay_rates,
        },
        "stationarity": {
            "exact_integer_weights": [38, 26, 9],
            "normalizer": 73,
            "distribution": stationary_exact.tolist(),
            "sum_residual": stationary_sum_residual,
            "generator_residual": stationary_generator_residual,
            "linear_solve_residual": stationary_solve_residual,
            "accessible_rounding_residual": accessible_rounding_residual,
        },
        "uniformization_irreducibility": {
            "rate": max_exit_rate,
            "kernel": uniformized.tolist(),
            "row_sum_residual": uniformized_row_residual,
            "minimum_entry": uniformized_minimum,
            "shortest_positive_path_lengths": path_lengths.tolist(),
            "lower_bound_time": lower_bound_time,
            "path_lower_bounds": lower_bound_residuals,
        },
        "transition_checks": transition_checks,
        "semigroup_composition": semigroup_checks,
        "trajectory_convergence": convergence,
        "strict_contraction": strict_contractions,
        "skeleton": {"step": 1.0, "checks": skeleton_checks},
        "mm1_drift": {
            "arrival_rate": arrival_rate,
            "service_rate": service_rate,
            "epsilon": epsilon,
            "finite_set": [0],
            "M": boundary_drift,
            "boundary_drift": boundary_drift,
            "interior_drifts": drift_interior.tolist(),
            "interior_residual": drift_interior_residual,
        },
        "finite_state_drift": {
            "constant_v": constant_value,
            "F": [0, 1, 2],
            "residual": finite_drift_residual,
        },
        "pure_birth_induction": {
            "prefix_size": birth_size,
            "rates": birth_rates.tolist(),
            "equation_matrix_rank": birth_rank,
            "zero_solution_residual": birth_zero_residual,
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
        f"stationary_residual={stationary_generator_residual:.3e} "
        f"final_l1={max(row['l1_distances'][-1] for row in convergence):.3e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
