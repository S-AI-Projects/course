# R16-T040: gradient-accumulation accounting

Applied example for the lesson "Fine-tuning a model with the Trainer API" (`chapters/en/chapter3/3.mdx`).

Task type: Scenario assessment.

## What it shows

Schedules optimizer steps for a batch count and an accumulation factor and handles the final partial group explicitly. Ten batches with accumulation 4 step after batches 4, 8 and 10. Zero batches give no step. Three applied questions (predict, diagnose, choose a policy) each have a rationale and an executable check.

## Run it

Python 3 standard library only.

```bash
python3 example.py
python3 -m unittest discover -s chapters/en/chapter3/applied-labs/r16-t040 -p "test_*.py"
```

## Output of `python3 example.py`

```text
10 batches, accumulation 4 -> [4, 8, 10]
0 batches, accumulation 4 -> []

Question (predict an output): 7 batches, accumulation 3: after which batches does the optimizer step?
Answer: After batches 3, 6 and 7 (batch 7 is the leftover group).
Why: Full groups of 3 end at batches 3 and 6. Batch 7 is left over and the default policy steps on it.
Executable check: PASS

Question (diagnose a failure): A run with 10 batches and accumulation 4 stepped only after batches 4 and 8. What went wrong?
Answer: The leftover group (batches 9 and 10) was dropped.
Why: Dropping it gives [4, 8]. Stepping on it gives [4, 8, 10].
Executable check: PASS

Question (choose a boundary policy): 10 batches, accumulation 4, and you do not want to waste data. Step on the leftover group or drop it?
Answer: Step on it (final_partial='step').
Why: It is the only policy where every batch reaches a step. The last step uses fewer batches than the others. This example only schedules steps and does not model gradient scaling.
Executable check: PASS
```

## Scope and limits

It only schedules steps. It does not compute gradients or scale losses. It is a local, deterministic teaching fixture. It makes no claim about real hardware, cloud service behavior or trained-model performance.
