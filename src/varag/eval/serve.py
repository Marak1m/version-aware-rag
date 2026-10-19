"""``varag serve check``: is the served model the configured one, with our sampling and our prompt?

Checks, per backend (handoff, "Serving configuration"):
- the server answers ``/models`` and lists the served model name;
- one completion with our system prompt and the explicit sampling block (temperature 0, top_p
  1.0, repetition penalty 1.0, fixed seed) returns code; the request body is printed, so the
  penalty we send is visible;
- the prompt after chat templating, through vLLM's tokenize and detokenize endpoints, starts with
  our system prompt and not the model's default one (reported as unavailable on llama.cpp);
- two identical uncached requests return identical text (a first serving-noise reading).
"""

from __future__ import annotations

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
    rendered = backend.rendered_prompt(messages)
    report["rendered_prompt"] = rendered
    if rendered is None:
        report["notes"] = ["the server has no tokenize endpoint: the rendered prompt could not be read (llama.cpp); check its --chat-template"]
    elif SYSTEM_PROMPT.splitlines()[0] not in rendered:
        report["problems"].append("the rendered prompt does not contain our system prompt")
    return report


def format_report(report: dict) -> str:
    lines = [f"{report['backend']} at {report['base_url']} serving {report['served_model_name']!r}"]
    if "models" in report:
        lines.append(f"  models: {report['models']}")
    if "request_body" in report:
        lines.append(f"  request: {report['request_body']}")
    if "deterministic" in report:
        lines.append(f"  deterministic: {report['deterministic']}")
    if report.get("rendered_prompt"):
        lines.append("  rendered prompt (first 300 chars): " + report["rendered_prompt"][:300].replace("\n", "\\n"))
    for note in report.get("notes", []):
        lines.append(f"  note: {note}")
    for problem in report["problems"]:
        lines.append(f"  PROBLEM: {problem}")
    lines.append("  ok" if not report["problems"] else f"  {len(report['problems'])} problem(s)")
    return "\n".join(lines)
