"""M6 on the mocks: every method completes, the guard triggers on mock_blend and abstains on a
generic .append(), a cached rerun makes zero model calls. Needs the committed corpus and diffs,
not the environments."""

import json

import pytest

from varag.bench.instances import build_instances
from varag.bench.schema import load_concepts
from varag.eval.run import library_versions, retrieval_for
from varag.inventory.build import load_diff
from varag.llm.client import ChatRequest, OpenAIChatBackend, ResponseCache, make_backend
from varag.llm.mock import blend_line
from varag.methods.registry import RunContext, all_methods, get_methods
from varag.pipeline.guard import BlendGuard, blend_static, violations
from varag.pipeline.signals import static_usages


@pytest.fixture(scope="module")
def world():
    concepts = {c.id: c for c in load_concepts()}
    versions = library_versions()
    instances = {i.instance_id: i for i in build_instances(list(concepts.values()), versions)}
    retrieved = retrieval_for(list(instances.values()), concepts)
    return concepts, versions, instances, retrieved


def test_every_method_completes_on_mock_ref(world):
    concepts, versions, instances, retrieved = world
    backend = make_backend("mock_ref")
    ctx = RunContext(user_arm="knows", retrieved=retrieved, concepts=concepts, guard=BlendGuard(backend, versions))
    methods = get_methods("all")
    assert {m.id for m in methods} >= {"no_retrieval", "plain_rag", "mind_version", "assume_state", "two_branch", "always_ask",
                                       "oracle_docs", "va_rag", "va_rag_no_infer", "va_rag_no_ask", "va_rag_no_guard"}
    for method in methods:
        for iid in ("pd-001/old/clue-pin", "np-001/new/no-clue", "pyd-001/old/stated", "ctl-np-001/control"):
            out = method.answer(instances[iid], backend, versions, ctx)
            inst = instances[iid]
            expected = concepts[inst.concept_id].reference(concepts[inst.concept_id].native_ref(inst.target) if inst.target else "portable").strip()
            assert out.code and out.code.strip() == expected, (method.id, iid, out.code)
            assert out.calls >= 1 and out.response_text


def test_two_branch_returns_two_labelled_answers_on_conflict(world):
    concepts, versions, instances, retrieved = world
    ctx = RunContext(retrieved=retrieved, concepts=concepts)
    out = all_methods()["two_branch"]().answer(instances["pd-001/new/no-clue"], make_backend("mock_ref"), versions, ctx)
    assert out.answers_returned == 2 and set(out.labelled) == {"old", "new"} and out.calls == 2
    control = all_methods()["two_branch"]().answer(instances["ctl-np-001/control"], make_backend("mock_ref"), versions, ctx)
    assert control.answers_returned == 1


def test_mock_ask_and_baselines_that_ask(world):
    concepts, versions, instances, retrieved = world
    ctx = RunContext(user_arm="knows", retrieved=retrieved, concepts=concepts)
    out = all_methods()["plain_rag"]().answer(instances["pd-001/new/no-clue"], make_backend("mock_ask"), versions, ctx)
    assert out.question and out.calls == 2 and out.code.strip() == concepts["pd-001"].reference("new").strip()
    suppressed = all_methods()["assume_state"]().answer(instances["pd-001/new/no-clue"], make_backend("mock_ask"), versions, ctx)
    assert suppressed.code is None and suppressed.trace.get("question_suppressed")


def test_blend_line_uses_the_new_gold_through_its_package():
    assert blend_line("numpy.trapezoid") == "import numpy\n_blend = numpy.trapezoid"
    assert blend_line("pydantic.Field(pattern)") == "import pydantic\n_blend = pydantic.Field(pattern=None)"
    assert blend_line('pandas.date_range(freq="ME")') == "import pandas\n_blend = pandas.date_range(freq='ME')"


