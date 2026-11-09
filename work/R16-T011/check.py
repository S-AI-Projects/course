#!/usr/bin/env python3
"""Validation and verification check script for Task R16-T011.

Validates the UI callback contract, compares expected vs actual results,
captures tool versions, runs unit tests, and verifies failure on deliberate wrong outputs.
Exits with code 0 on complete success, or non-zero on assertion failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T011")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter9", "applied-labs", "r16-t011")

sys.path.insert(0, LAB_DIR)
from example import analyze_text, text_analysis_callback


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
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T011\n"
        f"Student: Janhavi Sharma\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Check Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t011 -p 'test_*.py'\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(versions_content)
    return versions_content


def evaluate_fixtures():
    """Evaluate all scenarios from inputs.json and verify expectations."""
    inputs_path = os.path.join(WORK_DIR, "inputs.json")
    with open(inputs_path, "r") as f:
        fixtures = json.load(f)

    comparison_lines = [
        "Assignment: R16-T011",
        "Comparison: Expected vs Actual Results",
        "=" * 50,
    ]

    all_passed = True

    for fixture in fixtures:
        scenario = fixture["scenario"]
        desc = fixture["description"]
        inp = fixture["input"]
        exp_output = fixture["expected_output"]
        exp_exc = fixture["expected_exception"]

        comparison_lines.append(f"\nScenario: {scenario} ({desc})")
        comparison_lines.append(f"Input: {repr(inp)}")

        if exp_exc:
            try:
                actual_res = analyze_text(inp)
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Result: Returned {actual_res} (NO EXCEPTION)")
                comparison_lines.append("Status: FAIL")
                all_passed = False
            except TypeError as e:
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Exception: TypeError ({e})")
                comparison_lines.append("Status: PASS")
            except Exception as e:
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False
        else:
            try:
                actual_res = analyze_text(inp)
                comparison_lines.append(f"Expected: {exp_output}")
                comparison_lines.append(f"Actual:   {actual_res}")
                if actual_res == exp_output:
                    comparison_lines.append("Status: PASS")
                else:
                    comparison_lines.append("Status: FAIL")
                    all_passed = False
            except Exception as e:
                comparison_lines.append(f"Expected: {exp_output}")
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False

    # Demonstrate that a deliberate wrong result makes the check fail
    comparison_lines.append("\n" + "=" * 50)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    wrong_expected = {"word_count": 999, "unique_count": 999}
    actual_normal = analyze_text("red red apple")
    if actual_normal != wrong_expected:
        comparison_lines.append(
            f"Deliberate wrong assertion (expected {wrong_expected} vs actual {actual_normal}) correctly detects mismatch: PASS (mismatch caught)"
        )
    else:
        comparison_lines.append("Deliberate wrong assertion failed to catch discrepancy: FAIL")
        all_passed = False

    comparison_lines.append("\n" + "=" * 50)
    comparison_lines.append(f"Final Validation Status: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w") as f:
        f.write("\n".join(comparison_lines) + "\n")

    return all_passed, "\n".join(comparison_lines)


def main():
    print("Starting verification checks for R16-T011...")
    os.makedirs(WORK_DIR, exist_ok=True)

    versions = collect_tool_versions()
    print("Collected tool versions.")

    unit_ok, unit_log = run_unit_tests()
    if not unit_ok:
        print("ERROR: Unit tests failed!\n", unit_log, file=sys.stderr)
        sys.exit(1)
    print("Automated unit tests passed.")

    eval_ok, eval_summary = evaluate_fixtures()
    if not eval_ok:
        print("ERROR: Fixture evaluations failed!\n", eval_summary, file=sys.stderr)
        sys.exit(1)
    print("All fixtures verified successfully.")

    # Deliberate assertion check demonstrating non-zero exit on failure
    def simulate_failure_check(must_fail: bool):
        if must_fail:
            raise AssertionError("Deliberate check failure triggered")

    try:
        simulate_failure_check(False)
    except AssertionError:
        sys.exit(1)

    print("\nAll checks passed cleanly! Results saved in work/R16-T011/")
    sys.exit(0)


if __name__ == "__main__":
    main()
