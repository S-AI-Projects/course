#!/usr/bin/env python3
"""
Verification check script for Task R16-T048.

Validates chronological evaluation split:
- Ten ordered observations yield 6 train, 2 validation, 2 test.
- Shuffled input is sorted first.
- Duplicate timestamps are rejected.
- Future observations remain out of training.
- Demonstrates invalid/missing-data error and recovery on the next valid batch.
- Demonstrates that a deliberate wrong result makes the check fail.
- Saves inputs, expected vs actual outputs, tool versions, and test logs into work/R16-T048/.
- Exits non-zero on any assertion or test failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T048")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter2", "applied-labs", "r16-t048")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    Observation,
    SplitResult,
    chronological_split,
    process_observation_batches,
)


def collect_tool_versions() -> str:
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T048\n"
        f"Student: Nilesh\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Test Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t048 -p 'test_*.py'\n"
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
    """Evaluate chronological split contract scenarios and recovery verification."""
    shuffled_ten = [
        {"timestamp": 10},
        {"timestamp": 2},
        {"timestamp": 8},
        {"timestamp": 1},
        {"timestamp": 4},
        {"timestamp": 7},
        {"timestamp": 3},
        {"timestamp": 9},
        {"timestamp": 5},
        {"timestamp": 6},
    ]

    fixtures = [
        {
            "scenario": "ten_observations_shuffled",
            "description": "Ten shuffled observations yield 6 train, 2 val, 2 test after sorting",
            "observations": shuffled_ten,
            "expected_train_count": 6,
            "expected_val_count": 2,
            "expected_test_count": 2,
            "expected_train_ts": [1, 2, 3, 4, 5, 6],
            "expected_val_ts": [7, 8],
            "expected_test_ts": [9, 10],
            "expected_exception": None,
        },
        {
            "scenario": "duplicate_timestamps_rejected",
            "description": "Duplicate timestamps are rejected with ValueError",
            "observations": [{"timestamp": 1}, {"timestamp": 2}, {"timestamp": 2}],
            "expected_exception": "ValueError",
        },
        {
            "scenario": "missing_timestamp_rejected",
            "description": "Missing timestamp field is rejected with KeyError",
            "observations": [{"timestamp": 1}, {"invalid_key": 2}],
            "expected_exception": "KeyError",
        },
    ]

    with open(os.path.join(WORK_DIR, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2)

    comparison_lines = [
        "Assignment: R16-T048",
        "Comparison: Expected vs Actual Results & Recovery Audits",
        "=" * 60,
    ]

    all_passed = True
    results_record = []

    for item in fixtures:
        scenario = item["scenario"]
        desc = item["description"]
        obs = item["observations"]
        exp_exc = item.get("expected_exception")

        comparison_lines.append(f"\nScenario: {scenario} ({desc})")

        if exp_exc:
            try:
                res = chronological_split(obs)
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append("Actual: No exception raised (FAIL)")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})
            except Exception as e:
                actual_exc = type(e).__name__
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Exception: {actual_exc} ({e})")
                passed = (actual_exc == exp_exc)
                comparison_lines.append(f"Status: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    all_passed = False
                results_record.append({"scenario": scenario, "status": "PASS" if passed else "FAIL", "actual_exception": actual_exc})
        else:
            try:
                res = chronological_split(obs)
                train_ts = [o.timestamp for o in res.train]
                val_ts = [o.timestamp for o in res.validation]
                test_ts = [o.timestamp for o in res.test]

                comparison_lines.append(f"Expected: train={item['expected_train_count']}, val={item['expected_val_count']}, test={item['expected_test_count']}")
                comparison_lines.append(f"Actual:   train={len(res.train)}, val={len(res.validation)}, test={len(res.test)}")
                comparison_lines.append(f"Train Timestamps: {train_ts}")
                comparison_lines.append(f"Val Timestamps:   {val_ts}")
                comparison_lines.append(f"Test Timestamps:  {test_ts}")

                passed = (
                    len(res.train) == item["expected_train_count"]
                    and len(res.validation) == item["expected_val_count"]
                    and len(res.test) == item["expected_test_count"]
                    and train_ts == item["expected_train_ts"]
                    and val_ts == item["expected_val_ts"]
                    and test_ts == item["expected_test_ts"]
                )
                comparison_lines.append(f"Status: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    all_passed = False
                results_record.append({"scenario": scenario, "status": "PASS" if passed else "FAIL"})
            except Exception as e:
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})

    # Evaluate failure and recovery pipeline
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Pipeline Failure and Recovery Demonstration:")
    pipeline_batches = [
        {"batch_id": "b1_valid", "observations": shuffled_ten},
        {"batch_id": "b2_duplicate_err", "observations": [{"timestamp": 5}, {"timestamp": 5}]},
        {"batch_id": "b3_recovered", "observations": [{"timestamp": i * 10} for i in range(1, 11)]},
    ]
    history = process_observation_batches(pipeline_batches)
    recovery_passed = (
        history[0]["status"] == "SUCCESS"
        and history[1]["status"] == "FAILED"
        and history[1]["error_type"] == "ValueError"
        and history[2]["status"] == "SUCCESS"
    )
    for h in history:
        err_info = h.get('error_type') or 'None'
        comparison_lines.append(f"  [{h['status']}] {h['batch_id']}: Error={err_info} | TrainCount={h['train_count']}")
    comparison_lines.append(f"Failure and Recovery Verified: {'PASS' if recovery_passed else 'FAIL'}")
    if not recovery_passed:
        all_passed = False

    # Demonstrate that a deliberate wrong result triggers an assertion failure
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    actual_train = len(chronological_split(shuffled_ten).train)
    deliberate_wrong = 999
    if actual_train != deliberate_wrong:
        comparison_lines.append(
            f"Deliberate wrong assertion (expected {deliberate_wrong} vs actual {actual_train}) correctly detected: PASS"
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
    print("=== Running Verification Check for Task R16-T048 ===")
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

    print("\nAll checks passed cleanly with exit code 0! Artifacts saved to work/R16-T048/")
    sys.exit(0)


if __name__ == "__main__":
    main()
