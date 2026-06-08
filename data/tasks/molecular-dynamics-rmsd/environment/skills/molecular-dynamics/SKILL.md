---
name: molecular-dynamics
description: "Calculate RMSD between two sets of 3D atomic coordinates. Use when computing root mean square deviation between reference and target structures, or structural alignment quality assessment."
---

# Molecular Dynamics: RMSD Calculation

## Overview

Given reference and target atomic coordinates (3 atoms each), calculate RMSD.

## RMSD Formula

RMSD = sqrt(sum(|ri - ti|²) / N), where N = 3 atoms

## Calculation

```python
# Read 6 lines: 3 reference atoms + 3 target atoms
with open("/root/input.txt") as f:
    lines = f.read().strip().split("\n")

# Parse reference coordinates (lines 0-2)
ref = []
for i in range(3):
    x, y, z = map(float, lines[i].strip().split())
    ref.append((x, y, z))

# Parse target coordinates (lines 3-5)
target = []
for i in range(3, 6):
    x, y, z = map(float, lines[i].strip().split())
    target.append((x, y, z))

# Compute RMSD
N = 3
sum_sq = 0.0
for i in range(N):
    dx = ref[i][0] - target[i][0]
    dy = ref[i][1] - target[i][1]
    dz = ref[i][2] - target[i][2]
    sum_sq += dx*dx + dy*dy + dz*dz

rmsd = (sum_sq / N) ** 0.5

# Output (units are nanometers)
with open("/root/output.txt", "w") as f:
    f.write(f"RMSD: {rmsd:.4f} nm\n")
```

## Output Format

```
RMSD: X.XXXX nm
```

Round to 4 decimal places. Units are nanometers.

## Key Reference

- RMSD = sqrt(sum(|ri - ti|²) / N)
- N = number of atoms = 3
- Coordinates are in nm