import types
import unittest
from pathlib import Path

import example


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def load_mutated(old, new):
    """Load a copy of example.py with ONE deliberate change, to prove the checks can fail."""
    source = Path(example.__file__).read_text(encoding="utf-8")
    if old not in source:
        raise RuntimeError("mutation target not found: " + old)
    module = types.ModuleType("example_mutated")
    exec(compile(source.replace(old, new), "example_mutated.py", "exec"), module.__dict__)
    return module


def readme_text():
    return Path(example.__file__).with_name("README.md").read_text(encoding="utf-8")



def run_expectations(mod):
    results = mod.run_batch(mod.FIXTURE)
    check([r["status"] for r in results] == ["ok", "error", "error", "ok", "ok"],
          "statuses must be ok, error, error, ok, ok")
    check(results[0]["retained"] == ["one", "two", "three"] and results[0]["removed"] == 1,
          "budget 3 must retain three tokens and remove one")
    check("budget" in results[1]["error"], "the negative-budget error must mention the budget")
    check("prompt is missing" in results[2]["error"], "the missing-prompt error must say so")
    check(results[3]["retained"] == ["a", "b"], "the run must recover on the next valid input")
    check(results[4]["retained"] == [] and results[4]["removed"] == 0,
          "empty input retains nothing")


class RecoveryTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_direct_calls_raise(self):
        with self.assertRaises(ValueError):
            example.preflight("hello", -1)
        with self.assertRaises(ValueError):
            example.preflight(None, 3)

    def test_tokenizer_is_labelled(self):
        self.assertIn("teaching approximation", example.TOKENIZER_NOTE)

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated("budget < 0", "budget < -1")
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
