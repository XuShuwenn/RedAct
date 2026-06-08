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

- Before the first tool call, extract the exact required invocation pattern and any required completion token from the task instructions; if a schema is specified, use that schema for every tool call with no substitutions.
- If such a protocol is specified, use that exact format for every tool interaction from start to finish; do not switch interfaces, mix conventions from other tasks, or improvise a near match.
- Wait for each tool observation before issuing the next tool action when the task protocol requires stepwise `Thought`/`Action` sequencing.
- Make file creation observable: explicitly write `/root/output.txt` with the result, then verify it before finishing.
- Do not merely state that the file was written; perform the write and show evidence in the trace.
- Before the final response, verify the last line matches any required completion token verbatim.
- If an exact completion signal is required (for example `ACTION: TASK_COMPLETE`), emit it as the final line exactly, with no trailing explanation or summary after it.

- Do not substitute a prose summary when the task requires an exact completion signal.
- Treat procedural requirements as part of correctness: a correct angle written to the file is not sufficient if the required action format or completion message is wrong.

## Input Format

File `/root/input.txt` with one coordinate per line (x y z):
- Line 1: N atom position
- Line 2: CA atom position
- Line 3: C atom position
- Line 4: N' atom position (next residue)

- Preserve the four non-empty lines in this exact order and bind them explicitly as `N`, `CA`, `C`, and `N'` before doing any vector math.
- Assign points in file order: `p0=N`, `p1=CA`, `p2=C`, `p3=N'`; do not sort, relabel, or reorder coordinates, because the ordered backbone sequence determines the dihedral's sign and meaning.

## Calculation Method

