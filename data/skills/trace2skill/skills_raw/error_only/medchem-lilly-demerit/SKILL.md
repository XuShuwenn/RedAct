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
