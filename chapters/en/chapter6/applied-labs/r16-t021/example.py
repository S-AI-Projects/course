#!/usr/bin/env python3
"""
Applied Lab R16-T021: Greedy Subword Segmentation Concept Example.

This module provides a minimal, self-contained educational implementation
of the greedy subword segmentation algorithm used by WordPiece models
(such as BERT), as discussed in Chapter 6 Section 8 ("Building a tokenizer,
block by block") of the Hugging Face course.

Algorithm overview:
1. For each word, find the longest subword starting from the beginning
   that exists in the vocabulary.
2. If found, add it to the token list and proceed with the remaining substring.
3. For all continuation subwords (tokens after the first), prefix them with
   the continuation marker (default: '##') before checking vocabulary membership.
4. If at any position no prefix matches the vocabulary, the entire word cannot
   be segmented and is replaced with the unknown token (default: '[UNK]').

Standard fixture:
    Vocabulary: {"play", "##ing", "cat"}
    - "playing" -> ["play", "##ing"]
    - "cat"     -> ["cat"]
    - "dog"     -> ["[UNK]"]
"""

from typing import Iterable, List, Sequence, Set
import sys

DEFAULT_VOCAB: Set[str] = {"play", "##ing", "cat"}
DEFAULT_UNK_TOKEN: str = "[UNK]"
DEFAULT_CONTINUATION_PREFIX: str = "##"


def segment_word(
    word: str,
    vocab: Iterable[str] = DEFAULT_VOCAB,
    unk_token: str = DEFAULT_UNK_TOKEN,
    continuation_prefix: str = DEFAULT_CONTINUATION_PREFIX,
) -> List[str]:
    """
    Segment a single word into subwords using greedy longest-prefix matching.

    Args:
        word: The input word string to segment.
        vocab: The vocabulary collection of valid subword tokens.
        unk_token: The token to return if the word cannot be segmented.
        continuation_prefix: Prefix added to non-initial subwords.

    Returns:
        List of subword tokens, or [unk_token] if segmentation fails.
    """
    if not word:
        return []

    vocab_set = set(vocab)
    tokens: List[str] = []
    current = word
    is_first = True

    while current:
        prefix = "" if is_first else continuation_prefix
        matched = False

        # Try longest match first (from full length down to 1)
        for end in range(len(current), 0, -1):
            subword = prefix + current[:end]
            if subword in vocab_set:
                tokens.append(subword)
                current = current[end:]
                is_first = False
                matched = True
                break

        if not matched:
            # If any remaining part cannot be segmented, the whole word is [UNK]
            return [unk_token]

    return tokens


def tokenize_text(
    text: str,
    vocab: Iterable[str] = DEFAULT_VOCAB,
    unk_token: str = DEFAULT_UNK_TOKEN,
    continuation_prefix: str = DEFAULT_CONTINUATION_PREFIX,
) -> List[str]:
    """
    Tokenize whitespace-delimited text into subwords.

    Args:
        text: Input text string.
        vocab: Vocabulary of subwords.
        unk_token: Unknown token fallback.
        continuation_prefix: Continuation prefix.

    Returns:
        Flattened list of tokens across all words.
    """
    words = text.strip().split()
    tokens: List[str] = []
    for word in words:
        tokens.extend(segment_word(word, vocab, unk_token, continuation_prefix))
    return tokens


def main(args: Sequence[str] = ()) -> int:
    """Run demonstration with default vocabulary or CLI arguments."""
    target_words = list(args) if args else ["playing", "cat", "dog"]

    print("=== Greedy Subword Segmentation (WordPiece Model Concept) ===")
    print(f"Vocabulary: {sorted(DEFAULT_VOCAB)}")
    print(f"Continuation prefix: '{DEFAULT_CONTINUATION_PREFIX}'")
    print(f"Unknown token: '{DEFAULT_UNK_TOKEN}'")
    print("-" * 60)

    for word in target_words:
        result = segment_word(word, DEFAULT_VOCAB)
        print(f"'{word}' -> {result}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
