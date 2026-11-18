# R16-T035: worked decision example for sharing a model

Applied example for the lesson "Sharing pretrained models" (`chapters/en/chapter4/3.mdx`).

Task type: Offline service adapter.

## What it shows

Three scenarios (normal, boundary, missing information) each have input facts, a decision and a rationale. The model hub sits behind a callable interface and a deterministic offline adapter stands in for it. The checker fails when a decision is changed. A human reviewer should confirm that each rationale follows the lesson.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter4/applied-labs/r16-t035 -p "test_*.py"
```

## Output of `python3 example.py`

```text
| Scenario | Decision | Rationale |
| --- | --- | --- |
| normal | create_repo_and_push | A new repo name plus weights on disk means create the repo and push. |
| boundary | push_to_existing_repo | The repo name already exists, so push to it instead of creating it again. |
| missing_information | need_more_information | Without a weights flag the decision cannot be made, so ask first. |

Checker problems: []
This offline mock does not establish:
- real login, tokens or permissions
- real repo-name rules or name clashes
- upload size, network errors or rate limits
- how the real hub behaves today
```

## Scope and limits

The offline adapter does not establish real login, permissions, repo-name rules, upload limits, network errors or how the real hub behaves today. It is a local, deterministic teaching fixture. It makes no claim about real hardware, cloud service behavior or trained-model performance.
