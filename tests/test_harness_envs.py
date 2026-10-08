"""Harness checks that need the built environments (marked ``envs``)."""

import json

import pytest

from varag.config import project_root
from varag.eval.execute import execute
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


def test_pydantic_v1_style_answer_on_v2_is_soft_fail(tmp_path):
    code = "from pydantic import BaseModel\n\nclass M(BaseModel):\n    x: int\n\ndef f():\n    return len(M(x=1).dict())\n"
    result = execute("pydantic_new", code, write_test(tmp_path))
    assert result.status == "pass", result.output_tail
    assert result.soft_fail and result.deprecation_warnings >= 1
    assert any("dict" in w for w in result.warnings)


def test_warnings_as_errors_filter_fires_on_known_deprecated_call(tmp_path):
    code = "from pydantic import BaseModel\n\nclass M(BaseModel):\n    x: int\n\ndef f():\n    return len(M(x=1).dict())\n"
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
