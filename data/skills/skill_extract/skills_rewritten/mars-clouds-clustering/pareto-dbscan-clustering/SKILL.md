---
name: pareto-dbscan-clustering
description: "Optimize DBSCAN hyperparameters with an anisotropic distance, evaluate against reference points per image, and extract a Pareto frontier balancing F1 (maximize) and distance (minimize)."
---

# Pareto-Optimal DBSCAN Clustering Against Reference Points

This skill provides a reusable workflow for hyperparameter search of DBSCAN with an anisotropic distance, evaluated against per-image reference annotations. It computes per-image matching, aggregates metrics with explicit missing-data rules, filters by a minimum average F1 threshold, and extracts the Pareto frontier that maximizes F1 while minimizing average matching distance.

## When to Use

Use this skill when you need to:
- Tune DBSCAN (or similar density clustering) for 2D point annotations keyed by image IDs
- Use an anisotropic distance inside clustering while evaluating matches with standard Euclidean distance
- Compute per-image F1 and average distance, handle images with no usable matches, and average across all expert-listed images
- Identify Pareto-optimal hyperparameters trading off F1 (maximize) vs. distance (minimize)

## Core Workflow

1) Data preparation
- Load two datasets: predicted/annotated points (e.g., citizen science) and reference points (e.g., expert labels).
- Ensure both contain: image identifier (e.g., file ID without variants) and numeric x,y coordinates.
- Group both datasets by the image identifier. Use the set of unique images from the reference dataset as the authoritative list to evaluate.

2) Anisotropic clustering distance
- Inside DBSCAN, use a weighted Euclidean metric of the form: sqrt((w*Δx)^2 + ((2-w)*Δy)^2).
- Implement this by scaling coordinates before clustering: scale x by w and y by (2-w), then use standard Euclidean metric. Validate scale factors are positive.
- Keep epsilon in the same weighted space as the scaled coordinates.

3) Per-image evaluation for a hyperparameter setting
- For each image in the reference set:
  - If there are no predicted points, set image F1 = 0.0 and delta = NaN and continue.
  - Run DBSCAN on the scaled predicted points with the candidate (epsilon, min_samples, weight).
  - Compute cluster centroids from non-noise clusters (labels >= 0) in the ORIGINAL coordinate space.
  - Greedy match centroids to reference points using standard Euclidean distance with the task-specified cutoff (e.g., 100 pixels). Enforce one-to-one matches (closest pairs first; skip pairs beyond the cutoff).
  - Let TP = number of matches. FP = unmatched centroids. FN = unmatched reference points. Compute image F1 via TP,FP,FN. If TP == 0, set delta = NaN for this image. Otherwise set delta to the mean distance over matched pairs only.

4) Aggregation across images
- Average F1 across all images from the reference set. Include images with F1 = 0.0 (e.g., no predicted points, no clusters, or no matches) in this average.
- Compute average delta across only the images that had at least one match (exclude NaN deltas). If no image has a match, the mean delta is NaN for this hyperparameter setting.

5) Filtering and Pareto frontier
- Discard hyperparameter settings whose average F1 does not meet the required threshold (e.g., > 0.5 or task-specified).
- When extracting the Pareto frontier, use only rows with numeric delta values. A point A dominates B if A.F1 >= B.F1 and A.delta <= B.delta, with at least one strict inequality. Keep only non-dominated points.
- Optionally sort the resulting frontier for presentation (e.g., by F1 descending, then delta ascending) without altering set membership.

6) Output
- Write the frontier to the required CSV schema and rounding rules specified by the task (e.g., round metrics to fixed decimals, ensure integer hyperparameters remain integers, and round continuous weights to the required precision).

## Verification

Perform these checks before finalizing results:
- Column presence and types: reference and predicted datasets both have the image ID and numeric x,y.
- Image set: number of images evaluated equals the number of unique images in the reference dataset.
- Distance usage: anisotropic metric only inside clustering; matching and delta use standard Euclidean distance.
- Matching correctness: one-to-one greedy matching with a hard maximum distance cutoff; unmatched are counted as FP (predicted) or FN (reference).
- Aggregation rules: F1 averaged over all reference images; delta averaged only over images with at least one match; verify the count of deltas used is reported or logged.
- Threshold filter: ensure the average F1 threshold is applied after aggregation.
- Pareto correctness: no frontier row is dominated by another; optionally run a pairwise dominance check.
- Output formatting: verify rounding and integer casting for hyperparameters; ensure CSV header and column order match requirements.

## Common Pitfalls

- Using the weighted distance for matching: matching and delta must use standard Euclidean distance, not the weighted metric.
- Averaging F1 over only images with matches: F1 must include zeros for images with no clusters or no matches.
- Averaging delta over all images: delta must exclude NaN values and only average over images with matches.
- Looping over the predicted image set: always iterate over the reference image set to avoid silently skipping reference-only images.
- Mishandling DBSCAN noise: exclude label -1 when computing cluster centroids.
- Mis-scaled epsilon: when scaling coordinates to implement anisotropy, epsilon operates in the scaled space; be consistent.
- Writing integer columns as floats: cast or format integer hyperparameters explicitly.
- Pareto including NaN deltas: exclude NaN-delta rows from the frontier because dominance comparisons require numeric deltas.

## Success Criteria

- Aggregated metrics adhere to the averaging rules across the full reference image set.
- Filtered results meet the minimum average F1 threshold.
- The Pareto frontier contains only non-dominated points (maximize F1, minimize delta).
- Output CSV schema, column order, rounding, and integer formatting match the task specification.

## Optional Script Usage

A helper module is provided to:
- Run DBSCAN with anisotropic scaling
- Compute cluster centroids (original coordinates)
- Greedy-match centroids to reference points with a cutoff and compute per-image F1 and mean delta
- Aggregate metrics across images with the specified averaging rules
- Extract and verify a Pareto frontier for maximizing F1 and minimizing delta

Typical integration pattern:
- Pre-group data by image once.
- Parallelize over the hyperparameter grid, reusing grouped data.
- For each combination, call the helper functions to compute per-image metrics, aggregate, filter by F1 threshold, and accumulate results for Pareto selection.
