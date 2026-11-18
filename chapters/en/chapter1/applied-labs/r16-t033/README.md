# R16-T033: token-budget preflight

Applied example for the lesson "How Transformers solve tasks" (`chapters/en/chapter1/5.mdx`).

Task type: Compare two approaches.

## What it shows

Checks a prompt length against a budget with a whitespace tokenizer. The same inputs go through two approaches (slicing and counting) and an explicit expected-result table. Budget 3 with 'one two three four' retains [one, two, three] and removes one token.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t033 -p "test_*.py"
```

## Output of `python3 example.py`

```text
Whitespace splitting is a teaching approximation, not the model's real tokenizer.
'one two three four', budget 3: retained=['one', 'two', 'three'] removed=1 match=True
'', budget 3: retained=[] removed=0 match=True
'one two', budget 3: retained=['one', 'two'] removed=0 match=True
'one two three', budget 3: retained=['one', 'two', 'three'] removed=0 match=True
'one two three four', budget 0: retained=[] removed=4 match=True
budget -1 -> ValueError: budget must be 0 or more, got -1
```

## Scope and limits

Whitespace splitting is a teaching approximation, not the model's real tokenizer. It is a local, deterministic teaching fixture. It makes no claim about real hardware, cloud service behavior or trained-model performance.
