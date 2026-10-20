"""Framework fixes found while authoring the test split (2026-10-20)."""

from varag.corpus.retrieve import chunk_for_gold, doc_conflict
from varag.inventory.rules import replacements
from varag.pipeline.signals import _literal

import ast


def test_bool_literals_are_matchable_values():
    assert _literal(ast.parse("False", mode="eval").body) == (True, False)
    assert _literal(ast.parse("None", mode="eval").body) == (True, None)
    assert _literal(ast.parse("3", mode="eval").body) == (False, None)


def test_a_move_into_a_deprecated_module_is_not_a_replacement():
    assert not any(".deprecated." in v["new"] for v in replacements("pydantic").values())


def test_value_gold_falls_back_to_an_unread_owner_chunk():
    chunk = chunk_for_gold("numpy", "1.26.4", "numpy.array(copy=False)")
    assert chunk is not None and chunk["chunk_id"] == "numpy-1.26.4-array"


def test_value_link_matches_owner_chunks():
    old = {"version": "1", "chunk_id": "o", "symbols": ["lib.f"]}
    new = {"version": "2", "chunk_id": "n", "symbols": ["lib.f", "lib.f(p)"]}
    link = {"type": "value_rule", "old": "lib.f(p)", "new": "lib.f(p)", "owner": "lib.f", "symbol": "lib.f(p=False)", "replacement": "lib.f(p=None)"}
    from varag.inventory.diff import BUCKETS

    diff = {"library": "lib", **{b: [] for b in BUCKETS}}
    conflict, reasons = doc_conflict([old, new], diff, {}, {"old": "1", "new": "2"}, [link])
    assert conflict and reasons[0]["old_chunk"] == "o" and reasons[0]["new_chunk"] == "n"
