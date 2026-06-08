---
name: mars-clouds-clustering
description: "Optimize DBSCAN hyperparameters to find Pareto frontier of F1 score and centroid delta for Mars cloud annotations."
---

# Mars Cloud Clustering with DBSCAN

## When to Use

- Optimize clustering hyperparameters
- Find Pareto optimal solutions
- Evaluate citizen science vs expert annotations

## Input Data

- `/root/data/citsci_train.csv`: Citizen annotations (file_rad, x, y)
- `/root/data/expert_train.csv`: Expert annotations (file_rad, x, y)

**Before coding, inspect the real CSV headers and sample rows from both files.** If the files do not literally contain `file_rad`, `x`, and `y`, reconcile the actual schema first (for example, determine which column identifies the image and whether coordinates need renaming or extraction) before implementing clustering logic. If any logic depends on filename/path structure in `file_rad`, derive it from observed sample rows rather than assumptions.

Minimum schema/alignment check before coding:
- Read enough rows from both CSVs to identify the true image/group key and coordinate fields from observed data, not header names alone.
- Record basic sanity checks before coding: row counts, missing-value status for identifier/coordinate fields, number of unique image IDs in each dataset, and the overlap between citizen and expert image IDs.
- Use that inspection to choose the scoring domain explicitly; if expert annotations define the reference image population, score across those image keys so expert-only images still contribute `F1 = 0.0` and `delta = NaN` instead of being skipped.
- If `file_rad` is absent, derived, or structured unexpectedly, explicitly map the real columns to the per-image grouping key and coordinate columns before writing the main script.
- Do not start the full sweep until this mapping is confirmed from representative non-header rows.

## Hyperparameter Search

Grid search over:
- min_samples: 3-9 (integers)
- epsilon: 4-24 (step 2)
- shape_weight: 0.9-1.9 (step 0.1)

Before launching the full 847-combination sweep, run a small timing check on a few combinations. If runtime looks poor, restructure first rather than starting a long unattended run.

- Use the timing check to estimate total sweep runtime. If the estimate is not comfortably finishable in the current session, optimize first and rerun the timing check before committing to the full sweep.
- Prefer a single reproducible script for the full pipeline: inspect schema, confirm dependencies import, load and group data once, evaluate combinations, filter valid results, compute the Pareto frontier, and write `/root/pareto_frontier.csv`.
- First make one parameter-combination evaluator fully spec-correct and sanity-check its outputs; only then scale to the full grid.
- If runtime remains high after grouping/caching, parallelize across independent hyperparameter combinations or slices (for example `shape_weight`), but keep worker logic identical to the serial version and combine all results before global `F1 > 0.5` filtering and Pareto selection.
- Prefer a foreground run you can wait on to completion once performance is acceptable.


- Before the full sweep, run a smoke test that exercises the complete pipeline on a tiny subset or a few parameter combinations: schema mapping, per-image DBSCAN, greedy 100px matching, metric aggregation, `F1 > 0.5` filtering, Pareto extraction, and CSV writing/reading. Only launch the full 847-combination search after this end-to-end check succeeds.
- Treat the smoke test as a contract check, not just a performance check: verify at least one intermediate result and confirm the produced CSV has the exact required header/format before scaling up.


## Custom Distance Metric

DBSCAN uses:
```
d(a,b) = sqrt((w*Δx)² + ((2-w)*Δy)²)
```

Implementation guidance:
- Load both CSVs once and pre-group points by `file_rad`; do not re-read or re-filter the full datasets inside each parameter evaluation.
- Prefer implementing the weighted metric by transforming coordinates so Euclidean DBSCAN matches the formula exactly; for `shape_weight = w`, use `x_scaled = w * x` and `y_scaled = (2 - w) * y`.
- Verify this transformed Euclidean distance is algebraically identical to `sqrt((w*Δx)^2 + ((2-w)*Δy)^2)` before trusting results.
- If transformed coordinates are hard to validate, build a per-image precomputed distance matrix and run `DBSCAN(metric='precomputed')`; correctness of the specified geometry is more important than forcing one implementation style.
- Do not use a slow Python-callable pairwise metric inside the full sweep unless timing confirms it is acceptable.
- Keep clustering distance and evaluation distance separate: use the weighted/scaled geometry only for DBSCAN neighborhood formation, then compute cluster centroids, cluster-to-expert distances, the 100px cutoff, and `delta` in ordinary Euclidean pixels on the original coordinates.
- Reuse per-image expert/citizen subsets across combinations, and avoid recomputing transformed/grouped data more than necessary inside the 847-combination loop.

