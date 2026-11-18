#!/usr/bin/env python3
"""
Unit tests for Hugging Face Hub Integrations Worked Decision Example (R16-T025).

Verifies the normal, boundary, and missing-information scenarios,
validates the decision checker, and confirms that deliberate decision changes
trigger checker failures.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

# Ensure current lab directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (
    PUBLISHED_DECISION_TABLE,
    DecisionType,
    LocalDeterministicHubAdapter,
    ScenarioRecord,
    check_decision_table,
    main,
)


class TestHubIntegrationsDecisionExample(unittest.TestCase):
    """Test suite for the offline Hub integrations adapter and decision checker."""

    def setUp(self):
        self.adapter = LocalDeterministicHubAdapter()

    def test_normal_scenario_gpt_j_model(self):
        """
        Normal scenario:
        GPT-J-6B (6B params) on 4GB RAM machine -> LOAD_HUB_MODEL.
        Prefix: 'huggingface/EleutherAI/gpt-j-6B'.
        """
        facts = {
            "artifact_id": "EleutherAI/gpt-j-6B",
            "artifact_type": "model",
            "parameter_count": "6B",
            "local_ram_gb": 4,
            "network_online": True,
        }
        decision, prefix, rationale = self.adapter.evaluate(facts)
        self.assertEqual(decision, DecisionType.LOAD_HUB_MODEL)
        self.assertEqual(prefix, "huggingface/EleutherAI/gpt-j-6B")
        self.assertIn("Hugging Face Inference API", rationale)

    def test_boundary_scenario_space_app(self):
        """
        Boundary scenario:
        abidlabs/remove-bg full Space app -> LOAD_SPACES_APP.
        Prefix: 'spaces/abidlabs/remove-bg'.
        """
        facts = {
            "artifact_id": "abidlabs/remove-bg",
            "artifact_type": "space",
            "parameter_count": None,
            "local_ram_gb": 16,
            "custom_input": "webcam",
            "network_online": True,
        }
        decision, prefix, rationale = self.adapter.evaluate(facts)
        self.assertEqual(decision, DecisionType.LOAD_SPACES_APP)
        self.assertEqual(prefix, "spaces/abidlabs/remove-bg")
        self.assertIn("Spaces", rationale)

    def test_missing_information_scenario(self):
        """
        Missing-information scenario:
        Artifact type is None -> REJECT_INSUFFICIENT_INFORMATION.
        Prefix: None.
        """
        facts = {
            "artifact_id": "custom-org/unspecified-pkg",
            "artifact_type": None,
            "parameter_count": None,
            "local_ram_gb": 8,
            "network_online": True,
        }
        decision, prefix, rationale = self.adapter.evaluate(facts)
        self.assertEqual(decision, DecisionType.REJECT_INSUFFICIENT_INFORMATION)
        self.assertIsNone(prefix)
        self.assertIn("Missing essential artifact metadata", rationale)

    def test_checker_validates_published_table(self):
        """The checker passes completely on the standard published decision table."""
        report = check_decision_table(self.adapter, PUBLISHED_DECISION_TABLE)
        self.assertEqual(report["status"], "ALL_PASSED")
        self.assertEqual(len(report["results"]), 3)

    def test_checker_fails_on_deliberately_changed_decision(self):
        """
        Requirement: The checker MUST fail when a decision is deliberately changed.
        """
        # Mutate the expected decision of the normal scenario from LOAD_HUB_MODEL to LOAD_SPACES_APP
        tampered_table = [
            ScenarioRecord(
                name="normal",
                facts=PUBLISHED_DECISION_TABLE[0].facts,
                expected_decision=DecisionType.LOAD_SPACES_APP,  # DELIBERATE WRONG DECISION
                expected_prefix="spaces/EleutherAI/gpt-j-6B",
                rationale="Wrong decision for test",
            )
        ]

        with self.assertRaises(AssertionError) as ctx:
            check_decision_table(self.adapter, tampered_table)
        self.assertIn("Checker failure in scenario 'normal'", str(ctx.exception))

    def test_checker_fails_on_deliberately_changed_prefix(self):
        """The checker fails if expected prefix differs from actual."""
        tampered_table = [
            ScenarioRecord(
                name="normal",
                facts=PUBLISHED_DECISION_TABLE[0].facts,
                expected_decision=DecisionType.LOAD_HUB_MODEL,
                expected_prefix="huggingface/WRONG-PREFIX",  # DELIBERATE WRONG PREFIX
                rationale="Wrong prefix for test",
            )
        ]

        with self.assertRaises(AssertionError) as ctx:
            check_decision_table(self.adapter, tampered_table)
        self.assertIn("Checker failure in scenario 'normal'", str(ctx.exception))

    def test_unestablished_behaviors_documented(self):
        """Verify explicit list of real-service behaviors not established by mock."""
        behaviors = LocalDeterministicHubAdapter.UNESTABLISHED_BEHAVIORS
        self.assertIsInstance(behaviors, list)
        self.assertGreaterEqual(len(behaviors), 3)

    def test_cli_main_execution(self):
        """Verify CLI main entrypoint executes cleanly and produces expected output."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("Scenario: [NORMAL]", output)
        self.assertIn("Decision: LOAD_HUB_MODEL", output)
        self.assertIn("Scenario: [BOUNDARY]", output)
        self.assertIn("Decision: LOAD_SPACES_APP", output)
        self.assertIn("Scenario: [MISSING_INFORMATION]", output)
        self.assertIn("Decision: REJECT_INSUFFICIENT_INFORMATION", output)
        self.assertIn("Checker Status: ALL_PASSED", output)


if __name__ == "__main__":
    unittest.main()
