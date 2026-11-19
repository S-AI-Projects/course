"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t010 -p "test_*.py"
"""

import unittest

from example import QUESTIONS, preflight, tokenize


class TaskContract(unittest.TestCase):
    def test_budget_three_keeps_first_three_and_removes_one(self):
        result = preflight("one two three four", 3)
        self.assertEqual(result["retained"], ["one", "two", "three"])
        self.assertEqual(result["removed_count"], 1)
        self.assertTrue(result["truncated"])

    def test_empty_input_retains_none(self):
        result = preflight("", 3)
        self.assertEqual(result["retained"], [])
        self.assertEqual(result["removed_count"], 0)
        self.assertFalse(result["truncated"])

    def test_negative_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            preflight("one two", -1)

    def test_tokenizer_is_whitespace_split(self):
        self.assertEqual(tokenize("  one\ttwo\nthree "), ["one", "two", "three"])


class AppliedQuestions(unittest.TestCase):
    """One executable check per factual answer in QUESTIONS."""

    def test_three_questions_of_the_required_kinds(self):
        kinds = [q["kind"] for q in QUESTIONS]
        self.assertEqual(kinds, ["predict an output", "diagnose a failure", "choose a boundary policy"])
        for q in QUESTIONS:
            self.assertTrue(q["rationale"].strip())

    def test_q1_predict_output(self):
        result = preflight("a b c", 2)
        self.assertEqual(result["retained"], ["a", "b"])
        self.assertEqual(result["removed_count"], 1)
        self.assertTrue(result["truncated"])

    def test_q2_diagnose_failure(self):
        with self.assertRaises(TypeError) as ctx:
            preflight(["one", "two"], 3)
        self.assertEqual(str(ctx.exception), "prompt must be a str, got list")
        # The documented fix works.
        fixed = preflight(" ".join(["one", "two"]), 3)
        self.assertEqual(fixed["retained"], ["one", "two"])

    def test_q3_boundary_policy_exactly_at_budget_fits(self):
        result = preflight("one two three four", 4)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["removed_count"], 0)


class MoreBoundaries(unittest.TestCase):
    def test_zero_budget_removes_everything(self):
        result = preflight("one two", 0)
        self.assertEqual(result["retained"], [])
        self.assertEqual(result["removed_count"], 2)

    def test_one_over_budget_removes_one(self):
        self.assertEqual(preflight("one two three four five", 4)["removed_count"], 1)

    def test_non_int_budget_is_rejected(self):
        for bad in (3.0, "3", True, None):
            with self.subTest(budget=bad), self.assertRaises(TypeError):
                preflight("one two", bad)


if __name__ == "__main__":
    unittest.main()
