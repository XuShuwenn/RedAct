---
name: parallelize-cpu-map-reduce
description: "Design and implement deterministic, multiprocessing-based speedups for CPU-bound pipelines with independent per-item work and global aggregation, while preserving identical outputs."
---

# Parallelizing CPU-Bound Map-Reduce Pipelines (Deterministic, Result-Identical)

This skill teaches a reusable workflow for accelerating CPU-bound data pipelines (e.g., text indexing and batch scoring) using Python multiprocessing. It focuses on splitting work into independent map phases with a central reduce/aggregation step, minimizing inter-process communication, and preserving exact output equivalence to a sequential baseline.

## When to Use

Activate this skill when the task:
- Processes many items independently (documents, records, queries) with CPU-heavy compute.
- Requires global statistics (e.g., corpus-level frequencies) computed from per-item results.
- Must preserve identical outputs to an existing sequential implementation.
- Needs speedups on multi-core machines (e.g., target speedups with 4 workers).

## Core Workflow

1) Understand the Baseline
- Read the sequential implementation and identify:
  - Independent per-item computations (pure functions) suitable for parallel map steps.
  - Global aggregates derived from those per-item results (reduce step).
  - Final structures and output ordering that must match exactly.
- Note numerical formulas and tie-breaking rules used for ranking/sorting.

2) Design a Multi-Phase Parallel Plan
- Phase A (Map): For each item (e.g., document), compute per-item features and local aggregates (e.g., term frequencies and local document-frequency counts). Return only compact, picklable results.
- Phase A (Reduce): Combine per-chunk aggregates centrally (e.g., sum counts). Compute global constants once (e.g., IDF, normalizers) in the main process to avoid numeric drift.
- Phase B (Map): Using the global constants, compute per-item final representations and partial lookup structures (e.g., vectors, norms, partial inverted index). Return partial structures per chunk.
- Final Assembly (Reduce): Deterministically merge partial structures (e.g., extend postings lists, then sort consistently).

3) Worker and IPC Strategy
- Use process-based pools for CPU-bound work (the GIL limits threads on pure Python compute).
- Define all worker functions at module top-level so they are picklable.
- Use pool initializer to load read-only, shared state once per worker (avoid passing large objects per task).
- Batch input into chunks to reduce scheduling overhead.
- Keep task arguments small and serialization-friendly (e.g., IDs, small dicts, short lists).

4) Chunking, Sizing, and Concurrency
- Choose num_workers = min(available_cpu, workload size) rather than always using all cores.
- Pick chunk_size so each task has enough compute to amortize IPC (e.g., target a few chunks per worker).
- For batch scoring (e.g., queries):
  - Batch queries into groups per task to reduce IPC.
  - Preserve input order when reconstructing outputs.
  - Optionally fall back to sequential for very small workloads.

5) Deterministic Merge and Ordering
- Ensure merges are stable and deterministic:
  - For dict-of-lists (e.g., inverted index), extend lists per key and then sort consistently.
  - Use explicit tie-breakers in sorts (e.g., sort by score descending, then by ID ascending) to preserve exact order.
  - Avoid floating-point accumulation across partitions for global stats; compute globals once from integer counts.
- Preserve output ordering to match baseline (e.g., align result list positions to input order).

6) Search/Batched Scoring Pattern (if applicable)
- Initialize workers with the read-only index/state once (initializer) to avoid repeated transfers.
- Process queries in batches; each worker returns a list of results for its batch.
- Flatten batched results to match the original output order.
- Keep the same ranking function and tie-breaking as the baseline; do not alter formulas.

7) Measurement and Validation
- Measure with time.perf_counter().
- Run with a workload large enough to amortize pool startup and IPC overhead.
- Validate exact result equivalence:
  - Index contents (keys, lengths, norms) and per-entry values.
  - Rankings: same IDs, same scores, same order for ties.
- Confirm speedup targets (e.g., ≥1.5× for build, ≥2× for search with a specified worker count) under realistic workloads.

## Verification

Perform these checks before finalizing:
- Structural equality: The final data structures have the same types, keys, and sizes as the baseline.
- Numeric equality: Global constants (e.g., IDF), per-item vectors, and norms match exactly.
- Deterministic order: For lists that require sorting, verify identical order (use explicit tie-break rules).
- Batch search: For each query, ensure the top-k list (IDs and scores) is identical to the sequential implementation.
- Performance: Compare elapsed time for sequential vs parallel under a fixed workload and worker count; report speedups.

## Common Pitfalls and How to Avoid Them

- Passing large state on every task:
  - Use pool initializer to load large, read-only data once per worker.
- Too many tiny tasks:
  - Batch items to reduce scheduling and IPC overhead; target a modest number of chunks per worker.
- Over-parallelization:
  - Using more workers than useful can slow things down. Cap by workload size and available CPUs.
- Non-picklable workers or closures:
  - Keep worker functions at module top-level; avoid lambdas/closures in pool submission.
- Nondeterministic merging/sorting:
  - Always sort with explicit tie-breakers; avoid relying on implicit dict order for logic.
- Using threads for CPU-bound work:
  - Prefer processes for pure Python compute.
- Recomputing global stats in workers:
  - Compute once in main process to avoid numeric drift and duplicated work.
- Recreating pools repeatedly:
  - Create a pool once per phase; reuse within the phase.

## Optional Script Usage

This skill includes a generic helper script at scripts/parallel_utils.py:
- Chunking and worker-count helpers to size tasks and pools appropriately.
- Deterministic merges for dict-of-lists, plus stable sorting with tie-breakers.
- Timed calls for clean performance measurement.
- A simple worker-state initializer/getter for sharing read-only data across worker calls.

Example usage pattern:
- Determine workers via choose_num_workers(n_tasks).
- Compute chunk_size = compute_chunk_size(n_items, workers).
- Split data with chunked(iterable, chunk_size).
- Initialize workers once with init_worker_state(...) in pool initializer.
- Map worker over chunks; merge results with stable_merge_dict_of_lists and stable_sort_postings.
- Measure time with timed_call to report speedups.
