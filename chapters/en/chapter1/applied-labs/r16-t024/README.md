# Applied Lab R16-T024: Capability Negotiation Invariant and State Trace

A minimal, runnable concept lab demonstrating capability discovery, set-intersection negotiation, intermediate state tracing, and pre-dispatch feature gating, complementing [Chapter 1, Section 6 ("Transformer Architectures")](../../6.mdx).

---

## 1. Concept and Lesson Connection

In [Chapter 1, Section 6](../../6.mdx), modern Transformer architectures (particularly decoder-based LLMs) are shown extending beyond basic text prediction to diverse modalities and capabilities (tool calling, structured reasoning, multimodal extensions).

In agentic and client-server LLM environments (such as tool-calling runtimes or Model Context Protocol interfaces), the model server and client application negotiate supported features during handshake:
- **Capability Discovery**: Client and server independently announce their supported capability sets.
- **Intersection Negotiation**: The active session capability set is strictly defined as `client_capabilities ∩ server_capabilities`.
- **Pre-dispatch Feature Gating**: Invocations targeting unnegotiated capabilities are intercepted and rejected **before dispatch**, preventing unauthorized execution or unexpected server errors.

---

## 2. Invariants and State Trace

This lab explicitly records intermediate state snapshots after each transition and enforces three system invariants linking state to output:

1. **Negotiation Invariant**:
   $$\text{negotiated\_caps} = \text{client\_caps} \cap \text{server\_caps}$$
   The negotiated set must always equal the exact mathematical intersection of both parties' declared capabilities.
2. **Gating Invariant**:
   $$\forall c \in \text{dispatch\_log}, \quad c \in \text{negotiated\_caps}$$
   Every dispatched capability must strictly belong to the negotiated set.
3. **Pre-dispatch Rejection Invariant**:
   Any invocation targeting an unnegotiated capability must be rejected immediately, ensuring it never enters the execution dispatch log.

### State Transition Trace

| Step | Phase | Client Caps | Server Caps | Negotiated Caps | Action | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | `INITIALIZED` | `[]` | `[]` | `None` | `init` | `READY` |
| **1** | `CLIENT_REGISTERED` | `["resources", "tools"]` | `[]` | `None` | `register_client(...)` | `OK` |
| **2** | `SERVER_REGISTERED` | `["resources", "tools"]` | `["prompts", "tools"]` | `None` | `register_server(...)` | `OK` |
| **3** | `NEGOTIATED` | `["resources", "tools"]` | `["prompts", "tools"]` | `["tools"]` | `negotiate()` | `SETTLED(['tools'])` |
| **4** | `DISPATCH_EXECUTED` | `["resources", "tools"]` | `["prompts", "tools"]` | `["tools"]` | `invoke(tools)` | `DISPATCHED` |
| **5** | `DISPATCH_REJECTED` | `["resources", "tools"]` | `["prompts", "tools"]` | `["tools"]` | `invoke(resources)` | `REJECTED_BEFORE_DISPATCH` |

---

## 3. Fixture Contract and Boundary Decisions

### Standard Contract
- **Client capabilities**: `{"tools", "resources"}`
- **Server capabilities**: `{"tools", "prompts"}`
- **Negotiated capabilities**: `{"tools"}`
- **Dispatch `"tools"`**: Dispatches successfully (`status: DISPATCHED`).
- **Dispatch `"resources"`**: Raises `CapabilityNotNegotiatedError` and status is marked `REJECTED_BEFORE_DISPATCH`.

### Boundary Cases
- **Disjoint sets**: Client `{"tools"}`, Server `{"prompts"}` $\rightarrow$ Negotiated `set()`. Calling either capability is rejected.
- **Empty set**: Client `set()`, Server `{"tools"}` $\rightarrow$ Negotiated `set()`.
- **Pre-negotiation dispatch**: Invoking any capability before `negotiate()` completes raises `CapabilityNotNegotiatedError`.

---

## 4. Scope and Limitations

- **Pedagogical Scope**: Pure Python standard library demonstration of capability intersection and pre-dispatch gating.
- **Prerequisites**: Python 3 standard library (`dataclasses`, `unittest`, `typing`, `sys`).
- **No External Dependencies**: Requires no GPU, cloud API, or network socket communication.
- **Simplifications**: Simulates capability exchange in-memory without network serialization (e.g., JSON-RPC).

---

## 5. Usage and Invocations

### Direct CLI Invocation
```bash
python3 chapters/en/chapter1/applied-labs/r16-t024/example.py
```
Output:
```text
=== Capability Negotiation and Invariant State Trace ===
Client capabilities: ['resources', 'tools']
Server capabilities: ['prompts', 'tools']

Negotiated capabilities (Intersection): ['tools']

Attempting to dispatch negotiated capability 'tools'...
  Result: DISPATCHED for capability 'tools'

Attempting to dispatch unnegotiated capability 'resources'...
  PASS: 'resources' was rejected before dispatch (Capability 'resources' was not negotiated. Active negotiated set: ['tools'])

State Trace Invariant Check: PASSED

State Trace History:
  Step 0 [INITIALIZED]: init -> READY
  Step 1 [CLIENT_REGISTERED]: register_client(['resources', 'tools']) -> OK
  Step 2 [SERVER_REGISTERED]: register_server(['prompts', 'tools']) -> OK
  Step 3 [NEGOTIATED]: negotiate() -> SETTLED(['tools'])
  Step 4 [DISPATCH_EXECUTED]: invoke(tools) -> DISPATCHED
  Step 5 [DISPATCH_REJECTED]: invoke(resources) -> REJECTED_BEFORE_DISPATCH
```

### Python API
```python
from example import CapabilityNegotiator, CapabilityNotNegotiatedError

negotiator = CapabilityNegotiator()
negotiator.register_client({"tools", "resources"})
negotiator.register_server({"tools", "prompts"})
negotiated = negotiator.negotiate()
print(negotiated)  # {'tools'}

# Dispatches
negotiator.dispatch("tools")

# Raises CapabilityNotNegotiatedError
try:
    negotiator.dispatch("resources")
except CapabilityNotNegotiatedError as e:
    print(f"Blocked: {e}")
```

---

## 6. Automated Testing

Run unit tests via `unittest`:
```bash
python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t024 -p "test_*.py" -v
```
All 7 unit tests pass, verifying contract fixtures, boundary conditions, state trace progression, and deliberate invariant failure rejection.
