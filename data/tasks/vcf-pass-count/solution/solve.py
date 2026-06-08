#!/usr/bin/env python3
"""Solve vcf-pass-count task."""

def main():
    input_path = "/root/input.vcf"
    output_path = "/root/output.txt"

    total = 0
    passed = 0
    failed = 0

    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            # Skip header lines
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 7:
                continue
            total += 1
            filter_val = parts[6]
            if filter_val == 'PASS' or filter_val == '.':
                passed += 1
            else:
                failed += 1

    result = f"Total variants: {total}\nPassed variants: {passed}\nFailed variants: {failed}"
    with open(output_path, 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()