---
name: variant-analysis
description: "Annotate VCF variants with their type (SNP, MNP, INS, DEL) based on REF and ALT allele lengths. Use when parsing VCF files and classifying variant types from sequence changes."
---

# Variant Analysis: VCF Variant Type Annotation

## Overview

Given a VCF file, annotate each variant with its type (SNP, MNP, INS, DEL) based on the length difference between REF and ALT alleles.

## Variant Type Classification Rules

From the REF and ALT alleles:
- **SNP**: REF and ALT differ by exactly 1 base (single nucleotide substitution)
- **MNP**: REF and ALT differ by more than 1 base but same length (multiple nucleotide substitution)
- **INS**: ALT is longer than REF (insertion)
- **DEL**: ALT is shorter than REF (deletion)

## VCF Parsing

```python
def parse_vcf(filepath):
    """Parse VCF file and return list of variant records."""
    variants = []
    with open(filepath) as f:
        for line in f:
            if line.startswith("#"):
                continue  # Skip header
            fields = line.strip().split("\t")
            chrom = fields[0]
            pos = int(fields[1])
            ref = fields[3]
            alt = fields[4]
            variants.append((chrom, pos, ref, alt))
    return variants
```

## Variant Type Detection

```python
def classify_variant_type(ref, alt):
    """Classify variant as SNP, MNP, INS, or DEL."""
    ref_len = len(ref)
    alt_len = len(alt)
    len_diff = alt_len - ref_len

    if len_diff == 0:
        # Same length - SNP or MNP
        if ref_len == 1:
            return "SNP"
        else:
            return "MNP"
    elif len_diff > 0:
        return "INS"
    else:
        return "DEL"
```

## Complete Script

```python
def parse_vcf(filepath):
    variants = []
    with open(filepath) as f:
        for line in f:
            if line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            chrom = fields[0]
            pos = int(fields[1])
            ref = fields[3]
            alt = fields[4]
            variants.append((chrom, pos, ref, alt))
    return variants

def classify_variant_type(ref, alt):
    ref_len = len(ref)
    alt_len = len(alt)
    len_diff = alt_len - ref_len

    if len_diff == 0:
        return "SNP" if ref_len == 1 else "MNP"
    elif len_diff > 0:
        return "INS"
    else:
        return "DEL"

# Parse VCF and annotate
variants = parse_vcf("/root/input.vcf")

with open("/root/output.txt", "w") as f:
    for chrom, pos, ref, alt in variants:
        vtype = classify_variant_type(ref, alt)
        f.write(f"{chrom}:{pos} {vtype} {ref}>{alt}\n")
```

## Output Format

```
chr1:100 SNP A>G
chr2:200 INS T>TA
chr3:300 DEL ACG>AC
```

Format: `CHR:POS TYPE REF>ALT`

## Key Reference

- Parse VCF: skip header lines starting with `#`
- Fields: CHROM (0), POS (1), REF (3), ALT (4)
- Length comparison: INS if alt_len > ref_len, DEL if alt_len < ref_len, SNP/MNP if equal
- SNP: single base substitution (ref and alt both length 1)
- MNP: multi-base substitution (ref and alt same length > 1)