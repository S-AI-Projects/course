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
    check(mod.retrieve("red apple") == [("A", 2), ("B", 1)], "red apple must rank A before B")
    check(mod.retrieve("ocean") == [], "ocean must return no match")
    check(mod.retrieve("apple") == [("A", 1), ("B", 1)], "a tie is broken by document id")
    check(mod.retrieve("") == [], "an empty query matches nothing")
    check(mod.retrieve("RED") == [("A", 1)], "matching ignores case")
    try:
        mod.retrieve(42)
    except TypeError:
        pass
    else:
        raise AssertionError("a non-string query must raise TypeError")


class RetrieverTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_ties_use_document_id(self):
        docs = {"Z": "x", "B": "x"}
        self.assertEqual(example.retrieve("x", docs), [("B", 1), ("Z", 1)])

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated("score > 0", "score >= 0")
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
