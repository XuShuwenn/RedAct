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
- Before any tool use or code execution, extract the active environment contract from the task/system instructions: allowed tools, required action schema, observation/wait rules, required file paths, allowed dependency/network constraints, and any exact completion token.
- Follow that contract literally for the entire run. Do **not** substitute alternate tool syntaxes, wrappers, free-form narration, or near-miss completion phrases.
- Treat protocol compliance as blocking: a correct chemistry solution still fails if the required action format, file location, dependency constraints, or termination string is wrong.
- If the task requires a self-contained or local-only solution, do not introduce PubChem, pubchempy, web requests, or any other external chemistry service unless the task explicitly permits it.

## Key Components

### Morgan Fingerprints
- Radius = 2
- Include chirality
- Tanimoto similarity for comparison

### External Resources
- PubChem: chemical name → SMILES conversion
- RDKit: fingerprint computation
- Prefer local/self-contained extraction when the PDF already provides molecular structures, embedded chemical text, SMILES, or other machine-readable identifiers; use external lookup services as a fallback, not the default pipeline.
- Do not make network availability the core dependency when the task can be completed from the provided file plus local libraries.

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
- Do not stop at page-count metadata or first-page sampling: extract and review representative content from every page before trusting the candidate pool.
- If extraction output stops mid-token or mid-page, or early pages already show clipped tail entries or partial names, treat the pool as unvalidated and fix extraction before building or testing the ranking pipeline.
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
- External resources may help resolve structures for parsed pool entries, but they must never supply candidate names or become the reference set for correctness.
- If a test result includes a molecule name not present in the parsed PDF pool from that same run, stop: the implementation or validation has drifted away from the task input.

- Do not introduce alternate names, PubChem synonyms, or canonicalized labels as output names.
- Tie-breaking requirement is literal: if similarity scores are equal, sort by the molecule name in normal alphabetical order as written.
- Do NOT switch to case-insensitive ordering, locale-aware ordering, or any other modified interpretation unless the task explicitly asks for it.
- Example: use `key=lambda x: (-x[1], x[0])`, not `key=lambda x: (-x[1], x[0].lower())`.

- Return each pool molecule at most once in the final ranked list. If the PDF extraction contains duplicate names, deduplicate candidates before scoring/ranking so duplicate names do not occupy multiple result slots.
- Do not deduplicate only during caching and then rebuild results from the original repeated pool list; rank the deduplicated candidate set you actually intend to allow in output.


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

- Before implementing ranking, explicitly inspect parsed candidate names for separation errors such as merged molecule names, clipped entries, or malformed tails; one bad candidate is enough to invalidate downstream similarity results.
- When using PubChem or any external resolver, validate the intermediate resolution stage explicitly: inspect or report how many unique pool entries resolved, which representative/common names failed, and whether unresolved entries materially affect top-k computation.
- Do not assume retries/backoff made external lookup reliable; transient failures such as timeout, rate limit, server busy, or repeated common-name failures remain blockers until a fresh saved-artifact run succeeds.
- If repeated PubChem/network failures appear during development, treat that as an architecture risk: do not declare success while the final function still depends on live resolution working reliably at runtime.
- After any broad edit, search/replace, or multi-step patch, read back the saved solution file itself and inspect the affected region; do not trust intended edits without file verification.
- Run a fresh syntax/import check on the final saved artifact after the last edit, then run the main entry point again on that saved artifact with the exact input file and confirm a visible, non-ambiguous `[(molecule_name, similarity_score), ...]` result before finishing.
- Do not declare success from warnings-only logs, truncated inspection output, ambiguous/partial output, empty list `[]` when results should exist, exceptions, unresolved lookup failures, or protocol violations; fix the issue and rerun.
- If top results look chemically surprising or implausible for the target, do not accept the run at face value; inspect extraction quality, name resolution, self-match exclusion, duplicate handling, and whether unresolved entries distorted the candidate set.
- If you discover duplicate names in the parsed pool, explicitly check that the final returned names are unique unless the task explicitly requires preserving duplicates.
- If the task requires an exact completion signal, emit that exact string verbatim as the last message only after the final verification run passes.


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

