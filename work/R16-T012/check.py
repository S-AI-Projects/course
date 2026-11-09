#!/usr/bin/env python3
"""Validation and verification check script for Task R16-T012.

Validates the worked decision example for Chapter 2, executes unit tests,
compares expected vs actual decisions, verifies that deliberate wrong decisions fail,
and records all outputs and tool versions in work/R16-T012/.
"""

import copy
import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T012")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter2", "applied-labs", "r16-t012")

sys.path.insert(0, LAB_DIR)
from example import (
    PAD_AND_MASK,
    REJECT_EXCEEDS_MAX_LENGTH,
    REJECT_MISSING_INPUT,
    REJECT_UNBATCHED,
    SCENARIOS,
    VALID_DIRECT_INFERENCE,
    check_decision_table,
    evaluate_scenario,
)


def run_unit_tests():
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
    with open(os.path.join(WORK_DIR, "test-results.txt"), "w") as f:
        f.write(test_log)
    return proc.returncode == 0, test_log


def collect_tool_versions():
    """Collect platform, Python, Git, and branch information."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T012\n"
        f"Student: Janhavi Sharma\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Check Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t012 -p 'test_*.py'\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(versions_content)
    return versions_content


def evaluate_decision_table():
    """Evaluate all scenarios in the published decision table."""
    passed, results = check_decision_table(SCENARIOS)

    comparison_lines = [
        "Assignment: R16-T012",
        "Comparison: Expected vs Actual Decisions (Published Table)",
        "=" * 60,
    ]

    all_passed = passed

    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        comparison_lines.append(f"\nScenario: {item['id']} ({item['name']})")
        comparison_lines.append(f"Expected Decision: {item['expected']}")
        comparison_lines.append(f"Actual Decision:   {item['actual']}")
        comparison_lines.append(f"Status: {status}")
        comparison_lines.append(f"Rationale: {item['rationale']}")

    # Deliberate wrong decision test demonstration
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")

    corrupted_scenarios = copy.deepcopy(SCENARIOS)
    corrupted_scenarios[0]["expected_decision"] = VALID_DIRECT_INFERENCE
    corrupted_passed, corrupted_results = check_decision_table(corrupted_scenarios)

    if not corrupted_passed and not corrupted_results[0]["passed"]:
        comparison_lines.append(
            f"Deliberate wrong decision on scenario {corrupted_results[0]['id']} "
            f"(expected {VALID_DIRECT_INFERENCE} vs actual {corrupted_results[0]['actual']}) "
            f"correctly triggers failure: PASS (mismatch detected)"
        )
    else:
        comparison_lines.append("Deliberate wrong decision failed to trigger failure: FAIL")
        all_passed = False

    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append(f"Final Validation Status: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w") as f:
        f.write("\n".join(comparison_lines) + "\n")

    return all_passed, "\n".join(comparison_lines)


def main():
    print("Starting verification checks for R16-T012...")
    os.makedirs(WORK_DIR, exist_ok=True)

    versions = collect_tool_versions()
    print("Collected tool versions.")

    unit_ok, unit_log = run_unit_tests()
    if not unit_ok:
        print("ERROR: Unit tests failed!\n", unit_log, file=sys.stderr)
        sys.exit(1)
    print("Automated unit tests passed.")

    eval_ok, eval_summary = evaluate_decision_table()
    if not eval_ok:
        print("ERROR: Decision table evaluations failed!\n", eval_summary, file=sys.stderr)
        sys.exit(1)
    print("All decision table scenarios verified successfully.")

    print("\nAll checks passed cleanly! Results saved in work/R16-T012/")
    sys.exit(0)


if __name__ == "__main__":
    main()
