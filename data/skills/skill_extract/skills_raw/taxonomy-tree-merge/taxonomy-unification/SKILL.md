---
name: taxonomy-unification
description: "Unify multiple hierarchical category taxonomies into a single 5-level catalog using weighted text embeddings, recursive clustering, rule-based naming, and validation."
---

# Hierarchical Taxonomy Unification

Unify category taxonomies from different sources (e.g., marketplaces, catalogs) into a single 5-level hierarchy that satisfies structure and naming constraints. The workflow combines text preprocessing, weighted embeddings, recursive clustering, rule-based naming, and validation.

## When to Use

Use this skill when you need to:
- merge category hierarchies from multiple platforms into a single taxonomy
- enforce a 5-level hierarchy with consistent naming and structure
- generate cluster names that represent members and meet naming constraints
- validate the resulting taxonomy for structural and naming quality

## Core Workflow

1. Input Inspection and Normalization
   - Confirm each source has a column with hierarchical paths (e.g., "category_path").
   - Normalize separators into a single delimiter (e.g., ">"). Accept common delimiters such as ">", "/", "→", or "\\u203a" and normalize spacing (one space around the delimiter).
   - Split category paths into up to 5 levels: level_1..level_5.
   - Trim whitespace, lowercase, remove extra punctuation, and standardize spelling variants where possible.
   - Drop duplicates after normalization. Compute and store the depth of each input path.

2. Text Standardization (per level)
   - For each level token, apply:
     - lowercasing
     - punctuation cleanup (keep alphanumerics and space)
     - whitespace collapse
   - Optional: lemmatization or stemming (ensure required resources are available; otherwise fall back to simple normalization).
   - Keep a dictionary of normalized strings to original strings for reference during naming.

3. Weighted Embedding Generation
   - Produce a vector for each input path by combining level-wise text embeddings with exponential decay (heavier weight on higher levels).
     - Example: weight(level k) = base^(k-1), with base around 0.5–0.7.
   - Performance-critical: batch-encode unique strings per level and cache results. Avoid encoding the same token repeatedly.
   - Compute the path vector as a weighted sum (or average) of per-level embeddings for the available levels.
   - Set random seeds for deterministic behavior where models support it.

4. Recursive Clustering (Top-Down)
   - Level 1: cluster all items into 10–20 broad categories.
   - Levels 2–5: for each parent cluster, cluster its items into 3–20 subclusters.
   - Stop early if a parent has fewer than the minimum required items for subdivision.
   - Choose a distance metric appropriate for embeddings (e.g., cosine). Algorithms like agglomerative clustering or k-means are suitable. Use parameter search within allowed bounds to balance cluster sizes.
   - Aim for a balanced pyramid: more categories at deeper levels than at shallower ones, without exploding branch factors.
   - Encourage even distribution of sources: avoid clusters dominated by a single source when possible (e.g., via stratification or mild penalties during parameter selection).

5. Cluster Naming (Rule-Based)
   - Extract salient words from member category texts (weighted by level and frequency). Remove stopwords and very generic terms.
   - Select 2–5 representative words (max 5) and join with " | " to form the category name.
   - Ensure names are representative (≥70% of member items contain at least one of the chosen terms or reflect the core concept).
   - Enforce constraints:
     - no name overlap between a category and its parent (remove or substitute overlapping words)
     - sibling categories must be distinct: measure Jaccard overlap of token sets and keep it < 0.30; otherwise rename or merge
     - normalize variants (singular/plural), ensure consistent casing/style

6. Assignment and Export
   - For each input path from each source, record: source, original category_path, depth, and unified_level_1..unified_level_5.
   - Export two CSVs:
     - unified_taxonomy_full.csv: mapping of each input path to the unified levels
     - unified_taxonomy_hierarchy.csv: unique unified paths across levels (all valid paths from level 1 to deeper levels)

7. Validation
   - Run the validator script to check:
     - number of top-level categories is within 10–20
     - children per parent are within 3–20 for deeper levels (compliance rate)
     - names use " | " as intra-name separator with ≤5 terms
     - no parent-child name overlap
     - sibling distinctness (<30% word overlap)
     - balanced pyramid structure (monotonic increase of unique categories with depth is expected in aggregate, allowing for occasional plateaus)
     - even distribution of sources across levels (no single source overwhelmingly dominates most parents)

## Verification

Success criteria:
- Both CSVs exist and have expected columns.
- Top-level categories count is within 10–20.
- Most parent nodes have 3–20 children at each deeper level.
- All category names contain ≤5 terms and use " | " between terms.
- Parent-child pairs have zero overlapping name tokens (after normalization).
- Sibling pairs have <30% token overlap in the majority of cases.
- Pyramid structure shows reasonable growth with depth.
- Each source is present across a wide range of top-level categories.

Use the included validator script:
- python scripts/validate_taxonomy.py --full path/to/unified_taxonomy_full.csv --hierarchy path/to/unified_taxonomy_hierarchy.csv

## Common Pitfalls and Remedies

- Wrong or missing input column
  - Symptom: empty splits or NaNs for all levels.
  - Fix: ensure a column like "category_path" exists and normalize separators before splitting.

- Slow embedding generation
  - Symptom: extremely long runtime during encoding.
  - Fix: deduplicate and batch-encode unique tokens per level; cache embeddings; raise batch size if memory allows.

- Argument format confusion for external pipelines
  - Symptom: pipeline rejects sources.
  - Fix: verify the expected CLI usage (often path:name pairs). Avoid spaces around the colon; quote arguments if necessary.

- Naming violations
  - Symptom: names exceed 5 terms, overlap with parent, or siblings too similar.
  - Fix: enforce token filters, cap term count to 5, explicitly remove parent tokens from child names, and re-score candidate names for distinctness.

- Imbalanced clusters or source dominance
  - Symptom: many parents with too few or too many children; one source dominates clusters.
  - Fix: adjust cluster counts within allowed bounds; consider stratified sampling or penalties for source imbalance when choosing k.

- Depth inconsistencies
  - Symptom: paths exceed 5 levels or have missing intermediate levels.
  - Fix: truncate deeper paths to 5; allow None for missing deeper levels; never duplicate parent names to fill depth.

## Optional Script Usage

- scripts/validate_taxonomy.py: Validate the unified outputs against structural and naming rules. Run it after exporting your results.
- scripts/path_tools.py: Normalize input category paths (separator and text cleanup) and compute depth before embedding/clustering.

These utilities are independent of any specific dataset and can be integrated into your preprocessing and QA steps.
