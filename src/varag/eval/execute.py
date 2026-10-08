"""Two-environment execution harness (handoff, "Execution harness, outcomes and metrics").

Per call: a temp directory with solution.py, the concept's test file and the injected
conftest.py; ``{env_python} -m pytest -q -x -p no:cacheprovider`` under a timeout, a
stripped environment and, on POSIX, an address-space limit and no network. Generated code
is untrusted and never runs in the orchestrator process.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path

from varag.config import load_experiment, project_root
from varag.envs.build import read_manifest
from varag.envs.runner import env_python, stripped_env

STATUSES = ("pass", "fail", "error", "timeout", "infra_error")
POSIX = os.name == "posix"


@dataclass
class ExecResult:
    env: str
    status: str
    exit_code: int | None = None
    exc_type: str | None = None
    last_line: str | None = None
    stamp_version: str | None = None
    warning_counts: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    duration_s: float = 0.0
    output_tail: str = ""
    infra_reason: str | None = None
    collected: int = 0

    @property
    def passed(self) -> bool:
        return self.status == "pass"

    @property
    def failed_by_code(self) -> bool:
        """A failure the solution caused: test failure or exception, not timeout or infrastructure."""
        return self.status in ("fail", "error")

    @property
    def deprecation_warnings(self) -> int:
        return int(self.warning_counts.get("DeprecationWarning", 0)) + int(self.warning_counts.get("FutureWarning", 0))

    @property
    def soft_fail(self) -> bool:
        return self.passed and self.deprecation_warnings > 0

    def to_dict(self) -> dict:
        return asdict(self)


def conftest_source() -> str:
    return (project_root() / "scripts" / "conftest_template.py").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _unshare_prefix() -> list[str]:
    """``unshare -n`` when the OS allows it (Linux, with the needed privileges)."""
    if not sys.platform.startswith("linux"):
        return []
    exe = shutil.which("unshare")
    if not exe:
        return []
    try:
        ok = subprocess.run([exe, "-n", "true"], capture_output=True, timeout=10).returncode == 0
    except (OSError, subprocess.SubprocessError):
        ok = False
    return [exe, "-n"] if ok else []


def _preexec(memory_mb: int):
    if not POSIX:
        return None
    import resource

    limit = memory_mb * 1024 * 1024

    def set_limits():
        try:
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        except (ValueError, OSError):
            pass

    return set_limits


def _status_from(exit_code: int, record: dict | None) -> tuple[str, str | None]:
    if record is None:
        return "infra_error", "no result record written"
    if record.get("status") == "infra_error":
        return "infra_error", record.get("infra_reason")
    failures = record.get("failures", [])
    if exit_code == 0:
        if record.get("collected", 0) == 0:
            return "infra_error", "no tests collected"
        return "pass", None
    if exit_code == 1 or (exit_code == 2 and failures):
        if any(f.get("exc_type") != "AssertionError" for f in failures):
            return "error", None
        return "fail", None
    return "infra_error", f"pytest exit code {exit_code}"


def execute(
    env_name: str,
    solution_code: str,
    test_path: Path,
    warnings_as_errors: bool = False,
    timeout_s: int | None = None,
) -> ExecResult:
    manifest = read_manifest()[env_name]
    python = env_python(env_name)
    settings = load_experiment().get("execution", {})
    timeout_s = timeout_s or int(settings.get("timeout_s", 60))
    memory_mb = int(settings.get("memory_mb", 2048))

    with tempfile.TemporaryDirectory(prefix="varag-") as tmp:
        workdir = Path(tmp)
        (workdir / "solution.py").write_text(solution_code, encoding="utf-8")
        shutil.copyfile(test_path, workdir / "test_solution.py")
        (workdir / "conftest.py").write_text(conftest_source(), encoding="utf-8")
        result_path = workdir / "result.json"

        cmd = [*_unshare_prefix(), str(python), "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "--tb=short"]
        if warnings_as_errors:
            cmd += ["-W", "error::DeprecationWarning:solution", "-W", "error::FutureWarning:solution"]
        cmd.append("test_solution.py")
        env = stripped_env(python, {
            "VARAG_LIBRARY": manifest["module"],
            "VARAG_EXPECT_VERSION": manifest["library_version"],
            "VARAG_RESULT_PATH": str(result_path),
            "TEMP": str(workdir),
            "TMP": str(workdir),
            "TMPDIR": str(workdir),
        })

        started = time.monotonic()
        try:
            proc = subprocess.run(
                cmd, cwd=str(workdir), env=env, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=timeout_s, preexec_fn=_preexec(memory_mb),
            )
            exit_code: int | None = proc.returncode
            output = (proc.stdout or "") + (proc.stderr or "")
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            exit_code = None
            output = ((exc.stdout or b"") if isinstance(exc.stdout, (bytes, bytearray)) else (exc.stdout or "")).__str__()
            timed_out = True
        duration = time.monotonic() - started

        record = None
        if result_path.exists():
            try:
                record = json.loads(result_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                record = None

    tail = output[-3000:] if isinstance(output, str) else ""
    if timed_out:
        return ExecResult(env_name, "timeout", None, None, None, duration_s=duration, output_tail=tail,
                          infra_reason=None, stamp_version=(record or {}).get("stamp_version"))

    status, reason = _status_from(exit_code, record)
    record = record or {}
    failures = record.get("failures", [])
    first = failures[0] if failures else None
    return ExecResult(
        env=env_name,
        status=status,
        exit_code=exit_code,
        exc_type=first["exc_type"] if first else None,
        last_line=f"{first['exc_type']}: {first['message']}" if first else None,
        stamp_version=record.get("stamp_version"),
        warning_counts=record.get("warning_counts", {}),
        warnings=record.get("warnings", []),
        duration_s=duration,
        output_tail=tail,
        infra_reason=reason,
        collected=int(record.get("collected", 0)),
    )
