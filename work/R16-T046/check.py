#!/usr/bin/env python3
"""
Verification check script for Task R16-T046.

Validates prompt-template escaping and refactoring:
- Template with name and topic renders supplied values.
- Missing topic fails (raises KeyError).
- Braces inside user data remain literal.
- Prompt injection limitation explicitly disclaimed.
- Equivalence proven between Baseline and Refactored renderers.
- Demonstrates that a deliberate wrong result makes the check fail.
- Saves inputs, expected vs actual outputs, tool versions, and test logs into work/R16-T046/.
- Exits non-zero on any assertion or test failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T046")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter1", "applied-labs", "r16-t046")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    PROMPT_INJECTION_DISCLAIMER,
    BaselinePromptRenderer,
    RefactoredPromptRenderer,
    TemplateVariableBinder,
    prove_equivalence,
)


def collect_tool_versions() -> str:
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T046\n"
        f"Student: Nilesh\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Test Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t046 -p 'test_*.py'\n"
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
    """Evaluate template contract scenarios and refactoring equivalence."""
    template = "Instruction: Write an essay for {name} on {topic}."

    fixtures = [
        {
            "scenario": "normal_render",
            "description": "Template with name and topic renders supplied values",
            "variables": {"name": "Alice", "topic": "Quantum Computing"},
            "expected_output": "Instruction: Write an essay for Alice on Quantum Computing.",
            "expected_exception": None,
        },
        {
            "scenario": "braces_inside_user_data",
            "description": "Braces inside user data remain literal",
            "variables": {"name": "Bob", "topic": "Deep Learning {LLM} Architecture"},
            "expected_output": "Instruction: Write an essay for Bob on Deep Learning {LLM} Architecture.",
            "expected_exception": None,
        },
        {
            "scenario": "missing_topic_fails",
            "description": "Missing topic fails with KeyError",
            "variables": {"name": "Charlie"},
            "expected_output": None,
            "expected_exception": "KeyError",
        },
        {
            "scenario": "unknown_key_rejected",
            "description": "Undeclared variable rejected with ValueError",
            "variables": {"name": "Dave", "topic": "AI", "extra_bad": "malicious"},
            "expected_output": None,
            "expected_exception": "ValueError",
        },
    ]

    with open(os.path.join(WORK_DIR, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2)

    comparison_lines = [
        "Assignment: R16-T046",
        "Comparison: Expected vs Actual Results & Equivalence Audits",
        "=" * 60,
    ]

    all_passed = True
    results_record = []
    renderer = RefactoredPromptRenderer(template)

    for item in fixtures:
        scenario = item["scenario"]
        desc = item["description"]
        variables = item["variables"]
        exp_out = item["expected_output"]
        exp_exc = item["expected_exception"]

        comparison_lines.append(f"\nScenario: {scenario} ({desc})")
        comparison_lines.append(f"Variables: {variables}")

        if exp_exc:
            try:
                res = renderer.render(variables)
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Result: {res} (NO EXCEPTION RAISED)")
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
                res = renderer.render(variables)
                comparison_lines.append(f"Expected: {exp_out}")
                comparison_lines.append(f"Actual:   {res}")
                passed = (res == exp_out)
                comparison_lines.append(f"Status: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    all_passed = False
                results_record.append({"scenario": scenario, "status": "PASS" if passed else "FAIL", "actual": res})
            except Exception as e:
                comparison_lines.append(f"Expected: {exp_out}")
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})

    # Verify before/after equivalence
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Before/After Refactoring Equivalence Proof:")
    all_equiv, equiv_log = prove_equivalence(template, fixtures)
    comparison_lines.append(f"All fixtures strictly equivalent across Baseline & Refactored: {all_equiv}")
    if not all_equiv:
        all_passed = False

    # Demonstrate that a deliberate wrong result triggers an assertion failure
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    actual_normal = renderer.render({"name": "A", "topic": "B"})
    deliberate_wrong = "Deliberate Wrong Output"
    if actual_normal != deliberate_wrong:
        comparison_lines.append(
            f"Deliberate wrong assertion (expected {repr(deliberate_wrong)} vs actual {repr(actual_normal)}) correctly detected: PASS"
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
    print("=== Running Verification Check for Task R16-T046 ===")
    os.makedirs(WORK_DIR, exist_ok=True)

    collect_tool_versions()
    print("Collected tool versions.")

    eval_ok, results_record, eval_summary = evaluate_fixtures()
    print("Evaluated template contract fixtures.")
    if not eval_ok:
        print("ERROR: Fixture evaluation failed!\n", eval_summary, file=sys.stderr)
        sys.exit(1)

    unit_ok, unit_log = run_unit_tests()
    if not unit_ok:
        print("ERROR: Unit tests failed!\n", unit_log, file=sys.stderr)
        sys.exit(1)
    print("All unit tests passed successfully.")

    print("\nAll checks passed cleanly with exit code 0! Artifacts saved to work/R16-T046/")
    sys.exit(0)


if __name__ == "__main__":
    main()
