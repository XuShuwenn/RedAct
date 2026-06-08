#!/usr/bin/env python3
"""
Safely update a metrics CSV by replacing only the value column on metric rows.

- Preserves comment lines (lines starting with '#') exactly, including whitespace.
- Leaves non-matching metric rows unchanged.
- Updates are done in-place by writing to a temp file then renaming.

CSV assumptions:
- Each metric row is in the form: metric_name,value
- Comment lines start with '#'

Usage:
  python3 scripts/update_csv_values.py --csv /root/network_stats.csv --json metrics.json

If --json is omitted, reads JSON from stdin.
"""
import argparse
import json
import os
import re
import sys
import tempfile

ROW_RE = re.compile(r'^(?P<key>[^#,\s][^,]*?)\s*,\s*(?P<val>.*)$')


def load_mapping(json_path: str | None):
    if json_path:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return json.load(sys.stdin)


def update_csv(csv_path: str, mapping: dict):
    # Write to temp file, then replace
    dir_name = os.path.dirname(csv_path) or '.'
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_csv_', suffix='.txt')
    os.close(fd)

    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as src, \
             open(tmp_path, 'w', encoding='utf-8', newline='') as dst:
            for line in src:
                # Preserve comment lines exactly
                if line.lstrip().startswith('#'):
                    dst.write(line)
                    continue
                m = ROW_RE.match(line.rstrip('\n'))
                if not m:
                    # Unrecognized line, write back as-is
                    dst.write(line)
                    continue
                key = m.group('key')
                val = m.group('val')
                if key in mapping:
                    # Replace value only; keep key and a single comma separator
                    new_val = mapping[key]
                    # Convert Python values to a concise string
                    if isinstance(new_val, bool):
                        out_val = 'true' if new_val else 'false'
                    else:
                        out_val = str(new_val)
                    dst.write(f"{key},{out_val}\n")
                else:
                    dst.write(line)
        os.replace(tmp_path, csv_path)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


def main():
    parser = argparse.ArgumentParser(description='Safely update metrics CSV value column')
    parser.add_argument('--csv', required=True, help='Path to CSV template')
    parser.add_argument('--json', required=False, help='Path to JSON mapping; if omitted, reads from stdin')
    args = parser.parse_args()

    mapping = load_mapping(args.json)
    if not isinstance(mapping, dict):
        print('ERROR: JSON must be an object mapping metric_name -> value', file=sys.stderr)
        sys.exit(1)

    update_csv(args.csv, mapping)


if __name__ == '__main__':
    main()
