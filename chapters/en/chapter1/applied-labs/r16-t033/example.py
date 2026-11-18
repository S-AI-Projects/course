"""Token-budget preflight on a whitespace tokenizer, with two ways to compute it.

Whitespace splitting is a teaching approximation, not the model's real tokenizer.
Real subword tokenizers give different counts.
"""
TOKENIZER_NOTE = "Whitespace splitting is a teaching approximation, not the model's real tokenizer."

# prompt, budget, expected retained tokens, expected removed count
EXPECTED = [
    ("one two three four", 3, ["one", "two", "three"], 1),
    ("", 3, [], 0),
    ("one two", 3, ["one", "two"], 0),
    ("one two three", 3, ["one", "two", "three"], 0),
    ("one two three four", 0, [], 4),
]


def validate_budget(budget):
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise TypeError("budget must be an int")
    if budget < 0:
        raise ValueError(f"budget must be 0 or more, got {budget}")


def check_budget(prompt, budget):
    """Approach 1 (direct): slice the token list."""
    validate_budget(budget)
    tokens = prompt.split()
    retained = tokens[:budget]
    return {"retained": retained, "removed": len(tokens) - len(retained),
            "truncated": len(tokens) > budget}


def check_budget_by_counting(prompt, budget):
    """Approach 2 (independent): walk the tokens one by one, keep or drop."""
    validate_budget(budget)
    kept, dropped = [], 0
    for token in prompt.split():
        if len(kept) < budget:
            kept.append(token)
        else:
            dropped += 1
    return {"retained": kept, "removed": dropped, "truncated": dropped > 0}


def main():
    print(TOKENIZER_NOTE)
    for prompt, budget, retained, removed in EXPECTED:
        direct = check_budget(prompt, budget)
        counted = check_budget_by_counting(prompt, budget)
        same = (direct == counted and direct["retained"] == retained
                and direct["removed"] == removed)
        print(f"{repr(prompt)}, budget {budget}: retained={direct['retained']} "
              f"removed={direct['removed']} match={same}")
    try:
        check_budget("hello", -1)
    except ValueError as err:
        print(f"budget -1 -> ValueError: {err}")


if __name__ == "__main__":
    main()
