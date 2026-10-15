from varag.inventory.audit import Rule, audit_library
from varag.inventory.diff import BUCKETS, bucket_of, build_diff
from varag.inventory.rules import parse_npy201


def entry(symbol, kind="function", owner=None, params=None, signature=None, known=True, deprecated=False, default=None, deprecated_by=None, found_by="walk"):
    owner = owner or symbol.rpartition(".")[0]
    name = symbol.rpartition(".")[2].split("(")[0]
    e = {"symbol": symbol, "kind": kind, "owner": owner, "name": name, "params": params or [],
         "signature": signature, "signature_known": known, "deprecated": deprecated,
         "deprecated_by": deprecated_by or (["docstring"] if deprecated else []), "accepts_var_kwargs": False,
         "found_by": found_by}
    if kind == "param":
        e["default"] = default
    return e


OLD = [
    entry("lib.gone", params=["a"], signature="(a)"),
    entry("lib.same", params=["a"], signature="(a)"),
    entry("lib.changed", params=["a"], signature="(a)"),
    entry("lib.changed(a)", kind="param", owner="lib.changed", default=None),
    entry("lib.unknown", known=False),
    entry("lib.Model.dict", kind="method", owner="lib.Model", params=["by_alias"], signature="(self, by_alias=False)"),
    entry("lib.Model.append", kind="method", owner="lib.Model", params=[], signature="(self)"),
    entry("lib.ruled", params=[], signature="()"),
    entry("lib.seeded_gone", params=[], signature="()", found_by="rule_seed"),
    entry("lib.seeded_shared", params=[], signature="()", found_by="rule_seed"),
]
NEW = [
    entry("lib.seeded_shared", params=[], signature="()", found_by="walk"),
    entry("lib.added", params=["a"], signature="(a)"),
    entry("lib.same", params=["a"], signature="(a)"),
    entry("lib.changed", params=["a", "b"], signature="(a, b=1)"),
    entry("lib.changed(a)", kind="param", owner="lib.changed", default=None),
    entry("lib.changed(b)", kind="param", owner="lib.changed", default="1"),
    entry("lib.unknown", known=True, params=["x"], signature="(x)"),
    entry("lib.Model.dict", kind="method", owner="lib.Model", params=["by_alias"], signature="(self, by_alias=False)", deprecated=True, deprecated_by=["__deprecated__"]),
    entry("lib.Model.append", kind="method", owner="lib.Model", params=[], signature="(self)"),
    entry("lib.Other.append", kind="method", owner="lib.Other", params=[], signature="(self)"),
    entry("lib.ruled", params=[], signature="()"),
]


def test_buckets():
    diff = build_diff("lib", "1", "2", OLD, NEW, generic_names={"append"}, rule_deprecated={"lib.ruled"})
    assert bucket_of(diff, "lib.gone") == "old_only"
    assert bucket_of(diff, "lib.added") == "new_only"
    assert bucket_of(diff, "lib.same") == "shared_same"
    assert bucket_of(diff, "lib.changed") == "shared_changed"
    assert bucket_of(diff, "lib.changed(b)") == "new_only"
    assert bucket_of(diff, "lib.unknown") == "shared_unknown"
    assert bucket_of(diff, "lib.Model.dict") == "deprecated_in_new"
    assert bucket_of(diff, "lib.ruled") == "deprecated_in_new"
    assert diff["deprecated_in_new"]["lib.ruled"]["deprecated_by"] == ["rule_set"]   # no intrinsic route; a rule set filed it
    assert diff["deprecated_in_new"]["lib.Model.dict"]["deprecated_by"] == ["__deprecated__"]
    assert diff["shared_changed"]["lib.changed"]["old"]["params"] == ["a"]
    assert sum(diff["counts"].values()) == len({e["symbol"] for e in OLD + NEW})
    assert set(diff["counts"]) == set(BUCKETS)
    assert diff["old_only"]["lib.seeded_gone"]["found_by"] == "rule_seed"
    assert diff["shared_same"]["lib.seeded_shared"]["found_by"] == "rule_seed"   # one side needed seeding
    assert diff["shared_same"]["lib.same"]["found_by"] == "walk"


