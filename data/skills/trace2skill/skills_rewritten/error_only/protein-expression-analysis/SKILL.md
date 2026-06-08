---
name: protein-expression-analysis
description: "Analyze protein expression data from cancer cell lines comparing control vs treated conditions with fold change calculations."
---

# Protein Expression Analysis

## When to Use

- Analyze proteomics data from cancer cell lines
- Compare control vs treated expression levels
- Calculate fold changes and statistics

## Execution Protocol

- Before any tool use or final response, identify whether the task/environment requires a specific action syntax, tool-call schema, or exact completion token.
- If such a protocol exists, follow it exactly for every action and at finish; it overrides habitual formatting.
- Do **not** substitute approximate formats or end with a narrative summary when an exact schema or completion string is required.
- Treat protocol compliance as blocking: a correct workbook edit can still fail if actions or completion are reported in the wrong format.


## Input Files

- `protein_expression.xlsx`: Two sheets ("Task" and "Data")
- Data has 200 proteins × 50 samples (log2-transformed)

## Steps

**Range anchor rule:** Treat the user/task specification as the source of truth for required output blocks. For this skill, stay focused on `C11:L20`, `B24:K27`, and `C32:D41`; only inspect nearby headers/labels needed to map proteins, sample names, and Control vs Treated columns.

- If workbook text, blank regions, or embedded worksheet instructions appear to mention other ranges or alternate step blocks, do not pivot unless the actual task requires it; verify the named target ranges directly and continue.
- If task prose and workbook labels disagree, inspect enough surrounding rows/columns to determine the workbook's actual destination layout, labels, and orientation, then follow that observed layout consistently.


**Inspection-to-edit handoff:** As soon as you have enough structure to act, explicitly convert findings into a cell-level write plan for the required blocks (`C11:L20`, `B24:K27`, `C32:D41`): identify the exact destination cells, the formula pattern for each block, and then perform the workbook edits. Do not end after workbook reconnaissance.


4. **Write back to the workbook**
   - Populate the required cells in `Task`; do not stop after inspecting or summarizing.
   - When filling many cells, test one representative formula first, then propagate the same pattern across the range.
   - Prefer a short standalone script for repeated formula insertion and generation across `C11:L20`, `B24:K27`, and `C32:D41`; avoid long inline shell one-liners for complex Excel formula strings.
   - Before bulk-filling any region, prove the write path end to end on one representative cell: write it, save, recalculate/reopen, read back the exact stored formula/value, and confirm the result behaves correctly in this environment.
   - Build formula strings only from workbook coordinates/rules you have already confirmed; verify exact sheet name and quote syntax for cross-sheet formulas before propagating them broadly.
   - Treat every write as untrusted until the tool/script returns a clear success signal; repeated truncation, suspicious escaping, malformed stored formulas, or partial script echoes are blocking execution failures.

  - If a command/script is truncated, cut off, or echoed only partially, assume the workbook was not updated correctly. Stop, rewrite the edit in a shorter standalone script, rerun it, and read back the target cell(s) before doing any recalc or downstream debugging.
  - After every representative write, reopen the workbook and inspect the exact stored formula text in that cell. If the saved formula is corrupted, incomplete, or different from what you intended, fix the write path first; do not speculate about locale, separators, or function compatibility until the stored formula itself is correct.
   - If programmatic edits are long or keep getting cut off, switch to a standalone script file instead of pasting long inline commands.

5. **Verify before finishing**
   - Save the workbook, reopen it, and inspect all required output blocks: `C11:L20`, `B24:K27`, and `C32:D41`.
   - Confirm full coverage and orientation: every required cell in those blocks should be filled appropriately based on the workbook's observed layout, not an assumed template. Check corners plus at least one interior cell in each block.
   - Read back representative cells from each region and confirm formulas reference the intended protein row, sample header, and Control/Treated grouping.
   - Recalculate and validate the workbook after writing. Prefer `/root/.codex/skills/xlsx/recalc.py` when available, or another real spreadsheet engine when possible.
   - Verify both stored formulas and evaluated outputs: after save/reload, ensure representative cells from lookup, statistics, and fold-change sections still contain the expected pattern and evaluate to sensible numeric results or intended blanks.
   - If recalculation reports `#NAME?`, `#VALUE!`, `#DIV/0!`, broken references, or function-compatibility errors, fix the first failing representative cell or formula family, save again, and re-verify before finishing.

  - Treat repeated recalc failures as a hard stop, not a warning. Do not declare completion while known validation errors remain in the required output regions.
  - When many cells fail, inspect one failing saved formula directly in the workbook. If it is malformed, prioritize a clean rewrite of that formula family across the block instead of debugging hypothetical engine behavior.
   - If real-engine recalculation is unavailable, use reopened formula inspection, dependency checks, and representative result cells as a weaker fallback.
   - Do not consider the task complete until the workbook has been saved, recalculated when possible, the edited ranges have been verified cleanly, and any task-specific completion protocol has been satisfied exactly.


