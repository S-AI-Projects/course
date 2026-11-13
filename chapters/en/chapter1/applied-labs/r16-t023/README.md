# Applied Lab R16-T023: Token-Budget Preflight Comparison

A minimal, runnable concept lab demonstrating prompt token budgeting, preflight checks, and truncation reporting, complementing [Chapter 1 ("Introduction")](../../1.mdx).

---

## 1. Concept and Lesson Connection

In [Chapter 1 ("Introduction")](../../1.mdx), large language models (LLMs) and Transformer architectures are introduced as language processing systems that consume text converted into token sequences.

Every model deployment or inference API enforces strict **resource constraints and context window limits** (token budgets). When a prompt exceeds the configured budget:
- The system must either reject the prompt or truncate it.
- **Preflight checks** inspect prompt token counts before dispatching requests, explicitly reporting retained tokens and removed tokens to maintain transparency and avoid silent truncation errors.

> [!NOTE]
> **Tokenizer Teaching Approximation:**
> The tokenizer implemented in this lab is a deterministic whitespace-based educational approximation (`prompt.strip().split()`). It illustrates token counting and budget enforcement concepts without requiring heavy external tokenizer dependencies. Real production LLMs utilize learned subword tokenizers (e.g. Byte-Pair Encoding or WordPiece, as explored in Chapters 2 and 6) that segment text into subword units.

---

## 2. Comparing Two Approaches

This lab implements and validates two complementary approaches across identical inputs:

| Aspect | Approach 1: Engine Class (`TokenBudgetPreflight`) | Approach 2: Functional Reference (`reference_preflight_calc`) |
| :--- | :--- | :--- |
| **Paradigm** | Object-oriented preflight engine | Stateless pure functional calculation |
| **Output** | Strongly typed `PreflightReport` dataclass | Plain dictionary structure |
| **Validation** | Eager validation on initialization (`__init__`) | Guard check inside function body |
| **Use Case** | Reusable service component in an inference pipeline | Independent oracle / ground-truth validation test |

Both approaches produce identical results for all valid inputs and reject negative budgets with `ValueError`.

---

## 3. Fixture Contract and Boundary Decisions

### Standard Contract
- **Budget 3 with `"one two three four"`**:
  - Total tokens: 4
  - Retained tokens: `["one", "two", "three"]`
  - Removed tokens: 1
  - `is_truncated`: `True`
- **Empty input `""`**:
  - Total tokens: 0
  - Retained tokens: `[]`
  - Removed tokens: 0
  - `is_truncated`: `False`
- **Negative budget (e.g. `-1`)**:
  - **Decision**: Strictly rejected with `ValueError`. Negative budgets are mathematically and operationally invalid.

### Boundary Cases
| Prompt | Budget | Retained | Removed | Is Truncated | Explanation |
| :--- | :---: | :--- | :---: | :---: | :--- |
| `"one two three four"` | 3 | `["one", "two", "three"]` | 1 | `True` | Standard truncation fixture |
| `""` | 3 | `[]` | 0 | `False` | Empty input retains none |
| `"   "` | 2 | `[]` | 0 | `False` | Whitespace-only input handled cleanly |
| `"alpha beta"` | 5 | `["alpha", "beta"]` | 0 | `False` | Prompt length strictly under budget |
| `"alpha beta"` | 2 | `["alpha", "beta"]` | 0 | `False` | Prompt length exactly equals budget |
| `"red green blue"` | 0 | `[]` | 3 | `True` | Zero budget retains 0 tokens |
| `"test"` | -1 | *Raises `ValueError`* | - | - | Negative budget rejected |

---

## 4. Scope and Limitations

- **Pedagogical Scope**: Pure Python standard library demonstration of preflight token budgeting and truncation accounting.
- **Prerequisites**: Python 3 standard library (`dataclasses`, `unittest`, `sys`, `typing`).
- **No External Dependencies**: Requires no GPU, cloud service credentials, network access, or pretrained model weights.
- **Simplifications**: Whitespace splitting approximates tokenization; does not compute Byte-Pair Encoding merges or model-specific special token prefixes/suffixes (`[CLS]`, `[SEP]`, etc.).

---

## 5. Usage and Invocations

### Direct CLI Invocation
```bash
python3 chapters/en/chapter1/applied-labs/r16-t023/example.py
```
Output:
```text
=== Token-Budget Preflight Inspection ===
Notice: [TEACHING APPROXIMATION] Whitespace splitting is used here solely as a simple, deterministic educational proxy for tokenization. Production LLMs use learned subword tokenizers (e.g. BPE, WordPiece, Unigram) that split words into subword pieces.

Contract Case 1: Prompt: 'one two three four', Budget: 3
  Total tokens:   4
  Retained:       ['one', 'two', 'three']
  Removed tokens: 1
  Is truncated:   True

Contract Case 2: Empty input: '', Budget: 3
  Retained:       []
  Removed tokens: 0

Contract Case 3: Negative budget rejection (budget = -1)
  PASS: Correctly rejected negative budget (Token budget cannot be negative: received -1)

=== Comparing Approach 1 (Engine) vs Approach 2 (Reference Calc) ===
  Input: prompt='one two three four', budget=3 -> Match: True
  Input: prompt='one two three four', budget=4 -> Match: True
  Input: prompt='one two three four', budget=5 -> Match: True
  Input: prompt='one two three four', budget=0 -> Match: True
  Input: prompt='', budget=3 -> Match: True
  Input: prompt='   ', budget=2 -> Match: True
  Input: prompt='alpha beta', budget=1 -> Match: True

All comparison cases agreed identically.
```

### Python API
```python
from example import TokenBudgetPreflight, reference_preflight_calc

# Approach 1: Engine class
engine = TokenBudgetPreflight(budget=3)
report = engine.check("one two three four")
print(report.retained)       # ['one', 'two', 'three']
print(report.removed_count)  # 1

# Approach 2: Functional reference
ref = reference_preflight_calc("one two three four", budget=3)
print(ref["retained"])       # ['one', 'two', 'three']
```

---

## 6. Automated Testing

Run unit tests via `unittest`:
```bash
python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t023 -p "test_*.py" -v
```
All 8 tests run in fresh processes, covering contract fixtures, boundaries, error rejections, and approach comparisons.
