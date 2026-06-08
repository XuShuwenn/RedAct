# Partial Latest-Year Policy

Use this when the newest year in an annual macro series is built from quarterly rows rather than a completed annual table entry.

## Rule
- Do not include a partial latest year automatically.
- Include it when the task calls for the latest available data and the workbook provides multiple visible quarters that can be aggregated consistently into a latest-year annual proxy.
- If the workbook shows only a genuinely thin partial year, or the task is silent and completed annual observations already answer it, restrict the final HP-filter/correlation sample to completed annual observations.
- Decide the policy before implementation and print it in the run output so later diagnostics can be checked against that choice.
- Prefer the direct annual sample when it already satisfies the task; quarterly aggregation is a conditional extension, not an automatic default.

## Required checks
- Inspect the workbook bottom rows and count how many quarters are visibly present for the latest year.
- Compare that visible count to the parser's matched latest-year quarter rows.
- If the parser captured fewer quarters than are visible, fix parsing before any statistical computation.
- If only a genuinely partial year is available, run the final analysis on completed years unless the task clearly says to include the partial year.

- After choosing annual-only vs. quarterly-derived latest year, verify the final merged overlap years/count still matches that choice; treat any contradiction as a hard stop.
- If the script reports a derived latest-year value from only one quarter, treat that as a reject-by-default outcome unless manual inspection confirms the workbook truly shows only one quarter and the task explicitly wants that partial year included.
- Compare the constructed latest-year annual value to the previous completed annual observation(s) as a basic plausibility check; if it is obviously out of scale with nearby years, re-check quarter capture and value-column selection before proceeding.

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