#!/usr/bin/env python3
import os
"""Pytest-based verifier: compares agent output against oracle output."""

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

    def test_all_lines_present(self):
        for line in self.expected.split("\n"):
            key = line.split(":")[0] if ":" in line else line
            assert key in self.actual, f"Missing line: {key}"

    def test_sigma_x(self):
        m = re.search(r'Sigma X: ([-+0-9.]+)', self.actual)
        assert m is not None, "Could not find Sigma X"
        val = float(m.group(1))
        assert -1 <= val <= 1, f"Sigma X out of range: {val}"

    def test_sigma_z(self):
        m = re.search(r'Sigma Z: ([-+0-9.]+)', self.actual)
        assert m is not None, "Could not find Sigma Z"
        val = float(m.group(1))
        assert -1 <= val <= 1, f"Sigma Z out of range: {val}"
