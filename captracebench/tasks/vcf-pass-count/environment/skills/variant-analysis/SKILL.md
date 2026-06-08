---
name: variant-analysis
description: "Parse VCF files and count variants by FILTER status. Use when users ask about VCF file parsing, variant counting, or PASS/FAIL filter statistics."
---

# Variant Analysis: VCF Filtering and Counting

## Overview

VCF (Variant Call Format) is a standard file format for storing genetic variant data. This skill covers parsing VCF files and counting variants by their FILTER status.

## VCF Format

VCF files have:
- Header lines starting with `#`
- Variant records with columns: CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT, sample(s)

**FILTER column:**
- `PASS` — variant passed all filters
- `.` (dot/missing) — no filter applied, treated as PASS
- Other values (e.g., `LowQual`, `mapq`) — variant failed the filter

## Parsing VCF

```python
# Parse VCF file line by line
with open("/root/input.vcf") as f:
    for line in f:
        if line.startswith("#"):
            continue  # Skip header
        fields = line.strip().split("\t")
        chrom = fields[0]
        pos = fields[1]
        ref = fields[2]
        alt = fields[3]
        qual = fields[4]
        filt = fields[5]  # FILTER column
        info = fields[6]  # INFO column
```

## Counting FILTER Status

```python
total = 0
passed = 0
failed = 0

with open("/root/input.vcf") as f:
    for line in f:
        if line.startswith("#"):
            continue
        fields = line.strip().split("\t")
        filt = fields[5]  # FILTER column
        total += 1
        if filt == "PASS" or filt == ".":
            passed += 1
        else:
            failed += 1

print(f"Total variants: {total}")
print(f"Passed variants: {passed}")
print(f"Failed variants: {failed}")
```

## Key Rules

- A variant **passes** if FILTER column is `PASS` or `.` (missing/empty)
- A variant **fails** if FILTER column has any other value (e.g., `LowQual`, `mapq<20`)
- `PASS` and `.` are equivalent — both mean the variant passed filtering
- Header lines starting with `#` should not be counted as variants

## Using PyVCF (Optional)

```python
import vcf

reader = vcf.VCFReader(filename="/root/input.vcf")
records = list(reader)
total = len(records)
passed = sum(1 for r in records if r.FILTER is None or r.FILTER == "PASS")
failed = total - passed
```

## Key Reference

- VCF header lines start with `#` — skip these
- FILTER column is field index 5 (0-indexed)
- PASS means passed filters
- `.` (missing) means no filter applied — treated as PASS
- Other values mean the variant was filtered out