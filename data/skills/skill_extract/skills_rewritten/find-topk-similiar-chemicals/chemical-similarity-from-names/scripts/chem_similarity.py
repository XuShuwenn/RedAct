#!/usr/bin/env python3
"""
Chemical similarity utilities for workflows that start from chemical names.

Features:
- Extract names from a PDF (pdfplumber preferred, PyPDF2 fallback)
- Resolve names to isomeric SMILES via external services (PubChem, cactus) with retries and pacing
- Compute Morgan fingerprints (radius=2, useChirality=True) using RDKit
- Compute Tanimoto similarity and return top-k names with deterministic tie-breaking

Note: Requires network access for name resolution and RDKit for chemistry operations.
"""
from __future__ import annotations

import os
import re
import json
import time
import math
from typing import List, Tuple, Optional, Dict

# Optional imports with graceful failure messages
try:
    import requests
except Exception as e:  # pragma: no cover
    requests = None

# RDKit imports
try:
    from rdkit import Chem, DataStructs
    from rdkit.Chem import rdMolDescriptors
except Exception as e:  # pragma: no cover
    Chem = None
    DataStructs = None
    rdMolDescriptors = None

# PDF extractors
_pdf_backends = []
try:
    import pdfplumber  # type: ignore
    _pdf_backends.append('pdfplumber')
except Exception:
    pass
try:
    from PyPDF2 import PdfReader  # type: ignore
    _pdf_backends.append('pypdf2')
except Exception:
    pass


# ------------------------- PDF Name Extraction ------------------------- #

def extract_names_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract candidate chemical names from a PDF file.
    Strategy:
      1) Try pdfplumber for robust text extraction.
      2) Fallback to PyPDF2.
      3) Split by lines, strip, filter empties, deduplicate preserving order.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text_lines: List[str] = []

    if 'pdfplumber' in _pdf_backends:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ''
                    text_lines.extend(t.splitlines())
        except Exception:
            # fall through to PyPDF2
            pass

    if not text_lines and 'pypdf2' in _pdf_backends:
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                t = page.extract_text() or ''
                text_lines.extend(t.splitlines())
        except Exception:
            pass

    if not text_lines:
        raise RuntimeError("Failed to extract text from PDF with available backends.")

    # Basic cleanup and deduplication
    seen: set = set()
    names: List[str] = []
    for raw in text_lines:
        name = raw.strip()
        if not name:
            continue
        # Skip trivial page markers
        if re.fullmatch(r"\d+|Page\s+\d+|\d+\s*/\s*\d+", name, flags=re.IGNORECASE):
            continue
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


# -------------------- External Name-to-SMILES Resolver -------------------- #

class NameResolver:
    """
    Resolve chemical names to isomeric SMILES with retries and optional on-disk cache.
    Resolution order:
      1) PubChem PUG REST (IsomericSMILES)
      2) NIH Cactus resolver (SMILES)
    """

    def __init__(self, cache_path: Optional[str] = None, sleep: float = 0.2, max_retries: int = 3):
        if requests is None:
            raise ImportError("The 'requests' package is required for name resolution.")
        self.cache_path = cache_path
        self.sleep = max(0.0, sleep)
        self.max_retries = max(1, max_retries)
        self.cache: Dict[str, Optional[str]] = {}
        if cache_path and os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as fh:
                    self.cache = json.load(fh)
            except Exception:
                self.cache = {}

    def _save_cache(self) -> None:
        if not self.cache_path:
            return
        try:
            tmp = self.cache_path + ".tmp"
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(self.cache, fh, ensure_ascii=False, indent=2)
            os.replace(tmp, self.cache_path)
        except Exception:
            pass

    def resolve(self, name: str) -> Optional[str]:
        key = name.strip()
        if not key:
            return None
        if key in self.cache:
            return self.cache[key]

        smiles = self._resolve_pubchem_isomeric_smiles(key)
        if smiles is None:
            smiles = self._resolve_cactus_smiles(key)

        self.cache[key] = smiles
        self._save_cache()
        # polite pacing between external calls
        time.sleep(self.sleep)
        return smiles

    def _resolve_pubchem_isomeric_smiles(self, name: str) -> Optional[str]:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{requests.utils.quote(name)}/property/IsomericSMILES/JSON"
        return self._http_get_smiles(url, json_path=["PropertyTable", "Properties", 0, "IsomericSMILES"])

    def _resolve_cactus_smiles(self, name: str) -> Optional[str]:
        url = f"https://cactus.nci.nih.gov/chemical/structure/{requests.utils.quote(name)}/smiles"
        return self._http_get_text(url)

    def _http_get_smiles(self, url: str, json_path: List[object]) -> Optional[str]:
        for attempt in range(1, self.max_retries + 1):
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    val = data
                    for key in json_path:
                        val = val[key]
                    smiles = str(val).strip()
                    return smiles or None
            except Exception:
                pass
            time.sleep(self._backoff(attempt))
        return None

    def _http_get_text(self, url: str) -> Optional[str]:
        for attempt in range(1, self.max_retries + 1):
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    txt = r.text.strip()
                    return txt or None
            except Exception:
                pass
            time.sleep(self._backoff(attempt))
        return None

    @staticmethod
    def _backoff(attempt: int) -> float:
        # Exponential backoff with jitter-friendly base
        return min(8.0, 0.5 * (2 ** (attempt - 1)))


