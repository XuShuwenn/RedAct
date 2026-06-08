# Openpyxl Pivot Cache Pattern

Use this only when the task requires real Excel pivot-table objects and you are implementing them with openpyxl.

## Core rule

- For multiple pivot tables built from the same `SourceData`, reuse one shared pivot cache unless the workbook design clearly requires separate caches.
- After saving, reopen the workbook and confirm it still loads correctly and the pivot sheets are present.

## Practical guidance

- Build and verify `SourceData` first.
- Confirm the source range header row and data range are final before creating any pivot cache.
- Create the first pivot from that source range.
- Point subsequent pivots at the same cache rather than creating a fresh cache per sheet.
- Keep cache IDs consistent across the workbook.
- Save, reopen, and verify both workbook readability and pivot-backed output.
- After save/reopen, inspect every pivot sheet for populated results, not just object existence.
- If the workbook becomes unreadable after save/reload, or the reopened report sheets are blank, header-only, or placeholder shells, suspect cache inconsistency before changing the data pipeline.


## Do not rely on

- In-memory pivot metadata alone
- Sheet creation alone
- File existence alone

Always validate by reopening the saved workbook.