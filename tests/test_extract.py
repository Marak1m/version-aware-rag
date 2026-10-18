"""Signal-extractor fixtures (M5 acceptance: at least 40 snippets covering pins, named versions,
migration messages, errors, imports, symbols, keywords, values, config keys, deprecations,
version guards and contradictions). They run on the committed diffs and value rules; no
environment is needed."""

import pytest

from varag.pipeline.extract import extract_signals
from varag.pipeline.infer import CONTEXT_CONFLICT, INFER, UNCERTAIN, infer

VERSIONS = {"pandas": {"old": "1.5.3", "new": "3.0.6"}, "numpy": {"old": "1.26.4", "new": "2.4.6"},
            "pydantic": {"old": "1.10.13", "new": "2.13.4"}}
TB = "Traceback (most recent call last):\n  File \"x.py\", line 3, in <module>\n"
PD_DF = "import pandas as pd\ndf = pd.read_csv('a.csv')\n"
PYD_MODEL = "from pydantic import BaseModel\n\nclass U(BaseModel):\n    id: int\n"

# (id, library, context, expected S, expected D, expected decision kind, decided side)
FIXTURES = [
    # pins (decisive)
    ("pin-pandas-old", "pandas", "requests>=2.28\npandas>=1.3,<2\n", {}, {"old"}, INFER, "old"),
    ("pin-pandas-new", "pandas", "pandas>=3\n", {}, {"new"}, INFER, "new"),
    ("pin-numpy-old", "numpy", "numpy<2\nscipy>=1.9\n", {}, {"old"}, INFER, "old"),
    ("pin-numpy-new", "numpy", "numpy>=2.4\n", {}, {"new"}, INFER, "new"),
    ("pin-pydantic-old", "pydantic", "fastapi>=0.80,<0.100\npydantic>=1.9,<2\n", {}, {"old"}, INFER, "old"),
    ("pin-pydantic-new", "pydantic", "pydantic>=2\n", {}, {"new"}, INFER, "new"),
    ("pin-both-sides", "pandas", "pandas>=1.3\n", {}, set(), UNCERTAIN, None),
    ("pin-freeze", "pandas", "numpy==1.26.4\npandas==1.5.3\n", {}, {"old"}, INFER, "old"),
    ("pin-pyproject", "pandas", '[project.dependencies]\npandas = ">=3"\n', {}, {"new"}, INFER, "new"),
    ("pin-conda", "numpy", "dependencies:\n  - python=3.11\n  - numpy=1.26\n", {}, {"old"}, INFER, "old"),
    ("pin-other-library", "pandas", "requests>=2\n", {}, set(), UNCERTAIN, None),
    # named versions (decisive)
    ("mention-pandas-1.5", "pandas", "I use pandas 1.5 here, nothing fancy.", {}, {"old"}, INFER, "old"),
    ("mention-pydantic-v2", "pydantic", "We are on pydantic v2 in this service.", {}, {"new"}, INFER, "new"),
    ("mention-numpy-full", "numpy", "numpy 2.4.6 is installed.", {}, {"new"}, INFER, "new"),
    ("mention-unknown-major", "pandas", "pandas 2.1 is what the notebook used.", {}, set(), UNCERTAIN, None),
    ("mention-version-word", "pandas", "the server runs version 3 of the library", {}, {"new"}, INFER, "new"),
    # migration messages (decisive)
    ("message-removed-kwargs", "pydantic", "pydantic.errors.PydanticUserError: `regex` is removed. use `pattern` instead", {}, {"new"}, INFER, "new"),
    ("message-config-keys", "pydantic", "UserWarning: Valid config keys have changed in V2: 'orm_mode' has been renamed", {}, {"new"}, INFER, "new"),
    # errors naming symbols, keywords and values (weight 4, direction from the inventory)
    ("error-module-attr", "numpy", "import numpy as np\nnp.trapz([1, 2], [0, 1])\n" + TB + "AttributeError: module 'numpy' has no attribute 'trapz'",
     {"new": 4}, set(), INFER, "new"),
    ("error-object-attr", "pandas", PD_DF + "df.applymap(str)\n" + TB + "AttributeError: 'DataFrame' object has no attribute 'applymap'", {"new": 4}, set(), INFER, "new"),
    ("error-import-name", "pydantic", "from pydantic import field_validator\n" + TB + "ImportError: cannot import name 'field_validator' from 'pydantic'", {"old": 4}, set(), INFER, "old"),
    ("error-keyword", "pandas", PD_DF.replace("'a.csv'", "'a.csv', squeeze=True") + TB + "TypeError: read_csv() got an unexpected keyword argument 'squeeze'", {"new": 4}, set(), INFER, "new"),
    ("error-value-ME", "pandas", "import pandas as pd\nidx = pd.date_range('2020-01-01', periods=3, freq='ME')\n" + TB + "ValueError: Invalid frequency: ME", {"old": 4}, set(), INFER, "old"),
    ("error-value-M", "pandas", "import pandas as pd\nidx = pd.date_range('2020-01-01', periods=3, freq='M')\n" + TB + "ValueError: Invalid frequency: M. Failed to parse with error message: ValueError(\"Invalid frequency: M\")", {"new": 4}, set(), INFER, "new"),
    ("error-value-unit", "pandas", "import pandas as pd\npd.Timedelta(5, unit='T')\n" + TB + "ValueError: invalid unit abbreviation: T", {"new": 4}, set(), INFER, "new"),
    # imports and symbols
    ("import-exclusive", "pydantic", "from pydantic import field_validator\n", {"new": 4}, set(), INFER, "new"),
    ("symbol-resolved", "numpy", "import numpy as np\narea = np.trapz(y, x)\n", {"old": 3}, set(), INFER, "old"),
    ("symbol-heuristic", "pandas", "out = df.applymap(lambda v: v * 2)\n", {"old": 1.5}, set(), UNCERTAIN, None),
    ("symbol-new-resolved", "pandas", PD_DF + "out = df.map(str)\n", {"new": 3}, set(), INFER, "new"),
    # keywords
    ("keyword-exclusive", "pandas", "import pandas as pd\ns = pd.read_csv('a.csv', squeeze=True)\n", {"old": 3}, set(), INFER, "old"),
    ("keyword-confirmed-absorbed", "pydantic", "from pydantic import BaseModel, Field\n\nclass U(BaseModel):\n    code: str = Field(..., regex='^[A-Z]+$')\n", {"old": 3}, set(), INFER, "old"),
    ("keyword-unconfirmed-absorbed", "pydantic", "from pydantic import BaseModel, Field\n\nclass U(BaseModel):\n    x: int = Field(1, validation_alias='y')\n", {}, set(), UNCERTAIN, None),
    # values (user decisions 2026-10-18)
    ("value-keyword-M", "pandas", "import pandas as pd\nidx = pd.date_range('2020-01-01', periods=3, freq='M')\n", {"old": 3}, set(), INFER, "old"),
    ("value-keyword-ME", "pandas", "import pandas as pd\nidx = pd.date_range('2020-01-01', periods=3, freq='ME')\n", {"new": 3}, set(), INFER, "new"),
    ("value-positional-M", "pandas", PD_DF + "monthly = df.resample('M').sum()\n", {"old": 3}, set(), INFER, "old"),
    ("value-positional-ME", "pandas", PD_DF + "monthly = df.resample('ME').sum()\n", {"new": 3}, set(), INFER, "new"),
    ("value-positional-heuristic", "pandas", "monthly = df.resample('ME').sum()\n", {"new": 1.5}, set(), UNCERTAIN, None),
    ("value-anchored", "pandas", "import pandas as pd\nidx = pd.date_range('2020-01-01', periods=2, freq='Q-JUN')\n", {"old": 3}, set(), INFER, "old"),
    ("value-portable-h", "pandas", "import pandas as pd\nidx = pd.date_range('2020-01-01', periods=3, freq='h')\n", {}, set(), UNCERTAIN, None),
    ("value-to-period-M", "pandas", "import pandas as pd\ns = pd.Series([1.0], index=pd.date_range('2020-01-01', periods=1))\np = s.to_period('M')\n", {}, set(), UNCERTAIN, None),
    ("value-unconfirmed", "pandas", "import pandas as pd\nidx = pd.timedelta_range('1 day', periods=3, freq='BH')\n", {}, set(), UNCERTAIN, None),
    ("value-numpy-copy-none", "numpy", "import numpy as np\na = np.array([1, 2], copy=None)\n", {"new": 3}, set(), INFER, "new"),
    # config keys (D-f)
    ("config-class-body", "pydantic", PYD_MODEL + "\n    class Config:\n        orm_mode = True\n", {"old": 3}, set(), INFER, "old"),
    ("config-dict-literal", "pydantic", PYD_MODEL + "    model_config = {'from_attributes': True}\n", {"new": 3}, set(), INFER, "new"),
    # ConfigDict exists in pydantic 1.10 too (a TypedDict), so only the key is evidence.
    ("config-configdict-call", "pydantic", "from pydantic import BaseModel, ConfigDict\n\nclass U(BaseModel):\n    model_config = ConfigDict(str_strip_whitespace=True)\n    id: int\n",
     {"new": 3}, set(), INFER, "new"),
    ("config-unresolved-base", "pydantic", "class U(BaseModel):\n    id: int\n\n    class Config:\n        orm_mode = True\n", {"old": 1.5}, set(), UNCERTAIN, None),
    # deprecated usage, guards, method names, generic names
    ("deprecated-dict", "pydantic", PYD_MODEL + "\nu = U(id=1)\nprint(u.dict())\n", {"old": 1}, set(), UNCERTAIN, None),
    ("version-guard", "numpy", "try:\n    from numpy import trapezoid\nexcept ImportError:\n    from numpy import trapz as trapezoid\n", {}, set(), UNCERTAIN, None),
    ("method-name-index", "pandas", "for name, values in thing.iteritems():\n    print(name, values.sum())\n", {"old": 1.5}, set(), UNCERTAIN, None),
    ("generic-method", "pandas", "rows = []\nrows.append(1)\n", {}, set(), UNCERTAIN, None),
    ("regex-fallback", "numpy", "import numpy as np\narea = np.trapz(y, x\n", {"old": 1.5}, set(), UNCERTAIN, None),
    # contradiction
    ("contradiction", "pandas", "pandas>=1.3,<2\n```python\nimport pandas as pd\ndf = pd.read_csv('a.csv')\nout = df.map(str)\n```\n", {"new": 3}, {"old"}, CONTEXT_CONFLICT, None),
]


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f[0] for f in FIXTURES])
def test_fixture(fixture):
    _, library, context, expected_s, expected_d, kind, side = fixture
    signals = extract_signals("", context, library, versions=VERSIONS[library])
    S = {s: signals.S(s) for s in ("old", "new")}
    D = {s for s in ("old", "new") if signals.D(s)}
    assert {k: v for k, v in S.items() if v} == expected_s, signals.to_dict()
    assert D == expected_d, signals.to_dict()
    decision = infer(signals)
    assert (decision.kind, decision.side) == (kind, side), (decision, signals.to_dict())


