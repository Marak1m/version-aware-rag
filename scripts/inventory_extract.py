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
- a callable's signature comes from inspect.signature; when that fails or gives a bare
  (*args, **kwargs), from a text signature (__text_signature__, or a docstring first line that
  parses as one); otherwise signature_known is false. signature_source records which:
  inspect | text | none. Every entry records whether the object is callable;
- a symbol is deprecated when __deprecated__ is set, its docstring opens with a
  deprecation directive, or accessing it emits a deprecation warning. Rule-set listings are
  applied by the orchestrator's diff step.
"""

import ast
import hashlib
import importlib
import inspect
import json
import pkgutil
import re
import sys
import warnings

DEPRECATION_WARNINGS = (DeprecationWarning, FutureWarning, PendingDeprecationWarning)
DEPRECATED_DIRECTIVE = re.compile(r"\.\.\s*deprecated::|\A\s*deprecated\b", re.IGNORECASE)
SECTION_HEADER = re.compile(r"\n[A-Z][A-Za-z ]{2,30}\n-{3,}\n")
ADDRESS = re.compile(r" at 0x[0-9A-Fa-f]+")
SELF_NAMES = {"self", "cls"}
TEXT_SELF = re.compile(r"^\(\s*\$\w+\s*(?:,\s*)?")          # "($self, " / "($module, " in __text_signature__
LEADING_SLASH = re.compile(r"^\(\s*/\s*(?:,\s*)?")           # what is left of "($self, /, ...)"
DOC_SIGNATURE = re.compile(r"^([A-Za-z_][\w.]*)\(")


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


def public_names(obj, extra=()):
    """dir() plus __all__ plus rule-set names: NumPy's __dir__ and pydantic's migration
    __getattr__ both hide reachable members, so every candidate is probed by getattr."""
    try:
        names = set(dir(obj))
    except Exception:  # noqa: BLE001
        names = set(getattr(obj, "__dict__", {}).keys())
    exported = getattr(obj, "__all__", None)
    if isinstance(exported, (list, tuple)):
        names |= {n for n in exported if isinstance(n, str)}
    names |= set(extra)
    names |= submodule_names(obj)
    return sorted(n for n in names if n and not n.startswith("_"))


def submodule_names(obj):
    """A package's submodules are not attributes until imported (pydantic.v1, numpy.strings)."""
    path = getattr(obj, "__path__", None)
    if not inspect.ismodule(obj) or not path:
        return set()
    try:
        return {info.name for info in pkgutil.iter_modules(list(path))}
    except Exception:  # noqa: BLE001
        return set()


def in_all(obj, name):
    exported = getattr(obj, "__all__", None)
    return bool(isinstance(exported, (list, tuple)) and name in exported)


