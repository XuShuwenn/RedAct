---
name: molecular-dynamics-rmsd
description: "Calculate RMSD between reference and target atomic coordinate sets for molecular dynamics validation."
---

# RMSD Calculation for Molecular Dynamics

## When to Use

- Calculate RMSD between two molecular structures
- Validate molecular dynamics trajectories
- Compare reference vs target conformations

- Start by inspecting the working directory and relevant paths so you confirm `/root/input.txt` is present and `/root/output.txt` is the expected destination before computing.

## Input Format

File `/root/input.txt` - 6 lines with x y z coordinates:
- Lines 1-3: reference coordinates (3 atoms)
- Lines 4-6: target coordinates (3 atoms)


Use the fixed layout directly:
1. Read `/root/input.txt` once and confirm it has exactly 6 non-empty coordinate lines before calculating anything.
2. Parse each line as one atom with three numeric fields: `x y z`.
3. Use lines 1-3 as the reference atoms and lines 4-6 as the target atoms.
4. Preserve line order when pairing atoms: line 1 with line 4, line 2 with line 5, and line 3 with line 6.
5. Treat the file as two aligned 3-atom structures, not as one undifferentiated 6-atom set: reference = lines 1-3 and target = lines 4-6.
6. Establish this grouping before doing any math; because correspondence is already given by line order, do not remap or infer alternate matches.

## Formula

RMSD = sqrt(sum(|ri - ti|^2) / N)

Where N = 3 (number of atoms)


Use the provided RMSD formula directly on the 3 paired atoms with `N = 3`; do not add alignment, superposition, centering, reordering, or other extra normalization/transformation steps.
The listed atom order already defines one-to-one correspondence, so compute atom-wise Cartesian differences on those fixed pairs only; do not add fitting, optimization, remapping, or other preprocessing beyond parsing the numeric coordinates.

Recommended calculation order:
1. For each paired atom, compute component differences `(dx, dy, dz)`.
2. Compute that pair's squared 3D distance: `dx^2 + dy^2 + dz^2`.
3. Sum the 3 squared distances.
4. Divide by 3.
5. Take the square root once at the end.
6. Keep full precision during calculation and round only when formatting the final RMSD value to 4 decimal places.

## Output Format

To `/root/output.txt`:
```
RMSD: X.XXXX nm
```

Round to 4 decimal places. Units are nanometers.


Write `/root/output.txt` with exactly one line: `RMSD: X.XXXX nm`

Match the format exactly: keep the `RMSD:` prefix, use single spaces, include exactly 4 digits after the decimal point, include the `nm` unit, and do not write extra text or additional lines.


Final completion check:
- Do not stop after computing or stating the RMSD numerically; the task is complete only after writing `/root/output.txt`.
- Treat exact output formatting as part of the task: label, spacing, 4 decimal places, and `nm` must all match exactly.
- After writing `/root/output.txt`, read it back and confirm it is exactly one line in the form `RMSD: X.XXXX nm` with no extra whitespace or extra lines.


## Tips

- Parse 3D coordinates from text file
- Use numpy for vector operations
- Calculate Euclidean distance for each atom pair
- Verify units (coordinates in nm)


- Prefer a short one-shot script that performs read -> validate 6 non-empty lines -> parse coordinates -> compute RMSD -> write `/root/output.txt` -> read back to verify.
- Extract the parsed coordinates into two explicit 3-atom lists or arrays before calculating so the line-1→4, line-2→5, line-3→6 pairing stays obvious.
- Before writing, sanity-check that you used all 6 lines, preserved the required atom pairing, and used exactly 3 reference atoms, 3 target atoms, and `N = 3`.
- Prefer simple direct arithmetic or a tiny numpy calculation for this small fixed dataset; if you use a concise shell solution such as `awk`, ensure it computes the same RMSD formula and writes the exact required output format.
