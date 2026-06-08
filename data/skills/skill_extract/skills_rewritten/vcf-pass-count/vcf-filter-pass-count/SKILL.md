---
name: vcf-filter-pass-count
description: "Count total, PASS, and failed variants in VCF files by evaluating the FILTER column with robust parsing and verification."
---

# VCF FILTER Pass/Fail Counting

This skill provides a reliable workflow to count total variant records and classify them as PASS or failed using the VCF FILTER column. It is designed for tasks that require precise counting from VCFs while avoiding common parsing mistakes.

## When to Use

Use this skill when the user asks to:
- Count how many variants passed or failed filters in a VCF
- Report totals by FILTER status (e.g., PASS vs non-PASS)
- Produce summary counts derived from the VCF FILTER column

## Core Workflow

1. Load the VCF
   - Accept the file path from the task or user.
   - If the file may be compressed, ensure your tooling can read .gz.

2. Iterate over records
   - Skip header/meta lines starting with '#'.
   - Split data lines by tab characters only (VCF is tab-delimited).
   - Verify there are at least 7 columns before accessing FILTER (index 6, 1-based column 7).

3. Determine pass/fail per record
   - Read FILTER value and trim surrounding whitespace.
   - A record passes if FILTER is exactly "PASS" or "." (or truly empty), meaning no filter is applied or all filters were passed.
   - Any other FILTER string (including multiple semicolon-separated tags) indicates failure.

4. Count
   - Maintain counters: total (non-header data lines), passed, failed.
   - For each data line: total += 1; then increment passed or failed based on the rule above.

5. Validate counts
   - Ensure total == passed + failed before finalizing.
   - If mismatched, re-check for malformed lines, incorrect delimiter usage, or header inclusion.

6. Produce output in the exact format requested by the task
   - Use the counters to render the required lines/order/labels.
   - Do not add extra commentary or different labels when a strict format is specified.

## Verification

Perform at least one of these checks before finalizing:
- Invariant check: total == passed + failed.
- Spot-check a few records manually (inspect lines with "PASS" and non-PASS values) to confirm logic.
- Cross-check with an independent method, e.g., awk:
  - Total variants (non-header): `awk -F"\t" '!/^#/ {c++} END {print c}' file.vcf`
  - Passed variants (FILTER == PASS or . or empty):
    `awk -F"\t" '!/^#/ {f=$7; gsub(/^\s+|\s+$/, "", f); if (f=="PASS" || f=="." || f=="") p++} END {print p}' file.vcf`
  - Failed variants: compute total - passed.

If tools like bcftools are available, you can also approximate a cross-check with:
- Passed by PASS only: `bcftools view -f PASS -H file.vcf | wc -l`
Note: This does not count '.' as pass by default; adjust your final counts accordingly.

## Common Pitfalls and How to Avoid Them

- Counting headers as variants:
  - Always skip lines that start with '#'.
- Using the wrong column:
  - FILTER is column 7 (0-based index 6). QUAL is column 6; do not confuse them.
- Incorrect delimiter:
  - VCF is tab-delimited; use "\t". Splitting on spaces can corrupt columns.
- Misinterpreting '.' or empty FILTER:
  - In many tasks, '.' or empty means no filter applied, which should be treated as pass. Confirm task rules and implement accordingly.
- Loose text matching for PASS:
  - Do not grep the entire line for "PASS"; read the FILTER field only and compare exact values after trimming whitespace.
- Failing to validate totals:
  - If total != passed + failed, you likely included headers, used the wrong delimiter, or encountered malformed lines—fix before finalizing.
- Ignoring trailing carriage returns or whitespace:
  - Trim whitespace from the FILTER value before comparison.
- Compressed inputs:
  - If the file ends with .gz, open with gzip-aware tools.

## Optional Script Usage

You can use the provided script to robustly compute the counts:

- Example (JSON output):
  - `python scripts/vcf_filter_count.py --input file.vcf --format json`
- Example (plain text):
  - `python scripts/vcf_filter_count.py --input file.vcf --format text`

Script behavior:
- Skips header lines (#)
- Splits on tabs
- Counts a variant as pass if FILTER in {"PASS", ".", ""}
- Prints total, passed, failed
- Warns about malformed lines and ensures the invariant total == passed + failed

Use the script’s output to render the exact result format required by your task.
