"""Static usage extraction on fixture snippets against a synthetic diff."""

import pytest

from varag.pipeline.signals import static_usages


def entry(kind="function", **extra):
    return {"kind": kind, "owner": "", "name": "", **extra}


DIFF = {
    "library": "pandas",
    "old_only": {
        "pandas.DataFrame.applymap": entry("method"),
        "pandas.Series.iteritems": entry("method"),
        "pandas.DataFrame.iteritems": entry("method"),
        "pandas.read_csv(squeeze)": entry("param"),
        "pandas.DataFrame.append": entry("method"),
        "pandas.DatetimeProperties.week": entry("attribute"),
        "numpy.trapz": entry(),
    },
    "new_only": {
        "pandas.DataFrame.map": entry("method"),
        "pandas.read_csv(date_format)": entry("param"),
        "pandas.StringMethods.removeprefix": entry("method"),
        "numpy.trapezoid": entry(),
        "pydantic.field_validator": entry(),
        "pydantic.BaseModel.model_dump": entry("method"),
        "pydantic.Field(pattern)": entry("param"),
    },
    "deprecated_in_new": {"pydantic.BaseModel.dict": entry("method")},
    "shared_changed": {"pandas.read_csv": entry(accepts_var_kwargs=False, signature_known=True)},
    "shared_unknown": {"pandas.DataFrame.plot": entry("method")},
    "shared_same": {
        "pandas.DataFrame": entry("class"),
        "pandas.Series": entry("class"),
        "pandas.DataFrame.to_csv": entry("method", accepts_var_kwargs=True),
        "pandas.DataFrame.apply": entry("method"),
        "pandas.PeriodProperties.week": entry("attribute"),
        "pandas.StringMethods.contains": entry("method"),
        "pydantic.BaseModel": entry("class"),
        "pydantic.Field": entry(accepts_var_kwargs=False),
        "numpy.array": entry(),
    },
    "rule_listed": {"pydantic.Field(regex)": "bump-pydantic BP003", "pydantic.Field(pattern)": "bump-pydantic BP003 (replacement)"},
    "method_name_index": {
        "iteritems": {"old": ["pandas.DataFrame", "pandas.Series"], "new": [], "generic": False},
        "append": {"old": ["pandas.DataFrame"], "new": [], "generic": True},
        "map": {"old": ["pandas.Series"], "new": ["pandas.DataFrame", "pandas.Series"], "generic": True},
        "model_dump": {"old": [], "new": ["pydantic.BaseModel"], "generic": False},
    },
}


def test_module_alias_chain():
    u = static_usages("import numpy as np\n\ndef f(y, x):\n    return np.trapz(y, x)\n", DIFF)
    assert u.old == {"numpy.trapz"} and u.new == set()


def test_from_import_is_a_usage():
    u = static_usages("from numpy import trapezoid\nfrom pydantic import field_validator\n", DIFF)
    assert u.new == {"numpy.trapezoid", "pydantic.field_validator"}


def test_keyword_bound_to_resolved_callable():
    u = static_usages("import pandas as pd\ndf = pd.read_csv('f.csv', squeeze=True)\n", DIFF)
    assert u.old == {"pandas.read_csv(squeeze)"}
    u = static_usages("import pandas as pd\norders = pd.read_csv('f.csv', date_format='%Y')\n", DIFF)
    assert u.new == {"pandas.read_csv(date_format)"}


def test_receiver_from_constructor_reader_and_annotation():
    code = (
        "import pandas as pd\n"
        "df = pd.DataFrame({'a': [1]})\n"
        "out = df.applymap(str)\n"
        "def g(frame: pd.DataFrame):\n"
        "    return frame.map(str)\n"
    )
    u = static_usages(code, DIFF)
    assert u.old == {"pandas.DataFrame.applymap"} and u.new == {"pandas.DataFrame.map"}


def test_generic_name_on_unresolved_receiver_abstains_but_specific_name_counts():
    u = static_usages("items = []\nitems.append(1)\nfor k, v in thing.iteritems():\n    pass\n", DIFF)
    assert u.old == {"pandas.DataFrame.iteritems"}
    assert any(a["name"] == "append" and "generic" in a["reason"] for a in u.abstained)


