# Reusable analysis workflows

Use this reference after you have verified the correct accession number(s) from quarter-specific `COVERPAGE.tsv`.

## Proven pattern

1. Identify the exact filer and accession in the relevant quarter's `COVERPAGE.tsv`.
2. Feed the verified accession into existing analysis tooling for:
   - AUM / table value totals
   - holdings or stock counts
   - quarter-over-quarter changes against a verified baseline accession
3. Read back the computed output and confirm it still refers to the intended filer and quarter.

## When to prefer scripts over manual parsing

Prefer reusable scripts/tools when they already produce the requested summary metric or ranked comparison. This is usually safer and faster than manually rebuilding calculations from large `INFOTABLE` data.

## Minimal script-fix rule

If a reusable script fails because it hardcodes the wrong file location, make only the smallest fix needed to point it at the correct quarter-specific files (for example quarter `INFOTABLE.tsv` and matching `COVERPAGE.tsv`). Do not broaden the rewrite unless the script remains unverifiable after the path fix.

- Before editing a reusable script, inspect its current file/path assumptions or the exact command invocation and decide whether the failure is caused by wrong arguments, wrong working directory, or an actual hardcoded-path bug.
- Prefer invocation/path corrections over code edits: pass the correct quarter/path arguments, use absolute file paths, or wrap the existing utility with a short task-local command before considering any script modification.
- Do **not** edit shared skill/support code in the skills directory merely to accommodate the current task's filesystem layout.
- Only then make the smallest fix needed; do not broaden the rewrite unless the script remains unverifiable after the path fix.

## Validation after script use

- Confirm the script input accession number(s) match the intended filer(s).
- Confirm quarter labels and paths are correct.
- Confirm the final reported values or ranked identifiers are fully visible before writing the answer.

- If output is clipped, banner-only, or stops before the needed ranked rows, rerun with narrower filters or redirect to a file and inspect the exact final rows before answering.
- Treat partially visible rankings as unverified even if the visible prefix seems sufficient to guess the answer.
