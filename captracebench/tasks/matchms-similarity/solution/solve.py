#!/usr/bin/env python3
"""Solve matchms-similarity task: find most similar spectral pair."""

from matchms.importing import load_from_msp
from matchms.similarity import CosineGreedy
import numpy as np


def extract_score(pair_result):
    """Extract float score from pair() result, handling various types."""
    # If it's a numpy array
    if isinstance(pair_result, np.ndarray):
        if pair_result.ndim == 0:
            # 0-dimensional array: use .item() to extract
            item = pair_result.item()
            if isinstance(item, tuple):
                return float(item[0])
            return float(item)
        else:
            return float(pair_result[0])
    # If it's a tuple or list
    if isinstance(pair_result, (tuple, list)):
        return float(pair_result[0])
    # Otherwise assume it's already a scalar
    return float(pair_result)


def main():
    # Load all spectra from MSP file
    spectra = list(load_from_msp("/root/input.msp"))

    if len(spectra) < 2:
        result = "Most similar pair: N/A\nSimilarity: 0.000\n"
    else:
        # Compute pairwise similarities
        cosine_greedy = CosineGreedy(tolerance=0.1)

        best_score = -1.0
        best_pair = (None, None)

        for i in range(len(spectra)):
            for j in range(i + 1, len(spectra)):
                pair_result = cosine_greedy.pair(spectra[i], spectra[j])
                score = extract_score(pair_result)

                if score > best_score:
                    best_score = score
                    name_i = spectra[i].get("compound_name", spectra[i].get("name", f"Spectrum_{i}"))
                    name_j = spectra[j].get("compound_name", spectra[j].get("name", f"Spectrum_{j}"))
                    best_pair = (name_i, name_j)

        result = f"Most similar pair: {best_pair[0]} and {best_pair[1]}\n"
        result += f"Similarity: {best_score:.3f}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

    print(result)


if __name__ == "__main__":
    main()
