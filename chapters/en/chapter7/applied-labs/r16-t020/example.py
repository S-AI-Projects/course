"""Applied Lab R16-T020: Token-Budget Preflight — Scenario Assessment.

Task: R16-T020 (Issue #23)
Chapter: 7, Section 6 ("Training a causal language model from scratch")
Repository: https://github.com/S-AI-Projects/course

This module implements a deterministic local whitespace tokenization fixture
and token-budget preflight check for causal language model prompts, accompanied
by three applied scenario assessment questions with factual answers, rationales,
and executable verification checks:
1. Predict an output (code prompt truncation under budget constraints).
2. Diagnose a failure (negative budget and non-string type errors).
3. Choose a boundary policy (exact match and empty input handling).

SIMULATION NOTE / TEACHING APPROXIMATION:
The WhitespaceTokenizer in this lab is a pedagogical approximation, NOT the model's
real BPE tokenizer (such as the CodeParrot GPT-2 tokenizer). It does not compute subwords,
assign vocabulary IDs, or simulate GPU memory footprint or training latency.
"""

from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TokenBudgetResult:
    """Immutable result of a token-budget preflight check.

    Attributes:
        retained_tokens: Tokens retained within the configured budget.
        removed_tokens: Tokens truncated beyond the budget.
        removed_count: Count of removed (truncated) tokens.
        total_tokens: Total token count before truncation.
        budget: The configured maximum token budget.
        truncated: True if tokens were removed, False otherwise.
    """

    retained_tokens: List[str]
    removed_tokens: List[str]
    removed_count: int
    total_tokens: int
    budget: int
    truncated: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WhitespaceTokenizer:
    """Pedagogical whitespace tokenizer approximation."""

    is_teaching_approximation: bool = True

    def tokenize(self, text: str) -> List[str]:
        """Split text on whitespace boundaries into string tokens.

        Args:
            text: Input prompt string.

        Returns:
            List of string tokens (empty list if text is empty/whitespace).

        Raises:
            TypeError: If text is not a str.
        """
        if not isinstance(text, str):
            raise TypeError(f"text must be a str, got {type(text).__name__}")
        stripped = text.strip()
        if not stripped:
            return []
        return text.split()


