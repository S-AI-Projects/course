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


import tempfile


def run_expectations(mod):
    with tempfile.TemporaryDirectory() as folder:
        good = mod.build_manifest(folder, mod.VALID_TRAIN, mod.VALID_VALIDATION)
        check(mod.validate_dataset(good) == {"train": 2, "validation": 1},
              "the valid two-split fixture must pass")

        no_label = [mod.VALID_TRAIN[0], '{"id": "a2", "text": "dull film"}']
        bad = mod.build_manifest(folder, no_label, mod.VALID_VALIDATION)
        try:
            mod.validate_dataset(bad)
        except mod.ManifestError as err:
            check("train line 2" in str(err), "error must name train line 2")
            check("'label'" in str(err), "error must name the label field")
        else:
            raise AssertionError("a missing label must fail")

        again = ['{"id": "a1", "text": "again", "label": "pos"}']
        dup = mod.build_manifest(folder, mod.VALID_TRAIN, again)
        try:
            mod.validate_dataset(dup)
        except mod.ManifestError as err:
            check("duplicate id 'a1'" in str(err), "error must name the duplicate id")
        else:
            raise AssertionError("duplicate ids across splits must fail")


class ManifestTest(unittest.TestCase):
    def test_expected_results(self):
        run_expectations(example)

    def test_manifest_needs_both_splits(self):
        with self.assertRaises(example.ManifestError):
            example.validate_dataset({"train": "train.jsonl"})

    def test_deliberate_wrong_version_fails(self):
        wrong = load_mutated("start=1", "start=0")
        with self.assertRaises(AssertionError):
            run_expectations(wrong)


if __name__ == "__main__":
    unittest.main()
