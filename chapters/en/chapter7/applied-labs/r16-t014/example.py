"""Applied Lab R16-T014: Answer-Span Extraction — Invariant and State Trace.

This module implements span extraction for extractive Question Answering tied to
Chapter 7 Section 7 ("Question answering"). It:
- Validates start/end token indices against the fixed word-level token sequence.
- Maps token indices to character offsets in the context string.
- Recovers the answer substring from the context.
- Records intermediate state after each pipeline step.
- Tests the invariant linking intermediate state to the final extracted output.

Fixed context: "Ada wrote notes"
Word-level token spans (0-indexed):
  - Token 0 → "Ada"   (chars 0–3)
  - Token 1 → "wrote" (chars 4–9)
  - Token 2 → "notes" (chars 10–15)

Contract:
- span(0, 0) → "Ada"
- span(1, 2) → "wrote notes"
- span(2, 2) → "notes"
- span(end < start) → raises ValueError (invalid span)
- span(out of bounds) → raises IndexError
"""

from typing import Any, Dict, List, Optional, Tuple

CONTEXT = "Ada wrote notes"

# Word-level token sequence: (token_text, char_start, char_end)
# char_end is exclusive (Python slice convention)
TOKEN_OFFSETS: List[Tuple[str, int, int]] = [
    ("Ada",   0,  3),
    ("wrote", 4,  9),
    ("notes", 10, 15),
]


def build_token_sequence(context: str) -> List[Tuple[str, int, int]]:
    """Build word-level token offsets by splitting on whitespace.

    Records intermediate state: each token with its char_start and char_end.
    This mirrors the offset_mapping produced by HuggingFace tokenizers in the
    QA pipeline described in Chapter 7 Section 7.

    Args:
        context (str): The raw context string.

    Returns:
        List of (token_text, char_start, char_end) tuples.
    """
    tokens: List[Tuple[str, int, int]] = []
    pos = 0
    for word in context.split():
        char_start = context.index(word, pos)
        char_end = char_start + len(word)
        tokens.append((word, char_start, char_end))
        pos = char_end
    return tokens


def validate_span(start: int, end: int, num_tokens: int) -> None:
    """Validate start/end token indices before extraction.

    Invariant: 0 <= start <= end < num_tokens.

    Args:
        start (int): Start token index (inclusive).
        end (int): End token index (inclusive).
        num_tokens (int): Total number of tokens in the sequence.

    Raises:
        TypeError: If start or end is not an integer.
        ValueError: If end < start (span has inverted boundaries).
        IndexError: If start or end is out of the valid range [0, num_tokens-1].
    """
    if not isinstance(start, int) or not isinstance(end, int):
        raise TypeError(f"start and end must be integers, got {type(start).__name__} and {type(end).__name__}")
    if end < start:
        raise ValueError(
            f"Invalid span: end ({end}) is before start ({start}). "
            "In extractive QA, span end must be >= start."
        )
    if start < 0 or start >= num_tokens:
        raise IndexError(f"start index {start} is out of range [0, {num_tokens - 1}]")
    if end < 0 or end >= num_tokens:
        raise IndexError(f"end index {end} is out of range [0, {num_tokens - 1}]")


def extract_span(
    context: str,
    start: int,
    end: int,
    token_offsets: Optional[List[Tuple[str, int, int]]] = None,
) -> Dict[str, Any]:
    """Extract an answer substring from context given start/end token indices.

    Records intermediate state at each step of the pipeline:
    1. token_offsets: the offset map derived from context
    2. validated: confirmation that span bounds pass the invariant
    3. char_start: character position of the start token
    4. char_end: character position after the end token
    5. answer: the final extracted substring

    Invariant assertion: char_end - char_start > 0 for any valid non-empty span.

    Args:
        context (str): The raw context string.
        start (int): Start token index (inclusive).
        end (int): End token index (inclusive).
        token_offsets: Optional pre-built offset list (defaults to computing via context split).

    Returns:
        Dict with keys: token_offsets, validated, char_start, char_end, answer.

    Raises:
        TypeError: For non-integer index types.
        ValueError: If end < start.
        IndexError: If indices are out of range.
    """
    # Step 1: Build token offsets
    if token_offsets is None:
        token_offsets = build_token_sequence(context)

    state: Dict[str, Any] = {
        "token_offsets": token_offsets,
        "validated": False,
        "char_start": None,
        "char_end": None,
        "answer": None,
    }

    # Step 2: Validate span — invariant check
    validate_span(start, end, len(token_offsets))
    state["validated"] = True

    # Step 3: Map token indices to character offsets
    _, char_start, _ = token_offsets[start]
    _, _, char_end = token_offsets[end]
    state["char_start"] = char_start
    state["char_end"] = char_end

    # Step 4: Invariant — char span must have positive width
    assert char_end > char_start, (
        f"Invariant violated: char span [{char_start}, {char_end}) has zero or negative width"
    )

    # Step 5: Recover answer substring
    answer = context[char_start:char_end]
    state["answer"] = answer

    return state


if __name__ == "__main__":
    print(f"Context: {repr(CONTEXT)}")
    print(f"Token offsets: {TOKEN_OFFSETS}")
    print()

    test_cases = [
        (0, 0, "token 0..0 → 'Ada'"),
        (1, 2, "token 1..2 → 'wrote notes'"),
        (2, 2, "token 2..2 → 'notes'"),
    ]

    print("--- Normal and boundary extraction ---")
    for start, end, description in test_cases:
        result = extract_span(CONTEXT, start, end, token_offsets=TOKEN_OFFSETS)
        print(f"span({start}, {end}) [{description}]:")
        print(f"  validated:  {result['validated']}")
        print(f"  char range: [{result['char_start']}, {result['char_end']})")
        print(f"  answer:     {repr(result['answer'])}")
        print()

    print("--- Invalid span: end before start ---")
    for bad_start, bad_end in [(2, 0), (1, 0)]:
        try:
            extract_span(CONTEXT, bad_start, bad_end, token_offsets=TOKEN_OFFSETS)
            print(f"span({bad_start}, {bad_end}): ERROR — should have raised ValueError")
        except ValueError as e:
            print(f"span({bad_start}, {bad_end}): Correctly raised ValueError: {e}")
    print()

    print("--- Out-of-bounds span ---")
    try:
        extract_span(CONTEXT, 0, 99, token_offsets=TOKEN_OFFSETS)
    except IndexError as e:
        print(f"span(0, 99): Correctly raised IndexError: {e}")
