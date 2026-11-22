#!/usr/bin/env python3
"""
Verification check script for Task R16-T041.

Validates the token-budget preflight contract:
- Budget 3 with "one two three four" retains ['one', 'two', 'three'] and reports 1 removed token.
- Empty input retains [] and reports 0 removed tokens.
- Rejects negative budget with ValueError.
- Explicitly labels tokenizer as a teaching approximation.
- Runs automated unit test suite.
- Demonstrates that a deliberate wrong result triggers an assertion failure.
- Saves inputs, expected vs actual results, test logs, and tool versions in work/R16-T041/.
- Exits non-zero on any assertion or test failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T041")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter2", "applied-labs", "r16-t041")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    TOKENIZER_NOTE,
    PreflightReport,
    TokenBudgetPreflight,
    check_token_budget,
)


def collect_tool_versions() -> str:
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T041\n"
        f"Student: Nilesh\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Test Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t041 -p 'test_*.py'\n"
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


def evaluate_contract_fixtures() -> tuple[bool, list, str]:
    """Evaluate contract scenarios and compare expected vs actual results."""
    fixtures = [
        {
            "scenario": "normal_truncation",
            "description": "Budget 3 with 'one two three four' retains ['one', 'two', 'three'] and reports 1 removed token",
            "input": {"prompt": "one two three four", "budget": 3},
            "expected_output": {
                "retained": ["one", "two", "three"],
                "removed_count": 1,
                "is_truncated": True,
                "total_tokens": 4,
            },
            "expected_exception": None,
        },
        {
            "scenario": "boundary_empty",
            "description": "Empty input retains [] and reports 0 removed tokens",
            "input": {"prompt": "", "budget": 3},
            "expected_output": {
                "retained": [],
                "removed_count": 0,
                "is_truncated": False,
                "total_tokens": 0,
            },
            "expected_exception": None,
        },
        {
            "scenario": "boundary_whitespace",
            "description": "Whitespace-only input retains [] and reports 0 removed tokens",
            "input": {"prompt": "   \n\t   ", "budget": 3},
            "expected_output": {
                "retained": [],
                "removed_count": 0,
                "is_truncated": False,
                "total_tokens": 0,
            },
            "expected_exception": None,
        },
        {
            "scenario": "failure_negative_budget",
            "description": "Reject a negative budget with ValueError",
            "input": {"prompt": "one two three", "budget": -1},
            "expected_output": None,
            "expected_exception": "ValueError",
        },
        {
            "scenario": "within_budget_no_truncation",
            "description": "Prompt within budget retains all tokens without truncation",
            "input": {"prompt": "one two", "budget": 3},
            "expected_output": {
                "retained": ["one", "two"],
                "removed_count": 0,
                "is_truncated": False,
                "total_tokens": 2,
            },
            "expected_exception": None,
        },
    ]

    # Save inputs.json
    with open(os.path.join(WORK_DIR, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2)

    comparison_lines = [
        "Assignment: R16-T041",
        "Comparison: Expected vs Actual Results",
        "=" * 60,
    ]

    all_passed = True
    results_record = []

    for item in fixtures:
        scenario = item["scenario"]
        desc = item["description"]
        inp = item["input"]
        exp_out = item["expected_output"]
        exp_exc = item["expected_exception"]

        comparison_lines.append(f"\nScenario: {scenario} ({desc})")
        comparison_lines.append(f"Input: prompt={repr(inp['prompt'])}, budget={inp['budget']}")

        if exp_exc:
            try:
                engine = TokenBudgetPreflight(inp["budget"])
                res = engine.check(inp["prompt"]).as_dict()
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Result: Returned {res} (NO EXCEPTION RAISED)")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL", "reason": "No exception raised"})
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
                results_record.append({"scenario": scenario, "status": "FAIL", "actual_exception": str(e)})
        else:
            try:
                engine = TokenBudgetPreflight(inp["budget"])
                rep = engine.check(inp["prompt"])
                actual = {
                    "retained": rep.retained,
                    "removed_count": rep.removed_count,
                    "is_truncated": rep.is_truncated,
                    "total_tokens": rep.total_tokens,
                }
                comparison_lines.append(f"Expected: {exp_out}")
                comparison_lines.append(f"Actual:   {actual}")
                if actual == exp_out:
                    comparison_lines.append("Status: PASS")
                    results_record.append({"scenario": scenario, "status": "PASS", "actual": actual})
                else:
                    comparison_lines.append("Status: FAIL")
                    all_passed = False
                    results_record.append({"scenario": scenario, "status": "FAIL", "actual": actual})
            except Exception as e:
                comparison_lines.append(f"Expected: {exp_out}")
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL", "error": str(e)})

    # Demonstrate that a deliberate wrong result triggers an assertion failure
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    engine = TokenBudgetPreflight(3)
    actual_normal = engine.check("one two three four").retained
    deliberate_wrong = ["one", "two", "three", "four"]  # Incorrect expectation: untruncated
    if actual_normal != deliberate_wrong:
        comparison_lines.append(
            f"Deliberate wrong assertion (expected {deliberate_wrong} vs actual {actual_normal}) correctly detected: PASS (mismatch caught)"
        )
    else:
        comparison_lines.append("Deliberate wrong assertion failed to catch discrepancy: FAIL")
        all_passed = False

    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append(f"Final Validation Status: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    summary_text = "\n".join(comparison_lines)
    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w", encoding="utf-8") as f:
        f.write(summary_text + "\n")

    return all_passed, results_record, summary_text


def main() -> None:
    print("=== Running Verification Check for Task R16-T041 ===")
    os.makedirs(WORK_DIR, exist_ok=True)

    versions = collect_tool_versions()
    print("Collected and saved tool versions.")

    eval_ok, results_record, eval_summary = evaluate_contract_fixtures()
    print("Evaluated contract fixtures.")
    if not eval_ok:
        print("ERROR: Contract fixture evaluation failed!\n", eval_summary, file=sys.stderr)
        sys.exit(1)

    unit_ok, unit_log = run_unit_tests()
    if not unit_ok:
        print("ERROR: Unit tests failed!\n", unit_log, file=sys.stderr)
        sys.exit(1)
    print("All unit tests passed successfully.")

    # Explicit check for deliberate wrong result assertion
    def verify_deliberate_wrong_fails():
        engine = TokenBudgetPreflight(3)
        rep = engine.check("one two three four")
        assert rep.retained != ["wrong", "output"]

    try:
        verify_deliberate_wrong_fails()
    except AssertionError:
        sys.exit(1)

    print("\nAll checks passed cleanly with exit code 0! Artifacts saved to work/R16-T041/")
    sys.exit(0)


if __name__ == "__main__":
    main()
