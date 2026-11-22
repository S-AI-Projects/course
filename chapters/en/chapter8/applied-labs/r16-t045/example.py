#!/usr/bin/env python3
"""
Applied Lab R16-T045: Worked Decision Example for Introduction — Offline Service Adapter.

This module implements a three-scenario worked decision model connecting directly to
Chapter 8, Section 1 ("Introduction" [introduction] - What to do when you hit a problem).

Lesson Context:
In Chapter 8, Section 1, when developers encounter errors in machine learning workflows,
they must decide on the appropriate triage/resolution channel:
1. "LOCAL_DEBUG": For syntax, local runtime exceptions, or deterministic bugs reproducible offline.
2. "COMMUNITY_FORUM": For conceptual, hyperparameter tuning, or model training issues (Hugging Face Forums).
3. "LIBRARY_BUG_REPORT": For reproducible library defects in Hugging Face packages (GitHub Issue).
4. "REQUEST_MISSING_INFO": When essential triage facts (error type, stack trace, or minimal reproduction status) are missing.

Focus - Offline Service Adapter:
When triaging or posting issue reports, interacting with external cloud APIs or GitHub/Forum services
directly in test or build environments introduces network fragility.
Here, external communication is abstracted behind a callable interface (`ExternalServicePort`)
and fulfilled by a deterministic local adapter (`OfflineServiceAdapter`).

Real-Service Behavior Not Established by this Mock:
- Network latency, HTTP timeouts, and connection drops.
- OAuth token authentication, rate limiting, and 429 backoff headers.
- Live forum discourse moderation or GitHub issue triage bot automation.
- Server-side database persistence or markdown rendering engines.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ==============================================================================
# Callable Port & Deterministic Offline Service Adapter
# ==============================================================================
class ExternalServicePort:
    """Callable interface contract for service communication."""

    def submit_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class OfflineServiceAdapter(ExternalServicePort):
    """Deterministic local adapter mocking external issue/forum service dispatch.

    Provides stable, offline execution without network or API dependencies.
    """

    def __init__(self) -> None:
        self.dispatched_payloads: List[Dict[str, Any]] = []

    def submit_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Record and return deterministic mock response."""
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict")
        self.dispatched_payloads.append(payload)
        return {
            "status": "ACCEPTED",
            "receipt_id": f"MOCK-{len(self.dispatched_payloads):04d}",
            "destination": payload.get("destination", "offline_sink"),
        }


# ==============================================================================
# Worked Decision Logic
# ==============================================================================
@dataclass
class TriageDecisionResult:
    """Result of evaluating a triage decision."""

    scenario_name: str
    decision: str
    rationale: str
    input_facts: Dict[str, Any]
    service_response: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "decision": self.decision,
            "rationale": self.rationale,
            "input_facts": dict(self.input_facts),
            "service_response": self.service_response,
        }


def evaluate_triage_decision(
    scenario_name: str,
    facts: Dict[str, Any],
    service_adapter: Optional[ExternalServicePort] = None,
) -> TriageDecisionResult:
    """Evaluate triage channel for a troubleshooting issue with offline adapter dispatch."""
    if not isinstance(facts, dict):
        raise TypeError(f"facts must be a dict, got {type(facts).__name__}")

    # Check for missing required information
    required_keys = {"error_origin", "has_minimal_repro"}
    missing = [k for k in required_keys if k not in facts or facts[k] is None]

    if missing:
        decision = "REQUEST_MISSING_INFO"
        rationale = (
            f"Missing required triage facts {missing}. Per Chapter 8 Introduction, "
            f"identifying the error origin and having a minimal reproducible example "
            f"are mandatory prerequisites before reporting or seeking external help."
        )
        return TriageDecisionResult(
            scenario_name=scenario_name,
            decision=decision,
            rationale=rationale,
            input_facts=facts,
            service_response=None,
        )

    origin = str(facts["error_origin"]).lower()
    has_repro = bool(facts["has_minimal_repro"])
    is_upstream_bug = bool(facts.get("is_upstream_library_bug", False))

    if origin == "local_code" and not is_upstream_bug:
        decision = "LOCAL_DEBUG"
        rationale = (
            "Error originates within user local script / training pipeline and does not stem "
            "from an upstream library defect. Per Chapter 8 Introduction ('The first thing to do "
            "when you get an error' and 'How to debug your training pipeline'), inspect traceback "
            "and debug locally."
        )
    elif is_upstream_bug and has_repro:
        decision = "LIBRARY_BUG_REPORT"
        rationale = (
            "Confirmed library defect with a verified minimal reproduction. Per Chapter 8 Introduction "
            "('How to write a good issue'), file an actionable bug report on the Hugging Face repository issue tracker."
        )
    else:
        decision = "COMMUNITY_FORUM"
        rationale = (
            "Question involves conceptual understanding, hyperparameter behavior, or training dynamics without "
            "an upstream library bug. Per Chapter 8 Introduction ('How to ask for help on the forums'), "
            "post on Discuss Hugging Face forums."
        )

    # Dispatch to service adapter if provided
    service_resp = None
    if service_adapter is not None:
        service_resp = service_adapter.submit_report({
            "scenario": scenario_name,
            "destination": decision,
            "facts": facts,
        })

    return TriageDecisionResult(
        scenario_name=scenario_name,
        decision=decision,
        rationale=rationale,
        input_facts=facts,
        service_response=service_resp,
    )


