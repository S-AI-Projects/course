# R16-T002: Reproducible error and five-field bug report

A small, standard-library-only example for
[Asking for help on the forums](../../3.mdx). The lesson builds up a forum post
around an `IndexError` caused by an input longer than the model's maximum
sequence length (583 > 512). This lab copies that failure with a toy
"model" that has only **8 position slots**, then generates the report the
lesson recommends.

## The contract

- `embed_positions(token_ids)` gives each token the label of its position slot
  (`pos0`, `pos1`, ...). It is a stand-in for a forward pass.
- With **9** tokens it always raises `IndexError: list index out of range`.
- Removing the triggering 9th token (`FIXED_INPUT = FAILING_INPUT[:-1]`) makes
  it succeed.
- `build_report(token_ids)` returns exactly five fields: **environment,
  command, expected, actual, traceback**.

## Boundary decision

| Case | Tokens | Result | Why |
|---|---|---|---|
| Smallest valid | 1 | `["pos0"]` | Uses slot 0 |
| Boundary (valid) | 8 | `pos0..pos7` | Slots are numbered 0..7, so 8 tokens fit exactly |
| Invalid (the bug) | 9 | `IndexError` | Token 9 asks for slot 8, which does not exist |
| Rejected | 0 | `ValueError` | Nothing to embed |

The boundary is the classic off-by-one: `max_positions` slots allow
`max_positions` tokens, not `max_positions + 1`.

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter8/applied-labs/r16-t002/example.py
```

Expected output (traceback line numbers and paths may differ):

```
--- failing input (9 tokens, max 8) ---
**environment**
Python 3.x.y on <OS>

**command**
python3 chapters/en/chapter8/applied-labs/r16-t002/example.py

**expected**
9 position labels (pos0..pos8)

**actual**
IndexError: list index out of range

**traceback**
Traceback (most recent call last):
  ...
IndexError: list index out of range

--- fixed input (8 tokens: last token removed) ---
returned 8 position labels
```

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t002 -p "test_*.py"
```

Expected: `Ran 13 tests ... OK`, exit code 0.

## No secrets

The environment field contains only the Python version and the OS name. The
report never reads environment variables, and the home directory in traceback
paths is replaced by `~`. A test sets a fake `HF_TOKEN` and checks that it
does not appear in the report.

## Limitations

- **Simulation only.** `embed_positions` is not Transformers code. A real
  model's message, traceback and maximum length (for example 512) differ.
- The report shows the structure of a good forum post. It is not a template
  that guarantees anyone will answer.
