---
name: reaction-type
description: "Identify organic reaction types (addition, elimination, substitution, etc.) from SMILES reaction strings."
---

# Organic Reaction Type Identification

## When to Use

- Classify organic chemical reactions
- Identify reaction mechanisms
- Analyze SMILES reaction strings

## Runtime Protocol Check

- Before reading inputs, classifying reactions, or writing outputs, inspect the current runtime/task instructions and identify any required action syntax, tool-call schema, output path, file format, and completion token.
- If the environment specifies an exact action/message pattern or exact completion phrase, use that syntax verbatim for every step; do not substitute default tool-call styles or a conversational closing.
- Do not infer the deliverable format from `/root/input.csv` alone. Confirm the required destination and exact output wording for this run before generating results.


## Input Format

File `/root/input.csv`:
```
id,reaction
R01,reactant1.reactant2>>product1.product2
```
- First read `/root/input.csv` to confirm the header, record count, and exact `id` / `reaction` values before classifying anything.
- Treat each CSV row as one output line; maintain a direct one-to-one mapping from each input `id` to exactly one reaction-type label.
- Preserve input order from the file when generating `/root/output.txt`.

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

- Treat `/root/output.txt` as a strict machine-readable deliverable, not a place for reasoning or prose.
- Preserve IDs exactly as given in the input, including case; do not normalize, rename, or paraphrase them.
- Do not invent an alternative schema or assume the output path, file format, or completion behavior from prior tasks or from the input being CSV; if the current task/runtime instructions differ, follow the current instructions exactly.
- Write results only after confirming the exact destination and required format for this run.
- WRONG in file: `R01 is substitution` or `r01: likely substitution`
- RIGHT in file: `R01: Reaction type: substitution`

### Output Preflight

- Even though the input is CSV, do NOT switch the output to CSV, TSV, JSON, or prose unless the current runtime instructions explicitly override this skill.
- Before writing any result, confirm this run's destination path, exact line schema, and required completion signal/tool-call syntax.
- Base the output only on the rows actually present in `/root/input.csv` for this run.



## Execution Protocol

- After writing `/root/output.txt`, read it back and confirm every input row has exactly one corresponding line in the required format `{id}: Reaction type: {type}`, with no missing or extra IDs and only allowed labels.

- Start by reading `/root/input.csv` directly and enumerating every `id,reaction` row to process before assigning labels.
- For multiple rows, prefer a short Python script to read the CSV, classify each reaction in one pass, and write `/root/output.txt` directly in the final required format.
- Use a two-phase workflow: first determine one best-fit allowed label for every input ID, then write the final output in one pass.
- Keep a 1:1 mapping between input rows and output lines, preserving input order and exact IDs throughout.
- Before writing, ensure there is one planned classification for every input row; after writing, confirm line count equals input record count and each input ID appears exactly once in the original order.
- Final check before completion: verify output path, exact `{id}: Reaction type: {type}` formatting, exact ID preservation including case, allowed labels only, and the runtime-required completion token.

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

- Compare reactant and product structures first; for small explicit inputs, direct inspection is often enough.
- Use RDKit for SMILES parsing only when direct inspection is insufficient.
- Look first for functional-group changes and simple motif matches before considering broader mechanism labels.
- Do not overinfer mechanism from missing conditions; prioritize the visible net transformation.
