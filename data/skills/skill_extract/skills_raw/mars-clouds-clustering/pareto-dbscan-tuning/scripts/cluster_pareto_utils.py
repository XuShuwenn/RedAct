#!/usr/bin/env python3
"""Reusable utilities for clustering evaluation and Pareto filtering.

Functions:
- anisotropic_transform(X, w, total_weight=2.0): scale coordinates to emulate anisotropic distance.
- centroids_from_labels(X, labels): compute centroids of non-noise DBSCAN clusters.
- greedy_match_distances(centroids, experts, max_distance=100.0): greedy matching with Euclidean distance.
- f1_and_delta(match_distances, n_clusters, n_experts): compute F1 and mean delta with NaN handling.
- pareto_frontier(values, maximize): boolean mask of non-dominated points.
- fmt_fixed(value, ndigits): format numbers with fixed decimals (string).

All functions are NumPy-based and avoid external dependencies.
"""
from __future__ import annotations
import numpy as np
from typing import Iterable, List


def anisotropic_transform(X: np.ndarray, w: float, total_weight: float = 2.0) -> np.ndarray:
    """Scale coordinates to emulate anisotropic (weighted) Euclidean distance.

    d(a,b) = sqrt((w*dx)^2 + ((T-w)*dy)^2) is equivalent to Euclidean distance
    after scaling x by w and y by (T-w).

    Args:
        X: (n,2) array of points.
        w: shape weight for x-axis.
        total_weight: T; typically 2.0.
    Returns:
        (n,2) scaled coordinates.
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[1] != 2:
        raise ValueError("X must be of shape (n,2)")
    scale = np.array([w, total_weight - w], dtype=float)
    return X * scale


def centroids_from_labels(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Compute centroids of non-noise clusters from DBSCAN labels.

    Args:
        X: (n,2) original coordinates.
        labels: (n,) cluster labels, with -1 as noise.
    Returns:
        (k,2) array of centroids; k may be 0.
    """
    X = np.asarray(X, dtype=float)
    labels = np.asarray(labels)
    centroids: List[np.ndarray] = []
    for lab in np.unique(labels):
        if lab == -1:
            continue
        pts = X[labels == lab]
        if pts.size == 0:
            continue
        centroids.append(pts.mean(axis=0))
    if not centroids:
        return np.empty((0, 2), dtype=float)
    return np.vstack(centroids)


def _pairwise_euclidean(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Compute pairwise Euclidean distances between A and B.

    Args:
        A: (n,2)
        B: (m,2)
    Returns:
        (n,m) distance matrix.
    """
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    if A.size == 0 or B.size == 0:
        return np.empty((A.shape[0], B.shape[0]), dtype=float)
    diff = A[:, None, :] - B[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=2))


def greedy_match_distances(centroids: np.ndarray, experts: np.ndarray, max_distance: float = 100.0) -> List[float]:
    """Greedily match centroids to expert points using Euclidean distance.

    - Builds all candidate pairs with distance <= max_distance.
    - Sorts by distance ascending and selects pairs without reuse.

    Args:
        centroids: (k,2) centroid coordinates.
        experts: (m,2) reference coordinates.
        max_distance: maximum allowed matching distance.
    Returns:
        List of distances for matched pairs. Empty if no matches.
    """
    if centroids is None or experts is None:
        return []
    centroids = np.asarray(centroids, dtype=float)
    experts = np.asarray(experts, dtype=float)
    if centroids.ndim != 2 or experts.ndim != 2 or centroids.shape[1] != 2 or experts.shape[1] != 2:
        return []
    if centroids.shape[0] == 0 or experts.shape[0] == 0:
        return []

    D = _pairwise_euclidean(centroids, experts)
    candidates: List[tuple] = []  # (dist, i, j)
    k, m = D.shape
    for i in range(k):
        # Quickly filter by threshold to reduce candidate count
        valid_js = np.where(D[i] <= max_distance)[0]
        for j in valid_js:
            candidates.append((D[i, j], i, j))

    if not candidates:
        return []
    candidates.sort(key=lambda t: t[0])

    used_c = set()
    used_e = set()
    matched_distances: List[float] = []
    for dist, i, j in candidates:
        if i in used_c or j in used_e:
            continue
        matched_distances.append(float(dist))
        used_c.add(i)
        used_e.add(j)
    return matched_distances


def f1_and_delta(match_distances: Iterable[float], n_clusters: int, n_experts: int) -> tuple:
    """Compute F1 score and mean delta given match distances and counts.

    - Precision = matches / n_clusters (0 if n_clusters = 0)
    - Recall = matches / n_experts (0 if n_experts = 0)
    - F1 = harmonic mean (0 if both precision and recall are 0)
    - Delta = mean of match distances, NaN if no matches

    Args:
        match_distances: iterable of float distances for matched pairs.
        n_clusters: number of non-noise clusters.
        n_experts: number of reference points.
    Returns:
        (f1: float, delta: float or np.nan)
    """
    dists = np.array(list(match_distances), dtype=float)
    n_matches = int(dists.size)

    if n_matches == 0:
        return 0.0, float("nan")

    precision = (n_matches / n_clusters) if n_clusters > 0 else 0.0
    recall = (n_matches / n_experts) if n_experts > 0 else 0.0
    denom = precision + recall
    f1 = 0.0 if denom == 0.0 else 2.0 * (precision * recall) / denom
    delta = float(np.mean(dists))
    return float(f1), delta


def pareto_frontier(values: np.ndarray, maximize: List[bool]) -> np.ndarray:
    """Compute a non-dominated mask (Pareto frontier) for 2+ objectives.

    Args:
        values: (n, p) array of objective values.
        maximize: list of booleans; True for objectives to maximize, False to minimize.
    Returns:
        Boolean mask of shape (n,) where True indicates a non-dominated point.
    """
    V = np.asarray(values, dtype=float)
    if V.ndim != 2:
        raise ValueError("values must be a 2D array")
    n, p = V.shape
    if len(maximize) != p:
        raise ValueError("maximize length must equal number of objectives")

    # Convert to minimization: flip sign for objectives to maximize
    M = V.copy()
    for j, maxi in enumerate(maximize):
        if maxi:
            M[:, j] = -M[:, j]

    dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        if dominated[i]:
            continue
        for j in range(n):
            if i == j:
                continue
            # j dominates i if j is <= i on all objectives and < on at least one
            if np.all(M[j] <= M[i]) and np.any(M[j] < M[i]):
                dominated[i] = True
                break
    return ~dominated


def fmt_fixed(value: float, ndigits: int) -> str:
    """Return a string with fixed decimal places (e.g., for CSV writing)."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    fmt = f"{{:.{ndigits}f}}"
    return fmt.format(float(value))


if __name__ == "__main__":
    # Minimal self-test
    vals = np.array([
        [0.6, 16.0],
        [0.62, 16.2],
        [0.6, 15.8],
        [0.7, 17.0],
    ])
    mask = pareto_frontier(vals, maximize=[True, False])
    print("Pareto mask:", mask.tolist())
