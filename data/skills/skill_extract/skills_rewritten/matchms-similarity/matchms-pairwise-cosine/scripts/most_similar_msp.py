#!/usr/bin/env python3
"""Find the most similar pair of spectra in an MSP file using matchms CosineGreedy.

Usage:
  python scripts/most_similar_msp.py --input INPUT.msp [--output OUTPUT.txt]

This script:
  - Loads spectra from an MSP file.
  - Computes pairwise CosineGreedy similarity for all unique pairs.
  - Extracts the numeric score robustly from different possible return types.
  - Prints the most similar pair and similarity to stdout.
  - Optionally writes the result to an output file in a fixed 2-line format.

Output format (when --output is provided):
Most similar pair: {name1} and {name2}
Similarity: X.XXX
"""

import argparse
import math
from typing import Any, Optional

try:
    from matchms.importing import load_from_msp
    from matchms.similarity import CosineGreedy
except Exception as e:  # pragma: no cover - import-time diagnostics
    raise SystemExit(f"ERROR: Required package 'matchms' not available or failed to import: {e}")


def get_spectrum_name(s, idx: int) -> str:
    """Return a human-readable spectrum name with fallbacks.

    Tries common metadata keys. Falls back to an index-based label if missing.
    """
    meta = getattr(s, "metadata", {}) or {}
    for key in ("name", "compound_name", "title", "spectrum_id", "id"):
        val = meta.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return f"Spectrum_{idx+1}"


def extract_numeric_score(result: Any) -> Optional[float]:
    """Extract a numeric similarity score from various return types.

    Handles:
    - float/int
    - objects with .score or .value
    - (score, ...) tuples/lists
    - dict-like with 'score' key
    - objects convertible to float

    Returns None if a numeric score cannot be extracted.
    """
    # Direct numeric
    if isinstance(result, (int, float)):
        score = float(result)
        return score if math.isfinite(score) else None

    # Attribute-based
    for attr in ("score", "value", "similarity", "cosine"):
        if hasattr(result, attr):
            try:
                score = float(getattr(result, attr))
                return score if math.isfinite(score) else None
            except Exception:
                pass

    # Tuple/list
    if isinstance(result, (tuple, list)) and result:
        # Prefer first numeric-like element
        for elem in result:
            try:
                score = float(elem)
                if math.isfinite(score):
                    return score
            except Exception:
                continue

    # Dict-like
    if isinstance(result, dict):
        for key in ("score", "value", "similarity", "cosine"):
            if key in result:
                try:
                    score = float(result[key])
                    return score if math.isfinite(score) else None
                except Exception:
                    pass

    # Last resort: try to cast
    try:
        score = float(result)
        return score if math.isfinite(score) else None
    except Exception:
        return None


def find_most_similar_pair(spectra):
    """Return (name1, name2, best_score) for the most similar pair.

    Iterates unique pairs and computes CosineGreedy similarity.
    """
    n = len(spectra)
    if n < 2:
        raise ValueError("Need at least 2 spectra to compute pairwise similarity.")

    names = [get_spectrum_name(s, i) for i, s in enumerate(spectra)]
    measure = CosineGreedy()

    best_score = None
    best_i = None
    best_j = None

    for i in range(n):
        si = spectra[i]
        for j in range(i + 1, n):
            sj = spectra[j]
            try:
                res = measure.pair(si, sj)
            except Exception:
                # Skip pairs that fail due to missing data or incompatible spectra
                continue
            score = extract_numeric_score(res)
            if score is None or not (score == score):  # NaN check
                continue
            if best_score is None or score > best_score:
                best_score = score
                best_i = i
                best_j = j

    if best_score is None or best_i is None or best_j is None:
        raise RuntimeError("No valid similarity scores could be computed.")

    return names[best_i], names[best_j], float(best_score)


def main():
    parser = argparse.ArgumentParser(description="Find most similar spectrum pair (CosineGreedy)")
    parser.add_argument("--input", required=True, help="Path to input MSP file")
    parser.add_argument("--output", help="Path to write 2-line result (optional)")
    args = parser.parse_args()

    spectra = list(load_from_msp(args.input))
    name1, name2, score = find_most_similar_pair(spectra)

    line1 = f"Most similar pair: {name1} and {name2}"
    line2 = f"Similarity: {format(score, '.3f')}"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(line1 + "\n")
            f.write(line2 + "\n")
    else:
        print(line1)
        print(line2)


if __name__ == "__main__":
    main()
