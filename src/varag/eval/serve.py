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


def serve_check(model: str) -> dict:
    backend = make_backend(model)
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
