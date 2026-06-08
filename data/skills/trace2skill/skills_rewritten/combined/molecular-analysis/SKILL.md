---
name: molecular-analysis
description: "Perform complete molecular analysis from SMILES: molecular weight, functional groups, and hydrogen count."
---

# Complete Molecular Analysis

## When to Use

- Analyze molecules from SMILES strings
- Calculate molecular properties
- Identify functional groups

## Input

- `/root/input.txt`: Single line SMILES string

- Read `/root/input.txt` first and treat its single SMILES line as the sole authoritative analysis input.
- Strip trailing whitespace/newlines before passing the SMILES to RDKit.
- Read `/root/input.txt` before analysis and treat it as the only authoritative source of the SMILES; do not infer or guess from prior context.


## Output Format

To `/root/output.txt`:
```
Molecular weight: [value] g/mol
Functional groups: [group1], [group2], ...
Hydrogen count: [number]
```

- Write `/root/output.txt` with exactly the three labeled lines shown above, in the same order.
- Do not add extra commentary, blank lines, headers, alternate field names, or extra text beyond the required values.
- Use the unit `g/mol`, round molecular weight to 2 decimal places, and restrict functional groups to the allowed list in Requirements; if none are present, write `None`.

## Requirements

- Molecular weight: round to 2 decimal places
- Functional groups (alphabetical): carboxylic acid, ester, amide, ketone, aldehyde, alcohol, ether, amine, nitro, halide. "None" if none found
- Hydrogen count: all hydrogens (explicit + implicit)

- Before finalizing, cross-check atom interpretation against RDKit-derived properties; if you manually infer a formula/count, verify it is consistent with MW and total hydrogens.

- Parse the SMILES with RDKit first; derive molecular weight, functional groups, and hydrogen count from the same molecule object rather than relying on manual carbon/formula counting.
- Compute only the requested fields for final output: molecular weight, functional groups from the allowed list, and total hydrogen count.
- Report only the allowed functional-group labels, deduplicate them, sort them alphabetically, and output `None` if no allowed group is present.
- Validate each functional-group match against local atom context before reporting it; do not double-label a broader group when the same atoms belong to a more specific allowed group (for example, do not label the OH in a carboxylic acid as alcohol, or an ester fragment as ether).
- Prefer RDKit-derived values over manual chemistry inference for molecular weight and total hydrogens; if you manually infer motifs or formula as a cross-check, reconcile any disagreement before writing output.
- For hydrogen count, sum total hydrogens on all atoms (for example, `sum(atom.GetTotalNumHs() for atom in mol.GetAtoms())`); do not use `GetNumAtoms()` or atom/carbon heuristics as a proxy.
- If `Chem.MolFromSmiles(smiles)` fails or returns `None`, stop and investigate the parse issue; do not guess properties from the raw string.
- Use `Descriptors.MolWt(mol)` for molecular weight and `sum(atom.GetTotalNumHs() for atom in mol.GetAtoms())` for hydrogen count; never use atom count as a hydrogen proxy.
- Use one consistent workflow: parse the SMILES once, compute only the requested three fields from that molecule, then write only those results in the required output format.
- If overlap handling still leaves a doubtful functional-group label, inspect the matched atom indices or neighboring atoms for that specific match before writing output.
- Compute first, then format: keep RDKit-derived raw values until final presentation, then round MW to 2 decimals and write the three required output lines once in final form.

## RDKit Usage

```python
from rdkit import Chem
mol = Chem.MolFromSmiles(smiles)


## RDKit Usage

## Execution Protocol

- Follow the current task/system interaction protocol exactly; this skill only covers molecular-analysis steps.
- Before the first tool call, identify the required tool name and wrapper format from the task instructions; if it requires a specific schema (for example `Thought:` plus an `Action:` JSON object naming `bash`), use that exact format for every tool invocation.
- Wait for each tool observation before issuing the next action.
- Write `/root/output.txt` only after computing molecular weight, functional groups, and hydrogen count from the same parsed molecule.
- After writing `/root/output.txt`, read it back once to confirm the file exists, contains exactly the required three lines in order, and matches your computed values.
- If the task requires an exact final completion token or message (for example `ACTION: TASK_COMPLETE`), output it verbatim after verification and do not replace it with a conversational summary.
- Before finishing, verify both `/root/output.txt` contents and any required protocol/completion wording.
## Execution Protocol

## Execution Protocol

- Follow the current task/system interaction protocol exactly; this skill only covers molecular-analysis steps.
- If the environment requires a specific tool-call schema or wrapper (for example `Thought:` plus an `Action:` JSON object), use that exact format for every tool invocation.
- If the task requires an exact final completion token or message (for example `ACTION: TASK_COMPLETE`), output it verbatim and do not replace it with a conversational summary.
- Before finishing, verify both the analysis output file and any required protocol/completion wording.

# Use Descriptors.MolWt for MW
# Use GetNumAtoms for hydrogen count
# Detect functional groups via substructure matching
```

## Tips

- Protocol compliance is mandatory: correct chemistry does not compensate for using the wrong tool-call format or omitting a required completion token.
- DO NOT emit raw tool tags or alternate interfaces when the task requires a specific `Action` JSON wrapper; use the required wrapper on every call.
- DO NOT end with a conversational summary if an exact completion marker is required; output the required marker verbatim, with no extra text.

- Use RDKit for SMILES parsing and analysis
- Detect functional groups via SMARTS pattern matching
- Include implicit hydrogens in count

- Sanity-check the structure before writing output: atom counts implied by the SMILES should agree with the reported molecular weight and hydrogen count.

- Prefer one reproducible RDKit workflow for the full analysis instead of mixing library output with manual arithmetic.
- If an allowed functional group seems structurally present but matching misses it or double-counts it, refine the SMARTS/context checks and recompute before finalizing.
- A useful sanity-check workflow is: identify obvious motifs such as `C(=O)O`, `C(=O)N`, nitro, or halide connectivity, optionally confirm the molecular formula, then verify that MW and total hydrogens are consistent before saving.
- Final check: confirm the functional-group list is alphabetized, molecular weight is rounded to 2 decimals, and `/root/output.txt` has exactly the required three lines.
