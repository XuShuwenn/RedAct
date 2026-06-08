# Partial Latest-Year Policy

Use this when the newest year in an annual macro series is built from quarterly rows rather than a completed annual table entry.

## Rule
- Do not include a partial latest year by default.
- Include it only if the task explicitly requires using the latest available partial-year data.
- Otherwise, restrict the final HP-filter/correlation sample to completed annual observations.

## Required checks
- Inspect the workbook bottom rows and count how many quarters are visibly present for the latest year.
- Compare that visible count to the parser's matched latest-year quarter rows.
- If the parser captured fewer quarters than are visible, fix parsing before any statistical computation.
- If only a genuinely partial year is available, run the final analysis on completed years unless the task clearly says to include the partial year.

## Minimal diagnostic to print
- `Latest year visible quarters: ...`
- `Latest year captured quarters: ...`
- `Latest year included in final sample: yes/no`
- `Final year span/count used for HP filter: ...`

## Do / Do Not
- Do: make the include/exclude decision explicit in the script output.
- Do: prefer the last completed annual observation set when instructions are silent.
- Do not: quietly average one quarter and treat it as a normal annual observation.
- Do not: report a correlation until the run visibly prints the final sample span and the correlation itself.