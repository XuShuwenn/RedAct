---
name: scikit-survival-cox
description: "Fit Cox proportional hazards model to survival data using scikit-survival and extract concordance index."
---

# Cox Proportional Hazards Model

## When to Use

- Fit survival analysis models
- Calculate concordance index
- Use scikit-survival library


## Execution Protocol

## Execution Protocol

- Treat any surrounding system/task instructions about tool invocation format, message structure, or completion tokens as mandatory. Follow that protocol exactly, even if examples in this skill are plain Markdown/Python.
- If the environment requires a specific completion string or action syntax, use it exactly; do **not** substitute conversational wrap-up text.
- Apply this skill's modeling guidance within the required execution interface, not instead of it.

## Input

File `/root/input.csv` with columns:
- time
- event
- feature1
- feature2
- feature3
- 20 rows of data

- Read `/root/input.csv` first to confirm the actual schema before constructing `X` and `y`.
- Verify that `time` and `event` columns exist, there are 20 rows, and identify feature columns from the file contents rather than assuming blindly.
- Confirm `time` is numeric, `event` has a sensible event indicator representation, and feature columns used in `X` are numeric.
- Inspect a few rows and dtypes before modeling so you confirm the actual `time`, `event`, and feature schema from the file rather than relying only on expected column names.
- Use that inspection to verify the event encoding can be converted cleanly to boolean, there is at least one event and one non-event row, selected feature columns are the intended numeric predictors, and there are no missing values in `time`, `event`, or selected features.
- Before writing the full script, verify the installed `sksurv` API if there is any uncertainty about imports or class names; treat import uncertainty as a stop signal, not a cue to guess.

## Output Format

To `/root/output.txt`:
```
Concordance index: X.XXXX
```

Round to 4 decimal places.

Write `/root/output.txt` only after the full pipeline succeeds end-to-end: read CSV, build `X` and `y`, fit the model, and obtain a finite concordance index.

After writing `/root/output.txt`, read it back and confirm it exactly matches the required single-line format: `Concordance index: X.XXXX`.

- This read-back is mandatory: verify both the numeric value and the exact single-line formatting before finishing, and use the read-back value from `/root/output.txt` as the source of truth for any final response or completion action.
- If any traceback occurs, or fitting/scoring does not complete, do **not** write `/root/output.txt` yet.
- If you edited the script while debugging, rerun the entire workflow after the last edit and use only that clean successful run as the basis for the output file.
- Before your final response, check both: `/root/output.txt` has the required contents, and your chat response matches any externally specified completion format exactly.


## Using scikit-survival

```python
from scikit-survival import CoxPHSurvivalAnalysis


- Before writing the full script, sanity-check the actual installed API for this library/package family if there is any uncertainty. In particular, for scikit-survival use `from sksurv.linear_model import CoxPHSurvivalAnalysis`; do **not** assume lifelines-style names such as `CoxPHFitter` exist in `sksurv`.
- If imports fail or you are unsure about class names, inspect the installed module first, then code against the confirmed interface.


**Required model fidelity**
- If the task asks for a Cox proportional hazards model, use `CoxPHSurvivalAnalysis()` with default settings first.
- Do **not** switch to `CoxnetSurvivalAnalysis` or another survival model just because warnings appear or the first attempt fails.
- If `fit()` emits warnings, treat them as investigation signals, not automatic failure: first check whether `model.fit(X, y)` completed and whether `model.score(X, y)` returns a valid finite concordance index.
- Only if the plain default Cox PH path is correctly coded, rerun, and still fails or produces no finite concordance index for confirmed numerical reasons, you may make one narrowly scoped retry within the same estimator family using standardized features and, if supported by the installed API and permitted by the task, a very small stabilization value such as `CoxPHSurvivalAnalysis(alpha=1e-4)`. Report the unregularized result whenever the plain fit completes and scores successfully.
from sksurv.util import Surv
from sksurv.metrics import concordance_index_censored


# Fit model
model.fit(X, y)
c_index = model.score(X, y)
```

## Concordance Index

- Measures predictive ability
- Range 0-1 (0.5 = random)
- Higher = better discrimination

## Tips

