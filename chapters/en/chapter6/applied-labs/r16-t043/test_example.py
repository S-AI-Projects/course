"""Unit tests for Applied Lab R16-T043: Token-to-Character Alignment."""

import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    TokenSpan,
    TokenSpanAlignment,
    build_dense_char_to_token_map,
    compare_alignment_approaches,
)


class TestTokenToCharacterAlignment(unittest.TestCase):
    """Test suite validating token-to-character alignment contract and approach comparison."""

    def setUp(self):
        self.text = "red apple"
        self.spans = [(0, 3), (4, 9)]
        self.aligner = TokenSpanAlignment(self.text, self.spans)

    def test_character_5_maps_to_token_1(self):
        """For 'red apple', spans [0,3],[4,9] map character 5 to token 1."""
        self.assertEqual(self.aligner.char_to_token(5), 1)
        self.assertEqual(self.text[5], "p")

    def test_separating_space_maps_to_no_token(self):
        """The separating space at index 3 maps to no token (None)."""
        self.assertIsNone(self.aligner.char_to_token(3))
        self.assertEqual(self.text[3], " ")

    def test_all_character_mappings_in_red_apple(self):
        """Verify full mapping for 'red apple':
        Indices 0, 1, 2 ('r','e','d') -> token 0
        Index 3 (' ') -> None
        Indices 4, 5, 6, 7, 8 ('a','p','p','l','e') -> token 1
        """
        for i in [0, 1, 2]:
            self.assertEqual(self.aligner.char_to_token(i), 0)
        self.assertIsNone(self.aligner.char_to_token(3))
        for i in [4, 5, 6, 7, 8]:
            self.assertEqual(self.aligner.char_to_token(i), 1)

    def test_out_of_bounds_character_indices(self):
        """Indices negative or beyond text length return None."""
        self.assertIsNone(self.aligner.char_to_token(-1))
        self.assertIsNone(self.aligner.char_to_token(9))
        self.assertIsNone(self.aligner.char_to_token(100))

    def test_compare_approaches_identical(self):
        """Direct implementation matches dense expected-result table calculation on identical inputs."""
        matched, details = compare_alignment_approaches(self.text, self.spans)
        self.assertTrue(matched)
        self.assertTrue(details["all_matched"])

    def test_compare_approaches_on_multi_token_sentence(self):
        """Compare approaches on multi-token sentence with leading/trailing spaces."""
        text = "  quick brown fox  "
        spans = [(2, 7), (8, 13), (14, 17)]
        matched, _ = compare_alignment_approaches(text, spans)
        self.assertTrue(matched)

    def test_validation_rejects_overlapping_spans(self):
        """Overlapping spans must raise ValueError."""
        with self.assertRaises(ValueError):
            TokenSpanAlignment("hello world", [(0, 6), (5, 11)])

    def test_validation_rejects_invalid_span_bounds(self):
        """Invalid spans (start >= end or out of bounds) raise ValueError."""
        with self.assertRaises(ValueError):
            TokenSpanAlignment("hello", [(3, 2)])
        with self.assertRaises(ValueError):
            TokenSpanAlignment("hello", [(0, 10)])

    def test_deliberate_wrong_result_fails(self):
        """Demonstrate that an intentional wrong result makes test fail."""
        actual_token = self.aligner.char_to_token(5)
        wrong_expected = 0  # Character 5 ('p') is in token 1, not 0
        with self.assertRaises(AssertionError):
            self.assertEqual(actual_token, wrong_expected)


if __name__ == "__main__":
    unittest.main()
