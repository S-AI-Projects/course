# R16-T005: UI callback contract with an offline service adapter

A small, standard-library-only example for [Gradio, check!](../../8.mdx). The
chapter wraps functions in `gr.Interface(fn, inputs, outputs)` and connects
demos to models and Spaces on the Hub. This lab keeps the callback `fn`
**pure** and puts the external dependency behind a plain callable, so the
whole contract can be tested without Gradio, a network or a model.

## The contract

| Input | Output |
|---|---|
| `"red red apple"` | `{"word_count": 3, "unique_count": 2}` |
| `""` (or whitespace only) | `{"word_count": 0, "unique_count": 0}` |
| anything that is not a `str` (`42`, `None`, a list, bytes) | `TypeError` |

The output schema is checked separately by `validate_output()`:
- exactly the keys `word_count` and `unique_count`;
- both non-negative `int`s (`bool` is not accepted);
- `unique_count <= word_count`.

## The service interface

```python
def analyze_text(text, tokenize=local_tokenize): ...
```

- **Interface:** `tokenize(text: str) -> list[str]`. Any callable with this shape can be plugged in.
- **Offline adapter:** `local_tokenize` is a deterministic whitespace split, and it is case-sensitive (`"Red red"` gives 2 unique words). It is the default and is used by every test.
- **Guard:** if a service returns the wrong type (for example a string instead of a list), `analyze_text` raises `TypeError` instead of returning wrong counts.

In a real app you could pass a different `tokenize`, such as one that calls a
hosted model, without changing the callback. Wiring it into Gradio would look
like this. It is **not run here**, because Gradio is not a dependency of this lab:

```python
import gradio as gr
gr.Interface(fn=analyze_text, inputs="text", outputs="json").launch()
```

## What this mock does NOT establish

- Network behaviour of a real service: latency, timeouts, rate limits, outages, retries.
- Authentication or access tokens.
- How a real model tokenizes text. Subword tokenizers give different counts.
- Gradio itself: component conversion, queueing, the browser UI.

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter9/applied-labs/r16-t005/example.py
```

Expected output:

```
Service: local_tokenize (offline mock - no network, no model, no Gradio)
analyze_text('red red apple') -> {'word_count': 3, 'unique_count': 2}
analyze_text('') -> {'word_count': 0, 'unique_count': 0}
analyze_text(42) -> TypeError: text must be a str, got int
```

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t005 -p "test_*.py"
```

Expected: `Ran 12 tests ... OK`, exit code 0.
