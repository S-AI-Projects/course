"""check.py — Automated verification check for Task R16-T017.

Validates the worked decision example for Chapter 6 Section 1, executes unit tests,
evaluates the published decision table, proves that a deliberately corrupted decision
triggers failure, and saves evidence in work/R16-T017/.
Exits non-zero if any assertion fails.
"""

import copy
import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T017")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter6", "applied-labs", "r16-t017")

sys.path.insert(0, LAB_DIR)
from example import (
    REUSE_PRETRAINED_TOKENIZER,
    SCENARIOS,
    TRAIN_NEW_TOKENIZER,
    check_decision_table,
    evaluate_scenario,
    run_regression_test,
)


def run_unit_tests() -> bool:
    """Run automated unittest discovery suite and record full log."""
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

    if proc.returncode != 0:
        print("ERROR: Unit tests failed!", file=sys.stderr)
        print(test_log, file=sys.stderr)
        return False

    print(f"Unit tests: PASSED ({test_log.strip().splitlines()[-1]})")
    return True


def evaluate_decision_table() -> bool:
    """Evaluate all scenarios in the published decision table."""
    all_passed, audit_results = check_decision_table(SCENARIOS)

    comparison_lines = [
        "Assignment: R16-T017",
        "Comparison: Expected vs Actual Decisions (Published Table)",
        "=" * 70,
    ]

    for item in audit_results:
        status = "PASS" if item["passed"] else "FAIL"
        comparison_lines.append(f"\nScenario ID: {item['id']} ({item['name']})")
        comparison_lines.append(f"  Expected Decision: {item['expected']}")
        comparison_lines.append(f"  Actual Decision:   {item['actual']}")
        comparison_lines.append(f"  Status:            {status}")
        comparison_lines.append(f"  Rationale:         {item['rationale']}")

    # Deliberate wrong decision test demonstration
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Deliberate Wrong Decision Demonstration:")

    corrupted_scenarios = copy.deepcopy(SCENARIOS)
    corrupted_scenarios[0]["expected_decision"] = REUSE_PRETRAINED_TOKENIZER
    corrupted_passed, corrupted_results = check_decision_table(corrupted_scenarios)

    if not corrupted_passed and not corrupted_results[0]["passed"]:
        comparison_lines.append(
            f"Deliberate wrong decision on scenario {corrupted_results[0]['id']} "
            f"(expected {REUSE_PRETRAINED_TOKENIZER} vs actual {corrupted_results[0]['actual']}) "
            f"correctly triggers failure: PASS (mismatch detected)"
        )
    else:
        comparison_lines.append("Deliberate wrong decision failed to trigger failure: FAIL")
        all_passed = False

    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append(f"Final Validation Status: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w") as f:
        f.write("\n".join(comparison_lines) + "\n")

    return all_passed


def collect_tool_versions() -> None:
    """Collect platform, Python, Git, and branch information."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T017\n"
        f"Student: Janhavi Sharma\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Check Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t017 -p 'test_*.py'\n"
        f"Evidence Check Command:\n"
        f"  python3 work/R16-T017/check.py\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(versions_content)
    print("Tool versions recorded.")


def main() -> None:
    os.makedirs(WORK_DIR, exist_ok=True)
    print("Starting automated verification for Task R16-T017...")

    collect_tool_versions()

    if not run_unit_tests():
        sys.exit(1)

    if not evaluate_decision_table():
        print("ERROR: Decision table evaluation failed!", file=sys.stderr)
        sys.exit(1)

    print("ALL CHECKS PASSED cleanly — Task R16-T017")
    sys.exit(0)


if __name__ == "__main__":
    main()
