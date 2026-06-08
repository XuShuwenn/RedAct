#!/usr/bin/env python3
"""SMILES-based molecular analysis: average molecular weight, functional groups, total hydrogens.

Usage:
  python smiles_analyzer.py --smiles "CCO"
  echo "CCO" | python smiles_analyzer.py
  python smiles_analyzer.py --smiles "CC(=O)O" --largest-fragment

Outputs exactly three lines:
  Molecular weight: <value> g/mol
  Functional groups: <sorted list or None>
  Hydrogen count: <integer>
"""

import sys
import argparse

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
except ImportError as e:
    print("ERROR: RDKit is required for this script (pip install rdkit-pypi).", file=sys.stderr)
    sys.exit(2)

# Functional group SMARTS patterns
# Values may be a string or list of strings (for alternative forms)
PATTERNS = {
    "carboxylic acid": [r"[CX3](=O)[OX2H]"],
    "ester": [r"[CX3](=O)[OX2H0][#6]"],
    "amide": [r"[CX3](=O)[NX3;H0,H1,H2]"],
    "ketone": [r"[#6][CX3](=O)[#6]"],
    "aldehyde": [r"[CX3H1](=O)[#6]"],
    "alcohol": [r"[OX2H][#6]"],
    "ether": [r"[OD2]([#6])[#6]"],
    "amine": [r"[NX3;H0,H1,H2;!$(NC=O)]"],
    # Nitro: include common charged resonance form and a neutral fallback
    "nitro": [r"[$([N+](=O)[O-])]", r"[NX3](=O)=O"],
    # Halide: halogen bound to carbon (sp3 or aromatic)
    "halide": [r"[F,Cl,Br,I]-[CX4,c]"]
}

ALLOWED_GROUPS = tuple(PATTERNS.keys())


def parse_args():
    p = argparse.ArgumentParser(description="Analyze a SMILES: MW (average), functional groups, total H")
    p.add_argument("--smiles", help="SMILES string. If omitted, read from stdin (first line).")
    p.add_argument("--largest-fragment", action="store_true",
                   help="Analyze only the largest fragment by heavy-atom count if multiple fragments present.")
    return p.parse_args()


def load_smiles(smiles: str) -> Chem.Mol:
    smiles = (smiles or "").strip()
    if not smiles:
        raise ValueError("Empty SMILES input.")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Failed to parse SMILES.")
    return mol


def largest_fragment(mol: Chem.Mol) -> Chem.Mol:
    frags = Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=False)
    if not frags:
        return mol
    # Select fragment with the largest heavy-atom count
    def heavy_atoms(m: Chem.Mol) -> int:
        return sum(1 for a in m.GetAtoms() if a.GetAtomicNum() > 1)
    best = max(frags, key=heavy_atoms)
    Chem.SanitizeMol(best)
    return best


def molecular_weight_avg(mol: Chem.Mol) -> float:
    # Average molecular weight (not exact/monoisotopic)
    return float(Descriptors.MolWt(mol))


def total_hydrogens(mol: Chem.Mol) -> int:
    # Count hydrogens after expanding to explicit Hs
    molH = Chem.AddHs(mol)
    return sum(1 for a in molH.GetAtoms() if a.GetAtomicNum() == 1)


def detect_functional_groups(mol: Chem.Mol):
    found = set()
    for name, smarts_list in PATTERNS.items():
        for sm in (smarts_list if isinstance(smarts_list, (list, tuple)) else [smarts_list]):
            patt = Chem.MolFromSmarts(sm)
            if patt is None:
                continue
            if mol.HasSubstructMatch(patt):
                found.add(name)
                break  # don't double count the same group name
    # Keep only allowed canonical names and sort alphabetically
    canonical = [g for g in sorted(found) if g in ALLOWED_GROUPS]
    return canonical


def main():
    args = parse_args()

    smiles = args.smiles
    if not smiles:
        # Read first non-empty line from stdin
        for line in sys.stdin:
            line = line.strip()
            if line:
                smiles = line
                break
    if not smiles:
        print("ERROR: No SMILES provided.", file=sys.stderr)
        sys.exit(1)

    try:
        mol = load_smiles(smiles)
        if args.largest_fragment and "." in smiles:
            mol = largest_fragment(mol)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Compute outputs
    mw = molecular_weight_avg(mol)
    hcount = total_hydrogens(mol)
    groups = detect_functional_groups(mol)

    # Format outputs
    mw_str = f"{mw:.2f}"
    if groups:
        groups_str = ", ".join(groups)
    else:
        groups_str = "None"

    # Print exactly three lines as required
    print(f"Molecular weight: {mw_str} g/mol")
    print(f"Functional groups: {groups_str}")
    print(f"Hydrogen count: {hcount}")


if __name__ == "__main__":
    main()
