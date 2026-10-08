"""One chat-client interface for every backend (handoff, "Model backends").

``ChatRequest.meta`` carries the instance (concept directory, target side, kind). Real
backends ignore it; the mock backends read it to return the right reference. Every
sampling parameter is sent explicitly in ``params`` (handoff L1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from varag.config import load_models


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


def make_backend(model_id: str) -> Backend:
    backends = load_models()["backends"]
    if model_id not in backends:
        raise KeyError(f"unknown backend {model_id!r}; see configs/models.yaml")
    spec = backends[model_id]
    if spec["type"] == "mock":
        from varag.llm.mock import MockBackend

        return MockBackend(model_id, spec["behaviour"])
    raise NotImplementedError(f"backend type {spec['type']!r} is not implemented until M6")
