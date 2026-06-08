#!/usr/bin/env python3
"""Robust VCF FILTER pass/fail counter.

Features:
- Skips VCF headers (#)
- Tab-delimited parsing (uses column 7 as FILTER)
- Treats FILTER == "PASS" or "." or empty as pass; everything else as fail
- Supports plain text or JSON output
- Handles gzip-compressed input (.gz)

Usage:
  python scripts/vcf_filter_count.py --input input.vcf --format json
  python scripts/vcf_filter_count.py --input input.vcf.gz --format text
  cat input.vcf | python scripts/vcf_filter_count.py --format json
"""

import sys
import argparse
import gzip
import json
from typing import TextIO


def open_input(path: str) -> TextIO:
    if path == '-' or path is None:
        return sys.stdin
    if path.endswith('.gz'):
        return gzip.open(path, 'rt', encoding='utf-8', newline='')
    return open(path, 'r', encoding='utf-8', newline='')


def count_vcf_filter(fp: TextIO) -> dict:
    total = 0
    passed = 0
    failed = 0
    skipped_malformed = 0

    for raw in fp:
        if not raw:
            continue
        line = raw.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        # VCF is tab-delimited
        fields = line.split('\t')
        if len(fields) < 7:
            skipped_malformed += 1
            continue
        filt = fields[6].strip()
        if filt == 'PASS' or filt == '.' or filt == '':
            passed += 1
        else:
            failed += 1
        total += 1

    if total != passed + failed:
        # This should not happen; report for debugging.
        # Do not fail hard; return info to caller.
        pass

    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped_malformed': skipped_malformed,
        'invariant_ok': (total == passed + failed),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description='Count PASS vs failed variants from VCF FILTER column.')
    ap.add_argument('--input', '-i', default='-', help='VCF file path (use - for stdin). Supports .gz')
    ap.add_argument('--format', '-f', choices=['json', 'text'], default='json', help='Output format')
    args = ap.parse_args()

    try:
        with open_input(args.input) as fp:
            stats = count_vcf_filter(fp)
    except FileNotFoundError:
        print(f'ERROR: Input file not found: {args.input}', file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(2)

    if args.format == 'json':
        # Emit a compact, deterministic JSON object
        out = {
            'total': stats['total'],
            'passed': stats['passed'],
            'failed': stats['failed'],
            'invariant_ok': stats['invariant_ok'],
            'skipped_malformed': stats['skipped_malformed'],
        }
        print(json.dumps(out, separators=(',', ':'), sort_keys=True))
    else:
        # Plain text lines, suitable for quick reading
        print(f'Total: {stats["total"]}')
        print(f'Passed: {stats["passed"]}')
        print(f'Failed: {stats["failed"]}')
        if not stats['invariant_ok']:
            print(f'Note: skipped_malformed={stats["skipped_malformed"]} (total != passed+failed)', file=sys.stderr)


if __name__ == '__main__':
    main()
