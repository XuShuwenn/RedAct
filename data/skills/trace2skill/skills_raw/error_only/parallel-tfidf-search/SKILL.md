---
name: parallel-tfidf-search
description: "Parallelize TF-IDF search engine to achieve 1.5x indexing and 2x search speedup on multi-core systems."
---

# Parallel TF-IDF Search Engine

## When to Use

- Parallelize document search engine
- Speed up TF-IDF index building
- Accelerate similarity search with multiple workers

## Before You Code

- Read the full sequential baseline implementation end-to-end before changing anything.
- Confirm the exact input/output structures, ordering, scoring, tie-breaking, and return behavior of the sequential functions.
- Do not infer missing details from partial reads; inspect the whole baseline first, then preserve its externally visible behavior exactly.

## Required Functions

1. `build_tfidf_index_parallel(documents, num_workers=None, chunk_size=500)`
   - Return ParallelIndexingResult with same structure as sequential version
   - Target: 1.5x speedup over sequential

2. `batch_search_parallel(queries, index, top_k=10, num_workers=None, documents=None)`
   - Return (List[List[SearchResult]], elapsed_time)
   - Target: 2x speedup over sequential with 4 workers


## Verification Workflow

## Verification Workflow

- Verify against the sequential version with visible correctness evidence before claiming equivalence.
- Make performance claims only from complete benchmark output on the task's required configuration.
- After each major refactor or concurrency-model change, rerun full correctness and execution validation before further tuning.

## Key Requirements

- Produce identical results to sequential version
- Utilize all idle cores
- Handle document chunking for parallel processing
- Preserve the baseline implementation's exact data structures, formulas, ordering, tie-breaking, and return shapes.
- Parallelize the existing algorithm; do not invent alternate index/search behavior.
- Measure bottlenecks on the required benchmark/configuration before major design rewrites.
- Optimize the required functions themselves; do not claim speedup by changing tests, benchmarks, corpus size, query counts, driver logic, or only `main()`.
- Treat truncated benchmark/test output as unverified; make correctness and speedup claims only from complete observed run output with the required timings.
- Validate correctness against the sequential baseline after substantial changes and before claiming performance wins.
- Treat explicit interface/compliance checks as the source of truth; if they fail, keep optimizing or clearly report that the target is unmet.

## Implementation Approach

- Use multiprocessing.Pool or concurrent.futures
- Split documents into chunks
- Aggregate partial results
- Maintain result ordering identical to sequential

- Start by extracting the baseline contract from the sequential code: TF/IDF math, posting/index structure, search scoring, ordering rules, and output formatting.
- Prefer process-based parallelism for CPU-bound TF-IDF indexing/search unless measurements on the actual workload show a thread-based design is better.
- Parallelize only naturally independent hotspots with minimal semantic change.
- Treat process startup, serialization, and IPC volume as primary constraints; avoid sending the full index or other large shared structures in every task payload.
- Prefer worker designs that initialize shared read-only state once, process lightweight query/document slices, and build partial counts/postings once per chunk before combining them.
- For multiprocessing, define worker functions at module top level; do not use nested/local functions or lambdas as pool targets.
- Prefer standard-library parallelism and chunking helpers; avoid adding third-party dependencies unless availability is verified and they are truly necessary.
- If performance is poor, collect stage-level timings for indexing/search, worker startup, and serialization before changing architecture.
- If repeated benchmarks show poor or negative speedup, stop parameter tweaking and reconsider bottlenecks such as serialization, chunking, pool startup, or algorithmic cost.

## Tips

- Use multiprocessing.Pool or concurrent.futures first; keep dependencies minimal.
- Chunk documents for memory efficiency using standard-library logic.
- Read back the saved implementation file after writing it and run a direct syntax check or import on that exact artifact before concluding.
- Capture complete benchmark output for both indexing and search on the unchanged required workload; if output is truncated, rerun before diagnosing or claiming success.
- Verify result equivalence with the sequential version before tuning chunk size/worker count, then confirm the stated 1.5x indexing and 2x search targets were actually met.
- Follow any task-specific execution or completion protocol exactly; do not stop with "next steps" in place of required verification.

