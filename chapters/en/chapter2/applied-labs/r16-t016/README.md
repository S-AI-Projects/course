# R16-T016: Token-Budget Preflight — Refactor the Teaching Example

**Task**: R16-T016 · Issue #19  
**Chapter**: 2 — Section 4: "Tokenizers"  
**Branch**: `student/e26b07f0816/R06-T006`  
**Type**: Refactor the teaching example

---

## Overview

This applied lab extends the discussion on tokenization boundaries in Chapter 2, Section 4 by introducing a deterministic preflight check that validates prompt length against a configured token budget prior to model invocation.

In production transformer applications, sending prompts that exceed model context windows causes unhandled truncation, degraded completions, or API budget overruns. Preflight checking ensures resource limits are enforced deterministically and reported explicitly.

---

## Refactoring Focus

The primary software design focus of this task is **extracting a named responsibility** from a coupled baseline:

1. **Baseline (`token_budget_preflight_baseline`)**:
   A monolithic implementation where text splitting, budget clamping, and result reporting are tightly coupled in one routine.
2. **Extracted Responsibilities**:
   - `WhitespaceTokenizer`: Dedicated component responsible strictly for string tokenization.
   - `TokenBudgetEnforcer`: Extracted named responsibility dedicated strictly to budget boundary enforcement and truncation accounting.
3. **Public Contract (`token_budget_preflight`)**:
   Orchestrates the modular components while maintaining strict behavioural and interface equivalence with the baseline. This equivalence is verified across the full fixture suite.

---

## Contract

| Scenario | Input | Expected Output |
|---|---|---|
| **Budget 3 with 4 tokens** | `text="one two three four"`, `budget=3` | `retained_tokens=["one", "two", "three"]`, `removed_count=1`, `removed_tokens=["four"]`, `truncated=True` |
| **Empty input** | `text=""`, `budget=3` | `retained_tokens=[]`, `removed_count=0`, `removed_tokens=[]`, `truncated=False` |
| **Whitespace-only input** | `text="   \t\n  "`, `budget=3` | `retained_tokens=[]`, `removed_count=0`, `truncated=False` |
| **Exact budget match** | `text="one two three"`, `budget=3` | `retained_tokens=["one", "two", "three"]`, `removed_count=0`, `truncated=False` |
| **Budget exceeds tokens** | `text="one two"`, `budget=5` | `retained_tokens=["one", "two"]`, `removed_count=0`, `truncated=False` |
| **Zero budget** | `text="one two three"`, `budget=0` | `retained_tokens=[]`, `removed_count=3`, `truncated=True` |
| **Negative budget** | `text="one two"`, `budget=-1` | Raises `ValueError` ("budget cannot be negative") |
| **Invalid text type** | `text=123`, `budget=3` | Raises `TypeError` ("text must be a str") |
| **Invalid budget type** | `text="prompt"`, `budget="3"` | Raises `TypeError` ("budget must be an int") |

---

## Files

| File | Purpose |
|---|---|
| `example.py` | Baseline and refactored preflight implementation with `TokenBudgetResult`, `WhitespaceTokenizer`, and `TokenBudgetEnforcer` |
| `test_example.py` | 15 unit tests covering contract specifications, boundary scenarios, type validation, equivalence, and deliberate failure detection |
| `README.md` | Lab documentation, contract specification, and architectural explanation |

---

## Running

```bash
# Run unit tests from repository root:
python3 -m unittest discover \
  -s chapters/en/chapter2/applied-labs/r16-t016 \
  -p "test_*.py" -v

# Run the runnable demo:
python3 chapters/en/chapter2/applied-labs/r16-t016/example.py
```

---

## Simulation and Teaching Approximation Limitations

> **SIMULATION NOTE**: The tokenizer in this lab is a **teaching approximation**, NOT a real model tokenizer:
>
> - **Whitespace Splitting Only**: It splits on ASCII whitespace and does not perform subword segmentation (such as BPE, WordPiece, or SentencePiece).
> - **No Vocabulary Mapping**: It does not assign numerical token IDs, special tokens (`[CLS]`, `[SEP]`, `<eos>`), or attention masks.
> - **No Hardware or Cloud Claims**: This module runs offline using only the Python 3 standard library. It makes no claims regarding GPU memory footprint, KV-cache utilization, or cloud provider inference latency.
>
> Real transformer tokenization requires loading pretrained tokenizer assets from Hugging Face Hub, as demonstrated in Chapter 2, Section 4.

---

## Lesson Link

See the linked section at the end of
[`chapters/en/chapter2/4.mdx`](../../4.mdx)
for the textbook integration, invocations, and conceptual connections.