def test_fixture_count_meets_the_acceptance_bar():
    assert len(FIXTURES) >= 40


def test_error_named_symbol_is_removed_from_code_signals():
    context = "import numpy as np\nnp.trapz([1, 2], [0, 1])\n" + TB + "AttributeError: module 'numpy' has no attribute 'trapz'"
    signals = extract_signals("", context, "numpy", versions=VERSIONS["numpy"])
    kinds = {(s.kind, s.symbol) for s in signals.signals}
    assert ("error_symbol", "numpy.trapz") in kinds and ("symbol", "numpy.trapz") not in kinds
    assert any(a["reason"].startswith("named in the error") for a in signals.abstained)


def test_unconfirmed_keyword_and_generic_names_are_abstentions():
    signals = extract_signals("", "from pydantic import BaseModel, Field\n\nclass U(BaseModel):\n    x: int = Field(1, validation_alias='y')\n", "pydantic", versions=VERSIONS["pydantic"])
    assert any(a["reason"] == "keyword not confirmed on both sides" for a in signals.abstained)
    signals = extract_signals("", "rows = []\nrows.append(1)\n", "pandas", versions=VERSIONS["pandas"])
    assert any("generic" in a["reason"] for a in signals.abstained)


def test_guarded_usages_carry_weight_zero_and_spans():
    signals = extract_signals("", "try:\n    from numpy import trapezoid\nexcept ImportError:\n    from numpy import trapz as trapezoid\n", "numpy", versions=VERSIONS["numpy"])
    guarded = [s for s in signals.signals if "guarded" in s.detail]
    assert len(guarded) == 2 and all(s.weight == 0 for s in guarded) and all(s.line > 0 for s in guarded)


def test_pins_are_not_double_counted_as_mentions():
    signals = extract_signals("", "pandas>=1.3,<2\n", "pandas", versions=VERSIONS["pandas"])
    assert [s.kind for s in signals.signals] == ["pin"]


def test_query_text_is_scanned_too():
    signals = extract_signals("Write f() for pandas 3.0.6.", "", "pandas", versions=VERSIONS["pandas"])
    assert signals.D("new") and signals.signals[0].source == "query"
