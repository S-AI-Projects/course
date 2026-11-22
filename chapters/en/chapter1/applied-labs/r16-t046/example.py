#!/usr/bin/env python3
"""
Applied Lab R16-T046: Prompt-Template Escaping — Refactor the Teaching Example.

This module demonstrates safe prompt-template rendering from declared variables,
connecting directly to Chapter 1, Section 8 ("Deep dive into Text Generation
Inference with LLMs" [inference-with-llms]).

Lesson Context:
In LLM inference workflows, user inputs are formatted into structured prompt templates
prior to tokenization and prefill. If templates are rendered naively (e.g. repeated
`str.format()` or recursive variable replacement), user-supplied data containing curly
braces `{}` can cause template corruption, injection attacks, or KeyError exceptions.

Contract & Requirements:
- Render a template from declared variables (e.g., `name` and `topic`).
- Template with `name` and `topic` renders supplied values.
- Missing `topic` (or any required declared placeholder) fails (raises KeyError/ValueError).
- Braces inside user data MUST remain literal:
  e.g., user supplying topic "Quantum {Physics}" renders with literal "{Physics}",
  NOT treated as another template placeholder or format token.
- Keep user data distinct from fixed instruction fields:
  fixed instructions and declared template variables are kept strictly bounded.
- Do NOT claim templating alone prevents prompt injection:
  structural escaping isolates syntax (curly braces) but semantic prompt injection
  (adversarial system overrides, jailbreaks) requires system-level safeguards.
- Refactoring Focus:
  Implement a correct baseline (`BaselinePromptRenderer`), then extract one named
  responsibility (`TemplateVariableBinder`), and prove before/after equivalence across the fixture suite.
"""

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional, Set, Tuple


PROMPT_INJECTION_DISCLAIMER = (
    "[SECURITY NOTICE] Template escaping ensures syntactic isolation so that user-supplied "
    "braces '{}' remain literal and do not trigger unexpected format expansions. "
    "However, syntax escaping alone DOES NOT prevent semantic prompt injection (e.g. jailbreaks "
    "or instruction overrides). Additional guardrails and model-level controls are required."
)

PLACEHOLDER_REGEX = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


# ==============================================================================
# Baseline Implementation: Monolithic Renderer
# ==============================================================================
class BaselinePromptRenderer:
    """Monolithic baseline renderer implementing prompt variable binding and escaping."""

    def __init__(self, template: str) -> None:
        if not isinstance(template, str):
            raise TypeError("template must be a string")
        self.template: str = template
        self.declared_fields: Set[str] = set(PLACEHOLDER_REGEX.findall(template))

    def render(self, variables: Dict[str, Any]) -> str:
        """Render template with variables, ensuring literal braces in user values."""
        if not isinstance(variables, dict):
            raise TypeError("variables must be a dict")

        missing = [f for f in self.declared_fields if f not in variables]
        if missing:
            raise KeyError(f"Missing required template variables: {sorted(missing)}")

        extra = [k for k in variables if k not in self.declared_fields]
        if extra:
            raise ValueError(f"Unknown variables supplied: {sorted(extra)}")

        for k, v in variables.items():
            if not isinstance(v, str):
                raise TypeError(f"Variable '{k}' value must be str, got {type(v).__name__}")

        def repl(match):
            key = match.group(1)
            return variables[key]

        return PLACEHOLDER_REGEX.sub(repl, self.template)


# ==============================================================================
# Refactored Implementation: Extracted Responsibility (TemplateVariableBinder)
# ==============================================================================
class TemplateVariableBinder:
    """Extracted named responsibility: validates variables and performs literal binding.

    Guarantees user data is kept distinct from template syntax, preserving literal braces.
    """

    @staticmethod
    def validate_variables(variables: Dict[str, Any], declared_fields: Set[str]) -> None:
        """Validate that all required fields exist, no extra keys exist, and all are strings."""
        if not isinstance(variables, dict):
            raise TypeError("variables must be a dict")

        missing = [f for f in declared_fields if f not in variables]
        if missing:
            raise KeyError(f"Missing required template variables: {sorted(missing)}")

        extra = [k for k in variables if k not in declared_fields]
        if extra:
            raise ValueError(f"Unknown variables supplied: {sorted(extra)}")

        for k, v in variables.items():
            if not isinstance(v, str):
                raise TypeError(f"Variable '{k}' value must be str, got {type(v).__name__}")

    @classmethod
    def bind_literal_values(cls, template: str, variables: Dict[str, str], declared_fields: Set[str]) -> str:
        """Perform non-recursive literal substitution of variables into template placeholders."""
        cls.validate_variables(variables, declared_fields)
        return PLACEHOLDER_REGEX.sub(lambda m: variables[m.group(1)], template)


class RefactoredPromptRenderer:
    """Refactored prompt renderer delegating binding to TemplateVariableBinder."""

    def __init__(self, template: str, binder: Optional[TemplateVariableBinder] = None) -> None:
        if not isinstance(template, str):
            raise TypeError("template must be a string")
        self.template: str = template
        self.binder = binder or TemplateVariableBinder()
        self.declared_fields: Set[str] = set(PLACEHOLDER_REGEX.findall(template))

    def render(self, variables: Dict[str, Any]) -> str:
        """Render template by delegating variable validation and binding to binder."""
        return self.binder.bind_literal_values(self.template, variables, self.declared_fields)


def prove_equivalence(
    template: str, test_fixtures: List[Dict[str, Any]]
) -> Tuple[bool, List[Dict[str, Any]]]:
    """Prove before/after equivalence between Baseline and Refactored renderers."""
    baseline = BaselinePromptRenderer(template)
    refactored = RefactoredPromptRenderer(template)

    results = []
    all_equivalent = True

    for fixture in test_fixtures:
        scenario = fixture["scenario"]
        variables = fixture["variables"]
        exp_exception = fixture.get("expected_exception")

        base_res, base_exc = None, None
        ref_res, ref_exc = None, None

        # Run baseline
        try:
            base_res = baseline.render(variables)
        except Exception as e:
            base_exc = type(e).__name__

        # Run refactored
        try:
            ref_res = refactored.render(variables)
        except Exception as e:
            ref_exc = type(e).__name__

        equiv = (base_res == ref_res) and (base_exc == ref_exc)
        if not equiv:
            all_equivalent = False

        results.append({
            "scenario": scenario,
            "variables": variables,
            "baseline_result": base_res,
            "baseline_exception": base_exc,
            "refactored_result": ref_res,
            "refactored_exception": ref_exc,
            "is_equivalent": equiv,
        })

    return all_equivalent, results


if __name__ == "__main__":
    print("=== Prompt-Template Escaping Example (R16-T046) ===")
    print(f"Notice: {PROMPT_INJECTION_DISCLAIMER}\n")

    tpl = "Instruction: Write an essay for student {name} on topic: {topic}."

    renderer = RefactoredPromptRenderer(tpl)
    out1 = renderer.render({"name": "Alice", "topic": "Quantum Computing"})
    print(f"Normal Output:\n  {out1}\n")

    out2 = renderer.render({"name": "Bob", "topic": "Deep Learning {LLM} Architecture"})
    print(f"Braces in User Data Output:\n  {out2}\n")

    try:
        renderer.render({"name": "Charlie"})
    except KeyError as exc:
        print(f"Missing topic correctly failed: {exc}\n")
