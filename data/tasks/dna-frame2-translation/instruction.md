# Sequence Analysis Task

A DNA sequence is provided in `/root/input.txt`.

Perform the following analysis and write results to `/root/output.txt`:

1. Determine whether the sequence is DNA, RNA, or protein
2. Calculate GC content as a percentage (round to 1 decimal place)
3. Translate the sequence in reading frame 2 (stop codon = *)
4. Find the longest open reading frame across all three reading frames
   (start codon: ATG, stop codons: TAA/TAG/TGA)

Output format (exact, each on its own line):
```
Sequence type: {DNA|RNA|Protein}
GC content: XX.X%
Frame 2 translation: X...
Longest ORF length: N bp
```

The DNA sequence (5'->3') is:
`ATTGCAGTTGCCATGTTCGTAGCTAATGCCGTACGATGCATCATGTCAATGCCTGATC`