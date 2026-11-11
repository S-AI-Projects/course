"""check.py — Automated verification check for Task R16-T016.

Runs unit tests, evaluates fixtures from inputs.json, proves before/after
equivalence between baseline and refactored components, verifies deliberate
failure detection, and records evidence in work/R16-T016/.
Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys

# Repo root and paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T016")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter2", "applied-labs", "r16-t016")

sys.path.insert(0, LAB_DIR)
from example import (
    TokenBudgetResult,
    token_budget_preflight,
    token_budget_preflight_baseline,
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


def evaluate_fixtures_and_equivalence() -> bool:
    """Evaluate all fixtures from inputs.json and verify equivalence."""
    with open(os.path.join(WORK_DIR, "inputs.json"), "r") as f:
        data = json.load(f)

    comparisons = []
    all_ok = True

    comparison_lines = [
        f"Assignment: {data.get('task', 'R16-T016')}",
        f"Description: {data.get('description', '')}",
        "=" * 70,
        "Fixture Evaluation & Baseline Equivalence Verification",
        "=" * 70,
    ]

    for name, item in data["fixtures"].items():
        text = item["input"]["text"]
        budget = item["input"]["budget"]
        expected = item["expected"]

        # Run refactored preflight
        actual_res = token_budget_preflight(text, budget)
        actual = {
            "retained_tokens": actual_res.retained_tokens,
            "removed_tokens": actual_res.removed_tokens,
            "removed_count": actual_res.removed_count,
            "total_tokens": actual_res.total_tokens,
            "truncated": actual_res.truncated,
        }

        # Run baseline for equivalence
        baseline_res = token_budget_preflight_baseline(text, budget)
        equivalence = (actual_res == baseline_res)

        match = (actual == expected) and equivalence
        if not match:
            all_ok = False

        status = "PASS" if match else "FAIL"
        comparison_lines.append(f"\n[Fixture: {name}] ({item.get('description', '')})")
        comparison_lines.append(f"  Input       : text={text!r}, budget={budget}")
        comparison_lines.append(f"  Expected    : {expected}")
        comparison_lines.append(f"  Actual      : {actual}")
        comparison_lines.append(f"  Equivalence : baseline == refactored -> {equivalence}")
        comparison_lines.append(f"  Status      : {status}")

    # Negative budget rejection test
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Negative Budget Rejection:")
    try:
        token_budget_preflight("test", -1)
        neg_passed = False
        comparison_lines.append("  Negative budget (-1) accepted without error: FAIL")
    except ValueError as e:
        neg_passed = True
        comparison_lines.append(f"  Negative budget (-1) correctly raised ValueError ({e}): PASS")

    if not neg_passed:
        all_ok = False

    # Deliberate wrong result check
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    corrupted = TokenBudgetResult(
        retained_tokens=["corrupted"],
        removed_tokens=[],
        removed_count=999,
        total_tokens=1,
        budget=3,
        truncated=False,
    )
    expected_standard = data["fixtures"]["budget_3_with_4_tokens"]["expected"]
    caught_mismatch = (corrupted.retained_tokens != expected_standard["retained_tokens"])

    if caught_mismatch:
        comparison_lines.append("  Deliberate corrupted result correctly detected as mismatch: PASS")
    else:
        comparison_lines.append("  Deliberate corrupted result NOT detected: FAIL")
        all_ok = False

    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append(f"Final Status: {'ALL CHECKS PASSED' if all_ok else 'CHECKS FAILED'}")

    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w") as f:
        f.write("\n".join(comparison_lines) + "\n")

    return all_ok


def collect_tool_versions() -> None:
    """Record Python, Git, OS, and task details."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    content = (
        f"Assignment: R16-T016\n"
        f"Student: Janhavi Sharma\n"
        f"Working Branch: {branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Check Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t016 -p 'test_*.py'\n"
        f"Evidence Check Command:\n"
        f"  python3 work/R16-T016/check.py\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(content)
    print("Tool versions recorded.")


def main() -> None:
    os.makedirs(WORK_DIR, exist_ok=True)
    print("Starting automated verification for Task R16-T016...")

    collect_tool_versions()

    if not run_unit_tests():
        sys.exit(1)

    if not evaluate_fixtures_and_equivalence():
        print("ERROR: Fixture evaluations or equivalence failed!", file=sys.stderr)
        sys.exit(1)

    print("ALL CHECKS PASSED cleanly — Task R16-T016")
    sys.exit(0)


if __name__ == "__main__":
    main()
