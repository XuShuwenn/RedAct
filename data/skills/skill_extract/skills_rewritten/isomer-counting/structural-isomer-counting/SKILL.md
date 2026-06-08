---
name: structural-isomer-counting
description: "Determine the number of constitutional isomers for simple molecular formulas by parsing, validating (via degree of unsaturation), and applying curated lookups for supported classes (e.g., small acyclic alkanes)."
---

# Structural (Constitutional) Isomer Counting

Reusable workflow to count constitutional isomers for simple molecular formulas. The skill emphasizes robust input parsing, formula validation via degree of unsaturation (DBE), and a conservative lookup strategy (e.g., acyclic alkanes) to avoid including stereoisomers.

## When to Use

Activate this skill when a task requires:
- counting structural (constitutional) isomers from a plain-text molecular formula
- writing the result in a strict output format (e.g., `Number of isomers: N`)
- excluding stereoisomers (E/Z, R/S) and focusing on connectivity differences only

## Core Workflow

1. Acquire Input
   - Read the molecular formula string from the provided input source.
   - Trim whitespace and normalize casing.

2. Parse and Normalize the Formula
   - Parse element symbols (uppercase letter + optional lowercase) and their integer counts (default 1 when omitted).
   - Build a dictionary of element counts (e.g., {"C": 4, "H": 10}).
   - Reject or flag malformed inputs (e.g., invalid symbols, negative counts, zero counts, or stray characters).

3. Validate Compound Class with DBE
   - Compute degree of unsaturation (DBE) to classify the formula and verify alkane compatibility:
     - Use DBE = 1 + 0.5 * (2*C + 2 + N - H - X), where X is the total count of halogens (F, Cl, Br, I). Oxygen and sulfur do not affect DBE.
     - For hydrocarbon alkanes (C,H only), DBE == 0 and H must equal 2*C + 2.
   - Only proceed to direct lookup if the formula falls within a supported class (e.g., CH-only, DBE == 0).

4. Apply Curated Lookup (Supported Class)
   - For acyclic alkanes C_n H_(2n+2), use a curated mapping from carbon count to the number of constitutional isomers (e.g., known values for small n).
   - If the carbon count is within the supported range, return the mapped count.

5. Decide on Unsupported Cases
   - If the formula is outside supported classes (e.g., DBE > 0, heteroatoms present, or carbon count outside lookup range), do not guess.
   - Options:
     - Ask for clarification or confirm the intended scope (e.g., acyclic hydrocarbons only).
     - If required to produce an output file only, follow task instructions for unsupported inputs (e.g., provide a clear unsupported note if allowed; otherwise seek clarification).

6. Format and Write Output
   - Ensure the output strictly matches the required format, typically: `Number of isomers: N`.
   - Avoid extra text, units, or additional lines if the task specifies a strict format.

## Verification

Before finalizing:
- Parsing Checks
  - Reconstruct and sanity-check: For CH-only, verify H == 2*C + 2 when DBE == 0.
  - DBE should be a non-negative integer or half-integer consistent with the formula (reject negative).
- Supported Class Check
  - Confirm that only C and H are present for alkane lookup.
  - Confirm DBE == 0 before using the alkane table.
  - Confirm the carbon count exists in the curated mapping.
- Output Format Check
  - Confirm the exact label and a single integer answer: `Number of isomers: N`.
  - Ensure no leading/trailing spaces or extra lines if the task demands strict formatting.

## Common Pitfalls

- Counting stereoisomers instead of constitutional isomers.
- Skipping DBE validation and applying alkane counts to alkenes/alkynes or heteroatom-containing formulas.
- Misparsing condensed formulas (e.g., failing to default counts to 1 when omitted) or accepting invalid symbols.
- Using an alkane lookup outside the supported carbon range.
- Assuming cyclic structures in an acyclic lookup or vice versa.
- Producing the wrong output format or including explanatory text when a strict single-line answer is required.
- Silent normalization errors (e.g., lower/uppercase mishandling) that change the meaning of the formula.

## Optional Script Usage

Use `scripts/chem_formula_utils.py` to:
- Parse formulas into element counts safely.
- Compute DBE with support for halogens and nitrogen (O/S ignored for DBE).
- Count constitutional isomers for acyclic alkanes using a curated mapping for small n.

Example CLI usage:
- `python scripts/chem_formula_utils.py --formula "C4H10"`
  - Prints element counts, DBE, classification, and the isomer count if supported.

## Success Criteria

- Input formula parsed without error and validated via DBE.
- If CH-only and DBE == 0 with supported carbon count, output the exact number using the curated mapping.
- Output matches the exact required format and contains only the final answer line.
- No stereoisomer counting is included; only constitutional isomers are considered.
