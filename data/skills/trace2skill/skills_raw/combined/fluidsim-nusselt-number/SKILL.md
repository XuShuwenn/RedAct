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


Preferred parsing workflow:
- Read `/root/input.txt` and extract the numeric values for `h`, `k`, and `D` before calculating
- Map values by their explicit keys (`h`, `k`, `D`) exactly as labeled; do not reinterpret parameters
- Accept decimals and scientific notation when parsing
- If the input instead provides three unlabeled numeric values, map them in this order: `h`, then `k`, then `D`


## Calculation

Compute the Nusselt number with:

`Nu = h * D / k`

Use only the parsed input values, and round only when formatting the final result.

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


- Treat `/root/input.txt` as the source of truth; do not assume defaults, guess missing values, or invent extra parameters
- Use the simplest valid workflow: parse `h`, `k`, and `D`, compute `Nu = h * D / k` at full precision, then write `/root/output.txt`
- Write exactly one line: `Nusselt number: X.XX` with exactly 2 decimal places including trailing zeros
- Do not add units, extra labels, commentary, or extra lines
- Verify the final file content once after writing

