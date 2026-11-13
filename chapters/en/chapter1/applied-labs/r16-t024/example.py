#!/usr/bin/env python3
"""
Applied Lab R16-T024: Capability Negotiation Invariant and State Trace.

This module demonstrates capability discovery, intersection negotiation,
and feature gating as used in modern Transformer and LLM application architectures
(e.g., tool-use protocols, client-server model interfaces).

Contract:
- Client announces: {"tools", "resources"}
- Server announces: {"tools", "prompts"}
- Negotiation yields: {"tools"} (intersection of client and server capabilities)
- Invoking a negotiated capability ('tools') succeeds and dispatches.
- Invoking an unnegotiated capability ('resources') is strictly rejected BEFORE dispatch.
- Focus: Records intermediate state after each step and validates the invariant
  linking intermediate state to the final dispatch output.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Set
import sys


class CapabilityNotNegotiatedError(Exception):
    """Raised when an unnegotiated capability is invoked."""


@dataclass
class StepState:
    """Snapshot of system state at a specific step."""

    step: int
    phase: str
    client_caps: Set[str]
    server_caps: Set[str]
    negotiated_caps: Optional[Set[str]]
    last_action: str
    last_status: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert state snapshot to serializable dictionary."""
        d = asdict(self)
        d["client_caps"] = sorted(self.client_caps)
        d["server_caps"] = sorted(self.server_caps)
        d["negotiated_caps"] = (
            sorted(self.negotiated_caps) if self.negotiated_caps is not None else None
        )
        return d


class CapabilityNegotiator:
    """
    Manages client-server capability registration, intersection negotiation,
    and gated invocation dispatch with state tracing.
    """

    def __init__(self) -> None:
        self.client_caps: Set[str] = set()
        self.server_caps: Set[str] = set()
        self.negotiated_caps: Optional[Set[str]] = None
        self.dispatch_log: List[str] = []
        self.trace: List[StepState] = []
        self._record_step("INITIALIZED", "init", "READY")

    def _record_step(self, phase: str, action: str, status: str) -> None:
        """Record an immutable snapshot of the intermediate state."""
        state = StepState(
            step=len(self.trace),
            phase=phase,
            client_caps=set(self.client_caps),
            server_caps=set(self.server_caps),
            negotiated_caps=(
                set(self.negotiated_caps) if self.negotiated_caps is not None else None
            ),
            last_action=action,
            last_status=status,
        )
        self.trace.append(state)

    def register_client(self, capabilities: Set[str]) -> "CapabilityNegotiator":
        """Register capabilities announced by the client."""
        self.client_caps = set(capabilities)
        self.negotiated_caps = None  # Reset negotiation on re-registration
        self._record_step("CLIENT_REGISTERED", f"register_client({sorted(capabilities)})", "OK")
        return self

    def register_server(self, capabilities: Set[str]) -> "CapabilityNegotiator":
        """Register capabilities announced by the server."""
        self.server_caps = set(capabilities)
        self.negotiated_caps = None  # Reset negotiation on re-registration
        self._record_step("SERVER_REGISTERED", f"register_server({sorted(capabilities)})", "OK")
        return self

    def negotiate(self) -> Set[str]:
        """
        Negotiate capabilities by taking the intersection of client and server capabilities.
        """
        self.negotiated_caps = self.client_caps.intersection(self.server_caps)
        self._record_step(
            "NEGOTIATED",
            "negotiate()",
            f"SETTLED({sorted(self.negotiated_caps)})",
        )
        return set(self.negotiated_caps)

    def dispatch(self, capability: str, payload: Any = None) -> Dict[str, Any]:
        """
        Dispatch a capability invocation.

        Strictly enforces that capability MUST be in the negotiated set.
        Unnegotiated capabilities are rejected BEFORE dispatch.

        Args:
            capability: Name of the capability to invoke.
            payload: Optional payload passed to the capability handler.

        Returns:
            Execution result dictionary if allowed.

        Raises:
            CapabilityNotNegotiatedError: If capability was not negotiated.
        """
        if self.negotiated_caps is None:
            self._record_step("DISPATCH_ATTEMPT", f"invoke({capability})", "REJECTED_UNNEGOTIATED_SESSION")
            raise CapabilityNotNegotiatedError("Cannot dispatch before capability negotiation is completed.")

        if capability not in self.negotiated_caps:
            self._record_step(
                "DISPATCH_REJECTED",
                f"invoke({capability})",
                "REJECTED_BEFORE_DISPATCH",
            )
            raise CapabilityNotNegotiatedError(
                f"Capability '{capability}' was not negotiated. "
                f"Active negotiated set: {sorted(self.negotiated_caps)}"
            )

        # Successful dispatch
        self.dispatch_log.append(capability)
        result = {
            "capability": capability,
            "status": "DISPATCHED",
            "payload": payload,
        }
        self._record_step("DISPATCH_EXECUTED", f"invoke({capability})", "DISPATCHED")
        return result

    def verify_invariants(self) -> bool:
        """
        Verify the system invariants across the recorded state trace:
        1. Negotiation Invariant: Once negotiated, negotiated_caps == client_caps & server_caps.
        2. Gating Invariant: Every dispatched capability in dispatch_log MUST belong to negotiated_caps.
        3. Pre-dispatch Rejection Invariant: No capability recorded as REJECTED_BEFORE_DISPATCH
           was ever executed or added to dispatch_log.
        """
        for state in self.trace:
            if state.negotiated_caps is not None:
                # Invariant 1: Intersection property
                expected_intersection = state.client_caps.intersection(state.server_caps)
                if state.negotiated_caps != expected_intersection:
                    return False

            if state.last_status == "REJECTED_BEFORE_DISPATCH":
                # Invariant 3: Rejected action cannot be in dispatch log
                cap_name = state.last_action.replace("invoke(", "").replace(")", "")
                if cap_name in self.dispatch_log:
                    return False

        # Invariant 2: All dispatched capabilities were negotiated
        if self.negotiated_caps is not None:
            for dispatched_cap in self.dispatch_log:
                if dispatched_cap not in self.negotiated_caps:
                    return False

        return True

    def get_trace_dicts(self) -> List[Dict[str, Any]]:
        """Return state trace as a list of dicts."""
        return [s.to_dict() for s in self.trace]


