# R16-T003: Token-budget preflight, compared two ways

A small, standard-library-only example for the *limited context windows*
point in [Natural Language Processing and Large Language Models](../../2.mdx).
Before sending a prompt to a model you can run a **preflight** check: count the
tokens, compare the count with a budget, and report exactly what would be kept
and what would be cut.

> **Teaching approximation.** Tokens here are whitespace-separated words
> (`str.split()`). Real LLMs use subword tokenizers, so the same text usually
> has a different (often larger) token count. This is not any model's real
> tokenizer.

## The contract

`preflight(prompt, budget)` returns:

| Key | Meaning |
|---|---|
| `budget` | the budget you passed |
| `token_count` | number of whitespace tokens in the prompt |
| `retained` | the first `budget` tokens (or all of them, if they fit) |
| `removed_count` | how many tokens were cut |
| `truncated` | `True` if anything was cut |

- A negative budget raises `ValueError`. A non-`str` prompt or a non-`int` budget raises `TypeError`.
- The budget is a maximum: a prompt with exactly `budget` tokens fits and is not truncated.

## Two approaches, same inputs

| | Direct (`preflight`) | Independent (`reference_preflight`) |
|---|---|---|
| How | Loop over tokens, stop when `len(retained) == budget` | `tokens[:budget]`, and `removed = max(len(tokens) - budget, 0)` |
| Strength | Shows each keep/stop decision step by step | Short and hard to get wrong. Used as an oracle |

The tests check that both approaches match the hand-written `EXPECTED_TABLE`
**and** that they agree on every combination of 0–5 tokens and budget 0–6
(42 cases). If either one has an off-by-one bug, the comparison fails.

### Expected-result table

| Prompt | Budget | Retained | Removed | Truncated |
|---|---|---|---|---|
| `"one two three four"` | 3 | `[one, two, three]` | 1 | True |
| `""` | 3 | `[]` | 0 | False |
| `"one two three"` | 3 | `[one, two, three]` | 0 | False |
| `"one two"` | 3 | `[one, two]` | 0 | False |
| `"one two three four"` | 0 | `[]` | 4 | True |
| `"  one\ttwo\n three  "` | 2 | `[one, two]` | 1 | True |
| `"one two"` | -1 | ValueError | | |

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter1/applied-labs/r16-t003/example.py
```

Expected output:

```
Tokenizer: whitespace split (teaching approximation, not a model tokenizer)
'one two three four'     budget=3 tokens=4 retained=['one', 'two', 'three'] removed=1 -> TRUNCATED [agree]
''                       budget=3 tokens=0 retained=[] removed=0 -> fits [agree]
'one two three'          budget=3 tokens=3 retained=['one', 'two', 'three'] removed=0 -> fits [agree]
budget=-1 rejected: budget must be >= 0, got -1
```

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t003 -p "test_*.py"
```

Expected: `Ran 12 tests ... OK`, exit code 0.

## Limitations

- Whitespace tokens are not model tokens. Use the model's own tokenizer for real budgets.
- Real systems also reserve room for the model's output and for special tokens, and may cut from the start or the middle instead of the end. This example only keeps the first `budget` tokens.
- Nothing here calls a model or measures any model's context window.
