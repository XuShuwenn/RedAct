---
name: variant-annotation
description: "Annotate VCF variants with their type (SNP, MNP, INS, DEL) based on REF and ALT allele differences."
---

# VCF Variant Annotation

## When to Use

- Annotate genetic variants from VCF files
- Classify variant types from allele changes
- Process VCF INFO fields

## Input

- `/root/input.vcf`: VCF v4.2 format file

## Variant Type Rules

Based on REF vs ALT:
- **SNP**: REF and ALT differ by 1 base
- **MNP**: REF and ALT differ by multiple bases (same length)
- **INS**: ALT longer than REF (insertion)
- **DEL**: ALT shorter than REF (deletion)

## Output Format

To `/root/output.txt`:
```
chr1:100 SNP A>G
chr2:200 INS T>TA
```

Format: `CHR:POS TYPE REF>ALT`

## VCF Parsing

- CHROM: chromosome
- POS: position
- REF: reference allele
- ALT: alternate allele
- Use INFO field if needed

## Tips

- Parse VCF with pysam or pyvcf
- Compare allele lengths for type classification
- Handle multiple ALT alleles
- Check for complex variants
