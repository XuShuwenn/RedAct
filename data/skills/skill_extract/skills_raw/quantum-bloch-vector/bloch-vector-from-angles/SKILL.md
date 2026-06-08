---
name: bloch-vector-from-angles
description: "Convert Bloch angles (theta, phi) in degrees to Bloch vector components and write signed, rounded results."
---

# Bloch Vector from Angles

Skill to read Bloch sphere angles (theta, phi) given in degrees, compute the Cartesian Bloch vector components (rx, ry, rz), and write the results in a strict, signed, three-decimal format.

## When to Use

- The task provides Bloch angles (theta, phi) and asks for the corresponding Cartesian components (rx, ry, rz).
- Output requires fixed formatting with signs and three decimal places.
- Inputs are provided via a file (commonly /root/input.txt) and outputs must be written to a file (commonly /root/output.txt).

## Core Workflow

1. Ingest angles
   - Read the input file containing theta and phi in degrees.
   - Prefer labeled parsing if present (e.g., "theta:", "phi:"), otherwise read the first two numeric values in order as theta, then phi.
   - Be tolerant of extra whitespace, line breaks, or degree symbols.

2. Convert units
   - Convert degrees to radians before trigonometric calculations.
   - Use math.radians for conversion.

3. Compute components
   - rx = sin(theta) * cos(phi)
   - ry = sin(theta) * sin(phi)
   - rz = cos(theta)

4. Stabilize tiny values
   - Values very close to zero can format as -0.000 due to floating error. Before formatting, set any |value| < epsilon (e.g., 1e-12) to exactly 0.0.

5. Format and write output
   - Round and format each component with an explicit sign and exactly three decimals.
   - Output lines in this exact order and format:
     - rx: +0.XXX
     - ry: +0.XXX
     - rz: +0.XXX
   - Ensure each line ends with a newline and the file contains exactly three lines.

6. (Optional) Angle normalization
   - If inputs may be out of range, normalize:
     - phi := phi mod 360
     - theta := theta mod 360; if theta > 180, set theta := 360 - theta
   - Normalization does not change the resulting Bloch direction.

## Verification

- Pre-round magnitude check (optional): compute r2 = rx^2 + ry^2 + rz^2 before zero-clamping/rounding; it should be close to 1 within numerical tolerance (e.g., |r2 - 1| <= 1e-12).
- Output format check:
  - Exactly three lines.
  - Each line matches the pattern: label, colon, space, signed number with three decimals.
  - Labels and order must be rx, ry, rz.
- Sign check:
  - Positive numbers must include a leading +.
  - Near-zero values should appear as +0.000 (or -0.000 avoided via zero-clamping).
- Determinism check:
  - Recompute with the same inputs to confirm identical outputs.

## Common Pitfalls

- Degrees vs radians: forgetting to convert degrees to radians before sin/cos.
- Swapping angles: interpreting the first number as phi and the second as theta. Use labels when available; otherwise assume first = theta, second = phi.
- Formatting errors:
  - Missing explicit plus sign for positive values.
  - Using fewer/more than three decimal places.
  - Writing labels out of order or with extra spaces/characters.
  - Omitting trailing newlines or producing extra lines.
- Negative zero: formatting very small negative numbers as -0.000. Zero-clamp small magnitudes before formatting.
- Fragile parsing: failing when inputs include labels, commas, or degree symbols. Use a numeric extraction approach that tolerates such noise.

## Success Criteria

- The output file contains exactly three lines with rx, ry, rz in order, each as a signed number with three decimals.
- The computed vector matches the trigonometric definitions with degree-to-radian conversion.
- No -0.000 appears; vector magnitude is ~1 pre-rounding within tolerance.

## Optional Script Usage

- Provided helper script: scripts/bloch_vector.py
- Example usage:
  - python scripts/bloch_vector.py --input /root/input.txt --output /root/output.txt
  - Optional normalization and epsilon for zero-clamping:
    - python scripts/bloch_vector.py --input /root/input.txt --output /root/output.txt --normalize --epsilon 1e-12