## Evaluation Per Combination

1. Run DBSCAN on citizen science points per image
2. Match clusters to expert annotations (greedy, max 100px)
3. Compute F1 and average delta (Euclidean distance)
4. Only keep results with F1 > 0.5


Additional required rules:
- If DBSCAN finds no clusters for an image, set that image's `F1 = 0.0` and `delta = NaN`.
- If no cluster-expert matches are found for an image, set that image's `F1 = 0.0` and `delta = NaN`.
- Do not treat "both empty" as a perfect score.
- Average metrics across images, then keep only combinations with average `F1 > 0.5`.
- Apply the `F1 > 0.5` filter only after computing metrics for a hyperparameter combination.
- Do not fall back to including all combinations when none pass the `F1 > 0.5` filter.
- Iterate over the full scoring domain established from the observed data/spec; if expert/reference images define that domain, include expert-only images as `F1 = 0.0` and `delta = NaN` without running DBSCAN for them. Keep matching/evaluation work per image lightweight because it is repeated for every hyperparameter setting.
- Compute Pareto-optimal points with equality-aware dominance: a row is dominated if another row has `F1 >= current F1` and `delta <= current delta`, with at least one strict improvement.

**Validate the implementation against the spec before trusting results:**
- Check that clustering is run per image/group using the actual image identifier from the data.
- Confirm greedy matching uses a 100px maximum distance.
- Confirm `delta` is computed as average Euclidean centroid distance for matched pairs.

- Implement the task-specific scoring rules explicitly in code; do not rely on library defaults or implicit averaging behavior.
- Encapsulate scoring for one hyperparameter combination in a single function, then run the full grid with that same evaluator so performance changes do not alter scoring semantics.
- Implement image-level edge cases literally: if an image has no citizen points, DBSCAN yields zero clusters, or no cluster-expert match is found within 100px, record `F1 = 0.0` and `delta = NaN` for that image.
- Never assign `F1 = 1.0` for any "both empty" or similar convenience case.
- Average `F1` across all images in the scoring domain, including images scored as misses from no citizen points, no clusters, or no matches.
- Compute each image's `delta` as the mean matched centroid distance for that image, or `NaN` if it has no valid matches; when averaging across images, exclude `NaN` deltas from the delta mean rather than converting them to 0 or dropping the whole combination silently.
- Preserve per-image evaluation even if citizen and expert image sets differ; do not collapse all points across files into one clustering run.
- Before Pareto extraction, filter to combinations with average `F1 > 0.5` and non-NaN `delta`; if none pass, keep the filtered result empty rather than reverting to unfiltered results.
- Do not use a strict-both-sides dominance test such as `other.F1 > current.F1 and other.delta < current.delta`; use the required equality-aware dominance rule.


## Output

`/root/pareto_frontier.csv`:
```csv
F1,delta,min_samples,epsilon,shape_weight
```

- Round F1/delta to 5 decimals, shape_weight to 1 decimal
- Include all Pareto-optimal points


Before declaring completion, verify `/root/pareto_frontier.csv` was actually written, is non-empty, and is specification-compliant:
- Columns exactly: `F1,delta,min_samples,epsilon,shape_weight`
- `F1` and `delta` rounded to 5 decimals; `shape_weight` to 1 decimal
- Every row is Pareto-optimal and no dominated row remains
- Results only include combinations with `F1 > 0.5`
- Validate the complete file, not just `head` or a row count
- Spot-check at least one output row against the computation logic or intermediate results

- Explicitly select/rename output columns so the header is exactly `F1,delta,min_samples,epsilon,shape_weight` in that order and casing.
- When writing the CSV, use explicit formatting so `F1` and `delta` are rendered to 5 decimals, `shape_weight` to 1 decimal, and integer hyperparameters (`min_samples`, `epsilon`) are serialized as integers rather than values like `3.0`.
- If computation is correct but CSV formatting is not, rewrite only the output file with explicit format specifiers instead of rerunning the full search.
- After writing, read the complete CSV back and validate all rows, not just `head`: confirm it is non-empty, parses fully, each row has exactly 5 fields, numeric rounding matches the spec, and every remaining row is Pareto-optimal under equality-aware dominance.
- Reopen `/root/pareto_frontier.csv` and inspect its header plus at least one written data row; do not treat successful script exit alone as sufficient verification.



## New Section

## Execution Discipline

