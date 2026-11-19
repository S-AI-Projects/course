# R16-T010: Token-budget preflight with three applied questions

A small, standard-library-only example for
[What to do when you get an error](../../2.mdx). In the lesson's forward-pass
bug, the model was given the wrong kind of input (a Python `list` where a
tensor was expected), and the traceback only revealed it deep inside the
library. A **preflight** check validates inputs *before* the expensive call,
so mistakes fail early with a message that says what was expected.

This lab preflights a prompt against a token budget and reports exactly what
is kept and what is cut.

> **Teaching approximation.** Tokens here are whitespace-separated words
> (`str.split()`), not a real model tokenizer. Real token counts differ.

## The contract

`preflight(prompt, budget)` returns `budget`, `token_count`, `retained`,
`removed_count` and `truncated`.

- Budget 3 with `"one two three four"` keeps `['one', 'two', 'three']` and reports 1 removed token.
- Empty input keeps `[]` and removes 0.
- A negative budget raises `ValueError`. A non-`str` prompt or a non-`int` budget raises `TypeError`.

## Three applied questions

Each factual answer has an executable check in `test_example.py`, in the
`AppliedQuestions` class.

**Q1 (predict an output).** What does `preflight("a b c", 2)` keep, and how many tokens are removed?
- **Answer:** `retained=['a', 'b']`, `removed_count=1`, `truncated=True`.
- **Rationale:** the budget is 2, so only the first two tokens fit. The third is cut and counted.
- **Check:** `test_q1_predict_output`

**Q2 (diagnose a failure).** `preflight(['one', 'two'], 3)` raises an error. Which one, and how do you fix it?
- **Answer:** `TypeError: prompt must be a str, got list`. Fix it by passing text: `preflight(" ".join(['one', 'two']), 3)`.
- **Rationale:** this is the same kind of bug as the lesson's list-vs-tensor error. The data is right but the container type is wrong. The preflight catches it immediately with a clear message instead of a deep traceback.
- **Check:** `test_q2_diagnose_failure` (also checks that the fix works)

**Q3 (choose a boundary policy).** A prompt has exactly as many tokens as the budget (4 tokens, budget 4). Should it be truncated?
- **Answer:** No: `truncated=False`, `removed_count=0`.
- **Rationale:** a budget is a maximum ("at most N tokens"), so N tokens fit. A "fewer than N" policy would cut a token from prompts that are already valid.
- **Check:** `test_q3_boundary_policy_exactly_at_budget_fits`

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter8/applied-labs/r16-t010/example.py
```

Expected output (the first lines):

```
Tokenizer: whitespace split (teaching approximation, not a model tokenizer)
budget=3 tokens=4 retained=['one', 'two', 'three'] removed=1 -> TRUNCATED
budget=3 tokens=0 retained=[] removed=0 -> fits
budget=-1 rejected: budget must be >= 0, got -1
```

The three questions and their answers are printed after these lines.

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t010 -p "test_*.py"
```

Expected: `Ran 11 tests ... OK`, exit code 0.

## Limitations

- Whitespace tokens are not model tokens. Use the model's own tokenizer for real budgets.
- Real systems reserve room for output and special tokens, and may truncate differently. This lab only keeps the first `budget` tokens.
- No model or Hub call is made. The lesson's real `AttributeError` is only discussed, not reproduced.
