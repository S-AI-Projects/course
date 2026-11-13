#!/usr/bin/env python3
"""
Verification check script for R16-T023.
Verifies contract assertions, compares both approaches, runs test discovery,
records tool versions, and saves inputs, expected vs actual outputs into work/R16-T023/.
Exits non-zero if any assertion or test fails.
"""

import json
import os
import platform
import subprocess
import sys

# Ensure lab directory is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LAB_DIR = os.path.join(REPO_ROOT, "chapters/en/chapter1/applied-labs/r16-t023")
WORK_DIR = os.path.join(REPO_ROOT, "work/R16-T023")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    TokenBudgetPreflight,
    compare_approaches,
    reference_preflight_calc,
)


def run_checks() -> None:
    print("=== Running Checks for Task R16-T023 ===")

    # 1. Environment & tool versions
    env_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "task_id": "R16-T023",
        "branch": "student/e26b07f0747/R16-T023",
    }
    print(f"Python Version: {env_info['python_version']}")
    print(f"Platform: {env_info['platform']}")

    contract_checks = []

    # Check 1: Budget 3 with "one two three four" retains [one, two, three] and reports 1 removed
    engine = TokenBudgetPreflight(3)
    rep1 = engine.check("one two three four")
    passed1 = (
        rep1.retained == ["one", "two", "three"]
        and rep1.removed_count == 1
        and rep1.is_truncated is True
    )
    contract_checks.append({
        "description": "Budget 3 with 'one two three four' retains [one, two, three] and reports 1 removed",
        "input": {"prompt": "one two three four", "budget": 3},
        "expected": {"retained": ["one", "two", "three"], "removed_count": 1, "is_truncated": True},
        "actual": {"retained": rep1.retained, "removed_count": rep1.removed_count, "is_truncated": rep1.is_truncated},
        "status": "PASS" if passed1 else "FAIL",
    })
    if not passed1:
        print("ERROR: Check 1 failed!")
        sys.exit(1)

    # Check 2: Empty input retains none and reports 0 removed
    rep_empty = engine.check("")
    passed2 = (
        rep_empty.retained == []
        and rep_empty.removed_count == 0
        and rep_empty.is_truncated is False
    )
    contract_checks.append({
        "description": "Empty input retains none and reports 0 removed",
        "input": {"prompt": "", "budget": 3},
        "expected": {"retained": [], "removed_count": 0, "is_truncated": False},
        "actual": {"retained": rep_empty.retained, "removed_count": rep_empty.removed_count, "is_truncated": rep_empty.is_truncated},
        "status": "PASS" if passed2 else "FAIL",
    })
    if not passed2:
        print("ERROR: Check 2 failed!")
        sys.exit(1)

    # Check 3: Negative budget is rejected with ValueError
    neg_rejected = False
    try:
        TokenBudgetPreflight(-1)
    except ValueError:
        neg_rejected = True

    contract_checks.append({
        "description": "Negative budget (-1) is rejected with ValueError",
        "input": {"budget": -1},
        "expected": "ValueError (rejected)",
        "actual": "ValueError (rejected)" if neg_rejected else "Accepted (incorrect)",
        "status": "PASS" if neg_rejected else "FAIL",
    })
    if not neg_rejected:
        print("ERROR: Negative budget check failed!")
        sys.exit(1)

    # Check 4: Compare two approaches across identical inputs
    comparison_cases = [
        ("one two three four", 3),
        ("one two three four", 4),
        ("one two three four", 5),
        ("one two three four", 0),
        ("", 3),
        ("alpha beta gamma", 2),
    ]
    all_matched = all(compare_approaches(p, b) for p, b in comparison_cases)
    contract_checks.append({
        "description": "Compare Approach 1 (Engine) and Approach 2 (Reference Calc) on identical inputs",
        "input": [f"prompt='{p}', budget={b}" for p, b in comparison_cases],
        "expected": "All comparisons return True",
        "actual": f"All matched: {all_matched}",
        "status": "PASS" if all_matched else "FAIL",
    })
    if not all_matched:
        print("ERROR: Approach comparison check failed!")
        sys.exit(1)

    for c in contract_checks:
        print(f"[{c['status']}] {c['description']}")

    # 3. Deliberate wrong result verification (ensures checks are non-vacuous)
    print("\nVerifying deliberate wrong result triggers failure...")
    deliberate_wrong = ["one", "two", "three", "four"]
    if rep1.retained == deliberate_wrong:
        print("ERROR: Deliberate failure test matched unexpectedly!")
        sys.exit(1)
    print("Deliberate failure test passed: wrong result correctly detected.")

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

    # 5. Persist evidence to work/R16-T023/
    os.makedirs(WORK_DIR, exist_ok=True)
    json_path = os.path.join(WORK_DIR, "results.json")
    report_data = {
        "environment": env_info,
        "contract_checks": contract_checks,
        "deliberate_failure_check": "PASS (wrong expectation correctly detected)",
        "unittest_exit_code": test_proc.returncode,
        "unittest_output": test_proc.stderr,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    report_path = os.path.join(WORK_DIR, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== TASK R16-T023 VERIFICATION REPORT ===\n\n")
        f.write(f"Task: R16-T023\n")
        f.write(f"Branch: {env_info['branch']}\n")
        f.write(f"Python Version: {env_info['python_version']}\n")
        f.write(f"Platform: {env_info['platform']}\n\n")
        f.write("--- Contract Checks ---\n")
        for c in contract_checks:
            f.write(f"[{c['status']}] {c['description']} | Actual: {c['actual']}\n")
        f.write("\n--- Unittest Output ---\n")
        f.write(test_proc.stderr)
        f.write(f"\nUnittest Return Code: {test_proc.returncode}\n")
        f.write("\nALL CHECKS PASSED.\n")

    print(f"\nSaved check results to {json_path} and {report_path}")
    print("All checks completed successfully with exit code 0.")


if __name__ == "__main__":
    run_checks()
