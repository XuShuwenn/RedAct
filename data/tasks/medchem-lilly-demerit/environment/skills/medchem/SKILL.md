---
name: medchem
description: "Filter molecules using CommonAlertsFilters from medchem library. Detect structural alerts and problematic functional groups in molecules for drug discovery filtering."
---

# Medchem: Common Alerts Filter

## Overview

Use `CommonAlertsFilters` from the medchem library to detect problematic functional groups (structural alerts) in molecules. Write the number of alerts and pass/fail status to output.

## Installation

```bash
uv pip install medchem datamol
```

## Workflow

### Step 1: Load Library and Create Filter

```python
import medchem as mc

alert_filter = mc.structural.CommonAlertsFilters()
```

### Step 2: Read Input SMILES

```python
with open("/root/input.txt") as f:
    smiles = f.read().strip()
```

### Step 3: Convert to Molecule and Check

```python
import datamol as dm

mol = dm.to_mol(smiles)
has_alerts, details = alert_filter.check_mol(mol)
```

### Step 4: Determine Status and Pass/Fail

```python
if not has_alerts:
    num_alerts = 0
    status = "ok"
    passes = "yes"
else:
    num_alerts = len(details.get("alert_types", []))
    if num_alerts == 0:
        status = "annotations"
        passes = "yes"
    else:
        status = "alert"
        passes = "no"
```

### Step 5: Write Output

```python
with open("/root/output.txt", "w") as f:
    f.write(f"Common alerts: {num_alerts}\n")
    f.write(f"Status: {status}\n")
    f.write(f"Pass: {passes}\n")
```

## Complete Script

```python
import datamol as dm
import medchem as mc

# Read SMILES from input
with open("/root/input.txt") as f:
    smiles = f.read().strip()

# Create CommonAlertsFilters
alert_filter = mc.structural.CommonAlertsFilters()

# Convert SMILES to molecule object
mol = dm.to_mol(smiles)

# Check for structural alerts
has_alerts, details = alert_filter.check_mol(mol)

# Determine number of alerts and status
if not has_alerts:
    num_alerts = 0
    status = "ok"
    passes = "yes"
else:
    num_alerts = len(details.get("alert_types", []))
    if num_alerts == 0:
        status = "annotations"
        passes = "yes"
    else:
        status = "alert"
        passes = "no"

# Write results
with open("/root/output.txt", "w") as f:
    f.write(f"Common alerts: {num_alerts}\n")
    f.write(f"Status: {status}\n")
    f.write(f"Pass: {passes}\n")
```

## Output Format

```
Common alerts: N
Status: status
Pass: yes/no
```

**Status values:**
- `ok`: No alerts found
- `annotations`: Alerts present but flagged as annotations (0 alert reasons)
- `alert`: Structural alerts detected

**Pass/Fail:**
- `yes`: Molecule passes (no alerts, or annotations with 0 alert reasons)
- `no`: Molecule has structural alerts

## Key Reference

- `mc.structural.CommonAlertsFilters()` — Create common alerts filter
- `alert_filter.check_mol(mol)` — Returns (has_alerts, details) tuple
- `datamol.to_mol(smiles)` — Convert SMILES string to molecule object
- Pass if `status == "ok"` or `status == "annotations"` with 0 alert reasons