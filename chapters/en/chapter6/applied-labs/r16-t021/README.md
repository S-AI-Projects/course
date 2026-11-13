# Applied Lab R16-T021: Greedy Subword Segmentation Concept Example

A minimal, runnable concept example demonstrating greedy longest-prefix subword segmentation as used by WordPiece models (e.g. BERT), complementing [Chapter 6, Section 8 ("Building a tokenizer, block by block")](../../8.mdx).

---

## 1. Concept and Lesson Connection

In [Chapter 6, Section 8](../../8.mdx), tokenizers are assembled block by block:
- **Normalizer**: cleans and normalizes raw text.
- **Pre-tokenizer**: splits text into word units.
- **Model** (`models.WordPiece`): converts words into subword token sequences using vocabulary lookup and continuation prefixes (`##`).
- **Post-processor**: appends special tokens (e.g. `[CLS]`, `[SEP]`).
- **Decoder** (`decoders.WordPiece`): strips continuation prefixes to reconstruct words.

While the high-level 🤗 Tokenizers library encapsulates this model step in Rust, this applied lab implements the core tokenization algorithm in pure Python to illustrate what happens under the hood during the Model step.

### Algorithm (WordPiece Greedy Segmentation)
1. Given a word, scan from the end of the current substring down to length 1 to find the **longest prefix** present in the vocabulary.
2. For initial tokens (start of word), check without prefix.
3. For continuation tokens (subsequent parts of the word), prepend `##` (the continuation marker) before vocabulary lookup.
4. If at any point no prefix is found in the vocabulary, the whole word cannot be segmented and falls back to `[UNK]`.

---

## 2. Mandatory Fixture and Expected Behavior

- **Vocabulary**: `{"play", "##ing", "cat"}`
- **Continuation marker**: `##`
- **Unknown token**: `[UNK]`

| Input Word | Segmentation Process | Output Tokens |
| :--- | :--- | :--- |
| `playing` | `play` matches initial prefix; remaining `ing` prefixed with `##` matches `##ing` | `["play", "##ing"]` |
| `cat` | `cat` matches initial prefix; no remainder | `["cat"]` |
| `dog` | No prefix matches vocabulary | `["[UNK]"]` |
| `played` | `play` matches, but remainder `##ed` not in vocabulary; whole word fails | `["[UNK]"]` |
| `cats` | `cat` matches, but remainder `##s` not in vocabulary; whole word fails | `["[UNK]"]` |

---

## 3. Scope and Limitations

- **Pedagogical scope**: Demonstrates the discrete inner loop of WordPiece vocabulary lookup and continuation marking.
- **Pure standard library**: Requires only Python 3 standard library; no external libraries, tokenizers binaries, models, GPUs, or network access are required.
- **Explicit simplifications**:
  - Does not implement BPE merge-rule training or WordPiece likelihood-score training; assumes a pre-existing vocabulary fixture.
  - Does not perform Unicode NFD normalization, lowercasing, or regex punctuation splitting (assumes normalized word inputs or whitespace-separated tokens).
  - Does not replace production tokenizers (`tokenizers.models.WordPiece`), which are implemented in Rust for high-throughput batch processing.

---

## 4. Usage and Invocations

### Direct Execution
Run the standalone concept script:
```bash
python3 chapters/en/chapter6/applied-labs/r16-t021/example.py
```
Output:
```text
=== Greedy Subword Segmentation (WordPiece Model Concept) ===
Vocabulary: ['##ing', 'cat', 'play']
Continuation prefix: '##'
Unknown token: '[UNK]'
------------------------------------------------------------
'playing' -> ['play', '##ing']
'cat' -> ['cat']
'dog' -> ['[UNK]']
```

Pass custom words via CLI:
```bash
python3 chapters/en/chapter6/applied-labs/r16-t021/example.py playing cat dog played
```

### Python API
```python
from example import DEFAULT_VOCAB, segment_word, tokenize_text

tokens = segment_word("playing", DEFAULT_VOCAB)
# Returns: ['play', '##ing']

sentence = tokenize_text("playing cat dog", DEFAULT_VOCAB)
# Returns: ['play', '##ing', 'cat', '[UNK]']
```

---

## 5. Automated Testing

Run the unit test suite:
```bash
python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t021 -p "test_*.py" -v
```

All 9 tests cover normal cases, failure scenarios (`[UNK]` fallback on partial and complete misses), boundary conditions (empty string, custom markers), and CLI execution.
