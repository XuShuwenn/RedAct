#!/usr/bin/env python3
import os
"""Verifier for isomer counting."""

import re

class TestOutputs:
    @classmethod
    def setup_class(cls):
        with open("/root/output.txt") as f:
            cls.actual = f.read().strip()
        oracle_path = os.path.join(os.path.dirname(__file__), "oracle_output.txt")
        with open(oracle_path) as f:
            cls.expected = f.read().strip()

    def test_output_format(self):
        """Output must match expected format."""
        assert self.actual == self.expected, (
            f"Output mismatch.\nExpected: {self.expected}\nGot: {self.actual}"
        )

    def test_isomer_count_positive(self):
        """Number of isomers must be non-negative."""
        m = re.search(r'Number of isomers: (\d+)', self.actual)
        assert m is not None, "Could not find isomer count"
        count = int(m.group(1))
        assert count >= 0, "Number of isomers must be non-negative"