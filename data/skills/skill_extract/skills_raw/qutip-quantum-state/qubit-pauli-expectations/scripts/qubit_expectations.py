#!/usr/bin/env python3
"""
Compute single-qubit Pauli expectation values from Bloch angles.

Usage:
  python scripts/qubit_expectations.py --theta-deg 90 --phi-deg 0 --output out.txt
  python scripts/qubit_expectations.py --input angles.txt --output out.txt

The output file will contain exactly:
  Sigma X: +0.XXX
  Sigma Y: +0.XXX
  Sigma Z: +0.XXX

If QuTiP is available, uses QuTiP state construction and expect().
Falls back to analytic Bloch formulas only if QuTiP is unavailable.
"""

import argparse
import math
import sys
from typing import Tuple

import numpy as np

try:
    from qutip import expect, sigmax, sigmay, sigmaz, spin_coherent, basis
    HAS_QUTIP = True
except Exception:
    HAS_QUTIP = False


def parse_args():
    p = argparse.ArgumentParser(description="Qubit Pauli expectations from Bloch angles")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--theta-deg", type=float, help="Theta in degrees (0..180)")
    p.add_argument("--phi-deg", type=float, help="Phi in degrees (0..360)")
    g.add_argument("--input", help="Path to file containing: theta phi (degrees)")
    p.add_argument("--output", required=True, help="Path to write formatted results")
    return p.parse_args()


def read_angles(args) -> Tuple[float, float]:
    if args.input:
        txt = open(args.input, "r").read().strip()
        parts = txt.split()
        if len(parts) != 2:
            raise ValueError("Input must contain two numbers: theta phi (degrees)")
        theta_deg, phi_deg = map(float, parts)
    else:
        if args.phi_degf is None:
            # Work around argparse: require both when using --theta-deg
            pass
        theta_deg = args.theta_deg
        phi_deg = args.phi_deg
    return float(theta_deg), float(phi_deg)


def bloch_expectations(theta_rad: float, phi_rad: float) -> Tuple[float, float, float]:
    """Analytic expectations for a pure qubit at Bloch angles (theta, phi)."""
    sx = math.sin(theta_rad) * math.cos(phi_rad)
    sy = math.sin(theta_rad) * math.sin(phi_rad)
    sz = math.cos(theta_rad)
    return sx, sy, sz


def qubit_state_qutip(theta_rad: float, phi_rad: float):
    """Construct |psi> in QuTiP if available."""
    # Prefer spin_coherent for S=1/2.
    try:
        return spin_coherent(1/2, theta_rad, phi_rad)
    except Exception:
        # Explicit construction: |psi> = cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>
        c0 = math.cos(theta_rad / 2.0)
        c1 = complex(math.cos(phi_rad), math.sin(phi_rad)) * math.sin(theta_rad / 2.0)
        ket0 = basis(2, 0)
        ket1 = basis(2, 1)
        psi = c0 * ket0 + c1 * ket1
        # Normalize defensively (should already be unit norm)
        norm = float(np.sqrt((psi.dag() * psi).full()[0, 0]).real)
        if norm > 0:
            psi = psi / norm
        return psi


def expectations_qutip(theta_rad: float, phi_rad: float) -> Tuple[float, float, float]:
    psi = qubit_state_qutip(theta_rad, phi_rad)
    sx = float(np.real(expect(sigmax(), psi)))
    sy = float(np.real(expect(sigmay(), psi)))
    sz = float(np.real(expect(sigmaz(), psi)))
    return sx, sy, sz


def clean_value(x: float, tol: float = 1e-12) -> float:
    # Clamp tiny numerical noise to zero and bound to [-1, 1]
    if abs(x) < tol:
        return 0.0
    # Guard against tiny drift beyond bounds
    if x > 1 and x - 1 < 1e-9:
        return 1.0
    if x < -1 and -1 - x < 1e-9:
        return -1.0
    return x


def main():
    args = parse_args()

    # argparse quirk: when using --theta-deg, require --phi-deg too
    if args.theta_deg is not None and args.phi_deg is None and not args.input:
        print("Error: --theta-deg requires --phi-deg", file=sys.stderr)
        sys.exit(2)

    theta_deg, phi_deg = read_angles(args)

    # Convert to radians
    theta = math.radians(theta_deg)
    phi = math.radians(phi_deg)

    # Prefer QuTiP path if available; otherwise use analytic expectations
    if HAS_QUTIP:
        try:
            sx, sy, sz = expectations_qutip(theta, phi)
        except Exception:
            sx, sy, sz = bloch_expectations(theta, phi)
    else:
        sx, sy, sz = bloch_expectations(theta, phi)

    # Clean values and format
    sx = clean_value(float(sx))
    sy = clean_value(float(sy))
    sz = clean_value(float(sz))

    with open(args.output, "w") as f:
        f.write(f"Sigma X: {sx:+.3f}\n")
        f.write(f"Sigma Y: {sy:+.3f}\n")
        f.write(f"Sigma Z: {sz:+.3f}\n")


if __name__ == "__main__":
    main()
