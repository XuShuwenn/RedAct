---
name: matchms-similarity
description: "Find most similar spectrum pair in MSP file using CosineGreedy similarity algorithm from matchms library."
---

# Mass Spectrometry Spectral Similarity

## When to Use

- Find most similar spectrum pairs in MSP files
- Compute pairwise similarity using CosineGreedy
- Analyze mass spectrometry data

## Input

- `/root/input.msp`: MSP file with multiple spectra
- Inspect the MSP file first to confirm how many spectra it contains and what identifiers or names are available for reporting the final pair.

- Before coding the full comparison, confirm `/root/input.msp` exists and is readable so environment issues are separated from parsing or similarity logic.
- Read enough of the MSP file up front to identify the spectra to compare and the metadata fields available for labeling the final answer.

## Output

To `/root/output.txt`:
```
Most similar pair: {name1} and {name2}
Similarity: X.XXX
```

Round similarity to 3 decimal places.

- Build the result text only after the winning pair and numeric score are finalized.
- Write actual newline characters between the two required lines (not literal `\\n` text), e.g. a normal Python string with `\n` escapes.
- Keep `/root/output.txt` minimal and explicit: exactly the winning pair and the rounded similarity, with no extra diagnostic text in the final file.
- Prefer a single script that loads `/root/input.msp`, computes the best pair, and writes the final two-line result directly to `/root/output.txt` without extra intermediate artifacts.
- Before finishing, verify `/root/output.txt` exists and contains exactly the required two lines, not just a chat response or console print.
- After writing, read `/root/output.txt` back once to verify both the path and exact formatting before finishing.

## Using matchms

```python
from matchms import importing
loader = getattr(importing, "load_from_msp", None) or getattr(importing, "load_msp_file")
spectra = list(loader("/root/input.msp"))
```

- Convert the loader result to a list before comparison so you can iterate over all unique pairs reliably.

- Verify the exact MSP loader exposed by the installed `matchms.importing` module before proceeding; prefer the built-in MSP parser over manual parsing, and keep using the library's native cosine similarity implementation rather than custom scoring code.
- If loaded spectra do not retain the identifiers you need for reporting, parse the MSP text into records yourself and keep a parallel `labels` list under your own control while still using the resulting spectra for scoring.
- When manually parsing MSP text, split records on blank lines, capture the `Name:` field (and other needed identifiers) per record, and treat peak rows after `Num Peaks:` as that record's spectrum data.
- Inspect one loaded spectrum's metadata before choosing output labels; do not assume `.name` exists or is populated.
- If labels are unclear, use a tiny debug script to print one loaded spectrum's `metadata` dict (or just its keys) and confirm which MSP field the loader actually populated before finalizing the fallback chain.
- Prefer the metadata label actually present in the MSP data, commonly `compound_name`, then `name`/`Name`, then a deterministic fallback such as `Spectrum_{i}`.
- If exact external identifiers matter, keep labels in a separate list instead of relying only on parsed `Spectrum` attributes.
- Preserve source labels independently from the similarity loop: build a parallel `labels` list once from inspected metadata, then report `labels[i]`/`labels[j]` for the winning pair instead of re-deriving names afterward from possibly normalized objects.
- If you construct `matchms.Spectrum` objects manually, convert m/z and intensity values to typed NumPy arrays first rather than raw Python lists.
- Prefer explicit numeric NumPy dtypes when building spectra manually so downstream similarity calls receive library-native array inputs consistently.

## Similarity Calculation

- Use `matchms.Similarity.CosineGreedy` algorithm
- Keep the full pairwise-search script structure in place, but validate uncertain library behavior with one sample pair before running the complete scan.
- Once score extraction is confirmed on the probe pair, reuse the same extraction path for all remaining comparisons rather than inventing a separate full-run code path.
- For the small MSP files typical of this task, compare each unique unordered pair once with indexed iteration (`for i in range(len(spectra)): for j in range(i + 1, len(spectra))`) to avoid self-comparisons and duplicate work
- Before the full search, run `CosineGreedy().pair(reference, query)` on one sample pair and inspect the concrete return type and fields; do not assume it is a plain float
- Extract the numeric similarity defensively from the pair result in this order: named field/key such as `result['score']` when present, then an object attribute such as `.score`, then tuple/list-like forms, then a scalar-like value; normalize the chosen value to a plain `float` before comparing
- Track `best_score` and the corresponding best pair while scanning all pairs
- Keep the search logic and the labeling logic separate: identify the winning spectrum objects or indices from numeric scores first, then resolve their display names from metadata or the preserved `labels` list so naming fixes do not require recomputing similarities.
- Compute similarity scores first, then map the winning spectra to display names from the inspected metadata fields
- If the score is clearly correct but names look generic, empty, or wrong, keep the computed winning indices and score and fix only the presentation labels from metadata or the preserved `labels` list; do not rerun the full search just to repair reporting.
- After selecting the best pair, format the numeric similarity to 3 decimal places in the output

