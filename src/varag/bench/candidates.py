"""``varag bench candidates``: old/new pairings to mine for concepts, at two levels counted separately.

- Symbol pairs: a rule-set replacement (data/rules/<library>/replacements.json) from an old-side
  symbol (old_only or deprecated_in_new) to a symbol present on the new side.
- Keyword pairs: a keyword present on one side only, or renamed, on an owner present in both
  versions (numpy.reshape(newshape), numpy.percentile(interpolation), the pydantic Field V1
  keywords). A rename or replacement comes from the rule sets when they list it. Otherwise a
  keyword the owner lost is paired with one it gained when their names are related (one is a
  prefix or suffix of the other, or they are at least 75% similar), best match first, one to one.
  Such a rename is ``inferred``: before a concept can use it, the mapping has to be added to
  data/rules from the release notes (validation step 7). Remaining keywords are listed one-sided
  as removed, deprecated or added.

Each row shows, per side, whether the gold chunk shows an example that uses the symbol or keyword
(``discriminative``, ``portable`` or ``none``) and the ``gold_examples`` a concept built on the
pair would get (both or neither; user decision 2026-10-15).
"""

from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher

from varag.config import SIDES
from varag.corpus.retrieve import chunk_for, example_uses_gold, replacements, versions_for
from varag.inventory.build import load_diff
from varag.inventory.diff import bucket_of

OLD_SIDE = ("old_only", "deprecated_in_new")
SHOWN = ("discriminative", "portable")


def _owner(symbol: str) -> str:
    return symbol.split("(", 1)[0]


def _keyword(symbol: str) -> str:
    return symbol[symbol.index("(") + 1:-1]


def name_relation(old: str, new: str) -> float:
    """How strongly two keyword names suggest a rename: 1.0 when one is a prefix or suffix of the
    other (newshape/shape, quantile/q, value/secret_value), else their similarity ratio if it is at
    least 0.75, else 0."""
    a, b = old.strip("_").lower(), new.strip("_").lower()
    if a and b and (a.startswith(b) or b.startswith(a) or a.endswith(b) or b.endswith(a)):
        return 1.0
    ratio = SequenceMatcher(None, a, b).ratio()
    return ratio if ratio >= 0.75 else 0.0


def _present_in_both(diff: dict, symbol: str) -> bool:
    return bucket_of(diff, symbol) not in (None, "old_only", "new_only")


def _example(library: str, version: str, symbol: str | None) -> str:
    if symbol is None:
        return "-"
    try:
        chunk = chunk_for(library, version, symbol)
    except FileNotFoundError:
        chunk = None
    if not example_uses_gold(chunk, symbol):
        return "none"
    return "discriminative" if (chunk.get("example_check") or {}).get("discriminative") else "portable"


def _row(library: str, diff: dict, versions: dict, old: str | None, new: str | None, level: str, change: str, source: str) -> dict:
    row = {"old": old, "new": new, "level": level, "change": change, "source": source,
           "old_bucket": bucket_of(diff, old) if old else None, "new_bucket": bucket_of(diff, new) if new else None}
    for side, symbol in (("old", old), ("new", new)):
        row[f"{side}_example"] = _example(library, versions[side], symbol)
    if old is None or new is None:
        row["gold_examples"] = "-"
    else:
        row["gold_examples"] = "both" if all(row[f"{side}_example"] in SHOWN for side in SIDES) else "neither"
    return row


def symbol_pairs(library: str) -> list[dict]:
    diff, versions = load_diff(library), versions_for(library)
    out = []
    for old, new in sorted(replacements(library).items()):
        if "(" in old:
            continue                      # keyword level: keyword_pairs lists it
        if bucket_of(diff, old) not in OLD_SIDE or bucket_of(diff, new) in (None, "old_only"):
            continue
        out.append(_row(library, diff, versions, old, new, "symbol", "replaced", "rules"))
    return out


def keyword_pairs(library: str) -> list[dict]:
    diff, versions, mapping = load_diff(library), versions_for(library), replacements(library)

    def keywords(buckets: tuple[str, ...]) -> list[str]:
        return sorted(s for b in buckets for s in diff.get(b, {}) if "(" in s and _present_in_both(diff, _owner(s)))

    old_keywords, new_keywords = keywords(OLD_SIDE), keywords(("new_only",))
    rows: list[dict] = []
    paired: set[str] = set()
    for old in old_keywords:
        new = mapping.get(old)
        if new and bucket_of(diff, new) not in (None, "old_only"):
            change = "renamed" if "(" in new and _owner(new) == _owner(old) else "replaced"
            rows.append(_row(library, diff, versions, old, new, "keyword", change, "rules"))
            paired |= {old, new}
    by_owner: dict[str, tuple[list[str], list[str]]] = {}
    for index, symbols in enumerate((old_keywords, new_keywords)):
        for s in symbols:
            if s not in paired:
                by_owner.setdefault(_owner(s), ([], []))[index].append(s)
    for owner, (olds, news) in sorted(by_owner.items()):
        scored = sorted(((name_relation(_keyword(o), _keyword(n)), o, n) for o in olds for n in news), key=lambda t: (-t[0], t[1], t[2]))
        for score, old, new in scored:
            if score > 0 and old in olds and new in news:
                rows.append(_row(library, diff, versions, old, new, "keyword", "renamed", "inferred"))
                olds, news = [o for o in olds if o != old], [n for n in news if n != new]
        for old in olds:
            change = "deprecated" if bucket_of(diff, old) == "deprecated_in_new" else "removed"
            rows.append(_row(library, diff, versions, old, None, "keyword", change, "inventory"))
        rows += [_row(library, diff, versions, None, new, "keyword", "added", "inventory") for new in news]
    return rows


def counts(symbol_rows: list[dict], keyword_rows: list[dict]) -> dict:
    return {
        "symbol_pairs": len(symbol_rows),
        "symbol_discriminative_both": sum(1 for r in symbol_rows if r["old_example"] == r["new_example"] == "discriminative"),
        "keyword_pairs": len(keyword_rows),
        "keyword_by_change": dict(sorted(Counter(f"{r['change']} ({r['source']})" for r in keyword_rows).items())),
        "keyword_gold_examples_both": sum(1 for r in keyword_rows if r["gold_examples"] == "both"),
    }


def format_rows(title: str, rows: list[dict]) -> str:
    lines = [title, f"  {'old':50} {'new':50} {'change':22} {'buckets':36} examples (old/new)  gold_examples"]
    for r in rows:
        buckets = f"{r['old_bucket'] or '-'} -> {r['new_bucket'] or '-'}"
        lines.append(f"  {r['old'] or '-':50} {r['new'] or '-':50} {r['change'] + ' (' + r['source'] + ')':22} {buckets:36} "
                     f"{r['old_example']}/{r['new_example']}  {r['gold_examples']}")
    return "\n".join(lines)


def format_counts(by_library: dict[str, dict]) -> str:
    lines = ["counts per library"]
    for library, c in by_library.items():
        lines.append(f"  {library}: {c['symbol_pairs']} symbol pair(s), {c['symbol_discriminative_both']} with discriminative "
                     f"examples on both sides; {c['keyword_pairs']} keyword pair(s), {c['keyword_gold_examples_both']} with "
                     f"gold_examples both; " + ", ".join(f"{k} {v}" for k, v in c["keyword_by_change"].items()))
    return "\n".join(lines)
