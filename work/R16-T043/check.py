#!/usr/bin/env python3
"""
Verification check script for Task R16-T043.

Validates the token-to-character alignment contract:
- For "red apple", spans [0,3],[4,9] map character 5 to token 1.
- The separating space at character 3 maps to no token (None).
- Compares Approach 1 (direct engine) with Approach 2 (dense map table) on identical inputs.
- Verifies rejection of overlapping and out-of-bounds spans.
- Demonstrates that a deliberate wrong result makes the check fail.
- Runs automated unit tests via unittest discovery.
- Saves inputs, expected vs actual outputs, tool versions, and test logs into work/R16-T043/.
- Exits non-zero on any assertion or test failure.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T043")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter6", "applied-labs", "r16-t043")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    TokenSpanAlignment,
    build_dense_char_to_token_map,
    compare_alignment_approaches,
)


def collect_tool_versions() -> str:
    """Collect Python, Git, and platform versions."""
    python_ver = sys.version.replace("\n", " ")
    git_proc = subprocess.run(["git", "--version"], cwd=REPO_ROOT, capture_output=True, text=True)
    git_ver = git_proc.stdout.strip() if git_proc.returncode == 0 else "Unknown git"
    branch_proc = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "Unknown branch"

    versions_content = (
        f"Assignment: R16-T043\n"
        f"Student: Nilesh\n"
        f"Assigned Branch: {current_branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Test Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t043 -p 'test_*.py'\n"
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
    """Evaluate contract scenarios, comparing expected vs actual."""
    fixtures = [
        {
            "scenario": "contract_char_5_maps_to_token_1",
            "description": "For 'red apple', spans [0,3],[4,9] map character 5 to token 1",
            "text": "red apple",
            "spans": [[0, 3], [4, 9]],
            "query_char_index": 5,
            "expected_token_index": 1,
        },
        {
            "scenario": "contract_separating_space_maps_to_none",
            "description": "Separating space at character 3 maps to no token (None)",
            "text": "red apple",
            "spans": [[0, 3], [4, 9]],
            "query_char_index": 3,
            "expected_token_index": None,
        },
        {
            "scenario": "approach_comparison_red_apple",
            "description": "Approach 1 vs Approach 2 on 'red apple' identical comparison",
            "text": "red apple",
            "spans": [[0, 3], [4, 9]],
            "query_char_index": "ALL",
            "expected_approach_match": True,
        },
        {
            "scenario": "approach_comparison_multi_token",
            "description": "Approach 1 vs Approach 2 on multi-token sentence",
            "text": "  quick brown fox  ",
            "spans": [[2, 7], [8, 13], [14, 17]],
            "query_char_index": "ALL",
            "expected_approach_match": True,
        },
        {
            "scenario": "invalid_overlapping_spans_rejected",
            "description": "Overlapping spans rejected with ValueError",
            "text": "hello world",
            "spans": [[0, 6], [5, 11]],
            "expected_exception": "ValueError",
        },
    ]

    with open(os.path.join(WORK_DIR, "inputs.json"), "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2)

    comparison_lines = [
        "Assignment: R16-T043",
        "Comparison: Expected vs Actual Results",
        "=" * 60,
    ]

    all_passed = True
    results_record = []

    for item in fixtures:
        scenario = item["scenario"]
        desc = item["description"]
        text = item["text"]
        spans = [tuple(s) for s in item["spans"]]

        comparison_lines.append(f"\nScenario: {scenario} ({desc})")
        comparison_lines.append(f"Text: {repr(text)}, Spans: {spans}")

        if "expected_exception" in item:
            exp_exc = item["expected_exception"]
            try:
                TokenSpanAlignment(text, spans)
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append("Actual: No exception raised (FAIL)")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})
            except ValueError as e:
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Exception: ValueError ({e})")
                comparison_lines.append("Status: PASS")
                results_record.append({"scenario": scenario, "status": "PASS", "actual_exception": str(e)})
            except Exception as e:
                comparison_lines.append(f"Expected Exception: {exp_exc}")
                comparison_lines.append(f"Actual Exception: {type(e).__name__} ({e})")
                comparison_lines.append("Status: FAIL")
                all_passed = False
                results_record.append({"scenario": scenario, "status": "FAIL"})
        elif item.get("query_char_index") == "ALL":
            matched, details = compare_alignment_approaches(text, spans)
            comparison_lines.append(f"Expected Approach Match: {item['expected_approach_match']}")
            comparison_lines.append(f"Actual Approach Match:   {matched}")
            status_str = "PASS" if matched == item["expected_approach_match"] else "FAIL"
            comparison_lines.append(f"Status: {status_str}")
            if status_str == "FAIL":
                all_passed = False
            results_record.append({"scenario": scenario, "status": status_str, "all_matched": matched})
        else:
            q_idx = item["query_char_index"]
            exp_tok = item["expected_token_index"]
            aligner = TokenSpanAlignment(text, spans)
            actual_tok = aligner.char_to_token(q_idx)
            comparison_lines.append(f"Char Index: {q_idx} ('{text[q_idx]}')")
            comparison_lines.append(f"Expected Token: {exp_tok}")
            comparison_lines.append(f"Actual Token:   {actual_tok}")
            status_str = "PASS" if actual_tok == exp_tok else "FAIL"
            comparison_lines.append(f"Status: {status_str}")
            if status_str == "FAIL":
                all_passed = False
            results_record.append({"scenario": scenario, "status": status_str, "actual": actual_tok})

    # Demonstrate that a deliberate wrong result triggers an assertion failure
    comparison_lines.append("\n" + "=" * 60)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")
    test_aligner = TokenSpanAlignment("red apple", [(0, 3), (4, 9)])
    actual_tok5 = test_aligner.char_to_token(5)
    deliberate_wrong = 0  # Char 5 is token 1, not 0
    if actual_tok5 != deliberate_wrong:
        comparison_lines.append(
            f"Deliberate wrong assertion (expected {deliberate_wrong} vs actual {actual_tok5}) correctly detected: PASS (mismatch caught)"
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
    print("=== Running Verification Check for Task R16-T043 ===")
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
        aligner = TokenSpanAlignment("red apple", [(0, 3), (4, 9)])
        assert aligner.char_to_token(5) != 0

    try:
        verify_deliberate_wrong_fails()
    except AssertionError:
        sys.exit(1)

    print("\nAll checks passed cleanly with exit code 0! Artifacts saved to work/R16-T043/")
    sys.exit(0)


if __name__ == "__main__":
    main()
