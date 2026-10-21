"""The VA-RAG policy (handoff, "Policy"): decision, document filtering, one question at most,
negative constraints, the "both" fallback, and the trace record.

    signals  = extract_signals(query, context)
    decision = infer(signals)                      # INFER(v) | UNCERTAIN | CONTEXT_CONFLICT
    if INFER:            versions, by = [v], "inferred"
    elif no doc conflict: versions, by = [], "no_conflict"       # answer once on the deduplicated set
    else:                ask; v = parse_version(reply); versions, by = ([v], "asked") if v else ([old, new], "both")

``portable_first`` (L16, ``va_rag_portable_first``): where the policy would ask, a draft comes
first, on the ``shared_same`` chunks with "Use only APIs that exist in both {library} {old} and
{new}."; it is returned without a question (by = "portable") when the guard's static check finds no
exclusive or deprecated usage outside version guards, and discarded otherwise.

Generation goes through the ``Backend`` interface, so the policy runs on the mock backends now
and on the real client in M6. The blend guard is a callable the caller passes (M6); without one,
code is returned as generated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from varag.bench.instances import Instance
from varag.bench.schema import Concept
from varag.config import SIDES, load_experiment
from varag.corpus.retrieve import RetrievedSet, dedupe, keep_version, render, replacements
from varag.llm.client import Backend, ChatRequest, ChatResponse, default_params
from varag.pipeline.extract import Signals, extract_signals
from varag.pipeline.generate import SYSTEM_PROMPT, Extraction, extract_code, finish_prompt
from varag.pipeline.infer import CONTEXT_CONFLICT, INFER, UNCERTAIN, Decision, infer
from varag.pipeline.questions import conflict_question, parse_version, uncertain_question
from varag.pipeline.user import Reply, SimulatedUser
from varag.pipeline.values import value_index

# (code, committed side or None, context) -> (code to use, guard info). Supplied by M6.
Guard = Callable[[str, str | None, dict], tuple[str, dict]]


@dataclass
class Answer:
    side: str | None            # the version this answer is for; None when unresolved or no conflict
    by: str                     # inferred | asked | both | no_conflict | unresolved
    response_text: str
    extraction: Extraction
    code: str | None
    guard: dict = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    kept: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)


@dataclass
class PolicyResult:
    answers: list[Answer]
    decision: Decision
    signals: Signals
    question: str | None = None
    reply: Reply | None = None
    calls: int = 0
    portable: dict | None = None     # the portable-first draft and its check, when one was tried (L16)

    @property
    def by(self) -> str:
        return self.answers[0].by if self.answers else "none"

    def trace(self) -> dict:
        return {
            "signals": self.signals.to_dict(),
            "decision": self.decision.to_dict(),
            "by": self.by,
            "question": self.question,
            "reply": self.reply.text if self.reply else None,
            "question_relevant": self.reply.relevant if self.reply else None,
            "answers": [{"side": a.side, "kept": a.kept, "dropped": a.dropped, "constraints": a.constraints, "guard": a.guard,
                         "kind": a.extraction.kind} for a in self.answers],
            "calls": self.calls,
            "portable": self.portable,
        }


def user_message(query: str, context: str) -> str:
    text = f"Task:\n{query.strip()}\n"
    if context.strip():
        text += f"\nContext from the user:\n{context.strip()}\n"
    return text


def docs_block(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    flags = load_experiment().get("corpus", {})
    rendered = [render(c, bool(flags.get("show_version_tags", True)), bool(flags.get("strip_deprecation_notes", False))) for c in chunks]
    return "\nDocumentation:\n\n" + "\n\n".join(rendered) + "\n"


def state_line(library: str, version: str) -> str:
    return f"The user is on {library} {version}. Use only APIs available in that version."


def portable_line(library: str, versions: dict[str, str]) -> str:
    """The portable-first draft's instruction (handoff L16)."""
    return f"Use only APIs that exist in both {library} {versions['old']} and {versions['new']}."


