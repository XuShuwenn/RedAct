---
name: scikit-bio-sequence
description: "Count DNA k-mer occurrences using scikit-bio library for genomic sequence analysis."
---

# DNA K-mer Counting with scikit-bio

## When to Use

- Count k-mer occurrences in DNA sequences
- Analyze genomic sequence composition
- Use scikit-bio for sequence analysis

- For this simple file-to-file sequence counting task, prefer one short standalone script over an interactive or multi-step workflow.
- In sandboxed or filesystem-constrained environments, quickly inspect `/root` first if needed to confirm `/root/input.txt` is present and `/root/output.txt` is the intended output path before running code.

## Input

- `/root/input.txt`: Single DNA sequence


- Read `/root/input.txt` before computing anything, and apply `.strip()` so surrounding whitespace or trailing newlines do not affect the sequence.

- Treat the stripped file contents as the full DNA sequence; do not infer, normalize, or alter bases beyond removing surrounding whitespace.
- Use the stripped sequence read from `/root/input.txt` as the direct input to `skbio.DNA(...)`; do not assume or hardcode sequence content.

## K-mer Counting

- k = 3 (3-mers)
- Count all possible 3-mer combinations
- Only output k-mers with count > 0
- Sort alphabetically by k-mer


- Generate overlapping 3-mers across the full sequence.
- Count overlapping 3-mers using either `DNA(...).kmer_frequencies(k=3)` or a direct sliding-window pass over the stripped sequence.
- Count every contiguous window `sequence[i:i+3]` for `i = 0 .. len(sequence)-3`; do not use non-overlapping chunks or skip repeated/shifted overlaps.
- Treat the task as counting integer occurrences of each overlapping 3-mer, not reporting normalized frequencies.
- If using `DNA(sequence).kmer_frequencies(k=3)`, convert the returned relative frequencies to exact occurrence counts using the total number of overlapping windows `(len(sequence) - 2)` before writing output.
- Sanity-check totals: for sequence length `n`, reported 3-mer counts should sum to `n - 2` when `n >= 3`; if the stripped sequence length is less than 3, write an empty `/root/output.txt`.
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

- Ensure each reported `count` is an integer occurrence total, not a normalized frequency or percentage.
- Use script/tool feedback only as a quick milestone check; rely on the contents read back from `/root/output.txt` as the final source of truth.
- After writing, reopen `/root/output.txt` and confirm exact `KMER: count` formatting, alphabetical order, and that only observed 3-mers are present; each line should match `^[A-Z]{3}: \d+$`.

## Using scikit-bio

```python
from skbio import DNA
from skbio.sequence import KmerGenerator

- Build the `DNA` object from the already-read, stripped string from `/root/input.txt`; keep file I/O separate from k-mer analysis logic.
- Implement the task as one short Python script that reads `/root/input.txt`, computes 3-mer counts, writes `/root/output.txt`, then reads the output back once to verify it.
- Keep emitted k-mers uppercase if needed and write lines by iterating over `sorted(counts)`.

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

- Keep the workflow linear: inspect/read and `.strip()` the input, compute 3-mer counts once, write sorted nonzero `KMER: count` lines, then reread the output to verify exact contents.
- Use either `DNA(sequence).kmer_frequencies(k=3)` or a simple overlapping sliding-window count; prefer the approach that makes exact 3-mer occurrence counts easiest to verify.
- Do not rely on console output or a successful script exit as final validation; use the contents read back from `/root/output.txt` as the source of truth.
