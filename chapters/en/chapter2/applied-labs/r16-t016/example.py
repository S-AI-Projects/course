"""Token-Budget Preflight — Refactored Teaching Example.

Task: R16-T016 (Issue #19)
Chapter: 2, Section 4 ("Tokenizers")
Repository: https://github.com/S-AI-Projects/course

This module provides a deterministic local whitespace tokenization fixture
and token-budget preflight check. It reports retained tokens and truncation
explicitly.

SIMULATION NOTE / TEACHING APPROXIMATION:
The WhitespaceTokenizer in this lab is a pedagogical approximation designed
for offline algorithmic study. It splits on ASCII whitespace and does NOT
perform subword tokenization (BPE, WordPiece, SentencePiece) or vocabulary
lookup. It does not establish model-readiness, inference latency, or GPU
memory usage of production tokenizer pipelines.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TokenBudgetResult:
    """Immutable result of a token-budget preflight check.

    Attributes:
        retained_tokens: List of tokens retained within the budget.
        removed_tokens: List of tokens truncated beyond the budget.
        removed_count: Count of removed (truncated) tokens.
        total_tokens: Total token count before truncation.
        budget: Configured maximum token budget.
        truncated: True if tokens were removed, False otherwise.
    """

    retained_tokens: List[str]
    removed_tokens: List[str]
    removed_count: int
    total_tokens: int
    budget: int
    truncated: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a plain dictionary representation."""
        return asdict(self)


# ============================================================================
# 1. Monolithic Baseline Implementation (Pre-refactoring)
# ============================================================================

def token_budget_preflight_baseline(text: str, budget: int) -> TokenBudgetResult:
    """Baseline monolithic implementation: coupling tokenization and budget check.

    Args:
        text: Input prompt string.
        budget: Configured token budget (non-negative integer).

    Returns:
        TokenBudgetResult with retained tokens and truncation report.

    Raises:
        TypeError: If text is not str or budget is not int.
        ValueError: If budget is negative.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")
    if not isinstance(budget, int) or isinstance(budget, bool):
        raise TypeError(f"budget must be an int, got {type(budget).__name__}")
    if budget < 0:
        raise ValueError(f"budget cannot be negative, got {budget}")

    # Monolithic whitespace tokenization approximation
    tokens = text.split() if text.strip() else []

    total_tokens = len(tokens)
    retained = tokens[:budget]
    removed = tokens[budget:]
    removed_count = len(removed)
    truncated = removed_count > 0

    return TokenBudgetResult(
        retained_tokens=retained,
        removed_tokens=removed,
        removed_count=removed_count,
        total_tokens=total_tokens,
        budget=budget,
        truncated=truncated,
    )


# ============================================================================
# 2. Refactored Implementation (Extracted Responsibilities)
# ============================================================================

class WhitespaceTokenizer:
    """Teaching approximation of a tokenizer using whitespace boundary splitting.

    NOTE: This is a teaching approximation, NOT the model's real tokenizer.
    Real transformers tokenizers use subword algorithms (Byte-Pair Encoding,
    WordPiece, Unigram) with a fixed vocabulary and produce token IDs.
    """

    is_teaching_approximation: bool = True

    def tokenize(self, text: str) -> List[str]:
        """Split text into whitespace-delimited tokens.

        Args:
            text: Input string.

        Returns:
            List of string tokens (empty list if input is empty or whitespace).

        Raises:
            TypeError: If input text is not a str.
        """
        if not isinstance(text, str):
            raise TypeError(f"text must be a str, got {type(text).__name__}")
        stripped = text.strip()
        if not stripped:
            return []
        return text.split()


class TokenBudgetEnforcer:
    """Extracted responsibility: enforces budget limits and reports truncation."""

    def __init__(self, budget: int) -> None:
        """Initialize with a non-negative integer budget.

        Args:
            budget: Maximum number of tokens allowed.

        Raises:
            TypeError: If budget is not an integer.
            ValueError: If budget is negative.
        """
        if not isinstance(budget, int) or isinstance(budget, bool):
            raise TypeError(f"budget must be an int, got {type(budget).__name__}")
        if budget < 0:
            raise ValueError(f"budget cannot be negative, got {budget}")
        self.budget = budget

    def enforce(self, tokens: List[str]) -> TokenBudgetResult:
        """Apply budget limit to a token list and compute truncation details.

        Args:
            tokens: List of token strings.

        Returns:
            TokenBudgetResult containing retained tokens and explicit removal count.

        Raises:
            TypeError: If tokens is not a list.
        """
        if not isinstance(tokens, list):
            raise TypeError(f"tokens must be a list, got {type(tokens).__name__}")

        total_tokens = len(tokens)
        retained = tokens[: self.budget]
        removed = tokens[self.budget :]
        removed_count = len(removed)
        truncated = removed_count > 0

        return TokenBudgetResult(
            retained_tokens=retained,
            removed_tokens=removed,
            removed_count=removed_count,
            total_tokens=total_tokens,
            budget=self.budget,
            truncated=truncated,
        )


def token_budget_preflight(
    text: str,
    budget: int,
    tokenizer: Optional[WhitespaceTokenizer] = None,
) -> TokenBudgetResult:
    """Refactored preflight check: orchestrates tokenizer and budget enforcer.

    Maintains full behavioral equivalence with token_budget_preflight_baseline.

    Args:
        text: Input prompt string.
        budget: Configured token budget (non-negative integer).
        tokenizer: Optional tokenizer instance (defaults to WhitespaceTokenizer).

    Returns:
        TokenBudgetResult with retained tokens and truncation report.
    """
    if tokenizer is None:
        tokenizer = WhitespaceTokenizer()
    tokens = tokenizer.tokenize(text)
    enforcer = TokenBudgetEnforcer(budget)
    return enforcer.enforce(tokens)


# Standard runnable demonstration
def main() -> None:
    print("=== Token-Budget Preflight Demonstration (Task R16-T016) ===")
    print("NOTE: Teaching approximation only — not a real subword tokenizer.\n")

    scenarios = [
        ("Budget 3 with 'one two three four'", "one two three four", 3),
        ("Empty input with budget 3", "", 3),
        ("Exact fit: 3 tokens with budget 3", "one two three", 3),
        ("Generous budget: 2 tokens with budget 5", "one two", 5),
        ("Zero budget: 3 tokens with budget 0", "alpha beta gamma", 0),
    ]

    for label, text, budget in scenarios:
        res = token_budget_preflight(text, budget)
        print(f"[{label}]")
        print(f"  Input text     : {text!r}")
        print(f"  Budget         : {budget}")
        print(f"  Total tokens   : {res.total_tokens}")
        print(f"  Retained tokens: {res.retained_tokens}")
        print(f"  Removed count  : {res.removed_count} (removed: {res.removed_tokens})")
        print(f"  Truncated      : {res.truncated}\n")


if __name__ == "__main__":
    main()
