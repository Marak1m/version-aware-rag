"""``varag env build``: six environments from hash-pinned locks, plus envs/manifest.json.

Checks 1 and 2 of the handoff's verification table live here: the lock file carries
hashes and its sha256 is stored, and the manifest records what the probe saw.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from varag.config import env_names, env_spec, load_canaries, load_libraries, sha256_file
from varag.envs.runner import env_dir, env_python, envs_root, run_script, run_uv


def manifest_path() -> Path:
    return envs_root() / "manifest.json"


def read_manifest() -> dict:
    path = manifest_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(manifest: dict) -> None:
    manifest_path().write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def requirements_in(spec: dict) -> str:
    lines = [f"{spec['library']}=={spec['version']}", *spec["extra_pins"], "pytest"]
    return "\n".join(lines) + "\n"


def canary_paths(library: str, side: str) -> list[str]:
    entry = load_canaries().get(library, {}).get(side, {})
    return list(entry.get("present", [])) + list(entry.get("absent", []))


def probe(name: str) -> dict:
    spec = env_spec(name)
    return run_script(
        name,
        "probe_env.py",
        [spec["module"]],
        stdin_text=json.dumps(canary_paths(spec["library"], spec["side"])),
    )


def build_env(name: str, relock: bool = False, log: Callable[[str], None] = print) -> dict:
    spec = env_spec(name)
    python_version = str(load_libraries()["python"])
    directory = env_dir(name)
    directory.mkdir(parents=True, exist_ok=True)

    req_in = directory / "requirements.in"
    req_in.write_text(requirements_in(spec), encoding="utf-8")

    lock = directory / "requirements.lock"
    if relock or not lock.exists():
        log(f"[{name}] compiling {lock.name}")
        run_uv(
            [
                "pip", "compile", str(req_in), "-o", str(lock),
                "--generate-hashes", "--python-version", python_version,
                "--python", python_version, "--no-header", "--quiet",
            ],
            cwd=directory,
        )

    venv = directory / ".venv"
    if venv.exists():
        shutil.rmtree(venv)
    log(f"[{name}] creating venv (python {python_version})")
    run_uv(["venv", str(venv), "--python", python_version, "--quiet"], cwd=directory)
    log(f"[{name}] syncing from {lock.name}")
    run_uv(["pip", "sync", str(lock), "--python", str(env_python(name)), "--quiet"], cwd=directory)

    log(f"[{name}] probing")
    probed = probe(name)
    entry = {
        "library": spec["library"],
        "side": spec["side"],
        "module": spec["module"],
        "expected_version": spec["version"],
        "library_version": probed["library_version"],
        "interpreter": probed["interpreter"],
        "python_version": probed["python_version"],
        "platform": probed["platform"],
        "distributions": probed["distributions"],
        "import_warnings": probed["import_warnings"],
        "canaries": {path: value["present"] for path, value in probed["canaries"].items()},
        "lock_sha256": sha256_file(lock),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    log(f"[{name}] {spec['module']} {entry['library_version']} on Python {entry['python_version']}")
    for warning in entry["import_warnings"]:
        log(f"[{name}] import warning: {warning}")
    return entry


def build_all(only: str | None = None, relock: bool = False, log: Callable[[str], None] = print) -> dict:
    names = [only] if only else env_names()
    manifest = read_manifest()
    for name in names:
        manifest[name] = build_env(name, relock=relock, log=log)
        write_manifest(manifest)
    return manifest
