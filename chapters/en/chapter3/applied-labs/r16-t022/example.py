#!/usr/bin/env python3
"""
Applied Lab R16-T022: Training-Only Imputation Boundary-Case Example.

This module provides an educational, standalone implementation of
missing-value mean imputation with strict fit/transform separation,
connecting to Chapter 3 Section 2 ("Processing the data") of the
Hugging Face course.

Data Leakage Principle:
Preprocessing parameters (such as normalization statistics, vocabulary tokens,
or imputation values) must be computed exclusively from the training split
('fit') and then applied unchanged to validation/test splits ('transform').
Re-computing statistics on validation data causes data leakage and yields
overly optimistic evaluation metrics.

Contract:
- Training:   [2, None, 4]  -> fitted mean is 3
- Validation: [100, None]   -> imputed as [100, 3] (NOT [100, 100])
- Training with all-missing values (e.g. [None, None]) is rejected with ValueError.
"""

from typing import List, Optional, Sequence, Union
import sys

Number = Union[int, float]
OptionalNumber = Optional[Number]


class TrainingOnlyMeanImputer:
    """
    Mean imputer that enforces strict fit/transform separation.

    Fits the mean on non-missing observations from training data only,
    stores the value, and applies it to impute missing values (None)
    across any dataset split.
    """

    def __init__(self) -> None:
        self.mean_: Optional[Number] = None

    def fit(self, training_data: Sequence[OptionalNumber]) -> "TrainingOnlyMeanImputer":
        """
        Fit the imputer on training observations.

        Args:
            training_data: Sequence of numbers and/or None values.

        Returns:
            self with stored mean_.

        Raises:
            ValueError: If training data is empty or contains only None values.
            TypeError: If an element is neither numeric nor None.
        """
        if not training_data:
            raise ValueError("Cannot fit imputer on empty training input.")

        valid_vals: List[Number] = []
        for x in training_data:
            if x is None:
                continue
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise TypeError(f"Invalid non-numeric observation in training data: {x!r}")
            valid_vals.append(x)

        if not valid_vals:
            raise ValueError(
                "All-missing training input is rejected: at least one valid observation "
                "is required to compute the training mean."
            )

        mean_val = sum(valid_vals) / len(valid_vals)
        # Format as int if all observed values are integers and mean is an exact whole number
        if all(isinstance(x, int) and not isinstance(x, bool) for x in valid_vals) and mean_val.is_integer():
            self.mean_ = int(mean_val)
        else:
            self.mean_ = mean_val

        return self

    def transform(self, data: Sequence[OptionalNumber]) -> List[Number]:
        """
        Impute missing (None) values in data using the stored training mean.

        Args:
            data: Sequence of numbers and/or None values to transform.

        Returns:
            List of numbers with None replaced by the fitted mean.

        Raises:
            ValueError: If imputer has not been fitted yet.
            TypeError: If an element is neither numeric nor None.
        """
        if self.mean_ is None:
            raise ValueError("Imputer is not fitted. Call 'fit' before 'transform'.")

        result: List[Number] = []
        for x in data:
            if x is None:
                result.append(self.mean_)
            elif isinstance(x, bool) or not isinstance(x, (int, float)):
                raise TypeError(f"Invalid non-numeric observation in input data: {x!r}")
            else:
                result.append(x)
        return result

    def fit_transform(self, training_data: Sequence[OptionalNumber]) -> List[Number]:
        """Fit on training data and transform it in one step."""
        return self.fit(training_data).transform(training_data)


def run_pipeline(
    train_data: Sequence[OptionalNumber],
    val_data: Sequence[OptionalNumber],
) -> tuple[Number, List[Number], List[Number]]:
    """
    Convenience function to fit on training data and transform both splits.

    Returns:
        tuple of (fitted_mean, transformed_train, transformed_val)
    """
    imputer = TrainingOnlyMeanImputer()
    imputer.fit(train_data)
    fitted_mean = imputer.mean_
    assert fitted_mean is not None  # for type checking
    transformed_train = imputer.transform(train_data)
    transformed_val = imputer.transform(val_data)
    return fitted_mean, transformed_train, transformed_val


def main() -> int:
    """Demonstrate the required contract and boundary cases."""
    train_raw = [2, None, 4]
    val_raw = [100, None]

    print("=== Training-Only Mean Imputation (Fit/Transform Separation) ===")
    print(f"Raw training observations:   {train_raw}")
    print(f"Raw validation observations: {val_raw}")

    imputer = TrainingOnlyMeanImputer()
    imputer.fit(train_raw)
    fitted_mean = imputer.mean_
    print(f"\nFitted mean from training only: {fitted_mean}")

    imputed_train = imputer.transform(train_raw)
    imputed_val = imputer.transform(val_raw)

    print(f"Imputed training:   {imputed_train}")
    print(f"Imputed validation: {imputed_val} (using training mean {fitted_mean}, NOT validation mean 100)")

    # Boundary check: all-missing training input is rejected
    print("\nBoundary verification:")
    all_missing_train = [None, None]
    try:
        TrainingOnlyMeanImputer().fit(all_missing_train)
        print("ERROR: All-missing training was unexpectedly accepted!")
        return 1
    except ValueError as e:
        print(f"PASS: All-missing training input correctly rejected ({e})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
