#!/usr/bin/env python3
"""Rule-based SMILES reaction classification (no chemistry toolkits).

Classifies reaction SMILES into one of:
  addition, elimination, substitution, oxidation, reduction, hydrolysis, condensation, polymerization

Features and decisions are based on string-level heuristics:
- Unsaturation proxies: counts of '=' and '#'
- Carbonyl proxy: count of '=O'
- Heteroatom counts: O, N, S, P
- Halogen counts: F, Cl, Br, I
- Molecule counts from '.' tokenization

Usage examples:
  python scripts/smiles_reaction_heuristics.py --reaction "A.B>>C"
  python scripts/smiles_reaction_heuristics.py --csv input.csv

When using --csv, the file must contain at least two columns: id,reaction.
The script prints one line per reaction with an id and a classification, plus a brief feature summary.
"""

import argparse
import csv
import json
import sys
from typing import List, Tuple, Dict

HALOGEN_PAIRS = ["Cl", "Br"]
HALOGEN_SINGLE = ["F", "I"]


def split_reaction(reaction: str) -> Tuple[List[str], List[str]]:
    if ">>" not in reaction:
        raise ValueError("Reaction must contain '>>' separating reactants and products")
    left, right = reaction.split(">>", 1)
    left_tokens = [t.strip() for t in left.split(".") if t.strip()]
    right_tokens = [t.strip() for t in right.split(".") if t.strip()]
    return left_tokens, right_tokens


def count_substring(s: str, sub: str) -> int:
    # Non-overlapping count is fine for these markers
    return s.count(sub)


def side_features(mols: List[str]) -> Dict[str, int]:
    feats = {
        "unsat": 0,         # '=' and '#'
        "carbonyl": 0,      # '=O'
        "O": 0, "N": 0, "S": 0, "P": 0,
        "F": 0, "Cl": 0, "Br": 0, "I": 0,
        "mol_count": len(mols)
    }
    for m in mols:
        feats["unsat"] += m.count("=") + m.count("#")
        feats["carbonyl"] += m.count("=O")
        # Count halogen digraphs first to avoid double counting 'Cl' as 'C' + 'l'
        for pair in HALOGEN_PAIRS:
            feats[pair] += count_substring(m, pair)
        # Single-letter halogens
        for sing in HALOGEN_SINGLE:
            feats[sing] += m.count(sing)
        # Heteroatoms (simple char counts)
        for atom in ["O", "N", "S", "P"]:
            feats[atom] += m.count(atom)
    return feats


def delta_features(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    keys = set(left.keys()) | set(right.keys())
    return {k: right.get(k, 0) - left.get(k, 0) for k in keys}


def classify_by_rules(lf: Dict[str, int], rf: Dict[str, int]) -> str:
    d = delta_features(lf, rf)
    # Compact aliases
    d_unsat = d.get("unsat", 0)
    d_carbonyl = d.get("carbonyl", 0)
    d_O = d.get("O", 0)
    d_N = d.get("N", 0)
    d_S = d.get("S", 0)
    d_P = d.get("P", 0)
    d_mols = d.get("mol_count", 0)
    d_Cl = d.get("Cl", 0)
    d_Br = d.get("Br", 0)
    d_F = d.get("F", 0)
    d_I = d.get("I", 0)

    hetero_delta = d_O + d_N + d_S + d_P
    hal_delta = d_Cl + d_Br + d_F + d_I

    # Rule order matters. First match wins.
    # 1) Addition: unsaturation decreases with no clear oxidation signature
    if d_unsat < 0 and not (d_carbonyl > 0 and d_O > 0):
        return "addition"

    # 2) Elimination: unsaturation increases, often with heteroatom loss
    if d_unsat > 0 and hetero_delta <= 0:
        return "elimination"

    # 3) Substitution: bond order stable, functional group swap
    if d_unsat == 0 and ((hal_delta < 0 and (d_O > 0 or d_N > 0 or d_S > 0)) or hetero_delta != 0) and d_mols == 0:
        return "substitution"

    # 4) Oxidation: more carbonyl or more oxygen; unsaturation non-decreasing
    if d_carbonyl > 0 or (d_O > 0 and d_unsat >= 0):
        return "oxidation"

    # 5) Reduction: fewer carbonyls, or halogen loss without compensating heteroatom gain
    if d_carbonyl < 0 or (hal_delta < 0 and hetero_delta <= 0 and d_unsat <= 0):
        return "reduction"

    # 6) Hydrolysis: split into more molecules with oxygen incorporation
    if d_mols > 0 and d_O >= 0:
        return "hydrolysis"

    # 7) Condensation: fewer molecules with oxygen loss
    if d_mols < 0 and d_O < 0:
        return "condensation"

    # 8) Polymerization: multiple reactants merge into one, no strong ox/red signal
    if lf.get("mol_count", 0) >= 2 and rf.get("mol_count", 0) == 1 and d_unsat <= 0:
        return "polymerization"

    # Fallback: substitution is the conservative default for single-site changes
    return "substitution"


def explain_features(lf: Dict[str, int], rf: Dict[str, int]) -> Dict[str, Dict[str, int]]:
    return {"left": lf, "right": rf, "delta": delta_features(lf, rf)}


def classify_reaction(reaction: str) -> Dict[str, object]:
    left, right = split_reaction(reaction)
    lf = side_features(left)
    rf = side_features(right)
    label = classify_by_rules(lf, rf)
    return {"label": label, "features": explain_features(lf, rf)}


def run_single(reaction: str, verbose: bool):
    try:
        result = classify_reaction(reaction)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    print(result["label"]) if not verbose else print(json.dumps(result, indent=2))


def run_csv(path: str, verbose: bool):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    # Attempt to detect header
    start_idx = 1 if rows and rows[0] and rows[0][0].lower() == "id" else 0
    for row in rows[start_idx:]:
        if len(row) < 2:
            continue
        rid, reaction = row[0].strip(), row[1].strip()
        try:
            result = classify_reaction(reaction)
            label = result["label"]
            if verbose:
                print(json.dumps({"id": rid, **result}, indent=2))
            else:
                print(f"{rid}: {label}")
        except Exception as e:
            msg = f"{rid}: ERROR {e}"
            print(msg)


def main():
    p = argparse.ArgumentParser(description="Heuristic SMILES reaction classifier")
    p.add_argument("--reaction", help="Reaction SMILES string (reactants>>products)")
    p.add_argument("--csv", help="CSV file with id,reaction columns")
    p.add_argument("--verbose", action="store_true", help="Print features and label as JSON")
    args = p.parse_args()

    if bool(args.reaction) == bool(args.csv):
        print("Provide exactly one of --reaction or --csv", file=sys.stderr)
        sys.exit(1)

    if args.reaction:
        run_single(args.reaction, args.verbose)
    else:
        run_csv(args.csv, args.verbose)


if __name__ == "__main__":
    main()
