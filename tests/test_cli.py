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


def test_unbuilt_command_fails_cleanly():
    result = CliRunner().invoke(main, ["smoke"])
    assert result.exit_code == 1
    assert "not implemented until" in result.output
