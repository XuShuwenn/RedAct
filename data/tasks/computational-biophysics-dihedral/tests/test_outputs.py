#!/usr/bin/env python3
import os
"""Pytest-based verifier."""

import re

class TestOutputs:
    @classmethod
    def setup_class(cls):
        oracle_path = os.path.join(os.path.dirname(__file__), "oracle_output.txt")
        with open(oracle_path) as f:
            cls.expected = f.read()
        with open("/root/output.txt") as f:
            cls.actual = f.read()

    def test_output_matches(self):
        assert self.actual.strip() == self.expected.strip(), (
            f"Output mismatch.\nExpected:\n{self.expected}\nGot:\n{self.actual}"
        )

    def test_has_angle(self):
        assert "Dihedral angle:" in self.actual

    def test_angle_range(self):
        m = re.search(r"Dihedral angle: ([-+0-9.]+) degrees", self.actual)
        assert m is not None, "Could not find dihedral angle"
        angle = float(m.group(1))
        assert -180 <= angle <= 180, f"Angle out of range: {angle}"
