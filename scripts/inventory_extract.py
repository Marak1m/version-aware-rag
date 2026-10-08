"""Extract the public API inventory of one library. Stdlib only; runs inside envs/<name>/.venv.

usage: python inventory_extract.py <output.jsonl>  < spec.json

stdin: {"library", "version", "roots": [{"import": "pkg.mod[:attr]", "public": "pkg.Public"}],
        "config_keys": {"public": "...", "import": "...", "mode": "attributes|annotations"}}  (optional)
stdout: a JSON diagnostics object. The inventory itself goes to the output path, one JSON
object per line, sorted by symbol.

Pitfalls this handles (handoff L2):
- every symbol is keyed by its public access path, never by __module__;
- each root is imported explicitly, so lazily loaded submodules (NumPy's linalg, fft, ...)
  are reachable even when the parent's __dir__ hides them;
- every getattr is wrapped, with warnings captured, because NumPy 2 raises on expired names;
- inspect.signature failures and bare (*args, **kwargs) give signature_known: false;
- a symbol is deprecated when __deprecated__ is set, its docstring opens with a
  deprecation directive, or accessing it emits a deprecation warning. Rule-set listings are
  applied by the orchestrator's diff step.
"""

import hashlib
import importlib
import inspect
import json
import re
import sys
import warnings

DEPRECATION_WARNINGS = (DeprecationWarning, FutureWarning, PendingDeprecationWarning)
DEPRECATED_DIRECTIVE = re.compile(r"\.\.\s*deprecated::|^\s*deprecated\b", re.IGNORECASE | re.MULTILINE)
SELF_NAMES = {"self", "cls"}


def import_target(spec):
    """Resolve "pkg.mod" or "pkg.mod:attr". Falls back to attribute walking from the top package."""
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


def public_names(obj):
    if inspect.ismodule(obj) and isinstance(getattr(obj, "__all__", None), (list, tuple)):
        names = [n for n in obj.__all__ if isinstance(n, str)]
    else:
        try:
            names = dir(obj)
        except Exception:  # noqa: BLE001
            names = list(getattr(obj, "__dict__", {}).keys())
    return sorted({n for n in names if n and not n.startswith("_")})


