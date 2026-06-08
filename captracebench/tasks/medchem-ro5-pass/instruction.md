# Lipinski Rule of Five Pass/Fail Task

You have a list of drug-like molecules in `/root/input.csv`. The CSV has two columns: `id` and `smiles`.

For each molecule, apply the Lipinski Rule of Five (Ro5) using the `medchem` Python library:
- Molecular weight (MW) ≤ 500 Da
- LogP ≤ 5
- H-bond donors ≤ 5
- H-bond acceptors ≤ 10

Write results to `/root/output.txt`. For each molecule that PASSES all four criteria, write the line:
`{id}: PASS (MW={mw}, LogP={logp}, HBD={hbd}, HBA={hba})`

For each molecule that FAILS any criterion, write only the criterion NAME that failed (not the actual value):
`{id}: FAIL (LogP)` or `{id}: FAIL (MW)` or `{id}: FAIL (HBD)` etc.

At the end, append a summary line:
`Total: {pass_count} pass, {fail_count} fail`