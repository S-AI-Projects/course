"""Unit tests for Applied Lab R16-T046: Prompt-Template Escaping & Equivalence Proof."""

import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    PROMPT_INJECTION_DISCLAIMER,
    BaselinePromptRenderer,
    RefactoredPromptRenderer,
    TemplateVariableBinder,
    prove_equivalence,
)


class TestPromptTemplateEscaping(unittest.TestCase):
    """Test suite validating template escaping, boundary cases, and refactor equivalence."""

    def setUp(self):
        self.template = "Instruction: Write an essay for {name} on {topic}."
        self.renderer = RefactoredPromptRenderer(self.template)
        self.baseline = BaselinePromptRenderer(self.template)

    def test_normal_template_rendering_with_name_and_topic(self):
        """Template with name and topic renders supplied values correctly."""
        result = self.renderer.render({"name": "Nilesh", "topic": "Transformers"})
        expected = "Instruction: Write an essay for Nilesh on Transformers."
        self.assertEqual(result, expected)

    def test_missing_topic_fails_with_keyerror(self):
        """Missing topic fails (raises KeyError)."""
        with self.assertRaises(KeyError):
            self.renderer.render({"name": "Nilesh"})

        with self.assertRaises(KeyError):
            self.baseline.render({"name": "Nilesh"})

    def test_braces_inside_user_data_remain_literal(self):
        """Braces inside user data remain literal and are not evaluated as template tokens."""
        result = self.renderer.render({
            "name": "Nilesh",
            "topic": "Neural Networks {Deep} & {LLM}",
        })
        expected = "Instruction: Write an essay for Nilesh on Neural Networks {Deep} & {LLM}."
        self.assertEqual(result, expected)

    def test_unknown_variable_keys_rejected(self):
        """Variables not declared in template are rejected with ValueError."""
        with self.assertRaises(ValueError):
            self.renderer.render({
                "name": "Nilesh",
                "topic": "Transformers",
                "malicious_key": "injected",
            })

    def test_before_after_refactoring_equivalence(self):
        """Prove before/after equivalence on all fixtures across baseline and refactored renderers."""
        fixtures = [
            {
                "scenario": "normal",
                "variables": {"name": "Alice", "topic": "AI"},
            },
            {
                "scenario": "braces_in_topic",
                "variables": {"name": "Bob", "topic": "{Math} & {Physics}"},
            },
            {
                "scenario": "braces_in_name",
                "variables": {"name": "{User_1}", "topic": "Biology"},
            },
            {
                "scenario": "missing_topic",
                "variables": {"name": "Charlie"},
                "expected_exception": "KeyError",
            },
            {
                "scenario": "unknown_key",
                "variables": {"name": "Dave", "topic": "CS", "extra": "foo"},
                "expected_exception": "ValueError",
            },
        ]

        all_equiv, log = prove_equivalence(self.template, fixtures)
        self.assertTrue(all_equiv)
        for entry in log:
            self.assertTrue(entry["is_equivalent"])

    def test_prompt_injection_disclaimer_present(self):
        """Verify prompt injection limitation disclaimer is present."""
        self.assertIn("DOES NOT prevent semantic prompt injection", PROMPT_INJECTION_DISCLAIMER)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrate that an intentional wrong result makes the test fail."""
        actual = self.renderer.render({"name": "A", "topic": "B"})
        wrong_expected = "Wrong Output"
        with self.assertRaises(AssertionError):
            self.assertEqual(actual, wrong_expected)


if __name__ == "__main__":
    unittest.main()
