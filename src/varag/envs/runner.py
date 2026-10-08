"""Run stdlib-only scripts inside a library environment.

The orchestrator never imports pandas, NumPy or pydantic. Everything that needs them
is a script under ``scripts/`` started here as a subprocess with that environment's
interpreter, in a stripped environment, exchanging JSON.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from varag.config import project_root

WINDOWS = sys.platform.startswith("win")


class ScriptError(RuntimeError):
    """A script inside a library environment failed or printed no JSON."""


def uv_binary() -> str:
    found = shutil.which("uv")
    if found:
        return found
    candidate = Path.home() / ".local" / "bin" / ("uv.exe" if WINDOWS else "uv")
    if candidate.exists():
        return str(candidate)
    raise RuntimeError("uv not found on PATH or in ~/.local/bin")


def envs_root() -> Path:
    return project_root() / "envs"


def env_dir(name: str) -> Path:
    return envs_root() / name


def env_python(name: str) -> Path:
    venv = env_dir(name) / ".venv"
    return venv / "Scripts" / "python.exe" if WINDOWS else venv / "bin" / "python"


def scripts_dir() -> Path:
    return project_root() / "scripts"


def stripped_env(python: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    """A minimal process environment: no PYTHONPATH, no user site, deterministic hashing."""
    env: dict[str, str] = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
    }
    path_parts = [str(python.parent)]
    if WINDOWS:
        for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "COMSPEC"):
            if key in os.environ:
                env[key] = os.environ[key]
        system32 = Path(os.environ.get("SYSTEMROOT", r"C:\Windows")) / "System32"
        path_parts.append(str(system32))
    else:
        for key in ("TMPDIR", "LANG", "LC_ALL"):
            if key in os.environ:
                env[key] = os.environ[key]
        path_parts += ["/usr/local/bin", "/usr/bin", "/bin"]
    env["PATH"] = os.pathsep.join(path_parts)
    if extra:
        env.update(extra)
    return env


def run_script(
    name: str,
    script: str,
    args: tuple[str, ...] | list[str] = (),
    stdin_text: str | None = None,
    timeout: int = 300,
) -> dict:
    """Run ``scripts/<script>`` under environment ``name`` and parse its JSON stdout."""
    python = env_python(name)
    if not python.exists():
        raise ScriptError(f"environment {name} has no interpreter at {python}; run `varag env build`")
    cmd = [str(python), "-I", str(scripts_dir() / script), *args]
    proc = subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=stripped_env(python),
        cwd=str(env_dir(name)),
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise ScriptError(f"{script} failed in {name} (exit {proc.returncode}):\n{proc.stderr[-4000:]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ScriptError(f"{script} in {name} printed no JSON: {proc.stdout[-2000:]}") from exc


def run_uv(args: list[str], cwd: Path | None = None, timeout: int = 1800) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        [uv_binary(), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd) if cwd else None,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"uv {' '.join(args)} failed (exit {proc.returncode}):\n{proc.stderr[-4000:]}")
    return proc
