"""
Automated verification and contract check for Task R16-T028.

Verifies:
  1. A, B, A, C yields {'A': 2, 'B': 1, 'C': 1} with bounded state and zero errors.
  2. Empty input yields {}.
  3. Malformed JSON line is reported with exact 1-based line number.
  4. Stream recovers on the next valid record and completes aggregation.
  5. Missing category key is reported and stream recovers.
  6. Deliberate failure triggers non-zero exit / assertion error.
  7. Automated unit test suite execution and status reporting.

Saves structured execution results to results.json and human-readable summary to report.txt.
"""

from __future__ import annotations

import io
import json
import os
import platform
import sys
import unittest
from datetime import datetime
from pathlib import Path

# Add project root and lab directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LAB_DIR = PROJECT_ROOT / "chapters" / "en" / "chapter5" / "applied-labs" / "r16-t028"
WORK_DIR = PROJECT_ROOT / "work" / "R16-T028"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(LAB_DIR))

from example import (  # noqa: E402
    FIXTURE_ABAC,
    FIXTURE_EMPTY,
    FIXTURE_MALFORMED_WITH_RECOVERY,
    FIXTURE_MISSING_KEY_WITH_RECOVERY,
    StreamingCategoryAggregator,
)


def run_checks() -> dict:
    """Runs all contract checks and records environment metadata and results."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "task_id": "R16-T028",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "working_directory": str(PROJECT_ROOT),
        },
        "checks": [],
        "overall_status": "FAILED",
    }

    aggregator = StreamingCategoryAggregator()

    # --- Contract Check 1: Canonical A, B, A, C ---
    res_abac = aggregator.aggregate_string(FIXTURE_ABAC)
    check_1_pass = (
        res_abac.counts == {"A": 2, "B": 1, "C": 1}
        and res_abac.total_lines == 4
        and res_abac.valid_records == 4
        and len(res_abac.errors) == 0
    )
    assert check_1_pass, f"Contract 1 failed: expected {{'A': 2, 'B': 1, 'C': 1}}, got {res_abac.counts}"
    results["checks"].append({
        "name": "canonical_abac_counts",
        "status": "PASS",
        "expected": {"A": 2, "B": 1, "C": 1},
        "actual": res_abac.counts,
        "valid_records": res_abac.valid_records,
        "errors": len(res_abac.errors),
    })
    print("[PASS] Canonical stream A, B, A, C yielded expected counts {'A': 2, 'B': 1, 'C': 1}")

    # --- Contract Check 2: Empty input gives {} ---
    res_empty = aggregator.aggregate_string(FIXTURE_EMPTY)
    check_2_pass = (
        res_empty.counts == {}
        and res_empty.total_lines == 0
        and res_empty.valid_records == 0
        and len(res_empty.errors) == 0
    )
    assert check_2_pass, f"Contract 2 failed: expected {{}}, got {res_empty.counts}"
    results["checks"].append({
        "name": "empty_input_counts",
        "status": "PASS",
        "expected": {},
        "actual": res_empty.counts,
        "total_lines": res_empty.total_lines,
    })
    print("[PASS] Empty input yielded {}")

    # --- Contract Check 3: Malformed line reported with line number ---
    res_malformed = aggregator.aggregate_string(FIXTURE_MALFORMED_WITH_RECOVERY)
    err_3 = res_malformed.errors[0] if res_malformed.errors else None
    check_3_pass = (
        len(res_malformed.errors) == 1
        and err_3 is not None
        and err_3.line_number == 2
        and err_3.error_type == "SYNTAX_ERROR"
    )
    assert check_3_pass, f"Contract 3 failed: expected line 2 SYNTAX_ERROR, got {err_3}"
    results["checks"].append({
        "name": "malformed_line_reporting",
        "status": "PASS",
        "reported_line": err_3.line_number,
        "error_type": err_3.error_type,
        "message": err_3.message,
    })
    print(f"[PASS] Malformed record accurately reported at line {err_3.line_number}: {err_3.error_type}")

    # --- Contract Check 4: Recovery on next valid input ---
    check_4_pass = (
        res_malformed.recovered is True
        and res_malformed.counts == {"A": 2, "B": 1, "C": 1}
        and res_malformed.valid_records == 4
    )
    assert check_4_pass, f"Contract 4 failed: recovery failed, got counts {res_malformed.counts}"
    results["checks"].append({
        "name": "stream_recovery_after_error",
        "status": "PASS",
        "recovered": res_malformed.recovered,
        "final_counts": res_malformed.counts,
        "valid_records": res_malformed.valid_records,
    })
    print(f"[PASS] Ingestion demonstrated recovery on next input with counts: {res_malformed.counts}")

    # --- Contract Check 5: Missing key reported with line number and recovery ---
    res_missing = aggregator.aggregate_string(FIXTURE_MISSING_KEY_WITH_RECOVERY)
    err_5 = res_missing.errors[0] if res_missing.errors else None
    check_5_pass = (
        len(res_missing.errors) == 1
        and err_5 is not None
        and err_5.line_number == 2
        and err_5.error_type == "MISSING_FIELD"
        and res_missing.recovered is True
        and res_missing.counts == {"A": 2, "B": 1, "C": 1}
    )
    assert check_5_pass, f"Contract 5 failed: expected missing field error on line 2, got {err_5}"
    results["checks"].append({
        "name": "missing_field_reporting_and_recovery",
        "status": "PASS",
        "reported_line": err_5.line_number,
        "error_type": err_5.error_type,
        "recovered": res_missing.recovered,
    })
    print(f"[PASS] Missing field accurately reported at line {err_5.line_number} with successful recovery")

    # --- Contract Check 6: Deliberate failure test ---
    print("\nVerifying deliberate wrong result triggers failure...")
    try:
        assert res_abac.counts == {"A": 999, "B": 0}, "Simulated deliberate wrong check"
        raise RuntimeError("Deliberate failure check did not trigger assertion error!")
    except AssertionError:
        results["checks"].append({
            "name": "deliberate_failure_check",
            "status": "PASS",
            "detail": "AssertionError successfully raised on deliberate wrong result",
        })
        print("Deliberate failure test passed: wrong result correctly detected.")

    # --- Automated Unittest Suite Run ---
    print("\nRunning automated unittest discovery...")
    loader = unittest.TestLoader()
    suite = loader.discover(str(LAB_DIR), pattern="test_*.py")
    stream_buffer = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream_buffer, verbosity=2)
    test_result = runner.run(suite)
    stream_buffer.seek(0)
    unittest_log = stream_buffer.read()
    print(unittest_log)

    unittest_passed = test_result.wasSuccessful() and test_result.testsRun > 0
    assert unittest_passed, f"Unittest discovery failed or 0 tests run: {test_result}"

    results["unittests"] = {
        "tests_run": test_result.testsRun,
        "failures": len(test_result.failures),
        "errors": len(test_result.errors),
        "was_successful": test_result.wasSuccessful(),
    }

    results["overall_status"] = "PASSED"

    # Save results.json
    results_path = WORK_DIR / "results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Save report.txt
    report_path = WORK_DIR / "report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== Task R16-T028 Verification Report ===\n")
        f.write(f"Timestamp: {results['timestamp']}\n")
        f.write(f"Python Version: {results['environment']['python_version']}\n")
        f.write(f"Platform: {results['environment']['platform']}\n\n")
        f.write("Contract Checks:\n")
        for c in results["checks"]:
            f.write(f"  [{c['status']}] {c['name']}\n")
        f.write(f"\nUnittest Summary: {results['unittests']['tests_run']} tests run, {results['unittests']['failures']} failures, {results['unittests']['errors']} errors.\n")
        f.write(f"Overall Status: {results['overall_status']}\n")

    print(f"\nSaved check results to {results_path} and {report_path}")
    print("All checks completed successfully with exit code 0.")
    return results


if __name__ == "__main__":
    try:
        run_checks()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FATAL] Assertion failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
