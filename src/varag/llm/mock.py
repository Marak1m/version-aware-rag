"""Mock backends: harness anchors that need no GPU.

mock_ref    returns the target version's reference        -> 100% intended-version pass
mock_wrong  returns the other version's reference         -> 0%, every instance wrong_version
mock_blend  returns the old reference plus one line using the new-side gold symbol, so the code
            mixes both versions; on a repair prompt it returns the clean target reference
            (guard and blend-metric tests)
mock_ask    asks a version question first, then returns the target reference (ask-path tests)
The reference for a version is the concept's native one: ref_portable for a control and for the
new side of a one_directional concept.
"""

from __future__ import annotations

from pathlib import Path

from varag.bench.schema import load_concept
from varag.config import other_side
from varag.llm.client import ChatRequest, ChatResponse
from varag.pipeline.values import parse_gold

REF_FILES = {"old": "ref_old.py", "new": "ref_new.py", "portable": "ref_portable.py"}
REPAIR_MARKER = "Your previous answer used"


def fenced(code: str) -> str:
    return f"```python\n{code.rstrip()}\n```"


def blend_line(gold_new: str) -> str:
    """One statement that uses the new-side gold symbol through its package."""
    ref = parse_gold(gold_new)
    module = ref.owner.split(".")[0]
    if ref.has_value:
        return f"import {module}\n_blend = {ref.owner}({ref.param}={ref.value!r})"
    if ref.param:
        return f"import {module}\n_blend = {ref.owner}({ref.param}=None)"
    return f"import {module}\n_blend = {ref.owner}"


class MockBackend:
    def __init__(self, name: str, behaviour: str):
        self.name = name
        self.behaviour = behaviour
        self.calls = 0

    def _reference(self, concept_dir: Path, side: str) -> str:
        path = concept_dir / REF_FILES[side]
        if not path.exists():
            raise FileNotFoundError(f"{self.name}: {path} is missing")
        return path.read_text(encoding="utf-8")

    def complete(self, request: ChatRequest) -> ChatResponse:
        self.calls += 1
        meta = request.meta
        concept_dir = Path(meta["concept_dir"])
        concept = load_concept(concept_dir)
        target = meta.get("target")
        native = (lambda side: concept.native_ref(side)) if target else (lambda side: "portable")
        last_user = next((m["content"] for m in reversed(request.messages) if m["role"] == "user"), "")
        if self.behaviour == "ref":
            side = native(target) if target else "portable"
        elif self.behaviour == "wrong":
            side = native(other_side(target)) if target else "portable"
        elif self.behaviour == "ask":
            asked = any(m["role"] == "assistant" for m in request.messages)
            if not asked:
                return ChatResponse(text=f"QUESTION: Which version of {concept.library} are you on?", model=self.name)
            side = native(target) if target else "portable"
        elif self.behaviour == "blend":
            if REPAIR_MARKER in last_user or concept.is_control or not concept.gold.get("new"):
                side = native(target) if target else "portable"
            else:
                code = self._reference(concept_dir, concept.native_ref("old")).rstrip() + "\n" + blend_line(concept.gold["new"][0]) + "\n"
                return ChatResponse(text=fenced(code), model=self.name)
        else:
            raise NotImplementedError(f"mock behaviour {self.behaviour!r}")
        return ChatResponse(text=fenced(self._reference(concept_dir, side)), model=self.name)
