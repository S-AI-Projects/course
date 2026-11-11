"""Applied Lab R16-T018: Greedy Subword Segmentation — Failure and Recovery Example.

Task: R16-T018 (Issue #21)
Chapter: 6, Section 6 ("WordPiece tokenization")
Repository: https://github.com/S-AI-Projects/course

This module implements a deterministic local WordPiece tokenizer using greedy
longest-prefix subword segmentation with '##' continuation markers and '[UNK]'
fallback.

Contract:
- Vocabulary {play, ##ing, cat}:
    playing -> ["play", "##ing"]
    cat     -> ["cat"]
    dog     -> ["[UNK]"]
- Failure and recovery:
    Handles documented invalid/missing-data cases (None, non-string, empty vocab),
    explains the error, and proves state recovery on the next valid input.

SIMULATION NOTE / PEDAGOGICAL SCOPE:
This is a pure Python 3 standard library implementation designed for pedagogical
study of greedy WordPiece prefix segmentation. It does not load heavy native C++/Rust
tokenizers, download remote model weights, or require GPU hardware.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional, Set

DEFAULT_VOCAB = {"play", "##ing", "cat", "[UNK]"}
UNK_TOKEN = "[UNK]"


@dataclass(frozen=True)
class TokenizationResult:
    """Result of tokenizing a single input with diagnostic status.

    Attributes:
        input_data: The raw input provided.
        tokens: Resulting list of tokens (or None if error occurred).
        status: 'SUCCESS' or 'ERROR'.
        error_message: Detailed diagnostic error explanation if failed.
    """

    input_data: Any
    tokens: Optional[List[str]]
    status: str
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WordPieceTokenizer:
    """Pedagogical WordPiece tokenizer with longest-prefix segmentation

    and robust stream error recovery.
    """

    def __init__(self, vocab: Optional[Set[str]] = None, unk_token: str = UNK_TOKEN) -> None:
        """Initialize with vocabulary set and unknown token marker.

        Args:
            vocab: Set of vocabulary tokens. Defaults to DEFAULT_VOCAB.
            unk_token: Out-of-vocabulary fallback marker.
        """
        if vocab is not None and not isinstance(vocab, (set, list, tuple)):
            raise TypeError(f"vocab must be a set or list, got {type(vocab).__name__}")
        if vocab is not None and len(vocab) == 0:
            raise ValueError("vocabulary cannot be empty")

        self.vocab = set(vocab) if vocab is not None else set(DEFAULT_VOCAB)
        self.unk_token = unk_token

    def encode_word(self, word: str) -> List[str]:
        """Segment a single word by greedy longest-prefix match.

        Uses '##' for continuation tokens. Returns [unk_token] if any subword
        cannot be matched against the vocabulary.

        Args:
            word: Clean single-word string without whitespace.

        Returns:
            List of subword tokens or [unk_token].

        Raises:
            TypeError: If word is not a str.
        """
        if not isinstance(word, str):
            raise TypeError(f"Expected word to be str, got {type(word).__name__}")

        if not word:
            return []

        tokens: List[str] = []
        current = word
        while len(current) > 0:
            i = len(current)
            while i > 0 and current[:i] not in self.vocab:
                i -= 1
            if i == 0:
                return [self.unk_token]
            tokens.append(current[:i])
            current = current[i:]
            if len(current) > 0 and not current.startswith("##"):
                current = f"##{current}"

        return tokens

    def tokenize_text(self, text: str) -> List[str]:
        """Tokenize whitespace-separated text into a list of WordPiece tokens.

        Args:
            text: Input sentence or prompt string.

        Returns:
            Flat list of subword tokens.

        Raises:
            TypeError: If text is not a str.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected text to be str, got {type(text).__name__}")

        words = text.strip().split()
        if not words:
            return []

        all_tokens: List[str] = []
        for word in words:
            all_tokens.extend(self.encode_word(word))
        return all_tokens

    def tokenize_safe(self, item: Any) -> TokenizationResult:
        """Safely tokenize an input item, capturing and explaining errors.

        Ensures tokenizer internal state is unaffected by malformed items.

        Args:
            item: Input item (expected str).

        Returns:
            TokenizationResult reporting tokens on success or error explanation.
        """
        if item is None:
            return TokenizationResult(
                input_data=item,
                tokens=None,
                status="ERROR",
                error_message="Missing data: input cannot be None (expected str).",
            )

        if not isinstance(item, str):
            return TokenizationResult(
                input_data=item,
                tokens=None,
                status="ERROR",
                error_message=(
                    f"Invalid input type: expected str, got {type(item).__name__}."
                ),
            )

        try:
            tokens = self.tokenize_text(item)
            return TokenizationResult(
                input_data=item,
                tokens=tokens,
                status="SUCCESS",
                error_message=None,
            )
        except Exception as exc:  # Catch unexpected operational errors
            return TokenizationResult(
                input_data=item,
                tokens=None,
                status="ERROR",
                error_message=f"Tokenization failed: {exc}",
            )

    def tokenize_stream(self, stream: Iterable[Any]) -> List[TokenizationResult]:
        """Process a stream of inputs sequentially with failure isolation and recovery.

        When an invalid input is encountered, an error result is recorded, and
        processing immediately recovers on the next valid item in the stream.

        Args:
            stream: Iterable containing input items.

        Returns:
            List of TokenizationResult objects.
        """
        results: List[TokenizationResult] = []
        for item in stream:
            results.append(self.tokenize_safe(item))
        return results


def main() -> None:
    print("=== WordPiece Greedy Subword Segmentation (Task R16-T018) ===")
    print(f"Vocabulary: {sorted(list(DEFAULT_VOCAB))}\n")

    tokenizer = WordPieceTokenizer()

    # Core required contract examples
    words = ["playing", "cat", "dog"]
    print("--- Core Contract Verification ---")
    for w in words:
        tokens = tokenizer.encode_word(w)
        print(f"  Word: {w!r:10} -> Tokens: {tokens}")

    # Failure and recovery stream demonstration
    print("\n--- Failure and Recovery Stream Demonstration ---")
    stream = [
        "cat",                        # 1. Valid input
        None,                         # 2. Missing-data failure
        "playing",                    # 3. Recovery input
        12345,                        # 4. Invalid-type failure
        "dog",                        # 5. Recovery input
    ]

    results = tokenizer.tokenize_stream(stream)
    for i, res in enumerate(results, 1):
        if res.status == "SUCCESS":
            print(f"[{i}] SUCCESS  Input: {res.input_data!r:10} -> Tokens: {res.tokens}")
        else:
            print(f"[{i}] ERROR    Input: {res.input_data!r:10} -> {res.error_message}")


if __name__ == "__main__":
    main()
