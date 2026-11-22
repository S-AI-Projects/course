"""Unit tests for Applied Lab R16-T044: Worked Decision Example and State Trace."""

import copy
import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    PUBLISHED_DECISION_TABLE,
    DecisionResult,
    StepTrace,
    check_decision_table,
    evaluate_dataset_strategy,
)


class TestWorkedDecisionExample(unittest.TestCase):
    """Test suite validating decision outcomes, state traces, and table checker invariants."""

    def test_published_table_checker_passes(self):
        """Checker for published decision table passes for all three canonical scenarios."""
        ok, audit = check_decision_table()
        self.assertTrue(ok)
        self.assertEqual(len(audit), 3)
        for row in audit:
            self.assertEqual(row["status"], "PASS")
            self.assertTrue(row["decision_matches"])
            self.assertTrue(row["invariants_held"])
            self.assertTrue(row["rationale_verified"])

    def test_normal_scenario_state_trace_and_decision(self):
        """Normal scenario: small hub dataset resolves to HUB_IN_MEMORY with 4 steps."""
        facts = {
            "dataset_source": "hub",
            "dataset_name": "rotten_tomatoes",
            "size_gb": 0.5,
            "available_ram_gb": 16,
            "file_format": "parquet",
        }
        res = evaluate_dataset_strategy("normal_test", facts)
        self.assertEqual(res.decision, "HUB_IN_MEMORY")
        self.assertEqual(len(res.state_trace), 4)
        self.assertEqual(len(res.invariant_violations), 0)

        # Validate step invariants
        for idx, step in enumerate(res.state_trace, start=1):
            self.assertEqual(step.step_number, idx)
        self.assertEqual(res.state_trace[-1].current_decision, "HUB_IN_MEMORY")

    def test_boundary_scenario_huge_dataset_streams(self):
        """Boundary scenario: huge dataset (825 GB >= 16 GB RAM) resolves to STREAM_FROM_DISK_OR_URL."""
        facts = {
            "dataset_source": "hub",
            "dataset_name": "the_pile",
            "size_gb": 825.0,
            "available_ram_gb": 16,
            "file_format": "jsonl",
        }
        res = evaluate_dataset_strategy("boundary_test", facts)
        self.assertEqual(res.decision, "STREAM_FROM_DISK_OR_URL")
        self.assertIn("streaming", res.rationale.lower())
        self.assertEqual(len(res.invariant_violations), 0)
        self.assertEqual(res.state_trace[-1].current_decision, "STREAM_FROM_DISK_OR_URL")

    def test_missing_information_scenario_halts_early(self):
        """Missing information scenario: missing size_gb resolves to REQUEST_MISSING_INFO at step 1."""
        facts = {
            "dataset_source": "local",
            "size_gb": None,
            "file_format": "csv",
        }
        res = evaluate_dataset_strategy("missing_info_test", facts)
        self.assertEqual(res.decision, "REQUEST_MISSING_INFO")
        self.assertEqual(len(res.state_trace), 1)
        self.assertEqual(res.state_trace[0].step_number, 1)
        self.assertTrue(res.state_trace[0].decision_resolved)
        self.assertEqual(len(res.invariant_violations), 0)

    def test_checker_fails_when_decision_deliberately_changed(self):
        """Checker must fail when a decision in the table is deliberately altered."""
        corrupted_table = copy.deepcopy(PUBLISHED_DECISION_TABLE)
        # Deliberately change expected decision of normal scenario to STREAM
        corrupted_table[0]["expected_decision"] = "STREAM_FROM_DISK_OR_URL"

        ok, audit = check_decision_table(corrupted_table)
        self.assertFalse(ok)
        self.assertEqual(audit[0]["status"], "FAIL")
        self.assertFalse(audit[0]["decision_matches"])

    def test_deliberate_wrong_result_makes_test_fail(self):
        """Deliberate wrong expectation triggers assertion failure."""
        res = evaluate_dataset_strategy("test", PUBLISHED_DECISION_TABLE[0]["facts"])
        wrong_expected_decision = "WRONG_DECISION"
        with self.assertRaises(AssertionError):
            self.assertEqual(res.decision, wrong_expected_decision)


if __name__ == "__main__":
    unittest.main()
