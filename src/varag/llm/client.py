"""One chat-client interface for every backend (handoff, "Model backends").

``ChatRequest.meta`` carries the instance (concept directory, target side, kind). Real backends
ignore it; the mock backends read it to return the right reference. Every sampling parameter is
sent explicitly in ``params`` (handoff L1).

The real backend speaks the OpenAI chat-completions protocol only (``/chat/completions``,
``/models``, and vLLM's ``/tokenize`` and ``/detokenize`` when present), so vLLM and a llama.cpp
server are interchangeable at the same ``base_url``. Every request and response is cached on disk
under sha256(backend, revision, messages, params) and logged; a cache hit returns the stored text
unchanged and makes no call.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from varag.config import load_models, project_root


@dataclass
class ChatRequest:
    messages: list[dict]
    params: dict
    meta: dict = field(default_factory=dict)


@dataclass
class ChatResponse:
    text: str
    model: str = ""
    usage: dict = field(default_factory=dict)
    cached: bool = False
    provider: str | None = None        # the provider OpenRouter reports for this response


class Backend(Protocol):
    name: str

    def complete(self, request: ChatRequest) -> ChatResponse: ...


def default_params() -> dict:
    return dict(load_models()["sampling"])


def cache_dir() -> Path:
    return project_root() / load_models().get("cache_dir", "runs/_cache")


def cache_key(backend: str, revision: str | None, messages: list[dict], params: dict, repeat: int = 0) -> str:
    """sha256 of the request. ``repeat`` (user decision 2026-10-21: repeats per instance on noisy
    endpoints) enters the key only when non-zero, so repeat 0 keeps the keys every earlier run used."""
    record = {"backend": backend, "revision": revision, "messages": messages, "params": params}
    if repeat:
        record["repeat"] = int(repeat)
    payload = json.dumps(record, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ResponseCache:
    def __init__(self, directory: Path):
        self.directory = directory

    def path(self, key: str) -> Path:
        return self.directory / key[:2] / f"{key}.json"

    def get(self, key: str) -> dict | None:
        path = self.path(key)
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def put(self, key: str, record: dict) -> None:
        path = self.path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")

    def log(self, record: dict) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        with open(self.directory / "requests.jsonl", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


class OpenAIChatBackend:
    def __init__(self, name: str, spec: dict, cache: ResponseCache | None = None):
        self.name = name
        self.spec = spec
        self.base_url = str(spec["base_url"]).rstrip("/")
        self.model = spec.get("served_model_name") or spec["model"]
        self.timeout = int(spec.get("timeout_s", 300))
        self.cache = cache if cache is not None else ResponseCache(cache_dir())
        self.calls = 0
        self.cache_hits = 0
        self.first_messages: list[dict] | None = None    # rendered once per run into run.json (handoff L1)
        self.repeat = 0                                  # the repeat index the run loop is on; part of the cache key

    def body(self, request: ChatRequest) -> dict:
        p = request.params
        if self.spec.get("sampling_profile") == "model_default":
            # The L1 test's other arm: the server applies the repository's generation config, so
            # the request sends only the length cap and the seed (reproducible sampling).
            return {"model": self.model, "messages": request.messages, "max_tokens": p["max_tokens"], "seed": p.get("seed")}
        body = {"model": self.model, "messages": request.messages, "temperature": p["temperature"], "top_p": p["top_p"],
                "max_tokens": p["max_tokens"], "n": p.get("n", 1)}
        if p.get("seed") is not None:
            body["seed"] = p["seed"]
        if p.get("repetition_penalty") is not None:
            key = "repeat_penalty" if self.spec.get("server") == "llama_cpp" else "repetition_penalty"
            body[key] = p["repetition_penalty"]
        return body

    def _request(self, method: str, path: str, body: dict | None = None, attempts: int = 3, root: bool = False) -> dict:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        # vLLM serves /tokenize and /detokenize at the server root, beside /v1, not under it.
        base = self.base_url.removesuffix("/v1") if root else self.base_url
        req = urllib.request.Request(base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer none"})
        last: Exception | None = None
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:500]
                if exc.code == 404 and path in ("/tokenize", "/detokenize"):
                    raise FileNotFoundError(path) from exc
                if exc.code < 500:
                    raise RuntimeError(f"{self.name}: {method} {path} returned {exc.code}: {detail}") from exc
                last = RuntimeError(f"{self.name}: {method} {path} returned {exc.code}: {detail}")
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                last = RuntimeError(f"{self.name}: cannot reach {self.base_url}{path}: {exc}")
            time.sleep(2 * (attempt + 1))
        raise last or RuntimeError(f"{self.name}: request failed")

    def complete(self, request: ChatRequest, use_cache: bool = True) -> ChatResponse:
        if self.first_messages is None:
            self.first_messages = request.messages
        key = cache_key(self.name, self.spec.get("revision"), request.messages, request.params, self.repeat)
        hit = self.cache.get(key) if use_cache else None
        if hit is not None:
            self.cache_hits += 1
            return ChatResponse(hit["text"], hit.get("model", ""), hit.get("usage", {}), cached=True)
        body = self.body(request)
        started = time.monotonic()
        data = self._request("POST", "/chat/completions", body)
        self.calls += 1
        choice = (data.get("choices") or [{}])[0]
        text = (choice.get("message") or {}).get("content") or ""
        record = {"key": key, "backend": self.name, "model": data.get("model", self.model), "revision": self.spec.get("revision"),
                  "request": body, "text": text, "usage": data.get("usage", {}), "finish_reason": choice.get("finish_reason"),
                  "latency_s": round(time.monotonic() - started, 3), "meta": request.meta,
                  "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        if use_cache:
            self.cache.put(key, record)
        self.cache.log({k: v for k, v in record.items() if k != "request"} | {"n_messages": len(request.messages)})
        return ChatResponse(text, record["model"], record["usage"], cached=False)

    def server_version(self) -> str | None:
        try:
            return self._request("GET", "/version", root=True, attempts=1).get("version")
        except (RuntimeError, FileNotFoundError):
            return None

    def serving_record(self) -> dict:
        """What the handoff asks each run to log once: server version, revision, GPU, concurrency,
        seed, and the first instance's prompt after chat templating."""
        import subprocess

        try:
            gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                                 capture_output=True, text=True, timeout=20).stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            gpu = None
        return {"server": self.spec.get("server"), "server_version": self.server_version(), "model": self.spec.get("model"),
                "revision": self.spec.get("revision"), "served_model_name": self.model, "serve_args": self.spec.get("serve_args"),
                "sampling_profile": self.spec.get("sampling_profile", "pinned"), "gpu": gpu, "concurrency": 1,
                "calls": self.calls, "cache_hits": self.cache_hits,
                "first_prompt_rendered": self.rendered_prompt(self.first_messages) if self.first_messages else None}

    def models(self) -> list[str]:
        data = self._request("GET", "/models")
        return [m.get("id", "") for m in data.get("data", [])]

    def rendered_prompt(self, messages: list[dict]) -> str | None:
        """The prompt after chat templating, through vLLM's /tokenize and /detokenize; None when the
        server has no such endpoints (llama.cpp)."""
        for root in (True, False):
            try:
                tokens = self._request("POST", "/tokenize", {"model": self.model, "messages": messages, "add_generation_prompt": True}, root=root)["tokens"]
                return self._request("POST", "/detokenize", {"model": self.model, "tokens": tokens}, root=root)["prompt"]
            except (FileNotFoundError, KeyError, RuntimeError):
                continue
        return None


