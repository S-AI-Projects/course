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
    check(mod.check_table(mod.decide) == [], "the published decisions must match the code")
    results = [mod.evaluate(mod.STAGE_FOR_SYMPTOM[:size]) for size in (1, 2, 3)]
    check([r["correct"] for r in results] == [3, 4, 5], "correct counts must be 3, 4, 5")
    check([r["comparisons"] for r in results] == [4, 7, 9], "comparisons must be 4, 7, 9")


class EvaluationTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_changed_decision_is_caught(self):
        table = [dict(case) for case in example.DECISION_TABLE]
        table[2]["expected"] = "tokenizer"
        self.assertNotEqual(example.check_table(example.decide, table), [])

    def test_readme_publishes_the_same_table(self):
        self.assertIn(example.markdown_table(), readme_text())

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated('return "unknown_symptom", comparisons',
                             'return "tokenizer", comparisons')
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
