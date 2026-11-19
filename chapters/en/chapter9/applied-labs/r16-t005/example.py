"""R16-T005: a Gradio-style callback behind an offline service adapter (mock).

Companion to "Gradio, check!" (chapters/en/chapter9/8.mdx). The chapter shows
how to wrap a function in `gr.Interface(fn, inputs, outputs)` and how to
connect demos to models and Spaces on the Hub. This lab keeps the callback
`fn` *pure* and puts the external dependency (the text service) behind a
plain callable, so it can be tested without Gradio, a network or a model.

Contract for `analyze_text(text)`:
    "red red apple" -> {"word_count": 3, "unique_count": 2}
    ""              -> {"word_count": 0, "unique_count": 0}
    non-string      -> TypeError

The service interface is one callable:  tokenize(text: str) -> list[str]
`local_tokenize` is the deterministic offline adapter used by default and in
all tests (whitespace split, case-sensitive).

MOCK LIMITS: the local adapter does NOT establish anything about a real
hosted service: network latency, timeouts, rate limits, authentication,
outages, or how a real model tokenizes text. It also does not test Gradio
itself (component conversion, queueing, the browser UI).
"""

OUTPUT_SCHEMA = {"word_count": int, "unique_count": int}


def local_tokenize(text):
    """Offline adapter: deterministic whitespace split. No network, no model."""
    return text.split()


def validate_input(text):
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")


def validate_output(result):
    """Check the callback's output against OUTPUT_SCHEMA, independently of any UI."""
    if not isinstance(result, dict) or set(result) != set(OUTPUT_SCHEMA):
        raise ValueError(f"output must have exactly the keys {sorted(OUTPUT_SCHEMA)}")
    for key, expected_type in OUTPUT_SCHEMA.items():
        value = result[key]
        if isinstance(value, bool) or not isinstance(value, expected_type) or value < 0:
            raise ValueError(f"{key} must be a non-negative int, got {value!r}")
    if result["unique_count"] > result["word_count"]:
        raise ValueError("unique_count cannot exceed word_count")


def analyze_text(text, tokenize=local_tokenize):
    """Pure callback: count words and unique words using the given service."""
    validate_input(text)
    tokens = tokenize(text)
    if not isinstance(tokens, list) or not all(isinstance(t, str) for t in tokens):
        raise TypeError("tokenize service must return a list of str")
    result = {"word_count": len(tokens), "unique_count": len(set(tokens))}
    validate_output(result)
    return result


if __name__ == "__main__":
    print("Service: local_tokenize (offline mock - no network, no model, no Gradio)")
    for sample in ["red red apple", ""]:
        print(f"analyze_text({sample!r}) -> {analyze_text(sample)}")
    try:
        analyze_text(42)
    except TypeError as exc:
        print(f"analyze_text(42) -> TypeError: {exc}")
