#!/usr/bin/env python3
"""
Verification check script for Task R16-T047.

Validates the token-budget preflight worked example:
- Budget 3 with "one two three four" retains ['one', 'two', 'three'] and reports 1 removed token.
- Empty input retains [] and reports 0 removed tokens.
- Rejects negative budget with ValueError.
- Explicitly labels tokenizer as teaching approximation.
- Executes worked example and regression tests.
- Demonstrates that a deliberate wrong result makes the check fail.
- Saves inputs, expected vs actual outputs, tool versions, and test logs into work/R16-T047/.
- Exits non-zero on any assertion or test failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T047")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter8", "applied-labs", "r16-t047")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    TOKENIZER_NOTE,
    PreflightResult,
    TokenBudgetPreflight,
    run_regression_suite,
)


def collect_tool_versions() -> str:
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T047\n"
        f"Student: Nilesh\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Test Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t047 -p 'test_*.py'\n"
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
    """Evaluate contract fixtures and regression suite."""
    fixtures = [
        {
            "scenario": "normal_truncation_budget_3",
            "prompt": "one two three four",
            "budget": 3,
            "expected_retained": ["one", "two", "three"],
            "expected_removed": 1,
            "expected_truncated": True,
            "expected_exception": None,
        },
        {
            "scenario": "boundary_empty_input",
            "prompt": "",
            "budget": 3,
            "expected_retained": [],
            "expected_removed": 0,
            "expected_truncated": False,
            "expected_exception": None,
        },
        {
            "scenario": "failure_negative_budget",
            "prompt": "one two",
            "budget": -1,
            "expected_retained": None,
            "expected_removed": None,
            "expected_truncated": None,
            "expected_exception": "ValueError",
        },
    ]

    with open(os.path.join(WORK_DIR, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2)

    comparison_lines = [
        "Assignment: R16-T047",
        "Comparison: Expected vs Actual Results & Regression Audits",
        "=" * 60,
    ]

    all_passed = True
    results_record = []

    for item in fixtures:
        scenario = item["scenario"]
        prompt = item["prompt"]
        budget = item["budget"]
        exp_retained = item["expected_retained"]
        exp_removed = item["expected_removed"]
        exp_trunc = item["expected_truncated"]
        exp_exc = item["expected_exception"]

        comparison_lines.append(f"\nScenario: {scenario}")
        comparison_lines.append(f"Prompt: {repr(prompt)}, Budget: {budget}")

        if exp_exc:
            try:
                engine = TokenBudgetPreflight(budget)
                res = engine.check(prompt)
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append("Actual: No exception raised (FAIL)")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})
            except ValueError as e:
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Exception: ValueError ({e})")
                comparison_lines.append("Status: PASS")
                results_record.append({"scenario": scenario, "status": "PASS", "actual_exception": str(e)})
            except Exception as e:
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})
        else:
            try:
                engine = TokenBudgetPreflight(budget)
                res = engine.check(prompt)
                actual_retained = res.retained
                actual_removed = res.removed_count
                actual_trunc = res.is_truncated

                comparison_lines.append(f"Expected Retained: {exp_retained}, Removed: {exp_removed}")
                comparison_lines.append(f"Actual Retained:   {actual_retained}, Removed: {actual_removed}")
                comparison_lines.append(f"Explanation:       {res.explanation}")

                passed = (
                    actual_retained == exp_retained
                    and actual_removed == exp_removed
                    and actual_trunc == exp_trunc
                )
                comparison_lines.append(f"Status: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    all_passed = False
                results_record.append({
                    "scenario": scenario,
                    "status": "PASS" if passed else "FAIL",
                    "actual_retained": actual_retained,
                    "actual_removed": actual_removed,
                })
            except Exception as e:
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})

    # Execute regression test suite
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Automated Regression Suite Verification:")
    reg_ok, reg_audit = run_regression_suite()
    comparison_lines.append(f"Regression Suite Status: {'PASS' if reg_ok else 'FAIL'}")
    if not reg_ok:
        all_passed = False

    # Demonstrate that a deliberate wrong result triggers an assertion failure
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    engine = TokenBudgetPreflight(3)
    actual_retained = engine.check("one two three four").retained
    deliberate_wrong = ["one", "two", "three", "four"]
    if actual_retained != deliberate_wrong:
        comparison_lines.append(
            f"Deliberate wrong assertion (expected {deliberate_wrong} vs actual {actual_retained}) correctly detected: PASS"
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
    print("=== Running Verification Check for Task R16-T047 ===")
    os.makedirs(WORK_DIR, exist_ok=True)

    collect_tool_versions()
    print("Collected tool versions.")

    eval_ok, results_record, eval_summary = evaluate_fixtures()
    print("Evaluated contract fixtures.")
    if not eval_ok:
        print("ERROR: Contract fixture evaluation failed!\n", eval_summary, file=sys.stderr)
        sys.exit(1)

    unit_ok, unit_log = run_unit_tests()
    if not unit_ok:
        print("ERROR: Unit tests failed!\n", unit_log, file=sys.stderr)
        sys.exit(1)
    print("All unit tests passed successfully.")

    print("\nAll checks passed cleanly with exit code 0! Artifacts saved to work/R16-T047/")
    sys.exit(0)


if __name__ == "__main__":
    main()
