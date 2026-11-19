# R16-T005 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T005/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

Service used: `local_tokenize`, the offline mock (whitespace split, case-sensitive). No network, model or Gradio.

| Case | Input | Expected | Actual |
|---|---|---|---|
| Task fixture | `"red red apple"` | `{"word_count": 3, "unique_count": 2}` | same |
| Empty | `""` | `{"word_count": 0, "unique_count": 0}` | same |
| Non-string | `42`, `None`, list, bytes | `TypeError` | `TypeError` |
| Plugged-in service | custom callable returning `["fixed","fixed"]` | `{2, 1}`, called once | same (test) |
| Broken service | returns a `str` instead of a list | `TypeError` | `TypeError` (test) |
| Bad outputs | 7 schema violations | `ValueError` each | `ValueError` each (test) |

## Example run

Command (from the repo root): `python3 chapters/en/chapter9/applied-labs/r16-t005/example.py`

```
Service: local_tokenize (offline mock - no network, no model, no Gradio)
analyze_text('red red apple') -> {'word_count': 3, 'unique_count': 2}
analyze_text('') -> {'word_count': 0, 'unique_count': 0}
analyze_text(42) -> TypeError: text must be a str, got int
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t005 -p "test_*.py" -v`

```
test_invalid_outputs_are_rejected (test_example.OutputSchema.test_invalid_outputs_are_rejected) ... ok
test_schema_keys (test_example.OutputSchema.test_schema_keys) ... ok
test_valid_output_passes (test_example.OutputSchema.test_valid_output_passes) ... ok
test_any_callable_can_be_plugged_in (test_example.ServiceAdapter.test_any_callable_can_be_plugged_in) ... ok
test_counting_is_case_sensitive (test_example.ServiceAdapter.test_counting_is_case_sensitive) ... ok
test_default_service_is_the_local_adapter (test_example.ServiceAdapter.test_default_service_is_the_local_adapter) ... ok
test_local_adapter_is_deterministic (test_example.ServiceAdapter.test_local_adapter_is_deterministic) ... ok
test_service_returning_wrong_type_is_caught (test_example.ServiceAdapter.test_service_returning_wrong_type_is_caught) ... ok
test_whitespace_only_is_empty (test_example.ServiceAdapter.test_whitespace_only_is_empty) ... ok
test_empty_text_returns_zeros (test_example.TaskContract.test_empty_text_returns_zeros) ... ok
test_non_string_is_rejected (test_example.TaskContract.test_non_string_is_rejected) ... ok
test_red_red_apple (test_example.TaskContract.test_red_red_apple) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
```

Exit code: 0. Ran 12 tests in 0.000s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- "unique_count": len(set(tokens))}
+ "unique_count": len(tokens)}
```

Running the same test command against that copy:

```
FAIL: test_any_callable_can_be_plugged_in (test_example.ServiceAdapter.test_any_callable_can_be_plugged_in)
FAIL: test_red_red_apple (test_example.TaskContract.test_red_red_apple)

Ran 12 tests in 0.005s
FAILED (failures=2)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
