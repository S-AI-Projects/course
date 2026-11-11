"""Applied Lab R16-T017: Worked Decision Example for Introduction (Chapter 6).

Task: R16-T017 (Issue #20)
Chapter: 6, Section 1 ("Introduction")
Repository: https://github.com/S-AI-Projects/course

This module implements an original worked decision example and automated checker
for tokenizer selection and training strategy, based on the concepts in Chapter 6:
- When pretraining a language model from scratch on a new domain or language
  (e.g., Python code or Japanese text), an existing pretrained English tokenizer
  is suboptimal; a brand new tokenizer must be trained on the target corpus.
- When fine-tuning on a task matching the pretrained checkpoint domain, reusing
  the pretrained tokenizer preserves learned token embeddings.
- Missing or empty corpus inputs are rejected prior to training.

SIMULATION NOTE / PEDAGOGICAL SCOPE:
This is a deterministic offline decision engine and preflight checker implemented
using only the Python 3 standard library. It models the decision logic and schema
checks of tokenizer training pipelines without invoking GPU hardware, heavy native
Rust tokenizers builds, or external cloud endpoints.
"""

import copy
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# Standard Decision Outcomes
# ============================================================================

TRAIN_NEW_TOKENIZER = "TRAIN_NEW_TOKENIZER"
REUSE_PRETRAINED_TOKENIZER = "REUSE_PRETRAINED_TOKENIZER"
REJECT_MISSING_CORPUS = "REJECT_MISSING_CORPUS"
REJECT_EMPTY_CORPUS = "REJECT_EMPTY_CORPUS"
REJECT_INVALID_MODE = "REJECT_INVALID_MODE"

VALID_DECISIONS = {
    TRAIN_NEW_TOKENIZER,
    REUSE_PRETRAINED_TOKENIZER,
    REJECT_MISSING_CORPUS,
    REJECT_EMPTY_CORPUS,
    REJECT_INVALID_MODE,
}


def evaluate_scenario(facts: Optional[Dict[str, Any]]) -> str:
    """Evaluate candidate input facts and determine the tokenizer pipeline decision.

    Args:
        facts: Dictionary containing project input facts:
            - 'training_mode': 'scratch' (from scratch) or 'fine_tune'.
            - 'corpus_domain': Target corpus domain/language (e.g. 'python_code', 'japanese').
            - 'pretrained_domain': Domain of reference checkpoint (e.g. 'english').
            - 'corpus_texts': List of text sample strings or None.

    Returns:
        Decision string from VALID_DECISIONS.
    """
    if not facts or not isinstance(facts, dict):
        return REJECT_MISSING_CORPUS

    if "corpus_texts" not in facts or facts["corpus_texts"] is None:
        return REJECT_MISSING_CORPUS

    corpus = facts["corpus_texts"]
    if not isinstance(corpus, list):
        return REJECT_MISSING_CORPUS

    if len(corpus) == 0:
        return REJECT_EMPTY_CORPUS

    # Check if all samples are empty or whitespace
    if all(not isinstance(s, str) or not s.strip() for s in corpus):
        return REJECT_EMPTY_CORPUS

    mode = facts.get("training_mode")
    if mode not in ("scratch", "fine_tune"):
        return REJECT_INVALID_MODE

    # If training from scratch:
    # Chapter 6 Section 1: Pretraining from scratch requires training a new tokenizer
    # optimized for the vocabulary and character distribution of the target corpus.
    if mode == "scratch":
        return TRAIN_NEW_TOKENIZER

    # If fine-tuning:
    # If target domain matches the pretrained domain, reuse existing tokenizer
    corpus_domain = facts.get("corpus_domain", "english")
    pretrained_domain = facts.get("pretrained_domain", "english")
    if corpus_domain == pretrained_domain:
        return REUSE_PRETRAINED_TOKENIZER

    # Cross-domain fine-tuning requires a new or adapted tokenizer
    return TRAIN_NEW_TOKENIZER


# ============================================================================
# Published Decision Table (Three Core Scenarios + Boundaries)
# ============================================================================

SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "normal_scratch_domain_shift",
        "name": "Normal Scenario: Pretraining from Scratch on Python Code",
        "input_facts": {
            "training_mode": "scratch",
            "corpus_domain": "python_code",
            "pretrained_domain": "english",
            "corpus_texts": [
                "def calculate_loss(predictions, targets):\n    return torch.mean((predictions - targets) ** 2)",
                "import os\nfrom transformers import AutoTokenizer",
            ],
        },
        "expected_decision": TRAIN_NEW_TOKENIZER,
        "rationale": (
            "Directly implements Chapter 6, Section 1 ('Introduction'): When pretraining a model from scratch "
            "on a corpus from another domain or language (such as Python code or Japanese), using a tokenizer "
            "pretrained on standard English is suboptimal because whitespace, indentation, and syntax symbols "
            "have completely different semantics. The pipeline must train a brand new tokenizer on the target corpus."
        ),
    },
    {
        "id": "boundary_minimal_single_sample",
        "name": "Boundary Scenario: Minimal Valid Single-Sample Corpus",
        "input_facts": {
            "training_mode": "scratch",
            "corpus_domain": "domain_specific",
            "pretrained_domain": "english",
            "corpus_texts": ["minimal valid token stream for iterator initialization"],
        },
        "expected_decision": TRAIN_NEW_TOKENIZER,
        "rationale": (
            "Illustrates the minimal valid boundary case: A corpus containing exactly one non-empty string. "
            "While minimal in size, it meets the structural requirement of a valid text iterator for tokenizer "
            "training without raising missing-data or empty-iterator exceptions."
        ),
    },
    {
        "id": "missing_information_null_corpus",
        "name": "Missing-Information Scenario: Null Corpus Iterator",
        "input_facts": {
            "training_mode": "scratch",
            "corpus_domain": "python_code",
            "pretrained_domain": "english",
            "corpus_texts": None,
        },
        "expected_decision": REJECT_MISSING_CORPUS,
        "rationale": (
            "Illustrates missing-information failure: Tokenizer training algorithms require text data to compute "
            "subword frequencies and discover vocabulary merges. A null or missing corpus provides no text, so "
            "the preflight checker must reject the request before invoking tokenizer training routines."
        ),
    },
    {
        "id": "boundary_matching_domain_fine_tune",
        "name": "Boundary Scenario: Standard Fine-Tuning on Matching Domain",
        "input_facts": {
            "training_mode": "fine_tune",
            "corpus_domain": "english",
            "pretrained_domain": "english",
            "corpus_texts": [
                "Hugging Face course provides excellent tutorials on Natural Language Processing.",
            ],
        },
        "expected_decision": REUSE_PRETRAINED_TOKENIZER,
        "rationale": (
            "Recaps the distinction highlighted in Chapter 6 Section 1: In standard fine-tuning where the downstream "
            "task uses the same language as the pretrained checkpoint, reusing the model's pretrained tokenizer "
            "is necessary to retain learned token embeddings and model architecture compatibility."
        ),
    },
    {
        "id": "missing_information_empty_corpus",
        "name": "Missing-Information Scenario: Empty List Corpus",
        "input_facts": {
            "training_mode": "scratch",
            "corpus_domain": "python_code",
            "pretrained_domain": "english",
            "corpus_texts": [],
        },
        "expected_decision": REJECT_EMPTY_CORPUS,
        "rationale": (
            "An empty list contains 0 text samples, providing zero vocabulary information. "
            "The checker rejects empty corpora before training."
        ),
    },
]


def check_decision_table(
    scenarios: List[Dict[str, Any]],
) -> Tuple[bool, List[Dict[str, Any]]]:
    """Verify that actual evaluator decisions match published expectations.

    Args:
        scenarios: List of scenario specification dictionaries.

    Returns:
        Tuple of (all_passed: bool, detailed_results: List[Dict[str, Any]]).
    """
    all_passed = True
    results = []

    for item in scenarios:
        scenario_id = item["id"]
        facts = item["input_facts"]
        expected = item["expected_decision"]
        actual = evaluate_scenario(facts)
        passed = (actual == expected)
        if not passed:
            all_passed = False

        results.append({
            "id": scenario_id,
            "name": item["name"],
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "rationale": item["rationale"],
        })

    return all_passed, results


def run_regression_test(scenario: Dict[str, Any]) -> bool:
    """Execute a single scenario as an exact input-to-output regression test.

    Args:
        scenario: Scenario specification dictionary.

    Returns:
        True if actual decision matches expected decision, False otherwise.
    """
    actual = evaluate_scenario(scenario.get("input_facts"))
    return actual == scenario.get("expected_decision")


def main() -> None:
    print("=== Worked Decision Table: Chapter 6 Section 1 (Introduction) ===")
    print("Task: R16-T017 | Decision Engine & Regression Checker\n")

    passed, audit_results = check_decision_table(SCENARIOS)

    for item in audit_results:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"[{status}] {item['name']}")
        print(f"       Expected:  {item['expected']}")
        print(f"       Actual:    {item['actual']}")
        print(f"       Rationale: {item['rationale'][:85]}...\n")

    print("=" * 70)
    print(f"Audit Summary: {'ALL PASSED' if passed else 'FAILURES DETECTED'}")


if __name__ == "__main__":
    main()
