---
name: medchem
description: "Apply Lipinski Rule of Five (Ro5) to molecules: check MW, LogP, HBD, HBA. Use when users ask about drug-likeness, Lipinski rules, or oral bioavailability filters."
---

# Medchem: Lipinski Rule of Five

## Overview

Medchem is a Python library for molecular filtering. This skill covers applying the Lipinski Rule of Five (Ro5) to assess oral drug-likeness.

## Rule of Five (Lipinski)

**Reference:** Lipinski et al., Adv Drug Deliv Rev (1997) 23:3-25

**Purpose:** Predict oral bioavailability

**Criteria:**
- Molecular Weight ≤ 500 Da
- LogP ≤ 5
- Hydrogen Bond Donors ≤ 5
- Hydrogen Bond Acceptors ≤ 10

**Usage:**

```python
import medchem as mc
from rdkit import Chem

# Apply to SMILES string
passes = mc.rules.basic_rules.rule_of_five("CC(=O)OC1=CC=CC=C1C(=O)O")
# Returns: True or False

# Get individual properties
from rdkit.Chem import Descriptors
mol = Chem.MolFromSmiles("CC(=O)OC1=CC=CC=C1C(=O)O")
mw = Descriptors.MolWt(mol)
logp = Descriptors.MolLogP(mol)
hbd = Descriptors.NumHDonors(mol)
hba = Descriptors.NumHAcceptors(mol)
```

**Rule Filters for Multiple Molecules:**

```python
import datamol as dm
import medchem as mc

# Load molecules from SMILES list
mols = [dm.to_mol(smi) for smi in smiles_list]

# Apply Rule of Five
rfilter = mc.rules.RuleFilters(rule_list=["rule_of_five"])
results = rfilter(mols=mols, n_jobs=-1)
# Returns list of dicts with 'rule_of_five' key per molecule
```

**Result Format:**
```python
# Single molecule
mc.rules.basic_rules.rule_of_five(smiles)  # Returns bool

# Multiple molecules via RuleFilters
results = rfilter(mols=mols)
# Each result: {"rule_of_five": True/False}
```

## Key Reference

- `mc.rules.basic_rules.rule_of_five(mol)` — Check single molecule, returns bool
- `mc.rules.RuleFilters(rule_list=["rule_of_five"])` — Batch filter multiple molecules
- `Descriptors.MolWt(mol)` — Get molecular weight
- `Descriptors.MolLogP(mol)` — Get LogP value
- `Descriptors.NumHDonors(mol)` — Get H-bond donor count
- `Descriptors.NumHAcceptors(mol)` — Get H-bond acceptor count