---
name: scikit-bio-sequence
description: "Count DNA k-mer occurrences using scikit-bio library for genomic sequence analysis."
---

# DNA K-mer Counting with scikit-bio

## When to Use

- Count k-mer occurrences in DNA sequences
- Analyze genomic sequence composition
- Use scikit-bio for sequence analysis

## Input

- `/root/input.txt`: Single DNA sequence

## K-mer Counting

- k = 3 (3-mers)
- Count all possible 3-mer combinations
- Only output k-mers with count > 0
- Sort alphabetically by k-mer

## Output Format

To `/root/output.txt`:
```
AXXXXXXXXXX: count
```

One line per k-mer, sorted alphabetically.

## Using scikit-bio

```python
from skbio import DNA
from skbio.sequence import KmerGenerator

# Generate and count kmers
```

## K-mers

64 possible 3-mers: AAA, AAC, AAG, AAT, ACA, ..., TTG, TTT

## Tips

- Use skbio.DNA for sequence handling
- KmerGenerator or manual sliding window
- Count occurrences and filter > 0
- Sort output alphabetically