def safe_getattr(obj, name):
    """Returns (ok, member, warned, error)."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            member = getattr(obj, name)
        except Exception as exc:  # noqa: BLE001 - NumPy 2 raises AttributeError on expired names
            return False, None, False, f"{type(exc).__name__}: {exc}"[:200]
    warned = any(issubclass(w.category, DEPRECATION_WARNINGS) for w in caught)
    return True, member, warned, None


def docstring_of(member, static=None):
    doc = None
    try:
        doc = inspect.getdoc(member)
    except Exception:  # noqa: BLE001
        doc = None
    if doc is None and static is not None:
        try:
            doc = inspect.getdoc(static)
        except Exception:  # noqa: BLE001
            doc = None
    return doc or ""


def has_deprecated_attr(*objects):
    for obj in objects:
        if obj is None:
            continue
        try:
            if getattr(obj, "__deprecated__", None):
                return True
        except Exception:  # noqa: BLE001
            pass
        fget = getattr(obj, "fget", None)
        if fget is not None and getattr(fget, "__deprecated__", None):
            return True
    return False


def signature_info(member):
    """Returns (signature_str, params, signature_known, accepts_var_kwargs)."""
    try:
        sig = inspect.signature(member)
    except (ValueError, TypeError):
        return None, [], False, False
    except Exception:  # noqa: BLE001
        return None, [], False, False
    params = []
    var_only = True
    accepts_var_kwargs = False
    for p in sig.parameters.values():
        if p.name in SELF_NAMES and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and not params:
            continue
        if p.kind == p.VAR_KEYWORD:
            accepts_var_kwargs = True
            continue
        if p.kind == p.VAR_POSITIONAL:
            continue
        var_only = False
        default = None if p.default is inspect.Parameter.empty else repr(p.default)[:120]
        params.append({"name": p.name, "kind": p.kind.name, "default": default})
    known = not (var_only and len(sig.parameters) > 0)
    return str(sig)[:2000], params, known, accepts_var_kwargs


def classify(member, static, root_is_class):
    if inspect.ismodule(member):
        return "module"
    if inspect.isclass(member):
        return "class"
    if root_is_class:
        if isinstance(static, property) or (inspect.isdatadescriptor(static) and not inspect.isroutine(member)):
            return "attribute"
        if inspect.isroutine(member) or isinstance(static, (classmethod, staticmethod)):
            return "method"
        return "attribute"
    if inspect.isroutine(member) or callable(member) and not inspect.isclass(member) and hasattr(member, "__call__") and inspect.isroutine(getattr(member, "__call__", None)) is False and inspect.isfunction(member):
        return "function"
    if inspect.isroutine(member):
        return "function"
    return "attribute"


def describe(member, static, name, public, library, version, root_is_class, warned):
    kind = classify(member, static, root_is_class)
    doc = docstring_of(member, static)
    deprecated_by = []
    if has_deprecated_attr(member, static):
        deprecated_by.append("__deprecated__")
    if DEPRECATED_DIRECTIVE.search(doc[:400]):
        deprecated_by.append("docstring")
    if warned:
        deprecated_by.append("warning_on_access")

    entry = {
        "symbol": f"{public}.{name}",
        "library": library,
        "version": version,
        "kind": kind,
        "owner": public,
        "name": name,
        "params": [],
        "signature": None,
        "signature_known": False,
        "accepts_var_kwargs": False,
        "deprecated": bool(deprecated_by),
        "deprecated_by": deprecated_by,
        "doc_sha256": hashlib.sha256(doc.encode("utf-8")).hexdigest(),
    }
    param_entries = []
    if kind in ("function", "method", "class"):
        target = member
        if kind == "method" and isinstance(static, (classmethod, staticmethod)):
            target = static.__func__
        sig, params, known, var_kwargs = signature_info(target)
        entry["signature"] = sig
        entry["params"] = [p["name"] for p in params]
        entry["signature_known"] = known
        entry["accepts_var_kwargs"] = var_kwargs
        for p in params:
            param_entries.append({
                "symbol": f"{public}.{name}({p['name']})",
                "library": library,
                "version": version,
                "kind": "param",
                "owner": f"{public}.{name}",
                "name": p["name"],
                "param_kind": p["kind"],
                "default": p["default"],
                "deprecated": False,
                "deprecated_by": [],
            })
    return [entry] + param_entries


def walk_root(root, public, library, version):
    """Inventory every public member of one root object (module or class)."""
    entries = []
    diagnostics = {"public": public, "members": 0, "errors": {}, "warned": []}
    root_is_class = inspect.isclass(root)
    for name in public_names(root):
        ok, member, warned, error = safe_getattr(root, name)
        if not ok:
            diagnostics["errors"][name] = error
            continue
        try:
            static = inspect.getattr_static(root, name)
        except Exception:  # noqa: BLE001
            static = None
        if warned:
            diagnostics["warned"].append(name)
        entries.extend(describe(member, static, name, public, library, version, root_is_class, warned))
        diagnostics["members"] += 1
    return entries, diagnostics


def config_key_entries(spec, library, version):
    obj = import_target(spec["import"])
    public = spec["public"]
    if spec.get("mode") == "annotations":
        names = list(getattr(obj, "__annotations__", {}).keys())
    else:
        names = [n for n in dir(obj) if not n.startswith("_") and not callable(getattr(obj, n, None))]
    return [
        {
            "symbol": f"{public}.{n}",
            "library": library,
            "version": version,
            "kind": "config_key",
            "owner": public,
            "name": n,
            "params": [],
            "signature": None,
            "signature_known": False,
            "accepts_var_kwargs": False,
            "deprecated": False,
            "deprecated_by": [],
            "doc_sha256": hashlib.sha256(b"").hexdigest(),
        }
        for n in sorted(set(names))
    ]


def extract(spec):
    library, version = spec["library"], spec["version"]
    entries = []
    diagnostics = {"library": library, "version": version, "roots_ok": [], "roots_failed": {}, "roots": []}
    for root_spec in spec["roots"]:
        try:
            root = import_target(root_spec["import"])
        except Exception as exc:  # noqa: BLE001
            diagnostics["roots_failed"][root_spec["import"]] = f"{type(exc).__name__}: {exc}"[:300]
            continue
        root_entries, diag = walk_root(root, root_spec["public"], library, version)
        entries.extend(root_entries)
        diagnostics["roots_ok"].append(root_spec["public"])
        diagnostics["roots"].append(diag)
    if spec.get("config_keys"):
        try:
            entries.extend(config_key_entries(spec["config_keys"], library, version))
        except Exception as exc:  # noqa: BLE001
            diagnostics["roots_failed"]["config_keys"] = f"{type(exc).__name__}: {exc}"[:300]
    seen = {}
    for e in entries:
        seen.setdefault(e["symbol"], e)
    entries = sorted(seen.values(), key=lambda e: e["symbol"])
    diagnostics["n_entries"] = len(entries)
    return entries, diagnostics


def main():
    out_path = sys.argv[1]
    spec = json.loads(sys.stdin.read())
    entries, diagnostics = extract(spec)
    with open(out_path, "w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e, sort_keys=True) + "\n")
    json.dump(diagnostics, sys.stdout)


if __name__ == "__main__":
    main()
