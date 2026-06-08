#!/usr/bin/env python3
"""Pytest-based verifier for matchms-similarity task."""

import re


class TestOutputs:
    @classmethod
    def setup_class(cls):
        with open("/root/output.txt") as f:
            cls.actual = f.read()

    def test_format(self):
        """Output must have required fields."""
        assert "Most similar pair:" in self.actual, "Missing 'Most similar pair' line"
        assert "Similarity:" in self.actual, "Missing 'Similarity' line"

    def test_pair_format(self):
        """Pair line must be in format: Most similar pair: X and Y."""
        pair_match = re.search(r'Most similar pair:\s*(.+)\s+and\s+(.+)', self.actual)
        assert pair_match, "Invalid pair format"

    def test_similarity_range(self):
        """Similarity must be between 0 and 1."""
        sim_match = re.search(r'Similarity:\s*([\d.]+)', self.actual)
        assert sim_match, "Could not find similarity value"
        sim = float(sim_match.group(1))
        assert 0 <= sim <= 1, f"Similarity {sim} out of range [0, 1]"

    def test_similarity_rounded(self):
        """Similarity must be rounded to 3 decimal places."""
        sim_match = re.search(r'Similarity:\s*([\d.]+)', self.actual)
        assert sim_match, "Could not find similarity value"
        sim_str = sim_match.group(1)
        # Check it has at most 3 decimal places
        if '.' in sim_str:
            decimals = len(sim_str.split('.')[1])
            assert decimals <= 3, f"Similarity has more than 3 decimal places: {sim_str}"
