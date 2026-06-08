#!/usr/bin/env python3
"""Helper utilities for robust steady-state computation and Wigner I/O in QuTiP.

These functions are generic and can be reused across open-quantum simulation tasks.
They aim to prevent common solver, dimension, and output pitfalls.
"""
from __future__ import annotations

import sys
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np

try:
    import qutip as qt
except Exception as e:  # pragma: no cover
    qt = None
    _import_error = e
else:
    _import_error = None


def _require_qutip():
    if qt is None:
        raise RuntimeError(f"QuTiP not available: {_import_error}")


def make_grid(xmin: float, xmax: float, n: int) -> np.ndarray:
    """Return an evenly spaced 1D grid from xmin to xmax with n points."""
    return np.linspace(float(xmin), float(xmax), int(n))


def check_density_matrix(rho: 'qt.Qobj', atol: float = 1e-8) -> dict:
    """Return density-matrix validity diagnostics.

    - hermitian: bool
    - trace_close: bool
    - trace: float
    - min_eig: float (may be slightly <0 due to numerical noise)
    """
    _require_qutip()
    out = {}
    # Hermiticity
    herm = (rho - rho.dag()).norm() <= atol
    out["hermitian"] = herm
    # Trace
    tr = float((rho.tr()).real)
    out["trace"] = tr
    out["trace_close"] = abs(tr - 1.0) <= max(atol, 10 * np.finfo(float).eps)
    # Positivity (min eigenvalue)
    try:
        # For speed on small dims, dense eig is fine; for larger cases, use sparse eigs carefully
        evals = np.linalg.eigvalsh(rho.full())
        min_eig = float(np.min(evals).real)
    except Exception:
        # Fallback: Rayleigh quotient bound via random probes
        v = np.random.default_rng(0).standard_normal((rho.shape[0], 4)) + 1j * np.random.default_rng(1).standard_normal((rho.shape[0], 4))
        v = v / np.linalg.norm(v, axis=0, keepdims=True)
        min_eig = float(np.min([np.vdot(vi, (rho.full() @ vi)).real for vi in v.T]))
    out["min_eig"] = min_eig
    return out


def liouvillian_residual(H: 'qt.Qobj', c_ops: Sequence['qt.Qobj'], rho: 'qt.Qobj') -> float:
    """Compute ||L vec(rho)||_2 / ||vec(rho)||_2 as a steady-state residual.

    Smaller is better; target values depend on tolerance (e.g., <1e-8).
    """
    _require_qutip()
    L = qt.liouvillian(H, c_ops)
    vec_rho = qt.operator_to_vector(rho)
    resid = (L * vec_rho).norm() / max(vec_rho.norm(), 1e-30)
    return float(resid)


def _steadystate_attempt(H: 'qt.Qobj', c_ops: Sequence['qt.Qobj'], method: str,
                         tol: float, maxiter: int, use_rcm: bool) -> Optional['qt.Qobj']:
    """Try a single steadystate method; return rho or None on failure."""
    try:
        rho = qt.steadystate(H, c_ops,
                             method=method,
                             use_rcm=use_rcm,
                             tol=tol,
                             maxiter=maxiter)
        return rho
    except Exception:
        return None


