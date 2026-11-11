# R16-T017: Worked Decision Example for Introduction (Chapter 6)

**Task**: R16-T017 · Issue #20  
**Chapter**: 6 — Section 1: "Introduction"  
**Branch**: `student/e26b07f0816-R07-T007`  
**Type**: Worked example with checks

---

## Overview

This applied lab extends Chapter 6, Section 1 ("Introduction") by providing an original three-scenario worked example and automated decision checker for tokenizer training strategy.

When pretraining language models from scratch on domain-specific corpora (e.g., Python code or non-English text), using a tokenizer pretrained on another domain is suboptimal. This module formalizes those decisions into input facts, decisions, and lesson-aligned rationales, backed by automated regression tests.

---

## Published Decision Table

| Scenario ID | Name / Description | Input Facts | Expected Decision | Lesson Rationale |
|---|---|---|---|---|
| `normal_scratch_domain_shift` | **Normal Scenario**: Pretraining from scratch on Python Code | `mode="scratch"`, `domain="python_code"`, `corpus=[sample code]` | `TRAIN_NEW_TOKENIZER` | Directly recaps Chapter 6 Section 1: Pretraining from scratch on a new domain requires training a new tokenizer to avoid suboptimal whitespace and vocabulary segmentation. |
| `boundary_minimal_single_sample` | **Boundary Scenario**: Minimal single-sample corpus | `mode="scratch"`, `corpus=["single text sample"]` | `TRAIN_NEW_TOKENIZER` | Minimal valid input boundary: Exactly one non-empty string sample fulfills the iterator contract for vocabulary training without raising empty-data errors. |
| `missing_information_null_corpus` | **Missing-Information Scenario**: Null corpus iterator | `mode="scratch"`, `corpus=None` | `REJECT_MISSING_CORPUS` | Missing-information failure: Tokenizer training cannot proceed without text data to discover subword merges. Must reject prior to invoking backend trainers. |
| `boundary_matching_domain_fine_tune` | **Boundary Scenario**: Standard fine-tuning on matching domain | `mode="fine_tune"`, `domain="english"`, `pretrained="english"` | `REUSE_PRETRAINED_TOKENIZER` | Recaps Chapter 3 / Chapter 6 contrast: In downstream fine-tuning on the same domain, reusing the checkpoint's tokenizer preserves learned embedding alignments. |
| `missing_information_empty_corpus` | **Missing-Information Scenario**: Empty list corpus | `mode="scratch"`, `corpus=[]` | `REJECT_EMPTY_CORPUS` | An empty list yields zero text samples and zero vocabulary information; rejected as empty. |

---

## Files

| File | Purpose |
|---|---|
| `example.py` | Decision engine (`evaluate_scenario`), published `SCENARIOS` table, and table checker (`check_decision_table`) |
| `test_example.py` | 13 unit tests covering normal, boundary, missing-information, regression, and deliberate failure detection |
| `README.md` | Lab documentation, decision matrix, and simulation notes |

---

## Running

```bash
# Run unit tests from repository root:
python3 -m unittest discover \
  -s chapters/en/chapter6/applied-labs/r16-t017 \
  -p "test_*.py" -v

# Run the runnable demo:
python3 chapters/en/chapter6/applied-labs/r16-t017/example.py
```

---

## Simulation and Pedagogical Limitations

> **SIMULATION NOTE**: This module is a pedagogical decision engine and preflight checker implemented strictly with the Python 3 standard library:
>
> - **Decision Logic Simulation**: It models pipeline preprocessing checks and architectural decisions, not the underlying C++/Rust BPE tokenizer training loop.
> - **No External Cloud / GPU Claims**: Does not require or claim real GPU memory, training latency benchmarks, or cloud tokenizer deployment performance.
> - **Offline Execution**: Runs without external package dependencies (`tokenizers`, `transformers`) or network calls.

---

## Lesson Link

See the linked section at the end of
[`chapters/en/chapter6/1.mdx`](../../1.mdx)
for the curriculum integration and expected outputs.
