from click.testing import CliRunner

from varag.cli import main

EXPECTED = {
    "": ["env", "inventory", "corpus", "bench", "serve", "run", "report", "audit", "smoke"],
    "env": ["build", "verify"],
    "inventory": ["build", "audit"],
    "corpus": ["build"],
    "bench": ["candidates", "make-error-clue", "validate"],
    "serve": ["check"],
    "audit": ["sample"],
}


def test_help_lists_every_command():
    runner = CliRunner()
    for group, names in EXPECTED.items():
        args = ([group] if group else []) + ["--help"]
        result = runner.invoke(main, args)
        assert result.exit_code == 0, result.output
        for name in names:
            assert name in result.output, f"{name} missing from `varag {group} --help`"


def test_no_command_is_a_stub_any_more():
    import inspect

    from varag import cli

    assert "_todo(" not in inspect.getsource(cli)
    for args in (["smoke", "--help"], ["report", "--help"], ["audit", "sample", "--help"], ["serve", "check", "--help"],
                 ["bench", "make-error-clue", "--help"], ["bench", "probe", "--help"]):
        result = CliRunner().invoke(main, args)
        assert result.exit_code == 0, (args, result.output)


def test_probe_verdicts():
    from varag.bench.probe import concept_class, verdict

    base = {"old@old": "ok", "old@new": "error", "new@new": "ok", "new@old": "error"}
    assert verdict(base)[0] == "two_directional" and concept_class("symbol", "two_directional", base) == "removal"
    warns = {**base, "old@new": "warns"}
    assert verdict(warns)[0] == "two_directional" and concept_class("keyword", "two_directional", warns) == "deprecation"
    assert concept_class("behaviour", "two_directional", base) == "behavior"
    one = {**base, "new@old": "ok"}
    assert verdict(one)[0] == "one_directional" and concept_class("value", "one_directional", one) == "one_directional"
    assert verdict({**base, "old@new": "ok"}) == ("not_discriminative", "reverse: only the new form is exclusive")
    assert verdict({**base, "old@new": "ok", "new@old": "ok"})[0] == "not_discriminative"
    assert verdict({**base, "new@new": "error"}) == ("not_discriminative", "a form fails on its own side")
    # A warning on a form's own side is not a break.
    assert verdict({**base, "old@old": "warns"})[0] == "two_directional"


def test_access_snippet_uses_the_inventory_root():
    from varag.bench.probe import access_snippet, value_call

    assert access_snippet("pandas", "pandas.DataFrame.applymap") == "from pandas import DataFrame as _root\n_ = _root.applymap"
    assert access_snippet("numpy", "numpy.trapz") == "import numpy as _root\n_ = _root.trapz"
    assert access_snippet("numpy", "numpy.char.add") == "import numpy as _root\n_ = _root.char.add"
    assert access_snippet("pandas", "pandas.DatetimeProperties.week") == (
        "from pandas.core.indexes.accessors import DatetimeProperties as _root\n_ = _root.week")
    assert access_snippet("pydantic", "pydantic.Config.orm_mode") is None       # config keys are not attributes
    templates = {"pandas.date_range|freq": "pd.date_range('2020-01-01', periods=3, freq=VALUE)"}
    assert value_call(templates, {"callable": "pandas.date_range", "parameter": "freq", "value": "M"}) == "pd.date_range('2020-01-01', periods=3, freq='M')"
    assert value_call(templates, {"callable": "numpy.array", "parameter": "copy", "value": None}) is None
