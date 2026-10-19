"""Value and behaviour gold (D-b), portable controls (D-g), param_value (D-a): the pieces of the
concept infrastructure that run without environments, on the committed rules and corpus."""

import pytest

from varag.bench.schema import CHANGE_TYPES, Concept, KINDS, PARAMETER_LEVEL, load_concept
from varag.bench.validate import gold_bucket
from varag.corpus.examples import passes_keyword
from varag.corpus.retrieve import doc_conflict, example_uses_gold, gold_lookup_symbol, linked_pairs, rule_links
from varag.inventory.build import load_diff
from varag.inventory.rules import behaviour_rules


def test_schema_has_the_new_kind_and_change_type():
    assert "param_value" in CHANGE_TYPES and "param_value" in PARAMETER_LEVEL
    assert "portable_control" in KINDS
    c = Concept(id="x", library="pandas", kind="portable_control", split="dev", query="q", entry_point="f", directory=None)
    assert c.is_control and c.is_portable_control
    assert not Concept(id="y", library="pandas", kind="no_conflict", split="dev", query="q", entry_point="f", directory=None).is_portable_control


def test_value_gold_resolves_through_confirmed_rules():
    diff = load_diff("pandas")
    assert gold_bucket(diff, "pandas", 'pandas.date_range(freq="M")') == "old_only"
    assert gold_bucket(diff, "pandas", 'pandas.date_range(freq="ME")') == "new_only"
    assert gold_bucket(diff, "pandas", 'pandas.date_range(freq="h")') == "shared_same"      # no rule: works on both
    assert gold_bucket(diff, "pandas", "pandas.read_csv(date_parser)") == "old_only"        # keyword gold, unchanged
    assert gold_bucket(diff, "pandas", "pandas.DataFrame.applymap") == "old_only"
    assert gold_lookup_symbol('pandas.date_range(freq="M")') == "pandas.date_range(freq)"
    assert gold_lookup_symbol("pydantic.Field(regex)") == "pydantic.Field(regex)" and gold_lookup_symbol("numpy.trapz") == "numpy.trapz"


def test_linked_pairs_cover_replacements_values_and_behaviours():
    def concept(library, old, new):
        return Concept(id="x", library=library, kind="concept", split="dev", query="q", entry_point="f", directory=None, gold={"old": [old], "new": [new]})

    mapping = {"pandas.DataFrame.applymap": "pandas.DataFrame.map"}
    assert linked_pairs(concept("pandas", "pandas.DataFrame.applymap", "pandas.DataFrame.map"), mapping) == [("pandas.DataFrame.applymap", "pandas.DataFrame.map", "replacement")]
    assert linked_pairs(concept("pandas", 'pandas.date_range(freq="M")', 'pandas.date_range(freq="ME")'), {}) == [('pandas.date_range(freq="M")', 'pandas.date_range(freq="ME")', "value_rule")]
    assert linked_pairs(concept("pandas", 'pandas.date_range(freq="M")', 'pandas.date_range(freq="h")'), {}) == []
    assert linked_pairs(concept("pandas", "pandas.Series.astype", "pandas.DatetimeProperties.as_unit"), {}) == [("pandas.Series.astype", "pandas.DatetimeProperties.as_unit", "behaviour_rule")]
    assert linked_pairs(concept("numpy", "numpy.unique", "numpy.unique_inverse"), {}) == [("numpy.unique", "numpy.unique_inverse", "behaviour_rule")]
    assert linked_pairs(concept("numpy", "numpy.unique", "numpy.trapezoid"), {}) == []


def test_behaviour_rules_count_only_probe_confirmed_entries():
    confirmed = {r["probe_id"] for r in behaviour_rules("pandas")}
    assert {"pd-v03-as-unit", "pd-v04-value-counts-name", "pd-v19-cow-chained"} <= confirmed
    assert len(behaviour_rules("pandas", confirmed_only=False)) >= len(confirmed)
    assert {r["probe_id"] for r in behaviour_rules("numpy")} >= {"np-v04-unique-inverse", "np-v02-floor-int"}


