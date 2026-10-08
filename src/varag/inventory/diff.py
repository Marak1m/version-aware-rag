"""The old/new diff per library: the single source of truth for which symbols belong to
which version. Version inference, the blend guard and task mining all read it.

Buckets (handoff, "API inventory and diff"):
  old_only, new_only          present on one side
  deprecated_in_new           present on both, deprecated on the new side only (or rule-listed)
  shared_changed              same symbol, different parameters or defaults
  shared_unknown              signature not introspectable on at least one side
  shared_same                 everything else; also the allowlist for portable answers
  method_name_index           bare method name -> owners per side, with a generic flag
"""

from __future__ import annotations

from datetime import datetime, timezone

BUCKETS = ("old_only", "new_only", "deprecated_in_new", "shared_changed", "shared_unknown", "shared_same")
SIGNATURE_KINDS = ("function", "method", "class")


def _summary(entry: dict) -> dict:
    out = {"kind": entry["kind"], "owner": entry["owner"], "name": entry["name"], "found_by": entry.get("found_by", "walk")}
    if entry["kind"] == "param":
        out["default"] = entry.get("default")
    elif entry["kind"] in SIGNATURE_KINDS:
        out["signature"] = entry.get("signature")
        out["params"] = entry.get("params", [])
        out["signature_known"] = entry.get("signature_known", False)
        out["accepts_var_kwargs"] = entry.get("accepts_var_kwargs", False)
    if entry.get("deprecated"):
        out["deprecated_by"] = entry.get("deprecated_by", [])
    return out


def _bucket(old: dict, new: dict, rule_deprecated: set[str]) -> str:
    symbol = old["symbol"]
    if symbol in rule_deprecated or (new.get("deprecated") and not old.get("deprecated")):
        return "deprecated_in_new"
    kind = old["kind"]
    if kind == "param":
        return "shared_changed" if old.get("default") != new.get("default") else "shared_same"
    if kind in SIGNATURE_KINDS:
        if not (old.get("signature_known") and new.get("signature_known")):
            return "shared_unknown"
        if old.get("params") != new.get("params") or old.get("signature") != new.get("signature"):
            return "shared_changed"
    return "shared_same"


def _absorbed_keyword(entry: dict, new: dict[str, dict], rule_kept_keywords: set[str]) -> bool:
    """A keyword declared only on the old side, which the new side's callee still accepts
    through **kwargs with a deprecation warning (a rule set says so): deprecated_in_new."""
    if entry["kind"] != "param" or entry["symbol"] not in rule_kept_keywords:
        return False
    owner = new.get(entry["owner"])
    return bool(owner and owner.get("accepts_var_kwargs"))


def build_diff(
    library: str,
    old_version: str,
    new_version: str,
    old_entries: list[dict],
    new_entries: list[dict],
    generic_names: set[str],
    rule_deprecated: set[str] | None = None,
    provenance: dict | None = None,
    rule_kept_keywords: set[str] | None = None,
    rule_listed: dict[str, str] | None = None,
) -> dict:
    rule_deprecated = rule_deprecated or set()
    rule_kept_keywords = rule_kept_keywords or set()
    old = {e["symbol"]: e for e in old_entries}
    new = {e["symbol"]: e for e in new_entries}
    buckets: dict[str, dict] = {b: {} for b in BUCKETS}

    for symbol in sorted(set(old) | set(new)):
        if symbol in old and symbol not in new:
            if _absorbed_keyword(old[symbol], new, rule_kept_keywords):
                entry = _summary(old[symbol])
                entry["deprecated_by"] = ["rule_set"]
                entry["absorbed_by_var_kwargs"] = True
                buckets["deprecated_in_new"][symbol] = entry
            else:
                buckets["old_only"][symbol] = _summary(old[symbol])
        elif symbol in new and symbol not in old:
            buckets["new_only"][symbol] = _summary(new[symbol])
        else:
            bucket = _bucket(old[symbol], new[symbol], rule_deprecated)
            entry = _summary(new[symbol])
            # A shared symbol was found by the walk only if both sides' walks reached it.
            sides = (old[symbol].get("found_by", "walk"), new[symbol].get("found_by", "walk"))
            entry["found_by"] = "walk" if sides == ("walk", "walk") else "rule_seed"
            if bucket == "deprecated_in_new" and not entry.get("deprecated_by"):
                entry["deprecated_by"] = ["rule_set"]
            if bucket in ("shared_changed", "shared_unknown"):
                entry["old"] = _summary(old[symbol])
            buckets[bucket][symbol] = entry

    index: dict[str, dict] = {}
    for side, entries in (("old", old_entries), ("new", new_entries)):
        for e in entries:
            if e["kind"] != "method":
                continue
            slot = index.setdefault(e["name"], {"old": [], "new": [], "generic": e["name"] in generic_names})
            if e["owner"] not in slot[side]:
                slot[side].append(e["owner"])
    for slot in index.values():
        slot["old"].sort()
        slot["new"].sort()

    return {
        "library": library,
        "old_version": old_version,
        "new_version": new_version,
        **buckets,
        "method_name_index": dict(sorted(index.items())),
        "rule_listed": dict(sorted((rule_listed or {}).items())),
        "counts": {b: len(buckets[b]) for b in BUCKETS},
        "provenance": provenance or {},
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def bucket_of(diff: dict, symbol: str) -> str | None:
    for b in BUCKETS:
        if symbol in diff[b]:
            return b
    return None
