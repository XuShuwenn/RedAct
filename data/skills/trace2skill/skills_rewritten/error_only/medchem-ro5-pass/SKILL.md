---
name: medchem-ro5-pass
description: "Detect problematic functional groups in molecules using medchem CommonAlertsFilters."
---

# Common Alerts Filter with medchem

## When to Use

- Detect problematic functional groups in molecules
- Use medchem CommonAlertsFilters
- Follow task-specific implementation constraints exactly: use the required library/API directly, and do **not** substitute RDKit or another chemistry library unless the task explicitly allows it.

- Treat implementation constraints as hard requirements: if the task requires `medchem`, import and use `medchem` directly rather than reproducing the logic with RDKit or another library.
- Check if molecule passes safety criteria


## When to Use

## Critical Protocol Rules

- Treat the system/developer-specified execution interface as a hard requirement. If the environment requires a specific tool-call/action schema (for example, `Action:` followed by JSON for `bash`), use that exact format for **every** tool invocation.
- Do **not** improvise alternative tool syntaxes, wrappers, or pseudo-tool calls when the prompt specifies one. Wrong tool-call formatting is a task failure even if the chemistry/output is correct.
- If the environment requires an exact final completion token (for example, `ACTION: TASK_COMPLETE`), output that exact token verbatim as the final chat message with no extra text.
- Before declaring completion, verify full input coverage: every non-empty input record/ID appears in the output exactly once, and output count matches input count.
## Input

- `/root/input.txt`: SMILES input
- Do not assume exactly one molecule unless the file clearly contains only one record; if multiple non-empty molecule rows are present, process every row exactly once.

- Inspect the actual input file and schema before coding; do not assume plain line-by-line SMILES, delimiter choice, column names, or single-record structure from the path alone.
- Count the real non-empty records up front, identify molecule-bearing field(s) plus any task-provided IDs, preserve input order, and map each output row/block to its source record exactly once.

## Output Format

To `/root/output.txt`:
```
Common alerts: N
Status: status
Pass: yes/no
```

A molecule PASSES if:
- status is "ok", OR
- status is "annotations" with 0 alert reasons

- If the task input contains multiple molecule records or IDs, emit one result block/line per input record in the required task format, and ensure the output covers all records.

- Treat the requested output text as a strict interface: preserve the exact required fields, labels, ordering, punctuation, and block/line structure for each record.
- If the task specifies identifiers, summaries, case-specific formatting variants, or a different per-record schema, reproduce that contract verbatim instead of defaulting to the 3-line example.
- For exact-format outputs, include only the requested fields/tokens; do not append extra measured values, labels, or commentary unless explicitly required.

- Ground every reported field in the actual input or computed `medchem` result. If the input provides only IDs and SMILES, report only those task-required identifiers plus computed outputs.
- Do **not** add molecule names, identities, annotations, or other metadata unless they were explicitly present in the input/task or were derived through an explicit logged step required by the task.


## New Section

## Execution Checklist

- Write the required results to `/root/output.txt` before declaring completion.
- If `/root/input.txt` contains multiple molecule rows, process every non-empty record exactly once.
- Before finishing, verify output cardinality: the number of result blocks/lines matches the number of input records, and any summary totals agree.
- Also verify identity coverage for batch inputs: compare the full set of input IDs/rows against the output so no record is silently omitted even when totals look plausible.
- Follow task-level and system-level protocol exactly when present (required library/API, tool-call schema, or completion formatting). Higher-priority instructions override this skill's examples.
- If the environment requires an exact completion string (for example, `ACTION: TASK_COMPLETE`), emit that exact string verbatim as the final chat message, with no extra explanation before or after it.
- Finalization rule: when an exact completion token is required, make it the entire final message. Do **not** prepend a summary, success statement, or any extra text.
- After writing `/root/output.txt`, do not add tables, summaries, or commentary in chat unless the task explicitly asks for them.

