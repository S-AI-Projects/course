#!/usr/bin/env python3
"""
Applied Lab R16-T047: Token-Budget Preflight — Worked Example with Checks.

This module implements a deterministic local token-budget preflight check
connecting directly to Chapter 8, Section 7 ("End-of-chapter quiz" [end-of-chapter-quiz]).

Lesson Context:
In Chapter 8, debugging workflows emphasize verifying input bounds, data shapes,
and reproducible assertions before executing heavy model pipelines.
A token-budget preflight acts as a lightweight regression check ensuring that
inputs do not exceed memory or sequence limits.

Teaching Approximation:
The tokenizer in this module is a local whitespace-splitting teaching approximation
(`prompt.strip().split()`). It is NOT the model's real subword tokenizer (e.g. BPE,
WordPiece) and does not insert special tokens ([CLS]/[SEP]) or map vocabulary IDs.

Contract:
- Configured budget N (integer >= 0).
- Budget 3 with "one two three four" retains ['one', 'two', 'three'] and reports 1 removed token.
- Empty input retains [] and reports 0 removed tokens.
- Negative budgets (budget < 0) are rejected with ValueError.
- Focus: Publish a worked input-to-output explanation and execute the exact example
  as an automated regression test.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


TOKENIZER_NOTE = (
    "[TEACHING APPROXIMATION] Whitespace splitting is used here as a deterministic, "
    "local educational fixture to illustrate token budget enforcement and truncation reporting. "
    "It is NOT a trained model tokenizer (such as WordPiece or BPE) and does not perform subword "
    "segmentation, special token handling, or vocabulary ID lookup."
)


@dataclass(frozen=True)
class PreflightResult:
    """Structured report returned by the preflight check."""

    prompt: str
    budget: int
    total_tokens: int
    retained: List[str]
    removed_count: int
    is_truncated: bool
    explanation: str

    def as_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            "prompt": self.prompt,
            "budget": self.budget,
            "total_tokens": self.total_tokens,
            "retained": list(self.retained),
            "removed_count": self.removed_count,
            "is_truncated": self.is_truncated,
            "explanation": self.explanation,
        }


class TokenBudgetPreflight:
    """Preflight check engine verifying prompt length against a token budget."""

    def __init__(self, budget: int) -> None:
        if not isinstance(budget, int) or isinstance(budget, bool):
            raise TypeError(f"Budget must be an int, got {type(budget).__name__}")
        if budget < 0:
            raise ValueError(f"Token budget cannot be negative: received {budget}")
        self.budget: int = budget

    def tokenize(self, prompt: str) -> List[str]:
        """Tokenize text using whitespace teaching approximation."""
        if not isinstance(prompt, str):
            raise TypeError(f"Prompt must be a string, got {type(prompt).__name__}")
        cleaned = prompt.strip()
        if not cleaned:
            return []
        return cleaned.split()

    def check(self, prompt: str) -> PreflightResult:
        """Execute preflight check and generate worked input-to-output explanation."""
        tokens = self.tokenize(prompt)
        total = len(tokens)

        if total <= self.budget:
            retained = tokens
            removed = 0
            is_truncated = False
            explanation = (
                f"Input has {total} token(s), which fits within budget {self.budget}. "
                f"All tokens are retained: {retained}."
            )
        else:
            retained = tokens[: self.budget]
            removed = total - self.budget
            is_truncated = True
            explanation = (
                f"Input has {total} tokens, exceeding configured budget {self.budget}. "
                f"Truncated {removed} token(s). Retained: {retained}."
            )

        return PreflightResult(
            prompt=prompt,
            budget=self.budget,
            total_tokens=total,
            retained=retained,
            removed_count=removed,
            is_truncated=is_truncated,
            explanation=explanation,
        )


# ==============================================================================
# Regression Test Runner
# ==============================================================================
def run_regression_suite() -> Tuple[bool, List[Dict[str, Any]]]:
    """Execute canonical regression fixtures verifying exact input-to-output behavior."""
    test_cases = [
        {
            "id": "regression_budget_3_truncation",
            "prompt": "one two three four",
            "budget": 3,
            "expected_retained": ["one", "two", "three"],
            "expected_removed": 1,
            "expected_truncated": True,
        },
        {
            "id": "regression_empty_input",
            "prompt": "",
            "budget": 3,
            "expected_retained": [],
            "expected_removed": 0,
            "expected_truncated": False,
        },
        {
            "id": "regression_within_budget",
            "prompt": "alpha beta",
            "budget": 5,
            "expected_retained": ["alpha", "beta"],
            "expected_removed": 0,
            "expected_truncated": False,
        },
    ]

    all_passed = True
    audit = []

    for tc in test_cases:
        engine = TokenBudgetPreflight(tc["budget"])
        res = engine.check(tc["prompt"])
        passed = (
            res.retained == tc["expected_retained"]
            and res.removed_count == tc["expected_removed"]
            and res.is_truncated == tc["expected_truncated"]
        )
        if not passed:
            all_passed = False

        audit.append({
            "test_id": tc["id"],
            "prompt": tc["prompt"],
            "budget": tc["budget"],
            "expected_retained": tc["expected_retained"],
            "actual_retained": res.retained,
            "expected_removed": tc["expected_removed"],
            "actual_removed": res.removed_count,
            "explanation": res.explanation,
            "status": "PASS" if passed else "FAIL",
        })

    return all_passed, audit


if __name__ == "__main__":
    print("=== Token-Budget Preflight Worked Example (R16-T047) ===")
    print(f"Notice: {TOKENIZER_NOTE}\n")

    preflight = TokenBudgetPreflight(3)
    sample_prompt = "one two three four"
    result = preflight.check(sample_prompt)

    print("Worked Input-to-Output Demonstration:")
    print(f"  Input Prompt:  {repr(sample_prompt)}")
    print(f"  Config Budget: {result.budget}")
    print(f"  Total Tokens:  {result.total_tokens}")
    print(f"  Retained:      {result.retained}")
    print(f"  Removed:       {result.removed_count}")
    print(f"  Explanation:   {result.explanation}\n")

    print("Running Regression Suite:")
    ok, records = run_regression_suite()
    for r in records:
        print(f"  [{r['status']}] {r['test_id']}: {r['actual_retained']} (removed: {r['actual_removed']})")
    print(f"\nRegression Suite Status: {'PASSED' if ok else 'FAILED'}")
