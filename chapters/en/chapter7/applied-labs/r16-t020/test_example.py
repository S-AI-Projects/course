"""Unit tests for Token-Budget Preflight — Scenario Assessment (Task R16-T020).

Verifies the required preflight contract, the three applied assessment questions,
boundary policies, exception handling, and deliberate failure detection.
"""

import os
import sys
import unittest

# Ensure the lab directory is on sys.path
LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    APPLIED_QUESTIONS,
    TokenBudgetResult,
    WhitespaceTokenizer,
    check_question_1_predict_output,
    check_question_2_diagnose_failure,
    check_question_3_boundary_policy,
    evaluate_all_questions,
    token_budget_preflight,
)


class TestRequiredContract(unittest.TestCase):
    """Core acceptance tests specified by Issue #23 'Done when' checklist."""

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
        """Whitespace-only input retains no tokens."""
        result = token_budget_preflight("   \t\n  ", 3)
        self.assertEqual(result.retained_tokens, [])
        self.assertEqual(result.removed_count, 0)
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


class TestAppliedQuestions(unittest.TestCase):
    """Focus: Three applied questions — predict output, diagnose failure, boundary policy."""

    def test_question_1_predict_output(self):
        """Question 1 executable check passes."""
        self.assertTrue(
            check_question_1_predict_output(),
            "Question 1 (predict output) check failed.",
        )

    def test_question_2_diagnose_failure(self):
        """Question 2 executable check passes."""
        self.assertTrue(
            check_question_2_diagnose_failure(),
            "Question 2 (diagnose failure) check failed.",
        )

    def test_question_3_boundary_policy(self):
        """Question 3 executable check passes."""
        self.assertTrue(
            check_question_3_boundary_policy(),
            "Question 3 (boundary policy) check failed.",
        )

    def test_evaluate_all_questions_audit(self):
        """All three applied questions execute and pass their audits."""
        all_passed, audit = evaluate_all_questions()
        self.assertTrue(all_passed)
        self.assertEqual(len(audit), 3)
        for item in audit:
            self.assertTrue(item["passed"], f"Question {item['id']} failed check")
            self.assertGreater(len(item["rationale"]), 20)


class TestBoundaryAndEdgeCases(unittest.TestCase):
    """Additional edge cases and input validation."""

    def test_exact_budget_match(self):
        """Exact budget match retains all tokens with zero truncation."""
        res = token_budget_preflight("one two three", 3)
        self.assertEqual(res.retained_tokens, ["one", "two", "three"])
        self.assertEqual(res.removed_count, 0)
        self.assertFalse(res.truncated)

    def test_budget_exceeds_token_count(self):
        """Budget larger than token count retains all tokens."""
        res = token_budget_preflight("one two", 5)
        self.assertEqual(res.retained_tokens, ["one", "two"])
        self.assertEqual(res.removed_count, 0)
        self.assertFalse(res.truncated)

    def test_zero_budget(self):
        """Zero budget removes all tokens."""
        res = token_budget_preflight("alpha beta gamma", 0)
        self.assertEqual(res.retained_tokens, [])
        self.assertEqual(res.removed_count, 3)
        self.assertTrue(res.truncated)

    def test_invalid_types(self):
        """Non-string text and non-integer budgets raise TypeError."""
        with self.assertRaises(TypeError):
            token_budget_preflight(12345, 3)
        with self.assertRaises(TypeError):
            token_budget_preflight("prompt", "3")
        with self.assertRaises(TypeError):
            token_budget_preflight("prompt", True)


class TestDeliberateFailure(unittest.TestCase):
    """Contribution Focus: Demonstrates that an intentional wrong result fails."""

    def test_corrupted_result_fails_assertion(self):
        """Injecting a corrupted result triggers assertion failure."""
        correct = token_budget_preflight("one two three four", 3)
        corrupted = TokenBudgetResult(
            retained_tokens=["one", "two", "WRONG"],
            removed_tokens=["four"],
            removed_count=999,
            total_tokens=4,
            budget=3,
            truncated=True,
        )

        with self.assertRaises(AssertionError):
            self.assertEqual(corrupted.retained_tokens, correct.retained_tokens)

        with self.assertRaises(AssertionError):
            self.assertEqual(corrupted.removed_count, correct.removed_count)


if __name__ == "__main__":
    unittest.main()
