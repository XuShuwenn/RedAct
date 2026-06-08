#!/usr/bin/env python3
"""
Detect empty-string object keys in JSON documents.

Usage:
  python validate-empty-json-keys.py --file payload.json
  cat payload.json | python validate-empty-json-keys.py

Exit codes:
  0: No empty keys found
  1: One or more empty keys found or input error
"""
import argparse
import json
import sys
from typing import Any, List


def find_empty_keys(obj: Any, path: str = "$") -> List[str]:
    findings = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key_path = f"{path}/{k}" if k != "" else f"{path}/"  # show empty segment
            if k == "":
                findings.append(key_path)
            findings.extend(find_empty_keys(v, key_path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            findings.extend(find_empty_keys(v, f"{path}[{i}]"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect empty-string JSON keys")
    parser.add_argument("--file", help="Path to JSON file (reads stdin if omitted)")
    args = parser.parse_args()

    try:
        data_str = None
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                data_str = f.read()
        else:
            data_str = sys.stdin.read()
        data = json.loads(data_str)
    except Exception as e:
        print(f"ERROR: Failed to read/parse JSON: {e}", file=sys.stderr)
        return 1

    findings = find_empty_keys(data)
    if findings:
        print("Empty JSON keys detected at:")
        for p in findings:
            print(f"  {p}")
        return 1
    else:
        print("No empty JSON keys found.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
