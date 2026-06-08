# VCF Variant Annotation Task

Given a VCF file with variants in `/root/input.vcf`, annotate each variant with its type (SNP, MNP, INS, DEL).

Use the standard VCF INFO field to determine the variant type:
- If REF and ALT differ by 1 base: SNP or MNP
- If ALT is longer than REF: INS
- If ALT is shorter than REF: DEL

Write results to `/root/output.txt`:
```
chr1:100 SNP A>G
chr2:200 INS T>TA
...
```

Format: CHR:POS TYPE REF>ALT