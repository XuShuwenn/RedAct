#!/usr/bin/env python3
"""Solve molecular-dynamics-rmsd task."""

import math

def main():
    with open("/root/input.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse coordinates
    ref_coords = []
    target_coords = []
    for i, line in enumerate(lines):
        x, y, z = map(float, line.split())
        if i < 3:
            ref_coords.append((x, y, z))
        else:
            target_coords.append((x, y, z))

    # Calculate RMSD
    sum_sq = 0.0
    for r, t in zip(ref_coords, target_coords):
        dx = r[0] - t[0]
        dy = r[1] - t[1]
        dz = r[2] - t[2]
        sum_sq += dx*dx + dy*dy + dz*dz

    rmsd = math.sqrt(sum_sq / 3)

    result = f"RMSD: {rmsd:.4f} nm\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()