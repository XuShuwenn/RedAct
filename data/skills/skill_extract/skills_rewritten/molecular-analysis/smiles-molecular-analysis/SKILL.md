---
name: smiles-molecular-analysis
description: "Analyze a molecule from a SMILES string to compute average molecular weight, detect common functional groups, and count total hydrogens with strict output formatting."
---

# SMILES-Based Molecular Analysis

This skill provides a reliable workflow to analyze a molecule from a SMILES string and produce three results with strict formatting: molecular weight (average atomic weights), functional groups (from a specified list), and total hydrogen count (explicit + implicit).

Use this when you need to:
- Parse a SMILES string and compute molecular properties
- Identify common functional groups from a fixed vocabulary
- Produce exactly formatted results suitable for automated graders

## When to Use

Activate this skill when the task requires any combination of:
- Molecular weight (average isotopic mass) from a SMILES
- Functional group detection among: carboxylic acid, ester, amide, ketone, aldehyde, alcohol, ether, amine, nitro, halide
- Total hydrogen count including both explicit and implicit hydrogens
- Writing results in an exact three-line format with proper rounding and sorting

## Core Workflow

1. Input handling
   - Read the SMILES string from the designated source (file or argument).
   - Trim whitespace and validate the input is non-empty.

2. Parse the molecule
   - Use a cheminformatics toolkit (e.g., RDKit) to parse and sanitize the SMILES.
   - If parsing fails, report the error and stop; do not guess.
   - If the SMILES contains multiple disconnected fragments ("."), decide per task whether to analyze the whole input or just the largest organic fragment. Default approach: analyze the whole input unless the task specifies otherwise.

3. Molecular weight (average mass)
   - Compute the molecular weight using a library function that returns the average (isotopic) molecular weight, not the exact/monoisotopic mass.
   - Round to two decimal places and format with exactly two decimals (e.g., 123.40), then append " g/mol".

4. Hydrogen count (explicit + implicit)
   - Create a copy of the molecule with all implicit hydrogens made explicit (e.g., AddHs in RDKit).
   - Count the number of hydrogen atoms explicitly present in this hydrogenated copy.

5. Functional group detection
   - Search for the following groups using robust SMARTS patterns and substructure matching:
     - carboxylic acid
     - ester
     - amide
     - ketone
     - aldehyde
     - alcohol
     - ether
     - amine (exclude amide nitrogens)
     - nitro (cover both charged and resonance forms)
     - halide (halogen bound to carbon)
   - Deduplicate, map to the canonical names listed above, and sort alphabetically.
   - If no groups are found, output "None".

6. Output formatting
   - Write exactly three lines in this order:
     - Molecular weight: {value} g/mol
     - Functional groups: {comma-separated list in alphabetical order or "None"}
     - Hydrogen count: {integer}
   - Ensure exact capitalization, punctuation, and spacing.

## Verification

Perform these checks before finalizing:
- Molecular weight
  - Confirm you used average molecular weight (e.g., RDKit Descriptors.MolWt) and not exact/monoisotopic mass.
  - Verify formatting to two decimals using fixed-point formatting, not string rounding that may drop trailing zeros.
- Hydrogen count
  - Cross-check two ways if possible:
    1) Count H atoms after adding explicit hydrogens; 2) Sum hydrogens attached to heavy atoms (tool-dependent function). Results must match.
- Functional groups
  - Ensure names come only from the specified list and are alphabetized.
  - Confirm patterns do not overcount overlapping groups (e.g., don’t classify a carboxylic acid as an ester).
- Output
  - Exactly three lines, no extra commentary or blank lines.
  - Values are present and in the required units and formats.

## Common Pitfalls and How to Avoid Them

- Using exact/monoisotopic mass instead of average mass
  - Symptom: values differ by a few hundredths and fail rounding tests.
  - Fix: use the toolkit’s average molecular weight function; avoid manual sums with rounded atomic weights. If manual is unavoidable, use high-precision standard atomic weights and only round at the end.
- Dropping trailing zeros in molecular weight
  - Symptom: "123.4 g/mol" instead of "123.40 g/mol".
  - Fix: format with two decimals (e.g., f"{value:.2f}").
- Missing implicit hydrogens in the hydrogen count
  - Symptom: counts that ignore hydrogens on heteroatoms or aromatic carbons.
  - Fix: expand to explicit hydrogens and count H atoms.
- Misclassification of functional groups
  - Symptom: acids detected as esters, amides mistaken for amines, or nitro missed.
  - Fix: use discriminating SMARTS (ester requires non-hydroxyl O; amine excludes amide via !$(NC=O); nitro includes [N+](=O)[O-] forms).
- Unsorted or duplicate functional groups
  - Symptom: groups out of alphabetical order or repeated.
  - Fix: deduplicate via a set and sort alphabetically by name before output.
- Extra text or incorrect line order
  - Symptom: including molecule names, extra commentary, or reordering lines.
  - Fix: output exactly the three required lines in the specified order.

## Optional Script Usage

A helper script is provided to perform the entire analysis from a SMILES string using RDKit.

Examples:
- From an argument: `python scripts/smiles_analyzer.py --smiles "<SMILES>"`
- From stdin: `echo "<SMILES>" | python scripts/smiles_analyzer.py`
- Analyze only the largest fragment if multiple are present: add `--largest-fragment`

The script prints exactly the three required lines, ready to be written to the designated output file.
