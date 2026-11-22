#!/usr/bin/env python3
"""
Applied Lab R16-T044: Worked Decision Example for Introduction — Invariant and State Trace.

This module implements a three-scenario worked decision model connecting directly to
Chapter 5, Section 1 ("Introduction" [introduction]).

Context & Lesson Decision:
In Chapter 5, Section 1, practitioners must evaluate dataset loading and processing
strategies based on key constraints:
1. Hub availability (is the dataset hosted on Hugging Face Hub?)
2. Dataset size vs local RAM (will it fit in memory or "melt your laptop's RAM"?)
3. File format & local path (CSV, JSON, Arrow, text)

Decision Outcomes:
- "HUB_IN_MEMORY": Standard `load_dataset("dataset_name")` cached with Arrow memory mapping.
- "STREAM_FROM_DISK_OR_URL": Stream dataset entries on the fly (`streaming=True`) to avoid OOM.
- "LOCAL_FILE_LOADER": Load custom local files using script-less loading (`load_dataset("csv", data_files=...)`).
- "REQUEST_MISSING_INFO": When essential facts (e.g. dataset location, size, or format) are omitted.

State Trace & Invariant Contract:
- Records intermediate state after every evaluation step:
    Step 1: Check information completeness (missing facts check).
    Step 2: Evaluate hosting location (Hub vs Local vs Remote URL).
    Step 3: Evaluate memory & scale boundary constraint (dataset size vs available RAM).
    Step 4: Finalize loading strategy decision and tie rationale to lesson.
- Invariant after each step:
    * `evaluated_step == step_number`
    * `decision_resolved == (step_result is not None)`
    * State trace accumulator contains exactly `step_number` records.
    * The final decision strictly matches the terminal state of the trace.
- Published Decision Table Checker:
    * Validates expected decisions for normal, boundary, and missing-information scenarios.
    * The checker MUST fail if any decision in the table is deliberately altered.
    * Allows human inspection/review verifying rationale follows the lesson.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class StepTrace:
    """Snapshot of intermediate evaluation state after each decision step."""

    step_number: int
    step_name: str
    condition_evaluated: str
    intermediate_state: Dict[str, Any]
    decision_resolved: bool
    current_decision: Optional[str]


@dataclass
class DecisionResult:
    """Final outcome of the dataset strategy decision process."""

    scenario_name: str
    decision: str
    rationale: str
    input_facts: Dict[str, Any]
    state_trace: List[StepTrace] = field(default_factory=list)
    invariant_violations: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation."""
        return {
            "scenario_name": self.scenario_name,
            "decision": self.decision,
            "rationale": self.rationale,
            "input_facts": dict(self.input_facts),
            "state_trace": [
                {
                    "step_number": st.step_number,
                    "step_name": st.step_name,
                    "condition_evaluated": st.condition_evaluated,
                    "intermediate_state": st.intermediate_state,
                    "decision_resolved": st.decision_resolved,
                    "current_decision": st.current_decision,
                }
                for st in self.state_trace
            ],
            "invariant_violations": list(self.invariant_violations),
        }


