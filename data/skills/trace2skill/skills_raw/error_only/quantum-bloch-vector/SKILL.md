---
name: quantum-bloch-vector
description: "Calculate Bloch vector components from quantum state angles (theta, phi) in radians."
---

# Bloch Sphere Vector Calculation

## When to Use

- Calculate Bloch vector from quantum state angles
- Convert spherical coordinates to Cartesian
- Analyze quantum state representation

## Input Format

File `/root/input.txt`:
```
theta phi
```
- theta: 0-180 degrees
- phi: 0-360 degrees

## Bloch Vector Components

- rx = sin(θ) × cos(φ)
- ry = sin(θ) × sin(φ)
- rz = cos(θ)

Convert degrees to radians first!

## Output Format

To `/root/output.txt`:
```
rx: +0.XXX
ry: +0.XXX
rz: +0.XXX
```

Round to 3 decimal places. Include sign (+/-).

## Tips

- Use math.sin, math.cos with radians conversion
- Convert deg to rad: rad = deg × π/180
- Format with explicit sign (+0.XXX)
