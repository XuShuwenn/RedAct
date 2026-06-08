#!/usr/bin/env python3
"""Heuristic classifier for reaction SMILES.

Classifies into one of: addition, elimination, substitution, oxidation,
reduction, hydrolysis, condensation, polymerization.

Usage:
  - Single reaction:
      python smiles_reaction_classifier.py --reaction "CCCl>>CCO"

  - CSV input/output:
      python smiles_reaction_classifier.py --input path/to/input.csv --output path/to/output.txt
    Input CSV must have headers: id,reaction
    Output lines format: {id}: Reaction type: {type}
"""

import argparse
import csv
import sys
from typing import List, Tuple, Dict

ALLOWED_TYPES = {
    "addition", "elimination", "substitution", "oxidation",
    "reduction", "hydrolysis", "condensation", "polymerization",
}


def parse_reaction_smiles(s: str) -> Tuple[List[str], List[str]]:
    if ">>" not in s:
        raise ValueError("Reaction SMILES must contain '>>'.")
    left, right = s.split(">>", 1)
    reactants = [r for r in left.split(".") if r]
    products = [p for p in right.split(".") if p]
    return reactants, products


def count_features(smiles_list: List[str]) -> Dict[str, int]:
    """Count heuristic features across a list of SMILES strings.
    Elements counted: O, N, F, Cl, Br, I. Bonds: '=', '#'. Carbonyl proxy: '=O'.
    """
    features = {
        "O": 0, "N": 0, "F": 0, "Cl": 0, "Br": 0, "I": 0,
        "double_bonds": 0, "triple_bonds": 0, "carbonyls": 0,
        "molecules": len(smiles_list),
    }
    for s in smiles_list:
        # Count bonds and carbonyl proxies first (string-level counts)
        features["double_bonds"] += s.count("=")
        features["triple_bonds"] += s.count("#")
        features["carbonyls"] += s.count("=O")
        # Count elements with care for two-letter halogens
        i = 0
        L = len(s)
        while i < L:
            ch = s[i]
            nxt2 = s[i:i+2]
            if nxt2 == "Cl":
                features["Cl"] += 1
                i += 2
                continue
            if nxt2 == "Br":
                features["Br"] += 1
                i += 2
                continue
            # Single-letter elements
            if ch == "O":
                features["O"] += 1
            elif ch == "N":
                features["N"] += 1
            elif ch == "F":
                features["F"] += 1
            elif ch == "I":
                features["I"] += 1
            i += 1
    return features


def has_water(smiles_list: List[str]) -> bool:
    """Detect water as a separate molecule: SMILES 'O' exactly present."""
    return any(m == "O" for m in smiles_list)


def classify_reaction(reaction_smiles: str) -> Tuple[str, Dict[str, int], Dict[str, int]]:
    """Classify a reaction SMILES, returning (type, react_features, prod_features)."""
    reactants, products = parse_reaction_smiles(reaction_smiles.strip())
    rf = count_features(reactants)
    pf = count_features(products)

    # Deltas
    unsat_delta = (pf["double_bonds"] + pf["triple_bonds"]) - (rf["double_bonds"] + rf["triple_bonds"])
    carbonyl_delta = pf["carbonyls"] - rf["carbonyls"]
    O_delta = pf["O"] - rf["O"]
    halogen_r = rf["F"] + rf["Cl"] + rf["Br"] + rf["I"]
    halogen_p = pf["F"] + pf["Cl"] + pf["Br"] + pf["I"]
    halogen_delta = halogen_p - halogen_r

    # Special cases: hydrolysis and condensation via explicit water
    react_has_water = has_water(reactants)
    prod_has_water = has_water(products)

    if react_has_water and pf["molecules"] > rf["molecules"]:
        return "hydrolysis", rf, pf
    if prod_has_water and pf["molecules"] < rf["molecules"]:
        return "condensation", rf, pf

    # Polymerization: repeated identical monomer SMILES forming one larger product
    if pf["molecules"] == 1 and len(reactants) >= 2 and len(set(reactants)) == 1:
        # Further heuristic: small changes in heteroatoms and unsaturation
        if abs(O_delta) <= 1 and abs(unsat_delta) <= 1 and abs(halogen_delta) <= 1:
            return "polymerization", rf, pf

    # Oxidation and reduction precedence when O or carbonyl changes strongly
    if O_delta > 0 or carbonyl_delta > 0:
        return "oxidation", rf, pf
    if O_delta < 0 or carbonyl_delta < 0 or (halogen_delta < 0 and O_delta <= 0 and unsat_delta <= 0):
        return "reduction", rf, pf

    # Elimination: unsaturation increases with loss of a small group (O or halogen drop)
    if unsat_delta > 0 and (O_delta < 0 or halogen_delta < 0):
        return "elimination", rf, pf

    # Addition: unsaturation decreases without heteroatom loss
    if unsat_delta < 0 and O_delta >= 0 and halogen_delta >= 0:
        return "addition", rf, pf

    # Substitution: unsaturation ~ unchanged, one heteroatom decreases while another increases
    if unsat_delta == 0:
        hetero_change = (halogen_delta != 0) or (O_delta != 0) or (carbonyl_delta != 0)
        # prototypical: halogen down, oxygen up
        if (halogen_delta < 0 and O_delta > 0) or hetero_change:
            return "substitution", rf, pf

    # Fallbacks based on unsaturation
    if unsat_delta > 0:
        return "elimination", rf, pf
    if unsat_delta < 0:
        return "addition", rf, pf
    return "substitution", rf, pf


def classify_csv(input_path: str, output_path: str) -> None:
    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        if "id" not in reader.fieldnames or "reaction" not in reader.fieldnames:
            raise ValueError("Input CSV must have headers: id,reaction")
        rows = list(reader)

    outputs = []
    for row in rows:
        rid = str(row["id"]).strip()
        rxn = str(row["reaction"]).strip()
        if not rid or not rxn:
            raise ValueError("Empty id or reaction line encountered.")
        rtype, _, _ = classify_reaction(rxn)
        if rtype not in ALLOWED_TYPES:
            raise ValueError(f"Classifier produced an unsupported type: {rtype}")
        outputs.append(f"{rid}: Reaction type: {rtype}")

    with open(output_path, "w") as out:
        for line in outputs:
            out.write(line + "\n")


def main():
    parser = argparse.ArgumentParser(description="Reaction SMILES classifier")
    parser.add_argument("--reaction", help="Single reaction SMILES, e.g., 'CCCl>>CCO'", default=None)
    parser.add_argument("--input", help="CSV file with headers id,reaction", default=None)
    parser.add_argument("--output", help="Output file path (for CSV mode)", default=None)
    args = parser.parse_args()

    if args.reaction:
        rtype, rf, pf = classify_reaction(args.reaction)
        print(f"Type: {rtype}")
        # Brief feature summary for verification
        hal_r = rf["F"] + rf["Cl"] + rf["Br"] + rf["I"]
        hal_p = pf["F"] + pf["Cl"] + pf["Br"] + pf["I"]
        print("Reactants:", rf)
        print("Products:", pf)
        print("Deltas:", {
            "unsaturation": (pf["double_bonds"] + pf["triple_bonds"]) - (rf["double_bonds"] + rf["triple_bonds"]),
            "carbonyl": pf["carbonyls"] - rf["carbonyls"],
            "O": pf["O"] - rf["O"],
            "halogens": hal_p - hal_r,
            "molecules": pf["molecules"] - rf["molecules"],
        })
        return

    if args.input and args.output:
        classify_csv(args.input, args.output)
        print(f"Wrote classifications to {args.output}")
        return

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
