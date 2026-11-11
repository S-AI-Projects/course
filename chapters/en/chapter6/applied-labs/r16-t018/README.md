# R16-T018: Greedy Subword Segmentation — Failure and Recovery Example

**Task**: R16-T018 · Issue #21  
**Chapter**: 6 — Section 6: "WordPiece tokenization"  
**Branch**: `student/e26b07f0816-R08-T008`  
**Type**: Failure and recovery example

---

## Overview

This applied lab extends Chapter 6, Section 6 ("WordPiece tokenization") by implementing a deterministic local WordPiece tokenizer using greedy longest-prefix subword segmentation.

In WordPiece:
1. Words are segmented starting from the beginning by finding the longest subword in the vocabulary.
2. Subsequent parts of the word are prefixed with `##` to signify continuation tokens.
3. If at any stage a subword cannot be found in the vocabulary, the **whole word** is replaced with `[UNK]`.

---

## Contract

### Core Vocabulary Match Contract

With vocabulary `{"play", "##ing", "cat", "[UNK]"}`:

| Input Word | Output Tokens | Explanation |
|---|---|---|
| `"playing"` | `["play", "##ing"]` | Matched prefix `"play"`, then continuation `"##ing"`. |
| `"cat"` | `["cat"]` | Matched complete single-word token `"cat"`. |
| `"dog"` | `["[UNK]"]` | Prefix `"dog"` not in vocabulary; falls back to whole-word `[UNK]`. |
| `"cats"` | `["[UNK]"]` | `"cat"` matches, but continuation `"##s"` is not in vocabulary; whole word fails to `[UNK]`. |

### Failure and Recovery Contract

| Scenario | Input Data | Status | Diagnostic Explanation / Recovery Behavior |
|---|---|---|---|
| **Missing Data** | `None` | `ERROR` | `"Missing data: input cannot be None (expected str)."` |
| **Invalid Type** | `12345` | `ERROR` | `"Invalid input type: expected str, got int."` |
| **Stream Recovery** | `["cat", None, "playing"]` | `SUCCESS`, `ERROR`, `SUCCESS` | Element 2 reports missing data error; element 3 immediately recovers producing `["play", "##ing"]`. |

---

## Files

| File | Purpose |
|---|---|
| `example.py` | `WordPieceTokenizer` with `encode_word()`, `tokenize_text()`, `tokenize_safe()`, and `tokenize_stream()` |
| `test_example.py` | 14 unit tests covering core contract, failure/recovery cases, edge cases, and deliberate failure detection |
| `README.md` | Lab documentation, contract specifications, and architectural details |

---

## Running

```bash
# Run unit tests from repository root:
python3 -m unittest discover \
  -s chapters/en/chapter6/applied-labs/r16-t018 \
  -p "test_*.py" -v

# Run the demonstration:
python3 chapters/en/chapter6/applied-labs/r16-t018/example.py
```

---

## Simulation and Pedagogical Limitations

> **SIMULATION NOTE**: This tokenizer is a pedagogical Python 3 standard library implementation designed for algorithmic study:
>
> - **Prefix Search**: Implemented via greedy substring matching rather than a compiled Trie or Rust Aho-Corasick automaton.
> - **Pre-tokenization**: Employs basic whitespace splitting rather than full BERT rule-based punctuation normalization.
> - **No Remote Dependencies**: Requires no network, model downloads, GPU hardware, or external packages (`tokenizers`, `transformers`).

---

## Lesson Link

See the linked section at the end of
[`chapters/en/chapter6/6.mdx`](../../6.mdx)
for textbook integration and examples.
