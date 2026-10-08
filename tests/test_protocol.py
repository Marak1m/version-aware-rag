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
    return ExecResult(env="x", status=status, warning_counts={"DeprecationWarning": warnings})


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