def solve_steadystate_with_fallback(H: 'qt.Qobj', c_ops: Sequence['qt.Qobj'],
                                    methods: Optional[Iterable[str]] = None,
                                    tol: float = 1e-10,
                                    maxiter: int = 20000,
                                    use_rcm: bool = True,
                                    mesolve_fallback: bool = True,
                                    mesolve_T: float = 50.0,
                                    mesolve_steps: int = 2000,
                                    progress: bool = True) -> 'qt.Qobj':
    """Robust steady-state solver with method cycling and mesolve fallback.

    - methods: candidate steadystate methods in order. If None, try a robust default set.
    - tol/maxiter/use_rcm: solver options for iterative methods (ignored by some direct solvers).
    - mesolve_fallback: if all steadystate methods fail, evolve to long time and return the last state.
    - mesolve_T/mesolve_steps: total time and steps for mesolve fallback.

    Returns: rho_ss (Qobj density matrix).
    Raises: RuntimeError if no method succeeds and fallback is disabled.
    """
    _require_qutip()
    if methods is None:
        # Try direct/dense first for small problems, then iterative variants for larger ones.
        methods = (
            "direct",
            "eigen",
            "iterative-lgmres",
            "iterative-gmres",
            "iterative-bicg",
        )

    # Cycle through methods
    for m in methods:
        rho = _steadystate_attempt(H, c_ops, m, tol=tol, maxiter=maxiter, use_rcm=use_rcm)
        if rho is not None:
            if progress:
                print(f"[steadystate] Succeeded with method='{m}'", file=sys.stderr)
            return rho
        else:
            if progress:
                print(f"[steadystate] Method '{m}' failed; trying next...", file=sys.stderr)

    if not mesolve_fallback:
        raise RuntimeError("All steadystate methods failed and mesolve_fallback is disabled.")

    # mesolve fallback: evolve to long time
    if progress:
        print("[mesolve-fallback] Starting time evolution to approach steady state...", file=sys.stderr)
    # Initial state: vacuum ⊗ maximally mixed (or identity/dim). Use identity/dim for generality.
    H_dim = H.shape[0]
    rho0 = qt.qeye(H_dim) / H_dim
    tlist = np.linspace(0.0, float(mesolve_T), int(mesolve_steps))
    out = qt.mesolve(H, rho0, tlist, c_ops, [])
    rho = out.states[-1]
    if progress:
        print("[mesolve-fallback] Completed time evolution; returning final state.", file=sys.stderr)
    return rho


def fix_hermitian_trace(rho: 'qt.Qobj') -> 'qt.Qobj':
    """Symmetrize and renormalize to mitigate small numerical non-Hermiticity/trace drift."""
    _require_qutip()
    rho_h = 0.5 * (rho + rho.dag())
    tr = (rho_h.tr()).real
    if abs(tr) < 1e-30:
        return rho_h
    return rho_h / tr


def save_wigner_matrix_csv(W: np.ndarray, path: str, delimiter: str = ",") -> None:
    """Save a Wigner matrix (2D numeric array) as a numeric-only CSV.

    This avoids headers/metadata to match strict formats that expect raw grids.
    """
    if W.ndim != 2:
        raise ValueError("W must be a 2D array")
    np.savetxt(path, W, delimiter=delimiter)


def example_checklist_print(H: 'qt.Qobj', c_ops: Sequence['qt.Qobj'], rho: 'qt.Qobj',
                            cavity_dim: Optional[int] = None,
                            cavity_index: int = 0,
                            wigner_shape: Optional[Tuple[int, int]] = None) -> None:
    """Print diagnostics to help validate results against the skill's checks."""
    _require_qutip()
    try:
        res = liouvillian_residual(H, c_ops, rho)
        print(f"Residual ||L vec(rho)||/||vec(rho)|| = {res:.3e}")
    except Exception as e:
        print(f"Residual computation failed: {e}")

    try:
        dm = check_density_matrix(rho)
        print(f"Hermitian={dm['hermitian']} Trace≈1={dm['trace_close']} (trace={dm['trace']:.6f}) min_eig={dm['min_eig']:.3e}")
    except Exception as e:
        print(f"DM checks failed: {e}")

    if cavity_dim is not None:
        try:
            # Ensure dims set; if not, ptrace may fail. User must set dims consistently upstream.
            rho_sub = qt.ptrace(rho, cavity_index)
            ok_dim = (rho_sub.shape[0] == cavity_dim)
            print(f"Cavity ptrace: dim_ok={ok_dim} (dim={rho_sub.shape[0]})")
        except Exception as e:
            print(f"ptrace check failed: {e}")

    if wigner_shape is not None:
        print(f"Expected Wigner shape: {wigner_shape}")


if __name__ == "__main__":  # pragma: no cover
    # Lightweight self-check on import environment
    if qt is None:
        print(f"QuTiP import failed: {_import_error}", file=sys.stderr)
        sys.exit(1)
    print("steadystate_helpers.py: QuTiP detected. Utilities are ready.")
