#!/usr/bin/env python3
"""RMSD tools: parse 3D coordinates and compute direct RMSD.

Features:
- Parse coordinates from two files or from one file with two blocks
- Robust parsing: comments (#), spaces/tabs/commas, blank lines
- Direct (no-alignment) RMSD
- Fixed-decimal formatting and optional file output

Usage examples:
  python rmsd_tools.py --ref ref.txt --target tgt.txt --units nm --decimals 4
  python rmsd_tools.py --file coords.txt --n 3 --units nm --decimals 4 --output output.txt

The script intentionally does not perform alignment. If superposition is required,
implement Kabsch externally, then feed the superposed coordinates to this tool.
"""

import argparse
import math
import sys
from typing import List, Tuple


Vec3 = Tuple[float, float, float]


def _strip_comment(line: str) -> str:
    idx = line.find('#')
    return line[:idx] if idx != -1 else line


def _parse_vec3_line(line: str) -> Vec3:
    # Remove comments and normalize separators
    s = _strip_comment(line).strip()
    if not s:
        raise ValueError("empty")
    s = s.replace(',', ' ')
    parts = s.split()
    if len(parts) == 0:
        raise ValueError("empty")
    if len(parts) != 3:
        raise ValueError(f"expected 3 columns, got {len(parts)}: {parts}")
    try:
        x, y, z = (float(parts[0]), float(parts[1]), float(parts[2]))
    except ValueError as e:
        raise ValueError(f"non-numeric value in line: {line.rstrip()}" ) from e
    return (x, y, z)


def parse_coords_text(text: str) -> List[Vec3]:
    coords: List[Vec3] = []
    for raw in text.splitlines():
        try:
            v = _parse_vec3_line(raw)
            coords.append(v)
        except ValueError:
            # Skip blank/comment-only lines silently; re-raise for other issues
            s = _strip_comment(raw).strip()
            if s:
                # had content but failed to parse
                raise
            # else ignore blank
    return coords


def parse_coords_file(path: str) -> List[Vec3]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return parse_coords_text(f.read())
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def rmsd_direct(ref: List[Vec3], tgt: List[Vec3]) -> float:
    if len(ref) != len(tgt):
        raise ValueError(f"coordinate count mismatch: {len(ref)} vs {len(tgt)}")
    n = len(ref)
    if n == 0:
        raise ValueError("no coordinates provided")
    ssq = 0.0
    for (rx, ry, rz), (tx, ty, tz) in zip(ref, tgt):
        dx = rx - tx
        dy = ry - ty
        dz = rz - tz
        ssq += dx*dx + dy*dy + dz*dz
    return math.sqrt(ssq / n)


def load_two_sets(args) -> Tuple[List[Vec3], List[Vec3]]:
    if args.ref and args.target:
        ref = parse_coords_file(args.ref)
        tgt = parse_coords_file(args.target)
        return ref, tgt
    if args.file and args.n is not None:
        all_coords = parse_coords_file(args.file)
        n = int(args.n)
        if n <= 0:
            raise ValueError("--n must be positive")
        if len(all_coords) < 2 * n:
            raise ValueError(f"insufficient coordinates in {args.file}: need at least {2*n}, got {len(all_coords)}")
        ref = all_coords[:n]
        tgt = all_coords[n:n*2]
        return ref, tgt
    raise ValueError("Provide either --ref and --target, or --file and --n")


def main():
    p = argparse.ArgumentParser(description="Compute direct RMSD between two 3D coordinate sets")
    g = p.add_mutually_exclusive_group(required=False)
    p.add_argument('--ref', help='reference coordinates file (3 columns per line)')
    p.add_argument('--target', help='target coordinates file (3 columns per line)')
    p.add_argument('--file', help='single file containing reference then target blocks')
    p.add_argument('--n', type=int, help='number of atoms per block when using --file')
    p.add_argument('--units', default='nm', help='units label to display (default: nm)')
    p.add_argument('--decimals', type=int, default=4, help='decimal places for output (default: 4)')
    p.add_argument('--output', help='optional output file to write formatted RMSD line')

    args = p.parse_args()

    try:
        ref, tgt = load_two_sets(args)
        value = rmsd_direct(ref, tgt)
        if value < 0 and value > -1e-12:
            value = 0.0  # clamp tiny negative due to any numerical noise
        fmt = f"{{:.{args.decimals}f}}"
        line = f"RMSD: {fmt.format(value)} {args.units}\n"
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(line)
        else:
            sys.stdout.write(line)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
