#!/usr/bin/env python3
"""Pytest-based verifier for constrained optimization task.

Problem: Minimize f(x) = x1^2 + x2^2 subject to x1 + x2 >= 1
Theoretical optimal: x1 = x2 = 0.5, f = 0.5
"""

import re


class TestOutputs:
    @classmethod
    def setup_class(cls):
        with open("/root/output.txt") as f:
            cls.actual = f.read()

        # Parse values in setup_class so all tests can access them
        x1_match = re.search(r'Optimal x1:\s*([\d.]+)', cls.actual)
        x2_match = re.search(r'Optimal x2:\s*([\d.]+)', cls.actual)
        obj_match = re.search(r'Objective:\s*([\d.]+)', cls.actual)

        assert x1_match, "Could not find x1 value in output"
        assert x2_match, "Could not find x2 value in output"
        assert obj_match, "Could not find objective value in output"

        cls.x1 = float(x1_match.group(1))
        cls.x2 = float(x2_match.group(1))
        cls.obj = float(obj_match.group(1))

    def test_format(self):
        """Output must have required fields."""
        assert "Optimal x1:" in self.actual, "Missing Optimal x1"
        assert "Optimal x2:" in self.actual, "Missing Optimal x2"
        assert "Objective:" in self.actual, "Missing Objective"

    def test_bounds_satisfied(self):
        """Check x1 and x2 are within bounds [0, 10]."""
        assert 0 <= self.x1 <= 10, f"x1={self.x1} out of bounds [0, 10]"
        assert 0 <= self.x2 <= 10, f"x2={self.x2} out of bounds [0, 10]"

    def test_constraint_satisfied(self):
        """Check constraint x1 + x2 >= 1 is satisfied."""
        constraint_value = self.x1 + self.x2
        assert constraint_value >= 1 - 1e-6, (
            f"Constraint violated: x1 + x2 = {constraint_value} < 1"
        )

    def test_objective_reasonable(self):
        """Objective f = x1^2 + x2^2 should be close to theoretical optimal 0.5.

        The theoretical minimum is 0.5 at x1=x2=0.5.
        Allow tolerance for algorithm variation.
        """
        theoretical_optimal = 0.5
        tolerance = 0.2  # Allow some margin for algorithm variation
        assert self.obj <= theoretical_optimal + tolerance, (
            f"Objective {self.obj} exceeds optimal {theoretical_optimal} + {tolerance}"
        )

    def test_objective_matches_formula(self):
        """Objective should match x1^2 + x2^2."""
        expected_obj = self.x1**2 + self.x2**2
        assert abs(self.obj - expected_obj) < 0.01, (
            f"Objective {self.obj} != x1^2 + x2^2 = {expected_obj:.4f}"
        )
