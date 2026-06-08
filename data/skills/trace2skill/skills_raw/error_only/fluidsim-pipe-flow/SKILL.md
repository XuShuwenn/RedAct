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


## Flow Regime Classification

- Re < 2300: laminar
- 2300 ≤ Re < 4000: transitional
- Re ≥ 4000: turbulent

## Output Format

To `/root/output.txt`:
```
Reynolds number: XXXX.X
Flow regime: laminar/transitional/turbulent
```

Round Re to 1 decimal place.

## Tips

- Parse density, viscosity, diameter, velocity from input
- Handle scientific notation
- Verify units consistency (SI preferred)
