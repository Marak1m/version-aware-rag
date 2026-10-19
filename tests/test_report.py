"""Metrics and the report on a small synthetic run directory."""

import json

from varag.eval.audit import audit_sample
from varag.eval.metrics import compute
from varag.eval.report import render, write_report


def make_run(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    rows, traces = [], []
    concepts = {"pd-001": "pandas", "np-001": "numpy", "pyd-001": "pydantic"}
    for method, pass_pattern in (("va_rag", (1, 1, 1, 0)), ("plain_rag", (1, 0, 0, 0))):
        for cid, lib in concepts.items():
            for i, (target, cond) in enumerate((("old", "no-clue"), ("old", "clue"), ("new", "no-clue"), ("new", "clue"))):
                passed = bool(pass_pattern[i])
                iid = f"{cid}/{target}/{cond}"
                asked = method == "va_rag" and cond == "no-clue"
                rows.append({"instance_id": iid, "concept_id": cid, "library": lib, "target": target, "condition": cond, "kind": "ambiguous",
                             "clue_type": "pin" if cond == "clue" else None, "method": method, "outcome": "target_only" if passed else "wrong_version",
                             "outcome_strict": "target_only" if passed else "wrong_version", "outcome_lenient": "target_only" if passed else "wrong_version",
                             "intended_pass": passed, "soft_fail": False, "blend_static": not passed and method == "plain_rag", "blend_exec": False,
                             "guarded_portable": False, "question": "Which version?" if asked else None, "answers_returned": 1, "calls": 2 if asked else 1,
                             "code": "import numpy as np\nx = np.trapz([1])\n" if lib == "numpy" else "x = 1\n",
                             "exec": {"old": {"status": "pass"}, "new": {"status": "fail", "exc_type": "AttributeError", "last_line": "AttributeError: module 'numpy' has no attribute 'trapz'"}},
                             "exclusivity": "removal", "change_type": "symbol_rename", "gold_examples": "both", "user_arm": "knows"})
                traces.append({"instance_id": iid, "method": method, "retrieval": {"target_gold_first": i % 2 == 0},
                               "method_trace": {"decision": {"kind": "INFER" if cond == "clue" else "UNCERTAIN", "side": target if cond == "clue" else None, "margin": 3.0 if cond == "clue" else 0.0},
                                                "question_relevant": True if asked else None,
                                                "answers": [{"side": target, "guard": {"flagged": not passed, "outcome": "guard_rejected" if not passed else "clean"}}]} if method == "va_rag" else {}})
        rows.append({"instance_id": "ctl-np-001/control", "concept_id": "ctl-np-001", "library": "numpy", "target": None, "condition": "control", "kind": "control",
                     "method": method, "outcome": "pass_both", "intended_pass": True, "soft_fail": False, "question": None, "answers_returned": 1, "calls": 1, "code": "x = 1\n", "exec": {}})
    (run_dir / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("\n".join(json.dumps(t) for t in traces) + "\n", encoding="utf-8")
    (run_dir / "run.json").write_text(json.dumps({"run_id": "run-1", "model": "mock_ref", "split": "dev", "user_arm": "knows", "instances": 13,
                                                  "concepts": {c: {} for c in concepts}, "backend": {"type": "mock"}, "reportable": True,
                                                  "scoring": {"deprecation": {"primary": "strict"}}}), encoding="utf-8")
    return run_dir


def test_metrics_and_report(tmp_path):
    run_dir = make_run(tmp_path)
    metrics = compute(run_dir)
    va, plain = metrics["methods"]["va_rag"], metrics["methods"]["plain_rag"]
    assert va["n_targeted"] == 12 and va["intended_pass_rate"]["estimate"] == 0.75 and plain["intended_pass_rate"]["estimate"] == 0.25
    assert va["intended_pass_rate"]["bootstrap"][0] <= 0.75 <= va["intended_pass_rate"]["bootstrap"][1]
    assert va["ask_recall"] == 1.0 and va["ask_precision"] == 1.0 and va["over_ask_rate"] == 0.0 and plain["ask_recall"] == 0.0
    assert va["inference_coverage"] == 1.0 and va["inference_precision"] == 1.0 and va["decisions"] == {"INFER": 6, "UNCERTAIN": 6}
    assert va["guard"]["flagged"] == 3 and va["cost"]["calls_per_instance"] > plain["cost"]["calls_per_instance"]
    assert plain["blend_static"]["estimate"] == 0.75
    assert va["order_sensitivity"] is not None
    assert va["slices"]["library"]["numpy"]["n"] == 4 and "both / symbol_rename" in va["slices"]["gold_examples_x_change_type"]
    comp = metrics["comparisons"]["plain_rag"]["intended_pass"]
    assert comp["difference"] == 0.5 and comp["discordant"] == {"reference_only": 6, "baseline_only": 0}
    # Exact McNemar with 6 discordant pairs all one way: 2 / 2**6; Holm over the two contrasts doubles it.
    assert comp["mcnemar_p"] == 2 / 64 and comp["mcnemar_p_holm"] == 4 / 64
    de = metrics["detectable_effect"]
    assert de["n_instances"] == 12 and de["per_concept"] == 4 and len(de["rows"]) >= 3
    path = write_report(run_dir)
    text = path.read_text(encoding="utf-8")
    assert "## Primary metrics" in text and "va_rag" in text and "smoke-test readings" in text and "Holm p" in text
    assert (run_dir / "metrics.json").exists()
    sample = audit_sample(run_dir, n=5, seed=1)
    lines = sample.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 5 and {json.loads(l)["method"] for l in lines} == {"va_rag", "plain_rag"}
    assert (run_dir / "audit_sample.md").exists()


def test_render_marks_unreportable_runs(tmp_path):
    run_dir = make_run(tmp_path)
    metrics = compute(run_dir)
    metrics["reportable"] = False
    assert "Not for reporting" in render(metrics, json.loads((run_dir / "run.json").read_text(encoding="utf-8")))
