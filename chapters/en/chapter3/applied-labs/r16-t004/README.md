# R16-T004: Security-scenario rubric with a state trace

A small, standard-library-only example for the
[End-of-chapter Certificate](../../7.mdx) page, which closes chapter 3 with an
automatically graded quiz. This lab looks at **what an automatic grader can
and cannot check**. It grades three *fictional* security scenarios taken from
the chapter's own workflow: fine-tuning a model and sharing it on the Hub.

## The scenarios

| ID | Asset | Threat (`threat_type`) | Control (`addresses`) | Residual risk |
|---|---|---|---|---|
| S1-token | Write-access Hub token | Token pasted in a shared notebook (`credential-leak`) | `huggingface-cli login`, revoke if exposed (`credential-leak`) | Old outputs or shell history may still hold it |
| S2-dataset | Private customer-review data | Data folder pushed with the model (`data-exposure`) | Check the files before pushing, keep data out of the repo (`data-exposure`) | The model may reproduce rare examples |
| S3-quiz-login | Learner's Hub account | Look-alike sign-in page (`phishing`) | Sign in only on huggingface.co, turn on 2FA (`phishing`) | A convincing look-alike can still fool a user |

Two broken "student answers" are derived from them:
- `MISSING_ASSET` is S1 without its asset.
- `MISMATCHED_CONTROL` is S2 with a 2FA control, which addresses `phishing` rather than the named `data-exposure` threat.

## The checker and its trace

`check_scenario(scenario)` runs three steps and records its state after each one:

| Step | State recorded | Problem means |
|---|---|---|
| 1. `required_fields` | `{"missing": [...]}` | **fail**, and steps 2–3 are recorded as `"skipped"` |
| 2. `non_empty_text` | `{"blank": [...]}` | **fail**, and step 3 is recorded as `"skipped"` |
| 3. `control_matches` | `{"threat_type", "addresses", "matches"}` | **review** when `matches` is False |

All steps clean means **pass**.

**Invariant (tested):** the final verdict can always be worked out from the
recorded states alone. The test reads the trace independently and checks that
it leads to the same verdict for every case, including the broken ones.

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter3/applied-labs/r16-t004/example.py
```

Expected output (abridged):

```
S1-token: PASS
  after required_fields  {'missing': []}
  after non_empty_text   {'blank': []}
  after control_matches  {'threat_type': 'credential-leak', 'addresses': 'credential-leak', 'matches': True}
...
S1-no-asset: FAIL
  after required_fields  {'missing': ['asset']}
  after non_empty_text   skipped
  after control_matches  skipped
S2-wrong-control: REVIEW
  ...
  after control_matches  {'threat_type': 'data-exposure', 'addresses': 'phishing', 'matches': False}
```

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t004 -p "test_*.py"
```

Expected: `Ran 10 tests ... OK`, exit code 0.

## Limitations: what automatic grading cannot do

- The checker verifies **structure only**: fields are present, fields are not blank, and the tags match. A human reviewer judges whether the explanation is correct and sensible. One test shows that a well-formed but meaningless answer still passes.
- Whether a control "addresses" a threat is decided by a tag the author writes. The checker cannot tell if the tag is honest.
- The scenarios are fictional teaching material. They are not a security assessment of the Hub or of any real project.
