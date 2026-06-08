#!/usr/bin/env python3
"""Reusable MPC utilities: discrete-time LQR, discretization, and output validation.

Functions:
- dlqr(A, B, Q, R, max_iter=2000, tol=1e-9): compute discrete-time LQR gain via Riccati iteration
- discretize_exact(A, B, dt): exact discretization using matrix exponential (if SciPy available), else falls back to Euler
- discretize_euler(A, B, dt): forward Euler discretization
- validate_controller_params(path): check shapes, positivity, and required keys
- validate_control_log(path, required_seconds=5.0, eps=1e-6): verify schema and duration with float tolerance
- validate_metrics(path, required_keys=None): ensure required metric fields are present
- compute_settling_time(times, signals, refs, tol, step_time): generic settling-time computation

This script is generic and does not include task-specific constants.
"""
import json
import math
import sys
from typing import Dict, List, Optional, Tuple

try:
    import numpy as np
except Exception as e:
    raise RuntimeError("numpy is required for mpc_utils.py") from e


def dlqr(A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: np.ndarray,
         max_iter: int = 2000, tol: float = 1e-9) -> np.ndarray:
    """Discrete-time LQR via iterative Riccati equation.

    Solves P = A^T P A - A^T P B (R + B^T P B)^{-1} B^T P A + Q.
    Returns K = (R + B^T P B)^{-1} B^T P A.

    Preconditions: Q and R symmetric positive (semi)definite.
    """
    n_x = A.shape[0]
    P = Q.copy()
    for _ in range(max_iter):
        BtP = B.T @ P
        S = R + BtP @ B
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            # Regularize R if singular
            S_inv = np.linalg.inv(S + 1e-9 * np.eye(S.shape[0]))
        K = S_inv @ BtP @ A
        P_next = A.T @ P @ A - A.T @ P @ B @ K + Q
        if np.linalg.norm(P_next - P, ord='fro') < tol:
            P = P_next
            break
        P = P_next
    # Final gain
    BtP = B.T @ P
    S = R + BtP @ B
    try:
        S_inv = np.linalg.inv(S)
    except np.linalg.LinAlgError:
        S_inv = np.linalg.inv(S + 1e-9 * np.eye(S.shape[0]))
    K = S_inv @ BtP @ A
    return K


