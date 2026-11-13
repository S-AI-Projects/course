#!/usr/bin/env python3
"""
Verification check script for R16-T022.
Verifies contract assertions, runs test discovery, records tool versions,
and saves inputs, expected vs actual outputs into work/R16-T022/.
Exits non-zero if any assertion or test fails.
"""

import json
import os
import platform
import subprocess
import sys

# Ensure lab directory is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LAB_DIR = os.path.join(REPO_ROOT, "chapters/en/chapter3/applied-labs/r16-t022")
WORK_DIR = os.path.join(REPO_ROOT, "work/R16-T022")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import TrainingOnlyMeanImputer, run_pipeline


def run_checks() -> None:
    print("=== Running Checks for Task R16-T022 ===")

    # 1. Environment & tool versions
    env_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "task_id": "R16-T022",
        "branch": "student/e26b07f0747/R16-T022",
    }
    print(f"Python Version: {env_info['python_version']}")
    print(f"Platform: {env_info['platform']}")

    # 2. Contract checks
    contract_checks = []

    # Check 1: Training [2, None, 4] yields mean 3
    imp = TrainingOnlyMeanImputer().fit([2, None, 4])
    passed1 = imp.mean_ == 3
    contract_checks.append({
        "description": "Training [2, None, 4] yields mean 3",
        "input": [2, None, 4],
        "expected": 3,
        "actual": imp.mean_,
        "status": "PASS" if passed1 else "FAIL",
    })
    if not passed1:
        print("ERROR: Training mean computation failed!")
        sys.exit(1)

    # Check 2: Transformed training [2, None, 4] -> [2, 3, 4]
    t_train = imp.transform([2, None, 4])
    passed2 = t_train == [2, 3, 4]
    contract_checks.append({
        "description": "Transformed training [2, None, 4] -> [2, 3, 4]",
        "input": [2, None, 4],
        "expected": [2, 3, 4],
        "actual": t_train,
        "status": "PASS" if passed2 else "FAIL",
    })
    if not passed2:
        print("ERROR: Training transformation failed!")
        sys.exit(1)

    # Check 3: Transformed validation [100, None] -> [100, 3] (NOT [100, 100])
    t_val = imp.transform([100, None])
    passed3 = (t_val == [100, 3]) and (t_val != [100, 100])
    contract_checks.append({
        "description": "Validation [100, None] becomes [100, 3], not [100, 100]",
        "input": [100, None],
        "expected": [100, 3],
        "actual": t_val,
        "status": "PASS" if passed3 else "FAIL",
    })
    if not passed3:
        print("ERROR: Validation transformation failed or suffered from leakage!")
        sys.exit(1)

    # Check 4: Smallest valid case [5] -> mean 5, transform [None] -> [5]
    imp_single = TrainingOnlyMeanImputer().fit([5])
    t_single = imp_single.transform([None])
    passed4 = imp_single.mean_ == 5 and t_single == [5]
    contract_checks.append({
        "description": "Smallest valid training [5] -> mean 5; transform [None] -> [5]",
        "input": {"train": [5], "val": [None]},
        "expected": {"mean": 5, "val_imputed": [5]},
        "actual": {"mean": imp_single.mean_, "val_imputed": t_single},
        "status": "PASS" if passed4 else "FAIL",
    })
    if not passed4:
        print("ERROR: Smallest valid fixture check failed!")
        sys.exit(1)

    # Check 5: Boundary validation all-missing [None, None] -> [3, 3]
    t_all_none = imp.transform([None, None])
    passed5 = t_all_none == [3, 3]
    contract_checks.append({
        "description": "Boundary validation [None, None] -> [3, 3]",
        "input": [None, None],
        "expected": [3, 3],
        "actual": t_all_none,
        "status": "PASS" if passed5 else "FAIL",
    })
    if not passed5:
        print("ERROR: All-missing validation check failed!")
        sys.exit(1)

    # Check 6: Boundary decision - all-missing training input is rejected
    rejected = False
    try:
        TrainingOnlyMeanImputer().fit([None, None, None])
    except ValueError:
        rejected = True
    contract_checks.append({
        "description": "Boundary decision: all-missing training input [None, None, None] rejected with ValueError",
        "input": [None, None, None],
        "expected": "ValueError (rejected)",
        "actual": "ValueError (rejected)" if rejected else "Accepted (incorrect)",
        "status": "PASS" if rejected else "FAIL",
    })
    if not rejected:
        print("ERROR: All-missing training input was not rejected!")
        sys.exit(1)

    for c in contract_checks:
        print(f"[{c['status']}] {c['description']} | Actual: {c['actual']}")

    # 3. Deliberate wrong result check (ensures checks are non-vacuous)
    print("\nVerifying deliberate wrong result triggers failure...")
    deliberate_wrong = [100, 100]
    if t_val == deliberate_wrong:
        print("ERROR: Deliberate failure test was expected to differ but matched!")
        sys.exit(1)
    print("Deliberate failure test passed: wrong result correctly rejected.")

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

    # 5. Save outputs to work/R16-T022/
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
        f.write("=== TASK R16-T022 VERIFICATION REPORT ===\n\n")
        f.write(f"Task: R16-T022\n")
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
