#!/usr/bin/env python3
"""
Applied Lab R16-T023: Token-Budget Preflight Comparison Example.

This module demonstrates token-budget preflight checking and truncation reporting,
connecting to Chapter 1 ("Introduction") of the Hugging Face course.

IMPORTANT TEACHING APPROXIMATION NOTICE:
The tokenizer used in this module is a local whitespace-splitting teaching
approximation (`prompt.strip().split()`). It is designed solely for bounded
deterministic illustration of token counts and budget enforcement. It is NOT
a production model tokenizer (e.g. Byte-Pair Encoding or WordPiece as introduced
in Chapters 2 and 6) and does not reflect subword fragmentation, special tokens,
or model-specific vocabulary IDs.

Contract:
- Configured budget N (integer >= 0).
- Budget 3 with "one two three four" retains ['one', 'two', 'three'] and reports
  1 removed token.
- Empty input retains [] and reports 0 removed tokens.
- Negative budgets (budget < 0) are rejected with ValueError.
- Focus: Compares two independent approaches (Class-based Preflight Engine vs.
  Pure Functional Reference Calculation) across identical inputs.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence
import sys

TOKENIZER_NOTE = (
    "[TEACHING APPROXIMATION] Whitespace splitting is used here solely as a simple, "
    "deterministic educational proxy for tokenization. Production LLMs use learned "
    "subword tokenizers (e.g. BPE, WordPiece, Unigram) that split words into subword pieces."
)


@dataclass(frozen=True)
class PreflightReport:
    """Preflight check report for a single prompt against a token budget."""

    prompt: str
    budget: int
    total_tokens: int
    retained: List[str]
    removed_count: int
    is_truncated: bool

    def as_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            "prompt": self.prompt,
            "budget": self.budget,
            "total_tokens": self.total_tokens,
            "retained": list(self.retained),
            "removed_count": self.removed_count,
            "is_truncated": self.is_truncated,
        }


# ==============================================================================
# Approach 1: Object-Oriented Preflight Engine
# ==============================================================================
class TokenBudgetPreflight:
    """
    Engine to check prompt lengths against a configured token budget.

    Attributes:
        budget: Maximum number of tokens allowed.
    """

    def __init__(self, budget: int) -> None:
        if budget < 0:
            raise ValueError(f"Token budget cannot be negative: received {budget}")
        self.budget: int = budget

    def tokenize(self, prompt: str) -> List[str]:
        """
        Tokenize input text using whitespace approximation.

        NOTE: This is a teaching approximation, not a model tokenizer.
        """
        cleaned = prompt.strip()
        if not cleaned:
            return []
        return cleaned.split()

    def check(self, prompt: str) -> PreflightReport:
        """
        Execute preflight check on prompt and report truncation.

        Args:
            prompt: Raw prompt text.

        Returns:
            PreflightReport with retained tokens and truncation count.
        """
        tokens = self.tokenize(prompt)
        total = len(tokens)

        if total <= self.budget:
            retained = tokens
            removed = 0
            is_truncated = False
        else:
            retained = tokens[: self.budget]
            removed = total - self.budget
            is_truncated = True

        return PreflightReport(
            prompt=prompt,
            budget=self.budget,
            total_tokens=total,
            retained=retained,
            removed_count=removed,
            is_truncated=is_truncated,
        )


# ==============================================================================
# Approach 2: Functional Reference Calculation
# ==============================================================================
def reference_preflight_calc(prompt: str, budget: int) -> Dict[str, Any]:
    """
    Independent reference calculation computing truncation directly.

    Args:
        prompt: Raw prompt text.
        budget: Token budget (non-negative integer).

    Returns:
        Dictionary with identical keys to PreflightReport.as_dict().
    """
    if budget < 0:
        raise ValueError(f"Token budget cannot be negative: received {budget}")

    words = prompt.strip().split() if prompt.strip() else []
    retained = words[:budget]
    removed = max(0, len(words) - len(retained))

    return {
        "prompt": prompt,
        "budget": budget,
        "total_tokens": len(words),
        "retained": retained,
        "removed_count": removed,
        "is_truncated": removed > 0,
    }


def compare_approaches(prompt: str, budget: int) -> bool:
    """
    Compare Approach 1 and Approach 2 on identical inputs.

    Returns:
        True if outputs are identical, False otherwise.
    """
    engine = TokenBudgetPreflight(budget)
    report1 = engine.check(prompt).as_dict()
    report2 = reference_preflight_calc(prompt, budget)
    return report1 == report2


def main() -> int:
    """Run demonstration fixtures and compare both approaches."""
    print("=== Token-Budget Preflight Inspection ===")
    print(f"Notice: {TOKENIZER_NOTE}\n")

    # Contract Fixture 1: Standard prompt with truncation
    prompt_normal = "one two three four"
    budget = 3
    preflight = TokenBudgetPreflight(budget)
    report = preflight.check(prompt_normal)

    print(f"Contract Case 1: Prompt: '{prompt_normal}', Budget: {budget}")
    print(f"  Total tokens:   {report.total_tokens}")
    print(f"  Retained:       {report.retained}")
    print(f"  Removed tokens: {report.removed_count}")
    print(f"  Is truncated:   {report.is_truncated}")

    # Contract Fixture 2: Empty input
    prompt_empty = ""
    report_empty = preflight.check(prompt_empty)
    print(f"\nContract Case 2: Empty input: '{prompt_empty}', Budget: {budget}")
    print(f"  Retained:       {report_empty.retained}")
    print(f"  Removed tokens: {report_empty.removed_count}")

    # Contract Fixture 3: Negative budget rejection
    print("\nContract Case 3: Negative budget rejection (budget = -1)")
    try:
        TokenBudgetPreflight(-1)
        print("  ERROR: Negative budget was not rejected!")
        return 1
    except ValueError as e:
        print(f"  PASS: Correctly rejected negative budget ({e})")

    # Comparison across test suite
    print("\n=== Comparing Approach 1 (Engine) vs Approach 2 (Reference Calc) ===")
    test_cases = [
        ("one two three four", 3),
        ("one two three four", 4),
        ("one two three four", 5),
        ("one two three four", 0),
        ("", 3),
        ("   ", 2),
        ("alpha beta", 1),
    ]

    all_matched = True
    for p, b in test_cases:
        matches = compare_approaches(p, b)
        print(f"  Input: prompt='{p}', budget={b} -> Match: {matches}")
        if not matches:
            all_matched = False

    if not all_matched:
        print("ERROR: Approach discrepancy detected!")
        return 1

    print("\nAll comparison cases agreed identically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
