"""Unit tests for Applied Lab R16-T011 text analysis callback contract."""

import os
import sys
import unittest

# Ensure the lab module directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from example import analyze_text, text_analysis_callback


class TestTextAnalysisCallback(unittest.TestCase):
    """Test suite validating UI callback contract and schema."""

    def test_normal_input_red_red_apple(self):
        """Input 'red red apple' returns word_count=3 and unique_count=2."""
        result = analyze_text("red red apple")
        self.assertEqual(result, {"word_count": 3, "unique_count": 2})
        self.assertEqual(result["word_count"], 3)
        self.assertEqual(result["unique_count"], 2)

    def test_empty_string_returns_zeros(self):
        """Empty text returns zeros."""
        result = analyze_text("")
        self.assertEqual(result, {"word_count": 0, "unique_count": 0})
        self.assertEqual(result["word_count"], 0)
        self.assertEqual(result["unique_count"], 0)

    def test_whitespace_string_returns_zeros(self):
        """Whitespace-only string returns zeros."""
        result = analyze_text("   \n\t  ")
        self.assertEqual(result, {"word_count": 0, "unique_count": 0})

    def test_nonstring_input_rejected_none(self):
        """Non-string None input is rejected with TypeError."""
        with self.assertRaises(TypeError):
            analyze_text(None)

    def test_nonstring_input_rejected_number(self):
        """Non-string integer/float input is rejected with TypeError."""
        with self.assertRaises(TypeError):
            analyze_text(123)
        with self.assertRaises(TypeError):
            analyze_text(3.14)

    def test_nonstring_input_rejected_collection(self):
        """Non-string list/dict input is rejected with TypeError."""
        with self.assertRaises(TypeError):
            analyze_text(["red", "red", "apple"])
        with self.assertRaises(TypeError):
            analyze_text({"text": "red red apple"})

    def test_output_schema_keys_and_types(self):
        """Ensure schema keys are exactly 'word_count' and 'unique_count' (int)."""
        result = analyze_text("hello world")
        self.assertIsInstance(result, dict)
        self.assertEqual(set(result.keys()), {"word_count", "unique_count"})
        self.assertIsInstance(result["word_count"], int)
        self.assertIsInstance(result["unique_count"], int)

    def test_callback_alias(self):
        """Verify text_analysis_callback alias behaves identically."""
        self.assertEqual(
            text_analysis_callback("red red apple"),
            {"word_count": 3, "unique_count": 2},
        )

    def test_deliberate_wrong_result_fails(self):
        """Demonstrate that an intentional incorrect expectation triggers an assertion failure."""
        actual = analyze_text("red red apple")
        wrong_expected = {"word_count": 99, "unique_count": 99}
        with self.assertRaises(AssertionError):
            self.assertEqual(actual, wrong_expected)


if __name__ == "__main__":
    unittest.main()
