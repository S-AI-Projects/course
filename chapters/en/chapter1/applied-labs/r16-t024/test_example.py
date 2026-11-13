#!/usr/bin/env python3
"""
Unit tests for Capability Negotiation Invariant and State Trace Lab (R16-T024).

Verifies capability intersection, strict pre-dispatch gating, state tracing,
and invariant preservation across intermediate steps.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

# Ensure current lab directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (
    CapabilityNegotiator,
    CapabilityNotNegotiatedError,
    main,
)


class TestCapabilityNegotiation(unittest.TestCase):
    """Test suite for CapabilityNegotiator and State Trace Invariants."""

    def test_required_contract_negotiation_and_rejection(self):
        """
        Verify the core contract:
        Client {tools, resources}, Server {tools, prompts} -> Negotiates {tools}.
        Invoking 'tools' succeeds.
        Invoking 'resources' is rejected before dispatch.
        """
        negotiator = CapabilityNegotiator()
        negotiator.register_client({"tools", "resources"})
        negotiator.register_server({"tools", "prompts"})
        negotiated = negotiator.negotiate()

        # Negotiated intersection is {"tools"}
        self.assertEqual(negotiated, {"tools"})

        # 'tools' can be dispatched
        res = negotiator.dispatch("tools", payload={"arg": 1})
        self.assertEqual(res["status"], "DISPATCHED")
        self.assertEqual(res["capability"], "tools")
        self.assertIn("tools", negotiator.dispatch_log)

        # 'resources' is rejected BEFORE dispatch
        with self.assertRaises(CapabilityNotNegotiatedError):
            negotiator.dispatch("resources")

        # Invariant: 'resources' is NOT in the dispatch log
        self.assertNotIn("resources", negotiator.dispatch_log)

        # Invariant verification across trace
        self.assertTrue(negotiator.verify_invariants())

    def test_state_trace_progression(self):
        """
        Verify intermediate states are faithfully captured step-by-step
        and linked to the final output.
        """
        negotiator = CapabilityNegotiator()
        negotiator.register_client({"tools", "resources"})
        negotiator.register_server({"tools", "prompts"})
        negotiator.negotiate()
        negotiator.dispatch("tools")
        try:
            negotiator.dispatch("resources")
        except CapabilityNotNegotiatedError:
            pass

        trace = negotiator.trace
        self.assertEqual(len(trace), 6)

        # Step 0: INITIALIZED
        self.assertEqual(trace[0].phase, "INITIALIZED")
        self.assertIsNone(trace[0].negotiated_caps)

        # Step 1: CLIENT_REGISTERED
        self.assertEqual(trace[1].phase, "CLIENT_REGISTERED")
        self.assertEqual(trace[1].client_caps, {"tools", "resources"})

        # Step 2: SERVER_REGISTERED
        self.assertEqual(trace[2].phase, "SERVER_REGISTERED")
        self.assertEqual(trace[2].server_caps, {"tools", "prompts"})

        # Step 3: NEGOTIATED
        self.assertEqual(trace[3].phase, "NEGOTIATED")
        self.assertEqual(trace[3].negotiated_caps, {"tools"})

        # Step 4: DISPATCH_EXECUTED
        self.assertEqual(trace[4].phase, "DISPATCH_EXECUTED")
        self.assertEqual(trace[4].last_status, "DISPATCHED")

        # Step 5: DISPATCH_REJECTED
        self.assertEqual(trace[5].phase, "DISPATCH_REJECTED")
        self.assertEqual(trace[5].last_status, "REJECTED_BEFORE_DISPATCH")

    def test_boundary_disjoint_capabilities(self):
        """Disjoint capability sets negotiate to an empty set."""
        negotiator = CapabilityNegotiator()
        negotiator.register_client({"tools"})
        negotiator.register_server({"prompts"})
        negotiated = negotiator.negotiate()

        self.assertEqual(negotiated, set())
        with self.assertRaises(CapabilityNotNegotiatedError):
            negotiator.dispatch("tools")
        with self.assertRaises(CapabilityNotNegotiatedError):
            negotiator.dispatch("prompts")
        self.assertEqual(len(negotiator.dispatch_log), 0)
        self.assertTrue(negotiator.verify_invariants())

    def test_boundary_empty_capabilities(self):
        """Empty client or server set results in empty negotiated set."""
        negotiator = CapabilityNegotiator()
        negotiator.register_client(set())
        negotiator.register_server({"tools", "prompts"})
        self.assertEqual(negotiator.negotiate(), set())
        self.assertTrue(negotiator.verify_invariants())

    def test_dispatch_before_negotiate_rejected(self):
        """Attempting to dispatch before negotiation raises error."""
        negotiator = CapabilityNegotiator()
        negotiator.register_client({"tools"})
        negotiator.register_server({"tools"})
        # Do not call negotiate()
        with self.assertRaises(CapabilityNotNegotiatedError):
            negotiator.dispatch("tools")

    def test_deliberate_invariant_failure_detected(self):
        """
        Verify that tampering with internal state or dispatch log
        correctly causes verify_invariants() to return False.
        """
        negotiator = CapabilityNegotiator()
        negotiator.register_client({"tools"})
        negotiator.register_server({"tools"})
        negotiator.negotiate()

        # Artificially inject an unauthorized capability into the dispatch log
        negotiator.dispatch_log.append("unauthorized_leak")
        self.assertFalse(negotiator.verify_invariants())

    def test_cli_main_execution(self):
        """Verify CLI main entrypoint executes cleanly and produces expected text."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("Client capabilities: ['resources', 'tools']", output)
        self.assertIn("Server capabilities: ['prompts', 'tools']", output)
        self.assertIn("Negotiated capabilities (Intersection): ['tools']", output)
        self.assertIn("DISPATCHED for capability 'tools'", output)
        self.assertIn("'resources' was rejected before dispatch", output)
        self.assertIn("State Trace Invariant Check: PASSED", output)


if __name__ == "__main__":
    unittest.main()
