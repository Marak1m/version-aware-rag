"""Unit tests for the doc-conflict test, order assignment and filters (synthetic chunks)."""

from varag.bench.schema import Concept
import varag.corpus.retrieve as retrieve_mod
from varag.corpus.retrieve import (Retrieved, RetrievedSet, dedupe, doc_conflict, example_uses_gold, gold_examples,
                                   keep_version, order_assignment)

VERSIONS = {"old": "1.0", "new": "2.0"}
DIFF = {
    "library": "lib",
    "old_only": {"lib.trapz": {}, "lib.in1d": {}, "lib.Field(regex)": {}},
    "new_only": {"lib.trapezoid": {}, "lib.Field(pattern)": {}},
    "deprecated_in_new": {"lib.Model.dict": {}},
    "shared_changed": {"lib.Field": {}, "lib.reshape": {}},
    "shared_unknown": {},
    "shared_same": {"lib.cumsum": {}, "lib.Model.model_dump": {}, "lib.isin": {}},
}
MAPPING = {"lib.trapz": "lib.trapezoid", "lib.in1d": "lib.isin", "lib.Field(regex)": "lib.Field(pattern)",
           "lib.Model.dict": "lib.Model.model_dump"}


def chunk(version, *symbols):
    return {"chunk_id": f"lib-{version}-{symbols[0]}", "version": version, "symbols": list(symbols)}


def conflict(*chunks):
    return doc_conflict(list(chunks), DIFF, MAPPING, VERSIONS)


def test_unrelated_exclusive_distractor_alone_does_not_conflict():
    found, reasons = conflict(chunk("1.0", "lib.cumsum"), chunk("2.0", "lib.cumsum"), chunk("1.0", "lib.in1d"))
    assert not found and reasons == []
    # An exclusive symbol on each side, but not mapped to each other: still no conflict.
    found, _ = conflict(chunk("1.0", "lib.in1d"), chunk("2.0", "lib.trapezoid"))
    assert not found


def test_old_symbol_and_its_rule_replacement_conflict():
    found, reasons = conflict(chunk("1.0", "lib.trapz"), chunk("2.0", "lib.trapezoid"))
    assert found and reasons == [{"type": "rule_replacement", "bucket": "old_only", "symbol": "lib.trapz",
                                  "replacement": "lib.trapezoid", "old_chunk": "lib-1.0-lib.trapz", "new_chunk": "lib-2.0-lib.trapezoid"}]


def test_pair_must_cross_versions_in_the_right_direction():
    assert not conflict(chunk("2.0", "lib.trapz"), chunk("2.0", "lib.trapezoid"))[0]
    assert not conflict(chunk("1.0", "lib.trapezoid"), chunk("2.0", "lib.trapz"))[0]


def test_deprecated_in_new_plus_replacement_is_a_linked_pair():
    found, reasons = conflict(chunk("1.0", "lib.Model.dict"), chunk("2.0", "lib.Model.model_dump"))
    assert found and reasons[0]["bucket"] == "deprecated_in_new"


def test_keyword_pairs_link_through_owner_chunks():
    found, reasons = conflict(chunk("1.0", "lib.Field", "lib.Field(regex)"), chunk("2.0", "lib.Field", "lib.Field(pattern)"))
    assert found and {r["type"] for r in reasons} == {"shared_changed", "rule_replacement"}


def test_shared_changed_needs_both_versions():
    assert conflict(chunk("1.0", "lib.reshape"), chunk("2.0", "lib.reshape"))[0]
    assert not conflict(chunk("1.0", "lib.reshape"), chunk("1.0", "lib.cumsum"))[0]


def test_mapping_comes_only_from_the_argument():
    found, _ = doc_conflict([chunk("1.0", "lib.trapz"), chunk("2.0", "lib.trapezoid")], DIFF, {}, VERSIONS)
    assert not found


def concept(cid):
    return Concept(id=cid, library="lib", kind="concept", split="dev", query="q", entry_point="f", directory=None)


def test_order_assignment_is_exactly_half_and_deterministic():
    ids = [f"c/{side}/{cond}" for side in ("old", "new") for cond in ("no-clue", "clue-pin", "stated")]
    first = order_assignment(concept("c-001"), ids)
    assert sum(first.values()) == 3 and set(first) == set(ids)
    assert order_assignment(concept("c-001"), list(reversed(ids))) == first
    odd = order_assignment(concept("c-001"), ids[:5])
    assert sum(odd.values()) == 2


