"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t005 -p "test_*.py"
"""

import unittest

from example import OUTPUT_SCHEMA, analyze_text, local_tokenize, validate_output


class TaskContract(unittest.TestCase):
    def test_red_red_apple(self):
        self.assertEqual(analyze_text("red red apple"), {"word_count": 3, "unique_count": 2})

    def test_empty_text_returns_zeros(self):
        self.assertEqual(analyze_text(""), {"word_count": 0, "unique_count": 0})

    def test_non_string_is_rejected(self):
        for bad in (42, None, ["red", "apple"], b"red apple"):
            with self.subTest(value=bad), self.assertRaises(TypeError):
                analyze_text(bad)


class ServiceAdapter(unittest.TestCase):
    def test_default_service_is_the_local_adapter(self):
        self.assertEqual(
            analyze_text("red red apple"),
            analyze_text("red red apple", tokenize=local_tokenize),
        )

    def test_local_adapter_is_deterministic(self):
        results = {tuple(local_tokenize("red red apple")) for _ in range(5)}
        self.assertEqual(results, {("red", "red", "apple")})

    def test_any_callable_can_be_plugged_in(self):
        calls = []

        def recording_service(text):
            calls.append(text)
            return ["fixed", "fixed"]

        self.assertEqual(analyze_text("anything", tokenize=recording_service),
                         {"word_count": 2, "unique_count": 1})
        self.assertEqual(calls, ["anything"])

    def test_service_returning_wrong_type_is_caught(self):
        with self.assertRaises(TypeError):
            analyze_text("red apple", tokenize=lambda text: "red apple")

    def test_whitespace_only_is_empty(self):
        self.assertEqual(analyze_text("  \t\n "), {"word_count": 0, "unique_count": 0})

    def test_counting_is_case_sensitive(self):
        self.assertEqual(analyze_text("Red red"), {"word_count": 2, "unique_count": 2})


class OutputSchema(unittest.TestCase):
    def test_schema_keys(self):
        self.assertEqual(set(OUTPUT_SCHEMA), {"word_count", "unique_count"})

    def test_valid_output_passes(self):
        validate_output({"word_count": 3, "unique_count": 2})

    def test_invalid_outputs_are_rejected(self):
        bad_outputs = [
            {"word_count": 3},                                  # missing key
            {"word_count": 3, "unique_count": 2, "extra": 1},   # extra key
            {"word_count": "3", "unique_count": 2},             # wrong type
            {"word_count": 3, "unique_count": True},            # bool is not a count
            {"word_count": -1, "unique_count": 0},              # negative
            {"word_count": 2, "unique_count": 3},               # unique > total
            [3, 2],                                             # not a dict
        ]
        for bad in bad_outputs:
            with self.subTest(output=bad), self.assertRaises(ValueError):
                validate_output(bad)


if __name__ == "__main__":
    unittest.main()
