---
name: reaction-type
description: "Identify organic reaction types (addition, elimination, substitution, etc.) from SMILES reaction strings."
---

# Organic Reaction Type Identification

## When to Use

- Classify organic chemical reactions
- Identify reaction mechanisms
- Analyze SMILES reaction strings

## Input Format

File `/root/input.csv`:
```
id,reaction
R01,reactant1.reactant2>>product1.product2
```

## Reaction Types

Choose ONE best type from:
- addition
- elimination
- substitution
- oxidation
- reduction
- hydrolysis
- condensation
- polymerization

## Output Format

To `/root/output.txt`:
```
{id}: Reaction type: {type}
```

Example:
```
R01: Reaction type: substitution
```

- Write exactly one line per input record in `/root/output.txt` as `{id}: Reaction type: {type}`.
- Preserve each input ID exactly, keep input order, and use only allowed lowercase reaction-type labels.
- Do not add explanations, headers, extra columns, or other commentary.


## Execution Protocol

- After writing `/root/output.txt`, read it back and confirm every input row has exactly one corresponding line in the required format `{id}: Reaction type: {type}`, with no missing or extra IDs and only allowed labels.

## Execution Protocol

- Follow the current task/runtime instructions for tool use and completion exactly.
- If the environment specifies a required action schema, tool invocation format, or message pattern, use that exact syntax verbatim rather than any default style.
- If the environment requires an exact final completion token or phrase, output it exactly as specified when finished.
- Do not replace required machine-readable tool calls or completion markers with conversational summaries.
- Before finishing, verify both the requested file output and the required completion signal.

- Read the reaction as `reactants>>products` and compare reactants vs products directly.
- Classify from the dominant net structural change visible in the reaction string, not from guessed reagents, missing conditions, or speculative mechanism details.
- Check connectivity changes, bond formation or cleavage, bond-order changes, gain or loss of unsaturation, atom/group replacement, functional-group interconversion, and oxidation-level change.
- Choose exactly ONE best-fit label from the allowed reaction types; if several seem plausible, pick the closest allowed category that captures the main overall transformation rather than minor byproducts or spectator molecules.
- Useful mapping cues: addition = atoms/groups added across a multiple bond or saturation increases; elimination = loss of atoms/groups with multiple-bond formation or increased unsaturation; substitution = one group replaces another on the same main framework; oxidation = increased oxidation level such as more C-O/C-X bonding or fewer C-H bonds; reduction = decreased oxidation level or gain of H equivalents; hydrolysis = bond cleavage by water, often giving OH/H incorporation or simpler fragments; condensation = two components join with loss of a small molecule such as H2O; polymerization = repeating-unit chain growth or monomer linking into a macromolecular product.## Classification Approach

- Analyze reaction transformation pattern
- SMILES format: reactant1.reactant2>>product1.product2
- Consider: bond changes, atom additions/removals

## Tips

- Use RDKit for SMILES parsing
- Compare reactant and product structures
- Look for functional group changes
- Consider reaction mechanism patterns

- Hallmark cues for the fixed label set:
  - substitution: one group replaced by another on the same carbon/framework
  - addition: unsaturation decreases or atoms/groups add across a multiple bond
  - elimination: a small group is lost and a multiple bond forms
  - oxidation: alcohol -> carbonyl or overall increase in C/O bonds / decrease in C/H bonds
  - reduction: carbonyl or unsaturated bond becomes more saturated or overall increase in C/H bonds
  - hydrolysis: bond cleavage by water into smaller fragments
  - condensation: two molecules join with loss of a small molecule, often water
- If mechanism details are unclear, prefer the visible structural change at the changed site in the SMILES.
