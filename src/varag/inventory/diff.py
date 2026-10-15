"""The old/new diff per library: the single source of truth for which symbols belong to
which version. Version inference, the blend guard and task mining all read it.

Buckets (handoff, "API inventory and diff"):
  old_only, new_only          present on one side
  deprecated_in_new           present on both, deprecated on the new side only (or rule-listed)
  shared_changed              same symbol, both signatures read, different parameters or defaults
  shared_unknown              a kind mismatch, or a callable whose signature was not read on
                              one side (user decision 2026-10-15); also a parameter present on
                              one side only whose owner exists on both but was not read on the
                              other (unread signature or a kind mismatch), since its absence
                              there is not evidence
  shared_same                 read on both sides and equal: both signatures read and equal, or
                              both non-callables of the same kind; the allowlist for portable answers
  method_name_index           bare method name -> owners per side, with a generic flag
"""

from __future__ import annotations

from datetime import datetime, timezone

BUCKETS = ("old_only", "new_only", "deprecated_in_new", "shared_changed", "shared_unknown", "shared_same")
SIGNATURE_KINDS = ("function", "method", "class")


def _is_callable(entry: dict) -> bool:
    return entry["kind"] in SIGNATURE_KINDS or bool(entry.get("callable"))


def _summary(entry: dict) -> dict:
    out = {"kind": entry["kind"], "owner": entry["owner"], "name": entry["name"], "found_by": entry.get("found_by", "walk")}
    if entry["kind"] == "param":
        out["default"] = entry.get("default")
    elif _is_callable(entry):
        out["callable"] = True
        out["signature"] = entry.get("signature")
        out["params"] = entry.get("params", [])
        out["signature_known"] = entry.get("signature_known", False)
        out["signature_source"] = entry.get("signature_source", "inspect" if entry.get("signature_known") else "none")
        out["accepts_var_kwargs"] = entry.get("accepts_var_kwargs", False)
    if entry.get("deprecated"):
        out["deprecated_by"] = entry.get("deprecated_by", [])
    return out


def _bucket(old: dict, new: dict, rule_deprecated: set[str]) -> str:
    symbol = old["symbol"]
    if symbol in rule_deprecated or (new.get("deprecated") and not old.get("deprecated")):
        return "deprecated_in_new"
    if old["kind"] != new["kind"]:
        return "shared_unknown"
    if old["kind"] == "param":
        return "shared_changed" if old.get("default") != new.get("default") else "shared_same"
    if _is_callable(old) or _is_callable(new):
        if not (old.get("signature_known") and new.get("signature_known")):
            return "shared_unknown"
        if old.get("params") != new.get("params") or old.get("signature") != new.get("signature"):
            return "shared_changed"
    return "shared_same"


def _owner_unread_elsewhere(entry: dict, here: dict[str, dict], there: dict[str, dict]) -> bool:
    """A parameter whose owner exists on the other side too, but whose signature was not read there
    (or whose kind differs): the parameter's absence on that side is not evidence."""
    if entry["kind"] != "param":
        return False
    owner_here, owner_there = here.get(entry["owner"]), there.get(entry["owner"])
    if owner_here is None or owner_there is None:
        return False
    return owner_here["kind"] != owner_there["kind"] or not owner_there.get("signature_known")


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
            elif _owner_unread_elsewhere(old[symbol], old, new):
                buckets["shared_unknown"][symbol] = {**_summary(old[symbol]), "present_on": "old", "owner_unread_on": "new"}
            else:
                buckets["old_only"][symbol] = _summary(old[symbol])
        elif symbol in new and symbol not in old:
            if _owner_unread_elsewhere(new[symbol], new, old):
                buckets["shared_unknown"][symbol] = {**_summary(new[symbol]), "present_on": "new", "owner_unread_on": "old"}
            else:
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
