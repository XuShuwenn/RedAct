---
name: spectral-pair-similarity
description: "Find the most similar pair of spectra from an MSP file using matchms CosineGreedy and write a two-line, rounded report."
---

# Spectral Pair Similarity with matchms (CosineGreedy)

Compute pairwise spectral similarity from an MSP file using `matchms` and identify the most similar spectrum pair. This skill emphasizes robust handling of similarity return types and metadata name keys.

## When to Use

Use this skill when:
- Given an MSP file and asked to find the most similar spectra.
- Required to use `matchms` with `CosineGreedy` similarity.
- You must output the best pair and a similarity score rounded to 3 decimals.

## Core Workflow

1. Load spectra from MSP:
   - `from matchms.importing import load_from_msp`
   - `spectra = list(load_from_msp(<input_path>))`
   - Guard: If fewer than 2 spectra, stop and report an error.

2. Configure similarity:
   - Instantiate `CosineGreedy`, e.g., `CosineGreedy(tolerance=0.1)`.
   - Keep tolerance configurable; start with a reasonable default if unspecified.

3. Compute pairwise scores:
   - Iterate unique pairs with indices `i < j` to avoid duplicates.
   - For each pair, call `cg.pair(spectra[i], spectra[j])`.
   - Extract the numeric score robustly (see Score Extraction below).

4. Track the best:
   - Maintain `best_score` and `best_pair` (names/labels for the spectra).
   - For labels, try these metadata keys in order: `compound_name`, then `name`, then a deterministic fallback like `Spectrum_{index}`.

5. Format result:
   - Round the final score to 3 decimals.
   - Write exactly two lines to the output file:
     - `Most similar pair: {name1} and {name2}`
     - `Similarity: X.XXX`

## Score Extraction (Robust to matchms Variations)

`CosineGreedy.pair(a, b)` may return different shapes depending on version:
- A float-like numeric
- A tuple-like value where the first element is the score (e.g., `(score, matches)`)
- An object with attribute `.score`
- A mapping containing `"score"`
- A 0-D numpy array holding a tuple

Use this robust procedure:
- If it is a numpy scalar (ndim == 0): `val = res.item()` and then extract as below.
- If it has attribute `score`: use `float(res.score)`.
- If it is a tuple or sequence: use `float(res[0])`.
- If it is a mapping and contains `"score"`: use `float(res['score'])`.
- Else, try `float(res)`.

## Verification

Before finalizing:
- Ensure at least 2 spectra were loaded.
- Confirm the best score is within [0, 1] for cosine-like metrics.
- Confirm both names are non-empty strings.
- Confirm output contains exactly two lines and the score is rounded to 3 decimals.
- Optionally re-evaluate the winning pair to confirm the stored score matches the recomputed value within 1e-6.

## Common Pitfalls and How to Avoid Them

- Pitfall: Using the wrong metadata key for names (e.g., assuming `name`).
  - Fix: Check `compound_name` first, then `name`, then fallback label.

- Pitfall: Crashing due to unexpected return type from `CosineGreedy.pair`.
  - Fix: Implement the robust score extraction method described above.

- Pitfall: Evaluating duplicate or self-pairs.
  - Fix: Iterate pairs with `for i in range(n): for j in range(i+1, n): ...` only.

- Pitfall: Forgetting to round to 3 decimals or deviating from the required two-line format.
  - Fix: Use formatted printing `f"{score:.3f}"` and verify file contents after writing.

- Pitfall: Proceeding with fewer than 2 spectra.
  - Fix: Validate count and fail early with a clear message.

## Optional Script Usage

A helper script is provided to run the workflow from the command line:
- Example: `python scripts/msp_most_similar.py --input input.msp --output output.txt --tolerance 0.1`
- It implements the robust score extraction and name retrieval, and writes the two-line report.
