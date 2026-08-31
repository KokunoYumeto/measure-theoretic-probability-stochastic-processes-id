#!/usr/bin/env python3
"""Deterministic numerical QA for the Indonesian Kolmogorov-forward unit.

Run only with the lane's pinned offline QuantEcon replay interpreter.  The
script refuses source, target, runtime-lock, interpreter, or package drift and
writes one stable JSON receipt under ``qa/``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import expm


DATE = "2026-08-24"
SEED = 20260824
MATRIX_TOL = 1.0e-12
CENTRAL_DIFFERENCE_TOL = 1.0e-8
RIGHT_DERIVATIVE_TOL = 1.0e-5
NONNEGATIVITY_TOL = 1.0e-13
UNIFORMIZATION_TOL = 1.0e-12

EXPECTED_TARGET_BYTES = 22_210
EXPECTED_TARGET_SHA256 = (
    "19abc4dc6ef33c45917684bd487ffa367e36d929b3190960f96d7a7602cb6098"
)
EXPECTED_AUTHORITY_BYTES = 16_943
EXPECTED_AUTHORITY_SHA256 = (
    "21c694175c28885477fc77b62e8f6a38c8f1d80bbe61cf40c144d285aa6e4b03"
)
EXPECTED_RUNTIME_LOCK_SHA256 = (
    "7b7009aa8abf346cd7dec13c50f03f413471e7e0585ed23563685fd4b1f86210"
)
EXPECTED_INTERPRETER_SHA256 = (
    "0e818a1f9a0b8fbd4e7cc458a07cb7de2ea02ea326e387699a33b92f151242cd"
)
EXPECTED_PYTHON = (3, 13, 9)
EXPECTED_NUMPY = "2.4.4"
EXPECTED_SCIPY = "1.17.1"

EXPECTED_ENVIRONMENT = {
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "MKL_NUM_THREADS": "1",
    "MPLBACKEND": "Agg",
    "NUMBA_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PIP_NO_INDEX": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONNOUSERSITE": "1",
    "PYTHONUTF8": "1",
    "SOURCE_DATE_EPOCH": "315532800",
    "TZ": "UTC",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def max_abs(array: np.ndarray) -> float:
    return float(np.max(np.abs(array)))


def assert_le(value: float, limit: float, label: str) -> None:
    if not value <= limit:
        raise AssertionError(f"{label}: {value!r} exceeds {limit!r}")


def assert_ge(value: float, limit: float, label: str) -> None:
    if not value >= limit:
        raise AssertionError(f"{label}: {value!r} is below {limit!r}")


def check_identity(path: Path, expected_bytes: int, expected_sha256: str) -> dict[str, object]:
    actual_bytes = path.stat().st_size
    actual_sha256 = sha256_file(path)
    if actual_bytes != expected_bytes or actual_sha256 != expected_sha256:
        raise AssertionError(
            f"identity drift for {path}: bytes={actual_bytes}, sha256={actual_sha256}"
        )
    return {
        "path": path.as_posix(),
        "bytes": actual_bytes,
        "sha256": actual_sha256,
    }


def uniformization(
    q: np.ndarray, t: float, terms: int = 100
) -> tuple[np.ndarray, float, np.ndarray, str]:
    """Return a finite uniformization sum and expose the m=0 proof branch."""
    n = q.shape[0]
    identity = np.eye(n)
    m = float(np.max(np.abs(np.diag(q))))
    if m == 0.0:
        if max_abs(q) != 0.0:
            raise AssertionError("m=0 intensity branch contains a nonzero entry")
        return identity, m, identity, "zero_generator_identity"

    p_hat = identity + q / m
    weight = math.exp(-m * t)
    power = identity.copy()
    approximation = weight * power
    for k in range(1, terms + 1):
        power = power @ p_hat
        weight *= (m * t) / k
        approximation += weight * power
    return approximation, m, p_hat, "nontrivial_uniformization"


def main() -> None:
    lane = Path(__file__).resolve().parents[1]
    target = lane / "source" / "quantecon" / "lectures" / "kolmogorov_fwd.md"
    authority = (
        lane
        / "authority"
        / "quantecon"
        / "source_snapshot"
        / "continuous_time_mcs-8b06e0aa5a438692445b2c896f9d238c5a7d5eb7"
        / "lectures"
        / "kolmogorov_fwd.md"
    )
    runtime_lock = lane / "00_control" / "RUNTIME_LOCK.json"
    output = lane / "qa" / "QUANTECON_KOLMOGOROV_FWD_NUMERICAL_QA.json"

    target_identity = check_identity(
        target, EXPECTED_TARGET_BYTES, EXPECTED_TARGET_SHA256
    )
    authority_identity = check_identity(
        authority, EXPECTED_AUTHORITY_BYTES, EXPECTED_AUTHORITY_SHA256
    )
    runtime_lock_identity = check_identity(
        runtime_lock, runtime_lock.stat().st_size, EXPECTED_RUNTIME_LOCK_SHA256
    )

    interpreter = Path(sys.executable).resolve()
    interpreter_sha256 = sha256_file(interpreter)
    if interpreter_sha256 != EXPECTED_INTERPRETER_SHA256:
        raise AssertionError(
            f"unpinned interpreter: {interpreter} sha256={interpreter_sha256}"
        )
    if sys.version_info[:3] != EXPECTED_PYTHON:
        raise AssertionError(f"unexpected Python version: {sys.version_info[:3]}")
    if np.__version__ != EXPECTED_NUMPY or scipy.__version__ != EXPECTED_SCIPY:
        raise AssertionError(
            f"package drift: numpy={np.__version__}, scipy={scipy.__version__}"
        )
    observed_environment = {
        name: os.environ.get(name) for name in EXPECTED_ENVIRONMENT
    }
    if observed_environment != EXPECTED_ENVIRONMENT:
        raise AssertionError(
            f"deterministic environment drift: {observed_environment!r}"
        )

    authority_text = authority.read_text(encoding="utf-8")
    target_text = target.read_text(encoding="utf-8")
    for required in (
        "P = ((0.9, 0.1, 0.0),",
        "Q = ((-3, 2, 1),",
        "ψ_00 = np.array((0.01, 0.01, 0.99))",
    ):
        if required not in authority_text:
            raise AssertionError(f"authority fixture not found: {required}")
    for required in (
        "P = ((0.9, 0.1, 0.0),",
        "Q = ((-3, 2, 1),",
        "ψ_00 = np.array((0.01, 0.01, 0.98))",
        "ψ_01 = np.array((0.01, 0.98, 0.01))",
        "ψ_02 = np.array((0.98, 0.01, 0.01))",
    ):
        if required not in target_text:
            raise AssertionError(f"target fixture not found: {required}")

    random.seed(SEED)
    np.random.seed(SEED)

    p = np.array(
        (
            (0.9, 0.1, 0.0),
            (0.4, 0.4, 0.2),
            (0.1, 0.1, 0.8),
        ),
        dtype=float,
    )
    p_row_error = max_abs(p.sum(axis=1) - 1.0)
    p_min = float(np.min(p))
    assert_le(p_row_error, MATRIX_TOL, "displayed P row sums")
    assert_ge(p_min, 0.0, "displayed P nonnegativity")

    q = np.array(
        (
            (-3.0, 2.0, 1.0),
            (3.0, -5.0, 2.0),
            (4.0, 6.0, -10.0),
        )
    )
    q_row_error = max_abs(q.sum(axis=1))
    off_diagonal_mask = ~np.eye(q.shape[0], dtype=bool)
    q_off_diagonal_min = float(np.min(q[off_diagonal_mask]))
    q_diagonal_max = float(np.max(np.diag(q)))
    assert_le(q_row_error, MATRIX_TOL, "displayed Q row sums")
    assert_ge(q_off_diagonal_min, 0.0, "displayed Q off-diagonal entries")
    assert_le(q_diagonal_max, 0.0, "displayed Q diagonal entries")

    starts = np.array(
        (
            (0.01, 0.01, 0.98),
            (0.01, 0.98, 0.01),
            (0.98, 0.01, 0.01),
        )
    )
    start_sum_errors = np.abs(starts.sum(axis=1) - 1.0)
    start_min = float(np.min(starts))
    assert_le(float(np.max(start_sum_errors)), MATRIX_TOL, "corrected start sums")
    assert_ge(start_min, 0.0, "corrected start nonnegativity")

    representative_times = (0.0, 0.001, 0.1, 1.0, 10.0)
    transition_row_errors: list[float] = []
    transition_min_entries: list[float] = []
    evolved_sum_errors: list[float] = []
    evolved_min_entries: list[float] = []
    for t in representative_times:
        transition = expm(t * q)
        transition_row_errors.append(max_abs(transition.sum(axis=1) - 1.0))
        transition_min_entries.append(float(np.min(transition)))
        evolved = starts @ transition
        evolved_sum_errors.append(max_abs(evolved.sum(axis=1) - 1.0))
        evolved_min_entries.append(float(np.min(evolved)))
    assert_le(max(transition_row_errors), MATRIX_TOL, "transition row sums")
    assert_ge(min(transition_min_entries), -NONNEGATIVITY_TOL, "transition entries")
    assert_le(max(evolved_sum_errors), MATRIX_TOL, "evolved distribution sums")
    assert_ge(min(evolved_min_entries), -NONNEGATIVITY_TOL, "evolved distributions")

    derivative_time = 0.7
    derivative_step = 1.0e-5
    transition = expm(derivative_time * q)
    central_derivative = (
        expm((derivative_time + derivative_step) * q)
        - expm((derivative_time - derivative_step) * q)
    ) / (2.0 * derivative_step)
    forward_residual = max_abs(central_derivative - transition @ q)
    backward_residual = max_abs(central_derivative - q @ transition)
    commutator_residual = max_abs(transition @ q - q @ transition)
    assert_le(forward_residual, CENTRAL_DIFFERENCE_TOL, "forward equation")
    assert_le(backward_residual, CENTRAL_DIFFERENCE_TOL, "backward equation")
    assert_le(commutator_residual, MATRIX_TOL, "generator commutator")

    jump_k = np.array(
        (
            (0.0, 0.7, 0.3),
            (0.2, 0.0, 0.8),
            (0.6, 0.4, 0.0),
        )
    )
    jump_rates = np.array((0.5, 1.25, 2.0))
    exercise2_q = np.diag(jump_rates) @ (jump_k - np.eye(3))
    exercise2_row_error = max_abs(exercise2_q.sum(axis=1))
    exercise2_off_diagonal_min = float(
        np.min(exercise2_q[off_diagonal_mask])
    )
    assert_le(exercise2_row_error, MATRIX_TOL, "Exercise 2 Q row sums")
    assert_ge(
        exercise2_off_diagonal_min, 0.0, "Exercise 2 Q off-diagonal entries"
    )
    right_steps = (1.0e-3, 1.0e-4, 1.0e-5, 1.0e-6)
    right_derivative_residuals = [
        max_abs((expm(h * exercise2_q) - np.eye(3)) / h - exercise2_q)
        for h in right_steps
    ]
    if not all(
        later < earlier
        for earlier, later in zip(
            right_derivative_residuals, right_derivative_residuals[1:]
        )
    ):
        raise AssertionError(
            f"Exercise 2 right derivative does not converge: {right_derivative_residuals}"
        )
    assert_le(
        right_derivative_residuals[-1],
        RIGHT_DERIVATIVE_TOL,
        "Exercise 2 Q=P'_0",
    )

    zero_q = np.zeros((3, 3))
    zero_uniformized, zero_m, zero_p_hat, zero_branch = uniformization(
        zero_q, t=0.7
    )
    zero_identity_error = max_abs(zero_uniformized - np.eye(3))
    zero_p_hat_error = max_abs(zero_p_hat - np.eye(3))
    if zero_m != 0.0 or zero_branch != "zero_generator_identity":
        raise AssertionError("Exercise 3 m=0 branch was not selected")
    assert_le(zero_identity_error, MATRIX_TOL, "Exercise 3 zero-generator expm")
    assert_le(zero_p_hat_error, MATRIX_TOL, "Exercise 3 zero-generator P-hat")

    uniformization_time = 0.7
    uniformized, uniformization_m, p_hat, uniformization_branch = uniformization(
        q, t=uniformization_time, terms=100
    )
    if uniformization_branch != "nontrivial_uniformization" or uniformization_m <= 0:
        raise AssertionError("Exercise 3 nontrivial branch was not selected")
    p_hat_row_error = max_abs(p_hat.sum(axis=1) - 1.0)
    p_hat_min = float(np.min(p_hat))
    uniformization_residual = max_abs(
        uniformized - expm(uniformization_time * q)
    )
    assert_le(p_hat_row_error, MATRIX_TOL, "Exercise 3 P-hat row sums")
    assert_ge(p_hat_min, 0.0, "Exercise 3 P-hat nonnegativity")
    assert_le(
        uniformization_residual,
        UNIFORMIZATION_TOL,
        "Exercise 3 uniformization series",
    )

    receipt = {
        "schema": "o009.quantecon-kolmogorov-fwd-numerical-qa.v1",
        "date": DATE,
        "status": "pass",
        "target": {
            "path": target.relative_to(lane).as_posix(),
            "bytes": target_identity["bytes"],
            "sha256": target_identity["sha256"],
        },
        "authority": {
            "path": authority.relative_to(lane).as_posix(),
            "bytes": authority_identity["bytes"],
            "sha256": authority_identity["sha256"],
        },
        "runtime": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable": interpreter.relative_to(lane).as_posix(),
            "executable_sha256": interpreter_sha256,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "runtime_lock_sha256": runtime_lock_identity["sha256"],
            "network": "not accessed; pinned offline replay with PIP_NO_INDEX=1",
            "seed": SEED,
            "environment": observed_environment,
        },
        "tolerances": {
            "matrix_identities": MATRIX_TOL,
            "central_difference": CENTRAL_DIFFERENCE_TOL,
            "right_derivative": RIGHT_DERIVATIVE_TOL,
            "nonnegativity_floor": NONNEGATIVITY_TOL,
            "uniformization": UNIFORMIZATION_TOL,
        },
        "checks": {
            "displayed_P_min": p_min,
            "displayed_P_row_sum_max_error": p_row_error,
            "corrected_start_sum_errors": start_sum_errors.tolist(),
            "corrected_start_min": start_min,
            "displayed_Q_row_sum_max_error": q_row_error,
            "displayed_Q_off_diagonal_min": q_off_diagonal_min,
            "displayed_Q_diagonal_max": q_diagonal_max,
            "representative_times": list(representative_times),
            "transition_row_sum_max_errors": transition_row_errors,
            "transition_min_entries": transition_min_entries,
            "evolved_distribution_sum_max_errors": evolved_sum_errors,
            "evolved_distribution_min_entries": evolved_min_entries,
            "forward_equation_central_difference_residual": forward_residual,
            "backward_equation_central_difference_residual": backward_residual,
            "generator_commutator_residual": commutator_residual,
            "exercise2_K_row_sum_max_error": max_abs(jump_k.sum(axis=1) - 1.0),
            "exercise2_K_diagonal_max_absolute": max_abs(np.diag(jump_k)),
            "exercise2_Q_row_sum_max_error": exercise2_row_error,
            "exercise2_Q_off_diagonal_min": exercise2_off_diagonal_min,
            "exercise2_right_steps": list(right_steps),
            "exercise2_right_derivative_residuals": right_derivative_residuals,
            "exercise3_zero_m": zero_m,
            "exercise3_zero_branch": zero_branch,
            "exercise3_zero_identity_error": zero_identity_error,
            "exercise3_zero_P_hat_error": zero_p_hat_error,
            "exercise3_nontrivial_m": uniformization_m,
            "exercise3_nontrivial_branch": uniformization_branch,
            "exercise3_P_hat_row_sum_max_error": p_hat_row_error,
            "exercise3_P_hat_min": p_hat_min,
            "exercise3_uniformization_terms": 100,
            "exercise3_uniformization_residual": uniformization_residual,
        },
    }
    output.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "output": output.relative_to(lane).as_posix(),
                "bytes": output.stat().st_size,
                "sha256": sha256_file(output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
