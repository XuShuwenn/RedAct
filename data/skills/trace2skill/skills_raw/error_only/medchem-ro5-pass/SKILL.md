---
name: medchem-ro5-pass
description: "Detect problematic functional groups in molecules using medchem CommonAlertsFilters."
---

# Common Alerts Filter with medchem

## When to Use

- Detect problematic functional groups in molecules
- Use medchem CommonAlertsFilters
- Follow task-specific implementation constraints exactly: use the required library/API directly, and do **not** substitute RDKit or another chemistry library unless the task explicitly allows it.
- Check if molecule passes safety criteria

## Input

- `/root/input.txt`: SMILES input
- Do not assume exactly one molecule unless the file clearly contains only one record; if multiple non-empty molecule rows are present, process every row exactly once.

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


## New Section

## Execution Checklist

- Write the required results to `/root/output.txt` before declaring completion.
- If `/root/input.txt` contains multiple molecule rows, process every non-empty record exactly once.
- Before finishing, verify output cardinality: the number of result blocks/lines matches the number of input records, and any summary totals agree.
- Follow task-level and system-level protocol exactly when present (required library/API, tool-call schema, or completion formatting). Higher-priority instructions override this skill's examples.
- If the environment requires an exact completion string (for example, `ACTION: TASK_COMPLETE`), output that exact string verbatim as the final chat message and nothing else.
- Do not summarize results in chat after writing the file unless the task explicitly asks for it.
## Using medchem

```python
from medchem._filters import CommonAlertsFilters
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
