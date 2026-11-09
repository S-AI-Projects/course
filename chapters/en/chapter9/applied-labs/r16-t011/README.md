# Applied Lab R16-T011: UI Callback Contract (Text Analysis)

## Related Lesson
- **Chapter**: Chapter 9 - Building Interactive Demos with Gradio
- **Section**: [Introduction to Gradio (1.mdx)](../../1.mdx)

## Objective & Focus
This lab provides a minimal, complete runnable concept example demonstrating a UI callback contract for a text-analysis interface. It decouples the core callback function from the Gradio UI framework to allow independent, deterministic local validation of its input/output schema.

## Public Input/Output Contract
- **Input Component**: Text input component (`gr.Textbox`), passing a Python string (`str`).
- **Callback Signature**: `analyze_text(text: str) -> Dict[str, int]` (also aliased as `text_analysis_callback`).
- **Output Components**: Structured mapping corresponding to numerical UI outputs (`gr.Number`, `gr.Label`, or `gr.JSON`):
  - `word_count` (`int`): Total count of whitespace-delimited words.
  - `unique_count` (`int`): Count of distinct words.

### Contract Scenarios
1. **Normal Case**:
   - Input: `"red red apple"`
   - Expected Output: `{"word_count": 3, "unique_count": 2}`
2. **Boundary Cases**:
   - Input: `""` (empty string)
   - Expected Output: `{"word_count": 0, "unique_count": 0}`
   - Input: `"   \t\n  "` (whitespace-only)
   - Expected Output: `{"word_count": 0, "unique_count": 0}`
3. **Failure Scenarios**:
   - Non-string inputs (e.g., `None`, numbers, lists, dictionaries) are rejected with a `TypeError`.

## Prerequisites
- Python 3 standard library only (`typing`, `unittest`, `json`, `sys`, `os`).
- No external packages, network access, model downloads, GPU, or paid services are required.

## Running the Lab

### 1. Run the Example Directly
```bash
python3 chapters/en/chapter9/applied-labs/r16-t011/example.py
```

### 2. Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t011 -p "test_*.py" -v
```

### 3. Run Verification & Schema Comparison Checks
```bash
python3 work/R16-T011/check.py
```

## Scope and Limitations
- **Local Simulation**: This lab illustrates the callback function and contract schema of a Gradio demo without requiring a Gradio installation or web server.
- **Model Decoupling**: Tokenization is whitespace-delimited Python string operations for deterministic execution; no heavy neural network or pre-trained transformer model is involved.
- **Hardware & Service Neutral**: The example makes no claims about hardware acceleration (GPU/TPU), cloud service behaviors, or statistical model accuracy.
