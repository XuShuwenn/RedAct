#!/usr/bin/env python3
"""Utilities for robustly handling pymoo single-objective constrained runs.

Functions:
- best_from_result(result): Return (best_x, best_f, best_idx) by coercing shapes safely.
- max_constraint_violation(g_values): Max positive part across inequality constraints G(x) <= 0.
- write_rounded_solution(path, x, f, decimals=2): Write "Optimal x{i}" lines and an "Objective" line with rounding.

Optional:
- make_nsga2(...): Convenience constructor for NSGA-II.
"""

from typing import Tuple, Sequence, Optional
import numpy as np

try:
    from pymoo.algorithms.moo.nsga2 import NSGA2  # optional import
except Exception:  # pragma: no cover
    NSGA2 = None  # type: ignore


def _as_2d_x(x) -> np.ndarray:
    """Coerce a candidate X to shape (n_solutions, n_vars)."""
    arr = np.asarray(x, dtype=float)
    return np.atleast_2d(arr)


def _as_1d_f(f) -> np.ndarray:
    """Coerce objective values to shape (n_solutions,)."""
    arr = np.asarray(f, dtype=float)
    return arr.reshape(-1)


def best_from_result(result) -> Tuple[np.ndarray, float, int]:
    """Extract best solution robustly from pymoo minimize result.

    Works whether result.X is a 1-D vector or a 2-D array and whether result.F is scalar or array.
    Returns (best_x, best_f, best_idx).
    """
    X = _as_2d_x(getattr(result, 'X'))
    F = _as_1d_f(getattr(result, 'F'))

    if not np.all(np.isfinite(F)):
        raise ValueError("Objective contains non-finite values.")

    idx = int(np.argmin(F))
    return X[idx], float(F[idx]), idx


def max_constraint_violation(g_values: Optional[Sequence[float]]) -> float:
    """Return the maximum violation over G(x) <= 0.

    If g_values is empty or None, returns 0.0.
    """
    if g_values is None:
        return 0.0
    g = np.asarray(g_values, dtype=float).reshape(-1)
    if g.size == 0:
        return 0.0
    return float(np.maximum(g, 0.0).max())


def write_rounded_solution(path: str, x: Sequence[float], f: float, decimals: int = 2) -> None:
    """Write solution in the common benchmark format:
    Optimal x1: X.XX\n
    Optimal x2: X.XX\n
    ...\n
    Objective: Y.YY\n
    The number of decision variables is inferred from len(x).
    """
    x = np.asarray(x, dtype=float).reshape(-1)
    with open(path, 'w') as fh:
        for i, val in enumerate(x, start=1):
            fh.write(f"Optimal x{i}: {val:.{decimals}f}\n")
        fh.write(f"Objective: {float(f):.{decimals}f}\n")


def make_nsga2(pop_size: int = 100, n_offsprings: Optional[int] = None, eliminate_duplicates: bool = True):
    """Convenience constructor for NSGA-II. Requires pymoo to be installed."""
    if NSGA2 is None:
        raise ImportError("pymoo is not available; cannot construct NSGA2.")
    if n_offsprings is None:
        n_offsprings = pop_size
    return NSGA2(pop_size=pop_size, n_offsprings=n_offsprings, eliminate_duplicates=eliminate_duplicates)
