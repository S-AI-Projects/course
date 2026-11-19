# R16-T009: Reuse or train a new tokenizer? Decision and experiment

A small, standard-library-only example for the chapter 6
[Introduction](../../1.mdx). The lesson says:
- **When fine-tuning**, we use the same tokenizer the model was pretrained with.
- **When training from scratch** on another domain or language, a pretrained
  tokenizer is "typically suboptimal". For example, an English tokenizer does
  poorly on Japanese, where spaces are used very differently.

> **Simulation.** The "existing tokenizer" is a toy word-level tokenizer: a
> whitespace split checked against a 16-word English vocabulary. Real
> tokenizers are subword-based and rarely produce this many unknowns. The
> numbers below only illustrate the idea and say nothing about any real
> tokenizer or model.

## Metric

`unknown_rate = unknown tokens / all tokens`, kept as an exact `Fraction`. A
rate of exactly `1/4` is compared with the threshold without the rounding
errors of decimal numbers.

## Decision rules

1. If `training_mode` is missing, or it is `from-scratch` with no corpus sample, the decision is **need-more-info**.
2. If `training_mode` is `fine-tune`, the decision is **reuse** (keep the pretraining tokenizer).
3. If `training_mode` is `from-scratch`: when `unknown_rate > 1/4` the decision is **train-new**, otherwise **reuse**.

## Decision table

| Scenario | Facts | Unknown rate | Decision | Rationale |
|---|---|---|---|---|
| `normal` | from-scratch, Japanese sample | 1 | **train-new** | The lesson's example: whitespace splitting can't segment Japanese, so every token is unknown |
| `boundary` | from-scratch, `"the new text zebra"` | exactly 1/4 | **reuse** | The rule needs *more than* 1/4. One more unknown word flips it to train-new |
| `missing-information` | from-scratch, no sample | n/a | **need-more-info** | We can't measure fit without a corpus sample |

`check_table()` compares `decide` with this table and returns any mismatch.
If a decision is deliberately changed, the checker reports it. Whether each
rationale really follows the lesson is for a human reviewer to judge.

## Evaluation experiment: three vocabulary sizes

Same 12-token English corpus (`"we train a new tokenizer on the text of a new
corpus"`), with three controlled configurations: the first 4, 8 or 16 words of
the vocabulary.

| Vocab size | Unknown tokens | Unknown rate | Decision |
|---|---|---|---|
| 4 | 6 of 12 | 1/2 | train-new |
| 8 | 2 of 12 (`train`, `tokenizer`) | 1/6 | reuse |
| 16 | 0 of 12 | 0 | reuse |

**Correctness:** the tests check these exact values against a hand calculation.

**Trade-off:** a larger vocabulary leaves fewer words unknown, but a model
needs one embedding row per vocabulary entry, so a larger vocabulary means a
larger table to store and train. Here, going from 8 to 16 words doubles the
vocabulary to cover the last 2 of 12 tokens. This is a statement about this
toy setup only, not about real-world accuracy.

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter6/applied-labs/r16-t009/example.py
```

Expected output:

```
Toy word-level tokenizer (simulation) - not a real tokenizer.

[normal] {'training_mode': 'from-scratch', 'corpus_sample': '私は猫が好きです 今日は晴れです'} -> train-new
[boundary] {'training_mode': 'from-scratch', 'corpus_sample': 'the new text zebra'} -> reuse
[missing-information] {'training_mode': 'from-scratch', 'corpus_sample': None} -> need-more-info
check_table -> all decisions match

Experiment: 12-token corpus, threshold 1/4
vocab_size  unknown_rate  decision
         4    1/2 (0.50)  train-new
         8    1/6 (0.17)  reuse
        16      0 (0.00)  reuse
```

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t009 -p "test_*.py"
```

Expected: `Ran 12 tests ... OK`, exit code 0.

## Limitations

- A toy word-level tokenizer, not WordPiece, BPE or Unigram. The chapter covers those later.
- The 1/4 threshold is a teaching choice, not a recommended value.
- No tokenizer is trained, and no model or dataset is downloaded.
