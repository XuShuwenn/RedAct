---
name: coordinate-rmsd
description: "Compute RMSD between two equal-length sets of 3D coordinates and produce a precisely formatted result."
---

# Coordinate RMSD Calculation

Reusable workflow for calculating the Root Mean Square Deviation (RMSD) between two sets of paired 3D coordinates and writing the result in an exact, task-specified format.

## When to Use

Activate this skill when a task provides two coordinate sets (reference and target), with point-to-point correspondence, and asks for the RMSD and a specific output format (e.g., fixed decimal precision and units).

## Core Workflow

1. Parse Task Instructions
   - Identify how the input encodes the two sets (e.g., first N lines are reference, next N are target; or two separate files).
   - Note required output format: label, units, decimal precision, and exact spacing.

2. Read and Parse Coordinates
   - Extract coordinates as floats (x, y, z) per line.
   - Ignore empty lines and comments if present.
   - Validate each coordinate line has at least three numeric fields; use the first three as x, y, z.

3. Validate Pairing and Counts
   - Ensure both sets have the same number of points N (> 0).
   - Do not reorder or sort points; preserve the given pairing by index.

4. Compute RMSD
   - For i from 1..N, compute squared distance di^2 = (dx^2 + dy^2 + dz^2) for the i-th pair.
   - Mean squared deviation MSD = (sum of di^2) / N.
   - RMSD = sqrt(MSD).
   - Important invariants:
     - RMSD ≥ 0.
     - RMSD(ref, tgt) = RMSD(tgt, ref).
     - RMSD = 0 if and only if corresponding coordinates are identical.

5. Round and Format
   - Round to the exact number of decimals required (e.g., 4) using fixed-point formatting.
   - Avoid scientific notation; use a format specifier that preserves trailing zeros.
   - Include the exact label and units required by the task.
   - Example format pattern: "RMSD: {value:.4f} nm".

6. Write Output
   - Write exactly one line (unless otherwise specified) with the required format to the designated output file.
   - End with a newline.

## Verification

- Numerical Checks
  - Recompute quickly with an independent snippet or tool for sanity checking when possible.
  - Swap reference/target and confirm the same RMSD result.
  - Confirm the value is non-negative.

- Format Checks
  - Verify exact label text, colon and spacing, decimal precision (including trailing zeros), units, and a trailing newline.
  - Re-open and read the output file to confirm it matches the required pattern before finalizing.

## Common Pitfalls

- Using MSD instead of RMSD (forgetting the square root).
- Dividing by 3N (number of components) instead of N (number of points).
- Reordering or misaligning pairs (e.g., sorting lines); the task assumes index-wise pairing.
- Parsing errors when lines contain extra whitespace, tabs, or comments; handle flexibly and validate numeric fields.
- Printing with the wrong precision, missing trailing zeros, or scientific notation.
- Omitting units or using incorrect units.
- Extra whitespace or missing the trailing newline in the output file.

## Optional Script Usage

You can use the helper script to compute RMSD and optionally produce a formatted line. It supports either two separate files (reference and target) or a single combined file with the first N lines as reference and the next N lines as target.

Examples:
- Two files:
  - python scripts/compute_rmsd.py --ref ref.txt --tgt tgt.txt --precision 4 --label "RMSD" --unit "nm" --out output.txt
- Combined file with known split N:
  - python scripts/compute_rmsd.py --combined coords.txt --split 100 --precision 4 --label "RMSD" --unit "nm" --out output.txt
- Combined file with an even number of lines (auto-split in half):
  - python scripts/compute_rmsd.py --combined coords.txt --precision 4

Success Criteria:
- The output file exists and contains exactly one correctly formatted line with the required label, value at the correct precision, and units, followed by a newline.
- The numeric value equals sqrt(mean squared pairwise distances) over all paired points.
