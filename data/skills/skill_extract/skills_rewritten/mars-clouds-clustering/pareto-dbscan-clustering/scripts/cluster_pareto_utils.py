#!/usr/bin/env python3
"""Utilities for DBSCAN-based clustering evaluation and Pareto frontier extraction.

Functions
- scale_points(points, w): apply anisotropic scaling for clustering
- dbscan_labels(points, eps, min_samples, w): run DBSCAN with weighted metric via scaling
- cluster_centroids(points, labels): centroids in original coordinates for non-noise clusters
- greedy_match(a, b, max_dist): one-to-one greedy matching with Euclidean distance cutoff
- image_metrics(pred_points, ref_points, eps, min_samples, w, max_match_dist): per-image F1 and mean delta
- aggregate_metrics(metrics): average F1 over all images; average delta over images with matches only
- pareto_frontier_indices(f1s, deltas): non-dominated indices for maximize(F1), minimize(delta)
- verify_pareto(f1s, deltas, idxs): check that selected indices are not dominated

Notes
- Use anisotropic metric only inside clustering; matching uses standard Euclidean distance.
- Validate scaling factors are positive: scale_x = w, scale_y = 2 - w.
"""

from __future__ import annotations
import math
from typing import List, Tuple, Optional, Dict

import numpy as np
from sklearn.cluster import DBSCAN


def scale_points(points: np.ndarray, w: float) -> np.ndarray:
    """Scale 2D points for anisotropic weighted distance.

    Weighted distance: sqrt((w*dx)^2 + ((2-w)*dy)^2). Implement by scaling x by w and y by (2-w).
    Raises ValueError if scaling factors are not positive.
    """
    if points.size == 0:
        return points.copy()
    sx = float(w)
    sy = float(2.0 - w)
    if sx <= 0 or sy <= 0:
        raise ValueError(f"Invalid weight w={w}: scale factors must be positive (sx={sx}, sy={sy}).")
    P = np.asarray(points, dtype=float)
    if P.ndim != 2 or P.shape[1] != 2:
        raise ValueError("points must be an array of shape (N, 2)")
    S = P.copy()
    S[:, 0] *= sx
    S[:, 1] *= sy
    return S


def dbscan_labels(points: np.ndarray, eps: float, min_samples: int, w: float) -> np.ndarray:
    """Run DBSCAN in anisotropically scaled space, return labels (noise = -1)."""
    if points.size == 0:
        return np.empty((0,), dtype=int)
    scaled = scale_points(points, w)
    db = DBSCAN(eps=float(eps), min_samples=int(min_samples), metric='euclidean')
    labels = db.fit_predict(scaled)
    return labels.astype(int)


