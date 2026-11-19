"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t007 -p "test_*.py"
"""

import re
import unittest
from pathlib import Path

from example import OUTPUT_KEYS, WORKED_INPUT, analyze_text, explain

README = Path(__file__).with_name("README.md")


def readme_worked_example():
    """Extract the published worked-example lines from README.md."""
    text = README.read_text(encoding="utf-8")
    match = re.search(
        r"<!-- worked-example:start -->\s*```\n(.*?)\n```\s*<!-- worked-example:end -->",
        text,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("worked-example block not found in README.md")
    return match.group(1).splitlines()


class TaskContract(unittest.TestCase):
    def test_red_red_apple(self):
        self.assertEqual(analyze_text("red red apple"), {"word_count": 3, "unique_count": 2})

    def test_empty_text_returns_zeros(self):
        self.assertEqual(analyze_text(""), {"word_count": 0, "unique_count": 0})

    def test_non_string_is_rejected(self):
        for bad in (None, 3, ["red"], b"red"):
            with self.subTest(value=bad), self.assertRaises(TypeError):
                analyze_text(bad)


class WorkedExample(unittest.TestCase):
    def test_readme_worked_example_matches_code(self):
        # The published explanation is executed as a regression test.
        self.assertEqual(readme_worked_example(), explain(WORKED_INPUT))

    def test_worked_example_ends_with_the_real_output(self):
        last_line = explain(WORKED_INPUT)[-1]
        self.assertTrue(last_line.endswith(str(analyze_text(WORKED_INPUT))))

    def test_worked_example_has_six_steps(self):
        steps = explain(WORKED_INPUT)
        self.assertEqual([line.split(".")[0] for line in steps], ["1", "2", "3", "4", "5", "6"])


class OutputShape(unittest.TestCase):
    """What outputs="json" receives: exactly these keys, int values."""

    def test_output_keys_and_types(self):
        for text in ("red red apple", "", "a b a b c"):
            with self.subTest(text=text):
                result = analyze_text(text)
                self.assertEqual(tuple(result), OUTPUT_KEYS)
                for value in result.values():
                    self.assertIs(type(value), int)

    def test_unique_never_exceeds_total(self):
        for text in ("a", "a a a", "a b c", "  "):
            with self.subTest(text=text):
                result = analyze_text(text)
                self.assertLessEqual(result["unique_count"], result["word_count"])

    def test_whitespace_only_counts_as_empty(self):
        self.assertEqual(analyze_text(" \t\n"), {"word_count": 0, "unique_count": 0})

    def test_case_sensitive(self):
        self.assertEqual(analyze_text("Red red"), {"word_count": 2, "unique_count": 2})


if __name__ == "__main__":
    unittest.main()
