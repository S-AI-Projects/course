"""Unit tests for Token-Budget Preflight (Task R16-T016).

Verifies the contract of token_budget_preflight, baseline equivalence,
boundary conditions, exception handling, and deliberate failure detection.
"""

import os
import sys
import unittest

# Ensure the lab directory is on sys.path for direct imports
LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    TokenBudgetEnforcer,
    TokenBudgetResult,
    WhitespaceTokenizer,
    token_budget_preflight,
    token_budget_preflight_baseline,
)


class TestRequiredContract(unittest.TestCase):
    """Core acceptance tests specified by Issue #19 'Done when' checklist."""

    def test_budget_three_with_four_tokens(self):
        """Budget 3 with 'one two three four' retains [one, two, three] and reports 1 removed token."""
        result = token_budget_preflight("one two three four", 3)
        self.assertEqual(result.retained_tokens, ["one", "two", "three"])
        self.assertEqual(result.removed_tokens, ["four"])
        self.assertEqual(result.removed_count, 1)
        self.assertEqual(result.total_tokens, 4)
        self.assertEqual(result.budget, 3)
        self.assertTrue(result.truncated)

    def test_empty_input_retains_none(self):
        """Empty input retains no tokens and reports zero removed tokens."""
        result = token_budget_preflight("", 3)
        self.assertEqual(result.retained_tokens, [])
        self.assertEqual(result.removed_tokens, [])
        self.assertEqual(result.removed_count, 0)
        self.assertEqual(result.total_tokens, 0)
        self.assertFalse(result.truncated)

    def test_whitespace_only_input_retains_none(self):
        """Whitespace-only input is treated as empty."""
        result = token_budget_preflight("   \t\n  ", 3)
        self.assertEqual(result.retained_tokens, [])
        self.assertEqual(result.removed_count, 0)
        self.assertEqual(result.total_tokens, 0)
        self.assertFalse(result.truncated)

    def test_reject_negative_budget(self):
        """A negative budget must raise a ValueError."""
        with self.assertRaises(ValueError):
            token_budget_preflight("one two three four", -1)
        with self.assertRaises(ValueError):
            token_budget_preflight("", -5)

    def test_teaching_approximation_flag(self):
        """Verify the tokenizer is explicitly tagged as a teaching approximation."""
        tokenizer = WhitespaceTokenizer()
        self.assertTrue(
            getattr(tokenizer, "is_teaching_approximation", False),
            "Tokenizer must explicitly label itself as a teaching approximation.",
        )


class TestBoundaryAndEdgeCases(unittest.TestCase):
    """Boundary conditions for token budget checking."""

    def test_exact_budget_match(self):
        """Prompt length exactly equal to budget should retain all with zero truncation."""
        result = token_budget_preflight("one two three", 3)
        self.assertEqual(result.retained_tokens, ["one", "two", "three"])
        self.assertEqual(result.removed_count, 0)
        self.assertEqual(result.removed_tokens, [])
        self.assertFalse(result.truncated)

    def test_budget_exceeds_token_count(self):
        """Budget larger than token count retains all tokens without truncation."""
        result = token_budget_preflight("one two", 10)
        self.assertEqual(result.retained_tokens, ["one", "two"])
        self.assertEqual(result.removed_count, 0)
        self.assertFalse(result.truncated)

    def test_zero_budget(self):
        """Budget of 0 removes all tokens and retains an empty list."""
        result = token_budget_preflight("one two three", 0)
        self.assertEqual(result.retained_tokens, [])
        self.assertEqual(result.removed_count, 3)
        self.assertEqual(result.removed_tokens, ["one", "two", "three"])
        self.assertTrue(result.truncated)

    def test_multiple_whitespace_separators(self):
        """Consecutive spaces, tabs, and newlines do not produce empty tokens."""
        result = token_budget_preflight("word1   word2\t\nword3", 2)
        self.assertEqual(result.retained_tokens, ["word1", "word2"])
        self.assertEqual(result.removed_count, 1)
        self.assertEqual(result.removed_tokens, ["word3"])


class TestTypeValidation(unittest.TestCase):
    """Input validation and type checking."""

    def test_invalid_text_type(self):
        """Non-string inputs must raise TypeError."""
        for invalid in [None, 123, ["a", "b"], {"text": "hi"}]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    token_budget_preflight(invalid, 3)

    def test_invalid_budget_type(self):
        """Non-integer budgets (or bool) must raise TypeError."""
        for invalid in ["3", 3.5, True, False, None, [3]]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    token_budget_preflight("sample prompt", invalid)

    def test_enforcer_invalid_tokens_type(self):
        """TokenBudgetEnforcer.enforce must reject non-list input."""
        enforcer = TokenBudgetEnforcer(3)
        with self.assertRaises(TypeError):
            enforcer.enforce("not a list")


class TestRefactoringAndEquivalence(unittest.TestCase):
    """Focus: verifies that the baseline and refactored modular implementations

    produce strictly equivalent results across all scenarios.
    """

    def test_baseline_and_refactored_equivalence(self):
        """Compare baseline and refactored implementation across diverse inputs."""
        test_cases = [
            ("one two three four", 3),
            ("one two three four", 4),
            ("one two three four", 10),
            ("one two three four", 0),
            ("", 5),
            ("", 0),
            ("   ", 2),
            ("alpha beta gamma delta epsilon", 2),
            ("single", 1),
            ("single", 0),
        ]
        for text, budget in test_cases:
            with self.subTest(text=text, budget=budget):
                baseline = token_budget_preflight_baseline(text, budget)
                refactored = token_budget_preflight(text, budget)
                self.assertEqual(baseline, refactored)
                self.assertEqual(baseline.to_dict(), refactored.to_dict())

    def test_baseline_error_equivalence(self):
        """Compare error handling equivalence between baseline and refactored."""
        # Negative budget
        with self.assertRaises(ValueError):
            token_budget_preflight_baseline("sample", -1)
        with self.assertRaises(ValueError):
            token_budget_preflight("sample", -1)

        # Invalid types
        with self.assertRaises(TypeError):
            token_budget_preflight_baseline(123, 3)
        with self.assertRaises(TypeError):
            token_budget_preflight(123, 3)


class TestDeliberateFailure(unittest.TestCase):
    """Proves that a deliberate incorrect output or assertion failure is caught."""

    def test_corrupted_result_fails_contract_assertion(self):
        """Injecting a wrong retained token list or count triggers an assertion error."""
        correct = token_budget_preflight("one two three four", 3)

        # Simulated wrong implementation result
        corrupted = TokenBudgetResult(
            retained_tokens=["one", "two", "WRONG_TOKEN"],
            removed_tokens=["four"],
            removed_count=99,
            total_tokens=4,
            budget=3,
            truncated=True,
        )

        with self.assertRaises(AssertionError):
            self.assertEqual(corrupted.retained_tokens, ["one", "two", "three"])

        with self.assertRaises(AssertionError):
            self.assertEqual(corrupted.removed_count, 1)


if __name__ == "__main__":
    unittest.main()
