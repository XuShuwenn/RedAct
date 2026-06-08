---
name: dna-kmer-counting
description: "Count overlapping DNA k-mers using scikit-bio and produce alphabetically sorted, nonzero counts."
---

DNA K-mer Counting with scikit-bio

Skill for computing overlapping k-mer counts (e.g., k=3) from a DNA sequence using the scikit-bio library and writing alphabetically sorted, nonzero counts in a simple line-based format.

When to Use
- The prompt asks to count k-mers from a DNA sequence.
- The output must list only k-mers with count > 0.
- The output must be sorted alphabetically by k-mer.
- The task requires scikit-bio to be used.

Core Workflow
1. Preparation
   - Confirm the task’s required k value and output format.
   - Ensure scikit-bio is available (from skbio import DNA). If import fails, resolve installation before proceeding, or use a plain-Python cross-check only for verification.
   - Read the sequence from the provided input path. If the file is FASTA-like, skip any header lines that start with '>' and concatenate the remaining lines.
   - Normalize sequence to uppercase.
   - Unless the prompt states otherwise, sanitize to standard nucleotides A, C, G, T (remove other characters). This ensures deterministic k-mer windows.

2. Counting with scikit-bio
   - Use scikit-bio’s DNA sequence class and its k-mer frequency utility.
   - Example approach:
     - dna = DNA(cleaned_seq)
     - counts = dna.kmer_frequencies(k, overlap=True, relative=False)
   - This returns a mapping of observed k-mers to integer counts. The overlap=True parameter is critical to include all overlapping windows.

3. Filtering and Sorting
   - Filter to include only k-mers with count > 0.
   - Sort lexicographically by the k-mer string.

4. Formatting Output
   - For each k-mer, write one line as: "KMER: COUNT".
   - No extra spaces, punctuation, or table formatting; one k-mer per line.

5. Verification
   - Confirm alphabetical sort: keys are in non-decreasing lexicographic order.
   - Confirm all counts are positive integers (> 0).
   - Confirm formatting by matching each line against the pattern "^[ACGT]{k}: [0-9]+$".
   - Sanity-check counts: for a sanitized sequence of length L and k-mer size k, if L >= k, the total number of overlapping windows should be L - k + 1. The sum of counts should equal this number.
   - If any check fails, re-examine sequence cleaning, overlap settings, and sorting.

Common Pitfalls
- Using non-overlapping windows. Always set overlap=True; otherwise counts will be too low.
- Sorting by count instead of k-mer alphabetically. The required order is lexicographic by k-mer string, not by frequency.
- Emitting zero-count k-mers. Only include k-mers that appear at least once.
- Outputting a table or extra formatting. Use one line per k-mer: "KMER: COUNT".
- Ignoring sequence normalization. Mixed case or non-ACGT characters can cause incorrect window formation and mismatched totals.
- Using relative frequencies. The task requires integer counts; ensure relative=False.
- Skipping post-run verification. Simple checks catch overlap mistakes, sorting issues, or formatting deviations.

Success Criteria
- Counts computed using scikit-bio with overlap=True and relative=False.
- Only k-mers with count > 0 are output.
- Lines are formatted exactly as "KMER: COUNT".
- Lines are sorted alphabetically by the k-mer.
- The sum of counts equals the number of overlapping windows in the sanitized sequence.

Optional Script Usage
- A helper script is provided to sanitize DNA, compute overlapping k-mer counts using scikit-bio (fallback to pure Python if unavailable), and validate output.
- Typical use: provide input path, desired k, and output path; confirm verification passes before finalizing.
