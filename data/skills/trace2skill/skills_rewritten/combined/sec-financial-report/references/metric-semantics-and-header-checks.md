# Metric semantics and header checks

Use this reference when the task depends on what a field means, not just its numeric value.

## 1. Match the metric to the question

- Do not reuse the first summary number a tool prints unless its label matches the requested metric.
- Treat `AUM`, `TABLEVALUETOTAL`, `total holdings`, `stock holdings`, `VALUE`, and `shares` as different metrics until a header, schema note, or explicit tool label shows they are the same for this task.

## 2. Header-first rule for manual TSV work

1. Read the header row first.
2. Map needed fields by name.
3. Only then write `awk`/Python/grouping logic.

This avoids column-position mistakes and prevents ranking by the wrong field.

## 3. Security-ranking rule

- For issuer-specific questions, confirm the exact issuer/CUSIP pair from visible source rows before aggregating.
- Rank by the field named in the question or, if the prompt is ambiguous, by the field explicitly stated in the skill/task guidance.
- In these 13F tasks, use infotable `VALUE` for holder ranking unless the prompt explicitly asks for share count.

## 4. Stop conditions

Stop and resolve the semantics before answering if:
- a tool prints an unlabeled summary number,
- multiple plausible count/value fields are available,
- the issuer match is only a fuzzy name hit,
- or the aggregation field was assumed from memory rather than read from headers/schema.