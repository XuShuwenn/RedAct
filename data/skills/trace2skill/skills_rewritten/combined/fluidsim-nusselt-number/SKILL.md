---
name: fluidsim-nusselt-number
description: "Calculate Nusselt number for forced convection heat transfer from h, k, D parameters."
---

# Nusselt Number Calculation

## When to Use

- Calculate dimensionless heat transfer coefficient
- Solve forced convection problems
- Process physics/engineering input files

- For file-based tasks, first inspect `/root` to confirm the expected files are present, then read `/root/input.txt` before doing any calculation

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

- Before doing any arithmetic, confirm you have exactly one numeric value for each required input: `h`, `k`, and `D`
- Ignore descriptive text after the colon and parse the numeric token associated with each key
- Preserve signs and exponent markers when present (for example `-1.2`, `3.0e-4`, `6E2`)
- If the file provides three indexed or numbered values without repeating the parameter names, extract the three numbers first and treat them as the complete input set, preserving file order as `h`, `k`, `D`
- Normalize parsed values into explicit variables `h`, `k`, and `D` before doing any arithmetic


## Calculation

Compute the Nusselt number with:

`Nu = h * D / k`

Use only the parsed input values, and round only when formatting the final result.

- Follow this sequence: read `/root/input.txt` -> extract and assign `h`, `k`, and `D` completely -> compute `Nu = h * D / k` using only the extracted numeric values at full precision -> format to 2 decimals -> write `/root/output.txt`
- Apply the defining relation directly from the parsed values only; do not use alternate formulas, guessed inputs, or partially read text
- For a simple deterministic computation like this, prefer a short Python command or equivalent precise calculation method to avoid arithmetic mistakes

## Output Format

To `/root/output.txt`:
```
Nusselt number: X.XX
```

Round to 2 decimal places.

- Save the result to `/root/output.txt`; do not leave the answer only in the conversation
- Preserve the exact label and formatting, for example: `Nusselt number: 4.00`
- After writing `/root/output.txt`, read it back once and confirm it contains exactly one line in the form `Nusselt number: X.XX`.

## Tips

- Parse key-value pairs from input file
- Verify units are consistent
- Handle scientific notation in input


- Treat `/root/input.txt` as the source of truth; do not assume defaults, guess missing values, or invent extra parameters
- Use the simplest valid workflow: parse `h`, `k`, and `D`, compute `Nu = h * D / k` at full precision, then write `/root/output.txt`
- Write exactly one line: `Nusselt number: X.XX` with exactly 2 decimal places including trailing zeros
- Do not add units, extra labels, commentary, or extra lines
- Verify the final file content once after writing

