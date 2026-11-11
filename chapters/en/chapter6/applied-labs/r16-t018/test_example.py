"""Unit tests for WordPiece Subword Segmentation (Task R16-T018).

Verifies the greedy longest-prefix tokenization contract, failure and recovery,
boundary cases, and deliberate failure detection.
"""

import os
import sys
import unittest

# Ensure the lab directory is on sys.path
LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    DEFAULT_VOCAB,
    UNK_TOKEN,
    TokenizationResult,
    WordPieceTokenizer,
)


class TestRequiredContract(unittest.TestCase):
    """Core acceptance tests specified by Issue #21 'Done when' checklist."""

    def setUp(self):
        self.tokenizer = WordPieceTokenizer()

    def test_playing_segmented_to_play_and_continuation_ing(self):
        """Vocabulary {play,##ing,cat}: playing -> ['play', '##ing']."""
        tokens = self.tokenizer.encode_word("playing")
        self.assertEqual(tokens, ["play", "##ing"])

    def test_cat_segmented_to_cat(self):
        """Vocabulary {play,##ing,cat}: cat -> ['cat']."""
        tokens = self.tokenizer.encode_word("cat")
        self.assertEqual(tokens, ["cat"])

    def test_dog_segmented_to_unk(self):
        """Vocabulary {play,##ing,cat}: dog -> ['[UNK]']."""
        tokens = self.tokenizer.encode_word("dog")
        self.assertEqual(tokens, ["[UNK]"])


class TestFailureAndRecovery(unittest.TestCase):
    """Focus: Exercise documented invalid/missing-data cases, explain error,

    and demonstrate recovery on next valid input.
    """

    def setUp(self):
        self.tokenizer = WordPieceTokenizer()

    def test_none_input_failure_and_explanation(self):
        """None input produces a documented ERROR result with explanation."""
        res = self.tokenizer.tokenize_safe(None)
        self.assertEqual(res.status, "ERROR")
        self.assertIsNone(res.tokens)
        self.assertIn("Missing data", res.error_message)

    def test_invalid_type_failure_and_explanation(self):
        """Non-string inputs produce documented ERROR results explaining expected type."""
        for invalid in [123, 45.67, ["list"], {"key": "val"}]:
            with self.subTest(invalid=invalid):
                res = self.tokenizer.tokenize_safe(invalid)
                self.assertEqual(res.status, "ERROR")
                self.assertIsNone(res.tokens)
                self.assertIn("Invalid input type", res.error_message)

    def test_stream_failure_and_recovery(self):
        """Stream processing isolates failures and recovers immediately on the next valid item."""
        stream = ["cat", None, "playing", 9999, "dog"]
        results = self.tokenizer.tokenize_stream(stream)

        self.assertEqual(len(results), 5)

        # 1. First valid input succeeds
        self.assertEqual(results[0].status, "SUCCESS")
        self.assertEqual(results[0].tokens, ["cat"])

        # 2. Missing-data failure captured
        self.assertEqual(results[1].status, "ERROR")
        self.assertIn("Missing data", results[1].error_message)

        # 3. Next valid input recovers seamlessly
        self.assertEqual(results[2].status, "SUCCESS")
        self.assertEqual(results[2].tokens, ["play", "##ing"])

        # 4. Invalid-type failure captured
        self.assertEqual(results[3].status, "ERROR")
        self.assertIn("Invalid input type", results[3].error_message)

        # 5. Next valid input recovers seamlessly
        self.assertEqual(results[4].status, "SUCCESS")
        self.assertEqual(results[4].tokens, ["[UNK]"])

    def test_direct_exceptions_raised(self):
        """Calling encode_word or tokenize_text directly raises standard exceptions."""
        with self.assertRaises(TypeError):
            self.tokenizer.encode_word(None)
        with self.assertRaises(TypeError):
            self.tokenizer.tokenize_text(123)

    def test_empty_vocabulary_rejected(self):
        """Initializing with an empty vocabulary raises ValueError."""
        with self.assertRaises(ValueError):
            WordPieceTokenizer(vocab=set())


class TestBoundaryAndEdgeCases(unittest.TestCase):
    """Boundary conditions and WordPiece segmentation edge cases."""

    def setUp(self):
        self.tokenizer = WordPieceTokenizer()

    def test_empty_string(self):
        """Empty string returns empty token list."""
        self.assertEqual(self.tokenizer.encode_word(""), [])
        self.assertEqual(self.tokenizer.tokenize_text(""), [])

    def test_whitespace_only(self):
        """Whitespace-only string returns empty token list."""
        self.assertEqual(self.tokenizer.tokenize_text("   \n\t  "), [])

    def test_multi_word_text_tokenization(self):
        """Tokenize sentence composed of words matching contract."""
        tokens = self.tokenizer.tokenize_text("playing cat dog")
        self.assertEqual(tokens, ["play", "##ing", "cat", "[UNK]"])

    def test_partial_match_whole_word_unk(self):
        """In WordPiece, if any continuation fails, the whole word becomes [UNK]."""
        # 'cats': 'cat' is in vocab, but '##s' is not. Whole word becomes ['[UNK]'].
        tokens = self.tokenizer.encode_word("cats")
        self.assertEqual(tokens, ["[UNK]"])


class TestDeliberateFailure(unittest.TestCase):
    """Contribution Focus: Proves a deliberate wrong result makes the test fail."""

    def test_wrong_token_assertion_fails(self):
        """Injecting an incorrect token list triggers an assertion failure."""
        tokenizer = WordPieceTokenizer()
        actual = tokenizer.encode_word("playing")

        corrupted = ["play", "WRONG_TOKEN"]

        with self.assertRaises(AssertionError):
            self.assertEqual(actual, corrupted)

    def test_wrong_unk_fallback_fails(self):
        """Asserting out-of-vocabulary word does not return [UNK] fails."""
        tokenizer = WordPieceTokenizer()
        actual = tokenizer.encode_word("dog")

        with self.assertRaises(AssertionError):
            self.assertEqual(actual, ["dog"])


if __name__ == "__main__":
    unittest.main()
