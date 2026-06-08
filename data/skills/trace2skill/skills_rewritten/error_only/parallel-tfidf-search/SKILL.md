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

- Do not start implementing after a partial file read. If the sequential baseline is long or paginated, continue reading until you have inspected every function and helper that affects indexing/search behavior.
- Write down the baseline contract before coding: exact TF/IDF formula, index/posting structure, document/title handling, result ordering, tie-breaks, return types, and any required verification output behavior.
- Reuse the sequential module's existing classes, dataclasses, data models, tokenization, term-frequency, IDF, scoring helpers, and result/index types where possible instead of recreating parallel-only variants.
- Mirror the baseline's types and helper behavior first; add parallel orchestration around them so the execution strategy changes without changing TF-IDF math, scoring, or result shaping.
- If any part of the baseline is still unobserved or unclear, stop and inspect it instead of inferring behavior.
- Before your first implementation edit, inspect the current target implementation file end-to-end as well; do not rewrite from assumptions based on tiny snippets or guessed structure.
- Anchor edits to exact observed text or exact line ranges from the current file contents. If the expected target is not present, stop and reread the file instead of guessing a replacement.
- When writing or editing source files, write actual executable code only. Do not replace files or patches with summaries, placeholders, ellipses, or prose such as "implemented parallel version here".
- After each file write/edit, immediately reread the saved file and run a syntax/import check on that exact artifact before continuing.
- Before any tool use, inspect the task/environment instructions for the exact required action syntax, allowed tools, and completion signal; follow that protocol exactly for every command.
- If any file read is truncated or paginated, continue reading additional ranges until the relevant functions, helpers, signatures, dataclasses/types, and call flow are fully observed.
- Do not add third-party dependencies unless the task explicitly allows them and you have verified availability in the environment; prefer the Python standard library.

## Required Functions

1. `build_tfidf_index_parallel(documents, num_workers=None, chunk_size=500)`
   - Return ParallelIndexingResult with same structure as sequential version
   - Target: 1.5x speedup over sequential

2. `batch_search_parallel(queries, index, top_k=10, num_workers=None, documents=None)`
   - Return (List[List[SearchResult]], elapsed_time)
   - Target: 2x speedup over sequential with 4 workers


## Verification Workflow

- Treat task-level protocol compliance as part of verification: required tool/action format, output schema, wait pattern, and final completion signal must all be satisfied.
- For bash or verification steps, issue concrete executable commands only; do not write descriptive placeholders such as "run the benchmark" in place of a real command.
- Treat partial or truncated test/benchmark output as inconclusive. Rerun or capture output differently until indexing/search correctness checks and timing lines are fully visible.
- Separate observations from hypotheses: do not attribute slowdown to IPC, serialization, worker startup, scoring logic, or any other bottleneck unless completed benchmark/profiling evidence supports it.
- Keep validation artifacts and evaluation conditions unchanged while iterating: benchmark the implementation under the original required setup rather than rewriting tests, benchmarks, corpus/query sizes, worker settings, or harness logic to obtain better-looking numbers.
- Keep exploratory benchmarking separate from compliance validation: always rerun the required unchanged entry points and parameters before concluding success.
- If targets remain unmet after a benchmark round, do not keep cycling through worker counts, chunk sizes, oversubscription, or similar tuning alone; first identify the dominant stage cost from measured timings and change the architecture causing it.
- If the environment requires a final sentinel such as `ACTION: TASK_COMPLETE`, emit that exact line only after correctness/performance results have been observed to completion.
- Once correctness is confirmed and the required benchmark/interface conditions are met, stop redesigning and finish the task cleanly rather than continuing speculative optimization.

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

