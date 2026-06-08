---
name: rdkit-smarts-matcher
description: "Check whether a SMARTS functional-group pattern occurs in a SMILES molecule using RDKit and output yes/no."
---

# RDKit SMARTS Matcher

Use RDKit to determine if a molecule (SMILES) contains a substructure/functional group defined by a SMARTS pattern and report a yes/no result.

## When to Use

- You need to verify if a molecule contains a particular functional group or substructure.
- Inputs are a SMILES string (molecule) and a SMARTS pattern (query).
- The required output is a simple binary result: "Match: yes" or "Match: no".

## Core Workflow

1. Read inputs
   - Expect two non-empty lines: line 1 is SMILES, line 2 is SMARTS.
   - Strip whitespace; ignore extra blank lines.

2. Parse with RDKit
   - Create the target molecule using RDKit's MolFromSmiles.
   - Create the query pattern using RDKit's MolFromSmarts.
   - If either parsing fails, stop and report an error (do not guess).

3. Match strategy
   - First attempt: mol.HasSubstructMatch(query, useChirality=False)
   - If no match and the query contains explicit hydrogen atoms (atoms with atomic number 1), repeat the match on Chem.AddHs(mol).
   - Keep aromaticity as parsed (do not kekulize unless you have a specific reason), because SMARTS often uses aromatic lowercase symbols.

4. Decide result
   - If any match is found: write "Match: yes"
   - Otherwise: write "Match: no"

5. Write output
   - Write exactly the two-word format with a colon as: "Match: yes" or "Match: no" followed by a newline.

## Verification Checklist

- Input parsing
  - Two lines present and non-empty after stripping.
  - No trailing spaces in the output line.
- RDKit parsing
  - MolFromSmiles returns a molecule (not None).
  - MolFromSmarts returns a query (not None).
- Matching
  - First try matching without explicit hydrogens.
  - If the query has explicit hydrogen atoms, also try matching on an AddHs-augmented molecule.
- Output format
  - Exactly "Match: yes" or "Match: no" (case-sensitive, single space after colon).
  - One terminal newline; no extra commentary in the output file.

## Common Pitfalls and How to Avoid Them

- Implicit vs explicit hydrogens
  - Query patterns that include explicit hydrogen atoms (e.g., an [H] atom in SMARTS) require adding explicit hydrogens to the target molecule. If in doubt, attempt a second match using Chem.AddHs.
  - Hydrogen-count constraints (e.g., H1 within atom brackets) typically match implicit hydrogens and usually do not require AddHs, but a fallback attempt with AddHs is safe if the first match fails.
- Aromaticity handling
  - SMARTS patterns using aromatic atoms (e.g., "c") expect the molecule to retain aromatic perception. Do not kekulize unless necessary.
- Chirality
  - Unless specified, do not enforce chirality in matching (useChirality=False). Enabling chirality may cause expected matches to fail if stereochemistry is unspecified in the SMILES.
- Multi-fragment molecules
  - SMILES may contain multiple fragments separated by dots. Substructure matching will search across the entire molecule; no special handling is needed unless you require matching within a specific fragment.
- Input formatting mistakes
  - Swapping lines (SMARTS vs SMILES) or leaving leading/trailing whitespace can cause parsing failures. Always strip and validate.
- Parser failures
  - If parsing fails, do not continue. Report the error and request corrected inputs. Avoid silent fallbacks that change molecular identity.

## Success Criteria

- The tool produces exactly one line in the output file:
  - "Match: yes" if at least one substructure match is found.
  - "Match: no" otherwise.
- No additional lines or commentary are written to the output.

## Optional Script Usage

- Use scripts/smarts_match.py to run the workflow from command line:
  - Provide inputs directly: `--smiles <SMILES> --smarts <SMARTS>`
  - Or provide a two-line input file: `--input-file <path>`
  - Optionally force adding explicit hydrogens with `--force-addhs`.
  - Write the required result to a file with `--output <path>`.
