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
spectra = load_msp_file("input.msp")
```

## Similarity Calculation

- Use `matchms.Similarity.CosineGreedy` algorithm
- Compute pairwise similarity between all spectra
- Find pair with highest similarity score

## Tips

- Check spectrum names via .name attribute
- Handle multiple spectra in MSP file
- Use numpy for pairwise comparison optimization
