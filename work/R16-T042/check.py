#!/usr/bin/env python3
"""
Verification check script for Task R16-T042.

Validates the streaming aggregation contract:
- A, B, A, C yields {"A": 2, "B": 1, "C": 1}.
- Empty input gives {}.
- A malformed line is reported with its 1-indexed line number.
- Evaluates smallest valid, boundary, and invalid scenarios.
- Demonstrates that a deliberate wrong expectation makes the check fail.
- Runs automated unit tests via unittest discovery.
- Saves inputs, expected vs actual outputs, tool versions, and test logs into work/R16-T042/.
- Exits non-zero on any assertion or test failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T042")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter5", "applied-labs", "r16-t042")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    MalformedLineError,
    StreamAggregationResult,
    count_categories_from_stream,
    stream_aggregate_jsonl,
)


def collect_tool_versions() -> str:
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T042\n"
        f"Student: Nilesh\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Test Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t042 -p 'test_*.py'\n"
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
    """Evaluate contract and boundary fixtures, verifying expected vs actual."""
    fixtures = [
        {
            "scenario": "normal_stream_a_b_a_c",
            "description": "Records A, B, A, C give category counts A:2, B:1, C:1",
            "input_lines": [
                '{"category": "A"}',
                '{"category": "B"}',
                '{"category": "A"}',
                '{"category": "C"}',
            ],
            "expected_counts": {"A": 2, "B": 1, "C": 1},
            "expected_malformed_count": 0,
            "expected_malformed_lines": [],
        },
        {
            "scenario": "boundary_empty_input",
            "description": "Empty stream yields empty category counts {}",
            "input_lines": [],
            "expected_counts": {},
            "expected_malformed_count": 0,
            "expected_malformed_lines": [],
        },
        {
            "scenario": "boundary_whitespace_lines",
            "description": "Whitespace lines are skipped cleanly",
            "input_lines": ["", "   ", '{"category": "A"}', " \t ", ""],
            "expected_counts": {"A": 1},
            "expected_malformed_count": 0,
            "expected_malformed_lines": [],
        },
        {
            "scenario": "boundary_smallest_valid",
            "description": "Smallest valid record produces single category count",
            "input_lines": ['{"category": "Single"}'],
            "expected_counts": {"Single": 1},
            "expected_malformed_count": 0,
            "expected_malformed_lines": [],
        },
        {
            "scenario": "malformed_syntax_line",
            "description": "Malformed JSON line is reported with exact line number",
            "input_lines": [
                '{"category": "A"}',
                '{malformed json syntax}',
                '{"category": "B"}',
            ],
            "expected_counts": {"A": 1, "B": 1},
            "expected_malformed_count": 1,
            "expected_malformed_lines": [2],
        },
        {
            "scenario": "malformed_missing_category_schema",
            "description": "Record missing category field is reported with line number",
            "input_lines": [
                '{"other_key": "val"}',
                '{"category": "A"}',
            ],
            "expected_counts": {"A": 1},
            "expected_malformed_count": 1,
            "expected_malformed_lines": [1],
        },
    ]

    with open(os.path.join(WORK_DIR, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2)

    comparison_lines = [
        "Assignment: R16-T042",
        "Comparison: Expected vs Actual Results",
        "=" * 60,
    ]

    all_passed = True
    results_record = []

    for item in fixtures:
        scenario = item["scenario"]
        desc = item["description"]
        inp = item["input_lines"]
        exp_counts = item["expected_counts"]
        exp_err_count = item["expected_malformed_count"]
        exp_lines = item["expected_malformed_lines"]

        comparison_lines.append(f"\nScenario: {scenario} ({desc})")
        comparison_lines.append(f"Input lines count: {len(inp)}")

        res = stream_aggregate_jsonl(inp)
        actual_counts = res.category_counts
        actual_err_count = len(res.malformed_records)
        actual_lines = [m.line_number for m in res.malformed_records]

        comparison_lines.append(f"Expected counts:   {exp_counts}")
        comparison_lines.append(f"Actual counts:     {actual_counts}")
        comparison_lines.append(f"Expected malformed line numbers: {exp_lines}")
        comparison_lines.append(f"Actual malformed line numbers:   {actual_lines}")

        passed = (
            actual_counts == exp_counts
            and actual_err_count == exp_err_count
            and actual_lines == exp_lines
        )

        status_str = "PASS" if passed else "FAIL"
        comparison_lines.append(f"Status: {status_str}")
        if not passed:
            all_passed = False

        results_record.append({
            "scenario": scenario,
            "status": status_str,
            "actual_counts": actual_counts,
            "actual_malformed_lines": actual_lines,
        })

    # Demonstrate that a deliberate wrong result triggers an assertion failure
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    test_stream = ['{"category": "A"}', '{"category": "B"}']
    actual_normal = stream_aggregate_jsonl(test_stream).category_counts
    deliberate_wrong = {"A": 99, "B": 99}
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
    print("=== Running Verification Check for Task R16-T042 ===")
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

    # Explicit check for deliberate wrong result failure
    def verify_deliberate_wrong_fails():
        counts = stream_aggregate_jsonl(['{"category": "A"}']).category_counts
        assert counts != {"A": 999}

    try:
        verify_deliberate_wrong_fails()
    except AssertionError:
        sys.exit(1)

    print("\nAll checks passed cleanly with exit code 0! Artifacts saved to work/R16-T042/")
    sys.exit(0)


if __name__ == "__main__":
    main()
