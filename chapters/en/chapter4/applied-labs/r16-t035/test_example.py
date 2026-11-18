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
    hub = mod.make_offline_hub()
    check(mod.check_table(mod.decide, hub) == [], "the published decisions must match the code")
    new = {"repo_id": "student/new", "has_weights": True}
    check(mod.decide(new, hub) == "create_repo_and_push", "new repo with weights")
    check(mod.decide({"repo_id": "student/existing-model", "has_weights": True}, hub)
          == "push_to_existing_repo", "existing repo")
    check(mod.decide({"repo_id": "student/x"}, hub) == "need_more_information",
          "missing weights flag")
    check(mod.decide(new, mod.make_offline_hub(user=None)) == "log_in_first", "logged out")
    check(mod.decide({"repo_id": "student/new", "has_weights": False}, hub)
          == "nothing_to_upload", "no weights")


class SharingTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_any_callable_can_be_the_hub(self):
        def stub(action, repo_id=None):
            return "someone" if action == "whoami" else False
        facts = {"repo_id": "a/b", "has_weights": True}
        self.assertEqual(example.decide(facts, stub), "create_repo_and_push")

    def test_changed_decision_is_caught(self):
        table = [dict(case) for case in example.DECISION_TABLE]
        table[0]["expected"] = "push_to_existing_repo"
        self.assertNotEqual(example.check_table(example.decide, example.make_offline_hub(), table), [])

    def test_readme_publishes_the_same_table(self):
        self.assertIn(example.markdown_table(), readme_text())

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated('if hub("whoami") is None:', 'if hub("whoami") is not None:')
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
