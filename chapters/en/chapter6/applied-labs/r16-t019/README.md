# R16-T019: One BPE Merge Step — Evaluation Experiment

**Task**: R16-T019 · Issue #22  
**Chapter**: 6 — Section 5: "Byte-Pair Encoding tokenization"  
**Branch**: `student/e26b07f0816-R09-T009`  
**Type**: Evaluation experiment

---

## Overview

This applied lab extends Chapter 6, Section 5 ("Byte-Pair Encoding tokenization") by isolating a single discrete BPE merge step and running a comparative evaluation experiment across three controlled input configurations.

At each step of BPE tokenizer training:
1. All adjacent token pairs $(t_i, t_{i+1})$ in words are counted across the corpus.
2. The most frequent adjacent pair is selected for merging: $(a, b) \to ab$.
3. The merge is applied to each word sequence, replacing adjacent occurrences of $a, b$ with the merged token while strictly **preserving sequence order**.
4. Unmatched tokens and pairs remain completely separate and in their original order.

---

## Contract

| Scenario | Input Tokens | Merge Pair | Expected Output Tokens | Occurrences Merged | Token Reduction |
|---|---|---|---|---|---|
| **Core Contract** | `['l', 'o', 'w', 'e', 'r']` | `('l', 'o')` | `['lo', 'w', 'e', 'r']` | 1 | 1 |
| **Unmatched Input** | `['c', 'a', 't']` | `('l', 'o')` | `['c', 'a', 't']` | 0 | 0 |
| **Multiple Targets** | `['l', 'o', 'w', 'l', 'o']` | `('l', 'o')` | `['lo', 'w', 'lo']` | 2 | 2 |
| **Repeated Adjacent** | `['a', 'a', 'a']` | `('a', 'a')` | `['aa', 'a']` | 1 | 1 |

---

## Evaluation Experiment (Three Controlled Configurations)

The experiment evaluates the effect of applying the merge rule `('l', 'o') -> 'lo'` across three controlled corpus sizes:

| Configuration | Description | Sequences | Tokens Before | Tokens After | Tokens Reduced | Compression Ratio (%) | Pairs Before $\to$ After |
|---|---|---|---|---|---|---|---|
| **Small** | Single word `['l', 'o', 'w', 'e', 'r']` | 1 | 5 | 4 | 1 | 20.00% | 4 $\to$ 3 |
| **Medium** | Word family (`lower`, `lowest`, `lowering`) | 3 | 19 | 16 | 3 | 15.79% | 16 $\to$ 13 |
| **Large** | 6 mixed sequences with target & non-target words | 6 | 30 | 25 | 5 | 16.67% | 24 $\to$ 19 |

### Observed Trade-Off Analysis

- **Sequence Compression vs. Vocabulary Expansion**:
  - Each BPE merge reduces sequence length by 1 token per matched occurrence. Shorter sequences lower the quadratic computational cost ($\mathcal{O}(N^2)$) of Transformer self-attention layers during model training and inference.
  - In return, each merge rule expands the model's vocabulary size by $+1$ entry, which marginally increases the parameter footprint of the token embedding matrix ($\text{vocab\_size} \times d_{\text{model}}$).
- **Scope & Soundness**:
  - This experiment measures discrete structural token reduction and pair frequencies. It makes no unsupported claims regarding real-world model accuracy or task downstream perplexity.

---

## Files

| File | Purpose |
|---|---|
| `example.py` | `apply_merge()`, `count_adjacent_pairs()`, `run_evaluation_experiment()`, and data models |
| `test_example.py` | 12 unit tests verifying core contracts, boundary cases, metric calculations, and deliberate failure detection |
| `README.md` | Lab documentation, contract specifications, and experimental trade-off analysis |

---

## Running

```bash
# Run unit tests from repository root:
python3 -m unittest discover \
  -s chapters/en/chapter6/applied-labs/r16-t019 \
  -p "test_*.py" -v

# Run the demonstration and experiment table:
python3 chapters/en/chapter6/applied-labs/r16-t019/example.py
```

---

## Simulation and Pedagogical Limitations

> **SIMULATION NOTE**: This implementation is a pure Python 3 standard library pedagogical simulation:
>
> - Focuses on the discrete merge step and sequence length metric without running full corpus BPE training loops.
> - Does not utilize C++/Rust bindings or GPU acceleration.
> - Makes no unsupported claims about real hardware latency or trained language model accuracy.

---

## Lesson Link

See the linked section at the end of
[`chapters/en/chapter6/5.mdx`](../../5.mdx)
for textbook integration and examples.
