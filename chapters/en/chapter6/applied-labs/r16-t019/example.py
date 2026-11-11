"""Applied Lab R16-T019: One BPE Merge Step — Evaluation Experiment.

Task: R16-T019 (Issue #22)
Chapter: 6, Section 5 ("Byte-Pair Encoding tokenization")
Repository: https://github.com/S-AI-Projects/course

This module implements a deterministic single-step Byte-Pair Encoding (BPE)
merge operation and an evaluation experiment comparing sequence compression metrics
across three controlled input configurations:
- Counts adjacent token pairs in token sequences or tokenized corpora.
- Applies a supplied merge pair (a, b) -> ab while strictly preserving token order.
- Tokens ['l', 'o', 'w', 'e', 'r'] with merge ('l', 'o') -> ['lo', 'w', 'e', 'r'];
  unmatched pairs remain separate.
- Evaluation experiment compares 3 controlled input sizes (Small, Medium, Large)
  evaluating compression ratio, token reduction, and pair count reduction.

SIMULATION NOTE / PEDAGOGICAL SCOPE:
This is a deterministic pure Python 3 standard library implementation. It models
the discrete token merge step and vocabulary trade-off of BPE without claiming
real-world model accuracy, downstream task quality, or GPU acceleration.
"""

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class MergeResult:
    """Result of applying a single BPE merge step to a token sequence.

    Attributes:
        original_tokens: Input list of tokens before merge.
        merged_tokens: Resulting list of tokens after merge.
        merge_pair: The (a, b) pair that was merged.
        occurrences_merged: Number of times the pair was merged.
        token_reduction: Count of tokens reduced (original - merged).
    """

    original_tokens: List[str]
    merged_tokens: List[str]
    merge_pair: Tuple[str, str]
    occurrences_merged: int
    token_reduction: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentMetrics:
    """Metrics recorded for an evaluation configuration.

    Attributes:
        config_name: Identifier for the configuration/size.
        corpus_size_sequences: Number of sequences in corpus.
        tokens_before: Total token count before merge.
        tokens_after: Total token count after merge.
        tokens_reduced: tokens_before - tokens_after.
        compression_ratio: tokens_reduced / tokens_before (percentage).
        pairs_before: Total adjacent token pairs before merge.
        pairs_after: Total adjacent token pairs after merge.
    """

    config_name: str
    corpus_size_sequences: int
    tokens_before: int
    tokens_after: int
    tokens_reduced: int
    compression_ratio: float
    pairs_before: int
    pairs_after: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def count_adjacent_pairs(sequence: Sequence[str]) -> Counter:
    """Count frequency of each adjacent token pair in a single sequence.

    Args:
        sequence: List or tuple of token strings.

    Returns:
        Counter mapping (token_i, token_{i+1}) to occurrence count.
    """
    if not isinstance(sequence, (list, tuple)):
        raise TypeError(f"sequence must be a list or tuple, got {type(sequence).__name__}")

    pairs: Counter = Counter()
    if len(sequence) < 2:
        return pairs

    for i in range(len(sequence) - 1):
        pair = (sequence[i], sequence[i + 1])
        pairs[pair] += 1
    return pairs


def count_corpus_adjacent_pairs(corpus: Sequence[Sequence[str]]) -> Counter:
    """Count aggregate frequency of adjacent token pairs across a corpus.

    Args:
        corpus: List of token sequences.

    Returns:
        Counter mapping (token_i, token_{i+1}) to aggregate count.
    """
    if not isinstance(corpus, (list, tuple)):
        raise TypeError(f"corpus must be a list or tuple, got {type(corpus).__name__}")

    total_pairs: Counter = Counter()
    for seq in corpus:
        total_pairs.update(count_adjacent_pairs(seq))
    return total_pairs


def apply_merge(sequence: Sequence[str], pair: Tuple[str, str]) -> MergeResult:
    """Apply a single BPE merge rule (a, b) -> ab to a sequence, preserving order.

    Unmatched tokens and pairs remain untouched and in their exact original order.

    Args:
        sequence: List of input tokens.
        pair: Tuple of two token strings (a, b) to merge.

    Returns:
        MergeResult with original, merged tokens, and reduction metrics.

    Raises:
        TypeError: If sequence is not list/tuple or pair is not a 2-tuple of str.
        ValueError: If pair does not have exactly two elements.
    """
    if not isinstance(sequence, (list, tuple)):
        raise TypeError(f"sequence must be a list or tuple, got {type(sequence).__name__}")
    if not isinstance(pair, (tuple, list)):
        raise TypeError(f"pair must be a tuple, got {type(pair).__name__}")
    if len(pair) != 2:
        raise ValueError(f"pair must contain exactly 2 elements, got {len(pair)}")
    if not isinstance(pair[0], str) or not isinstance(pair[1], str):
        raise TypeError("pair elements must be strings")

    orig_tokens = list(sequence)
    if len(orig_tokens) < 2:
        return MergeResult(
            original_tokens=orig_tokens,
            merged_tokens=orig_tokens.copy(),
            merge_pair=(pair[0], pair[1]),
            occurrences_merged=0,
            token_reduction=0,
        )

    target_a, target_b = pair[0], pair[1]
    merged_token = target_a + target_b

    merged: List[str] = []
    i = 0
    occurrences = 0

    while i < len(orig_tokens):
        if (
            i < len(orig_tokens) - 1
            and orig_tokens[i] == target_a
            and orig_tokens[i + 1] == target_b
        ):
            merged.append(merged_token)
            i += 2
            occurrences += 1
        else:
            merged.append(orig_tokens[i])
            i += 1

    return MergeResult(
        original_tokens=orig_tokens,
        merged_tokens=merged,
        merge_pair=(target_a, target_b),
        occurrences_merged=occurrences,
        token_reduction=len(orig_tokens) - len(merged),
    )


