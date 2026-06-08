#!/usr/bin/env python3
"""Parse key-value style parameter files into JSON.

Features:
- Accepts separators ':', '=', or whitespace between key and value
- Ignores blank lines and comments starting with '#', '//' or ';'
- Extracts the first numeric token from each value (supports scientific notation)
- Case-insensitive keys; canonical form is lowercase

Usage:
  python scripts/kvfile.py --file /root/input.txt --key h --key k --key D
  python scripts/kvfile.py --file /root/input.txt --all

Outputs a JSON object to stdout with parsed key: float pairs.
Exits with non-zero code on missing requested keys or parse errors.
"""

import argparse
import json
import math
import re
import sys
from typing import Dict, Optional

COMMENT_PREFIXES = ("#", "//", ";")
NUM_RE = re.compile(r"[-+]?((\d+\.?\d*)|(\.\d+))([eE][-+]?\d+)?")


def parse_kv_file(path: str) -> Dict[str, float]:
    params: Dict[str, float] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                if any(line.startswith(p) for p in COMMENT_PREFIXES):
                    continue
                # Split key and value by first occurrence of separator
                key: Optional[str] = None
                value_part: Optional[str] = None
                for sep in (":", "=", None):
                    if sep is None:
                        # fallback: split on whitespace
                        parts = line.split()
                        if len(parts) >= 2:
                            key = parts[0]
                            value_part = " ".join(parts[1:])
                        break
                    if sep in line:
                        k, v = line.split(sep, 1)
                        key = k.strip()
                        value_part = v.strip()
                        break
                if not key or value_part is None:
                    # If no separator and only one token, skip
                    continue
                key_norm = key.strip().lower()
                m = NUM_RE.search(value_part)
                if not m:
                    # no numeric content found; skip this line
                    continue
                try:
                    val = float(m.group(0))
                except ValueError:
                    continue
                if math.isfinite(val):
                    params[key_norm] = val
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"ERROR: Unable to read file {path}: {e}", file=sys.stderr)
        sys.exit(2)
    return params


def main():
    ap = argparse.ArgumentParser(description="Parse parameter file into JSON")
    ap.add_argument("--file", required=True, help="Path to input file")
    ap.add_argument("--key", action="append", dest="keys", help="Parameter key to extract (can repeat)")
    ap.add_argument("--all", action="store_true", help="Return all parsed parameters")
    args = ap.parse_args()

    if not args.all and not args.keys:
        ap.error("Specify --all or at least one --key")

    params = parse_kv_file(args.file)

    if args.keys:
        missing = [k for k in args.keys if k.lower() not in params]
        if missing:
            print(f"ERROR: Missing required keys: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
        out = {k: params[k.lower()] for k in args.keys}
    else:
        out = params

    print(json.dumps(out, separators=(",", ":")))


if __name__ == "__main__":
    main()
