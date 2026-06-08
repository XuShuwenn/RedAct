---
name: file-scalar-compute
description: "Compute a single scalar (e.g., a dimensionless number) from parameters in an input file and write a strictly formatted, rounded result to an output file."
---

# File-Driven Scalar Computation

Use this skill to read a small set of parameters from an input file, compute a single scalar via a given formula, then write the result with exact formatting and rounding (e.g., computing a Nusselt number from h, k, D).

## When to Use

Activate this skill when the task specifies:
- reading named parameters from a file (often key-value lines)
- applying a simple algebraic formula to compute one scalar
- writing one formatted line to an output file with a specified rounding and text template

Examples: Nusselt number (h·D/k), Reynolds number (ρ·V·D/μ), or other one-line engineering metrics.

## Core Workflow

1. Read the input file
   - Default path is commonly `/root/input.txt` unless the task states otherwise.
   - Preserve the file content; do not assume ordering. Parse keys by name.

2. Parse required parameters
   - Accept common separators: `:`, `=`, or whitespace.
   - Ignore comments and blank lines.
   - Extract the first numeric token on each line (support integers, decimals, scientific notation).
   - Treat keys case-insensitively and normalize to a canonical form (e.g., lowercase).

3. Validate inputs
   - Presence: all required parameters exist.
   - Numeric: values parse as finite floats.
   - Domain checks: ensure denominators are nonzero; lengths and conductivities are positive where physically required; warn or stop on obviously invalid values.

4. Compute the scalar
   - Apply the formula exactly as specified by the task.
   - Use double precision floats. Avoid unnecessary unit conversions unless explicitly requested.

5. Round and format
   - Use string formatting to ensure the requested decimal places and avoid extra digits: `formatted = f"{value:.2f}"` or `"%.2f" % value`.
   - Do not include thousands separators or trailing spaces.

6. Write the output
   - Write exactly the required text line, including capitalization and punctuation.
   - Default path is commonly `/root/output.txt` unless otherwise specified.
   - Example template: `Noun: X.XX` (replace `Noun` and decimal places per task).

7. Verify
   - Re-open and read back `/root/output.txt`.
   - Check it matches the exact template (prefix text, colon, space, numeric with required decimals, newline).
   - Optionally, recompute the value and compare to the parsed output (within rounding tolerance) to catch formatting or calculation errors.

## Worked Pattern: Nusselt Number

- Inputs: h (convective coefficient), k (thermal conductivity), D (characteristic length)
- Formula: Nu = h × D / k
- Validation: k > 0, D > 0, h ≥ 0
- Output format: `Nusselt number: X.XX` (two decimals)

## Verification Checklist

- Parameters parsed correctly (names match, numeric values present)
- Denominator nonzero and physically valid
- Formula matches the task statement exactly
- Output line matches the exact required template
- Number has exactly the required number of decimal places
- Output file contains only the required line

## Common Pitfalls and How to Avoid Them

- Missing or misnamed parameters: parse by key name, not by line order. Fail fast if a required key is absent.
- Parsing noise (units/comments): extract only the first numeric token from each line; ignore trailing units and comments.
- Division by zero: check denominators explicitly before computing.
- Wrong rounding/formatting: use string formatting to enforce fixed decimal places; avoid printing raw floats.
- Extra text in output: write exactly the required line, no explanations or additional lines.
- Wrong paths: confirm read from the specified input file and write to the specified output file.

## Optional Script Usage

You can use the helper script to robustly parse key-value parameters from the input file and return JSON for downstream use.

Example:
- Parse required keys and inspect values:
  - `python scripts/kvfile.py --file /root/input.txt --key h --key k --key D`
- Programmatically consume JSON in your workflow, compute the scalar, then format and write the output.

Minimal formatting snippet for two decimals:
```
value_str = f"{value:.2f}"
```

Success criteria: the output file contains exactly one line with the correct label and a correctly rounded numeric value with the required decimal places.
