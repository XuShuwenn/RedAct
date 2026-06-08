#!/usr/bin/env python3
"""Pytest-based verifier: compares agent output against oracle output."""

import re


class TestOutputs:
    """Verify agent output matches oracle output exactly."""

    @classmethod
    def setup_class(cls):
        # Read oracle reference from tests directory (pre-generated, not from solution/)
        import os
        oracle_path = os.path.join(os.path.dirname(__file__), "oracle_output.txt")
        with open(oracle_path) as f:
            cls.expected = f.read()

        # Read agent output
        with open("/root/output.txt") as f:
            cls.actual = f.read()

    def test_output_matches(self):
        """Agent output must exactly match oracle output."""
        assert self.actual.strip() == self.expected.strip(), (
            f"Output mismatch.\nExpected:\n{self.expected}\nGot:\n{self.actual}"
        )

    def test_all_lines_present(self):
        """Every required line must be present."""
        for line in self.expected.split("\n"):
            key = line.split(":")[0] if ":" in line else line
            assert key in self.actual, f"Missing line: {key}"

    def test_sequence_type(self):
        m = re.search(r"Sequence type: (.+)", self.actual)
        assert m is not None and "DNA" in m.group(1)

    def test_gc_content(self):
        m = re.search(r"GC content: ([\d.]+)%", self.actual)
        assert m is not None
        gc = float(m.group(1))
        assert abs(gc - 46.6) < 0.1, f"GC content should be 46.6%, got {gc}"

    def test_frame2_translation(self):
        m = re.search(r"Frame 2 translation: ([A-Z*?]+)", self.actual)
        assert m is not None and m.group(1) == "LQLPCS*LMPYDASCQCLI"

    def test_longest_orf(self):
        m = re.search(r"Longest ORF length: (\d+) bp", self.actual)
        assert m is not None and int(m.group(1)) == 21, "Longest ORF should be 21 bp"
