"""The blend-audit judge without model calls: prompt content, reply parsing, sampling, kappa, the
calibration gate and the census-plus-stratified analysis."""

import json

from varag.bench.schema import load_concepts
from varag.eval.judge import (RUBRIC, analyse, calibrate, cohen_kappa, judge_items, judge_messages, parse_verdict,
                              stratified_sample)
from varag.eval.run import library_versions
from varag.llm.client import ChatResponse


class Scripted:
    """Says "yes" when the answer contains MIX, else "no"; counts calls like the OpenRouter backend."""

    name = "scripted"
    calls = cache_hits = 0
    cost_total = 0.0

    def complete(self, request):
        code = request.messages[-1]["content"].split("Answer to judge:")[1]
        yes = "MIX" in code
        return ChatResponse(json.dumps({"mixes_versions": "yes" if yes else "no", "basis": "exclusive" if yes else "none", "reason": "r"}))


def test_prompt_holds_the_references_and_versions_and_nothing_of_the_detector():
    concept = next(c for c in load_concepts() if c.id == "pd-001")
    versions = library_versions()["pandas"]
    content = judge_messages(concept, versions, "def f():\n    pass\n")[1]["content"]
    assert f"OLD = pandas {versions['old']}" in content and f"NEW = pandas {versions['new']}" in content
    assert concept.reference("old").strip() in content and concept.reference("new").strip() in content
    for leak in ("blend", "guard", "flagged", "detector", "replacements", "diff.json"):
        assert leak not in content.lower(), leak
    assert RUBRIC in content
    one_dir = next(c for c in load_concepts() if c.one_directional)
    assert "(it also runs on OLD)" in judge_messages(one_dir, library_versions()[one_dir.library], "x = 1\n")[1]["content"]


def test_parse_verdict():
    assert parse_verdict('{"mixes_versions": "yes", "basis": "exclusive", "reason": "a + b"}')["mixes_versions"] is True
    assert parse_verdict('```json\n{"mixes_versions": "no", "basis": "none", "reason": ""}\n```')["mixes_versions"] is False
    assert parse_verdict("I think so")["parse_error"]


def test_kappa_and_sampling():
    assert cohen_kappa([True, False, True, False], [True, False, True, False]) == 1.0
    assert abs(cohen_kappa([True, True, False, False], [True, False, True, False])) < 1e-12
    clean = [{"id": f"{m}/{meth}/{i}", "model": m, "method": meth} for m in ("a", "b") for meth in ("x", "y") for i in range(10 if m == "a" else 30)]
    sample, cells = stratified_sample(clean, 20)
    assert len(sample) == 20 and cells[("a", "x")] == {"population": 10, "sample": 3} and cells[("b", "y")]["sample"] == 7
    assert stratified_sample(clean, 20)[0] == sample                       # seeded


def test_calibration_gate_and_analysis(tmp_path):
    concepts = {c.id: c for c in load_concepts()}
    versions = library_versions()
    records = [{"model": "small", "method": "va_rag", "instance_id": "pd-001/new/no-clue", "code": "MIX\n" if i < 5 else "ok\n",
                "label": {"mixes_versions": "yes" if i < 6 else "no", "basis": "exclusive"}} for i in range(50)]
    path = tmp_path / "audit_sample.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    stats, out = calibrate(path, Scripted(), concepts, versions, log=lambda _: None)
    assert stats["agree"] == 49 and stats["passed"] and len(stats["disagreements"]) == 1 and stats["kappa"] > 0.85
    # Analysis: 4 flagged (2 static, of which 1 mixes; 1 guard-only mixing; 1 clean draft), 2 clean cells.
    pop = [{"id": f"f{i}", "model": "small", "method": "va_rag", "flagged": True, "code": "x = 1\n"} for i in range(4)]
    pop += [{"id": f"c{i}", "model": "small", "method": m, "flagged": False, "code": "x = 1\n"} for m in ("va_rag", "plain_rag") for i in range(100)]
    flagged_out = [{"kind": "final", "code": "x = 1\n", "blend_static": True, "mixes_versions": True, "basis": "exclusive"},
                   {"kind": "final", "code": "x = 1\n", "blend_static": True, "mixes_versions": False, "basis": "none"},
                   {"kind": "final", "code": "x = 1\n", "blend_static": False, "mixes_versions": True, "basis": "deprecated"},
                   {"kind": "final", "code": "x = 1\n", "blend_static": False, "mixes_versions": False, "basis": "none"},
                   {"kind": "draft", "code": "x = 1\n", "blend_static": False, "mixes_versions": True, "basis": "exclusive"}]
    clean_out = [{"kind": "clean", "model": "small", "method": "va_rag", "code": "x = 1\n", "mixes_versions": i == 0, "basis": "semantic" if i == 0 else "none"} for i in range(10)]
    clean_out += [{"kind": "clean", "model": "small", "method": "plain_rag", "code": "x = 1\n", "mixes_versions": False, "basis": "none"} for _ in range(10)]
    cells = {("small", "va_rag"): {"population": 100, "sample": 10}, ("small", "plain_rag"): {"population": 100, "sample": 10}}
    a = analyse(pop, flagged_out, clean_out, cells, n_boot=200)
    main = a["variants"]["main"]
    # Positives: 2 flagged (census) + 100/10 x 1 clean = 12; caught by the static detector: 1.
    assert main["precision"] == 0.5 and abs(main["recall"] - 1 / 12) < 1e-12 and abs(main["prevalence"] - 12 / 204) < 1e-12
    assert a["variants"]["semantic counted as no"]["recall"] == 0.5 and a["variants"]["deprecated counted as no"]["recall"] == 1 / 11
    assert a["guard_drafts_yes"] == 1 and a["clean_positives"] == 1


def test_judge_items_survives_a_failing_call():
    concepts = {c.id: c for c in load_concepts()}

    class Failing(Scripted):
        def complete(self, request):
            raise RuntimeError("401")

    out = judge_items([{"id": "a", "concept": concepts["pd-001"], "versions": library_versions()["pandas"], "code": "x"}], backend=Failing(), log=lambda _: None)
    assert out[0]["mixes_versions"] is None and "401" in out[0]["error"]
