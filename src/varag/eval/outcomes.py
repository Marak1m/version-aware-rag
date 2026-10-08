"""Outcome per instance from the two execution results (handoff, outcome table).

| passes target | passes other | outcome       |
| yes           | no           | target_only   |
| yes           | yes          | portable      |
| no            | yes          | wrong_version |
| no            | no           | broken        |

An infra_error on either side gives ``infra_error``: it is never scored as a failure.
No-conflict controls have no target: ``pass_both``, ``pass_one`` or ``broken``.
"""

from __future__ import annotations

from varag.eval.execute import ExecResult

OUTCOMES = ("target_only", "portable", "wrong_version", "broken", "infra_error")
CONTROL_OUTCOMES = ("pass_both", "pass_one", "broken", "infra_error")


def classify(target: ExecResult, other: ExecResult) -> str:
    if target.status == "infra_error" or other.status == "infra_error":
        return "infra_error"
    if target.passed:
        return "portable" if other.passed else "target_only"
    return "wrong_version" if other.passed else "broken"


def classify_control(old: ExecResult, new: ExecResult) -> str:
    if old.status == "infra_error" or new.status == "infra_error":
        return "infra_error"
    passes = int(old.passed) + int(new.passed)
    return {2: "pass_both", 1: "pass_one", 0: "broken"}[passes]


def intended_pass(outcome: str) -> bool:
    """The primary metric counts target_only and portable."""
    return outcome in ("target_only", "portable")
