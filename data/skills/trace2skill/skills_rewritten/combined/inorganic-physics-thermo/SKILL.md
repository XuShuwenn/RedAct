---
name: inorganic-physics-thermo
description: "Calculate Gibbs free energy and equilibrium constant from thermodynamic parameters (ΔH, ΔS, T)."
---

# Thermodynamics Equilibrium Calculation

## When to Use

- Calculate Gibbs free energy from enthalpy and entropy
- Compute equilibrium constant from ΔG
- Solve chemistry/thermodynamics problems

- Prefer a short script when the task requires exponentials, precise rounding, or strict output-file formatting.
- Default workflow for this skill: read `/root/input.txt` first, parse the three observed numeric lines by position, compute `ΔS` conversion, `TΔS`, `ΔG`, and `K` from those exact values with a short script, then write `/root/output.txt` and read it back to verify the required two-line format.

## Input Format

File `/root/input.txt` (one per line):
- ΔH: Reaction enthalpy (kJ/mol)
- ΔS: Reaction entropy (J/mol·K)
- T: Temperature (K)

- Map lines by position exactly when `/root/input.txt` contains three numeric lines: line 1 = ΔH (kJ/mol), line 2 = ΔS (J/mol·K), line 3 = T (K).
- Parse the observed numeric values exactly as written, including negatives and scientific notation; do not reorder, relabel, infer, or guess inputs.
- Assign the three parsed values to variables and restate them with units before doing any math.
- Separate data extraction from formula application: first identify the three raw inputs exactly as written, then start unit conversion and thermodynamic calculations.
- If parsing fails or the values seem inconsistent, inspect the raw contents of `/root/input.txt` first and confirm it contains exactly three newline-separated values before retrying.

## Calculations

1. Convert ΔS to kJ/mol: ΔS(kJ) = ΔS(J) / 1000
2. Calculate ΔG: ΔG = ΔH - T × ΔS(kJ)
3. Calculate K: K = exp(-ΔG / (R × T))

- If using ΔG in kJ/mol inside the exponent, convert it to J/mol: `K = exp(-(ΔG * 1000) / (8.314 * T))`.
- DO NOT flip the sign in the exponent: `exp((ΔG * 1000) / (8.314 * T))` is wrong.
- Sanity-check the result: if ΔG < 0, then `K > 1`; if ΔG > 0, then `K < 1`.

   - R = 8.314 J/mol·K

- Before computing K, make units consistent: either convert ΔG from kJ/mol to J/mol, or use R = 0.008314 kJ/mol·K.
- Normalize units before any final computation that depends on them; do not evaluate `exp(...)` until `ΔG`, `R`, and `T` are confirmed to be dimensionally consistent.
- Compute `K` from the same numeric `ΔG` you just calculated after unit-consistent conversion; do not recompute from rounded display values.
- Write the substituted arithmetic before finalizing: e.g., ΔS = 50 J/mol·K = 0.050 kJ/mol·K, so at T = 298 K, TΔS = 14.90 kJ/mol and ΔG = ΔH - TΔS = -100 - 14.90 = -114.90 kJ/mol.
- DO NOT change `ΔH - T×ΔS` into `ΔH + T×ΔS` unless ΔS itself is negative.

- Use this sequence consistently: read `ΔH`, `ΔS`, and `T` from `/root/input.txt` → compute raw values before formatting output → convert `ΔS` from J/mol·K to kJ/mol·K → compute `TΔS` → compute `ΔG = ΔH - TΔS` → use that same computed `ΔG` in the `K` formula → make the exponent units consistent → compute `K`.
- Before finalizing, substitute the actual observed numbers into each step to catch sign and unit mistakes.
- If `ΔS` is positive, subtract a positive `TΔS`; only a negative `ΔS` changes the sign of that term through substitution.
- For `K`, use one unambiguous unit-matched form: `-(ΔG*1000)/(8.314*T)` or equivalently `-ΔG/(0.008314*T)`; do not mix J and kJ choices within one calculation.
- Use a calculator or short script for the final `exp(...)` evaluation rather than mental arithmetic, especially when the exponent is large.
- After computing `K`, confirm the sanity check with the actual result: `ΔG < 0` must give `K > 1`, `ΔG > 0` must give `K < 1`, and `ΔG` near 0 should give `K` near 1.

- Make the derivation auditable: either compute with a short script/calculator command or explicitly write the substituted numeric steps before writing `/root/output.txt`.
- At minimum, record these concrete intermediate values from the observed inputs: converted `ΔS` in kJ/mol·K, `TΔS`, `ΔG`, and the exact exponent used for `K`.
- Do not jump directly from the three raw inputs to final `ΔG` and `K` with no visible calculation or verification step.


