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

    def test_all_kmers_are_3mers(self):
        for line in self.actual.strip().split('\n'):
            kmer = line.split(':')[0].strip()
            assert len(kmer) == 3, f"K-mer {kmer} is not 3 characters"

    def test_kmers_sorted(self):
        kmers = [line.split(':')[0].strip() for line in self.actual.strip().split('\n')]
        assert kmers == sorted(kmers), "K-mers not sorted alphabetically"
