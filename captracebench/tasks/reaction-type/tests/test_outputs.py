#!/usr/bin/env python3
"""Pytest-based verifier: compares agent output against oracle output."""

class TestOutputs:
    """Verify agent output matches oracle output exactly."""

    @classmethod
    def setup_class(cls):
        import os
        oracle_path = os.path.join(os.path.dirname(__file__), "oracle_output.txt")
        with open(oracle_path) as f:
            cls.expected = f.read().strip()
        with open("/root/output.txt") as f:
            cls.actual = f.read().strip()

    def test_output_format(self):
        """Output must match expected format exactly."""
        assert self.actual == self.expected, (
            f"Output mismatch.\nExpected:\n{self.expected}\nGot:\n{self.actual}"
        )

    def test_all_lines_present(self):
        """All reaction results must be present."""
        for line in self.expected.split("\n"):
            if line.strip():
                assert line.strip() in self.actual, f"Missing line: {line}"
