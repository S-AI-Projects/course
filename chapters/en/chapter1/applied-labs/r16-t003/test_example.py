"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t003 -p "test_*.py"
"""

import itertools
import unittest

from example import EXPECTED_TABLE, preflight, reference_preflight, tokenize


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
        with self.assertRaises(ValueError):
            reference_preflight("one two", -1)


class CompareApproaches(unittest.TestCase):
    def test_direct_matches_expected_table(self):
        for prompt, budget, retained, removed, truncated in EXPECTED_TABLE:
            with self.subTest(prompt=prompt, budget=budget):
                result = preflight(prompt, budget)
                self.assertEqual(result["retained"], retained)
                self.assertEqual(result["removed_count"], removed)
                self.assertEqual(result["truncated"], truncated)

    def test_reference_matches_expected_table(self):
        for prompt, budget, retained, removed, truncated in EXPECTED_TABLE:
            with self.subTest(prompt=prompt, budget=budget):
                result = reference_preflight(prompt, budget)
                self.assertEqual(result["retained"], retained)
                self.assertEqual(result["removed_count"], removed)
                self.assertEqual(result["truncated"], truncated)

    def test_direct_and_reference_agree_on_a_grid(self):
        words = ["a", "b", "c", "d", "e"]
        for length, budget in itertools.product(range(6), range(7)):
            prompt = " ".join(words[:length])
            with self.subTest(length=length, budget=budget):
                self.assertEqual(preflight(prompt, budget), reference_preflight(prompt, budget))


class Boundaries(unittest.TestCase):
    def test_exactly_at_budget_is_not_truncated(self):
        self.assertFalse(preflight("one two three", 3)["truncated"])

    def test_zero_budget_removes_everything(self):
        result = preflight("one two", 0)
        self.assertEqual(result["retained"], [])
        self.assertEqual(result["removed_count"], 2)

    def test_retained_plus_removed_equals_token_count(self):
        for prompt, budget, *_ in EXPECTED_TABLE:
            with self.subTest(prompt=prompt, budget=budget):
                r = preflight(prompt, budget)
                self.assertEqual(len(r["retained"]) + r["removed_count"], r["token_count"])

    def test_tokenizer_is_whitespace_split(self):
        self.assertEqual(tokenize("  hello\tworld\n"), ["hello", "world"])


class InvalidInput(unittest.TestCase):
    def test_non_string_prompt_is_rejected(self):
        with self.assertRaises(TypeError):
            preflight(["one", "two"], 3)

    def test_non_int_budget_is_rejected(self):
        for bad in (3.0, "3", True, None):
            with self.subTest(budget=bad), self.assertRaises(TypeError):
                preflight("one two", bad)


if __name__ == "__main__":
    unittest.main()
