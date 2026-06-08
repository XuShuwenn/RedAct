---
name: population-genetics-hwe
description: "Calculate Hardy-Weinberg equilibrium expected genotype counts and heterozygosity from allele counts."
---

# Hardy-Weinberg Equilibrium Calculation

## When to Use

- Calculate expected genotype frequencies under HWE
- Compute expected heterozygosity
- Analyze population genetics data

## Input Format

File `/root/input.txt`:
- AA: Number of homozygous reference
- Aa: Number of heterozygous
- aa: Number of homozygous alternate

## Output Format

To `/root/output.txt`:
```
Expected AA: X
Expected Aa: X
Expected aa: X
Expected heterozygosity: X.XXXX
Observed heterozygosity: X.XXXX
```

Round to 4 decimal places.

## Tips

- Use allele frequencies p and q
- Verify total counts match
- Handle edge cases (very small populations)
