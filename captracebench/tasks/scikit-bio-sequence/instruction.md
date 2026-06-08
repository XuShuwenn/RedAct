# DNA K-mer Counting Task

Given a DNA sequence in `/root/input.txt`, count the occurrences of all possible 3-mers (k=3) using the `scikit-bio` Python library.

Write results to `/root/output.txt`. For each k-mer that appears at least once, output one line:
```
AXXXXXXXXXX: count
```

Sort output by k-mer alphabetically. Include only k-mers with count > 0.