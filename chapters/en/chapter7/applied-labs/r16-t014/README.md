# Applied Lab R16-T014: Answer-Span Extraction — Invariant and State Trace

## Related Lesson
- **Chapter**: Chapter 7 - Main NLP Tasks
- **Section**: [Question answering (7.mdx)](../../7.mdx)

## Objective & Focus
This lab validates start/end token indices for extractive QA, maps them to character offsets, and recovers an answer substring from a fixed context. Each pipeline step records its intermediate state, and an invariant links the state to the final output.

**Fixed context**: `"Ada wrote notes"`

**Word-level token sequence**:
| Token Index | Token Text | char_start | char_end |
| --- | --- | --- | --- |
| 0 | Ada | 0 | 3 |
| 1 | wrote | 4 | 9 |
| 2 | notes | 10 | 15 |

## Span Extraction Contract

| Start | End | Expected Answer | Expected Result |
| --- | --- | --- | --- |
| 0 | 0 | `"Ada"` | PASS |
| 1 | 2 | `"wrote notes"` | PASS |
| 2 | 2 | `"notes"` | PASS |
| 2 | 0 | — | REJECT (ValueError: end before start) |
| 0 | 99 | — | REJECT (IndexError: out of range) |

## State Trace (Intermediate Pipeline Steps)

Each call to `extract_span()` returns:
```python
{
    "token_offsets": [...],   # Step 1: offset map derived from context
    "validated": True/False,  # Step 2: invariant check (0 <= start <= end < n)
    "char_start": int,        # Step 3: character start of span
    "char_end": int,          # Step 4: character end (exclusive)
    "answer": str,            # Step 5: recovered substring
}
```

## Key Invariants
1. **Span ordering invariant**: `0 <= start <= end < num_tokens`
2. **Positive width invariant**: `char_end > char_start` for all valid non-empty spans
3. **Answer-slice invariant**: `answer == context[char_start:char_end]`

## Running the Lab

### 1. Run the Example Directly
```bash
python3 chapters/en/chapter7/applied-labs/r16-t014/example.py
```

### 2. Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter7/applied-labs/r16-t014 -p "test_*.py" -v
```

### 3. Run Verification Checks
```bash
python3 work/R16-T014/check.py
```

## Scope and Limitations
- **Local Simulation**: Models the token-index-to-char-offset mapping step of the QA pipeline in pure Python without loading a BERT model or the SQuAD dataset.
- **Whitespace Tokenization**: Uses Python `.split()` as a simplified tokenizer; real HuggingFace tokenizers produce subword tokens and richer `offset_mapping`.
- **Hardware Agnostic**: Makes no claims about GPU inference speed, model accuracy, or cloud prediction quality.
