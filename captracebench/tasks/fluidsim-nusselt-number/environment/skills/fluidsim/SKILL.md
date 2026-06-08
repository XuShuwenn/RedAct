---
name: fluidsim
description: "Calculate Nusselt number for forced convection heat transfer. Use when computing dimensionless heat transfer coefficient, or analyzing convection heat transfer performance."
---

# FluidSim: Nusselt Number Calculation

## Overview

The Nusselt number (Nu) is a dimensionless parameter that characterizes convective heat transfer. It represents the ratio of convective to conductive heat transfer across a fluid boundary.

## Formula

```
Nu = h × D / k
```

Where:
- h: convective heat transfer coefficient (W/m²·K)
- D: characteristic length (m)
- k: thermal conductivity (W/m·K)

## Calculation

```python
# Read input: h (W/m²·K), k (W/m·K), D (m)
with open("/root/input.txt") as f:
    lines = f.read().strip().split("\n")
    h = float(lines[0].strip())   # convective coefficient
    k = float(lines[1].strip())   # thermal conductivity
    D = float(lines[2].strip())   # characteristic length

# Calculate Nusselt number
Nu = h * D / k

# Output
with open("/root/output.txt", "w") as f:
    f.write(f"Nusselt number: {Nu:.2f}\n")
```

## Output Format

```
Nusselt number: X.XX
```

Round to 2 decimal places.

## Physical Interpretation

| Nu Range | Interpretation |
|----------|---------------|
| Nu ≈ 1 | Pure conduction (no convection) |
| Nu ≈ 2–10 | Laminar flow in ducts |
| Nu > 10 | Turbulent forced convection |

## Key Reference

- Nu = h × D / k
- Units cancel to make Nu dimensionless
- Higher Nu means more effective convective heat transfer