class BudgetExceeded(RuntimeError):
    """The run's spending cap (``varag run --max-usd``) would be crossed by another paid call."""


class Budget:
    """A spending cap. One Budget may be shared by runs in several threads (the final sweep runs
    the three models side by side under one cap), so updates take a lock."""

    def __init__(self, max_usd: float | None):
        import threading

        self.max_usd = max_usd
        self.spent = 0.0
        self._lock = threading.Lock()

    def check(self) -> None:
        with self._lock:
            if self.max_usd is not None and self.spent >= self.max_usd:
                raise BudgetExceeded(f"spent ${self.spent:.4f} of the ${self.max_usd:.2f} cap")

    def add(self, usd: float) -> None:
        with self._lock:
            self.spent += usd

    def remaining(self) -> float | None:
        with self._lock:
            return None if self.max_usd is None else max(0.0, self.max_usd - self.spent)


def openrouter_key() -> str:
    """OPENROUTER_API_KEY from the environment, else from the git-ignored key file at the repository
    root (``OPENROUTER_API_KEY`` or ``openrouter-api-key``, a ``KEY=value`` line or the bare key).
    The key is never written to a file, a cache record or a log."""
    import os

    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    for name in ("OPENROUTER_API_KEY", "openrouter-api-key"):
        path = project_root() / name
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if "sk-or-" in line:
                    return line.split("=", 1)[-1].strip().strip("'\"")
    raise RuntimeError("no OpenRouter key: set OPENROUTER_API_KEY or put it in ./openrouter-api-key (git-ignored)")


