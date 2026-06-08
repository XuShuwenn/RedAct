# Protein Dihedral Angle Task

Given four atoms defining a dihedral angle (N-CA-C-N) in `/root/input.txt`, calculate the dihedral angle in degrees.

Input format (one coordinate per line, x y z):
- Line 1: N atom position
- Line 2: CA atom position
- Line 3: C atom position
- Line 4: N' atom position (next residue)

Calculate the dihedral angle using the torsion formula. The dihedral angle is the angle between the planes defined by (N, CA, C) and (CA, C, N').

Write result to `/root/output.txt`:
```
Dihedral angle: XXX.XX degrees
```

Round to 2 decimal places. Range is -180 to +180 degrees.