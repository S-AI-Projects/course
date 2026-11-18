# Applied Lab R16-T025: Hub Integrations Worked Decision Example

A minimal, runnable concept lab demonstrating decision-making for Gradio Hugging Face Hub and Spaces integrations, complementing [Chapter 9, Section 5 ("Integrations with the Hugging Face Hub")](../../5.mdx).

---

## 1. Concept and Lesson Connection

In [Chapter 9, Section 5](../../5.mdx), Gradio provides one-line integrations with the Hugging Face ecosystem via `gr.Interface.load()`:
1. **Model Loading (`huggingface/<model>` or `model/<model>`)**:
   Routes inference through the **Hugging Face Inference API** in the cloud rather than loading weights into local memory. This is critical for massive models (such as GPT-J-6B or T0pp) that exceed standard local RAM/VRAM capacity.
2. **Space Loading (`spaces/<space>`)**:
   Recreates an established, multi-component **Hugging Face Space** locally, allowing developers to customize UI parameters (such as overriding file upload with live webcam inputs).
3. **Decision & Routing Boundary**:
   Because `Interface.load()` depends on explicit prefix routing (`huggingface/` vs. `spaces/`), the integration layer must inspect artifact metadata. If essential information is missing, the request must be safely rejected before dispatch.

---

## 2. Three-Scenario Worked Decision Table

| Scenario | Input Facts | Decision | Target Prefix | Lesson-Tied Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Normal** | - Artifact: `EleutherAI/gpt-j-6B`<br>- Type: `model` (6B params)<br>- Local RAM: 4 GB<br>- Online: `True` | `LOAD_HUB_MODEL` | `huggingface/EleutherAI/gpt-j-6B` | GPT-J-6B requires ~24GB+ RAM in FP32/FP16, exceeding local 4GB host memory. Using `Interface.load('huggingface/EleutherAI/gpt-j-6B')` delegates execution to the HF Inference API without downloading weights locally. |
| **Boundary** | - Artifact: `abidlabs/remove-bg`<br>- Type: `space`<br>- Local RAM: 16 GB<br>- Custom input: `webcam`<br>- Online: `True` | `LOAD_SPACES_APP` | `spaces/abidlabs/remove-bg` | The target is an established multi-step Space application. `Interface.load('spaces/abidlabs/remove-bg')` recreates the remote Space locally while allowing parameter overrides (`inputs='webcam'`). |
| **Missing Information** | - Artifact: `custom-org/unspecified-pkg`<br>- Type: `None`<br>- Local RAM: 8 GB<br>- Online: `True` | `REJECT_INSUFFICIENT_INFORMATION` | `None` | The artifact type is unspecified. Without knowing whether the target is a model checkpoint or a Space, the system cannot determine the routing prefix and rejects the request before remote dispatch. |

---

## 3. Callable Interface and Offline Local Adapter

The external dependency is placed behind an abstract callable interface:
- **Interface**: `HubIntegrationService`
- **Adapter**: `LocalDeterministicHubAdapter`

### Real-Service Behaviors This Mock Does NOT Establish
As a deterministic offline adapter, this implementation deliberately avoids external network calls and does **NOT** establish:
1. **Real network latency & transport failures**: HTTP connection timeouts, DNS resolution failures, and intermittent packet drops.
2. **Rate limits & compute quotas**: Hugging Face Inference API HTTP 429 ("Too Many Requests") responses and user tier throttling.
3. **Authentication verification**: Token validation via `HF_TOKEN` for private repositories and gated model license agreements.
4. **Cold-start delays**: Remote model initialization latency (HTTP 503 "Model is currently loading").
5. **Live Space schema verification**: Validating that remote Space components match requested local parameter overrides.

---

## 4. Usage and Invocations

### Direct CLI Invocation
```bash
python3 chapters/en/chapter9/applied-labs/r16-t025/example.py
```
Output:
```text
=== Hugging Face Hub Integrations: Worked Decision Example ===

--- Published Scenarios & Decision Table ---

Scenario: [NORMAL]
  Facts:    {'artifact_id': 'EleutherAI/gpt-j-6B', 'artifact_type': 'model', 'parameter_count': '6B', 'local_ram_gb': 4, 'network_online': True}
  Decision: LOAD_HUB_MODEL
  Prefix:   huggingface/EleutherAI/gpt-j-6B
  Rationale: The model has 6 billion parameters and requires substantial RAM (~24GB+ in FP32/FP16), exceeding the local 4GB host memory...

Scenario: [BOUNDARY]
  Facts:    {'artifact_id': 'abidlabs/remove-bg', 'artifact_type': 'space', 'parameter_count': None, 'local_ram_gb': 16, 'custom_input': 'webcam', 'network_online': True}
  Decision: LOAD_SPACES_APP
  Prefix:   spaces/abidlabs/remove-bg
  Rationale: The target is an established, multi-component Space application...

Scenario: [MISSING_INFORMATION]
  Facts:    {'artifact_id': 'custom-org/unspecified-pkg', 'artifact_type': None, 'parameter_count': None, 'local_ram_gb': 8, 'network_online': True}
  Decision: REJECT_INSUFFICIENT_INFORMATION
  Prefix:   None
  Rationale: The artifact type (model vs. space) is unspecified...

--- Running Decision Table Checker ---
Checker Status: ALL_PASSED
  [PASS] normal -> LOAD_HUB_MODEL (huggingface/EleutherAI/gpt-j-6B)
  [PASS] boundary -> LOAD_SPACES_APP (spaces/abidlabs/remove-bg)
  [PASS] missing_information -> REJECT_INSUFFICIENT_INFORMATION (None)

--- Unestablished Real-Service Behaviors (Explicit Boundaries) ---
  1. Network latency, connection timeouts, and DNS resolution failures.
  2. Hugging Face Inference API rate limits (HTTP 429) and compute quotas.
  3. Authentication against private repositories using user access tokens (HF_TOKEN).
  4. Cold-start model loading delays on the remote Inference API.
  5. Real-time remote Space schema verification and component compatibility.
```

### Python API
```python
from example import LocalDeterministicHubAdapter, check_decision_table

adapter = LocalDeterministicHubAdapter()
decision, prefix, rationale = adapter.evaluate({
    "artifact_id": "EleutherAI/gpt-j-6B",
    "artifact_type": "model"
})
print(decision)  # DecisionType.LOAD_HUB_MODEL
print(prefix)    # "huggingface/EleutherAI/gpt-j-6B"

# Run checker
check_decision_table(adapter)
```

---

## 5. Automated Testing

Run unit tests via `unittest`:
```bash
python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t025 -p "test_*.py" -v
```
All 8 unit tests pass in a fresh process, verifying each scenario, the decision checker, deliberate failure detection when decisions are mutated, and the documented unestablished behaviors.
