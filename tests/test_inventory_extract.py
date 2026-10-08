"""Each known extraction pitfall (handoff L2) has a test here, on synthetic modules."""

import importlib.util
import re
import sys
import types
import warnings

import pytest

from varag.config import project_root


@pytest.fixture(scope="module")
def ext():
    path = project_root() / "scripts" / "inventory_extract.py"
    spec = importlib.util.spec_from_file_location("inventory_extract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_module(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


def by_symbol(entries):
    return {e["symbol"]: e for e in entries}


def test_symbol_keyed_by_public_path_not_module(ext):
    def func(x):
        return x

    func.__module__ = "fl_a._internal"
    make_module("fl_a", func=func, __all__=["func"])
    entries, _ = ext.extract({"library": "fl_a", "version": "1", "roots": [{"import": "fl_a", "public": "fl_a"}]})
    assert "fl_a.func" in by_symbol(entries)
    assert by_symbol(entries)["fl_a.func"]["owner"] == "fl_a"
    assert not any(s.startswith("fl_a._internal") for s in by_symbol(entries))


def test_lazy_submodule_is_imported_explicitly(ext):
    make_module("fl_b", __all__=["visible"], visible=lambda: None)
    make_module("fl_b.lazy", f=lambda a, b=1: None)
    roots = [{"import": "fl_b", "public": "fl_b"}, {"import": "fl_b.lazy", "public": "fl_b.lazy"}]
    entries, diag = ext.extract({"library": "fl_b", "version": "1", "roots": roots})
    symbols = by_symbol(entries)
    assert "fl_b.lazy.f" in symbols and "fl_b.lazy.f(b)" in symbols
    assert "fl_b.visible" in symbols
    assert diag["roots_failed"] == {}


def test_unimported_subpackage_is_listed_and_imported(ext, tmp_path):
    pkg = tmp_path / "fl_h"
    (pkg / "v1").mkdir(parents=True)
    (pkg / "__init__.py").write_text("__all__ = ['top']\ntop = 1\n", encoding="utf-8")
    (pkg / "v1" / "__init__.py").write_text("legacy = 2\n", encoding="utf-8")
    sys.path.insert(0, str(tmp_path))
    try:
        entries, _ = ext.extract({"library": "fl_h", "version": "2", "roots": [{"import": "fl_h", "public": "fl_h"}]})
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("fl_h", None)
        sys.modules.pop("fl_h.v1", None)
    symbols = by_symbol(entries)
    assert symbols["fl_h.v1"]["kind"] == "module" and symbols["fl_h.v1"]["in_all"] is False
    assert symbols["fl_h.top"]["in_all"] is True


def test_defaults_with_memory_addresses_are_stable(ext):
    class Sentinel:
        pass

    marker = Sentinel()

    def f(a, call=marker):
        pass

    make_module("fl_j", f=f)
    entries, _ = ext.extract({"library": "fl_j", "version": "1", "roots": [{"import": "fl_j", "public": "fl_j"}]})
    symbols = by_symbol(entries)
    raw = repr(marker)
    assert re.search(r" at 0x[0-9A-Fa-f]+>", raw)                       # the raw repr carries an address
    masked_expected = re.sub(r"(?<= at 0x)[0-9A-Fa-f]+", "...", raw)   # only the hex digits change
    assert symbols["fl_j.f(call)"]["default"] == masked_expected
    assert "Sentinel" in symbols["fl_j.f(call)"]["default"]             # the type name is kept
    assert masked_expected in symbols["fl_j.f"]["signature"]
    assert ext.stable_repr(marker) == masked_expected


def test_rule_seeded_names_are_tagged(ext):
    module = make_module("fl_i", __all__=["seen"], seen=lambda: None)
    hidden = lambda a, b=1: None  # noqa: E731
    module.__getattr__ = lambda name: hidden if name == "hidden" else (_ for _ in ()).throw(AttributeError(name))
    module.__dir__ = lambda: ["seen"]
    roots = [{"import": "fl_i", "public": "fl_i", "extra_names": ["hidden", "absent"]}]
    entries, diag = ext.extract({"library": "fl_i", "version": "1", "roots": roots})
    symbols = by_symbol(entries)
    assert symbols["fl_i.seen"]["found_by"] == "walk"
    assert symbols["fl_i.hidden"]["found_by"] == "rule_seed"
    assert symbols["fl_i.hidden(b)"]["found_by"] == "rule_seed"
    assert "fl_i.absent" not in symbols and "absent" in diag["roots"][0]["errors"]
    assert diag["roots"][0]["rule_seeded"] == ["hidden"]


def test_expired_attribute_raising_on_access_is_skipped(ext):
    module = make_module("fl_c", ok=lambda: None)

    def __getattr__(name):
        if name == "expired":
            raise AttributeError("`fl_c.expired` was removed in the fl_c 2.0 release.")
        raise AttributeError(name)

    module.__getattr__ = __getattr__
    module.__dir__ = lambda: ["ok", "expired"]
    entries, diag = ext.extract({"library": "fl_c", "version": "2", "roots": [{"import": "fl_c", "public": "fl_c"}]})
    symbols = by_symbol(entries)
    assert "fl_c.ok" in symbols and "fl_c.expired" not in symbols
    assert "expired" in diag["roots"][0]["errors"]


def test_unknown_signatures_are_never_treated_as_known(ext):
    def var_only(*args, **kwargs):
        pass

    def normal(a, b=2):
        pass

    make_module("fl_d", __all__=["mx", "var_only", "normal"], mx=max, var_only=var_only, normal=normal)
    entries, _ = ext.extract({"library": "fl_d", "version": "1", "roots": [{"import": "fl_d", "public": "fl_d"}]})
    symbols = by_symbol(entries)
    assert symbols["fl_d.mx"]["kind"] == "function"
    assert symbols["fl_d.mx"]["signature_known"] is False  # inspect.signature(max) raises ValueError
    assert symbols["fl_d.var_only"]["signature_known"] is False
    assert symbols["fl_d.var_only"]["accepts_var_kwargs"] is True
    assert symbols["fl_d.normal"]["signature_known"] is True
    assert symbols["fl_d.normal"]["params"] == ["a", "b"]


def test_every_deprecation_route_is_detected(ext):
    def by_attr():
        pass

    by_attr.__deprecated__ = "use by_attr2"

    def by_doc():
        """Old thing.

        .. deprecated:: 1.4.0
            Use new_thing instead.
        """

    def plain():
        """Mentions nothing."""

    def warned():
        pass

    module = make_module("fl_e", by_attr=by_attr, by_doc=by_doc, plain=plain)

    def __getattr__(name):
        if name == "warned":
            warnings.warn("fl_e.warned is deprecated", DeprecationWarning, stacklevel=2)
            return warned
        raise AttributeError(name)

    module.__getattr__ = __getattr__
    module.__dir__ = lambda: ["by_attr", "by_doc", "plain", "warned"]
    entries, _ = ext.extract({"library": "fl_e", "version": "1", "roots": [{"import": "fl_e", "public": "fl_e"}]})
    symbols = by_symbol(entries)
    assert symbols["fl_e.by_attr"]["deprecated_by"] == ["__deprecated__"]
    assert symbols["fl_e.by_doc"]["deprecated_by"] == ["docstring"]
    assert symbols["fl_e.warned"]["deprecated_by"] == ["warning_on_access"]
    assert symbols["fl_e.plain"]["deprecated"] is False


def test_class_methods_drop_self_and_emit_param_entries(ext):
    class Frame:
        def append(self, other, ignore_index=False, sort=False):
            """Append rows."""

        @property
        def shape(self):
            return (0, 0)

        @classmethod
        def from_dict(cls, data, orient="columns"):
            return cls()

        columns = ()

    make_module("fl_f", Frame=Frame)
    entries, _ = ext.extract({"library": "fl_f", "version": "1", "roots": [{"import": "fl_f:Frame", "public": "fl_f.Frame"}]})
    symbols = by_symbol(entries)
    assert symbols["fl_f.Frame.append"]["kind"] == "method"
    assert symbols["fl_f.Frame.append"]["params"] == ["other", "ignore_index", "sort"]
    assert symbols["fl_f.Frame.append"]["signature"].startswith("(self, other")
    param = symbols["fl_f.Frame.append(ignore_index)"]
    assert param["kind"] == "param" and param["owner"] == "fl_f.Frame.append" and param["default"] == "False"
    assert symbols["fl_f.Frame.shape"]["kind"] == "attribute"
    assert symbols["fl_f.Frame.from_dict"]["params"] == ["data", "orient"]
    assert symbols["fl_f.Frame.columns"]["kind"] == "attribute"


def test_config_keys_from_attributes_and_annotations(ext):
    class BaseConfig:
        orm_mode = False
        extra = "ignore"

        @classmethod
        def helper(cls):
            pass

    class ConfigDict(dict):
        __annotations__ = {"from_attributes": bool, "extra": str}

    make_module("fl_g", BaseConfig=BaseConfig, ConfigDict=ConfigDict)
    old, _ = ext.extract({"library": "fl_g", "version": "1", "roots": [],
                          "config_keys": {"public": "fl_g.config", "import": "fl_g:BaseConfig", "mode": "attributes"}})
    new, _ = ext.extract({"library": "fl_g", "version": "2", "roots": [],
                          "config_keys": {"public": "fl_g.config", "import": "fl_g:ConfigDict", "mode": "annotations"}})
    assert set(by_symbol(old)) == {"fl_g.config.orm_mode", "fl_g.config.extra"}
    assert set(by_symbol(new)) == {"fl_g.config.from_attributes", "fl_g.config.extra"}
    assert by_symbol(old)["fl_g.config.orm_mode"]["kind"] == "config_key"
