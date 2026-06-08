---
name: scikit-survival-cox
description: "Fit Cox proportional hazards model to survival data using scikit-survival and extract concordance index."
---

# Cox Proportional Hazards Model

## When to Use

- Fit survival analysis models
- Calculate concordance index
- Use scikit-survival library

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

## Using scikit-survival

```python
from scikit-survival import CoxPHSurvivalAnalysis


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
- If warnings occur during fitting, treat them as investigation signals, not automatic failure: first confirm `model.fit(X, y)` completed, then check whether `model.score(X, y)` returns a finite concordance index.
- Do **not** treat warnings alone as permission to add penalization, switch estimators, or otherwise change the requested model unless the task explicitly authorizes that change.
- If `CoxPHSurvivalAnalysis` fit fails, debug the requested model before changing approach: verify `event` is boolean, `time` is numeric and positive, features are numeric with no missing values, and `X`/`y` are aligned.
- Use this recovery order when the plain default fit is unstable: confirm `y` was built correctly with `Surv.from_arrays`, confirm features are numeric and aligned with no missing values, inspect highly correlated or near-duplicate predictors, drop constant or exact-duplicate feature columns, standardize features, then retry the same `CoxPHSurvivalAnalysis()` model.
- After any warning or retry, explicitly verify that `model.fit(X, y)` completed and `model.score(X, y)` returns a finite concordance index before writing output.
- For this skill's default task, fit the plain `CoxPHSurvivalAnalysis()` model first and report that concordance index whenever it works.
- If the surrounding task specifies an exact tool-use or completion format, follow that protocol exactly in addition to these modeling instructions.
- Write `/root/output.txt` exactly as `Concordance index: {c_index:.4f}`.