# ==============================================================================
# Published Decision Table & Checker
# ==============================================================================
PUBLISHED_DECISION_TABLE = [
    {
        "scenario_type": "normal",
        "scenario_name": "local_training_runtime_error",
        "facts": {
            "error_origin": "local_code",
            "has_minimal_repro": True,
            "is_upstream_library_bug": False,
            "error_type": "IndexError",
        },
        "expected_decision": "LOCAL_DEBUG",
        "rationale_keyword": "debug your training pipeline",
    },
    {
        "scenario_type": "boundary",
        "scenario_name": "reproducible_library_defect",
        "facts": {
            "error_origin": "transformers_core",
            "has_minimal_repro": True,
            "is_upstream_library_bug": True,
            "error_type": "AttributeError",
        },
        "expected_decision": "LIBRARY_BUG_REPORT",
        "rationale_keyword": "write a good issue",
    },
    {
        "scenario_type": "missing_information",
        "scenario_name": "vague_crash_without_origin_or_repro",
        "facts": {
            "error_origin": None,
            "has_minimal_repro": None,
            "error_type": "UnknownException",
        },
        "expected_decision": "REQUEST_MISSING_INFO",
        "rationale_keyword": "Missing required triage facts",
    },
]


def check_decision_table(
    table: Optional[List[Dict[str, Any]]] = None,
    service_adapter: Optional[ExternalServicePort] = None,
) -> Tuple[bool, List[Dict[str, Any]]]:
    """Checker for the published decision table.

    Validates:
    - Every scenario evaluates to its exact expected decision.
    - Offline adapter receives payloads deterministically.
    - Rationale keyword aligns with lesson topics.
    - Checker fails if any expected decision in the table is deliberately altered.
    """
    if table is None:
        table = PUBLISHED_DECISION_TABLE
    if service_adapter is None:
        service_adapter = OfflineServiceAdapter()

    all_passed = True
    audit_log = []

    for entry in table:
        name = entry["scenario_name"]
        facts = entry["facts"]
        exp_decision = entry["expected_decision"]
        kw = entry.get("rationale_keyword", "")

        res = evaluate_triage_decision(name, facts, service_adapter=service_adapter)
        decision_matches = (res.decision == exp_decision)
        rationale_valid = (kw.lower() in res.rationale.lower()) if kw else True

        passed = decision_matches and rationale_valid
        if not passed:
            all_passed = False

        audit_log.append({
            "scenario_name": name,
            "scenario_type": entry["scenario_type"],
            "expected_decision": exp_decision,
            "actual_decision": res.decision,
            "decision_matches": decision_matches,
            "rationale_verified": rationale_valid,
            "rationale": res.rationale,
            "service_response": res.service_response,
            "status": "PASS" if passed else "FAIL",
        })

    return all_passed, audit_log


if __name__ == "__main__":
    print("=== Worked Decision Example & Offline Adapter (R16-T045) ===")
    adapter = OfflineServiceAdapter()
    ok, log = check_decision_table(service_adapter=adapter)
    for row in log:
        print(f"\n[{row['status']}] Scenario: {row['scenario_name']} ({row['scenario_type']})")
        print(f"  Decision: Expected={row['expected_decision']} | Actual={row['actual_decision']}")
        print(f"  Rationale: {row['rationale']}")
        print(f"  Adapter Response: {row['service_response']}")
    print(f"\nDecision Table Verification: {'PASSED' if ok else 'FAILED'}")
    print(f"Total dispatched adapter payloads: {len(adapter.dispatched_payloads)}")
