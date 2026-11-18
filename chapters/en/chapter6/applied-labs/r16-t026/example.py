#!/usr/bin/env python3
"""
Applied Lab R16-T026: Normalization with Offsets - Refactor the Teaching Example.

This module illustrates normalization and pre-tokenization with character offsets,
connecting to Chapter 6 Section 4 ("Normalization and pre-tokenization") of the
Hugging Face course.

Contract:
- Input: "  red   apple "
- Normalizes repeated whitespace while retaining exact character offsets into the original text.
- Expected output:
  - "red" at span [2, 5)
  - "apple" at span [8, 13)
- Slices recover the original words: text[2:5] == "red", text[8:13] == "apple".
- Refactoring Focus:
  1. Implement a correct monolithic baseline (`baseline_tokenize_with_offsets`).
  2. Extract one named responsibility: span offset scanning (`WhitespaceSpanScanner`).
  3. Implement the refactored tokenizer (`refactored_tokenize_with_offsets`).
  4. Prove before/after equivalence on the standard fixture.
"""

from typing import List, NamedTuple, Sequence, Tuple
import sys


class TokenWithOffset(NamedTuple):
    """Token string with start and end character offsets into the original text."""

    token: str
    span: Tuple[int, int]


# ==============================================================================
# 1. Monolithic Baseline Implementation
# ==============================================================================
def baseline_tokenize_with_offsets(text: str) -> List[Tuple[str, Tuple[int, int]]]:
    """
    Monolithic baseline: simultaneously identifies non-whitespace character
    boundaries, computes offsets, and extracts tokens in a single loop.
    """
    results: List[Tuple[str, Tuple[int, int]]] = []
    n = len(text)
    i = 0

    while i < n:
        # Skip whitespace
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break

        start = i
        # Accumulate non-whitespace characters
        while i < n and not text[i].isspace():
            i += 1
        end = i

        token = text[start:end]
        results.append((token, (start, end)))

    return results


# ==============================================================================
# 2. Extracted Responsibility: Whitespace Span Scanner
# ==============================================================================
class WhitespaceSpanScanner:
    """
    Extracted named responsibility: identifies character boundary intervals [start, end)
    for non-whitespace segments without coupling to token creation or normalization.
    """

    @staticmethod
    def scan_spans(text: str) -> List[Tuple[int, int]]:
        """
        Scan text and return character offset tuples (start, end) for non-whitespace runs.

        Args:
            text: Raw input string.

        Returns:
            List of (start, end) index tuples.
        """
        spans: List[Tuple[int, int]] = []
        n = len(text)
        idx = 0

        while idx < n:
            if not text[idx].isspace():
                start = idx
                while idx < n and not text[idx].isspace():
                    idx += 1
                spans.append((start, idx))
            else:
                idx += 1

        return spans


# ==============================================================================
# 3. Refactored Implementation (Using Extracted Responsibility)
# ==============================================================================
def refactored_tokenize_with_offsets(text: str) -> List[Tuple[str, Tuple[int, int]]]:
    """
    Refactored tokenizer: delegates character boundary detection to
    WhitespaceSpanScanner, then extracts normalized tokens via string slicing.
    """
    spans = WhitespaceSpanScanner.scan_spans(text)
    return [(text[start:end], (start, end)) for start, end in spans]


# ==============================================================================
# 4. Equivalence and Slice Recovery Verification
# ==============================================================================
def recover_words_from_slices(
    text: str, token_spans: Sequence[Tuple[str, Tuple[int, int]]]
) -> List[str]:
    """Recover original substrings by directly slicing raw text with token offsets."""
    return [text[start:end] for _, (start, end) in token_spans]


def prove_equivalence(text: str) -> bool:
    """Validate that baseline and refactored implementations produce identical output."""
    baseline = baseline_tokenize_with_offsets(text)
    refactored = refactored_tokenize_with_offsets(text)
    return baseline == refactored


def main() -> int:
    """Run demonstration with the standard fixture and verify equivalence."""
    fixture = "  red   apple "

    print("=== Normalization with Offsets: Refactored Teaching Example ===")
    print(f"Raw Input: {fixture!r} (length: {len(fixture)})")

    # Baseline run
    baseline_result = baseline_tokenize_with_offsets(fixture)
    print("\n1. Baseline Output:")
    for token, (s, e) in baseline_result:
        print(f"   token: {token!r:8} span: [{s}, {e})")

    # Refactored run
    refactored_result = refactored_tokenize_with_offsets(fixture)
    print("\n2. Refactored Output (Extracted WhitespaceSpanScanner):")
    for token, (s, e) in refactored_result:
        print(f"   token: {token!r:8} span: [{s}, {e})")

    # Equivalence check
    is_equivalent = baseline_result == refactored_result
    print(f"\n3. Equivalence Check: {'PASSED' if is_equivalent else 'FAILED'}")

    # Slice recovery check
    recovered = recover_words_from_slices(fixture, refactored_result)
    print("\n4. Slice Recovery Invariant Verification:")
    all_slices_match = True
    for (token, (s, e)), rec in zip(refactored_result, recovered):
        matches = token == rec and fixture[s:e] == token
        print(f"   fixture[{s}:{e}] -> {fixture[s:e]!r} == token {token!r}: {matches}")
        if not matches:
            all_slices_match = False

    print(f"\nSlice Recovery Invariant: {'PASSED' if all_slices_match else 'FAILED'}")

    return 0 if (is_equivalent and all_slices_match) else 1


if __name__ == "__main__":
    sys.exit(main())