# ----------------------- Fingerprints and Similarity ----------------------- #

def mol_from_smiles(smiles: str):
    if Chem is None:
        raise ImportError("RDKit is required for chemistry operations.")
    try:
        return Chem.MolFromSmiles(smiles)
    except Exception:
        return None


def morgan_fp(mol, radius: int = 2, n_bits: int = 2048, use_chirality: bool = True):
    if rdMolDescriptors is None:
        raise ImportError("RDKit is required for fingerprint generation.")
    try:
        return rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits, useChirality=use_chirality)
    except Exception:
        return None


def tanimoto(fp_a, fp_b) -> Optional[float]:
    if DataStructs is None:
        raise ImportError("RDKit DataStructs is required for similarity calculation.")
    if fp_a is None or fp_b is None:
        return None
    try:
        return float(DataStructs.TanimotoSimilarity(fp_a, fp_b))
    except Exception:
        return None


# ---------------------------- Top-k Similarity ---------------------------- #

def topk_similarity_from_pdf(target_name: str, pdf_path: str, k: int, cache_path: Optional[str] = None,
                             exclude_target: bool = False) -> List[str]:
    """
    End-to-end helper: extract names, resolve to SMILES, compute Morgan (radius=2, chirality) + Tanimoto
    vs. the target, and return top-k names sorted by (score desc, name asc).

    Parameters:
      - target_name: name of the target molecule
      - pdf_path: path to the PDF containing molecule names
      - k: number of top results to return
      - cache_path: optional JSON path for persisting name->SMILES cache
      - exclude_target: optionally drop entries whose resolved SMILES match the target's resolved SMILES
    """
    if k <= 0:
        return []

    # 1) Extract names
    names = extract_names_from_pdf(pdf_path)
    if not names:
        return []

    # 2) Resolve target
    resolver = NameResolver(cache_path=cache_path)
    target_smiles = resolver.resolve(target_name)
    if not target_smiles:
        return []

    target_mol = mol_from_smiles(target_smiles)
    if target_mol is None:
        return []

    target_fp = morgan_fp(target_mol, radius=2, n_bits=2048, use_chirality=True)
    if target_fp is None:
        return []

    # 3) Resolve and score candidates
    scored: List[Tuple[str, float]] = []
    # Pre-resolve target SMILES (for exclude_target option)
    target_smiles_norm = target_smiles

    for nm in names:
        # Resolve candidate
        smi = resolver.resolve(nm)
        if not smi:
            continue
        if exclude_target and smi == target_smiles_norm:
            continue
        mol = mol_from_smiles(smi)
        if mol is None:
            continue
        fp = morgan_fp(mol, radius=2, n_bits=2048, use_chirality=True)
        if fp is None:
            continue
        sim = tanimoto(target_fp, fp)
        if sim is None or math.isnan(sim):
            continue
        scored.append((nm, sim))

    if not scored:
        return []

    # 4) Sort by (-similarity, alphabetical by name case-insensitive)
    scored.sort(key=lambda x: (-x[1], x[0].lower(), x[0]))

    # 5) Return top-k names
    return [name for name, _ in scored[:k]]


if __name__ == "__main__":  # optional CLI
    import argparse
    parser = argparse.ArgumentParser(description="Top-k chemical similarity from PDF names.")
    parser.add_argument("target", help="Target molecule name")
    parser.add_argument("pdf", help="Path to PDF containing molecule names")
    parser.add_argument("k", type=int, help="Number of top results to return")
    parser.add_argument("--cache", help="Optional JSON cache file for name->SMILES", default=None)
    parser.add_argument("--exclude-target", action="store_true", help="Exclude entries identical to target")
    args = parser.parse_args()

    try:
        results = topk_similarity_from_pdf(args.target, args.pdf, args.k, cache_path=args.cache,
                                           exclude_target=args.exclude_target)
        for r in results:
            print(r)
    except Exception as exc:
        import sys
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
