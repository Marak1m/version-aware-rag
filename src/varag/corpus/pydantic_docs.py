"""pydantic docs markdown at the release tag, split by heading (handoff: pydantic v1 docstrings are thin).

Sources (docs/plans/M4.md):
- 1.10.13: docs/usage/*.md, whose `{!.tmp_examples/NAME.md!}` include directives resolve to
  docs/examples/NAME.py at the same commit.
- 2.13.4: docs/concepts/*.md and docs/errors/*.md. docs/migration.md is migration material (D4)
  and the docs/api pages are mkdocstrings stubs; neither is used.

Files are fetched once at the tag's commit SHA and stored under data/corpus/pydantic/docs/<version>/
with a manifest of tag, commit, path and sha256 (verification check 6). Later builds read the
stored files and re-check their sha256.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Callable

import yaml

from varag.config import project_root
from varag.corpus.examples import fenced_blocks

REPO = "pydantic/pydantic"
HEADING = re.compile(r"^(#{1,4})\s+(.*?)\s*(?:\{[^}]*\})?\s*$")
INCLUDE = re.compile(r"\{!\.tmp_examples/([\w\-]+)\.md!\}")


def source_selector(version: str) -> Callable[[str], bool]:
    if version.startswith("1."):
        return lambda p: (p.startswith("docs/usage/") and p.endswith(".md")) or (p.startswith("docs/examples/") and p.endswith(".py"))
    return lambda p: p.endswith(".md") and (p.startswith("docs/concepts/") or p.startswith("docs/errors/"))


def docs_dir(version: str) -> Path:
    return project_root() / "data" / "corpus" / "pydantic" / "docs" / version


def _get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "varag"}), timeout=60).read()


def fetch_docs(version: str, log: Callable[[str], None] = print) -> dict:
    """Fetch (or verify the stored copy of) the docs files for one version. Returns the manifest."""
    directory = docs_dir(version)
    manifest_path = directory / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for path, sha in manifest["files"].items():
            if hashlib.sha256((directory / path).read_bytes()).hexdigest() != sha:
                raise RuntimeError(f"{directory / path} changed since it was fetched; delete {manifest_path} to re-fetch")
        return manifest
    tag = f"v{version}"
    ref = json.loads(_get(f"https://api.github.com/repos/{REPO}/git/ref/tags/{tag}"))
    commit = ref["object"]["sha"]
    if ref["object"]["type"] == "tag":
        commit = json.loads(_get(ref["object"]["url"]))["object"]["sha"]
    tree = json.loads(_get(f"https://api.github.com/repos/{REPO}/git/trees/{commit}?recursive=1"))
    wanted = sorted(t["path"] for t in tree["tree"] if t["type"] == "blob" and source_selector(version)(t["path"]))
    files = {}
    for path in wanted:
        data = _get(f"https://raw.githubusercontent.com/{REPO}/{commit}/{path}")
        target = directory / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files[path] = hashlib.sha256(data).hexdigest()
    manifest = {"repo": REPO, "tag": tag, "commit": commit, "files": files,
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log(f"[pydantic {version}] fetched {len(files)} docs files at {tag} ({commit[:12]})")
    return manifest


@dataclass
class Section:
    path: str
    heading: str
    body: str
    file_sha256: str
    blocks: list[str] = field(default_factory=list)

    @property
    def ref(self) -> str:
        return f"{self.path}#{self.heading}"


def resolve_includes(markdown: str, directory: Path) -> str:
    def replace(m: re.Match) -> str:
        source = directory / "docs" / "examples" / f"{m.group(1)}.py"
        if not source.exists():
            return ""
        return "```py\n" + source.read_text(encoding="utf-8").rstrip() + "\n```"

    return INCLUDE.sub(replace, markdown)


def split_sections(path: str, markdown: str, file_sha256: str) -> list[Section]:
    sections: list[Section] = []
    heading, lines, in_fence = "(top)", [], False
    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else HEADING.match(line)
        if m:
            if "".join(lines).strip():
                sections.append(Section(path, heading, "\n".join(lines), file_sha256))
            heading, lines = m.group(2).strip(), []
        else:
            lines.append(line)
    if "".join(lines).strip():
        sections.append(Section(path, heading, "\n".join(lines), file_sha256))
    for s in sections:
        s.blocks = fenced_blocks(s.body)
    return sections


def load_sections(version: str, log: Callable[[str], None] = print) -> tuple[dict, list[Section]]:
    manifest = fetch_docs(version, log)
    directory = docs_dir(version)
    sections: list[Section] = []
    for path, sha in sorted(manifest["files"].items()):
        if not path.endswith(".md"):
            continue
        text = (directory / path).read_text(encoding="utf-8")
        if version.startswith("1."):
            text = resolve_includes(text, directory)
        sections += split_sections(path, text, sha)
    return manifest, sections


def mention_pattern(name: str) -> re.Pattern:
    """A backticked mention: `name`, `name()`, `x.name(...)`, `Owner.name`."""
    return re.compile(r"`(?:[\w.]+\.)?" + re.escape(name) + r"(?:\([^`]*\))?`")


def first_sentence(markdown: str) -> str:
    prose = []
    in_fence = False
    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        indented = line.startswith(("    ", "\t"))     # admonition bodies and indented code
        if in_fence or indented or not line.strip() or line.lstrip().startswith(("!!!", "???", "|", "{!", "<", "*", "-", "#", ">")):
            if prose:
                break
            continue
        prose.append(line.strip())
    text = " ".join(prose)
    text = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:300]


@lru_cache(maxsize=1)
def seed_map() -> dict:
    path = project_root() / "data" / "corpus" / "pydantic" / "seed_map.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def section_for(symbol: str, version: str, sections: list[Section]) -> Section | None:
    """Hand map first (seed gold symbols), then a heading that names the symbol, then the first
    section whose body mentions it in backticks."""
    hand = (seed_map().get(symbol) or {}).get(version.split(".")[0] + ".x")
    if hand:
        for s in sections:
            if s.path == hand["path"] and s.heading == hand["heading"]:
                return s
    name = symbol.rsplit(".", 1)[-1]
    pattern = mention_pattern(name)
    for s in sections:
        if pattern.search(s.heading):
            return s
    for s in sections:
        if pattern.search(s.body):
            return s
    return None
