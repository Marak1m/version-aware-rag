"""``varag serve check``: is the served model the configured one, with our sampling and our prompt?

Checks, per backend (handoff, "Serving configuration"):
- the server answers ``/models`` and lists the served model name;
- one completion with our system prompt and the explicit sampling block (temperature 0, top_p
  1.0, repetition penalty 1.0, fixed seed) returns code; the request body is printed, so the
  penalty we send is visible;
- the prompt after chat templating, through vLLM's tokenize and detokenize endpoints, starts with
  our system prompt and not the model's default one (reported as unavailable on llama.cpp);
- two identical uncached requests return identical text (a first serving-noise reading);
- the effective sampling parameters, as the server resolved them, from the request log that
  `varag serve start` enables (``--enable-log-requests``): repetition penalty 1.0, temperature 0,
  top_p 1.0, our seed; and whether the server says it loaded the model's generation config.
"""

from __future__ import annotations

import re

from varag.llm.client import ChatRequest, OpenAIChatBackend, default_params, make_backend
from varag.pipeline.generate import SYSTEM_PROMPT

PROBE_TASK = ("Task:\nWrite `add_one(x)` returning x + 1.\n")


PARAM_KEYS = ("temperature", "top_p", "repetition_penalty", "max_tokens", "seed")


def endpoint_check(model: str) -> dict:
    """The OpenRouter replacement for the serve check (OpenRouter note, item 3). Per model: the pinned
    endpoint is live and declares every parameter we send; our probe prompt sent twice, uncached,
    returns identical text; the provider OpenRouter reports matches the pin on every call. Two
    behaviour probes say whether the provider honours the seed under sampling and the repetition
    penalty (require_parameters only proves it accepts them). The rendered prompt cannot be seen
    through OpenRouter (docs/DECISIONS.md)."""
    from varag import logbook
    from varag.llm.client import OpenRouterBackend
    from varag.pipeline.generate import finish_prompt

    backend = make_backend(model)
    if not isinstance(backend, OpenRouterBackend):
        raise RuntimeError(f"{model} is not an OpenRouter backend")
    backend.session = f"endpoint-check:{backend.provider}@{logbook.stamp()}"
    report: dict = {"backend": model, "model": backend.model, "provider_pin": backend.provider, "problems": [], "notes": []}
    endpoint = backend.pinned_endpoint()
    if endpoint is None:
        report["problems"].append(f"no endpoint for provider {backend.provider!r} on {backend.model}")
        return report
    supported = set(endpoint.get("supported_parameters") or [])
    report["endpoint"] = {k: endpoint.get(k) for k in ("provider_name", "tag", "status", "uptime_last_30m", "quantization", "context_length", "pricing")}
    missing = [k for k in PARAM_KEYS if k not in supported]
    if missing:
        report["problems"].append(f"the endpoint does not declare {missing}")
    query = "Write `add_one(x)` returning x + 1."
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": finish_prompt(f"Task:\n{query}\n", query, "add_one", no_question=False)}]
    request = ChatRequest(messages, default_params(), {"instance_id": "endpoint-check"})
    report["request_body"] = {k: v for k, v in backend.body(request).items() if k != "messages"}
    first = backend.complete(request, use_cache=False)
    second = backend.complete(request, use_cache=False)
    report["response"] = first.text[:400]
    report["deterministic"] = first.text == second.text
    report["providers_reported"] = [first.provider, second.provider]
    report["models_reported"] = [first.model, second.model]
    if not report["deterministic"]:
        report["problems"].append("the same prompt sent twice returned different text")
    if not all(backend.provider_matches(pr) for pr in (first.provider, second.provider)):
        report["problems"].append(f"reported provider {report['providers_reported']} does not match the pin {backend.provider!r}")
    if "```" not in first.text and "QUESTION:" not in first.text:
        report["problems"].append("the probe reply has neither a fenced block nor a QUESTION line")

    def probe(msgs, **over):
        return backend.complete(ChatRequest(msgs, {**default_params(), **over}, {"instance_id": "endpoint-check-probe"}), use_cache=False).text

    story = [{"role": "user", "content": "Write one sentence about a cat with an unusual name."}]
    words = [{"role": "user", "content": "Write the word apple 40 times, separated by single spaces, and nothing else."}]
    s1, s2 = probe(story, temperature=1.0, seed=7), probe(story, temperature=1.0, seed=7)
    r1, r2 = probe(words, max_tokens=200), probe(words, max_tokens=200, repetition_penalty=2.0)
    report["honours"] = {"seed_under_sampling": s1 == s2, "repetition_penalty": r1 != r2}
    if not report["honours"]["repetition_penalty"]:
        report["problems"].append("repetition_penalty 2.0 did not change the output: the provider accepts it but ignores it")
    if not report["honours"]["seed_under_sampling"]:
        report["notes"].append("the seed is not honoured under sampling (temperature 1); our requests use temperature 0, where it does not matter")
    report["notes"].append("the rendered prompt (after the provider's chat template) is not visible through OpenRouter")
    report["cost_usd"] = round(backend.cost_total, 6)
    report["log"] = str(logbook.write_check(f"endpoint-{model}", report))
    return report


