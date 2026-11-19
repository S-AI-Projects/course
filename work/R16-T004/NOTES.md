# R16-T004 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T004/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

| Case | Input | Expected verdict | Actual verdict | Trace highlights |
|---|---|---|---|---|
| S1-token | complete, credential-leak → credential-leak | pass | pass | no missing, no blank, matches=True |
| S2-dataset | complete, data-exposure → data-exposure | pass | pass | matches=True |
| S3-quiz-login | complete, phishing → phishing | pass | pass | matches=True |
| S1-no-asset | S1 without `asset` | fail | fail | missing=['asset'], later steps skipped |
| S2-wrong-control | S2 with a 2FA control (`addresses`=phishing) | review | review | matches=False |
| S3-blank-residual | S3 with residual_risk="   " | fail | fail (test) | blank=['residual_risk'] |
| Well-formed nonsense | single-letter fields, tags equal | pass (structure only) | pass (test) | shows the limit of automatic grading |

## Example run

Command (from the repo root): `python3 chapters/en/chapter3/applied-labs/r16-t004/example.py`

```
Structural rubric only - a human reviewer still judges the explanations.

S1-token: PASS
  after required_fields  {'missing': []}
  after non_empty_text   {'blank': []}
  after control_matches  {'threat_type': 'credential-leak', 'addresses': 'credential-leak', 'matches': True}
S2-dataset: PASS
  after required_fields  {'missing': []}
  after non_empty_text   {'blank': []}
  after control_matches  {'threat_type': 'data-exposure', 'addresses': 'data-exposure', 'matches': True}
S3-quiz-login: PASS
  after required_fields  {'missing': []}
  after non_empty_text   {'blank': []}
  after control_matches  {'threat_type': 'phishing', 'addresses': 'phishing', 'matches': True}
S1-no-asset: FAIL
  after required_fields  {'missing': ['asset']}
  after non_empty_text   skipped
  after control_matches  skipped
S2-wrong-control: REVIEW
  after required_fields  {'missing': []}
  after non_empty_text   {'blank': []}
  after control_matches  {'threat_type': 'data-exposure', 'addresses': 'phishing', 'matches': False}
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t004 -p "test_*.py" -v`

```
test_blank_text_field_fails (test_example.Boundaries.test_blank_text_field_fails) ... ok
test_checker_does_not_judge_content (test_example.Boundaries.test_checker_does_not_judge_content) ... ok
test_empty_answer_lists_every_missing_field (test_example.Boundaries.test_empty_answer_lists_every_missing_field) ... ok
test_complete_scenarios_pass (test_example.TaskContract.test_complete_scenarios_pass) ... ok
test_scenario_without_asset_fails (test_example.TaskContract.test_scenario_without_asset_fails) ... ok
test_there_are_three_fictional_scenarios_with_all_fields (test_example.TaskContract.test_there_are_three_fictional_scenarios_with_all_fields) ... ok
test_unrelated_control_is_flagged_for_review (test_example.TaskContract.test_unrelated_control_is_flagged_for_review) ... ok
test_every_step_is_recorded_in_order (test_example.TraceInvariant.test_every_step_is_recorded_in_order) ... ok
test_steps_after_a_failure_are_skipped (test_example.TraceInvariant.test_steps_after_a_failure_are_skipped) ... ok
test_verdict_matches_recorded_state (test_example.TraceInvariant.test_verdict_matches_recorded_state) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.000s

OK
```

Exit code: 0. Ran 10 tests in 0.000s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- matches = scenario["addresses"] == scenario["threat_type"]
+ matches = True
```

Running the same test command against that copy:

```
FAIL: test_unrelated_control_is_flagged_for_review (test_example.TaskContract.test_unrelated_control_is_flagged_for_review)

Ran 10 tests in 0.004s
FAILED (failures=1)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
