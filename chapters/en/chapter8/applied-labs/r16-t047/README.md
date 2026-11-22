# Applied Lab R16-T047: Token-Budget Preflight (Worked Example with Checks)

## Related Lesson
- **Chapter**: Chapter 8: How to Ask for Help and Debug
- **Section**: [End-of-chapter quiz (`end-of-chapter-quiz`)](../../7.mdx)

## Objective & Focus
In Chapter 8, Section 7, debugging questions emphasize verifying input shapes, bounds, and creating minimal reproducible checks before debugging model training pipelines.

This applied lab demonstrates:
1. A deterministic token-budget preflight check running as a lightweight regression test.
2. A published worked input-to-output explanation explaining how tokens are bounded and truncated.
3. Automated regression execution ensuring predictable behavior.

## Contract & Acceptance Criteria
- **Budget 3 with `"one two three four"`**:
  - Retained: `['one', 'two', 'three']`
  - Removed Count: `1`
  - Truncated: `True`
- **Empty Input**: Retains `[]` and reports `0` removed tokens.
- **Negative Budget**: Rejects negative budget ($N < 0$) with `ValueError`.
- **Teaching Approximation**: Explicitly labeled as a teaching fixture, not a production model tokenizer.

## Scope & Limitations
- **Pure Local Fixture**: Built with Python standard library.
- **No External Dependencies**: No model weights, Hugging Face Tokenizers installation, GPU hardware, or cloud services required.
- **Hardware Neutral**: Makes no claims about GPU memory or trained-model inference speed.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter8/applied-labs/r16-t047/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t047 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T047/check.py
```
