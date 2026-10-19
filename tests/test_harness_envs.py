"""Harness checks that need the built environments (marked ``envs``)."""

import json
import sys

import pytest

from varag.config import project_root
from varag.eval.execute import execute, isolation_status
from varag.inventory.diff import bucket_of

pytestmark = pytest.mark.envs

TEST_PASSES = "from solution import f\n\n\ndef test_f():\n    assert f() == 1\n"


def write_test(tmp_path, text=TEST_PASSES):
    path = tmp_path / "test_solution.py"
    path.write_text(text, encoding="utf-8")
    return path


def test_pass_and_stamp(tmp_path):
    result = execute("numpy_old", "def f():\n    return 1\n", write_test(tmp_path))
    assert result.status == "pass", result.output_tail
    assert result.stamp_version == "1.26.4"
    assert result.collected == 1 and not result.soft_fail


def test_assertion_failure_vs_exception(tmp_path):
    assert execute("numpy_old", "def f():\n    return 2\n", write_test(tmp_path)).status == "fail"
    result = execute("numpy_new", "import numpy as np\n\ndef f():\n    return np.trapz([1, 2], [0, 1])\n", write_test(tmp_path))
    assert result.status == "error" and result.exc_type == "AttributeError", result.last_line
    assert "trapz" in result.last_line


def test_import_time_error_is_error_not_infra(tmp_path):
    result = execute("pydantic_new", "from pydantic import BaseModel, Field\n\nclass M(BaseModel):\n    x: str = Field(regex='a')\n\ndef f():\n    return 1\n", write_test(tmp_path))
    assert result.status == "error", result.output_tail
    assert result.exc_type and result.exc_type != "AssertionError"


SOFT_FAIL_FIXTURES = {
    # V1 method called during the test: warning fires at call time.
    "dict_call": ("from pydantic import BaseModel\n\nclass M(BaseModel):\n    x: int\n\n"
                  "def f():\n    return len(M(x=1).dict())\n", "DeprecationWarning", "`dict` method is deprecated"),
    # V1 decorator at module level: warning fires while solution.py is imported.
    "module_level_validator": ("from pydantic import BaseModel, validator\n\nclass M(BaseModel):\n    x: int\n\n"
                               "    @validator('x')\n    def check(cls, v):\n        return v\n\n"
                               "def f():\n    return M(x=1).x\n", "DeprecationWarning", "`@validator` validators are deprecated"),
    # Class-based Config with a key that is valid in V2, so only the class-based deprecation fires.
    "class_based_config": ("from pydantic import BaseModel\n\nclass M(BaseModel):\n    x: str\n\n"
                           "    class Config:\n        str_strip_whitespace = True\n\n"
                           "def f():\n    return len(M(x=' a ').x)\n", "DeprecationWarning", "class-based `config` is deprecated"),
    # V1 config key in a V2 model_config: a UserWarning, counted through the migration-message pattern.
    "v1_config_key": ("from pydantic import BaseModel\n\nclass M(BaseModel):\n    x: str\n"
                      "    model_config = {'anystr_strip_whitespace': True}\n\n"
                      "def f():\n    return len(M(x='a').x)\n", "MigrationMessage", "Valid config keys have changed in V2"),
}

CLEAN_V2 = (
    "from pydantic import BaseModel, ConfigDict, field_validator\n\n"
    "class M(BaseModel):\n    model_config = ConfigDict(str_strip_whitespace=True)\n    x: str\n\n"
    "    @field_validator('x')\n    @classmethod\n    def check(cls, v):\n        return v\n\n"
    "def f():\n    return len(M(x=' a ').model_dump()['x'])\n"
)


@pytest.mark.parametrize("name", sorted(SOFT_FAIL_FIXTURES))
def test_v1_style_answers_on_v2_are_soft_fail(tmp_path, name):
    code, kind, text = SOFT_FAIL_FIXTURES[name]
    result = execute("pydantic_new", code, write_test(tmp_path))
    assert result.status == "pass", result.output_tail
    assert result.soft_fail, result.soft_warnings
    assert result.warning_counts[kind] >= 1, result.warning_counts
    assert any(text in w["message"] for w in result.soft_warnings), result.soft_warnings


