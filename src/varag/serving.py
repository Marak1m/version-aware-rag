"""Start and stop the model servers from configs/models.yaml (docs/GPU_HANDOFF.md).

``serve_command`` builds the exact vLLM command for a backend: the pinned repo and revision, the
served model name, the host and port from ``base_url``, the sampling seed, and the backend's
``serve_args`` (``--generation-config``, ``--max-model-len``, memory settings). Requests are logged
with their resolved sampling parameters (``--enable-log-requests``), so ``varag serve check`` can
read the *effective* repetition penalty from the server log, not only the value the client sends.

One server runs at a time: the GPU holds one model. Logs and pid files live in ``runs/_serve/``.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from varag.config import load_models, project_root
from varag.preflight import vllm_python


def serve_dir() -> Path:
    path = project_root() / "runs" / "_serve"
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_path(model: str) -> Path:
    return serve_dir() / f"{model}.log"


def pid_path(model: str) -> Path:
    return serve_dir() / f"{model}.pid"


def backend_spec(model: str) -> dict:
    spec = load_models()["backends"].get(model)
    if not spec or spec.get("type") != "openai_chat" or spec.get("server") != "vllm":
        raise KeyError(f"{model} is not a vLLM backend in configs/models.yaml")
    return spec


def serve_command(model: str) -> list[str]:
    spec = backend_spec(model)
    url = urlparse(spec["base_url"])
    vllm = vllm_python().parent / "vllm"
    return [str(vllm), "serve", spec["model"], "--revision", spec["revision"], "--tokenizer-revision", spec["revision"],
            "--served-model-name", spec.get("served_model_name") or model,
            "--host", url.hostname or "127.0.0.1", "--port", str(url.port or 8000),
            "--seed", str(load_models()["sampling"]["seed"]),
            "--enable-log-requests",
            *[str(a) for a in spec.get("serve_args", [])]]


def _ready(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/models", timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        return False


def running(model: str) -> int | None:
    path = pid_path(model)
    if not path.exists():
        return None
    pid = int(path.read_text().strip())
    try:
        os.kill(pid, 0)
    except OSError:
        path.unlink(missing_ok=True)
        return None
    return pid


def start(model: str, timeout_s: int = 1800, log=print) -> dict:
    """Start the server in the background and wait until ``/models`` answers. Returns the command,
    pid, log path and the seconds it took to become ready."""
    spec = backend_spec(model)
    for other in load_models()["backends"]:
        if other != model and load_models()["backends"][other].get("server") == "vllm" and running(other):
            raise RuntimeError(f"{other} is still being served; `varag serve stop --model {other}` first (one model at a time)")
    if running(model):
        raise RuntimeError(f"{model} is already being served (pid {running(model)})")
    command = serve_command(model)
    log("starting: " + " ".join(command))
    started = time.monotonic()
    with open(log_path(model), "w", encoding="utf-8") as fh:
        process = subprocess.Popen(command, stdout=fh, stderr=subprocess.STDOUT, start_new_session=True, env={**os.environ, "VLLM_LOGGING_LEVEL": "INFO"})
    pid_path(model).write_text(str(process.pid))
    while time.monotonic() - started < timeout_s:
        if process.poll() is not None:
            pid_path(model).unlink(missing_ok=True)
            tail = log_path(model).read_text(encoding="utf-8", errors="replace")[-3000:]
            raise RuntimeError(f"{model}: the server exited with {process.returncode}; log tail:\n{tail}")
        if _ready(spec["base_url"]):
            ready = round(time.monotonic() - started, 1)
            record = {"model": model, "pid": process.pid, "command": command, "log": str(log_path(model)), "ready_s": ready}
            (serve_dir() / f"{model}.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            log(f"{model} ready after {ready} s (pid {process.pid}, log {log_path(model)})")
            return record
        time.sleep(5)
    stop(model)
    raise RuntimeError(f"{model}: not ready after {timeout_s} s; see {log_path(model)}")


def stop(model: str, log=print) -> bool:
    pid = running(model)
    if pid is None:
        return False
    os.killpg(pid, signal.SIGTERM)
    for _ in range(60):
        try:
            os.kill(pid, 0)
        except OSError:
            break
        time.sleep(1)
    else:
        os.killpg(pid, signal.SIGKILL)
    pid_path(model).unlink(missing_ok=True)
    log(f"{model} stopped")
    return True


def logged_sampling_params(model: str, request_marker: str | None = None) -> list[str]:
    """The ``SamplingParams(...)`` texts the server logged for its requests, newest last."""
    path = log_path(model)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        idx = line.find("SamplingParams(")
        if idx >= 0 and (request_marker is None or request_marker in line):
            depth, end = 0, idx
            for end in range(idx, len(line)):
                depth += line[end] == "("
                depth -= line[end] == ")"
                if depth == 0 and line[end] == ")":
                    break
            out.append(line[idx:end + 1])
    return out
