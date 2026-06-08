---
name: fluidsim-pipe-flow
description: "Calculate Reynolds number for pipe flow to determine flow regime (laminar/transitional/turbulent) from fluid properties."
---

# Pipe Flow Reynolds Number Calculation

## When to Use

- Calculate Reynolds number for fluid flow in pipes
- Classify flow regime based on Re number
- Solve pipe flow and fluid dynamics problems

## Input Format

File `/root/input.txt`:
- ρ: Fluid density (kg/m³)
- μ: Dynamic viscosity (Pa·s)
- D: Pipe diameter (m)
- v: Flow velocity (m/s)

- Read `/root/input.txt` first and extract all input values before calculating.
- Ignore blank lines and confirm there are exactly 4 numeric entries.
- Map the entries in file order as `ρ`, `μ`, `D`, `v`; if the file contains four unlabeled or plain numeric values, treat line 1 = `ρ`, line 2 = `μ`, line 3 = `D`, line 4 = `v`.
- Prefer direct ordered extraction when the input matches the documented order, and do not reorder values by guessing from magnitude, units, expected ranges, or inferred defaults.


## Flow Regime Classification

- Re < 2300: laminar
- 2300 ≤ Re < 4000: transitional
- Re ≥ 4000: turbulent

- Compute Reynolds number exactly once using `Re = (ρ × v × D) / μ`, then classify from that result.
- Apply the thresholds exactly as written above with direct boundary checks: `2300` is transitional and `4000` is turbulent.

## Output Format

To `/root/output.txt`:
```
Reynolds number: XXXX.X
Flow regime: laminar/transitional/turbulent
```

Round Re to 1 decimal place.

- Write `/root/output.txt` using the exact two-line structure shown above, preserving labels, order, line breaks, and colon spacing.
- Keep labels exactly as `Reynolds number:` and `Flow regime:` with no extra text or units.
- Format the Reynolds number to exactly 1 decimal place.
- After writing, read `/root/output.txt` back once to confirm both lines are present and formatted correctly.

## Tips

- Parse density, viscosity, diameter, velocity from input
- Handle scientific notation
- Verify units consistency (SI preferred)

- For simple cases, prefer a single deterministic parsing/computation/formatting routine to keep the numeric result and regime label consistent.
