"""Worked decision example: which pipeline step should you inspect first?

Rule sets of three sizes are compared on a small hand-made fixture. The numbers
describe this fixture only. They say nothing about real-world model accuracy.
"""
STAGE_FOR_SYMPTOM = [
    ("tokens_look_wrong", "tokenizer"),
    ("output_shape_error", "model"),
    ("raw_logits_shown", "postprocessing"),
]

DECISION_TABLE = [
    {"name": "normal", "facts": {"symptom": "tokens_look_wrong"},
     "expected": "tokenizer",
     "rationale": "The symptom matches the tokenizer step, so look there first."},
    {"name": "boundary", "facts": {"symptom": "gpu_fan_noisy"},
     "expected": "unknown_symptom",
     "rationale": "A symptom outside the three steps is reported as unknown, not guessed."},
    {"name": "missing_information", "facts": {},
     "expected": "need_more_information",
     "rationale": "No symptom was given, so ask for it before choosing a step."},
]

FIXTURE = [
    ({"symptom": "tokens_look_wrong"}, "tokenizer"),
    ({"symptom": "output_shape_error"}, "model"),
    ({"symptom": "raw_logits_shown"}, "postprocessing"),
    ({}, "need_more_information"),
    ({"symptom": "gpu_fan_noisy"}, "unknown_symptom"),
]


def lookup(symptom, rules):
    """Return (decision, comparisons made)."""
    comparisons = 0
    for known, stage in rules:
        comparisons += 1
        if known == symptom:
            return stage, comparisons
    return "unknown_symptom", comparisons


def decide(facts, rules=STAGE_FOR_SYMPTOM):
    symptom = facts.get("symptom")
    if symptom is None:
        return "need_more_information"
    return lookup(symptom, rules)[0]


def evaluate(rules):
    """Exact-match correctness on the fixture, plus rule comparisons as a cost."""
    correct = 0
    comparisons = 0
    for facts, expected in FIXTURE:
        if decide(facts, rules) == expected:
            correct += 1
        if facts.get("symptom") is not None:
            comparisons += lookup(facts["symptom"], rules)[1]
    return {"rules": len(rules), "correct": correct, "cases": len(FIXTURE),
            "comparisons": comparisons}


def check_table(decide_fn, table=None):
    problems = []
    for case in (DECISION_TABLE if table is None else table):
        got = decide_fn(case["facts"])
        if got != case["expected"]:
            problems.append(f"{case['name']}: expected {case['expected']}, got {got}")
    return problems


def markdown_table():
    rows = ["| Scenario | Decision | Rationale |", "| --- | --- | --- |"]
    for case in DECISION_TABLE:
        rows.append(f"| {case['name']} | {case['expected']} | {case['rationale']} |")
    return "\n".join(rows)


def main():
    print(markdown_table())
    print()
    print("Checker problems:", check_table(decide))
    print("Three rule-set sizes on the same fixture:")
    for name, size in (("small", 1), ("medium", 2), ("full", 3)):
        r = evaluate(STAGE_FOR_SYMPTOM[:size])
        print(f"  {name}: rules={r['rules']} correct={r['correct']}/{r['cases']} "
              f"comparisons={r['comparisons']}")
    print("Trade-off seen here: more rules fit more fixture cases but cost more comparisons.")
    print("Fixture results only, not real-world model accuracy.")


if __name__ == "__main__":
    main()
