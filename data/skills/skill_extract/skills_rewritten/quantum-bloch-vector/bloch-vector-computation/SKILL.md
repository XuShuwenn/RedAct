---
name: bloch-vector-computation
description: "Compute Bloch sphere vector components (rx, ry, rz) from given angles with correct unit handling, rounding, and output formatting."
---

Bloch Vector Computation

Skill for converting Bloch angles (theta, phi) into Cartesian vector components (rx, ry, rz). It emphasizes unit handling (degrees vs radians), deterministic rounding, explicit sign formatting, and simple validation.

When to Use

- The user provides Bloch angles and asks for rx, ry, rz.
- The task requires a fixed output format with signed values and a specified decimal precision.
- You need a robust, repeatable procedure to parse angles from text files or strings and compute components.

Core Workflow

1. Parse angles from the input:
   - Extract two numeric values representing theta and phi.
   - Accept common layouts (comma-separated, whitespace-separated, or label-value lines).

2. Confirm units and convert:
   - If the task states degrees, convert degrees to radians before using trig functions.
   - radians = degrees × (π / 180).

3. Compute components:
   - rx = sin(theta) × cos(phi)
   - ry = sin(theta) × sin(phi)
   - rz = cos(theta)
   - Use double-precision floats for stable results.

4. Round and format deterministically:
   - Round each component to exactly 3 decimal places after computing.
   - Always include an explicit sign (+ or -) and three decimal digits (e.g., +0.000).
   - Use a consistent format specifier rather than ad hoc string operations.

5. Write output:
   - Produce exactly three lines in the required pattern:
     - rx: +0.XXX
     - ry: +0.XXX
     - rz: +0.XXX

Verification

- Unit check:
  - Validate that trigonometric functions receive radians. If the input is degrees, ensure conversion occurred.

- Magnitude (sanity) check:
  - Compute |r| = sqrt(rx^2 + ry^2 + rz^2). The Bloch vector is unit length; expect |r| ≈ 1.
  - Allow small deviation due to rounding (e.g., within 1e-3).

- Angle range awareness:
  - Typical ranges are theta in [0, 180] and phi in [0, 360]. Values outside these ranges are still computable using the formulas; flag if out-of-range but proceed.

- Output format consistency:
  - Ensure each line contains the correct label (rx/ry/rz), a colon, a space, and a signed value with exactly three decimals.
  - Confirm trailing zeros are present after rounding.

Common Pitfalls

- Forgetting degree-to-radian conversion before using sin/cos.
- Rounding inputs (theta, phi) early instead of rounding the final components.
- Omitting the explicit plus sign for positive values or producing inconsistent decimal places.
- Swapping formulas (e.g., using cos(phi) for rz) or mixing theta/phi.
- Failing to parse inputs containing labels or mixed separators, causing missing or misread angles.
- Writing extra lines, different labels, or different spacing than required, leading to format mismatches.

Success Criteria

- Components are computed from the provided angles using the correct formulas.
- Output values are rounded to exactly three decimal places and include explicit signs.
- The vector magnitude is approximately 1 within a small tolerance.
- The output consists of exactly three correctly labeled lines.

Optional Script Usage

- Use the helper script to parse angles from a file, compute components, validate magnitude, and write formatted output.
- Example invocation:
  - python scripts/bloch_vector.py input.txt output.txt
  - By default, the script assumes angles are in degrees and converts to radians internally.
