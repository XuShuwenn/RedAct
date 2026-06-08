#!/usr/bin/env python3
"""Solve qutip-quantum-state task."""

import math

def main():
    input_path = "/root/input.txt"
    output_path = "/root/output.txt"

    with open(input_path, 'r') as f:
        line = f.read().strip()
    theta_deg, phi_deg = map(float, line.split())

    theta = math.radians(theta_deg)
    phi = math.radians(phi_deg)

    # Bloch vector components
    sx = math.sin(theta) * math.cos(phi)
    sy = math.sin(theta) * math.sin(phi)
    sz = math.cos(theta)

    result = f"Sigma X: {sx:+.3f}\nSigma Y: {sy:+.3f}\nSigma Z: {sz:+.3f}"

    with open(output_path, 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()