def main() -> int:
    """Run demonstration with the standard contract fixture."""
    client_caps = {"tools", "resources"}
    server_caps = {"tools", "prompts"}

    print("=== Capability Negotiation and Invariant State Trace ===")
    print(f"Client capabilities: {sorted(client_caps)}")
    print(f"Server capabilities: {sorted(server_caps)}")

    negotiator = CapabilityNegotiator()
    negotiator.register_client(client_caps)
    negotiator.register_server(server_caps)
    negotiated = negotiator.negotiate()

    print(f"\nNegotiated capabilities (Intersection): {sorted(negotiated)}")

    # Test 1: Invoke negotiated capability ('tools')
    print("\nAttempting to dispatch negotiated capability 'tools'...")
    res = negotiator.dispatch("tools", payload={"tool_name": "calculator"})
    print(f"  Result: {res['status']} for capability '{res['capability']}'")

    # Test 2: Invoke unnegotiated capability ('resources')
    print("\nAttempting to dispatch unnegotiated capability 'resources'...")
    try:
        negotiator.dispatch("resources", payload={"uri": "file://data.csv"})
        print("  ERROR: 'resources' was dispatched unexpectedly!")
        return 1
    except CapabilityNotNegotiatedError as e:
        print(f"  PASS: 'resources' was rejected before dispatch ({e})")

    # Verify Invariants
    invariants_hold = negotiator.verify_invariants()
    print(f"\nState Trace Invariant Check: {'PASSED' if invariants_hold else 'FAILED'}")

    print("\nState Trace History:")
    for step in negotiator.trace:
        print(f"  Step {step.step} [{step.phase}]: {step.last_action} -> {step.last_status}")

    return 0 if invariants_hold else 1


if __name__ == "__main__":
    sys.exit(main())