def shared_same_chunks(chunks: list[dict], diff: dict) -> list[dict]:
    """The chunks whose symbol is in ``shared_same`` (the portable allowlist), one per symbol."""
    from varag.inventory.diff import bucket_of

    return dedupe([c for c in chunks if bucket_of(diff, c["symbols"][0]) == "shared_same"])


def unavailable_symbols(signals: Signals, side: str, library: str) -> list[tuple[str, str | None]]:
    """Every symbol, keyword, value or config key from the user's context that does not exist in
    the committed version: the one an error names, and any other-version usage (handoff L5)."""
    mapping = replacements(library)
    values = value_index(library)
    out: dict[str, str | None] = {}
    for s in signals.signals:
        if s.kind in ("import", "symbol", "keyword", "value", "config_key", "method"):
            unavailable = s.side != side
        elif s.kind == "error_symbol":
            unavailable = s.side == side and not s.symbol.startswith("*")   # raised on this side: it lacks the symbol
        elif s.kind == "error_value":
            unavailable = s.side == side
        else:
            continue
        if not unavailable:
            continue
        replacement = mapping.get(s.symbol)
        if replacement is None and s.kind == "value":
            owner, _, rest = s.symbol.partition("(")
            param = rest.split("=", 1)[0]
            for rule in values.get((owner, param), ()):
                if s.symbol.endswith(f"={rule['value']!r})") and rule.get("replacement") is not None:
                    replacement = f"{param}={rule['replacement']!r}"
        out.setdefault(s.symbol, replacement)
    return sorted(out.items())


def constraint_lines(library: str, version: str, items: list[tuple[str, str | None]]) -> list[str]:
    lines = []
    for symbol, replacement in items:
        line = f"`{symbol}` is not available in {library} {version}."
        if replacement:
            line += f" Use `{replacement}`."
        lines.append(line)
    return lines


def make_question(decision: Decision, signals: Signals, library: str, versions: dict[str, str]) -> str:
    if decision.kind == CONTEXT_CONFLICT:
        pins = [s for s in signals.signals if s.kind == "pin"]
        for pin in pins:
            other = "new" if pin.side == "old" else "old"
            symbols = [s for s in signals.signals if s.side == other and s.kind in ("import", "symbol", "keyword", "value", "config_key", "method")]
            if symbols:
                return conflict_question(library, versions, pin.detail or pin.symbol, symbols[0].symbol, other)
    return uncertain_question(library, versions)


def generate(backend: Backend, instance: Instance, chunks: list[dict], states: list[str], target: str | None) -> tuple[ChatResponse, Extraction]:
    content = user_message(instance.query, instance.context) + docs_block(chunks)
    if states:
        content += "\n" + "\n".join(states) + "\n"
    content = finish_prompt(content, instance.query, instance.entry_point, no_question=True)
    request = ChatRequest(
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}],
        params=default_params(),
        meta={"instance_id": instance.instance_id, "concept_dir": instance.concept_dir, "target": target,
              "kind": instance.kind, "library": instance.library},
    )
    response = backend.complete(request)
    return response, extract_code(response.text)


def portable_draft(backend: Backend, instance: Instance, chunks: list[dict], versions: dict[str, str], diff: dict) \
        -> tuple[ChatResponse, Extraction, list[dict], dict]:
    """The portable-first draft (handoff L16): the shared_same chunks only and the portable
    instruction; the guard's static check decides whether it stands without a question."""
    from varag.pipeline.guard import portable_violations
    from varag.pipeline.signals import static_usages

    docs = shared_same_chunks(chunks, diff)
    response, extraction = generate(backend, instance, docs, [portable_line(instance.library, versions)], instance.target)
    check: dict = {"kept": [c["chunk_id"] for c in docs], "kind": extraction.kind, "code": extraction.code, "violations": [], "abstained": []}
    if not extraction.code:
        check.update(accepted=False, reason="no code")
        return response, extraction, docs, check
    usages = static_usages(extraction.code, diff)
    if not usages.parsed:
        check.update(accepted=False, reason="does not parse")
        return response, extraction, docs, check
    found = portable_violations(usages)
    check.update(accepted=not found, violations=found, abstained=usages.abstained,
                 reason="no exclusive or deprecated usage" if not found else "exclusive or deprecated usage")
    return response, extraction, docs, check