6. **Use a one-cell formula gate before bulk fill**
   - Build each formula family first in one representative cell, save, reopen/recalculate, and confirm both the stored formula text and evaluated result are valid.
   - Only after that passes, propagate the same pattern across the rest of the target block.
   - If the first cell shows malformed syntax or errors such as `#NAME?` or `#VALUE!`, rewrite it immediately; do not continue filling the range with a broken pattern.
   - Treat function-name compatibility as part of this gate: if a candidate formula uses `STDEV.S`, `LET`, dynamic-array functions, or other newer names, recalculate that representative cell first and replace unsupported functions before any bulk fill.
   - For standard deviation specifically, test the exact function name in one target stats cell; if recalc shows `#NAME?`, switch to the workbook-compatible alternative (commonly `STDEV`) and retest before propagating.

**Execution checklist:** Before finishing, ensure all three output regions have been populated in the workbook: `C11:L20`, `B24:K27`, and `C32:D41`. Treat inspection as setup only; after confirming layout, write the outputs, save the file, reopen it, and verify the saved cells.


- If an initial write produced malformed formulas or corrupted cells anywhere, treat the workbook as suspect until you have revalidated all edited output blocks, not just a few sample cells.
- After any repair pass, run a block-level verification over every intended filled cell in `C11:L20`, `B24:K27`, and `C32:D41` (or an automated equivalent that checks coverage, stored-formula presence/pattern, and absence of formula errors), then inspect a few representatives manually.
- Do not rely on an unseen or opaque rewrite step by itself. If you switch to a standalone script, make the corrective logic inspectable in the session when possible, or compensate with stronger post-run verification that demonstrates what changed across the workbook.

7. **Finish only after actual in-session verification**
   - Do not treat writing formulas as completion.
   - Complete the save -> recalculate when possible -> reopen -> inspect workflow within the session before finishing.
   - If a required verification step has not been performed yet, the task is still unfinished; do not defer it to the user as a "next step."
   - If a recalculation helper or engine is not immediately available, keep searching for an in-environment verification method and only fall back to weaker checks when no real engine can be used.

- Verification is not just 'formula text exists'. For at least one representative lookup cell, explicitly confirm that the formula's **header row**, **first data row**, and **first value column** match the coordinate map you observed on `Data`.
- Trace one representative lookup end to end: target protein in `Task` -> matched protein row on `Data`; target sample header in `Task` -> matched sample column on `Data`; then confirm the formula references those aligned source ranges.
- If any representative formula combines coordinates from mixed contexts (for example, a header row from one observation and a value block from another), stop and rebuild that formula family before bulk verification.





## Preflight Checks

- Confirm the actual workbook filename and path before opening it; do not assume `protein_expression.xlsx` exists without checking.
- Inspect the workbook directly before writing formulas. Confirm sheet names, used ranges, the protein ID/symbol column, the sample header row, and where Control vs Treated labels appear.
- Inspect the `Task` sheet around the destination areas (`A11:L20`, `A24:K27`, `A32:D41`) so the output layout is taken from the workbook, not inferred from prose alone.
- If the workbook layout conflicts with the nominal description, follow the workbook's actual structure.
- If any inspection output is truncated or unclear, rerun a narrower inspection until the relevant rows/columns are fully visible.

1. **Pull expression data** (C11:L20 in Task sheet)
   - Match 10 target proteins (column A rows 11-20)
   - Match sample names from row 10
   - Use INDEX-MATCH or similar

2. **Calculate statistics** (rows 24-27, columns B-K)
   - For each protein: mean, stdev for Control and Treated
   - Row 9 shows Control (blue) vs Treated

3. **Fold change** (columns C-D, rows 32-41)
   - Log2 Fold Change = Treated Mean - Control Mean
   - Fold Change = 2^(Log2 Fold Change)

