# Reusable analysis workflows

Use this reference after you have verified the correct accession number(s) from quarter-specific `COVERPAGE.tsv`.


## Table-to-question mapping

- `COVERPAGE.tsv`: manager/filer identity, quarter-specific accession verification, accession→manager mapping.
- `SUMMARYPAGE.tsv`: filing-level aggregate totals and summary metrics.
- `INFOTABLE.tsv`: holding-level rows, issuer/CUSIP resolution, position values, and security-wide holder rankings.

Choose the table first, then choose the command or script. This avoids pulling aggregate answers from holding-level data or trying to resolve manager names from ranking output alone.

## Proven pattern

1. Identify the exact filer and accession in the relevant quarter's `COVERPAGE.tsv`.
2. Feed the verified accession into existing analysis tooling for:
   - AUM / table value totals
   - holdings or stock counts
   - quarter-over-quarter changes against a verified baseline accession
3. Read back the computed output and confirm it still refers to the intended filer and quarter.

- When several cover-page matches exist for a manager, confirm the filing/report type before choosing the accession; for holdings analysis, prefer the `13F HOLDINGS REPORT` accession over `13F NOTICE` or similar non-holdings entries.
- Before running a helper, do a quick read of the script to confirm expected data root, filenames, and quarter layout so you can invoke it correctly the first time.
- When moving between filer metadata, summary metrics, and holding-level results, keep the accession number fixed as the join key across every step.
- When broad name matching is noisy, query quarter-specific `COVERPAGE.tsv` directly by manager name to recover the exact filing row instead of iterating on fuzzy matches.
- If one verified fund script already reports multiple requested metrics for the same accession, reuse that single accession-confirmed workflow instead of rebuilding separate manual extractors.
- For business-metric questions, verify that the returned field actually matches the requested metric before answering. `COVERPAGE.tsv` establishes who the filer is; it does not by itself prove that a downstream summary field is AUM.
- If the chosen helper fails, first verify whether the problem is invocation/path selection rather than the analysis logic itself.
- If the helper outputs accession numbers only, immediately resolve those accessions back to manager names in the matching quarter's `COVERPAGE.tsv` before finalizing.
- If the computed output is accession-level but the question is manager-level, perform the final join or aggregation to manager name before selecting winners.

## When to prefer scripts over manual parsing

Prefer reusable scripts/tools when they already produce the requested summary metric or ranked comparison. This is usually safer and faster than manually rebuilding calculations from large `INFOTABLE` data.

- For quarter-over-quarter manager questions, prefer tools that accept both current and baseline accessions/filings directly; this is usually more reliable than reconstructing diffs from raw holdings tables.
- If the reusable script is not quickly recoverable, re-implement only the narrow required slice with a short one-off query/script against the quarter-specific TSVs instead of debugging unrelated helper features.
- Common safe fallback pattern: compute ranked `ACCESSION_NUMBER` results from `INFOTABLE.tsv`, then recover display names by joining those exact accessions back to the same quarter's `COVERPAGE.tsv`.
- Preserve the boundary between workflows: filing-summary tools are the default for manager-level metrics, while issuer/CUSIP-specific top-holder questions should be answered from holdings-table aggregation plus accession-to-manager lookup.
- If a helper fails for a non-path reason or remains incomplete after the minimal verified fix, switch once to a direct raw-data workflow instead of repeatedly debugging the same wrapper.
- A practical first step is to list the available local scripts/utilities and choose the one whose inputs already align with the verified accession(s), quarter, or comparison task.

## Minimal script-fix rule

If a reusable script fails on file loading, first inspect its expected paths and arguments, then prefer fixing invocation/environment (correct absolute paths, working directory, or a task-local dataset link/preparation step) over editing logic. Only if there is a clearly verified hardcoded-path bug should you make the smallest path fix needed to point it at the correct quarter-specific files.

- Before editing a reusable script, inspect its current invocation plus file/path assumptions and decide whether the failure is caused by wrong arguments, wrong working directory, or an actual hardcoded-path bug.
- When debugging a path failure, compare the failing script with a sibling script that already works on the same dataset and copy only the proven path convention, not broader logic changes.
- Prefer invocation/path corrections over code edits: pass the correct quarter/path arguments, use absolute file paths, or wrap the existing utility with a short task-local command before considering any script modification.
- After any path/invocation fix, rerun once and confirm the script is now reading the intended quarter directory rather than a default path or another quarter.
- For quarter-scoped datasets, explicitly check whether the tool incorrectly assumes files live in a flat root. Point it instead to the chosen quarter directory and ensure any companion metadata join uses that same quarter's `COVERPAGE.tsv`, not a different quarter or a default path.
- For holder-ranking questions, a path fix is incomplete unless the tool can read both holdings data and the metadata needed to resolve winning accessions back to manager names.
- Do **not** edit shared skill/support code in the skills directory merely to accommodate the current task's filesystem layout.
- Only then make the smallest fix needed; do not broaden the rewrite unless the script remains unverifiable after the path fix.

## Validation after script use

- Confirm the script input accession number(s) match the intended filer(s).
- Confirm quarter labels and paths are correct.
- Confirm the final reported values or ranked identifiers are fully visible before writing the answer.

- If output is clipped, banner-only, or stops before the needed ranked rows, rerun with narrower filters or redirect to a file and inspect the exact final rows before answering.
- Treat partially visible rankings as unverified even if the visible prefix seems sufficient to guess the answer.

- If the script emits both broader totals and stock-only counts, select the field whose label matches the question text exactly rather than the first metric shown.
- When a script succeeds after a path/invocation fix, still confirm the reported filer/accession and quarter in the output before trusting the computed values.
- For single-fund questions, verify that the script output labels match the requested metric before answering: `AUM`/table value totals for Q1-style questions, and stock/equity holdings count for Q2-style questions.
- If the script reports multiple related metrics, copy only the one whose label matches the question wording; do not substitute a nearby field because it is numerically available first.
- If the script succeeds only after a path/layout correction, verify that the correction preserved the intended quarter and did not silently mix Q2 and Q3 inputs.
- When the script's raw output is identifier-only, add the metadata join as part of the same workflow rather than treating it as optional cleanup.
- For summary metrics, read back the exact returned labels (for example AUM vs number of stock holdings) and match them to the question wording before answering.
- For comparison or ranking outputs, verify at least the final selected rows with a simple direct query against the underlying TSV/XML data so the chosen CUSIPs or managers are not based only on opaque tool output.
