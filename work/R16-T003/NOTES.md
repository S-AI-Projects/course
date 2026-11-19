# R16-T003 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T003/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

Tokenizer: whitespace split (`str.split()`), a teaching approximation, not a model tokenizer.

| Prompt | Budget | Expected retained / removed / truncated | Direct `preflight` | Independent `reference_preflight` |
|---|---|---|---|---|
| `"one two three four"` | 3 | `[one,two,three]` / 1 / True | match | match |
| `""` | 3 | `[]` / 0 / False | match | match |
| `"one two three"` | 3 | `[one,two,three]` / 0 / False | match | match |
| `"one two"` | 3 | `[one,two]` / 0 / False | match | match |
| `"one two three four"` | 0 | `[]` / 4 / True | match | match |
| `"  one\ttwo\n three  "` | 2 | `[one,two]` / 1 / True | match | match |
| `"one two"` | -1 | ValueError | ValueError | ValueError |

The two approaches were also compared on all 42 combinations of 0–5 tokens and budget 0–6: all equal.

## Example run

Command (from the repo root): `python3 chapters/en/chapter1/applied-labs/r16-t003/example.py`

```
Tokenizer: whitespace split (teaching approximation, not a model tokenizer)
'one two three four'     budget=3 tokens=4 retained=['one', 'two', 'three'] removed=1 -> TRUNCATED [agree]
''                       budget=3 tokens=0 retained=[] removed=0 -> fits [agree]
'one two three'          budget=3 tokens=3 retained=['one', 'two', 'three'] removed=0 -> fits [agree]
budget=-1 rejected: budget must be >= 0, got -1
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t003 -p "test_*.py" -v`

```
test_exactly_at_budget_is_not_truncated (test_example.Boundaries.test_exactly_at_budget_is_not_truncated) ... ok
test_retained_plus_removed_equals_token_count (test_example.Boundaries.test_retained_plus_removed_equals_token_count) ... ok
test_tokenizer_is_whitespace_split (test_example.Boundaries.test_tokenizer_is_whitespace_split) ... ok
test_zero_budget_removes_everything (test_example.Boundaries.test_zero_budget_removes_everything) ... ok
test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) ... ok
test_direct_matches_expected_table (test_example.CompareApproaches.test_direct_matches_expected_table) ... ok
test_reference_matches_expected_table (test_example.CompareApproaches.test_reference_matches_expected_table) ... ok
test_non_int_budget_is_rejected (test_example.InvalidInput.test_non_int_budget_is_rejected) ... ok
test_non_string_prompt_is_rejected (test_example.InvalidInput.test_non_string_prompt_is_rejected) ... ok
test_budget_three_keeps_first_three_and_removes_one (test_example.TaskContract.test_budget_three_keeps_first_three_and_removes_one) ... ok
test_empty_input_retains_none (test_example.TaskContract.test_empty_input_retains_none) ... ok
test_negative_budget_is_rejected (test_example.TaskContract.test_negative_budget_is_rejected) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.001s

OK
```

Exit code: 0. Ran 12 tests in 0.001s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- if len(retained) == budget:
+ if len(retained) == budget + 1:
```

Running the same test command against that copy:

```
FAIL: test_zero_budget_removes_everything (test_example.Boundaries.test_zero_budget_removes_everything)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=1, budget=0)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=2, budget=0)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=2, budget=1)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=3, budget=0)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=3, budget=1)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=3, budget=2)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=4, budget=0)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=4, budget=1)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=4, budget=2)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=4, budget=3)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=5, budget=0)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=5, budget=1)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=5, budget=2)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=5, budget=3)
FAIL: test_direct_and_reference_agree_on_a_grid (test_example.CompareApproaches.test_direct_and_reference_agree_on_a_grid) (length=5, budget=4)
FAIL: test_direct_matches_expected_table (test_example.CompareApproaches.test_direct_matches_expected_table) (prompt='one two three four', budget=3)
FAIL: test_direct_matches_expected_table (test_example.CompareApproaches.test_direct_matches_expected_table) (prompt='one two three four', budget=0)
FAIL: test_direct_matches_expected_table (test_example.CompareApproaches.test_direct_matches_expected_table) (prompt='  one\ttwo\n three  ', budget=2)
FAIL: test_budget_three_keeps_first_three_and_removes_one (test_example.TaskContract.test_budget_three_keeps_first_three_and_removes_one)

Ran 12 tests in 0.007s
FAILED (failures=20)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
