#!/usr/bin/env python3
"""
Batch Lipinski Rule of Five evaluation for SMILES in a CSV.

Input CSV columns: id, smiles
Output lines:
  - PASS: "{id}: PASS (MW={mw}, LogP={logp}, HBD={hbd}, HBA={hba})"
  - FAIL: "{id}: FAIL ({criterion})"  # by default, first failing criterion only
Final summary:
  - "Total: {pass_count} pass, {fail_count} fail"

Usage:
  python scripts/ro5_batch.py \
    --input /root/input.csv --output /root/output.txt \
    [--mw-max 500 --logp-max 5 --hbd-max 5 --hba-max 10] [--all-fail-reasons]

Notes:
- Decisions use raw (unrounded) descriptor values; MW/LogP are rounded only for display.
- LogP is computed using RDKit's Crippen.MolLogP for consistency.
"""

import argparse
import csv
import sys
from typing import List, Tuple

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski
except Exception as e:
    sys.stderr.write("ERROR: RDKit is required for this script.\n")
    raise


def compute_descriptors(smiles: str) -> Tuple[float, float, int, int]:
    """Return (mw, logp, hbd, hba) for a SMILES string.
    Raises ValueError if SMILES cannot be parsed.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid SMILES")
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    hbd = int(Lipinski.NumHDonors(mol))
    hba = int(Lipinski.NumHAcceptors(mol))
    return mw, logp, hbd, hba


def format_pass_line(mol_id: str, mw: float, logp: float, hbd: int, hba: int) -> str:
    return f"{mol_id}: PASS (MW={mw:.2f}, LogP={logp:.2f}, HBD={hbd}, HBA={hba})"


def decide_fail_reasons(mw: float, logp: float, hbd: int, hba: int,
                        mw_max: float, logp_max: float, hbd_max: int, hba_max: int,
                        all_reasons: bool) -> List[str]:
    reasons = []
    if mw > mw_max:
        reasons.append("MW")
    if logp > logp_max:
        reasons.append("LogP")
    if hbd > hbd_max:
        reasons.append("HBD")
    if hba > hba_max:
        reasons.append("HBA")
    if not all_reasons and reasons:
        return [reasons[0]]
    return reasons


def main():
    ap = argparse.ArgumentParser(description="Lipinski Rule of Five batch evaluator")
    ap.add_argument("--input", default="input.csv", help="Input CSV path (id,smiles)")
    ap.add_argument("--output", default="output.txt", help="Output text file path")
    ap.add_argument("--mw-max", type=float, default=500.0, help="Max MW threshold")
    ap.add_argument("--logp-max", type=float, default=5.0, help="Max LogP threshold")
    ap.add_argument("--hbd-max", type=int, default=5, help="Max HBD threshold")
    ap.add_argument("--hba-max", type=int, default=10, help="Max HBA threshold")
    ap.add_argument("--all-fail-reasons", action="store_true",
                    help="If set, list all failing criteria in canonical order")
    args = ap.parse_args()

    pass_count = 0
    fail_count = 0
    lines: List[str] = []

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"id", "smiles"}
        if not required.issubset({h.lower() for h in reader.fieldnames or []}):
            # Try case-sensitive fallback
            if not required.issubset(set(reader.fieldnames or [])):
                sys.stderr.write("ERROR: Input CSV must contain 'id' and 'smiles' columns.\n")
                sys.exit(1)
        # Map headers case-insensitively
        headers = {h.lower(): h for h in reader.fieldnames}
        id_col = headers.get("id", "id")
        smi_col = headers.get("smiles", "smiles")

        for row in reader:
            mol_id = row.get(id_col, "").strip()
            smiles = row.get(smi_col, "").strip()
            if not mol_id:
                continue  # skip blank ID rows
            try:
                mw, logp, hbd, hba = compute_descriptors(smiles)
            except ValueError:
                # If policy requires strict criterion-only fails, use a neutral tag or handle upstream.
                lines.append(f"{mol_id}: FAIL (Invalid)")
                fail_count += 1
                continue

            reasons = decide_fail_reasons(
                mw, logp, hbd, hba,
                args.mw_max, args.logp_max, args.hbd_max, args.hba_max,
                args.all_fail_reasons,
            )

            if reasons:
                if args.all_fail_reasons:
                    reason_str = ", ".join(reasons)
                else:
                    reason_str = reasons[0]
                lines.append(f"{mol_id}: FAIL ({reason_str})")
                fail_count += 1
            else:
                lines.append(format_pass_line(mol_id, mw, logp, hbd, hba))
                pass_count += 1

    with open(args.output, "w", encoding="utf-8") as out:
        for line in lines:
            out.write(line + "\n")
        out.write(f"Total: {pass_count} pass, {fail_count} fail\n")


if __name__ == "__main__":
    main()
