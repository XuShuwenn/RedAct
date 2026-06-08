# SMARTS Pattern Matching Task

Given a SMILES string in `/root/input.txt` and a SMARTS pattern, check if the molecule contains the functional group defined by the SMARTS pattern.

SMARTS patterns to check (one per line in input.txt):
- Line 1: SMILES string
- Line 2: SMARTS pattern

Use RDKit to perform the matching. Write to `/root/output.txt`:
```
Match: yes/no
```

Output "yes" if the pattern matches, "no" otherwise.