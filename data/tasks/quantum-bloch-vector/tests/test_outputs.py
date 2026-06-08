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

    def test_has_rx(self):
        assert "rx:" in self.actual

    def test_vector_magnitude(self):
        m_rx = re.search(r"rx: ([-+0-9.]+)", self.actual)
        m_ry = re.search(r"ry: ([-+0-9.]+)", self.actual)
        m_rz = re.search(r"rz: ([-+0-9.]+)", self.actual)
        assert m_rx and m_ry and m_rz
        rx, ry, rz = float(m_rx.group(1)), float(m_ry.group(1)), float(m_rz.group(1))
        mag = (rx*rx + ry*ry + rz*rz) ** 0.5
        assert 0.99 <= mag <= 1.01, f"Bloch vector magnitude should be ~1, got {mag}"