- Follow the task's required interaction and tool/action format exactly; if an exact completion string is required, use it verbatim.
- If you write a script, inspect the saved file, then run it and check for syntax/runtime errors before relying on it.
- Do not stop at "script written", "job started", or inferred progress. If you run work asynchronously or in the background, wait/poll until it finishes, then verify the artifact.
- Report only progress directly supported by command output or file inspection.
- After any performance-driven rewrite, re-check the final implementation against the task requirements: DBSCAN per image, greedy matching with max 100px, F1/delta computation, `F1 > 0.5` filtering, and Pareto selection.

- Treat any task-specific interaction/tool-call format and exact completion string as mandatory; before every tool use and before the final response, match the required protocol literally.
- After writing any script, immediately inspect the saved file contents to confirm they are complete and not truncated, then run a syntax/basic execution check before relying on it.
- Prefer finishing the full run in the foreground once performance is acceptable. If you do run work asynchronously, you must still wait/poll to completion, inspect the final artifact, and avoid concluding while optimization is still running.
- Do not claim numeric progress unless logs or command output explicitly show it; otherwise report only progress directly supported by output or file inspection.
- If you optimize performance via transformed coordinates, precomputed distances, batching, or parallelism, confirm the optimization does not change scoring semantics: matching and `delta` must still use ordinary Euclidean distance on original centroids.
- After any runtime/performance rewrite, re-check the final code against the task spec: per-image DBSCAN grouping, greedy 100px matching, required `F1=0`/`delta=NaN` edge cases, post-computation `F1 > 0.5` filtering, and equality-aware Pareto selection.
- Before finalizing, validate `/root/pareto_frontier.csv` end-to-end, then separately verify any required final completion string or response format.


Critical protocol and evidence checklist:
- Start by checking the task's allowed tool set, required action syntax, and exact completion contract. Use only the permitted interface for every step; do not improvise alternate tool names, wrapper formats, XML-style tags, or unofficial completion messages.
- If the environment requires a specific final completion string or action schema for shell commands, treat it as mandatory and emit it verbatim only after all required artifacts have been verified.
- Bash/tool inputs must be directly executable commands only. Do not send natural-language placeholders or intent labels such as `list files`, `check progress`, `monitor job`, or `run the optimization script with a timeout`; instead issue explicit commands such as `head -n 5 /root/data/citsci_train.csv`, `python /root/optimize_dbscan.py`, `tail -n 20 /root/log.txt`, or `cat /root/pareto_frontier.csv`.
- Check path type before operating on it: list directories first, then open specific files. Do not attempt to read a directory as if it were a file.
- When creating a script or other critical artifact, write the full intended contents in the file-creation step itself; do not use placeholders, TODOs, status notes, or prose summaries in place of executable code.
- After writing any script or critical artifact, read the saved file back from disk and confirm it is complete and non-placeholder before executing or relying on it.
- Before relying on a new script, run a basic validation step such as inspecting the saved contents and/or `python -m py_compile <script>`.
- When executing a script you created, invoke the exact saved path explicitly, not a paraphrase like `python optimization script`.
- Keep monitoring tied to the original job/process/artifact. Do not start separate background jobs merely to poll, wait, or monitor another background job unless the task explicitly requires it.
- If execution is launched in the background, poll/wait until it actually finishes, then verify the expected artifact before concluding. Never stop at `job started`, `process still running`, early log lines, or while output is still partial.
- When monitoring progress, use commands that produce observable evidence in this environment: inspect concrete files, logs, exit codes, and timestamps. Do not infer success from absence of errors while the process is still running.
- Treat progress logs as non-final evidence. Before moving on or declaring completion, directly verify `/root/pareto_frontier.csv` itself: existence, non-empty content, exact required header, and at least one data row when results are expected.
- Do not claim script contents, counts, filtering totals, implementation details, or results unless they were directly shown by file inspection, logs, or captured command output in the current session.
- Before any final report or completion signal, ensure every factual claim is traceable to observed command output, logs, or file contents from this run.
- If a script fails and you need to patch it, first inspect the traceback and read the relevant saved source lines around the failing code before editing. Make replacements against exact existing text from the file; do not issue edits against invented placeholders.
- Minimal debug loop: (1) run the script and capture the real error, (2) open the referenced code region, (3) edit the actual source text, (4) re-open the saved file to confirm the change, (5) rerun before proceeding.

Mandatory pre-final checklist:
1. Confirm every tool/action used the exact required interface for this environment.
2. If a script was written, inspect the actual saved contents before execution.
3. Run the script using its exact path.
4. Wait for completion rather than stopping at monitoring output.
5. Verify `/root/pareto_frontier.csv` exists, is non-empty, and matches the spec.
6. Emit any required final completion text verbatim.
