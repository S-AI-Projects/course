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
    result = mod.trace_preflight("one two three four", 3)
    check(result["retained"] == ["one", "two", "three"], "budget 3 must retain three tokens")
    check(result["removed"] == 1, "budget 3 must report one removed token")
    check(mod.invariant_problems(result, 3) == [], "the invariant must hold for the example")
    empty = mod.trace_preflight("", 3)
    check(empty["retained"] == [] and empty["removed"] == 0 and empty["steps"] == [],
          "empty input retains nothing")
    tokens = "one two three four".split()
    for budget in range(0, 7):
        res = mod.trace_preflight("one two three four", budget)
        check(mod.invariant_problems(res, budget) == [], f"invariant broken at budget {budget}")
        check(res["retained"] == tokens[:budget], f"final output wrong at budget {budget}")
        check(res["removed"] == max(0, len(tokens) - budget), f"removed wrong at budget {budget}")
    try:
        mod.trace_preflight("hello", -1)
    except ValueError:
        pass
    else:
        raise AssertionError("a negative budget must be rejected")


class TraceTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_tokenizer_is_labelled(self):
        self.assertIn("teaching approximation", example.TOKENIZER_NOTE)

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated("len(retained) < budget", "len(retained) <= budget")
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
