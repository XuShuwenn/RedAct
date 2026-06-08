#!/usr/bin/env python3
"""Solve population-genetics-hwe task."""

import math

def main():
    with open("/root/input.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    aa = int(lines[0])  # homozygous reference
    H = int(lines[1])  # heterozygous
    aa_alt = int(lines[2])  # homozygous alternate

    # Total individuals
    N = aa + H + aa_alt
    total_alleles = 2 * N

    # Allele frequencies
    p = (2 * aa + H) / total_alleles
    q = (2 * aa_alt + H) / total_alleles

    # Expected genotype counts under HWE
    exp_aa = p * p * N
    exp_Aa = 2 * p * q * N
    exp_aa_alt = q * q * N

    # Expected heterozygosity
    exp_het = 2 * p * q

    # Observed heterozygosity
    obs_het = H / N

    result = f"""Expected AA: {exp_aa:.4f}
Expected Aa: {exp_Aa:.4f}
Expected aa: {exp_aa_alt:.4f}
Expected heterozygosity: {exp_het:.4f}
Observed heterozygosity: {obs_het:.4f}"""

    with open("/root/output.txt", 'w') as f:
        f.write(result + "\n")

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result + "\n")

if __name__ == "__main__":
    main()