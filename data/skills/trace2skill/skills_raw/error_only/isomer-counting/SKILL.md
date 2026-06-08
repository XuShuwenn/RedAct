---
name: isomer-counting
description: "Count structural isomers for a given molecular formula by determining possible constitutional isomer configurations."
---

# Structural Isomer Counting

## When to Use

- Count constitutional isomers for a molecular formula
- Solve chemistry combinatorics problems
- Enumerate possible chemical structures

## Input Format

File `/root/input.txt` with molecular formula (e.g., C4H10)

## Output Format

To `/root/output.txt`:
```
Number of isomers: [count]
```

## Key Concepts

- Structural/constitutional isomers: same formula, different connectivity
- NOT stereoisomers (different spatial arrangements)
- Example: C4H10 → 2 isomers (butane, isobutane)

## Approach

1. Parse molecular formula to get atom counts
2. Generate all possible connectivity arrangements
3. Filter valid chemical structures
4. Count unique isomers

## Tips

- Use combinatorial enumeration
- Check valency rules for each atom type
- Handle common formulas (alkanes, alcohols, etc.)
