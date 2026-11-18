# R16-T034: token-budget preflight state trace

Applied example for the lesson "End-of-chapter quiz" (`chapters/en/chapter4/6.mdx`).

Task type: Invariant and state trace.

## What it shows

The token-budget check records its state after every token. The tests check the invariant (kept + dropped equals tokens seen, kept never exceeds the budget) at every step and link the final state to the final output.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter4/applied-labs/r16-t034 -p "test_*.py"
```

## Output of `python3 example.py`

```text
Whitespace splitting is a teaching approximation, not the model's real tokenizer.
after token 1 ('one'): keep, retained=['one'], removed=0
after token 2 ('two'): keep, retained=['one', 'two'], removed=0
after token 3 ('three'): keep, retained=['one', 'two', 'three'], removed=0
after token 4 ('four'): drop, retained=['one', 'two', 'three'], removed=1
final: {'retained': ['one', 'two', 'three'], 'removed': 1, 'truncated': True}
invariant problems: []
```

## Scope and limits

Whitespace splitting is a teaching approximation, not the model's real tokenizer. It is a local, deterministic teaching fixture. It makes no claim about real hardware, cloud service behavior or trained-model performance.
