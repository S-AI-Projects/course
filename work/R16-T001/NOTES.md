# R16-T001 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T001/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only: `unittest`, `numbers`)
- macOS (Darwin 27.2.0)

## Inputs and expected vs. actual

Command: `python3 chapters/en/chapter3/applied-labs/r16-t001/example.py`, run from the repo root.

| Case | Training | Validation | Expected | Actual |
|---|---|---|---|---|
| Task fixture | `[0.8, 0.5, 0.3]` | `[0.9, 0.6, 0.7]` | `True` | `True` |
| Both decreasing | `[0.8, 0.5, 0.3]` | `[0.9, 0.6, 0.4]` | `False` | `False` |

Actual output:

```
training   = [0.8, 0.5, 0.3]
validation = [0.9, 0.6, 0.7]
divergence on last step: True

training   = [0.8, 0.5, 0.3]
validation = [0.9, 0.6, 0.4]
divergence on last step: False
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t001 -p "test_*.py" -v`

```
test_both_rising_is_not_divergence ... ok
test_flat_training_is_not_falling ... ok
test_flat_validation_is_not_rising ... ok
test_only_last_step_matters ... ok
test_shortest_valid_input_two_steps ... ok
test_tuples_are_accepted ... ok
test_bool_value_is_rejected ... ok
test_empty_is_rejected ... ok
test_mismatched_lengths_are_rejected ... ok
test_non_numeric_value_is_rejected ... ok
test_non_sequence_is_rejected ... ok
test_too_short_is_rejected ... ok
test_both_decreasing_is_not_flagged ... ok
test_task_fixture_flags_divergence ... ok

Ran 14 tests in 0.001s
OK
```

Exit code: 0. 14 tests: 2 normal, 6 boundary, 6 failure.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I flipped one comparison in `detect_divergence`
so that "training fell" became "training rose":

```diff
-    training_fell = training[-1] < training[-2]
+    training_fell = training[-1] > training[-2]
```

Running the same test command against that copy:

```
FAIL: test_both_rising_is_not_divergence    AssertionError: True is not false
FAIL: test_shortest_valid_input_two_steps   AssertionError: False is not true
FAIL: test_tuples_are_accepted              AssertionError: False is not true
FAIL: test_task_fixture_flags_divergence    AssertionError: False is not true

Ran 14 tests
FAILED (failures=4)
```

Exit code: 1. The tests catch a reversed rule. The committed code was not changed.
