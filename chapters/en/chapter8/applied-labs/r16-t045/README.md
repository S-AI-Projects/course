# Applied Lab R16-T045: Worked Decision Example for Introduction (Offline Service Adapter)

## Related Lesson
- **Chapter**: Chapter 8: How to Ask for Help and Debug
- **Section**: [Introduction (`introduction`)](../../1.mdx)

## Objective & Focus
In Chapter 8, Section 1, developers are introduced to structured problem resolution:
1. Debugging local scripts/pipelines directly.
2. Asking for help on the Discuss Hugging Face forums.
3. Writing actionable GitHub bug reports for upstream library defects.

This applied lab implements:
1. An original **three-scenario worked decision model** (Normal, Boundary, Missing Information).
2. An **offline service adapter pattern**: abstracting external service calls behind a callable interface (`ExternalServicePort`) and supplying a deterministic local implementation (`OfflineServiceAdapter`).
3. An automated **published decision table checker** that validates decision consistency and fails if any decision is altered.

## Three-Scenario Worked Decision Table

| Scenario Type | Scenario Name | Input Facts | Expected Decision | Rationale Linked to Lesson |
|---|---|---|---|---|
| **Normal** | `local_training_runtime_error` | `error_origin='local_code'`, `has_minimal_repro=True`, `is_upstream_library_bug=False` | `LOCAL_DEBUG` | Inspect traceback and debug local training pipeline before escalating. |
| **Boundary** | `reproducible_library_defect` | `error_origin='transformers_core'`, `has_minimal_repro=True`, `is_upstream_library_bug=True` | `LIBRARY_BUG_REPORT` | Confirmed upstream defect with minimal reproduction; file a structured GitHub issue. |
| **Missing-Info** | `vague_crash_without_origin_or_repro` | `error_origin=None`, `has_minimal_repro=None` | `REQUEST_MISSING_INFO` | Essential facts missing; reproduction and origin required before seeking help. |

## External Dependency & Offline Service Adapter
- **Callable Interface**: `ExternalServicePort` defines `submit_report(payload: Dict[str, Any]) -> Dict[str, Any]`.
- **Deterministic Local Adapter**: `OfflineServiceAdapter` intercepts external calls in-memory, avoiding network dependencies.
- **Real-Service Behavior Not Established**:
  - Live HTTP networking, connection timeouts, and DNS resolution.
  - Authentication tokens, OAuth scopes, and HTTP 429 rate limits.
  - Forum Discourse / GitHub webhook processing and markdown parsing.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter8/applied-labs/r16-t045/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t045 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T045/check.py
```
