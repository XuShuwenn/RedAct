#!/usr/bin/env python3
"""Chemical similarity utilities for PDF name lists.

Features:
- Extract molecule names from PDFs (handles multi-column lines and tables)
- Resolve names to SMILES via PubChem (throttling, retries, caching)
- Compute Morgan fingerprints (radius=2, include chirality)
- Rank candidates by Tanimoto similarity to a target

CLI example:
  python scripts/chem_similarity.py --target "Aspirin" --pdf molecules.pdf --topk 10

Programmatic usage:
  from scripts.chem_similarity import topk_from_pdf
  results = topk_from_pdf("Aspirin", "molecules.pdf", 10)

Note: Requires pdfplumber, pubchempy, and rdkit.
"""

from __future__ import annotations

import argparse
import re
import time
from functools import lru_cache
from typing import Iterable, List, Tuple

import pdfplumber
import pubchempy as pcp
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem

try:
    from rdkit.Chem import rdFingerprintGenerator as FG
    _HAS_FG = True
except Exception:
    _HAS_FG = False

# Throttle between PubChem requests to reduce rate limiting
_THROTTLE_SECONDS = 0.2
_last_call_time = 0.0


def _throttle():
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if elapsed < _THROTTLE_SECONDS:
        time.sleep(_THROTTLE_SECONDS - elapsed)
    _last_call_time = time.time()


def _normalize_candidate(text: str) -> str:
    """Normalize a candidate line/cell into a molecule name.

    - Trim whitespace
    - Remove leading enumerations like '12. ' or '7) '
    - Keep internal numbers (e.g., '2-hydroxybenzoic acid')
    """
    if text is None:
        return ""
    s = text.strip()
    if not s:
        return ""
    s = re.sub(r"^\s*\d+\s*[\.)]\s*", "", s)
    return s.strip()


def extract_names_from_pdf(pdf_path: str) -> List[str]:
    """Extract molecule names from a PDF robustly.

    Strategy:
    - For each page, extract tables (if any) and split cells by newlines, tabs, or ≥2 spaces
    - Also extract text lines and split lines on tabs or ≥2 spaces for multi-column layouts
    - Normalize and deduplicate (case-insensitive) while preserving original order
    """
    names: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Tables first
            try:
                tables = page.extract_tables() or []
            except Exception:
                tables = []
            for table in tables:
                for row in table:
                    for cell in row or []:
                        if not cell:
                            continue
                        for part in re.split(r"\n|\t| {2,}", str(cell)):
                            name = _normalize_candidate(part)
                            if name:
                                names.append(name)

            # Then line-based text
            text = page.extract_text() or ""
            for raw_line in text.splitlines():
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                # Split multi-column lines on tabs or 2+ spaces, else keep as one
                segments = re.split(r"\t| {2,}", raw_line)
                for seg in segments:
                    name = _normalize_candidate(seg)
                    if name:
                        names.append(name)

    # Deduplicate case-insensitively, preserve original order
    seen = set()
    unique: List[str] = []
    for n in names:
        key = n.lower()
        if key not in seen:
            seen.add(key)
            unique.append(n)
    return unique


@lru_cache(maxsize=4096)
def resolve_smiles(name: str, retries: int = 3, backoff: float = 0.5) -> str | None:
    """Resolve a chemical name to SMILES using PubChem.

    - Prefers isomeric SMILES; falls back to canonical if necessary
    - Throttles and retries with exponential backoff on errors
    - LRU-cached to reduce repeated lookups
    """
    delay = backoff
    last_exc: Exception | None = None
    for _ in range(retries):
        try:
            _throttle()
            compounds = pcp.get_compounds(name, "name")
            if compounds:
                c = compounds[0]
                smi = getattr(c, "isomeric_smiles", None) or getattr(c, "canonical_smiles", None) or getattr(c, "smiles", None)
                return smi
            return None
        except Exception as e:
            last_exc = e
            time.sleep(delay)
            delay *= 2
    return None


def _mol_from_smiles(smiles: str) -> Chem.Mol | None:
    if not smiles:
        return None
    try:
        return Chem.MolFromSmiles(smiles)
    except Exception:
        return None


def morgan_fingerprint(mol: Chem.Mol, radius: int = 2, include_chirality: bool = True, n_bits: int = 2048):
    """Compute a Morgan fingerprint bit vector.

    Prefers the rdFingerprintGenerator API if available; otherwise
    falls back to AllChem.GetMorganFingerprintAsBitVect.
    """
    if mol is None:
        return None
    try:
        if _HAS_FG:
            gen = FG.GetMorganGenerator(radius=radius, includeChirality=include_chirality, fpSize=n_bits)
            return gen.GetFingerprint(mol)
    except Exception:
        pass
    return AllChem.GetMorganFingerprintAsBitVect(mol, radius=radius, nBits=n_bits, useChirality=include_chirality)


def _sorted_by_similarity(results: Iterable[Tuple[str, float]]) -> List[Tuple[str, float]]:
    return sorted(((n, float(s)) for n, s in results), key=lambda x: (-x[1], x[0].lower()))


def topk_from_pdf(target_name: str, pdf_path: str, k: int, exclude_target_name: bool = False) -> List[Tuple[str, float]]:
    """Return top-k most similar molecules to a target from a PDF name list.

    - Name resolution via PubChem (no manual mappings)
    - Morgan fingerprints (radius=2, chirality), Tanimoto similarity
    - Sorted by similarity desc, then alphabetical for ties
    - Optionally exclude exact target name match
    """
    if k <= 0:
        return []

    target_smiles = resolve_smiles(target_name)
    if not target_smiles:
        raise ValueError(f"Could not resolve target molecule: {target_name}")
    target_mol = _mol_from_smiles(target_smiles)
    if target_mol is None:
        raise ValueError(f"Could not parse target SMILES: {target_name}")
    target_fp = morgan_fingerprint(target_mol, radius=2, include_chirality=True, n_bits=2048)

    names = extract_names_from_pdf(pdf_path)

    results: List[Tuple[str, float]] = []
    for name in names:
        if exclude_target_name and name.strip().lower() == target_name.strip().lower():
            continue
        smi = resolve_smiles(name)
        if not smi:
            continue
        mol = _mol_from_smiles(smi)
        if mol is None:
            continue
        fp = morgan_fingerprint(mol, radius=2, include_chirality=True, n_bits=2048)
        if fp is None:
            continue
        sim = DataStructs.TanimotoSimilarity(target_fp, fp)
        results.append((name, float(sim)))

    return _sorted_by_similarity(results)[:k]


def main():
    parser = argparse.ArgumentParser(description="Top-k chemical similarity from PDF name lists (Morgan/Tanimoto)")
    parser.add_argument("--target", required=True, help="Target molecule name")
    parser.add_argument("--pdf", required=True, help="Path to PDF containing molecule names")
    parser.add_argument("--topk", type=int, default=10, help="Number of top results to return")
    parser.add_argument("--exclude-target", action="store_true", help="Exclude exact target name from results")
    args = parser.parse_args()

    results = topk_from_pdf(args.target, args.pdf, args.topk, exclude_target_name=args.exclude_target)
    for i, (name, score) in enumerate(results, 1):
        print(f"{i}. {name}\t{score:.4f}")


if __name__ == "__main__":
    main()
