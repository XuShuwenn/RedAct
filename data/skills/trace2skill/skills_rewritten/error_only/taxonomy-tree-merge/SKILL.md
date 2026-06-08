---
name: taxonomy-tree-merge
description: "Merge product category taxonomies from Amazon, Facebook, and Google Shopping into unified 5-level hierarchy."
---

# Taxonomy Tree Merge

## When to Use

- Merge multiple taxonomies into unified hierarchy
- Standardize e-commerce category systems
- Create 5-level category structure

## Execution Protocol

- Follow the task/environment's required tool-call or action format exactly.
- Use only the explicitly authorized toolset for the current session; do not invent alternate wrappers, XML-style calls, or subagent workflows.
- Do not claim a script, helper, or pipeline ran successfully unless you actually executed it and observed confirming output.
- Emit any exact required completion signal only after both required output files are verified on disk.


- Before the first action, identify the session's exact required action/tool-call schema and treat it as a hard constraint for every step.
- If the environment specifies an exact action syntax, use that syntax verbatim throughout.
- Use only tools explicitly authorized by the environment; do not invent alternate wrappers, XML-style tags, pseudo-tools, `read_file`, `run_shell_command`, `Read`, `Write`, `TaskOutput`, `TodoWrite`, or subagents when they were not provided.
- When the environment requires actions one at a time, emit one valid action, wait for its result, then decide the next step from the observed output.
- Read the current task instructions and any obvious local entry-point documentation if present to confirm deliverables, required filenames, and run procedure before implementation.
- Use concrete executable commands with real absolute paths and arguments; do not send descriptions such as "inspect inputs" or "run pipeline" as if they were commands.
- If a command fails, inspect the actual error, `--help`/usage text, or source before retrying; do not guess flags or positional arguments.
- If a command fails because a utility is unavailable, switch to confirmed alternatives such as Python one-liners, `find`, `grep`, direct `/proc` inspection, or file/timestamp checks.
- Do all file inspection, script creation, execution, monitoring, and output validation through the authorized interface only.
- Create new scripts or temporary code only inside confirmed allowed working/output directories for the task. Do not write helper files to unverified locations such as `/root/` unless explicitly permitted.
- After stating a plan, immediately issue the corresponding permitted action; do not stop at intent or setup narration.
- If the environment requires a specific completion token such as `ACTION: TASK_COMPLETE`, emit that exact token verbatim exactly once only after final validation.


## Input Files

- `/root/data/amazon_product_categories.csv`
- `/root/data/fb_product_categories.csv`
- `/root/data/google_shopping_product_categories.csv`

All contain `category_path` column with hierarchical paths like:
`electronics > computers > Laptops`

Facebook files may include extra columns (for example `category_id`) and may have a BOM-prefixed header. Read all three CSVs first, normalize column names, and confirm the `category_path` field before building the merge.

Once this inspection confirms the usable schema, do not delay implementation by searching for alternate datasets, unrelated skill folders, or generic taxonomy pipelines unless the task explicitly requires them.

Use the provided CSVs directly when possible. Prefer a self-contained script/notebook over external pipelines unless an existing script is first inspected and verified to produce the exact required output files, columns, and hierarchy constraints.


## Workflow

## Workflow

1. Inspect all three input CSVs before choosing an approach.
   - Read headers and sample rows from each file.
   - Confirm the `category_path` column exists and note delimiter, casing, spacing, quoting, null-value, depth, or encoding issues.
2. Work from the specified paths and scope.
   - Read inputs only from `/root/data/` and write outputs only to `/root/output/`.
   - Do not pivot to other CSVs, skill folders, or external frameworks unless the task explicitly authorizes them.
3. Prefer simple, inspectable methods first.
   - Start with deterministic normalization plus pandas and rule-based merging.
   - Use heavier clustering, embeddings, or download-heavy libraries only if there is clear evidence they are needed and dependencies are available.
