"""Run comparisons on synthetic runs: serving noise, the L1 test and the leak audit."""

import json

import pytest

from varag.eval.compare import l1, leak, noise


def write_run(root, name, rows, user_arm="knows", model="primary"):
    d = root / name
    d.mkdir()
    (d / "run.json").write_text(json.dumps({"run_id": name, "model": model, "user_arm": user_arm}), encoding="utf-8")
    (d / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return d


def row(method, iid, outcome, text="x", question=None):
    return {"method": method, "instance_id": iid, "outcome": outcome, "target": "old", "response_text": text, "question": question}


def test_noise_counts_text_and_outcome_changes(tmp_path):
    a = write_run(tmp_path, "a", [row("plain_rag", "i1", "target_only", "A"), row("plain_rag", "i2", "broken", "B")])
    b = write_run(tmp_path, "b", [row("plain_rag", "i1", "target_only", "A"), row("plain_rag", "i2", "portable", "C")])
    r = noise(a, b)
    assert (r["pairs"], r["text_changed"], r["outcome_changed"]) == (2, 1, 1)


def test_l1_compares_plain_rag_only(tmp_path):
    a = write_run(tmp_path, "a", [row("plain_rag", "i1", "target_only"), row("plain_rag", "i2", "target_only"), row("va_rag", "i1", "broken")])
    b = write_run(tmp_path, "b", [row("plain_rag", "i1", "broken", "y"), row("plain_rag", "i2", "target_only")], model="primary_genconfig")
    r = l1(a, b)
    assert r["instances"] == 2 and r["pinned"]["pass_rate"] == 1.0 and r["genconfig"]["pass_rate"] == 0.5
    assert (r["pass_to_fail"], r["fail_to_pass"], r["responses_differ"]) == (1, 0, 1)


def test_leak_fails_when_the_leak_arm_passes_more(tmp_path):
    lk = write_run(tmp_path, "lk", [row("va_rag", "i1", "target_only", question="q"), row("va_rag", "i2", "target_only", question="q")], user_arm="leak_audit")
    un = write_run(tmp_path, "un", [row("va_rag", "i1", "target_only"), row("va_rag", "i2", "broken")], user_arm="unsure")
    assert not leak(lk, un)["passed"]
    assert leak(lk, un, tolerance=0.5)["passed"]
    with pytest.raises(ValueError):
        leak(un, lk)
