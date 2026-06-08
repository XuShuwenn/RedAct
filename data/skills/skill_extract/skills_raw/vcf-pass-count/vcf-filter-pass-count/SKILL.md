---
name: vcf-filter-pass-count
description: "Use this skill to tally total, PASS, and non-PASS variants from a VCF’s FILTER column and produce an exact three-line summary."
---

# VCF FILTER Pass Counting

Count how many variants in a VCF pass filtering based on the FILTER column, and emit a strict three-line summary.

## When to Use

Activate this skill whenever you need to:
- Count total variant records in a VCF (excluding header lines)
- Count how many variants passed filtering (FILTER is PASS or missing/empty)
- Count how many variants failed (any FILTER value other than PASS, '.', or empty)
- Write results in exactly three lines: Total, Passed, Failed

## Core Workflow

1. Read the VCF file.
2. Skip header lines (any line starting with '#').
3. For each data line (variant record):
   - Split by TAB (VCF is tab-delimited; do not split on generic whitespace).
   - Inspect column 7 (1-indexed; zero-based index 6) = FILTER.
   - Normalize the FILTER value by trimming whitespace and removing trailing carriage returns.
4. Classification rule for a variant to PASS:
   - FILTER equals "PASS", or
   - FILTER equals "." (missing filter), or
   - FILTER is an empty string (some files may represent no filter as empty).
   - All other values (including single or multiple filter names separated by semicolons) are considered FAILED.
5. Tally counts:
   - total += 1 for each variant line
   - pass += 1 when the rule above matches
   - fail += 1 otherwise
6. Output exactly three lines in this order and formatting:
   - Total variants: N
   - Passed variants: M
   - Failed variants: K

## Verification

Perform these checks before finalizing:
- Header exclusion: Confirm the total equals the number of non-header lines, e.g., using an independent check like `grep -cv '^#'` (or an equivalent method) on the same input.
- Invariant: Verify total == passed + failed. If not, re-check header handling, field splitting, and FILTER normalization.
- FILTER logic: Confirm that only these count as PASS: "PASS", ".", or empty string. Any other string (including multiple semicolon-separated filters) is FAIL.
- Formatting: Ensure the output contains exactly three lines, with labels and capitalization matching:
  - Total variants: N
  - Passed variants: M
  - Failed variants: K
  No extra lines, bullets, or code fences.

## Common Pitfalls

- Counting header lines: Lines beginning with '#' are not variants. Always skip them.
- Wrong field separator: VCF is tab-delimited. Using a space-based split can shift columns and misread FILTER.
- Misclassifying '.' or empty as fail: In VCF, '.' indicates no filter applied (treat as pass). Some files may present an empty FILTER field; treat empty as pass as well.
- Case or concatenation confusion: FILTER must be exactly "PASS" to count as pass. Strings like "pass" or "PASS;q10" are not PASS and should be counted as fail.
- Windows line endings: If lines end with CRLF, trailing '\r' can remain in the FILTER field and break comparisons. Strip trailing '\r' before comparison.
- Off-by-one column indexing: FILTER is the 7th column (index 6 in zero-based arrays).
- Skipping verification: Failing to confirm total == pass + fail or to double-check header counts can hide logic errors.

## Reliable One-Liners (optional)

- awk (tab-delimited, robust to CRLF on FILTER, derive fail as total - pass):
```
awk -F '\t' 'BEGIN{t=0;p=0} /^#/ {next} {sub(/\r$/,"",$7); t++; f=$7; if (f=="PASS" || f=="." || f=="") p++} END{printf "Total variants: %d\nPassed variants: %d\nFailed variants: %d\n", t, p, t-p}' input.vcf > output.txt
```

- gzipped VCFs:
```
zcat input.vcf.gz | awk -F '\t' 'BEGIN{t=0;p=0} /^#/ {next} {sub(/\r$/,"",$7); t++; f=$7; if (f=="PASS" || f=="." || f=="") p++} END{printf "Total variants: %d\nPassed variants: %d\nFailed variants: %d\n", t, p, t-p}' - > output.txt
```

## Optional Script Usage

This repository includes a small Python helper to robustly tally counts from a VCF (supports stdin and .vcf.gz).

Examples:
- From a file:
```
python scripts/vcf_filter_tally.py input.vcf --format text > output.txt
```
- From stdin (e.g., gzipped):
```
zcat input.vcf.gz | python scripts/vcf_filter_tally.py - --format text > output.txt
```
- JSON output (for programmatic use):
```
python scripts/vcf_filter_tally.py input.vcf --format json
```

Expected text output format:
```
Total variants: N
Passed variants: M
Failed variants: K
```
