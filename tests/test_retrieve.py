"""Unit tests for the doc-conflict test, order assignment and filters (synthetic chunks)."""

from varag.bench.schema import Concept
from varag.corpus.retrieve import dedupe, doc_conflict, keep_version, order_assignment

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