def test_name_heuristic_is_flagged():
    u = static_usages("out = df.applymap(str)\n", DIFF)
    assert u.old == {"pandas.DataFrame.applymap"}
    assert u.usages[0].resolution == "heuristic"


def test_version_guard_excludes_usage():
    code = (
        "import pandas as pd\n"
        "df = pd.DataFrame()\n"
        "try:\n"
        "    out = df.map(str)\n"
        "except AttributeError:\n"
        "    out = df.applymap(str)\n"
    )
    u = static_usages(code, DIFF)
    assert u.old == set() and u.new == set()
    assert u.guarded == {"pandas.DataFrame.map", "pandas.DataFrame.applymap"}


def test_subclass_instances_resolve_to_base_and_deprecated_is_soft():
    code = (
        "from pydantic import BaseModel, Field\n"
        "class User(BaseModel):\n"
        "    code: str = Field(..., pattern='x')\n"
        "u = User(code='a')\n"
        "print(u.model_dump())\n"
        "legacy = User(code='b')\n"
        "print(legacy.dict())\n"
    )
    u = static_usages(code, DIFF)
    assert u.new == {"pydantic.Field(pattern)", "pydantic.BaseModel.model_dump"}
    assert u.deprecated_in_new == {"pydantic.BaseModel.dict"}
    assert u.old == set()


def test_unknown_callees_and_splats_abstain_on_keywords():
    code = "import pandas as pd\ndf = pd.DataFrame()\ndf.plot(kind='bar')\nopts = {}\npd.read_csv('f', **opts)\n"
    u = static_usages(code, DIFF)
    assert u.old == set() and u.new == set()
    reasons = {a["reason"] for a in u.abstained}
    assert reasons == {"callee in shared_unknown", "call forwards **kwargs"}


def test_keyword_declared_on_one_side_is_uncertain_when_other_side_takes_var_kwargs():
    diff = {**DIFF, "shared_same": {**DIFF["shared_same"], "pydantic.Field": entry(accepts_var_kwargs=True)}}
    u = static_usages("from pydantic import Field\nx = Field(..., pattern='a')\n", diff)
    assert u.new == {"pydantic.Field(pattern)"}
    assert [usage.uncertain for usage in u.usages if usage.kind == "keyword"] == [True]
    u = static_usages("from pydantic import Field\nx = Field(..., pattern='a')\n", DIFF)
    assert [usage.uncertain for usage in u.usages if usage.kind == "keyword"] == [False]


def test_accessor_members_resolve_to_the_accessor_class():
    u = static_usages("import pandas as pd\ns = pd.Series(['a'])\nout = s.str.removeprefix('x')\nok = s.str.contains('a')\n", DIFF)
    assert u.new == {"pandas.StringMethods.removeprefix"} and u.old == set()


def test_dt_accessor_abstains_when_the_dtype_decides():
    u = static_usages("import pandas as pd\ns = pd.Series([1])\nw = s.dt.week\n", DIFF)
    assert u.old == set() and u.new == set()
    assert any("dtype" in a["reason"] and "DatetimeProperties.week=old_only" in a["reason"] for a in u.abstained)


def test_dataframe_column_is_a_series():
    u = static_usages("import pandas as pd\ndf = pd.DataFrame()\nx = df['name'].str.removeprefix('x')\n", DIFF)
    assert u.new == {"pandas.StringMethods.removeprefix"}


def test_corroborated_flag_comes_from_rule_sets():
    u = static_usages("from pydantic import Field\nx = Field(..., pattern='a')\n", DIFF)
    assert [usage.corroborated for usage in u.usages if usage.kind == "keyword"] == [True]
    u = static_usages("import pandas as pd\npd.read_csv('f', date_format='x')\n", DIFF)
    assert [usage.corroborated for usage in u.usages if usage.kind == "keyword"] == [False]


def test_unparseable_code():
    u = static_usages("def broken(:\n", DIFF)
    assert not u.parsed and u.old == set()
