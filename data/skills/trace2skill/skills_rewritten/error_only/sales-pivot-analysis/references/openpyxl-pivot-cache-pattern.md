# Openpyxl Pivot Cache Pattern

Use this only when the task requires real Excel pivot-table objects and you are implementing them with openpyxl.

## Core rule

- For multiple pivot tables built from the same `SourceData`, reuse one shared pivot cache unless the workbook design clearly requires separate caches.
- After saving, reopen the workbook and confirm it still loads correctly and the pivot sheets are present.

## Practical guidance

- Build and verify `SourceData` first.
- Create the first pivot from that source range.
- Point subsequent pivots at the same cache rather than creating a fresh cache per sheet.
- Keep cache IDs consistent across the workbook.
- If the workbook becomes unreadable after save/reload, suspect cache inconsistency before changing the data pipeline.

## Do not rely on

- In-memory pivot metadata alone
- Sheet creation alone
- File existence alone

Always validate by reopening the saved workbook.