# R16-T010 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T010/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

Tokenizer: whitespace split (`str.split()`), a teaching approximation, not a model tokenizer.

| Case | Input | Expected | Actual |
|---|---|---|---|
| Task fixture | `"one two three four"`, budget 3 | retained `[one,two,three]`, removed 1, truncated | same |
| Empty | `""`, budget 3 | retained `[]`, removed 0 | same |
| Negative budget | budget -1 | `ValueError` | `ValueError` |
| Q1 predict | `"a b c"`, budget 2 | `[a,b]`, removed 1 | same (test) |
| Q2 diagnose | `['one','two']`, budget 3 | `TypeError: prompt must be a str, got list` | same (test); the fix keeps `[one,two]` |
| Q3 boundary | 4 tokens, budget 4 | not truncated, removed 0 | same (test) |

## Example run

Command (from the repo root): `python3 chapters/en/chapter8/applied-labs/r16-t010/example.py`

```
Tokenizer: whitespace split (teaching approximation, not a model tokenizer)
budget=3 tokens=4 retained=['one', 'two', 'three'] removed=1 -> TRUNCATED
budget=3 tokens=0 retained=[] removed=0 -> fits
budget=-1 rejected: budget must be >= 0, got -1

Q1 (predict an output): What does preflight('a b c', 2) retain, and how many tokens are removed?
   answer: retained=['a', 'b'], removed_count=1, truncated=True
Q2 (diagnose a failure): preflight(['one', 'two'], 3) raises an error. Which one, and how do you fix it?
   answer: TypeError: prompt must be a str, got list. Fix: pass the text, e.g. preflight(' '.join(['one', 'two']), 3).
Q3 (choose a boundary policy): A prompt has exactly as many tokens as the budget (4 tokens, budget 4). Should it be truncated?
   answer: No: truncated=False, removed_count=0.
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t010 -p "test_*.py" -v`

```
test_q1_predict_output (test_example.AppliedQuestions.test_q1_predict_output) ... ok
test_q2_diagnose_failure (test_example.AppliedQuestions.test_q2_diagnose_failure) ... ok
test_q3_boundary_policy_exactly_at_budget_fits (test_example.AppliedQuestions.test_q3_boundary_policy_exactly_at_budget_fits) ... ok
test_three_questions_of_the_required_kinds (test_example.AppliedQuestions.test_three_questions_of_the_required_kinds) ... ok
test_non_int_budget_is_rejected (test_example.MoreBoundaries.test_non_int_budget_is_rejected) ... ok
test_one_over_budget_removes_one (test_example.MoreBoundaries.test_one_over_budget_removes_one) ... ok
test_zero_budget_removes_everything (test_example.MoreBoundaries.test_zero_budget_removes_everything) ... ok
test_budget_three_keeps_first_three_and_removes_one (test_example.TaskContract.test_budget_three_keeps_first_three_and_removes_one) ... ok
test_empty_input_retains_none (test_example.TaskContract.test_empty_input_retains_none) ... ok
test_negative_budget_is_rejected (test_example.TaskContract.test_negative_budget_is_rejected) ... ok
test_tokenizer_is_whitespace_split (test_example.TaskContract.test_tokenizer_is_whitespace_split) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.000s

OK
```

Exit code: 0. Ran 11 tests in 0.000s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- retained = tokens[:budget]
+ retained = tokens[:max(budget - 1, 0)]
```

Running the same test command against that copy:

```
FAIL: test_q1_predict_output (test_example.AppliedQuestions.test_q1_predict_output)
FAIL: test_q3_boundary_policy_exactly_at_budget_fits (test_example.AppliedQuestions.test_q3_boundary_policy_exactly_at_budget_fits)
FAIL: test_one_over_budget_removes_one (test_example.MoreBoundaries.test_one_over_budget_removes_one)
FAIL: test_budget_three_keeps_first_three_and_removes_one (test_example.TaskContract.test_budget_three_keeps_first_three_and_removes_one)

Ran 11 tests in 0.006s
FAILED (failures=4)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
