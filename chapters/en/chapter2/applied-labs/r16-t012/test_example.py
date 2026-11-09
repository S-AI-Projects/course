"""Unit test suite for Applied Lab R16-T012 worked decision example."""

import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from example import (
    PAD_AND_MASK,
    REJECT_EXCEEDS_MAX_LENGTH,
    REJECT_MISSING_INPUT,
    REJECT_UNBATCHED,
    SCENARIOS,
    VALID_DECISIONS,
    VALID_DIRECT_INFERENCE,
    check_decision_table,
    evaluate_scenario,
)


class TestWorkedDecisionExample(unittest.TestCase):
    """Test suite verifying decision engine, table consistency, and failure behavior."""

    def test_normal_scenario_unequal_batch(self):
        """Normal scenario: batches with unequal lengths require padding and attention mask."""
        facts = {
            "sequence_ids": [[101, 2054, 2003, 102], [101, 7592, 102]],
            "max_model_length": 512,
        }
        self.assertEqual(evaluate_scenario(facts), PAD_AND_MASK)

    def test_boundary_smallest_valid_input(self):
        """Boundary scenario: smallest valid input [[101]] is rectangular and proceeds directly."""
        facts = {
            "sequence_ids": [[101]],
            "max_model_length": 512,
        }
        self.assertEqual(evaluate_scenario(facts), VALID_DIRECT_INFERENCE)

    def test_missing_information_scenario_none(self):
        """Missing-information scenario: None sequence_ids is rejected."""
        facts = {"sequence_ids": None}
        self.assertEqual(evaluate_scenario(facts), REJECT_MISSING_INPUT)

    def test_missing_information_empty_batch(self):
        """Missing-information scenario: empty list or empty sequence is rejected."""
        self.assertEqual(evaluate_scenario({"sequence_ids": []}), REJECT_MISSING_INPUT)
        self.assertEqual(evaluate_scenario({"sequence_ids": [[]]}), REJECT_MISSING_INPUT)
        self.assertEqual(evaluate_scenario(None), REJECT_MISSING_INPUT)

    def test_boundary_unbatched_1d_sequence(self):
        """Boundary scenario: unbatched 1D sequence triggers rejection to prevent IndexError."""
        facts = {"sequence_ids": [101, 2054, 102]}
        self.assertEqual(evaluate_scenario(facts), REJECT_UNBATCHED)

    def test_boundary_exact_max_context_length(self):
        """Boundary scenario: sequence exactly at max_model_length (512) is valid."""
        facts = {"sequence_ids": [[101] * 512], "max_model_length": 512}
        self.assertEqual(evaluate_scenario(facts), VALID_DIRECT_INFERENCE)

    def test_boundary_exceeding_max_context_length(self):
        """Boundary scenario: sequence exceeding max_model_length (513 > 512) is rejected."""
        facts = {"sequence_ids": [[101] * 513], "max_model_length": 512}
        self.assertEqual(evaluate_scenario(facts), REJECT_EXCEEDS_MAX_LENGTH)

    def test_all_published_scenarios_pass_checker(self):
        """Verify that every entry in SCENARIOS matches its expected decision."""
        passed, results = check_decision_table(SCENARIOS)
        self.assertTrue(passed)
        for item in results:
            self.assertTrue(item["passed"], f"Scenario {item['id']} failed")
            self.assertIn(item["expected"], VALID_DECISIONS)
            self.assertTrue(len(item["rationale"]) > 0)

    def test_deliberate_wrong_decision_makes_checker_fail(self):
        """Verify the checker flags failure when an expected decision is deliberately corrupted."""
        corrupted = copy.deepcopy(SCENARIOS)
        # Corrupt the expected decision of the first scenario
        corrupted[0]["expected_decision"] = VALID_DIRECT_INFERENCE

        passed, results = check_decision_table(corrupted)
        self.assertFalse(passed)
        self.assertFalse(results[0]["passed"])
        self.assertEqual(results[0]["expected"], VALID_DIRECT_INFERENCE)
        self.assertEqual(results[0]["actual"], PAD_AND_MASK)

    def test_deliberate_wrong_assertion_raises_error(self):
        """Verify an intentional wrong assertion raises an AssertionError."""
        facts = {"sequence_ids": [[101]]}
        actual = evaluate_scenario(facts)
        with self.assertRaises(AssertionError):
            self.assertEqual(actual, PAD_AND_MASK)


if __name__ == "__main__":
    unittest.main()
