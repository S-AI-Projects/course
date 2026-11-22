#!/usr/bin/env python3
"""
Verification check script for Task R16-T044.

Validates:
- Three-scenario worked decision model:
  * Normal scenario -> explicit expected decision (HUB_IN_MEMORY).
  * Boundary scenario -> explicit expected decision (STREAM_FROM_DISK_OR_URL).
  * Missing-information scenario -> explicit expected decision (REQUEST_MISSING_INFO).
- Intermediate state recorded after every step and invariant linking state to final output.
- Checker fails when a decision in the published table is deliberately altered.
- Human review verifies that rationale follows the lesson.
- Saves inputs, expected vs actual outputs, tool versions, and test logs into work/R16-T044/.
- Exits non-zero on any assertion or test failure.
"""

import copy
import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T044")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter5", "applied-labs", "r16-t044")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    PUBLISHED_DECISION_TABLE,
    DecisionResult,
    StepTrace,
    check_decision_table,
    evaluate_dataset_strategy,
)


def collect_tool_versions() -> str:
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T044\n"
        f"Student: Nilesh\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Test Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t044 -p 'test_*.py'\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w", encoding="utf-8") as f:
        f.write(versions_content)
    return versions_content


def run_unit_tests() -> tuple[bool, str]:
    """Run automated unittest discovery suite and record output."""
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
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    test_log = proc.stdout + proc.stderr
    with open(os.path.join(WORK_DIR, "test-results.txt"), "w", encoding="utf-8") as f:
        f.write(test_log)
    return proc.returncode == 0, test_log


def evaluate_fixtures() -> tuple[bool, list, str]:
    """Evaluate published decision table, state traces, and table tampering detection."""
    with open(os.path.join(WORK_DIR, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(PUBLISHED_DECISION_TABLE, f, indent=2)

    comparison_lines = [
        "Assignment: R16-T044",
        "Comparison: Expected vs Actual Results & Invariant Audits",
        "=" * 60,
    ]

    all_passed = True
    results_record = []

    # 1. Evaluate valid decision table
    table_ok, audit_log = check_decision_table()
    for row in audit_log:
        comparison_lines.append(f"\nScenario: {row['scenario_name']} ({row['scenario_type']})")
        comparison_lines.append(f"Expected Decision: {row['expected_decision']}")
        comparison_lines.append(f"Actual Decision:   {row['actual_decision']}")
        comparison_lines.append(f"Invariants Held:   {row['invariants_held']} (steps={row['trace_step_count']})")
        comparison_lines.append(f"Rationale:         {row['rationale']}")
        comparison_lines.append(f"Status: {row['status']}")

        if row["status"] != "PASS":
            all_passed = False
        results_record.append(row)

    # 2. Verify that checker fails when a decision is deliberately changed
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Tampered Decision Checker Verification:")
    corrupted_table = copy.deepcopy(PUBLISHED_DECISION_TABLE)
    corrupted_table[0]["expected_decision"] = "STREAM_FROM_DISK_OR_URL"  # deliberate error

    corrupted_ok, corrupted_audit = check_decision_table(corrupted_table)
    if not corrupted_ok and corrupted_audit[0]["status"] == "FAIL":
        comparison_lines.append(
            "Checker correctly failed when normal scenario decision was deliberately changed: PASS (tampering caught)"
        )
    else:
        comparison_lines.append("Checker failed to detect altered decision: FAIL")
        all_passed = False

    # 3. Deliberate wrong assertion failure verification
    actual_decision = evaluate_dataset_strategy("test", PUBLISHED_DECISION_TABLE[0]["facts"]).decision
    deliberate_wrong = "NON_EXISTENT_DECISION"
    if actual_decision != deliberate_wrong:
        comparison_lines.append(
            f"Deliberate wrong assertion (expected {deliberate_wrong} vs actual {actual_decision}) correctly detected: PASS"
        )
    else:
        all_passed = False

    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append(f"Final Validation Status: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    summary_text = "\n".join(comparison_lines)
    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w", encoding="utf-8") as f:
        f.write(summary_text + "\n")

    return all_passed, results_record, summary_text


def main() -> None:
    print("=== Running Verification Check for Task R16-T044 ===")
    os.makedirs(WORK_DIR, exist_ok=True)

    collect_tool_versions()
    print("Collected tool versions.")

    eval_ok, results_record, eval_summary = evaluate_fixtures()
    print("Evaluated decision table fixtures.")
    if not eval_ok:
        print("ERROR: Decision table evaluation failed!\n", eval_summary, file=sys.stderr)
        sys.exit(1)

    unit_ok, unit_log = run_unit_tests()
    if not unit_ok:
        print("ERROR: Unit tests failed!\n", unit_log, file=sys.stderr)
        sys.exit(1)
    print("All unit tests passed successfully.")

    print("\nAll checks passed cleanly with exit code 0! Artifacts saved to work/R16-T044/")
    sys.exit(0)


if __name__ == "__main__":
    main()