def test_keyword_absorbed_by_var_kwargs_is_deprecated_in_new_only_with_a_rule():
    old = [
        entry("lib.Field", params=["regex", "min_items"], signature="(regex=None, min_items=None, **extra)"),
        entry("lib.Field(regex)", kind="param", owner="lib.Field"),
        entry("lib.Field(min_items)", kind="param", owner="lib.Field"),
    ]
    new_var_kwargs = [{**entry("lib.Field", params=["pattern"], signature="(pattern=None, **extra)"), "accepts_var_kwargs": True},
                      entry("lib.Field(pattern)", kind="param", owner="lib.Field")]
    diff = build_diff("lib", "1", "2", old, new_var_kwargs, set(), rule_kept_keywords={"lib.Field(min_items)"}, rule_listed={"lib.Field(regex)": "t"})
    assert bucket_of(diff, "lib.Field(min_items)") == "deprecated_in_new"
    assert diff["deprecated_in_new"]["lib.Field(min_items)"]["absorbed_by_var_kwargs"] is True
    assert diff["deprecated_in_new"]["lib.Field(min_items)"]["deprecated_by"] == ["rule_set"]
    assert bucket_of(diff, "lib.Field(regex)") == "old_only"          # removed keyword stays old_only
    assert diff["rule_listed"] == {"lib.Field(regex)": "t"}
    # Without **kwargs on the new side the keyword cannot be absorbed: plain old_only.
    new_strict = [entry("lib.Field", params=["pattern"], signature="(pattern=None)"), entry("lib.Field(pattern)", kind="param", owner="lib.Field")]
    diff = build_diff("lib", "1", "2", old, new_strict, set(), rule_kept_keywords={"lib.Field(min_items)"})
    assert bucket_of(diff, "lib.Field(min_items)") == "old_only"
    # Without a rule nothing moves either.
    diff = build_diff("lib", "1", "2", old, new_var_kwargs, set())
    assert bucket_of(diff, "lib.Field(min_items)") == "old_only"


def test_method_name_index_marks_generic_names():
    diff = build_diff("lib", "1", "2", OLD, NEW, generic_names={"append"})
    index = diff["method_name_index"]
    assert index["append"] == {"old": ["lib.Model"], "new": ["lib.Model", "lib.Other"], "generic": True}
    assert index["dict"]["generic"] is False


def test_audit_recall_and_misses(monkeypatch):
    diff = build_diff("lib", "1", "2", OLD, NEW, generic_names=set(), rule_deprecated={"lib.ruled"})
    monkeypatch.setattr("varag.inventory.audit.applies", lambda library, symbol: not symbol.startswith("lib.outside"))
    rules = [
        Rule("lib", "lib.gone", ("old_only",), "t"),
        Rule("lib", "lib.Model.dict", ("deprecated_in_new",), "t"),
        Rule("lib", "lib.ruled", ("deprecated_in_new",), "t"),
        Rule("lib", "lib.same", ("old_only",), "t"),           # miss: it is shared_same
        Rule("lib", "lib.missing", ("old_only",), "t"),        # miss: not extracted at all
        Rule("lib", "lib.outside.x", ("old_only",), "t"),      # skipped: outside roots
        Rule("lib", "lib.seeded_gone", ("old_only",), "t"),     # hit, but only through rule-set seeding
    ]
    result = audit_library("lib", diff, rules)
    assert result.applicable == 6 and result.hits == 4 and result.skipped == 1
    assert {m["symbol"] for m in result.misses} == {"lib.same", "lib.missing"}
    assert result.deprecated_rule_only == ["lib.ruled"]
    assert result.walk_hits == 3 and result.seeded_hits == ["lib.seeded_gone"]
    assert abs(result.recall - 4 / 6) < 1e-9 and abs(result.walk_recall - 0.5) < 1e-9


RUST = '''
    let replacement = match qualified_name.segments() {
        ["numpy", "alltrue"] => Replacement {
            existing: "alltrue",
            details: Details::AutoImport {
                path: "numpy",
                name: "all",
                compatibility: Compatibility::BackwardsCompatible,
            },
        },
        ["numpy", "trapz"] => Replacement {
            existing: "trapz",
            details: Details::AutoImport {
                path: "numpy",
                name: "trapezoid",
                compatibility: Compatibility::Breaking,
            },
        },
        ["numpy", "NINF"] => Replacement {
            existing: "NINF",
            details: Details::AutoPurePython {
                python_expr: "-np.inf",
            },
        },
        ["numpy", "lib", "thing"] => Replacement {
            existing: "thing",
            details: Details::Manual {
                guideline: Some("Use `np.other` with a \\"flag\\"."),
            },
        },
        _ => return,
    };
'''


