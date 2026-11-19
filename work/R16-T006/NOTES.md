# R16-T006 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T006/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

Facts are typed in by hand. No checkpoint is downloaded or loaded.

| Scenario | Changed fact | Expected decision | `decide` (after) | `decide_baseline` (before) |
|---|---|---|---|---|
| normal | (none) | use | use | use |
| boundary | requested_task = text-classification | do-not-use | do-not-use | do-not-use |
| missing-information | model_card = None | need-more-info | need-more-info | need-more-info |

- Before and after were also compared on all 144 combinations of fact values: all equal.
- Checker with a deliberately changed table (`boundary` → `use`): reports `[("boundary", "use", "do-not-use")]`.

## Example run

Command (from the repo root): `python3 chapters/en/chapter4/applied-labs/r16-t006/example.py`

```
Simulated facts only - no checkpoint is downloaded or loaded.

[normal] camembert-base: head=fill-mask requested=fill-mask card=documented
   decision: use   missing: []
[boundary] camembert-base: head=fill-mask requested=text-classification card=documented
   decision: do-not-use   missing: []
[missing-information] camembert-base: head=fill-mask requested=fill-mask card=None
   decision: need-more-info   missing: ['model_card']

check_table(decide)          -> all decisions match
check_table(decide_baseline) -> all decisions match
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter4/applied-labs/r16-t006 -p "test_*.py" -v`

```
test_boundary_differs_from_normal_by_one_fact (test_example.DecisionTable.test_boundary_differs_from_normal_by_one_fact) ... ok
test_checker_fails_when_a_decision_is_changed (test_example.DecisionTable.test_checker_fails_when_a_decision_is_changed) ... ok
test_checker_passes_on_published_table (test_example.DecisionTable.test_checker_passes_on_published_table) ... ok
test_three_scenarios_with_explicit_decisions (test_example.DecisionTable.test_three_scenarios_with_explicit_decisions) ... ok
test_absent_key_counts_as_missing (test_example.Refactor.test_absent_key_counts_as_missing) ... ok
test_before_and_after_agree_on_every_combination (test_example.Refactor.test_before_and_after_agree_on_every_combination) ... ok
test_before_and_after_agree_on_fixture (test_example.Refactor.test_before_and_after_agree_on_fixture) ... ok
test_extracted_responsibility_lists_missing_facts (test_example.Refactor.test_extracted_responsibility_lists_missing_facts) ... ok
test_language_mismatch_is_do_not_use (test_example.Rules.test_language_mismatch_is_do_not_use) ... ok
test_missing_info_wins_over_mismatch (test_example.Rules.test_missing_info_wins_over_mismatch) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
```

Exit code: 0. Ran 10 tests in 0.001s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- if missing_facts(facts):
+ if missing_facts(facts) and False:
```

Running the same test command against that copy:

```
ERROR: test_absent_key_counts_as_missing
FAIL: test_checker_fails_when_a_decision_is_changed
FAIL: test_checker_passes_on_published_table
FAIL: test_before_and_after_agree_on_every_combination  (x128 subtests)
FAIL: test_before_and_after_agree_on_fixture
FAIL: test_missing_info_wins_over_mismatch

Ran 10 tests in 0.017s
FAILED (failures=132, errors=1)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
