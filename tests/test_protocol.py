from varag.eval.execute import ExecResult
from varag.eval.outcomes import classify, classify_control, intended_pass
from varag.pipeline.generate import extract_code, pick_labelled, version_label


def test_single_fenced_block():
    ext = extract_code("Here you go:\n```python\nimport numpy as np\n\ndef f():\n    return 1\n```\nDone.")
    assert ext.kind == "code" and ext.blocks == 1 and not ext.multi_block
    assert ext.code.startswith("import numpy as np")


def test_last_of_several_unlabelled_blocks_scores_and_counts_multi_block():
    text = "```python\nx = 1\n```\nthen\n```python\nx = 2\n```"
    ext = extract_code(text)
    assert ext.code == "x = 2" and ext.multi_block and ext.blocks == 2 and ext.labelled == {}


def test_two_labelled_blocks_split_by_label():
    text = (
        f"```python\n{version_label('pandas', '1.5.3')}\nimport pandas as pd\n```\n"
        f"```python\n{version_label('pandas', '3.0.6')}\nimport pandas as pd\n```"
    )
    ext = extract_code(text)
    assert ext.kind == "code" and not ext.multi_block and set(ext.labelled) == {"1.5.3", "3.0.6"}
    assert ext.answers_returned == 2
    assert pick_labelled(ext, "3.0.6").startswith("# --- for pandas 3.0.6")
    assert pick_labelled(ext, "1.5.9") == pick_labelled(ext, "1.5.3")   # major-version fallback
    assert pick_labelled(ext, "4.0.0") is None


def test_question_line():
    ext = extract_code("QUESTION: Which version of pandas are you on: 1.x or 3.x?")
    assert ext.kind == "question" and ext.question.startswith("Which version")


def test_bare_code_and_prose():
    assert extract_code("def f():\n    return 2\n").kind == "code"
    assert extract_code("I cannot help with that.").kind == "no_code"


def r(status, warnings=0):
    records = [{"kind": "DeprecationWarning", "category": "DeprecationWarning", "message": f"w{i}",
                "signature": f"DeprecationWarning: w{i}"} for i in range(warnings)]
    return ExecResult(env="x", status=status, warning_counts={"DeprecationWarning": warnings}, soft_warnings=records)


def test_outcomes():
    assert classify(r("pass"), r("fail")) == "target_only"
    assert classify(r("pass"), r("pass")) == "portable"
    assert classify(r("error"), r("pass")) == "wrong_version"
    assert classify(r("fail"), r("timeout")) == "broken"
    assert classify(r("pass"), r("infra_error")) == "infra_error"
    assert classify_control(r("pass"), r("pass")) == "pass_both"
    assert classify_control(r("pass"), r("error")) == "pass_one"
    assert classify_control(r("fail"), r("fail")) == "broken"
    assert intended_pass("portable") and intended_pass("target_only") and not intended_pass("wrong_version")


def test_soft_fail_needs_pass_and_a_warning():
    assert r("pass", 1).soft_fail and not r("pass").soft_fail and not r("fail", 1).soft_fail


def test_soft_fail_is_net_of_the_reference_baseline():
    result = r("pass", 2)
    assert result.soft_fail_against({"DeprecationWarning: w0"})                       # w1 remains
    assert not result.soft_fail_against({"DeprecationWarning: w0", "DeprecationWarning: w1"})
    assert result.net_soft_signatures({"DeprecationWarning: w0"}) == ["DeprecationWarning: w1"]
    assert result.soft_warning_count == 2


def test_conftest_soft_kind_and_signature():
    import importlib.util
    import os

    from varag.config import project_root

    os.environ["VARAG_WARNING_PATTERNS"] = '[{"pattern": "Valid config keys have changed"}, {"regex": "was removed in the NumPy \\\\d"}]'
    try:
        spec = importlib.util.spec_from_file_location("varag_conftest_probe", project_root() / "scripts" / "conftest_template.py")
        module = importlib.util.module_from_spec(spec)
        import warnings
        saved = (warnings.showwarning, list(warnings.filters))
        spec.loader.exec_module(module)
    finally:
        warnings.showwarning, warnings.filters[:] = saved[0], saved[1]
        del os.environ["VARAG_WARNING_PATTERNS"]

    class PydanticDeprecatedSince20(DeprecationWarning):
        pass

    assert module.soft_kind(PydanticDeprecatedSince20, "x") == "DeprecationWarning"
    assert module.soft_kind(FutureWarning, "x") == "FutureWarning"
    assert module.soft_kind(UserWarning, "Valid config keys have changed in V2:\n* 'a'") == "MigrationMessage"
    assert module.soft_kind(UserWarning, "`np.trapz` was removed in the NumPy 2.0 release") == "MigrationMessage"
    assert module.soft_kind(UserWarning, "unrelated") is None
    assert module.soft_kind(PendingDeprecationWarning, "x") is None
    assert module.signature("UserWarning", "obj <A at 0x1F2e>\n  spread") == "UserWarning: obj <A at 0x...> spread"


