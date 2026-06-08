---
name: vcf-variant-typing
description: "Classify VCF variants as SNP, MNP, INS, or DEL by comparing REF and ALT alleles and emit formatted annotations."
---

VCF Variant Typing and Annotation

This skill provides a robust, reusable workflow to parse VCF records, determine per-allele variant types from REF/ALT, and produce concise annotations in the form: CHROM:POS TYPE REF>ALT.

When to Use
- The user asks to identify variant types from a VCF file.
- You need to output one annotation per ALT allele with CHROM and POS preserved.
- Tasks require distinguishing SNP, MNP, INS, and DEL from REF and ALT lengths.

Core Workflow
1) Inspect the input VCF
- Read the file line by line.
- Skip header/comment lines starting with '#'.
- Ensure each variant line has at least columns: CHROM, POS, ID, REF, ALT.

2) Iterate per ALT allele
- ALT can contain multiple alleles separated by commas. Process each ALT independently and emit one output line per ALT.

3) Normalize alleles for robust typing (do not change display alleles)
- Use REF and the current ALT to find the core difference by trimming shared prefix and then trimming shared suffix while keeping at least one base in each allele when possible:
  - Trim from the left while ref[i] == alt[i].
  - Then trim from the right while both remaining lengths > 1 and last bases match.
- Use the trimmed alleles only for type determination. Keep the original REF and ALT strings for output formatting unless the task explicitly asks for normalized alleles.

4) Determine variant type from trimmed alleles
- If lengths are equal and both are 1 and bases differ: SNP.
- If lengths are equal and greater than 1: MNP (block substitution).
- If ALT length > REF length: INS.
- If ALT length < REF length: DEL.
- If REF equals ALT after trimming, this is a no-op/reference call; skip unless instructed otherwise.
- Symbolic/breakend ALT (e.g., <SV>, entries with [ or ], '*', or non-ACGTN characters) are out of scope for simple SNP/INDEL typing. Skip or label as OTHER only if the task requires including them.

5) Emit formatted annotations
- For each processed ALT, write a line with the exact format: CHROM:POS TYPE REF>ALT.
- Use CHROM and POS exactly as in the VCF. POS is already 1-based in VCF.
- Preserve REF and ALT strings as printed in the VCF for the REF>ALT part, unless the task states otherwise.

Verification
- Count check: The number of output lines should equal the total number of ALT alleles processed (excluding those skipped by policy, e.g., symbolic).
- Type consistency checks:
  - For SNP: len(REF) == len(ALT) == 1 and REF != ALT.
  - For MNP: len(REF) == len(ALT) > 1.
  - For INS: len(ALT) > len(REF).
  - For DEL: len(ALT) < len(REF).
- Header exclusion: Confirm no output line begins with '#'.
- Format check: Each line matches CHROM:POS SPACE TYPE SPACE REF>ALT with no extra fields.
- Newline termination: Ensure the output ends with a newline to avoid truncation issues in downstream tools.

Common Pitfalls
- Ignoring multi-allelic ALT: Always split ALT on commas and process each allele.
- Mislabeling MNP as SNP: Check length equality; SNP requires both alleles of length 1.
- Failing to normalize before classification: Left-anchored VCF indels may share flanking bases; trim shared prefix and, if possible, shared suffix before comparing lengths.
- Including headers in output: Skip lines starting with '#'.
- Mishandling symbolic or breakend alleles: Either skip them or explicitly label as OTHER per task requirements; do not attempt SNP/INDEL rules on symbolic strings.
- Wrong output order/format: The required order is CHROM:POS, then type, then REF>ALT, separated by single spaces.
- Using INFO to infer simple types: For basic SNP/MNP/INS/DEL typing, rely on REF and ALT comparison rather than INFO annotations unless the task explicitly mandates INFO-derived classification.

Success Criteria
- All non-symbolic ALT alleles are annotated with correct types based on normalized comparisons.
- Output lines strictly follow the requested format and count matches the processed alleles.
- No headers or extraneous fields appear in the output.

Optional Script Usage
- Use the provided helper script to parse a VCF and print annotations.
- Example usage:
  - Read from a file and write to stdout: python scripts/vcf_variant_typing.py -i input.vcf
  - Read from stdin and write to a file: cat input.vcf | python scripts/vcf_variant_typing.py -o output.txt
  - Include symbolic/breakend alleles as OTHER: python scripts/vcf_variant_typing.py -i input.vcf --include-symbolic