4. Reuse existing code only after validation.
   - If a helper script or pipeline exists, inspect its actual code or interface before using it.
   - Verify it reads the available inputs, can produce the exact required output filenames and schema, and meets the hierarchy constraints.
   - If no verified helper is suitable, write a small local end-to-end script that reads from `/root/data` and writes the required outputs.
5. Make runtime decisions from observable evidence.
   - Do not replace, interrupt, or optimize a running job unless logs, errors, stalled progress, timestamps, file growth, or measured bottlenecks show intervention is necessary.
   - If you edit code or switch scripts, inspect the updated file or generated output before assuming the change took effect.
6. Execute the merge end to end.
   - Produce both `/root/output/unified_taxonomy_full.csv` and `/root/output/unified_taxonomy_hierarchy.csv` before declaring success.

## Rules

1. Top level: 10-20 broad categories
2. Each level: 3-20 subcategories per parent
3. Use " | " separator, max 5 words per category
4. Category name representative of 70%+ subcategories
5. Standardize text, avoid overlap with parent
6. Siblings: < 30% word overlap
7. Balance cluster sizes (pyramid structure)
8. Even distribution from all sources

## Recovery Guardrails

- When recovering from a failing or uncertain approach, inspect the candidate replacement script or pipeline before running it.
- Never save planning notes, summaries, or placeholders into a `.py` file and execute it as if it were implementation.
- Prefer a quick verification step such as reopening the file, `python -m py_compile`, or an equivalent syntax check before a full run.

## Output Files

### unified_taxonomy_full.csv
- source, category_path, depth (1-5)
- unified_level_1 through unified_level_5

### unified_taxonomy_hierarchy.csv
- unified_level_1 through unified_level_5
- All paths from low to high granularity


> **Do not finish on intent, process activity, launch state, or a task ID alone.** A valid completion requires concrete commands issued through the environment's exact allowed interface, an observed merge execution result, both required CSVs present and non-empty in `/root/output/`, and on-disk verification after the final run.

Mandatory completion sequence:
1. Use the exact environment-required action/tool format on every step.
2. Run concrete executable commands only; no natural-language placeholders.
3. If any process was backgrounded, verify it actually finished successfully.
4. Verify both required CSVs on disk by reopening them.
5. Emit the exact completion signal only after steps 1-4 are satisfied.

Protocol checklist before completion:
- Confirm every action used the exact environment-required syntax and only the explicitly authorized tools.
- Confirm any shell commands were actual executable commands with concrete arguments, not descriptive placeholders.
- Confirm the final response includes the exact required completion signal if one was specified by the environment.

Validation checklist before completion:
- Confirm you actually inspected `/root/data/amazon_product_categories.csv`, `/root/data/fb_product_categories.csv`, and `/root/data/google_shopping_product_categories.csv` before selecting the implementation.
- Confirm you actually executed the merge step after inspection; input review alone is not completion.
- If you used an existing helper script or pipeline, confirm you verified its path, interface, and fit to this task before execution.
- If you created or modified code, confirm the saved file contents were written as intended and that the final run used that version.
- If any earlier command output was truncated or unclear, rerun a narrower inspection command before relying on that observation.
- Prefer completing a working end-to-end run over speculative performance tuning; only optimize after a concrete bottleneck blocks creation of the required output files.

- Confirm `/root/output/unified_taxonomy_full.csv` exists, is non-empty, and includes `source`, `category_path`, `depth`, and `unified_level_1` through `unified_level_5`.
- Confirm `/root/output/unified_taxonomy_hierarchy.csv` exists, is non-empty, and includes `unified_level_1` through `unified_level_5`.
- Inspect a few rows from each file to confirm paths are populated consistently, use ` | ` separators, and depths are within 1-5 where applicable.
- Only declare completion after both required files are present and validated on disk.
- If the environment requires an exact completion signal such as `ACTION: TASK_COMPLETE`, emit it verbatim only after all validation is complete.

