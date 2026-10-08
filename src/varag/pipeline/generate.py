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
