# R16-T037: trainable-parameter accounting

Applied example for the lesson "Fine-tuning, Check!" (`chapters/en/chapter3/6.mdx`).

Task type: Worked example with checks.

## What it shows

Counts total and trainable parameters from a local named-parameter manifest with a prefix-based freeze rule. With encoder:100 and head:20 and the encoder frozen, total is 120 and trainable is 20. A freeze prefix that matches nothing is reported.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t037 -p "test_*.py"
```

## Output of `python3 example.py`

```text
manifest: {'encoder': 100, 'head': 20}
Worked example, freeze ['encoder']:
  encoder: 100 -> frozen
  head: 20 -> trainable
freeze ['encoder'] -> {'total': 120, 'frozen': 100, 'trainable': 20, 'unmatched_prefixes': []}
freeze [] -> {'total': 120, 'frozen': 0, 'trainable': 120, 'unmatched_prefixes': []}
freeze ['encoder', 'decoder'] -> {'total': 120, 'frozen': 100, 'trainable': 20, 'unmatched_prefixes': ['decoder']}
```

## Scope and limits

The sizes are toy numbers and no real model is loaded. It is a local, deterministic teaching fixture. It makes no claim about real hardware, cloud service behavior or trained-model performance.
