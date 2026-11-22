"""Unit tests for Applied Lab R16-T041: Token-Budget Preflight."""

import os
import sys
import unittest

# Ensure the lab directory is importable
LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    TOKENIZER_NOTE,
    PreflightReport,
    TokenBudgetPreflight,
    check_token_budget,
)


class TestTokenBudgetPreflight(unittest.TestCase):
    """Test suite validating token-budget preflight contract."""

    def test_normal_budget_truncation(self):
        """Budget 3 with 'one two three four' retains [one,two,three] and reports 1 removed."""
        engine = TokenBudgetPreflight(3)
        report = engine.check("one two three four")

        self.assertEqual(report.retained, ["one", "two", "three"])
        self.assertEqual(report.removed_count, 1)
        self.assertTrue(report.is_truncated)
        self.assertEqual(report.total_tokens, 4)
        self.assertEqual(report.budget, 3)

        # Also verify functional interface
        func_rep = check_token_budget("one two three four", 3)
        self.assertEqual(func_rep["retained"], ["one", "two", "three"])
        self.assertEqual(func_rep["removed_count"], 1)
        self.assertTrue(func_rep["is_truncated"])

    def test_empty_input_retains_none(self):
        """Empty input retains [] and reports 0 removed."""
        engine = TokenBudgetPreflight(3)
        report = engine.check("")

        self.assertEqual(report.retained, [])
        self.assertEqual(report.removed_count, 0)
        self.assertFalse(report.is_truncated)
        self.assertEqual(report.total_tokens, 0)

    def test_whitespace_input_retains_none(self):
        """Whitespace-only input retains [] and reports 0 removed."""
        engine = TokenBudgetPreflight(3)
        report = engine.check("   \n\t   ")

        self.assertEqual(report.retained, [])
        self.assertEqual(report.removed_count, 0)
        self.assertFalse(report.is_truncated)
        self.assertEqual(report.total_tokens, 0)

    def test_negative_budget_rejected(self):
        """Reject negative budget with ValueError."""
        with self.assertRaises(ValueError):
            TokenBudgetPreflight(-1)

        with self.assertRaises(ValueError):
            check_token_budget("hello", -5)

    def test_within_budget_no_truncation(self):
        """Inputs within budget retain all tokens without truncation."""
        engine = TokenBudgetPreflight(5)
        report = engine.check("one two three")

        self.assertEqual(report.retained, ["one", "two", "three"])
        self.assertEqual(report.removed_count, 0)
        self.assertFalse(report.is_truncated)
        self.assertEqual(report.total_tokens, 3)

    def test_exact_budget_match(self):
        """Prompt length exactly matching budget retains all tokens without truncation."""
        engine = TokenBudgetPreflight(3)
        report = engine.check("alpha beta gamma")

        self.assertEqual(report.retained, ["alpha", "beta", "gamma"])
        self.assertEqual(report.removed_count, 0)
        self.assertFalse(report.is_truncated)
        self.assertEqual(report.total_tokens, 3)

    def test_zero_budget(self):
        """Budget 0 truncates all tokens and reports all removed."""
        engine = TokenBudgetPreflight(0)
        report = engine.check("one two three")

        self.assertEqual(report.retained, [])
        self.assertEqual(report.removed_count, 3)
        self.assertTrue(report.is_truncated)
        self.assertEqual(report.total_tokens, 3)

    def test_invalid_types_raise_typeerror(self):
        """Non-string prompt or non-integer budget raises TypeError."""
        with self.assertRaises(TypeError):
            TokenBudgetPreflight("three")  # type: ignore

        with self.assertRaises(TypeError):
            TokenBudgetPreflight(True)  # bool is subclass of int

        engine = TokenBudgetPreflight(3)
        with self.assertRaises(TypeError):
            engine.check(None)  # type: ignore

        with self.assertRaises(TypeError):
            engine.check(123)  # type: ignore

    def test_teaching_approximation_label_present(self):
        """Ensure tokenizer is explicitly labeled as teaching approximation."""
        self.assertIn("TEACHING APPROXIMATION", TOKENIZER_NOTE)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrate that an intentional incorrect result triggers assertion failure."""
        engine = TokenBudgetPreflight(3)
        report = engine.check("one two three four")
        wrong_retained = ["one", "two", "three", "four"]
        with self.assertRaises(AssertionError):
            self.assertEqual(report.retained, wrong_retained)


if __name__ == "__main__":
    unittest.main()
