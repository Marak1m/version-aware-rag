"""Repeats per instance (user decision 2026-10-21): the cache key, the metrics (an instance's score
is the mean over its repeats; the bootstrap resamples concepts), repeat disagreement, the final
sweep's plan and refusals, and the combined summary on synthetic runs."""

import json

from varag.eval.metrics import comparisons, compute, detectable_effect_table, intervals, repeat_disagreement, share
from varag.llm.client import cache_key


def test_repeat_zero_keeps_the_old_key_and_other_repeats_differ():
    args = ("small", "m@p", [{"role": "user", "content": "x"}], {"temperature": 0})
    assert cache_key(*args) == cache_key(*args, repeat=0)
    assert len({cache_key(*args, repeat=r) for r in range(3)}) == 3


def row(cid, iid, method, repeat, passed, text="t", target="old", condition="no-clue"):
    outcome = "target_only" if passed else "wrong_version"
    return {"instance_id": iid, "concept_id": cid, "library": "pandas", "target": target, "condition": condition, "kind": "ambiguous", "method": method,
            "repeat": repeat, "outcome": outcome, "outcome_strict": outcome, "outcome_lenient": outcome, "intended_pass": passed, "soft_fail": False,
            "response_text": text, "question": None, "answers_returned": 1, "calls": 1, "code": "x = 1\n", "exec": {}}


def repeated_rows():
    rows = []
    # c1: two instances; i1 passes in 2 of 3 repeats under va_rag, i2 always; plain_rag fails i1 always, passes i2 once.
    for r, (a, b, c, d) in enumerate(((1, 1, 0, 1), (1, 1, 0, 0), (0, 1, 0, 0))):
        rows += [row("c1", "c1/old/no-clue", "va_rag", r, bool(a), text=f"v{a}"), row("c1", "c1/new/no-clue", "va_rag", r, bool(b), target="new"),
                 row("c1", "c1/old/no-clue", "plain_rag", r, bool(c)), row("c1", "c1/new/no-clue", "plain_rag", r, bool(d), target="new")]
    for r in range(3):
        rows += [row("c2", "c2/old/no-clue", "va_rag", r, True), row("c2", "c2/old/no-clue", "plain_rag", r, False)]
    return rows


def test_rates_are_means_of_instance_scores():
    rows = repeated_rows()
    va = [r for r in rows if r["method"] == "va_rag"]
    assert abs(share(va, lambda r: r["intended_pass"]) - (2 / 3 + 1 + 1) / 3) < 1e-12
    iv = intervals(va, lambda r: r["intended_pass"])
    assert iv["n"] == 3 and iv["concepts"] == 2 and abs(iv["estimate"] - (2 / 3 + 1 + 1) / 3) < 1e-12


def test_mcnemar_uses_repeat_zero_and_the_bootstrap_uses_instance_scores():
    comp = comparisons(repeated_rows(), baselines=("plain_rag",))["plain_rag"]["intended_pass"]
    # Repeat 0: va_rag passes c1/old, c1/new, c2/old; plain_rag passes c1/new only.
    assert comp["discordant"] == {"reference_only": 2, "baseline_only": 0}
    # Per-concept differences of instance scores: c1 ((2/3 - 0) + (1 - 1/3)) / 2 = 2/3; c2 1.
    assert abs(comp["difference"] - (2 / 3 + 1) / 2) < 1e-12


def test_detectable_effect_counts_instances_not_rows():
    de = detectable_effect_table(repeated_rows())
    assert de["n_instances"] == 3 and de["repeats"] == 3 and de["concepts"] == 2
    assert any(r.get("measured_rho") for r in de["rows"]) and any(r.get("assumed") for r in de["rows"])
    # Observed discordance: mean squared difference of paired instance scores against va_rag.
    expected = ((2 / 3) ** 2 + (2 / 3) ** 2 + 1) / 3
    assert abs(de["discordant_observed"] - expected) < 1e-12


def test_repeat_disagreement():
    rd = repeat_disagreement(repeated_rows())
    assert rd["pairs"] == 6 and rd["repeats"] == 3
    # Texts differ only for va_rag c1/old (v1, v1, v0); outcomes differ there and for plain_rag c1/new (pass, fail, fail).
    assert abs(rd["text_differs"] - 1 / 6) < 1e-12 and abs(rd["outcome_differs"] - 2 / 6) < 1e-12
    assert repeat_disagreement([r for r in repeated_rows() if r["repeat"] == 0]) == {"pairs": 0}


