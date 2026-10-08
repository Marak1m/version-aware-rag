"""Method registry. Every method speaks the same protocol (handoff, "Interaction protocol").

M3 ships one method, ``direct``: the query and context go to the backend in one call and
the code is extracted. The seven baselines, VA-RAG and its ablations arrive in M6 through
the same ``answer`` interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from varag.bench.instances import Instance
from varag.llm.client import Backend, ChatRequest, ChatResponse, default_params
from varag.pipeline.generate import SYSTEM_PROMPT, Extraction, extract_code, pick_labelled


@dataclass
class MethodResult:
    method: str
    response_text: str
    extraction: Extraction
    code: str | None
    calls: int = 1
    answers_returned: int = 1
    question: str | None = None
    trace: dict = field(default_factory=dict)


def user_message(query: str, context: str = "") -> str:
    text = f"Task:\n{query.strip()}\n"
    if context.strip():
        text += f"\nContext from the user:\n{context.strip()}\n"
    return text


class Method(Protocol):
    id: str

    def answer(self, instance: Instance, backend: Backend, versions: dict[str, dict[str, str]]) -> MethodResult: ...


def scored_code(extraction: Extraction, instance: Instance, versions: dict[str, dict[str, str]]) -> str | None:
    """The block to score: the one labelled with the target version when there are labels."""
    if extraction.kind != "code":
        return None
    if extraction.labelled and instance.target:
        return pick_labelled(extraction, versions[instance.library][instance.target]) or extraction.code
    return extraction.code


class Direct:
    id = "direct"

    def answer(self, instance: Instance, backend: Backend, versions: dict[str, dict[str, str]]) -> MethodResult:
        request = ChatRequest(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message(instance.query, instance.context)},
            ],
            params=default_params(),
            meta={"instance_id": instance.instance_id, "concept_dir": instance.concept_dir,
                  "target": instance.target, "kind": instance.kind, "library": instance.library},
        )
        response: ChatResponse = backend.complete(request)
        extraction = extract_code(response.text)
        return MethodResult(
            method=self.id,
            response_text=response.text,
            extraction=extraction,
            code=scored_code(extraction, instance, versions),
            answers_returned=extraction.answers_returned,
            question=extraction.question,
            trace={"cached": response.cached, "model": response.model},
        )


METHODS: dict[str, type] = {"direct": Direct}


def get_methods(spec: str) -> list[Method]:
    ids = list(METHODS) if spec in ("all", "") else [s.strip() for s in spec.split(",") if s.strip()]
    unknown = [i for i in ids if i not in METHODS]
    if unknown:
        raise KeyError(f"unknown method(s) {unknown}; available: {sorted(METHODS)}")
    return [METHODS[i]() for i in ids]
