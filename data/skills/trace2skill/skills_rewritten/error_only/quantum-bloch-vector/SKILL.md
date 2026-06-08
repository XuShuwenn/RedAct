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
- theta: angle in degrees (typically 0-180)
- phi: angle in degrees (typically 0-360)

Read exactly two whitespace-separated numbers from `/root/input.txt` first, in this order: `theta phi`.
Do not swap them, and do not guess or hardcode example values.

## Bloch Vector Components

- rx = sin(θ) × cos(φ)
- ry = sin(θ) × sin(φ)
- rz = cos(θ)

The input angles are given in degrees. Convert `theta` and `phi` to radians before calling trig functions, e.g. with `math.radians(...)`. Apply these formulas directly after conversion; do not reorder inputs, add extra transformations, or substitute alternate coordinate conventions. Keep full precision during computation and round only when formatting the final output.


## New Section

## Workflow

1. Read `theta` and `phi` from `/root/input.txt`.
2. Convert both angles from degrees to radians.
3. Compute `rx`, `ry`, and `rz` using the formulas above.
4. Keep full precision during computation and round only when formatting the final output.
5. Write `/root/output.txt` with labels `rx:`, `ry:`, `rz:` in that order, using explicit signs and exactly 3 decimal places.
6. Re-open or inspect the saved output and verify labels, order, signs, and rounding before finishing.
## Output Format

To `/root/output.txt`:
```
rx: +0.XXX
ry: +0.XXX
rz: +0.XXX
```

Round to 3 decimal places. Include sign (+/-).

- Write only those three lines to `/root/output.txt`, preserving labels, order, explicit `+`/`-` signs, and exactly 3 decimal places.
- Use signed fixed-point formatting such as `{value:+.3f}` for each component.

## Tips

- Use math.sin, math.cos with radians conversion
- Convert deg to rad: rad = deg × π/180
- Format with explicit sign (+0.XXX)

- Prefer a single small Python script to read `/root/input.txt`, compute all three components, and write `/root/output.txt` in one pass
- Use `math.radians(theta)` and `math.radians(phi)` before calling `math.sin` or `math.cos`
- Do not compute from guessed defaults; always use the exact values read from `/root/input.txt`
- If `theta` or `phi` is a standard angle (for example 0°, 45°, 90°, 180°), use known exact trig values as a quick sanity check when helpful
- After writing the file, read `/root/output.txt` back once to confirm line order, labels, signed formatting, and 3-decimal rounding
