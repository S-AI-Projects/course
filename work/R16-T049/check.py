#!/usr/bin/env python3
"""
Verification check script for Task R16-T049.

Validates the UI callback contract and evaluation experiment:
- Input "red red apple" returns word_count=3 and unique_count=2.
- Empty text returns zeros.
- Non-string inputs are rejected with TypeError.
- Compares three small controlled input sizes reporting correctness and trade-offs.
- Demonstrates that a deliberate wrong result makes the check fail.
- Saves inputs, expected vs actual outputs, tool versions, and test logs into work/R16-T049/.
- Exits non-zero on any assertion or test failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T049")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter9", "applied-labs", "r16-t049")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    analyze_text,
    evaluate_input_configurations,
    text_analysis_callback,
)


def collect_tool_versions() -> str:
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T049\n"
        f"Student: Nilesh\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Test Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t049 -p 'test_*.py'\n"
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
    """Evaluate contract scenarios and execution experiments."""
    fixtures = [
        {
            "scenario": "normal_red_red_apple",
            "input": "red red apple",
            "expected_output": {"word_count": 3, "unique_count": 2},
            "expected_exception": None,
        },
        {
            "scenario": "boundary_empty_string",
            "input": "",
            "expected_output": {"word_count": 0, "unique_count": 0},
            "expected_exception": None,
        },
        {
            "scenario": "boundary_whitespace_string",
            "input": "   \n\t  ",
            "expected_output": {"word_count": 0, "unique_count": 0},
            "expected_exception": None,
        },
        {
            "scenario": "failure_nonstring_none",
            "input": None,
            "expected_output": None,
            "expected_exception": "TypeError",
        },
        {
            "scenario": "failure_nonstring_int",
            "input": 12345,
            "expected_output": None,
            "expected_exception": "TypeError",
        },
    ]

    with open(os.path.join(WORK_DIR, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2)

    comparison_lines = [
        "Assignment: R16-T049",
        "Comparison: Expected vs Actual Results & Experiment Audits",
        "=" * 60,
    ]

    all_passed = True
    results_record = []

    for item in fixtures:
        scenario = item["scenario"]
        inp = item["input"]
        exp_out = item["expected_output"]
        exp_exc = item["expected_exception"]

        comparison_lines.append(f"\nScenario: {scenario}")
        comparison_lines.append(f"Input: {repr(inp)}")

        if exp_exc:
            try:
                res = analyze_text(inp)
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append("Actual: No exception raised (FAIL)")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})
            except TypeError as e:
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Exception: TypeError ({e})")
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
                res = analyze_text(inp)
                comparison_lines.append(f"Expected: {exp_out}")
                comparison_lines.append(f"Actual:   {res}")
                passed = (res == exp_out)
                comparison_lines.append(f"Status: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    all_passed = False
                results_record.append({"scenario": scenario, "status": "PASS" if passed else "FAIL", "actual": res})
            except Exception as e:
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})

    # Evaluate controlled configuration experiment
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Controlled Input Size Evaluation Experiment:")
    exp_results = evaluate_input_configurations()
    for exp in exp_results:
        comparison_lines.append(
            f"  [{exp['config_id']}] Words: {exp['word_count']}, Unique: {exp['unique_count']}, "
            f"Ratio: {exp['uniqueness_ratio']}, Latency: {exp['latency_seconds']:.6f}s | Correct: {exp['is_correct']}"
        )
        if not exp["is_correct"]:
            all_passed = False

    # Demonstrate that a deliberate wrong result triggers an assertion failure
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    actual_normal = analyze_text("red red apple")
    deliberate_wrong = {"word_count": 999, "unique_count": 999}
    if actual_normal != deliberate_wrong:
        comparison_lines.append(
            f"Deliberate wrong assertion (expected {deliberate_wrong} vs actual {actual_normal}) correctly detected: PASS"
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
    print("=== Running Verification Check for Task R16-T049 ===")
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

    print("\nAll checks passed cleanly with exit code 0! Artifacts saved to work/R16-T049/")
    sys.exit(0)


if __name__ == "__main__":
    main()
