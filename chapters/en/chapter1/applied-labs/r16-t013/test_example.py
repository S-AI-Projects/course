"""Unit test suite for Applied Lab R16-T013 security rubric and comparison."""

import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from example import (
    REFERENCE_RESULTS,
    SCENARIOS,
    check_control_relevance,
    check_scenario_completeness,
    compare_both_approaches,
    evaluate_direct,
    evaluate_reference,
)


class TestSecurityScenarioRubric(unittest.TestCase):
    """Test suite validating scenario structural rubric and dual-approach agreement."""

    def test_complete_scenario_passes(self):
        """One complete scenario with matching control passes both completeness and relevance."""
        scenario = SCENARIOS[0]
        completeness = check_scenario_completeness(scenario)
        self.assertEqual(completeness["status"], "PASS")
        self.assertEqual(completeness["missing_fields"], [])

        relevance = check_control_relevance(scenario)
        self.assertEqual(relevance, "MATCH")

        self.assertEqual(evaluate_direct(scenario), ("PASS", "MATCH"))

    def test_missing_asset_scenario_fails(self):
        """A scenario without an asset fails the structural completeness rubric."""
        scenario = SCENARIOS[1]
        completeness = check_scenario_completeness(scenario)
        self.assertEqual(completeness["status"], "FAIL")
        self.assertIn("asset", completeness["missing_fields"])

        relevance = check_control_relevance(scenario)
        self.assertEqual(relevance, "MATCH")

        self.assertEqual(evaluate_direct(scenario), ("FAIL", "MATCH"))

    def test_unrelated_control_flagged_for_review(self):
        """A control unrelated to the named threat is flagged as REVIEW for human judgment."""
        scenario = SCENARIOS[2]
        completeness = check_scenario_completeness(scenario)
        self.assertEqual(completeness["status"], "PASS")

        relevance = check_control_relevance(scenario)
        self.assertEqual(relevance, "REVIEW")

        self.assertEqual(evaluate_direct(scenario), ("PASS", "REVIEW"))

    def test_missing_other_required_fields(self):
        """Ensure omitting threat, control, or residual_risk triggers FAIL."""
        for field in ["threat", "control", "residual_risk"]:
            incomplete = {"asset": "Server", "threat": "tampering", "control": "hash", "residual_risk": "low"}
            incomplete[field] = ""
            res = check_scenario_completeness(incomplete)
            self.assertEqual(res["status"], "FAIL")
            self.assertIn(field, res["missing_fields"])

    def test_both_approaches_agree_across_all_fixtures(self):
        """Verify that direct rule evaluation matches the independent reference table."""
        all_agreed, comparison_audit = compare_both_approaches(SCENARIOS)
        self.assertTrue(all_agreed)
        for rec in comparison_audit:
            self.assertTrue(rec["agreed"], f"Divergence in scenario {rec['id']}")
            self.assertEqual(rec["direct"], rec["reference"])

    def test_deliberate_corrupted_reference_fails_comparison(self):
        """Demonstrate that an intentional divergence between direct and reference fails comparison."""
        corrupted_scenarios = copy.deepcopy(SCENARIOS)
        corrupted_scenarios[0]["control"] = "completely irrelevant control action"
        # Direct will now evaluate to REVIEW while reference still expects MATCH
        all_agreed, comparison_audit = compare_both_approaches(corrupted_scenarios)
        self.assertFalse(all_agreed)
        self.assertFalse(comparison_audit[0]["agreed"])
        self.assertEqual(comparison_audit[0]["direct"], ("PASS", "REVIEW"))
        self.assertEqual(comparison_audit[0]["reference"], ("PASS", "MATCH"))

    def test_deliberate_wrong_assertion_raises_error(self):
        """Verify intentional wrong expectation raises an AssertionError."""
        actual = evaluate_direct(SCENARIOS[0])
        with self.assertRaises(AssertionError):
            self.assertEqual(actual, ("FAIL", "REVIEW"))


if __name__ == "__main__":
    unittest.main()
