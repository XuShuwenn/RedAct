---
name: find-topk-similiar-chemicals
description: "Find top-k similar chemicals using Morgan fingerprints and Tanimoto similarity, with PubChem/RDKit for molecular representations."
---

# Chemical Similarity Search

## When to Use

- Find similar chemicals in a molecule pool
- Convert chemical names to molecular SMILES
- Compute molecular fingerprints and similarity

- Follow this skill only after satisfying any task-specific tool-call, action-format, file-location, or completion-message contract; those procedural requirements override the skill workflow when present.

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

- Keep `molecule_pool_filepath` as a runtime argument throughout implementation, debugging, smoke tests, and any `__main__` example; do not hardcode alternate defaults such as `/root/...` or silently swap in another PDF path.
- If the task provides an absolute path, pass that exact path unchanged and use the same file for inspection, extraction, validation, and the final function call.
- When testing or debugging, log the exact runtime path being opened; do not switch between relative and absolute paths, directories, or alternate copies of the dataset unless you explicitly prove they are the same file.
- If a result contains molecule names absent from the parsed pool from that exact file, stop and debug a path or extraction mismatch before accepting the run.

- Treat the PDF contents as the authoritative candidate set; returned molecule names must come only from molecules actually parsed from this pool, not from PubChem synonyms, preferred labels, or external molecules.
- Inspect all pages of the PDF before coding extraction logic; molecule names/structures may be distributed across the full document.
- If PDF extraction looks truncated or malformed (for example abrupt cutoff, partial tokens, missing pages, wrapped names split incorrectly, headers/footers mixed into names, or suspiciously short output), re-extract/inspect before computing similarities.

- Inspect the PDF structure first and choose the simplest extraction method that matches what is actually present (for example, a plain text list of names versus drawn structures/tables).
- Inspect representative extracted text from every page before finalizing parser logic; molecule names may span page boundaries, wrap across lines, or be mixed with headers/footers.
- Treat malformed tail entries or clipped tokens (for example `Dicl`, `Diclo`, `Ph`, or abruptly cut last records) as extraction failure signals, not acceptable noise.
- Before using the pool for similarity ranking, confirm the last parsed entries are complete enough to be plausible molecule names; if not, switch extraction method or repair parsing first.
- Do not silently keep suspicious partial names in the candidate pool; either recover the full entry from the PDF or exclude it with explicit handling.


## Output

- Sorted list of top-k similar chemicals
- Format: [(molecule_name, similarity_score), ...]

- Preserve this output contract unless the task explicitly requires a different format.
- Do not switch to returning only names, only scores, dicts, or other structures based on assumption; if a task is ambiguous, keep `[(molecule_name, similarity_score), ...]`.


- Only return names exactly as they appear in the extracted molecule pool.

- Before trusting results, compare returned names against the parsed pool names from the same run; unseen names indicate a bug, not a successful synonym match.

- Do not introduce alternate names, PubChem synonyms, or canonicalized labels as output names.
- Tie-breaking requirement is literal: if similarity scores are equal, sort by the molecule name in normal alphabetical order as written.
- Do NOT switch to case-insensitive ordering, locale-aware ordering, or any other modified interpretation unless the task explicitly asks for it.
- Example: use `key=lambda x: (-x[1], x[0])`, not `key=lambda x: (-x[1], x[0].lower())`.


## Validation Checklist

- During the final test, print or otherwise confirm the exact `molecule_pool_filepath` being opened at runtime and inspect the parsed candidate names from that same run.
- If runtime observations disagree with earlier inspection or the output contains names absent from that parsed pool, treat that as a path/dataset mismatch or parsing bug and re-validate from scratch.
- Inspect representative extracted text from every page and ensure parser logic handles wrapped names, headers/footers, page boundaries, and multi-word names generically rather than with one-off molecule-specific fixes.
- If extracted text looks cut off, suspiciously short, or malformed, re-extract/re-inspect before changing ranking logic.
- Explicitly compare the set of returned names against the parsed PDF candidate-name set; if any returned name is outside that set, fail validation immediately.
- Do not use ad hoc or external molecule lists to judge correctness; all correctness checks must derive from the exact parsed `molecule_pool_filepath` contents.
- Add a synonym self-match check to validation: if the target is Aspirin and the output contains `Acetylsalicylic acid` at similarity 1.0 (or any equivalent same-molecule result), treat that as a bug and fix exclusion logic before finishing.
- In the final verification, explicitly confirm that exclusion was based on resolved molecular identity, not only raw name comparison.
- If end-to-end testing fails to resolve the target molecule, prioritize target-resolution or network diagnosis before investigating ranking or tie-breaking.
- Base diagnosis on the observed traceback or returned error, not on unrelated hypotheses.
- After creating or editing the solution file, inspect the saved implementation directly; after any broad replace or multi-step edit, recheck the affected function boundaries and exact required signature.
- After every substantive edit, rerun a fresh syntax/import check and then a new end-to-end call on the final saved artifact; if you modify code after a passing run, treat earlier results as stale.
- Treat warnings-only logs, hanging runs, repeated HTTP/network failures with no stable final list, partial/truncated output, empty results (`[]`) when resolvable candidates should exist, exceptions, or ambiguous output as blockers; rerun with explicit output/error capture until the completed returned tuple list is visible.
- Only report counts, page coverage, or pool contents that you directly verified during this run.


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
- Normalize lookup inputs before external search (trim whitespace and collapse obvious extraction artifacts) while preserving the original pool name separately for output.
- If a lookup that should be common fails, retry and cross-check with an alternate permitted resolution path before treating it as unresolved.
- Cache successful SMILES resolutions and confirmed clean "not found" results separately from transient lookup failures.