def run_policy(instance: Instance, concept: Concept, backend: Backend, versions: dict[str, dict[str, str]],
               retrieved: RetrievedSet, user: SimulatedUser, *, infer_enabled: bool = True, ask_enabled: bool = True,
               guard: Guard | None = None, diff: dict | None = None, portable_first: bool = False) -> PolicyResult:
    library = instance.library
    lib_versions = versions[library]
    signals = extract_signals(instance.query, instance.context, library, diff)
    if infer_enabled:
        decision = infer(signals)
    else:
        decision = Decision(UNCERTAIN, None, {s: signals.S(s) for s in SIDES}, {s: signals.D(s) for s in SIDES},
                            signals.S("old") - signals.S("new"), "inference disabled (ablation)")
    chunks = retrieved.chunks(library)
    question = reply = None
    draft = None

    if decision.kind == INFER:
        sides, by = [decision.side], "inferred"
    elif not retrieved.conflict:
        sides, by = [], "no_conflict"
    elif not ask_enabled:
        sides, by = [], "unresolved"
    else:
        # Portable first (L16): where the policy would ask, try a version-independent answer first
        # and ask only if the guard finds an exclusive or deprecated usage in it.
        if portable_first:
            from varag.inventory.build import load_diff

            draft = portable_draft(backend, instance, chunks, lib_versions, diff or load_diff(library))
        if draft is not None and draft[3]["accepted"]:
            sides, by = [], "portable"
        else:
            question = make_question(decision, signals, library, lib_versions)
            reply = user.reply(question, instance.target)
            side = parse_version(reply.text, lib_versions) if reply.relevant else None
            sides, by = ([side], "asked") if side else (list(SIDES), "both")

    answers: list[Answer] = []
    calls = 1 if draft is not None else 0
    if by == "portable":
        response, extraction, docs, check = draft
        info = {"flagged": False, "outcome": "clean", "violations": [], "abstained": check["abstained"], "pre_guard_code": extraction.code,
                "calls": 0, "portable_draft": True}
        answers.append(Answer(None, by, response.text, extraction, extraction.code, info, [],
                              kept=check["kept"], dropped=[c["chunk_id"] for c in chunks if c["chunk_id"] not in check["kept"]]))
    elif not sides:
        docs = dedupe(chunks) if by == "no_conflict" else chunks
        response, extraction = generate(backend, instance, docs, [], instance.target)
        calls += 1
        code, info = extraction.code, {}
        if guard and code:
            code, info = guard(code, None, {"instance": instance, "library": library})
        answers.append(Answer(None, by, response.text, extraction, code, info, [],
                              kept=[c["chunk_id"] for c in docs], dropped=[c["chunk_id"] for c in chunks if c not in docs]))
    else:
        for side in sides:
            version = lib_versions[side]
            docs = keep_version(chunks, version)
            constraints = constraint_lines(library, version, unavailable_symbols(signals, side, library))
            response, extraction = generate(backend, instance, docs, [state_line(library, version), *constraints], side)
            calls += 1
            code, info = extraction.code, {}
            if guard and code:
                code, info = guard(code, side, {"instance": instance, "library": library, "version": version})
            answers.append(Answer(side, by, response.text, extraction, code, info, constraints,
                                  kept=[c["chunk_id"] for c in docs], dropped=[c["chunk_id"] for c in chunks if c["version"] != version]))
    return PolicyResult(answers, decision, signals, question, reply, calls, draft[3] if draft is not None else None)