def token_budget_preflight(
    text: str, budget: int, tokenizer: Optional[WhitespaceTokenizer] = None
) -> TokenBudgetResult:
    """Perform preflight budget check on prompt text.

    Args:
        text: Input prompt string.
        budget: Non-negative integer token budget.
        tokenizer: Optional tokenizer instance.

    Returns:
        TokenBudgetResult detailing retained tokens and explicit truncation report.

    Raises:
        TypeError: If text is not a str or budget is not an int (or is bool).
        ValueError: If budget is negative.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")
    if not isinstance(budget, int) or isinstance(budget, bool):
        raise TypeError(f"budget must be an int, got {type(budget).__name__}")
    if budget < 0:
        raise ValueError(f"budget cannot be negative, got {budget}")

    if tokenizer is None:
        tokenizer = WhitespaceTokenizer()

    tokens = tokenizer.tokenize(text)
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
# Contribution Focus: Three Applied Scenario Assessment Questions
# ============================================================================

def check_question_1_predict_output() -> bool:
    """Executable check for Question 1: Predict an output.

    Scenario: A Python code completion prompt with 5 whitespace tokens
    'def calculate_loss(predictions, targets): return loss' is checked against budget 4.
    """
    prompt = "def calculate_loss(predictions, targets): return loss"
    budget = 4
    res = token_budget_preflight(prompt, budget)

    expected_retained = ["def", "calculate_loss(predictions,", "targets):", "return"]
    expected_removed = ["loss"]

    return (
        res.retained_tokens == expected_retained
        and res.removed_tokens == expected_removed
        and res.removed_count == 1
        and res.total_tokens == 5
        and res.truncated is True
    )


def check_question_2_diagnose_failure() -> bool:
    """Executable check for Question 2: Diagnose a failure.

    Scenario: Verify that invalid input types and negative budgets are rejected
    with explicit exceptions (TypeError and ValueError) rather than silent truncation.
    """
    prompt = "import torch"
    caught_negative = False
    caught_type = False

    try:
        token_budget_preflight(prompt, -3)
    except ValueError as e:
        if "budget cannot be negative" in str(e):
            caught_negative = True

    try:
        token_budget_preflight(12345, 10)  # type: ignore
    except TypeError as e:
        if "text must be a str" in str(e):
            caught_type = True

    return caught_negative and caught_type


def check_question_3_boundary_policy() -> bool:
    """Executable check for Question 3: Choose a boundary policy.

    Scenario: Verify boundary handling when prompt length exactly equals budget
    and when input text is completely empty.
    """
    # 1. Exact match boundary
    exact_res = token_budget_preflight("one two three", 3)
    exact_ok = (
        exact_res.retained_tokens == ["one", "two", "three"]
        and exact_res.removed_count == 0
        and exact_res.truncated is False
    )

    # 2. Empty input boundary
    empty_res = token_budget_preflight("", 5)
    empty_ok = (
        empty_res.retained_tokens == []
        and empty_res.removed_count == 0
        and empty_res.truncated is False
        and empty_res.total_tokens == 0
    )

    return exact_ok and empty_ok


APPLIED_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "Q1_predict_output",
        "topic": "Predict an output",
        "question": (
            "Given prompt 'def calculate_loss(predictions, targets): return loss' (5 whitespace tokens) "
            "and a configured budget of 4, what are the retained tokens, removed count, and truncation flag?"
        ),
        "expected_answer": {
            "retained_tokens": ["def", "calculate_loss(predictions,", "targets):", "return"],
            "removed_tokens": ["loss"],
            "removed_count": 1,
            "truncated": True,
        },
        "rationale": (
            "In causal language model preflight checks, prefix prompt tokens are preserved in sequence order "
            "up to the configured context budget. The remaining token ('loss') is truncated and explicitly "
            "reported as 1 removed token so callers can log or reject over-budget generation requests."
        ),
        "check_fn": check_question_1_predict_output,
    },
    {
        "id": "Q2_diagnose_failure",
        "topic": "Diagnose a failure",
        "question": (
            "If an inference caller provides a negative budget (e.g. -3) or a non-string input (e.g. 12345), "
            "how does the preflight check respond, and why is this diagnostic necessary?"
        ),
        "expected_answer": {
            "negative_budget_error": "ValueError: budget cannot be negative",
            "invalid_text_error": "TypeError: text must be a str",
        },
        "rationale": (
            "A negative budget is mathematically invalid for causal sequence context windows and indicates a "
            "caller configuration error. Non-string inputs cannot undergo text tokenization. Raising explicit "
            "exceptions immediately prevents silent data corruption or downstream PyTorch tensor dimension errors."
        ),
        "check_fn": check_question_2_diagnose_failure,
    },
    {
        "id": "Q3_boundary_policy",
        "topic": "Choose a boundary policy",
        "question": (
            "What policy governs prompt truncation when token count exactly equals the budget, "
            "or when prompt text is completely empty?"
        ),
        "expected_answer": {
            "exact_match_policy": "Retain all tokens, removed_count=0, truncated=False",
            "empty_input_policy": "Retain empty list [], removed_count=0, truncated=False",
        },
        "rationale": (
            "When token count is less than or equal to the budget, zero truncation occurs. For empty input text, "
            "no tokens are generated, so zero tokens are retained and zero removed, without raising false-positive "
            "truncation warnings."
        ),
        "check_fn": check_question_3_boundary_policy,
    },
]


def evaluate_all_questions() -> Tuple[bool, List[Dict[str, Any]]]:
    """Execute all applied question verification checks."""
    all_passed = True
    audit = []
    for q in APPLIED_QUESTIONS:
        passed = q["check_fn"]()
        if not passed:
            all_passed = False
        audit.append({
            "id": q["id"],
            "topic": q["topic"],
            "passed": passed,
            "rationale": q["rationale"],
        })
    return all_passed, audit


def main() -> None:
    print("=== Token-Budget Preflight — Scenario Assessment (Task R16-T020) ===")
    print("NOTE: Teaching approximation only — not a real model tokenizer.\n")

    # 1. Core Contract Verification
    res = token_budget_preflight("one two three four", 3)
    print("--- Core Contract Verification ---")
    print(f"  Input: 'one two three four', Budget: 3")
    print(f"  Retained: {res.retained_tokens}")
    print(f"  Removed:  {res.removed_tokens} (count={res.removed_count})")
    print(f"  Truncated: {res.truncated}\n")

    # 2. Applied Questions Assessment
    print("--- Applied Assessment Questions ---")
    all_ok, audit = evaluate_all_questions()
    for item in audit:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"[{status}] {item['topic']} ({item['id']})")
        print(f"       Rationale: {item['rationale'][:85]}...\n")

    print("=" * 70)
    print(f"Assessment Summary: {'ALL CHECKS PASSED' if all_ok else 'FAILURES DETECTED'}")


if __name__ == "__main__":
    main()
