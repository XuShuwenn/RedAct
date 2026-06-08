---
name: lipinski-ro5-screening
description: "Batch-screen SMILES against Lipinski’s Rule of Five, producing strict pass/fail lines and a summary."
---

# Lipinski Rule of Five Screening

Screen a list of molecules (SMILES) for oral drug-likeness using Lipinski’s Rule of Five (Ro5) and write a formatted pass/fail report.

Rules (pass if all are true):
- MW ≤ 500 Da
- LogP ≤ 5
- H-bond donors (HBD) ≤ 5
- H-bond acceptors (HBA) ≤ 10

Use this when given a CSV of ids and SMILES and asked to output one line per molecule plus a pass/fail summary.

## When to Use
- You receive a CSV with columns like `id,smiles` and must apply Ro5.
- The output format requires a strict line-based report and a final summary line.
- The task specifies using medchem or RDKit descriptors for MW, LogP, HBD, HBA.

## Core Workflow

1. Parse input
- Read the CSV using a DictReader to handle headers and quoting.
- Require two fields per row: `id` and `smiles`.
- Preserve input order for the output order.

2. Build molecule
- Convert SMILES to a molecule object (medchem or RDKit).
- If parsing fails, follow the task’s specified policy (e.g., skip or treat as failure) and keep counts consistent with the spec.

3. Compute properties (unrounded for decision, rounded for display)
- MW: molecular weight (Da)
- LogP: predicted octanol/water partition (e.g., Crippen logP if using RDKit)
- HBD: number of hydrogen bond donors
- HBA: number of hydrogen bond acceptors

4. Apply Ro5 with correct inequalities
- Check using raw float/integer values (not the rounded display values):
  - MW > 500 → fails MW
  - LogP > 5 → fails LogP
  - HBD > 5 → fails HBD
  - HBA > 10 → fails HBA
- Determine pass/fail:
  - PASS if no failures.
  - FAIL if any failures.
- If the task requires a single failure reason, emit exactly one criterion name using a consistent order (recommended order: MW, LogP, HBD, HBA). Only list multiple reasons if the instructions explicitly ask for them.

5. Format output lines exactly
- PASS line format:
  - `{id}: PASS (MW={mw}, LogP={logp}, HBD={hbd}, HBA={hba})`
- FAIL line format (single reason unless told otherwise):
  - `{id}: FAIL ({criterion})`
- Formatting rules:
  - Round MW and LogP to 2 decimals for display.
  - HBD and HBA are integers.
  - Do not include extra commentary, symbols, or tabular formatting.

6. Append summary
- After all molecules, append exactly one line:
  - `Total: {pass_count} pass, {fail_count} fail`
- Ensure `pass_count + fail_count` matches the number of molecules you reported on, per the task’s invalid-SMILES policy.

## Verification

Perform these checks before finalizing:
- Inequalities: confirm you used ≤ thresholds (don’t use < by mistake).
- Decision vs. display: thresholds were applied to unrounded values; rounding only affects how you print.
- Single reason on FAIL lines if required: print only one of MW/LogP/HBD/HBA.
- Output format:
  - No tables, bullets, or extra text.
  - Each molecule on its own line.
  - Summary is the last line and matches counts.
- Sanity spot-check: pick a couple of molecules and recompute MW/LogP/HBD/HBA to confirm values and pass/fail alignment.
- Order: output lines are in the same order as the input rows.

## Common Pitfalls and How to Avoid Them

- Wrong inequalities: using < instead of ≤ flips borderline cases. Always use ≤ for pass.
- Reporting numbers on FAIL: the spec often requires only the criterion name. Don’t print numeric values or explanations on FAIL lines unless the task allows it.
- Multiple failure reasons when only one is allowed: choose a deterministic single reason (e.g., first in order MW, LogP, HBD, HBA) unless told otherwise.
- Rounding for decision: don’t base pass/fail on rounded values. Compute on raw values, then format.
- Inconsistent LogP calculators: medchem vs. RDKit may differ slightly. Use the library requested by the task; if a fallback is needed, note that borderline cases can change. For strict reproducibility, stick to the specified tool.
- Invalid SMILES handling: don’t invent labels not in the spec. If the task doesn’t specify, either skip with a warning or make handling configurable; ensure totals reflect the intended behavior.
- Formatting drift: avoid Markdown tables, bullet points, or added commentary; keep to the exact line formats.

## Optional Script Usage

A reference CLI is provided to run the full workflow on a CSV.
- Default behavior:
  - Reports the first failing criterion only (order: MW, LogP, HBD, HBA).
  - Skips invalid SMILES without counting them (configurable).
- Example:
  - `python scripts/ro5_screen.py --input input.csv --output output.txt`
  - To list all reasons: `--fail-mode all`
  - To treat invalid SMILES as failures with a label (if allowed by task): `--invalid-policy fail --invalid-reason Invalid`

Success criteria:
- Correct Ro5 logic (≤ thresholds for pass), consistent descriptor tool, exact output formatting, accurate summary counts.
