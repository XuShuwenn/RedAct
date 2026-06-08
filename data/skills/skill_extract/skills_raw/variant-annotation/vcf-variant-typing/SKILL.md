---
name: vcf-variant-typing
description: "Classify VCF records as SNP, MNP, INS, or DEL from REF/ALT lengths and emit CHR:POS TYPE REF>ALT lines."
---

# VCF Variant Typing from REF/ALT Lengths

This skill annotates VCF variants by type using only REF and ALT allele lengths and produces lines of the form:

CHR:POS TYPE REF>ALT

Types:
- SNP: REF and ALT length both 1 and different
- MNP: REF and ALT equal length > 1 and different
- INS: ALT longer than REF
- DEL: ALT shorter than REF

When to Use
- Users ask to annotate variant types directly from a VCF file
- The desired output is per-allele lines like CHR:POS TYPE REF>ALT
- You need a fast, dependency-free approach that handles multi-allelic ALT fields

Core Workflow
1. Read the input VCF text.
2. Skip header/meta lines starting with '#'.
3. Parse columns: CHROM (1), POS (2), REF (4), ALT (5). Split ALT on commas to handle multi-allelic records; each ALT produces its own output line.
4. Classify each REF/ALT pair by length:
   - If len(ALT) == len(REF): SNP if length == 1 else MNP
   - If len(ALT) > len(REF): INS
   - If len(ALT) < len(REF): DEL
5. Emit "CHR:POS TYPE REF>ALT" exactly, preserving input CHROM, POS, REF, and ALT text for the output tokens.
6. Preserve input order; produce one line per ALT allele.

Decision Rules and Edge Handling
- Multi-allelic sites: Split ALT by "," and classify each separately.
- Missing or symbolic ALT (e.g., '.', '*', '<...>', breakends with '[' or ']'): these cannot be typed by length in a meaningful way. Prefer to skip them or, if required, label as OTHER per user instruction.
- Whitespace and line endings: Trim lines; split primarily on tabs. If tabs are absent, fall back to any whitespace.
- Case: Length checks are case-insensitive; preserve original allele strings for output.
- POS is 1-based in VCF; output the POS value as-is.

Verification
- Format check: Each output line should contain exactly three space-separated tokens after the CHR:POS key, e.g., key TYPE REF>ALT.
- Count check: Output lines should equal the number of ALT alleles processed (sum of ALTs per record, excluding skipped symbolic/missing alleles).
- Consistency check: For a random subset, verify type with simple length comparisons:
  - len(ALT) == len(REF) == 1 → SNP
  - len(ALT) == len(REF) > 1 → MNP
  - len(ALT) > len(REF) → INS
  - len(ALT) < len(REF) → DEL
- Input coverage: Ensure header lines were skipped; only variant records contribute to output.

Common Pitfalls
- Ignoring multi-allelic ALT values and producing a single line per record instead of per ALT.
- Including header lines in output by not filtering lines that start with '#'.
- Misclassifying symbolic or breakend ALT encodings; do not apply length-based rules to symbolic values unless instructed. Skip or label as OTHER explicitly.
- Mixing tabs and spaces when parsing: VCF is tab-delimited; always split on tabs first.
- Dropping or altering POS indexing: Use POS from the VCF verbatim; do not convert to 0-based.
- Adding extra text or different separators; adhere to exact spacing and the REF>ALT token with a single '>' character.

Success Criteria
- Every non-symbolic ALT allele in the VCF produces exactly one output line.
- Each line strictly matches the format CHR:POS TYPE REF>ALT.
- Type assignments follow the length rules above and are reproducible from the input.

Optional Script Usage
- Use scripts/vcf_annotate_types.py to generate annotations.
- Example:
  - python scripts/vcf_annotate_types.py --vcf input.vcf --out output.txt
  - To keep symbolic alleles labeled as OTHER: python scripts/vcf_annotate_types.py --vcf input.vcf --out output.txt --keep-symbolic
