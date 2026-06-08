#!/usr/bin/env python3
"""
Lipinski Rule of Five (Ro5) batch screening.

Reads a CSV with columns 'id' and 'smiles', computes MW, LogP, HBD, HBA,
applies Ro5 (MW<=500, LogP<=5, HBD<=5, HBA<=10), and writes formatted results.

Default behavior prints exactly one failure reason (first in MW, LogP, HBD, HBA)
and skips invalid SMILES. Configure to list all reasons or fail invalid SMILES
via CLI options.

Usage:
  python ro5_screen.py --input INPUT.csv --output OUTPUT.txt \
      [--fail-mode {first,all}] \
      [--invalid-policy {skip,fail}] [--invalid-reason Invalid]

Descriptor backends:
- RDKit (preferred fallback): Crippen.MolLogP, Descriptors.MolWt,
  Lipinski.NumHDonors, Lipinski.NumHAcceptors
- 'medchem' support is not assumed here; if your environment provides a
  'medchem' API for these descriptors, integrate it similarly.
"""

import argparse
import csv
import sys
from typing import Dict, List, Optional, Tuple

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski
except Exception as e:
    Chem = None


THRESHOLDS = {
    'MW': 500.0,
    'LogP': 5.0,
    'HBD': 5,
    'HBA': 10,
}

FAIL_ORDER = ['MW', 'LogP', 'HBD', 'HBA']


def compute_properties_rdkit(smiles: str) -> Optional[Dict[str, float]]:
    if Chem is None:
        raise RuntimeError("RDKit is not available in this environment.")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    mw = float(Descriptors.MolWt(mol))
    logp = float(Crippen.MolLogP(mol))
    hbd = int(Lipinski.NumHDonors(mol))
    hba = int(Lipinski.NumHAcceptors(mol))
    return {'MW': mw, 'LogP': logp, 'HBD': hbd, 'HBA': hba}


def ro5_failures(props: Dict[str, float], thr: Dict[str, float]) -> List[str]:
    fails = []
    if props['MW'] > thr['MW']:
        fails.append('MW')
    if props['LogP'] > thr['LogP']:
        fails.append('LogP')
    if props['HBD'] > thr['HBD']:
        fails.append('HBD')
    if props['HBA'] > thr['HBA']:
        fails.append('HBA')
    return fails


def format_pass_line(mol_id: str, props: Dict[str, float]) -> str:
    return (
        f"{mol_id}: PASS (MW={props['MW']:.2f}, "
        f"LogP={props['LogP']:.2f}, "
        f"HBD={int(props['HBD'])}, HBA={int(props['HBA'])})"
    )


def format_fail_line(mol_id: str, reasons: List[str], mode: str = 'first') -> str:
    if mode == 'all':
        reason_str = ', '.join(reasons)
    else:
        # Deterministic single reason using FAIL_ORDER priority
        for r in FAIL_ORDER:
            if r in reasons:
                reason_str = r
                break
        else:
            # Fallback if reasons empty (shouldn't happen if called correctly)
            reason_str = reasons[0] if reasons else 'MW'
    return f"{mol_id}: FAIL ({reason_str})"


def read_rows(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Normalize headers to lowercase for robustness
        field_map = {name: name.lower() for name in reader.fieldnames or []}
        for rec in reader:
            rid = rec.get('id') or rec.get('ID') or rec.get('Id')
            smi = rec.get('smiles') or rec.get('SMILES') or rec.get('Smiles')
            if rid is None and rec:
                # Try using normalized headers if present
                rid = rec.get(field_map.get('id', 'id'))
            if smi is None and rec:
                smi = rec.get(field_map.get('smiles', 'smiles'))
            if rid is None or smi is None:
                # Skip badly formed lines but keep order consistent for the rest
                continue
            rows.append({'id': str(rid).strip(), 'smiles': str(smi).strip()})
    return rows


def main():
    ap = argparse.ArgumentParser(description="Lipinski Rule of Five batch screening")
    ap.add_argument('--input', required=True, help='Input CSV with columns id,smiles')
    ap.add_argument('--output', required=True, help='Output text file path')
    ap.add_argument('--fail-mode', choices=['first', 'all'], default='first',
                    help='Report only the first failing criterion or all (comma-separated)')
    ap.add_argument('--invalid-policy', choices=['skip', 'fail'], default='skip',
                    help='Skip invalid SMILES or count as failure')
    ap.add_argument('--invalid-reason', default='Invalid',
                    help='Reason label when invalid-policy=fail (use only if allowed by task)')
    args = ap.parse_args()

    try:
        rows = read_rows(args.input)
    except Exception as e:
        print(f"ERROR: failed to read input CSV: {e}", file=sys.stderr)
        sys.exit(1)

    lines: List[str] = []
    pass_count = 0
    fail_count = 0

    for rec in rows:
        mol_id = rec['id']
        smi = rec['smiles']
        props = compute_properties_rdkit(smi)
        if props is None:
            if args.invalid_policy == 'fail':
                # Count as failure with a configurable reason (ensure this matches task spec)
                lines.append(f"{mol_id}: FAIL ({args.invalid_reason})")
                fail_count += 1
            # else skip silently
            continue

        failures = ro5_failures(props, THRESHOLDS)
        if not failures:
            lines.append(format_pass_line(mol_id, props))
            pass_count += 1
        else:
            lines.append(format_fail_line(mol_id, failures, mode=args.fail_mode))
            fail_count += 1

    try:
        with open(args.output, 'w', encoding='utf-8') as out:
            for line in lines:
                out.write(line + "\n")
            out.write(f"Total: {pass_count} pass, {fail_count} fail\n")
    except Exception as e:
        print(f"ERROR: failed to write output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
