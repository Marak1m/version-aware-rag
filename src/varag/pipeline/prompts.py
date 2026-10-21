"""The prompt freeze (OpenRouter note, item 5): one hash over every text the methods send.

``prompt_texts`` renders each template with placeholder values, so the hash moves when any wording
changes (the system prompt, the signature stub, the no-question line, the method additions, the
version statement, the question templates, the user's replies, the repair prompt) and does not
move for anything else. ``configs/experiment.yaml`` keeps the frozen hash under ``prompts``;
``varag run`` refuses the test split while the live hash differs from it.
"""

from __future__ import annotations

import hashlib
import json


def prompt_texts() -> dict[str, str]:
    from varag.methods import baselines
    from varag.pipeline import generate, policy, questions, user
    from varag.pipeline.guard import repair_prompt

    versions = {"old": "1.0.0", "new": "2.0.0"}

    class _Inst:
        query = "Write `f(x)` returning x."
        context = "CONTEXT"
        entry_point = "f"

    # The repair template's own wording: committed (no violation block, which quotes corpus chunks)
    # and unresolved (which names the mixed symbols).
    repair = [repair_prompt(_Inst(), "LIB", "2.0.0", [], "PREVIOUS"),
              repair_prompt(_Inst(), "LIB", None, [{"symbol": "LIB.old"}], "PREVIOUS")]
    return {
        "system": generate.SYSTEM_PROMPT,
        "no_question": generate.NO_QUESTION,
        "stub": generate.signature_stub("Write `f(x, y)` returning x.", "f"),
        "after_reply": generate.after_reply("REPLY"),
        "task": policy.user_message("QUERY", "CONTEXT"),
        "state_line": policy.state_line("LIB", "2.0.0"),
        "portable_line": policy.portable_line("LIB", versions),
        "mind_version": baselines.MIND_VERSION,
        "assume_state": baselines.ASSUME_STATE,
        "uncertain_question": questions.uncertain_question("pandas", versions),
        "conflict_question": questions.conflict_question("pandas", versions, "PIN", "SYMBOL", "new"),
        "user_knows": user.SimulatedUser("knows", "pandas", versions).reply("which version?", "new").text,
        "user_unsure": user.SimulatedUser("unsure", "pandas", versions).reply("which version?", "new").text,
        "user_irrelevant": user.SimulatedUser("knows", "pandas", versions).reply("which OS?", "new").text,
        "repair": json.dumps(repair, sort_keys=True),
    }


def prompts_sha256() -> str:
    return hashlib.sha256(json.dumps(prompt_texts(), sort_keys=True).encode("utf-8")).hexdigest()


def frozen_prompts() -> dict | None:
    from varag.config import load_experiment

    block = load_experiment().get("prompts") or {}
    return block if block.get("frozen_on") else None
