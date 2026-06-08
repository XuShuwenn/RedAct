#!/usr/bin/env python3
import os
"""Verifier for molecular analysis."""

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
            f"Output mismatch.\nExpected:\n{self.expected}\nGot:\n{self.actual}"
        )

    def test_molecular_weight(self):
        """Molecular weight must be reasonable."""
        m = re.search(r'Molecular weight: ([\d.]+) g/mol', self.actual)
        assert m is not None, "Could not find molecular weight"
        mw = float(m.group(1))
        assert 50 < mw < 2000, f"Molecular weight seems unreasonable: {mw}"

    def test_functional_groups(self):
        """Functional groups must be listed."""
        m = re.search(r'Functional groups: (.+)', self.actual)
        assert m is not None, "Could not find functional groups"

    def test_hydrogen_count(self):
        """Hydrogen count must be positive."""
        m = re.search(r'Hydrogen count: (\d+)', self.actual)
        assert m is not None, "Could not find hydrogen count"
        count = int(m.group(1))
        assert count > 0, "Hydrogen count must be positive"