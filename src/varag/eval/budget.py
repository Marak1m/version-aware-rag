"""The cost estimate ``varag run --max-usd`` prints before it starts (OpenRouter note, item 1d).

A dry pass walks every method over every instance with a stand-in backend that records each
request instead of sending it and answers with an empty code block. That reproduces each method's
first-turn prompts exactly (the documents, the version statements, the stub), so prompts already
in the response cache are known to be free. Each remaining request is priced at the pinned
provider's current rates from ``/models/<id>/endpoints``: its prompt tokens (counted with the
pinned Qwen tokenizer) plus an expected completion length (the mean of this backend's cached
completions, else ``DEFAULT_COMPLETION_TOKENS``), times ``TURN_FACTOR`` for the calls the dry
pass cannot see (a second turn after a question, a guard repair).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from varag.llm.client import ChatRequest, ChatResponse, cache_key

DEFAULT_COMPLETION_TOKENS = 300
TURN_FACTOR = 1.25


@dataclass
class Prices:
    prompt: float          # USD per prompt token
    completion: float      # USD per completion token
    request: float = 0.0   # USD per request

    def cost(self, prompt_tokens: int, completion_tokens: float) -> float:
        return prompt_tokens * self.prompt + completion_tokens * self.completion + self.request


def live_prices(backend) -> tuple[Prices, dict]:
    endpoint = backend.pinned_endpoint()
    if endpoint is None:
        raise RuntimeError(f"{backend.name}: no live endpoint for provider {backend.provider!r} on {backend.model}")
    p = endpoint.get("pricing", {})
    return Prices(float(p.get("prompt") or 0), float(p.get("completion") or 0), float(p.get("request") or 0)), endpoint


class DryBackend:
    """Records requests under the real backend's cache keys; answers with an empty code block."""

    def __init__(self, real):
        self.real = real
        self.name = real.name
        self.requests: list[tuple[str, list[dict]]] = []

    def complete(self, request: ChatRequest, use_cache: bool = True) -> ChatResponse:
        key = cache_key(self.real.name, self.real.cache_revision, request.messages, request.params)
        self.requests.append((key, request.messages))
        return ChatResponse("```python\npass\n```", model="dry-run")


def mean_completion_tokens(backend) -> float:
    path = backend.cache.directory / "requests.jsonl"
    values = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("backend") == backend.name and (rec.get("usage") or {}).get("completion_tokens"):
                values.append(rec["usage"]["completion_tokens"])
    return sum(values) / len(values) if len(values) >= 20 else float(DEFAULT_COMPLETION_TOKENS)


def estimate(backend, methods, instances, make_ctx, versions) -> dict:
    from varag.corpus.tokens import count_tokens

    dry = DryBackend(backend)
    ctx = make_ctx(dry)
    for instance in instances:
        for method in methods:
            method.answer(instance, dry, versions, ctx)
    prices, endpoint = live_prices(backend)
    completion = mean_completion_tokens(backend)
    uncached = [(k, m) for k, m in dry.requests if backend.cache.get(k) is None]
    prompt_tokens = sum(count_tokens("\n".join(x["content"] for x in m)) + 8 * len(m) for _, m in uncached)
    usd = sum(prices.cost(count_tokens("\n".join(x["content"] for x in m)) + 8 * len(m), completion) for _, m in uncached) * TURN_FACTOR
    return {"requests_first_turn": len(dry.requests), "cached": len(dry.requests) - len(uncached), "uncached": len(uncached),
            "prompt_tokens_uncached": prompt_tokens, "completion_tokens_per_call": round(completion, 1), "turn_factor": TURN_FACTOR,
            "prices_usd_per_million": {"prompt": prices.prompt * 1e6, "completion": prices.completion * 1e6, "request": prices.request},
            "provider_endpoint": {k: endpoint.get(k) for k in ("provider_name", "tag", "quantization", "status", "uptime_last_30m")},
            "usd": round(usd, 4)}


def format_estimate(model: str, e: dict) -> str:
    p = e["prices_usd_per_million"]
    return (f"[{model}] cost estimate ${e['usd']:.4f}: {e['uncached']} uncached first-turn requests of {e['requests_first_turn']} "
            f"({e['prompt_tokens_uncached']:,} prompt tokens, {e['completion_tokens_per_call']} completion tokens each, x{e['turn_factor']} for extra turns) "
            f"at ${p['prompt']:.3f}/M in, ${p['completion']:.3f}/M out on {e['provider_endpoint'].get('tag')}")
