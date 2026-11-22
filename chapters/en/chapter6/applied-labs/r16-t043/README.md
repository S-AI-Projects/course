# Applied Lab R16-T043: Token-to-Character Alignment (Compare Two Approaches)

## Related Lesson
- **Chapter**: Chapter 6: The 🤗 Tokenizers Library
- **Section**: [Fast tokenizers' special powers (`fast-tokenizers-special-powers`)](../../3.mdx)

## Objective & Focus
In Chapter 6, Section 3, fast tokenizers introduce offset tracking: mapping each token back to the character slice of the original text that generated it. This character offset mapping (`offset_mapping`) is critical for downstream tasks like named entity recognition (NER) and question answering (extracting answer spans from context).

This applied lab implements:
1. A local token-span lookup engine that validates non-overlapping half-open intervals `[start, end)`.
2. Character-to-token alignment resolving which token owns a given character offset or detecting untokenized whitespace separators.
3. A comparison between two independent methods:
   - **Approach 1**: An interval-based search engine (`TokenSpanAlignment`).
   - **Approach 2**: An explicit dense character map / expected-result table calculation (`build_dense_char_to_token_map`).

## Public Input/Output Contract
- **Input Text**: `"red apple"`
- **Token Spans**: `[(0, 3), (4, 9)]`
  - Token 0 (`"red"`): `[0, 3)`
  - Token 1 (`"apple"`): `[4, 9)`
- **Contract Checks**:
  - Character index 5 maps to token index `1` (`"apple"[1] == 'p'`).
  - Separating space at character index 3 maps to no token (`None`).
  - Approach 1 and Approach 2 yield identical results across all character indices.

## Teaching Approximation & Scope
- **Pure Local Fixture**: Built purely using the Python standard library.
- **Decoupled from Hugging Face / Rust**: Demonstrates character offset mathematics without requiring Rust builds, Hugging Face Tokenizers installation, model downloads, API tokens, or GPUs.
- **Hardware Neutral**: Makes no claims regarding model speed, tokenization throughput, or cloud infrastructure.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter6/applied-labs/r16-t043/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t043 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T043/check.py
```
