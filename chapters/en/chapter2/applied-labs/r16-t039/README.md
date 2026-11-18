# R16-T039: worked decision example for pipeline steps

Applied example for the lesson "Introduction" (`chapters/en/chapter2/1.mdx`).

Task type: Evaluation experiment.

## What it shows

Three scenarios decide which pipeline step to inspect. Rule sets of three sizes are compared on the same small fixture using exact-match correctness and the number of rule comparisons. The numbers describe this fixture only. A human reviewer should confirm that each rationale follows the lesson.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t039 -p "test_*.py"
```

## Output of `python3 example.py`

```text
| Scenario | Decision | Rationale |
| --- | --- | --- |
| normal | tokenizer | The symptom matches the tokenizer step, so look there first. |
| boundary | unknown_symptom | A symptom outside the three steps is reported as unknown, not guessed. |
| missing_information | need_more_information | No symptom was given, so ask for it before choosing a step. |

Checker problems: []
Three rule-set sizes on the same fixture:
  small: rules=1 correct=3/5 comparisons=4
  medium: rules=2 correct=4/5 comparisons=7
  full: rules=3 correct=5/5 comparisons=9
Trade-off seen here: more rules fit more fixture cases but cost more comparisons.
Fixture results only, not real-world model accuracy.
```

## Scope and limits

The results describe a five-case hand-made fixture only, not real-world model accuracy. It is a local, deterministic teaching fixture. It makes no claim about real hardware, cloud service behavior or trained-model performance.
