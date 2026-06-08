#!/usr/bin/env python3
import os
"""Pytest-based verifier."""

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

    def test_has_match(self):
        assert "Match:" in self.actual
