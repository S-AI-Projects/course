"""Schedule optimizer steps for gradient accumulation, plus three applied questions.

This only schedules steps. It does not compute gradients or scale losses, and it
makes no claim about speed, memory or training quality.
"""


def optimizer_steps(num_batches, accumulation, final_partial="step"):
    """Return the batch numbers (1-based) after which the optimizer steps.

    final_partial="step": a leftover group smaller than `accumulation` still steps.
    final_partial="drop": a leftover group is skipped.
    """
    for name, value in (("num_batches", num_batches), ("accumulation", accumulation)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an int")
    if num_batches < 0:
        raise ValueError("num_batches must be 0 or more")
    if accumulation < 1:
        raise ValueError("accumulation must be 1 or more")
    if final_partial not in ("step", "drop"):
        raise ValueError("final_partial must be 'step' or 'drop'")
    steps = list(range(accumulation, num_batches + 1, accumulation))
    if final_partial == "step" and num_batches % accumulation != 0:
        steps.append(num_batches)
    return steps


def covered_batches(num_batches, accumulation, final_partial="step"):
    """Batches whose gradients reach at least one optimizer step."""
    steps = optimizer_steps(num_batches, accumulation, final_partial)
    return list(range(1, (steps[-1] if steps else 0) + 1))


QUESTIONS = [
    {"kind": "predict an output",
     "question": "7 batches, accumulation 3: after which batches does the optimizer step?",
     "answer": "After batches 3, 6 and 7 (batch 7 is the leftover group).",
     "rationale": "Full groups of 3 end at batches 3 and 6. Batch 7 is left over and the "
                  "default policy steps on it.",
     "check": lambda: optimizer_steps(7, 3) == [3, 6, 7]},
    {"kind": "diagnose a failure",
     "question": "A run with 10 batches and accumulation 4 stepped only after batches 4 and 8. "
                 "What went wrong?",
     "answer": "The leftover group (batches 9 and 10) was dropped.",
     "rationale": "Dropping it gives [4, 8]. Stepping on it gives [4, 8, 10].",
     "check": lambda: optimizer_steps(10, 4, "drop") == [4, 8]
     and optimizer_steps(10, 4) == [4, 8, 10]},
    {"kind": "choose a boundary policy",
     "question": "10 batches, accumulation 4, and you do not want to waste data. "
                 "Step on the leftover group or drop it?",
     "answer": "Step on it (final_partial='step').",
     "rationale": "It is the only policy where every batch reaches a step. The last step "
                  "uses fewer batches than the others. This example only schedules steps "
                  "and does not model gradient scaling.",
     "check": lambda: covered_batches(10, 4, "step") == list(range(1, 11))
     and covered_batches(10, 4, "drop") == list(range(1, 9))},
]


def run_questions():
    return [(item["kind"], bool(item["check"]())) for item in QUESTIONS]


def main():
    print("10 batches, accumulation 4 ->", optimizer_steps(10, 4))
    print("0 batches, accumulation 4 ->", optimizer_steps(0, 4))
    for item, (_, passed) in zip(QUESTIONS, run_questions()):
        print()
        print(f"Question ({item['kind']}): {item['question']}")
        print(f"Answer: {item['answer']}")
        print(f"Why: {item['rationale']}")
        print(f"Executable check: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    main()
