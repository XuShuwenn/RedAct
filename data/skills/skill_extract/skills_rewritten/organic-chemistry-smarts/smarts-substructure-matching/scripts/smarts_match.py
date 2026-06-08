#!/usr/bin/env python3
"""SMARTS substructure matching using RDKit.

Reads two non-empty lines from an input file:
  1) SMILES string
  2) SMARTS pattern

Writes exactly one line to the output file:
  Match: yes
or
  Match: no

Options allow control over chirality and explicit hydrogen handling.
"""
import argparse
import sys
from typing import Tuple

try:
    from rdkit import Chem
except Exception as e:
    sys.stderr.write("ERROR: RDKit is required to run this script.\n")
    sys.exit(2)


def read_smiles_smarts(path: str) -> Tuple[str, str]:
    lines = []
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            s = raw.strip()
            if s:
                lines.append(s)
            if len(lines) >= 2:
                break
    if len(lines) < 2:
        raise ValueError("Input must contain at least two non-empty lines: SMILES and SMARTS.")
    return lines[0], lines[1]


def pattern_requires_explicit_h(smarts: str) -> bool:
    """Heuristic: explicit H atoms in SMARTS require explicit Hs on the molecule.
    Looks for '[H' or '[#1' token usage. Hydrogen count properties like 'H1' do not require explicit Hs.
    """
    s = smarts.replace(' ', '')
    return ('[H' in s) or ('[#1' in s)


def build_mol(smiles: str):
    mol = None
    try:
        mol = Chem.MolFromSmiles(smiles, sanitize=True)
    except Exception:
        mol = None
    if mol is None:
        try:
            mol = Chem.MolFromSmiles(smiles, sanitize=False)
            if mol is not None:
                try:
                    Chem.SanitizeMol(mol)
                except Exception:
                    # proceed with unsanitized mol if necessary
                    pass
        except Exception:
            mol = None
    return mol


def write_result(path: str, matched: bool) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"Match: {'yes' if matched else 'no'}\n")


def main():
    ap = argparse.ArgumentParser(description="SMARTS substructure matching (yes/no)")
    ap.add_argument('--input', required=True, help='Path to input file with SMILES and SMARTS on first two non-empty lines')
    ap.add_argument('--output', required=True, help='Path to output file for writing the result line')
    ap.add_argument('--use-chirality', action='store_true', help='Respect stereochemistry during matching')
    ap.add_argument('--explicit-hs', choices=['auto', 'yes', 'no'], default='auto',
                   help="Control explicit hydrogens: auto (add if SMARTS uses [H]/[#1]), yes (always add), no (never add)")
    ap.add_argument('--strict', action='store_true', help='On parse errors, exit non-zero instead of soft-failing to "Match: no"')
    args = ap.parse_args()

    try:
        smiles, smarts = read_smiles_smarts(args.input)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        if args.strict:
            sys.exit(1)
        write_result(args.output, False)
        return

    mol = build_mol(smiles)
    if mol is None:
        sys.stderr.write("ERROR: Could not parse SMILES.\n")
        if args.strict:
            sys.exit(1)
        write_result(args.output, False)
        return

    query = Chem.MolFromSmarts(smarts)
    if query is None:
        sys.stderr.write("ERROR: Could not parse SMARTS.\n")
        if args.strict:
            sys.exit(1)
        write_result(args.output, False)
        return

    # Decide explicit H handling
    add_hs = False
    if args.explicit_hs == 'yes':
        add_hs = True
    elif args.explicit_hs == 'auto' and pattern_requires_explicit_h(smarts):
        add_hs = True

    if add_hs:
        try:
            mol = Chem.AddHs(mol)
        except Exception:
            # If adding Hs fails, proceed without; it may still match for patterns not requiring [H]
            pass

    try:
        matched = mol.HasSubstructMatch(query, useChirality=args.use_chirality)
    except Exception:
        matched = False

    write_result(args.output, matched)


if __name__ == '__main__':
    main()
