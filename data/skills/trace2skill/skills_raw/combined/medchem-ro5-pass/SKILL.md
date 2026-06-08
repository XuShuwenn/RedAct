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


## New Section

## Execution Checklist

- Write the required results to `/root/output.txt` before declaring completion.
- If `/root/input.txt` contains multiple molecule rows, process every non-empty record exactly once.
- Before finishing, verify output cardinality: the number of result blocks/lines matches the number of input records, and any summary totals agree.
- Follow task-level and system-level protocol exactly when present (required library/API, tool-call schema, or completion formatting). Higher-priority instructions override this skill's examples.
- If the environment requires an exact completion string (for example, `ACTION: TASK_COMPLETE`), emit that exact string verbatim as the final chat message, with no extra explanation before or after it.
- After writing `/root/output.txt`, do not add tables, summaries, or commentary in chat unless the task explicitly asks for them.

- Before implementing, confirm the execution context: the input file exists, its real schema is understood, and the required library/imports are available.
- Before the first tool call, confirm the required interaction/tool-call protocol for this environment and use that exact structure for every invocation.
- If `medchem` is required, verify the actual code imports and calls `medchem` rather than a substitute library, and inspect the installed package/module contents so you use real API names instead of guessed import paths.
- Prefer one compact end-to-end script that inventories all records, applies `CommonAlertsFilters`, computes each record once, and writes `/root/output.txt` deterministically in one run.
- For each record, compute alert count and returned status first, then map them directly to the required fields: write `Common alerts: N`, write the returned `Status: ...`, and set `Pass: yes` only when status is `ok` or when status is `annotations` with 0 alert reasons; otherwise set `Pass: no`.
- Build any required summaries/totals from the completed per-record results, and if the task requires only one reported failure/alert reason, emit a single reason in a fixed deterministic order.
- After writing `/root/output.txt`, reopen it and verify the exact schema/content, required field order, file existence, and output record/block count against the processed input records before declaring completion.
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
