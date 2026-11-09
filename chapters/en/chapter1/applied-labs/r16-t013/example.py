"""Applied Lab R16-T013: Security Scenario Rubric Checker and Comparison.

This module evaluates fictional security scenarios tied to Chapter 1 ("Ungraded quiz",
covering model hubs, pipeline inference, and dataset biases) encoded with four fields:
- asset
- threat
- control
- residual_risk

It compares two independent evaluation approaches on identical inputs:
1. Direct implementation: Rule-based rubric checking structural completeness
   and control relevance.
2. Independent reference table: Explicit benchmark table of expected verdicts.
"""

from typing import Any, Dict, List, Tuple

REQUIRED_FIELDS = ["asset", "threat", "control", "residual_risk"]

CONTROL_KEYWORDS = {
    "tampering": ["hash", "signature", "verification", "checksum", "integrity"],
    "bias": ["auditing", "filtering", "sampling", "debiasing", "validation"],
    "ddos": ["rate limiting", "firewall", "load balancer", "traffic", "mitigation"],
}


def check_scenario_completeness(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Check structural completeness of a security scenario.

    Verifies that asset, threat, control, and residual_risk fields are present
    and non-empty.
    """
    missing_fields = []
    for field in REQUIRED_FIELDS:
        val = scenario.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            missing_fields.append(field)

    if missing_fields:
        return {"status": "FAIL", "missing_fields": missing_fields}
    return {"status": "PASS", "missing_fields": []}


def check_control_relevance(scenario: Dict[str, Any]) -> str:
    """Check whether proposed control contains keywords relevant to the named threat.

    Returns:
        'MATCH': If control aligns with known threat mitigation patterns.
        'REVIEW': If control appears unrelated and requires human evaluation.
    """
    threat = str(scenario.get("threat") or "").lower()
    control = str(scenario.get("control") or "").lower()

    for threat_key, keywords in CONTROL_KEYWORDS.items():
        if threat_key in threat:
            if any(kw in control for kw in keywords):
                return "MATCH"
            return "REVIEW"

    # Default to REVIEW for unmapped or ambiguous threats requiring human assessment
    return "REVIEW"


def evaluate_direct(scenario: Dict[str, Any]) -> Tuple[str, str]:
    """Direct approach: compute completeness status and control relevance verdict."""
    completeness = check_scenario_completeness(scenario)["status"]
    control_verdict = check_control_relevance(scenario)
    return completeness, control_verdict


# Fictional scenarios tied to Chapter 1 concepts (Hub checkpoints, bias, inference pipelines)
SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "model_hub_integrity",
        "name": "Scenario 1: Model Hub Checkpoint Integrity",
        "lesson_topic": "Question 1 (Model Hub checkpoints and pretrained weights)",
        "asset": "Pretrained RoBERTa model weights repository on Hugging Face Hub",
        "threat": "Unauthorized weight tampering or model supply-chain poisoning",
        "control": "Cryptographic hash verification and commit signature enforcement on model weights",
        "residual_risk": "A compromised maintainer token could sign poisoned weights before hash publication.",
    },
    {
        "id": "dataset_demographic_bias",
        "name": "Scenario 2: Pretraining Dataset Bias (Missing Asset)",
        "lesson_topic": "Question 11 (Sources of bias in pretrained training datasets)",
        "asset": "",  # Intentionally missing asset field
        "threat": "Demographic bias in training dataset skewing classification outcomes",
        "control": "Dataset demographic auditing and representation filtering",
        "residual_risk": "Latent proxy variables in uncurated web text may still induce subtle biases.",
    },
    {
        "id": "inference_pipeline_ddos",
        "name": "Scenario 3: Pipeline Inference Service (Unrelated Control)",
        "lesson_topic": "Questions 2 & 4 (Pipeline inference serving and error handling)",
        "asset": "Production NER pipeline inference API endpoint",
        "threat": "DDoS volumetric request flooding saturating transformer inference queue",
        "control": "Enforcing code comment indentation and docstring formatting standards",
        "residual_risk": "Inference server remains completely vulnerable to traffic saturation.",
    },
]

# Independent reference table of expected decisions
REFERENCE_RESULTS: Dict[str, Tuple[str, str]] = {
    "model_hub_integrity": ("PASS", "MATCH"),
    "dataset_demographic_bias": ("FAIL", "MATCH"),
    "inference_pipeline_ddos": ("PASS", "REVIEW"),
}


def evaluate_reference(scenario: Dict[str, Any]) -> Tuple[str, str]:
    """Reference approach: benchmark lookup from the independent decision table."""
    scenario_id = scenario.get("id")
    if scenario_id in REFERENCE_RESULTS:
        return REFERENCE_RESULTS[scenario_id]
    raise KeyError(f"Scenario ID '{scenario_id}' not found in reference decision table.")


def compare_both_approaches(scenarios: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
    """Compare direct rule evaluation against independent reference decisions."""
    all_agreed = True
    comparison_records = []

    for item in scenarios:
        direct_verdict = evaluate_direct(item)
        ref_verdict = evaluate_reference(item)
        agreed = direct_verdict == ref_verdict
        if not agreed:
            all_agreed = False

        comparison_records.append({
            "id": item["id"],
            "name": item["name"],
            "direct": direct_verdict,
            "reference": ref_verdict,
            "agreed": agreed,
        })

    return all_agreed, comparison_records


if __name__ == "__main__":
    print("Running Security Scenario Rubric Evaluation & Approach Comparison:")
    print("=" * 70)
    success, audit = compare_both_approaches(SCENARIOS)
    for rec in audit:
        status = "AGREED" if rec["agreed"] else "DISAGREED"
        print(f"[{status}] {rec['name']}")
        print(f"         Direct:    Completeness={rec['direct'][0]}, Control={rec['direct'][1]}")
        print(f"         Reference: Completeness={rec['reference'][0]}, Control={rec['reference'][1]}\n")

    print("=" * 70)
    print(f"Final Comparison Status: {'ALL APPROACHES AGREE' if success else 'DIVERGENCE DETECTED'}")
