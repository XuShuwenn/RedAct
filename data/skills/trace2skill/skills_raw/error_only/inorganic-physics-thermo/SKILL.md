---
name: inorganic-physics-thermo
description: "Calculate Gibbs free energy and equilibrium constant from thermodynamic parameters (ΔH, ΔS, T)."
---

# Thermodynamics Equilibrium Calculation

## When to Use

- Calculate Gibbs free energy from enthalpy and entropy
- Compute equilibrium constant from ΔG
- Solve chemistry/thermodynamics problems

## Input Format

File `/root/input.txt` (one per line):
- ΔH: Reaction enthalpy (kJ/mol)
- ΔS: Reaction entropy (J/mol·K)
- T: Temperature (K)

## Calculations

1. Convert ΔS to kJ/mol: ΔS(kJ) = ΔS(J) / 1000
2. Calculate ΔG: ΔG = ΔH - T × ΔS(kJ)
3. Calculate K: K = exp(-ΔG / (R × T))

- If using ΔG in kJ/mol inside the exponent, convert it to J/mol: `K = exp(-(ΔG * 1000) / (8.314 * T))`.
- DO NOT flip the sign in the exponent: `exp((ΔG * 1000) / (8.314 * T))` is wrong.
- Sanity-check the result: if ΔG < 0, then `K > 1`; if ΔG > 0, then `K < 1`.

   - R = 8.314 J/mol·K

- Before computing K, make units consistent: either convert ΔG from kJ/mol to J/mol, or use R = 0.008314 kJ/mol·K.
- Write the substituted arithmetic before finalizing: e.g., ΔS = 50 J/mol·K = 0.050 kJ/mol·K, so at T = 298 K, TΔS = 14.90 kJ/mol and ΔG = ΔH - TΔS = -100 - 14.90 = -114.90 kJ/mol.
- DO NOT change `ΔH - T×ΔS` into `ΔH + T×ΔS` unless ΔS itself is negative.


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

## Tips

- Parse values from input file
- Handle scientific notation
- Check unit consistency (convert J to kJ properly)


- Read `/root/input.txt` and use only observed values; do not assume missing inputs.
- Verify the sign by substituting the actual numbers, not just the symbols.
- Before evaluating `exp(...)`, confirm ΔG and `R×T` use the same energy units.
- Treat formatting as part of correctness: if the computed value is `-114.9`, write `ΔG: -114.90 kJ/mol`
- Use the exact two-line output structure with no extra commentary in `/root/output.txt`

