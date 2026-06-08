---
name: medchem-common-alerts-filter
description: "Run medchem CommonAlertsFilters on a SMILES string, robustly handle API variations, and produce a standardized pass/fail report."
---

# MedChem Common Alerts Filter

A robust workflow to run `medchem.structural.CommonAlertsFilters` on a single SMILES string and produce a normalized result with alert count, status, and pass decision.

Use this when you need to:
- screen a molecule for structural alerts using the medchem library
- handle differences across medchem versions (callable filter vs. `check_mol`)
- output a concise, standardized summary suitable for automated evaluation

## When to Use
- The input is a single SMILES string (e.g., provided in `/root/input.txt`).
- The task requires medchem's Common Alerts rules to detect problematic substructures.
- You must write results as three lines:
  - `Common alerts: N`
  - `Status: status`
  - `Pass: yes/no`

Pass rule:
- A molecule passes if status is `ok`, or if status is `annotations` with 0 alert reasons.

## Core Workflow

1. Read the SMILES input
   - Read from `/root/input.txt` and strip whitespace and newlines.
   - Ensure it is non-empty; if empty, fail fast with a clear error.

2. Instantiate the filter
   - `alert_filter = medchem.structural.CommonAlertsFilters()`

3. Detect and use the available API
   - Preferred path (newer medchem versions): the filter is callable.
     - Call `alert_filter([smiles], n_jobs=1)` to get a DataFrame-like object with one row.
     - Extract `status` (string) and `reasons` (string, list, or None). The reasons field may be named `reasons`, `alert_types`, or similar; resolve robustly.
   - Fallback path (older versions): `check_mol` exists on the filter.
     - Parse SMILES to a molecule using `datamol.to_mol` or `rdkit.Chem.MolFromSmiles`.
     - Call `alert_filter.check_mol(mol)` which typically returns `(has_alerts: bool, details: dict)`.
     - Extract alert reasons from `details` (e.g., `details['alert_types']` or `details['reasons']`).

4. Count the alerts robustly
   - If reasons is None or an empty/"None" string: count is 0.
   - If reasons is a string: split on semicolons/commas/pipes and count non-empty entries.
   - If reasons is a list/tuple/set: count non-empty entries.
   - If reasons is a dict: count keys or non-empty entries.

5. Determine status and pass
   - If `status` missing, infer: `ok` if alert count is 0, otherwise `alert`.
   - The molecule passes if `status == 'ok'` or `(status == 'annotations' and alert_count == 0)`. Otherwise it fails.

6. Write output to `/root/output.txt`
   - Exactly three lines in this order:
     - `Common alerts: N`
     - `Status: status`
     - `Pass: yes/no`

## Verification
- Input validation
  - SMILES is non-empty after stripping.
  - If using `check_mol`, confirm the molecule object is not None.
- API validation
  - If callable path is used, ensure one row is returned and fields are accessible.
  - If `check_mol` is used, ensure the tuple/dict is parsed safely.
- Reason parsing
  - Treat `None`, empty string, or literal "None" as zero reasons.
  - Split string reasons on `;`, `,`, or `|` and trim whitespace.
- Output validation
  - Confirm the three required lines are present and correctly spelled.
  - Ensure alert count is a non-negative integer.
  - Confirm pass rule corresponds to the status and count derived.

## Common Pitfalls
- Assuming a single API
  - Some medchem versions expose a callable filter returning a DataFrame, while others only support `check_mol`. Detect and handle both.
- Miscounting reasons
  - `reasons` can be `None`, empty, a delimiter-separated string, a list, or a dict. Normalize before counting to avoid false positives.
- Relying on library-provided pass flags
  - Prefer computing pass from the explicit rule (status `ok` or `annotations` with zero reasons) for consistency.
- Ignoring whitespace/newlines in SMILES
  - Always strip the input; trailing newlines can cause parse issues in older toolchains.
- Concurrency-induced surprises
  - When calling the filter on a list, set `n_jobs=1` to avoid non-deterministic behavior and simplify single-SMILES handling.

## Optional Script Usage
Use the helper script to perform the full workflow robustly across medchem versions:

- Example:
  - `python scripts/medchem_common_alerts.py --input /root/input.txt --output /root/output.txt`
  - Or directly: `python scripts/medchem_common_alerts.py --smiles "CCO"`

The script will:
- Read SMILES from `--smiles` or `--input`
- Run the filter (handling both API shapes)
- Compute alert count, status, and pass
- Write the required three lines to `--output`
