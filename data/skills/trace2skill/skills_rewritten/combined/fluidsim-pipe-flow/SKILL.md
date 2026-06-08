---
name: fluidsim-pipe-flow
description: "Calculate Reynolds number for pipe flow to determine flow regime (laminar/transitional/turbulent) from fluid properties."
---

# Pipe Flow Reynolds Number Calculation

## When to Use

- Calculate Reynolds number for fluid flow in pipes
- Classify flow regime based on Re number
- Solve pipe flow and fluid dynamics problems

- For file-based tasks, start with a quick directory inspection (for example, list `/root`) so you confirm `/root/input.txt` exists and `/root/output.txt` is the intended destination before reading or writing.

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

- If reading `/root/input.txt` is blocked by permissions or sandboxing, request/escalate access immediately; do not substitute another path or guess missing values.
- Before computing, assign the 4 extracted values exactly once to `ρ`, `μ`, `D`, and `v`; treat them as the canonical Reynolds-number inputs and use those same values directly in the standard formula without re-parsing, reordering, or reinterpreting them later.


## Flow Regime Classification

- Re < 2300: laminar
- 2300 ≤ Re < 4000: transitional
- Re ≥ 4000: turbulent

- Compute Reynolds number exactly once using `Re = (ρ × v × D) / μ`, then classify from that result.
- Apply the thresholds exactly as written above with direct boundary checks: `2300` is transitional and `4000` is turbulent.

- Use a strict two-step workflow: first map the four inputs to `ρ`, `μ`, `D`, `v` and compute `Re`, then classify the flow regime from that computed value.
- Do not infer the regime directly from raw or partial inputs, and do not stop after computing the numeric Reynolds number; always include the matching qualitative classification.

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

- Treat `/root/output.txt` as the required completion artifact and final source of truth: do not rely on a conversational answer in place of writing the file.
- After writing, read `/root/output.txt` back and confirm together that it contains only the exact required two lines, the Reynolds number is rounded to 1 decimal place, and the regime label matches the same computed `Re` value.

## Tips

- Parse density, viscosity, diameter, velocity from input
- Handle scientific notation
- Verify units consistency (SI preferred)

- For simple cases, prefer a single deterministic parsing/computation/formatting routine to keep the numeric result and regime label consistent.

- For this simple structured task, prefer one deterministic routine or script that: verifies expected files are present → reads `/root/input.txt` → extracts all 4 numeric values in file order → maps them to `ρ, μ, D, v` → substitutes those variables into `Re = (ρ × v × D) / μ` once to confirm no swap occurred → computes `Re` exactly once from the raw extracted values → classifies from that same unrounded computed `Re` using the stated thresholds → writes the exact 2-line `/root/output.txt` → reads the file back once to verify formatting.
- Keep the numeric result and regime label paired: do not classify from raw inputs, estimated ranges, partial calculations, or a separately rounded/recomputed value.
- Do not stop after the numeric calculation; always include both required output lines with exact labels, and round to 1 decimal place only when formatting the final Reynolds-number line.
