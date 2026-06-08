---
name: mars-clouds-clustering
description: "Optimize DBSCAN hyperparameters to find Pareto frontier of F1 score and centroid delta for Mars cloud annotations."
---

# Mars Cloud Clustering with DBSCAN

## When to Use

- Optimize clustering hyperparameters
- Find Pareto optimal solutions
- Evaluate citizen science vs expert annotations

## Input Data

- `/root/data/citsci_train.csv`: Citizen annotations (file_rad, x, y)
- `/root/data/expert_train.csv`: Expert annotations (file_rad, x, y)

**Before coding, inspect the real CSV headers and sample rows from both files.** If the files do not literally contain `file_rad`, `x`, and `y`, reconcile the actual schema first (for example, determine which column identifies the image and whether coordinates need renaming or extraction) before implementing clustering logic. If any logic depends on filename/path structure in `file_rad`, derive it from observed sample rows rather than assumptions.


## Hyperparameter Search

Grid search over:
- min_samples: 3-9 (integers)
- epsilon: 4-24 (step 2)
- shape_weight: 0.9-1.9 (step 0.1)

Before launching the full 847-combination sweep, run a small timing check on a few combinations. If runtime looks poor, restructure first rather than starting a long unattended run.

## Custom Distance Metric

DBSCAN uses:
```
d(a,b) = sqrt((w*Δx)² + ((2-w)*Δy)²)
```

Implementation guidance:
- Load both CSVs once and pre-group points by `file_rad`; do not re-read or re-filter the full datasets inside each parameter evaluation.
- Avoid Python-callable pairwise distance functions inside DBSCAN for the full sweep when possible; transform coordinates instead (e.g. scale x by `shape_weight` and y by `2-shape_weight`) so Euclidean distance matches the metric.
- Reuse per-image expert/citizen subsets across combinations.

## Evaluation Per Combination

1. Run DBSCAN on citizen science points per image
2. Match clusters to expert annotations (greedy, max 100px)
3. Compute F1 and average delta (Euclidean distance)
4. Only keep results with F1 > 0.5


Additional required rules:
- If DBSCAN finds no clusters for an image, set that image's `F1 = 0.0` and `delta = NaN`.
- If no cluster-expert matches are found for an image, set that image's `F1 = 0.0` and `delta = NaN`.
- Do not treat "both empty" as a perfect score.
- Average metrics across images, then keep only combinations with average `F1 > 0.5`.
- Apply the `F1 > 0.5` filter only after computing metrics for a hyperparameter combination.
- Do not fall back to including all combinations when none pass the `F1 > 0.5` filter.
- Iterate over images that actually have citizen points to cluster, and keep matching/evaluation work per image lightweight because it is repeated for every hyperparameter setting.
- Compute Pareto-optimal points with equality-aware dominance: a row is dominated if another row has `F1 >= current F1` and `delta <= current delta`, with at least one strict improvement.

**Validate the implementation against the spec before trusting results:**
- Check that clustering is run per image/group using the actual image identifier from the data.
- Confirm greedy matching uses a 100px maximum distance.
- Confirm `delta` is computed as average Euclidean centroid distance for matched pairs.


## Output

`/root/pareto_frontier.csv`:
```csv
F1,delta,min_samples,epsilon,shape_weight
```

- Round F1/delta to 5 decimals, shape_weight to 1 decimal
- Include all Pareto-optimal points


Before declaring completion, verify `/root/pareto_frontier.csv` was actually written, is non-empty, and is specification-compliant:
- Columns exactly: `F1,delta,min_samples,epsilon,shape_weight`
- `F1` and `delta` rounded to 5 decimals; `shape_weight` to 1 decimal
- Every row is Pareto-optimal and no dominated row remains
- Results only include combinations with `F1 > 0.5`
- Validate the complete file, not just `head` or a row count
- Spot-check at least one output row against the computation logic or intermediate results



## New Section

## Execution Discipline

- Follow the task's required interaction and tool/action format exactly; if an exact completion string is required, use it verbatim.
- If you write a script, inspect the saved file, then run it and check for syntax/runtime errors before relying on it.
- Do not stop at "script written", "job started", or inferred progress. If you run work asynchronously or in the background, wait/poll until it finishes, then verify the artifact.
- Report only progress directly supported by command output or file inspection.
- After any performance-driven rewrite, re-check the final implementation against the task requirements: DBSCAN per image, greedy matching with max 100px, F1/delta computation, `F1 > 0.5` filtering, and Pareto selection.