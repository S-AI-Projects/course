#!/usr/bin/env python3
"""Validation and verification check script for Task R16-T013.

Validates the security scenario rubric, executes unit tests,
compares direct vs reference evaluation approaches, demonstrates failure on wrong results,
and records all outputs and tool versions in work/R16-T013/.
"""

import copy
import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T013")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter1", "applied-labs", "r16-t013")

sys.path.insert(0, LAB_DIR)
from example import (
    REFERENCE_RESULTS,
    SCENARIOS,
    check_control_relevance,
    check_scenario_completeness,
    compare_both_approaches,
    evaluate_direct,
    evaluate_reference,
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
        f"Assignment: R16-T013\n"
        f"Student: Janhavi Sharma\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Check Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t013 -p 'test_*.py'\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(versions_content)
    return versions_content


def evaluate_and_compare_scenarios():
    """Evaluate scenarios using both direct and reference approaches and compare results."""
    all_agreed, comparison_audit = compare_both_approaches(SCENARIOS)

    comparison_lines = [
        "Assignment: R16-T013",
        "Comparison: Direct Implementation vs Independent Reference Table",
        "=" * 70,
    ]

    all_passed = all_agreed

    for item in comparison_audit:
        status = "AGREED" if item["agreed"] else "DISAGREED"
        comparison_lines.append(f"\nScenario: {item['id']} ({item['name']})")
        comparison_lines.append(f"Direct Approach:    Completeness={item['direct'][0]}, Control={item['direct'][1]}")
        comparison_lines.append(f"Reference Approach: Completeness={item['reference'][0]}, Control={item['reference'][1]}")
        comparison_lines.append(f"Status: {status}")

    # Specific scenario assertions
    scen_1_res = evaluate_direct(SCENARIOS[0])
    scen_2_res = evaluate_direct(SCENARIOS[1])
    scen_3_res = evaluate_direct(SCENARIOS[2])

    if scen_1_res != ("PASS", "MATCH"):
        comparison_lines.append("Assertion Failure: Scenario 1 did not evaluate to ('PASS', 'MATCH')")
        all_passed = False

    if scen_2_res != ("FAIL", "MATCH"):
        comparison_lines.append("Assertion Failure: Scenario 2 did not evaluate to ('FAIL', 'MATCH')")
        all_passed = False

    if scen_3_res != ("PASS", "REVIEW"):
        comparison_lines.append("Assertion Failure: Scenario 3 did not evaluate to ('PASS', 'REVIEW')")
        all_passed = False

    # Deliberate wrong result demonstration
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")

    corrupted_scenarios = copy.deepcopy(SCENARIOS)
    corrupted_scenarios[0]["control"] = "completely irrelevant control action"
    corrupted_agreed, corrupted_audit = compare_both_approaches(corrupted_scenarios)

    if not corrupted_agreed and not corrupted_audit[0]["agreed"]:
        comparison_lines.append(
            f"Deliberate divergence on scenario {corrupted_audit[0]['id']} "
            f"(direct {corrupted_audit[0]['direct']} vs reference {corrupted_audit[0]['reference']}) "
            f"correctly detected: PASS (discrepancy caught)"
        )
    else:
        comparison_lines.append("Deliberate divergence test failed: FAIL")
        all_passed = False

    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append(f"Final Validation Status: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w") as f:
        f.write("\n".join(comparison_lines) + "\n")

    return all_passed, "\n".join(comparison_lines)


def main():
    print("Starting verification checks for R16-T013...")
    os.makedirs(WORK_DIR, exist_ok=True)

    versions = collect_tool_versions()
    print("Collected tool versions.")

    unit_ok, unit_log = run_unit_tests()
    if not unit_ok:
        print("ERROR: Unit tests failed!\n", unit_log, file=sys.stderr)
        sys.exit(1)
    print("Automated unit tests passed.")

    eval_ok, eval_summary = evaluate_and_compare_scenarios()
    if not eval_ok:
        print("ERROR: Approach comparison failed!\n", eval_summary, file=sys.stderr)
        sys.exit(1)
    print("All scenarios and approach comparisons verified successfully.")

    print("\nAll checks passed cleanly! Results saved in work/R16-T013/")
    sys.exit(0)


if __name__ == "__main__":
    main()
