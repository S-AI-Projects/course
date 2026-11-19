"""R16-T006: worked decision example for "Using pretrained models" (simulation).

Companion to chapters/en/chapter4/2.mdx. The lesson makes two points about
picking a checkpoint from the Hub:
  * the checkpoint must suit the task: `camembert-base` is fine in a
    `fill-mask` pipeline, but in `text-classification` "the results would not
    make any sense because the head ... is not suitable";
  * check the model card for how the model was trained, its limits and biases.

Each scenario is a set of *input facts*, a *decision* and a *rationale*:
    facts:     checkpoint, head_task, requested_task, model_language,
               text_language, model_card
    decisions: "use" | "do-not-use" | "need-more-info"

Refactor (the focus of this task):
  * `decide_baseline` is the first, correct, all-in-one version.
  * `decide` gives the same answers, but the responsibility "find missing
    information" is moved into its own named function, `missing_facts`.
  The tests check that before and after give the same decisions on the
  fixture and on every combination of fact values.

Scope: the facts are typed in by hand. Nothing is downloaded and no
checkpoint is loaded. The rules are a teaching summary of the lesson, not a
complete checklist for choosing a model.
"""

REQUIRED_FACTS = (
    "checkpoint", "head_task", "requested_task",
    "model_language", "text_language", "model_card",
)

SCENARIOS = {
    "normal": {
        "facts": {
            "checkpoint": "camembert-base", "head_task": "fill-mask",
            "requested_task": "fill-mask", "model_language": "fr",
            "text_language": "fr", "model_card": "documented",
        },
        "decision": "use",
        "rationale": "The head matches the task (the lesson's own example), the text is French "
                     "like the model, and the model card can be checked for training data and limits.",
    },
    "boundary": {
        "facts": {
            "checkpoint": "camembert-base", "head_task": "fill-mask",
            "requested_task": "text-classification", "model_language": "fr",
            "text_language": "fr", "model_card": "documented",
        },
        "decision": "do-not-use",
        "rationale": "Same checkpoint and same language, only the task changes. The lesson says "
                     "results 'would not make any sense' because the fill-mask head does not fit "
                     "text classification. One changed fact flips the decision.",
    },
    "missing-information": {
        "facts": {
            "checkpoint": "camembert-base", "head_task": "fill-mask",
            "requested_task": "fill-mask", "model_language": "fr",
            "text_language": "fr", "model_card": None,
        },
        "decision": "need-more-info",
        "rationale": "Without a model card we cannot check how it was trained, on which data, its "
                     "limits or biases, which the lesson asks us to check before using a model.",
    },
}

# The published decision table: scenario id -> expected decision.
DECISION_TABLE = {sid: s["decision"] for sid, s in SCENARIOS.items()}


# ---- Before: correct baseline, everything in one function -------------------
def decide_baseline(facts):
    for name in REQUIRED_FACTS:
        if facts.get(name) in (None, ""):
            return "need-more-info"
    if facts["head_task"] != facts["requested_task"]:
        return "do-not-use"
    if facts["model_language"] != facts["text_language"]:
        return "do-not-use"
    return "use"


# ---- After: one named responsibility extracted ------------------------------
def missing_facts(facts):
    """Responsibility: list the facts we would need before deciding."""
    return [name for name in REQUIRED_FACTS if facts.get(name) in (None, "")]


def decide(facts):
    """Same contract as decide_baseline."""
    if missing_facts(facts):
        return "need-more-info"
    if facts["head_task"] != facts["requested_task"]:
        return "do-not-use"
    if facts["model_language"] != facts["text_language"]:
        return "do-not-use"
    return "use"


# ---- Checker for the published table ----------------------------------------
def check_table(decide_fn, table=DECISION_TABLE, scenarios=SCENARIOS):
    """Return a list of (scenario_id, expected, actual) for every mismatch."""
    mismatches = []
    for sid, expected in table.items():
        actual = decide_fn(scenarios[sid]["facts"])
        if actual != expected:
            mismatches.append((sid, expected, actual))
    return mismatches


if __name__ == "__main__":
    print("Simulated facts only - no checkpoint is downloaded or loaded.\n")
    for sid, scenario in SCENARIOS.items():
        facts = scenario["facts"]
        print(f"[{sid}] {facts['checkpoint']}: head={facts['head_task']} "
              f"requested={facts['requested_task']} card={facts['model_card']}")
        print(f"   decision: {decide(facts)}   missing: {missing_facts(facts)}")
    print()
    print(f"check_table(decide)          -> {check_table(decide) or 'all decisions match'}")
    print(f"check_table(decide_baseline) -> {check_table(decide_baseline) or 'all decisions match'}")
