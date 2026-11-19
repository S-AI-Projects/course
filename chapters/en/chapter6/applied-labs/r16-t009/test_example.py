"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter6/applied-labs/r16-t009 -p "test_*.py"
"""

import unittest
from fractions import Fraction

from example import (
    DECISION_TABLE,
    ENGLISH_WORDS,
    EXISTING_VOCAB,
    EXPERIMENT_CORPUS,
    MAX_UNKNOWN_RATE,
    SCENARIOS,
    check_table,
    decide,
    run_experiment,
    unknown_rate,
)


class DecisionTable(unittest.TestCase):
    def test_three_scenarios_with_explicit_decisions(self):
        self.assertEqual(DECISION_TABLE, {
            "normal": "train-new",
            "boundary": "reuse",
            "missing-information": "need-more-info",
        })
        for scenario in SCENARIOS.values():
            self.assertTrue(scenario["rationale"].strip())

    def test_checker_passes_on_published_table(self):
        self.assertEqual(check_table(), [])

    def test_checker_fails_when_a_decision_is_changed(self):
        changed = {**DECISION_TABLE, "boundary": "train-new"}
        self.assertEqual(check_table(table=changed), [("boundary", "train-new", "reuse")])

    def test_boundary_sits_exactly_on_the_threshold(self):
        sample = SCENARIOS["boundary"]["facts"]["corpus_sample"]
        self.assertEqual(unknown_rate(sample, EXISTING_VOCAB), MAX_UNKNOWN_RATE)
        # One more unknown word flips the decision.
        facts = {"training_mode": "from-scratch", "corpus_sample": sample + " giraffe"}
        self.assertEqual(decide(facts), "train-new")

    def test_japanese_sample_is_fully_unknown(self):
        sample = SCENARIOS["normal"]["facts"]["corpus_sample"]
        self.assertEqual(unknown_rate(sample, EXISTING_VOCAB), Fraction(1))


class Rules(unittest.TestCase):
    def test_fine_tune_always_reuses(self):
        for sample in (None, "", "私は猫が好きです"):
            with self.subTest(sample=sample):
                self.assertEqual(decide({"training_mode": "fine-tune", "corpus_sample": sample}), "reuse")

    def test_missing_or_unknown_mode_needs_more_info(self):
        for mode in (None, "", "pretrain?"):
            with self.subTest(mode=mode):
                self.assertEqual(decide({"training_mode": mode, "corpus_sample": "the text"}),
                                 "need-more-info")

    def test_whitespace_only_sample_needs_more_info(self):
        self.assertEqual(decide({"training_mode": "from-scratch", "corpus_sample": "   "}),
                         "need-more-info")

    def test_unknown_rate_rejects_empty_sample(self):
        with self.assertRaises(ValueError):
            unknown_rate("", EXISTING_VOCAB)


class Experiment(unittest.TestCase):
    def test_corpus_has_twelve_tokens(self):
        self.assertEqual(len(EXPERIMENT_CORPUS.split()), 12)

    def test_three_configurations_match_hand_calculation(self):
        # Worked out by hand: size 4 knows {the,a,new,of} -> 6 of 12 unknown;
        # size 8 adds {we,on,text,corpus} -> 2 unknown (train, tokenizer); size 16 -> 0.
        expected = [
            (4, Fraction(1, 2), "train-new"),
            (8, Fraction(1, 6), "reuse"),
            (16, Fraction(0), "reuse"),
        ]
        actual = [(r["vocab_size"], r["unknown_rate"], r["decision"]) for r in run_experiment()]
        self.assertEqual(actual, expected)

    def test_trade_off_bigger_vocab_never_increases_unknowns(self):
        rates = [r["unknown_rate"] for r in run_experiment(sizes=range(1, len(ENGLISH_WORDS) + 1))]
        self.assertEqual(rates, sorted(rates, reverse=True))


if __name__ == "__main__":
    unittest.main()