RETRYABLE = {408, 409, 425, 429, 500, 502, 503, 504, 520, 522, 524, 529}


class OpenRouterBackend(OpenAIChatBackend):
    """OpenRouter's chat-completions API with one pinned provider per model (handoff L1 for a hosted
    endpoint): every request sends the pinned sampling block and provider routing
    ``{order: [provider], allow_fallbacks: false, require_parameters: true}``, so a provider that
    would ignore seed or repetition_penalty is refused rather than silently used. Each response's
    provider, model id and usage (tokens, cost) is recorded; 429 and 5xx are retried with
    exponential backoff. The response cache works as for every backend; its key includes the
    model id and the pinned provider."""

    def __init__(self, name: str, spec: dict, cache: ResponseCache | None = None, budget: Budget | None = None):
        super().__init__(name, {**spec, "base_url": spec.get("base_url", "https://openrouter.ai/api/v1")}, cache)
        self.model = spec["model"]
        self.provider = spec["provider"]
        self.provider_name = spec.get("provider_name")
        self.timeout = int(spec.get("timeout_s", 180))
        self.max_attempts = int(spec.get("max_attempts", 8))
        self.budget = budget or Budget(None)
        self.call_log: list[dict] = []        # per-call metadata since the last drain(); rows read it
        self.cost_total = 0.0
        self.session: str | None = None

    @property
    def cache_revision(self) -> str:
        return f"{self.model}@{self.provider}"

    def body(self, request: ChatRequest) -> dict:
        p = request.params
        return {"model": self.model, "messages": request.messages, "temperature": p["temperature"], "top_p": p["top_p"],
                "repetition_penalty": p["repetition_penalty"], "max_tokens": p["max_tokens"], "seed": p["seed"],
                "provider": {"order": [self.provider], "allow_fallbacks": False, "require_parameters": True},
                "usage": {"include": True}}

    def _post(self, path: str, body: dict | None, method: str = "POST", meta: dict | None = None) -> dict:
        from varag import logbook

        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {openrouter_key()}",
                   "X-Title": "VA-RAG benchmark"}
        last = None
        for attempt in range(1, self.max_attempts + 1):
            req = urllib.request.Request(self.base_url + path, data=data, method=method, headers=headers)
            started = time.monotonic()
            status, retry_after, payload, error = None, None, None, None
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    status = resp.status
                    payload = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                status = exc.code
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                error = exc.read().decode("utf-8", "replace")[:2000]
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                error = f"{type(exc).__name__}: {exc}"
            # OpenRouter can also answer 200 with an error object (an upstream provider failure).
            if payload is not None and isinstance(payload.get("error"), dict):
                status = int(payload["error"].get("code") or 502) if str(payload["error"].get("code", "")).isdigit() else 502
                error = json.dumps(payload["error"])[:2000]
                payload = None
            latency = round(time.monotonic() - started, 3)
            retryable = payload is None and (status is None or status in RETRYABLE)
            wait = min(90.0, float(retry_after) if (retry_after or "").replace(".", "", 1).isdigit() else 2.0 * 2 ** (attempt - 1)) if retryable else 0.0
            logbook.openrouter({"backend": self.name, "path": path, "attempt": attempt, "status": status, "latency_s": latency,
                                "request": body, "response": payload, "error": error, "retry_in_s": wait if retryable and attempt < self.max_attempts else None,
                                "session": self.session, **(meta or {})})
            if payload is not None:
                return payload
            last = RuntimeError(f"{self.name}: {method} {path} returned {status}: {error}")
            if not retryable:
                raise last
            if attempt < self.max_attempts:
                time.sleep(wait)
        raise last or RuntimeError(f"{self.name}: request failed")

    def complete(self, request: ChatRequest, use_cache: bool = True) -> ChatResponse:
        from varag import logbook

        if self.first_messages is None:
            self.first_messages = request.messages
        key = cache_key(self.name, self.cache_revision, request.messages, request.params, self.repeat)
        hit = self.cache.get(key) if use_cache else None
        if hit is not None:
            self.cache_hits += 1
            meta = {"cached": True, "provider": hit.get("provider"), "model": hit.get("model"), "usage": hit.get("usage", {}),
                    "cost_usd": 0.0, "key": key, "instance_id": request.meta.get("instance_id"), "repeat": self.repeat}
            self.call_log.append(meta)
            logbook.openrouter({"backend": self.name, "cache_hit": key, "instance_id": request.meta.get("instance_id"), "repeat": self.repeat,
                                "session": self.session})
            return ChatResponse(hit["text"], hit.get("model", ""), hit.get("usage", {}), cached=True, provider=hit.get("provider"))
        self.budget.check()
        body = self.body(request)
        started = time.monotonic()
        data = self._post("/chat/completions", body, meta={"instance_id": request.meta.get("instance_id"), "repeat": self.repeat})
        self.calls += 1
        choice = (data.get("choices") or [{}])[0]
        text = (choice.get("message") or {}).get("content") or ""
        usage = data.get("usage", {}) or {}
        cost = float(usage.get("cost") or 0.0)
        self.budget.add(cost)
        self.cost_total += cost
        provider = data.get("provider")
        record = {"key": key, "backend": self.name, "model": data.get("model", self.model), "provider": provider,
                  "pinned_provider": self.provider, "provider_match": self.provider_matches(provider), "revision": self.cache_revision,
                  "request": body, "text": text, "usage": usage, "finish_reason": choice.get("finish_reason"),
                  "native_finish_reason": choice.get("native_finish_reason"), "generation_id": data.get("id"),
                  "latency_s": round(time.monotonic() - started, 3), "meta": request.meta, "repeat": self.repeat, "session": self.session,
                  "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        if use_cache:
            self.cache.put(key, record)
        self.cache.log({k: v for k, v in record.items() if k != "request"} | {"n_messages": len(request.messages)})
        meta = {"cached": False, "repeat": self.repeat, "provider": provider, "model": record["model"], "usage": usage, "cost_usd": cost, "key": key,
                "provider_match": record["provider_match"], "finish_reason": record["finish_reason"], "instance_id": request.meta.get("instance_id")}
        self.call_log.append(meta)
        logbook.cost({"backend": self.name, "model": record["model"], "provider": provider, "session": self.session,
                      "instance_id": request.meta.get("instance_id"), "repeat": self.repeat, "prompt_tokens": usage.get("prompt_tokens"),
                      "completion_tokens": usage.get("completion_tokens"), "cost_usd": cost, "run_spent_usd": round(self.budget.spent, 6)})
        return ChatResponse(text, record["model"], usage, cached=False, provider=provider)

    def provider_matches(self, reported: str | None) -> bool | None:
        if reported is None:
            return None
        want = {self.provider.split("/")[0].lower().replace("-", ""), (self.provider_name or "").lower().replace(" ", "").replace("-", "")} - {""}
        got = reported.lower().replace(" ", "").replace("-", "")
        return any(w == got or got.startswith(w) or w.startswith(got) for w in want)

    def drain(self) -> list[dict]:
        out, self.call_log = self.call_log, []
        return out

    def endpoints(self) -> dict:
        return self._post(f"/models/{self.model}/endpoints", None, method="GET")["data"]

    def pinned_endpoint(self) -> dict | None:
        for e in self.endpoints().get("endpoints", []):
            tag = (e.get("tag") or "").lower()
            if tag == self.provider.lower() or tag.split("/")[0] == self.provider.split("/")[0].lower():
                return e
        return None

    def models(self) -> list[str]:
        return [self.model]

    def rendered_prompt(self, messages: list[dict]) -> str | None:
        return None        # OpenRouter does not expose the provider's chat template (docs/DECISIONS.md)

    def serving_record(self) -> dict:
        return {"server": "openrouter", "model": self.model, "provider_pin": self.provider, "provider_name": self.provider_name,
                "routing": {"order": [self.provider], "allow_fallbacks": False, "require_parameters": True},
                "concurrency": 1, "calls": self.calls, "cache_hits": self.cache_hits, "cost_usd": round(self.cost_total, 6),
                "session": self.session, "first_prompt_rendered": None,
                "first_prompt_messages": self.first_messages}


def make_backend(model_id: str, budget: Budget | None = None, allow_inactive: bool = False) -> Backend:
    backends = load_models()["backends"]
    if model_id not in backends:
        raise KeyError(f"unknown backend {model_id!r}; see configs/models.yaml")
    spec = backends[model_id]
    if spec.get("active") is False and not allow_inactive:
        raise RuntimeError(f"backend {model_id!r} is inactive (configs/models.yaml); inference runs on OpenRouter now")
    if spec["type"] == "openrouter":
        return OpenRouterBackend(model_id, spec, budget=budget)
    if spec["type"] == "mock":
        from varag.llm.mock import MockBackend

        return MockBackend(model_id, spec["behaviour"])
    if spec["type"] == "openai_chat":
        return OpenAIChatBackend(model_id, spec)
    raise NotImplementedError(f"backend type {spec['type']!r}")