- Before implementing, confirm the execution context: the input file exists, its real schema is understood, and the required library/imports are available.
- Before the first tool call, confirm the required interaction/tool-call protocol for this environment and use that exact structure for every invocation.
- Treat the environment's tool-call syntax as a hard interface: if the system specifies an exact schema such as `Thought:` plus `Action:` with JSON, use that exact format for every tool invocation and do **not** substitute XML-like tags, free-form tool calls, or another wrapper.
- Do **not** invent alternate tool syntaxes or tool names. If the environment specifies a single action format, use that exact format for every operation.
- If `medchem` is required, verify the actual code imports and calls `medchem` rather than a substitute library, and inspect the installed package/module contents so you use real API names instead of guessed import paths.
- Prefer one compact end-to-end script that inventories all records, applies `CommonAlertsFilters`, computes each record once, and writes `/root/output.txt` deterministically in one run.
- Make critical execution steps observable: when you create or run the script that writes `/root/output.txt`, expose the actual command(s) used and then read back `/root/output.txt` so file creation, formatting, and record coverage are directly verifiable rather than only summarized in prose.
- Track record coverage explicitly during processing: capture the full set of non-empty input rows and any provided IDs before computation, then verify the output contains one result per source record/ID with no omissions or duplicates.
- For each record, compute alert count and returned status first, then map them directly to the required fields: write `Common alerts: N`, write the returned `Status: ...`, and set `Pass: yes` only when status is `ok` or when status is `annotations` with 0 alert reasons; otherwise set `Pass: no`.
- Preserve computed details exactly when reporting results: if the library/task output includes specific reasons, values, or thresholds, copy those details verbatim into the required output fields or summaries instead of shortening them to generic labels.
- Build any required summaries/totals from the completed per-record results, and if the task requires only one reported failure/alert reason, emit a single reason in a fixed deterministic order.
- Reconcile aggregates before finishing: input record count, emitted per-record result count, and any summary totals must all agree. If they do not, fix the output before declaring completion.
- After writing `/root/output.txt`, reopen it and verify the exact schema/content, required field order, file existence, and output record/block count against the processed input records before declaring completion.
- Do not declare success from a script message alone. Verify that the script actually ran cleanly, the output file exists, and every expected input record appears exactly once in the output.
- If any requirement is not visible in the prompt/context, do **not** claim 'exact format requested' or similar; state only what you directly verified.

- Perform an explicit coverage audit before finishing: enumerate input record IDs/count, enumerate output record IDs/count, and confirm there are no missing or duplicate records.
- If the task provides IDs, compare the exact input ID set/order against the written output rather than checking counts alone.
- Before claiming success, compare `/root/output.txt` to the user/task specification line-by-line: exact field names, order, casing, separators, per-record structure, and any required summaries/totals must match the original instructions, not your paraphrase.
- Validate on the real input source before finishing: inspect the actual rows/records being processed, confirm the molecule-bearing field and any IDs, and ensure your status/alert-to-output mapping is based on observed `medchem` results from that input rather than inferred labels or assumed edge-case behavior.
## Using medchem

```python
from medchem._filters import CommonAlertsFilters

- Use `medchem` `CommonAlertsFilters` directly for the required alert detection in this skill; do not switch to RDKit descriptors or other chemistry APIs unless the task explicitly overrides this requirement.
- Derive required output fields directly from `CommonAlertsFilters` results: map returned alert data to `Common alerts`, `Status`, and `Pass` rather than inferring chemistry outcomes manually.
# Apply CommonAlertsFilters to molecule
```

## Alert Detection

- CommonAlertsFilters detects problematic functional groups
- Count number of alerts
- Determine pass/fail based on status

- Process every molecule present in the input source.
- Before finishing, verify the number of output result blocks matches the number of input molecules/records.
- If you include totals or pass/fail counts, reconcile them against the full input set.

## Tips

- Check status field to determine pass/fail
- Zero alerts means pass (yes)
- Handle different status return types

- Before coding, verify all hard constraints: required library, exact input/output paths, and exact output format.
- For batch inputs, count input records first and reconcile them with the final output.
- Re-read task-specific output requirements before finishing; if the task requires an exact completion string or response format, use it verbatim.
- Do **not** claim the result is fully compliant unless you checked all stated task and environment constraints.

- Separate computation from reporting: first compute the library-backed alert/status result, then render only the fields and labels the task explicitly requires.
- For schema-constrained tasks, prefer strict literal matching over "helpful" extra detail.
- Re-read protocol requirements before acting and before finishing; correct chemistry output does not count if the required tool-call format or final completion token is wrong.
- A small single-script Python workflow is usually the most reliable way to handle batch `medchem` evaluation plus strict file-output formatting.
- Do not stop at script creation: run it, then inspect `/root/output.txt` to confirm exact formatting and full record coverage.

- Protocol compliance is mandatory, not cosmetic: correct chemistry results still fail if the required tool-call schema or final completion token is wrong.
- For protocol-constrained tasks, use literal matching for tool-call syntax and final completion strings.
- Never end with a prose status summary when an exact completion token is required; the mandated token must be the entire final message.
- Do **not** replace specific computed failure text with a simplified category; keep the exact observed detail when the task asks for reasons or summaries.
- Do not rely on narrative claims like "screened the molecules" or "wrote the file" for critical steps; show the concrete script/command and a readback or equivalent verification artifact.
- Avoid unsupported guarantees. Only say the output matches an exact required format when you have explicitly checked that requirement against the task instructions and the written file.
- If a label or identity was not present in the source data or explicitly derived, omit it.
