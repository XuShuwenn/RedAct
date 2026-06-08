---
name: scikit-survival
description: "Fit Cox proportional hazards model and compute concordance index using scikit-survival. Use when performing survival analysis, fitting Cox models, or evaluating survival predictions with concordance index."
---

# Cox Proportional Hazards Model

## Overview

Fit a Cox proportional hazards model to survival data and compute the concordance index (C-index) to evaluate model performance.

## Workflow

### Step 1: Load and Prepare Data

The input CSV has columns: time, event, feature1, feature2, feature3.

```python
import pandas as pd
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.metrics import concordance_index_censored
from sksurv.util import Surv

# Load survival data
df = pd.read_csv("/root/input.csv")
```

### Step 2: Create Survival Outcome

The survival outcome combines event indicator (1=event occurred, 0=censored) and time.

```python
y = Surv.from_arrays(
    event=df['event'].values,   # 1 = event, 0 = censored
    time=df['time'].values      # time of event or censoring
)
```

### Step 3: Extract Features

```python
X = df[['feature1', 'feature2', 'feature3']].values
```

### Step 4: Fit Cox Model

```python
model = CoxPHSurvivalAnalysis()
model.fit(X, y)
```

### Step 5: Predict and Evaluate

```python
# Predict risk scores on training data
risk_scores = model.predict(X)

# Compute Harrell's concordance index
c_index = concordance_index_censored(
    y['event'],
    y['time'],
    risk_scores
)[0]
```

### Step 6: Output Result

```python
with open("/root/output.txt", "w") as f:
    f.write(f"Concordance index: {c_index:.4f}\n")
```

## Complete Script

```python
import pandas as pd
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.metrics import concordance_index_censored
from sksurv.util import Surv

# Load CSV with columns: time, event, feature1, feature2, feature3
df = pd.read_csv("/root/input.csv")

# Create survival outcome (event, time)
y = Surv.from_arrays(event=df['event'].values, time=df['time'].values)

# Extract features
X = df[['feature1', 'feature2', 'feature3']].values

# Fit Cox proportional hazards model
model = CoxPHSurvivalAnalysis()
model.fit(X, y)

# Predict risk scores
risk_scores = model.predict(X)

# Compute concordance index
c_index = concordance_index_censored(y['event'], y['time'], risk_scores)[0]

# Write result
with open("/root/output.txt", "w") as f:
    f.write(f"Concordance index: {c_index:.4f}\n")
```

## Output Format

```
Concordance index: X.XXXX
```

Round to 4 decimal places.

## Key Reference

- `Surv.from_arrays(event=array, time=array)` — Create survival outcome from event and time arrays
- `CoxPHSurvivalAnalysis()` — Initialize Cox proportional hazards model
- `model.fit(X, y)` — Fit model on feature matrix and survival outcome
- `model.predict(X)` — Predict risk scores (higher = more risk)
- `concordance_index_censored(event, time, risk_scores)[0]` — Compute Harrell's C-index (range 0-1, 0.5 = random)

## About C-index

The concordance index measures how well the model ranks patients by risk:
- C-index = 1.0: perfect prediction
- C-index = 0.5: no better than random
- C-index < 0.5: predictions are worse than random (can be corrected by negating risk scores)