def discretize_euler(A: np.ndarray, B: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """Forward Euler discretization: A_d = I + A*dt, B_d = B*dt."""
    I = np.eye(A.shape[0])
    A_d = I + A * dt
    B_d = B * dt
    return A_d, B_d


def discretize_exact(A: np.ndarray, B: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """Exact discretization using matrix exponential if SciPy is available; else Euler fallback."""
    try:
        from scipy.linalg import expm
        n_x, n_u = A.shape[0], B.shape[1]
        Z = np.zeros((n_u, n_u))
        M = np.block([[A, B], [np.zeros((n_u, n_x)), Z]])
        Md = expm(M * dt)
        A_d = Md[:n_x, :n_x]
        B_d = Md[:n_x, n_x:]
        return A_d, B_d
    except Exception:
        return discretize_euler(A, B, dt)


def _as_np_matrix(mat: List[List[float]], name: str) -> np.ndarray:
    arr = np.array(mat, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be a 2D matrix")
    return arr


def _as_np_vector(vec: List[float], name: str) -> np.ndarray:
    arr = np.array(vec, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be a 1D array")
    return arr


def validate_controller_params(path: str) -> Dict[str, object]:
    """Validate controller_params.json structure and dimensions.

    Returns dict with keys: ok (bool), errors (list of str), summary (dict)
    """
    errors: List[str] = []
    summary: Dict[str, object] = {}
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return {"ok": False, "errors": [f"Failed to read {path}: {e}"], "summary": summary}

    required_keys = ["horizon_N", "Q_diag", "R_diag", "K_lqr", "A_matrix", "B_matrix"]
    for k in required_keys:
        if k not in data:
            errors.append(f"Missing key: {k}")

    if errors:
        return {"ok": False, "errors": errors, "summary": summary}

    try:
        A = _as_np_matrix(data["A_matrix"], "A_matrix")
        B = _as_np_matrix(data["B_matrix"], "B_matrix")
        K = _as_np_matrix(data["K_lqr"], "K_lqr")
        Qd = _as_np_vector(data["Q_diag"], "Q_diag")
        Rd = _as_np_vector(data["R_diag"], "R_diag")
        N = int(data["horizon_N"])  # may raise
    except Exception as e:
        errors.append(f"Type/shape error: {e}")
        return {"ok": False, "errors": errors, "summary": summary}

    n_x = A.shape[0]
    n_u = B.shape[1]
    # Dimension checks
    if A.shape[1] != n_x:
        errors.append("A_matrix must be square (n_x x n_x)")
    if B.shape[0] != n_x:
        errors.append("B_matrix rows must equal n_x")
    if K.shape != (n_u, n_x):
        errors.append("K_lqr shape must be (n_u x n_x)")
    if Qd.shape[0] != n_x:
        errors.append("Q_diag length must equal n_x")
    if Rd.shape[0] != n_u:
        errors.append("R_diag length must equal n_u")

    # Positivity checks
    if (Qd <= 0).any():
        errors.append("Q_diag entries must be positive")
    if (Rd <= 0).any():
        errors.append("R_diag entries must be positive")

    if N <= 0:
        errors.append("horizon_N must be a positive integer")

    summary.update({"n_x": n_x, "n_u": n_u, "horizon_N": N})
    return {"ok": len(errors) == 0, "errors": errors, "summary": summary}


def validate_control_log(path: str, required_seconds: float = 5.0, eps: float = 1e-6) -> Dict[str, object]:
    """Validate control_log.json schema and time span with float tolerance.

    Returns dict with keys: ok (bool), errors (list of str), summary (dict)
    """
    errors: List[str] = []
    summary: Dict[str, object] = {}
    try:
        with open(path, 'r') as f:
            log = json.load(f)
    except Exception as e:
        return {"ok": False, "errors": [f"Failed to read {path}: {e}"], "summary": summary}

    if "phase" not in log or "data" not in log:
        errors.append("Missing keys: phase and/or data")
        return {"ok": False, "errors": errors, "summary": summary}

    if not isinstance(log["data"], list) or len(log["data"]) == 0:
        errors.append("data must be a non-empty list")
        return {"ok": False, "errors": errors, "summary": summary}

    times: List[float] = []
    len_tensions = None
    len_velocities = None
    len_controls = None
    len_refs = None

    for i, entry in enumerate(log["data"]):
        for key in ("time", "tensions", "velocities", "control_inputs", "references"):
            if key not in entry:
                errors.append(f"Entry {i} missing key: {key}")
                return {"ok": False, "errors": errors, "summary": summary}
        try:
            t = float(entry["time"])
            tens = list(entry["tensions"])  # type: ignore
            vels = list(entry["velocities"])  # type: ignore
            ctrls = list(entry["control_inputs"])  # type: ignore
            refs = list(entry["references"])  # type: ignore
        except Exception:
            errors.append(f"Entry {i} has non-numeric or invalid fields")
            return {"ok": False, "errors": errors, "summary": summary}

        times.append(t)
        # Dimension consistency across entries
        if len_tensions is None:
            len_tensions = len(tens)
            len_velocities = len(vels)
            len_controls = len(ctrls)
            len_refs = len(refs)
        else:
            if len(tens) != len_tensions:
                errors.append(f"Entry {i} tensions length mismatch")
            if len(vels) != len_velocities:
                errors.append(f"Entry {i} velocities length mismatch")
            if len(ctrls) != len_controls:
                errors.append(f"Entry {i} control_inputs length mismatch")
            if len(refs) != len_refs:
                errors.append(f"Entry {i} references length mismatch")

    if len(times) >= 2:
        if any(math.isnan(t) or math.isinf(t) for t in times):
            errors.append("Times contain NaN or Inf")
        # check monotonic non-decreasing
        if any(times[i] < times[i-1] - eps for i in range(1, len(times))):
            errors.append("Times must be non-decreasing")
        duration = times[-1] - times[0]
        summary["duration"] = duration
        if duration < required_seconds - eps:
            errors.append(f"Duration {duration:.6f}s is less than required {required_seconds}s (tolerance {eps})")
    else:
        errors.append("Insufficient time entries to compute duration")

    # Reference dimension heuristic: references should match total state dimension.
    # If tensions and velocities represent state components, len_refs should equal len_tensions + len_velocities.
    if (len_tensions is not None and len_velocities is not None and len_refs is not None):
        if len_refs != len_tensions + len_velocities:
            # Not a hard error if task schema differs; report as warning in summary.
            summary["warning"] = "references length does not equal tensions+velocities; verify schema per task"

    summary.update({
        "entries": len(times),
        "len_tensions": len_tensions,
        "len_velocities": len_velocities,
        "len_controls": len_controls,
        "len_refs": len_refs,
    })
    return {"ok": len(errors) == 0, "errors": errors, "summary": summary}


def validate_metrics(path: str, required_keys: Optional[List[str]] = None) -> Dict[str, object]:
    """Validate metrics.json contains required fields.

    Returns dict with keys: ok (bool), errors (list of str), summary (dict)
    """
    errors: List[str] = []
    summary: Dict[str, object] = {}
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return {"ok": False, "errors": [f"Failed to read {path}: {e}"], "summary": summary}

    # Default to common metric keys if none provided.
    default_keys = ["steady_state_error", "settling_time", "max_tension", "min_tension"]
    required = required_keys if required_keys is not None else default_keys

    for k in required:
        if k not in data:
            errors.append(f"Missing metric key: {k}")

    # Basic type checks
    for k in required:
        if k in data and not isinstance(data[k], (int, float)):
            errors.append(f"Metric {k} must be numeric")

    summary.update({k: data.get(k) for k in required})
    return {"ok": len(errors) == 0, "errors": errors, "summary": summary}


def compute_settling_time(times: List[float], signals: np.ndarray, refs: np.ndarray,
                          tol: float, step_time: float) -> float:
    """Compute settling time: earliest t >= step_time such that for all subsequent times,
    |signals - refs| <= tol elementwise.

    Args:
        times: list of timestamps (monotonic non-decreasing)
        signals: shape (T, n) array of measured signals (e.g., tensions)
        refs: shape (T, n) array of reference signals corresponding to 'signals'
        tol: absolute tolerance per signal
        step_time: time from which settling is evaluated (e.g., time of step change)

    Returns:
        settling_time in seconds. If never settles, returns math.inf.
    """
    T = len(times)
    if signals.shape[0] != T or refs.shape[0] != T:
        raise ValueError("signals/refs must have the same number of rows as times")
    # Find index from which to evaluate settling
    start_idx = 0
    for i, t in enumerate(times):
        if t >= step_time:
            start_idx = i
            break
    # For each candidate index after step_time, check if all subsequent samples stay within tol
    for i in range(start_idx, T):
        err = np.abs(signals[i:] - refs[i:])
        if (err <= tol).all():
            return float(times[i] - step_time)
    return math.inf


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MPC utilities: validation and basic control math")
    sub = parser.add_subparsers(dest="cmd")

    p_cp = sub.add_parser("validate-params", help="Validate controller_params.json")
    p_cp.add_argument("path", help="Path to controller_params.json")

    p_cl = sub.add_parser("validate-log", help="Validate control_log.json")
    p_cl.add_argument("path", help="Path to control_log.json")
    p_cl.add_argument("--seconds", type=float, default=5.0, help="Required duration in seconds")
    p_cl.add_argument("--eps", type=float, default=1e-6, help="Float tolerance for duration")

    p_mt = sub.add_parser("validate-metrics", help="Validate metrics.json")
    p_mt.add_argument("path", help="Path to metrics.json")
    p_mt.add_argument("--keys", nargs="*", help="Optional list of required metric keys")

    p_dlqr = sub.add_parser("dlqr", help="Compute discrete-time LQR gain")
    p_dlqr.add_argument("A", help="Path to JSON 2D array for A")
    p_dlqr.add_argument("B", help="Path to JSON 2D array for B")
    p_dlqr.add_argument("Q", help="Path to JSON 1D or 2D array for Q")
    p_dlqr.add_argument("R", help="Path to JSON 1D or 2D array for R")

    args = parser.parse_args()

    if args.cmd == "validate-params":
        res = validate_controller_params(args.path)
        print(json.dumps(res, indent=2))
    elif args.cmd == "validate-log":
        res = validate_control_log(args.path, required_seconds=args.seconds, eps=args.eps)
        print(json.dumps(res, indent=2))
    elif args.cmd == "validate-metrics":
        keys = args.keys if args.keys else None
        res = validate_metrics(args.path, required_keys=keys)
        print(json.dumps(res, indent=2))
    elif args.cmd == "dlqr":
        # Load matrices/vectors from JSON files
        def load_mat(path: str) -> np.ndarray:
            with open(path, 'r') as f:
                obj = json.load(f)
            arr = np.array(obj, dtype=float)
            if arr.ndim == 1:
                return np.diag(arr)
            return arr
        A = load_mat(args.A)
        B = load_mat(args.B)
        Q = load_mat(args.Q)
        R = load_mat(args.R)
        K = dlqr(A, B, Q, R)
        print(json.dumps({"K_lqr": K.tolist()}, indent=2))
    else:
        parser.print_help()
