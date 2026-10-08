"""Chunk composition (handoff L11): fully qualified name, version tag, the exact signature for that
version (from the inventory), a one-line description, and one short example, in that order. A
deprecation note from the docstring is kept as one line after the description; the
``strip_deprecation_notes`` flag removes it at render time.

Cap (decision D2): 350 tokens, counted with the pinned generator tokenizer. Trimming order when
over the cap:
1. the example (an example is chosen only if it fits; examples are executed, so they are never cut);
2. the description, word by word down to 12 words;
3. the signature's annotations (names and defaults kept);
4. the signature's parameter list, keeping version-exclusive and gold keywords, then ", ...".
Every trim applied is recorded on the chunk. Chunks are not padded to a floor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

CAP = 350
ROLE = re.compile(r":(?:py:)?(?:func|meth|class|attr|mod|obj|data|exc|ref|doc|const)?:`~?([^`]+)`")
DEPRECATED = re.compile(r"\.\.\s*deprecated::\s*([^\n]*)\n((?:[ \t]+[^\n]*\n?)*)", re.I)


def clean_rst(text: str) -> str:
    text = ROLE.sub(r"\1", text)
    text = re.sub(r"``([^`]+)``", r"`\1`", text)
    return " ".join(text.split())


def description_from_summary(summary: str) -> str:
    """First sentence of the summary region, without directives."""
    body = DEPRECATED.sub("", summary)
    paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip() and not p.lstrip().startswith((".. ", ">>>"))]
    if not paragraphs:
        return ""
    text = clean_rst(paragraphs[0])
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:300]


def deprecation_note(summary: str) -> str | None:
    m = DEPRECATED.search(summary + "\n")
    if not m:
        return None
    version = m.group(1).strip()
    detail = clean_rst(m.group(2)) if m.group(2) else ""
    return (f"Deprecated since {version}: {detail}" if version else f"Deprecated: {detail}").strip().rstrip(":")


@dataclass
class Parts:
    fqn: str
    library: str
    version: str
    kind: str
    title: str
    signature: str | None
    description: str
    deprecation_note: str | None = None
    example: str | None = None


def render(parts: Parts, show_version_tags: bool = True, strip_deprecation_notes: bool = False) -> str:
    lines = []
    if show_version_tags:
        lines.append(f"[{parts.library} {parts.version} | api] {parts.title}")
    lines.append(parts.fqn)
    if show_version_tags:
        lines.append(f"Version: {parts.library} {parts.version}")
    lines.append(f"Signature: {parts.title}{parts.signature}" if parts.signature else f"Kind: {parts.kind}")
    if parts.description:
        lines.append(parts.description)
    if parts.deprecation_note and not strip_deprecation_notes:
        lines.append(parts.deprecation_note)
    if parts.example:
        lines.append("Example:")
        lines.append(parts.example)
    return "\n".join(lines)


def compact_signature(params: list[dict], accepts_var_kwargs: bool, keep: set[str] | None = None, limit: int | None = None) -> str:
    """Names and defaults only. With ``limit``, keep the first ``limit`` parameters plus ``keep``."""
    shown = []
    for i, p in enumerate(params):
        if limit is not None and i >= limit and p["name"] not in (keep or set()):
            continue
        shown.append(p["name"] if p.get("default") is None else f"{p['name']}={p['default']}")
    truncated = limit is not None and len(shown) < len(params)
    items = shown + (["..."] if truncated else []) + (["**kwargs"] if accepts_var_kwargs else [])
    return "(" + ", ".join(items) + ")"


@dataclass
class Composed:
    parts: Parts
    text: str
    n_tokens: int
    trims: list[str] = field(default_factory=list)


def fit(parts: Parts, count: Callable[[str], int], params: list[dict], accepts_var_kwargs: bool,
        keep_params: set[str], cap: int = CAP) -> Composed:
    """Apply trims 2 to 4 until the chunk without an example fits the cap."""
    trims: list[str] = []
    text = render(parts)
    if count(text) <= cap:
        return Composed(parts, text, count(text), trims)
    words = parts.description.split()
    while count(render(parts)) > cap and len(words) > 12:
        words = words[: max(12, len(words) - 8)]
        parts.description = " ".join(words) + " ..."
        if "description" not in trims:
            trims.append("description")
    if count(render(parts)) > cap and parts.signature and params:
        parts.signature = compact_signature(params, accepts_var_kwargs)
        trims.append("signature_annotations")
    limit = len(params)
    while count(render(parts)) > cap and parts.signature and limit > 0:
        limit = max(0, limit - 4)
        parts.signature = compact_signature(params, accepts_var_kwargs, keep_params, limit)
        if "signature_params" not in trims:
            trims.append("signature_params")
    text = render(parts)
    return Composed(parts, text, count(text), trims)


def with_example(composed: Composed, example: str, count: Callable[[str], int], cap: int = CAP) -> Composed | None:
    """The chunk with ``example`` added, or None when the example does not fit (trim 1)."""
    parts = Parts(**{**composed.parts.__dict__, "example": example})
    text = render(parts)
    n = count(text)
    if n > cap:
        return None
    return Composed(parts, text, n, list(composed.trims))
