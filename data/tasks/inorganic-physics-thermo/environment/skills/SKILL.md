---
name: inorganic-physical-chemistry
description: "Gibbs free energy and equilibrium constant calculation from thermodynamics data. Use when calculating ΔG from ΔH, ΔS, and T, or computing equilibrium constants."
---

# Inorganic & Physical Chemistry: Thermodynamics

## Overview

Given reaction enthalpy (ΔH) in kJ/mol, entropy (ΔS) in J/mol·K, and temperature (T) in K, calculate:
1. Gibbs free energy: ΔG = ΔH - T×ΔS (convert ΔS to kJ/mol first)
2. Equilibrium constant: K = exp(-ΔG / (R × T))

R = 8.314 J/mol·K (use 8.314, not 8.314462618)

## Calculation

```python
# Read input: ΔH (kJ/mol), ΔS (J/mol·K), T (K)
with open("/root/input.txt") as f:
    lines = f.read().strip().split("\n")
    dH = float(lines[0].strip())      # kJ/mol
    dS = float(lines[1].strip())       # J/mol·K
    T = float(lines[2].strip())        # K

# Convert ΔS to kJ/mol·K
dS_kJ = dS / 1000.0                    # J/mol·K -> kJ/mol·K

# Calculate ΔG (kJ/mol)
dG = dH - T * dS_kJ

# Calculate K
R = 8.314                               # J/mol·K
import math
K = math.exp(-dG * 1000 / (R * T))     # dG in J/mol for exponent

# Output
with open("/root/output.txt", "w") as f:
    f.write(f"ΔG: {dG:.2f} kJ/mol\n")
    f.write(f"K: {K:.4e}\n")
```

## Output Format

```
ΔG: XX.XX kJ/mol
K: X.XXXXe+N
```

Round ΔG to 2 decimal places. Use scientific notation for K (e.g., 1.23e+04).

## Key Reference

- ΔG (kJ/mol) = ΔH (kJ/mol) - T × ΔS (J/mol·K) / 1000
- Convert ΔS to kJ/mol·K before multiplying by T in kJ/mol units
- K = exp(-ΔG_J / (R × T)) where ΔG_J = ΔG_kJ × 1000
- R = 8.314 J/mol·K