#!/usr/bin/env python3
"""VCF FILTER pass counter.

Reads a VCF from a file path or stdin, counts total variants, passed variants, and failed variants
based on the FILTER column. A variant is considered PASS if FILTER is exactly "PASS", ".", or
empty after trimming. All other values are considered FAIL.

Usage:
  python vcf_filter_tally.py input.vcf --format text
  zcat input.vcf.gz | python vcf_filter_tally.py - --format json

Exit codes:
  0 on success
  2 on input/format errors (e.g., unreadable file)
"""

import sys
import argparse
import gzip
import io
import json
from typing import TextIO, Tuple


def open_maybe_gzip(path: str) -> TextIO:
    """Open a plain text or gzipped file; '-' means stdin."""
    if path == '-' or path is None:
        return sys.stdin
    if path.endswith('.gz'):
        return io.TextIOWrapper(gzip.open(path, 'rb'), encoding='utf-8', errors='replace')
    return open(path, 'r', encoding='utf-8', errors='replace')


def tally_vcf_filter(handle: TextIO) -> Tuple[int, int, int]:
    total = 0
    passed = 0
    failed = 0

    for line in handle:
        if line.startswith('#'):
            continue  # skip headers
        # Strip only newline; keep tabs. Remove trailing CR if present.
        line = line.rstrip('\n')
        if line.endswith('\r'):
            line = line[:-1]
        # Split by tab only (VCF is TAB-delimited)
        fields = line.split('\t')
        if len(fields) < 7:
            # Malformed or incomplete line; skip from counts
            # If strict behavior is desired, this could raise an error instead.
            continue
        filt = fields[6].strip()
        total += 1
        if filt == 'PASS' or filt == '.' or filt == '':
            passed += 1
        else:
            failed += 1

    return total, passed, failed


def main() -> int:
    parser = argparse.ArgumentParser(description='Count PASS/FAIL from VCF FILTER column.')
    parser.add_argument('vcf', nargs='?', default='-', help="VCF path or '-' for stdin (supports .vcf.gz)")
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    args = parser.parse_args()

    try:
        with open_maybe_gzip(args.vcf) as fh:
            total, passed, failed = tally_vcf_filter(fh)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 2

    # Verify invariant; if mismatch, recompute failed as total - passed while warning.
    if passed + failed != total:
        # Non-fatal warning to stderr; keep deterministic output.
        print('WARNING: passed + failed != total; adjusting failed = total - passed', file=sys.stderr)
        failed = total - passed

    if args.format == 'json':
        print(json.dumps({
            'total_variants': total,
            'passed_variants': passed,
            'failed_variants': failed
        }, separators=(',', ':')))
    else:
        # Strict three-line text format
        sys.stdout.write(f"Total variants: {total}\n")
        sys.stdout.write(f"Passed variants: {passed}\n")
        sys.stdout.write(f"Failed variants: {failed}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
