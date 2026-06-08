#!/usr/bin/env python3
"""Update a metric,value CSV with computed results while preserving comments.

- Preserves the header line exactly.
- Preserves lines starting with '#'.
- For data lines, replaces the value after the first comma when the metric is present in the results mapping.

Usage:
  python update_csv_values.py --csv /path/to/network_stats.csv --json /path/to/results.json
  cat results.json | python update_csv_values.py --csv /path/to/network_stats.csv

Results JSON format:
{
  "protocol_tcp": 123,
  "is_traffic_benign": "true",
  ...
}

Notes:
- Boolean values in the mapping will be converted to lowercase strings ("true"/"false").
- Other values are converted with str(value) without extra rounding.
"""

import argparse
import json
import sys
from typing import Dict


def _to_csv_value(v):
    if isinstance(v, bool):
        return str(v).lower()
    return str(v)


def update_csv(csv_path: str, results: Dict[str, object]) -> None:
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    out_lines = []
    for idx, line in enumerate(lines):
        # Preserve header exactly
        if idx == 0:
            out_lines.append(line)
            continue

        # Keep empty lines as-is
        if not line:
            out_lines.append(line)
            continue

        # Preserve comment lines exactly
        stripped = line.lstrip()
        if stripped.startswith('#'):
            out_lines.append(line)
            continue

        # Data line: replace value if metric is known
        if ',' in line:
            metric, _ = line.split(',', 1)
        else:
            metric = line
        metric = metric.strip()

        if metric in results:
            out_lines.append(f"{metric},{_to_csv_value(results[metric])}")
        else:
            out_lines.append(line)

    # Ensure trailing newline
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(out_lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Update metric,value CSV with computed results")
    parser.add_argument('--csv', required=True, help='Path to CSV file to update')
    parser.add_argument('--json', help='Path to JSON results mapping; if omitted, read from stdin')
    args = parser.parse_args()

    if args.json:
        with open(args.json, 'r', encoding='utf-8') as jf:
            results = json.load(jf)
    else:
        data = sys.stdin.read()
        if not data.strip():
            print('ERROR: No JSON provided on stdin and --json not set.', file=sys.stderr)
            sys.exit(1)
        results = json.loads(data)

    if not isinstance(results, dict):
        print('ERROR: Results JSON must be an object mapping metric->value.', file=sys.stderr)
        sys.exit(1)

    update_csv(args.csv, results)


if __name__ == '__main__':
    main()
