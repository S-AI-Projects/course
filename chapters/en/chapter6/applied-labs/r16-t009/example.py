"""R16-T009: reuse or train a new tokenizer? A worked decision and a small experiment.

Companion to "Introduction" (chapters/en/chapter6/1.mdx). The lesson says:
  * when fine-tuning, we use the same tokenizer the model was pretrained with;
  * when training from scratch on a different domain or language, a
    pretrained tokenizer is "typically suboptimal". For example, an English
    tokenizer does poorly on Japanese, where spaces are used very differently.

SIMULATION: the "existing tokenizer" is a toy word-level tokenizer, a
whitespace split checked against a small vocabulary. Words not in the
vocabulary count as unknown. Real tokenizers are subword-based and almost
never produce this many unknowns, so the numbers here only illustrate the
idea. They say nothing about any real tokenizer or model.

Metric: unknown_rate = unknown tokens / all tokens, kept as an exact
`Fraction`, so a rate of exactly 1/4 is compared with the threshold without
floating-point error.

Decision rules:
  1. training_mode missing, or "from-scratch" with no corpus sample -> "need-more-info"
  2. "fine-tune"                                                  -> "reuse"
  3. "from-scratch": unknown_rate > MAX_UNKNOWN_RATE (1/4)         -> "train-new", else "reuse"
"""

from fractions import Fraction

MAX_UNKNOWN_RATE = Fraction(1, 4)

# The toy existing tokenizer's vocabulary, most common words first.
ENGLISH_WORDS = [
    "the", "a", "new", "of", "we", "on", "text", "corpus",
    "tokenizer", "train", "model", "is", "to", "and", "for", "data",
]
EXISTING_VOCAB = set(ENGLISH_WORDS)


def unknown_rate(corpus_sample, vocab):
    """Exact fraction of whitespace tokens that are not in vocab."""
    tokens = corpus_sample.split()
    if not tokens:
        raise ValueError("corpus_sample has no tokens")
    unknown = sum(1 for t in tokens if t not in vocab)
    return Fraction(unknown, len(tokens))


def decide(facts, vocab=EXISTING_VOCAB):
    mode = facts.get("training_mode")
    sample = facts.get("corpus_sample")
    if mode not in ("fine-tune", "from-scratch"):
        return "need-more-info"
    if mode == "fine-tune":
        return "reuse"
    if not sample or not sample.split():
        return "need-more-info"
    return "train-new" if unknown_rate(sample, vocab) > MAX_UNKNOWN_RATE else "reuse"


SCENARIOS = {
    "normal": {
        "facts": {"training_mode": "from-scratch", "corpus_sample": "私は猫が好きです 今日は晴れです"},
        "decision": "train-new",
        "rationale": "The lesson's own example: Japanese barely uses spaces, so every whitespace "
                     "token is unknown to the English vocabulary (rate 1). Training from scratch "
                     "on this corpus calls for a new tokenizer.",
    },
    "boundary": {
        "facts": {"training_mode": "from-scratch", "corpus_sample": "the new text zebra"},
        "decision": "reuse",
        "rationale": "Exactly 1 of 4 tokens is unknown, a rate of exactly 1/4. The rule trains a "
                     "new tokenizer only when the rate is *more than* 1/4, so this case reuses the "
                     "existing one. One more unknown word would flip it.",
    },
    "missing-information": {
        "facts": {"training_mode": "from-scratch", "corpus_sample": None},
        "decision": "need-more-info",
        "rationale": "Without a sample of the new corpus we cannot measure how well the existing "
                     "tokenizer fits it, so we cannot decide.",
    },
}

DECISION_TABLE = {sid: s["decision"] for sid, s in SCENARIOS.items()}


def check_table(decide_fn=decide, table=DECISION_TABLE, scenarios=SCENARIOS):
    """Return a list of (scenario_id, expected, actual) for every mismatch."""
    return [
        (sid, expected, decide_fn(scenarios[sid]["facts"]))
        for sid, expected in table.items()
        if decide_fn(scenarios[sid]["facts"]) != expected
    ]


# ---- Evaluation experiment: three controlled configurations ----------------
EXPERIMENT_CORPUS = "we train a new tokenizer on the text of a new corpus"  # 12 tokens
VOCAB_SIZES = (4, 8, 16)


def run_experiment(corpus=EXPERIMENT_CORPUS, sizes=VOCAB_SIZES):
    """Same corpus, three vocabulary sizes (the first N words of ENGLISH_WORDS)."""
    rows = []
    for size in sizes:
        vocab = set(ENGLISH_WORDS[:size])
        rate = unknown_rate(corpus, vocab)
        rows.append({
            "vocab_size": size,
            "unknown_rate": rate,
            "decision": "train-new" if rate > MAX_UNKNOWN_RATE else "reuse",
        })
    return rows


if __name__ == "__main__":
    print("Toy word-level tokenizer (simulation) - not a real tokenizer.\n")
    for sid, scenario in SCENARIOS.items():
        print(f"[{sid}] {scenario['facts']} -> {decide(scenario['facts'])}")
    print(f"check_table -> {check_table() or 'all decisions match'}\n")
    print(f"Experiment: {len(EXPERIMENT_CORPUS.split())}-token corpus, threshold {MAX_UNKNOWN_RATE}")
    print("vocab_size  unknown_rate  decision")
    for row in run_experiment():
        rate = row["unknown_rate"]
        print(f"{row['vocab_size']:>10}  {str(rate):>5} ({float(rate):.2f})  {row['decision']}")
