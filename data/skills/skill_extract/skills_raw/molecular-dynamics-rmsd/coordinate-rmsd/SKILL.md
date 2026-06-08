---
name: coordinate-rmsd
description: "Compute RMSD between two 3D coordinate sets from text or files with validation, rounding, and precise output formatting."
---

# Coordinate RMSD Computation

A practical workflow for computing Root Mean Square Deviation (RMSD) between two sets of 3D atomic coordinates. Handles parsing, validation, direct (no-alignment) RMSD, rounding, and strict output formatting.

## When to Use

Activate this skill when the user asks to:
- compute RMSD between two structures or frames given as coordinate lists
- compare a reference and a target set of 3D points with one-to-one atom mapping
- produce a single numeric RMSD with specified precision and units

If the task explicitly requests superposition/alignment before RMSD, confirm the requirement. This skill focuses on direct RMSD; alignment can be added when specified (see notes below).

## Core Workflow

1) Gather Inputs
- Identify where the coordinates come from (file(s) or inline text).
- Confirm the mapping: pair i in reference maps to pair i in target. Do not reorder atoms unless instructed.

2) Parse Coordinates
- Expect 3 numbers per atom (x y z) per line.
- Robust parsing rules:
  - Ignore blank lines.
  - Strip comments starting with `#` on any line.
  - Allow spaces/tabs or commas as separators.
- Validate that both sets have the same atom count N and shape (N×3).

3) Choose RMSD Mode
- Direct RMSD (default unless alignment is requested):
  - RMSD = sqrt( (1/N) * Σ_i ||ri - ti||^2 ) where ||.|| is Euclidean norm in 3D.
- If alignment is explicitly required, perform rigid superposition (e.g., Kabsch) before the same RMSD formula. Do not align unless the instructions say so.

4) Compute Accurately
- Accumulate squared distances in full precision, take the square root once at the end.
- Divide by N (number of atoms), not by 3N and not by N−1.

5) Rounding and Units
- Round only the final RMSD to the required number of decimal places (commonly 4). Use fixed-width formatting to include trailing zeros.
- Use the units exactly as specified by the task; do not convert units unless explicitly asked.

6) Output Formatting
- Follow the exact format specified by the task (label, punctuation, spacing, units, newline). Example pattern:
  - "RMSD: X.XXXX nm" (with a single newline at the end)
- Write to the exact output location the task specifies.

## Verification

Perform these checks before finalizing:
- Shape check: both arrays are N×3; N > 0.
- Symmetry sanity check: RMSD(reference, target) equals RMSD(target, reference).
- Non-negativity: RMSD ≥ 0; clamp very small negative values to 0 due to numerical noise (if any).
- Manual spot-check: compute squared displacement for 1–2 atom pairs to confirm the aggregation logic (sum of squared component differences, not per-axis averages).
- Output check: read back the written file and ensure it matches the exact template (decimal places and units). A regex like `^RMSD: \d+\.?\d{4} \w+\n?$` can help when 4 decimals are required.

## Common Pitfalls

- Using N−1 instead of N, or dividing by 3N. The formula divides by N (atoms), after summing squared 3D distances.
- Forgetting the square root (reporting mean squared deviation instead of RMSD).
- Rounding intermediate values instead of the final RMSD, leading to small errors.
- Reordering or sorting atoms and breaking the one-to-one mapping.
- Mixing units (e.g., coordinates in Å but reporting nm) or changing units without instruction.
- Parsing failures due to commas or inline comments; always normalize separators and strip comments.
- Extra whitespace/lines or a mismatched output label that violates the required format.
- Performing rigid-body alignment when not requested, changing the intended result.

## Optional Script Usage

Use the helper to parse common text formats and compute direct RMSD. It supports:
- Two separate files: `--ref` and `--target`.
- One file with two consecutive blocks: `--file` plus `--n` (first N lines = reference, next N lines = target).
- Custom units label and decimal places; optional writing to an output file.

Examples:
- python scripts/rmsd_tools.py --ref ref.txt --target target.txt --units nm --decimals 4
- python scripts/rmsd_tools.py --file coords.txt --n 3 --units nm --decimals 4 --output output.txt

If alignment (superposition) is required by the task, implement a Kabsch-based preprocessing step or use a library/tool that provides it, then apply the same RMSD formula and formatting.