def test_filters():
    chunks = [chunk("1.0", "lib.a"), chunk("2.0", "lib.a"), chunk("2.0", "lib.b")]
    assert [c["chunk_id"] for c in keep_version(chunks, "2.0")] == ["lib-2.0-lib.a", "lib-2.0-lib.b"]
    assert [c["chunk_id"] for c in dedupe(chunks)] == ["lib-1.0-lib.a", "lib-2.0-lib.b"]


# --- gold examples: both or neither (user decision 2026-10-15) -----------------------------


def ex_chunk(version, symbol, example):
    owner = symbol.split("(")[0]
    return {"chunk_id": f"lib-{version}-{owner}", "library": "lib", "version": version, "symbols": [owner, symbol],
            "symbol_kind": "function", "title": owner, "text": "full text", "n_tokens": 40,
            "parts": {"fqn": owner, "signature": "(x)", "description": "Does a thing.", "deprecation_note": None, "example": example}}


def gold_concept(old, new):
    return Concept(id="c-001", library="lib", kind="concept", split="dev", query="q", entry_point="f", directory=None,
                   gold={"old": [old], "new": [new]})


def patch_corpus(monkeypatch, chunks):
    by_symbol = {(c["version"], s): c for c in chunks for s in c["symbols"]}
    monkeypatch.setattr(retrieve_mod, "versions_for", lambda library: VERSIONS)
    monkeypatch.setattr(retrieve_mod, "chunk_for", lambda library, version, symbol: by_symbol.get((version, symbol)))


def test_example_uses_gold_symbol_or_keyword():
    assert example_uses_gold(ex_chunk("1.0", "lib.trapz", "lib.trapz([1, 2])"), "lib.trapz")
    assert not example_uses_gold(ex_chunk("1.0", "lib.trapz", None), "lib.trapz")
    keyword_chunk = ex_chunk("1.0", "lib.Field(regex)", "x = Field(regex='a')")
    assert example_uses_gold(keyword_chunk, "lib.Field(regex)")
    assert not example_uses_gold(ex_chunk("1.0", "lib.Field(regex)", "x = Field(default=1)"), "lib.Field(regex)")
    assert not example_uses_gold(None, "lib.trapz")


def test_both_sides_with_examples_keep_them(monkeypatch):
    patch_corpus(monkeypatch, [ex_chunk("1.0", "lib.trapz", "lib.trapz([1, 2])"), ex_chunk("2.0", "lib.trapezoid", "lib.trapezoid([1, 2])")])
    assert gold_examples(gold_concept("lib.trapz", "lib.trapezoid")) == ("both", [])


def test_one_sided_example_is_stripped(monkeypatch):
    # The new side's example does not pass the gold keyword, so only the old side shows one.
    patch_corpus(monkeypatch, [ex_chunk("1.0", "lib.Field(regex)", "Field(regex='a')"),
                               ex_chunk("2.0", "lib.Field(pattern)", "Field(default=1)")])
    assert gold_examples(gold_concept("lib.Field(regex)", "lib.Field(pattern)")) == ("neither", ["old"])


def test_no_examples_is_neither(monkeypatch):
    patch_corpus(monkeypatch, [ex_chunk("1.0", "lib.Field(regex)", None), ex_chunk("2.0", "lib.Field(pattern)", None)])
    assert gold_examples(gold_concept("lib.Field(regex)", "lib.Field(pattern)")) == ("neither", [])


def test_stripped_gold_chunk_is_injected_without_its_example(monkeypatch):
    old = ex_chunk("1.0", "lib.trapz", "lib.trapz([1, 2])")
    new = ex_chunk("2.0", "lib.trapezoid", "lib.trapezoid([1, 2])")
    monkeypatch.setattr(retrieve_mod, "_chunks_by_id", lambda library, version: {"1.0": {old["chunk_id"]: old}, "2.0": {new["chunk_id"]: new}}[version])
    rs = RetrievedSet("c-001/old/no-clue", [Retrieved(old["chunk_id"], "1.0", "old", "gold", example_stripped=True),
                                            Retrieved(new["chunk_id"], "2.0", "new", "gold")], True, True, [], "neither")
    injected_old, injected_new = rs.chunks("lib")
    assert injected_old["parts"]["example"] is None and injected_old["example_stripped"]
    assert "Example:" not in injected_old["text"] and "lib.trapz([1, 2])" not in injected_old["text"]
    assert injected_new is new and old["parts"]["example"] == "lib.trapz([1, 2])"   # the corpus is unchanged
    assert rs.trace()["gold_examples"] == "neither" and rs.trace()["items"][0]["example_stripped"]
