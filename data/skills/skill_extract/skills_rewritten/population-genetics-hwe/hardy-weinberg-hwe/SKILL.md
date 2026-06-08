---
name: hardy-weinberg-hwe
description: "Compute expected genotype counts and heterozygosity under Hardy–Weinberg equilibrium from biallelic genotype counts and produce a correctly formatted result."
---

Hardy–Weinberg Equilibrium (HWE) from Genotype Counts

Skill for computing expected genotype counts and heterozygosity under HWE given genotype counts for a biallelic locus.

When to Use

- You are given genotype counts for AA (homozygous reference), Aa (heterozygous), and aa (homozygous alternate) for a single biallelic locus and must compute:
  - expected genotype counts under HWE
  - expected heterozygosity (2pq)
  - observed heterozygosity (Aa/N)
  - and write results in a strict line-by-line format

Core Workflow

1. Parse Inputs
   - Extract three non-negative genotype counts: AA, Aa, aa.
   - Validate that the total N = AA + Aa + aa is > 0.

2. Compute Allele Frequencies
   - p = (2·AA + Aa) / (2·N)
   - q = 1 − p
   - Optionally cross-check with q_alt = (2·aa + Aa) / (2·N) and verify |q − q_alt| is small.

3. Compute HWE Expectations
   - Expected AA = N · p^2
   - Expected Aa = N · 2pq
   - Expected aa = N · q^2

4. Compute Heterozygosity
   - Expected heterozygosity: H_e = 2pq
   - Observed heterozygosity: H_o = Aa / N

5. Rounding and Output
   - Round all reported numeric outputs to 4 decimal places.
   - Output exactly the following lines in this order:
     - Expected AA: X.XXXX
     - Expected Aa: X.XXXX
     - Expected aa: X.XXXX
     - Expected heterozygosity: X.XXXX
     - Observed heterozygosity: X.XXXX

Verification

- Frequency Checks
  - Ensure 0 ≤ p ≤ 1 and 0 ≤ q ≤ 1.
  - Verify p + q ≈ 1 (tolerance e.g., 1e-6).
  - Cross-check: H_e ≈ 1 − (p^2 + q^2).

- Count Checks
  - Expected AA + Expected Aa + Expected aa ≈ N (tolerance e.g., 1e-6).
  - Observed heterozygosity H_o ∈ [0, 1].

- Input Validation
  - Reject negative counts and N = 0.
  - If parsing from text, confirm all three genotype counts were found.

Common Pitfalls

- Using N instead of 2N in allele frequency calculation. Always use p = (2·AA + Aa) / (2·N).
- Confusing allele counts with genotype counts. Ensure inputs are genotype counts: AA, Aa, aa.
- Premature rounding. Perform rounding only at final reporting; compute with full precision internally.
- Mislabeling or swapping outputs (e.g., writing expected Aa where AA belongs). Follow the exact output order.
- Ignoring case or label variability in input files. If parsing from text, search for AA, Aa, aa robustly and fall back to the first three numbers if labeled lines are absent.
- Forgetting to round expected counts to 4 decimals. The task requires all reported numbers to be rounded to 4 decimals.

Optional Script Usage

- Use scripts/hwe_tools.py to parse genotype counts (from CLI flags or an input text file), compute HWE expectations, and write the formatted output.
- Examples:
  - Compute from numbers and print to stdout:
    - python scripts/hwe_tools.py --AA 120 --Aa 60 --aa 20
  - Read from an input text file and write to an output file:
    - python scripts/hwe_tools.py --input path/to/input.txt --output path/to/output.txt

Success Criteria

- Output file contains exactly five lines with the labels shown above, each value rounded to 4 decimals.
- Internal checks pass: p + q ≈ 1, expected counts sum ≈ N, 0 ≤ H_o,H_e ≤ 1.
- No negative or missing counts, and no division-by-zero errors.