def test_clean_v2_model_is_not_soft_fail(tmp_path):
    result = execute("pydantic_new", CLEAN_V2, write_test(tmp_path))
    assert result.status == "pass", result.output_tail
    assert not result.soft_fail and result.soft_warning_count == 0, result.soft_warnings


def test_v1_style_answer_on_v1_is_not_soft_fail(tmp_path):
    code, _, _ = SOFT_FAIL_FIXTURES["module_level_validator"]
    result = execute("pydantic_old", code, write_test(tmp_path))
    assert result.status == "pass" and not result.soft_fail, result.soft_warnings


def test_warning_raised_outside_solution_is_not_attributed(tmp_path):
    test = ("import warnings\nfrom solution import f\n\n\ndef test_f():\n"
            "    warnings.warn('test-side deprecation', DeprecationWarning)\n    assert f() == 1\n")
    result = execute("pydantic_new", CLEAN_V2.replace("return len(", "return 1 or len("), write_test(tmp_path, test))
    assert result.status == "pass", result.output_tail
    assert not result.soft_fail and result.soft_warning_count == 0


def test_reference_warnings_are_subtracted(tmp_path):
    code, _, _ = SOFT_FAIL_FIXTURES["dict_call"]
    result = execute("pydantic_new", code, write_test(tmp_path))
    baseline = frozenset(result.soft_signatures)
    assert result.soft_fail and not result.soft_fail_against(baseline)
    assert result.net_soft_signatures(baseline) == []


def test_warnings_as_errors_fires_on_known_deprecated_call(tmp_path):
    code, _, _ = SOFT_FAIL_FIXTURES["dict_call"]
    result = execute("pydantic_new", code, write_test(tmp_path), warnings_as_errors=True)
    assert result.status == "error", result.output_tail
    assert "Deprecat" in (result.exc_type or ""), result.exc_type


def test_warnings_as_errors_fires_on_import_time_warning(tmp_path):
    code, _, _ = SOFT_FAIL_FIXTURES["module_level_validator"]
    result = execute("pydantic_new", code, write_test(tmp_path), warnings_as_errors=True)
    assert result.status == "error", result.output_tail
    assert "Deprecat" in (result.exc_type or ""), result.exc_type


def test_timeout(tmp_path):
    result = execute("numpy_old", "def f():\n    while True:\n        pass\n", write_test(tmp_path), timeout_s=5)
    assert result.status == "timeout"


def test_version_stamp_mismatch_is_infra_error(tmp_path, monkeypatch):
    import varag.eval.execute as ex

    real = ex.read_manifest

    def tampered():
        manifest = json.loads(json.dumps(real()))
        manifest["numpy_old"]["library_version"] = "1.26.3"
        return manifest

    monkeypatch.setattr(ex, "read_manifest", tampered)
    result = execute("numpy_old", "def f():\n    return 1\n", write_test(tmp_path))
    assert result.status == "infra_error" and "stamp" in (result.infra_reason or "")


