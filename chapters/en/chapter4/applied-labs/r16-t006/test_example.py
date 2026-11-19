"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter4/applied-labs/r16-t006 -p "test_*.py"
"""

import itertools
import unittest

from example import (
    DECISION_TABLE,
    REQUIRED_FACTS,
    SCENARIOS,
    check_table,
    decide,
    decide_baseline,
    missing_facts,
)


class DecisionTable(unittest.TestCase):
    def test_three_scenarios_with_explicit_decisions(self):
        self.assertEqual(DECISION_TABLE, {
            "normal": "use",
            "boundary": "do-not-use",
            "missing-information": "need-more-info",
        })
        for scenario in SCENARIOS.values():
            self.assertTrue(scenario["rationale"].strip())

    def test_checker_passes_on_published_table(self):
        self.assertEqual(check_table(decide), [])

    def test_checker_fails_when_a_decision_is_changed(self):
        changed = {**DECISION_TABLE, "boundary": "use"}
        self.assertEqual(check_table(decide, table=changed), [("boundary", "use", "do-not-use")])

    def test_boundary_differs_from_normal_by_one_fact(self):
        normal = SCENARIOS["normal"]["facts"]
        boundary = SCENARIOS["boundary"]["facts"]
        differing = [k for k in REQUIRED_FACTS if normal[k] != boundary[k]]
        self.assertEqual(differing, ["requested_task"])


class Refactor(unittest.TestCase):
    def test_before_and_after_agree_on_fixture(self):
        self.assertEqual(check_table(decide_baseline), [])
        for sid, scenario in SCENARIOS.items():
            with self.subTest(scenario=sid):
                self.assertEqual(decide(scenario["facts"]), decide_baseline(scenario["facts"]))

    def test_before_and_after_agree_on_every_combination(self):
        values = {
            "checkpoint": ["camembert-base", None],
            "head_task": ["fill-mask", "text-classification", ""],
            "requested_task": ["fill-mask", "text-classification"],
            "model_language": ["fr", "en"],
            "text_language": ["fr", "en", None],
            "model_card": ["documented", None],
        }
        count = 0
        for combo in itertools.product(*values.values()):
            facts = dict(zip(values, combo))
            with self.subTest(facts=facts):
                self.assertEqual(decide(facts), decide_baseline(facts))
            count += 1
        self.assertEqual(count, 2 * 3 * 2 * 2 * 3 * 2)  # 144 combinations

    def test_extracted_responsibility_lists_missing_facts(self):
        facts = {**SCENARIOS["normal"]["facts"], "model_card": None, "text_language": ""}
        self.assertEqual(missing_facts(facts), ["text_language", "model_card"])
        self.assertEqual(missing_facts(SCENARIOS["normal"]["facts"]), [])

    def test_absent_key_counts_as_missing(self):
        self.assertEqual(missing_facts({}), list(REQUIRED_FACTS))
        self.assertEqual(decide({}), "need-more-info")


class Rules(unittest.TestCase):
    def test_language_mismatch_is_do_not_use(self):
        facts = {**SCENARIOS["normal"]["facts"], "text_language": "en"}
        self.assertEqual(decide(facts), "do-not-use")

    def test_missing_info_wins_over_mismatch(self):
        facts = {**SCENARIOS["boundary"]["facts"], "model_card": None}
        self.assertEqual(decide(facts), "need-more-info")


if __name__ == "__main__":
    unittest.main()
