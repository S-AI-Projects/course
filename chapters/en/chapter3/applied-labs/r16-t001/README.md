# R16-T001: Learning-curve divergence example

A small, standard-library-only example for the
[Overfitting](../../5.mdx#overfitting) part of *Understanding Learning Curves*.
The lesson describes overfitting as "training loss continues to decrease while
validation loss increases". This example turns that description into one
explicit rule and checks it on hand-written loss values.

## The rule

> Flag divergence when, between the **last two** recorded steps, training loss
> **falls** (`training[-1] < training[-2]`) **and** validation loss **rises**
> (`validation[-1] > validation[-2]`).

How "over the last two steps" is interpreted:

- Only the final pair of values is compared. Earlier steps are ignored, so a
  run that diverged earlier but recovered on the last step is not flagged.
- Equal values count as neither falling nor rising, so a plateau is not flagged.
- Inputs must be equal-length lists/tuples of at least two numbers. Anything
  else raises `ValueError` (too short, different lengths) or `TypeError`
  (not a list or tuple, or non-numeric values).

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter3/applied-labs/r16-t001/example.py
```

Expected output:

```
training   = [0.8, 0.5, 0.3]
validation = [0.9, 0.6, 0.7]
divergence on last step: True

training   = [0.8, 0.5, 0.3]
validation = [0.9, 0.6, 0.4]
divergence on last step: False
```

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t001 -p "test_*.py"
```

Expected: `Ran 14 tests ... OK`, exit code 0. Any failing assertion exits non-zero.

## Fixture

| Case | Training | Validation | Last step | Flagged |
|---|---|---|---|---|
| Task example | `[0.8, 0.5, 0.3]` | `[0.9, 0.6, 0.7]` | train falls, val rises | **True** |
| Healthy | `[0.8, 0.5, 0.3]` | `[0.9, 0.6, 0.4]` | both fall | **False** |

## Limitations

- **Simulation only.** The losses are typed by hand. Nothing is trained or
  downloaded, and the example says nothing about how any real model performs.
- **A heuristic, not a diagnosis.** One noisy evaluation step can trip a
  two-step rule. That is why the lesson's `EarlyStoppingCallback` uses
  `early_stopping_patience=3` and waits several evaluations before stopping.
- It does not look at accuracy curves, the size of the train/validation gap,
  or plateaus. The lesson covers those separately.