- Prefer a parsing strategy driven by observed PDF structure rather than molecule-specific cleanup rules; if merged names, split tokens, or truncated tails appear, change the extraction method instead of hard-coding fixes for individual chemicals.
- First decide whether external resolution is actually allowed and necessary. If the PDF/task already provides usable structures or explicitly requires a self-contained solution, resolve molecules locally from the provided data and RDKit instead of calling PubChem.
- Do **not** assume PubChem is always appropriate just because this skill mentions it; external lookup is optional fallback guidance, not a requirement, and task constraints override it.
- Parse and deduplicate the full pool first, then resolve each unique candidate and the target once via a shared within-run cache; do not keep PubChem calls inside repeated ranking or debugging loops.
- Do not postpone remote-lookup reliability checks until the final end-to-end test; verify early that the chosen resolver works in the current environment for common names and that retry/backoff behavior is actually effective.
- If the primary PubChem path is unstable, verify a secondary permitted programmatic path on the same molecule before proceeding, but never invent manual name→SMILES mappings.



# Chemical Similarity Search

## Execution and Finalization Protocol

- Follow any task-, harness-, or environment-specific tool-call schema, file-location requirement, action format, or exact completion/output token literally; this skill does not override those constraints.
- If the environment requires waiting for a tool observation before the next step, do so; do not batch unsupported tool calls or continue outside the required protocol.
- If the environment mandates a specific action wrapper or message schema, use that exact format for every step.
- Do not substitute near-miss completion phrases, summaries, or explanations for an exact required completion token.
- When asked to create, edit, inspect, or run files, use real executable commands or tool invocations with concrete paths, filenames, and arguments; do not issue placeholder actions such as "write the solution file" as if they were commands.
- If the task requires producing a script/file, write it explicitly to the required location, then read back the saved file from disk before declaring completion.
- Before writing, verify the target path or parent directory exists and is writable, or create it if the task allows; do not assume a guessed workspace path.
- Write actual executable source code to the required file path; do not write prose placeholders, summaries of intended behavior, TODO text, or natural-language descriptions in place of implementation.
- Treat readback as mandatory verification of the actual on-disk artifact: the file must contain literal executable code, not placeholders, summaries, or narrative descriptions.
- If any write, directory-creation, or setup step initially fails, treat validation as reset: confirm the corrected path exists, re-read the full saved artifact from disk, and run a fresh end-to-end check on that saved file before declaring success.
- If the readback is truncated, malformed, or differs from the intended code, fix it and re-read until the observed contents match.
- After the final write, run a lightweight syntax/import check or executable smoke test on the saved artifact, not just on intended code in memory.
- Treat a test as passing only if it clearly finishes and shows the observable expected result, such as a visible printed `repr(result)` or equivalent completed return output.
- Do not finish on warnings-only logs, partial output, file inspection alone, or inferred behavior.
- If output is truncated, buffered, ambiguous, hangs, or is missing the final tuple list, fetch the remaining output or rerun a narrower foreground test until the concrete result is visible.
- If you edit the code after a successful test, re-run the final saved version before declaring success; earlier validation no longer counts.
- Base completion claims on the latest observed run of the final saved file only.
- When the same anomalous runtime symptom appears more than once, stop making speculative code changes and localize the failure stage first (PDF extraction, name resolution/network, fingerprinting, ranking, or final print/output).
- Prefer concrete, anchored edits over vague placeholder replacements: first read the exact existing code, then patch that verified text, and re-open the affected region after editing to confirm function boundaries and call sites are intact.
- Prefer validation steps that use broadly available tools or Python itself; do not depend on utilities like `ps`, `rg`, or similar commands unless you have already confirmed they exist in the current environment.
- If shell tooling is limited, use Python for file existence checks, directory listing, content inspection, and smoke tests.
- Final reports must be strictly observation-backed: mention only file contents, test outcomes, rankings, or returned molecules that were directly seen in tool output from this run.
- If a run did not visibly print the result list, say verification is incomplete and run another explicit check instead of asserting success.
- Do **not** state concrete examples such as specific top matches unless those exact names and scores appeared in the captured output.
- Before finishing, verify whether the task requires an exact completion string or termination format and emit it verbatim as the last message when required.
