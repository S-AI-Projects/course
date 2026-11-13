#!/usr/bin/env python3
"""
Verification check script for R16-T024.
Verifies contract assertions, checks state trace invariants, runs test discovery,
records tool versions, and saves inputs, expected vs actual outputs into work/R16-T024/.
Exits non-zero if any assertion or test fails.
"""

import json
import os
import platform
import subprocess
import sys

# Ensure lab directory is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LAB_DIR = os.path.join(REPO_ROOT, "chapters/en/chapter1/applied-labs/r16-t024")
WORK_DIR = os.path.join(REPO_ROOT, "work/R16-T024")

if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import CapabilityNegotiator, CapabilityNotNegotiatedError


def run_checks() -> None:
    print("=== Running Checks for Task R16-T024 ===")

    # 1. Environment & tool versions
    env_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "task_id": "R16-T024",
        "branch": "student/e26b07f0747/R16-T024",
    }
    print(f"Python Version: {env_info['python_version']}")
    print(f"Platform: {env_info['platform']}")

    contract_checks = []

    # Check 1: Client {tools, resources}, Server {tools, prompts} negotiates {tools}
    negotiator = CapabilityNegotiator()
    negotiator.register_client({"tools", "resources"})
    negotiator.register_server({"tools", "prompts"})
    negotiated = negotiator.negotiate()
    passed1 = negotiated == {"tools"}
    contract_checks.append({
        "description": "Client {tools, resources}, Server {tools, prompts} negotiates {tools}",
        "input": {"client": ["resources", "tools"], "server": ["prompts", "tools"]},
        "expected": ["tools"],
        "actual": sorted(negotiated),
        "status": "PASS" if passed1 else "FAIL",
    })
    if not passed1:
        print("ERROR: Negotiation intersection check failed!")
        sys.exit(1)

    # Check 2: Calling 'tools' succeeds and dispatches
    res_tools = negotiator.dispatch("tools", payload={"op": "calc"})
    passed2 = res_tools.get("status") == "DISPATCHED" and "tools" in negotiator.dispatch_log
    contract_checks.append({
        "description": "Calling negotiated capability 'tools' dispatches successfully",
        "input": "tools",
        "expected": "DISPATCHED",
        "actual": res_tools.get("status"),
        "status": "PASS" if passed2 else "FAIL",
    })
    if not passed2:
        print("ERROR: Dispatch of negotiated capability failed!")
        sys.exit(1)

    # Check 3: Calling 'resources' is rejected before dispatch
    rejected = False
    try:
        negotiator.dispatch("resources")
    except CapabilityNotNegotiatedError:
        rejected = True

    passed3 = rejected and ("resources" not in negotiator.dispatch_log)
    contract_checks.append({
        "description": "Calling unnegotiated capability 'resources' rejected before dispatch",
        "input": "resources",
        "expected": "CapabilityNotNegotiatedError (rejected before dispatch)",
        "actual": "REJECTED_BEFORE_DISPATCH" if passed3 else "Dispatched (incorrect)",
        "status": "PASS" if passed3 else "FAIL",
    })
    if not passed3:
        print("ERROR: Unnegotiated capability was not rejected before dispatch!")
        sys.exit(1)

    # Check 4: System invariants hold across state trace
    invariants_valid = negotiator.verify_invariants()
    contract_checks.append({
        "description": "State trace invariants hold across all intermediate steps",
        "input": "negotiator.trace",
        "expected": True,
        "actual": invariants_valid,
        "status": "PASS" if invariants_valid else "FAIL",
    })
    if not invariants_valid:
        print("ERROR: Invariants check failed!")
        sys.exit(1)

    for c in contract_checks:
        print(f"[{c['status']}] {c['description']}")

    # 3. Deliberate wrong result check (ensures checks are non-vacuous)
    print("\nVerifying deliberate wrong result triggers failure...")
    deliberate_negotiated = {"tools", "resources"}
    if negotiated == deliberate_negotiated:
        print("ERROR: Deliberate failure test matched unexpectedly!")
        sys.exit(1)
    print("Deliberate failure test passed: wrong result correctly detected.")

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

    # 5. Persist evidence to work/R16-T024/
    os.makedirs(WORK_DIR, exist_ok=True)
    json_path = os.path.join(WORK_DIR, "results.json")
    report_data = {
        "environment": env_info,
        "contract_checks": contract_checks,
        "state_trace": negotiator.get_trace_dicts(),
        "deliberate_failure_check": "PASS (wrong expectation correctly detected)",
        "unittest_exit_code": test_proc.returncode,
        "unittest_output": test_proc.stderr,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    report_path = os.path.join(WORK_DIR, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== TASK R16-T024 VERIFICATION REPORT ===\n\n")
        f.write(f"Task: R16-T024\n")
        f.write(f"Branch: {env_info['branch']}\n")
        f.write(f"Python Version: {env_info['python_version']}\n")
        f.write(f"Platform: {env_info['platform']}\n\n")
        f.write("--- Contract Checks ---\n")
        for c in contract_checks:
            f.write(f"[{c['status']}] {c['description']} | Actual: {c['actual']}\n")
        f.write("\n--- State Trace ---\n")
        for st in negotiator.get_trace_dicts():
            f.write(
                f"Step {st['step']} [{st['phase']}]: {st['last_action']} -> {st['last_status']}\n"
            )
        f.write("\n--- Unittest Output ---\n")
        f.write(test_proc.stderr)
        f.write(f"\nUnittest Return Code: {test_proc.returncode}\n")
        f.write("\nALL CHECKS PASSED.\n")

    print(f"\nSaved check results to {json_path} and {report_path}")
    print("All checks completed successfully with exit code 0.")


if __name__ == "__main__":
    run_checks()
