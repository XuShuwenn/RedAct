---
name: gibbs-equilibrium-thermo
description: "Compute ΔG and equilibrium constant K from ΔH (kJ/mol), ΔS (J/mol·K), and T (K) with correct unit handling, formatting, and verification checks."
---

# Gibbs Free Energy and Equilibrium Constant Calculation

Reusable workflow for computing Gibbs free energy (ΔG) and the equilibrium constant (K) from reaction enthalpy (ΔH), entropy (ΔS), and temperature (T). Includes robust unit handling, formatting, and sanity checks to avoid common sign and unit errors.

## When to Use

Activate this skill when a task requires:
- Calculating ΔG from ΔH (kJ/mol), ΔS (J/mol·K), and T (K)
- Computing the equilibrium constant K using K = exp(−ΔG/RT)
- Writing results in a strict textual format (e.g., fixed decimals, scientific notation)

## Core Workflow

1. Collect inputs
   - Inputs: ΔH in kJ/mol, ΔS in J/mol·K, T in K.
   - Validate: all numeric, T > 0, and units are as specified. If reading from a file, trim whitespace, ignore empty/comment lines, and parse the first numeric value per line.

2. Normalize units consistently
   - For ΔG calculation: convert ΔS from J/mol·K to kJ/mol·K by dividing by 1000.
   - For K calculation: ensure the exponent is unitless. Use one of:
     - Convert ΔG to J/mol (multiply kJ/mol by 1000) and use R in J/mol·K; or
     - Use R in kJ/mol·K (R_kJ = R_J / 1000) and keep ΔG in kJ/mol.
   - Pick one method and stick to it within the calculation.

3. Compute
   - ΔG_kJ = ΔH_kJ − T_K × (ΔS_J / 1000)
   - If using R in J/mol·K: ΔG_J = 1000 × ΔG_kJ and K = exp(−ΔG_J / (R_J × T_K))
   - If using R in kJ/mol·K: K = exp(−ΔG_kJ / (R_kJ × T_K))

4. Format output
   - ΔG rounded to 2 decimal places in kJ/mol
   - K in scientific notation with 4 digits after the decimal using lowercase e (format specifier: .4e)
   - Example layout (no extra spaces):
     - "ΔG: XX.XX kJ/mol"
     - "K: X.XXXXe+NN"

5. Write and verify
   - Write exactly two lines as specified.
   - Re-open and read the file to confirm it matches the required format and rounding.

## Verification

Perform these checks before finalizing:
- Dimensional sanity: The exponent −ΔG/(R×T) must be unitless.
- Sign sanity:
  - If ΔG < 0, expect K > 1
  - If ΔG > 0, expect K < 1
  - If ΔG ≈ 0, expect K ≈ 1
- Consistency check using ln K:
  - Compute lnK = ln(K). Verify that |lnK + ΔG_J/(R_J × T)| ≤ small tolerance (e.g., 1e−9 to 1e−6 depending on precision), where ΔG_J is ΔG in J/mol.
- Formatting check:
  - ΔG shows exactly two decimals.
  - K uses lowercase e scientific notation with four decimals (.4e), and no trailing spaces.

## Common Pitfalls and How to Avoid Them

- Sign error in exponent:
  - Mistake: Using exp(+ΔG/RT) or introducing double negatives.
  - Fix: Always compute K = exp(−ΔG/(R×T)) using ΔG with the same energy units as R×T.
- Mixed units between steps:
  - Mistake: Using ΔG in kJ with R in J/mol·K.
  - Fix: Either convert ΔG to J/mol or convert R to kJ/mol·K and keep consistent.
- Premature rounding:
  - Mistake: Rounding ΔG before computing K.
  - Fix: Keep full precision for calculations; round only for final output strings.
- Temperature in °C instead of K:
  - Mistake: Using Celsius directly.
  - Fix: Ensure input T is in K. If given in °C, convert: T_K = T_°C + 273.15.
- Output format drift:
  - Mistake: Extra spaces, wrong number of decimals, uppercase E, missing newline.
  - Fix: Use formatted strings (e.g., f"{value:.2f}", f"{K:.4e}") and write exactly two lines.
- Not verifying file write:
  - Mistake: Claiming success without checking the output contents.
  - Fix: Re-open and read the output to confirm exact formatting and values.

## Success Criteria

- Numerically correct ΔG and K with consistent units.
- Output contains exactly two lines with required formatting and units.
- Sanity checks pass (sign of ΔG vs. magnitude of K, lnK consistency).

## Optional Script Usage

A helper script is provided to compute and format results either from CLI values or from a three-line input file.

Examples:
- From explicit values:
  - python scripts/thermo_gibbs.py --dh-kj <ΔH_kJ> --ds-j <ΔS_J> --temp-k <T_K> --out-file output.txt
- From file with three lines (ΔH, ΔS, T):
  - python scripts/thermo_gibbs.py --in-file input.txt --out-file output.txt
- Override gas constant (J/mol·K) if the task specifies a value:
  - python scripts/thermo_gibbs.py --in-file input.txt --R 8.314 --out-file output.txt