Dihedral angle = angle between planes defined by (N, CA, C) and (CA, C, N')

Use the coordinates from `/root/input.txt` directly and compute the torsion from those four ordered points; do not infer the angle from a sketch or qualitative geometry alone.

Use torsion formula:
1. Compute vectors
2. Compute normals via cross products
3. Calculate angle between normals using dot product
4. Adjust sign based on direction


Use the full signed four-point torsion calculation directly for planes `(N, CA, C)` and `(CA, C, N')`; do not substitute a simpler bond-angle, unsigned angle-between-planes, or reordered-atom formula.

Use a signed `atan2`-based torsion formula as the default method so the result naturally lands in the required `-180` to `+180` range. Keep the computed angle at full precision during calculation; round only when formatting the final line for `/root/output.txt`.

Prefer a standard-library implementation (`math`) for vector arithmetic, cross products, dot products, norms, and `atan2`-based signed torsion unless the environment clearly provides `numpy`.

Do not assume external packages are installed for this task. If basic arithmetic is sufficient, use built-in Python only.


Prefer a single compact Python script that reads `/root/input.txt`, maps the points explicitly to `N, CA, C, N'`, computes the signed torsion once with the standard `atan2` workflow, writes `/root/output.txt`, and then verifies the written file. This reduces transcription mistakes in self-contained file tasks.

Before writing the result, perform a quick sanity check:
- If all four atoms are coplanar, the dihedral should be near `0` or `±180` degrees.
- For fully planar inputs (for example all atoms sharing the same `z` value), do not accept `0` vs `±180` blindly: inspect the bond directions or confirm with the alternate `atan2` formulation before choosing the persisted sign/magnitude.

- If either plane normal has near-zero magnitude (colinear or duplicate points), treat the angle as degenerate and do not trust a raw numeric output without inspecting the geometry.
- Verify the sign/magnitude with an alternate formulation such as `atan2((b2/|b2|)·(n1×n2), n1·n2)` when the configuration is close to planar.

## Output Format

Write to `/root/output.txt`:
```
Dihedral angle: XXX.XX degrees
```

Round to 2 decimal places. Range: -180 to +180 degrees.
Do not change formatting during finalization: keep the exact label `Dihedral angle:`, include a space before the numeric value and before `degrees`, and preserve two decimal places even for whole-number angles (for example `180.00`).


## New Section

## Execution Checklist

- Read `/root/input.txt` and confirm there are exactly 4 coordinate lines.

- Before the first tool call, identify any required Thought/Action schema, JSON wrapper, exact tool name, or completion signal and follow it verbatim for the entire run.
- Parse the four coordinates into explicit numeric 3D coordinates and map them in order to `N`, `CA`, `C`, and `N'`; do not sort or relabel points.
- Compute the angle and round to 2 decimals.
- If the coordinates are obviously coplanar or nearly coplanar, expect a result near `0.00`, `180.00`, or `-180.00` and use that geometry as a quick validation of the computed sign/magnitude.
- Treat output formatting as part of correctness: preserve the exact prefix `Dihedral angle: `, include exactly two decimal places, and end with ` degrees`.

- Explicitly write the exact required line to `/root/output.txt`; printing the result to stdout is not sufficient.

- Use only the task-specified absolute paths (`/root/input.txt`, `/root/output.txt`) for this workflow.
- Make the run auditable end to end: show an observable input read, an observable compute step (command or script), an observable write to `/root/output.txt`, and an observable read-back verification.
- Make the file creation observable with a concrete write action (for example a shell redirect, Python `Path(...).write_text(...)`, or equivalent tool step recorded in the trace).
- Treat the write as incomplete until you read the file back and confirm the exact persisted line, especially if you changed your mind about `-180.00` vs `180.00` or other normalization details.
- Do not rely on stdout output from a calculation script as evidence that `/root/output.txt` exists.
- Do not start with `numpy` for this task unless you have already confirmed it is available; built-in Python plus `math` is the default.
- Make the write step observable in your actions; do not claim the file was written unless you actually wrote it.
- If the task specifies a required tool-call syntax or final completion token, follow that protocol exactly.


## New Section

## Finalization Checklist

- Immediately read `/root/output.txt` back and confirm it matches the intended final value exactly.

- Confirm the reread content includes the exact required prefix, numeric rounding to 2 decimals, the `degrees` suffix, and the trailing newline; formatting mistakes can invalidate an otherwise correct angle.
- If the read-back shows stale, opposite-sign, or otherwise unexpected content, perform a corrective rewrite immediately and verify again; do not assume the prior write succeeded.
- Confirm the trace contains the explicit write action that created or overwrote `/root/output.txt`; a later read-back alone does not prove the file was written in this run.
- Do not emit any final answer or required completion token until the verified file content, your chosen sign/normalization, and your reported result all match exactly.
- If the file content does not match, rewrite it and verify again before finishing.
- If you reconsider sign or normalization (for example `-180.00` vs `180.00`), update the file so the persisted output matches your final decision.

- For planar or nearly degenerate coordinates, explicitly confirm why the final value is `0`, `180`, or `-180` before accepting the file contents.
- Do not conclude the task while reasoning, reported answer, and `/root/output.txt` disagree.

- Perform a final protocol check before responding: confirm both the tool-call format used during execution and the final completion message match the task's required schema exactly.


## Tips

- Preserve the atom order exactly as given: N, CA, C, N' (do not reorder points).
- Prefer a short Python script with built-in `math` and simple helper functions for vector arithmetic; use `numpy` only if the environment clearly provides it.
- Compute the signed dihedral from plane normals with an `atan2` formulation so the result stays in the `-180` to `180` range.
- Keep full precision during computation; round only in the final formatted write to `/root/output.txt`.
- For straightforward tasks, use one short script that reads input, computes the signed torsion, writes `/root/output.txt`, and then reads it back to verify formatting.
- Check for colinear atoms or repeated points before trusting the numeric output.
- Verify coordinate units before computing.


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
N, CA, C, N_next = pts
b0 = sub(CA, N)
b1 = sub(C, CA)
b2 = sub(N_next, C)
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

print(Path('/root/output.txt').read_text(), end='')  # verify persisted output

```
