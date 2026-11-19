"""R16-T002: a reproducible error and a structured bug report (simulation).

Companion to "Asking for help on the forums" (chapters/en/chapter8/3.mdx).
The lesson's running example is an IndexError raised because an input is
longer than the model's maximum sequence length (583 > 512). This file copies
that situation with a toy "model" that has only MAX_POSITIONS = 8 position
slots, so the failure is tiny, deterministic and needs no download.

It then builds the five-field report the lesson argues for:
environment, exact command, expected result, actual result, full traceback.

Boundary decision: positions are numbered 0..MAX_POSITIONS-1. An input of
exactly MAX_POSITIONS tokens uses slots 0..7 and is valid. One more token asks
for slot 8, which does not exist, so it raises IndexError.

Scope and limits:
- `embed_positions` is a stand-in for a forward pass, not real Transformers
  code. The real library's message and traceback differ.
- The report includes only the Python version and OS name as "environment",
  and replaces the home directory in paths with "~". It never reads
  environment variables, so tokens such as HF_TOKEN cannot leak into it.
"""

import platform
import traceback
from pathlib import Path

MAX_POSITIONS = 8

# Fixture: 9 token ids, one more than the toy model supports.
FAILING_INPUT = [101, 7592, 2088, 2003, 1037, 2146, 6251, 2005, 102]
# Removing the triggering (9th) token gives exactly MAX_POSITIONS tokens.
FIXED_INPUT = FAILING_INPUT[:-1]

COMMAND = "python3 chapters/en/chapter8/applied-labs/r16-t002/example.py"
REPORT_FIELDS = ("environment", "command", "expected", "actual", "traceback")


def embed_positions(token_ids, max_positions=MAX_POSITIONS):
    """Toy forward pass: give each token the label of its position slot.

    Raises IndexError when there are more tokens than position slots.
    """
    if not isinstance(token_ids, list) or not all(
        isinstance(t, int) and not isinstance(t, bool) for t in token_ids
    ):
        raise TypeError("token_ids must be a list of ints")
    if not token_ids:
        raise ValueError("token_ids must contain at least one token")

    position_table = [f"pos{i}" for i in range(max_positions)]
    # No length check on purpose: this lookup is the bug being reported.
    return [position_table[i] for i in range(len(token_ids))]


def _redact(text):
    """Replace the home directory so the report does not reveal local paths."""
    return text.replace(str(Path.home()), "~")


def build_report(token_ids, command=COMMAND):
    """Run embed_positions on token_ids and return the five-field report."""
    report = {
        "environment": f"Python {platform.python_version()} on {platform.system()}",
        "command": command,
        "expected": f"{len(token_ids)} position labels (pos0..pos{len(token_ids) - 1})",
    }
    try:
        labels = embed_positions(token_ids)
    except Exception as exc:  # the report should describe any failure
        report["actual"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = _redact(traceback.format_exc()).rstrip()
    else:
        report["actual"] = f"returned {len(labels)} position labels"
        report["traceback"] = "(no exception)"
    return report


def render_report(report):
    """Format the report as a forum-ready Markdown body."""
    lines = []
    for field in REPORT_FIELDS:
        lines.append(f"**{field}**")
        if field == "traceback":
            lines.append("```")
            lines.append(report[field])
            lines.append("```")
        else:
            lines.append(report[field])
        lines.append("")
    return "\n".join(lines).rstrip()


if __name__ == "__main__":
    print(f"--- failing input ({len(FAILING_INPUT)} tokens, max {MAX_POSITIONS}) ---")
    print(render_report(build_report(FAILING_INPUT)))
    print()
    print(f"--- fixed input ({len(FIXED_INPUT)} tokens: last token removed) ---")
    print(build_report(FIXED_INPUT)["actual"])
