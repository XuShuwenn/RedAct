#!/bin/bash
# Oracle solution for molecular analysis

python3 - << 'EOF'
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen

with open('/root/input.txt') as f:
    smiles = f.read().strip()

mol = Chem.MolFromSmiles(smiles)
if mol is None:
    raise ValueError(f"Could not parse SMILES: {smiles}")

# 1. Molecular weight
mw = Descriptors.MolWt(mol)

# 2. Functional groups
carbonyls = set()
for c in mol.GetAtoms():
    if c.GetAtomicNum() == 6:
        os = [n for n in c.GetNeighbors() if n.GetAtomicNum() == 8]
        if len(os) >= 2:
            for o in os:
                bond = mol.GetBondBetweenAtoms(c.GetIdx(), o.GetIdx())
                if bond and bond.GetBondType() == Chem.BondType.DOUBLE:
                    carbonyls.add(c.GetIdx())
                    break

found = []
for ci in carbonyls:
    c = mol.GetAtomWithIdx(ci)
    os = [n for n in c.GetNeighbors() if n.GetAtomicNum() == 8]
    for o in os:
        bond = mol.GetBondBetweenAtoms(ci, o.GetIdx())
        if bond and bond.GetBondType() == Chem.BondType.SINGLE:
            if o.GetTotalNumHs() > 0:
                found.append('carboxylic acid')
            else:
                found.append('ester')

# Ether: O attached to 2 C, not adjacent to carbonyl
for o in mol.GetAtoms():
    if o.GetAtomicNum() == 8 and o.GetTotalNumHs() == 0:
        c_neighbors = [n for n in o.GetNeighbors() if n.GetAtomicNum() == 6]
        if len(c_neighbors) >= 2 and not any(c.GetIdx() in carbonyls for c in c_neighbors):
            found.append('ether')

# Alcohol: OH not adjacent to carbonyl
for o in mol.GetAtoms():
    if o.GetAtomicNum() == 8 and o.GetTotalNumHs() > 0:
        c_neighbors = [n for n in o.GetNeighbors() if n.GetAtomicNum() == 6]
        if c_neighbors and not any(c.GetIdx() in carbonyls for c in c_neighbors):
            found.append('alcohol')

# Amine
for n in mol.GetAtoms():
    if n.GetAtomicNum() == 7:
        if [x for x in n.GetNeighbors() if x.GetAtomicNum() == 6]:
            found.append('amine')

# 3. Hydrogen count
h_count = sum(a.GetTotalNumHs() for a in mol.GetAtoms())

# Format output
functional_groups = ', '.join(sorted(set(found))) if found else 'None'
result = f"""Molecular weight: {mw:.2f} g/mol
Functional groups: {functional_groups}
Hydrogen count: {h_count}"""

with open('/root/oracle_output.txt', 'w') as f:
    f.write(result + '\n')

with open('/root/output.txt', 'w') as f:
    f.write(result + '\n')

print(result)
EOF