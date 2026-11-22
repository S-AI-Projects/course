# Applied Lab R16-T050: Token-Budget Preflight (Scenario Assessment)

## Related Lesson
- **Chapter**: Chapter 1: Transformer Models
- **Section**: [Introduction (`introduction`)](../../1.mdx)

## Objective & Focus
In Chapter 1, Section 1, the course establishes foundations for processing NLP and LLM workloads. Managing token limits and understanding the boundaries of input preparation is the first line of defense in sequence modeling.

This applied lab demonstrates:
1. A deterministic token-budget preflight check fixture.
2. An applied **scenario assessment** answering three core questions:
   - **Predict an output**: Predict token retention and truncation given a prompt and budget.
   - **Diagnose a failure**: Identify why a negative budget triggers a `ValueError`.
   - **Choose a boundary policy**: Determine behavior for empty strings (`""`) and why no truncation occurs.
3. Executable verification checks with lesson-aligned rationales for every factual answer.

## Contract & Acceptance Criteria
- **Budget 3 with `"one two three four"`**:
  - Retained: `['one', 'two', 'three']`
  - Removed Count: `1`
  - Truncated: `True`
- **Empty Input**: Retains `[]` and reports `0` removed tokens.
- **Negative Budget**: Rejects negative budget ($N < 0$) with `ValueError`.
- **Teaching Approximation**: Explicitly labeled as a teaching fixture, not a production model tokenizer.

## Scope & Limitations
- **Pure Local Fixture**: Implemented purely in Python standard library.
- **No External Dependencies**: Requires no model downloads, paid cloud services, GPU hardware, or external tokenization packages.
- **Hardware Neutral**: Focuses on algorithmic preflight bounds without asserting hardware performance.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter1/applied-labs/r16-t050/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t050 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T050/check.py
```
