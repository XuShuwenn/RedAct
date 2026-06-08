#!/usr/bin/env python3
"""Solve inorganic-physics-thermo task."""

import math

def main():
    with open("/root/input.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    delta_h = float(lines[0])  # kJ/mol
    delta_s = float(lines[1])  # J/mol*K
    T = float(lines[2])  # K

    R = 8.314  # J/mol*K

    # Convert ΔS to kJ/mol
    delta_s_kJ = delta_s / 1000.0

    # ΔG = ΔH - T×ΔS
    delta_g = delta_h - T * delta_s_kJ

    # K = exp(-ΔG / (R × T))
    # Need ΔG in J/mol for this formula
    delta_g_J = delta_g * 1000.0
    K = math.exp(-delta_g_J / (R * T))

    result = f"ΔG: {delta_g:.2f} kJ/mol\nK: {K:.4e}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()