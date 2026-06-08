---
name: compute-signed-dihedral
description: "Compute a signed dihedral (torsion) angle from four 3D coordinates and produce a precisely formatted result."
---

# Signed Dihedral (Torsion) Angle from Four 3D Points

Use this skill when given four Cartesian coordinates that define a torsion (e.g., protein backbone N–CA–C–N') and you must compute the dihedral angle in degrees with the correct sign and formatting.

## When to Use

Activate this skill for tasks that:
- Provide four 3D points (each as x y z) and ask for the dihedral/torsion angle
- Require the angle in degrees in the range [-180, 180]
- Specify strict output formatting and rounding (e.g., two decimals)

## Core Workflow

1. Parse Input
   - Expect four lines, each with three real numbers: x y z.
   - Robustly split on whitespace and parse floats.
   - Validate: exactly four points, each with three numbers.

2. Build Vectors (using the ordered points P1, P2, P3, P4)
   - b1 = P2 − P1
   - b2 = P3 − P2
   - b3 = P4 − P3

3. Compute Plane Normals and Signed Angle (arctan2 formulation)
   - n1 = b1 × b2
   - n2 = b2 × b3
   - u = b2 / ||b2||  (unit vector along b2)
   - m1 = n1 × u
   - x = n1 · n2
   - y = m1 · n2
   - angle_rad = atan2(y, x)
   - angle_deg = angle_rad × 180 / π
   - The arctan2 formulation preserves the sign and directly yields an angle in [-180, 180].

4. Range and Rounding
   - Ensure angle is within [-180, 180] (atan2 already yields this range).
   - Round to exactly 2 decimals.
   - Normalize negative zero: if abs(angle) < 0.005, set to 0.00 before formatting.

5. Output Formatting
   - Write exactly one line:
     - Dihedral angle: {ANGLE:.2f} degrees

## Verification

Perform these checks before finalizing the answer:
- Geometry sanity checks
  - ||b2|| must be non-zero; otherwise the torsion is undefined.
  - If ||n1|| or ||n2|| is near zero, the four points are nearly collinear or coplanar about one bond; the torsion will be close to 0 or ±180. The arctan2 method remains numerically robust, but be aware of precision limits.
- Sign validation
  - Using the arctan2 formulation above should produce a sign-consistent result. As a cross-check, compute an alternative y value: y_alt = ||b2|| · (b1 · n2). Then verify sign(atan2(y_alt, x)) matches your computed sign.
- Order check
  - Confirm the points are used in the specified order (e.g., N, CA, C, N'). Reordering points changes the sign.
- Formatting check
  - Confirm two decimals, exact label text, and a trailing newline if the task requires it.
  - Ensure the numeric value is in [-180.00, 180.00].

## Common Pitfalls and How to Avoid Them

- Losing the sign by using acos on a dot product
  - Pitfall: angle = acos((n1·n2)/(|n1||n2|)) returns [0, 180] and drops sign.
  - Fix: use atan2 with the y/x formulation shown above to preserve sign.
- Wrong atom/order input
  - Pitfall: swapping the order of points flips the sign or changes the value.
  - Fix: strictly follow the input order specified by the task.
- Normalization mistakes around b2
  - Pitfall: omitting normalization in the m1 = n1 × (b2/||b2||) term can yield incorrect sign.
  - Fix: explicitly normalize b2 when computing m1, or use the alternative atan2 form: atan2(||b2||·(b1·n2), n1·n2).
- Degenerate geometry
  - Pitfall: zero-length or nearly zero-length bonds cause division by zero or unstable normals.
  - Fix: detect ||b2|| < eps (e.g., 1e-12) and handle gracefully (e.g., report 0.00 or error per task policy).
- Formatting mismatches
  - Pitfall: wrong number of decimals, missing keywords, or angle outside the required range.
  - Fix: format with exactly two decimals and the exact required label text.

## Optional Script Usage

You can use the included script to compute the signed dihedral robustly:
- From a file with four lines of "x y z":
  - python scripts/dihedral_tools.py --file input.txt
- From 12 numeric arguments:
  - python scripts/dihedral_tools.py --values x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4

The script prints a single line in the expected format and implements the atan2-based signed torsion calculation with numeric safeguards.
