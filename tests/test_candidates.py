"""Unit tests for `bench candidates`: symbol pairs and keyword-level pairs (synthetic diff)."""

import pytest

import varag.bench.candidates as cand

VERSIONS = {"old": "1.0", "new": "2.0"}
DIFF = {
    "old_only": {"lib.trapz": {}, "lib.reshape(newshape)": {}, "lib.Field(regex)": {}, "lib.Field(const)": {},
                 "lib.percentile(interpolation)": {}, "lib.fillna(method)": {}, "lib.gone": {}, "lib.gone(x)": {}},
    "new_only": {"lib.trapezoid": {}, "lib.reshape(shape)": {}, "lib.reshape(copy)": {}, "lib.Field(pattern)": {},
                 "lib.zeros(device)": {}, "lib.percentile(weights)": {}},
    "deprecated_in_new": {"lib.Field(min_items)": {}},
    "shared_changed": {"lib.reshape": {}, "lib.Field": {}, "lib.Field(min_length)": {}, "lib.fillna": {}},
    "shared_unknown": {},
    "shared_same": {"lib.percentile": {}, "lib.zeros": {}, "lib.ffill": {}},
}
MAPPING = {"lib.trapz": "lib.trapezoid", "lib.Field(regex)": "lib.Field(pattern)",
           "lib.Field(min_items)": "lib.Field(min_length)", "lib.fillna(method)": "lib.ffill"}
EXAMPLES = {("1.0", "lib.Field(regex)"): "Field(regex='a')", ("2.0", "lib.Field(pattern)"): "Field(pattern='a')",
            ("1.0", "lib.Field(min_items)"): "Field(regex='a')", ("2.0", "lib.Field(min_length)"): "Field(pattern='a')"}


@pytest.fixture(autouse=True)
def synthetic(monkeypatch):
    def chunk_for(library, version, symbol):
        example = EXAMPLES.get((version, symbol))
        return {"parts": {"example": example}, "example_check": {"discriminative": True}} if example else None

    monkeypatch.setattr(cand, "load_diff", lambda library: DIFF)
    monkeypatch.setattr(cand, "versions_for", lambda library: VERSIONS)
    monkeypatch.setattr(cand, "replacements", lambda library: MAPPING)
    monkeypatch.setattr(cand, "chunk_for", chunk_for)


def by_old(rows):
    return {(r["old"], r["new"]): r for r in rows}


def test_symbol_pairs_come_from_rules_and_exclude_keywords():
    rows = cand.symbol_pairs("lib")
    assert [(r["old"], r["new"]) for r in rows] == [("lib.trapz", "lib.trapezoid")]


def test_keyword_pairs():
    rows = by_old(cand.keyword_pairs("lib"))
    assert rows[("lib.Field(regex)", "lib.Field(pattern)")]["change"] == "renamed"
    assert rows[("lib.Field(regex)", "lib.Field(pattern)")]["source"] == "rules"
    assert rows[("lib.Field(min_items)", "lib.Field(min_length)")]["source"] == "rules"
    assert rows[("lib.fillna(method)", "lib.ffill")]["change"] == "replaced"
    # reshape lost newshape and gained shape and copy: the related name is paired, copy is added.
    inferred = rows[("lib.reshape(newshape)", "lib.reshape(shape)")]
    assert (inferred["change"], inferred["source"]) == ("renamed", "inferred")
    assert rows[(None, "lib.reshape(copy)")]["change"] == "added"
    # percentile lost interpolation and gained weights: unrelated names are not paired.
    assert rows[("lib.percentile(interpolation)", None)]["change"] == "removed"
    assert rows[(None, "lib.percentile(weights)")]["change"] == "added"
    assert rows[("lib.Field(const)", None)]["change"] == "removed"
    assert rows[(None, "lib.zeros(device)")]["change"] == "added"
    # A keyword whose owner exists on one side only is a symbol-level change, not a keyword pair.
    assert not any(r["old"] == "lib.gone(x)" for r in rows.values())
    assert len(rows) == 9


def test_keyword_rows_report_gold_examples():
    rows = by_old(cand.keyword_pairs("lib"))
    assert rows[("lib.Field(regex)", "lib.Field(pattern)")]["gold_examples"] == "both"
    # The owner chunks have examples, but they do not pass min_items / min_length.
    assert rows[("lib.Field(min_items)", "lib.Field(min_length)")]["gold_examples"] == "neither"
    assert rows[("lib.percentile(interpolation)", None)]["gold_examples"] == "-"


def test_counts_separate_symbol_and_keyword_pairs():
    c = cand.counts(cand.symbol_pairs("lib"), cand.keyword_pairs("lib"))
    assert c["symbol_pairs"] == 1 and c["keyword_pairs"] == 9
    assert c["keyword_by_change"] == {"added (inventory)": 3, "removed (inventory)": 2, "renamed (inferred)": 1,
                                      "renamed (rules)": 2, "replaced (rules)": 1}
    assert c["keyword_gold_examples_both"] == 1


def test_name_relation():
    assert cand.name_relation("newshape", "shape") == 1.0
    assert cand.name_relation("quantile", "q") == 1.0
    assert cand.name_relation("value", "secret_value") == 1.0
    assert cand.name_relation("interpolation", "weights") == 0.0
    assert cand.name_relation("downcast", "limit_area") == 0.0
    assert cand.name_relation("axis", "numeric_only") == 0.0
