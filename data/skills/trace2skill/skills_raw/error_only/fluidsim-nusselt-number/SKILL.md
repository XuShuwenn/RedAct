---
name: fluidsim-nusselt-number
description: "Calculate Nusselt number for forced convection heat transfer from h, k, D parameters."
---

# Nusselt Number Calculation

## When to Use

- Calculate dimensionless heat transfer coefficient
- Solve forced convection problems
- Process physics/engineering input files

## Input Format

File `/root/input.txt`:
```
h: convective heat transfer coefficient (W/m²·K)
k: thermal conductivity (W/m·K)
D: characteristic length (m)
```

## Output Format

To `/root/output.txt`:
```
Nusselt number: X.XX
```

Round to 2 decimal places.

## Tips

- Parse key-value pairs from input file
- Verify units are consistent
- Handle scientific notation in input