def test_parse_npy201_handles_every_arm_shape():
    entries = {e["path"]: e for e in parse_npy201(RUST)}
    assert entries["numpy.alltrue"]["replacement"] == "numpy.all" and entries["numpy.alltrue"]["backwards_compatible"] is True
    assert entries["numpy.trapz"]["replacement"] == "numpy.trapezoid" and entries["numpy.trapz"]["backwards_compatible"] is False
    assert entries["numpy.NINF"]["replacement"] == "-np.inf"
    assert entries["numpy.lib.thing"]["kind"] == "Manual" and "np.other" in entries["numpy.lib.thing"]["guideline"]
    assert len(entries) == 4


def test_shared_same_needs_both_sides_read_and_equal():
    old = [
        entry("lib.attr_to_func", kind="attribute", known=False),
        entry("lib.both_unread", kind="attribute", known=False),
        entry("lib.text_read", params=["a"], signature="(a)"),
        entry("lib.CONST", kind="attribute", known=False),
        entry("lib.sub", kind="module", known=False),
        entry("lib.mod_to_attr", kind="module", known=False),
    ]
    new = [
        entry("lib.attr_to_func", params=["a"], signature="(a)"),
        entry("lib.both_unread", kind="attribute", known=False),
        entry("lib.text_read", params=["a"], signature="(a)"),
        entry("lib.CONST", kind="attribute", known=False),
        entry("lib.sub", kind="module", known=False),
        entry("lib.mod_to_attr", kind="attribute", known=False),
    ]
    old[1]["callable"] = new[1]["callable"] = True          # a callable object, signature never read
    old[2]["signature_source"] = "text"
    diff = build_diff("lib", "1.0", "2.0", old, new, set())
    assert bucket_of(diff, "lib.attr_to_func") == "shared_unknown"     # kind mismatch
    assert bucket_of(diff, "lib.both_unread") == "shared_unknown"      # callable, never read
    assert bucket_of(diff, "lib.text_read") == "shared_same"           # read (text on one side) and equal
    assert diff["shared_same"]["lib.text_read"]["signature_source"] == "inspect"
    assert bucket_of(diff, "lib.CONST") == "shared_same"               # non-callables of one kind
    assert bucket_of(diff, "lib.sub") == "shared_same"
    assert bucket_of(diff, "lib.mod_to_attr") == "shared_unknown"


def test_one_sided_param_of_an_owner_unread_elsewhere_is_unknown():
    old = [entry("lib.ufunc", kind="attribute", known=False),            # signature not read on the old side
           entry("lib.read", params=["a"], signature="(a)"),
           entry("lib.morph", kind="attribute", params=["x"], signature="(x)"),
           entry("lib.morph(x)", kind="param", owner="lib.morph")]
    new = [entry("lib.ufunc", kind="attribute", params=["x", "out"], signature="(x, out=None)"),
           entry("lib.ufunc(x)", kind="param", owner="lib.ufunc"),
           entry("lib.ufunc(out)", kind="param", owner="lib.ufunc", default="None"),
           entry("lib.read", params=["a", "b"], signature="(a, b=1)"),
           entry("lib.read(b)", kind="param", owner="lib.read", default="1"),
           entry("lib.morph", kind="function", params=[], signature="()")]
    old[0]["callable"] = new[0]["callable"] = True
    diff = build_diff("lib", "1.0", "2.0", old, new, set())
    assert bucket_of(diff, "lib.ufunc") == "shared_unknown"
    assert bucket_of(diff, "lib.ufunc(out)") == "shared_unknown"            # absence on old is not evidence
    assert diff["shared_unknown"]["lib.ufunc(out)"]["owner_unread_on"] == "old"
    assert bucket_of(diff, "lib.read(b)") == "new_only"                     # owner read on both: a real addition
    assert bucket_of(diff, "lib.morph(x)") == "shared_unknown"              # owner changed kind
