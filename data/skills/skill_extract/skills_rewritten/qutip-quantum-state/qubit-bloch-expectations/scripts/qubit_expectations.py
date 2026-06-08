#!/usr/bin/env python3
"""Compute qubit Pauli expectation values from Bloch angles using QuTiP.

Features:
- Builds |psi> = cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>
- Computes <sigma_x>, <sigma_y>, <sigma_z> via QuTiP expect()
- Optional analytic cross-check against Bloch vector (sin th cos ph, sin th sin ph, cos th)
- Formats outputs with explicit sign and 3 decimals

Usage examples:
  python scripts/qubit_expectations.py --theta-deg 90 --phi-deg 0
  echo "90 0" | python scripts/qubit_expectations.py --stdin
  python scripts/qubit_expectations.py --theta-deg 45 --phi-deg 30 --output /tmp/out.txt --verify

Exit codes:
  0 on success; non-zero on errors or verification failure (when --verify is set).
"""

import sys
import math
import argparse
from typing import Tuple, List

try:
    import numpy as np
    from qutip import basis, sigmax, sigmay, sigmaz, expect
except Exception as e:  # pragma: no cover
    print(f"ERROR: Required packages not available: {e}", file=sys.stderr)
    sys.exit(2)


def parse_angles_from_stdin() -> Tuple[float, float]:
    """Read a single line "theta phi" from stdin and return degrees as floats."""
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        raise ValueError("Expected two values: theta phi (degrees)")
    th_deg, ph_deg = float(data[0]), float(data[1])
    return th_deg, ph_deg


def build_ket_from_bloch(theta_rad: float, phi_rad: float):
    """Return a QuTiP ket for |psi> = cos(th/2)|0> + e^{i phi} sin(th/2)|1>."""
    a = math.cos(theta_rad / 2.0)
    b = math.sin(theta_rad / 2.0) * np.exp(1j * phi_rad)
    return a * basis(2, 0) + b * basis(2, 1)


def expectations_qubit(ket) -> List[float]:
    """Compute expectations of Pauli X, Y, Z for given ket. Returns real floats."""
    sx, sy, sz = sigmax(), sigmay(), sigmaz()
    vals = expect([sx, sy, sz], ket)
    # Coerce tiny imaginary parts due to numerical error
    out = []
    for v in vals:
        v_real = np.real_if_close(v, tol=1e-12)
        out.append(float(np.real(v_real)))
    return out


def bloch_vector_analytic(theta_rad: float, phi_rad: float) -> Tuple[float, float, float]:
    """Analytic Bloch vector components for a pure state at (theta, phi)."""
    s, c = math.sin(theta_rad), math.cos(theta_rad)
    return (s * math.cos(phi_rad), s * math.sin(phi_rad), c)


def fmt_signed_3(v: float) -> str:
    return f"{v:+0.3f}"


def main():
    p = argparse.ArgumentParser(description="Qubit expectations from Bloch angles using QuTiP")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--stdin", action="store_true", help="Read a single line: 'theta phi' from stdin (degrees)")
    src.add_argument("--theta-deg", type=float, help="Polar angle theta in degrees")
    p.add_argument("--phi-deg", type=float, help="Azimuthal angle phi in degrees (required if --theta-deg used)")
    p.add_argument("--verify", action="store_true", help="Cross-check with analytic Bloch vector")
    p.add_argument("--tol", type=float, default=1e-9, help="Verification absolute tolerance (default: 1e-9)")
    p.add_argument("--output", type=str, default=None, help="Optional output file path; otherwise prints to stdout")

    args = p.parse_args()

    try:
        if args.stdin:
            th_deg, ph_deg = parse_angles_from_stdin()
        else:
            if args.phi_deg is None:
                p.error("--phi-deg is required when --theta-deg is provided")
            th_deg, ph_deg = args.theta_deg, args.phi_deg
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    th = math.radians(th_deg)
    ph = math.radians(ph_deg)

    ket = build_ket_from_bloch(th, ph)

    # Optional normalization check (robust for debugging)
    norm = float((ket.dag() * ket).full()[0, 0].real)
    if not math.isfinite(norm) or abs(norm - 1.0) > 1e-12:
        print(f"ERROR: State not normalized (norm={norm})", file=sys.stderr)
        sys.exit(1)

    sx_val, sy_val, sz_val = expectations_qubit(ket)

    if args.verify:
        bx, by, bz = bloch_vector_analytic(th, ph)
        if not (abs(sx_val - bx) <= args.tol and abs(sy_val - by) <= args.tol and abs(sz_val - bz) <= args.tol):
            print(
                "ERROR: Analytic cross-check failed: "
                f"QuTiP=({sx_val:.12f},{sy_val:.12f},{sz_val:.12f}) vs "
                f"Analytic=({bx:.12f},{by:.12f},{bz:.12f}) with tol={args.tol}",
                file=sys.stderr,
            )
            sys.exit(1)

    lines = [
        f"Sigma X: {fmt_signed_3(sx_val)}",
        f"Sigma Y: {fmt_signed_3(sy_val)}",
        f"Sigma Z: {fmt_signed_3(sz_val)}",
    ]

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except Exception as e:
            print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n".join(lines))


if __name__ == "__main__":
    main()