def load_diff(library):
    return json.loads((project_root() / "data" / "inventories" / library / "diff.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("library,symbol,bucket", [
    ("numpy", "numpy.trapz", "old_only"),
    ("numpy", "numpy.in1d", "old_only"),
    ("numpy", "numpy.trapezoid", "new_only"),
    ("numpy", "numpy.reshape(newshape)", "old_only"),
    ("pandas", "pandas.DataFrame.append", "old_only"),
    ("pandas", "pandas.DataFrame.applymap", "old_only"),
    ("pandas", "pandas.DataFrame.map", "new_only"),
    ("pandas", "pandas.read_csv(squeeze)", "old_only"),
    ("pydantic", "pydantic.Field(regex)", "old_only"),
    ("pydantic", "pydantic.Field(pattern)", "new_only"),
    ("pydantic", "pydantic.BaseModel.dict", "deprecated_in_new"),
    ("pydantic", "pydantic.validator", "deprecated_in_new"),
    ("pydantic", "pydantic.field_validator", "new_only"),
    ("pydantic", "pydantic.Config.orm_mode", "old_only"),
    ("pydantic", "pydantic.Config.from_attributes", "new_only"),
    ("pydantic", "pydantic.v1", "new_only"),
    ("pydantic", "pydantic.Field(const)", "old_only"),
    ("pydantic", "pydantic.Field(unique_items)", "old_only"),
    ("pydantic", "pydantic.Field(min_items)", "deprecated_in_new"),
    ("pydantic", "pydantic.Field(max_items)", "deprecated_in_new"),
    ("pydantic", "pydantic.Field(allow_mutation)", "deprecated_in_new"),
    ("pydantic", "pydantic.Field(include)", "deprecated_in_new"),
    ("pydantic", "pydantic.PyObject", "deprecated_in_new"),
    ("pydantic", "pydantic.types.ConstrainedStr", "old_only"),
    ("pandas", "pandas.DatetimeProperties.week", "old_only"),
    ("pandas", "pandas.DatetimeProperties.weekofyear", "old_only"),
    ("pandas", "pandas.PeriodProperties.week", "shared_same"),
    ("pandas", "pandas.StringMethods.contains", ("shared_same", "shared_changed")),   # present on both; signature differs
])
def test_canary_symbols_land_in_expected_buckets(library, symbol, bucket):
    expected = bucket if isinstance(bucket, tuple) else (bucket,)
    assert bucket_of(load_diff(library), symbol) in expected


def test_field_regex_is_a_corroborated_exclusive_keyword():
    from varag.pipeline.signals import static_usages

    code = (project_root() / "data" / "tasks" / "pydantic" / "pyd-001" / "ref_old.py").read_text(encoding="utf-8")
    usages = static_usages(code, load_diff("pydantic"))
    regex = next(u for u in usages.usages if u.symbol == "pydantic.Field(regex)")
    assert regex.side == "old" and regex.kind == "keyword"
    assert regex.uncertain is True          # Field takes **extra on V2
    assert regex.corroborated is True       # listed by bump-pydantic BP003 and by Field's removed-kwargs handling
    assert "pydantic.Field(regex)" in load_diff("pydantic")["rule_listed"]


def test_generic_names_marked_in_method_index():
    index = load_diff("pandas")["method_name_index"]
    assert index["append"]["generic"] is True and index["applymap"]["generic"] is False
    assert index["applymap"]["old"] and not index["applymap"]["new"]


linux_only = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="the limits apply on Linux (WSL2) only")


@linux_only
def test_linux_host_applies_both_limits():
    assert isolation_status() == {"memory_limit": True, "network_isolation": True}


@linux_only
def test_solution_has_no_network(tmp_path):
    code = ("import socket\n\ndef f():\n    s = socket.socket()\n    s.settimeout(3)\n"
            "    return 1 if s.connect_ex(('1.1.1.1', 80)) != 0 else 0\n")
    result = execute("numpy_old", code, write_test(tmp_path))
    assert result.status == "pass", result.output_tail


@linux_only
def test_solution_memory_is_capped(tmp_path):
    code = ("def f():\n    try:\n        block = bytearray(3 * 1024 ** 3)\n    except MemoryError:\n"
            "        return 1\n    return 0\n")
    result = execute("numpy_old", code, write_test(tmp_path))
    assert result.status == "pass", result.output_tail


@pytest.mark.parametrize("env", ["pandas_old", "pandas_new", "numpy_old", "numpy_new", "pydantic_old", "pydantic_new"])
def test_zoneinfo_reads_only_the_pinned_tzdata(tmp_path, env):
    # PYTHONTZPATH="" empties zoneinfo's search path, so names resolve from the tzdata package
    # (pinned in every environment), never the host database.
    code = "import zoneinfo\n\ndef f():\n    return zoneinfo.TZPATH, zoneinfo.ZoneInfo('US/Eastern').key\n"
    test = "from solution import f\n\n\ndef test_f():\n    assert f() == ((), 'US/Eastern')\n"
    result = execute(env, code, write_test(tmp_path, test))
    assert result.status == "pass", result.output_tail


