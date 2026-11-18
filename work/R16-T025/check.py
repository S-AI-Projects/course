#!/usr/bin/env python3
"""
Verification check script for R16-T025.
Verifies contract assertions, checks the decision table, confirms deliberate
failure detection, records tool versions, and saves inputs/outputs into work/R16-T025/.
Exits non-zero if any assertion or test fails.
"""

import json
import os
import platform
import subprocess
import sys

# Ensure lab directory is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LAB_DIR = os.path.join(REPO_ROOT, "chapters/en/chapter9/applied-labs/r16-t025")
WORK_DIR = os.path.join(REPO_ROOT, "work/R16-T025")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    PUBLISHED_DECISION_TABLE,
    DecisionType,
    LocalDeterministicHubAdapter,
    ScenarioRecord,
    check_decision_table,
)


def run_checks() -> None:
    print("=== Running Checks for Task R16-T025 ===")

    # 1. Environment & tool versions
    env_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "task_id": "R16-T025",
        "branch": "student/e26b07f0747/R16-T025",
    }
    print(f"Python Version: {env_info['python_version']}")
    print(f"Platform: {env_info['platform']}")

    adapter = LocalDeterministicHubAdapter()
    contract_checks = []

    # Check 1: Normal scenario
    normal_s = PUBLISHED_DECISION_TABLE[0]
    dec1, pref1, rat1 = adapter.evaluate(normal_s.facts)
    passed1 = (
        dec1 == DecisionType.LOAD_HUB_MODEL
        and pref1 == "huggingface/EleutherAI/gpt-j-6B"
    )
    contract_checks.append({
        "description": "Normal scenario: high-RAM model GPT-J-6B routes to LOAD_HUB_MODEL",
        "input": normal_s.facts,
        "expected": {"decision": DecisionType.LOAD_HUB_MODEL.value, "prefix": "huggingface/EleutherAI/gpt-j-6B"},
        "actual": {"decision": dec1.value, "prefix": pref1},
        "status": "PASS" if passed1 else "FAIL",
    })
    if not passed1:
        print("ERROR: Normal scenario check failed!")
        sys.exit(1)

    # Check 2: Boundary scenario
    boundary_s = PUBLISHED_DECISION_TABLE[1]
    dec2, pref2, rat2 = adapter.evaluate(boundary_s.facts)
    passed2 = (
        dec2 == DecisionType.LOAD_SPACES_APP
        and pref2 == "spaces/abidlabs/remove-bg"
    )
    contract_checks.append({
        "description": "Boundary scenario: Spaces demo remove-bg routes to LOAD_SPACES_APP",
        "input": boundary_s.facts,
        "expected": {"decision": DecisionType.LOAD_SPACES_APP.value, "prefix": "spaces/abidlabs/remove-bg"},
        "actual": {"decision": dec2.value, "prefix": pref2},
        "status": "PASS" if passed2 else "FAIL",
    })
    if not passed2:
        print("ERROR: Boundary scenario check failed!")
        sys.exit(1)

    # Check 3: Missing-information scenario
    missing_s = PUBLISHED_DECISION_TABLE[2]
    dec3, pref3, rat3 = adapter.evaluate(missing_s.facts)
    passed3 = (
        dec3 == DecisionType.REJECT_INSUFFICIENT_INFORMATION
        and pref3 is None
    )
    contract_checks.append({
        "description": "Missing-information scenario: unspecified artifact type rejected before dispatch",
        "input": missing_s.facts,
        "expected": {"decision": DecisionType.REJECT_INSUFFICIENT_INFORMATION.value, "prefix": None},
        "actual": {"decision": dec3.value, "prefix": pref3},
        "status": "PASS" if passed3 else "FAIL",
    })
    if not passed3:
        print("ERROR: Missing-information scenario check failed!")
        sys.exit(1)

    # Check 4: Published decision table validation via checker
    checker_report = check_decision_table(adapter, PUBLISHED_DECISION_TABLE)
    passed4 = checker_report.get("status") == "ALL_PASSED"
    contract_checks.append({
        "description": "Decision table checker validates published decision table",
        "input": "PUBLISHED_DECISION_TABLE",
        "expected": "ALL_PASSED",
        "actual": checker_report.get("status"),
        "status": "PASS" if passed4 else "FAIL",
    })
    if not passed4:
        print("ERROR: Checker verification failed!")
        sys.exit(1)

    for c in contract_checks:
        print(f"[{c['status']}] {c['description']}")

    # 3. Deliberate failure detection (Requirement: checker must fail when a decision is deliberately changed)
    print("\nVerifying deliberate decision change triggers checker failure...")
    tampered_record = [
        ScenarioRecord(
            name="tampered_normal",
            facts=normal_s.facts,
            expected_decision=DecisionType.LOAD_SPACES_APP,  # DELIBERATE WRONG DECISION
            expected_prefix="spaces/EleutherAI/gpt-j-6B",
            rationale="Wrong decision",
        )
    ]
    tamper_failed_as_expected = False
    try:
        check_decision_table(adapter, tampered_record)
    except AssertionError:
        tamper_failed_as_expected = True

    if not tamper_failed_as_expected:
        print("ERROR: Checker unexpectedly succeeded on tampered decision!")
        sys.exit(1)
    print("Deliberate failure test passed: checker correctly failed on mutated decision.")

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

    # 5. Persist evidence to work/R16-T025/
    os.makedirs(WORK_DIR, exist_ok=True)
    json_path = os.path.join(WORK_DIR, "results.json")
    report_data = {
        "environment": env_info,
        "contract_checks": contract_checks,
        "unestablished_real_service_behaviors": LocalDeterministicHubAdapter.UNESTABLISHED_BEHAVIORS,
        "deliberate_failure_check": "PASS (checker correctly rejected tampered decision)",
        "unittest_exit_code": test_proc.returncode,
        "unittest_output": test_proc.stderr,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    report_path = os.path.join(WORK_DIR, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== TASK R16-T025 VERIFICATION REPORT ===\n\n")
        f.write(f"Task: R16-T025\n")
        f.write(f"Branch: {env_info['branch']}\n")
        f.write(f"Python Version: {env_info['python_version']}\n")
        f.write(f"Platform: {env_info['platform']}\n\n")
        f.write("--- Contract Checks ---\n")
        for c in contract_checks:
            f.write(f"[{c['status']}] {c['description']} | Actual: {c['actual']}\n")
        f.write("\n--- Unestablished Real-Service Behaviors ---\n")
        for i, b in enumerate(LocalDeterministicHubAdapter.UNESTABLISHED_BEHAVIORS, 1):
            f.write(f"{i}. {b}\n")
        f.write("\n--- Unittest Output ---\n")
        f.write(test_proc.stderr)
        f.write(f"\nUnittest Return Code: {test_proc.returncode}\n")
        f.write("\nALL CHECKS PASSED.\n")

    print(f"\nSaved check results to {json_path} and {report_path}")
    print("All checks completed successfully with exit code 0.")


if __name__ == "__main__":
    run_checks()
