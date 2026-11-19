"""R16-T004: security-scenario rubric checker with a state trace (simulation).

Companion to "End-of-chapter Certificate" (chapters/en/chapter3/7.mdx).
That page ends the chapter with an automatically graded quiz. This lab looks
at what an automatic grader can and cannot check, using three *fictional*
security scenarios drawn from chapter 3's workflow (fine-tune, then share on
the Hub).

Each scenario has four rubric fields:
    asset          - what needs protecting
    threat         - what could go wrong (with a `threat_type` tag)
    control        - what reduces the risk (with an `addresses` tag)
    residual_risk  - what risk remains after the control

The checker runs three steps and records its state after each one:
    1. required_fields  - which required keys are missing
    2. non_empty_text   - which present fields are blank
    3. control_matches  - does the control's `addresses` tag equal the threat's `threat_type`?

Verdicts:
    "fail"   - step 1 or step 2 found a problem (later steps are skipped)
    "review" - the structure is fine but the control does not target the named threat
    "pass"   - all three steps are clean

LIMIT: the checker only verifies this *structural* rubric. Whether an
explanation is correct, specific or sensible is a job for a human reviewer.
A scenario full of confident nonsense passes if it is well formed.
"""

REQUIRED_FIELDS = ("asset", "threat", "threat_type", "control", "addresses", "residual_risk")
TEXT_FIELDS = ("asset", "threat", "control", "residual_risk")

# Three fictional scenarios (no real incident, person or organisation).
SCENARIOS = [
    {
        "id": "S1-token",
        "asset": "Hugging Face access token with write permission, used to push the fine-tuned model",
        "threat": "The token is pasted into a notebook cell and the notebook is shared publicly",
        "threat_type": "credential-leak",
        "control": "Log in with `huggingface-cli login` so the token never appears in code; "
                   "revoke and replace the token if it is ever exposed",
        "addresses": "credential-leak",
        "residual_risk": "Old notebook outputs or shell history may still contain the token until they are cleaned",
    },
    {
        "id": "S2-dataset",
        "asset": "A private set of customer reviews used for fine-tuning",
        "threat": "The raw data folder is uploaded alongside the model when pushing to the Hub",
        "threat_type": "data-exposure",
        "control": "Check the list of files before pushing and keep the data folder out of the model repository",
        "addresses": "data-exposure",
        "residual_risk": "The model itself may still reproduce rare training examples",
    },
    {
        "id": "S3-quiz-login",
        "asset": "The learner's Hugging Face account used to take the certificate quiz",
        "threat": "A message links to a look-alike sign-in page that asks for the password",
        "threat_type": "phishing",
        "control": "Sign in only on huggingface.co and turn on two-factor authentication",
        "addresses": "phishing",
        "residual_risk": "A convincing look-alike domain can still fool a hurried user",
    },
]


def _without(scenario, field):
    return {k: v for k, v in scenario.items() if k != field}


# Two broken "student answers" derived from the scenarios above.
MISSING_ASSET = {**_without(SCENARIOS[0], "asset"), "id": "S1-no-asset"}
MISMATCHED_CONTROL = {
    **SCENARIOS[1],
    "id": "S2-wrong-control",
    "control": "Turn on two-factor authentication for the Hub account",
    "addresses": "phishing",  # does not target the named data-exposure threat
}


def check_scenario(scenario):
    """Grade one scenario. Returns {"id", "verdict", "trace"}.

    trace is a list of (step_name, state) recorded after each step.
    A step that is not run is recorded with state "skipped".
    """
    trace = []

    missing = [f for f in REQUIRED_FIELDS if f not in scenario]
    trace.append(("required_fields", {"missing": missing}))
    if missing:
        trace += [("non_empty_text", "skipped"), ("control_matches", "skipped")]
        return {"id": scenario.get("id"), "verdict": "fail", "trace": trace}

    blank = [f for f in TEXT_FIELDS if not str(scenario[f]).strip()]
    trace.append(("non_empty_text", {"blank": blank}))
    if blank:
        trace.append(("control_matches", "skipped"))
        return {"id": scenario.get("id"), "verdict": "fail", "trace": trace}

    matches = scenario["addresses"] == scenario["threat_type"]
    trace.append(("control_matches", {
        "threat_type": scenario["threat_type"],
        "addresses": scenario["addresses"],
        "matches": matches,
    }))
    return {"id": scenario.get("id"), "verdict": "pass" if matches else "review", "trace": trace}


def format_result(result):
    lines = [f"{result['id']}: {result['verdict'].upper()}"]
    for step, state in result["trace"]:
        lines.append(f"  after {step:16} {state}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("Structural rubric only - a human reviewer still judges the explanations.\n")
    for scenario in SCENARIOS + [MISSING_ASSET, MISMATCHED_CONTROL]:
        print(format_result(check_scenario(scenario)))
