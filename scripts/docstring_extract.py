"""Read installed docstrings for a list of symbols. Stdlib only; runs inside envs/<name>/.venv.

usage: python docstring_extract.py <output.json>  < spec.json

stdin: {"roots": [{"import": "pkg.mod[:attr]", "public": "pkg.Public"}], "symbols": ["pkg.Public.name", ...]}
output file: {symbol: {"summary_region", "examples", "doc_sha256"} | {"error": ...}}

Symbols are resolved through the same roots as the inventory, so `pandas.DatetimeProperties.week`
is read from the class that defines it. The summary region is the docstring before its first
numpydoc section header; `examples` is the body of the Examples section (empty when absent).
"""

import hashlib
import importlib
import inspect
import json
import re
import sys
import warnings

SECTION = re.compile(r"^([A-Z][A-Za-z ]{2,30})\n-{3,}\s*$", re.M)


def import_target(spec):
    mod_name, _, attr = spec.partition(":")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            obj = importlib.import_module(mod_name)
        except ImportError:
            parts = mod_name.split(".")
            obj = importlib.import_module(parts[0])
            for part in parts[1:]:
                obj = getattr(obj, part)
        if attr:
            obj = getattr(obj, attr)
    return obj


def split_docstring(doc):
    """Returns (summary_region, examples_section_body)."""
    headers = list(SECTION.finditer(doc))
    summary = doc[: headers[0].start()] if headers else doc
    examples = ""
    for i, m in enumerate(headers):
        if m.group(1).strip() == "Examples":
            end = headers[i + 1].start() if i + 1 < len(headers) else len(doc)
            examples = doc[m.end():end]
            break
    return summary.strip(), examples.strip("\n")


def main():
    out_path = sys.argv[1]
    spec = json.loads(sys.stdin.read())
    roots = {}
    for root in spec["roots"]:
        try:
            roots[root["public"]] = import_target(root["import"])
        except Exception:  # noqa: BLE001
            continue
    ordered = sorted(roots, key=len, reverse=True)
    out = {}
    for symbol in spec["symbols"]:
        owner = next((p for p in ordered if symbol.startswith(p + ".")), None)
        if owner is None:
            out[symbol] = {"error": "no root"}
            continue
        obj = roots[owner]
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for name in symbol[len(owner) + 1:].split("."):
                    static = inspect.getattr_static(obj, name, None)
                    member = getattr(obj, name)
                    obj = member
            doc = inspect.getdoc(member) or (inspect.getdoc(static) if static is not None else "") or ""
        except Exception as exc:  # noqa: BLE001
            out[symbol] = {"error": f"{type(exc).__name__}: {exc}"[:200]}
            continue
        summary, examples = split_docstring(doc)
        out[symbol] = {
            "summary_region": summary[:4000],
            "examples": examples[:8000],
            "doc_sha256": hashlib.sha256(doc.encode("utf-8")).hexdigest(),
        }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh)
    json.dump({"symbols": len(out), "errors": sum(1 for v in out.values() if "error" in v)}, sys.stdout)


if __name__ == "__main__":
    main()
