"""Method registry. Every method speaks the same protocol (handoff, "Interaction protocol").

M3 ships ``direct`` (query and context in one call). M5 adds ``va_rag`` and its three ablations
on top of the policy; the seven baselines arrive in M6 through the same ``answer`` interface.
``RunContext`` carries what a method may need beyond the instance: the retrieved documents, the
concepts, the user arm and the blend guard.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from varag.bench.instances import Instance
from varag.llm.client import Backend, ChatRequest, ChatResponse, default_params
from varag.pipeline.generate import SYSTEM_PROMPT, Extraction, extract_code, pick_labelled, version_label


@dataclass
class RunContext:
    user_arm: str = "knows"
    retrieved: dict = field(default_factory=dict)      # instance_id -> RetrievedSet
    concepts: dict = field(default_factory=dict)       # concept_id -> Concept
    guard: Callable | None = None                      # the blend guard (M6)


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
    labelled: dict[str, str] = field(default_factory=dict)   # side -> code when two answers were returned


def user_message(query: str, context: str = "") -> str:
    text = f"Task:\n{query.strip()}\n"
    if context.strip():
        text += f"\nContext from the user:\n{context.strip()}\n"
    return text


class Method(Protocol):
    id: str

    def answer(self, instance: Instance, backend: Backend, versions: dict[str, dict[str, str]],
               ctx: RunContext | None = None) -> MethodResult: ...


def scored_code(extraction: Extraction, instance: Instance, versions: dict[str, dict[str, str]]) -> str | None:
    """The block to score: the one labelled with the target version when there are labels."""
    if extraction.kind != "code":
        return None
    if extraction.labelled and instance.target:
        return pick_labelled(extraction, versions[instance.library][instance.target]) or extraction.code
    return extraction.code


class Direct:
    id = "direct"

    def answer(self, instance: Instance, backend: Backend, versions: dict[str, dict[str, str]],
               ctx: RunContext | None = None) -> MethodResult:
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


class VaRag:
    """VA-RAG through the policy; the ablations flip one switch each."""

    id = "va_rag"
    infer_enabled = True
    ask_enabled = True
    guarded = True

    def answer(self, instance: Instance, backend: Backend, versions: dict[str, dict[str, str]],
               ctx: RunContext | None = None) -> MethodResult:
        from varag.pipeline.policy import run_policy
        from varag.pipeline.user import SimulatedUser

        if ctx is None or instance.instance_id not in ctx.retrieved:
            raise RuntimeError(f"{self.id} needs the retrieved documents for {instance.instance_id}")
        concept = ctx.concepts[instance.concept_id]
        user = SimulatedUser(ctx.user_arm, instance.library, versions[instance.library])
        result = run_policy(instance, concept, backend, versions, ctx.retrieved[instance.instance_id], user,
                            infer_enabled=self.infer_enabled, ask_enabled=self.ask_enabled,
                            guard=ctx.guard if self.guarded else None)
        trace = {**result.trace(), "model": getattr(backend, "name", "")}
        if len(result.answers) == 2:
            labelled = {a.side: a.code or "" for a in result.answers}
            blocks = [f"```python\n{version_label(instance.library, versions[instance.library][a.side])}\n{a.code or ''}\n```" for a in result.answers]
            text = "\n\n".join(blocks)
            extraction = extract_code(text)
            code = labelled.get(instance.target) if instance.target else labelled["old"]
            return MethodResult(self.id, text, extraction, code, calls=result.calls, answers_returned=2,
                                question=result.question, trace=trace, labelled=labelled)
        answer = result.answers[0]
        return MethodResult(self.id, answer.response_text, answer.extraction, answer.code, calls=result.calls,
                            answers_returned=1 if answer.code else 0, question=result.question, trace=trace)


class VaRagNoInfer(VaRag):
    id = "va_rag_no_infer"
    infer_enabled = False


class VaRagNoAsk(VaRag):
    id = "va_rag_no_ask"
    ask_enabled = False


class VaRagNoGuard(VaRag):
    id = "va_rag_no_guard"
    guarded = False


METHODS: dict[str, type] = {"direct": Direct, "va_rag": VaRag, "va_rag_no_infer": VaRagNoInfer,
                            "va_rag_no_ask": VaRagNoAsk, "va_rag_no_guard": VaRagNoGuard}


def get_methods(spec: str) -> list[Method]:
    ids = list(METHODS) if spec in ("all", "") else [s.strip() for s in spec.split(",") if s.strip()]
    unknown = [i for i in ids if i not in METHODS]
    if unknown:
        raise KeyError(f"unknown method(s) {unknown}; available: {sorted(METHODS)}")
    return [METHODS[i]() for i in ids]
