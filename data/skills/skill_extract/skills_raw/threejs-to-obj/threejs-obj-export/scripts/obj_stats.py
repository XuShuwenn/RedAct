#!/usr/bin/env python3
"""
Quick OBJ stats: counts vertices, normals, faces, and objects.

Usage:
  python3 scripts/obj_stats.py path/to/model.obj
"""
import sys
from collections import Counter

if len(sys.argv) != 2:
    print("Usage: python3 scripts/obj_stats.py path/to/model.obj", file=sys.stderr)
    sys.exit(1)

p = sys.argv[1]
try:
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        counts = Counter()
        for line in f:
            if line.startswith('v '):
                counts['v'] += 1
            elif line.startswith('vn '):
                counts['vn'] += 1
            elif line.startswith('f '):
                counts['f'] += 1
            elif line.startswith('o '):
                counts['o'] += 1
        print(f"File: {p}")
        print(f"Objects (o): {counts['o']}")
        print(f"Vertices (v): {counts['v']}")
        print(f"Normals (vn): {counts['vn']}")
        print(f"Faces (f): {counts['f']}")
except FileNotFoundError:
    print(f"ERROR: File not found: {p}", file=sys.stderr)
    sys.exit(1)