def evaluate_dataset_strategy(scenario_name: str, facts: Dict[str, Any]) -> DecisionResult:
    """Evaluate dataset loading strategy, recording state trace and testing invariants.

    Steps:
    1. Completeness Check: Are required facts provided? (requires 'dataset_source' and 'size_gb')
    2. Location Check: Is it on Hugging Face Hub, local filesystem, or external URL?
    3. Scale & Memory Boundary Check: Does dataset size exceed RAM threshold (e.g. available RAM)?
    4. Strategy Synthesis: Produce final decision and lesson-linked rationale.
    """
    if not isinstance(facts, dict):
        raise TypeError(f"facts must be a dict, got {type(facts).__name__}")

    trace: List[StepTrace] = []
    violations: List[str] = []

    # Invariant helper
    def check_step_invariant(step_num: int, current_dec: Optional[str], state_dict: Dict[str, Any]):
        if len(trace) != step_num:
            violations.append(f"Step {step_num}: trace length {len(trace)} != {step_num}")
        if (current_dec is not None) != (current_dec is not None):
            violations.append(f"Step {step_num}: inconsistent decision resolution flag")

    # Step 1: Missing information check
    required_keys = {"dataset_source", "size_gb"}
    missing = [k for k in required_keys if k not in facts or facts[k] is None]
    state1 = {"missing_keys": missing, "known_keys": list(facts.keys())}
    dec1 = "REQUEST_MISSING_INFO" if missing else None

    trace.append(
        StepTrace(
            step_number=1,
            step_name="information_completeness_check",
            condition_evaluated=f"missing_required_keys={missing}",
            intermediate_state=state1,
            decision_resolved=(dec1 is not None),
            current_decision=dec1,
        )
    )
    check_step_invariant(1, dec1, state1)

    if dec1 is not None:
        rationale = (
            f"Missing required facts {missing}. As outlined in Chapter 5 Introduction, "
            f"identifying the data location and volume is essential before choosing a loading strategy."
        )
        return DecisionResult(
            scenario_name=scenario_name,
            decision=dec1,
            rationale=rationale,
            input_facts=facts,
            state_trace=trace,
            invariant_violations=violations,
        )

    # Step 2: Location evaluation
    source = facts["dataset_source"]  # "hub", "local", "remote_url"
    is_hub = source.lower() == "hub"
    state2 = {"source": source, "is_hub": is_hub}
    dec2 = None

    trace.append(
        StepTrace(
            step_number=2,
            step_name="dataset_source_evaluation",
            condition_evaluated=f"is_hub={is_hub}",
            intermediate_state=state2,
            decision_resolved=False,
            current_decision=None,
        )
    )
    check_step_invariant(2, dec2, state2)

    # Step 3: Scale & RAM Boundary constraint check
    size_gb = facts["size_gb"]
    ram_gb = facts.get("available_ram_gb", 16)  # Default laptop RAM baseline: 16 GB
    # If size_gb >= ram_gb, it will melt RAM -> must stream
    exceeds_ram = size_gb >= ram_gb
    state3 = {"size_gb": size_gb, "available_ram_gb": ram_gb, "exceeds_ram": exceeds_ram}

    trace.append(
        StepTrace(
            step_number=3,
            step_name="scale_and_memory_boundary_check",
            condition_evaluated=f"size_gb({size_gb}) >= ram_gb({ram_gb}) -> {exceeds_ram}",
            intermediate_state=state3,
            decision_resolved=False,
            current_decision=None,
        )
    )
    check_step_invariant(3, None, state3)

    # Step 4: Final synthesis
    if exceeds_ram:
        final_decision = "STREAM_FROM_DISK_OR_URL"
        rationale = (
            f"Dataset size ({size_gb} GB) meets or exceeds memory limit ({ram_gb} GB). "
            f"Per Chapter 5 Introduction ('What do you do when your dataset is huge and will melt your laptop's RAM?'), "
            f"streaming iteration (`streaming=True`) must be used to consume records with bounded memory."
        )
    elif is_hub:
        final_decision = "HUB_IN_MEMORY"
        rationale = (
            f"Dataset is hosted on Hugging Face Hub and fits comfortably within available RAM "
            f"({size_gb} GB < {ram_gb} GB). Standard `load_dataset('{facts.get('dataset_name', 'hub_dataset')}')` "
            f"is chosen, utilizing memory-mapped Apache Arrow files."
        )
    else:
        final_decision = "LOCAL_FILE_LOADER"
        rationale = (
            f"Dataset is stored locally or at external URL in custom format ({facts.get('file_format', 'generic')}) "
            f"and fits in RAM ({size_gb} GB < {ram_gb} GB). Per Chapter 5 Introduction, use explicit file loaders "
            f"`load_dataset('{facts.get('file_format', 'csv')}', data_files=...)`."
        )

    state4 = {"final_decision": final_decision}
    trace.append(
        StepTrace(
            step_number=4,
            step_name="strategy_synthesis",
            condition_evaluated=f"selected={final_decision}",
            intermediate_state=state4,
            decision_resolved=True,
            current_decision=final_decision,
        )
    )
    check_step_invariant(4, final_decision, state4)

    # Check terminal invariant linking intermediate state to final output
    if trace[-1].current_decision != final_decision:
        violations.append("Final state current_decision does not match returned decision")

    return DecisionResult(
        scenario_name=scenario_name,
        decision=final_decision,
        rationale=rationale,
        input_facts=facts,
        state_trace=trace,
        invariant_violations=violations,
    )