def test_one_directional_concept_validates(make_one_directional):
    # numpy percentile(interpolation) -> percentile(method): ref_old passes 1.26 and fails 2.4;
    # ref_portable passes both; no ref_new.
    from varag.bench.schema import load_concept
    from varag.bench.validate import validate_concept

    record = validate_concept(load_concept(make_one_directional()), repeats=2, log=lambda _: None)
    steps = {n: s["status"] for n, s in record["steps"].items()}
    assert record["passed"], record["steps"]
    assert steps == {"1": "pass", "2": "pass", "3": "pass", "4": "pass", "5": "pass", "6": "pass", "7": "pass", "8": "pass", "9": "pass"}
    assert set(record["runs"]) == {"ref_old/old", "ref_old/new", "ref_portable/old", "ref_portable/new"}
    assert record["runs"]["ref_old/new"]["status"] == "error"
    assert record["gold_examples"] in ("both", "neither")


@pytest.mark.parametrize("library,symbol,bucket", [
    # ndarray.mean takes **kwargs on 2.4, so keepdims (declared only in 1.26's text signature) is
    # not evidence of either version without a rule or probe (user decision 2026-10-15).
    ("numpy", "numpy.ndarray.mean(keepdims)", "shared_unknown"),
    # asarray takes no **kwargs on 1.26: the 2.x keywords stay exclusive.
    ("numpy", "numpy.asarray(copy)", "new_only"),
    ("numpy", "numpy.asarray(device)", "new_only"),
    # V2 Field takes **extra, but the Field probe and the rules confirm regex is gone.
    ("pydantic", "pydantic.Field(regex)", "old_only"),
    ("pydantic", "pydantic.Field(pattern)", "new_only"),
])
def test_absorbed_keywords_need_confirmation(library, symbol, bucket):
    diff = json.loads((project_root() / "data" / "inventories" / library / "diff.json").read_text(encoding="utf-8"))
    assert bucket_of(diff, symbol) == bucket
    if bucket != "shared_unknown":
        assert symbol in diff["rule_listed"] or library == "numpy"


def test_probe_results_match_the_known_pairs():
    # Written by `varag bench probe` on the Linux environments; the seed pairs anchor its verdicts.
    report = json.loads((project_root() / "data" / "candidates" / "probes.json").read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in report["candidates"]}
    assert by_id["pandas.DataFrame.applymap -> pandas.DataFrame.map"]["concept_class"] == "removal"
    assert by_id["numpy.trapz -> numpy.trapezoid"]["concept_class"] == "removal"
    assert by_id["pydantic.Field(regex) -> pydantic.Field(pattern)"]["concept_class"] == "removal"
    assert by_id["pydantic.BaseModel.dict -> pydantic.BaseModel.model_dump"]["concept_class"] == "deprecation"
    assert by_id["numpy.percentile(interpolation) -> numpy.percentile(method)"]["verdict"] == "one_directional"
    assert by_id["pd-v03-as-unit"]["concept_class"] == "behavior"
    manifest = json.loads((project_root() / "envs" / "manifest.json").read_text(encoding="utf-8"))
    assert report["lock_sha256"]["numpy"]["old"] == manifest["numpy_old"]["lock_sha256"]


def test_confirmed_value_rules():
    from varag.inventory.rules import value_rules

    confirmed = {(r["callable"], r["parameter"], r["value"], r["side"]) for r in value_rules("pandas")}
    assert ("pandas.date_range", "freq", "M", "old") in confirmed
    assert ("pandas.date_range", "freq", "ME", "new") in confirmed
    assert ("pandas.to_datetime", "format", "ISO8601", "new") in confirmed
    assert ("numpy.array", "copy", None, "new") in {(r["callable"], r["parameter"], r["value"], r["side"]) for r in value_rules("numpy")}
