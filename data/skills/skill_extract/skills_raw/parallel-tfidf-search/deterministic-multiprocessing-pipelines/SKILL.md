---
name: deterministic-multiprocessing-pipelines
description: "Parallelize CPU-bound Python pipelines (e.g., TF-IDF indexing/search) with multiprocessing while preserving sequential results exactly and achieving real speedups."
---

# Deterministic Multiprocessing Pipelines

A reusable workflow for converting a sequential, CPU-bound Python pipeline (e.g., TF‑IDF indexing and batch search) into a correct, deterministic, and efficient multiprocessing implementation that achieves practical speedups without altering outputs.

## When to Use

Use this skill when you need to:
- parallelize a multi-phase CPU-bound pipeline (text tokenization, vectorization, inverted index construction, similarity search)
- maintain bit-for-bit identical outputs to a known sequential baseline
- achieve real speedups on multi-core systems while avoiding multiprocessing overhead pitfalls

Examples: search engines (TF‑IDF/keyword), similarity ranking, feature extraction, per-item computations with a reduction/merge phase.

## Core Workflow

Use a structured, phase-based approach. Design each phase for parallel safety, deterministic merging, and minimal inter-process communication (IPC).

1) Map the Pipeline Phases
- Identify independent map steps (e.g., per-document tokenization, per-term posting list, per-document vector/norm).
- Identify global reduce steps (e.g., document frequency aggregation, IDF calculation). Keep small global steps sequential.
- Decide partitioning strategy per phase (per-document vs per-term) based on data size and reuse.

2) Design Data Flow to Minimize IPC
- Workers return compact results only (e.g., per-doc TF dicts and term sets). Avoid sending the full index back and forth.
- For search, send only read-only subsets needed by workers (e.g., idf, inverted_index, doc_vectors, doc_norms). Exclude unused fields.
- Use a pool initializer to load large read-only structures into worker globals once per process (not per task).

3) Implement Workers at Module Level
- Define worker functions at top level (not nested) so they’re picklable.
- Keep workers pure (no side effects beyond returning results). Ensure deterministic iteration (e.g., sort when needed).

4) Parallel Index Building (TF‑IDF Example)
- Phase A (per-document map): tokenize and compute per-document term frequencies (TF). Return {doc_id → tf_dict} and {doc_id → term_set} and a local vocab set.
- Merge partial results on the main process: update global vocabulary, build a list of doc_term_sets for later use.
- Phase B (reduce): compute document frequencies df(term) across documents. Parallelize per-term counting with an initializer that shares doc_term_sets for fast membership checks. For small corpora, do this sequentially.
- Compute IDF sequentially (fast): idf(term) = log(N/df(term)) + 1 (or your baseline’s exact formula).
- Phase C (per-term map): build posting lists in parallel (initializer shares doc TF dicts and idf). Sort each posting list deterministically (e.g., by descending score, then by doc_id as a tie-breaker) to match baseline order.
- Phase D (per-document map): compute document vectors and norms in parallel (initializer shares idf). Norm = sqrt(sum(tfidf^2)).

5) Parallel Batch Search
- Use a pool initializer to share the index once per worker (idf, inverted_index, doc_vectors, doc_norms, optional title map). Avoid sending the full index with each task.
- Batch multiple queries per task to amortize IPC and scheduling overhead. Restore original query order by carrying (query_index, query_text) pairs and sorting results by index.
- For very small query counts, fall back to sequential to avoid pool startup costs.

6) Chunking & Batching Heuristics
- Compute an effective chunksize that yields a few batches per worker (e.g., ~2–4) to balance load and minimize IPC.
- Documents: split into many more chunks than workers if document lengths vary widely; otherwise use larger chunks to reduce overhead.
- Queries: group into batches so each worker handles multiple queries per task.

7) Ordering & Determinism
- Preserve deterministic output by:
  - Building posting lists with stable sort keys (e.g., sort by (-score, doc_id)).
  - Iterating docs in a preserved deterministic order when merging (e.g., maintain a doc_id_order list from input sequence if the baseline depends on it).
  - Avoiding iteration over sets/dicts without defining order—convert to sorted lists where the baseline implies an order.

8) Performance Measurement
- Measure phase timings with time.perf_counter().
- Compare total elapsed time vs sequential for: index build and batch search.
- Expect diminishing returns for small workloads due to pool startup and serialization.

## Verification

Always validate the parallel outputs against the sequential baseline before claiming speedups.

Checks to perform:
- Structural equality:
  - num_documents matches
  - vocabulary sets equal
  - document_frequencies equal
- Numerical equality:
  - idf(term) values within strict tolerance (or exact if integers/logs match exactly)
  - doc_vectors[doc_id][term] equal (or within tiny float tolerance)
  - doc_norms[doc_id] equal within tiny tolerance
- Posting lists:
  - same (doc_id, score) pairs in the same order
- Search results:
  - same number of results per query
  - same doc_id at each rank, identical or near-identical scores

Recommended tolerances: <= 1e-10 for scores when your baseline uses the same arithmetic order. If tiny ordering differences arise from float associativity, enforce deterministic iteration to eliminate drift.

## Common Pitfalls and How to Avoid Them

- Nested or local worker functions cannot be pickled
  - Define all worker functions and dataclasses at module scope.

- Massive IPC cost from sending large objects per task
  - Use pool initializer to set globals once per worker; send only small arguments per task.
  - Batch multiple items per task to amortize overhead.

- Non-deterministic results due to unordered iteration
  - Sort posting lists by a stable key; preserve original doc order where the baseline depends on it.
  - Do not rely on set or dict iteration order.

- Over-parallelization on small workloads
  - Add thresholds to fall back to sequential for small N or few queries.

- Using threads for CPU-bound loops
  - Prefer multiprocessing for CPU-bound Python loops (GIL). Consider threads only if workload releases GIL or is I/O-bound.

- Recomputing or transferring unneeded data
  - Exclude unused index fields from worker state during search.

- Platform/start-method differences
  - On Linux (fork), globals may be inherited; on other OS (spawn), you must use initializers. Code for both by always providing an initializer.

## Optional Script Usage

The scripts/parallel_utils.py utility offers reusable helpers for chunking, batching, stable top‑K, order restoration, and a generic global-initializer pattern for multiprocessing pools.

Example patterns:

- Chunking into N roughly equal parts
- Computing a chunksize for map to get a target number of batches per worker
- Stable top‑K with deterministic tie-breaking
- Worker initializer to set global state once per process and later access it in worker calls

Use these helpers to standardize parallelization across phases.

## Success Criteria

- Correctness: parallel outputs are identical to sequential baseline (within specified tolerances), including result ordering.
- Performance (illustrative targets):
  - Index build: achieve measurable speedup (e.g., ≥1.5× with 4 workers on sufficiently large corpora)
  - Batch search: ≥2× speedup with 4 workers on sufficiently large batches of queries
- Robustness: graceful sequential fallback for small workloads; no deadlocks; workers exit cleanly.
