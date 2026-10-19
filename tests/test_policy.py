"""The policy on the mock backends: commit, no-conflict single answer, the ask path with each user
arm, the "both" fallback, and the ablation switches. Needs the committed corpus and diffs, not the
environments."""

import pytest

from varag.bench.instances import build_instances
from varag.bench.schema import load_concepts
from varag.eval.run import library_versions, retrieval_for
from varag.llm.client import make_backend
from varag.methods.registry import RunContext, get_methods
from varag.pipeline.policy import run_policy
from varag.pipeline.user import SimulatedUser


@pytest.fixture(scope="module")
def world():
    concepts = {c.id: c for c in load_concepts()}
    versions = library_versions()
    instances = {i.instance_id: i for i in build_instances(list(concepts.values()), versions)}
    retrieved = retrieval_for(list(instances.values()), concepts)
    return concepts, versions, instances, retrieved


def policy(world, instance_id, arm="knows", **kwargs):
    concepts, versions, instances, retrieved = world
    inst = instances[instance_id]
    user = SimulatedUser(arm, inst.library, versions[inst.library])
    return run_policy(inst, concepts[inst.concept_id], make_backend("mock_ref"), versions, retrieved[instance_id], user, **kwargs), inst


def test_clue_commits_without_a_question(world):
    result, inst = policy(world, "pd-001/old/clue-pin")
    assert result.decision.kind == "INFER" and result.decision.side == "old"
    assert result.by == "inferred" and result.question is None and result.calls == 1
    answer = result.answers[0]
    assert answer.side == "old" and answer.code == world[0]["pd-001"].reference("old").strip() + "\n" or answer.code.strip() == world[0]["pd-001"].reference("old").strip()
    assert answer.kept and all(c.startswith("pandas-1.5.3-") for c in answer.kept) and all(c.startswith("pandas-3.0.6-") for c in answer.dropped)


def test_no_conflict_control_answers_once(world):
    result, _ = policy(world, "ctl-np-001/control")
    assert result.by == "no_conflict" and result.question is None and len(result.answers) == 1 and result.answers[0].side is None


def test_no_clue_asks_and_the_knowing_user_resolves_it(world):
    result, _ = policy(world, "pd-001/new/no-clue")
    assert result.decision.kind == "UNCERTAIN" and result.by == "asked"
    assert result.question and "pandas" in result.question and result.reply.relevant
    assert result.reply.text == "I'm on pandas 3.0.6." and result.answers[0].side == "new" and result.calls == 1


def test_unsure_user_gets_two_labelled_answers(world):
    result, _ = policy(world, "pd-001/new/no-clue", arm="unsure")
    assert result.by == "both" and [a.side for a in result.answers] == ["old", "new"] and result.calls == 2
    assert all(a.code for a in result.answers)
    concepts, versions, instances, retrieved = world
    method = get_methods("va_rag")[0]
    ctx = RunContext(user_arm="unsure", retrieved=retrieved, concepts=concepts)
    out = method.answer(instances["pd-001/new/no-clue"], make_backend("mock_ref"), versions, ctx)
    assert out.answers_returned == 2 and set(out.labelled) == {"old", "new"}
    assert out.extraction.labelled and "# --- for pandas 3.0.6 ---" in out.response_text
    assert out.code.strip() == concepts["pd-001"].reference("new").strip()


def test_ablations(world):
    result, _ = policy(world, "pd-001/old/clue-pin", infer_enabled=False)
    assert result.decision.kind == "UNCERTAIN" and result.by == "asked"     # no inference: the clue is ignored, so it asks
    result, _ = policy(world, "pd-001/new/no-clue", ask_enabled=False)
    assert result.by == "unresolved" and result.question is None and result.answers[0].side is None


def test_committed_prompt_carries_the_state_and_negative_constraints(world):
    concepts, versions, instances, retrieved = world
    inst = instances["pd-001/old/clue-pin"]
    captured = {}

    class Spy:
        name = "spy"

        def complete(self, request):
            captured["content"] = request.messages[1]["content"]
            return make_backend("mock_ref").complete(request)

    user = SimulatedUser("knows", "pandas", versions["pandas"])
    result = run_policy(inst, concepts["pd-001"], Spy(), versions, retrieved[inst.instance_id], user)
    assert result.by == "inferred" and result.answers[0].side == "old"
    assert "The user is on pandas 1.5.3. Use only APIs available in that version." in captured["content"]
    assert "Documentation:" in captured["content"] and "[pandas 3.0.6" not in captured["content"]


def test_leak_audit_arm_never_answers_the_version():
    from varag.pipeline.user import SimulatedUser

    user = SimulatedUser("leak_audit", "pandas", {"old": "1.5.3", "new": "3.0.6"})
    reply = user.reply("Which version of pandas are you on: 1.x or 3.x?", "new")
    assert (reply.text, reply.relevant) == ("I'm not sure what you're asking.", False)
