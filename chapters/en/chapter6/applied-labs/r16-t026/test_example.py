#!/usr/bin/env python3
"""
Unit tests for Normalization with Offsets Refactoring Lab (R16-T026).

Verifies the standard contract, baseline vs. refactored equivalence,
slice recovery invariant, and boundary handling.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

# Ensure current lab directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (
    WhitespaceSpanScanner,
    baseline_tokenize_with_offsets,
    main,
    prove_equivalence,
    recover_words_from_slices,
    refactored_tokenize_with_offsets,
)


class TestNormalizationWithOffsets(unittest.TestCase):
    """Test suite for tokenization with character offsets and refactoring equivalence."""

    def test_required_contract_fixture(self):
        """
        Verify the core contract:
        '  red   apple ' yields 'red' at [2, 5) and 'apple' at [8, 13),
        and slices recover the original words.
        """
        text = "  red   apple "
        expected = [("red", (2, 5)), ("apple", (8, 13))]

        # 1. Test baseline implementation
        baseline_result = baseline_tokenize_with_offsets(text)
        self.assertEqual(baseline_result, expected)

        # 2. Test refactored implementation
        refactored_result = refactored_tokenize_with_offsets(text)
        self.assertEqual(refactored_result, expected)

        # 3. Test slice recovery invariant
        self.assertEqual(text[2:5], "red")
        self.assertEqual(text[8:13], "apple")

        recovered = recover_words_from_slices(text, refactored_result)
        self.assertEqual(recovered, ["red", "apple"])

    def test_baseline_refactored_equivalence(self):
        """Prove before/after equivalence on the standard fixture and additional strings."""
        test_strings = [
            "  red   apple ",
            "simple text without extra space",
            "   leading space",
            "trailing space   ",
            "   multiple   spaces   everywhere   ",
            "",
            "   ",
            "\n\t mixed \t whitespace \n",
        ]
        for s in test_strings:
            with self.subTest(text=repr(s)):
                self.assertTrue(prove_equivalence(s))
                self.assertEqual(
                    baseline_tokenize_with_offsets(s),
                    refactored_tokenize_with_offsets(s),
                )

    def test_extracted_scanner_spans(self):
        """Verify the extracted WhitespaceSpanScanner responsibility independently."""
        text = "  red   apple "
        spans = WhitespaceSpanScanner.scan_spans(text)
        self.assertEqual(spans, [(2, 5), (8, 13)])

    def test_boundary_empty_and_whitespace_only(self):
        """Verify handling of empty strings and whitespace-only strings."""
        self.assertEqual(refactored_tokenize_with_offsets(""), [])
        self.assertEqual(refactored_tokenize_with_offsets("      "), [])
        self.assertEqual(refactored_tokenize_with_offsets("\t\n\r  "), [])

    def test_boundary_single_word(self):
        """Verify single word with and without padding."""
        self.assertEqual(
            refactored_tokenize_with_offsets("hello"),
            [("hello", (0, 5))],
        )
        self.assertEqual(
            refactored_tokenize_with_offsets("   hello   "),
            [("hello", (3, 8))],
        )

    def test_slice_recovery_invariant_universality(self):
        """Ensure slice recovery invariant text[start:end] == token holds on all outputs."""
        sample = " The quick brown fox jumps over the lazy dog "
        tokens = refactored_tokenize_with_offsets(sample)
        for token, (start, end) in tokens:
            self.assertEqual(sample[start:end], token)

    def test_deliberate_wrong_result_fails(self):
        """Deliberate wrong expected result triggers failure."""
        text = "  red   apple "
        wrong_expected = [("red", (0, 3)), ("apple", (5, 10))]
        actual = refactored_tokenize_with_offsets(text)
        self.assertNotEqual(actual, wrong_expected)

    def test_cli_main_execution(self):
        """Verify CLI main entrypoint executes cleanly and produces expected text."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("token: 'red'    span: [2, 5)", output)
        self.assertIn("token: 'apple'  span: [8, 13)", output)
        self.assertIn("Equivalence Check: PASSED", output)
        self.assertIn("Slice Recovery Invariant: PASSED", output)


if __name__ == "__main__":
    unittest.main()
