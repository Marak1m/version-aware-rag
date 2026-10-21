"""The blend guard (handoff, "Blend guard"): a static check on the generated code that runs before
execution and allows exactly one regeneration.

Detection runs the AST extractor on the output: ``U_old`` and ``U_new`` are the exclusive usages
outside version guards (symbols, keywords, values, config keys on resolved receivers, non-generic
method names); a ``deprecated_in_new`` usage is a soft old-side usage, a violation only when
committed to the new version. The guard abstains, and logs it, on generic names, ``shared_unknown``
callees and calls that forward ``**kwargs`` (the extractor's abstentions).

| State | Violation |
| committed to v | any usage exclusive to the other side, soft usages included when v is new |
| no conflict or unresolved | U_old and U_new both non-empty, soft usages excluded |

Regeneration starts a fresh conversation: the original query and context, the version
statement, one repair block per offending call (replacement from the rule sets or value rules,
with the committed version's chunk; else the two most similar committed-version chunks), the
previous answer, and "Rewrite it using only {library} {version} APIs." The regenerated code is
kept only if it parses, has strictly fewer violations and introduces none; otherwise the first
answer is returned and ``guard_rejected`` logged. No second retry; a remaining violation is
``guard_unresolved``. The guard never sees tests or execution results.
"""

from __future__ import annotations

from varag.bench.instances import Instance
from varag.config import SIDES, other_side
from varag.corpus.retrieve import chunk_for, render, replacements, similar_chunks
from varag.inventory.build import load_diff
from varag.llm.client import Backend, ChatRequest, default_params
from varag.pipeline.generate import SYSTEM_PROMPT, extract_code, finish_prompt, parses
from varag.pipeline.policy import state_line, user_message
from varag.pipeline.signals import StaticUsages, Usage, static_usages
from varag.pipeline.values import parse_gold, value_index

REPAIR_MARKER = "Your previous answer used"


def violations(usages: StaticUsages, committed: str | None) -> list[dict]:
    exclusive = [u for u in usages.usages if not u.guarded]
    if committed:
        other = other_side(committed)
        bad = [u for u in exclusive if u.side == other or (committed == "new" and u.side == "deprecated_in_new")]
    else:
        hard = [u for u in exclusive if u.side in SIDES]
        bad = hard if {u.side for u in hard} == set(SIDES) else []
    return [{"symbol": u.symbol, "side": u.side, "kind": u.kind, "line": u.line, "resolution": u.resolution} for u in bad]


def portable_violations(usages: StaticUsages) -> list[dict]:
    """The portable-first check (L16): every usage outside version guards that is exclusive to one
    side or deprecated on the new one. A draft passes only when this is empty."""
    return [{"symbol": u.symbol, "side": u.side, "kind": u.kind, "line": u.line, "resolution": u.resolution}
            for u in usages.usages if not u.guarded]


def blend_static(usages: StaticUsages) -> bool:
    """U_old and U_new both non-empty outside version guards, soft usages excluded."""
    return bool(usages.old) and bool(usages.new)


def guarded_both_sides(usages: StaticUsages) -> bool:
    sides = {u.side for u in usages.usages if u.guarded and u.side in SIDES}
    return sides == set(SIDES)


def replacement_for(library: str, symbol: str) -> str | None:
    mapping = replacements(library)
    if symbol in mapping:
        return mapping[symbol]
    ref = parse_gold(symbol)
    if ref.has_value:
        for rule in value_index(library).get((ref.owner, ref.param), ()):
            if rule["value"] == ref.value and rule.get("replacement") is not None:
                return f"{ref.owner}({ref.param}={rule['replacement']!r})"
    return None


def chunk_lines(chunk: dict) -> list[str]:
    parts = chunk["parts"]
    lines = []
    if parts.get("signature"):
        lines.append(f"  {parts['fqn']}{parts['signature']}")
    if parts.get("example"):
        lines.append("  Example: " + parts["example"].strip().splitlines()[-1])
    return lines


def repair_block(library: str, version: str, violation: dict) -> str:
    symbol = violation["symbol"]
    lines = [f"{REPAIR_MARKER} `{symbol}` (line {violation['line']}), which does not exist in {library} {version}."]
    replacement = replacement_for(library, symbol)
    if replacement:
        lines.append(f"Use `{replacement}` instead:")
        chunk = chunk_for(library, version, parse_gold(replacement).owner)
        if chunk:
            lines += chunk_lines(chunk)
    else:
        for chunk in similar_chunks(library, version, symbol.replace(".", " ").replace("(", " ").replace(")", " "), 2):
            lines.append(render(chunk))
    return "\n".join(lines)


def repair_prompt(instance: Instance, library: str, version: str | None, violations_: list[dict], previous: str) -> list[dict]:
    content = user_message(instance.query, instance.context)
    if version:
        content += "\n" + state_line(library, version) + "\n\n" + "\n\n".join(repair_block(library, version, v) for v in violations_)
        ending = f"Rewrite it using only {library} {version} APIs."
    else:
        mixed = ", ".join(sorted({v["symbol"] for v in violations_}))
        content += f"\nYour previous answer mixes APIs from different {library} versions: {mixed}."
        ending = f"Rewrite it so that it uses the APIs of one {library} version only."
    content += f"\n\nPrevious answer:\n```python\n{previous.rstrip()}\n```\n{ending}\n"
    content = finish_prompt(content, instance.query, instance.entry_point, no_question=True)
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}]


class BlendGuard:
    """Callable guard for the policy and the methods: (code, committed side, context) -> (code, info)."""

    def __init__(self, backend: Backend, versions: dict[str, dict[str, str]]):
        self.backend = backend
        self.versions = versions

    def __call__(self, code: str, committed: str | None, ctx: dict) -> tuple[str, dict]:
        instance: Instance = ctx["instance"]
        library = ctx["library"]
        diff = load_diff(library)
        usages = static_usages(code, diff)
        info: dict = {"flagged": False, "outcome": "clean", "violations": [], "abstained": usages.abstained,
                      "blend_static": blend_static(usages) if usages.parsed else None, "pre_guard_code": code, "calls": 0}
        if not usages.parsed:
            info["outcome"] = "unparsed"
            return code, info
        found = violations(usages, committed)
        if not found:
            return code, info
        info.update(flagged=True, violations=found, regenerated=True, calls=1)
        version = self.versions[library][committed] if committed else None
        request = ChatRequest(repair_prompt(instance, library, version, found, code), default_params(),
                              meta={"instance_id": instance.instance_id, "concept_dir": instance.concept_dir, "target": committed or instance.target,
                                    "kind": instance.kind, "library": library, "repair": True})
        response = self.backend.complete(request)
        extraction = extract_code(response.text)
        new_code = extraction.code
        if not new_code or not parses(new_code):
            info.update(accepted=False, outcome="guard_rejected", reason="regenerated answer has no parsable code")
            return code, info
        after = violations(static_usages(new_code, diff), committed)
        new_symbols = {v["symbol"] for v in after} - {v["symbol"] for v in found}
        accepted = len(after) < len(found) and not new_symbols
        info.update(accepted=accepted, violations_after=after)
        if not accepted:
            info.update(outcome="guard_rejected", reason="not strictly fewer violations" if not new_symbols else f"new violations {sorted(new_symbols)}")
            return code, info
        info["outcome"] = "fixed" if not after else "guard_unresolved"
        return new_code, info
