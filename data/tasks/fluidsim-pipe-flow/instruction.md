# Pipe Flow Reynolds Number Task

Given fluid properties and pipe parameters in `/root/input.txt`:
- Fluid density ρ (kg/m³)
- Dynamic viscosity μ (Pa·s)
- Pipe diameter D (m)
- Flow velocity v (m/s)

Calculate the Reynolds number: Re = ρ × v × D / μ

Write result to `/root/output.txt`:
```
Reynolds number: XXXX.X
Flow regime: laminar/transitional/turbulent
```

Classify the flow regime:
- Re < 2300: laminar
- 2300 ≤ Re < 4000: transitional
- Re ≥ 4000: turbulent

Round Reynolds number to 1 decimal place.