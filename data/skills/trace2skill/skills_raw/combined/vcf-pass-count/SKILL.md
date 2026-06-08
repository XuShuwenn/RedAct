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

Field check for raw VCF rows:
- Column 6 / index 5 = `QUAL`
- Column 7 / index 6 = `FILTER`
- Classify from `FILTER` only; never from `QUAL`.



Important: apply the task definition literally when counting.
- Treat `PASS` as pass.
- Treat an empty/missing FILTER value as pass.
- In standard VCF text, a FILTER value of `.` means no filters applied, so count `.` as pass when it appears in the file.
- Any other non-empty FILTER value (for example `q10` or `LowQual`) is fail.
- Do **not** narrow the pass rule to only `PASS` and `.` if the task also says empty/missing counts as pass.
- Do **not** add extra interpretation rules beyond the task definition and the values actually present in the file.

## Output Format

To `/root/output.txt`:
```
Total variants: N
Passed variants: M
Failed variants: K
```


- Write `/root/output.txt` in the exact three-line format shown above, with labels, order, and line breaks unchanged.

## VCF Structure

A VCF data row uses the 7th column (`FILTER`) for pass/fail classification:

```text
#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO
chr1    100     .       A       G       .       PASS    ...
chr2    200     .       C       T       .       .       ...
```

- Confirm from the `#CHROM` header or a sample row that `FILTER` is the 7th column (index 6).
- Dot (`.`) in `FILTER` means no filters applied = PASS.

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

- A simple raw-text scan is often the safest option for this task: ignore lines starting with `#`, split variant rows by tabs, read column 7 / index 6, and update total/pass/fail in one pass.
- Before writing output, sanity-check one parsed variant line and confirm the code reads `FILTER` from column 7 / index 6, not `QUAL`.
- If using a script, library, or aggregate command, read back a few raw variant lines and confirm the pass/fail decisions match the FILTER values.
- Do **not** invent extra PASS criteria or exclusions; use only the rules stated in this skill and the values present in the file.
- Preserve the requested output labels and order exactly when writing `/root/output.txt`.
- If using a library or command that returns aggregate counts, cross-check against the raw FILTER column in `/root/input.vcf`.
- If counts look unexpected, inspect a few variant rows or summarize distinct FILTER values rather than trusting a cached summary.
- Sanity-check that `Total = Passed + Failed` before finalizing output.
