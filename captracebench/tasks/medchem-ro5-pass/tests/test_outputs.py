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

    def test_pass_count(self):
        m = re.search(r"Total: (\d+) pass", self.actual)
        assert m is not None and int(m.group(1)) == 3, "Should have 3 passing molecules"

    def test_fail_count(self):
        m = re.search(r"(\d+) fail", self.actual)
        assert m is not None and int(m.group(1)) == 2, "Should have 2 failing molecules"

    def test_mol004_fail(self):
        assert "mol004: FAIL" in self.actual and "LogP" in self.actual, "mol004 should fail LogP"

    def test_mol005_fail(self):
        assert "mol005: FAIL" in self.actual and "LogP" in self.actual, "mol005 should fail LogP"
