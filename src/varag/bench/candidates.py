"""``varag bench candidates``: old/new pairings to mine for concepts.

Pairs come from the rule-set replacements (data/rules/<library>/replacements.json): an old-side
symbol (old_only or deprecated_in_new) whose replacement is present on the new side. Each pair is
shown with its buckets, change level (symbol or keyword), and whether the corpus has a
discriminative example for each side, which is what a concept's gold chunks will show the model.
"""

from __future__ import annotations

from varag.corpus.retrieve import chunk_for, replacements, versions_for
from varag.inventory.build import load_diff
from varag.inventory.diff import bucket_of


def candidate_pairs(library: str) -> list[dict]:
    diff = load_diff(library)
    versions = versions_for(library)
    out = []
    for old, new in sorted(replacements(library).items()):
        old_bucket, new_bucket = bucket_of(diff, old), bucket_of(diff, new)
        if old_bucket not in ("old_only", "deprecated_in_new") or new_bucket in (None, "old_only"):
            continue
        row = {"old": old, "new": new, "old_bucket": old_bucket, "new_bucket": new_bucket,
               "level": "keyword" if "(" in old else "symbol"}
        for side, symbol in (("old", old), ("new", new)):
            try:
                chunk = chunk_for(library, versions[side], symbol)
            except FileNotFoundError:
                chunk = None
            check = (chunk or {}).get("example_check") or {}
            row[f"{side}_example"] = "none" if not chunk or not chunk["parts"]["example"] else (
                "discriminative" if check.get("discriminative") else "portable")
        out.append(row)
    return out


def format_pairs(rows: list[dict]) -> str:
    lines = [f"{'old':45} {'new':45} {'level':8} {'buckets':30} examples (old/new)"]
    for r in rows:
        lines.append(f"{r['old']:45} {r['new']:45} {r['level']:8} {r['old_bucket'] + ' -> ' + r['new_bucket']:30} "
                     f"{r['old_example']}/{r['new_example']}")
    lines.append(f"{len(rows)} pair(s); {sum(1 for r in rows if r['old_example'] == r['new_example'] == 'discriminative')} "
                 "with discriminative examples on both sides")
    return "\n".join(lines)
