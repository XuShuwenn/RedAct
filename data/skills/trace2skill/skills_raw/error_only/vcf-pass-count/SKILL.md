---
name: vcf-pass-count
description: "Count variants in VCF file that have PASS filter or no filter applied."
---

# VCF PASS Count

## When to Use

- Count filtered variants in VCF files
- Analyze VCF FILTER column
- Calculate pass/fail variant statistics

## Input

- `/root/input.vcf`: VCF v4.2 format

## Variant Classification

A variant PASSES if:
- FILTER column is "PASS", OR
- FILTER column is missing/empty

A variant FAILS if:
- FILTER column has any other value


Important: apply the task definition literally when counting.
- Treat `PASS` as pass.
- Treat an empty/missing FILTER value as pass.
- In standard VCF text, a FILTER value of `.` means no filters applied, so count `.` as pass.
- Any other non-empty FILTER value (for example `q10` or `LowQual`) is fail.
- Do **not** add extra interpretation rules beyond the task definition and the values actually present in the file.

## Output Format

To `/root/output.txt`:
```
Total variants: N
Passed variants: M
Failed variants: K
```

## VCF Structure

```

## Verification

## Verification

- Inspect `/root/input.vcf` directly before writing final counts; do not rely only on a precomputed summary.
- Skip header lines beginning with `#`, then classify each variant from the 7th column (`FILTER`).
- Verify the final numbers satisfy `Total = Passed + Failed`.
#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO
chr1    100     .       A       G       .       PASS    ...
chr2    200     .       C       T       .       .       ...
```

Dot (.) means no value applied = PASS.

## Tips

- Parse VCF with pysam or pyvcf
- Handle header lines starting with #
- Count rows where FILTER is PASS or missing
- Total = passed + failed

- Before writing output, sanity-check one parsed variant line and confirm the code reads `FILTER` from column 7 / index 6
- Do **not** classify using `QUAL` (index 5); that is a common off-by-one mistake
- If using a library or command that returns aggregate counts, cross-check against the raw FILTER column in `/root/input.vcf`.
- If counts look unexpected, inspect a few variant rows or summarize distinct FILTER values rather than trusting a cached summary.
- Sanity-check that `Total = Passed + Failed` before finalizing output.
