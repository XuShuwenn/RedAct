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

## Output Format

To `/root/output.txt`:
```
Molecular weight: [value] g/mol
Functional groups: [group1], [group2], ...
Hydrogen count: [number]
```

## Requirements

- Molecular weight: round to 2 decimal places
- Functional groups (alphabetical): carboxylic acid, ester, amide, ketone, aldehyde, alcohol, ether, amine, nitro, halide. "None" if none found
- Hydrogen count: all hydrogens (explicit + implicit)

- Before finalizing, cross-check atom interpretation against RDKit-derived properties; if you manually infer a formula/count, verify it is consistent with MW and total hydrogens.

## RDKit Usage

```python
from rdkit import Chem
mol = Chem.MolFromSmiles(smiles)

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

- Use RDKit for SMILES parsing and analysis
- Detect functional groups via SMARTS pattern matching
- Include implicit hydrogens in count

- Sanity-check the structure before writing output: atom counts implied by the SMILES should agree with the reported molecular weight and hydrogen count.
