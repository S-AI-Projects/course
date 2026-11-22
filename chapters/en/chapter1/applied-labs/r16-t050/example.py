#!/usr/bin/env python3
"""
Applied Lab R16-T050: Token-Budget Preflight — Scenario Assessment.

This module implements a deterministic token-budget preflight check with an applied
scenario assessment suite connecting directly to Chapter 1, Section 1
("Introduction" [introduction]).

Teaching Approximation:
The tokenizer used in this module is a local whitespace-splitting teaching approximation
(`prompt.strip().split()`). It is NOT the model's real subword tokenizer (e.g. WordPiece, BPE)
and does not insert special tokens ([CLS]/[SEP]) or map vocabulary IDs.

Contract:
- Configured budget N (integer >= 0).
- Budget 3 with "one two three four" retains ['one', 'two', 'three'] and reports 1 removed token.
- Empty input retains [] and reports 0 removed tokens.
- Negative budgets (budget < 0) are rejected with ValueError.

Scenario Assessment Focus:
Add three applied questions about the local example:
1. Predict an output: When prompt is "apple banana cherry date" with budget 2,
   what tokens are retained and how many are removed?
2. Diagnose a failure: When budget is passed as -3, what exception is raised and why?
3. Choose a boundary policy: When prompt is empty string "" with budget 3,
   what should be retained, what is the truncation flag, and why?
Each question includes a lesson-tied rationale and an executable check verifying the factual answer.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple


TOKENIZER_NOTE = (
    "[TEACHING APPROXIMATION] Whitespace splitting is used here solely as a simple, "
    "deterministic educational proxy for tokenization. It is NOT a production model "
    "tokenizer (e.g. BPE, WordPiece) and does not reflect subword fragmentation, "
    "vocabulary lookup, or special tokens."
)


@dataclass(frozen=True)
class PreflightReport:
    """Preflight check report for a prompt evaluated against a token budget."""

    prompt: str
    budget: int
    total_tokens: int
    retained: List[str]
    removed_count: int
    is_truncated: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "budget": self.budget,
            "total_tokens": self.total_tokens,
            "retained": list(self.retained),
            "removed_count": self.removed_count,
            "is_truncated": self.is_truncated,
        }


class TokenBudgetPreflight:
    """Engine to check prompt length against a configured token budget."""

    def __init__(self, budget: int) -> None:
        if not isinstance(budget, int) or isinstance(budget, bool):
            raise TypeError(f"Budget must be an int, got {type(budget).__name__}")
        if budget < 0:
            raise ValueError(f"Token budget cannot be negative: received {budget}")
        self.budget: int = budget

    def tokenize(self, prompt: str) -> List[str]:
        """Tokenize text using whitespace splitting (teaching approximation)."""
        if not isinstance(prompt, str):
            raise TypeError(f"Prompt must be a string, got {type(prompt).__name__}")
        cleaned = prompt.strip()
        if not cleaned:
            return []
        return cleaned.split()

    def check(self, prompt: str) -> PreflightReport:
        """Run preflight check against budget and report retained tokens and truncation."""
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
# Three Applied Scenario Questions with Executable Checks
# ==============================================================================
APPLIED_SCENARIO_QUESTIONS = [
    {
        "question_id": "Q1_predict_output",
        "topic": "Predict an output",
        "question": (
            "Given prompt 'apple banana cherry date' and budget 2, "
            "what tokens are retained and how many tokens are removed?"
        ),
        "expected_factual_answer": {
            "retained": ["apple", "banana"],
            "removed_count": 2,
            "is_truncated": True,
        },
        "rationale": (
            "Per Chapter 1 tokenization and inference prefill principles, "
            "the prompt is split into 4 whitespace tokens. Since budget is 2, the earliest "
            "2 tokens ('apple', 'banana') are retained and 4 - 2 = 2 tokens are truncated."
        ),
        "executable_check": lambda: (
            TokenBudgetPreflight(2).check("apple banana cherry date").as_dict()
        ),
    },
    {
        "question_id": "Q2_diagnose_failure",
        "topic": "Diagnose a failure",
        "question": (
            "When instantiating TokenBudgetPreflight with negative budget -3, "
            "what failure occurs and why?"
        ),
        "expected_factual_answer": {
            "exception_type": "ValueError",
            "message_contains": "cannot be negative",
        },
        "rationale": (
            "A negative token capacity is mathematically undefined for sequence limits; "
            "the preflight engine validates budget >= 0 and raises ValueError to protect "
            "downstream model memory allocation."
        ),
        "executable_check": lambda: (
            _run_negative_budget_check(-3)
        ),
    },
    {
        "question_id": "Q3_boundary_policy",
        "topic": "Choose a boundary policy",
        "question": (
            "When prompt is an empty string '' with budget 3, "
            "what is the boundary policy regarding retained tokens and truncation flag?"
        ),
        "expected_factual_answer": {
            "retained": [],
            "removed_count": 0,
            "is_truncated": False,
        },
        "rationale": (
            "Empty input contains 0 tokens, which does not exceed budget 3. "
            "The boundary policy cleanly retains an empty list without reporting truncation "
            "or throwing false positive errors."
        ),
        "executable_check": lambda: (
            TokenBudgetPreflight(3).check("").as_dict()
        ),
    },
]


def _run_negative_budget_check(budget: int) -> Dict[str, Any]:
    try:
        TokenBudgetPreflight(budget)
        return {"raised": False}
    except ValueError as e:
        return {
            "raised": True,
            "exception_type": "ValueError",
            "message": str(e),
            "message_contains": "cannot be negative" in str(e),
        }
    except Exception as e:
        return {"raised": True, "exception_type": type(e).__name__}


def execute_scenario_assessments() -> Tuple[bool, List[Dict[str, Any]]]:
    """Execute all scenario assessment questions and verify their factual answers."""
    all_passed = True
    audit = []

    for q in APPLIED_SCENARIO_QUESTIONS:
        qid = q["question_id"]
        check_fn = q["executable_check"]
        exp = q["expected_factual_answer"]

        actual = check_fn()

        if qid == "Q1_predict_output":
            passed = (
                actual["retained"] == exp["retained"]
                and actual["removed_count"] == exp["removed_count"]
                and actual["is_truncated"] == exp["is_truncated"]
            )
        elif qid == "Q2_diagnose_failure":
            passed = (
                actual.get("exception_type") == exp["exception_type"]
                and actual.get("message_contains") is True
            )
        elif qid == "Q3_boundary_policy":
            passed = (
                actual["retained"] == exp["retained"]
                and actual["removed_count"] == exp["removed_count"]
                and actual["is_truncated"] == exp["is_truncated"]
            )
        else:
            passed = False

        if not passed:
            all_passed = False

        audit.append({
            "question_id": qid,
            "topic": q["topic"],
            "passed": passed,
            "rationale": q["rationale"],
            "expected": exp,
            "actual": actual,
        })

    return all_passed, audit


if __name__ == "__main__":
    print("=== Token-Budget Preflight & Scenario Assessment (R16-T050) ===")
    print(f"Notice: {TOKENIZER_NOTE}\n")

    # Contract case
    preflight = TokenBudgetPreflight(3)
    rep = preflight.check("one two three four")
    print(f"Contract Normal: {rep.as_dict()}")
    print(f"Contract Empty:  {preflight.check('').as_dict()}\n")

    print("Running Scenario Assessment Checks:")
    ok, records = execute_scenario_assessments()
    for r in records:
        print(f"  [{'PASS' if r['passed'] else 'FAIL'}] {r['question_id']} ({r['topic']})")
        print(f"    Rationale: {r['rationale']}")
    print(f"\nAll Scenario Assessments Passed: {ok}")
