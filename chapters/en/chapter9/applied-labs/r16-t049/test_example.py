"""Unit tests for Applied Lab R16-T049: UI Callback Contract and Evaluation Experiment."""

import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    analyze_text,
    evaluate_input_configurations,
    text_analysis_callback,
)


class TestUICallbackContractR16T049(unittest.TestCase):
    """Test suite validating UI callback contract and evaluation experiment."""

    def test_normal_input_red_red_apple(self):
        """Input 'red red apple' returns word_count=3 and unique_count=2."""
        res = analyze_text("red red apple")
        self.assertEqual(res, {"word_count": 3, "unique_count": 2})
        self.assertEqual(res["word_count"], 3)
        self.assertEqual(res["unique_count"], 2)

    def test_empty_text_returns_zeros(self):
        """Empty text returns zeros."""
        res = analyze_text("")
        self.assertEqual(res, {"word_count": 0, "unique_count": 0})

    def test_whitespace_only_returns_zeros(self):
        """Whitespace string returns zeros."""
        res = analyze_text("   \n\t  ")
        self.assertEqual(res, {"word_count": 0, "unique_count": 0})

    def test_nonstring_input_rejected_none(self):
        """Non-string None input is rejected with TypeError."""
        with self.assertRaises(TypeError):
            analyze_text(None)

    def test_nonstring_input_rejected_types(self):
        """Non-string int, list, dict inputs rejected with TypeError."""
        with self.assertRaises(TypeError):
            analyze_text(123)
        with self.assertRaises(TypeError):
            analyze_text(["red", "apple"])
        with self.assertRaises(TypeError):
            analyze_text({"text": "red apple"})

    def test_callback_alias_identical(self):
        """text_analysis_callback behaves identically to analyze_text."""
        self.assertEqual(
            text_analysis_callback("red red apple"),
            {"word_count": 3, "unique_count": 2},
        )

    def test_evaluation_experiment_compares_three_configurations(self):
        """Verify experiment evaluates three controlled input sizes with metrics."""
        results = evaluate_input_configurations()
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertTrue(r["is_correct"])
            self.assertGreater(r["word_count"], 0)
            self.assertGreater(r["unique_count"], 0)
            self.assertGreaterEqual(r["uniqueness_ratio"], 0.0)
            self.assertLessEqual(r["uniqueness_ratio"], 1.0)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrate that an intentional wrong result makes test fail."""
        actual = analyze_text("red red apple")
        wrong_expected = {"word_count": 999, "unique_count": 999}
        with self.assertRaises(AssertionError):
            self.assertEqual(actual, wrong_expected)


if __name__ == "__main__":
    unittest.main()
