# R16-T006: Worked decision example for "Using pretrained models"

A small, standard-library-only example for
[Using pretrained models](../../2.mdx). The lesson makes two points about
picking a checkpoint from the Hub:

1. The checkpoint must suit the task. `camembert-base` is fine in a
   `fill-mask` pipeline, but in `text-classification` the results "would not
   make any sense" because its head does not fit that task.
2. Check the model card for how the model was trained, its limits and its biases.

## The decision table

Each scenario has input facts, a decision and a rationale tied to the lesson.

| Scenario | Key facts | Decision | Rationale |
|---|---|---|---|
| `normal` | head `fill-mask`, requested `fill-mask`, fr/fr, card documented | **use** | Head matches the task, language matches, and the card can be checked |
| `boundary` | the same, but requested `text-classification` | **do-not-use** | One changed fact (the task) flips the decision: the fill-mask head does not fit classification |
| `missing-information` | like `normal`, but `model_card` is `None` | **need-more-info** | Without a card we can't check the training data, limits or biases |

The rules, in order:
1. If any required fact is missing, the decision is **need-more-info**.
2. If the head task doesn't match the requested task, or the language doesn't match, the decision is **do-not-use**.
3. Otherwise the decision is **use**.

`check_table(decide)` compares a decision function with the published table
and returns every mismatch. If a decision in the table is deliberately
changed (for example `boundary` to `use`), the checker reports
`[("boundary", "use", "do-not-use")]`.

**Human review:** the checker only checks decisions. Whether each rationale
really follows the lesson is for a human reviewer to judge.

## Refactor: before and after

- **Before:** `decide_baseline(facts)` is one correct, all-in-one function.
- **After:** `decide(facts)` keeps the same contract, but the responsibility
  "find missing information" moves into its own named function,
  `missing_facts(facts)`. That function returns *which* facts are missing,
  which the baseline could not tell you.
- **Proof of equivalence:** the tests check that before and after give the same
  decision on the three scenarios **and** on all 144 combinations of fact
  values (including `None` and `""`).

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter4/applied-labs/r16-t006/example.py
```

Expected output:

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

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter4/applied-labs/r16-t006 -p "test_*.py"
```

Expected: `Ran 10 tests ... OK`, exit code 0.

## Limitations

- The facts are typed in by hand. Nothing is downloaded, and no checkpoint or pipeline is loaded.
- The three rules are a teaching summary of this lesson. Real model selection also weighs licence, size, evaluation results and more.
- `"documented"` only records that a model card exists. The lab does not read or judge any real model card.