- Before any tool use, check whether the environment/task requires an exact interaction protocol or completion token; follow it exactly for every step and at finish.
- Resolve the workbook to the real on-disk path before editing (prefer an absolute path once found), verify it exists there, and use that same path consistently for open/save/reopen steps.
- Treat the live workbook layout as the implementation source of truth: inspect `Task!9:10`, `Task!A11:A20`, the destination areas around `A11:L20`, `A24:K27`, and `A32:D41`, plus the `Data` used range, protein-ID column, sample-header row, and starting sample column.
- Before writing any formulas, build the exact mapping table for this workbook: Task protein IDs/names -> `Data` row numbers, Task sample labels -> `Data` column numbers, and Control/Treated group membership -> the columns actually used by the statistics block.
- Verify the lookup keys actually exist before propagating formulas: confirm each target protein in `Task!A11:A20` is present in the `Data` protein ID/symbol column, and confirm each sample name in `Task!C10:L10` matches a `Data` header.
- Specifically inspect row 9 and row 10 in `Task` before writing statistics formulas. Confirm group membership from labels/headers rather than color alone, and determine whether Control and Treated samples occupy contiguous column blocks.
- Check whether the `Task` extraction grid already matches the `Data` sheet protein/sample order; when alignment is already present, prefer direct references over unnecessary lookup formulas.
- Record the confirmed coordinates/rules you will use before writing. If sheet previews are truncated or any mapping detail remains uncertain, inspect narrower row/column windows until the relevant labels are fully visible.

- Check the available scripting runtime before your first inspection/edit command. Prefer `python3` for scripts unless `python` is explicitly confirmed to exist; if one interpreter fails, switch immediately to the available one and continue.
- Do not burn the first workbook-inspection step on an unverified interpreter assumption.
- Before planning around any helper script, executable, or package, verify it exists at the exact path you intend to use. Do not assume `/root/.codex/skills/xlsx/recalc.py` or any other helper is present.
- If `/root/.codex/skills/xlsx/recalc.py` or another recalc engine is unavailable, immediately switch to the fallback validation path already allowed by this skill: save, reopen, inspect stored formulas, trace dependencies, and verify representative evaluated cells when possible.
- Before writing any lookup/statistics formula, freeze one explicit source coordinate map for `Data`: **protein lookup column**, **header row containing sample names**, **first data row**, and **first sample/value column**. Use those same coordinates in every related formula family.
- If inspections came from different row windows, display formats, or sheets, do **not** merge them implicitly. Re-inspect until you can state one consistent map such as `headers on row X`, `data start on row Y`, `samples start in column Z`; only then write formulas.
- For any `INDEX`/`MATCH` lookup, ensure the value matrix and the header lookup row come from the same confirmed source block. Do not pair a header row from one observed context with a value range from another.
- Before concluding inspection, state the concrete next write step to yourself: which block you will fill first, one representative destination cell in that block, and the exact formula/reference pattern it will test.
- Once the representative cell works, continue immediately to populate the remaining required cells; do not pause at a descriptive summary of workbook structure.
- Before finishing, confirm both: (a) the workbook was actually modified and saved, and (b) any task-required completion/action token was emitted exactly as instructed.


## Important Notes

- Don't modify file format, colors, or fonts
- No macros or VBA
- Use formulas not hard-coded values
- Sample names have prefixes like "MDAMB468_BREAST_TenPx01"


- This is an edit-the-file task, not a report-only task: workbook inspection is only preparation for writing the requested outputs.
- Build formulas only from confirmed workbook structure; do not assume `Data` ranges, header positions, sample-group splits, or destinations without inspection.
- Build Excel formulas as plain strings with exact sheet/range syntax; double-check quotes and parentheses before writing.
- Prefer the simplest proven cross-sheet reference form first (for example `Data!C5` or `Data!$C$5`), then confirm the saved workbook preserved that exact syntax.
- Prefer widely supported functions such as `INDEX`, `MATCH`, `AVERAGE`, `IF`, `SUMPRODUCT`, `COUNT`/`COUNTIF`/`COUNTIFS`, and basic arithmetic.
- For standard deviation, prefer the workbook-compatible function after testing/recalc; use `STDEV.S` only if you have confirmed it recalculates successfully in the target engine, otherwise use `STDEV` and verify again after save/reopen/recalc.
- Do **not** rely on newer or dynamic-array functions such as `FILTER` unless you have confirmed they recalculate successfully in this workbook environment.
- Treat truncated commands, partial tool output, or malformed first writes as blocking issues: fix the write path, then verify the saved workbook rather than guessing at alternate formula syntax.

- If a first bulk write was corrupted, a later spot check is not enough. Re-check the entirety of each edited target block, or run an automated scan over all cells in those blocks, before declaring success.
- When executing a repair script, avoid blind trust: either inspect the script contents in-session or verify its effects with comprehensive before/after cell checks across the required ranges.

