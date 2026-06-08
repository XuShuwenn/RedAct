---
name: taxonomy-unification
description: "Build, balance, and validate a unified 5-level taxonomy from multiple heterogeneous category hierarchies."
---

# Unified Taxonomy Construction and Validation

A reusable workflow to merge multiple e-commerce (or similar) category taxonomies into one 5-level hierarchy that is balanced, consistently named, and suitable for cross-source analytics.

## When to Use

Use this skill when you need to:
- Consolidate category hierarchies from multiple sources into a single taxonomy
- Standardize naming and structure for downstream reporting and metrics
- Enforce structural and naming constraints (branching limits, overlap rules, balanced pyramid)

## Core Workflow

Follow these phases end-to-end. Do not finalize until verification passes.

Phase 0 — Inputs and Expectations
- Inputs: multiple CSV files each containing category paths (e.g., "A > B > C") in a column such as `category_path` and a `source` label you assign per file.
- Output 1 (mapping): one row per input path with columns: `source`, `category_path`, `depth` (1–5), and `unified_level_1` … `unified_level_5` (empty where not applicable).
- Output 2 (hierarchy): all unique unified paths, as columns `unified_level_1` … `unified_level_5`.

Phase 1 — Load and Standardize Inputs
- Load each file; confirm a category path column exists. If the column name varies, alias it to `category_path`.
- Parse hierarchical paths robustly:
  - Accept delimiters like `>`, `/`, `|`, `→`; normalize all to `>` before splitting.
  - Strip extra whitespace; collapse duplicate delimiters; drop empty nodes.
- Standardize text:
  - Lowercase; trim; normalize Unicode; remove repeated punctuation; standardize common conjunctions (`&` → `and` or keep consistently) and spacing.
  - Normalize singular/plural only if deterministic; avoid aggressive stemming that changes meaning.
- Deduplicate identical paths per source; record original depth.

Phase 2 — Canonical Tokenization and Signatures
- For each node text, build a normalized token set for later comparisons:
  - Split on non-alphanumeric boundaries; remove stopwords (e.g., a, the, of, for, with, in, on) and short noise tokens.
  - Keep domain-relevant numerics (e.g., `3d`), but normalize units if needed.
- Create a canonical form for naming and comparison (used later for overlap checks and naming).

Phase 3 — Candidate Top-Level (Level 1) Design
- Goal: 10–20 broad, mutually distinct categories covering all sources.
- Strategy options (pick one; use the other as fallback):
  1) Lightweight TF-IDF + KMeans/MinibatchKMeans over unique full paths or top segments; sweep K in [10, 20], select by silhouette/Calinski-Harabasz and coverage.
  2) Embeddings (if available) + hierarchical clustering; cache embeddings for unique strings only; batch to avoid bottlenecks; persist cache for reruns.
- Ensure coverage: every input path assigns to a top-level cluster.

Phase 4 — Recursive Clustering (Levels 2–5)
- For each parent cluster, recursively cluster its members into 3–20 children.
- Balance:
  - If a parent would have <3 children, merge it with a nearby sibling parent or lift children upward.
  - If a parent would have >20 children, split by salient terms, TF-IDF topics, or cluster again with a higher K.
- Stop when either:
  - You reach level 5, or
  - Further splitting would violate child count constraints or harm distinctness.

Phase 5 — Category Naming
- Derive names from members’ texts using token frequencies:
  - Compute per-cluster term scores (e.g., TF-IDF within the cluster vs. siblings).
  - Select top informative terms (1–5) and join with " | " to form the category label.
- Enforce:
  - Max 5 words per name.
  - Avoid parent-child overlap: child name should introduce new terms vs. parent.
  - Distinct siblings: pairwise word overlap < 30% (use intersection over min-size as the ratio).
- If violations occur, adjust term selection or re-cluster borderline items.

Phase 6 — Even Source Distribution
- Check that categories at each level are not dominated by a single source:
  - Compute per-source counts within each top-level and across levels.
  - If extreme skews occur, reassign borderline items where semantically valid or refine splitting criteria so clusters capture cross-source commonality.

Phase 7 — Produce Outputs
- Mapping (full): for every input path, assign `unified_level_1..5`; set `depth` to the count of non-empty unified levels (max 5).
- Hierarchy: unique combinations of `unified_level_1..5`. Include shorter paths by leaving trailing levels empty.
- Ensure consistent separators and casing in all unified labels.

## Verification

Success criteria (use the provided validator to check):
- Top-level count is within 10–20.
- Every parent (levels 1–4) has 3–20 distinct children, except true leaves.
- Each category name has ≤ 5 words, uses a consistent style (e.g., "term1 | term2").
- No parent-child name overlap beyond the allowed threshold (default 0%).
- Siblings are distinct: pairwise word overlap < 30%.
- The hierarchy forms a reasonable pyramid (counts generally increase with depth).
- Sources are represented across the taxonomy without extreme concentration.

Run validator:
- python scripts/taxonomy_validator.py --full path/to/unified_taxonomy_full.csv --hierarchy path/to/unified_taxonomy_hierarchy.csv
- Optional thresholds are configurable; see script help.

## Common Pitfalls and How to Avoid Them
- Embedding bottlenecks: compute embeddings only for unique strings, cache to disk, and batch requests. Fall back to TF-IDF if embeddings are unavailable or too slow.
- Skipping validation: always run automated checks before finalizing; adjust clusters/names until constraints pass.
- Overfitting top-levels: ensure 10–20 broad buckets; do not let niche topics become level 1.
- Name collisions and overlap: enforce constraints programmatically; regenerate names using alternative terms if overlap is high.
- Unbalanced branching: merge tiny child clusters (<3) or split oversized clusters (>20) systematically.
- Inconsistent separators/casing: normalize once centrally and reuse.
- Process management errors: run the pipeline to completion (foreground or supervised), avoid starting uncontrolled background jobs you can’t track, and persist intermediate artifacts (e.g., caches, logs) deterministically.
- Missing columns: verify required columns exist before processing; fail fast with clear messages.

## Optional Script Usage

Use the validator to confirm structural and naming compliance and to diagnose where to refine clustering or naming.

Examples:
- Basic validation:
  - python scripts/taxonomy_validator.py --full unified_taxonomy_full.csv
- With hierarchy and stricter sibling overlap:
  - python scripts/taxonomy_validator.py --full unified_taxonomy_full.csv --hierarchy unified_taxonomy_hierarchy.csv --sibling-overlap-threshold 0.25
- JSON report to file:
  - python scripts/taxonomy_validator.py --full unified_taxonomy_full.csv --json > validation_report.json
