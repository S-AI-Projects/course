"""Unit tests for Applied Lab R16-T047: Token-Budget Preflight Worked Example."""

import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    TOKENIZER_NOTE,
    PreflightResult,
    TokenBudgetPreflight,
    run_regression_suite,
)


class TestTokenBudgetPreflightR16T047(unittest.TestCase):
    """Test suite validating preflight regression fixtures and contract criteria."""

    def setUp(self):
        self.preflight = TokenBudgetPreflight(3)

    def test_budget_3_with_one_two_three_four(self):
        """Budget 3 with 'one two three four' retains [one,two,three] and reports 1 removed."""
        res = self.preflight.check("one two three four")
        self.assertEqual(res.retained, ["one", "two", "three"])
        self.assertEqual(res.removed_count, 1)
        self.assertTrue(res.is_truncated)
        self.assertIn("Truncated 1 token(s)", res.explanation)

    def test_empty_input_retains_none(self):
        """Empty input retains none ([]) and reports 0 removed."""
        res = self.preflight.check("")
        self.assertEqual(res.retained, [])
        self.assertEqual(res.removed_count, 0)
        self.assertFalse(res.is_truncated)

    def test_whitespace_only_retains_none(self):
        """Whitespace string retains none and reports 0 removed."""
        res = self.preflight.check("   \n\t  ")
        self.assertEqual(res.retained, [])
        self.assertEqual(res.removed_count, 0)

    def test_reject_negative_budget(self):
        """Reject negative budget with ValueError."""
        with self.assertRaises(ValueError):
            TokenBudgetPreflight(-1)
        with self.assertRaises(ValueError):
            TokenBudgetPreflight(-10)

    def test_regression_suite_execution(self):
        """Execute the exact worked example regression suite."""
        all_ok, records = run_regression_suite()
        self.assertTrue(all_ok)
        for r in records:
            self.assertEqual(r["status"], "PASS")

    def test_teaching_approximation_disclaimer_present(self):
        """Ensure tokenizer is labeled as a teaching approximation."""
        self.assertIn("TEACHING APPROXIMATION", TOKENIZER_NOTE)

    def test_deliberate_wrong_result_fails(self):
        """Deliberate wrong expectation triggers assertion failure."""
        res = self.preflight.check("one two three four")
        wrong_retained = ["one", "two", "three", "four"]
        with self.assertRaises(AssertionError):
            self.assertEqual(res.retained, wrong_retained)


if __name__ == "__main__":
    unittest.main()
