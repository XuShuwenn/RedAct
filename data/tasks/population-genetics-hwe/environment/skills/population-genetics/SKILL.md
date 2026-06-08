---
name: population-genetics
description: "Hardy-Weinberg equilibrium expected genotype counts and heterozygosity calculation. Use when computing expected genotype frequencies, expected heterozygosity, or observed heterozygosity from allele counts."
---

# Population Genetics: Hardy-Weinberg Equilibrium

## Overview

Given observed genotype counts (AA, Aa, aa), calculate expected genotype counts under Hardy-Weinberg equilibrium and compare heterozygosity.

## Hardy-Weinberg Equilibrium

For alleles A and a with frequencies p and q = 1 - p:
- AA (homozygous reference): p²
- Aa (heterozygous): 2pq
- aa (homozygous alternate): q²

If genotype counts are given, compute allele frequencies first:
- p = (2×AA + Aa) / (2×N)
- q = 1 - p

Then expected counts = N × genotype frequency.

## Calculation

```python
# Read input: AA count, Aa count, aa count
with open("/root/input.txt") as f:
    lines = f.read().strip().split("\n")
    obs_AA = int(lines[0].strip())
    obs_Aa = int(lines[1].strip())
    obs_aa = int(lines[2].strip())

N = obs_AA + obs_Aa + obs_aa

# Compute allele frequencies
p = (2 * obs_AA + obs_Aa) / (2 * N)
q = 1.0 - p

# Expected genotype counts under HWE
exp_AA = N * p * p
exp_Aa = N * 2 * p * q
exp_aa = N * q * q

# Expected heterozygosity = 2 * p * q
exp_het = 2 * p * q

# Observed heterozygosity = Aa / N
obs_het = obs_Aa / N

# Output
with open("/root/output.txt", "w") as f:
    f.write(f"Expected AA: {exp_AA:.4f}\n")
    f.write(f"Expected Aa: {exp_Aa:.4f}\n")
    f.write(f"Expected aa: {exp_aa:.4f}\n")
    f.write(f"Expected heterozygosity: {exp_het:.4f}\n")
    f.write(f"Observed heterozygosity: {obs_het:.4f}\n")
```

## Output Format

```
Expected AA: X
Expected Aa: X
Expected aa: X
Expected heterozygosity: X.XXXX
Observed heterozygosity: X.XXXX
```

Round to 4 decimal places.

## Key Reference

- p = (2×AA + Aa) / (2×N)
- q = 1 - p
- Expected AA = N × p²
- Expected Aa = N × 2pq
- Expected aa = N × q²
- Expected heterozygosity = 2pq
- Observed heterozygosity = Aa / N