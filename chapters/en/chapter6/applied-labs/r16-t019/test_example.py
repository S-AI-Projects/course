"""Unit tests for One BPE Merge Step and Evaluation Experiment (Task R16-T019).

Verifies the BPE merge contract, pair counting, evaluation experiment metrics,
trade-off accounting, and deliberate failure detection.
"""

import os
import sys
import unittest

# Ensure the lab directory is on sys.path
LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    CONFIGURATIONS,
    MergeResult,
    apply_merge,
    apply_merge_to_corpus,
    count_adjacent_pairs,
    count_corpus_adjacent_pairs,
    run_evaluation_experiment,
)


class TestRequiredContract(unittest.TestCase):
    """Core acceptance tests specified by Issue #22 'Done when' checklist."""

    def test_lower_merge_lo_produces_lo_w_e_r(self):
        """Tokens [l,o,w,e,r] with merge (l,o) become [lo,w,e,r]; unmatched pairs remain separate."""
        tokens = ["l", "o", "w", "e", "r"]
        merge_pair = ("l", "o")
        res = apply_merge(tokens, merge_pair)

        self.assertEqual(res.merged_tokens, ["lo", "w", "e", "r"])
        self.assertEqual(res.occurrences_merged, 1)
        self.assertEqual(res.token_reduction, 1)
        # Verify unmatched tokens remain separate
        self.assertEqual(res.merged_tokens[1:], ["w", "e", "r"])

    def test_unmatched_tokens_remain_separate(self):
        """When merge pair does not occur in sequence, tokens remain unchanged."""
        tokens = ["c", "a", "t"]
        merge_pair = ("l", "o")
        res = apply_merge(tokens, merge_pair)

        self.assertEqual(res.merged_tokens, ["c", "a", "t"])
        self.assertEqual(res.occurrences_merged, 0)
        self.assertEqual(res.token_reduction, 0)


class TestPairCountingAndEdgeCases(unittest.TestCase):
    """Adjacent pair frequency counting and boundary cases."""

    def test_adjacent_pair_counting(self):
        """Count adjacent pairs accurately in a token sequence."""
        tokens = ["l", "o", "w", "e", "r"]
        counts = count_adjacent_pairs(tokens)

        self.assertEqual(counts[("l", "o")], 1)
        self.assertEqual(counts[("o", "w")], 1)
        self.assertEqual(counts[("w", "e")], 1)
        self.assertEqual(counts[("e", "r")], 1)
        self.assertEqual(sum(counts.values()), 4)

    def test_single_token_and_empty_sequence(self):
        """Empty or single-token sequences have zero pairs and cannot be merged."""
        self.assertEqual(count_adjacent_pairs([]), {})
        self.assertEqual(count_adjacent_pairs(["only"]), {})

        res_empty = apply_merge([], ("a", "b"))
        self.assertEqual(res_empty.merged_tokens, [])
        self.assertEqual(res_empty.occurrences_merged, 0)

        res_single = apply_merge(["single"], ("a", "b"))
        self.assertEqual(res_single.merged_tokens, ["single"])
        self.assertEqual(res_single.occurrences_merged, 0)

    def test_multiple_occurrences_in_single_sequence(self):
        """Sequence with multiple targets merges all instances without overlap issues."""
        tokens = ["l", "o", "w", "l", "o"]
        res = apply_merge(tokens, ("l", "o"))
        self.assertEqual(res.merged_tokens, ["lo", "w", "lo"])
        self.assertEqual(res.occurrences_merged, 2)
        self.assertEqual(res.token_reduction, 2)

    def test_overlapping_identical_pairs(self):
        """Identical adjacent tokens merge greedily from left to right."""
        tokens = ["a", "a", "a"]
        res = apply_merge(tokens, ("a", "a"))
        # First ('a', 'a') merges into 'aa', leaving ['aa', 'a']
        self.assertEqual(res.merged_tokens, ["aa", "a"])
        self.assertEqual(res.occurrences_merged, 1)

    def test_input_validation(self):
        """Invalid inputs to apply_merge raise TypeError or ValueError."""
        with self.assertRaises(TypeError):
            apply_merge("not a list", ("a", "b"))
        with self.assertRaises(TypeError):
            apply_merge(["a", "b"], "not a tuple")
        with self.assertRaises(ValueError):
            apply_merge(["a", "b"], ("a", "b", "c"))
        with self.assertRaises(TypeError):
            apply_merge(["a", "b"], (1, 2))


class TestEvaluationExperiment(unittest.TestCase):
    """Focus: Compare three small controlled configurations or input sizes

    using appropriate metrics (token reduction, compression ratio, pair count).
    """

    def test_three_configurations_evaluated(self):
        """Verify that exactly three controlled configurations are evaluated."""
        metrics = run_evaluation_experiment(CONFIGURATIONS)
        self.assertEqual(len(metrics), 3)

        config_names = [m.config_name for m in metrics]
        self.assertEqual(
            config_names,
            [
                "Config_Small_SingleWord",
                "Config_Medium_WordFamily",
                "Config_Large_DiverseCorpus",
            ],
        )

    def test_experiment_metric_correctness(self):
        """Check mathematical consistency of compression metrics across configs."""
        metrics = run_evaluation_experiment(CONFIGURATIONS)

        for m in metrics:
            with self.subTest(config=m.config_name):
                # tokens_reduced == tokens_before - tokens_after
                self.assertEqual(m.tokens_reduced, m.tokens_before - m.tokens_after)
                # tokens_after < tokens_before (since target pair occurs in each config)
                self.assertLess(m.tokens_after, m.tokens_before)
                # compression ratio strictly positive
                self.assertGreater(m.compression_ratio, 0.0)
                # pairs_after < pairs_before
                self.assertLess(m.pairs_after, m.pairs_before)

    def test_trade_off_observation(self):
        """Verify the trade-off: sequence length decreases with merge count."""
        metrics = run_evaluation_experiment(CONFIGURATIONS)
        small, medium, large = metrics[0], metrics[1], metrics[2]

        # Larger corpus with more occurrences achieves higher absolute token reduction
        self.assertLess(small.tokens_reduced, medium.tokens_reduced)
        self.assertLess(medium.tokens_reduced, large.tokens_reduced)


class TestDeliberateFailure(unittest.TestCase):
    """Contribution Focus: Proves a deliberate wrong result makes the test fail."""

    def test_corrupted_merge_output_fails(self):
        """Asserting wrong tokens after merge triggers an assertion failure."""
        res = apply_merge(["l", "o", "w", "e", "r"], ("l", "o"))
        corrupted = ["lo", "wrong", "r"]

        with self.assertRaises(AssertionError):
            self.assertEqual(res.merged_tokens, corrupted)

    def test_corrupted_reduction_count_fails(self):
        """Asserting wrong reduction count triggers an assertion failure."""
        res = apply_merge(["l", "o", "w", "e", "r"], ("l", "o"))
        with self.assertRaises(AssertionError):
            self.assertEqual(res.token_reduction, 999)


if __name__ == "__main__":
    unittest.main()