- Make merged or aggregated outputs deterministic before comparison/return; mirror the sequential version's exact secondary sort keys, stable equal-score ordering, and any posting-list/document-id ordering rules.
- Before changing architecture, identify whether the slowdown comes from useful compute or from pool startup, IPC, and repeated serialization of the same large structures.
- Do not modify benchmark inputs, corpus sizes, query sets, thresholds, worker settings, evaluation scripts, or driver logic to make speedups look better; optimize the required functions against the stated evaluation setup.
- Demonstrate speedup from `build_tfidf_index_parallel` and `batch_search_parallel` themselves, not from moving work outside those functions or from benchmark-only shortcuts.
- Do not treat custom smoke tests or side experiments as proof of task compliance; compare directly against the baseline behavior and the required benchmark results.
- If required-condition validation fails, either continue optimizing the implementation or explicitly report that the target remains unmet.
- Do not infer unseen timings, speedups, or correctness results from partial logs; absent metrics are unknown, not approximately satisfied.
- Treat task-level execution/interface instructions as mandatory requirements: use the specified tool-call format, output schema, and exact completion signal when provided.

- Follow the task environment's required interaction contract exactly. If the system specifies an `Action:` JSON tool-call format or an exact completion line such as `ACTION: TASK_COMPLETE`, use that exact syntax; unsupported approximations are task failures.
- Do not modify tests, benchmark scripts, corpus sizes, query sets, evaluation thresholds, worker settings, or other validation artifacts unless the task explicitly requires it.
- Do not make blind edits against placeholder strings such as `existing helper`, invented code structure, or assumed anchors; inspect the real file content first, patch using observed text, then re-read the saved file to confirm the intended change landed.
- Do not make optimization or debugging decisions from partial file reads, partial diffs, or truncated benchmark output; gather the missing code/output first.
- Regard direct compliance checks on the specified call pattern, required function signatures, and required workload as authoritative over side experiments.
- Do not stop after launching a final benchmark/test. A command being started is not evidence of success; observe the result, verify whether requirements were met, and only then emit any required completion signal.

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

- Reuse the sequential module's existing tokenization, TF/IDF math, scoring helpers, posting/index structures, and result/index dataclasses whenever possible; change execution strategy, not observable semantics.
- Copy the sequential text-processing and scoring pipeline exactly before introducing concurrency: tokenization, stop-word filtering, term-frequency normalization, IDF formula, cosine-similarity flow, and any tie-breaking behavior.
- Keep multiprocessing worker callables and reusable helpers at module top level from the start; avoid nested functions or lambdas as pool targets.
- Prefer a map-reduce or hybrid shape that mirrors the sequential pipeline: parallelize independent per-document indexing work and per-query search work, merge global counts/statistics centrally, derive shared corpus-wide state such as DF/IDF once, then perform final assembly in a deterministic main-process pass.
- Prefer document-partitioned work for indexing: workers handle independent per-document tokenization and term-frequency extraction, while the main process merges results and computes corpus-level document frequencies, IDF, postings, norms, and final index assembly unless benchmarking shows a different split is better.
- Separate independent per-item work from shared global computations explicitly; parallelize the former and keep the latter centralized when exact equivalence depends on corpus-wide totals.
- Reuse a worker pool across the full indexing/search phase or adjacent compatible phases when possible instead of creating short-lived pools for small substeps.
- Before major architecture changes, collect stage-level timings for at least: worker startup/init, indexing work, merge/aggregation, query scoring, and serialization/data transfer.
- Do not switch between threads, processes, executors, or other architectures based only on intuition or general beliefs; use measured timings on the actual required workload first. If repeated measurements show an approach repeatedly misses target, stop parameter churn and redesign around the dominant cost.
- If measurements show serialization, pickling the index, IPC volume, or pool overhead dominates, change the worker architecture instead of only tuning chunk sizes or worker counts.
- Keep worker payloads small: send lightweight document/query slices or simple arguments rather than repeatedly transmitting the full index, `doc_term_freqs`, or other large shared structures.
- For large read-only search/index state, initialize shared structures once per worker with a pool/executor initializer or equivalent module-level setup and send only lightweight document/query slices or IDs thereafter; do not pass the full index or other large shared structures in every task payload.
- For batch search over a large immutable index, prefer partitioning queries across workers while initializing shared read-only state once per process, then dispatch only small per-query arguments such as `(query, top_k)`.
- Preserve baseline ordering semantics during merge/assembly; if posting lists, vocabulary insertion, or tie behavior depend on encounter order, reconstruct them in the same effective order as the sequential code.
- Reuse baseline search/scoring logic inside workers when practical instead of re-deriving formulas independently.
- Do not parallelize cheap combination steps just for symmetry; keep lightweight DF/IDF aggregation or other inexpensive merges sequential unless timings show they are real bottlenecks.
- Add workload-size-aware behavior: batch per-document/per-query work when tasks are too small to amortize multiprocessing overhead, use a sequential fallback for small query/document batches when pool startup or IPC would dominate, and treat `chunk_size` or batch size as a benchmarked tuning parameter rather than relying blindly on defaults.
- If the sequential pipeline makes multiple compatible expensive full-data passes, see whether tokenization, per-document TF computation, and document-frequency contribution counting can be merged into one worker pass without changing outputs.
- Keep ordering-sensitive steps such as IDF computation, posting/index assembly, and final result ordering in a controlled aggregation step so outputs remain identical to the sequential version.
- Prefer standard-library parallelism and chunking helpers; avoid adding third-party dependencies unless availability is verified and they are truly necessary while preserving importability of the target module.

