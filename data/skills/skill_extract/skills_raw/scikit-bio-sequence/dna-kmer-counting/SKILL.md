---
name: dna-kmer-counting
description: "Count overlapping DNA k-mers using scikit-bio and output alphabetically sorted counts."
---

# DNA k-mer Counting with scikit-bio

Reusable workflow for counting overlapping DNA k-mers with the scikit-bio library and writing alphabetically sorted counts. Use this when a task asks for k-mer frequency counts from a DNA sequence, requires overlapping windows, and specifies a strict output format (e.g., one line per observed k-mer like `KMER: count`).

## When to Use

Activate this skill when the user asks you to:
- Count k-mer occurrences in a DNA sequence (typically overlapping windows)
- Use scikit-bio to process the sequence
- Produce counts for each observed k-mer, sorted lexicographically
- Exclude zero-count k-mers from the output

## Core Workflow

1. Read input sequence
   - Load the DNA sequence from the specified input path (or stdin).
   - Join lines and strip whitespace. Uppercase the sequence.
   - Convert any `U` to `T` if present.
   - Validate characters against the IUPAC DNA alphabet (A, C, G, T, and ambiguous codes RYSWKMBDHVN). If invalid symbols are present, either stop with a clear error or sanitize per task instructions.

2. Decide k and ambiguity handling
   - Ensure `1 <= k <= len(sequence)`. If `k` is larger than the sequence length, the result is empty.
   - Clarify whether to include k-mers with ambiguous bases. If not specified, a safe default is to exclude k-mers containing characters outside A, C, G, T.

3. Generate overlapping k-mers using scikit-bio
   - Create a `skbio.DNA` object from the sequence.
   - Iterate overlapping k-mers using `DNA.iter_kmers(k)` to obtain all sliding windows of length k.
   - If ambiguity is excluded, skip any k-mer that contains characters beyond A/C/G/T.

4. Count and sort
   - Use a counter/dictionary to tally k-mer occurrences.
   - Sort the k-mers alphabetically (lexicographic order) by the k-mer string.

5. Output formatting
   - Write one line per observed k-mer in the exact format required, e.g., `KMER: count`.
   - Include only k-mers with count > 0.
   - Write to the path specified by the prompt.

## Verification

Before finalizing output, perform these checks:
- Overlap check: The total number of overlapping windows is `max(len(seq) - k + 1, 0)`. If you exclude ambiguous windows, the sum of counts must equal this total minus the number of skipped windows.
- Sort check: Confirm the output is sorted lexicographically by the k-mer string (not by count).
- Inclusion check: Ensure no zero-count k-mers are present in the output; only observed k-mers should be written.
- Character normalization: Confirm the sequence was uppercased and any `U` was converted to `T`.
- Library usage: Confirm scikit-bio is used for k-mer iteration or sequence handling to meet the requirement.

## Common Pitfalls and How to Avoid Them

- Non-overlapping windows: Counting k-mers in steps of k instead of sliding by 1 will undercount. Always use overlapping windows for standard k-mer counting.
- Wrong sort key: Sorting by count or mixed criteria instead of by k-mer string. Always sort alphabetically by the k-mer token.
- Case sensitivity and whitespace: Forgetting to uppercase or strip newlines/whitespace leads to mismatches. Normalize early.
- Ambiguity handling: Including k-mers with ambiguous characters when the task expects only A/C/G/T (or vice versa). Decide and document ambiguity policy; if excluding, filter k-mers containing non-ACGT characters.
- Off-by-one at edges: Missing the last possible k-mer window (`len(seq) - k + 1` windows). Use an iterator that enforces correct windowing.
- Using relative frequencies: Some APIs can return relative frequencies; ensure you collect raw counts when counts are requested.
- Library omission: If the task explicitly requires scikit-bio, instantiate a `DNA` object and iterate k-mers via scikit-bio, even if you also implement a fallback.

## Success Criteria

- Uses scikit-bio to process the DNA sequence and/or iterate k-mers.
- Counts overlapping k-mers of the requested k.
- Outputs only observed k-mers with counts > 0.
- Lines are sorted lexicographically by k-mer string.
- Output format matches the exact pattern requested (e.g., `KMER: count`).

## Optional Script Usage

A helper script is provided to perform robust k-mer counting and optional verification.

Example:
- Count 3-mers, exclude ambiguous k-mers, write to an output file:
  - `python scripts/kmer_count.py --input input.txt --output output.txt --k 3 --exclude-ambiguous`
- Read from stdin and write to stdout:
  - `cat input.txt | python scripts/kmer_count.py --k 4 --exclude-ambiguous`
- Add a verification check:
  - `python scripts/kmer_count.py --input input.txt --output output.txt --k 5 --exclude-ambiguous --verify`

If scikit-bio is not installed, install it in your environment (e.g., `pip install scikit-bio`) before running.
