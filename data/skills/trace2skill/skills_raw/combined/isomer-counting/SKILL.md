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

- Read `/root/input.txt` first and base all reasoning on the exact formula found there.
- Do not assume an example formula is the task input.

## Output Format

To `/root/output.txt`:
```
Number of isomers: [count]
```


Write exactly one line to `/root/output.txt` with no extra text:
`Number of isomers: [count]`

## Key Concepts

- Structural/constitutional isomers: same formula, different connectivity
- NOT stereoisomers (different spatial arrangements)
- Example: C4H10 → 2 isomers (butane, isobutane)

## Approach

1. Read `/root/input.txt` first and parse the molecular formula actually provided
2. Parse the formula into element counts and classify the formula pattern when helpful
3. For small common formulas with reliable well-known constitutional-isomer counts, use direct chemistry knowledge or direct enumeration of distinct connectivity families instead of unnecessary full exhaustive generation
4. Otherwise, separate hydrogens from heavy atoms, assign standard valences, and enumerate heavy-atom bond graphs whose degrees and bond-order totals can satisfy the formula
5. Prune partial candidates early using valence limits, remaining bond total, and connectivity feasibility
6. Convert valid heavy-atom graphs to implied hydrogen counts and keep only exact formula matches
7. Deduplicate by canonicalizing only within identical-element groups, then count unique constitutional isomers
8. Exclude stereoisomers and conformations; count connectivity differences only
9. Write the result to `/root/output.txt` exactly as `Number of isomers: [count]`

## Tips

- Use combinatorial enumeration
- Check valency rules for each atom type
- Handle common formulas (alkanes, alcohols, etc.)
