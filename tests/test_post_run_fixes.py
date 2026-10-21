"""Metric corrections after the final sweep (2026-10-21): "test failed, then pytest crashed while
reporting" is a failure; the strict-named guard oracle; hand-label scoring of the audit sample."""

import json

from varag.eval.audit import score_labels
from varag.eval.execute import crashed_after_failure, reclassify
from varag.eval.oracle import Evidence, evidence, strict_named, usage_evidenced

CRASH_TAIL = ("INTERNALERROR>   File \"pydantic/error_wrappers.py\", line 63, in pydantic.error_wrappers.ValidationError.errors\n"
              "INTERNALERROR> AttributeError: 'list' object has no attribute '__pydantic_model__'\n\n"
              "!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!\n1 failed in 0.01s\n")


def test_a_crash_after_a_failed_test_is_a_failure():
    assert crashed_after_failure(3, 3, CRASH_TAIL)
    assert not crashed_after_failure(3, 3, "INTERNALERROR> boom\n")          # no failed test: still infra
    assert not crashed_after_failure(3, 0, CRASH_TAIL)                       # nothing collected
    assert not crashed_after_failure(2, 3, CRASH_TAIL)
    stored = {"status": "infra_error", "exit_code": 3, "collected": 3, "infra_reason": "pytest exit code 3", "output_tail": CRASH_TAIL,
              "exc_type": None, "last_line": None}
    fixed = reclassify(stored)
    assert fixed["status"] == "error" and fixed["infra_reason"] is None and fixed["reclassified"]["from"] == "infra_error"
    assert fixed["last_line"].startswith("pytest crashed while reporting a failed test: AttributeError")
    assert reclassify({**stored, "output_tail": "INTERNALERROR> x\n"}) is None and reclassify({**stored, "status": "error"}) is None


def test_rescore_row_turns_the_crash_into_broken():
    from varag.bench.schema import load_concepts
    from varag.eval.run import rescore_row

    concept = next(c for c in load_concepts() if c.id == "pyd-021")
    crash = {"env": "pydantic_old", "status": "infra_error", "exit_code": 3, "collected": 3, "infra_reason": "pytest exit code 3",
             "output_tail": CRASH_TAIL, "exc_type": None, "last_line": None, "soft_warnings": [], "warning_counts": {}}
    error = {"env": "pydantic_new", "status": "error", "exit_code": 1, "collected": 3, "exc_type": "AttributeError",
             "last_line": "AttributeError: x", "output_tail": "", "soft_warnings": [], "warning_counts": {}}
    row = {"instance_id": "pyd-021/old/clue-error", "concept_id": "pyd-021", "library": "pydantic", "split": "test", "kind": "ambiguous",
           "target": "old", "condition": "clue", "query": concept.query, "context": "", "concept_dir": str(concept.directory),
           "entry_point": concept.entry_point, "scoring": "strict", "code": "def f():\n    pass\n", "defines_entry_point": True,
           "exec": {"old": dict(crash), "new": dict(error)}, "outcome": "infra_error", "outcome_strict": "infra_error",
           "outcome_lenient": "infra_error", "intended_pass": False}
    assert rescore_row(row, concept) == ["old"]
    assert row["outcome"] == row["outcome_strict"] == row["outcome_lenient"] == "broken" and row["intended_pass"] is False
    assert row["outcome_before_rescore"] == "infra_error" and row["exec"]["old"]["reclassified"]["from"] == "infra_error"
    assert rescore_row(row, concept) == []                                   # idempotent


def ev(**kw):
    base = {"failed": True, "error": "", "trace": "", "warnings": [], "lines": []}
    return Evidence(**{**base, **kw})


def test_strict_named_sees_values_keywords_and_deprecations():
    q = ev(error="ValueError: Invalid frequency: Q. Failed to parse with error message: ValueError(\"'Q' is no longer supported\")")
    assert usage_evidenced("pandas.DataFrame.resample(rule='Q')", q)
    assert not usage_evidenced("pandas.DataFrame.resample(rule='QE')", q)
    copy = ev(error="ValueError: Unable to avoid copy while creating an array as requested.", lines=["    return np.array(x, copy=False)"])
    assert usage_evidenced("numpy.array(copy=False)", copy) and not usage_evidenced("numpy.array(copy=None)", copy)
    kw = ev(error="TypeError: to_datetime() got an unexpected keyword argument 'infer_datetime_format'")
    assert usage_evidenced("pandas.to_datetime(infer_datetime_format)", kw)
    dep = ev(warnings=["PydanticDeprecatedSince20: The `schema` method is deprecated; use `model_json_schema` instead."])
    assert usage_evidenced("pydantic.BaseModel.schema", dep) and not usage_evidenced("pydantic.BaseModel.dict", dep)
    assert not strict_named(ev(failed=False, warnings=dep.warnings), ["pydantic.BaseModel.schema"])
    assert not usage_evidenced("pydantic.BaseModel.dict", ev(error="the result was not a dict of floats"))   # a bare word in prose


def test_evidence_reads_the_failing_line_but_not_for_the_answers_own_errors():
    code = "import numpy as np\n\ndef f(x):\n    return np.array(x, copy=False)\n"
    rec = {"status": "error", "exc_type": "ValueError", "last_line": "ValueError: Unable to avoid copy", "output_tail": "solution.py:4: in f\n    return np.array(x, copy=False)\nE   ValueError: Unable to avoid copy\n"}
    e = evidence(code, rec, [])
    assert e.failed and e.lines == ["    return np.array(x, copy=False)"] and usage_evidenced("numpy.array(copy=False)", e)
    own = evidence(code, {**rec, "exc_type": "NameError", "last_line": "NameError: name 'np' is not defined"}, [])
    assert own.lines == [] and not usage_evidenced("numpy.array(copy=False)", own)
    assert evidence(code, {"status": "pass"}, ["DeprecationWarning: x"]).failed           # a strict failure through a warning
    assert not evidence(code, {"status": "infra_error"}, []).failed


def test_audit_scoring_from_hand_labels(tmp_path):
    path = tmp_path / "audit_sample.jsonl"
    recs = []
    for i in range(4):
        recs.append({"stratum": "detector_flagged", "stratum_population": 20, "detector": {"flagged": True}, "label": {"mixes_versions": "yes" if i < 3 else "no"}})
    for i in range(4):
        recs.append({"stratum": "detector_clean", "stratum_population": 400, "detector": {"flagged": False}, "label": {"mixes_versions": "yes" if i == 0 else ("no" if i < 3 else None)}})
    path.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    s = score_labels(path)
    assert s["labelled"] == 7 and not s["complete"] and s["precision"] == 0.75 and s["precision_n"] == 4
    # caught: 20/4 * 3 = 15; missed: 400/3 * 1 = 133.3; recall = 15 / 148.3
    assert abs(s["recall"] - 15 / (15 + 400 / 3)) < 1e-12
    path.write_text("\n".join(json.dumps({**r, "label": {"mixes_versions": None}}) for r in recs) + "\n", encoding="utf-8")
    assert score_labels(path)["labelled"] == 0 and score_labels(path)["precision"] is None
