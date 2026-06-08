# VCF Filter Pass Count Task

Given a VCF file at `/root/input.vcf`, count how many variants have PASS in their FILTER column (or have no filter, which means PASS).

Write results to `/root/output.txt` with this exact format:
```
Total variants: N
Passed variants: M
Failed variants: K
```

The VCF file follows the standard VCF v4.2 format. A variant passes if:
- The FILTER column is "PASS", or
- The FILTER column is missing/empty (meaning no filter was applied)