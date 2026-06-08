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


- Read `/root/input.txt` before computing anything, and apply `.strip()` so surrounding whitespace or trailing newlines do not affect the sequence.

## K-mer Counting

- k = 3 (3-mers)
- Count all possible 3-mer combinations
- Only output k-mers with count > 0
- Sort alphabetically by k-mer


- Generate overlapping 3-mers across the full sequence.
- Prefer `DNA(...).kmer_frequencies(k=3)` over manual sliding-window counting when using scikit-bio.
- Only report observed k-mers with count > 0, and sort the reported k-mers alphabetically before writing.

## Output Format

To `/root/output.txt`:
```
AXXXXXXXXXX: count
```

One line per k-mer, sorted alphabetically.


- Write results directly to `/root/output.txt` in exact `KMER: count` format, one entry per line.
- Enforce output constraints while writing: include only 3-mers with count > 0 and sort k-mers alphabetically.
- After writing, read `/root/output.txt` back once to verify formatting and alphabetical order.

## Using scikit-bio

```python
from skbio import DNA
from skbio.sequence import KmerGenerator

# Generate and count kmers
```

## K-mers

64 possible 3-mers: AAA, AAC, AAG, AAT, ACA, ..., TTG, TTT

## Tips

- Use `skbio.DNA` for sequence handling.
- Prefer `DNA(sequence).kmer_frequencies(k=3)` over `KmerGenerator` or a purely manual implementation.
- Prefer one short script that reads `/root/input.txt`, counts 3-mers, and writes `/root/output.txt`.
- When writing output, iterate over `sorted(counts)` and emit only observed/nonzero k-mers as `KMER: count`.
- After running the script, confirm `/root/output.txt` exists and sanity-check its contents against the input sequence.
