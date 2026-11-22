# Applied Lab R16-T041: Token-Budget Preflight

## Related Lesson
- **Chapter**: Chapter 2: Using 🤗 Transformers
- **Section**: [Models (`the-models`)](../../3.mdx)

## Objective & Focus
This applied lab implements a minimal, complete, and deterministic concept example of a **token-budget preflight** checker.

In Chapter 2, Section 3, transformer models accept batches of tensor inputs (`input_ids`) shaped to rectangular dimensions and bounded by hardware/context constraints (such as `max_position_embeddings`). Before sending raw text to downstream tensor conversion and model inference, applications perform a **preflight check** against a configured token budget to manage resource constraints, avoid unexpected context overflow, and explicitly report any token truncation.

## Public Input/Output Contract
- **Configured Token Budget**: Integer $N \ge 0$.
- **Negative Budget Handling**: Any negative budget ($N < 0$) is rejected with a `ValueError`.
- **Preflight Check Input**: Raw text string (`prompt: str`).
- **Preflight Check Output**: Structured report containing:
  - `prompt`: Input prompt string.
  - `budget`: Maximum allowed tokens.
  - `total_tokens`: Total token count identified.
  - `retained`: Ordered list of retained token strings within budget.
  - `removed_count`: Number of truncated / removed tokens.
  - `is_truncated`: Boolean flag indicating whether truncation occurred.

### Contract Scenarios
1. **Normal Truncation Case**:
   - Budget: `3`
   - Prompt: `"one two three four"`
   - Retained: `['one', 'two', 'three']`
   - Removed: `1`
   - Truncated: `True`
2. **Empty Input Case**:
   - Budget: `3`
   - Prompt: `""`
   - Retained: `[]`
   - Removed: `0`
   - Truncated: `False`
3. **Negative Budget Case**:
   - Budget: `-1`
   - Output: Raises `ValueError`

## Teaching Approximation & Simplifications
> **Important Distinction**:
> The tokenizer implemented in this lab is a **deterministic local whitespace-splitting teaching fixture** (`prompt.strip().split()`).
> - It is **NOT** a trained model tokenizer (such as WordPiece for BERT or BPE for GPT).
> - It does not perform subword segmentation (e.g. splitting `tokenization` into subwords).
> - It does not map tokens to vocabulary IDs or add special tokens (`[CLS]`, `[SEP]`).
> - It requires **no model downloads**, **no external dependencies**, **no paid cloud API keys**, and **no GPU/hardware acceleration**.
>
> This simplification allows deterministic, transparent inspection of the token boundary and preflight resource budget logic.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter2/applied-labs/r16-t041/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t041 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T041/check.py
```
