"""Token-budget preflight that survives bad input and recovers on the next one.

Whitespace splitting is a teaching approximation, not the model's real tokenizer.
Documented errors: a missing prompt (None) and a negative budget.
"""
TOKENIZER_NOTE = "Whitespace splitting is a teaching approximation, not the model's real tokenizer."

FIXTURE = [
    ("one two three four", 3),
    ("hello world", -1),
    (None, 3),
    ("a b", 3),
    ("", 3),
]


def preflight(prompt, budget):
    if prompt is None:
        raise ValueError("prompt is missing (got None)")
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise TypeError("budget must be an int")
    if budget < 0:
        raise ValueError(f"budget must be 0 or more, got {budget}")
    tokens = prompt.split()
    retained = tokens[:budget]
    return {"retained": retained, "removed": len(tokens) - len(retained)}


def run_batch(requests):
    """Run (prompt, budget) pairs. A bad request is reported and the next one still runs."""
    results = []
    for index, (prompt, budget) in enumerate(requests, start=1):
        try:
            results.append({"request": index, "status": "ok", **preflight(prompt, budget)})
        except (ValueError, TypeError) as err:
            results.append({"request": index, "status": "error", "error": str(err)})
    return results


def main():
    print(TOKENIZER_NOTE)
    results = run_batch(FIXTURE)
    for item in results:
        print(item)
    recovered = results[3]["status"] == "ok" and results[2]["status"] == "error"
    print("recovered on the next valid input:", recovered)


if __name__ == "__main__":
    main()
