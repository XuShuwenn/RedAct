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

## Output Format

To `/root/output.txt`:
```
Match: yes/no
```

Output "yes" if pattern matches, "no" otherwise.

## Using RDKit

```python
from rdkit import Chem

mol = Chem.MolFromSmiles(smiles)
pattern = Chem.MolFromSmarts(smarts_pattern)

if mol.HasSubstructMatch(pattern):
    # Match found
```

## SMARTS Patterns

- Common patterns for functional groups
- Use RDKit's SMARTS support for matching
- Handle aromatic and aliphatic variants

## Tips

- Parse SMILES and SMARTS from input file
- Use HasSubstructMatch for checking
- Handle invalid patterns gracefully
