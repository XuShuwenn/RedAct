---
name: fluidsim
description: "Pipe flow Reynolds number calculation and flow regime classification. Use when calculating Re from fluid properties and pipe parameters, or classifying flow as laminar/transitional/turbulent."
---

# FluidSim: Pipe Flow Reynolds Number

## Overview

Calculate Reynolds number from fluid properties and pipe parameters, then classify the flow regime.

## Reynolds Number Calculation

```python
# Read input: rho (kg/m³), mu (Pa·s), D (m), v (m/s)
with open("/root/input.txt") as f:
    lines = f.read().strip().split("\n")
    rho = float(lines[0].strip())    # fluid density kg/m³
    mu = float(lines[1].strip())     # dynamic viscosity Pa·s
    D = float(lines[2].strip())      # pipe diameter m
    v = float(lines[3].strip())      # flow velocity m/s

# Calculate Reynolds number
Re = rho * v * D / mu

# Classify flow regime
if Re < 2300:
    regime = "laminar"
elif Re < 4000:
    regime = "transitional"
else:
    regime = "turbulent"

# Output
with open("/root/output.txt", "w") as f:
    f.write(f"Reynolds number: {Re:.1f}\n")
    f.write(f"Flow regime: {regime}\n")
```

## Flow Regime Classification

- Re < 2300: laminar
- 2300 ≤ Re < 4000: transitional
- Re ≥ 4000: turbulent

## Output Format

```
Reynolds number: XXXX.X
Flow regime: laminar/transitional/turbulent
```

Round Reynolds number to 1 decimal place.

## Key Reference

- Re = ρ × v × D / μ
- ρ: fluid density (kg/m³)
- v: flow velocity (m/s)
- D: pipe diameter (m)
- μ: dynamic viscosity (Pa·s)