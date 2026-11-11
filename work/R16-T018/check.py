"""check.py — Automated verification check for Task R16-T018.

Validates the WordPiece greedy subword segmentation, executes unit tests,
demonstrates failure handling and state recovery across a mixed stream,
verifies that deliberate wrong results trigger failure, and records evidence in work/R16-T018/.
Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T018")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter6", "applied-labs", "r16-t018")

sys.path.insert(0, LAB_DIR)
from example import WordPieceTokenizer


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


def evaluate_fixtures_and_recovery() -> bool:
    """Evaluate contract fixtures from inputs.json and verify stream recovery."""
    with open(os.path.join(WORK_DIR, "inputs.json"), "r") as f:
        data = json.load(f)

    tokenizer = WordPieceTokenizer()
    comparison_lines = [
        f"Assignment: {data.get('task', 'R16-T018')}",
        f"Description: {data.get('description', '')}",
        "=" * 70,
        "Vocabulary Contract & Failure Recovery Verification",
        "=" * 70,
    ]

    all_ok = True

    # 1. Evaluate individual fixtures
    for name, item in data["fixtures"].items():
        raw_input = item["input"]
        expected_tokens = item["expected_tokens"]
        expected_status = item["expected_status"]

        result = tokenizer.tokenize_safe(raw_input)
        match_status = (result.status == expected_status)
        match_tokens = (result.tokens == expected_tokens)
        passed = match_status and match_tokens

        if not passed:
            all_ok = False

        status = "PASS" if passed else "FAIL"
        comparison_lines.append(f"\n[Fixture: {name}]")
        comparison_lines.append(f"  Input:           {raw_input!r}")
        comparison_lines.append(f"  Expected Status: {expected_status} | Actual: {result.status}")
        comparison_lines.append(f"  Expected Tokens: {expected_tokens} | Actual: {result.tokens}")
        if result.error_message:
            comparison_lines.append(f"  Diagnostic:      {result.error_message}")
        comparison_lines.append(f"  Status:          {status}")

    # 2. Sequential Stream Failure & Recovery Demonstration
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Sequential Stream Failure and Recovery Demonstration:")

    stream = ["cat", None, "playing", 12345, "dog"]
    stream_results = tokenizer.tokenize_stream(stream)

    expected_stream_statuses = ["SUCCESS", "ERROR", "SUCCESS", "ERROR", "SUCCESS"]
    stream_passed = True

    for i, (item, res) in enumerate(zip(stream, stream_results)):
        exp_status = expected_stream_statuses[i]
        matched = (res.status == exp_status)
        if not matched:
            stream_passed = False
            all_ok = False
        comparison_lines.append(
            f"  Step {i+1}: input={item!r:<10} -> status={res.status:<7} "
            f"(tokens={res.tokens}) {'[RECOVERED]' if i in (2, 4) else ''}"
        )

    comparison_lines.append(f"  Stream Recovery Verified: {'PASS' if stream_passed else 'FAIL'}")

    # 3. Deliberate wrong result check
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Deliberate Wrong Result Test Demonstration:")

    actual_playing = tokenizer.encode_word("playing")
    wrong_expectation = ["play", "WRONG_TOKEN"]
    detected_mismatch = (actual_playing != wrong_expectation)

    if detected_mismatch:
        comparison_lines.append(
            f"  Deliberate wrong expectation {wrong_expectation} correctly triggers mismatch: PASS"
        )
    else:
        comparison_lines.append("  Deliberate wrong expectation NOT detected: FAIL")
        all_ok = False

    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append(f"Final Status: {'ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED'}")

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
        f"Assignment: R16-T018\n"
        f"Student: Janhavi Sharma\n"
        f"Assigned Branch: {branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Check Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t018 -p 'test_*.py'\n"
        f"Evidence Check Command:\n"
        f"  python3 work/R16-T018/check.py\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(content)
    print("Tool versions recorded.")


def main() -> None:
    os.makedirs(WORK_DIR, exist_ok=True)
    print("Starting automated verification for Task R16-T018...")

    collect_tool_versions()

    if not run_unit_tests():
        sys.exit(1)

    if not evaluate_fixtures_and_recovery():
        print("ERROR: Fixture evaluations or stream recovery failed!", file=sys.stderr)
        sys.exit(1)

    print("ALL CHECKS PASSED cleanly — Task R16-T018")
    sys.exit(0)


if __name__ == "__main__":
    main()
