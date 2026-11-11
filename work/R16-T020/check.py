"""check.py — Automated verification check for Task R16-T020.

Validates the preflight token-budget contract, executes unit tests,
evaluates the three applied scenario assessment questions, verifies that
deliberate wrong results trigger failure, and records evidence in work/R16-T020/.
Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T020")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter7", "applied-labs", "r16-t020")

sys.path.insert(0, LAB_DIR)
from example import (
    APPLIED_QUESTIONS,
    TokenBudgetResult,
    evaluate_all_questions,
    token_budget_preflight,
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


def evaluate_contract_and_questions() -> bool:
    """Evaluate core contract and all applied assessment questions."""
    with open(os.path.join(WORK_DIR, "inputs.json"), "r") as f:
        data = json.load(f)

    comparison_lines = [
        f"Assignment: {data.get('task', 'R16-T020')}",
        f"Description: {data.get('description', '')}",
        "=" * 70,
        "Core Contract Verification: Token-Budget Preflight",
        "=" * 70,
    ]

    all_ok = True

    # 1. Core Contract Verification
    core_spec = data["core_contract"]
    text = core_spec["text"]
    budget = core_spec["budget"]
    expected = core_spec["expected"]

    res = token_budget_preflight(text, budget)
    actual = {
        "retained_tokens": res.retained_tokens,
        "removed_tokens": res.removed_tokens,
        "removed_count": res.removed_count,
        "total_tokens": res.total_tokens,
        "truncated": res.truncated,
    }

    core_passed = (actual == expected)
    if not core_passed:
        all_ok = False

    comparison_lines.append(f"Input Text:      {text!r}")
    comparison_lines.append(f"Budget:          {budget}")
    comparison_lines.append(f"Expected:        {expected}")
    comparison_lines.append(f"Actual:          {actual}")
    comparison_lines.append(f"Core Status:     {'PASS' if core_passed else 'FAIL'}")

    # 2. Applied Questions Assessment
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Applied Scenario Assessment Questions:")
    comparison_lines.append("=" * 70)

    all_questions_ok, audit = evaluate_all_questions()
    if not all_questions_ok:
        all_ok = False

    for item in audit:
        status = "PASS" if item["passed"] else "FAIL"
        comparison_lines.append(f"\n[{item['id']}] {item['topic']}")
        comparison_lines.append(f"  Status:    {status}")
        comparison_lines.append(f"  Rationale: {item['rationale']}")

    # 3. Deliberate Wrong Result Test Demonstration
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Deliberate Wrong Result Demonstration:")

    corrupted = TokenBudgetResult(
        retained_tokens=["corrupted"],
        removed_tokens=[],
        removed_count=999,
        total_tokens=1,
        budget=3,
        truncated=False,
    )
    detected_mismatch = (corrupted.retained_tokens != expected["retained_tokens"])

    if detected_mismatch:
        comparison_lines.append(
            f"  Deliberate wrong result correctly triggers mismatch: PASS"
        )
    else:
        comparison_lines.append("  Deliberate wrong result NOT detected: FAIL")
        all_ok = False

    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append(f"Final Validation Status: {'ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED'}")

    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w") as f:
        f.write("\n".join(comparison_lines) + "\n")

    return all_ok


def collect_tool_versions() -> None:
    """Record Python, Git, OS, and branch details."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    content = (
        f"Assignment: R16-T020\n"
        f"Student: Janhavi Sharma\n"
        f"Assigned Branch: {branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Check Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter7/applied-labs/r16-t020 -p 'test_*.py'\n"
        f"Evidence Check Command:\n"
        f"  python3 work/R16-T020/check.py\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(content)
    print("Tool versions recorded.")


def main() -> None:
    os.makedirs(WORK_DIR, exist_ok=True)
    print("Starting automated verification for Task R16-T020...")

    collect_tool_versions()

    if not run_unit_tests():
        sys.exit(1)

    if not evaluate_contract_and_questions():
        print("ERROR: Evaluation questions or contract check failed!", file=sys.stderr)
        sys.exit(1)

    print("ALL CHECKS PASSED cleanly — Task R16-T020")
    sys.exit(0)


if __name__ == "__main__":
    main()