- Do not declare completion after only printing formula strings or checking a few cells; verify the full required output areas are filled coherently.
- Follow any task-specific tool-use or completion protocol outside this skill exactly as given.

- This is an edit-the-file task: inspect workbook structure first, then write native Excel formulas into the workbook, not pasted reports or hard-coded results.
- Do not stop after reconnaissance, analysis, or a narrative summary. The deliverable is the edited workbook with the required ranges filled.
- Do not force lookup formulas when a simpler confirmed mapping works; direct references are often more robust when Task/Data are already aligned.
- For cross-sheet expression lookups, use fully qualified references and a range wide enough to include every populated sample column; do not guess a short range if the used range extends farther.

- Do **not** guess `Data` offsets like `row 1`, `row 2`, or `column D` from habit. Wrong: `=INDEX(Data!$D$2:$BA$201, ..., MATCH(C$10, Data!$D$1:$BA$1, 0))` when you have not confirmed that row 1 is the sample-header row and column D is the first sample column. Right: derive the header row, first data row, and first sample column from inspection, then build both the header range and value matrix from that same block.
- When the output section transposes or reorders the source data, write down the mapping first, then generate formulas from that mapping instead of copying a pattern blindly.
- Treat spreadsheet recalculation as both a math check and a function-compatibility check: if a formula family is structurally correct but unsupported, replace only the incompatible function and verify again.
- If `pandas` is unavailable or unnecessary, continue with `openpyxl`; it is sufficient for inspecting workbook structure, preserving formatting, and writing formulas directly.
- If a stored formula comes back malformed, assume the write method corrupted it; switch to a standalone script and rewrite before doing further debugging.
- If a representative formula fails recalc or shows `#NAME?`, `#VALUE!`, or similar, treat that failing cell as the debugging starting point: inspect the stored formula text there, correct the syntax, reference, or function choice, then retest before filling the rest of the range.
- When a downstream block shows `#DIV/0!`, blanks, or similar errors, trace back to the earliest dependency block (usually the expression pull in `C11:L20`) before changing later formulas.
- Do not claim success after printing formulas or running a script once; claim completion only after an observed successful write, reopen, and verification loop.

- Recalculation helpers are optional, not assumed. Check availability first, then use them; otherwise complete the strongest available fallback verification instead of failing on a missing script.
- Recalculation errors are blocking, not informational. If recalc reports `#NAME?`, `#VALUE!`, `#DIV/0!`, or similar anywhere in the required output blocks, perform another write-fix-save-recalc loop and do not stop until the affected formula family is corrected.
- External validation state is authoritative: if your latest recalc/read-back checks still show unresolved errors or malformed saved formulas, the task is not complete.
- Debug in this order: (1) confirm the tool/script executed fully, (2) confirm the saved formula text is exactly correct in representative cells, (3) run recalc, (4) only then investigate function compatibility or workbook-specific behavior.
- Do not finish with "the user can open/recalculate later" when verification/recalculation is part of the requested workflow.



## Tips

- openpyxl for Excel reading/writing
- Prefer `openpyxl` for workbook inspection and formula-preserving edits; use it as the default fallback when `pandas` or other analysis libraries are unavailable.
- Use pandas for data manipulation
- Verify log2 transformation for fold change


- Prefer shorter, complete scripts over long inline commands when editing many cells.
- After writing formulas, perform a write-read-recalc loop: save the workbook, recalculate when possible, reopen once to inspect stored formulas, then reopen with `data_only=True` (or equivalent) to confirm computed values are populated and free of `#NAME?`, `#VALUE!`, `#DIV/0!`, or similar errors.
- Default recalc command: run `/root/.codex/skills/xlsx/recalc.py` on the edited workbook after saving to confirm the formulas are accepted by the spreadsheet engine.
- Use recalculation as a diagnostic step: note which cells still show errors after recalc, then trace those specific formulas back to the protein-row mapping, sample-column mapping, compatibility choice, or sparse-data handling instead of reworking the whole sheet.
- If your writing library does not evaluate formulas, use an external spreadsheet engine or provided recalculation step before the final validation read.
- If errors appear, rewrite the affected formulas, save again, and repeat verification until the target cells evaluate cleanly.

- For repeated workbook edits, prefer one short script that inspects the workbook and writes all target ranges in one pass.
- Use representative checks from all three output regions over a single spot check so mapping mistakes are caught early.

