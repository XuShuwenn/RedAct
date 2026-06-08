---
name: dna-frame2-translation
description: "Analyze DNA sequences for type (DNA/RNA/Protein), calculate GC content, translate to proteins, and find longest ORF."
---

# DNA Sequence Analysis

## When to Use

- Analyze DNA/RNA sequences for composition
- Calculate GC content percentage
- Translate DNA sequences to protein sequences
- Find open reading frames (ORFs) in DNA

## Key Calculations

### Sequence Type Detection
- DNA: contains T (thymine)
- RNA: contains U (uracil) but no T
- Protein: contains letters beyond A, C, G, T, U

### GC Content
- GC% = (G + C) / total_bases × 100
- Round to 1 decimal place
- Compute counts and denominator from the full normalized input sequence (uppercase, with whitespace removed).
- Verify counts from that same normalized sequence before reporting: compute `length = len(seq)` and count `G` and `C` directly.
- Use the full validated nucleotide length as the denominator, and ensure any cited counts are consistent with the reported GC%.

### Translation (Frame 2)
- Codons are read starting from position 2 (0-indexed)
- Start codon: ATG
- Stop codons: TAA, TAG, TGA (use * for stop)
- In this skill, `frame 2` means start offset `1` (the second nucleotide; position 2 in 1-based numbering).
- Build the frame-2 codon list explicitly from `seq[1:]`, grouping successive triplets from that offset.
- Translate the entire remaining frame to the end; do not stop at the first stop codon unless the task explicitly asks for an ORF or peptide-until-stop.
- Map each in-frame stop codon to `*` and ignore any trailing 1–2 bases that do not form a full codon.
- Cross-check that the final peptide length equals the number of full frame-2 codons and that no amino acids were inserted or omitted.

### Longest ORF
- Scan all three reading frames codon-by-codon.
- In each frame, consider only starts and stops that lie on that frame's codon boundaries.
- For each `ATG` start, find the first in-frame stop codon (`TAA`, `TAG`, or `TGA`) that closes it.
- Compute ORF length in bp from start codon through stop codon inclusive.
- Compare all complete start→stop segments and report the maximum validated ORF length in bp.
- If no complete ORF exists in any frame, say so explicitly.

## Output Format

```
Sequence type: {DNA|RNA|Protein}
GC content: XX.X%
Frame 2 translation: X...
Longest ORF length: N bp
```


## New Section

## Final Checks

- Normalize the sequence once before any counting or frame analysis.
- Recompute the frame-2 codon list before writing the answer.
- If reporting a translation, ensure it matches the codon list exactly, one amino acid per full codon, with `*` for stop codons.
- If reporting an ORF length, confirm: start codon present, stop codon present, same frame, and length = number_of_codons × 3 bp.
- Ensure any position-, count-, or length-based claim matches the source sequence exactly before output.
## Tips

- Use string methods to count G and C
- Handle mixed case input (uppercase it)

- For translation and ORF tasks, write out codons for each relevant frame first, then derive the peptide or ORF length from that codon list.
- Keep translation and ORF analysis separate: translation reports the whole requested frame, while longest ORF uses start→stop logic.
- Before finalizing, verify the reported frame-2 peptide and longest ORF are both supported by an explicit frame scan.
