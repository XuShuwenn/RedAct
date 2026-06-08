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

    def test_total_spectra(self):
        m = re.search(r"Total spectra: (\d+)", self.actual)
        assert m is not None and int(m.group(1)) == 3, "Should have 3 spectra"

    def test_most_peaks_spectrum(self):
        m = re.search(r"Spectrum with most peaks: (\S+) \((\d+) peaks\)", self.actual)
        assert m is not None
        assert m.group(1) == "Spectrum_C", f"Should be Spectrum_C, got {m.group(1)}"
        assert int(m.group(2)) == 7, f"Should have 7 peaks, got {m.group(2)}"

    def test_total_peaks(self):
        m = re.search(r"Total peaks across all spectra: (\d+)", self.actual)
        assert m is not None and int(m.group(1)) == 15, "Total peaks should be 15"