def test_guard_triggers_on_mock_blend_and_the_repair_is_accepted(world):
    concepts, versions, instances, retrieved = world
    backend = make_backend("mock_blend")
    guard = BlendGuard(backend, versions)
    inst = instances["np-001/old/clue-pin"]
    blended = backend.complete(ChatRequest([{"role": "user", "content": "x"}], {}, {"concept_dir": inst.concept_dir, "target": "old"})).text
    code = blended.split("```python\n", 1)[1].rsplit("```", 1)[0]
    usages = static_usages(code, load_diff("numpy"))
    assert blend_static(usages)
    assert [v["symbol"] for v in violations(usages, "old")] == ["numpy.trapezoid"]
    fixed, info = guard(code, "old", {"instance": inst, "library": "numpy", "version": "1.26.4"})
    assert info["flagged"] and info["regenerated"] and info["accepted"] and info["outcome"] == "fixed"
    assert fixed.strip() == concepts["np-001"].reference("old").strip() and info["pre_guard_code"] == code
    # Through va_rag: the guard runs inside the policy; the ablation skips it.
    ctx = RunContext(user_arm="knows", retrieved=retrieved, concepts=concepts, guard=guard)
    out = all_methods()["va_rag"]().answer(inst, backend, versions, ctx)
    assert out.code.strip() == concepts["np-001"].reference("old").strip() and out.trace["answers"][0]["guard"]["outcome"] == "fixed"
    raw = all_methods()["va_rag_no_guard"]().answer(inst, backend, versions, ctx)
    assert "numpy.trapezoid" in raw.code


def test_guard_abstains_on_generic_append_and_passes_clean_code(world):
    concepts, versions, instances, retrieved = world
    guard = BlendGuard(make_backend("mock_ref"), versions)
    inst = instances["pd-001/old/clue-pin"]
    code = "import pandas as pd\n\ndef f(rows):\n    out = []\n    out.append(rows)\n    return pd.DataFrame(out)\n"
    kept, info = guard(code, "new", {"instance": inst, "library": "pandas", "version": "3.0.6"})
    assert kept == code and not info["flagged"] and info["outcome"] == "clean"
    assert any("generic" in a["reason"] for a in info["abstained"])


def test_unresolved_state_flags_only_a_true_mix(world):
    diff = load_diff("numpy")
    mixed = "import numpy as np\n\ndef f(y):\n    a = np.trapz(y)\n    return np.trapezoid(y) + a\n"
    assert [v["symbol"] for v in violations(static_usages(mixed, diff), None)] == ["numpy.trapz", "numpy.trapezoid"]
    one_side = "import numpy as np\n\ndef f(y):\n    return np.trapz(y)\n"
    assert violations(static_usages(one_side, diff), None) == []
    assert [v["symbol"] for v in violations(static_usages(one_side, diff), "new")] == ["numpy.trapz"]


def test_openai_backend_caches_and_a_rerun_makes_no_call(tmp_path, monkeypatch):
    spec = {"type": "openai_chat", "model": "m", "revision": "r", "base_url": "http://localhost:1/v1", "server": "vllm"}
    backend = OpenAIChatBackend("fake", spec, cache=ResponseCache(tmp_path))
    calls = []

    def fake_request(method, path, body=None, attempts=3):
        calls.append((method, path, body))
        return {"model": "m", "choices": [{"message": {"content": "```python\ndef f():\n    return 1\n```"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 9}}

    monkeypatch.setattr(backend, "_request", fake_request)
    request = ChatRequest([{"role": "user", "content": "hi"}], {"temperature": 0.0, "top_p": 1.0, "max_tokens": 16, "seed": 1, "repetition_penalty": 1.0, "n": 1})
    first = backend.complete(request)
    assert not first.cached and first.text.startswith("```python") and len(calls) == 1
    assert calls[0][2]["repetition_penalty"] == 1.0 and calls[0][2]["seed"] == 1 and calls[0][2]["temperature"] == 0.0
    second = backend.complete(request)
    assert second.cached and second.text == first.text and len(calls) == 1
    log = [json.loads(l) for l in (tmp_path / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(log) == 1 and log[0]["backend"] == "fake"
    llama = OpenAIChatBackend("tiny", {**spec, "server": "llama_cpp"}, cache=ResponseCache(tmp_path))
    assert "repeat_penalty" in llama.body(request) and "repetition_penalty" not in llama.body(request)
