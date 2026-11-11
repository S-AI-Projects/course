# R16-T020: Token-Budget Preflight — Scenario Assessment

**Task**: R16-T020 · Issue #23  
**Chapter**: 7 — Section 6: "Training a causal language model from scratch"  
**Branch**: `student/e26b07f0816-R10-T010`  
**Type**: Scenario assessment

---

## Overview

This applied lab extends Chapter 7, Section 6 ("Training a causal language model from scratch") by providing a deterministic token-budget preflight check for causal model prompts (e.g. CodeParrot code generation prompts), coupled with three applied assessment questions:
1. **Predict an output**: Calculate truncation behavior on code prompt inputs.
2. **Diagnose a failure**: Explain why negative budgets and non-string types must trigger explicit exceptions.
3. **Choose a boundary policy**: Define the system behavior on exact matches and empty prompt inputs.

---

## Contract

| Scenario | Input | Configured Budget | Retained Tokens | Removed Count | Truncated? |
|---|---|---|---|---|---|
| **Core Contract** | `"one two three four"` | 3 | `['one', 'two', 'three']` | 1 (`['four']`) | `True` |
| **Empty Input** | `""` | 3 | `[]` | 0 | `False` |
| **Whitespace Input** | `"   \t\n  "` | 3 | `[]` | 0 | `False` |
| **Exact Fit** | `"one two three"` | 3 | `['one', 'two', 'three']` | 0 | `False` |
| **Generous Budget** | `"one two"` | 5 | `['one', 'two']` | 0 | `False` |
| **Zero Budget** | `"alpha beta gamma"` | 0 | `[]` | 3 | `True` |
| **Negative Budget** | `"sample prompt"` | -1 | *Raises `ValueError`* | — | — |

---

## Three Applied Scenario Assessment Questions

### Question 1: Predict an Output
- **Question**: Given prompt `'def calculate_loss(predictions, targets): return loss'` (5 whitespace tokens) and a configured budget of 4, what are the retained tokens, removed count, and truncation flag?
- **Factual Answer**:
  - `retained_tokens`: `["def", "calculate_loss(predictions,", "targets):", "return"]`
  - `removed_tokens`: `["loss"]`
  - `removed_count`: `1`
  - `truncated`: `True`
- **Rationale**: In causal language modeling, prompt prefix tokens are preserved up to the available context window budget. The trailing token is truncated and explicitly reported so callers can handle context overflows deterministically.
- **Executable Check**: `check_question_1_predict_output()`

### Question 2: Diagnose a Failure
- **Question**: If an inference caller provides a negative budget (e.g. `-3`) or a non-string input (e.g. `12345`), how does the preflight check respond, and why is this diagnostic necessary?
- **Factual Answer**:
  - Negative budget raises `ValueError: budget cannot be negative`.
  - Non-string input raises `TypeError: text must be a str`.
- **Rationale**: A negative budget is mathematically impossible for sequence context windows. Non-string inputs cannot undergo text tokenization. Rejecting with explicit exceptions prevents silent pipeline corruption and downstream tensor shape errors.
- **Executable Check**: `check_question_2_diagnose_failure()`

### Question 3: Choose a Boundary Policy
- **Question**: What policy governs prompt truncation when token count exactly equals the budget, or when prompt text is completely empty?
- **Factual Answer**:
  - Exact match: Retain all tokens, `removed_count=0`, `truncated=False`.
  - Empty input: Retain empty list `[]`, `removed_count=0`, `truncated=False`.
- **Rationale**: When token count $\le$ budget, zero truncation occurs and no tokens are dropped. Empty inputs contain zero content tokens and require no prompt truncation.
- **Executable Check**: `check_question_3_boundary_policy()`

---

## Files

| File | Purpose |
|---|---|
| `example.py` | `token_budget_preflight()`, `WhitespaceTokenizer`, applied questions, and executable checks |
| `test_example.py` | 14 unit tests covering core contract, applied question checks, boundary policies, and deliberate failure detection |
| `README.md` | Lab documentation, contract specifications, and scenario assessment questions |

---

## Running

```bash
# Run unit tests from repository root:
python3 -m unittest discover \
  -s chapters/en/chapter7/applied-labs/r16-t020 \
  -p "test_*.py" -v

# Run the demonstration and question assessment:
python3 chapters/en/chapter7/applied-labs/r16-t020/example.py
```

---

## Simulation and Pedagogical Limitations

> **SIMULATION NOTE**: The tokenizer in this lab is a **teaching approximation** (whitespace-based), NOT a real subword/BPE model tokenizer (such as CodeParrot GPT-2). It splits on whitespace, does not produce numerical token IDs or embeddings, and makes no unsupported claims regarding GPU memory, training throughput, or model accuracy.

---

## Lesson Link

See the linked section at the end of
[`chapters/en/chapter7/6.mdx`](../../6.mdx)
for textbook integration and examples.
