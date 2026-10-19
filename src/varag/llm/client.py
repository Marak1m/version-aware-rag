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


class Backend(Protocol):
    name: str

    def complete(self, request: ChatRequest) -> ChatResponse: ...


def default_params() -> dict:
    return dict(load_models()["sampling"])


def cache_dir() -> Path:
    return project_root() / load_models().get("cache_dir", "runs/_cache")


def cache_key(backend: str, revision: str | None, messages: list[dict], params: dict) -> str:
    payload = json.dumps({"backend": backend, "revision": revision, "messages": messages, "params": params}, sort_keys=True)
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

    def body(self, request: ChatRequest) -> dict:
        p = request.params
        body = {"model": self.model, "messages": request.messages, "temperature": p["temperature"], "top_p": p["top_p"],
                "max_tokens": p["max_tokens"], "n": p.get("n", 1)}
        if p.get("seed") is not None:
            body["seed"] = p["seed"]
        if p.get("repetition_penalty") is not None:
            key = "repeat_penalty" if self.spec.get("server") == "llama_cpp" else "repetition_penalty"
            body[key] = p["repetition_penalty"]
        return body

    def _request(self, method: str, path: str, body: dict | None = None, attempts: int = 3) -> dict:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(self.base_url + path, data=data, method=method,
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
        key = cache_key(self.name, self.spec.get("revision"), request.messages, request.params)
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

    def models(self) -> list[str]:
        data = self._request("GET", "/models")
        return [m.get("id", "") for m in data.get("data", [])]

    def rendered_prompt(self, messages: list[dict]) -> str | None:
        """The prompt after chat templating, through vLLM's /tokenize and /detokenize; None when the
        server has no such endpoints (llama.cpp)."""
        try:
            tokens = self._request("POST", "/tokenize", {"model": self.model, "messages": messages, "add_generation_prompt": True})["tokens"]
            return self._request("POST", "/detokenize", {"model": self.model, "tokens": tokens})["prompt"]
        except (FileNotFoundError, KeyError, RuntimeError):
            return None


def make_backend(model_id: str) -> Backend:
    backends = load_models()["backends"]
    if model_id not in backends:
        raise KeyError(f"unknown backend {model_id!r}; see configs/models.yaml")
    spec = backends[model_id]
    if spec["type"] == "mock":
        from varag.llm.mock import MockBackend

        return MockBackend(model_id, spec["behaviour"])
    if spec["type"] == "openai_chat":
        return OpenAIChatBackend(model_id, spec)
    raise NotImplementedError(f"backend type {spec['type']!r}")
