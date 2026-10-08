from varag.inventory.audit import Rule, audit_library
from varag.inventory.diff import BUCKETS, bucket_of, build_diff
from varag.inventory.rules import parse_npy201


def entry(symbol, kind="function", owner=None, params=None, signature=None, known=True, deprecated=False, default=None, deprecated_by=None):
    owner = owner or symbol.rpartition(".")[0]
    name = symbol.rpartition(".")[2].split("(")[0]
    e = {"symbol": symbol, "kind": kind, "owner": owner, "name": name, "params": params or [],
         "signature": signature, "signature_known": known, "deprecated": deprecated,
         "deprecated_by": deprecated_by or (["docstring"] if deprecated else []), "accepts_var_kwargs": False}
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
]
NEW = [
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
    assert diff["deprecated_in_new"]["lib.ruled"].get("deprecated_by", []) == []
    assert diff["shared_changed"]["lib.changed"]["old"]["params"] == ["a"]
    assert sum(diff["counts"].values()) == len({e["symbol"] for e in OLD + NEW})
    assert set(diff["counts"]) == set(BUCKETS)


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
    ]
    result = audit_library("lib", diff, rules)
    assert result.applicable == 5 and result.hits == 3 and result.skipped == 1
    assert {m["symbol"] for m in result.misses} == {"lib.same", "lib.missing"}
    assert result.deprecated_rule_only == ["lib.ruled"]
    assert abs(result.recall - 0.6) < 1e-9


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
