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
    check(mod.check_table(mod.decide_baseline) == [], "baseline must match the table")
    check(mod.check_table(mod.decide_refactored) == [], "refactored must match the table")
    combos = list(mod.fact_combinations())
    check(len(combos) == 27, "expected 27 fact combinations")
    for facts in combos:
        check(mod.decide_baseline(facts) == mod.decide_refactored(facts),
              f"before/after differ for {facts}")


class RefactorTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_extracted_responsibility(self):
        self.assertEqual(example.unknown_facts({"has_traceback": True}),
                         ["has_minimal_example", "has_versions"])

    def test_changed_decision_is_caught(self):
        table = [dict(case) for case in example.DECISION_TABLE]
        table[1]["expected"] = "post_question"
        self.assertNotEqual(example.check_table(example.decide_refactored, table), [])

    def test_readme_publishes_the_same_table(self):
        self.assertIn(example.markdown_table(), readme_text())

    def test_deliberate_wrong_version_fails(self):
        old = 'not (facts["has_traceback"] and facts["has_minimal_example"])'
        new = 'not (facts["has_traceback"] or facts["has_minimal_example"])'
        with self.assertRaises(AssertionError):
            run_expectations(load_mutated(old, new))


if __name__ == "__main__":
    unittest.main()
