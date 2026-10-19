"""``varag preflight``: everything the GPU session needs before the first model is served
(docs/GPU_HANDOFF.md, step 1).

Checks, in order: the GPU is visible from WSL; the vLLM venv's torch sees it with CUDA 12.8 or
later and kernels for its compute capability; the pinned vLLM version is installed; free VRAM
against each model's weights; free disk at HF_HOME; Hugging Face serves both pinned revisions; uv;
the six environments verify and their manifest matches the committed one on every lock-derived
field; the harness can apply the memory limit and network isolation. Each check is ``ok``,
``warn`` or ``fail``; any ``fail`` makes the command exit non-zero.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from packaging.version import InvalidVersion, Version

from varag.config import load_models, project_root

# Manifest fields that come from the locks and the libraries; interpreter paths, the platform
# string, the CPython patch and timestamps legitimately differ between machines.
STABLE_FIELDS = ("lock_sha256", "library", "side", "library_version", "expected_version", "distributions")
OVERHEAD_GB = 1.5          # CUDA context, activations, sampler and one 8192-token KV cache, above the weights
MIN_UV = "0.11"


@dataclass
class Check:
    name: str
    status: str            # ok | warn | fail
    detail: str
    fix: str = ""


def _run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)
    return out.returncode, (out.stdout + out.stderr).strip()


def vllm_python() -> Path:
    return Path(os.path.expanduser(load_models()["serving"]["vllm"]["python"]))


def hf_home() -> Path:
    return Path(os.environ.get("HF_HOME") or os.path.expanduser("~/.cache/huggingface"))


def hf_token() -> str | None:
    token = os.environ.get("HF_TOKEN")
    path = hf_home() / "token"
    return token or (path.read_text(encoding="utf-8").strip() if path.exists() else None)


def served_backends() -> dict[str, dict]:
    return {k: v for k, v in load_models()["backends"].items() if v.get("type") == "openai_chat" and v.get("server") == "vllm"}


# --- individual checks -----------------------------------------------------------------------


def gpu() -> tuple[Check, dict]:
    code, out = _run(["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,driver_version,compute_cap",
                      "--format=csv,noheader,nounits"])
    if code != 0 or not out:
        return Check("gpu", "fail", f"nvidia-smi failed: {out[:200]}", "install the NVIDIA driver on Windows; WSL2 needs no driver of its own"), {}
    name, total, used, free, driver, cap = [x.strip() for x in out.splitlines()[0].split(",")]
    info = {"name": name, "total_mib": int(total), "used_mib": int(used), "free_mib": int(free), "driver": driver, "compute_cap": cap}
    return Check("gpu", "ok", f"{name}, {int(total) / 1024:.1f} GiB, driver {driver}, compute capability {cap}"), info


def cuda_and_vllm(gpu_info: dict) -> list[Check]:
    serving = load_models()["serving"]["vllm"]
    python = vllm_python()
    if not python.exists():
        return [Check("vllm", "fail", f"no vLLM venv at {python}", serving["install"])]
    probe = ("import json, torch, vllm; print(json.dumps({'vllm': vllm.__version__, 'torch': torch.__version__, "
             "'cuda': torch.version.cuda, 'available': torch.cuda.is_available(), "
             "'cap': list(torch.cuda.get_device_capability(0)) if torch.cuda.is_available() else None, "
             "'arch': torch.cuda.get_arch_list()}))")
    code, out = _run([str(python), "-c", probe], timeout=180)
    if code != 0:
        return [Check("vllm", "fail", f"importing vllm/torch failed: {out[-300:]}", serving["install"])]
    info = json.loads(out.strip().splitlines()[-1])
    checks = []
    ok_version = info["vllm"] == serving["version"]
    checks.append(Check("vllm", "ok" if ok_version else "fail", f"vLLM {info['vllm']} (pinned {serving['version']}), torch {info['torch']}",
                        "" if ok_version else serving["install"]))
    problems = []
    if not info["available"]:
        problems.append("torch.cuda.is_available() is False")
    if not info["cuda"] or Version(info["cuda"]) < Version(serving["min_cuda"]):
        problems.append(f"torch CUDA {info['cuda']} < {serving['min_cuda']}")
    if info["cap"]:
        arch = f"sm_{info['cap'][0]}{info['cap'][1]}"
        if arch not in info["arch"]:
            problems.append(f"torch has no {arch} kernels ({', '.join(info['arch'])})")
    checks.append(Check("cuda", "fail" if problems else "ok",
                        "; ".join(problems) or f"torch CUDA {info['cuda']}, kernels for sm_{''.join(map(str, info['cap']))}",
                        "reinstall vLLM with --torch-backend=auto so torch matches the driver" if problems else ""))
    return checks


def model_weights_gb(repo: str, revision: str) -> float | None:
    try:
        meta = _hf_json(f"https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None
    sizes = [s.get("size") or 0 for s in meta.get("siblings", []) if s["rfilename"].endswith(".safetensors")]
    return sum(sizes) / 1e9 if sizes else None


def vram(gpu_info: dict) -> list[Check]:
    if not gpu_info:
        return []
    free_gb = gpu_info["free_mib"] / 1024
    out = []
    for name, backend in served_backends().items():
        weights = model_weights_gb(backend["model"], backend["revision"])
        if weights is None:
            out.append(Check(f"vram:{name}", "warn", "weights size unknown (Hugging Face API unreachable)"))
            continue
        need = weights + OVERHEAD_GB
        enough = free_gb >= need
        out.append(Check(f"vram:{name}", "ok" if enough else "warn",
                         f"needs about {need:.1f} GiB ({weights:.1f} weights + {OVERHEAD_GB}); {free_gb:.1f} GiB free, "
                         f"{gpu_info['used_mib'] / 1024:.1f} GiB held by other processes",
                         "" if enough else "close GPU-heavy Windows apps (browsers, Discord, overlays), or lower "
                                           "--gpu-memory-utilization / --max-num-seqs before shortening the context"))
    return out


def disk() -> Check:
    need = float(load_models()["serving"].get("min_free_disk_gb", 20))
    home = hf_home()
    probe_dir = home if home.exists() else home.parent if home.parent.exists() else Path.home()
    free = shutil.disk_usage(probe_dir).free / 1e9
    return Check("disk", "ok" if free >= need else "fail", f"{free:.0f} GB free at {probe_dir} (need {need:g})",
                 "" if free >= need else "free disk space or point HF_HOME at a larger filesystem")


def _hf_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {hf_token()}"} if hf_token() else {})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def hf_access() -> list[Check]:
    out = []
    for name, backend in served_backends().items():
        repo, revision = backend["model"], backend["revision"]
        try:
            meta = _hf_json(f"https://huggingface.co/api/models/{repo}/revision/{revision}")
        except urllib.error.HTTPError as exc:
            out.append(Check(f"hf:{name}", "fail", f"{repo}@{revision[:12]}: HTTP {exc.code}", "log in with `huggingface-cli login` or set HF_TOKEN"))
            continue
        except (urllib.error.URLError, TimeoutError) as exc:
            out.append(Check(f"hf:{name}", "fail", f"{repo}: {exc}", "check the network"))
            continue
        files = {s["rfilename"] for s in meta.get("siblings", [])}
        problems = [p for p, bad in (("sha differs", meta.get("sha") != revision), ("gated without a token", bool(meta.get("gated")) and not hf_token()),
                                    ("no config.json", "config.json" not in files)) if bad]
        out.append(Check(f"hf:{name}", "fail" if problems else "ok", f"{repo}@{revision[:12]}" + (f": {'; '.join(problems)}" if problems else f", {len(files)} files")))
    return out


def uv() -> Check:
    path = shutil.which("uv") or os.path.expanduser("~/.local/bin/uv")
    code, out = _run([path, "--version"])
    match = re.search(r"uv (\d+\.\d+(?:\.\d+)?)", out)
    try:
        ok = code == 0 and bool(match) and Version(match.group(1)) >= Version(MIN_UV)
    except InvalidVersion:
        ok = False
    return Check("uv", "ok" if ok else "fail", out.splitlines()[0] if out else "not found",
                 "" if ok else "curl -LsSf https://astral.sh/uv/install.sh | sh")


def manifest_drift(current: dict, committed: dict) -> list[str]:
    """Lock-derived fields that differ between this machine's manifest and the committed one."""
    problems = []
    for name in sorted(set(current) | set(committed)):
        a, b = current.get(name), committed.get(name)
        if a is None or b is None:
            problems.append(f"{name}: {'missing here' if a is None else 'not committed'}")
            continue
        for field in STABLE_FIELDS:
            if a.get(field) != b.get(field):
                problems.append(f"{name}: {field} differs from the committed manifest")
        if str(a.get("python_version", "")).split(".")[:2] != str(b.get("python_version", "")).split(".")[:2]:
            problems.append(f"{name}: Python minor version differs ({a.get('python_version')} vs {b.get('python_version')})")
    return problems


