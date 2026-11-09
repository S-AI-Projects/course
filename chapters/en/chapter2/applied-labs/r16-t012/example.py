"""Applied Lab R16-T012: Worked Decision Example for Basic Usage Completed.

This module implements a deterministic decision engine and checker for Transformer
model input preprocessing based on Chapter 2 ("Using Transformers"):
- Normal scenario: Multiple sequences of differing lengths require padding and attention mask.
- Boundary scenario (smallest valid input): Minimal single-token sequence in 2D batch [1, 1]
  proceeds directly without padding.
- Missing-information scenario: Empty or missing sequence inputs are rejected.
- Additional boundary checks: Unbatched 1D inputs and sequences exceeding max length.
"""

from typing import Any, Dict, List, Optional, Tuple

# Standard decision outcomes
PAD_AND_MASK = "PAD_AND_MASK"
VALID_DIRECT_INFERENCE = "VALID_DIRECT_INFERENCE"
REJECT_MISSING_INPUT = "REJECT_MISSING_INPUT"
REJECT_UNBATCHED = "REJECT_UNBATCHED"
REJECT_EXCEEDS_MAX_LENGTH = "REJECT_EXCEEDS_MAX_LENGTH"

VALID_DECISIONS = {
    PAD_AND_MASK,
    VALID_DIRECT_INFERENCE,
    REJECT_MISSING_INPUT,
    REJECT_UNBATCHED,
    REJECT_EXCEEDS_MAX_LENGTH,
}


def evaluate_scenario(facts: Optional[Dict[str, Any]]) -> str:
    """Evaluate candidate input facts and determine the required pipeline decision.

    Args:
        facts (Optional[Dict[str, Any]]): Dictionary containing input facts:
            - 'sequence_ids': List representing the sequence tokens.
            - 'max_model_length': Optional maximum context length (default 512).

    Returns:
        str: Decision label from VALID_DECISIONS.
    """
    if not facts or "sequence_ids" not in facts or facts["sequence_ids"] is None:
        return REJECT_MISSING_INPUT

    seqs = facts["sequence_ids"]
    if not isinstance(seqs, list) or len(seqs) == 0:
        return REJECT_MISSING_INPUT

    # Section 5 rule: Transformers models expect a batch dimension (2D list)
    if not isinstance(seqs[0], list):
        return REJECT_UNBATCHED

    lengths = [len(s) for s in seqs]

    # Empty sequence inside batch
    if any(length == 0 for length in lengths):
        return REJECT_MISSING_INPUT

    max_len = facts.get("max_model_length", 512)
    if any(length > max_len for length in lengths):
        return REJECT_EXCEEDS_MAX_LENGTH

    # Unequal lengths require rectangular padding and an attention mask
    if len(set(lengths)) > 1:
        return PAD_AND_MASK

    # Uniform lengths within context limit can proceed directly
    return VALID_DIRECT_INFERENCE


# Published decision table
SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "normal_unequal_batch",
        "name": "Normal Scenario: Unequal Sequence Batch",
        "input_facts": {
            "sequence_ids": [
                [101, 2054, 2003, 102],  # Length 4
                [101, 7592, 102],        # Length 3
            ],
            "max_model_length": 512,
        },
        "expected_decision": PAD_AND_MASK,
        "rationale": (
            "Recaps Chapter 2 Section 5 ('Handling multiple sequences'): Transformer models "
            "require rectangular input tensors. When batching sequences of different lengths "
            "(4 and 3), the shorter sequence must be padded to the batch max length with pad token ID, "
            "and an attention mask (1s for real tokens, 0s for pad tokens) must be provided so "
            "self-attention layers ignore padding."
        ),
    },
    {
        "id": "boundary_smallest_valid",
        "name": "Boundary Scenario: Smallest Valid Input (Minimal Boundary)",
        "input_facts": {
            "sequence_ids": [[101]],  # Batch size 1, sequence length 1
            "max_model_length": 512,
        },
        "expected_decision": VALID_DIRECT_INFERENCE,
        "rationale": (
            "Illustrates the minimal valid boundary case: A single token sequence enclosed in a 2D batch "
            "[1, 1]. All sequences in the batch have uniform length (1), sequence length is >= 1, "
            "and length is <= max_model_length (512). The tensor is already rectangular and valid for direct forward pass; "
            "no padding or pad-masking is necessary."
        ),
    },
    {
        "id": "missing_information",
        "name": "Missing-Information Scenario: None or Empty Input",
        "input_facts": {
            "sequence_ids": None,
            "max_model_length": 512,
        },
        "expected_decision": REJECT_MISSING_INPUT,
        "rationale": (
            "Illustrates invalid missing information: Tokenization pipeline requires at least one token sequence "
            "to construct input tensors. A null or empty input provides no tokens from which to construct a 2D tensor."
        ),
    },
    {
        "id": "boundary_unbatched_1d",
        "name": "Boundary Scenario: Unbatched 1D Sequence (Dimension Boundary)",
        "input_facts": {
            "sequence_ids": [101, 2054, 102],  # 1D list missing outer batch dimension
            "max_model_length": 512,
        },
        "expected_decision": REJECT_UNBATCHED,
        "rationale": (
            "Directly reflects the IndexError demonstrated in Section 5 ('Models expect a batch of inputs'). "
            "Passing a 1D tensor [seq_len] instead of a 2D tensor [batch_size, seq_len] causes dimension out of range."
        ),
    },
    {
        "id": "boundary_exact_max_context",
        "name": "Boundary Scenario: Exact Maximum Model Context (Upper Boundary)",
        "input_facts": {
            "sequence_ids": [[101] * 512],  # Exactly 512 tokens
            "max_model_length": 512,
        },
        "expected_decision": VALID_DIRECT_INFERENCE,
        "rationale": (
            "Exact boundary decision: At length exactly equal to max_model_length (512), the sequence fits within "
            "the context window and can be processed without truncation."
        ),
    },
    {
        "id": "boundary_exceeding_max_context",
        "name": "Boundary Scenario: Exceeding Maximum Model Context (Upper Boundary + 1)",
        "input_facts": {
            "sequence_ids": [[101] * 513],  # 513 tokens
            "max_model_length": 512,
        },
        "expected_decision": REJECT_EXCEEDS_MAX_LENGTH,
        "rationale": (
            "Upper boundary failure: Exceeding max_model_length by even 1 token (513 > 512) violates positional "
            "embedding limits and requires truncation before model input."
        ),
    },
]


def check_decision_table(scenarios: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
    """Verify that actual evaluator decisions match published expectations.

    Args:
        scenarios (List[Dict[str, Any]]): List of scenario records.

    Returns:
        Tuple[bool, List[Dict[str, Any]]]: (all_passed, detailed_results)
    """
    all_passed = True
    results = []

    for item in scenarios:
        scenario_id = item["id"]
        facts = item["input_facts"]
        expected = item["expected_decision"]
        actual = evaluate_scenario(facts)
        passed = actual == expected
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


if __name__ == "__main__":
    print("Evaluating Worked Decision Table for Chapter 2:")
    print("=" * 60)
    success, audit_results = check_decision_table(SCENARIOS)
    for res in audit_results:
        status = "PASS" if res["passed"] else "FAIL"
        print(f"[{status}] {res['name']}")
        print(f"       Expected: {res['expected']}")
        print(f"       Actual:   {res['actual']}")
        print(f"       Rationale: {res['rationale'][:80]}...\n")

    print("=" * 60)
    print(f"Overall Decision Table Verification: {'PASSED' if success else 'FAILED'}")
