#!/usr/bin/env python3
"""
Unit tests for Training-Only Imputation Boundary-Case Example (R16-T022).

Verifies strict fit/transform separation, prevention of data leakage,
smallest valid fixtures, boundary conditions, and invalid input rejections.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

# Ensure current lab directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import TrainingOnlyMeanImputer, main, run_pipeline


class TestTrainingOnlyMeanImputer(unittest.TestCase):
    """Test suite for TrainingOnlyMeanImputer."""

    def test_required_contract_fixtures(self):
        """
        Verify the core contract:
        Training [2, None, 4] yields mean 3.
        Validation [100, None] becomes [100, 3], NOT [100, 100].
        """
        train = [2, None, 4]
        val = [100, None]

        imputer = TrainingOnlyMeanImputer()
        imputer.fit(train)

        # 1. Fitted mean is 3
        self.assertEqual(imputer.mean_, 3)

        # 2. Transformed training replaces None with 3
        self.assertEqual(imputer.transform(train), [2, 3, 4])

        # 3. Transformed validation uses training mean (3), not validation mean (100)
        imputed_val = imputer.transform(val)
        self.assertEqual(imputed_val, [100, 3])
        self.assertNotEqual(imputed_val, [100, 100])

    def test_run_pipeline_helper(self):
        """Verify the helper pipeline function on the standard contract."""
        mean, train_imp, val_imp = run_pipeline([2, None, 4], [100, None])
        self.assertEqual(mean, 3)
        self.assertEqual(train_imp, [2, 3, 4])
        self.assertEqual(val_imp, [100, 3])

    def test_smallest_valid_training_cases(self):
        """
        Verify smallest valid training fixtures:
        - Single non-missing observation: [5]
        - Single non-missing observation surrounded by None: [None, 7, None]
        """
        imputer1 = TrainingOnlyMeanImputer().fit([5])
        self.assertEqual(imputer1.mean_, 5)
        self.assertEqual(imputer1.transform([None]), [5])

        imputer2 = TrainingOnlyMeanImputer().fit([None, 7, None])
        self.assertEqual(imputer2.mean_, 7)
        self.assertEqual(imputer2.transform([None, 10]), [7, 10])

    def test_boundary_validation_cases(self):
        """
        Verify boundary conditions on the validation split:
        - All-missing validation split is valid and filled with training mean
        - No-missing validation split remains unchanged
        - Empty validation list returns empty list
        """
        imputer = TrainingOnlyMeanImputer().fit([10, None, 20])
        self.assertEqual(imputer.mean_, 15)

        # All-missing validation
        self.assertEqual(imputer.transform([None, None]), [15, 15])

        # No-missing validation
        self.assertEqual(imputer.transform([1, 2, 3]), [1, 2, 3])

        # Empty validation
        self.assertEqual(imputer.transform([]), [])

    def test_float_and_negative_numbers(self):
        """Verify handling of floats, decimals, and negative numbers."""
        imputer = TrainingOnlyMeanImputer().fit([-10, None, 10])
        self.assertEqual(imputer.mean_, 0)
        self.assertEqual(imputer.transform([None]), [0])

        imputer_float = TrainingOnlyMeanImputer().fit([1.5, None, 2.5])
        self.assertEqual(imputer_float.mean_, 2.0)
        self.assertEqual(imputer_float.transform([None, 0.5]), [2.0, 0.5])

    def test_invalid_all_missing_training_rejected(self):
        """
        Verify boundary decision:
        All-missing training input must be rejected with ValueError.
        """
        imputer = TrainingOnlyMeanImputer()
        with self.assertRaises(ValueError):
            imputer.fit([None, None, None])

    def test_invalid_empty_training_rejected(self):
        """Empty training input must be rejected with ValueError."""
        imputer = TrainingOnlyMeanImputer()
        with self.assertRaises(ValueError):
            imputer.fit([])

    def test_transform_before_fit_rejected(self):
        """Calling transform before fit raises ValueError."""
        imputer = TrainingOnlyMeanImputer()
        with self.assertRaises(ValueError):
            imputer.transform([1, None])

    def test_invalid_types_rejected(self):
        """Non-numeric values (including booleans and strings) raise TypeError."""
        imputer = TrainingOnlyMeanImputer()
        with self.assertRaises(TypeError):
            imputer.fit([1, "bad", 3])

        with self.assertRaises(TypeError):
            imputer.fit([True, None])

        imputer.fit([1, 2])
        with self.assertRaises(TypeError):
            imputer.transform(["string"])

    def test_fit_transform_method(self):
        """Verify fit_transform convenience method."""
        imputer = TrainingOnlyMeanImputer()
        res = imputer.fit_transform([2, None, 4])
        self.assertEqual(res, [2, 3, 4])
        self.assertEqual(imputer.mean_, 3)

    def test_cli_main_execution(self):
        """Verify CLI main entrypoint executes cleanly and produces expected output."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("Fitted mean from training only: 3", output)
        self.assertIn("Imputed training:   [2, 3, 4]", output)
        self.assertIn("Imputed validation: [100, 3]", output)
        self.assertIn("PASS: All-missing training input correctly rejected", output)


if __name__ == "__main__":
    unittest.main()
