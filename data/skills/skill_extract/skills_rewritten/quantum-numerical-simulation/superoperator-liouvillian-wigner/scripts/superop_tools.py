#!/usr/bin/env python3
"""Superoperator and Wigner utilities for robust open-system workflows.

Functions:
- commutator_super(H): build -i[H, ·] as a superoperator
- validate_density_matrix(rho, tol=1e-7): basic validity checks
- chunked_wigner_to_csv(rho, xvec, pvec, filepath, chunk=64, method=None, fmt='%.10e'): compute Wigner in chunks and stream to CSV

These helpers are generic and avoid task-specific constants.
"""

from typing import Optional, Dict, Any
import numpy as np

try:
    import qutip as qt
except Exception as exc:
    raise RuntimeError("This helper requires QuTiP (qutip) to be installed.") from exc


def commutator_super(H: qt.Qobj) -> qt.Qobj:
    """Return the commutator superoperator -i[H, ·].
    H must be a Hilbert-space operator (type 'oper').
    The result is a superoperator (type 'super').
    """
    if not isinstance(H, qt.Qobj) or H.type != 'oper':
        raise ValueError("commutator_super expects a Hilbert-space operator (Qobj type 'oper').")
    return -1j * (qt.spre(H) - qt.spost(H))


def validate_density_matrix(rho: qt.Qobj, tol: float = 1e-7) -> Dict[str, Any]:
    """Check basic density matrix properties: hermiticity, trace ~ 1, positivity.
    Returns a dict with booleans and diagnostics for quick verification.
    """
    if not isinstance(rho, qt.Qobj) or rho.type != 'oper':
        raise ValueError("validate_density_matrix expects a Hilbert-space operator (density matrix).")

    # Hermiticity
    diff = (rho - rho.dag()).full()
    herm_err = np.linalg.norm(diff, ord='fro')
    is_hermitian = herm_err <= tol

    # Trace ~ 1
    tr = float(rho.tr())
    trace_err = abs(tr - 1.0)
    trace_ok = trace_err <= tol

    # Positivity (allow tiny negative eigenvalues due to numerical error)
    evals = np.linalg.eigvalsh(rho.full())
    min_eval = float(np.min(evals))
    pos_ok = min_eval >= -10 * tol

    return {
        "is_hermitian": is_hermitian,
        "hermiticity_error": herm_err,
        "trace": tr,
        "trace_ok": trace_ok,
        "trace_error": trace_err,
        "min_eigenvalue": min_eval,
        "positive_semidefinite": pos_ok,
    }


def chunked_wigner_to_csv(
    rho: qt.Qobj,
    xvec: np.ndarray,
    pvec: np.ndarray,
    filepath: str,
    chunk: int = 64,
    method: Optional[str] = None,
    fmt: str = "%.10e",
) -> Dict[str, Any]:
    """Compute Wigner(rho, xvec, pvec) in column chunks and stream to CSV.

    - Processes x in segments of size `chunk` to reduce memory usage.
    - Writes each computed row to `filepath` immediately.
    - Returns metadata about the write.

    Parameters:
        rho: density matrix (Hilbert space Qobj) of the target mode.
        xvec, pvec: 1D arrays of phase-space coordinates.
        filepath: output CSV path.
        chunk: number of x points to compute per block.
        method: optional method string supported by the toolkit's wigner function.
        fmt: format for numeric output.

    Returns:
        dict with keys: rows_written, cols, chunks, dtype, method
    """
    if not isinstance(rho, qt.Qobj) or rho.type != 'oper':
        raise ValueError("chunked_wigner_to_csv expects a Hilbert-space density matrix (Qobj type 'oper').")
    xvec = np.asarray(xvec, dtype=float)
    pvec = np.asarray(pvec, dtype=float)
    if xvec.ndim != 1 or pvec.ndim != 1:
        raise ValueError("xvec and pvec must be 1D arrays.")

    rows_written = 0
    cols = pvec.size
    blocks = 0

    with open(filepath, "w") as f:
        for start in range(0, xvec.size, chunk):
            stop = min(start + chunk, xvec.size)
            xs = xvec[start:stop]
            # Compute a block of the Wigner function.
            W_block = qt.wigner(rho, xs, pvec, method=method)
            # Ensure array shape is (len(xs), len(pvec))
            W_block = np.asarray(W_block)
            if W_block.shape != (xs.size, pvec.size):
                raise RuntimeError(
                    f"Unexpected Wigner block shape {W_block.shape}; expected ({xs.size}, {pvec.size})."
                )
            # Stream rows
            for k in range(W_block.shape[0]):
                line = ",".join(format(val, fmt) for val in W_block[k])
                f.write(line + "\n")
                rows_written += 1
            f.flush()
            blocks += 1

    return {
        "rows_written": rows_written,
        "cols": cols,
        "chunks": blocks,
        "dtype": str(W_block.dtype),
        "method": method or "default",
    }
