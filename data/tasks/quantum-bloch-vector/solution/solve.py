#!/usr/bin/env python3
"""Solve quantum-bloch-vector task."""

import math

def main():
    with open("/root/input.txt") as f:
        line = f.read().strip()

    parts = line.split()
    theta_deg = float(parts[0])
    phi_deg = float(parts[1])

    theta = math.radians(theta_deg)
    phi = math.radians(phi_deg)

    rx = math.sin(theta) * math.cos(phi)
    ry = math.sin(theta) * math.sin(phi)
    rz = math.cos(theta)

    result = f"rx: {rx:+.3f}\nry: {ry:+.3f}\nrz: {rz:+.3f}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()