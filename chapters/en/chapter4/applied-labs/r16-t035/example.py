"""Worked decision example: is a model ready to share?

The model hub is an external service, so it sits behind a callable interface:
hub(action, repo_id=None). make_offline_hub() is a deterministic local stand-in.
"""
NOT_ESTABLISHED = [
    "real login, tokens or permissions",
    "real repo-name rules or name clashes",
    "upload size, network errors or rate limits",
    "how the real hub behaves today",
]

DECISION_TABLE = [
    {"name": "normal",
     "facts": {"repo_id": "student/my-model", "has_weights": True},
     "expected": "create_repo_and_push",
     "rationale": "A new repo name plus weights on disk means create the repo and push."},
    {"name": "boundary",
     "facts": {"repo_id": "student/existing-model", "has_weights": True},
     "expected": "push_to_existing_repo",
     "rationale": "The repo name already exists, so push to it instead of creating it again."},
    {"name": "missing_information",
     "facts": {"repo_id": "student/other-model"},
     "expected": "need_more_information",
     "rationale": "Without a weights flag the decision cannot be made, so ask first."},
]


def make_offline_hub(user="student", repos=("student/existing-model",)):
    """Deterministic local adapter. It never touches the network."""
    known = set(repos)

    def hub(action, repo_id=None):
        if action == "whoami":
            return user
        if action == "repo_exists":
            return repo_id in known
        raise ValueError(f"unknown hub action: {action}")

    return hub


def decide(facts, hub):
    if not facts.get("repo_id") or "has_weights" not in facts:
        return "need_more_information"
    if hub("whoami") is None:
        return "log_in_first"
    if not facts["has_weights"]:
        return "nothing_to_upload"
    if hub("repo_exists", facts["repo_id"]):
        return "push_to_existing_repo"
    return "create_repo_and_push"


def check_table(decide_fn, hub, table=None):
    """Return a list of mismatches between decide_fn and the decision table."""
    problems = []
    for case in (DECISION_TABLE if table is None else table):
        got = decide_fn(case["facts"], hub)
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
    print("Checker problems:", check_table(decide, make_offline_hub()))
    print("This offline mock does not establish:")
    for item in NOT_ESTABLISHED:
        print("-", item)


if __name__ == "__main__":
    main()
