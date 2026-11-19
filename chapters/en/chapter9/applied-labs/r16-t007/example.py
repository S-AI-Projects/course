"""R16-T007: a worked input-to-output example for an Interface callback.

Companion to "Understanding the Interface class" (chapters/en/chapter9/3.mdx).
`gr.Interface(fn, inputs, outputs)` needs three things:
    fn      - the function to wrap
    inputs  - the component(s) whose values become fn's arguments
    outputs - the component(s) that display fn's return value(s)

This lab writes `fn` for a one-textbox-in, JSON-out text-analysis demo and
checks its contract *without* Gradio:
    inputs="text"  -> fn receives exactly one str
    outputs="json" -> fn returns {"word_count": int, "unique_count": int}

    "red red apple" -> {"word_count": 3, "unique_count": 2}
    ""              -> {"word_count": 0, "unique_count": 0}
    non-string      -> TypeError

`explain(text)` prints each step from input to output. The README publishes
the steps for "red red apple", and a test checks that the README matches
`explain()` exactly, so the documentation cannot drift from the code.

Scope: Gradio is not imported or run. Words are whitespace-separated and
case-sensitive. This is a teaching callback, not a model.
"""

OUTPUT_KEYS = ("word_count", "unique_count")
WORKED_INPUT = "red red apple"


def analyze_text(text):
    """The `fn` for gr.Interface(fn=analyze_text, inputs="text", outputs="json")."""
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")
    tokens = text.split()
    unique = len(set(tokens))
    return {"word_count": len(tokens), "unique_count": unique}


def explain(text):
    """Return the worked example as a list of lines, one per step."""
    tokens = text.split()
    distinct = sorted(set(tokens), key=tokens.index)  # first-seen order, for readability
    result = analyze_text(text)
    steps = [
        ('1. input (inputs="text")', repr(text)),
        ("2. split on whitespace", tokens),
        ("3. word_count = len(tokens)", len(tokens)),
        ("4. distinct words", distinct),
        ("5. unique_count = len(set)", len(distinct)),
        ('6. return (outputs="json")', result),
    ]
    return [f"{label:<28}: {value}" for label, value in steps]


if __name__ == "__main__":
    print("\n".join(explain(WORKED_INPUT)))
    print()
    print(f"analyze_text('') -> {analyze_text('')}")
    try:
        analyze_text(None)
    except TypeError as exc:
        print(f"analyze_text(None) -> TypeError: {exc}")
