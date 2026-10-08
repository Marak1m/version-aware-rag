"""Probe a library environment. Stdlib only; runs inside envs/<name>/.venv.

usage: python probe_env.py <module>  < canaries.json

stdin holds a JSON list of dotted symbol paths to probe (may be empty).
stdout gets one JSON object: interpreter, python version, platform, the library's
__version__, every installed distribution, import-time warnings, and per-canary
presence. Presence is decided by importing the longest importable module prefix and
walking getattr; any exception on the way (including NumPy 2's module __getattr__ for
expired names) reads as absent.
"""

import importlib
import importlib.metadata
import json
import platform
import sys
import warnings


def resolve(path):
    parts = path.split(".")
    obj = None
    i = len(parts)
    while i > 0:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                obj = importlib.import_module(".".join(parts[:i]))
            break
        except Exception:
            i -= 1
    if obj is None:
        return {"present": False, "detail": "no importable prefix"}
    for name in parts[i:]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                obj = getattr(obj, name)
        except Exception as exc:  # noqa: BLE001 - any failure means absent
            return {"present": False, "detail": f"{type(exc).__name__}: {exc}"[:300]}
    return {"present": True, "detail": type(obj).__name__}


def main():
    module_name = sys.argv[1]
    raw = sys.stdin.read().strip()
    canaries = json.loads(raw) if raw else []

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        lib = importlib.import_module(module_name)
    import_warnings = [f"{w.category.__name__}: {w.message}"[:300] for w in caught]

    distributions = {}
    for dist in importlib.metadata.distributions():
        name = (dist.metadata["Name"] or "").lower()
        if name:
            distributions[name] = dist.version

    out = {
        "module": module_name,
        "library_version": str(getattr(lib, "__version__", "")),
        "interpreter": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "distributions": dict(sorted(distributions.items())),
        "import_warnings": import_warnings,
        "canaries": {path: resolve(path) for path in canaries},
    }
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
