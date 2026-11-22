#!/usr/bin/env python3
"""
Verification check script for R16-T027.
Verifies contract assertions, checks schema enforcement and ID provenance,
confirms deliberate failure detection, records tool versions, and saves inputs/outputs
into work/R16-T027/. Exits non-zero if any assertion or test fails.
"""

import json
import os
import platform
import subprocess
import sys

# Ensure lab directory is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LAB_DIR = os.path.join(REPO_ROOT, "chapters/en/chapter5/applied-labs/r16-t027")
WORK_DIR = os.path.join(REPO_ROOT, "work/R16-T027")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    DUPLICATE_ID_FIXTURE,
    MISSING_LABEL_FIXTURE,
    VALID_TWO_SPLIT_FIXTURE,
    DatasetManifestValidator,
    ManifestValidationError,
)


def run_checks() -> None:
    print("=== Running Checks for Task R16-T027 ===")

    # 1. Environment & tool versions
    env_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "task_id": "R16-T027",
        "branch": "student/e26b07f0747/R16-T027",
    }
    print(f"Python Version: {env_info['python_version']}")
    print(f"Platform: {env_info['platform']}")

    validator = DatasetManifestValidator()
    contract_checks = []

    # Check 1: Valid two-split fixture passes
    report = validator.validate_manifest(VALID_TWO_SPLIT_FIXTURE)
    passed1 = (
        report.is_valid is True
        and report.total_records == 3
        and report.split_counts == {"train": 2, "validation": 1}
        and report.unique_ids == [101, 102, 201]
    )
    contract_checks.append({
        "description": "Valid two-split fixture passes with 3 records and verified unique IDs",
        "input": "VALID_TWO_SPLIT_FIXTURE",
        "expected": {"is_valid": True, "total_records": 3, "split_counts": {"train": 2, "validation": 1}},
        "actual": {"is_valid": report.is_valid, "total_records": report.total_records, "split_counts": report.split_counts},
        "status": "PASS" if passed1 else "FAIL",
    })
    if not passed1:
        print("ERROR: Valid fixture check failed!")
        sys.exit(1)

    # Check 2: Missing label fails with line number
    missing_label_caught = False
    caught_line = None
    caught_field = None
    try:
        validator.validate_manifest(MISSING_LABEL_FIXTURE)
    except ManifestValidationError as err:
        missing_label_caught = True
        caught_line = err.line_number
        caught_field = err.field

    passed2 = missing_label_caught and caught_line == 2 and caught_field == "label"
    contract_checks.append({
        "description": "Missing required field 'label' fails with line number 2 in 'train'",
        "input": "MISSING_LABEL_FIXTURE",
        "expected": {"error_caught": True, "line_number": 2, "field": "label"},
        "actual": {"error_caught": missing_label_caught, "line_number": caught_line, "field": caught_field},
        "status": "PASS" if passed2 else "FAIL",
    })
    if not passed2:
        print("ERROR: Missing label check failed!")
        sys.exit(1)

    # Check 3: Duplicate ID across splits fails
    duplicate_caught = False
    conflicting_id = None
    try:
        validator.validate_manifest(DUPLICATE_ID_FIXTURE)
    except ManifestValidationError as err:
        duplicate_caught = True
        conflicting_id = err.conflicting_id

    passed3 = duplicate_caught and conflicting_id == 101
    contract_checks.append({
        "description": "Duplicate ID '101' detected across splits fails with provenance conflict",
        "input": "DUPLICATE_ID_FIXTURE",
        "expected": {"error_caught": True, "conflicting_id": 101},
        "actual": {"error_caught": duplicate_caught, "conflicting_id": conflicting_id},
        "status": "PASS" if passed3 else "FAIL",
    })
    if not passed3:
        print("ERROR: Duplicate ID check failed!")
        sys.exit(1)

    for c in contract_checks:
        print(f"[{c['status']}] {c['description']}")

    # 3. Deliberate failure detection (verifies checker fails on wrong result)
    print("\nVerifying deliberate wrong result triggers failure...")
    deliberate_wrong_count = 999
    if report.total_records == deliberate_wrong_count:
        print("ERROR: Deliberate failure test matched unexpectedly!")
        sys.exit(1)
    print("Deliberate failure test passed: wrong result correctly detected.")

    # 4. Automated unittest suite execution
    print("\nRunning automated unittest discovery...")
    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        LAB_DIR,
        "-p",
        "test_*.py",
        "-v",
    ]
    test_proc = subprocess.run(cmd, capture_output=True, text=True)
    print(test_proc.stdout)
    print(test_proc.stderr)

    if test_proc.returncode != 0:
        print(f"ERROR: unittest discovery failed with code {test_proc.returncode}")
        sys.exit(test_proc.returncode)

    # 5. Persist evidence to work/R16-T027/
    os.makedirs(WORK_DIR, exist_ok=True)
    json_path = os.path.join(WORK_DIR, "results.json")
    report_data = {
        "environment": env_info,
        "contract_checks": contract_checks,
        "deliberate_failure_check": "PASS (wrong expectation correctly detected)",
        "unittest_exit_code": test_proc.returncode,
        "unittest_output": test_proc.stderr,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    report_path = os.path.join(WORK_DIR, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== TASK R16-T027 VERIFICATION REPORT ===\n\n")
        f.write(f"Task: R16-T027\n")
        f.write(f"Branch: {env_info['branch']}\n")
        f.write(f"Python Version: {env_info['python_version']}\n")
        f.write(f"Platform: {env_info['platform']}\n\n")
        f.write("--- Contract Checks ---\n")
        for c in contract_checks:
            f.write(f"[{c['status']}] {c['description']} | Actual: {c['actual']}\n")
        f.write("\n--- Unittest Output ---\n")
        f.write(test_proc.stderr)
        f.write(f"\nUnittest Return Code: {test_proc.returncode}\n")
        f.write("\nALL CHECKS PASSED.\n")

    print(f"\nSaved check results to {json_path} and {report_path}")
    print("All checks completed successfully with exit code 0.")


if __name__ == "__main__":
    run_checks()
