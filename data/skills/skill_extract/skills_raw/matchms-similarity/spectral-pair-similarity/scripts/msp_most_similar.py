#!/usr/bin/env python3
"""Find the most similar pair of spectra in an MSP file using matchms CosineGreedy.

Usage:
  python msp_most_similar.py --input input.msp --output output.txt [--tolerance 0.1]

This script:
  1) Loads spectra from an MSP file.
  2) Computes pairwise CosineGreedy similarity for all unique pairs (i<j).
  3) Identifies the pair with the highest score.
  4) Writes two lines to the output file:
       Most similar pair: {name1} and {name2}
       Similarity: X.XXX

Notes:
- Name retrieval checks 'compound_name' first, then 'name', then falls back to 'Spectrum_{index}'.
- Score extraction is robust to matchms return type variations.

Dependencies:
- matchms (and its required dependencies)
"""

import argparse
import sys
from typing import Any, Tuple

try:
    import numpy as np
except Exception:  # numpy may not be strictly necessary, handle absent gracefully
    np = None  # type: ignore

from matchms.importing import load_from_msp
from matchms.similarity import CosineGreedy


def extract_score(result: Any) -> float:
    """Extract a numeric score from various possible return types of CosineGreedy.pair().

    Handles:
    - float-like values
    - tuples where the first element is the score
    - objects with a .score attribute
    - mappings with key 'score'
    - 0-D numpy arrays containing a tuple or numeric
    """
    # Handle numpy 0-D arrays if numpy is available and result is such an array
    if np is not None and isinstance(result, np.ndarray) and result.ndim == 0:
        result = result.item()

    # Object with 'score' attribute
    if hasattr(result, 'score'):
        try:
            return float(result.score)
        except Exception:
            pass

    # Mapping with 'score'
    if isinstance(result, dict) and 'score' in result:
        try:
            return float(result['score'])
        except Exception:
            pass

    # Tuple or indexable sequence: first element is score
    try:
        # Avoid treating strings as sequences here
        if not isinstance(result, (str, bytes)) and hasattr(result, '__getitem__'):
            first = result[0]
            return float(first)
    except Exception:
        pass

    # Fallback: cast directly to float
    return float(result)


def spectrum_label(spec: Any, index: int) -> str:
    """Retrieve a display label for a spectrum with fallbacks."""
    # matchms Spectrum has .get(key) for metadata
    try:
        name = spec.get('compound_name')
        if name:
            return str(name)
        name = spec.get('name')
        if name:
            return str(name)
    except Exception:
        pass
    # Final fallback
    return f"Spectrum_{index}"


def find_most_similar_pair(spectra: list, tolerance: float) -> Tuple[str, str, float]:
    """Return (name1, name2, best_score) for the most similar pair."""
    n = len(spectra)
    if n < 2:
        raise ValueError("Need at least 2 spectra to compute pairwise similarity.")

    cg = CosineGreedy(tolerance=tolerance)
    best_score = float('-inf')
    best_names = ("", "")

    for i in range(n):
        for j in range(i + 1, n):
            res = cg.pair(spectra[i], spectra[j])
            score = extract_score(res)
            if score > best_score:
                best_score = score
                ni = spectrum_label(spectra[i], i)
                nj = spectrum_label(spectra[j], j)
                best_names = (ni, nj)

    return best_names[0], best_names[1], best_score


def main() -> None:
    parser = argparse.ArgumentParser(description="Most similar spectral pair from MSP via matchms CosineGreedy")
    parser.add_argument("--input", required=True, help="Path to input MSP file")
    parser.add_argument("--output", required=True, help="Path to output text file")
    parser.add_argument("--tolerance", type=float, default=0.1, help="m/z tolerance for CosineGreedy (default: 0.1)")
    args = parser.parse_args()

    spectra = list(load_from_msp(args.input))
    if len(spectra) < 2:
        print("ERROR: MSP must contain at least 2 spectra.", file=sys.stderr)
        sys.exit(1)

    try:
        n1, n2, score = find_most_similar_pair(spectra, args.tolerance)
    except Exception as e:
        print(f"ERROR: Failed to compute similarity: {e}", file=sys.stderr)
        sys.exit(1)

    # Sanity checks
    try:
        if not isinstance(n1, str) or not n1:
            n1 = "Spectrum_A"
        if not isinstance(n2, str) or not n2:
            n2 = "Spectrum_B"
        if not (0.0 <= float(score) <= 1.0):
            # Some metrics may slightly exceed due to numerical issues; clamp for reporting
            score = max(0.0, min(1.0, float(score)))
    except Exception:
        pass

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(f"Most similar pair: {n1} and {n2}\n")
        f.write(f"Similarity: {score:.3f}\n")

    # Optional console message
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
