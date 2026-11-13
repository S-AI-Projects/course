#!/usr/bin/env python3
"""
Unit tests for Token-Budget Preflight Comparison Lab (R16-T023).

Verifies the prompt token-budget check contract, truncation reporting,
empty input handling, negative budget rejection, and equivalence between
the two preflight approaches.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

# Ensure current lab directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (
    TokenBudgetPreflight,
    compare_approaches,
    main,
    reference_preflight_calc,
)


class TestTokenBudgetPreflight(unittest.TestCase):
    """Test suite for token budget preflight engine and comparison."""

    def test_required_contract_budget_3(self):
        """
        Verify required contract:
        Budget 3 with "one two three four" retains [one, two, three]
        and reports 1 removed token.
        """
        prompt = "one two three four"
        budget = 3

        engine = TokenBudgetPreflight(budget)
        report = engine.check(prompt)

        self.assertEqual(report.total_tokens, 4)
        self.assertEqual(report.retained, ["one", "two", "three"])
        self.assertEqual(report.removed_count, 1)
        self.assertTrue(report.is_truncated)

    def test_required_contract_empty_input(self):
        """
        Verify required contract:
        Empty input retains none and reports 0 removed tokens.
        """
        engine = TokenBudgetPreflight(3)

        # Empty string
        report_empty = engine.check("")
        self.assertEqual(report_empty.total_tokens, 0)
        self.assertEqual(report_empty.retained, [])
        self.assertEqual(report_empty.removed_count, 0)
        self.assertFalse(report_empty.is_truncated)

        # Whitespace-only string
        report_ws = engine.check("    \t\n  ")
        self.assertEqual(report_ws.total_tokens, 0)
        self.assertEqual(report_ws.retained, [])
        self.assertEqual(report_ws.removed_count, 0)
        self.assertFalse(report_ws.is_truncated)

    def test_required_contract_negative_budget_rejected(self):
        """
        Verify required contract:
        Negative budget is rejected with ValueError.
        """
        with self.assertRaises(ValueError):
            TokenBudgetPreflight(-1)

        with self.assertRaises(ValueError):
            TokenBudgetPreflight(-10)

        with self.assertRaises(ValueError):
            reference_preflight_calc("one two", -1)

    def test_boundary_zero_budget(self):
        """Budget 0 retains no tokens and reports all tokens as removed."""
        engine = TokenBudgetPreflight(0)
        report = engine.check("one two three")
        self.assertEqual(report.total_tokens, 3)
        self.assertEqual(report.retained, [])
        self.assertEqual(report.removed_count, 3)
        self.assertTrue(report.is_truncated)

    def test_boundary_exact_and_under_budget(self):
        """
        Verify inputs that fit within the budget are not truncated:
        - Exactly equal to budget: 0 removed tokens
        - Less than budget: 0 removed tokens
        """
        engine = TokenBudgetPreflight(4)

        # Exact fit
        report_exact = engine.check("one two three four")
        self.assertEqual(report_exact.retained, ["one", "two", "three", "four"])
        self.assertEqual(report_exact.removed_count, 0)
        self.assertFalse(report_exact.is_truncated)

        # Under budget
        report_under = engine.check("one two")
        self.assertEqual(report_under.retained, ["one", "two"])
        self.assertEqual(report_under.removed_count, 0)
        self.assertFalse(report_under.is_truncated)

    def test_compare_approaches_identical_results(self):
        """
        Verify that Approach 1 (Engine) and Approach 2 (Reference Calc)
        produce identical results across a diverse set of inputs.
        """
        test_inputs = [
            ("one two three four", 3),
            ("one two three four", 4),
            ("one two three four", 5),
            ("one two three four", 0),
            ("", 5),
            ("   ", 3),
            ("alpha beta gamma delta epsilon", 2),
            ("single", 1),
        ]
        for prompt, budget in test_inputs:
            with self.subTest(prompt=prompt, budget=budget):
                self.assertTrue(compare_approaches(prompt, budget))

    def test_explicit_expected_result_table(self):
        """
        Verify both approaches against an independently defined
        ground-truth table of expected values.
        """
        table = [
            {
                "prompt": "one two three four",
                "budget": 3,
                "retained": ["one", "two", "three"],
                "removed": 1,
                "truncated": True,
            },
            {
                "prompt": "",
                "budget": 3,
                "retained": [],
                "removed": 0,
                "truncated": False,
            },
            {
                "prompt": "apple banana",
                "budget": 5,
                "retained": ["apple", "banana"],
                "removed": 0,
                "truncated": False,
            },
            {
                "prompt": "red green blue",
                "budget": 0,
                "retained": [],
                "removed": 3,
                "truncated": True,
            },
        ]

        for entry in table:
            prompt = entry["prompt"]
            budget = entry["budget"]

            # Test Approach 1
            rep1 = TokenBudgetPreflight(budget).check(prompt)
            self.assertEqual(rep1.retained, entry["retained"])
            self.assertEqual(rep1.removed_count, entry["removed"])
            self.assertEqual(rep1.is_truncated, entry["truncated"])

            # Test Approach 2
            rep2 = reference_preflight_calc(prompt, budget)
            self.assertEqual(rep2["retained"], entry["retained"])
            self.assertEqual(rep2["removed_count"], entry["removed"])
            self.assertEqual(rep2["is_truncated"], entry["truncated"])

    def test_cli_main_execution(self):
        """Verify CLI main entrypoint executes cleanly and produces expected text."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("Contract Case 1: Prompt: 'one two three four', Budget: 3", output)
        self.assertIn("Retained:       ['one', 'two', 'three']", output)
        self.assertIn("Removed tokens: 1", output)
        self.assertIn("Contract Case 2: Empty input: '', Budget: 3", output)
        self.assertIn("PASS: Correctly rejected negative budget", output)
        self.assertIn("All comparison cases agreed identically.", output)


if __name__ == "__main__":
    unittest.main()
