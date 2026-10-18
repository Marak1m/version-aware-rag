"""Value-level rules in the pipeline (user decisions 2026-10-18).

- Gold references may name a value: ``pandas.date_range(freq="M")``. ``parse_gold`` reads the
  owner, the parameter and the literal.
- ``value_index`` holds the confirmed records of data/rules/<library>/value_rules.json keyed by
  (callable, parameter); ``match_value`` finds the record for a literal, including the anchored
  forms of an alias (``Q-JUN`` matches the ``Q`` rule).
- ``rejected_values`` reads an error message that names a value the installed version rejects
  ("Invalid frequency: ME"): the installed version lacks that value, so the message supports the
  side whose rules do not list it.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from functools import lru_cache

from varag.inventory.rules import value_rules

GOLD = re.compile(r"^(?P<owner>[\w.]+)\((?P<param>\w+)(?:=(?P<value>.+))?\)$", re.S)
POSITIONAL_KINDS = ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")

# Error messages that quote the rejected argument value. The value is matched against every
# confirmed rule of the library, whatever the callable.
REJECTED_VALUE = [
    re.compile(r"[Ii]nvalid frequency:?\s*['\"]?(?P<value>[A-Za-z][\w\-]*)"),
    re.compile(r"invalid unit abbreviation:?\s*['\"]?(?P<value>\w+)"),
    re.compile(r"[Ii]nvalid (?:error|errors) value specified(?:[^'\"\n]*['\"](?P<value>[^'\"]+)['\"])?"),
    re.compile(r"[Uu]nsupported (?:value|alias|unit|resolution)[^'\"\n]*['\"](?P<value>[^'\"]+)['\"]"),
]


@dataclass(frozen=True)
class GoldRef:
    owner: str
    param: str | None = None
    value: object = None
    has_value: bool = False

    @property
    def keyword_symbol(self) -> str | None:
        return f"{self.owner}({self.param})" if self.param else None

    @property
    def symbol(self) -> str:
        """The inventory symbol: the owner for a symbol gold, ``owner(param)`` otherwise."""
        return self.keyword_symbol or self.owner


def parse_gold(text: str) -> GoldRef:
    m = GOLD.match(text.strip())
    if not m:
        return GoldRef(text.strip())
    if m.group("value") is None:
        return GoldRef(m.group("owner"), m.group("param"))
    try:
        value = ast.literal_eval(m.group("value"))
    except (ValueError, SyntaxError):
        value = m.group("value").strip()
    return GoldRef(m.group("owner"), m.group("param"), value, True)


def value_symbol(callable_: str, parameter: str, value: object) -> str:
    return f"{callable_}({parameter}={value!r})"


@lru_cache(maxsize=8)
def value_index(library: str) -> dict[tuple[str, str], tuple[dict, ...]]:
    """(callable, parameter) -> confirmed value rules."""
    index: dict[tuple[str, str], list[dict]] = {}
    for rule in value_rules(library):
        index.setdefault((rule["callable"], rule["parameter"]), []).append(rule)
    return {k: tuple(v) for k, v in index.items()}


def match_value(index: dict, callable_: str, parameter: str, value: object) -> dict | None:
    rules = index.get((callable_, parameter), ())
    for rule in rules:
        if rule["value"] == value and type(rule["value"]) is type(value):
            return rule
    if isinstance(value, str):
        for rule in rules:
            if rule.get("anchored") and isinstance(rule["value"], str) and value.startswith(rule["value"] + "-"):
                return rule
    return None


def sides_of_value(index: dict, value: object) -> set[str]:
    """Every side whose confirmed rules list this literal, on any callable."""
    sides: set[str] = set()
    for rules in index.values():
        for rule in rules:
            if rule["value"] == value and type(rule["value"]) is type(value):
                sides.add(rule["side"])
            elif isinstance(value, str) and rule.get("anchored") and isinstance(rule["value"], str) and value.startswith(rule["value"] + "-"):
                sides.add(rule["side"])
    return sides


def rejected_values(index: dict, text: str) -> list[tuple[str, str, str]]:
    """(value, side supported, message) for each rejected value an error message names. The
    installed version lacks the value, so the evidence goes to the other side."""
    out: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for pattern in REJECTED_VALUE:
        for m in pattern.finditer(text):
            value = m.group("value")
            if not value or value in seen:
                continue
            sides = sides_of_value(index, value)
            if len(sides) != 1:
                continue
            seen.add(value)
            lacking = sides.pop()
            out.append((value, "new" if lacking == "old" else "old", m.group(0).strip()))
    return out
