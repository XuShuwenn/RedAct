#!/usr/bin/env python3
"""
Compute the signed dihedral (torsion) angle from four 3D points.

Usage:
  python dihedral_tools.py --file input.txt
  python dihedral_tools.py --values x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4

Output:
  Dihedral angle: XX.XX degrees

Implements a robust arctan2-based signed torsion calculation:
  b1 = p2 - p1
  b2 = p3 - p2
  b3 = p4 - p3
  n1 = b1 x b2
  n2 = b2 x b3
  u = b2 / ||b2||
  m1 = n1 x u
  angle = atan2(m1 · n2, n1 · n2) in radians
"""

import sys
import math
import argparse
from typing import Tuple, List

Vec3 = Tuple[float, float, float]


def sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])


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


def normalize(a: Vec3, eps: float = 1e-15) -> Vec3:
    n = norm(a)
    if n < eps:
        return (0.0, 0.0, 0.0)
    return (a[0]/n, a[1]/n, a[2]/n)


def dihedral_angle_deg(p1: Vec3, p2: Vec3, p3: Vec3, p4: Vec3) -> float:
    """Return signed dihedral angle in degrees, in [-180, 180]."""
    b1 = sub(p2, p1)
    b2 = sub(p3, p2)
    b3 = sub(p4, p3)

    n1 = cross(b1, b2)
    n2 = cross(b2, b3)

    u = normalize(b2)
    m1 = cross(n1, u)

    x = dot(n1, n2)
    y = dot(m1, n2)

    angle_rad = math.atan2(y, x)
    angle_deg = math.degrees(angle_rad)

    # Normalize to [-180, 180] exactly (atan2 already does this, but keep for safety)
    if angle_deg > 180.0:
        angle_deg -= 360.0
    elif angle_deg <= -180.0:
        angle_deg += 360.0

    # Avoid negative zero in formatting
    if abs(angle_deg) < 0.005:
        angle_deg = 0.0

    return round(angle_deg, 2)


def parse_file(path: str) -> List[Vec3]:
    pts: List[Vec3] = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            try:
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
            except ValueError:
                raise ValueError(f"Invalid coordinate line: {line.strip()}")
            pts.append((x, y, z))
            if len(pts) == 4:
                break
    if len(pts) != 4:
        raise ValueError("Expected four 3D points (one per line with x y z)")
    return pts


def parse_values(vals: List[str]) -> List[Vec3]:
    if len(vals) != 12:
        raise ValueError("--values requires exactly 12 numbers (x1 y1 z1 ... x4 y4 z4)")
    nums = list(map(float, vals))
    return [(nums[i], nums[i+1], nums[i+2]) for i in range(0, 12, 3)]


def main() -> None:
    ap = argparse.ArgumentParser(description="Signed dihedral (torsion) angle calculator")
    ap.add_argument('--file', type=str, help='Path to a file with four lines: x y z')
    ap.add_argument('--values', nargs='+', help='Twelve numbers: x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4')
    args = ap.parse_args()

    try:
        if args.file:
            p1, p2, p3, p4 = parse_file(args.file)
        elif args.values:
            p1, p2, p3, p4 = parse_values(args.values)
        else:
            # Fallback: read from stdin
            data = sys.stdin.read().strip().splitlines()
            if not data:
                ap.print_help()
                sys.exit(1)
            pts = []
            for line in data:
                if not line.strip():
                    continue
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                pts.append((float(parts[0]), float(parts[1]), float(parts[2])))
                if len(pts) == 4:
                    break
            if len(pts) != 4:
                raise ValueError("Expected four 3D points from stdin")
            p1, p2, p3, p4 = pts

        angle = dihedral_angle_deg(p1, p2, p3, p4)
        # Exact required output line format
        print(f"Dihedral angle: {angle:.2f} degrees")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
