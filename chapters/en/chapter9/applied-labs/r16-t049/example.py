#!/usr/bin/env python3
"""
Applied Lab R16-T049: UI Callback Contract — Evaluation Experiment.

This module implements a pure callback function for a text-analysis UI interface (such as Gradio)
and validates its input/output schema independently of the UI framework, connecting directly
to Chapter 9, Section 8 ("Gradio, check!" [gradio-check]).

Lesson Context:
In Chapter 9, Gradio interfaces connect frontend components (e.g. `gr.Textbox`) to backend
Python callback functions (`fn`) that return structured data for outputs (e.g. `gr.JSON`, `gr.Label`).
Validating callback contracts and evaluating execution metrics across different input sizes
offline guarantees predictable behavior without spinning up a live web server.

Contract:
- Input: String from a text component.
- Returns: Dict with 'word_count' (int) and 'unique_count' (int).
- Input "red red apple" returns word_count=3 and unique_count=2.
- Empty text returns zeros (word_count=0, unique_count=0).
- Non-string inputs are rejected with TypeError.

Evaluation Experiment Focus:
- Compares three small controlled input sizes (e.g. small: 3 words, medium: 10 words, large: 25 words).
- Computes contract metrics: correctness (schema compliance), vocabulary richness / uniqueness ratio
  (unique_count / word_count), and execution step scaling.
- Reports trade-offs without claiming real-world model accuracy.
"""

import time
from typing import Any, Dict, List, Optional, Tuple


def analyze_text(text: Any) -> Dict[str, int]:
    """Pure callback function for text analysis.

    Decoupled from Gradio UI for deterministic local verification.

    Args:
        text: Input string from UI component.

    Returns:
        Dict[str, int]: {"word_count": int, "unique_count": int}

    Raises:
        TypeError: If text is not a str.
    """
    if not isinstance(text, str):
        raise TypeError(f"Input must be a string, got {type(text).__name__}")

    words = text.split()
    if not words:
        return {"word_count": 0, "unique_count": 0}

    return {
        "word_count": len(words),
        "unique_count": len(set(words)),
    }


# UI framework callback alias
text_analysis_callback = analyze_text


# ==============================================================================
# Evaluation Experiment
# ==============================================================================
def evaluate_input_configurations() -> List[Dict[str, Any]]:
    """Compare three controlled configurations/input sizes using contract metrics."""
    configurations = [
        {
            "config_id": "small_sentence",
            "description": "Short input (3 words with repetition)",
            "text": "red red apple",
            "expected": {"word_count": 3, "unique_count": 2},
        },
        {
            "config_id": "medium_sentence",
            "description": "Medium input (10 words with repeated phrases)",
            "text": "the quick brown fox jumps over the lazy dog again",
            "expected": {"word_count": 10, "unique_count": 9},
        },
        {
            "config_id": "large_paragraph",
            "description": "Larger input (25 words multi-sentence sequence)",
            "text": (
                "hugging face transformers provides tools for machine learning "
                "models and datasets for natural language processing tasks across "
                "many domains and frameworks with simple python code"
            ),
            "expected": {"word_count": 25, "unique_count": 23},
        },
    ]

    results = []

    for cfg in configurations:
        t0 = time.perf_counter()
        output = analyze_text(cfg["text"])
        duration = time.perf_counter() - t0

        word_cnt = output["word_count"]
        uniq_cnt = output["unique_count"]
        ratio = (uniq_cnt / word_cnt) if word_cnt > 0 else 0.0

        is_correct = (output == cfg["expected"])

        results.append({
            "config_id": cfg["config_id"],
            "description": cfg["description"],
            "text": cfg["text"],
            "word_count": word_cnt,
            "unique_count": uniq_cnt,
            "uniqueness_ratio": round(ratio, 4),
            "is_correct": is_correct,
            "latency_seconds": duration,
        })

    return results


if __name__ == "__main__":
    print("=== UI Callback Contract & Evaluation Experiment (R16-T049) ===")

    # Contract cases
    sample = "red red apple"
    res = analyze_text(sample)
    print(f"Contract Normal: {repr(sample)} -> {res}")
    print(f"Contract Empty:  '' -> {analyze_text('')}\n")

    print("Controlled Input Size Evaluation Experiment:")
    exp_results = evaluate_input_configurations()
    for r in exp_results:
        print(f"  [{r['config_id']}] Words: {r['word_count']}, Unique: {r['unique_count']} "
              f"(Uniqueness Ratio: {r['uniqueness_ratio']}) | Correct: {r['is_correct']}")
