---
name: structural-isomer-counting
description: "Count constitutional isomers from a molecular formula, with a fast path for small acyclic alkanes and strict output formatting."
---

# Structural Isomer Counting

Reusable workflow to determine the number of constitutional (structural) isomers given a molecular formula, write the exact required output line, and avoid common scope and formatting mistakes.

## When to Use

Activate this skill when:
- the user provides a molecular formula and asks for the count of structural (constitutional) isomers
- stereochemistry should be ignored (no stereoisomer counting)
- the output must be exactly: `Number of isomers: <count>`

## Core Workflow

1. Read and Normalize Input
   - Read the formula string from the designated input file.
   - Strip whitespace and normalize case (element symbols are case-sensitive, but overall spacing is not).

2. Parse the Formula
   - Tokenize into element/count pairs (e.g., C4H10 → {C:4, H:10}).
   - Default missing counts to 1 (e.g., "CH4" means C:1, H:4).
   - Validate: counts must be positive integers.

3. Assess Saturation via Index of Hydrogen Deficiency (IHD/DBE)
   - Use DBE = (2C + 2 + N − H − X) / 2, where X is the total count of halogens (F, Cl, Br, I). Oxygen (and sulfur) do not affect DBE.
   - If DBE < 0 or not an integer, treat as outside scope or malformed input.

4. Fast Path (Acyclic Alkanes Only)
   - If the formula contains only C and H and DBE == 0, the compound family is an acyclic alkane (CnH2n+2).
   - Use a known mapping for small n (number of carbons) to the count of constitutional isomers. A reference sequence is well-established for alkanes and can be embedded for quick answers. The provided helper script includes counts for small n.
   - If n is beyond the embedded mapping, either expand the mapping via a trusted reference or fall back to tool-based enumeration.

5. General Case (Beyond Acyclic Alkanes)
   - If DBE > 0 or heteroatoms are present, counting structural isomers becomes significantly more complex (rings, multiple bonds, functional groups).
   - Prefer a cheminformatics approach (e.g., graph generation with canonical deduplication using libraries such as RDKit) or consult curated references/tables. Do not guess.

6. Write Output in Exact Format
   - Create the file at the required path and write exactly one line:
     - `Number of isomers: <count>`
   - No extra commentary, labels, or additional lines.

## Verification

Before finalizing:
- Formula parsing
  - Confirm elements and integer counts were parsed correctly. Missing counts default to 1.
  - Ensure DBE is a nonnegative integer for valid closed-shell formulas.
- Scope check
  - If using the fast path, ensure the formula is strictly C/H and DBE == 0.
- Result check
  - For fast path, confirm the carbon count exists in the mapping. If not, switch to a supported method or report unsupported rather than guessing.
- Output format
  - Verify the output file contains exactly: `Number of isomers: <integer>` with a trailing newline.
  - No extra text, symbols, or units.

## Common Pitfalls

- Counting the wrong thing
  - Including stereoisomers (E/Z, R/S) or conformers; only constitutional isomers count.
- Misusing DBE
  - Forgetting halogens count like hydrogens (as X), or mistakenly including oxygen/sulfur in the DBE formula.
  - Proceeding with a non-integer/negative DBE without checking for input validity.
- Overgeneralizing the fast path
  - Applying alkane counts to formulas with DBE > 0 or with heteroatoms.
- Parsing mistakes
  - Not defaulting empty counts to 1.
  - Case errors on element symbols (e.g., "CL" vs "Cl").
- Output errors
  - Adding annotations or multiple lines; using a different label text; missing the newline.

## Optional Script Usage

Use the helper to parse formulas, compute DBE, and return counts for small acyclic alkanes.

- Fast path (alkanes):
  - `python scripts/isomer_counter.py --formula "C<integer>H<integer>"`
  - Prints `Number of isomers: <count>` if supported.
- If unsupported (e.g., DBE > 0 or elements beyond C/H), the script reports the condition so you can switch to a cheminformatics enumeration or a curated reference.

Success Criteria:
- The final output file exists and contains exactly one line: `Number of isomers: <count>` matching the structural isomer count under the problem's scope.