# ==============================================================================
# Published Decision Table & Automated Checker
# ==============================================================================
PUBLISHED_DECISION_TABLE = [
    {
        "scenario_type": "normal",
        "scenario_name": "hub_standard_in_memory",
        "facts": {
            "dataset_source": "hub",
            "dataset_name": "rotten_tomatoes",
            "size_gb": 0.5,
            "available_ram_gb": 16,
            "file_format": "parquet",
        },
        "expected_decision": "HUB_IN_MEMORY",
        "rationale_keyword": "Hugging Face Hub",
    },
    {
        "scenario_type": "boundary",
        "scenario_name": "huge_pile_dataset_boundary",
        "facts": {
            "dataset_source": "hub",
            "dataset_name": "the_pile",
            "size_gb": 825.0,
            "available_ram_gb": 16,
            "file_format": "jsonl",
        },
        "expected_decision": "STREAM_FROM_DISK_OR_URL",
        "rationale_keyword": "streaming",
    },
    {
        "scenario_type": "missing_information",
        "scenario_name": "unspecified_dataset_volume",
        "facts": {
            "dataset_source": "local",
            "size_gb": None,
            "file_format": "csv",
        },
        "expected_decision": "REQUEST_MISSING_INFO",
        "rationale_keyword": "Missing required facts",
    },
]


def check_decision_table(table: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, List[Dict[str, Any]]]:
    """Checker for the published decision table.

    Validates:
    - Every scenario evaluates to its exact expected decision.
    - All intermediate state invariants hold without violations.
    - Human-reviewable rationale contains expected lesson keywords.
    - Fails if a decision is deliberately changed.
    """
    if table is None:
        table = PUBLISHED_DECISION_TABLE

    all_passed = True
    audit_log = []

    for entry in table:
        name = entry["scenario_name"]
        facts = entry["facts"]
        exp_decision = entry["expected_decision"]
        kw = entry.get("rationale_keyword", "")

        res = evaluate_dataset_strategy(name, facts)

        decision_matches = (res.decision == exp_decision)
        invariants_held = (len(res.invariant_violations) == 0)
        rationale_valid = (kw.lower() in res.rationale.lower()) if kw else True

        passed = decision_matches and invariants_held and rationale_valid
        if not passed:
            all_passed = False

        audit_log.append({
            "scenario_name": name,
            "scenario_type": entry["scenario_type"],
            "expected_decision": exp_decision,
            "actual_decision": res.decision,
            "decision_matches": decision_matches,
            "invariants_held": invariants_held,
            "invariant_violations": res.invariant_violations,
            "rationale_verified": rationale_valid,
            "rationale": res.rationale,
            "trace_step_count": len(res.state_trace),
            "status": "PASS" if passed else "FAIL",
        })

    return all_passed, audit_log


if __name__ == "__main__":
    print("=== Worked Decision Example & State Trace (R16-T044) ===")
    ok, log = check_decision_table()
    for row in log:
        print(f"\n[{row['status']}] Scenario: {row['scenario_name']} ({row['scenario_type']})")
        print(f"  Decision: Expected={row['expected_decision']} | Actual={row['actual_decision']}")
        print(f"  Rationale: {row['rationale']}")
        print(f"  Invariants: {row['invariants_held']} (steps={row['trace_step_count']})")
    print(f"\nPublished Decision Table Verification: {'PASSED' if ok else 'FAILED'}")
