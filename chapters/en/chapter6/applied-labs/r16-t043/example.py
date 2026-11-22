#!/usr/bin/env python3
"""
Applied Lab R16-T043: Token-to-Character Alignment — Compare Two Approaches.

This module implements a local token-span lookup and validates non-overlapping
half-open spans [start, end) against the original text, connecting directly to
Chapter 6, Section 3 ("Fast tokenizers' special powers" [fast-tokenizers-special-powers]).

Educational Scope & Simplifications:
- Fast tokenizers in Hugging Face provide offset mappings (pairs of integers denoting
  start and end character indices for each token).
- This lab implements a deterministic, local offset-mapping fixture and character-to-token
  lookup mechanism.
- The example uses standard library Python; no Hugging Face transformers, Rust binaries,
  external dependencies, model checkpoints, paid APIs, or GPU hardware are required.

Contract:
- For text "red apple", spans are [0, 3) for "red" (token 0) and [4, 9) for "apple" (token 1).
- Character index 5 maps to token index 1 ('apple'[1] == 'p').
- Character index 4 maps to token index 1 ('apple'[0] == 'a').
- Character index 3 (the separating whitespace) maps to no token (None).
- Focus: Compare two independent approaches:
  1. Approach 1 (Interval Tree / Search Binary Alignment Engine):
     Evaluates intervals and validates non-overlapping half-open bounds.
  2. Approach 2 (Direct Dense Character Map / Explicit Expected-Result Table):
     Directly computes or indexes the expected character-to-token table.
  Both approaches are verified against identical inputs.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TokenSpan:
    """Represents a token and its half-open character span [start, end)."""

    token_index: int
    token_text: str
    start: int
    end: int

    def contains(self, char_index: int) -> bool:
        """Check if char_index lies in half-open interval [start, end)."""
        return self.start <= char_index < self.end


# ==============================================================================
# Approach 1: Span Alignment Engine (Interval Validation & Search)
# ==============================================================================
class TokenSpanAlignment:
    """Manages token spans and character-to-token alignment for a given text.

    Validates that:
    - Each span is a valid half-open interval [start, end) where 0 <= start < end <= len(text).
    - Spans are strictly non-overlapping.
    - Slices text[start:end] match token_text.
    """

    def __init__(self, original_text: str, spans: List[Tuple[int, int]]) -> None:
        if not isinstance(original_text, str):
            raise TypeError(f"original_text must be str, got {type(original_text).__name__}")
        if not isinstance(spans, list):
            raise TypeError(f"spans must be list of tuples, got {type(spans).__name__}")

        self.original_text = original_text
        self.spans: List[TokenSpan] = []
        self._validate_and_build(spans)

    def _validate_and_build(self, raw_spans: List[Tuple[int, int]]) -> None:
        text_len = len(self.original_text)
        prev_end = 0

        for idx, span in enumerate(raw_spans):
            if not (isinstance(span, (tuple, list)) and len(span) == 2):
                raise ValueError(f"Span at index {idx} must be a 2-tuple (start, end), got {span}")
            start, end = span

            if not (isinstance(start, int) and isinstance(end, int)):
                raise TypeError(f"Span indices must be integers, got ({type(start)}, {type(end)})")

            if start < 0 or end > text_len:
                raise ValueError(
                    f"Span [{start}, {end}) out of bounds for text of length {text_len}"
                )
            if start >= end:
                raise ValueError(
                    f"Span [{start}, {end}) is empty or invalid (start must be < end)"
                )
            if start < prev_end:
                raise ValueError(
                    f"Overlapping or out-of-order span [{start}, {end}) with previous end {prev_end}"
                )

            token_text = self.original_text[start:end]
            self.spans.append(
                TokenSpan(
                    token_index=idx,
                    token_text=token_text,
                    start=start,
                    end=end,
                )
            )
            prev_end = end

    def char_to_token(self, char_index: int) -> Optional[int]:
        """Map a character index in original_text to its corresponding token index.

        Returns None if char_index falls outside all token spans (e.g., whitespace).
        """
        if not isinstance(char_index, int) or isinstance(char_index, bool):
            raise TypeError(f"char_index must be int, got {type(char_index).__name__}")

        if char_index < 0 or char_index >= len(self.original_text):
            return None

        # Binary search or interval inspection
        for span in self.spans:
            if span.contains(char_index):
                return span.token_index
            if char_index < span.start:
                # Since spans are sorted and non-overlapping, char lies in gap before this span
                return None

        return None


# ==============================================================================
# Approach 2: Explicit Dense Character Map / Expected-Result Table Calculation
# ==============================================================================
def build_dense_char_to_token_map(
    original_text: str, spans: List[Tuple[int, int]]
) -> Dict[int, Optional[int]]:
    """Independent reference calculation building an explicit character lookup table.

    Computes a mapping for every character index in range(len(original_text)):
    char_index -> token_index if inside a span, or None if in a separating gap.
    """
    if not isinstance(original_text, str):
        raise TypeError("original_text must be str")

    dense_map: Dict[int, Optional[int]] = {i: None for i in range(len(original_text))}

    for token_idx, (start, end) in enumerate(spans):
        for c in range(start, end):
            dense_map[c] = token_idx

    return dense_map


def compare_alignment_approaches(
    original_text: str, spans: List[Tuple[int, int]]
) -> Tuple[bool, Dict[str, Any]]:
    """Compare Approach 1 (TokenSpanAlignment engine) and Approach 2 (Dense Map) across all chars."""
    engine = TokenSpanAlignment(original_text, spans)
    dense_table = build_dense_char_to_token_map(original_text, spans)

    char_comparisons = {}
    matches = True

    for c in range(len(original_text)):
        res1 = engine.char_to_token(c)
        res2 = dense_table[c]
        char_comparisons[c] = {
            "char": original_text[c],
            "approach1": res1,
            "approach2": res2,
            "match": res1 == res2,
        }
        if res1 != res2:
            matches = False

    return matches, {
        "text": original_text,
        "spans": spans,
        "all_matched": matches,
        "per_character": char_comparisons,
    }


if __name__ == "__main__":
    print("=== Token-to-Character Alignment Demo (R16-T043) ===")
    sample_text = "red apple"
    sample_spans = [(0, 3), (4, 9)]

    aligner = TokenSpanAlignment(sample_text, sample_spans)
    print(f"Text: {repr(sample_text)}, Spans: {sample_spans}")

    # Contract cases:
    c5 = aligner.char_to_token(5)
    c3 = aligner.char_to_token(3)
    print(f"Character index 5 ('{sample_text[5]}') -> token {c5} (Expected: 1)")
    print(f"Character index 3 ('{sample_text[3]}') -> token {c3} (Expected: None)")

    # Compare approaches
    identical, details = compare_alignment_approaches(sample_text, sample_spans)
    print(f"Comparison of Approach 1 vs Approach 2 matches completely: {identical}")
