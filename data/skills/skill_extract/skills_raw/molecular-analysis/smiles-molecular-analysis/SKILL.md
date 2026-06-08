---
name: smiles-molecular-analysis
description: "Given a SMILES string, compute molecular weight, detect key functional groups via SMARTS, and count all hydrogens with toolkit-backed verification and precise output formatting."
---

# SMILES Molecular Analysis

Compute molecular weight (average atomic weights), identify common functional groups via SMARTS patterns, and count all hydrogens (explicit + implicit) from a SMILES string. Produce stable, precisely formatted outputs.

## When to Use

Use this skill when asked to analyze a molecule from a SMILES string to report:
- molecular weight (rounded to 2 decimals)
- presence of specific functional groups (alphabetically, comma-separated; or "None")
- total hydrogen count including implicit hydrogens

## Core Workflow

1. Parse the SMILES with a cheminformatics toolkit (e.g., RDKit):
   - Sanitize on load. If parsing fails, request a valid SMILES.
   - Keep the full molecule as provided (multi-fragment inputs are allowed; compute totals across fragments).

2. Molecular weight (average mass):
   - Use toolkit's average atomic weights (e.g., RDKit `Descriptors.MolWt`).
   - Round to exactly 2 decimals and format with two digits after the decimal.

3. Hydrogen count (explicit + implicit):
   - Add explicit hydrogens in silico (e.g., `Chem.AddHs(mol)` in RDKit).
   - Count atoms with atomic number 1 to include all H.

4. Functional group detection (presence-only):
   - Match SMARTS patterns against the unsaturated (original) molecule.
   - Use patterns that avoid overlaps (e.g., avoid counting carboxylic acid OH as an alcohol; avoid classifying esters/amides as ketones).
   - Collect unique group names present from this fixed set:
     - alcohol: [OX2H][#6;!$(C=O)]
     - aldehyde: [CX3H1](=O)[#6]
     - amide: [CX3](=O)[NX3H0,H1,H2]
     - amine: [NX3;H2,H1,H0;!$(NC=O);!$([N+]);!$([N-])][#6]
     - carboxylic acid: [CX3](=O)[OX2H1]
     - ester: [CX3](=O)[OX2][#6]
     - ether: [OD2]([#6;!$(C=O)])[#6;!$(C=O)]
     - halide: [#6][F,Cl,Br,I]
     - ketone: [CX3](=O)([#6])[#6]
     - nitro: [N+](=O)[O-] or [NX3](=O)=O
   - Sort detected group names alphabetically. If none found, output "None".

5. Output formatting (exact lines):
   - Molecular weight: {value} g/mol
   - Functional groups: {group1}, {group2}, ... | or "None"
   - Hydrogen count: {integer}

## Verification

Perform these checks before finalizing:
- SMILES parse succeeded and molecule has at least one atom.
- Molecular weight is computed using average atomic weights (e.g., RDKit `Descriptors.MolWt`), not monoisotopic mass.
- Hydrogen count after adding hydrogens equals the count of H atoms in the expanded molecule.
- Functional groups list is alphabetically sorted, de-duplicated, and matches only the intended classes (no alcohol from carboxylic acids; no ketone from amides/esters).
- Output lines are exactly three and strictly match the required labels and punctuation, with molecular weight shown to two decimal places.

Optional cross-checks:
- Compare hydrogen count to the hydrogen count inferred from the molecular formula (e.g., via RDKit `CalcMolFormula`). They should agree for neutral molecules.
- Spot-check the presence of carbonyls ("C=O") vs. detected carbonyl-derived classes; report inconsistency if, e.g., carbonyl present but no aldehyde/ketone/amide/ester/acid detected.

## Common Pitfalls

- Using monoisotopic mass (e.g., exact mass) instead of average molecular weight; this often differs at the second decimal place. Use average mass and format to 2 decimals.
- Under-counting hydrogens by not adding implicit hydrogens before counting. Always add hydrogens in silico and then count H atoms.
- Misclassifying functional groups:
  - Alcohol from carboxylic acids: exclude OH directly bound to a carbonyl carbon.
  - Ketone from esters/amides: require both carbonyl substituents to be carbons.
  - Amine vs amide: exclude N bound to a carbonyl (amide) from the amine class.
  - Nitro representations vary; match both [N+](=O)[O-] and N(=O)=O forms.
  - Halide: ensure the halogen is carbon-bound, not part of a counterion.
- Not sorting functional groups alphabetically or emitting an empty string instead of "None" when none are found.
- Rounding/formatting errors (e.g., 2.1 instead of 2.10). Use fixed-point formatting.

## Success Criteria

- Molecular weight reported using average atomic weights, correctly rounded to 2 decimals.
- Functional groups present are correctly detected from the specified set, alphabetically listed, or "None".
- Hydrogen count includes all hydrogens (implicit + explicit).
- Output strictly follows the three-line required format.

## Optional Script Usage

A helper script is provided to perform the full analysis with RDKit.

Examples:
- From a SMILES string:
  - python scripts/smiles_molecular_analysis.py --smiles "CC(=O)Oc1ccccc1C(=O)O" --out output.txt
- From an input file containing a single SMILES line:
  - python scripts/smiles_molecular_analysis.py --in input.txt --out output.txt

The script writes exactly three lines in the required format to the specified output file.
