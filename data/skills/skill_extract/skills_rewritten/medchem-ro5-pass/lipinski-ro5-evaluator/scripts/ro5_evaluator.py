#!/usr/bin/env python3
"""
Lipinski Rule of Five evaluator.

Reads a CSV with columns (id, smiles), computes MW, LogP, HBD, HBA using a
chemistry library (e.g., medchem), applies RO5 thresholds, and writes a strictly
formatted pass/fail report with a final summary.

Usage:
  python scripts/ro5_evaluator.py --input INPUT.csv --output OUTPUT.txt

Notes:
- Expects a library capable of parsing SMILES and computing descriptors.
- By default, attempts to use `medchem` with flexible descriptor name matching.
- Adjust DESCRIPTOR_NAME_CANDIDATES below if your library uses different names.
"""

import argparse
import csv
import os
import sys
from typing import Dict, Tuple, Optional

# Thresholds (inclusive)
MW_MAX = 500.0
LOGP_MAX = 5.0
HBD_MAX = 5
HBA_MAX = 10

# Descriptor name candidates for flexible library binding
DESCRIPTOR_NAME_CANDIDATES = {
    'mw': ['mw', 'molecular_weight', 'molweight', 'exact_mw', 'exact_mass'],
    'logp': ['logp', 'clogp', 'alogp'],
    'hbd': ['hbd', 'hbdonors', 'hbond_donors', 'h_donors', 'h_donor_count'],
    'hba': ['hba', 'hbacceptors', 'hbond_acceptors', 'h_acceptors', 'h_acceptor_count'],
}

class PropertyComputer:
    """Attempts to compute descriptors using a medchem-like API.

    This implementation tries multiple API shapes:
    - medchem.Molecule.from_smiles(smiles) or medchem.Molecule(smiles)
    - descriptor functions in medchem.descriptors (e.g., descriptors.mw(mol))
    - attribute access on molecule (e.g., mol.mw)
    """
    def __init__(self):
        try:
            # Lazy imports to keep script generic
            import medchem  # type: ignore
            self.medchem = medchem
            self.descriptors = getattr(medchem, 'descriptors', None)
            self.Molecule = getattr(medchem, 'Molecule', None)
        except Exception as e:
            raise RuntimeError(
                'Required chemistry library not available: medchem.\n'
                'Install and ensure it exposes Molecule and descriptors APIs, '
                'or adapt this script to your library.'
            ) from e

    def _make_mol(self, smiles: str):
        if self.Molecule is None:
            raise RuntimeError('medchem.Molecule class not found.')
        # Try common constructors
        if hasattr(self.Molecule, 'from_smiles'):
            return self.Molecule.from_smiles(smiles)
        try:
            return self.Molecule(smiles)
        except Exception:
            # Some APIs use factory functions under medchem (e.g., medchem.from_smiles)
            maker = getattr(self.medchem, 'from_smiles', None)
            if callable(maker):
                return maker(smiles)
            raise

    def _get_descriptor_value(self, mol, key: str) -> Optional[float]:
        """Resolve a descriptor by trying candidate names on descriptors module and mol attributes."""
        names = DESCRIPTOR_NAME_CANDIDATES[key]
        # Try descriptors.<name>(mol)
        if self.descriptors is not None:
            for name in names:
                fn = getattr(self.descriptors, name, None)
                if callable(fn):
                    try:
                        return fn(mol)
                    except Exception:
                        continue
        # Try mol.<name>
        for name in names:
            if hasattr(mol, name):
                try:
                    val = getattr(mol, name)
                    # Call if callable, else treat as value
                    return val() if callable(val) else val
                except Exception:
                    continue
        return None

    def compute(self, smiles: str) -> Dict[str, float]:
        mol = self._make_mol(smiles)
        if mol is None:
            raise RuntimeError('Failed to create molecule from SMILES.')
        mw = self._get_descriptor_value(mol, 'mw')
        logp = self._get_descriptor_value(mol, 'logp')
        hbd = self._get_descriptor_value(mol, 'hbd')
        hba = self._get_descriptor_value(mol, 'hba')
        missing = [k for k, v in {'MW': mw, 'LogP': logp, 'HBD': hbd, 'HBA': hba}.items() if v is None]
        if missing:
            raise RuntimeError(f'Missing descriptor(s): {", ".join(missing)}')
        return {
            'MW': float(mw),
            'LogP': float(logp),
            'HBD': int(round(float(hbd))),
            'HBA': int(round(float(hba))),
        }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description='Lipinski Rule of Five evaluator')
    ap.add_argument('--input', required=True, help='Input CSV with columns id, smiles')
    ap.add_argument('--output', required=True, help='Output report file path')
    return ap.parse_args()


def normalize_headers(headers):
    return [h.strip().lower() for h in headers]


def find_columns(headers):
    h = normalize_headers(headers)
    try:
        id_idx = h.index('id')
        smi_idx = h.index('smiles')
        return id_idx, smi_idx
    except ValueError:
        raise RuntimeError('Input CSV must contain headers: id, smiles')


def decide_ro5(props: Dict[str, float]) -> Tuple[bool, Optional[str]]:
    # Deterministic order: MW, LogP, HBD, HBA
    if props['MW'] > MW_MAX:
        return False, 'MW'
    if props['LogP'] > LOGP_MAX:
        return False, 'LogP'
    if props['HBD'] > HBD_MAX:
        return False, 'HBD'
    if props['HBA'] > HBA_MAX:
        return False, 'HBA'
    return True, None


def format_pass_line(mol_id: str, props: Dict[str, float]) -> str:
    return f"{mol_id}: PASS (MW={props['MW']:.2f}, LogP={props['LogP']:.2f}, HBD={int(props['HBD'])}, HBA={int(props['HBA'])})"


def format_fail_line(mol_id: str, criterion: str) -> str:
    return f"{mol_id}: FAIL ({criterion})"


def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    pc = PropertyComputer()

    lines = []
    pass_count = 0
    fail_count = 0

    with open(args.input, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            print('ERROR: Empty input CSV.', file=sys.stderr)
            sys.exit(1)
        id_idx, smi_idx = find_columns(headers)
        row_num = 1
        for row in reader:
            row_num += 1
            # Skip completely empty rows
            if not row or all(not str(c).strip() for c in row):
                continue
            try:
                mol_id = str(row[id_idx]).strip()
                smiles = str(row[smi_idx]).strip()
            except IndexError:
                print(f"ERROR: Malformed row {row_num}: {row}", file=sys.stderr)
                sys.exit(1)
            if not mol_id or not smiles:
                print(f"ERROR: Missing id or smiles at row {row_num}", file=sys.stderr)
                sys.exit(1)
            try:
                props = pc.compute(smiles)
            except Exception as e:
                print(f"ERROR: Failed to compute properties for id={mol_id}: {e}", file=sys.stderr)
                sys.exit(1)
            is_pass, fail_key = decide_ro5(props)
            if is_pass:
                lines.append(format_pass_line(mol_id, props))
                pass_count += 1
            else:
                lines.append(format_fail_line(mol_id, fail_key))
                fail_count += 1

    # Append summary
    lines.append(f"Total: {pass_count} pass, {fail_count} fail")

    with open(args.output, 'w', encoding='utf-8') as out:
        out.write("\n".join(lines))

    # Optional: print a brief confirmation
    print(f"Wrote {len(lines)-1} results and summary to {args.output}")


if __name__ == '__main__':
    main()
