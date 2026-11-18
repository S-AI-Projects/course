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
    check(mod.optimizer_steps(10, 4) == [4, 8, 10], "ten batches with accumulation 4")
    check(mod.optimizer_steps(0, 4) == [], "zero batches produce no step")
    check(mod.optimizer_steps(3, 4) == [3], "a lone partial group still steps")
    check(mod.optimizer_steps(8, 4) == [4, 8], "no partial group when it divides evenly")
    check(mod.optimizer_steps(10, 4, "drop") == [4, 8], "drop skips the leftover group")
    results = mod.run_questions()
    check(len(results) == 3, "three applied questions")
    check(all(passed for _, passed in results), "every question check must pass")


class AccumulationTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_bad_input_is_rejected(self):
        with self.assertRaises(ValueError):
            example.optimizer_steps(-1, 4)
        with self.assertRaises(ValueError):
            example.optimizer_steps(10, 0)
        with self.assertRaises(ValueError):
            example.optimizer_steps(10, 4, "keep")

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated("num_batches % accumulation != 0", "num_batches % accumulation == 0")
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
