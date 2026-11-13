#!/usr/bin/env python3
"""
Verification check script for R16-T021.
Verifies contract assertions, runs test discovery, records tool versions,
and saves inputs, expected vs actual outputs into work/R16-T021/.
Exits non-zero if any assertion or test fails.
"""

import json
import os
import platform
import subprocess
import sys
import unittest

# Ensure lab directory is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LAB_DIR = os.path.join(REPO_ROOT, "chapters/en/chapter6/applied-labs/r16-t021")
WORK_DIR = os.path.join(REPO_ROOT, "work/R16-T021")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import DEFAULT_VOCAB, segment_word, tokenize_text


def run_checks() -> None:
    print("=== Running Checks for Task R16-T021 ===")

    # 1. Collect environment and tool versions
    env_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "task_id": "R16-T021",
        "branch": "student/e26b07f0747/R16-T021",
    }
    print(f"Python Version: {env_info['python_version']}")
    print(f"Platform: {env_info['platform']}")

    # 2. Test Cases (Input, Expected)
    test_cases = [
        {
            "description": "Required fixture: playing -> ['play', '##ing']",
            "input": "playing",
            "expected": ["play", "##ing"],
        },
        {
            "description": "Required fixture: cat -> ['cat']",
            "input": "cat",
            "expected": ["cat"],
        },
        {
            "description": "Required fixture: dog -> ['[UNK]']",
            "input": "dog",
            "expected": ["[UNK]"],
        },
        {
            "description": "Partial match with missing suffix: played -> ['[UNK]']",
            "input": "played",
            "expected": ["[UNK]"],
        },
        {
            "description": "Partial match with missing suffix: cats -> ['[UNK]']",
            "input": "cats",
            "expected": ["[UNK]"],
        },
        {
            "description": "Compound without ##: playcat -> ['[UNK]']",
            "input": "playcat",
            "expected": ["[UNK]"],
        },
        {
            "description": "Boundary: empty string -> []",
            "input": "",
            "expected": [],
        },
        {
            "description": "Multi-word text: 'playing cat dog' -> ['play', '##ing', 'cat', '[UNK]']",
            "input": "playing cat dog",
            "expected": ["play", "##ing", "cat", "[UNK]"],
            "type": "text",
        },
    ]

    results = []
    for tc in test_cases:
        if tc.get("type") == "text":
            actual = tokenize_text(tc["input"], DEFAULT_VOCAB)
        else:
            actual = segment_word(tc["input"], DEFAULT_VOCAB)

        passed = actual == tc["expected"]
        record = {
            "description": tc["description"],
            "input": tc["input"],
            "expected": tc["expected"],
            "actual": actual,
            "status": "PASS" if passed else "FAIL",
        }
        results.append(record)
        print(f"[{record['status']}] {tc['description']} | Actual: {actual}")
        if not passed:
            print(f"ERROR: Assertion failed for input '{tc['input']}'!")
            sys.exit(1)

    # 3. Deliberate failure scenario check (ensures checks are non-vacuous)
    print("\nVerifying that deliberate wrong expectation triggers failure...")
    deliberate_wrong = ["wrong_token"]
    actual_playing = segment_word("playing", DEFAULT_VOCAB)
    if actual_playing == deliberate_wrong:
        print("ERROR: Deliberate failure test was expected to differ but matched!")
        sys.exit(1)
    print("Deliberate failure test passed: wrong result successfully rejected.")

    # 4. Run automated test discovery via unittest
    print("\nRunning test discovery: python3 -m unittest discover...")
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

    # 5. Persist evidence to work/R16-T021/
    os.makedirs(WORK_DIR, exist_ok=True)
    report_data = {
        "environment": env_info,
        "contract_checks": results,
        "deliberate_failure_check": "PASS (wrong expectation correctly detected)",
        "unittest_exit_code": test_proc.returncode,
        "unittest_output": test_proc.stderr,
    }

    json_path = os.path.join(WORK_DIR, "results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    report_path = os.path.join(WORK_DIR, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== TASK R16-T021 VERIFICATION REPORT ===\n\n")
        f.write(f"Task: R16-T021\n")
        f.write(f"Branch: {env_info['branch']}\n")
        f.write(f"Python Version: {env_info['python_version']}\n")
        f.write(f"Platform: {env_info['platform']}\n\n")
        f.write("--- Contract Checks ---\n")
        for r in results:
            f.write(
                f"[{r['status']}] Input: '{r['input']}' | Expected: {r['expected']} | Actual: {r['actual']}\n"
            )
        f.write("\n--- Unittest Output ---\n")
        f.write(test_proc.stderr)
        f.write(f"\nUnittest Return Code: {test_proc.returncode}\n")
        f.write("\nALL CHECKS PASSED.\n")

    print(f"\nSaved check results to {json_path} and {report_path}")
    print("All checks completed successfully with exit code 0.")


if __name__ == "__main__":
    run_checks()