- If you used an existing helper, modified pipeline, or background job, confirm from logs, exit status, fresh timestamps, or the actual generated CSVs that the final run completed successfully; do not treat launch alone as completion.
- Re-open the written CSVs from `/root/output/` and verify the required columns from the actual saved files, not just in-memory DataFrames or intended code paths.
- If you changed approaches mid-task, re-verify that the final method still reads the intended `/root/data/` inputs and produces the exact required outputs.
- Check the generated hierarchy against the stated rules on sampled and aggregated output: top-level count is 10-20, per-parent child counts are typically 3-20, labels are concise (max 5 words each), levels are populated consistently up to a 5-level maximum, and there is no obvious parent/child duplication or excessive sibling overlap.
- Do not claim completion from intent alone; verify the merge actually ran and produced both CSVs on disk.



## Tips

- pandas for CSV processing
- Hierarchical clustering or rule-based merging
- Text similarity for disambiguation

- Prefer a short, self-contained pandas script or notebook that reads the three provided CSVs, normalizes `category_path`, builds the unified hierarchy, and writes both outputs in one run.
- If you must reuse existing code, inspect enough of the implementation to confirm input paths, output paths, output columns, and hierarchy behavior before running it.
- When monitoring execution, use concrete checks such as file existence, file growth, row counts, recent log lines, and exit status.


- Confirm you followed the environment's exact action/tool protocol throughout; do not switch to unsupported call formats mid-task.
- Confirm the trajectory included actual execution steps, not just planning statements about what you would run.
- If you mention existing scripts, notebooks, or docs, make sure the log includes actual file-reading actions for them; otherwise remove those claims.
- If you relied on any existing project script, README, or workflow file, confirm you first located its real absolute path and directly inspected enough of it to verify how it should be run and what outputs it should produce.
- If you used an existing helper, pipeline, repository code, or CLI, confirm you inspected enough of it to know the exact invocation syntax before the first substantive run rather than inferring or guessing the command.
- If you created helper code, confirm it was saved only in an explicitly allowed directory and that you inspected the saved contents before running it.
- If a command failed with `usage:` output, argument errors, or missing required flags, confirm you used that feedback to form and run the corrected command; do not count the failed launch as progress.
- If you launched an existing or replacement pipeline, inspect post-launch evidence from the actual run: exit code, recent log lines, fresh output timestamps, file sizes, or sample rows from generated CSVs.
- Do not stop a running job or switch approaches based on a warning, startup banner, or brief inactivity alone; first confirm whether outputs are still being produced or progress has actually stalled.
- If any job was backgrounded or asynchronous, confirm it reached a terminal state and that validation is based on finished output files, not intermediate logs.
- If an initial helper, pipeline, or long-running job did not produce validated outputs promptly, confirm you actually executed a fallback approach rather than only monitoring the original run.
- Verify completion from deliverables, not from process activity: both required CSVs must exist, be readable, and have the required columns and sampled contents.
- Do not claim you updated a script, switched pipelines, or reran anything unless the edit/run is visible in your actual actions and you verified the resulting file, logs, exit status, or outputs.
- If the environment requires an exact completion signal such as `ACTION: TASK_COMPLETE`, emit it verbatim only after all validation is complete.


- Prefer a short, self-contained pandas script run in the foreground when practical; it reduces protocol mistakes and makes completion easier to verify.
- When you do use background execution, capture the PID or log path, then explicitly check for process completion and output-file creation with concrete commands.
- Good inspection commands are concrete and reproducible, e.g. `ls -l /root/data`, `head -n 5 file.csv`, `python - <<'PY' ... PY`, or `python script.py --help`.
- Bad tool usage: vague requests like "check files", "preview the CSVs", or "run the taxonomy pipeline" without an actual command.
- Before a full run, verify both the input schema and the chosen script's invocation/arguments with small, explicit checks.
- Operational checklist: inspect inputs using exact absolute paths -> run the merge command -> verify both output files from disk -> emit the exact required completion signal.
- Do not substitute narrative intent for execution; completion requires the concrete command and its observed result.
- Every read/write/run target should be an actual absolute path visible in the environment.

