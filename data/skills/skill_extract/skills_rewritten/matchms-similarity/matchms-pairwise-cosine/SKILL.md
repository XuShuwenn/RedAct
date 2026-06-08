---
name: matchms-pairwise-cosine
description: "Load spectra from an MSP file and find the most similar pair using matchms CosineGreedy with robust score extraction and exact output formatting."
---

# Pairwise Spectral Similarity with matchms (CosineGreedy)

This skill computes pairwise similarity between mass spectra loaded from an MSP file using the matchms CosineGreedy algorithm and reports the most similar pair. It includes robust handling of different return types for similarity results and guidance for formatting the output consistently.

## When to Use

Use this skill when you need to:
- Read multiple spectra from an MSP file
- Compute pairwise similarities with matchms and the CosineGreedy measure
- Identify and report the most similar spectrum pair (top score) with a fixed numeric formatting

## Core Workflow

1. Load spectra
   - Use `matchms.importing.load_from_msp(path)` and immediately convert the generator to a list to avoid one-time iteration issues.
   - Optionally apply a basic filter pipeline (e.g., `default_filters`) if the spectra require cleaning. Keep it optional to avoid breaking when metadata are missing.

2. Prepare names
   - For each spectrum, determine a human-readable name from metadata (e.g., `name`, `compound_name`, `title`, `spectrum_id`). Fallback to an index-based label when missing.

3. Compute pairwise similarities
   - Instantiate `CosineGreedy()` with default parameters unless task specifies otherwise.
   - Iterate over unique pairs only (i.e., indices `i < j`) to avoid self-comparisons and duplicate comparisons.
   - Compute similarity for each pair via `CosineGreedy().pair(s1, s2)`.
   - Extract a numeric score robustly because different matchms versions may return different structures (e.g., float, tuple, or an object with a `.score` attribute). See the helper rules in the script or Verification section.

4. Track the best match
   - Maintain the highest numeric score and the corresponding spectrum pair.
   - Skip pairs with invalid/None/NaN scores.

5. Format and write output
   - Round the score to 3 decimal places and format as a fixed-width string (e.g., using `format(score, '.3f')`).
   - Write exactly two lines in the required format:
     - `Most similar pair: {name1} and {name2}`
     - `Similarity: X.XXX`

## Verification

Before finalizing, verify:
- Input validation
  - The MSP file exists and is readable.
  - At least two spectra loaded (`len(spectra) >= 2`).

- Pairing logic
  - No self-comparisons are included.
  - Each pair `(i, j)` is evaluated only once (use `for i in range(n): for j in range(i+1, n): ...`).

- Score extraction
  - Confirm the similarity result is converted to a numeric value:
    - If it is a float/int, use it directly.
    - If it has `score` or `value` attributes, use those.
    - If it is a tuple/list, take the first numeric element (commonly the score).
    - If it is a dict-like, try the `score` key.
    - As a last resort, attempt `float(result)`; otherwise treat as invalid.
  - Ensure the score is a finite number (not NaN or inf) and typically within [0, 1] for cosine-based measures.

- Output formatting
  - Score is rounded to exactly 3 decimal places.
  - Output lines match the required text and order exactly.
  - Names are present; if metadata are missing, fallback names are used consistently.

## Common Pitfalls

- Misinterpreting similarity return type
  - Some matchms versions return a structured object (e.g., with `.score`) or a tuple rather than a plain float. Always normalize to a float with a robust extractor.

- Forgetting to listify the spectra generator
  - `load_from_msp` returns a generator. If not converted to a list, you might unexpectedly exhaust it and end up with zero spectra for later steps.

- Including self-pairs or duplicate comparisons
  - Use unique pairs (`i < j`) to avoid inflating the best score with self-similarity or duplicate calculations.

- Missing spectrum names
  - Do not assume `metadata["name"]` is present. Fall back to alternative metadata keys or construct a deterministic index-based label.

- Incorrect rounding or output text
  - Always format the score to 3 decimal places and match the exact line text to satisfy downstream checks.

## Optional Script Usage

A ready-to-use helper script is provided.

Example usage:
- Compute most similar pair and write to an output file:
  - `python scripts/most_similar_msp.py --input path/to/input.msp --output path/to/output.txt`
- Dry run that prints the result to stdout without writing a file:
  - `python scripts/most_similar_msp.py --input path/to/input.msp`

Configuration notes:
- By default the script uses `CosineGreedy()` with default parameters.
- If needed, you can extend the script to apply filters or adjust CosineGreedy parameters.
