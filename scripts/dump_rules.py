"""Dump the migration rule tables a library ships with. Stdlib only; runs in the *new* environment.

usage: python dump_rules.py numpy|pydantic  -> JSON on stdout

numpy:    numpy._expired_attrs_2_0.__expired_attributes__  (name -> message)
pydantic: pydantic._migration MOVED_IN_V2, DEPRECATED_MOVED_IN_V2, REDIRECT_TO_V1, REMOVED_IN_V2,
          plus how each name behaves when accessed on this version (served_behaviour), and the
          V1 keywords that Field() pops from **extra, classified by executing Field(kw=...).
"""

import importlib
import inspect
import json
import re
import sys
import warnings


def dump_numpy():
    mod = importlib.import_module("numpy._expired_attrs_2_0")
    table = getattr(mod, "__expired_attributes__", {})
    return {"expired_attributes": {str(k): str(v) for k, v in table.items()}}


def served_behaviour(tables):
    """How each migration-table name behaves on the installed version: resolves (with which
    warning categories) or raises (which exception)."""
    out = {}
    for table, value in tables.items():
        keys = value.keys() if isinstance(value, dict) else value
        for key in sorted(keys):
            mod_name, _, attr = key.partition(":")
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    mod = importlib.import_module(mod_name)
            except Exception as exc:  # noqa: BLE001
                out[key] = {"table": table, "outcome": "module_missing", "type": type(exc).__name__}
                continue
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    getattr(mod, attr)
                except Exception as exc:  # noqa: BLE001
                    out[key] = {"table": table, "outcome": "raises", "type": type(exc).__name__, "message": str(exc).splitlines()[0][:200]}
                    continue
            out[key] = {"table": table, "outcome": "resolves", "warnings": sorted({w.category.__name__ for w in caught})}
    return out


def field_v1_kwargs():
    """V1 keywords Field() pops from **extra, classified by execution: removed (raises) or
    deprecated (accepted with a warning). Messages are the library's own text."""
    from pydantic import Field

    source = inspect.getsource(Field)
    names = re.findall(r"extra\.pop\(\s*['\"](\w+)['\"]", source)
    params = list(inspect.signature(Field).parameters)
    keywords = {}
    for name in names:
        value = "x" if name == "regex" else 1
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                Field(**{name: value})
            except Exception as exc:  # noqa: BLE001
                keywords[name] = {
                    "handling": "removed",
                    "exception": type(exc).__name__,
                    "code": getattr(exc, "code", None),
                    "message": str(exc).splitlines()[0][:300],
                }
                continue
        own = [w for w in caught if f"`{name}`" in str(w.message)] or list(caught)
        first = own[0] if own else None
        keywords[name] = {
            "handling": "deprecated",
            "warning": first.category.__name__ if first else None,
            "message": str(first.message).split(". Deprecated in")[0][:300] if first else "",
        }
    return {
        "source": "pydantic.fields.Field: V1 keywords popped from **extra, classified by executing Field(kw=...)",
        "field_params": params,
        "keywords": keywords,
    }


def dump_pydantic():
    mod = importlib.import_module("pydantic._migration")
    tables = {}
    for name in ("MOVED_IN_V2", "DEPRECATED_MOVED_IN_V2", "REDIRECT_TO_V1", "REMOVED_IN_V2"):
        value = getattr(mod, name, None)
        if value is None:
            continue
        tables[name] = {str(k): str(v) for k, v in value.items()} if isinstance(value, dict) else sorted(str(v) for v in value)
    out = dict(tables)
    out["served_behaviour"] = served_behaviour(tables)
    out["field_v1_kwargs"] = field_v1_kwargs()
    return out


def main():
    library = sys.argv[1]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lib = importlib.import_module(library)
        data = dump_numpy() if library == "numpy" else dump_pydantic()
    data["library"] = library
    data["version"] = str(getattr(lib, "__version__", ""))
    json.dump(data, sys.stdout)


if __name__ == "__main__":
    main()
