---
name: hardy-weinberg-hwe
description: "Compute Hardy–Weinberg expected genotype counts and heterozygosity from observed genotype counts with validation and precise formatting."
---

# Hardy–Weinberg Equilibrium: Expected Counts and Heterozygosity

This skill computes expected genotype counts under Hardy–Weinberg equilibrium (HWE) and both expected and observed heterozygosity from observed biallelic genotype counts (AA, Aa, aa). It includes verification checks and a reusable helper script.

## When to Use

Use this skill when you have counts for AA, Aa, and aa at a single biallelic locus and need to:
- compute allele frequencies (p and q) from genotype counts
- calculate expected genotype counts under HWE
- report expected heterozygosity (He = 2pq) and observed heterozygosity (Ho = Aa/N)
- write results in a consistent, 4-decimal formatted output

## Core Workflow

1. Parse Inputs
   - Extract non-negative integer counts for AA, Aa, aa.
   - Compute total N = AA + Aa + aa; require N > 0.

2. Allele Frequencies
   - p (reference-allele frequency) = (2×AA + Aa) / (2×N)
   - q = 1 − p

3. HWE Expectations
   - Expected AA = N × p²
   - Expected Aa = N × 2pq
   - Expected aa = N × q²

4. Heterozygosity
   - Expected heterozygosity (He) = 2pq
   - Observed heterozygosity (Ho) = Aa / N

5. Output Formatting
   - Keep internal calculations in full precision; round only when producing output.
   - Print (or write) exactly with 4 decimals:
     - Expected AA: X.XXXX
     - Expected Aa: X.XXXX
     - Expected aa: X.XXXX
     - Expected heterozygosity: X.XXXX
     - Observed heterozygosity: X.XXXX

## Verification

Perform these checks before finalizing results:
- Bounds: 0 ≤ p ≤ 1 and 0 ≤ q ≤ 1; |(p + q) − 1| ≤ 1e-12.
- Mass conservation: (Expected AA + Expected Aa + Expected aa) ≈ N (tolerance 1e-6).
- Consistency: He ≈ (Expected Aa / N) (tolerance 1e-12).
- Observed heterozygosity: Ho = Aa / N (exact by definition).
- Input integrity: counts are integers and non-negative; N > 0.

If any check fails, halt and report a clear error instead of emitting possibly incorrect results.

## Common Pitfalls

- Using N instead of 2N in the allele frequency numerator/denominator.
- Rounding p or q early; always round only at final output to preserve accuracy.
- Mixing counts and frequencies (e.g., treating Aa as a frequency when it is a count).
- Swapping Aa with aa or mis-parsing case-sensitive labels; normalize keys and trim whitespace.
- Proceeding with N = 0 or negative counts; always validate inputs.
- Forgetting that He equals both 2pq and Expected Aa / N; use this as a cross-check.

## Success Criteria

- Outputs are present and formatted to 4 decimals for all five lines.
- p and q within [0,1]; expected counts sum to N within tolerance.
- He and Ho reported and consistent with definitions.
- No unhandled edge cases (e.g., N=0, malformed input).

## Optional Script Usage

A reusable helper script is provided.

Examples:
- From direct counts
  - python scripts/hwe.py --AA 12 --Aa 7 --aa 5
- From a text file containing lines with AA, Aa, aa (case-insensitive, any order)
  - python scripts/hwe.py --input path/to/input.txt
- Write to a file instead of stdout
  - python scripts/hwe.py --AA 12 --Aa 7 --aa 5 --out results.txt

The script validates inputs, computes HWE expectations, runs verification checks, and prints the five required lines with 4-decimal formatting.
