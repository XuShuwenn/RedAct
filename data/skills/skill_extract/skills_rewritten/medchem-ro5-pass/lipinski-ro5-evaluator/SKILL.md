---
name: lipinski-ro5-evaluator
description: "Evaluate molecules against the Lipinski Rule of Five and produce a strict pass/fail report with exact formatting and a summary."
---

# Lipinski Rule of Five Evaluator

Reusable workflow for taking a list of molecules (id, SMILES), computing key properties with a specified chemistry library (e.g., medchem), applying the Lipinski Rule of Five thresholds, and writing a strictly formatted pass/fail report with a final summary line.

## When to Use

Activate this skill when a task asks you to:
- Read a CSV of molecules with columns like `id` and `smiles`
- Compute MW (molecular weight), LogP, H-bond donors (HBD), and H-bond acceptors (HBA) using a specific chemistry library (e.g., `medchem`)
- Decide pass/fail by Lipinski Rule of Five thresholds
- Produce a line-per-molecule report in a strict text format and append a summary count line

## Core Workflow

1. Input parsing
   - Read the CSV input in a robust, header-aware way.
   - Treat column names case-insensitively and map to `id` and `smiles`.
   - Preserve the input row order in the output.
   - Skip empty rows or rows missing `id` or `smiles` with a clear error or by stopping to correct the input (do not fabricate IDs or SMILES).

2. Property computation (library-backed)
   - Use the library specified by the task (e.g., `medchem`) to compute:
     - MW: molecular weight (Da)
     - LogP: partition coefficient (use the library’s standard LogP/cLogP; be consistent across molecules)
     - HBD: H-bond donors
     - HBA: H-bond acceptors
   - Normalize outputs:
     - Represent MW and LogP as fixed-point with two decimals for display.
     - Represent HBD and HBA as integers.
   - If the library exposes multiple names (e.g., `logp` vs `clogp`), choose one consistently and verify with a known small test molecule prior to batch processing.

3. Pass/fail decision
   - Apply Lipinski thresholds (inclusive):
     - MW ≤ 500
     - LogP ≤ 5
     - HBD ≤ 5
     - HBA ≤ 10
   - Deterministic evaluation order for a single reported failure: MW → LogP → HBD → HBA.
     - If any criterion fails, immediately classify as FAIL and report only the first failing criterion’s NAME.
     - If none fail, classify as PASS.

4. Output formatting (exact)
   - For PASS:
     - `{id}: PASS (MW={mw}, LogP={logp}, HBD={hbd}, HBA={hba})`
     - Use the exact token spelling and capitalization for criterion names: `MW`, `LogP`, `HBD`, `HBA`.
   - For FAIL:
     - `{id}: FAIL ({CRITERION})` where `{CRITERION}` is exactly one of: `MW`, `LogP`, `HBD`, `HBA`.
     - Do not include values, limits, or multiple criteria.
   - Append the final summary line after all molecules:
     - `Total: {pass_count} pass, {fail_count} fail`

5. File writing
   - Write all lines in input order followed by the summary line.
   - Do not include tables, markdown, extra commentary, or blank lines.

## Verification

Use these checks before finalizing:
- Line count:
  - Equals the number of input molecules plus one summary line.
- PASS lines:
  - Exactly one line per passing molecule, with all four values present and formatted.
  - MW and LogP show two decimal places; HBD and HBA are integers.
- FAIL lines:
  - Exactly one criterion name in parentheses; no values or additional text.
- Summary:
  - `pass_count` equals number of PASS lines; `fail_count` equals number of FAIL lines.
- Thresholds:
  - Molecules exactly at the limits (e.g., MW=500.00) are counted as PASS.
- Determinism:
  - If a molecule fails multiple criteria, only the first failing criterion (in the defined order) is reported.

## Common Pitfalls

- Formatting deviations:
  - Including extra words (e.g., limits or explanations) in FAIL lines. Only print the criterion name.
  - Using different capitalization (e.g., `Hba`) or alternative names. Use exactly `MW`, `LogP`, `HBD`, `HBA`.
  - Adding markdown tables, headers, or blank lines to the output file.
- Wrong thresholds or comparison operators:
  - Use ≤ (less than or equal) as specified for all four criteria.
- Misidentified properties:
  - Mixing different LogP variants or sources without verifying consistency. Select one (e.g., the library’s standard) and stick to it.
- Multiple failure reporting:
  - Listing more than one failing criterion. Report only the first in the predefined order.
- Silent parsing errors:
  - Proceeding when a SMILES fails to parse or a property is missing returns incorrect outputs. Instead, fail fast with a clear error so the input/library can be corrected.

## Optional Script Usage

A generic helper script is included to streamline evaluation using a chemistry library (e.g., `medchem`). It assumes the library can parse SMILES and compute MW, LogP, HBD, HBA (possibly under different descriptor names). Adjust the descriptor name list in the script if your library uses different identifiers.

Example:
- Run: `python scripts/ro5_evaluator.py --input /path/to/input.csv --output /path/to/output.txt`
- The script preserves input order, applies the checks, and writes strictly formatted results and summary.