- If online resolution is unreliable, try multiple resolution paths, such as PubChem name/synonym search and direct SMILES parsing when the input already looks like a SMILES string.
- Do **not** create manual or hand-written chemical-name → SMILES mappings or local caches; use permitted programmatic resolution only.
- Use external resources only to obtain structures/SMILES for the target and pool entries; keep a mapping back to the original pool text and emit those original names.
- Do not use PubChem or other external sources to expand the molecule pool; rank only within the names extracted from `molecule_pool_filepath`.
- Exclude the target molecule by resolved molecular identity, not just raw name equality; synonyms that resolve to the same canonical molecule should not appear as similarity 1.0 matches.

- Implement self-match exclusion after structure resolution: compare canonical identity (for example canonical SMILES/InChIKey if available, or exact structure equivalence) rather than `molecule_name == target_molecule_name`.
- If a synonym of the target appears in the pool, exclude it from ranking exactly like the original target entry.

- Prefer a quick visible end-to-end smoke test after implementation so malformed code or RDKit argument errors are caught immediately.

- Prefer a two-phase pipeline: (1) parse and validate the full PDF candidate pool, deduplicate pool names, and resolve structures once per unique entry; (2) compute fingerprints and rank similarities from those resolved entries.
- Structure the pipeline as: extract pool -> deduplicate candidate names -> resolve each unique name once with caching/retries -> compute fingerprints -> rank similarities.
- Separate extraction validation from ranking: first inspect parsed names for completeness/truncation, then resolve structures, then compute similarity.
- Separate concerns cleanly: network/name resolution should be a precomputation stage, not something repeated inside ranking/comparison loops.
- Keep candidate records as `(original_pool_name, resolved_mol)` or equivalent; use resolved structures for similarity/exclusion, but always emit the original pool name as output.
- Keep external structure resolution and pool provenance separate: PubChem/RDKit may resolve structures, but they do not authorize adding names that were not parsed from the PDF.
- Minimize live external lookups: deduplicate the full pool first, resolve each unique name once, reuse those results for ranking, and avoid per-comparison network calls.
- Keep any cache strictly to within-run programmatic resolution results; never seed it with manual chemical mappings, fixtures, or hand-written name→SMILES files.
- Use the RDKit call exactly as `AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=True)`; do not substitute unsupported keyword names such as `includeChirality`.
- Prefer the stable fingerprint call unless you have a verified reason to change it; if you switch to an RDKit fingerprint-generator API, verify the exact call signature against the installed RDKit version with a small smoke test before using it in the ranking pipeline.
- Prefer keeping a known-good PubChem lookup path unless a replacement is verified against an observed response sample for the same API endpoint.
- On timeout, rate limit, server busy, connection reset, or similar temporary PubChem errors, retry with backoff and leave the entry retriable; do not store `None` as a permanent miss for those exception paths.
- Treat a name as a permanent miss only after a clean lookup path completes without transient errors and returns no structure.
- A good final check is: parse pool names -> resolve structures -> score only those entries -> sort with `key=lambda x: (-x[1], x[0])` -> verify all output names are in the pool.
- Prefer a minimal smoke test that prints an unambiguous result, for example `result = topk_tanimoto_similarity_molecules(...); print(repr(result))`.
- If the smoke test is ambiguous, instrument the pipeline in order: PDF extraction count/sample names -> name/SMILES resolution counts -> fingerprint generation counts -> final ranked list.



# Chemical Similarity Search

## Execution and Finalization Protocol

- Follow any task-, harness-, or environment-specific tool-call schema, file-location requirement, action format, or exact completion/output token literally; this skill does not override those constraints.
- If the task requires producing a script/file, write it explicitly to the required location, then read back the saved file from disk before declaring completion.
- If the readback is truncated, malformed, or differs from the intended code, fix it and re-read until the observed contents match.
- After the final write, run a lightweight syntax/import check or executable smoke test on the saved artifact, not just on intended code in memory.
- If you edit the code after a successful test, re-run the final saved version before declaring success; earlier validation no longer counts.
- Before finishing, verify whether the task requires an exact completion string or termination format and emit it verbatim as the last message when required.
