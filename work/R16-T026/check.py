#!/usr/bin/env python3
"""
Verification check script for R16-T026.
Verifies contract assertions, checks baseline vs. refactored equivalence,
confirms deliberate failure detection, records tool versions, and saves inputs/outputs
into work/R16-T026/. Exits non-zero if any assertion or test fails.
"""

import json
import os
import platform
import subprocess
import sys

# Ensure lab directory is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LAB_DIR = os.path.join(REPO_ROOT, "chapters/en/chapter6/applied-labs/r16-t026")
WORK_DIR = os.path.join(REPO_ROOT, "work/R16-T026")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    WhitespaceSpanScanner,
    baseline_tokenize_with_offsets,
    prove_equivalence,
    recover_words_from_slices,
    refactored_tokenize_with_offsets,
)


def run_checks() -> None:
    print("=== Running Checks for Task R16-T026 ===")

    # 1. Environment & tool versions
    env_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "task_id": "R16-T026",
        "branch": "student/e26b07f0747/R16-T026",
    }
    print(f"Python Version: {env_info['python_version']}")
    print(f"Platform: {env_info['platform']}")

    fixture = "  red   apple "
    expected_output = [("red", (2, 5)), ("apple", (8, 13))]
    contract_checks = []

    # Check 1: Refactored output matches contract
    refactored_result = refactored_tokenize_with_offsets(fixture)
    passed1 = refactored_result == expected_output
    contract_checks.append({
        "description": "Refactored tokenizer produces expected tokens and spans for '  red   apple '",
        "input": fixture,
        "expected": expected_output,
        "actual": refactored_result,
        "status": "PASS" if passed1 else "FAIL",
    })
    if not passed1:
        print("ERROR: Refactored output check failed!")
        sys.exit(1)

    # Check 2: Slice recovery invariant
    slice_red = fixture[2:5]
    slice_apple = fixture[8:13]
    recovered = recover_words_from_slices(fixture, refactored_result)
    passed2 = (slice_red == "red") and (slice_apple == "apple") and (recovered == ["red", "apple"])
    contract_checks.append({
        "description": "Slice recovery invariant: fixture[2:5] == 'red' and fixture[8:13] == 'apple'",
        "input": {"slice_red": "fixture[2:5]", "slice_apple": "fixture[8:13]"},
        "expected": {"slice_red": "red", "slice_apple": "apple"},
        "actual": {"slice_red": slice_red, "slice_apple": slice_apple},
        "status": "PASS" if passed2 else "FAIL",
    })
    if not passed2:
        print("ERROR: Slice recovery check failed!")
        sys.exit(1)

    # Check 3: Extracted WhitespaceSpanScanner responsibility
    scanned_spans = WhitespaceSpanScanner.scan_spans(fixture)
    passed3 = scanned_spans == [(2, 5), (8, 13)]
    contract_checks.append({
        "description": "Extracted WhitespaceSpanScanner correctly detects spans [(2, 5), (8, 13)]",
        "input": fixture,
        "expected": [(2, 5), (8, 13)],
        "actual": scanned_spans,
        "status": "PASS" if passed3 else "FAIL",
    })
    if not passed3:
        print("ERROR: Scanner check failed!")
        sys.exit(1)

    # Check 4: Baseline vs Refactored equivalence
    baseline_result = baseline_tokenize_with_offsets(fixture)
    is_equiv = prove_equivalence(fixture) and (baseline_result == refactored_result)
    contract_checks.append({
        "description": "Baseline and refactored implementations produce identical outputs",
        "input": fixture,
        "expected": True,
        "actual": is_equiv,
        "status": "PASS" if is_equiv else "FAIL",
    })
    if not is_equiv:
        print("ERROR: Baseline vs refactored equivalence check failed!")
        sys.exit(1)

    for c in contract_checks:
        print(f"[{c['status']}] {c['description']}")

    # 3. Deliberate failure detection
    print("\nVerifying deliberate wrong result triggers failure...")
    deliberate_wrong = [("red", (0, 3)), ("apple", (5, 10))]
    if refactored_result == deliberate_wrong:
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

    # 5. Persist evidence to work/R16-T026/
    os.makedirs(WORK_DIR, exist_ok=True)
    json_path = os.path.join(WORK_DIR, "results.json")
    report_data = {
        "environment": env_info,
        "contract_checks": contract_checks,
        "deliberate_failure_check": "PASS (wrong expected offsets correctly failed match)",
        "unittest_exit_code": test_proc.returncode,
        "unittest_output": test_proc.stderr,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    report_path = os.path.join(WORK_DIR, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== TASK R16-T026 VERIFICATION REPORT ===\n\n")
        f.write(f"Task: R16-T026\n")
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
