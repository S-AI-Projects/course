# R16-T007: Interface callback, worked example with checks

A small, standard-library-only example for
[Understanding the Interface class](../../3.mdx).
`gr.Interface(fn, inputs, outputs)` needs a function and the components for
its inputs and outputs. This lab writes the `fn` for a one-textbox-in,
JSON-out text-analysis demo and checks its contract **without Gradio**:

| Interface part | In this lab | Contract |
|---|---|---|
| `fn` | `analyze_text` | pure function, no side effects |
| `inputs="text"` | one `str` argument | non-`str` raises `TypeError` |
| `outputs="json"` | a `dict` | exactly `word_count` and `unique_count`, both `int` |

## Worked example: `"red red apple"`

The block below is produced by `explain("red red apple")`. The test
`test_readme_worked_example_matches_code` reads this README and checks that
the block matches the code line for line. If either one changes, the test fails.

<!-- worked-example:start -->
```
1. input (inputs="text")    : 'red red apple'
2. split on whitespace      : ['red', 'red', 'apple']
3. word_count = len(tokens) : 3
4. distinct words           : ['red', 'apple']
5. unique_count = len(set)  : 2
6. return (outputs="json")  : {'word_count': 3, 'unique_count': 2}
```
<!-- worked-example:end -->

Why each step:
- **Step 2:** whitespace split turns the textbox string into words. Repeated words stay as separate items.
- **Step 3:** `word_count` counts every item, including repeats, so it is 3.
- **Steps 4–5:** a `set` keeps one copy of each word, so `red` counts once and `unique_count` is 2.
- **Step 6:** the dict is what the `"json"` output component would display.

Other cases: `""` returns `{"word_count": 0, "unique_count": 0}`.
`analyze_text(None)` raises `TypeError: text must be a str, got NoneType`.

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter9/applied-labs/r16-t007/example.py
```

The output is the worked example above, followed by:

```
analyze_text('') -> {'word_count': 0, 'unique_count': 0}
analyze_text(None) -> TypeError: text must be a str, got NoneType
```

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t007 -p "test_*.py"
```

Expected: `Ran 10 tests ... OK`, exit code 0.

To try it in a real UI, you would run the code below. It is **not run or
tested here**, because Gradio is not a dependency of this lab:

```python
import gradio as gr
gr.Interface(fn=analyze_text, inputs="text", outputs="json").launch()
```

## Limitations

- Gradio is never imported. The lab checks the callback's contract, not Gradio's component conversion or UI.
- Words are whitespace-separated and case-sensitive (`"Red red"` gives 2 unique words). There is no stemming or punctuation handling.
- This is a teaching callback, not a model, and makes no claims about model behaviour.
