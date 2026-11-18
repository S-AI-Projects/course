# R16-T036: worked decision example for asking for help

Applied example for the lesson "Introduction" (`chapters/en/chapter8/1.mdx`).

Task type: Refactor the teaching example.

## What it shows

Three scenarios decide whether a help request is ready to post. A correct baseline is written first, then one named responsibility (finding unknown facts) is extracted. The tests prove before/after equivalence on the fixture and on all 27 fact combinations. A human reviewer should confirm that each rationale follows the lesson.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t036 -p "test_*.py"
```

## Output of `python3 example.py`

```text
| Scenario | Decision | Rationale |
| --- | --- | --- |
| normal | post_question | A traceback, a minimal example and versions give readers what they need. |
| boundary | add_versions_then_post | Only the versions are missing, so add them and then post. |
| missing_information | need_more_information | Two facts are unknown, so gather them before deciding. |

Checker problems (baseline): []
Checker problems (refactored): []
Before/after equivalent on 27 fact combinations: True
```

## Scope and limits

It is a local, deterministic teaching fixture. It makes no claim about real hardware, cloud service behavior or trained-model performance.
