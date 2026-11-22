"""Unit tests for Applied Lab R16-T050: Token-Budget Preflight & Scenario Assessment."""

import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    APPLIED_SCENARIO_QUESTIONS,
    TOKENIZER_NOTE,
    PreflightReport,
    TokenBudgetPreflight,
    execute_scenario_assessments,
)


class TestTokenBudgetScenarioAssessment(unittest.TestCase):
    """Test suite validating preflight contracts and scenario assessment questions."""

    def setUp(self):
        self.preflight = TokenBudgetPreflight(3)

    def test_budget_3_with_one_two_three_four(self):
        """Budget 3 with 'one two three four' retains [one,two,three] and reports 1 removed."""
        rep = self.preflight.check("one two three four")
        self.assertEqual(rep.retained, ["one", "two", "three"])
        self.assertEqual(rep.removed_count, 1)
        self.assertTrue(rep.is_truncated)
        self.assertEqual(rep.total_tokens, 4)

    def test_empty_input_retains_none(self):
        """Empty input retains [] and reports 0 removed."""
        rep = self.preflight.check("")
        self.assertEqual(rep.retained, [])
        self.assertEqual(rep.removed_count, 0)
        self.assertFalse(rep.is_truncated)

    def test_whitespace_only_retains_none(self):
        """Whitespace string retains [] and reports 0 removed."""
        rep = self.preflight.check("   \n\t  ")
        self.assertEqual(rep.retained, [])
        self.assertEqual(rep.removed_count, 0)

    def test_reject_negative_budget(self):
        """Reject negative budget with ValueError."""
        with self.assertRaises(ValueError):
            TokenBudgetPreflight(-1)
        with self.assertRaises(ValueError):
            TokenBudgetPreflight(-5)

    def test_three_applied_scenario_assessment_questions(self):
        """Verify all three applied questions (predict output, diagnose failure, boundary policy) pass checks."""
        self.assertEqual(len(APPLIED_SCENARIO_QUESTIONS), 3)
        all_passed, audit = execute_scenario_assessments()
        self.assertTrue(all_passed)
        for entry in audit:
            self.assertTrue(entry["passed"])
            self.assertIn("rationale", entry)
            self.assertTrue(len(entry["rationale"]) > 0)

    def test_teaching_approximation_label_present(self):
        """Ensure tokenizer is labeled as a teaching approximation."""
        self.assertIn("TEACHING APPROXIMATION", TOKENIZER_NOTE)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrate that an intentional wrong result makes test fail."""
        rep = self.preflight.check("one two three four")
        wrong_retained = ["one", "two", "three", "four"]
        with self.assertRaises(AssertionError):
            self.assertEqual(rep.retained, wrong_retained)


if __name__ == "__main__":
    unittest.main()
