#!/usr/bin/env python3
"""Compute RMSD between two sets of 3D coordinates.

Supports two modes:
  1) Two separate files: --ref REF --tgt TGT
  2) One combined file: --combined FILE [--split N]
     If --split is omitted, the file must contain an even number of
     coordinate lines; the first half is reference, the second half target.

Each coordinate line should contain at least three numeric values (x y z).
Blank lines and lines starting with '#' are ignored. Extra columns are ignored.

By default prints the RMSD as a plain number with fixed precision. Use
--label and/or --unit to emit a formatted line like: "RMSD: 0.1234 nm".
Optionally write to a file with --out.
"""

import argparse
import math
import sys
from typing import List, Tuple

Coord = Tuple[float, float, float]


def parse_coords_from_lines(lines: List[str]) -> List[Coord]:
    coords: List[Coord] = []
    for lineno, raw in enumerate(lines, start=1):
        s = raw.strip()
        if not s or s.startswith('#'):
            continue
        # Support comma-separated by replacing commas with spaces
        s = s.replace(',', ' ')
        parts = s.split()
        nums = []
        for p in parts:
            try:
                nums.append(float(p))
            except ValueError:
                # Non-numeric tokens are ignored; continue scanning the line
                continue
        if len(nums) < 3:
            raise ValueError(f"Line {lineno}: expected at least 3 numeric values, got {len(nums)}")
        x, y, z = nums[0], nums[1], nums[2]
        coords.append((x, y, z))
    return coords


def read_coords_file(path: str) -> List[Coord]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return parse_coords_from_lines(f.readlines())
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")


def compute_rmsd(ref: List[Coord], tgt: List[Coord]) -> float:
    if len(ref) != len(tgt):
        raise ValueError(f"Mismatched point counts: ref={len(ref)}, tgt={len(tgt)}")
    n = len(ref)
    if n == 0:
        raise ValueError("Empty coordinate sets; N must be > 0")
    ssd = 0.0
    for (rx, ry, rz), (tx, ty, tz) in zip(ref, tgt):
        dx = rx - tx
        dy = ry - ty
        dz = rz - tz
        ssd += dx*dx + dy*dy + dz*dz
    msd = ssd / n
    return math.sqrt(msd)


def format_value(val: float, precision: int, label: str = None, unit: str = None) -> str:
    num = f"{val:.{precision}f}"
    if label or unit:
        label_part = f"{label}: " if label else ""
        unit_part = f" {unit}" if unit else ""
        return f"{label_part}{num}{unit_part}"
    return num


def main() -> None:
    p = argparse.ArgumentParser(description="RMSD between paired 3D coordinate sets")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--combined', type=str, help='Path to combined file (first N ref, next N target)')
    g.add_argument('--ref', type=str, help='Path to reference coordinates file')
    p.add_argument('--tgt', type=str, help='Path to target coordinates file (required if --ref is used)')
    p.add_argument('--split', type=int, help='Number of reference lines in combined file')
    p.add_argument('--precision', type=int, default=4, help='Decimal places for output (default: 4)')
    p.add_argument('--label', type=str, help='Optional label to prefix (e.g., "RMSD")')
    p.add_argument('--unit', type=str, help='Optional unit to suffix (e.g., "nm")')
    p.add_argument('--out', type=str, help='Optional output file path to write the formatted line')

    args = p.parse_args()

    try:
        if args.combined:
            with open(args.combined, 'r', encoding='utf-8') as f:
                all_coords = parse_coords_from_lines(f.readlines())
            total = len(all_coords)
            if total == 0:
                raise ValueError("No coordinates found in combined file")
            if args.split is not None:
                n = args.split
                if 2 * n != total:
                    raise ValueError(f"--split {n} does not match total lines ({total}); expected total=2*N")
            else:
                if total % 2 != 0:
                    raise ValueError("Combined file has odd number of coordinate lines; specify --split")
                n = total // 2
            ref = all_coords[:n]
            tgt = all_coords[n:]
        else:
            if not args.tgt:
                raise ValueError("--tgt is required when using --ref")
            ref = read_coords_file(args.ref)
            tgt = read_coords_file(args.tgt)

        val = compute_rmsd(ref, tgt)
        text = format_value(val, args.precision, args.label, args.unit)

        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(text + "\n")
        else:
            print(text)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
