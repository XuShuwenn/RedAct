#!/usr/bin/env python3
"""Solve fluidsim-nusselt-number task."""

def main():
    with open("/root/input.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    h = float(lines[0])   # W/m²·K
    k = float(lines[1])   # W/m·K
    D = float(lines[2])  # m

    Nu = h * D / k

    result = f"Nusselt number: {Nu:.2f}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()