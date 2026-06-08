---
name: reaction-smiles-classification
description: "Classify organic reaction types from reaction SMILES by comparing reactant and product features (unsaturation, heteroatom changes, and molecule count)."
---

# Reaction SMILES Classification

Classify organic reaction types from reaction SMILES strings (reactants>>products) using structural change signals: unsaturation, heteroatom counts, presence/absence of small molecules, and molecule counts.

Supported types: addition, elimination, substitution, oxidation, reduction, hydrolysis, condensation, polymerization.

## When to Use

Use this skill when the task asks you to:
- read reaction SMILES from a file (e.g., CSV id,reaction format)
- identify a single reaction type from a standard set
- write per-reaction classifications to an output file

## Core Workflow

1. Read all reactions from the provided input path. Expect format like `id,reaction` with `reaction` as `reactant1.reactant2...>>product1.product2...`.
2. For each reaction:
   - Split into reactant and product lists on `>>` and `.`.
   - Extract structural features for both sides:
     - unsaturation markers: counts of `=` and `#`
     - carbonyl proxy: count of `=O`
     - heteroatom counts: O, N, halogens (F, Cl, Br, I)
     - number of molecules on each side
     - presence of water as a separate molecule (`O` exactly) on either side
   - Compute deltas: product minus reactant for unsaturation, carbonyls, O, halogens.
   - Apply decision rules (below) to choose the single best reaction type.
3. Verification:
   - Confirm the chosen type is within the allowed set.
   - Confirm every input id has exactly one output line in the required format.
   - Cross-check that the chosen type is consistent with the measured feature deltas.
4. Write results in the exact required output format: `{id}: Reaction type: {type}`.

## Decision Rules

Apply rules in this order, using simple heuristics derived from SMILES string patterns. If multiple rules could apply, choose the first that matches with strong signals.

1. Hydrolysis
   - Condition: `O` appears as a separate reactant molecule and the product side has more molecules than the reactant side.
   - Interpretation: water-mediated bond cleavage.

2. Condensation
   - Condition: `O` appears as a separate product molecule and the product side has fewer molecules than the reactant side.
   - Interpretation: two molecules joined with water (or a small molecule) expelled.

3. Polymerization
   - Condition: multiple identical monomers on the reactant side (`reactants` contain repeated identical SMILES) forming a single, much larger product; heteroatom deltas small and unsaturation change minor.
   - Interpretation: many monomers combine into one macromolecule.

4. Oxidation
   - Strong signals: increase in oxygen count (O_delta > 0) and/or increase in carbonyl count (carbonyl_delta > 0), often with an increase in unsaturation.
   - Examples: alcohol → carbonyl, addition of O or formation of C=O.

5. Reduction
   - Strong signals: decrease in oxygen count (O_delta < 0), decrease in carbonyls, or removal of electronegative substituents (halogen_delta < 0) without compensating heteroatom increases.
   - Examples: carbonyl → alcohol, loss of halide from carbon chain replaced by hydrogen.

6. Elimination
   - Strong signals: unsaturation increases (unsat_delta > 0) with concurrent loss of a small group (e.g., halogen or O decrease).
   - Examples: dehydrohalogenation, dehydration producing a double bond.

7. Addition
   - Strong signals: unsaturation decreases (unsat_delta < 0) without significant heteroatom loss; no water formation/consumption events.
   - Examples: adding across a double bond (including hydrogenation when no net O change and no halogen removal is detected).

8. Substitution
   - Strong signals: unsaturation remains unchanged while one heteroatom is replaced by another (e.g., halogen decreases while oxygen increases). Net heavy-atom count remains similar.
   - Examples: halide → alcohol via nucleophilic substitution.

Fallback: If no rule fits clearly, prefer substitution when a heteroatom changes type with minimal unsaturation change, else choose addition/elimination based on the sign of unsaturation delta.

## Verification

Before finalizing results:
- Allowed set check: Ensure each classification is one of {addition, elimination, substitution, oxidation, reduction, hydrolysis, condensation, polymerization}.
- Coverage check: Every id from the input appears once in the output.
- Consistency checks:
  - Oxidation: O_delta ≥ 1 or carbonyl_delta ≥ 1 and not flagged as hydrolysis/condensation/polymerization.
  - Reduction: O_delta ≤ -1 or carbonyl_delta ≤ -1 or halogen_delta ≤ -1 with no offsetting O increase.
  - Elimination: unsat_delta ≥ 1 and (halogen_delta ≤ -1 or O_delta ≤ -1).
  - Addition: unsat_delta ≤ -1 and O_delta ≈ 0 and halogen_delta ≥ 0.
  - Substitution: unsat_delta ≈ 0 and at least one heteroatom decreases while another increases (e.g., halogen down, oxygen up).
- Formatting: Output lines exactly match the required pattern without extra spaces or punctuation beyond the specified format.

## Common Pitfalls

- Miscounting halogens: Always treat two-character halogens (`Cl`, `Br`) as single elements; do not count `C` from `Cl` as carbon.
- Confusing reduction with substitution: If a halogen is removed and replaced by hydrogen (with no new heteroatom introduced), it is reduction, not substitution. Substitution should show one heteroatom decreasing while another increases, with unsaturation unchanged.
- Confusing hydrogenation with reduction: Addition across a C=C (unsaturation decreases) without changes in heteroatom counts is best labeled as addition. Reduction is preferred when a carbon’s oxidation state drops (e.g., carbonyl → alcohol or removal of O).
- Ignoring unsaturation signals: `=` and `#` counts are strong indicators. Increased `=`/`#` suggests elimination or oxidation; decreased suggests addition or reduction.
- Overlooking small molecule participation: Water in SMILES is `O`. Its explicit presence on the reactant side often indicates hydrolysis; on the product side often indicates condensation.
- Incorrect output format: Ensure each line is `{id}: Reaction type: {type}` with the exact type string.

## Success Criteria

- All reactions classified with one allowed type.
- Classifications are supported by feature deltas.
- Output lines are correctly formatted and cover all input ids.

## Optional Script Usage

Use the provided helper to compute features and classify reactions deterministically.

Examples:
- Classify a single reaction SMILES: `python scripts/smiles_reaction_classifier.py --reaction "reactant1.reactant2>>product1"`
- Classify reactions in a CSV and write the required output file: `python scripts/smiles_reaction_classifier.py --input path/to/input.csv --output path/to/output.txt`

The script prints the chosen type and a brief feature summary for single-reaction mode, and writes properly formatted lines for CSV mode.
