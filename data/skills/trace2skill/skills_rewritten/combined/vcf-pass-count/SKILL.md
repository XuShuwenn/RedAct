---
name: vcf-pass-count
description: "Count variants in VCF file that have PASS filter or no filter applied."
---

# VCF PASS Count

## When to Use

- Count filtered variants in VCF files
- Analyze VCF FILTER column
- Calculate pass/fail variant statistics


## Execution Protocol

- Before the first tool call, identify the exact required action-message schema and use that schema for every tool invocation; if the environment specifies a `Thought:` / `Action:` pattern, JSON payload, or standalone action wrapper, copy it verbatim.
- Start by checking the workspace (for example, list `/root`) so you confirm `/root/input.vcf` is present and `/root/output.txt` is the correct destination.
- Prefer the simplest reliable workflow for this task: a lightweight one-pass raw-text scan of `/root/input.vcf` is usually better than adding extra parsing layers.
- Before the final response, confirm every claim about counts or file writes is supported by an observation from the current run, and if the environment requires a literal completion token or exact final line, output that exact string and nothing else.

## Execution Protocol

- Follow the runtime or task instructions for tool-call formatting exactly; this skill does not override any required `Thought`/`Action` structure, JSON schema, or other action-message format.
- After each tool action, wait for the corresponding observation or result before making further claims or taking the next step.
- Do not claim `/root/output.txt` was written or counts were computed unless the available observations confirm it.
- If the environment requires a literal completion token or exact final line, output that exact string and nothing else.
- Before sending the final response, re-check whether the task specifies a required terminator or exact action-message syntax.

## Input

- `/root/input.vcf`: VCF v4.2 format

## Variant Classification

A variant PASSES if:
- FILTER column is `PASS`, OR
- FILTER column is `.`, OR
- FILTER column is truly empty/missing in the row

A variant FAILS if:
- FILTER column has any other value

Field check for raw VCF rows:
- Column 6 / index 5 = `QUAL`
- Column 7 / index 6 = `FILTER`
- Classify from `FILTER` only; never from `QUAL`.

Important: apply the task definition literally when counting.
- Treat `PASS`, `.`, and a truly empty FILTER value as pass.
- Treat any other non-empty FILTER value (for example `q10` or `LowQual`) as fail.
- Do **not** classify from `QUAL`.
- Do **not** add extra interpretation rules beyond the task definition and the values actually present in the file.

## Output Format

To `/root/output.txt`:
```
Total variants: N
Passed variants: M
Failed variants: K
```


- Write `/root/output.txt` in the exact three-line format shown above, with labels, order, and line breaks unchanged.
- Finalize by actually writing the formatted result to `/root/output.txt`; computing the counts without saving the file is incomplete.
- After writing `/root/output.txt`, read it back or otherwise confirm it exists and contains the exact three requested lines with the intended numbers before declaring completion.

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

- Prefer a lightweight one-pass raw-text solution for this task when practical (for example, `awk` or a short script) rather than heavier tooling when the goal is only counting rows by `FILTER`.
- Default workflow: inspect the `#CHROM` header, skip all lines beginning with `#`, split each remaining row on tabs, count every non-header row toward Total, read `FILTER` from column 7 / index 6, and classify immediately.
- A short Python script is also a good option for structured counting when available.
- Safe counting pattern: for each non-header row, increment `total`; if column 7 / index 6 is `PASS`, `.`, or empty/missing as defined by the task, increment `passed`; compute `failed = total - passed` at the end.
- Before writing output, sanity-check one parsed variant line and confirm the code reads `FILTER` from column 7 / index 6, not `QUAL`.
- Validate on a few raw rows that `PASS`, `.`, and any truly empty/missing FILTER values are counted as pass and all other FILTER values as fail.
- Do **not** infer pass/fail from `QUAL`, header-inclusive row counts, or any summary that was not checked against raw variant rows.
- Do **not** invent extra PASS criteria or exclusions; use only the rules stated in this skill and the values present in the file.
- Preserve the requested output labels and order exactly when writing `/root/output.txt`.
- If counts look unexpected, inspect a few variant rows or summarize distinct FILTER values rather than trusting a cached summary.
- After writing `/root/output.txt`, read it back once to confirm both the exact three-line format and the computed counts before finishing.
- Sanity-check that `Total = Passed + Failed` before finalizing output.
