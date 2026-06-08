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

## Output

To `/root/output.txt`:
```
Most similar pair: {name1} and {name2}
Similarity: X.XXX
```

Round similarity to 3 decimal places.

## Using matchms

```python
from matchms.importing import load_msp_file
spectra = list(load_msp_file("/root/input.msp"))
```

- Convert the loader result to a list before comparison so you can iterate over all unique pairs reliably.
- Inspect one loaded spectrum's metadata before choosing output labels; do not assume `.name` exists or is populated.
- Prefer the metadata label actually present in the MSP data, commonly `compound_name`, then `name`/`Name`, then a deterministic fallback such as `Spectrum_{i}`.
- If exact external identifiers matter, keep labels in a separate list instead of relying only on parsed `Spectrum` attributes.
- If you construct `matchms.Spectrum` objects manually, convert m/z and intensity values to typed NumPy arrays first rather than raw Python lists.

## Similarity Calculation

- Use `matchms.Similarity.CosineGreedy` algorithm
- For the small MSP files typical of this task, compare each unique unordered pair once with indexed iteration (`for i in range(len(spectra)): for j in range(i + 1, len(spectra))`) to avoid self-comparisons and duplicate work
- Before the full search, run `CosineGreedy().pair(reference, query)` on one sample pair and inspect the returned value; do not assume it is a plain float
- Extract the numeric similarity defensively from the pair result, handling cases such as an object with `.score`, a mapping/structured value like `result['score']`, tuple/list-like forms, or a scalar-like value, then normalize it to a plain `float` before comparing
- Track `best_score` and the corresponding best pair while scanning all pairs
- Compute similarity scores first, then map the winning spectra to display names from the inspected metadata fields
- After selecting the best pair, format the numeric similarity to 3 decimal places in the output

## Tips

- Handle multiple spectra in the MSP file and evaluate all unique pairs
- Do not rely on `.name` alone; inspect `spectrum.metadata` keys and use a fallback chain such as `compound_name`, then `name`/`Name`, then `Spectrum_{i}`
- Prefer the simplest complete pairwise search for small inputs rather than extra optimization complexity
- If the scoring call behaves unexpectedly, print or inspect one sample return value first to confirm its type and available fields before changing extraction logic
- Treat parser or library warnings about missing optional metadata separately from task logic; if spectra still load and pairwise similarity computes, continue and report the requested result
- After writing `/root/output.txt`, read it back and confirm it matches the required two-line format and rounds similarity to 3 decimal places