- Follow this order for reliability: (1) load all spectra, (2) inspect one sample `CosineGreedy().pair(...)` result and finalize one score-extraction path, (3) compute scores across all unique pairs and keep the winning indices or objects, (4) inspect metadata for the winning spectra, (5) resolve display labels with the fallback chain or preserved `labels` list, (6) write the final two-line output.
- Do not rank pairs until the score extraction is confirmed on that sample result; a misread field can silently choose the wrong best pair.
- When normalizing the pair result, convert the extracted score to `float` immediately before ranking so `best_score` comparisons do not depend on library-specific result types.
- Treat warnings about missing optional metadata such as `precursor_mz` as non-fatal unless they prevent spectra from loading or scoring; continue the pairwise search when spectra load and `CosineGreedy().pair(...)` returns usable results.
- Prefer one complete Python script that loads the MSP file, evaluates all unique pairs, tracks the best-scoring pair, and writes `/root/output.txt` in the required format rather than splitting the work across multiple partial steps.
- During development, print or inspect pair labels and normalized scores while scanning pairs as a lightweight check to confirm winner updates before writing the final output.
- After any fix to score handling, rerun the full script end-to-end to confirm the best pair selection and final formatted output still work.

## Tips

- Handle multiple spectra in the MSP file and evaluate all unique pairs
- Do not rely on `.name` alone; inspect `spectrum.metadata` keys and use a fallback chain such as `compound_name`, then `name`/`Name`, then `Spectrum_{i}`
- Prefer the simplest complete pairwise search for small inputs rather than extra optimization complexity
- If the scoring call behaves unexpectedly, inspect one sample return value first—ideally in a tiny debug script—to confirm its type, shape, and score-bearing fields before changing extraction logic; when a structured result exposes a `score` field, use that field directly instead of casting the whole result.
- If an indexing attempt fails, read the traceback before guessing; use it to decide whether the score is scalar-like, tuple-like, field-based, or a NumPy structured value that should be inspected via `dtype` and field names.
- Treat parser or library warnings about missing optional metadata separately from task logic; if spectra still load and `CosineGreedy().pair()` returns usable scores, focus on real exceptions or tracebacks rather than debugging the warnings.
- Distinguish warnings from failures: only stop for true blocking errors such as load failures, exceptions during scoring, or an unusable sample `pair()` result after inspection.
- After writing `/root/output.txt`, read it back and confirm it matches the required two-line format and rounds similarity to 3 decimal places

- If the numeric winner is clear but identifiers look wrong, generic, or inconsistent, keep the computed best pair and inspect only the winning spectra's metadata-to-label mapping before writing `/root/output.txt`; do not rerun the similarity search just to fix presentation.
- Keep the exhaustive unique-pair search as the default workflow for this task type; it is the most reliable way to identify the true best match on small MSP inputs.
- When debugging, separate analysis from presentation: first identify the winning spectrum indices by score, then resolve those indices to output labels from inspected metadata or a preserved `labels` list.
- Confirm success from `/root/output.txt`, not terminal noise alone: read the file back and ensure it exists at the correct path, contains the best-pair labels, and has a similarity rounded to 3 decimal places in the required two-line format.
- Focus debugging on failures that block loading, scoring, or output formatting; do not let repeated non-fatal warnings distract from verifying the actual similarity result structure.
- Treat the work as three explicit phases: preflight input access, compute the best-scoring pair, then format and write the exact two-line output.


## Execution Checklist

## Execution Checklist

- Load all spectra from `/root/input.msp` into a list, then inspect available metadata keys or values on at least one loaded spectrum before deciding output labels.
- Score every unique unordered pair with `CosineGreedy`, convert each result to a plain float score using the same verified extraction rule, and keep the highest-scoring pair.
- Only after finding the best-scoring spectra, resolve their display names using the inspected metadata fallback chain or a preserved parallel `labels` list.
- Write the final two-line result to `/root/output.txt`, then read the file back and confirm the labels and 3-decimal similarity formatting are correct.
