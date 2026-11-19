"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t001 -p "test_*.py"
"""

import unittest

from example import (
    HEALTHY_VALIDATION_LOSSES,
    TRAINING_LOSSES,
    VALIDATION_LOSSES,
    detect_divergence,
)


class NormalCases(unittest.TestCase):
    def test_task_fixture_flags_divergence(self):
        # Training 0.5 -> 0.3 falls, validation 0.6 -> 0.7 rises.
        self.assertEqual(TRAINING_LOSSES, [0.8, 0.5, 0.3])
        self.assertEqual(VALIDATION_LOSSES, [0.9, 0.6, 0.7])
        self.assertTrue(detect_divergence(TRAINING_LOSSES, VALIDATION_LOSSES))

    def test_both_decreasing_is_not_flagged(self):
        self.assertFalse(detect_divergence(TRAINING_LOSSES, HEALTHY_VALIDATION_LOSSES))


class BoundaryCases(unittest.TestCase):
    def test_shortest_valid_input_two_steps(self):
        self.assertTrue(detect_divergence([0.5, 0.3], [0.6, 0.7]))
        self.assertFalse(detect_divergence([0.5, 0.3], [0.6, 0.4]))

    def test_flat_validation_is_not_rising(self):
        # A plateau is a warning sign in the lesson, but not "rising" under this rule.
        self.assertFalse(detect_divergence([0.8, 0.5, 0.3], [0.9, 0.6, 0.6]))

    def test_flat_training_is_not_falling(self):
        self.assertFalse(detect_divergence([0.8, 0.3, 0.3], [0.9, 0.6, 0.7]))

    def test_only_last_step_matters(self):
        # Divergence happened at step 2, but at the last step both fall again.
        self.assertFalse(detect_divergence([0.8, 0.5, 0.3], [0.6, 0.9, 0.7]))

    def test_both_rising_is_not_divergence(self):
        self.assertFalse(detect_divergence([0.3, 0.5], [0.6, 0.7]))

    def test_tuples_are_accepted(self):
        self.assertTrue(detect_divergence((0.5, 0.3), (0.6, 0.7)))


class FailureCases(unittest.TestCase):
    def test_too_short_is_rejected(self):
        with self.assertRaises(ValueError):
            detect_divergence([0.8], [0.9])

    def test_empty_is_rejected(self):
        with self.assertRaises(ValueError):
            detect_divergence([], [])

    def test_mismatched_lengths_are_rejected(self):
        with self.assertRaises(ValueError):
            detect_divergence([0.8, 0.5, 0.3], [0.9, 0.6])

    def test_non_numeric_value_is_rejected(self):
        with self.assertRaises(TypeError):
            detect_divergence([0.8, "0.5"], [0.9, 0.6])

    def test_bool_value_is_rejected(self):
        with self.assertRaises(TypeError):
            detect_divergence([0.8, True], [0.9, 0.6])

    def test_non_sequence_is_rejected(self):
        with self.assertRaises(TypeError):
            detect_divergence(0.8, [0.9, 0.6])


if __name__ == "__main__":
    unittest.main()
