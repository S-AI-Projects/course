# Applied Lab R16-T046: Prompt-Template Escaping (Refactor the Teaching Example)

## Related Lesson
- **Chapter**: Chapter 1: Transformer Models
- **Section**: [Deep dive into Text Generation Inference with LLMs (`inference-with-llms`)](../../8.mdx)

## Objective & Focus
In Chapter 1, Section 8, prompt formatting is shown to precede tokenization and prefill during LLM inference. In production inference setups, prompt templates structure user data into fixed instructions.

This applied lab demonstrates:
1. Safe prompt-template rendering from declared variables (e.g. `{name}` and `{topic}`).
2. Strict validation: missing required variables fail (`KeyError`), and undeclared keys are rejected (`ValueError`).
3. Literal brace preservation: user input containing `{` or `}` remains strictly literal without triggering format corruption.
4. **Refactoring & Equivalence**: A correct baseline (`BaselinePromptRenderer`) is implemented, a named responsibility is extracted (`SafeVariableEscaper` / `RefactoredPromptRenderer`), and mathematical before/after equivalence is proven across the test suite.
5. **Security Scope**: Explicitly clarifying that syntactic escaping prevents format errors but **does not claim** to prevent semantic prompt injection.

## Public Input/Output Contract
- **Template**: `"Instruction: Write an essay for {name} on {topic}."`
- **Supplied Values**:
  - `{"name": "Alice", "topic": "Quantum Computing"}` renders supplied values.
  - Missing `topic` (e.g. `{"name": "Alice"}`) fails with `KeyError`.
  - User data containing braces (e.g. `{"topic": "{Physics}"}`) renders as literal `{Physics}`.
- **Refactoring Proof**: Baseline and Refactored renderers produce identical outputs and identical exceptions across all test cases.

## Security Scope & Disclaimer
> [!IMPORTANT]
> **Prompt Injection Disclaimer**:
> Syntactic escaping ensures curly braces in user variables do not corrupt template formatting.
> However, **templating alone does not prevent semantic prompt injection** (e.g., adversarial prompt overrides like `"Ignore previous instructions"`).
> System-level guardrails and instruction fine-tuning are required to address semantic injection.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter1/applied-labs/r16-t046/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter1/applied-labs/r16-t046 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T046/check.py
```