def write_run(directory, run_id, model, split, arm, rows):
    run_dir = directory / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    (run_dir / "run.json").write_text(json.dumps({"run_id": run_id, "model": model, "split": split, "user_arm": arm, "instances": 3, "repeats": [0, 1, 2],
                                                  "concepts": {"c1": {}, "c2": {}}, "backend": {"type": "openrouter", "model": "m"},
                                                  "cost_usd": 0.5, "wall_seconds": 60, "session": "phala@x"}), encoding="utf-8")
    return run_dir


def test_metrics_on_a_repeated_run(tmp_path):
    run_dir = write_run(tmp_path, "r1", "small", "test", "knows", repeated_rows())
    m = compute(run_dir)
    assert m["methods"]["va_rag"]["n_targeted"] == 3 and m["methods"]["va_rag"]["n_rows"] == 9
    assert m["repeat_disagreement"]["pairs"] == 6


def test_final_items_and_refusals(monkeypatch):
    import varag.sweep as sw

    small = sw.final_items("small", ["knows", "unsure"])
    mid = sw.final_items("mid", ["knows", "unsure"])
    assert [i["name"] for i in small] == ["dev-knows", "dev-unsure", "test-knows", "test-unsure"] and small[0]["repeats"] == [0, 1, 2]
    assert [i["name"] for i in mid] == ["dev-knows", "dev-noise-repeat", "dev-unsure", "test-knows", "test-unsure"]
    assert mid[1]["repeats"] == [1] and len(mid[1]["instance_ids"]) == 20 and mid[0]["repeats"] == [0]
    monkeypatch.setattr(sw, "code_changes", lambda: ["src/varag/x.py"])
    assert any("code is not frozen" in p for p in sw.final_refusals())
    record = sw.final_sweep(dry_run=True, log=lambda _: None)
    assert not record["ok"] and "code is not frozen" in record["error"]


def test_combined_summary_on_synthetic_runs(tmp_path, monkeypatch):
    import varag.eval.run as run_module
    import varag.eval.summary as summary_module

    rows = repeated_rows()
    for r in rows:
        r.update(exclusivity="removal", change_type="symbol_rename", model="small")
    rows += [{**r, "method": "va_rag_portable_first"} for r in rows if r["method"] == "va_rag"]
    monkeypatch.setattr(run_module, "runs_dir", lambda: tmp_path)
    monkeypatch.setattr(summary_module, "results_dir", lambda stamp: tmp_path / f"final-{stamp}")
    for name, split, arm in (("test-knows", "test", "knows"), ("test-unsure", "test", "unsure"), ("dev-knows", "dev", "knows")):
        write_run(tmp_path, f"run-{name}", "small", split, arm, rows)
    record = {"stamp": "20261021T000000Z", "git_commit": "abc", "max_usd": 20, "failures": ["large: test-knows stopped: budget"],
              "models": {"small": {"session": "phala@x", "items": [{"repeats": [0, 1, 2]}], "endpoint_check": {"cost_usd": 0.001},
                                   "runs": {"test-knows": "run-test-knows", "test-unsure": "run-test-unsure", "dev-knows": "run-dev-knows"}}}}
    path = summary_module.write_final(record, log=lambda _: None)
    text = path.read_text(encoding="utf-8")
    for heading in ("primary score (strict on deprecation concepts", "strict on every concept", "lenient", "Portable first", "measured rho", "By library", "By class", "By change type", "By clue type",
                    "By user arm", "Within-session repeat disagreement", "What failed or was interrupted", "budget"):
        assert heading in text, heading
    data = json.loads((path.parent / "summary.json").read_text(encoding="utf-8"))
    assert data["models"]["small"]["runs"]["test-knows"]["methods"]["va_rag"]["n_instances"] == 3
    assert (path.parent / "small.md").exists() and (path.parent / "audit_sample.jsonl").exists()
    assert abs(data["cost_usd"] - 1.5) < 1e-9          # no ledger calls for this session: the runs' own costs
    for heading in ("## Limitations", "## Guard and detector accuracy", "not labelled yet", "utility c=0.3"):
        assert heading in text, heading
    # The audit sample is drawn once: a second summary keeps it and reads its hand labels.
    sample = path.parent / "audit_sample.jsonl"
    labelled = [{**json.loads(line), "label": {"mixes_versions": "yes"}} for line in sample.read_text(encoding="utf-8").splitlines()]
    sample.write_text("\n".join(json.dumps(r) for r in labelled) + "\n", encoding="utf-8")
    text = summary_module.write_final(record, log=lambda _: None).read_text(encoding="utf-8")
    assert all(json.loads(line)["label"]["mixes_versions"] == "yes" for line in sample.read_text(encoding="utf-8").splitlines())
    assert "## Blend detector against hand labels" in text and "| main |" in text
