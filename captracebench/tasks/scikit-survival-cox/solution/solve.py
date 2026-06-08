#!/usr/bin/env python3
"""Solve scikit-survival-cox task."""

import pandas as pd
from sksurv.linear_model import CoxnetSurvivalAnalysis

def main():
    df = pd.read_csv("/root/input.csv")

    X = df[['feature1', 'feature2', 'feature3']].values
    y = [(bool(e), t) for e, t in zip(df['event'], df['time'])]
    y = pd.DataFrame(y, columns=['event', 'time']).to_records(index=False)

    model = CoxnetSurvivalAnalysis(l1_ratio=0.99)
    model.fit(X, y)

    # Get concordance index
    c_index = model.score(X, y)

    result = f"Concordance index: {c_index:.4f}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()