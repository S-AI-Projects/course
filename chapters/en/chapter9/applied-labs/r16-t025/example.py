#!/usr/bin/env python3
"""
Applied Lab R16-T025: Worked Decision Example for Hugging Face Hub Integrations.

This module provides a deterministic local service adapter and decision checker
for Chapter 9 Section 5 ("Integrations with the Hugging Face Hub") of the
Hugging Face course.

The lesson covers two primary Gradio integration pathways:
1. `Interface.load("huggingface/<model>")`: Delegates execution to the Hugging Face
   Inference API. Ideal for huge models (e.g., GPT-J-6B) where local RAM is insufficient.
2. `Interface.load("spaces/<space>")`: Recreates and loads a complete remote Space
   demo application locally, allowing parameter customization (e.g. overriding inputs to webcam).

Contract:
- Original three-scenario worked example:
  1. Normal scenario: High-RAM model on constrained local host -> LOAD_HUB_MODEL
  2. Boundary scenario: Full Space demo with UI customization -> LOAD_SPACES_APP
  3. Missing-information scenario: Unspecified artifact type -> REJECT_INSUFFICIENT_INFORMATION
- External dependency is abstracted behind a callable interface (`HubIntegrationService`)
  and supplied with a deterministic local adapter (`LocalDeterministicHubAdapter`).
- Explicitly documents real-service behaviors that this mock does NOT establish.
- Automated checker verifies that all decisions match the published decision table.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import sys


class DecisionType(str, Enum):
    """Integration decisions corresponding to Chapter 9 Section 5 pathways."""

    LOAD_HUB_MODEL = "LOAD_HUB_MODEL"
    LOAD_SPACES_APP = "LOAD_SPACES_APP"
    REJECT_INSUFFICIENT_INFORMATION = "REJECT_INSUFFICIENT_INFORMATION"


@dataclass(frozen=True)
class ScenarioRecord:
    """A worked scenario with input facts, expected decision, and rationale."""

    name: str
    facts: Dict[str, Any]
    expected_decision: DecisionType
    expected_prefix: Optional[str]
    rationale: str


# ==============================================================================
# Published Decision Table (Standard Fixture)
# ==============================================================================
PUBLISHED_DECISION_TABLE: List[ScenarioRecord] = [
    ScenarioRecord(
        name="normal",
        facts={
            "artifact_id": "EleutherAI/gpt-j-6B",
            "artifact_type": "model",
            "parameter_count": "6B",
            "local_ram_gb": 4,
            "network_online": True,
        },
        expected_decision=DecisionType.LOAD_HUB_MODEL,
        expected_prefix="huggingface/EleutherAI/gpt-j-6B",
        rationale=(
            "The model has 6 billion parameters and requires substantial RAM (~24GB+ in FP32/FP16), "
            "exceeding the local 4GB host memory. As taught in Chapter 9 Section 5, "
            "gr.Interface.load('huggingface/EleutherAI/gpt-j-6B') delegates computation to the "
            "Hugging Face Inference API in the cloud without loading weights into local memory."
        ),
    ),
    ScenarioRecord(
        name="boundary",
        facts={
            "artifact_id": "abidlabs/remove-bg",
            "artifact_type": "space",
            "parameter_count": None,
            "local_ram_gb": 16,
            "custom_input": "webcam",
            "network_online": True,
        },
        expected_decision=DecisionType.LOAD_SPACES_APP,
        expected_prefix="spaces/abidlabs/remove-bg",
        rationale=(
            "The target is an established, multi-component Space application (background removal pipeline). "
            "Under Chapter 9 Section 5, gr.Interface.load('spaces/abidlabs/remove-bg') loads the remote Space "
            "and recreates it locally while allowing parameter overrides (e.g. inputs='webcam')."
        ),
    ),
    ScenarioRecord(
        name="missing_information",
        facts={
            "artifact_id": "custom-org/unspecified-pkg",
            "artifact_type": None,
            "parameter_count": None,
            "local_ram_gb": 8,
            "network_online": True,
        },
        expected_decision=DecisionType.REJECT_INSUFFICIENT_INFORMATION,
        expected_prefix=None,
        rationale=(
            "The artifact type (model vs. space) is unspecified. Interface.load() requires an explicit routing "
            "prefix ('huggingface/' vs 'spaces/'). Without knowing whether the target is a model checkpoint or a Space, "
            "the integration cannot be determined and must be rejected before remote dispatch."
        ),
    ),
]


# ==============================================================================
# Callable Service Interface & Deterministic Local Adapter
# ==============================================================================
class HubIntegrationService(ABC):
    """Abstract callable interface for Hugging Face Hub integration decisions."""

    @abstractmethod
    def evaluate(self, facts: Dict[str, Any]) -> Tuple[DecisionType, Optional[str], str]:
        """
        Evaluate input facts and determine integration decision, target prefix, and rationale.
        """


class LocalDeterministicHubAdapter(HubIntegrationService):
    """
    Deterministic offline adapter implementing Hub integration decision logic
    without requiring network connectivity, GPUs, or API tokens.

    Real-Service Behaviors This Mock Does NOT Establish:
    1. Real network latency, packet loss, and HTTP connection timeouts.
    2. Hugging Face Inference API rate limits (HTTP 429), user token quotas, and paid endpoints.
    3. Hub authentication verification via real Hugging Face user access tokens (HF_TOKEN)
       for private repositories and gated models.
    4. Remote model cold-start delays (e.g. 'Model is currently loading' 503 responses).
    5. Live remote Space schema verification and interactive component rendering.
    """

    UNESTABLISHED_BEHAVIORS = [
        "Network latency, connection timeouts, and DNS resolution failures.",
        "Hugging Face Inference API rate limits (HTTP 429) and compute quotas.",
        "Authentication against private repositories using user access tokens (HF_TOKEN).",
        "Cold-start model loading delays on the remote Inference API.",
        "Real-time remote Space schema verification and component compatibility.",
    ]

    def evaluate(self, facts: Dict[str, Any]) -> Tuple[DecisionType, Optional[str], str]:
        artifact_id = facts.get("artifact_id")
        artifact_type = facts.get("artifact_type")

        # Missing-information scenario check
        if not artifact_type or not artifact_id:
            return (
                DecisionType.REJECT_INSUFFICIENT_INFORMATION,
                None,
                (
                    "Missing essential artifact metadata (artifact_id or artifact_type is None). "
                    "Cannot determine whether to route to 'huggingface/' or 'spaces/'."
                ),
            )

        if artifact_type == "model":
            return (
                DecisionType.LOAD_HUB_MODEL,
                f"huggingface/{artifact_id}",
                (
                    f"Selected Hugging Face Inference API for model '{artifact_id}' to avoid "
                    f"local memory overhead, routing through gr.Interface.load('huggingface/{artifact_id}')."
                ),
            )

        if artifact_type == "space":
            return (
                DecisionType.LOAD_SPACES_APP,
                f"spaces/{artifact_id}",
                (
                    f"Selected Hugging Face Spaces integration for Space '{artifact_id}', "
                    f"routing through gr.Interface.load('spaces/{artifact_id}')."
                ),
            )

        return (
            DecisionType.REJECT_INSUFFICIENT_INFORMATION,
            None,
            f"Unrecognized artifact type '{artifact_type}'.",
        )


def check_decision_table(
    service: HubIntegrationService,
    table: List[ScenarioRecord] = PUBLISHED_DECISION_TABLE,
) -> Dict[str, Any]:
    """
    Verify that the service evaluation matches the published decision table.

    Raises:
        AssertionError: If any actual decision differs from the expected decision.
    """
    results = []
    for scenario in table:
        actual_decision, actual_prefix, _ = service.evaluate(scenario.facts)

        if actual_decision != scenario.expected_decision:
            raise AssertionError(
                f"Checker failure in scenario '{scenario.name}': "
                f"expected decision {scenario.expected_decision}, got {actual_decision}"
            )

        if actual_prefix != scenario.expected_prefix:
            raise AssertionError(
                f"Checker failure in scenario '{scenario.name}': "
                f"expected prefix '{scenario.expected_prefix}', got '{actual_prefix}'"
            )

        results.append({
            "scenario": scenario.name,
            "decision": actual_decision.value,
            "prefix": actual_prefix,
            "status": "PASS",
        })

    return {"status": "ALL_PASSED", "results": results}


def main() -> int:
    """Run demonstration across all three scenarios and execute checker."""
    print("=== Hugging Face Hub Integrations: Worked Decision Example ===")
    adapter = LocalDeterministicHubAdapter()

    print("\n--- Published Scenarios & Decision Table ---")
    for s in PUBLISHED_DECISION_TABLE:
        actual_dec, actual_prefix, actual_rat = adapter.evaluate(s.facts)
        print(f"\nScenario: [{s.name.upper()}]")
        print(f"  Facts:    {s.facts}")
        print(f"  Decision: {actual_dec.value}")
        print(f"  Prefix:   {actual_prefix}")
        print(f"  Rationale: {s.rationale}")

    print("\n--- Running Decision Table Checker ---")
    report = check_decision_table(adapter)
    print(f"Checker Status: {report['status']}")
    for r in report["results"]:
        print(f"  [{r['status']}] {r['scenario']} -> {r['decision']} ({r['prefix']})")

    print("\n--- Unestablished Real-Service Behaviors (Explicit Boundaries) ---")
    for i, b in enumerate(LocalDeterministicHubAdapter.UNESTABLISHED_BEHAVIORS, 1):
        print(f"  {i}. {b}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
