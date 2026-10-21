"""va_rag_portable_first (L16) on the mock backends and a scripted backend: the draft stands without
a question only when the guard finds no exclusive or deprecated usage; otherwise the policy asks as
va_rag does. Needs the committed corpus and diffs, not the environments."""

import pytest

from varag.bench.instances import build_instances
from varag.bench.schema import load_concepts
from varag.eval.run import library_versions, retrieval_for
from varag.inventory.build import load_diff
from varag.inventory.diff import bucket_of
from varag.llm.client import ChatResponse, make_backend
from varag.methods.registry import RunContext, get_methods
from varag.pipeline.generate import NO_QUESTION
from varag.pipeline.policy import portable_line, run_policy
from varag.pipeline.user import SimulatedUser


@pytest.fixture(scope="module")
def world():
    concepts = {c.id: c for c in load_concepts()}
    versions = library_versions()
    instances = {i.instance_id: i for i in build_instances(list(concepts.values()), versions)}
    retrieved = retrieval_for(list(instances.values()), concepts)
    return concepts, versions, instances, retrieved


def policy(world, instance_id, backend=None, arm="knows", **kwargs):
    concepts, versions, instances, retrieved = world
    inst = instances[instance_id]
    user = SimulatedUser(arm, inst.library, versions[inst.library])
    return run_policy(inst, concepts[inst.concept_id], backend or make_backend("mock_ref"), versions, retrieved[instance_id], user, **kwargs)


class Scripted:
    """Answers each request with the next scripted reply and keeps the requests."""

    name = "scripted"

    def __init__(self, *replies):
        self.replies = list(replies)
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        return ChatResponse(self.replies.pop(0) if len(self.replies) > 1 else self.replies[0], model="scripted")


def test_portable_control_is_answered_by_the_draft_without_a_question(world):
    result = policy(world, "ctl-pyd-001/control", portable_first=True)
    assert result.decision.kind == "UNCERTAIN" and result.by == "portable" and result.question is None and result.calls == 1
    assert result.portable["accepted"] and result.portable["violations"] == []
    assert result.answers[0].side is None and result.answers[0].code
    base = policy(world, "ctl-pyd-001/control")            # va_rag asks on the same instance
    assert base.question and base.portable is None


def test_draft_with_an_exclusive_symbol_falls_back_to_the_question(world):
    result = policy(world, "pd-001/new/no-clue", portable_first=True)
    assert not result.portable["accepted"] and [v["symbol"] for v in result.portable["violations"]] == ["pandas.DataFrame.map"]
    assert result.by == "asked" and result.question and result.calls == 2 and result.answers[0].side == "new"
    unsure = policy(world, "pd-001/new/no-clue", arm="unsure", portable_first=True)
    assert unsure.by == "both" and unsure.calls == 3 and [a.side for a in unsure.answers] == ["old", "new"]


def test_inferred_and_no_conflict_paths_make_no_draft(world):
    for instance_id in ("pd-001/old/clue-pin", "ctl-np-001/control"):
        result = policy(world, instance_id, portable_first=True)
        base = policy(world, instance_id)
        assert result.portable is None and result.by == base.by and result.calls == base.calls


def test_draft_prompt_has_only_shared_same_chunks_and_the_portable_line(world):
    concepts, versions, instances, _ = world
    inst = instances["np-001/old/no-clue"]
    clean = f"```python\nimport numpy as np\n\ndef {inst.entry_point}(*args, **kwargs):\n    return np.sum(args[0])\n```"
    backend = Scripted(clean)
    result = policy(world, "np-001/old/no-clue", backend=backend, portable_first=True)
    assert result.by == "portable" and result.question is None and len(backend.requests) == 1
    content = backend.requests[0].messages[-1]["content"]
    assert portable_line("numpy", versions["numpy"]) in content and content.rstrip().endswith(NO_QUESTION)
    assert portable_line("numpy", versions["numpy"]) == f"Use only APIs that exist in both numpy {versions['numpy']['old']} and {versions['numpy']['new']}."
    diff = load_diff("numpy")
    kept = result.portable["kept"]
    assert kept, "np-001's distractors include shared_same chunks"
    from varag.corpus.retrieve import _chunks_by_id

    for chunk_id in kept:
        version = next(v for v in versions["numpy"].values() if chunk_id.startswith(f"numpy-{v}-"))
        assert bucket_of(diff, _chunks_by_id("numpy", version)[chunk_id]["symbols"][0]) == "shared_same"
    assert "trapz" not in content.split("Documentation:")[-1].split(portable_line("numpy", versions["numpy"]))[0]


def test_a_question_or_unparsable_draft_is_rejected(world):
    concepts, versions, instances, _ = world
    inst = instances["np-001/old/no-clue"]
    code = f"```python\nimport numpy as np\n\ndef {inst.entry_point}(y, x):\n    return np.trapz(y, x)\n```"
    for draft, reason in (("QUESTION: Which NumPy version are you on?", "no code"), ("```python\ndef broken(:\n```", None)):
        backend = Scripted(draft, code)
        result = policy(world, "np-001/old/no-clue", backend=backend, portable_first=True)
        assert not result.portable["accepted"] and result.by == "asked" and len(backend.requests) == 2
        if reason:
            assert result.portable["reason"] == reason


def test_a_deprecated_usage_rejects_the_draft(world):
    concepts, versions, instances, _ = world
    inst = instances["pyd-002/new/no-clue"] if "pyd-002/new/no-clue" in instances else next(i for i in instances.values() if i.library == "pydantic" and i.condition == "no-clue")
    deprecated = f"```python\nfrom pydantic import BaseModel\n\ndef {inst.entry_point}(model: BaseModel):\n    return model.dict()\n```"
    result = policy(world, inst.instance_id, backend=Scripted(deprecated, deprecated), portable_first=True)
    assert not result.portable["accepted"] and any(v["side"] == "deprecated_in_new" for v in result.portable["violations"])
    assert result.question


def test_method_answer_and_trace(world):
    concepts, versions, instances, retrieved = world
    method = get_methods("va_rag_portable_first")[0]
    ctx = RunContext(user_arm="knows", retrieved=retrieved, concepts=concepts)
    out = method.answer(instances["ctl-pyd-001/control"], make_backend("mock_ref"), versions, ctx)
    assert out.method == "va_rag_portable_first" and out.question is None and out.calls == 1 and out.code
    assert out.trace["by"] == "portable" and out.trace["portable"]["accepted"]
    asked = method.answer(instances["pd-001/new/no-clue"], make_backend("mock_ref"), versions, ctx)
    assert asked.question and asked.calls == 2 and asked.trace["portable"]["accepted"] is False
