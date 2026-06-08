# Common Alerts Filter Task

Given a SMILES string in `/root/input.txt`, run the CommonAlertsFilters from the `medchem` Python library to detect problematic functional groups.

Write result to `/root/output.txt`:
```
Common alerts: N
Status: status
Pass: yes/no
```

A molecule passes if it has no alerts (status is "ok" or "annotations" with 0 alert reasons).