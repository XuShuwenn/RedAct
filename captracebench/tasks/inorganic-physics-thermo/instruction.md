# Thermodynamics Equilibrium Calculation Task

Given reaction enthalpy (ΔH) in kJ/mol, entropy (ΔS) in J/mol·K, and temperature (T) in K in `/root/input.txt` (one per line), calculate:
1. Gibbs free energy: ΔG = ΔH - T×ΔS (convert ΔS to kJ/mol first)
2. Equilibrium constant: K = exp(-ΔG / (R × T)) where R = 8.314 J/mol·K

Write results to `/root/output.txt`:
```
ΔG: XX.XX kJ/mol
K: X.XXXXe+N
```

Round ΔG to 2 decimal places. Use scientific notation for K (1.23e+04 format).