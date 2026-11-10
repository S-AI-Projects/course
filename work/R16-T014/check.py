#!/usr/bin/env python3
"""Verification check script for Task R16-T014.

Runs unit tests, evaluates all fixture scenarios, verifies span invariants,
demonstrates deliberate failure, and saves evidence in work/R16-T014/.
Exits non-zero on any assertion failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T014")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter7", "applied-labs", "r16-t014")

sys.path.insert(0, LAB_DIR)
from example import CONTEXT, TOKEN_OFFSETS, build_token_sequence, extract_span


def run_unit_tests():
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", LAB_DIR, "-p", "test_*.py", "-v"]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    test_log = proc.stdout + proc.stderr
    with open(os.path.join(WORK_DIR, "test-results.txt"), "w") as f:
        f.write(test_log)
    return proc.returncode == 0, test_log


def collect_tool_versions():
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], capture_output=True, text=True)
    git_ver = git_proc.stdout.strip()
    branch_proc = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip()
    content = (
        f"Assignment: R16-T014\n"
        f"Student: Janhavi Sharma\n"
        f"Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python: {python_ver}\n"
        f"Git: {git_ver}\n"
        f"Check command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter7/applied-labs/r16-t014 -p 'test_*.py'\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(content)
    return content


def evaluate_fixtures():
    inputs_path = os.path.join(WORK_DIR, "inputs.json")
    with open(inputs_path) as f:
        fixtures = json.load(f)

    lines = ["Assignment: R16-T014", "Comparison: Expected vs Actual Results", "=" * 60]
    all_passed = True

    for fix in fixtures:
        fid = fix["id"]
        start = fix["start"]
        end = fix["end"]
        exp_answer = fix["expected_answer"]
        exp_exc = fix["expected_exception"]

        lines.append(f"\nScenario: {fid}")
        lines.append(f"Input: span({start}, {end}), context={repr(CONTEXT)}")

        if exp_exc:
            try:
                extract_span(CONTEXT, start, end, token_offsets=TOKEN_OFFSETS)
                lines.append(f"Expected Exception: {exp_exc}")
                lines.append("Actual: No exception raised — FAIL")
                all_passed = False
            except (ValueError, IndexError) as e:
                lines.append(f"Expected Exception: {exp_exc}")
                lines.append(f"Actual Exception: {type(e).__name__}: {e}")
                lines.append("Status: PASS")
        else:
            state = extract_span(CONTEXT, start, end, token_offsets=TOKEN_OFFSETS)
            actual_answer = state["answer"]
            char_start = state["char_start"]
            char_end = state["char_end"]
            lines.append(f"Expected answer: {repr(exp_answer)}")
            lines.append(f"Actual answer:   {repr(actual_answer)}")
            lines.append(f"char range: [{char_start}, {char_end})")
            # Invariant assertions
            assert state["validated"], "validated flag must be True"
            assert char_end > char_start, "char_end > char_start invariant violated"
            assert actual_answer == CONTEXT[char_start:char_end], "answer-slice invariant violated"
            if actual_answer == exp_answer:
                lines.append("Status: PASS")
            else:
                lines.append("Status: FAIL")
                all_passed = False

    # Deliberate wrong result demonstration
    lines.append("\n" + "=" * 60)
    lines.append("Deliberate Wrong Result Demonstration:")
    state = extract_span(CONTEXT, 0, 0, token_offsets=TOKEN_OFFSETS)
    if state["answer"] != "wrote":
        lines.append(
            f"Wrong expected 'wrote' vs actual {repr(state['answer'])}: "
            "mismatch correctly detected — PASS"
        )
    else:
        lines.append("Deliberate wrong test did not detect mismatch — FAIL")
        all_passed = False

    lines.append("\n" + "=" * 60)
    lines.append(f"Final Status: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")

    with open(os.path.join(WORK_DIR, "comparison-results.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")

    return all_passed, "\n".join(lines)


def main():
    print("Starting verification for R16-T014...")
    os.makedirs(WORK_DIR, exist_ok=True)

    collect_tool_versions()
    print("Collected tool versions.")

    unit_ok, unit_log = run_unit_tests()
    if not unit_ok:
        print("ERROR: Unit tests failed!", file=sys.stderr)
        print(unit_log, file=sys.stderr)
        sys.exit(1)
    print("Unit tests passed.")

    eval_ok, summary = evaluate_fixtures()
    if not eval_ok:
        print("ERROR: Fixture evaluation failed!", file=sys.stderr)
        print(summary, file=sys.stderr)
        sys.exit(1)
    print("All fixtures verified successfully.")
    print("\nAll checks passed! Results saved in work/R16-T014/")
    sys.exit(0)


if __name__ == "__main__":
    main()
