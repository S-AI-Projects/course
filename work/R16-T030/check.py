"""
Automated verification and contract check for Task R16-T030.

Verifies:
  1. (id1, score: 2), (id2, score: 5), (id3, score: 5) filtered by score >= 5
     and projected on 'id' yields ['id2', 'id3'] in order.
  2. Source collection immutability (input sequence is not mutated).
  3. Scenario Question 1 (Predict Output) verified with executable check.
  4. Scenario Question 2 (Diagnose Failure) verified with executable check.
  5. Scenario Question 3 (Boundary Policy) verified with executable check.
  6. Deliberate failure triggers assertion error and non-zero exit.
  7. Automated unit test suite execution and status reporting.

Saves structured execution results to results.json and human-readable summary to report.txt.
"""

from __future__ import annotations

import copy
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
LAB_DIR = PROJECT_ROOT / "chapters" / "en" / "chapter5" / "applied-labs" / "r16-t030"
WORK_DIR = PROJECT_ROOT / "work" / "R16-T030"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(LAB_DIR))

from example import (  # noqa: E402
    APPLIED_QUESTIONS,
    CANONICAL_ROWS,
    DatasetSelection,
    check_question_1_predict_output,
    check_question_2_diagnose_failure,
    check_question_3_boundary_policy,
    filter_and_project,
    verify_applied_questions,
)


def run_checks() -> dict:
    """Runs all contract checks and records environment metadata and results."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "task_id": "R16-T030",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "working_directory": str(PROJECT_ROOT),
        },
        "checks": [],
        "overall_status": "FAILED",
    }

    # --- Contract Check 1: Canonical Selection and Projection ---
    input_rows = copy.deepcopy(CANONICAL_ROWS)
    source_snapshot = copy.deepcopy(input_rows)

    projected_ids, projected_records = filter_and_project(
        input_rows,
        predicate=lambda r: r["score"] >= 5,
        column="id",
    )

    check_1_pass = projected_ids == ["id2", "id3"]
    assert check_1_pass, f"Contract 1 failed: expected ['id2', 'id3'], got {projected_ids}"
    results["checks"].append({
        "name": "canonical_filter_and_project",
        "status": "PASS",
        "expected": ["id2", "id3"],
        "actual": projected_ids,
        "projected_records": projected_records,
    })
    print("[PASS] Rows filtered score>=5 projected 'id' yielded ['id2', 'id3'] in order")

    # --- Contract Check 2: Source Immutability ---
    check_2_pass = input_rows == source_snapshot
    assert check_2_pass, "Contract 2 failed: source collection was mutated during operation"
    results["checks"].append({
        "name": "source_collection_immutability",
        "status": "PASS",
        "detail": "Input sequence and record dictionaries remained unmutated",
    })
    print("[PASS] Source collection remained completely unmutated")

    # --- Contract Check 3: Q1 Predict Output ---
    q1_pass = check_question_1_predict_output()
    assert q1_pass, "Contract 3 failed: Q1 executable check failed"
    results["checks"].append({
        "name": "scenario_q1_predict_output",
        "status": "PASS",
        "verified": True,
    })
    print("[PASS] Scenario Assessment Q1 (Predict Output) verified")

    # --- Contract Check 4: Q2 Diagnose Failure ---
    q2_pass = check_question_2_diagnose_failure()
    assert q2_pass, "Contract 4 failed: Q2 executable check failed"
    results["checks"].append({
        "name": "scenario_q2_diagnose_failure",
        "status": "PASS",
        "verified": True,
    })
    print("[PASS] Scenario Assessment Q2 (Diagnose Failure) verified")

    # --- Contract Check 5: Q3 Boundary Policy ---
    q3_pass = check_question_3_boundary_policy()
    assert q3_pass, "Contract 5 failed: Q3 executable check failed"
    results["checks"].append({
        "name": "scenario_q3_boundary_policy",
        "status": "PASS",
        "verified": True,
    })
    print("[PASS] Scenario Assessment Q3 (Boundary Policy) verified")

    # --- Contract Check 6: Deliberate failure test ---
    print("\nVerifying deliberate wrong result triggers failure...")
    try:
        assert projected_ids == ["id1"], "Simulated deliberate wrong check"
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
        f.write("=== Task R16-T030 Verification Report ===\n")
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
