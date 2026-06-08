#!/usr/bin/env python3
"""Pytest-based verifier: compares agent output against oracle output."""

import re


class TestOutputs:
    """Verify agent output matches oracle output exactly."""

    @classmethod
    def setup_class(cls):
        import os
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

    def test_total_variants(self):
        m = re.search(r"Total variants: (\d+)", self.actual)
        assert m is not None and int(m.group(1)) == 8, "Should have 8 total variants"

    def test_passed_variants(self):
        m = re.search(r"Passed variants: (\d+)", self.actual)
        assert m is not None and int(m.group(1)) == 5, "Should have 5 passed variants"

    def test_failed_variants(self):
        m = re.search(r"Failed variants: (\d+)", self.actual)
        assert m is not None and int(m.group(1)) == 3, "Should have 3 failed variants"
