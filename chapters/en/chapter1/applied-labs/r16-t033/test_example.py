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
    for prompt, budget, retained, removed in mod.EXPECTED:
        direct = mod.check_budget(prompt, budget)
        counted = mod.check_budget_by_counting(prompt, budget)
        check(direct["retained"] == retained, f"direct retained wrong for {repr(prompt)}, {budget}")
        check(direct["removed"] == removed, f"direct removed wrong for {repr(prompt)}, {budget}")
        check(direct == counted, f"the two approaches disagree for {repr(prompt)}, {budget}")
    for function in (mod.check_budget, mod.check_budget_by_counting):
        try:
            function("hello", -1)
        except ValueError:
            pass
        else:
            raise AssertionError("a negative budget must be rejected")


class BudgetTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_issue_example(self):
        result = example.check_budget("one two three four", 3)
        self.assertEqual(result["retained"], ["one", "two", "three"])
        self.assertEqual(result["removed"], 1)

    def test_tokenizer_is_labelled(self):
        self.assertIn("teaching approximation", example.TOKENIZER_NOTE)

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated("tokens[:budget]", "tokens[:budget + 1]")
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
