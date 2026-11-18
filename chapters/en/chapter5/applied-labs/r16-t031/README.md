# R16-T031: dataset manifest validation

Applied example for the lesson "What if my dataset isn't on the Hub?" (`chapters/en/chapter5/2.mdx`).

Task type: Runnable concept example.

## What it shows

Validates a local JSONL dataset with required id, text and label fields and a train/validation manifest. A missing label fails with a line number, duplicate ids across splits fail, and a valid two-split fixture passes.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t031 -p "test_*.py"
```

## Output of `python3 example.py`

```text
valid two splits -> PASS {'train': 2, 'validation': 1}
missing label -> FAIL: train line 2: missing required field 'label'
duplicate id across splits -> FAIL: duplicate id 'a1': train line 1 and validation line 1
```

## Scope and limits

It checks file structure only, not data quality. It does not use the Hub, the datasets library or any model.
