#!/usr/bin/env python3
"""SMILES Molecular Analysis

Computes average molecular weight (2 decimals), detects specified functional groups,
and counts all hydrogens (explicit + implicit). Writes results in fixed format.

Usage:
  python smiles_molecular_analysis.py --smiles "CC(=O)Oc1ccccc1C(=O)O" --out /path/to/output.txt
  python smiles_molecular_analysis.py --in /path/to/input.txt --out /path/to/output.txt

Dependencies:
  - RDKit (https://www.rdkit.org/)
"""

import argparse
import sys
from typing import Dict, Iterable, List, Set, Union

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
except Exception as e:
    print("ERROR: RDKit is required for this script (pip install rdkit-pypi).", file=sys.stderr)
    sys.exit(1)


FG_SMARTS: Dict[str, Union[str, List[str]]] = {
    # Use patterns that avoid common overlaps.
    # carboxylic acid OH is excluded from 'alcohol'; esters/amides excluded from 'ketone'; amide excluded from 'amine'.
    "carboxylic acid": "[CX3](=O)[OX2H1]",
    "ester": "[CX3](=O)[OX2][#6]",
    "amide": "[CX3](=O)[NX3H0,H1,H2]",
    "ketone": "[CX3](=O)([#6])[#6]",
    "aldehyde": "[CX3H1](=O)[#6]",
    "alcohol": "[OX2H][#6;!$(C=O)]",
    "ether": "[OD2]([#6;!$(C=O)])[#6;!$(C=O)]",
    "amine": "[NX3;H2,H1,H0;!$(NC=O);!$([N+]);!$([N-])][#6]",
    "nitro": ["[N+](=O)[O-]", "[NX3](=O)=O"],
    "halide": "[#6][F,Cl,Br,I]",
}


def _compile_smarts(smarts: Union[str, List[str]]) -> List[Chem.Mol]:
    if isinstance(smarts, str):
        smarts_list = [smarts]
    else:
        smarts_list = smarts
    pats: List[Chem.Mol] = []
    for s in smarts_list:
        p = Chem.MolFromSmarts(s)
        if p is None:
            raise ValueError(f"Invalid SMARTS: {s}")
        pats.append(p)
    return pats


COMPILED_FG = {name: _compile_smarts(s) for name, s in FG_SMARTS.items()}


def detect_functional_groups(mol: Chem.Mol) -> List[str]:
    present: Set[str] = set()
    for name, patterns in COMPILED_FG.items():
        for p in patterns:
            if mol.HasSubstructMatch(p):
                present.add(name)
                break
    groups = sorted(present)
    return groups


def molecular_weight_avg(mol: Chem.Mol) -> float:
    # RDKit Descriptors.MolWt uses average atomic weights
    return float(Descriptors.MolWt(mol))


def hydrogen_count_all(mol: Chem.Mol) -> int:
    # Add explicit hydrogens and count all H atoms
    with_h = Chem.AddHs(mol)
    return sum(1 for a in with_h.GetAtoms() if a.GetAtomicNum() == 1)


def analyze_smiles(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES string."}

    mw = molecular_weight_avg(mol)
    hcount = hydrogen_count_all(mol)
    groups = detect_functional_groups(mol)

    return {
        "molecular_weight": mw,
        "hydrogen_count": hcount,
        "functional_groups": groups,
    }


def write_output(path: str, mw: float, groups: Iterable[str], hcount: int) -> None:
    groups_list = list(groups)
    groups_str = ", ".join(groups_list) if groups_list else "None"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Molecular weight: {mw:.2f} g/mol\n")
        f.write(f"Functional groups: {groups_str}\n")
        f.write(f"Hydrogen count: {hcount}\n")


def main():
    ap = argparse.ArgumentParser(description="Analyze a SMILES for MW, functional groups, and hydrogen count.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--smiles", help="SMILES string to analyze")
    src.add_argument("--in", dest="infile", help="Path to input file containing a single SMILES line")
    ap.add_argument("--out", required=True, help="Path to write results")
    args = ap.parse_args()

    if args.smiles:
        smiles = args.smiles.strip()
    else:
        try:
            with open(args.infile, "r", encoding="utf-8") as fh:
                smiles = fh.readline().strip()
        except Exception as e:
            print(f"ERROR: Failed to read input file: {e}", file=sys.stderr)
            sys.exit(1)

    if not smiles:
        print("ERROR: Empty SMILES input.", file=sys.stderr)
        sys.exit(1)

    result = analyze_smiles(smiles)
    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)

    try:
        write_output(args.out, result["molecular_weight"], result["functional_groups"], result["hydrogen_count"])
    except Exception as e:
        print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