def safe_getattr(obj, name):
    """Returns (ok, member, warned, error)."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            member = getattr(obj, name)
        except Exception as exc:  # noqa: BLE001 - NumPy 2 raises AttributeError on expired names
            if inspect.ismodule(obj) and getattr(obj, "__path__", None):
                try:
                    member = importlib.import_module(f"{obj.__name__}.{name}")
                    return True, member, False, None
                except Exception:  # noqa: BLE001
                    pass
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


def summary_region(doc):
    """The docstring before its first section header: where a whole-object directive lives."""
    m = SECTION_HEADER.search(doc)
    return doc[: m.start()] if m else doc


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
        default = None if p.default is inspect.Parameter.empty else stable_repr(p.default)[:120]
        params.append({"name": p.name, "kind": p.kind.name, "default": default})
    known = not (var_only and len(sig.parameters) > 0)
    return ADDRESS.sub(" at 0x...", str(sig))[:2000], params, known, accepts_var_kwargs


def parse_signature_text(text):
    """(signature_str, params, signature_known, accepts_var_kwargs) from signature text such as
    "($module, a, /, b=1)" or "(a, axis=None) -> int"; None when it does not parse. Parsed only,
    never executed; defaults are kept as source text."""
    text = LEADING_SLASH.sub("(", TEXT_SELF.sub("(", text.strip(), count=1), count=1)
    try:
        tree = ast.parse(f"def _f{text}: pass")
    except (SyntaxError, ValueError):
        return None
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        return None
    args = tree.body[0].args
    positional = [(a, "POSITIONAL_ONLY") for a in args.posonlyargs] + [(a, "POSITIONAL_OR_KEYWORD") for a in args.args]
    defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
    params = []
    for (a, kind), d in zip(positional, defaults):
        if a.arg in SELF_NAMES and not params:
            continue
        params.append({"name": a.arg, "kind": kind, "default": None if d is None else ast.unparse(d)[:120]})
    for a, d in zip(args.kwonlyargs, args.kw_defaults):
        params.append({"name": a.arg, "kind": "KEYWORD_ONLY", "default": None if d is None else ast.unparse(d)[:120]})
    total = len(positional) + len(args.kwonlyargs) + bool(args.vararg) + bool(args.kwarg)
    known = not (not params and total > 0)
    return ADDRESS.sub(" at 0x...", text)[:2000], params, known, args.kwarg is not None


def text_signature(member, names, doc):
    """A signature from __text_signature__, else from a docstring first line naming the object."""
    try:
        text = getattr(member, "__text_signature__", None)
    except Exception:  # noqa: BLE001
        text = None
    candidates = [text] if isinstance(text, str) and text.startswith("(") else []
    first = next((line.strip() for line in doc.splitlines() if line.strip()), "")
    m = DOC_SIGNATURE.match(first)
    if m and m.group(1).rsplit(".", 1)[-1] in names:
        candidates.append(first[m.end() - 1:])
    for candidate in candidates:
        parsed = parse_signature_text(candidate)
        if parsed and parsed[2]:
            return parsed
    return None


def is_callable(member):
    try:
        return bool(callable(member))
    except Exception:  # noqa: BLE001
        return False


def stable_repr(value):
    """repr() with memory addresses masked, so inventories are byte-identical across builds."""
    try:
        text = repr(value)
    except Exception:  # noqa: BLE001
        text = f"<unrepresentable {type(value).__name__}>"
    return ADDRESS.sub(" at 0x...", text)


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
    if inspect.isroutine(member):
        return "function"
    return "attribute"


def describe(member, static, name, public, library, version, root_is_class, warned, exported=False, found_by="walk"):
    kind = classify(member, static, root_is_class)
    doc = docstring_of(member, static)
    deprecated_by = []
    if has_deprecated_attr(member, static):
        deprecated_by.append("__deprecated__")
    if DEPRECATED_DIRECTIVE.search(summary_region(doc)):
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
        "signature_source": "none",
        "callable": kind in ("function", "method", "class") or is_callable(member),
        "accepts_var_kwargs": False,
        "deprecated": bool(deprecated_by),
        "deprecated_by": deprecated_by,
        "in_all": exported,
        "found_by": found_by,
        "doc_sha256": hashlib.sha256(doc.encode("utf-8")).hexdigest(),
    }
    param_entries = []
    if entry["callable"]:
        target = member
        if kind == "method" and isinstance(static, (classmethod, staticmethod)):
            target = static.__func__
        sig, params, known, var_kwargs = signature_info(target)
        source = "inspect" if known else "none"
        if not known:
            names = {name, getattr(target, "__name__", None)}
            parsed = text_signature(target, names, doc)
            if parsed:
                sig, params, known, var_kwargs = parsed
                source = "text"
        entry["signature_source"] = source
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
                "found_by": found_by,
            })
    return [entry] + param_entries


def walk_root(root, public, library, version, extra_names=()):
    """Inventory every public member of one root object (module or class)."""
    entries = []
    diagnostics = {"public": public, "members": 0, "errors": {}, "warned": []}
    root_is_class = inspect.isclass(root)
    walked = set(public_names(root))          # dir() | __all__ | submodules, without rule-set seeds
    diagnostics["rule_seeded"] = []
    for name in public_names(root, extra_names):
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
        found_by = "walk" if name in walked else "rule_seed"
        if found_by == "rule_seed":
            diagnostics["rule_seeded"].append(name)
        entries.extend(describe(member, static, name, public, library, version, root_is_class, warned, in_all(root, name), found_by))
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
            "signature_source": "none",
            "callable": False,
            "accepts_var_kwargs": False,
            "deprecated": False,
            "deprecated_by": [],
            "in_all": False,
            "found_by": "walk",
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
        root_entries, diag = walk_root(root, root_spec["public"], library, version, root_spec.get("extra_names", ()))
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
