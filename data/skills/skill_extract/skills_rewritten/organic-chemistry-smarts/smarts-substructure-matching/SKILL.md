---
name: smarts-substructure-matching
description: "Check if a SMARTS pattern occurs in a SMILES molecule using RDKit and emit a yes/no match."
---

# SMARTS Substructure Matching

Use this skill to determine whether a molecule (given as a SMILES string) contains a functional group or substructure defined by a SMARTS pattern. It standardizes the matching workflow, handles common RDKit pitfalls (sanitization, explicit hydrogens, chirality), and produces a deterministic yes/no result.

## When to Use

Activate this skill when:
- You are given a SMILES string and a SMARTS pattern and must answer if the pattern is present in the molecule.
- You need a robust, minimal-output check suitable for automated grading or pipelines that expect "Match: yes" or "Match: no".

## Core Workflow

1. Parse input
   - Expect two non-empty lines:
     - Line 1: SMILES string
     - Line 2: SMARTS pattern
   - Trim whitespace and ignore empty lines beyond the first two.

2. Build RDKit objects
   - Create an RDKit Mol from the SMILES with sanitization:
     - Use `Chem.MolFromSmiles(smiles, sanitize=True)`.
     - If that fails, retry with `sanitize=False`, then attempt `Chem.SanitizeMol(mol)`. Proceed only if a Mol is obtained.
   - Create the SMARTS query with `Chem.MolFromSmarts(smarts)`. If this returns `None`, the pattern is invalid.

3. Decide on explicit hydrogens
   - SMARTS that specify hydrogen atoms explicitly (e.g., `[H]` or `[#1]`) require explicit Hs on the molecule to match.
   - Rule of thumb:
     - If SMARTS contains `[H` or `[#1`, add explicit Hs to the molecule via `Chem.AddHs(mol)` before matching.
     - SMARTS using hydrogen count properties like `[NH]` or `H1` do not require explicit Hs; they match implicit hydrogens.
   - Allow an override to force explicit Hs on/off when needed.

4. Perform the match
   - Use `mol.HasSubstructMatch(query, useChirality=...)`.
   - Default to `useChirality=False` unless the task explicitly requires stereospecific matching. Provide a flag to enable.

5. Output exactly
   - Write a single line: `Match: yes` if any match is found, otherwise `Match: no`.
   - Do not include extra commentary or additional lines in the output artifact intended for grading.

## Verification

- Sanity checks before matching:
  - Ensure both SMILES and SMARTS are non-empty.
  - Ensure `mol` and `query` are not `None`.
- Quick functional tests (conceptual, not tied to any particular task input):
  - A simple pattern like an aliphatic carbon `C` should match most organic SMILES with carbons.
  - A hydroxyl pattern `[OX2H]` should match alcohols; it relies on implicit Hs and should not require explicit Hs.
  - A pattern with explicit hydrogen `[H]O` requires adding explicit Hs; verify that toggling explicit hydrogens affects the result as expected.
- Confirm that output contains exactly two tokens separated by a colon and space ("Match: yes/no").

## Common Pitfalls

- Invalid inputs:
  - Malformed SMILES or SMARTS yield `None` from RDKit constructors. Handle gracefully and, if a strict failure mode is not allowed, return `Match: no` while logging the error to stderr.
- Missing sanitization:
  - Without sanitization, aromaticity and valence information may be incomplete, causing aromatic SMARTS (e.g., `a`) to fail. Prefer sanitized molecules; only proceed unsanitized if necessary and accepted.
- Explicit hydrogens:
  - SMARTS with explicit hydrogen atoms (`[H]` or `[#1]`) will not match a molecule that only has implicit hydrogens unless you add explicit Hs with `Chem.AddHs`.
  - Do not add explicit Hs indiscriminately; it can change matching behavior for some patterns and slow down matching.
- Chirality and stereochemistry:
  - If the pattern encodes stereochemistry and you do not enable `useChirality`, matches may be missed. Conversely, enabling chirality can cause expected non-stereospecific matches to fail. Choose the flag based on task requirements.
- Whitespace and extra lines:
  - Leading/trailing spaces or blank lines can break parsing. Strip input lines and ignore empties.
- Extra output:
  - Any additional text in the graded output file can cause failures. Keep the result file to exactly the required line.

## Success Criteria

- The output file contains exactly one line in the form: `Match: yes` or `Match: no`.
- Matching accounts for explicit H requirements and (optionally) chirality as dictated by the pattern and task.
- Invalid inputs are handled deterministically in the configured mode (soft-fail to `no` with stderr logging, or strict failure).

## Optional Script Usage

Use the helper script to perform matching in a reproducible way.

- Basic usage:
  - `python scripts/smarts_match.py --input input.txt --output output.txt`
- Options:
  - `--use-chirality` to require stereochemical consistency in matching.
  - `--explicit-hs {auto,yes,no}` to control explicit hydrogen handling (default `auto`).
  - `--strict` to exit with a non-zero code on parse errors instead of soft-failing to `Match: no`.

Input file format expected by the script:
- Line 1: SMILES
- Line 2: SMARTS

The script will write exactly one line to the specified output file: `Match: yes` or `Match: no`.
