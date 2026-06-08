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

## Output Format

To `/root/output.txt`:
```
Concordance index: X.XXXX
```

Round to 4 decimal places.

After writing `/root/output.txt`, read it back and confirm it exactly matches the required single-line format: `Concordance index: X.XXXX`.

- If the surrounding task or system message requires an exact completion token or final-response protocol (for example, a literal sentinel such as `ACTION: TASK_COMPLETE`), emit that exact string and do not substitute a prose summary.
- Before your final response, check both: `/root/output.txt` has the required contents, and your chat response matches any externally specified completion format exactly.


## Using scikit-survival

```python
from scikit-survival import CoxPHSurvivalAnalysis


- Before writing the full script, sanity-check the actual installed API for this library/package family if there is any uncertainty. In particular, for scikit-survival use `from sksurv.linear_model import CoxPHSurvivalAnalysis`; do **not** assume lifelines-style names such as `CoxPHFitter` exist in `sksurv`.
- If imports fail or you are unsure about class names, inspect the installed module first, then code against the confirmed interface.


**Required model fidelity**
- If the task asks for a Cox proportional hazards model, use `CoxPHSurvivalAnalysis()` with default settings unless the task explicitly permits changes.
- Do **not** switch to `CoxnetSurvivalAnalysis` or another survival model, and do not silently add regularization or change hyperparameters just because warnings appear.
- If `fit()` emits warnings, treat them as investigation signals, not automatic failure: first check whether `model.fit(X, y)` completed and whether `model.score(X, y)` returns a valid concordance index before trying any workaround.

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
- Use `.score(X, y)` for concordance when it returns a valid result.
- If you need to verify concordance explicitly, compute risk scores with `model.predict(X)` and then use `concordance_index_censored(y['event'], y['time'], risk_scores)[0]`.
- Before coding, verify you are using the scikit-survival API for this skill: `from sksurv.linear_model import CoxPHSurvivalAnalysis`, not similarly named classes from other survival libraries.
- Keep the default workflow: inspect the CSV schema, build `X` and `y` correctly, fit plain `CoxPHSurvivalAnalysis()` first, and report that concordance index if scoring succeeds.
- Debug in this order before diagnosing numerical instability or changing models: (1) inspect the actual script/file contents for truncated or incomplete lines, imports, or assignments; (2) rerun and read the exact exception; (3) verify `X`/`y` construction and dtypes; only then consider data-conditioning issues.
- Do **not** attribute failure to collinearity, instability, or data properties while the script is incomplete, partially edited, or failing for a coding/configuration reason.

- If warnings occur during fitting, treat them as investigation signals, not automatic failure: first confirm `model.fit(X, y)` completed, then check whether `model.score(X, y)` returns a finite concordance index.
- Do **not** treat warnings alone as permission to add penalization, switch estimators, or otherwise change the requested model unless the task explicitly authorizes that change.

- Do **not** replace `CoxPHSurvivalAnalysis()` with `CoxnetSurvivalAnalysis` or any alternative just because the first run failed. First prove the default Cox PH implementation itself is correctly coded and that the failure is genuinely model/data-related rather than a syntax, import, truncation, dtype, or parameter mistake.
- If you ever are explicitly allowed to try an alternative estimator, validate that new estimator with a minimal known-valid parameterization and confirm it runs before treating it as the solution.
- If `CoxPHSurvivalAnalysis` fit fails, debug the requested model before changing approach: verify `event` is boolean, `time` is numeric and positive, features are numeric with no missing values, and `X`/`y` are aligned.
- Use this recovery order when the plain default fit is unstable: confirm `y` was built correctly with `Surv.from_arrays`, confirm features are numeric and aligned with no missing values, inspect highly correlated or near-duplicate predictors, drop constant or exact-duplicate feature columns, standardize features, then retry the same `CoxPHSurvivalAnalysis()` model.
- After any warning or retry, explicitly verify that `model.fit(X, y)` completed and `model.score(X, y)` returns a finite concordance index before writing output.
- For this skill's default task, fit the plain `CoxPHSurvivalAnalysis()` model first and report that concordance index whenever it works.
- If the surrounding task specifies an exact tool-use or completion format, follow that protocol exactly in addition to these modeling instructions.
- Write `/root/output.txt` exactly as `Concordance index: {c_index:.4f}`.

- Treat import errors for survival-model classes as a stop signal: verify the installed `sksurv` API before continuing, rather than guessing alternate class names.
- Do **not** write `/root/output.txt`, report a concordance index, or declare completion until the full pipeline has run end-to-end: read CSV, build `X`/`y`, fit the model, compute a finite concordance index, write the file, then read the file back and confirm exact format.
- If you edit the script during debugging, rerun the entire script after the last edit and use that successful run as the only basis for the reported output.

