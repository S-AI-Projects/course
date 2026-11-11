"""Applied Lab R16-T011: UI Callback Contract - Text Analysis Interface.

This module implements a pure callback function for a text-analysis UI interface
(such as Gradio) and validates its input/output schema independently of the UI framework.

Contract:
- Input: String from a UI text component (e.g., gr.Textbox).
- Output: Dictionary with 'word_count' (int) and 'unique_count' (int).
- Normal case: "red red apple" -> word_count=3, unique_count=2.
- Boundary case: Empty or whitespace string -> word_count=0, unique_count=0.
- Failure case: Non-string input is rejected with a TypeError.
"""

from typing import Any, Dict


def analyze_text(text: Any) -> Dict[str, int]:
    """Analyze input text and return word count and unique word count.

    This function represents the pure callback logic that underlies a UI demo.
    It isolates the core computation from UI rendering, permitting deterministic
    local testing without browser, server, or ML model dependencies.

    Args:
        text (Any): The input string to analyze.

    Returns:
        Dict[str, int]: A dictionary with keys:
            - 'word_count': Total number of whitespace-separated words.
            - 'unique_count': Number of distinct whitespace-separated words.

    Raises:
        TypeError: If the input text is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(f"Input must be a string, got {type(text).__name__}")

    words = text.split()
    if not words:
        return {"word_count": 0, "unique_count": 0}

    return {
        "word_count": len(words),
        "unique_count": len(set(words)),
    }


# Callback alias for UI framework compatibility
text_analysis_callback = analyze_text


if __name__ == "__main__":
    test_cases = [
        "red red apple",
        "",
        "   \t\n   ",
        "quick brown fox jumps over the lazy dog",
    ]

    print("Running text analysis callback example:\n" + "-" * 40)
    for sample in test_cases:
        res = analyze_text(sample)
        print(f"Input: {repr(sample)}")
        print(f"Output: {res}\n")

    print("Testing nonstring rejection:")
    for invalid in [None, 123, ["red", "apple"]]:
        try:
            analyze_text(invalid)
            print(f"FAILED to reject: {repr(invalid)}")
        except TypeError as exc:
            print(f"Rejected {repr(invalid)} as expected: {exc}")
