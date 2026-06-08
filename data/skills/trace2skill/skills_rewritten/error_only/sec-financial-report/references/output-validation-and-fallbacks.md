# Output validation and fallback patterns

Use this reference when outputs are truncated, ranked results are incomplete, or accession lists still need manager-name resolution.

## 1. Truncated output is not evidence

- If a search, diff, ranking, or script output is cut off, do not infer the unseen remainder.
- Rerun with narrower filtering, redirected output, or a short saved script that prints only the needed rows/fields.
- For ranking questions, require the final ordered rows to be fully visible before selecting winners.

## 2. Minimal fallback after script failure

1. Read the failing script or command assumption.
2. If the problem is just a wrong path or quarter file, make only the smallest fix needed.
3. Re-run and confirm the output still refers to the verified accession(s) and intended quarter.
4. If the tool still does not produce a complete result, switch to a direct query/script that emits the exact needed fields.

## 3. Completion criteria for accession-based rankings

- A ranked accession list is not the final answer when the question asks for manager names.
- Map every winning accession back to the same quarter's `COVERPAGE.tsv`.
- If even one top accession lacks a confirmed manager-name mapping, the answer is still incomplete.

## 4. Do not finalize early

Before writing the deliverable, confirm there are no open investigations remaining. If you still need to rerun Berkshire comparison output or complete Palantir holder-name mapping, finalization is premature.