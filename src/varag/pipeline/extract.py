"""The full signal extractor (handoff, "Signals"): every signal in the query and context with
its source span, symbol, side and weight.

| Signal | Side | Weight |
| version named in text | named | decisive |
| requirement pin satisfied by exactly one side | that side | decisive |
| migration message (configs/migration_messages.yaml) | emitting side | decisive |
| error names a missing symbol, keyword or module | the side that lacks it | 4 |
| error names a value a confirmed value rule rejects | the side that lacks it | 4 |
| exclusive import | having side | 4 |
| exclusive symbol, keyword, value or config key on a resolved receiver | having side | 3 |
| the same on a heuristic receiver, or a non-generic method on an unresolved one | having side | 1.5 |
| deprecated-in-new usage on a resolved receiver | old, weakly | 1 |
| generic name, shared_unknown callee, unconfirmed keyword or value, guarded usage | neither | 0 |

Rules: a symbol named in an error is removed from the code signals; each distinct symbol counts
once; a pin both sides satisfy is no signal; usage inside a version guard counts for neither
side; parsing order is fenced blocks, ``ast.parse``, dedent, line salvage, then a regex fallback
at half weight.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from varag.config import load_libraries, load_migration_messages
from varag.inventory.build import load_diff
from varag.inventory.diff import bucket_of
from varag.pipeline.signals import SIDE_OF_BUCKET, Usage, parse_code, static_usages
from varag.pipeline.values import rejected_values, value_index

DECISIVE = "decisive"
WEIGHTS = {"import": 4.0, "symbol": 3.0, "keyword": 3.0, "value": 3.0, "config_key": 3.0, "method": 1.5}
HEURISTIC_WEIGHT = 1.5
DEPRECATED_WEIGHT = 1.0
ERROR_WEIGHT = 4.0

FENCE = re.compile(r"```[ \t]*(?:python|py)?[ \t]*\r?\n(.*?)```", re.S)
PYPROJECT_LINE = re.compile(r"^\s*(?P<name>[A-Za-z][\w.-]*)\s*=\s*(?:\{[^}]*version\s*=\s*)?[\"'](?P<spec>[^\"']+)[\"']", re.I)
CONDA_LINE = re.compile(r"^\s*-\s*(?P<name>[A-Za-z][\w.-]*)\s*(?P<spec>(?:==|>=|<=|~=|!=|=|<|>)\s*[\w.*,<>=!~ ]+)?\s*$")
MENTION = re.compile(
    r"(?i)\b(?P<lib>pandas|numpy|pydantic)\b\s*(?:version\s*)?(?:==|>=|<=|~=|<|>)?\s*v?(?P<ver>\d+(?:\.\d+)*)"
    r"|\bversion\s*(?P<ver2>\d+(?:\.\d+)*)\b"
    r"|\b[vV](?P<ver3>\d+(?:\.\d+)*)\b"
    r"|\b(?P<ver4>\d+\.\d+\.\d+)\b"
)
ERROR_PATTERNS = [
    ("module", re.compile(r"module '(?P<module>[\w.]+)' has no attribute '(?P<name>\w+)'")),
    ("object", re.compile(r"(?:type object|'(?P<type>\w+)' object) '?(?P<type2>\w+)?'? ?has no attribute '(?P<name>\w+)'")),
    ("import", re.compile(r"cannot import name '(?P<name>\w+)' from '(?P<module>[\w.]+)'")),
    ("keyword", re.compile(r"got an unexpected keyword argument '(?P<name>\w+)'")),
    ("nomodule", re.compile(r"No module named '(?P<module>[\w.]+)'")),
]
REGEX_FALLBACK = re.compile(r"\b(?P<alias>np|numpy|pd|pandas|pydantic)\.(?P<path>[A-Za-z_][\w.]*)")
ALIASES = {"np": "numpy", "pd": "pandas", "numpy": "numpy", "pandas": "pandas", "pydantic": "pydantic"}
TRACEBACK = "Traceback (most recent call last)"


@dataclass(frozen=True)
class Signal:
    source: str          # query | context | error
    kind: str            # version | pin | message | error_symbol | error_value | import | symbol | keyword | value | config_key | method | deprecated
    symbol: str
    side: str            # old | new
    weight: float        # 0 for decisive signals; see decisive
    decisive: bool = False
    line: int = 0
    col: int = 0
    detail: str = ""


@dataclass
class Signals:
    library: str
    signals: list[Signal] = field(default_factory=list)
    abstained: list[dict] = field(default_factory=list)
    code_parse: str = "none"         # ast | dedent | salvage | regex | none
    error_symbols: set[str] = field(default_factory=set)

    def S(self, side: str) -> float:
        return sum(s.weight for s in self.signals if s.side == side and not s.decisive)

    def D(self, side: str) -> bool:
        return any(s.decisive for s in self.signals if s.side == side)

    def symbols(self, side: str) -> set[str]:
        return {s.symbol for s in self.signals if s.side == side}

    def to_dict(self) -> dict:
        return {"library": self.library, "code_parse": self.code_parse,
                "S": {"old": self.S("old"), "new": self.S("new")}, "D": {"old": self.D("old"), "new": self.D("new")},
                "signals": [s.__dict__ for s in self.signals], "abstained": self.abstained}


def library_versions_for(library: str, versions: dict[str, str] | None = None) -> dict[str, str]:
    """Exact versions per side: from the environment manifest when built, else configs/libraries.yaml."""
    if versions:
        return versions
    try:
        from varag.eval.run import library_versions

        return library_versions()[library]
    except (FileNotFoundError, KeyError):
        spec = load_libraries()["libraries"][library]
        return {side: str(spec[side]["version"]).replace("*", "0") for side in ("old", "new")}


def side_of_major(major: int, versions: dict[str, str]) -> str | None:
    majors = {side: int(v.split(".")[0]) for side, v in versions.items()}
    hits = [side for side, m in majors.items() if m == major]
    return hits[0] if len(hits) == 1 else None


# --- text signals ---------------------------------------------------------------------------


def pin_signals(text: str, library: str, versions: dict[str, str], source: str) -> tuple[list[Signal], list[dict], set[int]]:
    """Requirement, pyproject, conda and pip-freeze lines naming the library. Returns the signals,
    abstentions, and the indexes of lines that were pins (so they are not re-read as mentions)."""
    signals, abstained, pin_lines = [], [], set()
    for index, raw in enumerate(text.splitlines()):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        name, spec = None, None
        m = CONDA_LINE.match(line) or PYPROJECT_LINE.match(line)
        if m:
            name, spec = m.group("name"), (m.group("spec") or "").strip()
            if m.re is CONDA_LINE and spec.startswith("=") and not spec.startswith("=="):
                version = spec[1:].strip()             # conda `name=1.26` means any 1.26.x
                spec = f"=={version}.*" if version.count(".") < 2 and "*" not in version else f"=={version}"
        else:
            try:
                req = Requirement(line)
                name, spec = req.name, str(req.specifier)
            except InvalidRequirement:
                continue
        if name is None or name.lower().replace("_", "-") != library:
            continue
        pin_lines.add(index)
        if not spec:
            abstained.append({"name": line, "line": index + 1, "reason": "pin names the library without a version"})
            continue
        try:
            specifier = SpecifierSet(spec)
            satisfied = {side: specifier.contains(Version(versions[side]), prereleases=True) for side in ("old", "new")}
        except (InvalidSpecifier, InvalidVersion):
            abstained.append({"name": line, "line": index + 1, "reason": "unparsable pin"})
            continue
        sides = [side for side, ok in satisfied.items() if ok]
        if len(sides) == 1:
            signals.append(Signal(source, "pin", f"{library}{spec}", sides[0], 0.0, decisive=True, line=index + 1, detail=line))
        else:
            abstained.append({"name": line, "line": index + 1, "reason": "pin satisfied by both sides" if sides else "pin satisfied by neither side"})
    return signals, abstained, pin_lines


def mention_signals(text: str, library: str, versions: dict[str, str], source: str, skip_lines: set[int]) -> list[Signal]:
    signals = []
    for index, line in enumerate(text.splitlines()):
        if index in skip_lines:
            continue
        for m in MENTION.finditer(line):
            lib = (m.group("lib") or "").lower()
            if lib and lib != library:
                continue
            version = m.group("ver") or m.group("ver2") or m.group("ver3") or m.group("ver4")
            if not version:
                continue
            side = side_of_major(int(version.split(".")[0]), versions)
            if side:
                signals.append(Signal(source, "version", f"{library} {version}", side, 0.0, decisive=True, line=index + 1, col=m.start(), detail=m.group(0)))
    return signals


def message_signals(text: str, library: str, source: str) -> list[Signal]:
    signals = []
    for entry in load_migration_messages().get(library) or []:
        pattern, regex = entry.get("pattern"), entry.get("regex")
        hit = None
        if pattern and pattern in text:
            hit = pattern
        elif regex and re.search(regex, text):
            hit = regex
        if hit:
            signals.append(Signal(source, "message", f"message:{entry.get('kind', hit)}", entry["side"], 0.0, decisive=True, detail=hit))
    return signals


# --- error signals ------------------------------------------------------------------------------


def _lacking_side(diff: dict, symbol: str) -> str | None:
    """The side that lacks ``symbol``: an error naming it was raised on that side."""
    bucket = bucket_of(diff, symbol)
    return {"old_only": "new", "new_only": "old"}.get(bucket or "")


def _candidates_ending(diff: dict, suffix: str) -> list[str]:
    return sorted(s for b in ("old_only", "new_only") for s in diff[b] if s.endswith(suffix) and "(" not in s)


def error_signals(text: str, library: str, diff: dict, values: dict) -> tuple[list[Signal], list[dict], set[str]]:
    """Symbols, keywords, modules and values an error message names. Direction comes from the
    inventory or the value rules, never from the exception type."""
    signals, abstained, named = [], [], set()
    snippet = text.split(TRACEBACK, 1)[0]
    for kind, pattern in ERROR_PATTERNS:
        for m in pattern.finditer(text):
            if kind == "module":
                symbol = f"{m.group('module')}.{m.group('name')}"
                candidates = [symbol] if bucket_of(diff, symbol) else _candidates_ending(diff, f".{m.group('name')}")
            elif kind == "object":
                type_name = m.group("type") or m.group("type2") or ""
                candidates = _candidates_ending(diff, f".{type_name}.{m.group('name')}") or _candidates_ending(diff, f".{m.group('name')}")
            elif kind == "import":
                symbol = f"{m.group('module')}.{m.group('name')}"
                candidates = [symbol] if bucket_of(diff, symbol) else _candidates_ending(diff, f".{m.group('name')}")
            elif kind == "nomodule":
                candidates = [m.group("module")] if bucket_of(diff, m.group("module")) else []
            else:   # keyword: every exclusive parameter with that name, narrowed to callables the snippet names
                params = sorted(s for b in ("old_only", "new_only") for s in diff[b] if s.endswith(f"({m.group('name')})"))
                narrowed = [p for p in params if re.search(r"\b" + re.escape(p.split("(")[0].rsplit(".", 1)[-1]) + r"\s*\(", snippet)]
                candidates = narrowed or params
            if not candidates:
                continue
            sides = {_lacking_side(diff, c) for c in candidates}
            sides.discard(None)
            if len(sides) != 1:
                abstained.append({"name": m.group(0), "reason": "error names a symbol whose candidates disagree or sit in a shared bucket", "candidates": candidates[:6]})
                continue
            named.update(candidates)
            signals.append(Signal("error", "error_symbol", candidates[0] if len(candidates) == 1 else f"*{m.group('name')}", sides.pop(), ERROR_WEIGHT, detail=m.group(0)))
    named_values: set[str] = set()
    for value, side, message in rejected_values(values, text):
        named_values.add(value)
        signals.append(Signal("error", "error_value", f"value:{value!r}", side, ERROR_WEIGHT, detail=message))
    return signals, abstained, named, named_values


# --- code signals -------------------------------------------------------------------------------


def code_blocks(text: str) -> tuple[list[str], str]:
    """Fenced blocks when present, else the whole text as one block."""
    blocks = [m.group(1) for m in FENCE.finditer(text)]
    return (blocks, "fenced") if blocks else ([text], "whole")


def salvage_lines(code: str) -> tuple[str, str]:
    """Line-by-line salvage: (the lines that compile on their own, the lines that do not). The
    first set is parsed; the second goes to the regex fallback."""
    kept, dropped = [], []
    for line in code.splitlines():
        try:
            compile(line.strip() + "\n", "<salvage>", "exec")
            kept.append(line.strip())
        except SyntaxError:
            dropped.append(line)
    return "\n".join(kept), "\n".join(dropped)


def weight_of(usage: Usage) -> tuple[str, float]:
    """(side, weight) for a static usage; guarded usages weigh 0."""
    if usage.guarded:
        return usage.side if usage.side != "deprecated_in_new" else "old", 0.0
    if usage.side == "deprecated_in_new":
        return "old", DEPRECATED_WEIGHT
    if usage.resolution in ("heuristic", "name_index"):
        return usage.side, HEURISTIC_WEIGHT
    return usage.side, WEIGHTS.get(usage.kind, 3.0)


def regex_fallback(code: str, library: str, diff: dict) -> list[Signal]:
    """Dotted library paths and pydantic imports found by regex, at half weight."""
    signals, seen = [], set()
    for m in REGEX_FALLBACK.finditer(code):
        if ALIASES[m.group("alias")] != library:
            continue
        path = m.group("path").split("(")[0]
        parts = path.split(".")
        for i in range(len(parts), 0, -1):
            symbol = f"{library}." + ".".join(parts[:i])
            side = SIDE_OF_BUCKET.get(bucket_of(diff, symbol) or "")
            if side and symbol not in seen:
                seen.add(symbol)
                weight = DEPRECATED_WEIGHT / 2 if side == "deprecated_in_new" else WEIGHTS["symbol"] / 2
                signals.append(Signal("context", "symbol", symbol, "old" if side == "deprecated_in_new" else side, weight, detail="regex fallback"))
                break
    for m in re.finditer(r"from\s+pydantic\s+import\s+([\w, ]+)", code):
        for name in (n.strip() for n in m.group(1).split(",")):
            symbol = f"pydantic.{name}"
            side = SIDE_OF_BUCKET.get(bucket_of(diff, symbol) or "")
            if side and library == "pydantic" and symbol not in seen:
                seen.add(symbol)
                signals.append(Signal("context", "import", symbol, "old" if side == "deprecated_in_new" else side, WEIGHTS["import"] / 2, detail="regex fallback"))
    return signals


def code_signals(text: str, library: str, diff: dict, values: dict, error_symbols: set[str],
                 error_values: set[str] = frozenset()) -> tuple[list[Signal], list[dict], str]:
    blocks, how = code_blocks(text)
    candidates: list[Signal] = []
    abstained: list[dict] = []
    parse = "none"
    rejected_suffixes = tuple(f"={v!r})" for v in error_values)
    for block in blocks:
        code = block.split(TRACEBACK, 1)[0] if how == "whole" else block
        usages = static_usages(code, diff, values)
        this_parse = "ast"
        if not usages.parsed:
            salvaged, dropped = salvage_lines(code)
            usages = static_usages(salvaged, diff, values) if salvaged.strip() else usages
            this_parse = "salvage"
            candidates += [s for s in regex_fallback(dropped, library, diff) if s.symbol not in error_symbols]
        if not usages.parsed:
            candidates += [s for s in regex_fallback(code, library, diff) if s.symbol not in error_symbols]
            parse = "regex"
            continue
        parse = this_parse if parse in ("none", "ast") else parse
        abstained += usages.abstained
        for u in usages.usages:
            named = u.symbol in error_symbols or u.symbol.split("(")[0] in error_symbols
            if named or (u.kind == "value" and u.symbol.endswith(rejected_suffixes)):
                abstained.append({"name": u.symbol, "line": u.line, "reason": "named in the error: the code is what failed"})
                continue
            side, weight = weight_of(u)
            kind = "deprecated" if u.side == "deprecated_in_new" else u.kind
            detail = f"{u.resolution}" + (", guarded" if u.guarded else "") + (", uncertain" if u.uncertain else "") + (", corroborated" if u.corroborated else "")
            candidates.append(Signal("context", kind, u.symbol, side, weight, line=u.line, col=u.col, detail=detail))
    # Each distinct symbol counts once, however often it appears: keep its heaviest signal
    # (an imported and then called symbol is one signal at the import weight).
    best: dict[str, Signal] = {}
    for s in candidates:
        if s.symbol not in best or s.weight > best[s.symbol].weight:
            best[s.symbol] = s
    return list(best.values()), abstained, parse


# --- entry point --------------------------------------------------------------------------------


def extract_signals(query: str, context: str, library: str, diff: dict | None = None,
                    versions: dict[str, str] | None = None, values: dict | None = None) -> Signals:
    diff = diff or load_diff(library)
    values = value_index(library) if values is None else values
    versions = library_versions_for(library, versions)
    out = Signals(library)
    for source, text in (("query", query or ""), ("context", context or "")):
        if not text.strip():
            continue
        pins, abstained, pin_lines = pin_signals(text, library, versions, source)
        out.signals += pins
        out.abstained += abstained
        out.signals += mention_signals(text, library, versions, source, pin_lines)
        out.signals += message_signals(text, library, source)
    errors, abstained, named, named_values = error_signals(context or "", library, diff, values)
    out.signals += errors
    out.abstained += abstained
    out.error_symbols = named | {f"value:{v!r}" for v in named_values}
    if (context or "").strip():
        code, abstained, parse = code_signals(context, library, diff, values, named, named_values)
        out.signals += code
        out.abstained += abstained
        out.code_parse = parse
    return out
