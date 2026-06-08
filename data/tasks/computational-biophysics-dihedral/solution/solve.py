#!/usr/bin/env python3
"""Solve computational-biophysics-dihedral task."""

import math

def vec_sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def vec_cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )

def vec_dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def vec_norm(a):
    return math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])

def dihedral(p0, p1, p2, p3):
    """Calculate dihedral angle between four points."""
    b1 = vec_sub(p1, p0)
    b2 = vec_sub(p2, p1)
    b3 = vec_sub(p3, p2)

    n1 = vec_cross(b1, b2)
    n2 = vec_cross(b2, b3)

    norm_n1 = vec_norm(n1)
    norm_n2 = vec_norm(n2)

    if norm_n1 < 1e-10 or norm_n2 < 1e-10:
        return 0.0

    n1 = (n1[0]/norm_n1, n1[1]/norm_n1, n1[2]/norm_n1)
    n2 = (n2[0]/norm_n2, n2[1]/norm_n2, n2[2]/norm_n2)

    m1 = vec_cross(n1, b2)
    x = vec_dot(n1, n2)
    y = vec_dot(m1, n2)

    angle = math.atan2(y, x)
    return math.degrees(angle)

def main():
    with open("/root/input.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    p0 = tuple(map(float, lines[0].split()))  # N
    p1 = tuple(map(float, lines[1].split()))  # CA
    p2 = tuple(map(float, lines[2].split()))  # C
    p3 = tuple(map(float, lines[3].split()))  # N'

    angle = dihedral(p0, p1, p2, p3)

    result = f"Dihedral angle: {angle:.2f} degrees\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()