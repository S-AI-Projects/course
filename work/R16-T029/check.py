"""
Automated verification and contract check for Task R16-T029.

Verifies:
  1. (15, 75) is classified as INSIDE.
  2. Boundary (10, 70) is classified as INSIDE (inclusive boundary).
  3. (21, 75) is classified as OUTSIDE.
  4. Invalid latitude 100 is rejected with InvalidCoordinateError.
  5. 3 controlled configurations are evaluated with accuracy and throughput trade-off reporting.
  6. Non-spherical distance model disclaimer is explicitly recorded.
  7. Deliberate failure triggers assertion error and non-zero exit.
  8. Automated unit test suite execution and status reporting.

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
LAB_DIR = PROJECT_ROOT / "chapters" / "en" / "chapter5" / "applied-labs" / "r16-t029"
WORK_DIR = PROJECT_ROOT / "work" / "R16-T029"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(LAB_DIR))

from example import (  # noqa: E402
    POINT_BOUNDARY,
    POINT_INSIDE,
    POINT_INVALID,
    POINT_OUTSIDE,
    GeofenceResult,
    InvalidCoordinateError,
    RectangularGeofence,
    run_controlled_evaluation,
)


def run_checks() -> dict:
    """Runs all contract checks and records environment metadata and results."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "task_id": "R16-T029",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "working_directory": str(PROJECT_ROOT),
        },
        "model_disclaimer": "Planar 2D rectangular bounding box fixture; not a spherical-distance model.",
        "checks": [],
        "overall_status": "FAILED",
    }

    geofence = RectangularGeofence(min_lat=10.0, max_lat=20.0, min_lon=70.0, max_lon=80.0)

    # --- Contract Check 1: Inside point (15, 75) ---
    res_inside = geofence.classify_point(POINT_INSIDE[0], POINT_INSIDE[1])
    assert res_inside.status == "INSIDE" and res_inside.is_inside is True, (
        f"Contract 1 failed: expected (15, 75) to be INSIDE, got {res_inside}"
    )
    results["checks"].append({
        "name": "point_inside",
        "point": POINT_INSIDE,
        "status": "PASS",
        "expected": "INSIDE",
        "actual": res_inside.status,
    })
    print(f"[PASS] Point {POINT_INSIDE} classified as INSIDE (is_inside=True)")

    # --- Contract Check 2: Boundary point (10, 70) ---
    res_bnd = geofence.classify_point(POINT_BOUNDARY[0], POINT_BOUNDARY[1])
    assert res_bnd.status == "INSIDE" and res_bnd.is_inside is True, (
        f"Contract 2 failed: expected boundary (10, 70) to be INSIDE, got {res_bnd}"
    )
    results["checks"].append({
        "name": "boundary_point_inclusive",
        "point": POINT_BOUNDARY,
        "status": "PASS",
        "expected": "INSIDE",
        "actual": res_bnd.status,
    })
    print(f"[PASS] Boundary point {POINT_BOUNDARY} classified as INSIDE (is_inside=True)")

    # --- Contract Check 3: Outside point (21, 75) ---
    res_out = geofence.classify_point(POINT_OUTSIDE[0], POINT_OUTSIDE[1])
    assert res_out.status == "OUTSIDE" and res_out.is_inside is False, (
        f"Contract 3 failed: expected (21, 75) to be OUTSIDE, got {res_out}"
    )
    results["checks"].append({
        "name": "point_outside",
        "point": POINT_OUTSIDE,
        "status": "PASS",
        "expected": "OUTSIDE",
        "actual": res_out.status,
    })
    print(f"[PASS] Point {POINT_OUTSIDE} classified as OUTSIDE (is_inside=False)")

    # --- Contract Check 4: Invalid latitude 100 rejected ---
    invalid_rejected = False
    try:
        geofence.classify_point(POINT_INVALID[0], POINT_INVALID[1], safe=False)
    except InvalidCoordinateError as err:
        invalid_rejected = True
        results["checks"].append({
            "name": "invalid_latitude_rejected",
            "point": POINT_INVALID,
            "status": "PASS",
            "detail": f"Correctly rejected with error: {err.message}",
        })
        print(f"[PASS] Invalid latitude {POINT_INVALID} correctly rejected with InvalidCoordinateError")

    assert invalid_rejected, f"Contract 4 failed: Point {POINT_INVALID} was not rejected"

    # --- Contract Check 5: 3-Configuration Evaluation Experiment ---
    eval_report = run_controlled_evaluation()
    configs = eval_report.get("configurations", [])
    assert len(configs) == 3, f"Expected 3 controlled configurations, found {len(configs)}"
    for cfg in configs:
        assert cfg["accuracy_pct"] == 100.0, f"Expected 100% accuracy, got {cfg['accuracy_pct']}"
        assert cfg["sample_size"] in [5, 25, 100]

    results["checks"].append({
        "name": "three_configuration_evaluation",
        "status": "PASS",
        "configurations_evaluated": len(configs),
        "configurations": configs,
    })
    print(f"[PASS] Controlled evaluation across 3 configurations verified 100% accuracy and trade-off metrics")

    # --- Contract Check 6: Deliberate failure test ---
    print("\nVerifying deliberate wrong result triggers failure...")
    try:
        assert geofence.contains(POINT_OUTSIDE[0], POINT_OUTSIDE[1]) is True, "Simulated deliberate wrong check"
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
        f.write("=== Task R16-T029 Verification Report ===\n")
        f.write(f"Timestamp: {results['timestamp']}\n")
        f.write(f"Python Version: {results['environment']['python_version']}\n")
        f.write(f"Platform: {results['environment']['platform']}\n")
        f.write(f"Model Disclaimer: {results['model_disclaimer']}\n\n")
        f.write("Contract Checks:\n")
        for c in results["checks"]:
            f.write(f"  [{c['status']}] {c['name']}\n")
        f.write("\nEvaluation Configurations:\n")
        for cfg in configs:
            f.write(
                f"  - {cfg['configuration']}: N={cfg['sample_size']}, Accuracy={cfg['accuracy_pct']}%, "
                f"Throughput={cfg['throughput_rec_per_sec']} rec/s ({cfg['elapsed_microseconds']} us)\n"
            )
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
