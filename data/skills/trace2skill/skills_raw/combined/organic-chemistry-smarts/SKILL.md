---
name: organic-chemistry-smarts
description: "Match SMILES molecules against SMARTS patterns to detect functional groups using RDKit."
---

# SMARTS Pattern Matching for Molecules

## When to Use

- Check if molecules contain specific functional groups
- Use SMARTS patterns for substructure search
- Detect chemical features via pattern matching

## Input Format

File `/root/input.txt` (2 lines):
- Line 1: SMILES string
- Line 2: SMARTS pattern

- Read `/root/input.txt` as exactly two line-based fields: line 1 is the target molecule SMILES and line 2 is the SMARTS query pattern.
- Strip trailing newlines/whitespace from each line, assign them to `smiles` and `smarts_pattern`, and do not swap or combine their roles.

## Output Format

To `/root/output.txt`:
```
Match: yes/no
```

Output "yes" if pattern matches, "no" otherwise.

- Always write exactly one line to `/root/output.txt`: `Match: yes` or `Match: no`
- Always write the file even if parsing fails; invalid or missing SMILES/SMARTS should produce `Match: no`
- Do not add explanations, alternate labels, extra whitespace, blank lines, or additional lines; a trailing newline is fine
- After writing, read `/root/output.txt` back once when possible to confirm the exact required content

## Using RDKit

```python
from rdkit import Chem

mol = Chem.MolFromSmiles(smiles)
pattern = Chem.MolFromSmarts(smarts_pattern)

if mol is None or pattern is None:
    matched = False
else:
    matched = mol.HasSubstructMatch(pattern)

result = "yes" if matched else "no"
```

Use RDKit directly for the yes/no decision: parse line 1 as the molecule SMILES, parse line 2 as the SMARTS query, and only call `HasSubstructMatch` when both parsed objects are valid.

## SMARTS Patterns

- Common patterns for functional groups
- Use RDKit's SMARTS support for matching
- Handle aromatic and aliphatic variants

## Tips

- Follow a direct workflow: read input by fixed line position -> parse with RDKit -> run `HasSubstructMatch` only if both parses succeed -> write output -> verify the output file.
- Use `Chem.MolFromSmiles(smiles)` for line 1 and `Chem.MolFromSmarts(smarts_pattern)` for line 2; do not swap them or infer chemistry from raw strings.
- If either parser returns `None`, treat the result as no match instead of calling methods on an invalid object.
- Keep output exact and lowercase: `Match: yes` or `Match: no`.
- Prefer RDKit's native parsing and substructure matching; do not add custom chemistry logic for this fixed-format task.