def test_rule_links_make_value_and_behaviour_pairs_conflict():
    versions = {"old": "1.5.3", "new": "3.0.6"}
    diff = load_diff("pandas")
    links = rule_links("pandas")
    assert any(l["type"] == "value_rule" and l["old"] == "pandas.date_range(freq)" for l in links)
    assert any(l["type"] == "behaviour_rule" and l["new"] == "pandas.DatetimeProperties.as_unit" for l in links)
    old_dr = {"chunk_id": "pandas-1.5.3-date_range", "version": "1.5.3", "symbols": ["pandas.date_range", "pandas.date_range(freq)"]}
    new_dr = {"chunk_id": "pandas-3.0.6-date_range", "version": "3.0.6", "symbols": ["pandas.date_range", "pandas.date_range(freq)"]}
    found, reasons = doc_conflict([old_dr, new_dr], diff, {}, versions, links)
    assert found and any(r["type"] == "value_rule" and r["symbol"].startswith("pandas.date_range(freq=") for r in reasons)
    # One version alone, or the same owner without any link, does not conflict.
    assert not doc_conflict([old_dr], diff, {}, versions, links)[0]
    old_x = {"chunk_id": "pandas-1.5.3-DataFrame.explode", "version": "1.5.3", "symbols": ["pandas.DataFrame.explode"]}
    new_x = {"chunk_id": "pandas-3.0.6-DataFrame.explode", "version": "3.0.6", "symbols": ["pandas.DataFrame.explode"]}
    assert not doc_conflict([old_x, new_x], diff, {}, versions, links)[0]
    # A same-symbol behaviour pair (value_counts) conflicts when both versions' chunks are present.
    old_vc = {"chunk_id": "pandas-1.5.3-Series.value_counts", "version": "1.5.3", "symbols": ["pandas.Series.value_counts"]}
    new_vc = {"chunk_id": "pandas-3.0.6-Series.value_counts", "version": "3.0.6", "symbols": ["pandas.Series.value_counts"]}
    found, reasons = doc_conflict([old_vc, new_vc], {**diff, "shared_changed": {k: v for k, v in diff["shared_changed"].items() if k != "pandas.Series.value_counts"}}, {}, versions, links)
    assert found and any(r["type"] == "behaviour_rule" for r in reasons)


def test_examples_can_prefer_a_gold_value():
    code = "idx = pd.date_range('2020-01-01', periods=3, freq='M')\n"
    assert passes_keyword(code, "date_range", "freq") and passes_keyword(code, "date_range", "freq", "M")
    assert not passes_keyword(code, "date_range", "freq", "ME")
    chunk = {"parts": {"example": code}}
    assert example_uses_gold(chunk, 'pandas.date_range(freq="M")') and not example_uses_gold(chunk, 'pandas.date_range(freq="ME")')
    assert example_uses_gold(chunk, "pandas.date_range(freq)") and example_uses_gold(chunk, "pandas.date_range")


def test_portable_control_loads_from_a_directory(tmp_path):
    d = tmp_path / "ptc-pyd-900"
    d.mkdir()
    (d / "concept.yaml").write_text(
        "id: ptc-pyd-900\nlibrary: pydantic\nkind: portable_control\nsplit: dev\nquery: >\n  Write `make_point(x, y)` returning a model instance with integer fields x and y.\n"
        "entry_point: make_point\ngold:\n  shared: [\"pydantic.BaseModel\"]\n", encoding="utf-8")
    (d / "ref_portable.py").write_text("from pydantic import BaseModel\n\nclass Point(BaseModel):\n    x: int\n    y: int\n\ndef make_point(x, y):\n    return Point(x=x, y=y)\n", encoding="utf-8")
    (d / "test_solution.py").write_text("from solution import make_point\n\ndef test_point():\n    assert make_point(1, 2).y == 2\n", encoding="utf-8")
    c = load_concept(d)
    assert c.is_control and c.is_portable_control and c.has_portable and c.target_sides == ()
