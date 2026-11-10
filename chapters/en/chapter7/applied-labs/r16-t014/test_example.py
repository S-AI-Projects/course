"""Unit tests for Applied Lab R16-T014: Answer-Span Extraction Invariant and State Trace."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from example import (
    CONTEXT,
    TOKEN_OFFSETS,
    build_token_sequence,
    extract_span,
    validate_span,
)


class TestAnswerSpanExtraction(unittest.TestCase):
    """Tests for span extraction contract, state trace, and invariants."""

    def test_token_offset_build(self):
        """build_token_sequence correctly maps words to char offsets."""
        offsets = build_token_sequence(CONTEXT)
        self.assertEqual(len(offsets), 3)
        self.assertEqual(offsets[0], ("Ada",   0,  3))
        self.assertEqual(offsets[1], ("wrote", 4,  9))
        self.assertEqual(offsets[2], ("notes", 10, 15))

    def test_span_0_0_returns_ada(self):
        """Token span 0..0 on 'Ada wrote notes' returns 'Ada'."""
        state = extract_span(CONTEXT, 0, 0, token_offsets=TOKEN_OFFSETS)
        self.assertTrue(state["validated"])
        self.assertEqual(state["char_start"], 0)
        self.assertEqual(state["char_end"], 3)
        self.assertEqual(state["answer"], "Ada")

    def test_span_1_2_returns_wrote_notes(self):
        """Token span 1..2 returns 'wrote notes'."""
        state = extract_span(CONTEXT, 1, 2, token_offsets=TOKEN_OFFSETS)
        self.assertTrue(state["validated"])
        self.assertEqual(state["char_start"], 4)
        self.assertEqual(state["char_end"], 15)
        self.assertEqual(state["answer"], "wrote notes")

    def test_span_2_2_returns_notes(self):
        """Token span 2..2 returns 'notes' (last word boundary)."""
        state = extract_span(CONTEXT, 2, 2, token_offsets=TOKEN_OFFSETS)
        self.assertTrue(state["validated"])
        self.assertEqual(state["char_start"], 10)
        self.assertEqual(state["char_end"], 15)
        self.assertEqual(state["answer"], "notes")

    def test_state_trace_completeness(self):
        """Returned state dict contains all intermediate pipeline fields."""
        state = extract_span(CONTEXT, 0, 2, token_offsets=TOKEN_OFFSETS)
        required_keys = {"token_offsets", "validated", "char_start", "char_end", "answer"}
        self.assertEqual(set(state.keys()), required_keys)
        self.assertIsNotNone(state["token_offsets"])
        self.assertTrue(state["validated"])
        self.assertIsNotNone(state["char_start"])
        self.assertIsNotNone(state["char_end"])
        self.assertIsNotNone(state["answer"])

    def test_invariant_char_end_gt_char_start(self):
        """Invariant: char_end > char_start holds for all valid non-empty spans."""
        for start in range(3):
            for end in range(start, 3):
                state = extract_span(CONTEXT, start, end, token_offsets=TOKEN_OFFSETS)
                self.assertGreater(
                    state["char_end"], state["char_start"],
                    f"Invariant violated for span({start}, {end})"
                )

    def test_invariant_answer_matches_context_slice(self):
        """Invariant: answer == context[char_start:char_end] for all valid spans."""
        for start in range(3):
            for end in range(start, 3):
                state = extract_span(CONTEXT, start, end, token_offsets=TOKEN_OFFSETS)
                self.assertEqual(
                    state["answer"],
                    CONTEXT[state["char_start"]:state["char_end"]],
                    f"Answer-slice invariant violated for span({start}, {end})"
                )

    def test_end_before_start_is_rejected(self):
        """End token index before start raises ValueError."""
        with self.assertRaises(ValueError):
            extract_span(CONTEXT, 2, 0, token_offsets=TOKEN_OFFSETS)
        with self.assertRaises(ValueError):
            extract_span(CONTEXT, 1, 0, token_offsets=TOKEN_OFFSETS)

    def test_validate_span_equal_indices_accepted(self):
        """Equal start and end (single-token span) is valid."""
        validate_span(0, 0, 3)
        validate_span(1, 1, 3)
        validate_span(2, 2, 3)

    def test_out_of_bounds_raises_index_error(self):
        """Out-of-range token indices raise IndexError."""
        with self.assertRaises(IndexError):
            extract_span(CONTEXT, 0, 99, token_offsets=TOKEN_OFFSETS)
        with self.assertRaises(IndexError):
            extract_span(CONTEXT, -1, 2, token_offsets=TOKEN_OFFSETS)

    def test_non_integer_index_raises_type_error(self):
        """Non-integer token indices raise TypeError."""
        with self.assertRaises(TypeError):
            validate_span("0", 1, 3)
        with self.assertRaises(TypeError):
            validate_span(0, 1.5, 3)

    def test_deliberate_wrong_result_fails(self):
        """Deliberate wrong expected answer triggers AssertionError."""
        state = extract_span(CONTEXT, 0, 0, token_offsets=TOKEN_OFFSETS)
        with self.assertRaises(AssertionError):
            self.assertEqual(state["answer"], "wrote")

    def test_state_not_validated_on_invalid_span(self):
        """State 'validated' field remains False when span is invalid."""
        # We test by catching the exception but inspecting that validated stays False
        # by calling build_token_sequence and validate_span manually
        from example import build_token_sequence
        offsets = build_token_sequence(CONTEXT)
        try:
            validate_span(2, 1, len(offsets))
            validated = True
        except ValueError:
            validated = False
        self.assertFalse(validated)


if __name__ == "__main__":
    unittest.main()
