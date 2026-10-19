"""OpenRouter backend, prompt-review protocol pieces and the logbook, without network calls."""

import pytest

from varag.llm.client import Budget, BudgetExceeded, ChatRequest, OpenRouterBackend, default_params
from varag.logbook import redact
from varag.pipeline.generate import NO_QUESTION, after_reply, defines_entry_point, finish_prompt, signature_stub

SPEC = {"type": "openrouter", "model": "qwen/qwen3-coder", "provider": "deepinfra/turbo", "provider_name": "DeepInfra"}


def test_request_body_pins_sampling_and_one_provider():
    body = OpenRouterBackend("large", SPEC).body(ChatRequest([{"role": "user", "content": "hi"}], default_params()))
    assert (body["temperature"], body["top_p"], body["repetition_penalty"], body["max_tokens"], body["seed"]) == (0.0, 1.0, 1.0, 1024, 1234)
    assert body["provider"] == {"order": ["deepinfra/turbo"], "allow_fallbacks": False, "require_parameters": True}
    assert body["model"] == "qwen/qwen3-coder" and body["usage"] == {"include": True}


def test_provider_match_accepts_the_reported_display_name_only():
    b = OpenRouterBackend("large", SPEC)
    assert b.provider_matches("DeepInfra") and not b.provider_matches("Google") and b.provider_matches(None) is None
    assert OpenRouterBackend("x", {**SPEC, "provider": "google-vertex", "provider_name": "Google"}).provider_matches("Google")


def test_cache_key_includes_model_and_pin():
    a, b = OpenRouterBackend("large", SPEC), OpenRouterBackend("large", {**SPEC, "provider": "google-vertex"})
    assert a.cache_revision != b.cache_revision


def test_budget_refuses_the_call_after_the_cap():
    budget = Budget(0.01)
    budget.check()
    budget.add(0.011)
    with pytest.raises(BudgetExceeded):
        budget.check()
    Budget(None).check()


def test_keys_are_redacted_from_logs():
    assert "sk-or-v1-abcdef" not in redact("Authorization: Bearer sk-or-v1-abcdef0123456789")


def test_signature_stub_copies_the_query_signature():
    stub = signature_stub("Write `make_sku(code: str)` returning a model.", "make_sku")
    assert stub == "Complete this function:\n```python\ndef make_sku(code: str):\n    ...\n```"
    with pytest.raises(ValueError):
        signature_stub("Write make_sku returning a model.", "make_sku")


def test_prompt_ends_with_stub_then_the_no_question_line():
    text = finish_prompt("Task:\nWrite `f(x)` returning x.\n", "Write `f(x)` returning x.", "f", no_question=True)
    assert text.rstrip().endswith(NO_QUESTION) and "def f(x):" in text
    assert finish_prompt("Task: `f(x)`", "Write `f(x)`.", "f", no_question=False).rstrip().endswith("```")
    assert after_reply("I'm not sure.") == "I'm not sure.\n\n" + NO_QUESTION


@pytest.mark.parametrize("code,expected", [
    ("def f(x):\n    return x\n", True),
    ("from math import sqrt as f\n", True),
    ("f = lambda x: x\n", True),
    ("class Model:\n    pass\n", False),
    ("def g(x):\n    def f():\n        pass\n", False),
    ("def f(:\n", None),
])
def test_defines_entry_point(code, expected):
    assert defines_entry_point(code, "f") is expected
