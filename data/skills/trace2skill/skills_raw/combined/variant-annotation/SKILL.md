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

- Read the VCF header and one or more data lines first to confirm the expected columns before parsing (`CHROM`, `POS`, `REF`, `ALT`).


## Minimal Workflow

## Minimal Workflow

1. Read `/root/input.vcf` and extract `CHROM`, `POS`, `REF`, and `ALT` from each non-header record.
2. Classify each ALT allele directly from the REF/ALT values using the length-based rules in this skill; do not infer type from INFO when REF/ALT already determine it.
3. Write `/root/output.txt` in the exact format `CHR:POS TYPE REF>ALT`, with one output line per ALT allele.
4. After writing the file, read it back and confirm every line matches the required format.

## Variant Type Rules

Based on REF vs ALT:
- **SNP**: REF and ALT differ by 1 base
- **MNP**: REF and ALT differ by multiple bases (same length)
- **INS**: ALT longer than REF (insertion)
- **DEL**: ALT shorter than REF (deletion)

Classify each REF/ALT pair by direct length comparison:
- If `len(REF) == 1` and `len(ALT) == 1`, classify as `SNP`
- If `len(REF) == len(ALT)` and length > 1, classify as `MNP`
- If `len(ALT) > len(REF)`, classify as `INS`
- If `len(ALT) < len(REF)`, classify as `DEL`
- If `ALT` contains multiple comma-separated alleles, classify each ALT allele separately against the same REF.

## Output Format

To `/root/output.txt`:
```
chr1:100 SNP A>G
chr2:200 INS T>TA
```

Format: `CHR:POS TYPE REF>ALT`

- Match the output schema exactly: write one annotation per line as `CHR:POS TYPE REF>ALT` with no extra text.
- If a record has multiple ALT alleles, emit one output line per ALT allele.

## VCF Parsing

- Skip VCF metadata lines starting with `##` and the column header line starting with `#CHROM`
- CHROM: chromosome
- POS: position
- REF: reference allele (column 4)
- ALT: alternate allele(s) (column 5)
- Process only tab-delimited variant data rows using `CHROM`, `POS`, `REF`, and `ALT`
- For simple type annotation, classify directly from `REF` and `ALT` without using INFO unless the task explicitly requires it

## Tips

- Parse VCF with pysam or plain text parsing if the file is simple
- Prefer simple field-based parsing for straightforward VCF-to-text transformations
- Classify each ALT allele independently from its REF/ALT length relationship
- Use `/root/input.vcf` as input and write final results to `/root/output.txt` exactly as requested
- After writing `/root/output.txt`, read it back and confirm every line matches `CHR:POS TYPE REF>ALT`
