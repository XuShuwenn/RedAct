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

## Output Format

To `/root/output.txt`:
```
Concordance index: X.XXXX
```

Round to 4 decimal places.

## Using scikit-survival

```python
from scikit-survival import CoxPHSurvivalAnalysis


**Required model fidelity**
- If the task asks for a Cox proportional hazards model, use `CoxPHSurvivalAnalysis()` with default settings unless the task explicitly permits changes.
- Do **not** switch to `CoxnetSurvivalAnalysis` or another survival model, and do not silently add regularization or change hyperparameters just because warnings appear.
- If `fit()` emits warnings, treat them as investigation signals, not automatic failure: first check whether `model.fit(X, y)` completed and whether `model.score(X, y)` returns a valid concordance index before trying any workaround.


# Fit model
model.fit(X, y)
c_index = model.score(X, y)
```

## Concordance Index

- Measures predictive ability
- Range 0-1 (0.5 = random)
- Higher = better discrimination

## Tips

- Use CoxPHSurvivalAnalysis
- Prepare feature matrix X and event/time y
- Use .score() for concordance

- Build `y` as the survival outcome expected by scikit-survival, with event indicator and time together; do not pass separate plain arrays to `.fit()`.
- If `CoxPHSurvivalAnalysis` fit fails, debug the requested model before changing approach: verify `event` is boolean, `time` is numeric and positive, features are numeric with no missing values, and `X`/`y` are aligned.
- For numerical instability, try model-preserving fixes first: standardize features, remove constant or duplicate columns, and re-check data construction.
- If warnings occur during fitting, verify completion and scoring first; only deviate from the requested approach if the task explicitly authorizes it.
- For this skill's default task, report the concordance index from the plain `CoxPHSurvivalAnalysis()` model fit to the provided data.
