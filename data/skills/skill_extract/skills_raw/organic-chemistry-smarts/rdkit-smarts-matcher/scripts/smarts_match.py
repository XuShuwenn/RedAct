#!/usr/bin/env python3
"""RDKit SMARTS matcher: check if a SMARTS pattern occurs in a SMILES molecule.

Usage examples:
  python smarts_match.py --smiles "CCO" --smarts "[C;H1](=O)[O;H1]"
  python smarts_match.py --input-file /path/to/input.txt --output /path/to/output.txt

Input file format (two non-empty lines):
  Line 1: SMILES string
  Line 2: SMARTS pattern

Exit codes:
  0: success
  1: bad arguments or I/O error
  2: RDKit import error
  3: parsing error (invalid SMILES or SMARTS)

Output:
  Prints or writes exactly: "Match: yes" or "Match: no"
"""

import argparse
import sys
from typing import Optional, Tuple

try:
    from rdkit import Chem
except Exception as e:  # pragma: no cover
    sys.stderr.write("ERROR: RDKit is required for this script.\n")
    sys.exit(2)


def read_inputs(smiles: Optional[str], smarts: Optional[str], input_file: Optional[str]) -> Tuple[str, str]:
    """Resolve SMILES and SMARTS from args or a two-line file."""
    if input_file:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = [ln.strip() for ln in f if ln.strip()]
        except Exception as e:
            sys.stderr.write(f"ERROR: Failed to read input file: {e}\n")
            sys.exit(1)
        if len(lines) < 2:
            sys.stderr.write("ERROR: Input file must contain at least two non-empty lines (SMILES, SMARTS).\n")
            sys.exit(1)
        return lines[0], lines[1]
    if not smiles or not smarts:
        sys.stderr.write("ERROR: Provide both --smiles and --smarts, or use --input-file.\n")
        sys.exit(1)
    return smiles.strip(), smarts.strip()


def parse_molecules(smi: str, sma: str) -> Tuple[Chem.Mol, Chem.Mol]:
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        sys.stderr.write("ERROR: Invalid SMILES string; parsing failed.\n")
        sys.exit(3)
    qmol = Chem.MolFromSmarts(sma)
    if qmol is None:
        sys.stderr.write("ERROR: Invalid SMARTS pattern; parsing failed.\n")
        sys.exit(3)
    return mol, qmol


def query_has_explicit_hydrogen(qmol: Chem.Mol) -> bool:
    """Return True if the SMARTS query contains explicit hydrogen atoms."""
    return any(atom.GetAtomicNum() == 1 for atom in qmol.GetAtoms())


def match_smarts(mol: Chem.Mol, qmol: Chem.Mol, use_chirality: bool, force_addhs: bool) -> bool:
    # First attempt on the molecule as-is (implicit Hs)
    if not force_addhs:
        if mol.HasSubstructMatch(qmol, useChirality=use_chirality):
            return True
    # If query has explicit H atoms or user requested explicit Hs, try with AddHs
    if force_addhs or query_has_explicit_hydrogen(qmol):
        mol_h = Chem.AddHs(mol)
        if mol_h.HasSubstructMatch(qmol, useChirality=use_chirality):
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Check if a SMARTS pattern occurs in a SMILES molecule using RDKit.")
    ap.add_argument('--smiles', help='SMILES string for the target molecule')
    ap.add_argument('--smarts', help='SMARTS pattern to search for')
    ap.add_argument('--input-file', help='Path to a two-line file: SMILES on line 1, SMARTS on line 2')
    ap.add_argument('--output', help='Path to write result ("Match: yes" or "Match: no")')
    ap.add_argument('--use-chirality', action='store_true', help='Consider stereochemistry during matching')
    ap.add_argument('--force-addhs', action='store_true', help='Force adding explicit hydrogens to the target before matching')
    args = ap.parse_args()

    smi, sma = read_inputs(args.smiles, args.smarts, args.input_file)
    mol, qmol = parse_molecules(smi, sma)

    is_match = match_smarts(mol, qmol, use_chirality=args.use_chirality, force_addhs=args.force_addhs)
    result_str = f"Match: {'yes' if is_match else 'no'}\n"

    try:
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result_str)
        else:
            sys.stdout.write(result_str)
    except Exception as e:
        sys.stderr.write(f"ERROR: Failed to write output: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
