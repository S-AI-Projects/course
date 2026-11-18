"""Worked decision example: is a help request ready to post?

decide_baseline() is the correct first version. decide_refactored() extracts one
named responsibility, unknown_facts(), and keeps the same contract.
"""
import itertools

REQUIRED_FACTS = ("has_traceback", "has_minimal_example", "has_versions")

DECISION_TABLE = [
    {"name": "normal",
     "facts": {"has_traceback": True, "has_minimal_example": True, "has_versions": True},
     "expected": "post_question",
     "rationale": "A traceback, a minimal example and versions give readers what they need."},
    {"name": "boundary",
     "facts": {"has_traceback": True, "has_minimal_example": True, "has_versions": False},
     "expected": "add_versions_then_post",
     "rationale": "Only the versions are missing, so add them and then post."},
    {"name": "missing_information",
     "facts": {"has_traceback": True},
     "expected": "need_more_information",
     "rationale": "Two facts are unknown, so gather them before deciding."},
]


def decide_baseline(facts):
    for key in REQUIRED_FACTS:
        if key not in facts:
            return "need_more_information"
    if not facts["has_traceback"] or not facts["has_minimal_example"]:
        return "debug_more_first"
    if not facts["has_versions"]:
        return "add_versions_then_post"
    return "post_question"


def unknown_facts(facts):
    """The extracted responsibility: which required facts were not supplied."""
    return [key for key in REQUIRED_FACTS if key not in facts]


def decide_refactored(facts):
    if unknown_facts(facts):
        return "need_more_information"
    if not (facts["has_traceback"] and facts["has_minimal_example"]):
        return "debug_more_first"
    if not facts["has_versions"]:
        return "add_versions_then_post"
    return "post_question"


def fact_combinations():
    """Every mix of absent / True / False for the three facts (27 in total)."""
    for values in itertools.product((None, True, False), repeat=len(REQUIRED_FACTS)):
        yield {key: value for key, value in zip(REQUIRED_FACTS, values) if value is not None}


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
    combos = list(fact_combinations())
    same = all(decide_baseline(f) == decide_refactored(f) for f in combos)
    print("Checker problems (baseline):", check_table(decide_baseline))
    print("Checker problems (refactored):", check_table(decide_refactored))
    print(f"Before/after equivalent on {len(combos)} fact combinations: {same}")


if __name__ == "__main__":
    main()
