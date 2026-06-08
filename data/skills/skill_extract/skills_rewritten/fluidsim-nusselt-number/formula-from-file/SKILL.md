---
name: formula-from-file
description: "Calculate a scalar from parameters in an input file using a specified formula, then write a precisely formatted, rounded result to an output file."
---

# Compute a Formula Result from File Parameters

Use this skill when a task provides named parameters in a text file, specifies a mathematical formula to compute a single numeric result, and requires writing that result to an output file with exact formatting and rounding rules.

## When to Use

Activate this skill when the task:
- Points to an input file containing parameters (e.g., `h`, `k`, `D`) as key-value pairs.
- Specifies a formula (e.g., result = f(parameters)).
- Requires rounding to a fixed number of decimal places and an exact output line format.
- Requires writing to a specific output path with no extra commentary.

## Core Workflow

1. Extract Requirements
   - Identify: input file path, output file path, variable names, the exact formula, rounding precision (e.g., 2 decimals), and the required output label and format.
   - Note any constraints (e.g., units, valid ranges, division by zero avoidance).

2. Read the Input File
   - Open the specified input file in text mode.
   - If reading fails due to environment permissions or path issues, re-check the path and retry. Do not guess values.

3. Parse Parameters Robustly
   - Accept lines formatted like `key: value`, `key = value`, or `key value`.
   - Ignore comments and blank lines.
   - Parse the first numeric token in a value field; support integers, decimals, and scientific notation.
   - Treat parameter names case-insensitively and trim whitespace.
   - Validate: ensure all variables required by the formula are present and numeric.

4. Compute the Formula Safely
   - Use floating-point or decimal arithmetic; prefer decimal for deterministic rounding.
   - Ensure non-integer division (i.e., avoid integer truncation).
   - Guard against division by zero and other invalid operations; provide a clear error if encountered.

5. Apply Rounding Rules
   - Round to the exact number of decimal places specified by the task (commonly 2).
   - Preserve trailing zeros (e.g., show `X.00` if required) so the output matches the exact format.

6. Format the Output Exactly
   - Construct exactly the required line, including label, colon, single space, the rounded number, and a terminating newline.
   - Do not include extra lines or commentary.

7. Write and Verify
   - Write the single formatted line to the specified output file path.
   - Re-open the output file and verify:
     - The content matches the required label and formatting.
     - The number of decimal places is correct.
     - There are no extra lines or spaces.

## Verification

Before finalizing, confirm all of the following:
- Inputs parsed: each required variable is present and numeric.
- Computation: matches the stated formula exactly; parentheses applied as needed.
- Rounding: correct number of decimal places; trailing zeros present when required.
- Output format: exactly `Label: X.YY` (or the label/precision specified), followed by a newline, and nothing else.
- File paths: wrote to the exact output path specified by the task.

Optional automated checks:
- Recompute the value from the parsed inputs and compare the formatted string to the file content.
- Validate the output with a regular expression like `^Label: -?\d+(?:\.\d{N})?$` where `N` is the required decimal count and `Label` is task-specified.

## Common Pitfalls and How to Avoid Them

- Missing or misnamed parameters: cross-check required variable names against the formula; handle case-insensitively.
- Unit text in values: strip units and parse only the numeric part of the value.
- Integer division: ensure division yields a floating/decimal result, not truncated integers.
- Division by zero: explicitly check denominators and fail gracefully if zero.
- Rounding inconsistencies: binary floating-point can produce unexpected rounding; use decimal-based rounding to an exact precision.
- Wrong output label or spacing: match the label and punctuation exactly (including colon and spaces).
- Extra output: do not add explanations or multiple lines to the output file.
- Missing trailing newline: many tasks require a newline at the end of the file; include it.
- Not verifying the write: always re-open the output file to confirm exact content.

## Optional Script Usage

You can use the helper script to compute a formula from a parameter file with strict parsing, safe evaluation, decimal rounding, and exact output formatting.

Example usage pattern (replace paths, label, expression, and precision as required by the task):

- Compute from file and write formatted result:
  - python scripts/compute_from_file.py --input path/to/input.txt --output path/to/output.txt --expr "h * D / k" --label "Nusselt number" --round 2

- Dry-run to see parsed variables and computed value without writing:
  - python scripts/compute_from_file.py --input path/to/input.txt --expr "h * D / k" --round 2 --dry-run

Success criteria: the output file contains exactly one line with the correct label and a number rounded to the specified decimals, followed by a newline, matching a recomputation from the parsed inputs.
