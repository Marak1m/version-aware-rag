"""``varag inventory audit``: check each diff against the published rule sets.

Any listed name missing from its expected bucket is an extraction bug. Recall is printed
per library; M2 does not pass below 95% for NumPy and pydantic. pandas has no
machine-readable set, so its recall is reported, not gated.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from varag.inventory.diff import bucket_of
from varag.inventory.rules import Rule, applies, load_rules
from varag.inventory.schema import diff_path

GATED = {"numpy": 0.95, "pydantic": 0.95}


@dataclass
class AuditResult:
    library: str
    applicable: int = 0
    hits: int = 0
    walk_hits: int = 0            # hits whose inventory entry the plain walk found (no rule-set seeding)
    misses: list[dict] = field(default_factory=list)
    skipped: int = 0
    deprecated_rule_only: list[str] = field(default_factory=list)
    seeded_hits: list[str] = field(default_factory=list)

    @property
    def recall(self) -> float:
        """Overall recall: the gate."""
        return self.hits / self.applicable if self.applicable else 1.0

    @property
    def walk_recall(self) -> float:
        """Recall counting only entries the walk found by itself. Printed, not gated."""
        return self.walk_hits / self.applicable if self.applicable else 1.0

    @property
    def gate(self) -> float | None:
        return GATED.get(self.library)

    @property
    def passed(self) -> bool:
        return self.gate is None or self.recall >= self.gate


def audit_library(library: str, diff: dict, rules: list[Rule] | None = None) -> AuditResult:
    result = AuditResult(library)
    for rule in rules if rules is not None else load_rules(library):
        if not applies(library, rule.symbol):
            result.skipped += 1
            continue
        result.applicable += 1
        actual = bucket_of(diff, rule.symbol)
        if actual in rule.expected:
            result.hits += 1
            if diff[actual][rule.symbol].get("found_by", "walk") == "walk":
                result.walk_hits += 1
            else:
                result.seeded_hits.append(rule.symbol)
            if actual == "deprecated_in_new":
                detected_by = diff["deprecated_in_new"][rule.symbol].get("deprecated_by", [])
                if not detected_by:
                    result.deprecated_rule_only.append(rule.symbol)
        else:
            result.misses.append({"symbol": rule.symbol, "expected": list(rule.expected), "actual": actual, "source": rule.source})
    return result


def audit_all(libraries: list[str]) -> dict[str, AuditResult]:
    out = {}
    for library in libraries:
        path = diff_path(library)
        if not path.exists():
            raise FileNotFoundError(f"{path} missing: run `varag inventory build`")
        out[library] = audit_library(library, json.loads(path.read_text(encoding="utf-8")))
    return out


def format_result(r: AuditResult) -> str:
    gate = f" (gate {r.gate:.0%})" if r.gate is not None else " (not gated)"
    lines = [
        f"{r.library}: recall {r.recall:.1%} = {r.hits}/{r.applicable} applicable rules, {r.skipped} outside inventory roots{gate}",
        f"  walk-only recall {r.walk_recall:.1%} = {r.walk_hits}/{r.applicable}; {len(r.seeded_hits)} hit(s) reached only through rule-set seeding"
        + (f": {', '.join(r.seeded_hits[:8])}" if r.seeded_hits else ""),
    ]
    for miss in r.misses:
        lines.append(f"  MISS {miss['symbol']}: expected {'/'.join(miss['expected'])}, found {miss['actual']}  [{miss['source']}]")
    if r.deprecated_rule_only:
        lines.append(f"  {len(r.deprecated_rule_only)} deprecated_in_new symbols come only from a rule set: {', '.join(r.deprecated_rule_only[:8])}")
    return "\n".join(lines)