def environments() -> list[Check]:
    from varag.envs.build import read_manifest
    from varag.envs.verify import verify_all

    try:
        mismatches = [str(m) for found in verify_all().values() for m in found]
    except FileNotFoundError as exc:
        return [Check("envs", "fail", f"{exc}", "uv run varag env build")]
    checks = [Check("env verify", "fail" if mismatches else "ok", "; ".join(mismatches[:3]) or "six environments match their manifest and canaries",
                    "uv run varag env build (never --relock unless pins change)" if mismatches else "")]
    code, out = _run(["git", "-C", str(project_root()), "show", "HEAD:envs/manifest.json"])
    if code != 0:
        checks.append(Check("manifest", "warn", "no committed envs/manifest.json to compare with"))
        return checks
    drift = manifest_drift(read_manifest(), json.loads(out))
    checks.append(Check("manifest", "fail" if drift else "ok", "; ".join(drift[:3]) or "lock hashes, versions and distributions match the committed manifest",
                        "the locks or the build differ from the commit: rebuild with `varag env build`, never --relock" if drift else ""))
    return checks


def isolation() -> Check:
    from varag.eval.execute import isolation_status

    status = isolation_status()
    missing = [k for k, v in status.items() if not v]
    return Check("isolation", "fail" if missing else "ok", "memory limit and network isolation apply" if not missing else f"missing: {', '.join(missing)}",
                 "run under WSL2 with unprivileged user namespaces (unshare -rn)" if missing else "")


def preflight() -> list[Check]:
    gpu_check, gpu_info = gpu()
    checks = [gpu_check]
    checks += cuda_and_vllm(gpu_info) if gpu_info else []
    checks += vram(gpu_info)
    checks.append(disk())
    checks += hf_access()
    checks.append(uv())
    checks += environments()
    checks.append(isolation())
    return checks


def format_checks(checks: list[Check]) -> str:
    width = max(len(c.name) for c in checks)
    lines = []
    for c in checks:
        lines.append(f"[{c.status:4}] {c.name:{width}}  {c.detail}")
        if c.fix and c.status != "ok":
            lines.append(f"       {'':{width}}  fix: {c.fix}")
    failed = [c for c in checks if c.status == "fail"]
    lines.append(f"{len(checks) - len(failed)}/{len(checks)} checks without failure" + (f"; FAILED: {', '.join(c.name for c in failed)}" if failed else ""))
    return "\n".join(lines)
