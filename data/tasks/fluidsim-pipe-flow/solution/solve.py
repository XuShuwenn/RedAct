#!/usr/bin/env python3
"""Solve fluidsim-pipe-flow task."""

def main():
    with open("/root/input.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    rho = float(lines[0])  # kg/m³
    mu = float(lines[1])  # Pa·s
    D = float(lines[2])  # m
    v = float(lines[3])  # m/s

    # Reynolds number
    Re = rho * v * D / mu

    # Flow regime
    if Re < 2300:
        regime = "laminar"
    elif Re < 4000:
        regime = "transitional"
    else:
        regime = "turbulent"

    result = f"Reynolds number: {Re:.1f}\nFlow regime: {regime}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()