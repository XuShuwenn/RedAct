#!/usr/bin/env python3
"""Utilities for robust extraction of feasible solutions from pymoo results.

Handles both single-solution and population outputs, applies feasibility
filtering with tolerance, and selects the best feasible solution for minimization.

Functions:
- select_best_feasible(X, F, G=None, tol=1e-8):
    Returns (x_best, f_best, feasible, index). If no feasible found, returns
    the lowest objective solution and feasible=False for recovery handling.
- is_feasible(G, tol=1e-8):
    Returns True if all constraint values are <= tol.
- recompute_objective(x, obj_func):
    Helper to verify objectives by recomputing from x.
"""

from typing import Any, Callable, Tuple
import numpy as np


def is_feasible(G: Any, tol: float = 1e-8) -> bool:
    """Check feasibility under G(x) <= tol convention.

    G may be scalar, 1D, or 2D (constraints per solution)."""
    if G is None:
        # If constraints are not provided, treat as unconstrained (caller should recompute if needed)
        return True
    G_np = np.array(G)
    if G_np.ndim == 0:
        return bool(G_np <= tol)
    if G_np.ndim == 1:
        return bool(np.all(G_np <= tol))
    # 2D: constraints per solution
    return bool(np.all(G_np <= tol))


def _feas_mask_from_G(G_np: np.ndarray, tol: float) -> np.ndarray:
    """Create a feasibility mask for population constraints.

    G_np shape:
    - (n_solutions,) : single inequality per solution
    - (n_solutions, n_constraints) : multiple inequalities per solution"""
    if G_np.ndim == 1:
        return G_np <= tol
    return np.all(G_np <= tol, axis=1)


def select_best_feasible(X: Any, F: Any, G: Any = None, tol: float = 1e-8) -> Tuple[np.ndarray, float, bool, int]:
    """Select the best feasible solution (minimum F) with tolerance.

    Accepts single-solution or population outputs from pymoo:
    - Single solution: X shape (n_vars,), F scalar or shape (1,), G scalar or (n_constraints,)
    - Population: X shape (n_solutions, n_vars), F shape (n_solutions,),
                  G shape (n_solutions,) or (n_solutions, n_constraints)

    Returns:
    - x_best: np.ndarray of shape (n_vars,)
    - f_best: float
    - feasible: bool (True if the selected solution satisfies G <= tol)
    - index: int (index within population; 0 for single solution)
    """
    X_np = np.array(X)
    F_np = np.array(F)
    G_np = None if G is None else np.array(G)

    # Detect single-solution case
    single_solution = (X_np.ndim == 1) or (F_np.ndim == 0) or (F_np.size == 1)

    if single_solution:
        # Normalize F scalar
        f_val = float(F_np.reshape(-1)[0])
        # Feasibility check
        feasible = True if G_np is None else is_feasible(G_np, tol)
        return X_np.reshape(-1), f_val, feasible, 0

    # Population case
    # Ensure shapes: F is (n_solutions,), X is (n_solutions, n_vars)
    if F_np.ndim != 1:
        F_np = F_np.reshape(F_np.shape[0])
    if X_np.ndim != 2:
        X_np = X_np.reshape(X_np.shape[0], -1)

    # Build feasibility mask
    if G_np is None:
        feas_mask = np.ones_like(F_np, dtype=bool)
    else:
        feas_mask = _feas_mask_from_G(G_np, tol)

    if not np.any(feas_mask):
        # No feasible solution found; return the best overall for recovery
        idx = int(np.argmin(F_np))
        return X_np[idx], float(F_np[idx]), False, idx

    # Choose feasible with minimal objective
    feasible_indices = np.nonzero(feas_mask)[0]
    local_best = int(np.argmin(F_np[feasible_indices]))
    idx = int(feasible_indices[local_best])
    return X_np[idx], float(F_np[idx]), True, idx


def recompute_objective(x: Any, obj_func: Callable[[np.ndarray], float]) -> float:
    """Recompute objective from decision vector x using the provided callable."""
    x_np = np.array(x, dtype=float).reshape(-1)
    return float(obj_func(x_np))
