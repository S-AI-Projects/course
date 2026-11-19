"""R16-T010: token-budget preflight with three applied questions (simulation).

Companion to "What to do when you get an error" (chapters/en/chapter8/2.mdx).
The lesson's forward-pass bug came from handing the model the wrong kind of
input (a Python list where a tensor was expected), and the traceback only
showed it deep inside the library. A *preflight* check validates inputs before
the expensive call, so mistakes fail early with a clear message.

This example preflights a prompt against a token budget and reports exactly
what is kept and what is cut.

TEACHING APPROXIMATION: tokens here are whitespace-separated words
(`str.split()`). Real models use subword tokenizers, so real token counts
differ. Nothing here calls or imitates a real tokenizer or model.
"""


def tokenize(prompt):
    """Teaching approximation: split on whitespace."""
    return prompt.split()


def preflight(prompt, budget):
    """Check prompt length against budget and report retained/removed tokens.

    Policy: the budget is a maximum, so exactly `budget` tokens fit.
    Truncation keeps the first `budget` tokens.
    """
    if not isinstance(prompt, str):
        raise TypeError(f"prompt must be a str, got {type(prompt).__name__}")
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise TypeError(f"budget must be an int, got {type(budget).__name__}")
    if budget < 0:
        raise ValueError(f"budget must be >= 0, got {budget}")

    tokens = tokenize(prompt)
    retained = tokens[:budget]
    removed = len(tokens) - len(retained)
    return {
        "budget": budget,
        "token_count": len(tokens),
        "retained": retained,
        "removed_count": removed,
        "truncated": removed > 0,
    }


# Three applied questions about this example. Each factual answer is
# executed as a regression check in test_example.py (class AppliedQuestions).
QUESTIONS = [
    {
        "id": "Q1",
        "kind": "predict an output",
        "question": "What does preflight('a b c', 2) retain, and how many tokens are removed?",
        "answer": "retained=['a', 'b'], removed_count=1, truncated=True",
        "rationale": "The budget is 2, so only the first two whitespace tokens fit; "
                     "the third token is cut and counted as removed.",
    },
    {
        "id": "Q2",
        "kind": "diagnose a failure",
        "question": "preflight(['one', 'two'], 3) raises an error. Which one, and how do you fix it?",
        "answer": "TypeError: prompt must be a str, got list. Fix: pass the text, "
                  "e.g. preflight(' '.join(['one', 'two']), 3).",
        "rationale": "Like the lesson's list-instead-of-tensor bug, the data is right but "
                     "the container type is wrong. Preflight catches it before any model call, "
                     "with a message naming the expected and actual types.",
    },
    {
        "id": "Q3",
        "kind": "choose a boundary policy",
        "question": "A prompt has exactly as many tokens as the budget (4 tokens, budget 4). "
                    "Should it be truncated?",
        "answer": "No: truncated=False, removed_count=0.",
        "rationale": "A budget is a maximum ('at most N tokens'), so N tokens fit. Treating it "
                     "as 'fewer than N' would cut a token from prompts that are already valid.",
    },
]


def format_report(result):
    status = "TRUNCATED" if result["truncated"] else "fits"
    return (
        f"budget={result['budget']} tokens={result['token_count']} "
        f"retained={result['retained']} removed={result['removed_count']} -> {status}"
    )


if __name__ == "__main__":
    print("Tokenizer: whitespace split (teaching approximation, not a model tokenizer)")
    print(format_report(preflight("one two three four", 3)))
    print(format_report(preflight("", 3)))
    try:
        preflight("one two", -1)
    except ValueError as exc:
        print(f"budget=-1 rejected: {exc}")
    print()
    for q in QUESTIONS:
        print(f"{q['id']} ({q['kind']}): {q['question']}")
        print(f"   answer: {q['answer']}")
