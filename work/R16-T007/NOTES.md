# R16-T007 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T007/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

| Case | Input | Expected | Actual |
|---|---|---|---|
| Worked example | `"red red apple"` | `{"word_count": 3, "unique_count": 2}` | same |
| README block | the published 6 steps | identical to `explain("red red apple")` | identical (test) |
| Empty | `""` | `{"word_count": 0, "unique_count": 0}` | same |
| Non-string | `None`, `3`, list, bytes | `TypeError` | `TypeError` |
| Case | `"Red red"` | `{2, 2}` (case-sensitive) | same (test) |

## Example run

Command (from the repo root): `python3 chapters/en/chapter9/applied-labs/r16-t007/example.py`

```
1. input (inputs="text")    : 'red red apple'
2. split on whitespace      : ['red', 'red', 'apple']
3. word_count = len(tokens) : 3
4. distinct words           : ['red', 'apple']
5. unique_count = len(set)  : 2
6. return (outputs="json")  : {'word_count': 3, 'unique_count': 2}

analyze_text('') -> {'word_count': 0, 'unique_count': 0}
analyze_text(None) -> TypeError: text must be a str, got NoneType
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t007 -p "test_*.py" -v`

```
test_case_sensitive (test_example.OutputShape.test_case_sensitive) ... ok
test_output_keys_and_types (test_example.OutputShape.test_output_keys_and_types) ... ok
test_unique_never_exceeds_total (test_example.OutputShape.test_unique_never_exceeds_total) ... ok
test_whitespace_only_counts_as_empty (test_example.OutputShape.test_whitespace_only_counts_as_empty) ... ok
test_empty_text_returns_zeros (test_example.TaskContract.test_empty_text_returns_zeros) ... ok
test_non_string_is_rejected (test_example.TaskContract.test_non_string_is_rejected) ... ok
test_red_red_apple (test_example.TaskContract.test_red_red_apple) ... ok
test_readme_worked_example_matches_code (test_example.WorkedExample.test_readme_worked_example_matches_code) ... ok
test_worked_example_ends_with_the_real_output (test_example.WorkedExample.test_worked_example_ends_with_the_real_output) ... ok
test_worked_example_has_six_steps (test_example.WorkedExample.test_worked_example_has_six_steps) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
```

Exit code: 0. Ran 10 tests in 0.001s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- unique = len(set(tokens))
+ unique = len(tokens)
```

Running the same test command against that copy:

```
FAIL: test_red_red_apple (test_example.TaskContract.test_red_red_apple)
FAIL: test_readme_worked_example_matches_code (test_example.WorkedExample.test_readme_worked_example_matches_code)

Ran 10 tests in 0.002s
FAILED (failures=2)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
