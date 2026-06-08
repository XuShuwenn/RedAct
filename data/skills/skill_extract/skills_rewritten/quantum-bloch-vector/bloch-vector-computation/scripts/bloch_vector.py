#!/usr/bin/env python3
"""Bloch vector computation utility.

Reads theta and phi angles from an input text file, computes Bloch vector
components (rx, ry, rz), and writes them with explicit sign and 3-decimal
format to an output file.

Usage:
    python bloch_vector.py <input_path> <output_path> [--radians]

Notes:
- By default, angles are interpreted as degrees and converted to radians.
- If --radians is supplied, input angles are treated as radians directly.
- The parser extracts the first two numeric tokens in the file as theta and phi.
- The output format is:
    rx: +0.XXX
    ry: +0.XXX
    rz: +0.XXX
"""

import argparse
import math
import re
import sys
from typing import Tuple


def parse_angles(text: str) -> Tuple[float, float]:
    """Extract theta and phi as floats from arbitrary text.

    Strategy:
    - Find the first two numeric tokens using a regex that captures integers and decimals
      with optional sign.
    - Returns (theta, phi).
    - Raises ValueError if fewer than two numbers are found.
    """
    # Regex matches numbers like -12, +3.45, 0.5, .75, 2., 1e-3, -4.2E+1
    num_pattern = re.compile(r"[+\-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+\-]?\d+)?")
    nums = num_pattern.findall(text)
    if len(nums) < 2:
        raise ValueError("Could not find two numeric angle values (theta, phi) in input.")
    theta = float(nums[0])
    phi = float(nums[1])
    return theta, phi


def to_radians(theta: float, phi: float, already_radians: bool) -> Tuple[float, float]:
    """Convert to radians if needed."""
    if already_radians:
        return theta, phi
    rad = math.pi / 180.0
    return theta * rad, phi * rad


def bloch_components(theta_rad: float, phi_rad: float) -> Tuple[float, float, float]:
    """Compute Bloch vector components from radians."""
    rx = math.sin(theta_rad) * math.cos(phi_rad)
    ry = math.sin(theta_rad) * math.sin(phi_rad)
    rz = math.cos(theta_rad)
    return rx, ry, rz


def format_signed_3dp(x: float) -> str:
    """Format with explicit sign and exactly three decimals."""
    # Using format spec ensures trailing zeros and explicit sign
    return f"{x:+0.3f}"


def magnitude(rx: float, ry: float, rz: float) -> float:
    return math.sqrt(rx * rx + ry * ry + rz * rz)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_output(path: str, rx: float, ry: float, rz: float) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"rx: {format_signed_3dp(rx)}\n")
        f.write(f"ry: {format_signed_3dp(ry)}\n")
        f.write(f"rz: {format_signed_3dp(rz)}\n")


def main():
    parser = argparse.ArgumentParser(description="Compute Bloch vector components from angles")
    parser.add_argument("input", help="Path to input text containing theta and phi")
    parser.add_argument("output", help="Path to write formatted rx, ry, rz")
    parser.add_argument("--radians", action="store_true", help="Treat input angles as radians (default: degrees)")
    args = parser.parse_args()

    try:
        text = read_text(args.input)
        theta, phi = parse_angles(text)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    theta_rad, phi_rad = to_radians(theta, phi, already_radians=args.radians)

    rx, ry, rz = bloch_components(theta_rad, phi_rad)

    # Optional sanity check: magnitude should be ~1
    mag = magnitude(rx, ry, rz)
    if not (0.999 <= mag <= 1.001):
        print(f"WARNING: Vector magnitude deviates from 1 (|r|={mag:.6f}). This may be due to input or rounding.", file=sys.stderr)

    try:
        write_output(args.output, rx, ry, rz)
    except Exception as e:
        print(f"ERROR writing output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
