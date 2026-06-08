---
name: organic-chemistry
description: "Check if a SMARTS pattern matches a molecule using RDKit. Use when performing substructure matching on SMILES structures with SMARTS patterns, or checking functional groups in molecules."
---

# Organic Chemistry: SMARTS Pattern Matching

## Overview

Given a SMILES string and a SMARTS pattern, use RDKit to check if the molecule contains the functional group defined by the SMARTS pattern.

## SMARTS Matching with RDKit

```python
from rdkit import Chem

# Read input: SMILES on line 1, SMARTS on line 2
with open("/root/input.txt") as f:
    lines = f.read().strip().split("\n")
    smiles = lines[0].strip()
    smarts = lines[1].strip()

# Parse SMILES to molecule
mol = Chem.MolFromSmiles(smiles)
if mol is None:
    with open("/root/output.txt", "w") as f:
        f.write("Match: no\n")
    exit()

# Parse SMARTS to molecule pattern
pattern = Chem.MolFromSmarts(smarts)
if pattern is None:
    with open("/root/output.txt", "w") as f:
        f.write("Match: no\n")
    exit()

# Check if SMARTS matches the molecule
match = mol.HasSubstructMatch(pattern)

# Output
with open("/root/output.txt", "w") as f:
    f.write(f"Match: {'yes' if match else 'no'}\n")
```

## Output Format

```
Match: yes
```
or
```
Match: no
```

## Key Reference

- `Chem.MolFromSmiles(smiles)` — Parse SMILES string to molecule
- `Chem.MolFromSmarts(smarts)` — Parse SMARTS pattern to molecule pattern
- `mol.HasSubstructMatch(pattern)` — Returns True if pattern matches molecule
- Output "yes" if match exists, "no" otherwise