- Before editing, inspect the actual search/index code path end-to-end and base changes on the observed bottleneck location, not on generic beliefs about threads vs. processes.
- Do not assume thread oversubscription will help CPU-bound TF-IDF text processing; treat it as unproven until benchmark timings on the required workload show a real gain.
- If search speedup remains poor after basic chunk-size/worker tuning, investigate architectural causes such as per-query serialization, repeated pool startup, index transfer, or duplicated scoring work instead of continuing parameter churn.

## Tips

- Use multiprocessing.Pool or concurrent.futures first; keep dependencies minimal.
- Chunk documents for memory efficiency using standard-library logic.
- Read back the saved implementation file after writing it and run a direct syntax check or import on that exact artifact before concluding.
- Capture complete benchmark output for both indexing and search on the unchanged required workload; if output is truncated, rerun before diagnosing or claiming success.
- Verify result equivalence with the sequential version before tuning chunk size/worker count, then confirm the stated 1.5x indexing and 2x search targets were actually met.
- Follow any task-specific execution or completion protocol exactly; do not stop with "next steps" in place of required verification.

- Before optimizing, keep a short written checklist of the exact sequential contract for both required functions so later refactors can be checked against it quickly.
- Use a quick sequential-vs-parallel equality/benchmark check during iteration so correctness regressions and weak speedups are visible immediately.
- After creating or overwriting code with shell redirection/heredocs, immediately inspect the saved file and run `python -m py_compile` or an equivalent import check on that exact path.
- Do not judge multiprocessing speedup from tiny benchmarks alone; validate on the required workload and check first for repeated pool creation or repeatedly shipping the full index/documents to workers.
- If measured speedup is poor, first remove repeated serialization of large dictionaries/vectors by switching task payloads to lightweight slices plus worker-initialized shared read-only state.
- Use benchmark variations only to diagnose bottlenecks; keep optimization effort focused on `build_tfidf_index_parallel` and `batch_search_parallel`, not on making `main()` or the demo workload look faster.
- If a run cuts off during a benchmark section, rerun in a way that exposes the missing lines before concluding anything.
- Prefer benchmark-driven tuning of `chunksize` and fallback thresholds; keep them simple and justify them with observed timings on the required workload.
- Prefer one well-chosen parallel phase over multiple marginal ones when extra pools or passes add more overhead than speedup.
- If the task requires a final line such as `ACTION: TASK_COMPLETE`, make that exact required line the ending of the response.

- Never treat a descriptive sentence inside a `.py` file as a temporary stand-in; if you cannot yet implement a function, stop and inspect requirements rather than writing placeholder text.
- Before each edit, identify the exact file region from the observed source that you are changing; after the edit, read that region back to verify the code now matches your intent.
- When using file-writing commands, treat the saved artifact as untrusted until you read it back and verify it contains real Python code rather than explanatory text.
- If benchmark output ends mid-section, do not diagnose causes or claim equivalence yet; rerun to capture the full output first.
- If benchmark evidence keeps missing the target, prefer one measured redesign of the dominant cost over many small tuning changes.
- If a command shows full correctness/equivalence and required validations passing, prefer preserving that stable implementation and completing the task over further large refactors.