def cluster_centroids(points: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Compute centroids (mean x,y) for non-noise clusters in ORIGINAL coordinate space.
    Returns array of shape (K, 2)."""
    if points.size == 0 or labels.size == 0:
        return np.empty((0, 2), dtype=float)
    out = []
    for lab in np.unique(labels):
        if lab < 0:
            continue  # skip noise
        mask = labels == lab
        if not np.any(mask):
            continue
        centroid = np.mean(points[mask], axis=0)
        out.append(centroid)
    if not out:
        return np.empty((0, 2), dtype=float)
    return np.vstack(out)


def _pairwise_euclidean(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute pairwise Euclidean distances between (Na,2) and (Nb,2)."""
    if a.size == 0 or b.size == 0:
        return np.empty((a.shape[0], b.shape[0]), dtype=float)
    diffs = a[:, None, :] - b[None, :, :]
    d2 = np.sum(diffs * diffs, axis=2)
    return np.sqrt(d2)


def greedy_match(a: np.ndarray, b: np.ndarray, max_dist: float) -> Tuple[List[Tuple[int, int, float]], List[int], List[int]]:
    """Greedy one-to-one matching of points 'a' to points 'b' by Euclidean distance up to max_dist.

    Returns
    - matches: list of (i, j, d)
    - unmatched_a: indices in 'a' with no match
    - unmatched_b: indices in 'b' with no match

    Matching is deterministic: candidate pairs sorted by (distance asc, i asc, j asc).
    """
    Na = a.shape[0]
    Nb = b.shape[0]
    if Na == 0 or Nb == 0:
        return [], list(range(Na)), list(range(Nb))

    D = _pairwise_euclidean(a, b)
    # Build candidate list with cutoff
    cand = []
    for i in range(Na):
        for j in range(Nb):
            dij = D[i, j]
            if dij <= max_dist:
                cand.append((dij, i, j))
    # Sort by distance, then i, then j for determinism
    cand.sort(key=lambda t: (t[0], t[1], t[2]))

    used_a = set()
    used_b = set()
    matches: List[Tuple[int, int, float]] = []
    for d, i, j in cand:
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        matches.append((i, j, float(d)))

    unmatched_a = [i for i in range(Na) if i not in used_a]
    unmatched_b = [j for j in range(Nb) if j not in used_b]
    return matches, unmatched_a, unmatched_b


def _f1_from_counts(tp: int, fp: int, fn: int) -> float:
    denom = (2 * tp + fp + fn)
    if denom <= 0:
        return 0.0
    return 2.0 * tp / denom


def image_metrics(
    pred_points: np.ndarray,
    ref_points: np.ndarray,
    eps: float,
    min_samples: int,
    w: float,
    max_match_dist: float,
) -> Tuple[float, float]:
    """Compute (F1, mean_delta) for a single image.

    - pred_points: (N,2) predicted/annotated points
    - ref_points: (M,2) reference points
    - mean_delta: average Euclidean distance over matched pairs; NaN if no matches
    - F1: 2*TP / (2*TP + FP + FN), with TP from greedy matching of cluster centroids to refs
    """
    P = np.asarray(pred_points, dtype=float).reshape(-1, 2)
    R = np.asarray(ref_points, dtype=float).reshape(-1, 2)

    if P.shape[0] == 0:
        return 0.0, float('nan')

    labels = dbscan_labels(P, eps=eps, min_samples=min_samples, w=w)
    cents = cluster_centroids(P, labels)
    if cents.shape[0] == 0:
        return 0.0, float('nan')

    matches, unmatched_c, unmatched_r = greedy_match(cents, R, max_match_dist)
    tp = len(matches)
    fp = len(unmatched_c)
    fn = len(unmatched_r)
    f1 = _f1_from_counts(tp, fp, fn)
    if tp == 0:
        return f1, float('nan')
    mean_delta = float(np.mean([d for (_, _, d) in matches]))
    return f1, mean_delta


def aggregate_metrics(per_image: List[Tuple[float, float]]) -> Tuple[float, float, int]:
    """Aggregate per-image (F1, delta) into (mean_F1, mean_delta, n_delta).

    - mean_F1 over all images, including zeros
    - mean_delta over images where delta is finite (exclude NaN)
    - n_delta is the number of images contributing to mean_delta
    """
    if not per_image:
        return 0.0, float('nan'), 0

    f1s = [f for (f, _) in per_image]
    deltas = [d for (_, d) in per_image if d == d]  # filter NaN by d==d
    mean_f1 = float(np.mean(f1s)) if f1s else 0.0
    if deltas:
        mean_delta = float(np.mean(deltas))
        n_delta = len(deltas)
    else:
        mean_delta = float('nan')
        n_delta = 0
    return mean_f1, mean_delta, n_delta


def pareto_frontier_indices(f1s: np.ndarray, deltas: np.ndarray) -> List[int]:
    """Return indices of non-dominated points for maximize(F1), minimize(delta).

    Excludes rows where delta is NaN.
    Efficient method for 2 objectives: sort by F1 desc, delta asc; keep points with strictly
    improving (lower) delta as F1 decreases.
    """
    f1s = np.asarray(f1s, dtype=float)
    deltas = np.asarray(deltas, dtype=float)

    mask = ~np.isnan(deltas)
    idxs = np.where(mask)[0]
    if idxs.size == 0:
        return []

    order = np.lexsort((deltas[idxs], -f1s[idxs]))  # primary: -F1 (desc), secondary: delta (asc)
    sorted_idx = idxs[order]

    frontier: List[int] = []
    best_delta = math.inf
    for k in sorted_idx:
        d = deltas[k]
        if d < best_delta:
            frontier.append(int(k))
            best_delta = d
    return frontier


def verify_pareto(f1s: np.ndarray, deltas: np.ndarray, idxs: List[int]) -> bool:
    """Pairwise dominance check: ensure no selected point is dominated.
    Returns True if all selected are non-dominated within the selected set and w.r.t. all points.
    """
    n = len(f1s)
    selected = set(int(i) for i in idxs)

    for a in selected:
        for b in range(n):
            if a == b:
                continue
            if np.isnan(deltas[b]) or np.isnan(deltas[a]):
                # skip comparisons involving NaN delta; NaNs should be excluded beforehand
                continue
            dom = (f1s[b] >= f1s[a]) and (deltas[b] <= deltas[a]) and ((f1s[b] > f1s[a]) or (deltas[b] < deltas[a]))
            if dom:
                return False
    return True


if __name__ == "__main__":
    # Minimal smoke test (not exhaustive)
    P = np.array([[0, 0], [1, 0], [10, 10], [11, 10]], dtype=float)
    R = np.array([[0, 0], [11, 10]], dtype=float)
    f1, d = image_metrics(P, R, eps=1.5, min_samples=2, w=1.0, max_match_dist=5.0)
    print({"F1": round(f1, 4), "delta": d})

    f1s = np.array([0.7, 0.7, 0.6, 0.65])
    deltas = np.array([15.0, 16.0, 14.0, 14.0])
    idxs = pareto_frontier_indices(f1s, deltas)
    print({"frontier_indices": idxs, "verified": verify_pareto(f1s, deltas, idxs)})
