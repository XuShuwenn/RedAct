---
name: computational-biophysics-dihedral
description: "Calculate dihedral angles for protein backbone (N-CA-C-N) using torsion formula from atomic coordinates."
---

# Protein Dihedral Angle Calculation

## When to Use

- Calculate torsion angle between two planes in a protein backbone
- Parse 3D atomic coordinates from text files
- Compute geometric angles for molecular analysis


## New Section

## Task-Protocol Override

- Follow any task-specific tool-call format, action schema, or completion signal exactly as given by the current task or system instructions.
- Treat task-level protocol requirements as mandatory overrides to this skill's scientific guidance.
- Before using tools, check whether the task requires a specific `Action` format, JSON schema, or other invocation syntax.
- Make file creation observable: explicitly write `/root/output.txt` with the result, then verify it before finishing.
- Do not merely state that the file was written; perform the write and show evidence in the trace.
- Before the final response, verify the last line matches any required completion token verbatim.
- Do not substitute a prose summary when the task requires an exact completion signal.
- Treat procedural requirements as part of correctness: a correct angle written to the file is not sufficient if the required action format or completion message is wrong.

## Input Format

File `/root/input.txt` with one coordinate per line (x y z):
- Line 1: N atom position
- Line 2: CA atom position
- Line 3: C atom position
- Line 4: N' atom position (next residue)

## Calculation Method

Dihedral angle = angle between planes defined by (N, CA, C) and (CA, C, N')

Use torsion formula:
1. Compute vectors
2. Compute normals via cross products
3. Calculate angle between normals using dot product
4. Adjust sign based on direction

Prefer a standard-library implementation (`math`) for vector arithmetic, cross products, dot products, norms, and `atan2`-based signed torsion unless the environment clearly provides `numpy`.

Do not assume external packages are installed for this task. If basic arithmetic is sufficient, use built-in Python only.

Before writing the result, perform a quick sanity check:
- If all four atoms are coplanar, the dihedral should be near `0` or `±180` degrees.
- If either plane normal has near-zero magnitude (colinear or duplicate points), treat the angle as degenerate and do not trust a raw numeric output without inspecting the geometry.
- Verify the sign/magnitude with an alternate formulation such as `atan2((b2/|b2|)·(n1×n2), n1·n2)` when the configuration is close to planar.

## Output Format

Write to `/root/output.txt`:
```
Dihedral angle: XXX.XX degrees
```

Round to 2 decimal places. Range: -180 to +180 degrees.


## New Section

## Execution Checklist

- Read `/root/input.txt` and confirm there are exactly 4 coordinate lines.
- Compute the angle and round to 2 decimals.
- Explicitly write the exact required line to `/root/output.txt`; printing the result to stdout is not sufficient.
- Make the write step observable in your actions; do not claim the file was written unless you actually wrote it.
- If the task specifies a required tool-call syntax or final completion token, follow that protocol exactly.


## New Section

## Finalization Checklist

- Immediately read `/root/output.txt` back and confirm it matches the intended final value exactly.
- If the file content does not match, rewrite it and verify again before finishing.
- If you reconsider sign or normalization (for example `-180.00` vs `180.00`), update the file so the persisted output matches your final decision.
- Do not conclude the task while reasoning, reported answer, and `/root/output.txt` disagree.

## Tips

- Use numpy for cross product and dot product
- Check for colinear atoms (handle edge cases)
- Verify coordinate units before computing


## New Section

## Minimal Example

```python
from pathlib import Path
from math import atan2, degrees, sqrt


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def norm(v):
    return sqrt(dot(v, v))


def scale(v, s):
    return [x * s for x in v]


lines = [line.strip() for line in Path('/root/input.txt').read_text().splitlines() if line.strip()]
if len(lines) != 4:
    raise ValueError('Expected exactly 4 coordinate lines')
pts = [[float(x) for x in line.split()] for line in lines]
p0, p1, p2, p3 = pts

b0 = sub(p1, p0)
b1 = sub(p2, p1)
b2 = sub(p3, p2)
n0 = cross(b0, b1)
n1 = cross(b1, b2)
b1_norm = norm(b1)
if norm(n0) == 0 or norm(n1) == 0 or b1_norm == 0:
    raise ValueError('Colinear or repeated atoms; dihedral undefined')

n0u = scale(n0, 1.0 / norm(n0))
n1u = scale(n1, 1.0 / norm(n1))
b1u = scale(b1, 1.0 / b1_norm)
m1 = cross(n0u, b1u)
angle = degrees(atan2(dot(m1, n1u), dot(n0u, n1u)))
Path('/root/output.txt').write_text(f'Dihedral angle: {angle:.2f} degrees\n')
```
