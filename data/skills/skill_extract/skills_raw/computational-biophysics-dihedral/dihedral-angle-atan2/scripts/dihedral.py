#!/usr/bin/env python3
"""
Compute the signed dihedral (torsion) angle from four 3D points.

Usage:
  - From a file with four lines of "x y z":
      python dihedral.py --file input.txt [--out output.txt] [--precision 2]
  - From 12 numeric arguments (x0 y0 z0 x1 y1 z1 x2 y2 z2 x3 y3 z3):
      python dihedral.py x0 y0 z0 x1 y1 z1 x2 y2 z2 x3 y3 z3 [--precision 2]

Outputs the angle in degrees in the range [-180, 180]. If --out is provided,
writes a single line: "Dihedral angle: XX.XX degrees".
"""

import sys
import math
import argparse
from typing import Tuple, List

Vec3 = Tuple[float, float, float]


def sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a: Vec3, b: Vec3) -> float:
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )


def norm(a: Vec3) -> float:
    return math.sqrt(dot(a, a))


def dihedral_deg(p0: Vec3, p1: Vec3, p2: Vec3, p3: Vec3, eps: float = 1e-12) -> float:
    """Return the signed dihedral angle (degrees) in [-180, 180].

    Uses robust atan2 formulation:
        b0 = p1 - p0; b1 = p2 - p1; b2 = p3 - p2
        n1 = b0 x b1; n2 = b1 x b2
        x = n1^ · n2^
        y = (n1^ x b1^) · n2^
        phi = atan2(y, x)
    where ^ denotes unit vectors.
    """
    b0 = sub(p1, p0)
    b1 = sub(p2, p1)
    b2 = sub(p3, p2)

    b1_len = norm(b1)
    if b1_len < eps:
        raise ValueError("Central bond vector has near-zero length; dihedral undefined.")

    n1 = cross(b0, b1)
    n2 = cross(b1, b2)
    n1_len = norm(n1)
    n2_len = norm(n2)

    if n1_len < eps or n2_len < eps:
        # Degenerate geometry: planes ill-defined. By convention we return 0.0,
        # but callers may choose to handle this as an error instead.
        return 0.0

    # Normalize
    b1u = (b1[0]/b1_len, b1[1]/b1_len, b1[2]/b1_len)
    n1u = (n1[0]/n1_len, n1[1]/n1_len, n1[2]/n1_len)
    n2u = (n2[0]/n2_len, n2[1]/n2_len, n2[2]/n2_len)

    x = dot(n1u, n2u)
    m1 = cross(n1u, b1u)
    y = dot(m1, n2u)

    angle = math.degrees(math.atan2(y, x))

    # Wrap to [-180, 180]
    if angle > 180.0:
        angle -= 360.0
    if angle <= -180.0:
        # Keep -180 as-is to stay within the closed interval; adjust only if below
        if angle < -180.0:
            angle += 360.0
    return angle


def parse_file(path: str) -> List[Vec3]:
    pts: List[Vec3] = []
    with open(path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            try:
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
            except ValueError:
                raise ValueError(f"Non-numeric coordinate in line: {line.strip()}")
            pts.append((x, y, z))
            if len(pts) == 4:
                break
    if len(pts) != 4:
        raise ValueError("Expected four 3D points (one per line).")
    return pts


def format_output(angle: float, precision: int = 2) -> str:
    fmt = f"{{angle:.{precision}f}}"
    return f"Dihedral angle: {fmt.format(angle=angle)} degrees"


def main():
    parser = argparse.ArgumentParser(description="Compute signed dihedral (torsion) angle from four 3D points.")
    parser.add_argument('--file', help='Input file with four lines: x y z')
    parser.add_argument('--out', help='Optional output file to write formatted result')
    parser.add_argument('--precision', type=int, default=2, help='Decimal places for output (default: 2)')
    parser.add_argument('coords', nargs='*', help='12 numbers: x0 y0 z0 x1 y1 z1 x2 y2 z2 x3 y3 z3')
    args = parser.parse_args()

    if args.file:
        pts = parse_file(args.file)
    else:
        if len(args.coords) == 12:
            try:
                vals = [float(c) for c in args.coords]
            except ValueError:
                print("ERROR: All coordinates must be numeric.", file=sys.stderr)
                sys.exit(1)
            pts = [(vals[i], vals[i+1], vals[i+2]) for i in range(0, 12, 3)]
        else:
            parser.print_help()
            sys.exit(1)

    try:
        angle = dihedral_deg(*pts)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Print numeric angle and optionally formatted line
    print(f"Angle (deg): {angle:.{args.precision}f}")

    if args.out:
        line = format_output(angle, precision=args.precision)
        with open(args.out, 'w') as f:
            f.write(line + "\n")
        # Also echo the line for visibility
        print(line)


if __name__ == '__main__':
    main()