def apply_merge_to_corpus(
    corpus: Sequence[Sequence[str]], pair: Tuple[str, str]
) -> List[List[str]]:
    """Apply a merge pair to every sequence in a corpus."""
    return [apply_merge(seq, pair).merged_tokens for seq in corpus]


# ============================================================================
# Evaluation Experiment: Three Controlled Configurations
# ============================================================================

CONFIGURATIONS: Dict[str, Dict[str, Any]] = {
    "Config_Small_SingleWord": {
        "description": "Small input: Single word sequence ['l', 'o', 'w', 'e', 'r']",
        "corpus": [
            ["l", "o", "w", "e", "r"],
        ],
        "merge_pair": ("l", "o"),
    },
    "Config_Medium_WordFamily": {
        "description": "Medium input: 3 related words ['lower', 'lowest', 'lowering']",
        "corpus": [
            ["l", "o", "w", "e", "r"],
            ["l", "o", "w", "e", "s", "t"],
            ["l", "o", "w", "e", "r", "i", "n", "g"],
        ],
        "merge_pair": ("l", "o"),
    },
    "Config_Large_DiverseCorpus": {
        "description": "Large input: 6 mixed sequences with multiple target & non-target tokens",
        "corpus": [
            ["l", "o", "w", "e", "r"],
            ["l", "o", "w", "e", "s", "t"],
            ["l", "o", "w", "e", "r", "i", "n", "g"],
            ["f", "l", "o", "w"],
            ["s", "l", "o", "w"],
            ["c", "a", "t"],
        ],
        "merge_pair": ("l", "o"),
    },
}


def run_evaluation_experiment(
    configs: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[ExperimentMetrics]:
    """Execute evaluation experiment comparing compression trade-offs across configurations.

    Metric:
    - Sequence compression ratio: (tokens_before - tokens_after) / tokens_before.
    - Demonstrates that merging frequent pairs reduces sequence length by 1 per match.
    - Trade-off: Lower sequence length decreases Transformer attention computational steps
      at the expense of expanding the vocabulary size by 1 entry per learned merge rule.
    """
    if configs is None:
        configs = CONFIGURATIONS

    metrics_list: List[ExperimentMetrics] = []

    for name, cfg in configs.items():
        corpus = cfg["corpus"]
        merge_pair = cfg["merge_pair"]

        tokens_before = sum(len(seq) for seq in corpus)
        pairs_before = sum(count_adjacent_pairs(seq).total() for seq in corpus)

        merged_corpus = apply_merge_to_corpus(corpus, merge_pair)

        tokens_after = sum(len(seq) for seq in merged_corpus)
        pairs_after = sum(count_adjacent_pairs(seq).total() for seq in merged_corpus)

        tokens_reduced = tokens_before - tokens_after
        compression_ratio = (
            (tokens_reduced / tokens_before) * 100.0 if tokens_before > 0 else 0.0
        )

        metrics = ExperimentMetrics(
            config_name=name,
            corpus_size_sequences=len(corpus),
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            tokens_reduced=tokens_reduced,
            compression_ratio=round(compression_ratio, 2),
            pairs_before=pairs_before,
            pairs_after=pairs_after,
        )
        metrics_list.append(metrics)

    return metrics_list


def main() -> None:
    print("=== BPE Single Merge Step & Evaluation Experiment (Task R16-T019) ===")

    # 1. Core Contract Demonstration
    core_tokens = ["l", "o", "w", "e", "r"]
    core_merge = ("l", "o")
    result = apply_merge(core_tokens, core_merge)
    print("\n--- Core Contract ---")
    print(f"  Input Tokens: {core_tokens}")
    print(f"  Merge Pair:   {core_merge}")
    print(f"  Output:       {result.merged_tokens}")
    print(f"  Reduction:    {result.token_reduction} token(s)")

    # 2. Evaluation Experiment Across Three Configurations
    print("\n--- Evaluation Experiment (Three Controlled Configurations) ---")
    experiment_results = run_evaluation_experiment()
    print(
        f"{'Config Name':<28} | {'Seqs':<4} | {'Before':<6} | {'After':<5} | "
        f"{'Reduced':<7} | {'Compression %':<13} | {'Pairs Diff'}"
    )
    print("-" * 85)
    for m in experiment_results:
        pair_diff = f"{m.pairs_before} -> {m.pairs_after}"
        print(
            f"{m.config_name:<28} | {m.corpus_size_sequences:<4} | {m.tokens_before:<6} | "
            f"{m.tokens_after:<5} | {m.tokens_reduced:<7} | {m.compression_ratio:>12}% | {pair_diff}"
        )

    print("\nTrade-off Summary:")
    print("  - Applying a merge reduces sequence length linearly with pair occurrences.")
    print("  - Sequence reduction lowers Transformer quadratic attention cost.")
    print("  - Vocabulary size grows by +1 entry per learned merge rule.")


if __name__ == "__main__":
    main()
