---
name: quantum-bloch-vector
description: "Calculate Bloch vector components from quantum state angles (theta, phi) in radians."
---

# Bloch Sphere Vector Calculation

## When to Use

- Calculate Bloch vector from quantum state angles provided in `/root/input.txt`
- Convert the given degree inputs `(theta, phi)` to Cartesian Bloch components
- Analyze quantum state representation using the standard Bloch-vector formulas

## Input Format

File `/root/input.txt`:
```
theta phi
```
- theta: polar angle in degrees (typically 0-180)
- phi: azimuthal angle in degrees (typically 0-360)

Read exactly two whitespace-separated numbers from `/root/input.txt` before doing any computation, in this order: `theta phi`.
Use the exact values from the file as the only source of truth. Interpret the first value as `theta` and the second as `phi`; do not swap them, and do not guess, hardcode, or infer substitute values.
Treat both input angles as degrees when read from the file, then convert each to radians exactly once before calling trig functions.

## Bloch Vector Components

- rx = sin(θ) × cos(φ)
- ry = sin(θ) × sin(φ)
- rz = cos(θ)

The input angles are given in degrees. Convert `theta` and `phi` to radians before calling trig functions, e.g. with `math.radians(...)`. Apply these formulas directly after conversion; do not reorder inputs, add extra transformations, or substitute alternate coordinate conventions. Keep full precision during computation and round only when formatting the final output.
## File Check

- In file-based tasks, quickly inspect `/root` first so you use the authoritative input and output paths actually present.
- Read `/root/input.txt` before computing anything; do not infer values from the prompt or from examples in this skill.
- Treat `/root/input.txt` as the source of truth for `theta phi`, and write the result only to `/root/output.txt`.


## Workflow

1. Read exactly two whitespace-separated numbers from `/root/input.txt` first, in order: `theta phi`.
2. Convert both angles from degrees to radians.
3. Compute `rx`, `ry`, and `rz` using the formulas above from those exact inputs.
4. Keep full precision during computation and round only when formatting the final output.
5. Write `/root/output.txt` with labels `rx:`, `ry:`, `rz:` in that order, using explicit signs and exactly 3 decimal places.
6. Re-open or inspect the saved output and verify labels, order, signs, and rounding before finishing.

   - Confirm the file contains exactly three lines and nothing else.


7. Before finishing, do a quick sanity check: confirm you used the two parsed inputs in order (`theta`, then `phi`), converted degrees to radians, and applied the standard formulas directly without extra transformations.
8. Prefer one small Python script that reads `/root/input.txt`, computes all three components, writes `/root/output.txt`, and then reads the file back for a final check.
9. If helpful, use standard-angle checks to catch mistakes: if `theta = 0`, expect `rz ≈ +1`; if `theta = 180`, expect `rz ≈ -1`; if `theta = 90`, expect `rz ≈ 0` and `rx`,`ry` to follow `phi`.
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


- Preserve the computed sign when formatting each value, including near-zero results (for example `+0.000` when appropriate).

## Tips

- Use math.sin, math.cos with radians conversion
- Convert deg to rad: rad = deg × π/180
- Format with explicit sign (+0.XXX)

- Prefer a single small Python script to read `/root/input.txt`, compute all three components, and write `/root/output.txt` in one pass
- Use `math.radians(theta)` and `math.radians(phi)` before calling `math.sin` or `math.cos`
- Do not compute from guessed defaults; always use the exact values read from `/root/input.txt`
- If `theta` or `phi` is a standard angle (for example 0°, 45°, 90°, 180°), use known exact trig values as a quick sanity check when helpful
- After writing the file, read `/root/output.txt` back once to confirm line order, labels, signed formatting, and 3-decimal rounding

- Treat exact output text as part of the task: preserve labels, line order, explicit signs, and fixed 3-decimal formatting exactly
- Start from the files on disk, not assumptions: confirm the workspace contents, then read `/root/input.txt` as the authoritative source before computing anything

