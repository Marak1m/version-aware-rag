"""Mock backends: harness anchors that need no GPU.

mock_ref    returns the target version's reference        -> 100% intended-version pass
mock_wrong  returns the other version's reference         -> 0%, every instance wrong_version
The reference for a version is the concept's native one: ref_portable for a control and for the
new side of a one_directional concept.
mock_blend, mock_ask arrive in M6 with the guard and the ask path.
"""

from __future__ import annotations

from pathlib import Path

from varag.bench.schema import load_concept
from varag.config import other_side
from varag.llm.client import ChatRequest, ChatResponse

REF_FILES = {"old": "ref_old.py", "new": "ref_new.py", "portable": "ref_portable.py"}


def fenced(code: str) -> str:
    return f"```python\n{code.rstrip()}\n```"


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
        if self.behaviour == "ref":
            side = concept.native_ref(target) if target else "portable"
        elif self.behaviour == "wrong":
            side = concept.native_ref(other_side(target)) if target else "portable"
        else:
            raise NotImplementedError(f"mock behaviour {self.behaviour!r} is not implemented until M6")
        return ChatResponse(text=fenced(self._reference(concept_dir, side)), model=self.name)
