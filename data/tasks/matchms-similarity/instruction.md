# Spectral Similarity Task

Given an MSP file containing multiple mass spectrometry spectra in `/root/input.msp`, find the most similar pair of spectra using the `matchms` Python library with CosineGreedy algorithm.

Read all spectra from the MSP file, compute pairwise CosineGreedy similarity between all spectra, and identify the pair with the highest similarity.

Write result to `/root/output.txt`:
```
Most similar pair: {name1} and {name2}
Similarity: X.XXX
```

Round similarity to 3 decimal places.
