"""Token-budget preflight that records its state after every token.

Whitespace splitting is a teaching approximation, not the model's real tokenizer.
Invariant after each step: kept + dropped == tokens seen, and kept <= budget.
"""
TOKENIZER_NOTE = "Whitespace splitting is a teaching approximation, not the model's real tokenizer."


def validate_budget(budget):
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise TypeError("budget must be an int")
    if budget < 0:
        raise ValueError(f"budget must be 0 or more, got {budget}")


def trace_preflight(prompt, budget):
    """Return the final result plus the state after each token."""
    validate_budget(budget)
    retained, removed, steps = [], 0, []
    for seen, token in enumerate(prompt.split(), start=1):
        if len(retained) < budget:
            retained.append(token)
            action = "keep"
        else:
            removed += 1
            action = "drop"
        steps.append({"seen": seen, "token": token, "action": action,
                      "retained": list(retained), "removed": removed})
    return {"retained": retained, "removed": removed, "truncated": removed > 0,
            "steps": steps}


def invariant_problems(result, budget):
    """List every step where the invariant is broken (empty list = holds)."""
    problems = []
    for step in result["steps"]:
        if len(step["retained"]) + step["removed"] != step["seen"]:
            problems.append(f"step {step['seen']}: kept + dropped != tokens seen")
        if len(step["retained"]) > budget:
            problems.append(f"step {step['seen']}: kept more than the budget")
    return problems


def main():
    print(TOKENIZER_NOTE)
    result = trace_preflight("one two three four", 3)
    for step in result["steps"]:
        print(f"after token {step['seen']} ({repr(step['token'])}): {step['action']}, "
              f"retained={step['retained']}, removed={step['removed']}")
    print("final:", {key: result[key] for key in ("retained", "removed", "truncated")})
    print("invariant problems:", invariant_problems(result, 3))


if __name__ == "__main__":
    main()
