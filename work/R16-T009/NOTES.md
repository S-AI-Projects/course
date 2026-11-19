# R16-T009 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T009/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

Toy word-level tokenizer (whitespace split plus a 16-word English vocabulary). This is a simulation, not a real tokenizer.

| Scenario | Facts | Unknown rate | Expected | Actual |
|---|---|---|---|---|
| normal | from-scratch, Japanese sample | 1 | train-new | train-new |
| boundary | from-scratch, `"the new text zebra"` | 1/4 (exactly) | reuse | reuse |
| missing-information | from-scratch, sample None | n/a | need-more-info | need-more-info |

Experiment (same 12-token corpus, threshold 1/4):

| Vocab size | Expected rate (hand calculation) | Actual rate | Decision |
|---|---|---|---|
| 4 | 1/2 | 1/2 | train-new |
| 8 | 1/6 | 1/6 | reuse |
| 16 | 0 | 0 | reuse |

## Example run

Command (from the repo root): `python3 chapters/en/chapter6/applied-labs/r16-t009/example.py`

```
Toy word-level tokenizer (simulation) - not a real tokenizer.

[normal] {'training_mode': 'from-scratch', 'corpus_sample': '私は猫が好きです 今日は晴れです'} -> train-new
[boundary] {'training_mode': 'from-scratch', 'corpus_sample': 'the new text zebra'} -> reuse
[missing-information] {'training_mode': 'from-scratch', 'corpus_sample': None} -> need-more-info
check_table -> all decisions match

Experiment: 12-token corpus, threshold 1/4
vocab_size  unknown_rate  decision
         4    1/2 (0.50)  train-new
         8    1/6 (0.17)  reuse
        16      0 (0.00)  reuse
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t009 -p "test_*.py" -v`

```
test_boundary_sits_exactly_on_the_threshold (test_example.DecisionTable.test_boundary_sits_exactly_on_the_threshold) ... ok
test_checker_fails_when_a_decision_is_changed (test_example.DecisionTable.test_checker_fails_when_a_decision_is_changed) ... ok
test_checker_passes_on_published_table (test_example.DecisionTable.test_checker_passes_on_published_table) ... ok
test_japanese_sample_is_fully_unknown (test_example.DecisionTable.test_japanese_sample_is_fully_unknown) ... ok
test_three_scenarios_with_explicit_decisions (test_example.DecisionTable.test_three_scenarios_with_explicit_decisions) ... ok
test_corpus_has_twelve_tokens (test_example.Experiment.test_corpus_has_twelve_tokens) ... ok
test_three_configurations_match_hand_calculation (test_example.Experiment.test_three_configurations_match_hand_calculation) ... ok
test_trade_off_bigger_vocab_never_increases_unknowns (test_example.Experiment.test_trade_off_bigger_vocab_never_increases_unknowns) ... ok
test_fine_tune_always_reuses (test_example.Rules.test_fine_tune_always_reuses) ... ok
test_missing_or_unknown_mode_needs_more_info (test_example.Rules.test_missing_or_unknown_mode_needs_more_info) ... ok
test_unknown_rate_rejects_empty_sample (test_example.Rules.test_unknown_rate_rejects_empty_sample) ... ok
test_whitespace_only_sample_needs_more_info (test_example.Rules.test_whitespace_only_sample_needs_more_info) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.000s

OK
```

Exit code: 0. Ran 12 tests in 0.000s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- return "train-new" if unknown_rate(sample, vocab) > MAX_UNKNOWN_RATE else "reuse"
+ return "train-new" if unknown_rate(sample, vocab) >= MAX_UNKNOWN_RATE else "reuse"
```

Running the same test command against that copy:

```
FAIL: test_checker_fails_when_a_decision_is_changed
FAIL: test_checker_passes_on_published_table

Ran 12 tests in 0.002s
FAILED (failures=2)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
