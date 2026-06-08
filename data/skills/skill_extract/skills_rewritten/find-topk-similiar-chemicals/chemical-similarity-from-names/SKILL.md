---
name: chemical-similarity-from-names
description: "Extract chemical names from documents, resolve to structures via external resources, and compute top‑k similar chemicals using Morgan fingerprints (radius 2, with chirality) and Tanimoto similarity with deterministic tie-breaking."
---

# Chemical Similarity from Names

This skill provides a reusable workflow for: (1) extracting chemical names from a document, (2) resolving names to molecular structures using external chemistry resources (no manual mapping), and (3) computing top‑k most similar chemicals using Morgan fingerprints (radius = 2, include chirality) and Tanimoto similarity. It also standardizes deterministic sorting and tie-breaking.

## When to Use

Use this skill when you need to:
- Start from chemical names (in a PDF or text) and find the most similar molecules to a target name.
- Convert names to structures via an external resource (e.g., PubChem or a name-to-structure resolver) without hardcoded mappings.
- Compute similarity with Morgan fingerprints (radius 2, chirality enabled) and Tanimoto similarity.
- Return a top‑k list sorted by similarity descending with alphabetical ordering on ties.

## Core Workflow

1. Input and Environment Checks
   - Confirm the input document is accessible and identify its format (PDF or text).
   - Verify required libraries are available: a PDF text extractor, HTTP client, and a chemistry toolkit (e.g., RDKit). If some are missing, either install them or use the provided fallbacks.

2. Extract Candidate Names
   - Extract text from the document.
   - Split into lines, trim whitespace, and filter empty lines.
   - Optionally filter obvious non-name noise (e.g., page headers/footers) with simple heuristics, but avoid aggressive filters that drop valid names.
   - Deduplicate names while preserving their first-seen order for efficient lookup.

3. Resolve Names to Structures
   - For each unique name, resolve to a structural representation (prefer isomeric SMILES to preserve chirality) using an external chemistry resource.
   - Use retries with exponential backoff and modest pacing between requests to avoid rate limits.
   - Cache resolved names in-memory; optionally persist a local cache to reduce repeated network calls across runs.
   - Do not write any manual mapping from names to structures.

4. Build Molecular Fingerprints
   - Parse SMILES to molecules using the chemistry toolkit, sanitize molecules, and skip any that fail to parse.
   - Compute Morgan fingerprints with:
     - radius = 2
     - useChirality = True
     - a standard bit vector size (e.g., 2048)

5. Similarity Computation
   - Resolve and fingerprint the target molecule name.
   - Compute Tanimoto similarity between the target fingerprint and each candidate fingerprint.

6. Ranking and Tie-Breaking
   - Sort results by:
     - similarity score in descending order, then
     - chemical name in ascending alphabetical order (deterministic tie-breaker).
   - Return the top k names (and optionally scores for diagnostics).

## Fingerprint and Similarity Settings

- Fingerprint: Morgan/ECFP-like bit vector using radius=2 and useChirality=True.
- Similarity: Tanimoto similarity on bit vectors.
- Keep the radius and chirality exactly as specified; changing them alters rankings and violates requirements.

## Verification

Perform these checks to validate your implementation:
- Dependency check: confirm the PDF extractor and chemistry toolkit imports succeed. If not, install or choose the fallback extractor.
- Name extraction sanity check: ensure the extracted list is non-empty and contains plausible chemical names (no page numbers only).
- Resolution coverage: log count of resolvable vs. unresolvable names; a non-zero resolvable subset should be present.
- Fingerprint correctness: assert that all fingerprints have the expected bit length and that chirality is enabled.
- Deterministic sorting: verify that when two candidates have identical similarity scores, their alphabetical order determines their relative ranking.
- Output shape: confirm the function returns exactly a list of names (or list of (name, score) if your interface requires it) and exactly k entries when possible.

## Common Pitfalls

- Manual name-to-structure mapping: prohibited. Always use an external resolver (e.g., PubChem, public name-to-structure services) or toolkit name parsers.
- Wrong fingerprint settings: forgetting to set radius=2 or useChirality=True leads to incorrect similarity results.
- Using the wrong similarity metric: ensure you specifically compute Tanimoto similarity for bit vectors, not Dice or Cosine.
- RDKit parsing issues: Chem.MolFromSmiles can return None; skip such entries and continue rather than failing the whole run.
- Aggressive text filtering: removing lines too aggressively can drop valid names. Prefer simple heuristics and manual review if needed.
- Rate limiting and timeouts: unthrottled resolver requests can fail. Implement retry with exponential backoff and short sleeps between calls.
- Non-deterministic ties: rounding scores before sorting can mask ties or reorder near-equal scores. Sort by the raw score (descending) and then by name (ascending) to enforce deterministic output.
- Case sensitivity in ties: inconsistent casing can cause unstable order. Use a consistent case (e.g., lowercase) for the secondary sort key.

## Optional Script Usage

This skill provides an optional helper script (scripts/chem_similarity.py) that:
- Extracts names from a PDF (with a fallback extractor),
- Resolves names to isomeric SMILES via external services with retries and caching,
- Computes Morgan fingerprints (radius=2, chirality on), and
- Returns top‑k similar names to a target.

Example (Python):
- from scripts.chem_similarity import topk_similarity_from_pdf
- results = topk_similarity_from_pdf(target_name="Acetaminophen", pdf_path="molecules.pdf", k=5)
- print(results)

You can adapt the helper functions to match any required function signature in your task, preserving the workflow and verification checks above.
