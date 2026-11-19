"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t004 -p "test_*.py"
"""

import unittest

from example import (
    MISMATCHED_CONTROL,
    MISSING_ASSET,
    REQUIRED_FIELDS,
    SCENARIOS,
    check_scenario,
)

STEPS = ["required_fields", "non_empty_text", "control_matches"]


def expected_verdict_from_trace(trace):
    """Independent reading of the trace: what verdict SHOULD it lead to?"""
    states = dict(trace)
    if states["required_fields"]["missing"]:
        return "fail"
    if states["non_empty_text"]["blank"]:
        return "fail"
    return "pass" if states["control_matches"]["matches"] else "review"


ALL_CASES = SCENARIOS + [
    MISSING_ASSET,
    MISMATCHED_CONTROL,
    {**SCENARIOS[2], "id": "S3-blank-residual", "residual_risk": "   "},
    {"id": "empty-answer"},
]


class TaskContract(unittest.TestCase):
    def test_complete_scenarios_pass(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario["id"]):
                self.assertEqual(check_scenario(scenario)["verdict"], "pass")

    def test_scenario_without_asset_fails(self):
        result = check_scenario(MISSING_ASSET)
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(dict(result["trace"])["required_fields"], {"missing": ["asset"]})

    def test_unrelated_control_is_flagged_for_review(self):
        result = check_scenario(MISMATCHED_CONTROL)
        self.assertEqual(result["verdict"], "review")
        state = dict(result["trace"])["control_matches"]
        self.assertEqual((state["threat_type"], state["addresses"]), ("data-exposure", "phishing"))

    def test_there_are_three_fictional_scenarios_with_all_fields(self):
        self.assertEqual(len(SCENARIOS), 3)
        for scenario in SCENARIOS:
            self.assertTrue(set(REQUIRED_FIELDS) <= set(scenario))


class TraceInvariant(unittest.TestCase):
    def test_every_step_is_recorded_in_order(self):
        for case in ALL_CASES:
            with self.subTest(case=case["id"]):
                steps = [name for name, _ in check_scenario(case)["trace"]]
                self.assertEqual(steps, STEPS)

    def test_verdict_matches_recorded_state(self):
        # The invariant: the final verdict follows from the recorded states.
        for case in ALL_CASES:
            with self.subTest(case=case["id"]):
                result = check_scenario(case)
                self.assertEqual(result["verdict"], expected_verdict_from_trace(result["trace"]))

    def test_steps_after_a_failure_are_skipped(self):
        trace = dict(check_scenario(MISSING_ASSET)["trace"])
        self.assertEqual(trace["non_empty_text"], "skipped")
        self.assertEqual(trace["control_matches"], "skipped")


class Boundaries(unittest.TestCase):
    def test_blank_text_field_fails(self):
        case = {**SCENARIOS[2], "residual_risk": "   "}
        result = check_scenario(case)
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(dict(result["trace"])["non_empty_text"], {"blank": ["residual_risk"]})

    def test_empty_answer_lists_every_missing_field(self):
        result = check_scenario({"id": "empty-answer"})
        self.assertEqual(dict(result["trace"])["required_fields"]["missing"], list(REQUIRED_FIELDS))

    def test_checker_does_not_judge_content(self):
        # Well formed but meaningless: the structural rubric still passes it.
        nonsense = {
            "id": "nonsense", "asset": "x", "threat": "y", "threat_type": "t",
            "control": "z", "addresses": "t", "residual_risk": "w",
        }
        self.assertEqual(check_scenario(nonsense)["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()
