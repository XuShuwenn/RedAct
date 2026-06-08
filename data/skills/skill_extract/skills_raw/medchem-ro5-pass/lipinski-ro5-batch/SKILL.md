---
name: lipinski-ro5-batch
description: "Batch-evaluate SMILES against Lipinski Rule of Five and write strict PASS/FAIL lines plus a summary."
---

# Lipinski Rule of Five Batch Evaluation

Apply Lipinski's Rule of Five (Ro5) to a CSV of molecules and produce a deterministic PASS/FAIL report with a final summary line.

Rules (defaults):
- MW ≤ 500 Da
- LogP ≤ 5 (use a single consistent model, e.g., RDKit Crippen MolLogP)
- HBD ≤ 5
- HBA ≤ 10

## When to Use

Use this skill when:
- You are given a CSV with molecule IDs and SMILES and must report Ro5 pass/fail.
- Output format must be line-based and strict, ending with a total pass/fail summary.

## Core Workflow

1. Read Input
   - Load the CSV using a robust parser (e.g., Python csv.DictReader).
   - Expect columns: id and smiles. Preserve input order.

2. Parse Molecules
   - Convert SMILES to molecules (RDKit Chem.MolFromSmiles or medchem equivalent).
   - If parsing fails, decide on handling before proceeding (see Verification > Invalid SMILES). For strict tasks with guaranteed-valid inputs, no special handling is needed.

3. Compute Descriptors (use a consistent source)
   - MW: RDKit Descriptors.MolWt
   - LogP: RDKit Crippen.MolLogP (stick to this consistently)
   - HBD: RDKit Lipinski.NumHDonors
   - HBA: RDKit Lipinski.NumHAcceptors

4. Decide Pass/Fail (compare unrounded values)
   - Use ≤ comparisons for the thresholds.
   - Determine failing criteria in canonical order: MW, LogP, HBD, HBA.
   - If none fail → PASS.
   - If any fail → FAIL.
   - Display values only for PASS lines. For FAIL, display only the criterion name(s) per requirements.
     - Default conservative behavior: report the first failing criterion in the canonical order. If the task explicitly requests all failing criteria, join names with ", " in that same order.

5. Format Output Lines exactly
   - PASS: "{id}: PASS (MW={mw}, LogP={logp}, HBD={hbd}, HBA={hba})"
     - Round MW and LogP for display (e.g., 2 decimals). Keep HBD/HBA as integers.
     - Use unrounded values for decisions; rounding is for display only.
   - FAIL: "{id}: FAIL ({criterion})"
     - Use only the criterion name(s), no numeric values.

6. Append Summary
   - Final line: "Total: {pass_count} pass, {fail_count} fail"

## Verification

Before finalizing:
- Descriptor Sources:
  - Confirm you used RDKit Crippen.MolLogP for LogP and RDKit Lipinski.NumHDonors/NumHAcceptors for HBD/HBA. Mixing descriptor sources can change numbers.
- Threshold Logic:
  - Verify boundary behavior: values equal to thresholds must PASS (≤).
  - Compare thresholds using raw floats; do not base decisions on rounded display values.
- Output Format:
  - Ensure exact spacing, capitalization, punctuation, and field order.
  - One line per input in the same order, then a single summary line.
  - No extra headers, Markdown tables, emojis, or commentary in the output file.
- Sanity Checks (optional):
  - Spot-check a few molecules: high aromatic ring counts often increase LogP; polar groups increase HBD/HBA.

### Invalid SMILES Handling (if applicable)
- If inputs can be invalid and the task allows, either:
  - Treat as FAIL with a clear tag (e.g., "FAIL (Invalid)") and count as fail, or
  - Skip with a logged warning and do not count them in totals.
- Follow the user’s specified policy. If none is specified and inputs are guaranteed valid, omit special handling.

## Common Pitfalls and How to Avoid Them

- Wrong descriptor functions:
  - Using heteroatom counts for HBA/HBD is incorrect. Use RDKit Lipinski.NumHAcceptors/NumHDonors.
- Inconsistent LogP models:
  - Mixing cLogP implementations (e.g., XlogP3 vs RDKit Crippen) changes results. Pick one (Crippen) and stick to it.
- Decision based on rounded values:
  - Don’t compare thresholds after rounding. Always compare raw values; only round for display.
- Output format drift:
  - Adding Markdown tables, extra commentary, or different punctuation breaks strict graders. Match the exact line format.
- Reporting too much on FAIL:
  - If the task requires only criterion names on failure, don’t include numeric values or reasons like "exceeds limit" unless explicitly allowed.
- Multiple failing criteria ordering:
  - If listing multiple, maintain a stable order (MW, LogP, HBD, HBA) for reproducibility.

## Success Criteria

- Every input row yields exactly one PASS/FAIL line in input order.
- PASS lines display MW, LogP (rounded), HBD, HBA; FAIL lines show only criterion name(s).
- Summary line totals equal the number of processed molecules.
- Descriptor computations and threshold decisions adhere to Ro5 and consistent descriptor sources.

## Optional Script Usage

You can use the included script to run the full pipeline:

- Default behavior (reads ./input.csv, writes ./output.txt):
  - python scripts/ro5_batch.py

- With explicit paths:
  - python scripts/ro5_batch.py --input /path/to/input.csv --output /path/to/output.txt

- Override thresholds (if needed):
  - python scripts/ro5_batch.py --mw-max 500 --logp-max 5 --hbd-max 5 --hba-max 10

- List all failing criteria instead of first only:
  - python scripts/ro5_batch.py --all-fail-reasons

Ensure RDKit is installed in the environment.
