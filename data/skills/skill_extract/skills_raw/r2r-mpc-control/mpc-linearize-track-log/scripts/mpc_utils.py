#!/usr/bin/env python3
"""Reusable MPC utilities: discretization, LQR (DARE & finite-horizon),
metrics, and basic output validation.

All functions are generic and do not assume a specific plant.
"""
from __future__ import annotations
import math
from typing import Dict, Tuple, List, Optional

import numpy as np

# SciPy is optional. If unavailable, we fall back to iteration and Euler.
try:
    import scipy.linalg as _la
    _HAVE_SCIPY = True
except Exception:  # pragma: no cover
    _la = None
    _HAVE_SCIPY = False


def euler_discretize(A_c: np.ndarray, B_c: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """Forward-Euler discretization consistent with x[k+1] = x[k] + dt*(A_c x + B_c u)."""
    n = A_c.shape[0]
    A_d = np.eye(n) + dt * A_c
    B_d = dt * B_c
    return A_d, B_d


def exact_discretize(A_c: np.ndarray, B_c: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """Exact discretization using matrix exponential of augmented system.

    If SciPy is unavailable, falls back to Euler.
    """
    if not _HAVE_SCIPY:
        return euler_discretize(A_c, B_c, dt)
    n, m = A_c.shape[0], B_c.shape[1]
    aug = np.zeros((n + m, n + m))
    aug[:n, :n] = A_c * dt
    aug[:n, n:] = B_c * dt
    aug_exp = _la.expm(aug)
    A_d = aug_exp[:n, :n]
    B_d = aug_exp[:n, n:]
    return A_d, B_d


def dare_lqr(A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: np.ndarray,
             max_iter: int = 5000, tol: float = 1e-10) -> Tuple[np.ndarray, np.ndarray]:
    """Infinite-horizon discrete LQR via DARE (SciPy) or fixed-point iteration.

    Returns (K, P) where K is the steady-state gain and P the Riccati solution.
    """
    if _HAVE_SCIPY and hasattr(_la, "solve_discrete_are"):
        P = _la.solve_discrete_are(A, B, Q, R)
    else:
        # Fixed-point iteration on the discrete Riccati equation.
        P = Q.copy()
        for _ in range(max_iter):
            S = R + B.T @ P @ B
            K = np.linalg.solve(S, B.T @ P @ A)
            P_new = Q + A.T @ P @ (A - B @ K)
            if np.max(np.abs(P_new - P)) < tol:
                P = P_new
                break
            P = P_new
    S = R + B.T @ P @ B
    K = np.linalg.solve(S, B.T @ P @ A)
    return K, P


def finite_horizon_gains(A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: np.ndarray,
                         N: int, P_terminal: Optional[np.ndarray] = None) -> np.ndarray:
    """Backward Riccati recursion for finite-horizon LQR.

    Args:
        A, B, Q, R: discrete-time system and cost matrices.
        N: horizon length (>=1)
        P_terminal: terminal cost; if None, use infinite-horizon Riccati solution when possible, else Q.
    Returns:
        K_seq: array of shape (N, m, n) with gains K_0..K_{N-1}.
    """
    n = A.shape[0]
    m = B.shape[1]

    if P_terminal is None:
        try:
            K_inf, P_inf = dare_lqr(A, B, Q, R)
            P = P_inf.copy()
        except Exception:  # pragma: no cover
            P = Q.copy()
    else:
        P = P_terminal.copy()

    K_seq = np.zeros((N, m, n))
    for k in range(N - 1, -1, -1):
        S = R + B.T @ P @ B
        K = np.linalg.solve(S, B.T @ P @ A)
        K_seq[k] = K
        P = Q + A.T @ P @ (A - B @ K)
    return K_seq


def compute_settling_time(times: np.ndarray, errors: np.ndarray, band: float,
                          require_persistence: bool = True, confirm_window_s: float = 0.5,
                          dt: Optional[float] = None, start_time: float = 0.0) -> float:
    """Compute first time when all-channel errors enter a band and stay there.

    Args:
        times: shape (T,), monotonically increasing.
        errors: shape (T, p), absolute errors per channel.
        band: absolute band limit (e.g., 2.0 units).
        require_persistence: if True, confirm they remain within band.
        confirm_window_s: window length for confirmation if require_persistence.
        dt: optional step; if None, inferred from times.
        start_time: do not consider times < start_time.
    Returns:
        settling_time (float): time since start_time when settled; if none, returns times[-1] - start_time.
    """
    if dt is None and len(times) >= 2:
        dt = float(np.median(np.diff(times)))
    if dt is None or dt <= 0:
        dt = 1.0

    start_idx = int(np.searchsorted(times, start_time, side="left"))
    confirm_steps = max(1, int(round(confirm_window_s / dt)))

    T = errors.shape[0]
    fallback = float(times[-1] - start_time)

    for i in range(start_idx, T):
        if np.all(errors[i] <= band):
            if not require_persistence:
                return float(times[i] - start_time)
            j_end = min(T, i + confirm_steps)
            if np.all(errors[i:j_end] <= band):
                # If require staying to the end, check the remainder as well
                if np.all(errors[j_end - 1:] <= band):
                    return float(times[i] - start_time)
    return fallback


def compute_metrics(times: np.ndarray, values: np.ndarray, refs: np.ndarray,
                    dt: float, band: float = 2.0, ss_window_s: float = 1.0,
                    step_time: Optional[float] = None) -> Dict[str, float]:
    """Compute generic metrics: steady-state error, settling time, max/min.

    Args:
        times: (T,)
        values: (T, p) actual signals
        refs: (T, p) reference signals (same shape as values)
        dt: step size
        band: absolute tolerance for settling
        ss_window_s: last-window length for steady-state error
        step_time: if provided, settling time is measured relative to this time
    Returns:
        dict with steady_state_error, settling_time, max_value, min_value
    """
    T = values.shape[0]
    window = max(1, int(round(ss_window_s / max(dt, 1e-9))))
    s_idx = max(0, T - window)

    ss_err = float(np.mean(np.abs(values[s_idx:] - refs[s_idx:])))

    errors = np.abs(values - refs)
    if step_time is None:
        # Measure settling relative to the first sample
        settle_t = compute_settling_time(times, errors, band, True, 0.5, dt, start_time=times[0])
    else:
        settle_t = compute_settling_time(times, errors, band, True, 0.5, dt, start_time=step_time)

    max_v = float(np.max(values))
    min_v = float(np.min(values))

    return {
        "steady_state_error": ss_err,
        "settling_time": float(settle_t),
        "max_value": max_v,
        "min_value": min_v,
    }


def validate_outputs(controller_params: Dict,
                     control_log: Dict,
                     metrics: Dict,
                     n_states: Optional[int] = None,
                     n_inputs: Optional[int] = None,
                     min_duration_s: Optional[float] = None) -> List[str]:
    """Validate shapes and minimal content of typical MPC artifacts.

    Returns a list of error messages (empty if all checks pass).
    """
    errs: List[str] = []

    # controller_params.json checks
    req_keys = ["horizon_N", "Q_diag", "R_diag", "K_lqr", "A_matrix", "B_matrix"]
    for k in req_keys:
        if k not in controller_params:
            errs.append(f"controller_params missing key: {k}")

    if "Q_diag" in controller_params:
        if not all(float(q) > 0 for q in controller_params["Q_diag"]):
            errs.append("Q_diag must have positive entries")
    if "R_diag" in controller_params:
        if not all(float(r) > 0 for r in controller_params["R_diag"]):
            errs.append("R_diag must have positive entries")

    if n_states is not None and "A_matrix" in controller_params:
        A = controller_params["A_matrix"]
        if not (len(A) == n_states and len(A[0]) == n_states):
            errs.append(f"A_matrix must be {n_states}x{n_states}")
    if n_states is not None and n_inputs is not None and "B_matrix" in controller_params:
        B = controller_params["B_matrix"]
        if not (len(B) == n_states and len(B[0]) == n_inputs):
            errs.append(f"B_matrix must be {n_states}x{n_inputs}")
    if n_states is not None and n_inputs is not None and "K_lqr" in controller_params:
        K = controller_params["K_lqr"]
        if not (len(K) == n_inputs and len(K[0]) == n_states):
            errs.append(f"K_lqr must be {n_inputs}x{n_states}")

    # control_log.json checks
    if control_log.get("phase") != "control":
        errs.append("control_log.phase must be 'control'")
    data = control_log.get("data", [])
    if not isinstance(data, list) or len(data) == 0:
        errs.append("control_log.data must be a non-empty list")
    else:
        first = data[0]
        for fld in ["time", "tensions", "velocities", "control_inputs", "references"]:
            if fld not in first:
                errs.append(f"control_log.data[0] missing field: {fld}")
        # Minimal duration estimation
        if min_duration_s is not None and len(data) >= 2:
            t0 = float(data[0]["time"]) if "time" in data[0] else None
            tN = float(data[-1]["time"]) if "time" in data[-1] else None
            if t0 is not None and tN is not None:
                if (tN - t0) + 1e-9 < min_duration_s:
                    errs.append(f"control_log duration {(tN - t0):.3f}s < required {min_duration_s:.3f}s")

    # metrics.json checks
    for k in ["steady_state_error", "settling_time"]:
        if k not in metrics:
            errs.append(f"metrics missing key: {k}")

    return errs