- Use `CoxPHSurvivalAnalysis`.
- Prepare feature matrix `X` and build `y` with `Surv.from_arrays(event=df['event'].astype(bool), time=df['time'])`; do not pass separate plain arrays to `.fit()`.
- If the script has an incomplete, missing, or malformed target/label assignment, fix `y` construction first before investigating warnings, convergence, or model choice. For this skill, repair it by rebuilding `y` with `Surv.from_arrays(...)` and rerun the full pipeline.
- Use `.score(X, y)` for concordance when it returns a valid result.
- If you need to verify concordance explicitly, compute risk scores with `model.predict(X)` and then use `concordance_index_censored(y['event'], y['time'], risk_scores)[0]`.
- Before coding, verify you are using the scikit-survival API for this skill: `from sksurv.linear_model import CoxPHSurvivalAnalysis`, not similarly named classes from other survival libraries.
- Keep the default workflow: inspect the CSV schema, build `X` and `y` correctly, fit plain `CoxPHSurvivalAnalysis()` first, and report that concordance index if scoring succeeds.
- Use this execution order strictly: inspect schema and dtypes -> confirm/verify `sksurv` API if needed -> code the default Cox PH workflow -> run end-to-end -> confirm finite `model.score(X, y)` -> write `/root/output.txt` -> read it back -> emit the exact required completion token.
- Debug in this order before diagnosing numerical instability or changing models: (1) inspect the actual script/file contents for truncated or incomplete lines, especially `y`/target assignments, imports, and feature definitions; (2) rerun and read the exact exception; (3) verify `X`/`y` construction and dtypes, with `y` rebuilt via `Surv.from_arrays(...)` if needed; only then consider data-conditioning issues.
- Do **not** attribute failure to collinearity, instability, or data properties while the script is incomplete, partially edited, or failing for a coding/configuration reason.

- If warnings occur during fitting, treat them as investigation signals, not automatic failure: first confirm `model.fit(X, y)` completed, then check whether `model.score(X, y)` returns a finite concordance index.
- Do **not** treat warnings alone as permission to switch estimators or make large modeling changes. If the plain fit completes and `.score(X, y)` is finite, use that result. If recovery is explicitly allowed and the plain default Cox PH fit is unusable after validation, prefer at most one tiny same-estimator fallback before considering any different model family.

- Do **not** replace `CoxPHSurvivalAnalysis()` with `CoxnetSurvivalAnalysis` or any alternative just because the first run failed. First prove the default Cox PH implementation itself is correctly coded and that the failure is genuinely model/data-related rather than a syntax, import, truncation, dtype, or parameter mistake.
- If you ever are explicitly allowed to try an alternative estimator, validate that new estimator with a minimal known-valid parameterization and confirm it runs before treating it as the solution.
- If `CoxPHSurvivalAnalysis` fit fails, debug the requested model before changing approach: verify `event` is boolean, `time` is numeric and positive, features are numeric with no missing values, and `X`/`y` are aligned.
- When debugging fit issues, also inspect event counts so you can distinguish malformed survival targets from optimizer instability.
- Use this recovery order when the plain default fit is unstable: confirm `y` was built correctly with `Surv.from_arrays`, confirm features are numeric and aligned with no missing values, inspect highly correlated or near-duplicate predictors, drop constant or exact-duplicate feature columns, standardize features, then retry the same `CoxPHSurvivalAnalysis()` model; only if instability still clearly remains may you try at most one tiny same-estimator fallback such as `CoxPHSurvivalAnalysis(alpha=1e-4)`.
- After any warning or retry, explicitly verify that `model.fit(X, y)` completed and `model.score(X, y)` returns a finite concordance index before writing output.
- For this skill's default task, fit the plain `CoxPHSurvivalAnalysis()` model first and report that concordance index whenever it works.
- If the surrounding task specifies an exact tool-use or completion format, follow that protocol exactly in addition to these modeling instructions.
- Write `/root/output.txt` exactly as `Concordance index: {c_index:.4f}`.

- Treat import errors for survival-model classes as a stop signal: verify the installed `sksurv` API before continuing, rather than guessing alternate class names.
- Do **not** write `/root/output.txt`, report a concordance index, or declare completion until the full pipeline has run end-to-end: read CSV, build `X`/`y`, fit the model, compute a finite concordance index, write the file, then read the file back and confirm exact format.
- If you edit the script during debugging, rerun the entire script after the last edit and use that successful run as the only basis for the reported output.
- Prefer a single end-to-end Python script for this task: read `/root/input.csv`, validate schema/dtypes, build `X` and `y`, fit the model, compute the concordance index, write `/root/output.txt`, then read the file back to verify the exact required line.
- If fitting emits warnings but `model.fit(X, y)` completes and `model.score(X, y)` is finite, use that concordance index and finish; warnings by themselves do not invalidate the required output.
- Keep `/root/output.txt` minimal: write only the single required line with no extra labels, commentary, or additional metrics.
- Before finishing, rerun the final end-to-end script or metric computation once more and confirm the concordance index and `/root/output.txt` contents are unchanged.

