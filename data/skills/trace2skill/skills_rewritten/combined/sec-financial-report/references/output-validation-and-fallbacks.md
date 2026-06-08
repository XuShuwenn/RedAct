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

- First try fixing the invocation, not the tool: pass the correct quarter/path arguments, use absolute dataset paths, or wrap the helper with a tiny one-off command in an allowed working location.
- Do not edit shared support code in the skills directory unless the task explicitly requires code changes and you have already confirmed the issue is a real code bug rather than a bad invocation/path assumption.

## 3. Completion criteria for accession-based rankings

- A ranked accession list is not the final answer when the question asks for manager names.
- Map every winning accession back to the same quarter's `COVERPAGE.tsv`.
- If even one top accession lacks a confirmed manager-name mapping, the answer is still incomplete.

- For top-k outputs, compare the expected count to the resolved count before finalizing.
- Example: if the ranking returns 3 accessions but the manager lookup shows only 2 rows, the result is incomplete; rerun the lookup or join until all 3 are directly resolved.
- Never fill the missing row from institution familiarity, prior expectations, or the apparent popularity of a manager.
- For top-k security/CUSIP answers, if company-name validation returns noisy or conflicting matches, rerun an exact CUSIP lookup scoped to the chosen filing/accession context before keeping the name.

## 4. Do not finalize early

Before writing the deliverable, confirm there are no open investigations remaining. If you still need to rerun Berkshire comparison output or complete Palantir holder-name mapping, finalization is premature.

- Use an explicit stop gate before file-writing: for each question, confirm `entity/accession verified -> computation complete -> ranked/result rows fully visible -> required name mapping complete`.
- For Berkshire-style comparison questions, partial checks of a few CUSIPs or one new position do not substitute for the final ordered top-k output.
- For Palantir-style holder rankings, accession-only output is intermediate data; completion requires all requested manager names to be resolved from `COVERPAGE.tsv`.