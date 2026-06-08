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

## Validation after script use

- Confirm the script input accession number(s) match the intended filer(s).
- Confirm quarter labels and paths are correct.
- Confirm the final reported values or ranked identifiers are fully visible before writing the answer.
