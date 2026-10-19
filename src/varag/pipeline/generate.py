"""The shared output protocol (handoff, "Interaction protocol").

One system prompt for every method. The model replies with a single fenced Python block
that defines the entry point, or a single line starting ``QUESTION:``. Methods that answer
for both versions return two fenced blocks, each opening with
``# --- for {library} {version} ---``.

Extraction: the last fenced Python block; if none, the whole message when it parses;
otherwise ``no_code``. Labelled two-block answers are split by label. Several unlabelled
blocks score on the last one and are counted in ``multi_block_rate``.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field

SYSTEM_PROMPT = (
    "You are a Python coding assistant.\n"
    "Reply in exactly one of two ways.\n"
    "1. A single fenced Python code block (```python ... ```) that defines the function named in the task, "
    "including every import it needs. Write no prose outside the block.\n"
    "2. If you need information from the user before you can answer, reply with a single line that starts "
    "with `QUESTION:` followed by your question, and nothing else.\n"
)

# Prompt-review fixes (user, 2026-10-19; docs/DECISIONS.md). Every task prompt ends with a
# HumanEval-style signature stub: the def line exactly as the query states the signature, then
# "...". Generation calls where the policy decides, or that never ask, end with NO_QUESTION; where
# the model decides, NO_QUESTION follows every simulated-user reply.
NO_QUESTION = "Write the code now. Do not ask a question."
SIGNATURE = r"`({name}\([^`]*\))`"


def signature_stub(query: str, entry_point: str) -> str:
    m = re.search(SIGNATURE.format(name=re.escape(entry_point)), query)
    if not m:
        raise ValueError(f"the query does not state the signature of {entry_point!r} in backticks")
    return f"Complete this function:\n```python\ndef {m.group(1)}:\n    ...\n```"


def finish_prompt(content: str, query: str, entry_point: str, no_question: bool) -> str:
    """The end of every task prompt: the signature stub, then NO_QUESTION where it applies."""
    out = content.rstrip("\n") + "\n\n" + signature_stub(query, entry_point) + "\n"
    return out + ("\n" + NO_QUESTION + "\n" if no_question else "")


def after_reply(reply: str) -> str:
    """A simulated-user reply as the harness sends it: the reply, then NO_QUESTION."""
    return f"{reply}\n\n{NO_QUESTION}"


def defines_entry_point(code: str, entry_point: str) -> bool | None:
    """True when module-level code defines or imports ``entry_point``; None when the code does not parse."""
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError):
        return None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == entry_point:
            return True
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == entry_point for t in targets):
                return True
        if isinstance(node, (ast.Import, ast.ImportFrom)) and any((a.asname or a.name.split(".")[0]) == entry_point for a in node.names):
            return True
    return False


FENCE = re.compile(r"```[ \t]*(?:python|py)?[ \t]*\r?\n(.*?)```", re.S)
LABEL = re.compile(r"^\s*#\s*---\s*for\s+(?P<library>[\w.-]+)\s+(?P<version>[\w.*+-]+)\s*---\s*$", re.M)
QUESTION = re.compile(r"^\s*QUESTION:\s*(?P<q>.*)$", re.S)


def version_label(library: str, version: str) -> str:
    return f"# --- for {library} {version} ---"


def parses(code: str) -> bool:
    try:
        ast.parse(code)
    except (SyntaxError, ValueError, RecursionError):
        return False
    return True


@dataclass
class Extraction:
    kind: str                      # code | question | no_code
    code: str | None = None
    question: str | None = None
    blocks: int = 0
    multi_block: bool = False
    labelled: dict[str, str] = field(default_factory=dict)   # version -> code

    @property
    def answers_returned(self) -> int:
        return len(self.labelled) if self.labelled else (1 if self.code else 0)


def extract_code(text: str) -> Extraction:
    stripped = text.strip()
    q = QUESTION.match(stripped)
    if q and "```" not in stripped:
        return Extraction(kind="question", question=q.group("q").strip().splitlines()[0] if q.group("q").strip() else "")

    blocks = [b.strip("\r\n") for b in FENCE.findall(text)]
    if not blocks:
        if stripped and parses(stripped):
            return Extraction(kind="code", code=stripped, blocks=0)
        return Extraction(kind="no_code", blocks=0)

    labelled: dict[str, str] = {}
    for block in blocks:
        first = block.lstrip().splitlines()[0] if block.strip() else ""
        m = LABEL.match(first)
        if m:
            labelled[m.group("version")] = block
    if len(blocks) >= 2 and len(labelled) == len(blocks):
        return Extraction(kind="code", code=blocks[-1], blocks=len(blocks), multi_block=False, labelled=labelled)
    return Extraction(kind="code", code=blocks[-1], blocks=len(blocks), multi_block=len(blocks) > 1)


def pick_labelled(extraction: Extraction, version: str) -> str | None:
    """The block labelled with ``version`` (exact, then major-version prefix match)."""
    if version in extraction.labelled:
        return extraction.labelled[version]
    major = version.split(".")[0]
    for label, code in extraction.labelled.items():
        if label.split(".")[0] == major:
            return code
    return None
