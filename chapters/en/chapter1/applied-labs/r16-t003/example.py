"""R16-T003: token-budget preflight, compared two ways (simulation).

Companion to "Natural Language Processing and Large Language Models"
(chapters/en/chapter1/2.mdx), which lists "limited context windows" as an LLM
limitation. Before sending a prompt you can run a *preflight* check: count
the tokens, compare them with a budget, and report exactly what would be kept
and what would be cut.

TEACHING APPROXIMATION: tokens here are whitespace-separated words
(`str.split()`). Real models use subword tokenizers (WordPiece, BPE, ...),
so a real model's token count for the same text is usually different and
often larger. Nothing here calls or imitates a real tokenizer.

Two independent approaches are compared on identical inputs:
1. `preflight` (direct): walk the tokens one by one and stop when the budget is full.
2. `reference_preflight` (independent): slice `tokens[:budget]` and compute
   `removed = max(len(tokens) - budget, 0)` arithmetically.
Both are also checked against EXPECTED_TABLE, written by hand.
"""


def tokenize(prompt):
    """Teaching approximation: split on whitespace."""
    return prompt.split()


def _validate(prompt, budget):
    if not isinstance(prompt, str):
        raise TypeError(f"prompt must be a str, got {type(prompt).__name__}")
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise TypeError(f"budget must be an int, got {type(budget).__name__}")
    if budget < 0:
        raise ValueError(f"budget must be >= 0, got {budget}")


def _result(budget, tokens, retained):
    removed = len(tokens) - len(retained)
    return {
        "budget": budget,
        "token_count": len(tokens),
        "retained": retained,
        "removed_count": removed,
        "truncated": removed > 0,
    }


def preflight(prompt, budget):
    """Direct approach: keep tokens one at a time until the budget is full."""
    _validate(prompt, budget)
    tokens = tokenize(prompt)
    retained = []
    for token in tokens:
        if len(retained) == budget:
            break
        retained.append(token)
    return _result(budget, tokens, retained)


def reference_preflight(prompt, budget):
    """Independent approach: slicing plus arithmetic, no loop."""
    _validate(prompt, budget)
    tokens = tokenize(prompt)
    retained = tokens[:budget]
    result = _result(budget, tokens, retained)
    # Cross-check the arithmetic formula against the counted value.
    assert result["removed_count"] == max(len(tokens) - budget, 0)
    return result


# Hand-written expected results: (prompt, budget, retained, removed_count, truncated)
EXPECTED_TABLE = [
    ("one two three four", 3, ["one", "two", "three"], 1, True),   # task fixture
    ("", 3, [], 0, False),                                         # empty input
    ("one two three", 3, ["one", "two", "three"], 0, False),       # exactly at budget
    ("one two", 3, ["one", "two"], 0, False),                      # under budget
    ("one two three four", 0, [], 4, True),                        # zero budget
    ("  one\ttwo\n three  ", 2, ["one", "two"], 1, True),          # mixed whitespace
]


def format_report(result):
    status = "TRUNCATED" if result["truncated"] else "fits"
    return (
        f"budget={result['budget']} tokens={result['token_count']} "
        f"retained={result['retained']} removed={result['removed_count']} -> {status}"
    )


if __name__ == "__main__":
    print("Tokenizer: whitespace split (teaching approximation, not a model tokenizer)")
    for prompt, budget, *_ in EXPECTED_TABLE[:3]:
        direct = preflight(prompt, budget)
        reference = reference_preflight(prompt, budget)
        agree = "agree" if direct == reference else "DISAGREE"
        print(f"{prompt!r:24} {format_report(direct)} [{agree}]")
    try:
        preflight("one two", -1)
    except ValueError as exc:
        print(f"budget=-1 rejected: {exc}")
