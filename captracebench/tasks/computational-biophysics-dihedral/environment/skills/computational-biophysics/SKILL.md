---
name: computational-biophysics
description: "Calculate protein dihedral angle (phi/psi) from atomic coordinates using the torsion formula. Use when computing backbone dihedral angles from atomic positions or validating protein geometry."
---

# Computational Biophysics: Protein Dihedral Angle

## Overview

Given four atoms defining a protein backbone dihedral angle (N-CA-C-N'), calculate the dihedral angle in degrees using the torsion formula.

## Dihedral Angle Formula

The dihedral angle is the angle between two planes:
- Plane 1: defined by atoms (N, CA, C)
- Plane 2: defined by atoms (CA, C, N')

Using vector cross products and dot product:

```
b1 = CA - N
b2 = C - CA
b3 = N' - C

# Normal to plane 1
n1 = cross(b1, b2)

# Normal to plane 2
n2 = cross(b2, b3)

# Torsion angle
m1 = cross(n1, n2)
x = dot(m1, b2 / |b2|)
y = dot(n1, n2)

angle = atan2(x, y)
degrees = angle * 180 / pi
```

Range: -180 to +180 degrees.

## Calculation

```python
import math

def parse_coords(lines, indices):
    return [tuple(map(float, lines[i].strip().split())) for i in indices]

def vec_sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def cross(u, v):
    return (
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    )

def dot(u, v):
    return u[0]*v[0] + u[1]*v[1] + u[2]*v[2]

def norm(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def dihedral(p0, p1, p2, p3):
    b1 = vec_sub(p1, p0)
    b2 = vec_sub(p2, p1)
    b3 = vec_sub(p3, p2)
    n1 = cross(b1, b2)
    n2 = cross(b2, b3)
    m1 = cross(n1, b2)
    x = dot(m1, (b2[0]/norm(b2), b2[1]/norm(b2), b2[2]/norm(b2)))
    y = dot(n1, n2)
    return math.degrees(math.atan2(x, y))

# Read input
with open("/root/input.txt") as f:
    lines = f.read().strip().split("\n")

p0, p1, p2, p3 = parse_coords(lines, [0, 1, 2, 3])

angle = dihedral(p0, p1, p2, p3)

# Output
with open("/root/output.txt", "w") as f:
    f.write(f"Dihedral angle: {angle:.2f} degrees\n")
```

## Output Format

```
Dihedral angle: XXX.XX degrees
```

Round to 2 decimal places. Range: -180 to +180 degrees.

## Key Reference

- Dihedral angle between planes (N, CA, C) and (CA, C, N')
- Use torsion formula with cross products and atan2
- Output in degrees