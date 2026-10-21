"""Execution oracles for the blend guard (handoff L3, "Guard accuracy against execution").

``exclusive_error`` (the M7 oracle, ``metrics.names_exclusive``): the pre-guard answer fails in the
target environment with an AttributeError, ImportError, ModuleNotFoundError or TypeError whose last
line names one of the code's exclusive symbols. It misses a rejected value (``freq="Q"`` raises a
ValueError; ``copy=False`` raises one that names nothing) and a strict deprecation failure
(``.dict()``, ``.schema()`` pass the tests and fail only through their warning).

``strict_named`` (2026-10-21, a metric correction made after the final sweep): the pre-guard answer
fails in the committed version under the strict score (a failing test, or a pass with a
solution-attributed soft warning net of the reference) and a usage (symbol, keyword or value)
appears in the evidence: the error text or traceback, a warning the strict score counts as an
error, or the failing line of the answer. The usages looked for:

- precision: a flagged answer counts when one of the guard's own flagged usages is evidenced;
- recall: the positives are the answers where a usage that conflicts with the committed version
  is evidenced: the static extractor's conflicting usages (what the guard checks) and the
  concept's gold symbols of the other version (what a wrong-version answer uses, also where the
  extractor abstains), except for behaviour concepts, whose gold is the same API on both sides,
  and a gold symbol the target version also uses. Recall is the share of positives the guard
  flagged.

The failing line is no evidence when the error is one the answer's own code raises (NameError,
UnboundLocalError, SyntaxError, IndentationError): a missing ``import pandas`` fails on the line
that holds ``freq="H"`` without implicating it.

A name matches in the error text, traceback or warnings only in a form that points at it
(``.name``, ``name(``, ``name=``, or quoted), not as a bare word in prose. On the failing line any
whole-word occurrence counts. A value matches
as ``param=value`` on the failing line, or, for a string value, quoted or as a whole word in the
error text or a warning (pandas: "Invalid frequency: Q").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from varag.config import other_side
from varag.pipeline.values import parse_gold

SOLUTION_LINE = re.compile(r"solution\.py:(\d+)")
# Errors the answer's own code raises, never the library: the failing line cannot implicate a usage.
OWN_ERRORS = ("NameError", "UnboundLocalError", "SyntaxError", "IndentationError")


@dataclass
class Evidence:
    failed: bool                       # strict failure in the committed version
    error: str = ""                    # the exception line(s)
    trace: str = ""                    # pytest's output tail
    warnings: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)   # the answer's lines the traceback passes through


def evidence(code: str | None, exec_record: dict | None, net_soft: list[str] | None) -> Evidence:
    rec = exec_record or {}
    tail = rec.get("output_tail") or ""
    soft = list(net_soft or [])
    failed = rec.get("status") not in ("pass", None) or bool(soft)
    if rec.get("status") in ("infra_error", "timeout"):
        failed = False
    errors = [rec.get("last_line") or ""] + [line[1:].strip() for line in tail.splitlines() if line.startswith("E ")]
    source = (code or "").splitlines()
    numbers = sorted({int(n) for n in SOLUTION_LINE.findall(tail)})
    lines = [source[n - 1] for n in numbers if 0 < n <= len(source)]
    if (rec.get("exc_type") or "") in OWN_ERRORS or (rec.get("last_line") or "").startswith(OWN_ERRORS):
        lines = []
    return Evidence(failed, "\n".join(e for e in errors if e), tail, soft, lines)


def _name_forms(name: str) -> re.Pattern:
    n = re.escape(name)
    return re.compile(rf"\.{n}\b|\b{n}\s*\(|\b{n}\s*=|['\"`]{n}['\"`]")


def _value_text(value) -> str:
    return value if isinstance(value, str) else repr(value)


def usage_evidenced(symbol: str, ev: Evidence) -> bool:
    ref = parse_gold(symbol)
    if ref.has_value:
        lit = _value_text(ref.value)
        quoted = rf"['\"]{re.escape(lit)}['\"]" if isinstance(ref.value, str) else re.escape(lit)
        on_line = re.compile(rf"\b{re.escape(ref.param)}\s*=\s*{quoted}")
        if any(on_line.search(line) for line in ev.lines):
            return True
        if isinstance(ref.value, str):
            word = re.compile(rf"['\"]{re.escape(lit)}['\"]|(?<![\w-]){re.escape(lit)}(?![\w-])")
            return bool(word.search(ev.error)) or any(word.search(w) for w in ev.warnings)
        return False
    name = ref.param or ref.owner.rsplit(".", 1)[-1]
    if not name:
        return False
    if any(re.search(rf"\b{re.escape(name)}\b", line) for line in ev.lines):
        return True
    forms = _name_forms(name)
    return bool(forms.search(ev.error) or forms.search(ev.trace) or any(forms.search(w) for w in ev.warnings))


def strict_named(ev: Evidence, symbols: list[str]) -> bool:
    return ev.failed and any(usage_evidenced(s, ev) for s in symbols)


def pre_guard_evidence(row: dict) -> tuple[str | None, Evidence]:
    """The pre-guard answer's code and its evidence in the committed (target) version."""
    before = row.get("pre_guard") or {}
    code = before.get("code") or row.get("code")
    side = row["target"]
    exec_record = (before.get("exec") or row.get("exec") or {}).get(side)
    net = (before.get("net_soft_warnings") or row.get("net_soft_warnings") or {}).get(side)
    return code, evidence(code, exec_record, net)


def conflicting_usages(code: str | None, library: str, target: str) -> list[str]:
    """The static extractor's usages outside version guards that the committed version rejects."""
    from varag.inventory.build import load_diff
    from varag.pipeline.signals import static_usages

    if not code:
        return []
    usages = static_usages(code, load_diff(library))
    if not usages.parsed:
        return []
    other = other_side(target)
    return [u.symbol for u in usages.usages if not u.guarded and (u.side == other or (target == "new" and u.side == "deprecated_in_new"))]
