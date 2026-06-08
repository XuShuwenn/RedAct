---
name: taxonomy-tree-merge
description: "Merge product category taxonomies from Amazon, Facebook, and Google Shopping into unified 5-level hierarchy."
---

# Taxonomy Tree Merge

## When to Use

- Merge multiple taxonomies into unified hierarchy
- Standardize e-commerce category systems
- Create 5-level category structure

## Input Files

- `/root/data/amazon_product_categories.csv`
- `/root/data/fb_product_categories.csv`
- `/root/data/google_shopping_product_categories.csv`

All contain `category_path` column with hierarchical paths like:
`electronics > computers > Laptops`

Facebook files may include extra columns (for example `category_id`) and may have a BOM-prefixed header. Read all three CSVs first, normalize column names, and confirm the `category_path` field before building the merge.

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
- Confirm `/root/output/unified_taxonomy_full.csv` exists, is non-empty, and includes `source`, `category_path`, `depth`, and `unified_level_1` through `unified_level_5`.
- Confirm `/root/output/unified_taxonomy_hierarchy.csv` exists, is non-empty, and includes `unified_level_1` through `unified_level_5`.
- Inspect a few rows from each file to confirm paths are populated consistently, use ` | ` separators, and depths are within 1-5 where applicable.
- Only declare completion after both required files are present and validated on disk; if the environment requires an exact completion signal such as `ACTION: TASK_COMPLETE`, emit it verbatim after verification.


## Tips

- pandas for CSV processing
- Hierarchical clustering or rule-based merging
- Text similarity for disambiguation
