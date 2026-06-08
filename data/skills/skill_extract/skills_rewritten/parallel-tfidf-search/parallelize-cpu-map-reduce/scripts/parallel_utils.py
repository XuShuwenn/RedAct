#!/usr/bin/env python3
"""Generic helpers for multiprocessing-based, deterministic parallel pipelines.

Functions:
- available_cpu_count(): robust CPU count
- choose_num_workers(n_tasks, max_workers=None): pick sensible worker count
- compute_chunk_size(n_items, workers, target_batches_per_worker=4, min_chunk=1)
- chunked(seq, size): yield fixed-size chunks
- timed_call(func, *args, **kwargs): return (result, elapsed_seconds)
- stable_merge_dict_of_lists(base, part): deterministic merge of dict->list
- stable_sort_postings(postings, key_index=1, tie_break_index=0, reverse=True): stable sort tuples
- init_worker_state(**kwargs): set module-level read-only state dict
- get_worker_state(): retrieve module-level state dict

These are generic and avoid any task-specific logic. They can be reused across
pipelines that follow a map-reduce style with deterministic merging.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterable, Iterator, List, Sequence, Tuple


# Module-level read-only state for workers (set via initializer)
_WORKER_STATE: Dict[str, Any] = {}


def available_cpu_count() -> int:
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1


def choose_num_workers(n_tasks: int, max_workers: int | None = None) -> int:
    cpu = available_cpu_count()
    if max_workers is None:
        max_workers = cpu
    # Do not use more workers than tasks
    return max(1, min(max_workers, cpu, n_tasks if n_tasks > 0 else 1))


def compute_chunk_size(
    n_items: int,
    workers: int,
    target_batches_per_worker: int = 4,
    min_chunk: int = 1,
) -> int:
    if n_items <= 0 or workers <= 0:
        return 1
    # Aim for W * target_batches_per_worker chunks overall
    target_chunks = max(1, workers * max(1, target_batches_per_worker))
    size = max(min_chunk, n_items // target_chunks)
    return max(min_chunk, size)


def chunked(seq: Sequence[Any] | Iterable[Any], size: int) -> Iterator[List[Any]]:
    if size <= 0:
        size = 1
    buf: List[Any] = []
    for item in seq:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def timed_call(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


def stable_merge_dict_of_lists(base: Dict[Any, List[Any]], part: Dict[Any, List[Any]]) -> Dict[Any, List[Any]]:
    """Deterministically extend base dict-of-lists with part dict-of-lists.
    Does not deduplicate; assumes caller controls uniqueness semantics.
    """
    for k, vlist in part.items():
        if not vlist:
            continue
        if k not in base:
            base[k] = []
        base[k].extend(vlist)
    return base


def stable_sort_postings(
    postings: List[Tuple[Any, ...]],
    key_index: int = 1,
    tie_break_index: int = 0,
    reverse: bool = True,
) -> None:
    """Sort a list of tuples deterministically by value then tie-break.
    Example: postings of (doc_id, score) -> sort by score desc then doc_id asc.
    """
    if not postings:
        return
    # Python sort is stable; supply explicit tie-break ordering.
    if reverse:
        postings.sort(key=lambda x: (x[key_index], -x[tie_break_index]))
        postings.reverse()
    else:
        postings.sort(key=lambda x: (x[key_index], x[tie_break_index]))


def init_worker_state(**kwargs) -> None:
    """Initializer to be called in worker processes. Values should be read-only."""
    global _WORKER_STATE
    _WORKER_STATE = dict(kwargs) if kwargs else {}


def get_worker_state() -> Dict[str, Any]:
    return _WORKER_STATE
