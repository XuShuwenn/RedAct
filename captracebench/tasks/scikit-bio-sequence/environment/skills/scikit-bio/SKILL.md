---
name: scikit-bio
description: "Count k-mers (subsequences of length k) in DNA sequences. Use when counting DNA k-mers, analyzing sequence composition, or computing k-mer frequency distributions."
---

# scikit-bio: DNA K-mer Counting

## Overview

Given a DNA sequence, count occurrences of all k-mers (subsequences of length k). Output k-mers with count > 0, sorted alphabetically.

## K-mer Counting

```python
from skbio import DNA

# Read DNA sequence from file
with open("/root/input.txt") as f:
    seq_str = f.read().strip()

# Create DNA sequence object
dna = DNA(seq_str)

# Count k-mers (k=3 for 3-mers)
kmers = dna.kmer_frequencies(k=3)

# Sort by k-mer alphabetically
for kmer in sorted(kmers.keys()):
    count = kmers[kmer]
    print(f"{kmer}: {count}")
```

## K-mer Frequencies

```python
# Get all k-mers of length k
kmers = dna.kmer_frequencies(k=3)

# Returns dict: {'AAA': 3, 'AAC': 1, ...}
# Each k-mer appears count times in sequence

# For overlapping k-mers (sliding window)
# Default behavior: overlapping counts

# Non-overlapping k-mers
# Not directly supported; use step parameter if available
```

## Output Format

For each k-mer with count > 0:
```
AXXXXXXXXXX: count
```

Sorted alphabetically by k-mer name.

```python
with open("/root/output.txt", "w") as f:
    for kmer in sorted(kmers.keys()):
        f.write(f"{kmer}: {kmers[kmer]}\n")
```

## Key Reference

- `DNA(sequence_string)` — Create DNA sequence object
- `dna.kmer_frequencies(k=N)` — Count all k-mers of length N
- `sorted(dict.keys())` — Get k-mers in alphabetical order
- Only k-mers with count > 0 are returned in the dict