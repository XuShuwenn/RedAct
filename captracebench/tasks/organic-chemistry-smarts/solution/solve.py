#!/usr/bin/env python3
"""Solve organic-chemistry-smarts task."""

from rdkit import Chem

def main():
    with open("/root/input.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    smiles = lines[0]
    smarts_pattern = lines[1]

    mol = Chem.MolFromSmiles(smiles)
    pattern = Chem.MolFromSmarts(smarts_pattern)

    if mol is None or pattern is None:
        match = "no"
    else:
        match = "yes" if mol.HasSubstructMatch(pattern) else "no"

    result = f"Match: {match}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()