---
name: population-genetics-hwe
description: "Calculate Hardy-Weinberg equilibrium expected genotype counts and heterozygosity from allele counts."
---

# Hardy-Weinberg Equilibrium Calculation

## When to Use

- Calculate expected genotype frequencies under HWE
- Compute expected heterozygosity
- Analyze population genetics data

- For this file-based task, confirm the expected paths are `/root/input.txt` for input and `/root/output.txt` for output before computing.

## Input Format

File `/root/input.txt`:
- AA: Number of homozygous reference
- Aa: Number of heterozygous
- aa: Number of homozygous alternate


Before calculating, read `/root/input.txt` and extract the provided `AA`, `Aa`, and `aa` genotype counts exactly as written. Parse them into numeric variables before doing any calculations; do not assume values or ordering without checking the file contents.

Validate that all three genotype labels (`AA`, `Aa`, `aa`) are present exactly once and mapped to the correct numeric counts before calculating. Do not swap `AA` with `aa`, and do not treat these genotype counts as allele counts.

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


Write the completed result block to `/root/output.txt` using the exact five labels shown above, in that order, with all numeric values rounded to 4 decimal places.


## Calculation Workflow

## Calculation Workflow

1. Compute total individuals: `N = AA + Aa + aa`.
2. Verify `N > 0` before dividing.
3. Compute allele frequencies from genotype counts:
   - `p = (2*AA + Aa) / (2*N)`
   - `q = (2*aa + Aa) / (2*N)` (equivalently, `q = 1 - p`)
4. Compute expected genotype counts under HWE:
   - `Expected AA = p^2 * N`
   - `Expected Aa = 2*p*q * N`
   - `Expected aa = q^2 * N`
5. Compute heterozygosity values:
   - `Expected heterozygosity = 2*p*q`
   - `Observed heterozygosity = Aa / N`
6. Write results to `/root/output.txt` using the exact labels and order shown above.
## Tips

- Verify `N = AA + Aa + aa` before calculating, and handle the edge case `N = 0` before dividing
- Compute heterozygosity separately from genotype counts: expected heterozygosity `= 2*p*q`, observed heterozygosity `= Aa / N`
- Do not confuse expected heterozygosity (a proportion) with expected heterozygote count `2*p*q*N`
- Preserve the input mapping exactly: `AA`, `Aa`, and `aa` are genotype counts, not allele counts
- Sanity-check that `p + q = 1` within small floating-point error, and that expected counts sum to `N` up to rounding
- Prefer a short script to parse `/root/input.txt`, perform all calculations, and write `/root/output.txt`
- Match the output labels, line order, and numeric formatting exactly as shown above; format every reported value to 4 decimal places
- After writing `/root/output.txt`, read it back once to verify all five lines, labels, order, values, and formatting

- Treat successful script or command execution as a checkpoint only; do not conclude the task until you inspect `/root/output.txt`
- Base every calculation on the exact `AA`, `Aa`, and `aa` values read from `/root/input.txt`; do not rely on assumptions, defaults, or remembered examples
- Compute allele frequencies, expected genotype counts, and both heterozygosity measures from the same parsed `AA`, `Aa`, and `aa` values in one pass to keep results consistent
- For this small three-count task, prefer direct formula application once `AA`, `Aa`, and `aa` are parsed correctly; avoid unnecessary extra analysis or tooling
- Use heterozygosity as a quick validation check: compare `Observed heterozygosity = Aa / N` against `Expected heterozygosity = 2*p*q` to spot inconsistencies before saving output
- Compare expected genotype counts (`p^2*N`, `2*p*q*N`, `q^2*N`) against observed `AA`, `Aa`, and `aa` as a final sanity check; if they match within rounding, treat that as confirmation that the sample already fits HWE, but still write only the required five output lines to `/root/output.txt`
- Use obvious symmetries as a quick check: if `AA = aa`, then expect `p = q = 0.5`; if observed heterozygotes are also near half the population, expected and observed values may closely match
