# Organic Chemistry: Molecular Properties

## Overview

This skill covers analyzing organic molecules from SMILES strings to determine molecular properties and functional groups.

## SMILES Basics

SMILES represents molecular structure as a string:
- `C`, `N`, `O`, `S` = carbon, nitrogen, oxygen, sulfur atoms
- `C=C`, `C#C` = double, triple bonds
- `()` = branching
- `c` = aromatic carbon, `C` = aliphatic carbon

## Functional Group Detection

**IMPORTANT**: Detection order matters due to overlapping patterns. Use the order below and skip already-detected groups.

```python
from rdkit import Chem

def find_functional_groups(smiles):
    mol = Chem.MolFromSmiles(smiles)
    groups = []

    # 1. Carboxylic acid: carbonyl C bonded to exactly 1 C and =O and OH
    # Pattern: [C](=O)[O;D1] where O has exactly 1 non-H neighbor (the OH)
    carboxylic_acid = Chem.MolFromSmarts('[C;D3](=O)[O;D1]')
    if mol.HasSubstructMatch(carboxylic_acid):
        groups.append('carboxylic acid')

    # 2. Ester: carbonyl C bonded to exactly 1 C and =O and O (not OH)
    # Pattern: [C](=O)O[C,c] where the O is NOT bonded to H
    # To avoid matching carboxylic acid, we check that O is not [O;D1]
    ester = Chem.MolFromSmarts('[C;D3](=O)O[C,c]')
    if mol.HasSubstructMatch(ester):
        groups.append('ester')

    # 3. Ketone: carbonyl C bonded to exactly 2 carbons (not bonded to O other than =O)
    # Pattern: [C;D3](=O)[C;D1][C;D1] - C with 3 bonds to non-H atoms, double bonded to O, bonded to C with 1 non-H neighbor
    # Simpler: [C](=O)[C;!$(C(=O)O)] - carbonyl C bonded to C, where that C is NOT part of carboxylic acid/ester
    ketone = Chem.MolFromSmarts('[C;D3](=O)[C;!R][C;!R]')
    if mol.HasSubstructMatch(ketone) and not mol.HasSubstructMatch(carboxylic_acid) and not mol.HasSubstructMatch(ester):
        groups.append('ketone')

    # 4. Alcohol: OH group bonded to carbon (excluding carboxylic acids already detected)
    # Pattern: [OH1;!$(p)]
    alcohol = Chem.MolFromSmarts('[OH1;!$(C(=O)O);!$(CO)]')
    # Actually simpler: OH not attached to C(=O) and not attached to O (peroxide)
    alcohol = Chem.MolFromSmarts('[OH1;!$(C=O);!$(OO)]')
    if mol.HasSubstructMatch(alcohol):
        groups.append('alcohol')

    # 5. Ether: C-O-C (not ester, not alcohol)
    ether = Chem.MolFromSmarts('[C;R0;!$(C=O)]O[C;R0;!$(C=O)]')
    if mol.HasSubstructMatch(ether):
        groups.append('ether')

    # 6. Aldehyde: [CH1](=O) at chain end
    aldehyde = Chem.MolFromSmarts('[CH1](=O)')
    if mol.HasSubstructMatch(aldehyde):
        groups.append('aldehyde')

    # 7. Amide: C(=O)N
    amide = Chem.MolFromSmarts('[C;D3](=O)N')
    if mol.HasSubstructMatch(amide):
        groups.append('amide')

    # 8. Amine: N bonded to C (not amide N)
    amine = Chem.MolFromSmarts('[N;D2,D3][C]')
    if mol.HasSubstructMatch(amine):
        groups.append('amine')

    # 9. Nitro: [N+](=O)[O-]
    nitro = Chem.MolFromSmarts('[N+](=O)[O-]')
    if mol.HasSubstructMatch(nitro):
        groups.append('nitro')

    # 10. Halide: carbon bonded to F, Cl, Br, I (not aromatic halide)
    halide = Chem.MolFromSmarts('[C;R0][F,Cl,Br,I]')
    if mol.HasSubstructMatch(halide):
        groups.append('halide')

    return sorted(groups)
```

## Simpler Alternative (may have some overlap issues)

If the above is too complex, use these patterns with careful ordering:

```python
from rdkit import Chem

def find_functional_groups(smiles):
    mol = Chem.MolFromSmiles(smiles)
    groups = []
    patterns = {
        'carboxylic acid': 'C(=O)[OH1]',  # MUST be checked first
        'ester': 'C(=O)O[C,c]',             # checked after carboxylic acid
        'ketone': '[C;D3](=O)[C;D1][C;D1]', # carbonyl with 2 C neighbors
        'alcohol': '[OH1][C;!$(C=O)]',      # OH not on carbonyl C
        'ether': 'COC',                      # ether C-O-C
        'aldehyde': '[CH1](=O)',             # chain-end aldehyde
        'amide': 'C(=O)N',                  # amide
        'amine': '[ND2,ND3][C]',            # amine N
        'nitro': '[N+](=O)[O-]',            # nitro
        'halide': '[C][F,Cl,Br,I]'          # halide
    }

    found = {}
    for name, smarts in patterns.items():
        if name == 'carboxylic acid':
            if mol.HasSubstructMatch(Chem.MolFromSmarts(smarts)):
                found[name] = True
        elif name in ('ester', 'ketone'):
            # These can overlap - only add if not already found as carboxylic acid
            if not found.get('carboxylic acid') and mol.HasSubstructMatch(Chem.MolFromSmarts(smarts)):
                found[name] = True
        else:
            if mol.HasSubstructMatch(Chem.MolFromSmarts(smarts)):
                found[name] = True

    return sorted(found.keys())
```

## Molecular Weight

Use RDKit's `Descriptors.MolWt`:

```python
from rdkit.Chem import Descriptors
mw = Descriptors.MolWt(mol)
```

## Hydrogen Counting

Count all hydrogens (explicit and implicit):

```python
h_count = sum(a.GetTotalNumHs() for a in mol.GetAtoms())
```

## Quick Reference

- RDKit `Chem.MolFromSmiles()` parses SMILES
- `mol.GetAtoms()` returns all atoms
- `atom.GetTotalNumHs()` returns implicit + explicit hydrogens
- `atom.GetSymbol()` returns element symbol
- SMARTS: `[D3]` = 3 heavy atom neighbors, `[R0]` = non-ring atom
