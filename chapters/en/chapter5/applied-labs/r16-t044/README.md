# Applied Lab R16-T044: Worked Decision Example for Introduction (Invariant and State Trace)

## Related Lesson
- **Chapter**: Chapter 5: The 🤗 Datasets Library
- **Section**: [Introduction (`introduction`)](../../1.mdx)

## Objective & Focus
In Chapter 5, Section 1, the course poses fundamental architecture questions:
- *What do you do when your dataset is not on the Hub?*
- *What do you do when your dataset is huge and will melt your laptop's RAM?*

This applied lab implements:
1. An original **three-scenario worked example** (Normal, Boundary, Missing Information).
2. Explicit step-by-step state traces capturing the intermediate state after each evaluation step.
3. Invariant checks linking intermediate state evolution to the final output.
4. A **published decision table checker** that validates decision outcomes and fails when a decision is deliberately altered.
5. Human-reviewable rationale tied directly to Chapter 5 core concepts.

## Three-Scenario Worked Decision Table

| Scenario Type | Scenario Name | Input Facts | Expected Decision | Rationale Linked to Lesson |
|---|---|---|---|---|
| **Normal** | `hub_standard_in_memory` | `source='hub'`, `size_gb=0.5`, `ram_gb=16` | `HUB_IN_MEMORY` | Dataset is hosted on the Hub and fits within memory; uses Apache Arrow memory mapping. |
| **Boundary** | `huge_pile_dataset_boundary` | `source='hub'`, `size_gb=825.0`, `ram_gb=16` | `STREAM_FROM_DISK_OR_URL` | Dataset exceeds RAM ("melts laptop's RAM"); streaming iteration (`streaming=True`) is required. |
| **Missing-Info** | `unspecified_dataset_volume` | `source='local'`, `size_gb=None` | `REQUEST_MISSING_INFO` | Essential dataset volume fact is missing; cannot decide between in-memory loading and streaming without volume. |

## Invariants & State Tracing Contract
- **Intermediate States**: Captured at each discrete step (`completeness_check`, `source_evaluation`, `scale_and_memory_boundary_check`, `strategy_synthesis`).
- **Invariant Rules**:
  - `step_number == len(trace)` at each step.
  - Final decision in terminal step matches the returned result.
  - Decision table checker validates exact decision matches and fails if any row is tampered with.

## Scope & Simplifications
- **Deterministic Standard Library Model**: Uses Python dataclasses and dictionaries without external libraries.
- **No External Services**: No real datasets downloaded, no paid cloud APIs, no network access, and no GPU resources required.
- **Hardware Neutral**: Models memory thresholds symbolically; makes no hardware performance claims.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter5/applied-labs/r16-t044/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t044 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T044/check.py
```
