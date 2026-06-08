---
name: dihedral-angle-atan2
description: "Compute signed dihedral (torsion) angles from four 3D points and report degrees in [-180, 180] using a robust atan2 formulation."
---

# Robust Dihedral (Torsion) Angle Computation

This skill computes the signed dihedral angle defined by four ordered 3D points using a numerically stable atan2-based formulation. It standardizes sign conventions, handles degeneracy checks, and guides precise output formatting.

## When to Use

Use this skill when a task asks to:
- compute a dihedral/torsion angle from four points (e.g., protein backbone N–CA–C–N')
- determine the signed angle between two planes defined by consecutive triplets of points
- output the angle in degrees within the range [-180, 180] with fixed decimal precision

## Core Workflow

1. Parse Input
   - Expect four 3D coordinates (x, y, z) in order along the chain/path.
   - Validate that each line yields three finite numeric values.

2. Define Bond Vectors
   - b0 = p1 − p0
   - b1 = p2 − p1
   - b2 = p3 − p2
   - Ensure |b1| ≠ 0 (central bond cannot be zero-length).

3. Plane Normals
   - n1 = b0 × b1  (normal to plane p0–p1–p2)
   - n2 = b1 × b2  (normal to plane p1–p2–p3)
   - If |n1| ≈ 0 or |n2| ≈ 0, the angle is undefined (colinear/degenerate). Decide whether to emit 0.00 with a note or fail with a clear error per task requirements.

4. atan2 Dihedral Formula (signed and robust)
   - Let b1̂ = b1 / |b1|
   - Let n1̂ = n1 / |n1| and n2̂ = n2 / |n2|
   - x = n1̂ · n2̂
   - y = (n1̂ × b1̂) · n2̂
   - φ = atan2(y, x) in radians, then convert to degrees
   - Wrap to [-180, 180]: add/subtract 360° as needed to land in this interval.

5. Rounding and Output
   - Round to the requested precision (e.g., 2 decimals) using standard rounding.
   - Emit exactly the required line structure if specified by the task (e.g., "Dihedral angle: XX.XX degrees").

## Verification

Implement these checks before finalizing output:
- Geometry sanity:
  - |b1| > 0; |n1| and |n2| are not near zero (use a small epsilon, e.g., 1e-12).
- Sign and orientation consistency:
  - Reversing the full point order (p3, p2, p1, p0) should yield the same φ.
  - Swapping the first two points or the last two points (breaking the chain order) will flip the sign; use this to debug ordering mistakes.
- Alternate computation cross-check (optional):
  - Compute v = b0 − proj(b0, b1) and w = b2 − proj(b2, b1);
    φ_alt = atan2(|b1| · det(b0, b1, b2), v · w) with det(b0,b1,b2) = b1 · (b0 × b2).
  - φ and φ_alt should match within a small tolerance.
- Formatting:
  - Confirm the angle is in degrees, wrapped to [-180, 180], and rounded as required.
  - Confirm the output line matches the exact requested format.

## Common Pitfalls and Fixes

- Sign lost by acos:
  - Mistake: using acos(dot(n1̂, n2̂)) gives only [0, 180] and loses sign.
  - Fix: use the atan2(y, x) formulation described above.
- Wrong point order:
  - Mistake: misordering points or central bond direction causes a ±180° sign flip.
  - Fix: ensure the four points are in order along the chain so b1 points from the second to third point.
- Missing normalization of the central bond in the atan2 formula:
  - Mistake: omitting b1̂ can flip signs or destabilize y.
  - Fix: always normalize b1 when computing y = (n1̂ × b1̂) · n2̂.
- Degenerate geometry:
  - Mistake: dividing by near-zero normal magnitudes (colinear points) or zero-length central bond.
  - Fix: check magnitudes; either return an informative error or a defined fallback per task spec.
- Unit/format errors:
  - Mistake: returning radians, wrong decimal places, or mismatched output text.
  - Fix: convert to degrees, round to the specified precision, and follow the exact output string.
- Angle wrapping:
  - Mistake: returning angles outside [-180, 180] due to direct degrees conversion.
  - Fix: wrap by adding/subtracting 360° until within the interval; preserve the sign convention.

## Success Criteria

- Uses the atan2-based dihedral formula with correct vector ordering and normalization.
- Handles degenerate cases explicitly.
- Returns a degree value in [-180, 180], rounded to the required precision.
- Writes exactly the requested output format.

## Optional Script Usage

You can use scripts/dihedral.py to compute the dihedral from either a file containing four lines of "x y z" or from 12 numeric arguments:

- From a file:
  - python scripts/dihedral.py --file input.txt --out output.txt
- From command-line numbers:
  - python scripts/dihedral.py x0 y0 z0 x1 y1 z1 x2 y2 z2 x3 y3 z3

The script prints the angle and, if an output path is provided, writes a formatted line: "Dihedral angle: XX.XX degrees".
