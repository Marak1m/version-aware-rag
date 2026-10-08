"""Dump the migration rule tables a library ships with. Stdlib only; runs in the *new* environment.

usage: python dump_rules.py numpy|pydantic  -> JSON on stdout

numpy:    numpy._expired_attrs_2_0.__expired_attributes__  (name -> message)
pydantic: pydantic._migration MOVED_IN_V2, DEPRECATED_MOVED_IN_V2, REDIRECT_TO_V1, REMOVED_IN_V2
"""

import importlib
import json
import sys
import warnings


def dump_numpy():
    mod = importlib.import_module("numpy._expired_attrs_2_0")
    table = getattr(mod, "__expired_attributes__", {})
    return {"expired_attributes": {str(k): str(v) for k, v in table.items()}}


def dump_pydantic():
    mod = importlib.import_module("pydantic._migration")
    out = {}
    for name in ("MOVED_IN_V2", "DEPRECATED_MOVED_IN_V2", "REDIRECT_TO_V1", "REMOVED_IN_V2"):
        value = getattr(mod, name, None)
        if value is None:
            continue
        if isinstance(value, dict):
            out[name] = {str(k): str(v) for k, v in value.items()}
        else:
            out[name] = sorted(str(v) for v in value)
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
