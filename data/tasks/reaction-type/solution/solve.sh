#!/bin/bash
# Oracle solution for reaction type identification

python3 - << 'EOF'
import csv
from rdkit import Chem

def get_all_counts(mol):
    """Count all atoms including implicit hydrogens."""
    counts = {}
    for a in mol.GetAtoms():
        sym = a.GetSymbol()
        counts[sym] = counts.get(sym, 0) + 1
        h = a.GetTotalNumHs()
        if h > 0:
            counts['H'] = counts.get('H', 0) + h
    return counts

def classify_reaction(r_counts, p_counts):
    """Classify organic reaction type based on atom count changes."""
    halogens = ['F', 'Cl', 'Br', 'I']
    r_hal = sum(r_counts.get(h, 0) for h in halogens)
    p_hal = sum(p_counts.get(h, 0) for h in halogens)
    r_H = r_counts.get('H', 0)
    p_H = p_counts.get('H', 0)
    r_O = r_counts.get('O', 0)
    p_O = p_counts.get('O', 0)

    # Halogen replaced by non-halogen (e.g., Cl -> OH) -> substitution
    if r_hal > 0 and p_hal == 0 and p_O > 0:
        return "substitution"
    # Halogen removed (no replacement) -> reduction
    if r_hal > 0 and p_hal == 0:
        return "reduction"
    # Halogen added -> addition
    if r_hal == 0 and p_hal > 0:
        return "addition"
    # Halogen present in both -> substitution
    if r_hal > 0 and p_hal > 0:
        return "substitution"
    # H and O both decrease -> elimination (loss of H2O)
    if r_H > p_H and r_O > p_O:
        return "elimination"
    # H removed with same O -> oxidation (dehydrogenation)
    if r_H > p_H and r_O == p_O:
        return "oxidation"
    # O removed with same or increased H -> reduction (deoxygenation)
    if r_O > p_O:
        return "reduction"
    # H added (no halogen) -> addition (hydrogenation)
    if p_H > r_H:
        return "addition"

    return "substitution"

# Read reactions from CSV
reactions = []
with open('/root/input.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        reactions.append((row['id'], row['reaction']))

results = []

for rid, reaction_smiles in reactions:
    parts = reaction_smiles.split('>>')
    if len(parts) != 2:
        results.append(f"{rid}: Invalid format")
        continue

    reactant_smiles = parts[0]
    product_smiles = parts[1]

    # Parse reactants and products (may be multiple separated by .)
    reactants = [Chem.MolFromSmiles(s.strip()) for s in reactant_smiles.split('.')]
    products = [Chem.MolFromSmiles(s.strip()) for s in product_smiles.split('.')]

    # Count atoms
    def total_counts(mols):
        total = {}
        for m in mols:
            if m is None:
                continue
            for sym, cnt in get_all_counts(m).items():
                total[sym] = total.get(sym, 0) + cnt
        return total

    r_counts = total_counts(reactants)
    p_counts = total_counts(products)

    reaction_type = classify_reaction(r_counts, p_counts)
    results.append(f"{rid}: Reaction type: {reaction_type}")

# Write output
output = "\n".join(results)
with open('/root/output.txt', 'w') as f:
    f.write(output + "\n")

# Also write oracle output for verification
with open('/root/oracle_output.txt', 'w') as f:
    f.write(output + "\n")

print(output)
EOF
