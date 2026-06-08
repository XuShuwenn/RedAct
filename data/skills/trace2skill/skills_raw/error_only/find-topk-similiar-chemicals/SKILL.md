---
name: find-topk-similiar-chemicals
description: "Find top-k similar chemicals using Morgan fingerprints and Tanimoto similarity, with PubChem/RDKit for molecular representations."
---

# Chemical Similarity Search

## When to Use

- Find similar chemicals in a molecule pool
- Convert chemical names to molecular SMILES
- Compute molecular fingerprints and similarity

## Key Components

### Morgan Fingerprints
- Radius = 2
- Include chirality
- Tanimoto similarity for comparison

### External Resources
- PubChem: chemical name → SMILES conversion
- RDKit: fingerprint computation

## Function Signature

```python
def topk_tanimoto_similarity_molecules(target_molecule_name, molecule_pool_filepath, top_k) -> list:
    # Returns list of top-k similar molecules sorted by similarity descending
    # Alphabetical ordering for ties
```

## Input

- Target molecule name (string)
- Molecule pool file (PDF with chemical names/structures)

- Treat `molecule_pool_filepath` as the source of truth; do not replace it with a guessed absolute path.
- Treat the PDF contents as the authoritative candidate set; returned molecule names must come only from molecules actually parsed from this pool, not from PubChem synonyms, preferred labels, or external molecules.
- Inspect all pages of the PDF before coding extraction logic; molecule names/structures may be distributed across the full document.
- If PDF extraction looks truncated or malformed (for example abrupt cutoff, partial tokens, missing pages, wrapped names split incorrectly, headers/footers mixed into names, or suspiciously short output), re-extract/inspect before computing similarities.

## Output

- Sorted list of top-k similar chemicals
- Format: [(molecule_name, similarity_score), ...]

- Only return names exactly as they appear in the extracted molecule pool.
- Do not introduce alternate names, PubChem synonyms, or canonicalized labels as output names.
- Tie-breaking requirement is literal: if similarity scores are equal, sort by the molecule name in normal alphabetical order as written.
- Do NOT switch to case-insensitive ordering, locale-aware ordering, or any other modified interpretation unless the task explicitly asks for it.
- Example: use `key=lambda x: (-x[1], x[0])`, not `key=lambda x: (-x[1], x[0].lower())`.


## Validation Checklist

## Validation Checklist

- Test with the exact provided molecule pool file path; do not inspect one PDF and validate against another.
- Build the candidate list from the extracted PDF first, then compute similarity only for those entries.
- Validate the parsed molecule pool before scoring: confirm all pages were read and extraction is not cut off, truncated, or malformed.
- Verify that every returned molecule name appears in the parsed PDF pool before concluding the result is correct.
- If any output molecule is absent from the extracted pool, treat it as a bug in parsing, path usage, name mapping, or evaluation setup.
- If some molecules cannot be resolved to structures, handle them explicitly (for example skip with logging or clear error behavior) and ensure the final top-k still comes only from remaining valid pool entries.
- Validate lookup behavior with several common chemicals such as Caffeine, Aspirin, Ibuprofen, Naproxen, and Phenol. Repeated failures on these are blocking, not acceptable noise.
- Verify the final list is sorted by similarity descending, with literal alphabetical ordering for ties.
- Run at least one fresh end-to-end call of `topk_tanimoto_similarity_molecules(...)` after the last substantive edit and confirm it returns a visible list of `(molecule_name, similarity_score)` tuples.
- Treat warnings-only runs, truncated output, empty results (`[]`), exceptions, or incomplete verification as blockers; rerun with explicit output/error capture and fix the issue before finishing.
- Only claim dataset counts or coverage that you explicitly observed from parsing or checks; do not infer totals from partial extraction.
## Tips

- Use pubchempy or requests for PubChem API
- Recommended default imports: `from rdkit.Chem import AllChem, DataStructs`
- RDKit Morgan fingerprint: `AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=True)`
- Compute similarity with `DataStructs.TanimotoSimilarity(fp1, fp2)`.
- Tanimoto: |A∩B| / |A∪B|

- Parse and verify the PDF-derived molecule pool first, then normalize/deduplicate names and resolve each unique name to SMILES at most once.
- Compute fingerprints only after successful SMILES resolution; avoid interleaving network lookups with similarity ranking logic.
- Cache successful name→SMILES resolutions within the run, and do not repeatedly query PubChem inside ranking loops.
- For PubChem lookups, use retries with timeouts/backoff and distinguish transient network failures from true "not found" results; do not cache temporary failures as missing molecules.
- If online resolution is unreliable, try multiple resolution paths, such as PubChem name/synonym search and direct SMILES parsing when the input already looks like a SMILES string.
- Do **not** create manual or hand-written chemical-name → SMILES mappings or local caches; use permitted programmatic resolution only.
- Use external resources only to obtain structures/SMILES for the target and pool entries; keep a mapping back to the original pool text and emit those original names.
- Do not use PubChem or other external sources to expand the molecule pool; rank only within the names extracted from `molecule_pool_filepath`.
- Exclude the target molecule by resolved molecular identity, not just raw name equality; synonyms that resolve to the same canonical molecule should not appear as similarity 1.0 matches.
- Prefer a quick visible end-to-end smoke test after implementation so malformed code or RDKit argument errors are caught immediately.
