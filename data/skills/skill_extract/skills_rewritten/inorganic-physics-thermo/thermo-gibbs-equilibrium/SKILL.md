---
name: thermo-gibbs-equilibrium
description: "Compute Gibbs free energy and the equilibrium constant from enthalpy, entropy, and temperature with correct unit handling and strict output formatting."
---

# Thermodynamics: Gibbs Free Energy and Equilibrium Constant

Reusable workflow to read reaction enthalpy (ΔH), entropy (ΔS), and temperature (T), compute ΔG and the equilibrium constant K, and write results with strict formatting. Emphasizes unit consistency, rounding discipline, and verification checks to avoid common errors.

## When to Use

Use this skill when a task asks to:
- compute ΔG from ΔH, ΔS, and T, especially when ΔH is in kJ/mol and ΔS is in J/mol·K
- compute the equilibrium constant K from ΔG using K = exp(−ΔG/(R·T))
- produce outputs with specific rounding and scientific notation requirements

## Core Workflow

1. Parse inputs
   - Read three numeric values in order: ΔH (kJ/mol), ΔS (J/mol·K), T (K).
   - Strip whitespace, ignore blank lines, and validate that exactly three numbers are obtained.
   - Validate that T > 0 K.

2. Convert units
   - Convert entropy to kJ/mol·K: ΔS_kJ = ΔS_J / 1000.

3. Compute Gibbs free energy (in kJ/mol)
   - ΔG_kJ = ΔH_kJ − T × ΔS_kJ
   - Keep full precision internally; do not round yet.

4. Compute equilibrium constant
   - Ensure the exponent is dimensionless. Use either of the following equivalent, unit-consistent formulations:
     - Convert ΔG_kJ to J/mol: ΔG_J = ΔG_kJ × 1000, then K = exp(−ΔG_J / (R_J × T)) with R_J = 8.314 J/mol·K.
     - Or, use R in kJ/mol·K: R_kJ = 0.008314 kJ/mol·K, then K = exp(−ΔG_kJ / (R_kJ × T)).
   - Use the same internal (unrounded) ΔG value for K.

5. Format output
   - Round and format ΔG to exactly 2 decimal places: e.g., "ΔG: −123.45 kJ/mol".
   - Format K in scientific notation: e.g., "K: 1.2345e+04" (lowercase e, explicit sign on exponent). If the task specifies a different precision for K, follow it; otherwise, 4 digits after the decimal is a robust default.

6. Write results
   - Write exactly two lines in the specified order and format:
     - ΔG: <value> kJ/mol
     - K: <value in scientific notation>

## Verification

- Dimensional consistency
  - Check that the exponent −ΔG/(R·T) is unitless by ensuring ΔG and R·T use the same energy units (both in J or both in kJ).

- Dual-route equivalence
  - Compute K via both routes (J-based and kJ-based R). The results should agree within floating-point tolerance. If they differ significantly, a unit mismatch exists.

- Sign and magnitude sanity checks
  - If ΔG < 0 with appreciable magnitude, expect K ≫ 1.
  - If ΔG > 0 with appreciable magnitude, expect K ≪ 1.
  - ln K should be approximately −ΔG/(R·T). This quick check catches sign mistakes.

- Rounding discipline
  - Round only for display. Do not feed rounded ΔG into the K computation.

- Output compliance
  - Ensure units and punctuation match the requested format exactly (colon and space after labels, unit strings, lowercase "e" with signed exponent).

## Common Pitfalls

- Missing unit conversion for ΔS (forgetting to divide J by 1000).
- Mixing units in the exponent (e.g., ΔG in kJ with R in J) leading to large errors.
- Sign error in the exponent (using exp(+ΔG/(R·T)) instead of exp(−ΔG/(R·T))), which inverts K.
- Premature rounding (rounding ΔG before computing K), causing noticeable deviation.
- Using temperature in °C instead of K; always ensure T is in K.
- Formatting K without scientific notation or with the wrong exponent sign/letter case.

## Success Criteria

- ΔG reported to exactly 2 decimal places with units kJ/mol.
- K reported in scientific notation with the requested precision and lowercase "e" (e.g., 1.2345e+06).
- Internal calculations use consistent units; verification checks pass.
- Output file contains exactly the specified two lines in the correct order and format.

## Optional Script Usage

A helper script is provided to perform the computation and enforce formatting.

Examples:
- Using explicit values:
  - python scripts/gibbs_equilibrium.py --dh 10.5 --ds 25.0 --t 298
- Using an input file with three lines (ΔH, ΔS, T):
  - python scripts/gibbs_equilibrium.py --input path/to/input.txt --output path/to/output.txt

The script validates inputs, computes ΔG and K with correct units, and writes the two-line formatted output. Use --k-decimals to adjust the number of decimal places in K's scientific notation if the task specifies a different precision.
