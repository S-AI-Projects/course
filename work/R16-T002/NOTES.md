# R16-T002 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T002/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

| Case | Input | Expected | Actual |
|---|---|---|---|
| Failing fixture | 9 token ids (max 8) | `IndexError: list index out of range` | `IndexError: list index out of range` |
| Trigger removed | first 8 of those ids | 8 position labels | `returned 8 position labels` |
| Smallest valid | `[101]` | `["pos0"]` | `["pos0"]` (test) |
| Empty | `[]` | `ValueError` | `ValueError` (test) |
| Report fields | failing fixture | environment, command, expected, actual, traceback | all five present, non-empty (test) |
| Secrets | fake `HF_TOKEN` in env | not in report | not in report (test) |

## Example run

Command (from the repo root): `python3 chapters/en/chapter8/applied-labs/r16-t002/example.py`

```
--- failing input (9 tokens, max 8) ---
**environment**
Python 3.14.7 on Darwin

**command**
python3 chapters/en/chapter8/applied-labs/r16-t002/example.py

**expected**
9 position labels (pos0..pos8)

**actual**
IndexError: list index out of range

**traceback**
```
Traceback (most recent call last):
  File "~/course/chapters/en/chapter8/applied-labs/r16-t002/example.py", line 69, in build_report
    labels = embed_positions(token_ids)
  File "~/course/chapters/en/chapter8/applied-labs/r16-t002/example.py", line 53, in embed_positions
    return [position_table[i] for i in range(len(token_ids))]
            ~~~~~~~~~~~~~~^^^
IndexError: list index out of range
```

--- fixed input (8 tokens: last token removed) ---
returned 8 position labels
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t002 -p "test_*.py" -v`

```
test_exactly_max_positions_is_valid (test_example.BoundaryCases.test_exactly_max_positions_is_valid) ... ok
test_one_over_max_positions_raises_index_error (test_example.BoundaryCases.test_one_over_max_positions_raises_index_error) ... ok
test_smallest_valid_input_one_token (test_example.BoundaryCases.test_smallest_valid_input_one_token) ... ok
test_empty_input_is_rejected (test_example.InvalidInput.test_empty_input_is_rejected) ... ok
test_non_int_token_is_rejected (test_example.InvalidInput.test_non_int_token_is_rejected) ... ok
test_non_list_is_rejected (test_example.InvalidInput.test_non_list_is_rejected) ... ok
test_report_contains_no_secrets_or_home_path (test_example.Report.test_report_contains_no_secrets_or_home_path) ... ok
test_report_for_fixed_input_has_no_exception (test_example.Report.test_report_for_fixed_input_has_no_exception) ... ok
test_report_has_exactly_the_five_fields (test_example.Report.test_report_has_exactly_the_five_fields) ... ok
test_report_records_the_exception (test_example.Report.test_report_records_the_exception) ... ok
test_failure_is_deterministic (test_example.Reproduction.test_failure_is_deterministic) ... ok
test_fixture_is_one_token_too_long (test_example.Reproduction.test_fixture_is_one_token_too_long) ... ok
test_removing_trigger_makes_it_succeed (test_example.Reproduction.test_removing_trigger_makes_it_succeed) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.002s

OK
```

Exit code: 0. Ran 13 tests in 0.002s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- for i in range(max_positions)]
+ for i in range(max_positions + 1)]
```

Running the same test command against that copy:

```
FAIL: test_one_over_max_positions_raises_index_error (test_example.BoundaryCases.test_one_over_max_positions_raises_index_error)
FAIL: test_report_records_the_exception (test_example.Report.test_report_records_the_exception)
FAIL: test_failure_is_deterministic (test_example.Reproduction.test_failure_is_deterministic)

Ran 13 tests in 0.005s
FAILED (failures=3)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
