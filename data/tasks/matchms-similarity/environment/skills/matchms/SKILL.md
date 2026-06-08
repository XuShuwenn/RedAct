---
name: matchms
description: "Find the most similar spectral pair from MSP files using CosineGreedy similarity. Use when comparing multiple mass spectra, computing pairwise similarity matrices, or identifying best matches in metabolomics."
---

# Matchms: Find Most Similar Spectral Pair

## Overview

Given an MSP file with multiple spectra, find the pair with the highest CosineGreedy similarity score.

## Loading MSP Files with Multiple Spectra

```python
from matchms.importing import load_from_msp

def load_all_spectra(filepath):
    """Load all spectra from an MSP file."""
    return list(load_from_msp(filepath))
```

## Computing Pairwise Similarities

```python
from matchms.similarity import CosineGreedy
from matchms.importing import load_from_msp

# Load all spectra
spectra = load_all_spectra("/root/input.msp")

# Compute pairwise similarities
cosine_greedy = CosineGreedy(tolerance=0.1)

best_pair = None
best_score = -1

for i in range(len(spectra)):
    for j in range(i + 1, len(spectra)):
        score = cosine_greedy.pair(spectra[i], spectra[j])
        if score > best_score:
            best_score = score
            best_pair = (spectra[i].get("compound_name", spectra[i].get("name", f"Spectrum_{i}")),
                        spectra[j].get("compound_name", spectra[j].get("name", f"Spectrum_{j}")))

# Write result
with open("/root/output.txt", "w") as f:
    f.write(f"Most similar pair: {best_pair[0]} and {best_pair[1]}\n")
    f.write(f"Similarity: {best_score:.3f}\n")
```

## Complete Script

```python
from matchms.importing import load_from_msp
from matchms.similarity import CosineGreedy

# Load all spectra from MSP file
spectra = list(load_from_msp("/root/input.msp"))

# Initialize similarity calculator
cosine_greedy = CosineGreedy(tolerance=0.1)

# Find most similar pair
best_score = -1
best_pair = (None, None)

for i in range(len(spectra)):
    for j in range(i + 1, len(spectra)):
        score = cosine_greedy.pair(spectra[i], spectra[j])
        if score > best_score:
            best_score = score
            name_i = spectra[i].get("compound_name", spectra[i].get("name", f"Spectrum_{i}"))
            name_j = spectra[j].get("compound_name", spectra[j].get("name", f"Spectrum_{j}"))
            best_pair = (name_i, name_j)

# Write result
with open("/root/output.txt", "w") as f:
    f.write(f"Most similar pair: {best_pair[0]} and {best_pair[1]}\n")
    f.write(f"Similarity: {best_score:.3f}\n")
```

## Output Format

```
Most similar pair: {name1} and {name2}
Similarity: X.XXX
```

## Key Reference

- `load_from_msp(filepath)` — Load all spectra from MSP file
- `CosineGreedy(tolerance=0.1)` — Create similarity calculator (tolerance in m/z)
- `cosine_greedy.pair(spec1, spec2)` — Compute similarity between two spectra
- `spectrum.get("compound_name")` — Get spectrum name from MSP Name: field (matchms stores it as 'compound_name')
