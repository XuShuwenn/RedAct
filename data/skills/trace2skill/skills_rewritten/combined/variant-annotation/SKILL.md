---
name: variant-annotation
description: "Annotate VCF variants with their type (SNP, MNP, INS, DEL) based on REF and ALT allele differences."
---

# VCF Variant Annotation

## When to Use

- Annotate genetic variants from VCF files
- Classify variant types from allele changes
- Process simple VCF records where `CHROM`, `POS`, `REF`, and `ALT` are sufficient

## Input

- `/root/input.vcf`: VCF v4.2 format file
- Confirm `/root/input.vcf` exists before processing.
- Before coding or transforming, open the VCF and inspect the header plus at least one data line to confirm the tab-delimited columns and locate `CHROM`, `POS`, `REF`, and `ALT`.
- If the task or workspace already provides a script/tool for the annotation, prefer running that existing workflow and then validating its output instead of reimplementing the transformation.


## Minimal Workflow

## Minimal Workflow

1. Read `/root/input.vcf` and extract `CHROM`, `POS`, `REF`, and `ALT` from each non-header record.
2. Classify each ALT allele directly from the REF/ALT values using the length-based rules in this skill; do not infer type from INFO when REF/ALT already determine it.
3. Write `/root/output.txt` in the exact format `CHR:POS TYPE REF>ALT`, with one output line per ALT allele.
4. After writing the file, read it back and confirm every line matches the required format.

## Variant Type Rules

Based on REF vs ALT:
- **SNP**: REF and ALT are both length 1 and the base changes
- **MNP**: REF and ALT have the same length > 1 and differ
- **INS**: ALT longer than REF (insertion)
- **DEL**: ALT shorter than REF (deletion)

Classify each REF/ALT pair by direct comparison:
- If `len(REF) == 1` and `len(ALT) == 1` and `REF != ALT`, classify as `SNP`
- If `len(REF) == len(ALT)` and length > 1 and `REF != ALT`, classify as `MNP`
- If `len(ALT) > len(REF)`, classify as `INS`
- If `len(ALT) < len(REF)`, classify as `DEL`
- If `ALT` contains multiple comma-separated alleles, classify each ALT allele separately against the same REF.
- Compare the full REF and ALT allele strings directly; do not trim shared prefixes/suffixes or reinterpret simple alleles through INFO for this task.
- Apply these rules only to literal sequence alleles. Do not treat symbolic or missing ALT values such as `.`, `*`, `<DEL>`, or breakend-style alleles as ordinary sequence alleles unless the task explicitly asks for them.

## Output Format

To `/root/output.txt`:
```
chr1:100 SNP A>G
chr2:200 INS T>TA
```

Format: `CHR:POS TYPE REF>ALT`

- Match the output schema exactly: write one annotation per line as `CHR:POS TYPE REF>ALT` with no extra text.
- If a record has multiple ALT alleles, emit one output line per ALT allele.

- Do not add headers, explanations, numbering, or blank lines.
- Preserve the literal `REF>ALT` allele strings from the VCF record for each emitted line.

## VCF Parsing

- Skip VCF metadata lines starting with `##` and the column header line starting with `#CHROM`
- CHROM: chromosome
- POS: position
- REF: reference allele (column 4)
- ALT: alternate allele(s) (column 5); if multiple alleles appear, split on commas and emit one output line per ALT allele
- Process only tab-delimited variant data rows using `CHROM`, `POS`, `REF`, and `ALT`; do not parse by arbitrary whitespace if you can avoid it
- Preserve `CHROM` and `POS` exactly as they appear in the VCF when formatting `CHR:POS TYPE REF>ALT`
- Ignore QUAL, FILTER, INFO, and sample columns unless the task explicitly asks for them; for this skill, derive the type from `REF` and each `ALT` allele without using INFO unless explicitly required

## Tips

- Prefer a small purpose-built script or simple plain-text parser for straightforward VCF-to-text transformations; use heavier tooling only if the task needs it
- Start by opening the input file and inspecting a few real records before coding the parser
- Classify each ALT allele independently from its REF/ALT length relationship
- If `ALT` has comma-separated alleles, split on commas and emit one independently classified line per allele
- Use `/root/input.vcf` as input and write final results to `/root/output.txt` exactly as requested
- After writing `/root/output.txt`, read it back, verify sampled annotations against the source VCF, and confirm the output line count matches the total ALT allele count
- Convert each parsed record directly into the requested output line; do not add headers, comments, or explanatory text
- Base any final reporting on the generated `/root/output.txt` contents rather than re-deriving annotations separately
