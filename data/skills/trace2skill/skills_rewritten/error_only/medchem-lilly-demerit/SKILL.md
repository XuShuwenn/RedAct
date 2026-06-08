---
name: medchem-lilly-demerit
description: "Apply Lipinski Rule of Five criteria to check drug-likeness of molecules using medchem library."
---

# Lipinski Rule of Five Pass/Fail

## When to Use

- Evaluate drug-likeness of molecules
- Check Ro5 criteria: MW, LogP, HBD, HBA
- Use medchem Python library for analysis

## Input

- `/root/input.csv`: CSV with columns `id`, `smiles`

## Ro5 Criteria

- Molecular weight (MW) ≤ 500 Da
- LogP ≤ 5
- H-bond donors (HBD) ≤ 5
- H-bond acceptors (HBA) ≤ 10

## Output Format

For PASS (all criteria met):
```
{id}: PASS (MW={mw}, LogP={logp}, HBD={hbd}, HBA={hba})
```

For FAIL (first failed criterion):
```
{id}: FAIL (LogP)
```
or `FAIL (MW)`, `FAIL (HBD)`, `FAIL (HBA)`

Summary line:
```
Total: {pass_count} pass, {fail_count} fail
```

## Using medchem

```python
from medchem import Descriptors
# Use Descriptors.MW, Descriptors.LogP, etc.
```

## Tips

- Only report the FIRST failed criterion
- Round values appropriately
- Count pass/fail totals at end


- Verify one sample molecule end-to-end before processing the whole CSV: confirm the import/callable name, accepted input shape, returned fields/types, and rounding, then format output.
- If a call raises a type or shape error, use the traceback plus runtime inspection to determine whether the API expects a single molecule, a SMILES string, or a collection, then retry with the matching form.
- If `medchem` returns structured or non-scalar values, normalize/extract plain numeric per-molecule MW, LogP, HBD, and HBA values, and handle null-like values before comparing to thresholds.
- Base PASS/FAIL on this skill's explicit criteria (MW ≤ 500, LogP ≤ 5, HBD ≤ 5, HBA ≤ 10); if multiple criteria fail, report only the first failure in this fixed order: MW, LogP, HBD, HBA.
- Keep final formatting exact: PASS includes all four values, FAIL reports only the first violated criterion, totals are reported at the end, and after writing the final result file, read `/root/output.txt` back once to confirm every line matches the required format.

