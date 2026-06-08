---
name: smiles-reaction-classification
description: "Classify organic reaction types from reaction SMILES using rule-based structural-change heuristics and verify before writing results."
---

# SMILES Reaction Classification

A practical, reusable workflow for mapping reaction SMILES (reactants>>products) to a single best reaction class among: addition, elimination, substitution, oxidation, reduction, hydrolysis, condensation, polymerization.

This skill focuses on lightweight string-derived features (no chemistry toolkits) and prioritizes consistent verification to avoid common misclassifications.

## When to Use

Use this skill when you are given reaction SMILES strings and asked to choose the closest reaction class from a fixed list, especially when:
- The task provides an input file of `id,reaction` pairs.
- Only a single final label per reaction is required.
- You must work without external chemistry libraries.

## Core Workflow

1. Read and parse the input reliably
   - Load the CSV with a robust parser (e.g., Python's `csv` module). Expect a header.
   - Each row: `id,reaction` where reaction uses the syntax `reactant1.reactant2...>>product1.product2...`.
   - Do not guess; always inspect the actual file before writing outputs.

2. Split each reaction into components
   - Split once on `>>` into left (reactants) and right (products).
   - Split each side on `.` to get individual SMILES strings.
   - Trim whitespace and ignore empty tokens.

3. Derive lightweight features from SMILES strings
   For each side (left/right), compute:
   - Unsaturation proxy: count of `=` and `#` characters.
   - Carbonyl proxy: count of `=O` substrings.
   - Heteroatom counts: totals of `O`, `N`, `S`, `P` characters.
   - Halogen counts: number of `Cl`, `Br`, `I` substrings and `F` characters.
   - Molecule count: number of tokens on that side.

   Then compute deltas (products − reactants) for each feature.

4. Decide the reaction class using ordered rules
   Apply rules in this order (first match wins):
   - Addition
     - Unsaturation decreases (delta_unsat < 0), and there is no clear increase in heteroatoms that indicates oxidation.
     - Typical signs: double/triple bonds reduced to single bonds without introducing new heteroatoms.
   - Elimination
     - Unsaturation increases (delta_unsat > 0), often with a decrease in heteroatoms (e.g., loss of OH leading to C=C).
   - Substitution
     - Unsaturation approximately unchanged, but a functional group is replaced (e.g., halogen decreases and O/N/S increases), with overall molecule count unchanged.
   - Oxidation
     - Carbonyls increase (delta_carbonyl > 0) or heteroatoms (notably O) increase in a way that corresponds to higher oxidation state; unsaturation may increase or stay similar.
   - Reduction
     - Carbonyls decrease (delta_carbonyl < 0), or halogens disappear without being replaced by other heteroatoms (halogen delta < 0 and heteroatom delta ≤ 0), and unsaturation does not increase.
     - Important: dehalogenation to a saturated hydrocarbon (loss of halogen, no compensating heteroatom gain) is reduction, not substitution.
   - Hydrolysis
     - Molecule count increases (products > reactants) with an increase in O, often splitting one molecule into two and incorporating an OH.
   - Condensation
     - Molecule count decreases (products < reactants) with a decrease in O, consistent with loss of a small molecule like water/alcohol upon bond formation.
   - Polymerization
     - Multiple reactants merge into one product (reactants ≥ 2, products = 1) forming a larger unit; often unsaturation decreases or remains similar; repeated monomer patterns may be present.
   - Fallback: If no rule triggers, choose substitution as the conservative default for single-site functional group changes.

5. Format and write outputs exactly as required
   - For each row: `{id}: Reaction type: {type}` using one of the allowed labels only.
   - Preserve the original order of input rows unless instructed otherwise.

## Verification

Before finalizing results:
- Sanity checks against feature changes
  - If you labeled addition, confirm delta_unsat < 0.
  - If you labeled elimination, confirm delta_unsat > 0.
  - If you labeled substitution, confirm delta_unsat ≈ 0 and heteroatom changes compensate (e.g., halogen loss with O/N gain).
  - If you labeled oxidation, confirm increases in `=O` or total O and no decrease in unsaturation contradicting the call.
  - If you labeled reduction, confirm halogen or carbonyl decreases without compensating heteroatom gain.
- Edge-case tie-breakers
  - If halogens vanish and no other heteroatom is added, prefer reduction over substitution.
  - If both unsaturation and heteroatoms decrease, prefer addition if the change is dominated by π-bond saturation; prefer reduction if the key change is loss of carbonyl or halogen.
- Output format check
  - Ensure each line strictly matches: `{id}: Reaction type: {type}`.
  - Verify every input `id` has exactly one output line and the type is one of the allowed categories.

## Common Pitfalls and How to Avoid Them

- Misclassifying dehalogenation as substitution
  - Fix: If halogen count decreases and no other heteroatom increases, classify as reduction.
- Inferring hydrogen counts from SMILES
  - Avoid assumptions about implicit hydrogens; rely on bond-order proxies (`=`, `#`), carbonyl counts (`=O`), and heteroatom/halogen deltas.
- Ignoring multiple components
  - Always split on `.` and track molecule counts; changes can indicate hydrolysis/condensation.
- Skipping input validation or premature writing
  - Always read the actual input first and confirm expected format before writing results.
- Formatting errors
  - Stick to the exact output line format and allowed label set; no extra commentary in the output file.

## Success Criteria

- Every reaction `id` from the input has exactly one output line.
- Each line uses one of the allowed labels.
- Classification aligns with feature-change rules and passes verification checks.

## Optional Script Usage

This repository includes a helper script implementing the above heuristics without external dependencies.

Example CLI:
- Classify a single reaction: `python scripts/smiles_reaction_heuristics.py --reaction "R1=react1.react2>>prod1.prod2"`
- Classify from a CSV: `python scripts/smiles_reaction_heuristics.py --csv path/to/input.csv`

The script prints suggested labels and key features to aid verification before writing final outputs.
