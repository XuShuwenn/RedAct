---
name: medchem-common-alerts
description: "Screen a SMILES string with medchem Common Alerts filters and report alert count, status, and pass/fail in a fixed three-line format."
---

# MedChem Common Alerts Screening

Use this skill to run the "Common Alerts" filter set from the `medchem` Python library on a SMILES string and output a normalized, deterministic result.

## When to Use

Activate this skill when the task requires:
- Screening a molecule for common problematic functional groups with `medchem` Common Alerts
- A strict three-line output with alert count, status string, and pass/fail
- Pass criteria: no alerts, and status is either `ok` or `annotations` with zero alert reasons

## Core Workflow

1. Environment preparation
   - Ensure Python can import both `rdkit` and `medchem`:
     - Install RDKit (e.g., `pip install rdkit-pypi`) if not already available
     - Install MedChem library (e.g., `pip install medchem`) if not already available
   - If the environment is offline, use prebuilt wheels or a preconfigured image that includes RDKit and the medchem package.

2. Read input SMILES
   - Read the SMILES string from the specified input file. If the task specifies fixed paths, honor them exactly.
   - Trim whitespace and ignore empty lines; use the first non-empty line.

3. Run the Common Alerts filter
   - Initialize the medchem Common Alerts filter object (class and import path may vary by library version). Typical patterns:
     - `from medchem.filters import CommonAlertsFilter`
     - `from medchem.filters.common_alerts import CommonAlertsFilter`
     - `from medchem.filters.common_alerts import CommonAlerts`
   - Invoke the filter on the SMILES string. If the API expects an RDKit Mol, construct one from the SMILES.

4. Normalize results
   - Extract a `status` string and the number of alerts (`n_alerts`). Robust parsing rules:
     - If the result is a dict, prefer keys in this order:
       - `status` for the string status
       - `alerts_count` or `n_alerts` for an integer count
       - Otherwise, if `alerts` or `reasons` is a list, use its length as the count
     - If the result is an object, look for attributes `status`, `n_alerts`, `alerts`, or `reasons` with the same logic
     - If execution fails or the structure is unrecognized, set `status = "error"` and `n_alerts = 0`

5. Compute pass/fail
   - Pass if and only if (`status == "ok"` and `n_alerts == 0`) OR (`status == "annotations"` and `n_alerts == 0`)
   - Otherwise, fail

6. Write the exact output format
   - Write exactly three lines to the required output path:
     - `Common alerts: <N>`
     - `Status: <status>`
     - `Pass: <yes|no>`
   - Use lowercase `yes` or `no`. Do not add extra lines or trailing spaces.

## Verification

- Output shape
  - Confirm the output file contains exactly 3 lines with the keys spelled exactly: `Common alerts`, `Status`, and `Pass`.
  - Confirm `Common alerts:` is followed by a non-negative integer.
  - Confirm `Pass:` is either `yes` or `no` (lowercase).

- Sanity checks
  - If the medchem call returns `status = annotations`, ensure you checked the alert/reason count. Only zero counts pass.
  - If the SMILES is invalid and the tool returns an error-like status, the result should be `Pass: no`.
  - If available, validate the SMILES using RDKit (`MolFromSmiles`) to preempt obvious parsing errors.

- Determinism
  - Re-run the filter on the same SMILES: alert count and status should be consistent.

## Common Pitfalls

- Missing dependencies
  - RDKit not installed: medchem may rely on RDKit to parse molecules, causing import or runtime errors. Install RDKit before medchem.
  - medchem not installed or wrong import path: adjust the import path for the Common Alerts filter and verify the available API in your environment.

- Misinterpreting `annotations`
  - Treating any `annotations` status as pass without checking reasons/alerts count. Only pass if `annotations` AND zero alert reasons.

- Input handling errors
  - Passing raw file content with trailing whitespace/newlines directly to the filter without trimming.
  - Assuming multiple lines are acceptable; select the first non-empty line as the SMILES.

- Output formatting drift
  - Extra spaces, additional lines, different key capitalization, or uppercase `YES/NO` can cause evaluation mismatches.

- Silent fallbacks
  - If you cannot load medchem or the filter API, do not silently claim success. Emit `Status: error` and `Pass: no` to reflect the failure to evaluate.

## Optional Script Usage

This repository includes a helper script to standardize screening and output writing.

- Example usages:
  - `python scripts/medchem_common_alerts.py --smiles "C(C)O" --outfile /root/output.txt`
  - `python scripts/medchem_common_alerts.py --infile /root/input.txt --outfile /root/output.txt`

The script will attempt common import paths for the medchem Common Alerts filter, try both SMILES and RDKit Mol inputs, and normalize the result to the required three-line format.

## Success Criteria

- The output file exists and contains exactly three lines with the specified keys
- The alert count is an integer and reflects the filter output
- Pass is `yes` only if there are zero alerts and status is `ok` or `annotations` with no reasons
- Any errors in tool availability or execution result in `Status: error` and `Pass: no`
