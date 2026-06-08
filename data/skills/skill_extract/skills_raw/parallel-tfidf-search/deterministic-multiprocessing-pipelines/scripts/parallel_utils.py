#!/usr/bin/env python3
"""Generic multiprocessing utilities for deterministic parallel pipelines.

This module provides:
- chunk_list: split a list into approx-equal chunks
- compute_chunksize: choose a map chunksize for N tasks and W workers
- stable_topk: deterministic top-K with tie-breaking
- restore_order: restore original order from (index, value) pairs
- global initializer patterns for multiprocessing workers

These helpers are domain-agnostic and suitable for TF-IDF-like pipelines
and other CPU-bound map/reduce workflows.
"""
from __future__ import annotations

import heapq
from math import ceil
from typing import Iterable, List, Sequence, Tuple, Any

# ---------------------------------------------------------------------------
# Chunking utilities
# ---------------------------------------------------------------------------

def chunk_list(items: Sequence[Any], num_chunks: int) -> List[List[Any]]:
    """Split items into num_chunks approximately equal chunks.

    If num_chunks <= 0 or items is empty, returns [items] or [].
    """
    n = len(items)
    if n == 0:
        return []
    if num_chunks <= 0:
        return [list(items)]
    size = max(1, ceil(n / num_chunks))
    return [list(items[i:i+size]) for i in range(0, n, size)]


def compute_chunksize(n_tasks: int, n_workers: int, target_batches_per_worker: int = 4) -> int:
    """Heuristic chunksize for executor.map/Pool.map.

    Aim for about target_batches_per_worker batches per worker to balance
    scheduling overhead and load balancing.
    """
    if n_workers <= 0:
        return max(1, n_tasks)
    total_batches = max(1, n_workers * target_batches_per_worker)
    return max(1, ceil(n_tasks / total_batches))

# ---------------------------------------------------------------------------
# Deterministic top-K
# ---------------------------------------------------------------------------

def stable_topk(pairs: Iterable[Tuple[int, float]], k: int) -> List[Tuple[int, float]]:
    """Return top-K by descending score with deterministic tie-breaking.

    pairs: iterable of (id, score)
    Tie-breaker: higher score first; if equal, smaller id first.
    Returns a list sorted by (score desc, id asc).
    """
    # Use nlargest on key and then sort for total ordering if needed
    top = heapq.nlargest(k, pairs, key=lambda p: (p[1], -p[0]))
    # Enforce deterministic total order: score desc, id asc
    top.sort(key=lambda p: (-p[1], p[0]))
    return top

# ---------------------------------------------------------------------------
# Order restoration
# ---------------------------------------------------------------------------

def restore_order(indexed_values: Iterable[Tuple[int, Any]]) -> List[Any]:
    """Restore order from (index, value) pairs.

    Sorts by index ascending and returns values list.
    """
    sorted_pairs = sorted(indexed_values, key=lambda x: x[0])
    return [v for _, v in sorted_pairs]

# ---------------------------------------------------------------------------
# Global initializer pattern for multiprocessing
# ---------------------------------------------------------------------------
# Workers often need to access read-only large objects without passing them
# as arguments for every task. Use init_globals in Pool/Executor initializer
# to set once per worker. Access with get_global inside workers.

_GLOBALS: dict[str, Any] = {}


def init_globals(**kwargs: Any) -> None:
    """Initializer function for worker processes.

    Example:
        with Pool(processes=W, initializer=init_globals, initargs=(...,)):
            # Noting that initargs must be a tuple; pack key-values in a dict

    Prefer using: initializer=init_globals, initargs=(dict_data,) and then
    call init_globals(**dict_data) from a thin wrapper initializer.
    """
    _GLOBALS.clear()
    _GLOBALS.update(kwargs)


def get_global(name: str, default: Any = None) -> Any:
    """Retrieve a global set by init_globals in worker process."""
    return _GLOBALS.get(name, default)

# Thin wrapper to bridge Pool initializer tuple constraint

def make_initializer(payload: dict[str, Any]):
    """Return a function that calls init_globals(**payload) in each worker."""
    def _init() -> None:
        init_globals(**payload)
    return _init
