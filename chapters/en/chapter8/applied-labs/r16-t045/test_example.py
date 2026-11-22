"""Unit tests for Applied Lab R16-T045: Worked Decision Example and Offline Service Adapter."""

import copy
import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    PUBLISHED_DECISION_TABLE,
    ExternalServicePort,
    OfflineServiceAdapter,
    TriageDecisionResult,
    check_decision_table,
    evaluate_triage_decision,
)


class TestWorkedDecisionExampleR16T045(unittest.TestCase):
    """Test suite validating triage decision table, offline adapter contract, and error rejection."""

    def setUp(self):
        self.adapter = OfflineServiceAdapter()

    def test_published_table_checker_passes(self):
        """Checker passes on canonical three-scenario table."""
        ok, audit = check_decision_table(service_adapter=self.adapter)
        self.assertTrue(ok)
        self.assertEqual(len(audit), 3)
        for row in audit:
            self.assertEqual(row["status"], "PASS")
            self.assertTrue(row["decision_matches"])
            self.assertTrue(row["rationale_verified"])

    def test_normal_scenario_local_debug(self):
        """Normal scenario: local training error resolves to LOCAL_DEBUG."""
        facts = {
            "error_origin": "local_code",
            "has_minimal_repro": True,
            "is_upstream_library_bug": False,
        }
        res = evaluate_triage_decision("normal_test", facts, self.adapter)
        self.assertEqual(res.decision, "LOCAL_DEBUG")
        self.assertIn("debug your training pipeline", res.rationale)
        self.assertIsNotNone(res.service_response)
        self.assertEqual(res.service_response["status"], "ACCEPTED")

    def test_boundary_scenario_upstream_bug_reports_issue(self):
        """Boundary scenario: upstream library bug with repro resolves to LIBRARY_BUG_REPORT."""
        facts = {
            "error_origin": "transformers_core",
            "has_minimal_repro": True,
            "is_upstream_library_bug": True,
        }
        res = evaluate_triage_decision("boundary_test", facts, self.adapter)
        self.assertEqual(res.decision, "LIBRARY_BUG_REPORT")
        self.assertIn("write a good issue", res.rationale)
        self.assertEqual(res.service_response["destination"], "LIBRARY_BUG_REPORT")

    def test_missing_info_scenario_requests_clarification(self):
        """Missing information scenario: missing required keys resolves to REQUEST_MISSING_INFO."""
        facts = {
            "error_origin": None,
            "has_minimal_repro": None,
        }
        res = evaluate_triage_decision("missing_test", facts, self.adapter)
        self.assertEqual(res.decision, "REQUEST_MISSING_INFO")
        self.assertIn("Missing required triage facts", res.rationale)
        self.assertIsNone(res.service_response)

    def test_offline_adapter_records_dispatches(self):
        """Verify OfflineServiceAdapter accumulates payloads deterministically."""
        self.assertEqual(len(self.adapter.dispatched_payloads), 0)
        self.adapter.submit_report({"test": 123})
        self.assertEqual(len(self.adapter.dispatched_payloads), 1)
        self.assertEqual(self.adapter.dispatched_payloads[0], {"test": 123})

    def test_checker_fails_when_decision_deliberately_changed(self):
        """Checker must fail when a decision in the table is deliberately altered."""
        tampered_table = copy.deepcopy(PUBLISHED_DECISION_TABLE)
        tampered_table[0]["expected_decision"] = "COMMUNITY_FORUM"  # Altered from LOCAL_DEBUG

        ok, audit = check_decision_table(tampered_table, self.adapter)
        self.assertFalse(ok)
        self.assertEqual(audit[0]["status"], "FAIL")
        self.assertFalse(audit[0]["decision_matches"])

    def test_deliberate_wrong_result_makes_test_fail(self):
        """Deliberate wrong expectation triggers assertion failure."""
        res = evaluate_triage_decision("test", PUBLISHED_DECISION_TABLE[0]["facts"])
        wrong_expected = "WRONG_DECISION"
        with self.assertRaises(AssertionError):
            self.assertEqual(res.decision, wrong_expected)


if __name__ == "__main__":
    unittest.main()