def test_unshare_falls_back_to_a_user_namespace(monkeypatch):
    import subprocess
    from types import SimpleNamespace

    import varag.eval.execute as ex

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd[1:-1])
        return SimpleNamespace(returncode=0 if cmd[1:-1] == ["-rn"] else 1)

    monkeypatch.setattr(ex.sys, "platform", "linux")
    monkeypatch.setattr(ex.shutil, "which", lambda name: "/usr/bin/unshare")
    monkeypatch.setattr(subprocess, "run", fake_run)
    ex._unshare_prefix.cache_clear()
    try:
        assert ex._unshare_prefix() == ["/usr/bin/unshare", "-rn"]
        assert calls == [["-n"], ["-rn"]]
    finally:
        ex._unshare_prefix.cache_clear()


def test_summary_is_sliced_by_gold_examples():
    from varag.eval.run import summarize

    def row(outcome, passed, gold_examples, target="old"):
        return {"method": "direct", "target": target, "outcome": outcome, "intended_pass": passed,
                "soft_fail": False, "gold_examples": gold_examples}

    rows = [row("target_only", True, "both"), row("wrong_version", False, "both"), row("target_only", True, "neither"),
            row("pass_both", True, "both", target=None)]
    s = summarize(rows)["direct"]
    assert s["targeted"] == 3 and s["controls"] == 1
    assert s["by_gold_examples"] == {"both": {"targeted": 2, "intended_pass_rate": 0.5},
                                     "neither": {"targeted": 1, "intended_pass_rate": 1.0}}


def test_summary_reports_exclusivity_classes_separately():
    from varag.eval.run import summarize

    rows = [{"method": "direct", "target": "new", "outcome": "portable", "intended_pass": True, "soft_fail": False,
             "gold_examples": "neither", "exclusivity": "one_directional"},
            {"method": "direct", "target": "old", "outcome": "wrong_version", "intended_pass": False, "soft_fail": False,
             "gold_examples": "both", "exclusivity": "removal"}]
    s = summarize(rows)["direct"]
    assert s["by_exclusivity"] == {"one_directional": {"targeted": 1, "intended_pass_rate": 1.0},
                                   "removal": {"targeted": 1, "intended_pass_rate": 0.0}}


def test_effective_sampling_parsed_from_the_vllm_request_log():
    from varag.eval.serve import parse_sampling_params

    line = ("SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.0, "
            "top_p=1.0, top_k=0, min_p=0.0, seed=1234, stop=[], max_tokens=1024, min_tokens=0)")
    assert parse_sampling_params(line) == {"repetition_penalty": 1.0, "temperature": 0.0, "top_p": 1.0, "top_k": 0, "seed": 1234,
                                           "presence_penalty": 0.0, "frequency_penalty": 0.0, "max_tokens": 1024}


def test_logged_sampling_params_extracts_balanced_text(tmp_path, monkeypatch):
    import varag.serving as serving

    monkeypatch.setattr(serving, "log_path", lambda model: tmp_path / "x.log")
    (tmp_path / "x.log").write_text("INFO 10-19 x Received request chatcmpl-1: params: SamplingParams(n=1, stop=[], repetition_penalty=1.1), lora: None\n")
    assert serving.logged_sampling_params("primary") == ["SamplingParams(n=1, stop=[], repetition_penalty=1.1)"]


def test_model_default_profile_sends_only_length_and_seed():
    from varag.llm.client import ChatRequest, OpenAIChatBackend, default_params

    spec = {"base_url": "http://x/v1", "model": "m", "served_model_name": "m", "server": "vllm", "sampling_profile": "model_default"}
    body = OpenAIChatBackend("b", spec).body(ChatRequest([{"role": "user", "content": "hi"}], default_params()))
    assert set(body) == {"model", "messages", "max_tokens", "seed"}
    pinned = OpenAIChatBackend("b", {**spec, "sampling_profile": None}).body(ChatRequest([], default_params()))
    assert pinned["repetition_penalty"] == 1.0 and pinned["temperature"] == 0.0 and pinned["top_p"] == 1.0
