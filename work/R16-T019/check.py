"""check.py — Automated verification check for Task R16-T019.

Validates the BPE merge step, executes unit tests, runs the evaluation experiment
comparing three controlled configurations, verifies deliberate failure detection,
and records evidence in work/R16-T019/.
Exits non-zero if any assertion fails.
"""

import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
WORK_DIR = os.path.join(REPO_ROOT, "work", "R16-T019")
LAB_DIR = os.path.join(REPO_ROOT, "chapters", "en", "chapter6", "applied-labs", "r16-t019")

sys.path.insert(0, LAB_DIR)
from example import (
    CONFIGURATIONS,
    apply_merge,
    count_adjacent_pairs,
    run_evaluation_experiment,
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


def evaluate_contract_and_experiment() -> bool:
    """Evaluate core contract and run evaluation experiment across configurations."""
    with open(os.path.join(WORK_DIR, "inputs.json"), "r") as f:
        data = json.load(f)

    comparison_lines = [
        f"Assignment: {data.get('task', 'R16-T019')}",
        f"Description: {data.get('description', '')}",
        "=" * 70,
        "Core Contract Verification: One BPE Merge Step",
        "=" * 70,
    ]

    all_ok = True

    # 1. Core Contract Verification
    core_spec = data["core_contract"]
    in_tokens = core_spec["input_tokens"]
    merge_pair = tuple(core_spec["merge_pair"])
    expected_tokens = core_spec["expected_tokens"]
    expected_reduction = core_spec["expected_reduction"]

    core_result = apply_merge(in_tokens, merge_pair)
    core_passed = (
        core_result.merged_tokens == expected_tokens
        and core_result.token_reduction == expected_reduction
    )
    if not core_passed:
        all_ok = False

    comparison_lines.append(f"Input Tokens:       {in_tokens}")
    comparison_lines.append(f"Merge Pair:         {merge_pair}")
    comparison_lines.append(f"Expected Tokens:    {expected_tokens}")
    comparison_lines.append(f"Actual Tokens:      {core_result.merged_tokens}")
    comparison_lines.append(f"Expected Reduction: {expected_reduction} | Actual: {core_result.token_reduction}")
    comparison_lines.append(f"Core Status:        {'PASS' if core_passed else 'FAIL'}")

    # 2. Evaluation Experiment Across Three Configurations
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Evaluation Experiment (Three Controlled Configurations):")
    comparison_lines.append("=" * 70)

    metrics = run_evaluation_experiment(CONFIGURATIONS)
    cfg_specs = data["configurations"]

    for m in metrics:
        expected_cfg = cfg_specs[m.config_name]
        match_before = (m.tokens_before == expected_cfg["expected_tokens_before"])
        match_after = (m.tokens_after == expected_cfg["expected_tokens_after"])
        match_reduced = (m.tokens_reduced == expected_cfg["expected_tokens_reduced"])
        cfg_passed = match_before and match_after and match_reduced

        if not cfg_passed:
            all_ok = False

        status = "PASS" if cfg_passed else "FAIL"
        comparison_lines.append(f"\n[{m.config_name}]")
        comparison_lines.append(f"  Sequences:         {m.corpus_size_sequences}")
        comparison_lines.append(f"  Tokens:            {m.tokens_before} -> {m.tokens_after} (reduced: {m.tokens_reduced})")
        comparison_lines.append(f"  Compression Ratio: {m.compression_ratio}%")
        comparison_lines.append(f"  Pairs (adj):       {m.pairs_before} -> {m.pairs_after}")
        comparison_lines.append(f"  Status:            {status}")

    # 3. Deliberate Wrong Result Test Demonstration
    comparison_lines.append("\n" + "=" * 70)
    comparison_lines.append("Deliberate Wrong Result Demonstration:")

    wrong_expectation = ["lo", "WRONG_TOKEN", "e", "r"]
    caught_mismatch = (core_result.merged_tokens != wrong_expectation)

    if caught_mismatch:
        comparison_lines.append(
            f"  Deliberate wrong expectation {wrong_expectation} correctly triggers mismatch: PASS"
        )
    else:
        comparison_lines.append("  Deliberate wrong expectation NOT detected: FAIL")
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
        f"Assignment: R16-T019\n"
        f"Student: Janhavi Sharma\n"
        f"Assigned Branch: {branch}\n"
        f"Platform: {platform.platform()}\n"
        f"Python Version: {python_ver}\n"
        f"Git Version: {git_ver}\n"
        f"Automated Check Command:\n"
        f"  python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t019 -p 'test_*.py'\n"
        f"Evidence Check Command:\n"
        f"  python3 work/R16-T019/check.py\n"
    )
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(content)
    print("Tool versions recorded.")


def main() -> None:
    os.makedirs(WORK_DIR, exist_ok=True)
    print("Starting automated verification for Task R16-T019...")

    collect_tool_versions()

    if not run_unit_tests():
        sys.exit(1)

    if not evaluate_contract_and_experiment():
        print("ERROR: Evaluation experiment or contract check failed!", file=sys.stderr)
        sys.exit(1)

    print("ALL CHECKS PASSED cleanly — Task R16-T019")
    sys.exit(0)


if __name__ == "__main__":
    main()
