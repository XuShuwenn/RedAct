---
name: pareto-dbscan-tuning
description: "Tune DBSCAN with an anisotropic distance via coordinate scaling, evaluate F1 vs. localization error across grouped images, and extract the Pareto frontier."
---

# Pareto-Oriented DBSCAN Hyperparameter Tuning

Optimize DBSCAN hyperparameters when clustering point annotations with a custom anisotropic distance. Evaluate per-image F1 (agreement) and localization error (delta), average across images, then extract the Pareto frontier (maximize F1, minimize delta).

## When to Use

Use this skill when you need to:
- Cluster 2D points using DBSCAN with a directional/anisotropic distance.
- Compare clusters to reference points (e.g., expert annotations).
- Balance two objectives (e.g., F1 vs. average matched distance) via a Pareto frontier.
- Evaluate across grouped subsets (e.g., per image) and aggregate with strict missing-data handling.

## Core Workflow

1. Inspect and organize data
   - Identify grouping key (e.g., image ID), and columns for x and y.
   - Build two dictionaries keyed by the grouping key:
     - detected_points[key] → Nx2 array of citizen-science points
     - reference_points[key] → Mx2 array of expert points
   - Define the full set of keys from the reference dataset; all these groups must be evaluated, even if detected points are missing.

2. Implement anisotropic distance via coordinate scaling
   - For a weight w in [w_min, w_max], define:
     - x' = w * x
     - y' = (T - w) * y   (use T=2.0 if a two-axis tradeoff is intended)
   - Run DBSCAN on the scaled coordinates using standard Euclidean distance. Keep original coordinates for centroid computation.
   - This approach avoids O(n^2) precomputed distance matrices and is usually faster and more memory-efficient than custom metric callables.

3. Cluster and compute centroids per group
   - For each group key in the reference set:
     - If no detected points: set F1 = 0.0 and delta = NaN for this group.
     - Otherwise, transform points by scaling, run DBSCAN (eps, min_samples), and get labels.
     - Exclude noise (label = -1).
     - For each cluster label, compute centroid in the ORIGINAL coordinate space.

4. Greedy matching against reference points (localization evaluation)
   - Use standard Euclidean distance for matching, NOT the anisotropic metric.
   - Create all centroid–reference pairs under a max distance threshold (e.g., 100 units). Sort by distance ascending.
   - Greedily assign pairs without reusing a centroid or reference point.

5. Per-group metrics and aggregation
   - For each group:
     - n_clusters = number of non-noise clusters
     - n_refs = number of reference points
     - n_matches = number of greedy matches
     - precision = n_matches / n_clusters (0 if n_clusters=0)
     - recall = n_matches / n_refs (0 if n_refs=0)
     - F1 = 2 * precision * recall / (precision + recall) (0 if both denom terms are 0)
     - delta_group = mean distance of matched pairs; if no matches, delta_group = NaN
   - Aggregation across groups:
     - Average F1 across ALL reference groups (include zeros).
     - Average delta across groups with valid matches only (exclude NaNs).

6. Grid search and parallelization
   - Evaluate a full grid over (min_samples, epsilon, shape_weight=w), using joblib/multiprocessing.
   - Load and group data once; pass immutable structures to workers to avoid reloading.
   - Prefer coordinate scaling over precomputed NxN distance matrices for performance and memory.

7. Filter and compute Pareto frontier
   - Discard configurations with average F1 below a meaningful threshold (e.g., F1 > 0.5, or task-specific).
   - Pareto-optimal = non-dominated points where no other point has both higher F1 and lower delta.
   - Sort results for readability (e.g., F1 desc, delta asc).

8. Output formatting
   - When writing to CSV or reports, enforce fixed decimal places with formatted strings (e.g., F1/delta to 5 decimals, shape_weight to 1 decimal). Do not rely solely on DataFrame rounding for fixed-width formats.

## Implementation Details

- Coordinate scaling for anisotropy:
  - Use x' = w * x and y' = (T - w) * y, with T typically 2.0.
  - w > 1 attenuates y distances; w < 1 attenuates x distances.
- DBSCAN:
  - Use metric='euclidean' on scaled coordinates.
  - Exclude label -1 as noise when computing centroids.
- Greedy matching:
  - Always compute matching distances with standard Euclidean distance.
  - Enforce a max matching distance; unmatched points contribute to lower recall/precision, not to delta.
- Aggregation:
  - Iterate over ALL reference groups, not just those with detected points.
  - Include F1=0 for groups with no detected points or no matches.
  - Exclude NaN deltas from the delta average (average only where matches exist).
- Pareto frontier:
  - Convert to a minimization problem internally (flip signs for objectives meant to be maximized) or explicitly compare objective pairs.
  - A dominates B if it is at least as good in all objectives and strictly better in at least one.

## Verification

- Group coverage:
  - The number of per-group F1 entries should equal the number of unique reference groups.
  - Count how many groups contributed to delta; delta average denominator must equal this count (excluding NaNs).
- Matching correctness:
  - No centroid or reference point should be matched more than once.
  - Distances in matches must be ≤ max distance threshold.
- Noise handling:
  - Confirm label -1 points are excluded from centroid calculation.
- Objective metrics:
  - For a synthetic case with no overlaps, verify F1=0 and delta=NaN.
  - For exact overlaps within threshold, verify high precision/recall and finite delta.
- Pareto validation:
  - For any pair of reported Pareto points A and B, ensure neither strictly dominates the other on (F1, delta).
- Output formatting:
  - Spot-check that F1 and delta are written with exactly 5 decimal places and shape_weight with 1 decimal place.

## Common Pitfalls

- Using the anisotropic/custom metric for matching instead of standard Euclidean. Always match with standard Euclidean.
- Ignoring reference groups with no detected points. These must contribute F1 = 0 to the average.
- Averaging delta over all groups, including NaNs. Only average over groups with at least one match.
- Counting noise (label = -1) as clusters when computing precision. Exclude noise.
- Building full precomputed distance matrices for every combination and group. This is slow and memory-heavy; prefer coordinate scaling and Euclidean metric.
- Incorrect Pareto logic (e.g., using the unfiltered set, or requiring strict improvements in both objectives only). Use the standard non-dominance definition.
- Floating point grid steps causing key mismatches or instability (e.g., 0.899999...). Round shape_weight for logging/indexing and output formatting.
- Relying on DataFrame rounding alone for CSV rendering when fixed decimals are required. Use formatted strings.

## Optional Script Usage

This skill ships a reusable helper module with:
- greedy matching without reuse
- F1/delta computation with NaN handling
- Pareto frontier mask generation
- Fixed-decimal formatting

Example (pseudocode):
- Transform points with x' = w*x, y' = (T-w)*y; run DBSCAN and compute centroids.
- Use `greedy_match_distances(centroids, experts, max_distance)` to get distances for matches.
- Compute `f1, delta = f1_and_delta(match_distances, n_clusters, n_experts)`.
- Aggregate across groups, filter by F1, then compute `mask = pareto_frontier(values, maximize=[True, False])`.

## Success Criteria

- A CSV/report of Pareto-optimal (F1, delta, hyperparameters) where:
  - F1 and delta are aggregated with the specified inclusion/exclusion rules.
  - Matching uses standard Euclidean with a max distance threshold.
  - Noise points are excluded from cluster counts.
  - F1 and delta are formatted with fixed decimal precision.
- Pareto points are non-dominated on (maximize F1, minimize delta).
