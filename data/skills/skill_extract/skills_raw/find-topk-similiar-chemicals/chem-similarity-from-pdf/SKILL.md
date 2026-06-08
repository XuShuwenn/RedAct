---
name: chem-similarity-from-pdf
description: "Find top-k similar molecules to a target by parsing names from documents, resolving names via PubChem, and comparing Morgan fingerprints (radius=2, chirality) using Tanimoto similarity."
---

# Chemical Similarity from PDF Name Lists

A reusable workflow to extract molecule names from PDFs or text, resolve names to structures using PubChem, compute Morgan fingerprints (radius=2, include chirality), and rank candidates by Tanimoto similarity to a target molecule.

## When to Use

Activate this skill when you need to:
- Find the most similar chemicals to a target given a list of chemical names in a PDF or text document
- Convert names to structures without manual name→SMILES mappings
- Compute similarity using Morgan fingerprints with Tanimoto similarity

## Core Workflow

1. Inspect and Extract Molecule Names
   - Use a robust PDF parser (e.g., pdfplumber or pypdf) to extract text from each page.
   - Treat each line as a potential molecule name. Handle multi-column or concatenated entries by additionally splitting on tabs and sequences of ≥2 spaces.
   - If tables exist, extract cell contents and split cells on newlines, tabs, and ≥2 spaces.
   - Normalize entries:
     - Trim whitespace
     - Remove leading enumerations like "12. " or "7) " while preserving chemical numerals inside names
     - Deduplicate names while preserving original order (case-insensitive key, original casing retained)

2. Resolve Names to Structures (no manual mappings)
   - Use PubChem via PubChemPy to resolve names:
     - pcp.get_compounds(name, 'name')
     - Prefer isomeric SMILES; fall back to canonical SMILES if needed
   - Implement resiliency:
     - Add lightweight throttling (e.g., ≥0.2 s between requests) to avoid rate limits
     - Add retry with exponential backoff for transient errors (e.g., HTTP 503)
     - Cache name→SMILES results in-memory (and optionally on-disk) to minimize repeated calls
   - Validate by constructing an RDKit Mol from the SMILES; skip entries that fail to parse

3. Compute Target and Candidate Fingerprints
   - Use RDKit Morgan fingerprints:
     - Radius = 2
     - Include chirality = True
     - Bit vector size recommended = 2048
   - Accept both APIs:
     - rdFingerprintGenerator.GetMorganGenerator(radius=2, includeChirality=True, fpSize=2048)
     - AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=True)

4. Score and Rank
   - Compute Tanimoto similarity DataStructs.TanimotoSimilarity(target_fp, candidate_fp)
   - Sort results by:
     - Primary: similarity descending
     - Secondary: case-insensitive alphabetical order of candidate names (for ties)
   - Optionally exclude the exact target name if it appears in the pool under the same spelling (configurable)

5. Return Results
   - Return the top-k results in the format required by the task (e.g., list of tuples [(name, score), ...] sorted as specified)

## Verification

- Name Extraction
  - Confirm the extracted list contains expected multi-word names intact (no splitting of hyphenated or multi-token chemical names)
  - Check that multi-column lines and table cells are properly split by tabs or ≥2 spaces
- Structure Resolution
  - Verify SMILES resolution for a small sample of names and that RDKit can parse them (Mol is not None)
  - Ensure caching reduces repeated network calls for the same names
- Fingerprints & Similarity
  - Confirm fingerprint parameters: radius=2, include chirality=True, consistent bit size
  - Verify Tanimoto similarity is used (not Dice or cosine)
- Sorting & Ties
  - Confirm descending similarity order and deterministic alphabetical tie-breaking using a case-insensitive key
- Determinism
  - Run the process twice with caching enabled and verify identical outputs when network responses are stable

## Common Pitfalls and How to Avoid Them

- Splitting on generic whitespace: This breaks multi-word names. Split by lines first, then further split on tabs or ≥2 spaces for multi-column lines.
- Hardcoding line-specific fixes: Do not write one-off string matches for specific documents. Use general tokenization rules and deduplication.
- Ignoring PubChem rate limits: Add throttling, retries with backoff, and caching. Avoid burst queries.
- Missing chirality or wrong radius: Ensure useChirality=True (or includeChirality=True) and radius=2 explicitly.
- Wrong similarity or fingerprint: Use Morgan fingerprints and Tanimoto similarity, not other fingerprints or metrics.
- Unstable tie-breaking: Always add a secondary alphabetical key (case-insensitive) after similarity.
- Failing to validate structures: Always check RDKit Mol objects and skip invalid ones.
- Returning the wrong format: Match the calling task’s expected return type and structure exactly.

## Optional Script Usage

The provided helper script implements this workflow in a reusable way:
- Parse PDFs and extract molecule names robustly
- Resolve names to SMILES with throttling, retries, and caching
- Compute Morgan fingerprints (radius=2, chirality)
- Rank by Tanimoto and return top-k

Example (CLI):
- python scripts/chem_similarity.py --target "Aspirin" --pdf /path/to/molecules.pdf --topk 10

Example (import in Python):
- from scripts.chem_similarity import topk_from_pdf
- results = topk_from_pdf("TargetName", "/path/to/list.pdf", 10)

Success Criteria
- Uses PubChem (no manual name→SMILES mapping)
- Morgan fingerprints (radius=2, chirality) and Tanimoto similarity
- Robust PDF parsing with multi-column handling
- Sorted by similarity desc, alphabetical on ties
- Handles rate-limits and retries; caches lookups