def serve_check(model: str) -> dict:
    from varag.config import load_models

    if load_models()["backends"].get(model, {}).get("type") == "openrouter":
        return endpoint_check(model)
    backend = make_backend(model, allow_inactive=True)
    if not isinstance(backend, OpenAIChatBackend):
        raise RuntimeError(f"{model} is not an OpenAI-compatible backend")
    report: dict = {"backend": model, "base_url": backend.base_url, "served_model_name": backend.model, "problems": []}
    try:
        ids = backend.models()
    except RuntimeError as exc:
        report["problems"].append(str(exc))
        return report
    report["models"] = ids
    if backend.model not in ids:
        report["problems"].append(f"served models {ids} do not include {backend.model!r}")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": PROBE_TASK}]
    request = ChatRequest(messages, default_params(), {"instance_id": "serve-check"})
    report["request_body"] = {k: v for k, v in backend.body(request).items() if k != "messages"}
    penalty = report["request_body"].get("repetition_penalty", report["request_body"].get("repeat_penalty"))
    if penalty != 1.0:
        report["problems"].append(f"repetition penalty sent is {penalty}, not 1.0")
    first = backend.complete(request, use_cache=False)
    second = backend.complete(request, use_cache=False)
    report["response"] = first.text[:400]
    report["deterministic"] = first.text == second.text
    if not report["deterministic"]:
        report["problems"].append("two identical requests returned different text (serving noise)")
    if "```" not in first.text and "QUESTION:" not in first.text:
        report["problems"].append("the probe reply has neither a fenced block nor a QUESTION line")
    effective_sampling(model, report)
    report["server_version"] = backend.server_version()
    rendered = backend.rendered_prompt(messages)
    report["rendered_prompt"] = rendered
    if rendered is None:
        report.setdefault("notes", []).append("the server has no tokenize endpoint: the rendered prompt could not be read (llama.cpp); check its --chat-template")
    elif SYSTEM_PROMPT.splitlines()[0] not in rendered:
        report["problems"].append("the rendered prompt does not contain our system prompt")
    return report


EFFECTIVE_KEYS = ("repetition_penalty", "temperature", "top_p", "top_k", "seed", "presence_penalty", "frequency_penalty", "max_tokens")
EXPECTED = {"repetition_penalty": 1.0, "temperature": 0.0, "top_p": 1.0, "presence_penalty": 0.0, "frequency_penalty": 0.0}


def parse_sampling_params(text: str) -> dict:
    out = {}
    for key in EFFECTIVE_KEYS:
        m = re.search(rf"\b{key}=([-\w.]+)", text)
        if m:
            value = m.group(1)
            try:
                out[key] = float(value) if "." in value else int(value)
            except ValueError:
                out[key] = value
    return out


def effective_sampling(model: str, report: dict) -> None:
    """Read the server log of `varag serve start` for the parameters the server applied."""
    from varag.serving import backend_spec, log_path, logged_sampling_params

    try:
        backend_spec(model)
    except KeyError:
        report.setdefault("notes", []).append("not a vLLM backend: effective sampling parameters not read")
        return
    logged = logged_sampling_params(model)
    if not logged:
        report.setdefault("notes", []).append(f"no SamplingParams in {log_path(model)}: start the server with `varag serve start` to read the effective parameters")
        return
    effective = parse_sampling_params(logged[-1])
    report["effective_sampling"] = effective
    expected = {**EXPECTED, "seed": default_params().get("seed")}
    for key, want in expected.items():
        if key in effective and effective[key] != want:
            report["problems"].append(f"effective {key} is {effective[key]}, not {want}")
    if "repetition_penalty" not in effective:
        report["problems"].append("the server log does not show the effective repetition penalty")
    text = log_path(model).read_text(encoding="utf-8", errors="replace")
    report["server_generation_config"] = [line.split("] ", 1)[-1] for line in text.splitlines()
                                          if "generation config" in line.lower() or "generation_config" in line.lower()][:3]


def format_report(report: dict) -> str:
    if "provider_pin" in report:
        return format_endpoint_report(report)
    lines = [f"{report['backend']} at {report['base_url']} serving {report['served_model_name']!r}"]
    if "models" in report:
        lines.append(f"  models: {report['models']}")
    if "request_body" in report:
        lines.append(f"  request: {report['request_body']}")
    if "deterministic" in report:
        lines.append(f"  deterministic: {report['deterministic']}")
    if "effective_sampling" in report:
        lines.append(f"  effective sampling (server log): {report['effective_sampling']}")
    for line in report.get("server_generation_config", []):
        lines.append(f"  server: {line[:200]}")
    if report.get("server_version"):
        lines.append(f"  server version: {report['server_version']}")
    if report.get("rendered_prompt"):
        lines.append("  rendered prompt (after chat templating):")
        lines += ["    | " + line for line in report["rendered_prompt"].splitlines()]
    for note in report.get("notes", []):
        lines.append(f"  note: {note}")
    for problem in report["problems"]:
        lines.append(f"  PROBLEM: {problem}")
    lines.append("  ok" if not report["problems"] else f"  {len(report['problems'])} problem(s)")
    return "\n".join(lines)


def format_endpoint_report(r: dict) -> str:
    lines = [f"{r['backend']}: {r['model']} pinned to {r['provider_pin']}"]
    if r.get("endpoint"):
        e = r["endpoint"]
        lines.append(f"  endpoint: {e.get('provider_name')} ({e.get('tag')}), status {e.get('status')}, uptime {e.get('uptime_last_30m')}, "
                     f"quantization {e.get('quantization')}, context {e.get('context_length')}")
    if "request_body" in r:
        lines.append(f"  request: {r['request_body']}")
    if "deterministic" in r:
        lines.append(f"  same prompt twice identical: {r['deterministic']}; providers reported {r['providers_reported']}; models {r['models_reported']}")
    if "honours" in r:
        lines.append(f"  honours: {r['honours']}")
    for note in r.get("notes", []):
        lines.append(f"  note: {note}")
    for problem in r["problems"]:
        lines.append(f"  PROBLEM: {problem}")
    if "cost_usd" in r:
        lines.append(f"  cost ${r['cost_usd']:.6f}; log {r.get('log')}")
    lines.append("  ok" if not r["problems"] else f"  {len(r['problems'])} problem(s)")
    return "\n".join(lines)
