# Applied Lab R16-T022: Training-Only Imputation Boundary-Case Example

A minimal, runnable concept lab demonstrating strict **fit/transform separation** and **data leakage prevention** during dataset preprocessing, complementing [Chapter 3, Section 2 ("Processing the data")](../../2.mdx).

---

## 1. Concept and Lesson Connection

In [Chapter 3, Section 2 ("Processing the data")](../../2.mdx), datasets are split into `train`, `validation`, and `test` splits. A fundamental rule of machine learning preprocessing is:

> **Parameters and statistics (e.g. vocabularies, mean/variance normalizers, imputation values) must be computed ("fit") strictly on the training split, and then applied ("transform") unchanged to validation and test splits.**

If preprocessing parameters are recomputed on validation data (e.g., computing a validation-specific mean), information about the validation distribution leaks into the evaluation pipeline. This **data leakage** corrupts validation metrics and gives an overly optimistic assessment of model generalization.

This lab demonstrates the fit/transform boundary using missing-value mean imputation.

---

## 2. Fixture Contract and Boundary Decisions

### Standard Contract
- **Training Observations**: `[2, None, 4]`
  - Non-missing values: `2` and `4`
  - Computed training mean: `(2 + 4) / 2 = 3`
- **Validation Observations**: `[100, None]`
  - Using stored training mean `3`: `[100, 3]`
  - **Why not `[100, 100]`?** If the imputer were refitted on the validation split, the validation mean of `[100]` would be `100`, turning `[100, None]` into `[100, 100]`. That is a classic data leakage bug. Applying the stored training mean preserves the integrity of the evaluation split.

| Split | Raw Observations | Fitted Mean | Transformed Output | Explanation |
| :--- | :--- | :--- | :--- | :--- |
| **Training** | `[2, None, 4]` | `3` | `[2, 3, 4]` | Missing value imputed with training mean |
| **Validation** | `[100, None]` | *(uses 3)* | `[100, 3]` | Imputed with training mean; avoids leakage |

---

### Smallest Valid, Boundary, and Invalid Cases

#### 1. Smallest Valid Case
- **Training**: Single non-missing observation `[5]` or `[None, 7, None]`.
- **Decision**: Valid. A single valid observation provides sufficient statistical evidence to define a sample mean.
- **Example**: `fit([5])` $\rightarrow$ `mean_ = 5`. `transform([None])` $\rightarrow$ `[5]`.

#### 2. Boundary Cases (Validation Split)
- **All-missing validation**: `[None, None]` $\rightarrow$ `[3, 3]`.
  - **Decision**: Valid. Validation samples frequently lack features; filling them with the training mean is the intended imputation behavior.
- **No-missing validation**: `[10, 20]` $\rightarrow$ `[10, 20]`.
  - **Decision**: Valid. If no values are missing, all observed numbers pass through unaltered.
- **Empty validation**: `[]` $\rightarrow$ `[]`.
  - **Decision**: Valid. Empty sequence transforms to empty sequence.

#### 3. Invalid Cases (Training Split)
- **All-missing training**: `[None, None, None]` $\rightarrow$ **Rejected (`ValueError`)**.
  - **Exact Boundary Decision**: A mean cannot be mathematically or statistically computed when zero non-missing values exist ($0 / 0$ is undefined). The imputer refuses to guess or silently produce `NaN`; it fails fast and demands at least one valid observation.
- **Empty training**: `[]` $\rightarrow$ **Rejected (`ValueError`)**.
  - **Decision**: Cannot fit on an empty sequence.
- **Unfitted transform**: Calling `transform()` before `fit()` $\rightarrow$ **Rejected (`ValueError`)**.
- **Non-numeric observations**: `[2, "text", 4]` or `[True, None]` $\rightarrow$ **Rejected (`TypeError`)**.

---

## 3. Scope and Limitations

- **Pedagogical Scope**: Pure Python standard library demonstration of fit/transform separation without data leakage.
- **Prerequisites**: Python 3 standard library (`unittest`, `sys`, `typing`). No GPUs, third-party libraries (`scikit-learn`, `numpy`), or cloud APIs are required.
- **Simplifications**:
  - Focuses on 1D numerical sequences rather than multi-column tabular DataFrames or text token tensors.
  - Implements arithmetic mean imputation; does not implement median, mode, or k-NN imputation.

---

## 4. Usage and Invocations

### Direct CLI Invocation
```bash
python3 chapters/en/chapter3/applied-labs/r16-t022/example.py
```
Output:
```text
=== Training-Only Mean Imputation (Fit/Transform Separation) ===
Raw training observations:   [2, None, 4]
Raw validation observations: [100, None]

Fitted mean from training only: 3
Imputed training:   [2, 3, 4]
Imputed validation: [100, 3] (using training mean 3, NOT validation mean 100)

Boundary verification:
PASS: All-missing training input correctly rejected (All-missing training input is rejected: at least one valid observation is required to compute the training mean.)
```

### Python API
```python
from example import TrainingOnlyMeanImputer

imputer = TrainingOnlyMeanImputer()
imputer.fit([2, None, 4])
print(imputer.mean_)  # 3

val_imputed = imputer.transform([100, None])
print(val_imputed)    # [100, 3]
```

---

## 5. Automated Verification

Run unit tests via `unittest`:
```bash
python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t022 -p "test_*.py" -v
```
All 11 tests pass in fresh processes, covering standard fixtures, boundary conditions, and deliberate failure checks.
