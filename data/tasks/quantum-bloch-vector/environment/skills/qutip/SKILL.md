---
name: qutip
description: "Calculate Bloch vector components from spherical coordinates (theta, phi). Use when converting Bloch sphere angles to Cartesian coordinates, or working with quantum state geometry."
---

# Quantum Bloch Vector from Spherical Coordinates

## Overview

Given a quantum state on the Bloch sphere with polar angle θ and azimuthal angle φ, compute the Cartesian Bloch vector components (rx, ry, rz).

## Bloch Sphere Geometry

The Bloch sphere represents a pure qubit state as a point on a unit sphere:
- Polar angle θ (0 to π): angle from the +z axis
- Azimuthal angle φ (0 to 2π): angle in the xy-plane from +x axis

## Bloch Vector Components

```
rx = sin(θ) × cos(φ)
ry = sin(θ) × sin(φ)
rz = cos(θ)
```

Where θ and φ are in degrees.

## Calculation

```python
import math

# Read theta and phi in degrees
with open("/root/input.txt") as f:
    theta_deg, phi_deg = map(float, f.read().strip().split())

# Convert to radians
theta = math.radians(theta_deg)
phi = math.radians(phi_deg)

# Compute Bloch vector components
rx = math.sin(theta) * math.cos(phi)
ry = math.sin(theta) * math.sin(phi)
rz = math.cos(theta)

# Output with 3 decimal places and explicit sign
with open("/root/output.txt", "w") as f:
    f.write(f"rx: {rx:+.3f}\n")
    f.write(f"ry: {ry:+.3f}\n")
    f.write(f"rz: {rz:+.3f}\n")
```

## Output Format

```
rx: +0.XXX
ry: +0.XXX
rz: +0.XXX
```

Round to 3 decimal places. Always show explicit sign (+/-).

## Key Reference

- θ (theta): polar angle from +z axis, range 0 to 180 degrees
- φ (phi): azimuthal angle from +x axis, range 0 to 360 degrees
- |r| = sqrt(rx² + ry² + rz²) = 1 for pure states

## Examples

| θ | φ | rx | ry | rz |
|---|---|----|----|----|
| 0° | 0° | 0 | 0 | +1 |
| 90° | 0° | +1 | 0 | 0 |
| 90° | 90° | 0 | +1 | 0 |
| 180° | 0° | 0 | 0 | -1 |