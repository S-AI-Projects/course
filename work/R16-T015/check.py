"""
check.py — Automated check for R16-T015
Runs unit tests and validates fixtures from inputs.json.
Exits non-zero if any assertion fails.
"""
import subprocess
import sys
import json
import os

# Navigate from work/R16-T015/check.py up two levels to repo root
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAB  = os.path.join(ROOT, "chapters", "en", "chapter5", "applied-labs", "r16-t015")
WORK = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, LAB)
from example import validate_manifest

def run_unit_tests():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover",
         "-s", LAB, "-p", "test_*.py", "-v"],
        capture_output=True, text=True
    )
    with open(os.path.join(WORK, "test-results.txt"), "w") as f:
        f.write(result.stdout)
        f.write(result.stderr)
    if result.returncode != 0:
        print("UNIT TESTS FAILED")
        print(result.stderr)
        sys.exit(1)
    print("Unit tests: PASSED")
    return result.stderr  # unittest writes to stderr

def check_fixtures():
    with open(os.path.join(WORK, "inputs.json")) as f:
        data = json.load(f)
    comparisons = []
    all_ok = True

    for name, fixture in data["fixtures"].items():
        result = validate_manifest(fixture["manifest"])
        exp = fixture["expected"]
        actual = {"ok": result.ok, "errors": result.errors}
        match = (result.ok == exp["ok"])
        comparisons.append({
            "fixture": name,
            "expected": exp,
            "actual": actual,
            "match": match
        })
        if not match:
            all_ok = False
            print(f"FIXTURE MISMATCH: {name}")
            print(f"  expected ok={exp['ok']}, got ok={result.ok}")

    with open(os.path.join(WORK, "comparison-results.txt"), "w") as f:
        for c in comparisons:
            f.write(f"Fixture: {c['fixture']}\n")
            f.write(f"  Expected : {c['expected']}\n")
            f.write(f"  Actual   : {c['actual']}\n")
            f.write(f"  Match    : {c['match']}\n\n")

    if not all_ok:
        sys.exit(1)
    print("Fixture checks: PASSED")

def write_tool_versions():
    version = sys.version
    with open(os.path.join(WORK, "tool-versions.txt"), "w") as f:
        f.write(f"python: {version}\n")
        f.write("external_packages: none (stdlib only)\n")
        f.write("task: R16-T015\n")
    print(f"Tool versions recorded: Python {version}")

if __name__ == "__main__":
    run_unit_tests()
    check_fixtures()
    write_tool_versions()
    print("ALL CHECKS PASSED — R16-T015")
    sys.exit(0)

