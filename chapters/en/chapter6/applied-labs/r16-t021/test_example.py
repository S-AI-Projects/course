#!/usr/bin/env python3
"""
Unit tests for Greedy Subword Segmentation Concept Example (R16-T021).

Verifies the contract of greedy longest-prefix subword segmentation as
used in WordPiece tokenizers, including normal, boundary, and failure cases.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

# Ensure current lab directory is on sys.path for direct script execution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (
    DEFAULT_CONTINUATION_PREFIX,
    DEFAULT_UNK_TOKEN,
    DEFAULT_VOCAB,
    main,
    segment_word,
    tokenize_text,
)


class TestGreedySubwordSegmentation(unittest.TestCase):
    """Test suite for greedy subword segmentation logic."""

    def test_required_fixture_normal_cases(self):
        """Test the exact required examples with the fixture vocabulary."""
        # playing -> ["play", "##ing"]
        self.assertEqual(segment_word("playing", DEFAULT_VOCAB), ["play", "##ing"])
        # cat -> ["cat"]
        self.assertEqual(segment_word("cat", DEFAULT_VOCAB), ["cat"])

    def test_required_fixture_unknown_cases(self):
        """Test completely unknown word."""
        # dog -> ["[UNK]"]
        self.assertEqual(segment_word("dog", DEFAULT_VOCAB), ["[UNK]"])

    def test_partial_match_failure(self):
        """
        Test words where a prefix matches but continuation subwords fail.

        WordPiece fails closed: if any subword is missing, the entire word
        is tokenized as [UNK], rather than leaving partially matched tokens.
        """
        # "play" is in vocab, but "##ed" is not -> entire word is [UNK]
        self.assertEqual(segment_word("played", DEFAULT_VOCAB), ["[UNK]"])

        # "cat" is in vocab, but "##s" is not -> entire word is [UNK]
        self.assertEqual(segment_word("cats", DEFAULT_VOCAB), ["[UNK]"])

        # "play" and "cat" are in vocab, but continuation requires "##cat"
        self.assertEqual(segment_word("playcat", DEFAULT_VOCAB), ["[UNK]"])

    def test_boundary_empty_string(self):
        """Empty string returns empty token list."""
        self.assertEqual(segment_word("", DEFAULT_VOCAB), [])

    def test_custom_vocabulary_and_markers(self):
        """Test segmentation with a custom vocabulary, continuation prefix, and unk token."""
        custom_vocab = {"hug", "##s", "b", "##u", "##gs"}
        # Greedy longest prefix: "hug" is matched first, then "##s"
        self.assertEqual(
            segment_word("hugs", vocab=custom_vocab),
            ["hug", "##s"],
        )
        # "bugs": matches "b", then "##u", then "##gs" -> ["b", "##u", "##gs"] if ##u and ##gs in vocab
        # Here "b" matches, "##ugs" not in vocab, "##u" matches, "##gs" matches
        self.assertEqual(
            segment_word("bugs", vocab=custom_vocab),
            ["b", "##u", "##gs"],
        )
        # Word with missing piece -> <unk>
        self.assertEqual(
            segment_word(
                "mug",
                vocab=custom_vocab,
                unk_token="<unk>",
                continuation_prefix="##",
            ),
            ["<unk>"],
        )

    def test_custom_continuation_prefix(self):
        """Test with an alternative prefix such as '@@'."""
        vocab = {"run", "@@ner"}
        self.assertEqual(
            segment_word("runner", vocab=vocab, continuation_prefix="@@"),
            ["run", "@@ner"],
        )

    def test_tokenize_text(self):
        """Test whitespace-separated text tokenization across multiple words."""
        text = "playing cat dog"
        expected = ["play", "##ing", "cat", "[UNK]"]
        self.assertEqual(tokenize_text(text, DEFAULT_VOCAB), expected)

    def test_main_cli_default(self):
        """Test main CLI entrypoint with default arguments."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main([])
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("'playing' -> ['play', '##ing']", output)
        self.assertIn("'cat' -> ['cat']", output)
        self.assertIn("'dog' -> ['[UNK]']", output)

    def test_main_cli_custom_args(self):
        """Test main CLI entrypoint with custom arguments."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["playing", "dog"])
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("'playing' -> ['play', '##ing']", output)
        self.assertIn("'dog' -> ['[UNK]']", output)
        self.assertNotIn("'cat' ->", output)


if __name__ == "__main__":
    unittest.main()
