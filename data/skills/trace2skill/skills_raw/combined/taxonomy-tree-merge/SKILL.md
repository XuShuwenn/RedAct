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

## Output Files

### unified_taxonomy_full.csv
- source, category_path, depth (1-5)
- unified_level_1 through unified_level_5

### unified_taxonomy_hierarchy.csv
- unified_level_1 through unified_level_5
- All paths from low to high granularity


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

