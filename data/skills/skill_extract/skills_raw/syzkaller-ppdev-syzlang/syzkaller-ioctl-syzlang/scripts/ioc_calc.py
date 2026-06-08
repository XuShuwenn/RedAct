#!/usr/bin/env python3
"""
Compute Linux ioctl command numbers with optional per-arch sizes.

Usage examples:
  # Simple no-arg (_IO) and read (_IOR) examples
  python3 scripts/ioc_calc.py --type-char p \
    --def FOO:_IO:0x80 \
    --def BAR:_IOR:0x81:1

  # Write (_IOW) with arch-specific payload sizes (amd64_size:386_size)
  python3 scripts/ioc_calc.py --type-char p \
    --def BAZ:_IOW:0x82:16:8

This prints lines suitable for a .const file. If an i386 override is
provided and differs from the default, output is: NAME = default, 386:override
Otherwise, a single value is printed.
"""

import argparse
from typing import Tuple

# Linux _IOC bit widths (asm-generic/ioctl.h)
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

# Directions (Linux): keep as 0/1/2/3
_IOC_NONE = 0
_IOC_WRITE = 1  # historically _IOC_WRITE
_IOC_READ = 2   # historically _IOC_READ
# _IOC_READ | _IOC_WRITE == 3 for _IOWR

def _IOC(dir_: int, type_: int, nr: int, size: int) -> int:
    return ((dir_ << _IOC_DIRSHIFT) |
            (type_ << _IOC_TYPESHIFT) |
            (nr << _IOC_NRSHIFT) |
            (size << _IOC_SIZESHIFT)) & 0xFFFFFFFF

def _IO(type_: int, nr: int) -> int:
    return _IOC(_IOC_NONE, type_, nr, 0)

def _IOR(type_: int, nr: int, size: int) -> int:
    return _IOC(_IOC_READ, type_, nr, size)

def _IOW(type_: int, nr: int, size: int) -> int:
    return _IOC(_IOC_WRITE, type_, nr, size)

def _IOWR(type_: int, nr: int, size: int) -> int:
    return _IOC(_IOC_READ | _IOC_WRITE, type_, nr, size)

def parse_def(s: str) -> Tuple[str, str, int, int, int]:
    """Parse one --def: NAME:DIR:NR[:SIZE64[:SIZE32]]
    DIR in {_IO,_IOR,_IOW,_IOWR}
    NR accepts decimal or hex (e.g., 0x80). SIZE64 and SIZE32 are optional.
    If SIZE64 missing, size=0. If SIZE32 missing, use SIZE64 for both.
    Returns (name, dir, nr, size64, size32).
    """
    parts = s.split(':')
    if len(parts) < 3:
        raise ValueError(f"Bad def '{s}': need NAME:DIR:NR[:SIZE64[:SIZE32]]")
    name, dir_, nr_s, *rest = parts
    nr = int(nr_s, 0)
    if not rest:
        size64 = 0
        size32 = 0
    elif len(rest) == 1:
        size64 = int(rest[0], 0)
        size32 = size64
    else:
        size64 = int(rest[0], 0)
        size32 = int(rest[1], 0)
    return name, dir_, nr, size64, size32

def main():
    ap = argparse.ArgumentParser(description="Compute Linux ioctl numbers")
    ap.add_argument('--type-char', required=True,
                    help="Single character used by the ioctl type (e.g., 'p')")
    ap.add_argument('--def', dest='defs', action='append', default=[],
                    help="Definition: NAME:DIR:NR[:SIZE64[:SIZE32]] where DIR is one of _IO,_IOR,_IOW,_IOWR")
    args = ap.parse_args()

    if len(args.type_char) != 1:
        raise SystemExit("--type-char must be a single character")
    type_val = ord(args.type_char)

    for d in args.defs:
        name, dir_, nr, size64, size32 = parse_def(d)
        if dir_ == '_IO':
            v64 = _IO(type_val, nr)
            v32 = v64
        elif dir_ == '_IOR':
            v64 = _IOR(type_val, nr, size64)
            v32 = _IOR(type_val, nr, size32)
        elif dir_ == '_IOW':
            v64 = _IOW(type_val, nr, size64)
            v32 = _IOW(type_val, nr, size32)
        elif dir_ == '_IOWR':
            v64 = _IOWR(type_val, nr, size64)
            v32 = _IOWR(type_val, nr, size32)
        else:
            raise SystemExit(f"Unknown DIR '{dir_}' in '{d}'")

        v64 &= 0xFFFFFFFF
        v32 &= 0xFFFFFFFF
        if v64 != v32:
            print(f"{name} = {v64}, 386:{v32}")
        else:
            print(f"{name} = {v64}")

if __name__ == '__main__':
    main()
