# Sequence Alignment Score Task

Given two DNA sequences in `/root/input.txt` (one per line), calculate the alignment score using simple scoring:
- Match: +2
- Mismatch: -1
- Gap: -2 (opening), -1 (extension)

Use local alignment (Smith-Waterman) approach. Write result to `/root/output.txt`:
```
Alignment score: X
```

Output is an integer.