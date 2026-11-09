# Applied Lab R16-T012: Worked Decision Example for Basic Usage Completed

## Related Lesson
- **Chapter**: Chapter 2 - Using Transformers
- **Section**: [Basic usage completed! (7.mdx)](../../7.mdx) (Recapping Sections 1-6)

## Objective & Focus
This lab provides a worked decision example and rule-based validation engine that evaluates input facts for Transformer model inference and produces pipeline decisions with lesson-backed rationales. It emphasizes smallest valid, boundary, and invalid/missing-information cases.

## Decision Table

| Scenario ID | Name | Input Facts | Decision | Lesson Rationale |
| --- | --- | --- | --- | --- |
| `normal_unequal_batch` | Normal Scenario | `[[101, 2054, 2003, 102], [101, 7592, 102]]` | `PAD_AND_MASK` | Chapter 2 Section 5: Batched inputs must form rectangular 2D tensors. Sequences of differing lengths require padding with the pad token ID and an attention mask so self-attention ignores pad tokens. |
| `boundary_smallest_valid` | Smallest Valid Input | `[[101]]` (batch 1, length 1) | `VALID_DIRECT_INFERENCE` | Smallest valid boundary: A single token sequence enclosed in a 2D batch `[1, 1]`. All sequences are equal in length (1) and within context limits; no padding or attention mask adjustments required. |
| `missing_information` | Missing Information | `None` or `[]` | `REJECT_MISSING_INPUT` | Chapter 2 Section 2-4: The model pipeline requires token IDs to construct input tensors. Missing or null input data cannot form a valid tensor. |
| `boundary_unbatched_1d` | Unbatched Sequence | `[101, 2054, 102]` (1D list) | `REJECT_UNBATCHED` | Chapter 2 Section 5: Passing a 1D tensor without an outer batch dimension triggers `IndexError: Dimension out of range`. Models expect a batch dimension `[batch_size, seq_len]`. |
| `boundary_exact_max_context` | Exact Max Context | `[[101] * 512]` (length = 512) | `VALID_DIRECT_INFERENCE` | Upper boundary: Fits exactly within the maximum context length (512) and executes without truncation. |
| `boundary_exceeding_max_context` | Exceeding Max Context | `[[101] * 513]` (length = 513) | `REJECT_EXCEEDS_MAX_LENGTH` | Upper boundary violation: Exceeding max context window (513 > 512) violates positional embedding constraints and requires truncation. |

## Boundary Decision Details
- **Minimal Valid Boundary (`boundary_smallest_valid`)**:
  - The minimal valid tensor is shape `[1, 1]` (batch size 1, sequence length 1).
  - At length 1, no padding is needed. At length 0, it becomes an invalid empty sequence.
- **Batch Dimension Boundary (`boundary_unbatched_1d`)**:
  - A 1D sequence of tokens fails model input requirements because Transformer models expect a 2D tensor `[batch_size, sequence_length]`.
- **Upper Context Boundary (`boundary_exact_max_context` vs `boundary_exceeding_max_context`)**:
  - Exactly at 512 tokens, inference is valid.
  - At 513 tokens (boundary + 1), the sequence exceeds the model's position embeddings and must be truncated.

## Running the Lab

### 1. Run the Example Directly
```bash
python3 chapters/en/chapter2/applied-labs/r16-t012/example.py
```

### 2. Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t012 -p "test_*.py" -v
```

### 3. Run Verification & Comparison Checks
```bash
python3 work/R16-T012/check.py
```

## Scope and Limitations
- **Educational Simulation**: Evaluates structural tensor properties and pipeline contracts deterministically in pure Python without requiring PyTorch or Hugging Face model downloads.
- **Zero External Dependencies**: Operates entirely with the Python 3 standard library.
- **Hardware Agnostic**: Makes no claims regarding real GPU/TPU execution performance, memory footprints, or statistical model accuracy.
