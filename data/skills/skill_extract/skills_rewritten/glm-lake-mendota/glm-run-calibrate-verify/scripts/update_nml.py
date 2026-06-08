#!/usr/bin/env python3
"""
Safely update specific keys in a Fortran namelist (e.g., glm3.nml) within a given group.

Usage:
  python3 scripts/update_nml.py --file glm3.nml --group <namelist_group> \
    --set key1=value1 --set key2=value2 [--backup-suffix .bak]

Notes:
- Preserves formatting and comments as much as possible by only replacing the
  value portion of existing key assignments within the specified group.
- If a key does not exist in the group, it will be inserted before the group's '/' terminator.
- Creates a backup copy by default.
"""

import argparse
import os
import re
import shutil
import sys
from typing import List, Tuple

ASSIGN_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*(.*?)(\s*(?:!,.*)?)$")
GROUP_START_RE = re.compile(r"^\s*&\s*([A-Za-z0-9_]+)\s*$")
GROUP_END_RE = re.compile(r"^\s*/\s*$")


def parse_set_args(set_args: List[str]) -> List[Tuple[str, str]]:
    pairs = []
    for s in set_args:
        if "=" not in s:
            raise ValueError(f"--set expects key=value, got: {s}")
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise ValueError(f"Invalid key in --set: {s}")
        pairs.append((k, v))
    return pairs


def update_group(lines: List[str], group: str, updates: List[Tuple[str, str]]) -> List[str]:
    # Locate group boundaries
    start_idx = None
    end_idx = None
    group_lower = group.lower()
    for i, line in enumerate(lines):
        m = GROUP_START_RE.match(line)
        if m and m.group(1).lower() == group_lower:
            start_idx = i
            break
    if start_idx is None:
        raise ValueError(f"Group '&{group}' not found")

    for j in range(start_idx + 1, len(lines)):
        if GROUP_END_RE.match(lines[j]):
            end_idx = j
            break
    if end_idx is None:
        raise ValueError(f"Group '&{group}' is not properly terminated with '/'")

    # Build a map for quick lookup (case-insensitive key)
    key_to_line_idx = {}
    for i in range(start_idx + 1, end_idx):
        m = ASSIGN_RE.match(lines[i])
        if m:
            key_lower = m.group(1).lower()
            key_to_line_idx[key_lower] = i

    # Apply updates
    for key, value in updates:
        k_lower = key.lower()
        if k_lower in key_to_line_idx:
            i = key_to_line_idx[k_lower]
            m = ASSIGN_RE.match(lines[i])
            # Preserve trailing comment if present
            comment = m.group(3) if m else ''
            # Keep a comma if original value appeared to end with a comma; otherwise, do not enforce
            # For robustness, append no comma; GLM namelist generally tolerates lines without trailing commas.
            lines[i] = re.sub(ASSIGN_RE, f"{key} = {value}\\1", lines[i]) if False else f"  {key} = {value}{comment}\n"
        else:
            # Insert new assignment before end of group
            insertion = f"  {key} = {value}\n"
            lines.insert(end_idx, insertion)
            end_idx += 1
    return lines


def main():
    ap = argparse.ArgumentParser(description="Safe updater for Fortran namelist files")
    ap.add_argument("--file", required=True, help="Path to namelist file (e.g., glm3.nml)")
    ap.add_argument("--group", required=True, help="Namelist group to edit (without '&')")
    ap.add_argument("--set", action="append", default=[], help="key=value to set (can repeat)")
    ap.add_argument("--backup-suffix", default=".bak", help="Backup suffix to use")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    updates = parse_set_args(args.set)
    if not updates:
        print("ERROR: No --set key=value provided", file=sys.stderr)
        sys.exit(1)

    backup_path = args.file + args.backup_suffix
    try:
        shutil.copy2(args.file, backup_path)
    except Exception as e:
        print(f"ERROR: Failed to create backup: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines_new = update_group(lines, args.group, updates)
        with open(args.file, "w", encoding="utf-8") as f:
            f.writelines(lines_new)
    except Exception as e:
        # Attempt restore on failure
        try:
            shutil.copy2(backup_path, args.file)
        except Exception:
            pass
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Summary output
    print(f"Updated {args.file} in group '&{args.group}'. Backup: {backup_path}")
    for k, v in updates:
        print(f"  {k} = {v}")


if __name__ == "__main__":
    main()
