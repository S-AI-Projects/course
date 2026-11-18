# Applied Lab R16-T026: Normalization with Offsets - Refactor the Teaching Example

A minimal, runnable concept lab demonstrating whitespace normalization paired with character offset tracking and code refactoring, complementing [Chapter 6, Section 4 ("Normalization and pre-tokenization")](../../4.mdx).

---

## 1. Concept and Lesson Connection

In [Chapter 6, Section 4](../../4.mdx), pre-tokenizers split text into words while recording **character offsets** (start and end index spans into the original raw text):
```python
tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str("Hello, how are  you?")
# [('Hello', (0, 5)), (',', (5, 6)), ('how', (7, 10)), ('are', (11, 14)), ('you', (16, 19)), ('?', (19, 20))]
```
When tokenizers normalize repeated whitespace (e.g. collapsing multiple consecutive spaces), maintaining offset mappings ensures that downstream tasks (such as named entity recognition or extractive question answering) can map model predictions directly back to character spans in the original source text.

---

## 2. Refactoring Focus: Extract Named Responsibility

This lab demonstrates how to cleanly refactor a monolithic pre-tokenizer into decoupled single-responsibility components while preserving strict behavioral equivalence.

### Baseline (Monolithic)
`baseline_tokenize_with_offsets(text)` combines whitespace scanning, boundary index arithmetic, and token slicing within a single intertwined loop.

### Extracted Responsibility: `WhitespaceSpanScanner`
We extract character boundary detection into an independent component:
```python
class WhitespaceSpanScanner:
    @staticmethod
    def scan_spans(text: str) -> List[Tuple[int, int]]:
        ...
```
`WhitespaceSpanScanner` owns a single, cohesive responsibility: scanning the raw string and returning the half-open intervals `[start, end)` corresponding to non-whitespace character runs.

### Refactored Implementation
`refactored_tokenize_with_offsets(text)` delegates interval discovery to `WhitespaceSpanScanner` and constructs normalized `(token, span)` pairs via clean slice comprehension:
```python
def refactored_tokenize_with_offsets(text: str) -> List[Tuple[str, Tuple[int, int]]]:
    spans = WhitespaceSpanScanner.scan_spans(text)
    return [(text[start:end], (start, end)) for start, end in spans]
```

### Equivalence Guarantee
Both implementations produce identical output on all valid inputs:
$$\text{baseline\_tokenize\_with\_offsets}(text) \equiv \text{refactored\_tokenize\_with\_offsets}(text)$$

---

## 3. Fixture Contract and Slice Recovery Invariant

- **Input**: `"  red   apple "` (length 14)
- **Extracted Tokens and Spans**:
  - `"red"` at `[2, 5)`
  - `"apple"` at `[8, 13)`
- **Slice Recovery Invariant**:
  $$text[start:end] == token$$
  - `text[2:5] == "red"` $\rightarrow$ `True`
  - `text[8:13] == "apple"` $\rightarrow$ `True`

### Boundary Cases
| Input Text | Output Spans | Explanation |
| :--- | :--- | :--- |
| `"  red   apple "` | `[('red', (2, 5)), ('apple', (8, 13))]` | Standard fixture with repeated spaces |
| `""` | `[]` | Empty string yields empty list |
| `"      "` | `[]` | Whitespace-only string yields empty list |
| `"hello"` | `[('hello', (0, 5))]` | Single word without surrounding spaces |
| `"\tfoo \n bar\t"` | `[('foo', (1, 4)), ('bar', (8, 11))]` | Mixed tabs and newlines handled cleanly |

---

## 4. Scope and Limitations

- **Pedagogical Scope**: Pure Python standard library demonstration of offset tracking and single-responsibility refactoring.
- **Prerequisites**: Python 3 standard library (`typing`, `unittest`, `sys`).
- **No External Dependencies**: Requires no GPU, cloud services, pretrained tokenizers, or external libraries.
- **Simplifications**: Focuses on whitespace normalization and non-whitespace spans; does not implement Unicode NFD normalization or subword merges (covered in later sections).

---

## 5. Usage and Invocations

### Direct CLI Invocation
```bash
python3 chapters/en/chapter6/applied-labs/r16-t026/example.py
```
Output:
```text
=== Normalization with Offsets: Refactored Teaching Example ===
Raw Input: '  red   apple ' (length: 14)

1. Baseline Output:
   token: 'red'    span: [2, 5)
   token: 'apple'  span: [8, 13)

2. Refactored Output (Extracted WhitespaceSpanScanner):
   token: 'red'    span: [2, 5)
   token: 'apple'  span: [8, 13)

3. Equivalence Check: PASSED

4. Slice Recovery Invariant Verification:
   fixture[2:5] -> 'red' == token 'red': True
   fixture[8:13] -> 'apple' == token 'apple': True

Slice Recovery Invariant: PASSED
```

### Python API
```python
from example import refactored_tokenize_with_offsets, recover_words_from_slices

text = "  red   apple "
tokens = refactored_tokenize_with_offsets(text)
# [('red', (2, 5)), ('apple', (8, 13))]

words = recover_words_from_slices(text, tokens)
# ['red', 'apple']
```

---

## 6. Automated Testing

Run unit tests via `unittest`:
```bash
python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t026 -p "test_*.py" -v
```
All 8 unit tests pass, verifying the contract fixture, baseline-refactor equivalence, slice recovery, boundary cases, and deliberate failure detection.