- Treat the `ΔG`→`K` handoff as a checkpoint: after computing the exponent, verify it has the opposite sign of `ΔG` when using `K = exp(-(ΔG*1000)/(8.314*T))`, then evaluate `K` from that exact exponent.


## Output Format

To `/root/output.txt`:
```
ΔG: XX.XX kJ/mol
K: X.XXXXe+N
```

- Round ΔG to 2 decimal places
- Scientific notation for K (e.g., 1.23e+04)
- Format ΔG with exactly 2 digits after the decimal point, even when trailing zeros are needed (e.g., `-114.90`, not `-114.9`)
- Before finishing, read `/root/output.txt` and verify both lines match the required labels, units, decimal precision, and scientific notation

- Prefer programmatic formatting such as `ΔG` with `:.2f` and `K` with `:.4e`; do not rely on default numeric string conversion.
- Treat post-write verification as mandatory: after writing `/root/output.txt`, read it back and confirm there are exactly two lines in the required order: `ΔG` first, then `K`.
- Do not stop after computing the numbers: completing the task requires persisting the final formatted values to `/root/output.txt` and verifying the saved file contents.
- Use the read-back check to confirm the file contains the final computed values, not placeholders or partially written output.
- Re-check character-for-character that the labels are exactly `ΔG:` and `K:`, the units are correct, `ΔG` has exactly 2 digits after the decimal point, `K` is in scientific notation, and there is no extra commentary.


- Recommended final check: after writing `/root/output.txt`, reopen it and verify the contents are exactly the two expected lines, with no blank lines before, between, or after them.
- During post-write verification, also confirm the written values are thermodynamically consistent: a negative written `ΔG` must be paired with a written `K` greater than 1, and a positive written `ΔG` must be paired with a written `K` less than 1.
- If you provide a brief interpretation (for example, that negative `ΔG` favors spontaneity or large `K` favors products), keep it in the chat response only; `/root/output.txt` must still contain exactly the required two lines and nothing else.
- If the execution environment imposes a required tool-call or completion protocol, follow that protocol exactly in addition to producing the correct file.

## Tips

- Parse values from input file
- Handle scientific notation
- Check unit consistency (convert J to kJ properly)


- Read `/root/input.txt` and use only observed values; do not assume missing inputs.
- Verify the sign by substituting the actual numbers, not just the symbols.
- Before evaluating `exp(...)`, confirm ΔG and `R×T` use the same energy units.
- Treat formatting as part of correctness: if the computed value is `-114.9`, write `ΔG: -114.90 kJ/mol`
- Use the exact two-line output structure with no extra commentary in `/root/output.txt`

- Prefer a single short Python script or similarly reproducible workflow to read `/root/input.txt`, compute intermediate values explicitly, format both lines, write `/root/output.txt`, and read it back to verify formatting.
- Keep computation and presentation separate: finish the unit-consistent arithmetic before applying rounding or scientific-notation formatting.
- Do not calculate from guessed values; if a read fails or a value is missing, stop and retry the read rather than inventing inputs.


- Preferred reliable workflow: use one short script or calculator command to read `/root/input.txt`, parse the three observed numbers in order, restate them with units, compute `ΔS` conversion, `TΔS`, `ΔG`, the unit-consistent exponent, and `K`, then write `/root/output.txt` and immediately read it back to verify the exact two-line format.
- Keep raw computed values in variables separate from formatted output strings so rounding and scientific-notation formatting happen only when writing the final file.
- When using a script, preserve the same computed `ΔG` for both reporting and the `K` calculation; do not recompute it from rounded display values.
- Ground every claim in an actual observation from the environment: do not say `/root/input.txt` was read, `/root/output.txt` was written, or a value was computed unless the corresponding command/tool result succeeded.
- If any command fails or returns no usable output, stop and retry or correct the command; do not continue with guessed inputs, unverified file operations, or unsupported final numbers.



## Execution Protocol

## Execution Protocol

- Follow any environment-specific action/response format exactly when using this skill.
- If the system or environment requires a literal completion token (for example, `ACTION: TASK_COMPLETE`), end with exactly that token and no extra commentary.
- Treat protocol compliance as part of correctness: a correct `/root/output.txt` is not sufficient if the required tool-call or completion format is violated.
- Before the final response, explicitly check whether a special completion string or strict response schema was required and use it exactly.
