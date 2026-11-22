# Applied Lab R16-T049: UI Callback Contract (Evaluation Experiment)

## Related Lesson
- **Chapter**: Chapter 9: Building Interactive Demos with Gradio
- **Section**: [Gradio, check! (`gradio-check`)](../../8.mdx)

## Objective & Focus
In Chapter 9, Section 8, the course recaps the construction of interactive ML interfaces. Before attaching Python backend callback functions to web interfaces or Hugging Face Spaces, validating input/output schemas and analyzing performance across different input sizes guarantees deterministic behavior.

This applied lab demonstrates:
1. A pure Python callback function (`analyze_text` / `text_analysis_callback`) decoupled from the Gradio web server framework.
2. Complete schema validation:
   - Input `"red red apple"` returns `{"word_count": 3, "unique_count": 2}`.
   - Empty text returns zeros `{"word_count": 0, "unique_count": 0}`.
   - Non-string inputs are rejected with `TypeError`.
3. An **evaluation experiment**:
   - Compares three controlled input sizes (small: 3 words, medium: 10 words, large: 25 words).
   - Computes contract metrics (schema correctness, uniqueness ratio `unique_count / word_count`, latency).
   - Reports trade-offs without claiming real-world model accuracy.

## Scope & Limitations
- **Pure Local Fixture**: Uses Python standard library without requiring Gradio installation, web servers, or browser interactions.
- **Model Decoupled**: Evaluates pure text processing logic rather than heavy neural model inference.
- **Hardware Neutral**: Does not assert physical GPU hardware or cloud service performance.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter9/applied-labs/r16-t049/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter9/applied-labs/r16-t049 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T049/check.py
```
