# RMSD Calculation Task

Given two sets of atomic coordinates (reference and target), calculate the RMSD (Root Mean Square Deviation) between them.

The input file `/root/input.txt` contains coordinates for reference and target structures, 3 atoms each (x y z per line):
- Lines 1-3: reference coordinates
- Lines 4-6: target coordinates

Calculate RMSD = sqrt(sum(|ri - ti|^2) / N) where N=3.

Write result to `/root/output.txt`:
```
RMSD: X.XXXX nm
```

Round to 4 decimal places. Units are nanometers.