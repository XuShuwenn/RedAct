#!/usr/bin/env python3
"""Pytest-based verifier for pymoo-optimization task.

Verifies that the output contains valid Pareto front points for:
- f1(x) = (x1 - 2)^2
- f2(x) = (x1 + 2)^2
- Subject to: -10 <= x1 <= 10
"""

import re


class TestOutputs:
    @classmethod
    def setup_class(cls):
        with open("/root/output.txt") as f:
            cls.actual = f.read()

    def test_has_pareto_points(self):
        """Output must contain at least one point."""
        lines = [l for l in self.actual.strip().split('\n') if l.strip()]
        assert len(lines) > 0, "No Pareto points found"
        assert len(lines) <= 100, "Too many points, check output format"

    def test_format(self):
        """Each line must be in format: x1=f1,f2"""
        lines = [l for l in self.actual.strip().split('\n') if l.strip()]
        for i, line in enumerate(lines):
            assert '=' in line, f"Line {i+1}: missing '=' separator: {line}"
            parts = line.split('=')
            assert len(parts) == 2, f"Line {i+1}: too many '=' separators: {line}"
            x1_str, rest = parts
            assert ',' in rest, f"Line {i+1}: missing ',' between f1 and f2: {line}"
            f_parts = rest.split(',')
            assert len(f_parts) == 2, f"Line {i+1}: too many ',' separators: {line}"

    def test_points_on_pareto_front(self):
        """Each point must satisfy f1=(x1-2)^2 and f2=(x1+2)^2 within tolerance."""
        lines = [l for l in self.actual.strip().split('\n') if l.strip()]
        for i, line in enumerate(lines):
            x1 = float(line.split('=')[0])
            rest = line.split('=')[1]
            f1 = float(rest.split(',')[0])
            f2 = float(rest.split(',')[1])

            # Check x1 is in bounds
            assert -10 <= x1 <= 10, f"Line {i+1}: x1={x1} out of bounds [-10,10]"

            # Check f1 = (x1-2)^2
            expected_f1 = (x1 - 2)**2
            assert abs(f1 - expected_f1) < 0.005, f"Line {i+1}: f1={f1} != (x1-2)^2={expected_f1:.3f} (error={abs(f1-expected_f1):.6f})"

            # Check f2 = (x1+2)^2
            expected_f2 = (x1 + 2)**2
            assert abs(f2 - expected_f2) < 0.005, f"Line {i+1}: f2={f2} != (x1+2)^2={expected_f2:.3f} (error={abs(f2-expected_f2):.6f})"

    def test_points_sorted(self):
        """Points must be sorted by x1 in ascending order."""
        lines = [l for l in self.actual.strip().split('\n') if l.strip()]
        x_vals = [float(line.split('=')[0]) for line in lines]
        assert x_vals == sorted(x_vals), "Points not sorted by x1 ascending"

    def test_minimum_points(self):
        """Must have at least 10 Pareto points (NSGA-II should produce many)."""
        lines = [l for l in self.actual.strip().split('\n') if l.strip()]
        assert len(lines) >= 10, f"Only {len(lines)} points, expected at least 10"
