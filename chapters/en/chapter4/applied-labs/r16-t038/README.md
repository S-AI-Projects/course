# R16-T038: token-budget preflight failure and recovery

Applied example for the lesson "End-of-chapter quiz" (`chapters/en/chapter4/6.mdx`).

Task type: Failure and recovery example.

## What it shows

The token-budget check rejects a negative budget and a missing prompt with a clear error. A batch runner reports the error and still handles the next valid input, which shows recovery.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter4/applied-labs/r16-t038 -p "test_*.py"
```

## Output of `python3 example.py`

```text
Whitespace splitting is a teaching approximation, not the model's real tokenizer.
{'request': 1, 'status': 'ok', 'retained': ['one', 'two', 'three'], 'removed': 1}
{'request': 2, 'status': 'error', 'error': 'budget must be 0 or more, got -1'}
{'request': 3, 'status': 'error', 'error': 'prompt is missing (got None)'}
{'request': 4, 'status': 'ok', 'retained': ['a', 'b'], 'removed': 0}
{'request': 5, 'status': 'ok', 'retained': [], 'removed': 0}
recovered on the next valid input: True
```

## Scope and limits

Whitespace splitting is a teaching approximation, not the model's real tokenizer. It is a local, deterministic teaching fixture. It makes no claim about real hardware, cloud service behavior or trained-model performance.
