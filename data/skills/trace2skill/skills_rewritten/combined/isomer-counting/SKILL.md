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

- After solving, write the result to `/root/output.txt` rather than only stating it in the chat response.
- Verify the file contains exactly one line in this format: `Number of isomers: [count]`.

## Key Concepts

- Structural/constitutional isomers: same formula, different connectivity
- NOT stereoisomers (different spatial arrangements)
- Example: C4H10 → 2 isomers (butane, isobutane)

## Approach

1. Read `/root/input.txt` before doing any chemistry reasoning; extract and use the exact molecular formula found there, not an example formula from the skill or a remembered nearby case
2. Parse that exact formula into element counts and classify the formula pattern when helpful
3. For a small, common formula with a reliable well-known constitutional-isomer count, prefer the shortest reliable path: use the direct known result or concise family enumeration instead of unnecessary exhaustive generation
4. Otherwise, separate hydrogens from heavy atoms, assign standard valences, and enumerate heavy-atom bond graphs whose degrees and bond-order totals can satisfy the formula
5. If planning to use a chemistry toolkit or external library for enumeration or canonicalization, first confirm it is available in the environment; otherwise use a pure-Python graph-enumeration approach
6. Prune partial candidates early using valence limits, remaining bond total, and connectivity feasibility
7. Convert valid heavy-atom graphs to implied hydrogen counts and keep only exact formula matches
8. Deduplicate by canonicalizing only within identical-element groups, then count unique constitutional isomers
9. Exclude stereoisomers and conformations; count connectivity differences only
10. Before finishing, confirm the count corresponds to the exact input formula and to constitutional isomers only
11. Write exactly one line to `/root/output.txt` as `Number of isomers: [count]` with no extra commentary, names of isomers, or extra whitespace
12. Verify `/root/output.txt` contains exactly that one required line

## Tips

- Use combinatorial enumeration
- Check valency rules for each atom type
- Handle common formulas (alkanes, alcohols, etc.)
