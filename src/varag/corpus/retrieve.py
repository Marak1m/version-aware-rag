"""v0 retrieval: gold injection, BM25 distractors, counterbalanced order, and the doc-conflict test.

Decisions (docs/plans/M4.md, as revised by the user on 2026-10-08):
- Gold chunks for both versions are always present. A keyword gold symbol resolves to its owner's
  chunk, whose `symbols` list carries the keyword (D5).
- Distractors are drawn the same way for every instance, controls included: the top
  `k_distract` BM25 hits per version over the whole corpus minus the concept's gold symbols. The
  query is the concept's task text only, not the user's context, so all instances of a concept
  share distractors.
- Order: per concept, a permutation seeded from the experiment seed and the concept id puts the
  target's gold chunk first in exactly half of the targeted instances.
- Doc conflict: a set conflicts only if it holds a linked pair across versions:
    (a) a `shared_changed` symbol with chunks from both versions, or
    (b) an old-side symbol (`old_only` or `deprecated_in_new`) in an old-version chunk and its
        mapped replacement in a new-version chunk.
  Mappings come from data/rules (replacements.json) only, never from concept gold. Each linked
  pair is reported as a conflict reason.
- Gold examples (user decision 2026-10-15): a concept's gold chunks on the two sides either both
  show an example that uses the gold symbol or keyword, or neither does. When only one side has
  one, it is stripped at injection time for that concept's instances; the corpus is unchanged.
  The result, `both` or `neither`, is recorded in validation.json and slices the results.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass, field
from functools import lru_cache

from varag.bench.instances import Instance
from varag.bench.schema import Concept
from varag.config import SIDES, env_name, load_experiment, other_side
from varag.corpus.bm25 import BM25
from varag.corpus.build import corpus_path
from varag.corpus.chunks import Parts, render as render_parts
from varag.corpus.examples import uses_symbol
from varag.envs.build import read_manifest
from varag.inventory.build import load_diff
from varag.inventory.diff import bucket_of
from varag.inventory.rules import rules_dir

OLD_SIDE_BUCKETS = ("old_only", "deprecated_in_new")
PROVENANCE_FIELDS = ("library", "version", "lock_sha256", "source", "content_sha256", "created_at", "tokenizer")


# --- loading -------------------------------------------------------------------------------


def versions_for(library: str) -> dict[str, str]:
    manifest = read_manifest()
    return {side: manifest[env_name(library, side)]["library_version"] for side in SIDES}


@lru_cache(maxsize=16)
def load_corpus(library: str, version: str) -> tuple[dict, ...]:
    path = corpus_path(library, version)
    if not path.exists():
        raise FileNotFoundError(f"{path} missing: run `varag corpus build`")
    return tuple(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


@lru_cache(maxsize=16)
def _symbol_index(library: str, version: str) -> dict[str, str]:
    index: dict[str, str] = {}
    for chunk in load_corpus(library, version):
        for symbol in chunk["symbols"]:
            index.setdefault(symbol, chunk["chunk_id"])
    return index


@lru_cache(maxsize=16)
def _chunks_by_id(library: str, version: str) -> dict[str, dict]:
    return {c["chunk_id"]: c for c in load_corpus(library, version)}


@lru_cache(maxsize=16)
def _bm25(library: str, version: str) -> BM25:
    return BM25([(c["chunk_id"], c["text"]) for c in load_corpus(library, version)])


@lru_cache(maxsize=8)
def replacements(library: str) -> dict[str, str]:
    path = rules_dir(library) / "replacements.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return {old: v["new"] for old, v in data.get("replacements", {}).items()}


def chunk_for(library: str, version: str, symbol: str) -> dict | None:
    chunk_id = _symbol_index(library, version).get(symbol)
    return _chunks_by_id(library, version)[chunk_id] if chunk_id else None


# --- retrieval -----------------------------------------------------------------------------


@dataclass
class Retrieved:
    chunk_id: str
    version: str
    side: str
    role: str                 # gold | distractor
    score: float | None = None
    example_stripped: bool = False


@dataclass
class RetrievedSet:
    instance_id: str
    items: list[Retrieved]
    target_gold_first: bool | None
    conflict: bool
    conflict_reason: list[dict] = field(default_factory=list)
    gold_examples: str = ""   # both | neither

    def chunks(self, library: str) -> list[dict]:
        """The chunks as injected: a gold chunk whose example was stripped comes without it."""
        out = []
        for r in self.items:
            chunk = _chunks_by_id(library, r.version)[r.chunk_id]
            out.append(without_example(chunk) if r.example_stripped else chunk)
        return out

    def trace(self) -> dict:
        return asdict(self)


def gold_symbols(concept: Concept, side: str) -> list[str]:
    return list(concept.gold.get("shared", [])) if concept.is_control else list(concept.gold.get(side, []))


def gold_chunks(concept: Concept, side: str, version: str) -> list[dict]:
    out, seen = [], set()
    for symbol in gold_symbols(concept, side):
        chunk = chunk_for(concept.library, version, symbol)
        if chunk and chunk["chunk_id"] not in seen:
            out.append(chunk)
            seen.add(chunk["chunk_id"])
    return out


def example_uses_gold(chunk: dict | None, symbol: str) -> bool:
    """The chunk shows an example that uses the gold symbol, or for a keyword gold
    (``owner(keyword)``) one that passes the keyword to the owner."""
    example = (chunk or {}).get("parts", {}).get("example")
    if not example:
        return False
    owner, _, rest = symbol.partition("(")
    return uses_symbol(example, owner.rsplit(".", 1)[-1], rest[:-1] or None)


def gold_examples(concept: Concept) -> tuple[str, list[str]]:
    """``both`` or ``neither``, and the sides whose gold examples are stripped at injection so
    that only one side never shows one."""
    versions = versions_for(concept.library)
    shows = {side: any(example_uses_gold(chunk_for(concept.library, versions[side], s), s) for s in gold_symbols(concept, side))
             for side in SIDES}
    if all(shows.values()):
        return "both", []
    return "neither", [side for side in SIDES if shows[side]]


def without_example(chunk: dict) -> dict:
    stripped = {**chunk, "parts": {**chunk["parts"], "example": None}, "example_stripped": True, "n_tokens": None}
    stripped["text"] = render(stripped)
    return stripped


def distractors(concept: Concept, version: str, k: int) -> list[tuple[str, float]]:
    """Top-k BM25 chunks for the concept's task text, excluding the concept's gold chunks."""
    gold_ids = set()
    for side in SIDES:
        for symbol in gold_symbols(concept, side):
            chunk_id = _symbol_index(concept.library, version).get(symbol)
            if chunk_id:
                gold_ids.add(chunk_id)
    return _bm25(concept.library, version).top(concept.query, k, exclude=gold_ids)


def similar_chunks(library: str, version: str, query: str, k: int = 2) -> list[dict]:
    """The k BM25-nearest chunks of one version to a free-text query (the guard's fallback when no
    replacement is known for an offending symbol)."""
    by_id = _chunks_by_id(library, version)
    return [by_id[cid] for cid, _ in _bm25(library, version).top(query, k, exclude=set())]


def _seed(concept_id: str) -> int:
    base = int(load_experiment().get("seed", 0))
    return int(hashlib.sha256(f"{base}:{concept_id}".encode()).hexdigest()[:12], 16)


def order_assignment(concept: Concept, instance_ids: list[str]) -> dict[str, bool]:
    """instance id -> whether the target's (or, for a control, the old side's) gold chunk comes first.
    Exactly half of each concept's instances get True; with an odd count the extra one gets False."""
    ids = sorted(instance_ids)
    rng = random.Random(_seed(concept.id))
    shuffled = ids[:]
    rng.shuffle(shuffled)
    first = set(shuffled[: len(ids) // 2])
    return {i: i in first for i in ids}


def retrieve(instance: Instance, concept: Concept, gold_first: bool, k: int | None = None) -> RetrievedSet:
    library = concept.library
    versions = versions_for(library)
    k = int(load_experiment().get("corpus", {}).get("k_distract", 2)) if k is None else k
    lead = instance.target or "old"
    order = [lead, other_side(lead)] if gold_first else [other_side(lead), lead]
    label, strip_sides = gold_examples(concept)
    items: list[Retrieved] = []
    for side in order:
        items += [Retrieved(c["chunk_id"], versions[side], side, "gold", example_stripped=side in strip_sides and bool(c["parts"]["example"]))
                  for c in gold_chunks(concept, side, versions[side])]
    for side in order:
        items += [Retrieved(cid, versions[side], side, "distractor", round(score, 4)) for cid, score in distractors(concept, versions[side], k)]
    chunks = [_chunks_by_id(library, r.version)[r.chunk_id] for r in items]
    conflict, reasons = doc_conflict(chunks, load_diff(library), replacements(library), versions)
    return RetrievedSet(instance.instance_id, items, gold_first if instance.target else None, conflict, reasons, label)


# --- conflict test and filters ------------------------------------------------------------


def doc_conflict(chunks: list[dict], diff: dict, mapping: dict[str, str], versions: dict[str, str]) -> tuple[bool, list[dict]]:
    """True when the set holds a linked pair across versions (see module docstring)."""
    by_version: dict[str, dict[str, str]] = {versions["old"]: {}, versions["new"]: {}}
    for chunk in chunks:
        if chunk["version"] in by_version:
            for symbol in chunk["symbols"]:
                by_version[chunk["version"]].setdefault(symbol, chunk["chunk_id"])
    old, new = by_version[versions["old"]], by_version[versions["new"]]
    reasons: list[dict] = []
    for symbol in sorted(set(old) & set(new)):
        if bucket_of(diff, symbol) == "shared_changed":
            reasons.append({"type": "shared_changed", "symbol": symbol, "old_chunk": old[symbol], "new_chunk": new[symbol]})
    for symbol in sorted(old):
        bucket = bucket_of(diff, symbol)
        replacement = mapping.get(symbol)
        if bucket in OLD_SIDE_BUCKETS and replacement and replacement in new:
            reasons.append({"type": "rule_replacement", "bucket": bucket, "symbol": symbol, "replacement": replacement,
                            "old_chunk": old[symbol], "new_chunk": new[replacement]})
    return bool(reasons), reasons


def keep_version(chunks: list[dict], version: str) -> list[dict]:
    return [c for c in chunks if c["version"] == version]


def dedupe(chunks: list[dict]) -> list[dict]:
    """One chunk per primary symbol, first occurrence kept."""
    seen, out = set(), []
    for c in chunks:
        if c["symbols"][0] not in seen:
            seen.add(c["symbols"][0])
            out.append(c)
    return out


def render(chunk: dict, show_version_tags: bool = True, strip_deprecation_notes: bool = False) -> str:
    p = chunk["parts"]
    parts = Parts(fqn=p["fqn"], library=chunk["library"], version=chunk["version"], kind=chunk["symbol_kind"],
                  title=chunk["title"], signature=p["signature"], description=p["description"],
                  deprecation_note=p["deprecation_note"], example=p["example"])
    return render_parts(parts, show_version_tags, strip_deprecation_notes)


# --- validation step 7 ---------------------------------------------------------------------


def _provenance_problems(chunk: dict, lock: str) -> list[str]:
    prov = chunk.get("provenance", {})
    missing = [f for f in PROVENANCE_FIELDS if not prov.get(f)]
    problems = [f"{chunk['chunk_id']}: provenance missing {missing}"] if missing else []
    if prov.get("lock_sha256") and prov["lock_sha256"] != lock:
        problems.append(f"{chunk['chunk_id']}: built from lock {prov['lock_sha256'][:12]}, manifest has {lock[:12]}")
    if not chunk.get("source", {}).get("sha256"):
        problems.append(f"{chunk['chunk_id']}: source sha256 missing")
    return problems


def check_gold_chunks(concept: Concept) -> dict:
    """Validation step 7. Problems fail the step; info is reported either way."""
    library = concept.library
    versions = versions_for(library)
    manifest = read_manifest()
    problems: list[str] = []
    info: list[str] = []
    for side in SIDES:
        lock = manifest[env_name(library, side)]["lock_sha256"]
        for symbol in gold_symbols(concept, side):
            chunk = chunk_for(library, versions[side], symbol)
            if chunk is None:
                problems.append(f"no {versions[side]} chunk for gold {symbol}")
                continue
            problems += _provenance_problems(chunk, lock)
            example = "example " + ("discriminative" if (chunk.get("example_check") or {}).get("discriminative") else "kept") \
                if chunk["parts"]["example"] else f"no example ({chunk['example_dropped']})"
            kw = "" if chunk.get("keyword_example") is None else f", passes keyword: {'yes' if chunk['keyword_example'] else 'no'}"
            info.append(f"{side} gold {symbol} -> {chunk['chunk_id']} ({example}{kw})")
    diff = load_diff(library)
    mapping = replacements(library)
    if not concept.is_control:
        linked = [(o, mapping[o]) for o in gold_symbols(concept, "old") if mapping.get(o) in gold_symbols(concept, "new")]
        if linked:
            info.append("gold pair detected from rules: " + ", ".join(f"{o} -> {n}" for o, n in linked))
        else:
            problems.append("gold pair not linked by data/rules; add the mapping from the release notes")
    gold_set = [c for side in SIDES for c in gold_chunks(concept, side, versions[side])]
    gold_conflict, gold_reasons = doc_conflict(gold_set, diff, mapping, versions)
    probe = Instance(f"{concept.id}/probe", concept.id, library, concept.split, "ambiguous" if not concept.is_control else "control",
                     None if concept.is_control else "old", "probe", concept.query, concept_dir=str(concept.directory))
    full = retrieve(probe, concept, gold_first=True)
    info.append(f"gold-only conflict {gold_conflict} {[r['type'] + ':' + r['symbol'] for r in gold_reasons]}; "
                f"retrieved-set conflict {full.conflict} {[r['type'] + ':' + r['symbol'] for r in full.conflict_reason]}")
    expected = not concept.is_control
    if full.conflict != expected:
        problems.append(f"retrieved set conflict is {full.conflict}, expected {expected}; conflict_reason {full.conflict_reason}")
    label, strip_sides = gold_examples(concept)
    info.append(f"gold_examples {label}" + (f" ({', '.join(strip_sides)} example stripped at injection)" if strip_sides else ""))
    return {"problems": problems, "info": "; ".join(info), "record": {"gold_examples": label}}
