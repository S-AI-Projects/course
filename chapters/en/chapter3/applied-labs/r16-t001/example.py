"""R16-T001: learning-curve divergence check (simulation with hand-written losses).

Companion to "Understanding Learning Curves" -> "Overfitting"
(chapters/en/chapter3/5.mdx). The lesson lists the first overfitting symptom as
"training loss continues to decrease while validation loss increases". This
example turns that sentence into one explicit, testable teaching rule:

    Flag divergence when, between the last two recorded steps,
    training loss falls AND validation loss rises.

Scope and limits:
- The loss values are typed in by hand. No model is trained, nothing is
  downloaded, and no real training run is being diagnosed.
- The rule only looks at the last two steps. A real early-stopping callback
  (e.g. EarlyStoppingCallback(early_stopping_patience=3) in the lesson) waits
  for several evaluations without improvement before acting, because a single
  noisy step can trigger this rule.
- "Equal" counts as neither falling nor rising, so a flat (plateaued)
  validation loss is NOT flagged by this rule.
"""

from numbers import Real

# Fixture from the task: validation goes 0.6 -> 0.7 (rises) while training
# goes 0.5 -> 0.3 (falls), so the last step is flagged.
TRAINING_LOSSES = [0.8, 0.5, 0.3]
VALIDATION_LOSSES = [0.9, 0.6, 0.7]

# Contrast fixture: both losses keep falling, which is healthy, not flagged.
HEALTHY_VALIDATION_LOSSES = [0.9, 0.6, 0.4]


def _validate(name, losses):
    """Reject inputs the rule cannot be applied to."""
    if not isinstance(losses, (list, tuple)):
        raise TypeError(f"{name} must be a list or tuple of numbers")
    if len(losses) < 2:
        raise ValueError(f"{name} needs at least 2 values to compare the last two steps")
    for value in losses:
        # bool is a subclass of int in Python, so exclude it explicitly.
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"{name} must contain only numbers, got {value!r}")


def detect_divergence(training, validation):
    """Return True if training loss fell while validation loss rose on the last step.

    training, validation: equal-length sequences of loss values, one per
    evaluation step, oldest first.
    """
    _validate("training", training)
    _validate("validation", validation)
    if len(training) != len(validation):
        raise ValueError(
            f"training and validation must have the same length "
            f"({len(training)} != {len(validation)})"
        )

    training_fell = training[-1] < training[-2]
    validation_rose = validation[-1] > validation[-2]
    return training_fell and validation_rose


if __name__ == "__main__":
    print(f"training   = {TRAINING_LOSSES}")
    print(f"validation = {VALIDATION_LOSSES}")
    print(f"divergence on last step: {detect_divergence(TRAINING_LOSSES, VALIDATION_LOSSES)}")
    print()
    print(f"training   = {TRAINING_LOSSES}")
    print(f"validation = {HEALTHY_VALIDATION_LOSSES}")
    print(f"divergence on last step: {detect_divergence(TRAINING_LOSSES, HEALTHY_VALIDATION_LOSSES)}")
