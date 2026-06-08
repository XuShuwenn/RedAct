# Task: Complete Molecular Analysis

Given a SMILES string, perform a complete molecular analysis including molecular weight, functional groups, and hydrogen count.

## Input

The SMILES string is provided in `/root/input.txt` (a single line, just the SMILES).

## Output

Write your analysis to `/root/output.txt`. Format each result on its own line:
```
Molecular weight: [value] g/mol
Functional groups: [group1], [group2], ...
Hydrogen count: [number]
```

### Requirements

- Molecular weight: round to 2 decimal places
- Functional groups: list all present, alphabetically, separated by commas. Options: carboxylic acid, ester, amide, ketone, aldehyde, alcohol, ether, amine, nitro, halide. If none found, write "None".
- Hydrogen count: include all hydrogens (explicit and implicit)

## Your Task

Read the SMILES from `/root/input.txt` and write your analysis to `/root/output.txt`.