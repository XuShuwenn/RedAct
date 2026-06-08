#!/usr/bin/env python3
"""Validate field_values.json against field_info.json and common formatting rules.

Usage:
  python3 scripts/validate_field_values.py /path/field_info.json /path/field_values.json

Checks:
- Every field_id exists in field_info.json
- Checkbox values appear plausible (e.g., '/1' or '/2')
- 'Date'-like field_ids use YYYY-MM-DD
- 'Amount'-like field_ids contain numeric values (suggests normalization)

Exit code is 0 with warnings printed to stdout. For stricter behavior,
use shell `grep`/CI to fail on the word 'WARNING'.
"""
import json
import re
import sys
from typing import Dict

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NUMERIC_RE = re.compile(r"^[-+]?(\d+)(\.\d+)?$")


def load_json(path: str):
    with open(path, 'r') as f:
        return json.load(f)


def sanitize_numeric(s: str) -> str:
    # Drop commas and currency symbols for validation suggestion
    return s.replace(",", "").replace("$", "").strip()


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 validate_field_values.py <field_info.json> <field_values.json>")
        sys.exit(2)

    info_path, values_path = sys.argv[1], sys.argv[2]
    info = load_json(info_path)
    values = load_json(values_path)

    id_to_type: Dict[str, str] = {d.get('field_id'): d.get('type') for d in info}
    valid_ids = set(id_to_type.keys())

    warnings = 0

    for i, entry in enumerate(values, 1):
        fid = entry.get('field_id')
        val = entry.get('value', "")
        if fid not in valid_ids:
            print(f"WARNING: [{i}] field_id not found in field_info: {fid}")
            warnings += 1
            continue
        ftype = id_to_type.get(fid, '')
        lower_id = (fid or '').lower()

        # Checkbox plausibility
        if ftype in ("checkbox", "radio_group"):
            if val not in {"/1", "/2", "/Yes", "Yes", "On"}:
                print(f"WARNING: [{i}] checkbox/radio value '{val}' may be invalid for {fid}. Typical values are '/1' or '/2'.")
                warnings += 1

        # Date heuristic
        if "date" in lower_id:
            if not isinstance(val, str) or not DATE_RE.match(val.strip()):
                print(f"WARNING: [{i}] value for date-like field {fid} should be YYYY-MM-DD (got '{val}').")
                warnings += 1

        # Amount heuristic
        if any(k in lower_id for k in ("amount", "claimamount")):
            sval = str(val)
            sv = sanitize_numeric(sval)
            if not NUMERIC_RE.match(sv):
                print(f"WARNING: [{i}] amount-like field {fid} should be numeric (consider '1500.00'). Got '{val}'.")
                warnings += 1

    if warnings == 0:
        print("OK: field_values look consistent with field_info and formatting heuristics.")
    else:
        print(f"Completed with {warnings} warning(s). Review and adjust field_values.json.")


if __name__ == "__main__":
    main()
