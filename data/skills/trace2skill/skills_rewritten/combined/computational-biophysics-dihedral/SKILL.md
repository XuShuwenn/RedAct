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
- Treat the first tool call as a contract test: if the task mandates `Thought` followed by `Action:` JSON, your first operational turn must already use that exact pattern, not an exploratory near-match or alternate wrapper.
- If the task mandates an exact completion line such as `ACTION: TASK_COMPLETE`, reserve all prose for earlier steps and make that literal token the only final line.

- First-message gate: if the task specifies a required `Thought`/`Action` format, do not emit any alternative tool syntax. Your very first tool invocation must already match the required schema exactly.
- If the required tool name is `bash`, emit `Action:` with the exact JSON object for `bash`; do not substitute another tool name unless the task explicitly allows it.
- If such a protocol is specified, use that exact format for every tool interaction from start to finish; do not switch interfaces, mix conventions from other tasks, or improvise a near match.
- Wait for each tool observation before issuing the next tool action when the task protocol requires stepwise `Thought`/`Action` sequencing.
- Make file creation observable: explicitly write `/root/output.txt` with the result, then verify it before finishing.
- Do not merely state that the file was written; perform the write and show evidence in the trace.
- Before the final response, verify the last line matches any required completion token verbatim.
- If an exact completion signal is required (for example `ACTION: TASK_COMPLETE`), emit it as the final line exactly, with no trailing explanation or summary after it.

- Do not substitute a prose summary when the task requires an exact completion signal.
- Treat procedural requirements as part of correctness: a correct angle written to the file is not sufficient if the required action format or completion message is wrong.

- **Protocol gate before any tool call:** if the task specifies an exact `Thought`/`Action` or `Action: { ... }` schema, use that exact wrapper, tool name/schema, and final completion token from the first tool call onward.
- If the task specifies a single allowed tool pathway (for example only `bash` via `Action:` JSON), use only that pathway for reads, computation, and writes; do not substitute `Read File`, `Write`, `Terminal`, XML-style tool calls, prose descriptions of actions, or any other helper interface.
- **DO NOT** emit tool calls as XML-style tags, pseudo-functions, or ad hoc wrappers when a schema is mandated.
  - Wrong: `<tool_call name="Write">...</tool_call>`, `Terminal(...)`, or `I wrote /root/output.txt`.
  - Right: `Action: {"tool":"bash","cmd":"... > /root/output.txt"}` using the exact required JSON/object format from the task instructions.
- When the task requires stepwise Thought/Action sequencing, emit exactly one properly formatted action, wait for the observation, then continue; do not batch mixed interfaces.
- If you discover an execution issue mid-run (for example missing `numpy`), change only the computation method; do **not** change the mandated action format, authorized tool pathway, file-write evidence requirements, or completion signal.

- When a strict protocol is present, follow this mandatory sequence: identify the exact schema and allowed tool -> use only that schema for every tool call -> perform an observable write to `/root/output.txt` -> read `/root/output.txt` back to verify the persisted line -> emit the exact required completion token as the final line.
- If a retry is needed because computation code failed, change only the computation method; do not change the mandated tool wrapper, authorized interface, write-verification requirements, or final completion signal.

## Input Format

File `/root/input.txt` with one coordinate per line (x y z):
- Line 1: N atom position
- Line 2: CA atom position
- Line 3: C atom position
- Line 4: N' atom position (next residue)

- Preserve the four non-empty lines in this exact order and bind them explicitly as `N`, `CA`, `C`, and `N'` before doing any vector math.
- Assign points in file order: `p0=N`, `p1=CA`, `p2=C`, `p3=N'`; do not sort, relabel, or reorder coordinates, because the ordered backbone sequence determines the dihedral's sign and meaning.

- Parse each non-empty line as exactly 3 whitespace-separated numeric fields (`x y z`). If any line has the wrong field count or a non-numeric token, stop and fix the parsing/input issue before computing.
- Do not infer missing coordinates, ignore extra numeric fields, or continue with partial parsing; malformed input invalidates the dihedral calculation.

## Calculation Method

