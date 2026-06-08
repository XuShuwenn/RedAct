---
name: molecular-dynamics-rmsd
description: "Calculate RMSD between reference and target atomic coordinate sets for molecular dynamics validation."
---

# RMSD Calculation for Molecular Dynamics

## When to Use

- Calculate RMSD between two molecular structures
- Validate molecular dynamics trajectories
- Compare reference vs target conformations

## Input Format

File `/root/input.txt` - 6 lines with x y z coordinates:
- Lines 1-3: reference coordinates (3 atoms)
- Lines 4-6: target coordinates (3 atoms)

## Formula

RMSD = sqrt(sum(|ri - ti|^2) / N)

Where N = 3 (number of atoms)

## Output Format

To `/root/output.txt`:
```
RMSD: X.XXXX nm
```

Round to 4 decimal places. Units are nanometers.

## Tips

- Parse 3D coordinates from text file
- Use numpy for vector operations
- Calculate Euclidean distance for each atom pair
- Verify units (coordinates in nm)
