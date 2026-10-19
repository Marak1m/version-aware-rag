"""The seven baselines (handoff, "Methods"). Every one speaks the same protocol and shares the
system prompt; they differ in the documents given, one prompt addition, who decides to ask, and
whether the guard runs (it does not, for any baseline).

| Id | Documents | Addition | Asks |
| no_retrieval | none | none | the model |
| plain_rag | mixed, both versions | none | the model |
| mind_version | mixed | "The documents may describe different versions. ..." | the model |
| assume_state | mixed | "If the version is unclear, pick the one ..." | never |
| two_branch | two calls, one version each | version stated in each call | never; both labelled answers when documents conflict |
| always_ask | mixed, then filtered by the answer | version stated after the answer | forced, templated question |
| oracle_docs | target version only | none | the model |
"""

from __future__ import annotations

from varag.bench.instances import Instance
from varag.config import SIDES
from varag.corpus.retrieve import dedupe, keep_version
from varag.llm.client import Backend, ChatRequest, ChatResponse, default_params
from varag.methods.registry import MethodResult, RunContext, scored_code
from varag.pipeline.generate import SYSTEM_PROMPT, Extraction, extract_code, version_label
from varag.pipeline.policy import docs_block, state_line, user_message
from varag.pipeline.questions import parse_version, uncertain_question
from varag.pipeline.user import SimulatedUser

MIND_VERSION = ("The documents may describe different versions. Work out the user's version from their context. "
                "If you cannot, ask.")
ASSUME_STATE = ("If the version is unclear, pick the one the user's context suggests, say which you assumed in a "
                "comment, and add one line on what changes for the other.")


def meta_for(instance: Instance, target: str | None) -> dict:
    return {"instance_id": instance.instance_id, "concept_dir": instance.concept_dir, "target": target,
            "kind": instance.kind, "library": instance.library}


def chat(backend: Backend, messages: list[dict], meta: dict) -> tuple[ChatResponse, Extraction]:
    response = backend.complete(ChatRequest(messages, default_params(), meta))
    return response, extract_code(response.text)


class _Baseline:
    id = ""
    docs = "mixed"          # none | mixed | target
    addition: str | None = None
    may_ask = True

    def chunks(self, instance: Instance, versions: dict, ctx: RunContext) -> list[dict]:
        if self.docs == "none":
            return []
        chunks = ctx.retrieved[instance.instance_id].chunks(instance.library)
        if self.docs == "target":
            return keep_version(chunks, versions[instance.library][instance.target]) if instance.target else dedupe(chunks)
        return chunks

    def answer(self, instance: Instance, backend: Backend, versions: dict[str, dict[str, str]],
               ctx: RunContext | None = None) -> MethodResult:
        ctx = ctx or RunContext()
        chunks = self.chunks(instance, versions, ctx)
        content = user_message(instance.query, instance.context) + docs_block(chunks)
        if self.addition:
            content += "\n" + self.addition + "\n"
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}]
        response, extraction = chat(backend, messages, meta_for(instance, instance.target))
        calls, question, trace = 1, None, {"docs": [c["chunk_id"] for c in chunks], "model": response.model}
        if extraction.kind == "question":
            question = extraction.question
            if self.may_ask:
                user = SimulatedUser(ctx.user_arm, instance.library, versions[instance.library])
                reply = user.reply(question, instance.target)
                trace.update(reply=reply.text, question_relevant=reply.relevant)
                messages += [{"role": "assistant", "content": response.text}, {"role": "user", "content": reply.text}]
                response, extraction = chat(backend, messages, meta_for(instance, instance.target))
                calls = 2
            else:
                trace["question_suppressed"] = True     # the method never asks: a question stands as no code
        return MethodResult(self.id, response.text, extraction, scored_code(extraction, instance, versions), calls=calls,
                            answers_returned=extraction.answers_returned, question=question, trace=trace)


class NoRetrieval(_Baseline):
    id = "no_retrieval"
    docs = "none"


class PlainRag(_Baseline):
    id = "plain_rag"


class MindVersion(_Baseline):
    id = "mind_version"
    addition = MIND_VERSION


class AssumeState(_Baseline):
    id = "assume_state"
    addition = ASSUME_STATE
    may_ask = False


class OracleDocs(_Baseline):
    id = "oracle_docs"
    docs = "target"


class TwoBranch:
    """Two calls, each on one version's documents with that version stated; both labelled answers
    are returned when the documents conflict, one answer otherwise. Never asks."""

    id = "two_branch"

    def answer(self, instance: Instance, backend: Backend, versions: dict[str, dict[str, str]],
               ctx: RunContext | None = None) -> MethodResult:
        ctx = ctx or RunContext()
        retrieved = ctx.retrieved[instance.instance_id]
        chunks = retrieved.chunks(instance.library)
        lib_versions = versions[instance.library]
        if not retrieved.conflict:
            content = user_message(instance.query, instance.context) + docs_block(dedupe(chunks))
            response, extraction = chat(backend, [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}], meta_for(instance, instance.target))
            return MethodResult(self.id, response.text, extraction, scored_code(extraction, instance, versions),
                                answers_returned=extraction.answers_returned, trace={"branches": 1, "model": response.model})
        labelled: dict[str, str] = {}
        blocks = []
        for side in SIDES:
            version = lib_versions[side]
            content = user_message(instance.query, instance.context) + docs_block(keep_version(chunks, version)) + "\n" + state_line(instance.library, version) + "\n"
            response, extraction = chat(backend, [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}], meta_for(instance, side))
            labelled[side] = extraction.code or ""
            blocks.append(f"```python\n{version_label(instance.library, version)}\n{labelled[side]}\n```")
        text = "\n\n".join(blocks)
        extraction = extract_code(text)
        code = labelled.get(instance.target) if instance.target else labelled["old"]
        return MethodResult(self.id, text, extraction, code or None, calls=2, answers_returned=2, labelled=labelled,
                            trace={"branches": 2, "model": response.model})


class AlwaysAsk:
    """A forced, templated question; the documents are then filtered by the answer and the version
    stated. An unsure user gets the mixed documents and no version statement."""

    id = "always_ask"

    def answer(self, instance: Instance, backend: Backend, versions: dict[str, dict[str, str]],
               ctx: RunContext | None = None) -> MethodResult:
        ctx = ctx or RunContext()
        lib_versions = versions[instance.library]
        chunks = ctx.retrieved[instance.instance_id].chunks(instance.library)
        question = uncertain_question(instance.library, lib_versions)
        user = SimulatedUser(ctx.user_arm, instance.library, lib_versions)
        reply = user.reply(question, instance.target)
        side = parse_version(reply.text, lib_versions) if reply.relevant else None
        if side:
            docs, states = keep_version(chunks, lib_versions[side]), "\n" + state_line(instance.library, lib_versions[side]) + "\n"
        else:
            docs, states = chunks, ""
        content = user_message(instance.query, instance.context) + docs_block(docs) + states
        response, extraction = chat(backend, [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}],
                                    meta_for(instance, side or instance.target))
        return MethodResult(self.id, response.text, extraction, scored_code(extraction, instance, versions), calls=1,
                            answers_returned=extraction.answers_returned, question=question,
                            trace={"reply": reply.text, "question_relevant": reply.relevant, "resolved": side, "model": response.model})


BASELINES: dict[str, type] = {m.id: m for m in (NoRetrieval, PlainRag, MindVersion, AssumeState, TwoBranch, AlwaysAsk, OracleDocs)}