Dihedral angle = angle between planes defined by (N, CA, C) and (CA, C, N')

Use the coordinates from `/root/input.txt` directly and compute the torsion from those four ordered points; do not infer the angle from a sketch or qualitative geometry alone.

Recognize this as a standard backbone torsion task and apply the canonical signed dihedral formula directly rather than using an indirect workaround or geometric guess.
Model the dihedral explicitly as the angle between the planes `(N, CA, C)` and `(CA, C, N')` formed by the parsed ordered coordinates, keeping that shared-edge plane interpretation throughout the calculation.

Use torsion formula:
1. Compute vectors
2. Compute normals via cross products
3. Calculate angle between normals using dot product
4. Adjust sign based on direction


Use the full signed four-point torsion calculation directly for planes `(N, CA, C)` and `(CA, C, N')`; do not substitute a simpler bond-angle, unsigned angle-between-planes, or reordered-atom formula.

For ordinary four-point coordinate inputs, go straight from parsed ordered coordinates to the canonical signed torsion computation; avoid unnecessary intermediate transforms, qualitative inference, or biochemical labeling before the numeric result is computed and saved.


Use a signed `atan2`-based torsion formula as the default method so the result naturally lands in the required `-180` to `+180` range. Keep the computed angle at full precision during calculation; round only when formatting the final line for `/root/output.txt`.

Prefer a standard-library implementation (`math`) for vector arithmetic, cross products, dot products, norms, and `atan2`-based signed torsion unless the environment clearly provides `numpy`.

Do not assume external packages are installed for this task. If basic arithmetic is sufficient, use built-in Python only.
- For this task, do **not** start with a `numpy`-based script as the first attempt. Begin with standard-library Python (`math`, basic lists) unless the environment explicitly confirms `numpy` is available.
- If a prior run showed an import failure for an optional package, remove that dependency entirely for the retry rather than probing with more package-dependent variants.
- Do not introduce `numpy` or other optional packages for the main computation or for a secondary verification pass unless you have already confirmed availability in the environment.
- For this four-point torsion task, standard-library Python is the default and usually sufficient end to end.


Prefer a single compact Python script that reads `/root/input.txt`, maps the points explicitly to `N, CA, C, N'`, computes the signed torsion once with the standard `atan2` workflow, writes `/root/output.txt`, and then verifies the written file. This reduces transcription mistakes in self-contained file tasks.

Before writing the result, perform a quick sanity check:
- If all four atoms are coplanar, the dihedral should be near `0` or `±180` degrees.
- For fully planar inputs (for example all atoms sharing the same `z` value), do not accept `0` vs `±180` blindly: inspect the bond directions or confirm with the alternate `atan2` formulation before choosing the persisted sign/magnitude.

- If either plane normal has near-zero magnitude (colinear or duplicate points), treat the angle as degenerate and do not trust a raw numeric output without inspecting the geometry.
- Verify the sign/magnitude with an alternate formulation such as `atan2((b2/|b2|)·(n1×n2), n1·n2)` when the configuration is close to planar.
- If the geometry is planar or at a wraparound boundary, treat `180` and `-180` as equivalent boundary representations unless the task specifies a convention.
- Do not choose between `180.00` and `-180.00` arbitrarily: state the convention you are using or preserve the direct output of one consistent signed `atan2` formulation and keep that same value in `/root/output.txt`.

- When any adjacent bond vectors are collinear or either plane normal is zero/near-zero, treat the torsion as degenerate or convention-sensitive rather than as an ordinary signed angle; do not present a single raw value as fully settled without noting that limitation.
- For planar inputs, distinguish ordinary coplanarity from degeneracy: planar but nondegenerate points can support `0` or `±180`, while collinear triples or repeated points make the dihedral undefined or convention-dependent.
- If you still need to persist a numeric value because the task requires one, first state in your reasoning that the geometry is degenerate/convention-sensitive and that the chosen sign reflects the specific formula used, not a uniquely determined physical interpretation.
- For coplanar boundary outputs, do not choose `180.00` vs `-180.00` by preference or intuition. Use one explicit signed `atan2` torsion formula, keep its direct boundary output unchanged, and carry that same value consistently into `/root/output.txt`.
- If any adjacent bond vector has zero length or either plane normal is zero/near-zero, treat the case as degenerate or convention-sensitive rather than an ordinary well-defined signed dihedral.

## Output Format

Write to `/root/output.txt`:
```
Dihedral angle: XXX.XX degrees
```

Round to 2 decimal places. Range: -180 to +180 degrees.
Do not change formatting during finalization: keep the exact label `Dihedral angle:`, include a space before the numeric value and before `degrees`, and preserve two decimal places even for whole-number angles (for example `180.00`).

- Treat the exact output string as part of the deliverable: after computing the angle, persist only the requested line with the required label, spacing, and two-decimal precision.


## New Section

## Execution Checklist

- For file-based tasks, begin with a brief filesystem/path check only if needed to confirm the actual workspace layout and that `/root/input.txt` is the source and `/root/output.txt` is the destination; then use those task-specified absolute paths throughout.

- Read `/root/input.txt` and confirm there are exactly 4 coordinate lines.

- Inspect the actual contents of `/root/input.txt` before doing any math; treat the file contents as the source of truth rather than guessed, remembered, or prompt-restated coordinates.
- Ground the computation in the provided data: parse the four non-empty lines into explicit numeric 3D coordinates before any geometry reasoning, confirm you obtained 4 coordinate rows of 3 numeric values each, preserve file order, and bind the points in order to `N`, `CA`, `C`, and `N'`.
- Prefer the minimal direct workflow once paths are confirmed: **read `/root/input.txt` -> map the ordered points -> compute the signed dihedral -> write the exact required line to `/root/output.txt` -> read it back to verify**.

- Before the first tool call, identify any required Thought/Action schema, JSON wrapper, exact tool name, or completion signal and follow it verbatim for the entire run.
- Pause and compare your intended first tool call against the required schema character-for-character; if it is not an exact match in wrapper/prefix/style, rewrite it before sending.
- Protocol check is a hard gate: do not make any tool call until you can state the exact required action syntax, the single authorized tool/interface, and the exact final completion line.

- Reject near-miss wrappers before acting: do not use XML-like tool tags, helper tools such as `Read File`/`Write`/`Terminal`, or any mixed-interface pattern when the task specifies a single `Action:` JSON pathway.
- If the task authorizes only one pathway such as `bash`, perform file reads, Python execution, and file writes through that interface only, using absolute paths.
- Parse the four coordinates into explicit numeric 3D coordinates and map them in order to `N`, `CA`, `C`, and `N'`; do not sort or relabel points.
- Before any torsion math, explicitly enumerate the ordered mapping once in code or reasoning so the association from file lines to `N`, `CA`, `C`, and `N'` is unambiguous.
- Before trusting a numeric torsion result, inspect whether any adjacent bond vector has zero length or whether either plane normal is zero/near-zero; if so, treat the case as degenerate or convention-sensitive.
- For planar inputs, do not accept a single script output blindly: confirm whether the geometry supports `0` versus `±180` under the chosen signed `atan2` convention, and keep that convention consistent through write-back.

- Compute the angle and round to 2 decimals.
- Prefer one short self-contained standard-library Python script for this task: read `/root/input.txt`, validate 4 lines × 3 numbers, compute the signed torsion once, write `/root/output.txt`, then verify by reading the file back.

- If the coordinates are obviously coplanar or nearly coplanar, expect a result near `0.00`, `180.00`, or `-180.00` and use that geometry as a quick validation of the computed sign/magnitude.
- Before accepting a computed `0.00` or `±180.00`, explicitly inspect whether any three consecutive atoms are collinear or any bond vector has zero length; if so, treat the case as degenerate/convention-sensitive and do not trust the numeric output as uniquely determined.
- Do not rely on a single opaque script output for borderline geometries; cross-check the normals, coplanarity, and whether the sign could flip under an alternate but valid convention.
- Treat output formatting as part of correctness: preserve the exact prefix `Dihedral angle: `, include exactly two decimal places, and end with ` degrees`.

- Explicitly write the exact required line to `/root/output.txt`; printing the result to stdout is not sufficient.
- Treat any statement like `written to /root/output.txt` as forbidden until the trace already contains a concrete write command or script that writes the file.
- After writing, perform a separate observable read-back of `/root/output.txt`; do not rely on the same script's stdout alone as proof of persistence.

- Never state or imply that `/root/output.txt` was written unless the trace already contains the concrete write action and its observation; a plan to write, a script shown in markdown, or stdout showing the answer is not evidence of file creation.
- After any compute script that prints a result, separately confirm whether it also wrote `/root/output.txt`; stdout output alone does not satisfy a file-output requirement.

- Use only the task-specified absolute paths (`/root/input.txt`, `/root/output.txt`) for this workflow.
- Make the run auditable end to end: show an observable input read, an observable compute step (command or script), an observable write to `/root/output.txt`, and an observable read-back verification.
- Make the file creation observable with a concrete write action (for example a shell redirect, Python `Path(...).write_text(...)`, or equivalent tool step recorded in the trace).
- Treat the write as incomplete until you read the file back and confirm the exact persisted line, especially if you changed your mind about `-180.00` vs `180.00` or other normalization details.
- Do not rely on stdout output from a calculation script as evidence that `/root/output.txt` exists.
- Do not start with `numpy` for this task unless you have already confirmed it is available; built-in Python plus `math` is the default.
- Make the write step observable in your actions; do not claim the file was written unless you actually wrote it.
- If the task specifies a required tool-call syntax or final completion token, follow that protocol exactly.
- When a strict `Action:`/JSON protocol is in force, use this decision rule: **extract protocol -> issue only compliant tool calls -> explicitly write `/root/output.txt` -> read it back -> emit the exact completion token as the final line**.

- Hard stop: if no trace step explicitly writes `/root/output.txt` and no later step reads it back, the task is not ready for finalization even if the angle has been computed.


## New Section

## Finalization Checklist

- Immediately read `/root/output.txt` back and confirm it matches the intended final value exactly.

- Treat verification as two separate checks: confirm the intended numeric angle, then confirm `/root/output.txt` contains that same value in the exact required format.
- Confirm the verified file contains exactly one formatted result line of the form `Dihedral angle: XXX.XX degrees`.
- Once the four points are parsed correctly and the value is verified, avoid adding extra structural interpretation or side analysis unless the task explicitly asks for it.

- Confirm the reread content includes the exact required prefix, numeric rounding to 2 decimals, the `degrees` suffix, and the trailing newline; formatting mistakes can invalidate an otherwise correct angle.
- If the read-back shows stale, opposite-sign, or otherwise unexpected content, perform a corrective rewrite immediately and verify again; do not assume the prior write succeeded.
- Confirm the trace contains the explicit write action that created or overwrote `/root/output.txt`; a later read-back alone does not prove the file was written in this run.
- Do not emit any final answer or required completion token until the verified file content, your chosen sign/normalization, and your reported result all match exactly.
- If no observed write action exists in the trace, do not finalize; perform the write, verify it, and only then emit the required completion signal.
- The final line must be the exact required completion signal when the task defines one; do not add any summary, explanation, or extra line after that token.
- If the file content does not match, rewrite it and verify again before finishing.
- If you reconsider sign or normalization (for example `-180.00` vs `180.00`), update the file so the persisted output matches your final decision.

- For planar or nearly degenerate coordinates, explicitly confirm why the final value is `0`, `180`, or `-180` before accepting the file contents.
- If the final value is a boundary case such as `180.00` or `-180.00`, explicitly confirm that this choice follows from the selected torsion convention and is not just an arbitrary sign pick.
- If your reasoning identifies the geometry as degenerate, zero-normal, or otherwise convention-sensitive, acknowledge that limitation before finalizing rather than presenting the boundary sign as uniquely physically determined.

- If the task does not define a special convention for boundary cases, keep one convention consistently through computation, file write, and final report.
- Do not conclude the task while reasoning, reported answer, and `/root/output.txt` disagree.

- Perform a final protocol check before responding: confirm both the tool-call format used during execution and the final completion message match the task's required schema exactly.
- If an exact completion marker is required (for example `ACTION: TASK_COMPLETE`), output that literal string as the final line exactly, with no extra sentence before or after it.

- Before sending the final message, compare it against the required completion token character-for-character; if anything else remains in the draft, delete it and leave only the exact token.
- Do not end with a prose success message such as `Result written to /root/output.txt` when the task requires a fixed completion token.
- Do not end with a natural-language summary when the protocol requires a fixed completion token.
- After any fallback or retry, re-check all non-numeric constraints before finishing: required tool-call syntax, observable write to `/root/output.txt`, read-back verification, and the exact completion token.

- Keep the final deliverable limited to what was actually computed and verified. Do not add biochemical or structural labels such as `trans`, `cis`, `extended`, or similar interpretations unless the task explicitly asks for them and you derived them separately from observable steps.
- If the geometry was degenerate or convention-sensitive, avoid overstating certainty in the final wording; persist only the required output line and keep any explanation strictly to the verified limitation.


## Tips

- Preserve the atom order exactly as given: N, CA, C, N' (do not reorder points).
- Start by converting the 4 input lines into explicit point tuples/lists; this reduces ambiguity and makes the point ordering and vector construction auditable.

- Prefer a short Python script with built-in `math` and simple helper functions for vector arithmetic; use `numpy` only if the environment clearly provides it.
- Compute the signed dihedral from plane normals with an `atan2` formulation so the result stays in the `-180` to `180` range.
- Keep full precision during computation; round only in the final formatted write to `/root/output.txt`.
- For straightforward tasks, use one short script that reads input, computes the signed torsion, writes `/root/output.txt`, and then reads it back to verify formatting.

- Prefer a single end-to-end script over split manual steps when possible: read the observed file contents, map `N, CA, C, N'` in order, compute signed `atan2` torsion with built-in `math`, write the exact formatted line, then reread the file to confirm persistence and formatting.
- For small coordinate-geometry tasks like this, this compact script-first approach is usually safer than hand calculation because it reduces arithmetic, transcription, and sign-convention mistakes.
- Check for colinear atoms or repeated points before trusting the numeric output.
- Assume the coordinates are plain Cartesian coordinates unless the task explicitly states otherwise; do not invent unit conversions, rescaling, or alternate interpretations.


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
