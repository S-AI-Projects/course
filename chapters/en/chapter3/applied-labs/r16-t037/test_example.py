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
    manifest = {"encoder": 100, "head": 20}
    result = mod.account_parameters(manifest, ["encoder"])
    check(result["total"] == 120, "total must be 120")
    check(result["trainable"] == 20, "trainable must be 20 with the encoder frozen")
    check(result["frozen"] == 100, "frozen must be 100")
    check(result["unmatched_prefixes"] == [], "encoder matches, so nothing is unmatched")
    missing = mod.account_parameters(manifest, ["encoder", "decoder"])
    check(missing["unmatched_prefixes"] == ["decoder"], "an unmatched prefix must be reported")
    check(mod.account_parameters(manifest)["trainable"] == 120, "no freeze means all trainable")


class ParameterTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_bad_size_is_rejected(self):
        for bad in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                example.account_parameters({"encoder": bad})

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated('"trainable": total - frozen', '"trainable": total')
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
