#!/usr/bin/env python3
"""Solve medchem-ro5-pass task."""

from rdkit.Chem import Descriptors, Lipinski
import datamol as dm
import csv

def main():
    input_path = "/root/input.csv"
    output_path = "/root/output.txt"

    # Read molecules
    mols = {}
    with open(input_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mol = dm.to_mol(row["smiles"])
            if mol:
                mols[row["id"]] = mol

    results = []
    pass_count = 0
    fail_count = 0

    for mid, mol in mols.items():
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Lipinski.NumHDonors(mol)
        hba = Lipinski.NumHAcceptors(mol)

        checks = {
            "MW": mw <= 500,
            "LogP": logp <= 5,
            "HBD": hbd <= 5,
            "HBA": hba <= 10
        }

        passed = all(checks.values())
        failed_criteria = [k for k, v in checks.items() if not v]

        if passed:
            results.append(f"{mid}: PASS (MW={round(mw, 2)}, LogP={round(logp, 2)}, HBD={hbd}, HBA={hba})")
            pass_count += 1
        else:
            results.append(f"{mid}: FAIL ({', '.join(failed_criteria)})")
            fail_count += 1

    results.append(f"Total: {pass_count} pass, {fail_count} fail")

    output = "\n".join(results)
    with open(output_path, 'w') as f:
        f.write(output)

    # Also write oracle output
    with open("/root/oracle_output.txt", 'w') as f:
        f.write(output)

if __name__ == "__main__":
    main()