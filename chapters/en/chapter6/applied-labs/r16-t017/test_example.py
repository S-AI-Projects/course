"""Unit tests for Worked Decision Example (Task R16-T017).

Verifies the published decision table, scenario evaluations, boundary conditions,
regression tests, and deliberate failure detection for Chapter 6 Section 1.
"""

import copy
import os
import sys
import unittest

# Ensure the lab directory is on sys.path for direct imports
LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    REJECT_EMPTY_CORPUS,
    REJECT_INVALID_MODE,
    REJECT_MISSING_CORPUS,
    REUSE_PRETRAINED_TOKENIZER,
    SCENARIOS,
    TRAIN_NEW_TOKENIZER,
    VALID_DECISIONS,
    check_decision_table,
    evaluate_scenario,
    run_regression_test,
)


class TestRequiredContract(unittest.TestCase):
    """Core acceptance tests specified by Issue #20 'Done when' checklist."""

    def test_normal_scenario_train_new_tokenizer(self):
        """Normal scenario: Pretraining from scratch on domain corpus decides TRAIN_NEW_TOKENIZER."""
        normal_scenario = next(s for s in SCENARIOS if s["id"] == "normal_scratch_domain_shift")
        actual = evaluate_scenario(normal_scenario["input_facts"])
        self.assertEqual(actual, TRAIN_NEW_TOKENIZER)
        self.assertEqual(actual, normal_scenario["expected_decision"])
        self.assertIn("Chapter 6, Section 1", normal_scenario["rationale"])

    def test_boundary_scenario_minimal_corpus(self):
        """Boundary scenario: Smallest valid single-sample corpus decides TRAIN_NEW_TOKENIZER."""
        boundary_scenario = next(s for s in SCENARIOS if s["id"] == "boundary_minimal_single_sample")
        actual = evaluate_scenario(boundary_scenario["input_facts"])
        self.assertEqual(actual, TRAIN_NEW_TOKENIZER)
        self.assertEqual(actual, boundary_scenario["expected_decision"])
        self.assertIn("minimal", boundary_scenario["rationale"].lower())

    def test_missing_information_null_corpus(self):
        """Missing-information scenario: Null corpus iterator decides REJECT_MISSING_CORPUS."""
        missing_scenario = next(s for s in SCENARIOS if s["id"] == "missing_information_null_corpus")
        actual = evaluate_scenario(missing_scenario["input_facts"])
        self.assertEqual(actual, REJECT_MISSING_CORPUS)
        self.assertEqual(actual, missing_scenario["expected_decision"])
        self.assertIn("missing", missing_scenario["rationale"].lower())


class TestBoundaryAndEdgeCases(unittest.TestCase):
    """Additional edge cases and boundary conditions."""

    def test_matching_domain_fine_tune_reuses_tokenizer(self):
        """Standard fine-tuning on matching domain decides REUSE_PRETRAINED_TOKENIZER."""
        scenario = next(s for s in SCENARIOS if s["id"] == "boundary_matching_domain_fine_tune")
        actual = evaluate_scenario(scenario["input_facts"])
        self.assertEqual(actual, REUSE_PRETRAINED_TOKENIZER)

    def test_empty_corpus_list_rejected(self):
        """Empty list of texts is rejected as REJECT_EMPTY_CORPUS."""
        facts = {
            "training_mode": "scratch",
            "corpus_domain": "python_code",
            "corpus_texts": [],
        }
        self.assertEqual(evaluate_scenario(facts), REJECT_EMPTY_CORPUS)

    def test_whitespace_only_corpus_rejected(self):
        """Corpus containing only whitespace strings is rejected as REJECT_EMPTY_CORPUS."""
        facts = {
            "training_mode": "scratch",
            "corpus_domain": "python_code",
            "corpus_texts": ["   \n\t  ", "  "],
        }
        self.assertEqual(evaluate_scenario(facts), REJECT_EMPTY_CORPUS)

    def test_invalid_training_mode_rejected(self):
        """Unknown or missing training_mode is rejected as REJECT_INVALID_MODE."""
        facts = {
            "training_mode": "unsupported_mode",
            "corpus_domain": "python_code",
            "corpus_texts": ["sample code text"],
        }
        self.assertEqual(evaluate_scenario(facts), REJECT_INVALID_MODE)

    def test_none_facts_rejected(self):
        """Passing None or non-dict facts returns REJECT_MISSING_CORPUS."""
        self.assertEqual(evaluate_scenario(None), REJECT_MISSING_CORPUS)
        self.assertEqual(evaluate_scenario("not a dict"), REJECT_MISSING_CORPUS)

    def test_all_decisions_valid(self):
        """Ensure all returned decisions belong to the VALID_DECISIONS set."""
        for scenario in SCENARIOS:
            decision = evaluate_scenario(scenario["input_facts"])
            self.assertIn(decision, VALID_DECISIONS)


class TestDecisionTableChecker(unittest.TestCase):
    """Verifies the table checker and regression test suite."""

    def test_check_decision_table_all_pass(self):
        """The checker passes when validating the published SCENARIOS table."""
        all_passed, results = check_decision_table(SCENARIOS)
        self.assertTrue(all_passed)
        self.assertEqual(len(results), len(SCENARIOS))
        for res in results:
            self.assertTrue(res["passed"], f"Scenario {res['id']} failed check")

    def test_regression_test_runner(self):
        """Every individual published scenario passes the exact regression test."""
        for scenario in SCENARIOS:
            with self.subTest(scenario_id=scenario["id"]):
                self.assertTrue(run_regression_test(scenario))


class TestDeliberateFailure(unittest.TestCase):
    """Contribution Focus: Demonstrates that a deliberately altered decision fails."""

    def test_deliberate_wrong_decision_fails_checker(self):
        """Deliberately changing an expected decision makes check_decision_table return False."""
        corrupted = copy.deepcopy(SCENARIOS)
        # Flip the normal scenario expected decision
        corrupted[0]["expected_decision"] = REUSE_PRETRAINED_TOKENIZER

        all_passed, results = check_decision_table(corrupted)
        self.assertFalse(all_passed, "Checker should fail when a decision is deliberately changed")
        self.assertFalse(results[0]["passed"], "Mutated scenario should fail validation")
        self.assertNotEqual(results[0]["expected"], results[0]["actual"])

    def test_deliberate_wrong_regression_fails(self):
        """Deliberately corrupted regression test expectation returns False."""
        corrupted = copy.deepcopy(SCENARIOS[0])
        corrupted["expected_decision"] = "DELIBERATE_WRONG_DECISION"
        self.assertFalse(run_regression_test(corrupted))


if __name__ == "__main__":
    unittest.main()
