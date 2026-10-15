"""The ``varag`` command line. Every command from the handoff is listed here; the
ones a later milestone builds raise ``not implemented until M<n>``."""

from __future__ import annotations

import click


def _todo(milestone: str) -> None:
    raise click.ClickException(f"not implemented until {milestone}")


@click.group()
@click.version_option(package_name="varag")
def main() -> None:
    """VA-RAG: version-aware RAG benchmark, pipeline and two-environment harness."""


# --- env -------------------------------------------------------------------


@main.group()
def env() -> None:
    """Build and verify the six library environments."""


@env.command("build")
@click.option("--only", "only", default=None, help="Build one environment, e.g. pandas_old.")
@click.option("--relock", is_flag=True, help="Recompile requirements.lock even if it exists.")
def env_build(only: str | None, relock: bool) -> None:
    """Create the environments from hash-pinned locks and write envs/manifest.json."""
    from varag.envs.build import build_all

    manifest = build_all(only=only, relock=relock, log=click.echo)
    click.echo(f"manifest written for {len(manifest)} environment(s)")


@env.command("verify")
def env_verify() -> None:
    """Re-probe versions and canaries; non-zero exit on any mismatch."""
    from varag.envs.verify import verify_all

    failures = 0
    for name, found in verify_all().items():
        if found:
            failures += len(found)
            for mismatch in found:
                click.echo(f"MISMATCH {mismatch}")
        else:
            click.echo(f"ok {name}")
    if failures:
        raise click.ClickException(f"{failures} mismatch(es)")


# --- inventory -------------------------------------------------------------


@main.group()
def inventory() -> None:
    """API inventories per environment and the old/new diff per library."""


@inventory.command("build")
def inventory_build() -> None:
    """Extract inventories in each environment and write the diffs."""
    from varag.inventory.build import build_inventories

    build_inventories(log=click.echo)


@inventory.command("audit")
def inventory_audit() -> None:
    """Check the diffs against the published rule sets and print recall per library."""
    from varag.config import library_names
    from varag.inventory.audit import audit_all, format_result

    failed = []
    for library, result in audit_all(library_names()).items():
        click.echo(format_result(result))
        if not result.passed:
            failed.append(library)
    if failed:
        raise click.ClickException(f"audit recall below gate for: {', '.join(failed)}")


# --- corpus ----------------------------------------------------------------


@main.group()
def corpus() -> None:
    """Version-tagged documentation corpus."""


@corpus.command("build")
@click.option("--library", "libraries", multiple=True, help="Build one library (repeatable); default all.")
def corpus_build(libraries: tuple[str, ...]) -> None:
    """Build version-tagged chunks with provenance and check each example by execution."""
    from varag.corpus.build import build_corpus

    build_corpus(list(libraries) or None, log=click.echo)


# --- bench -----------------------------------------------------------------


@main.group()
def bench() -> None:
    """Benchmark concepts: candidates, clues and validation."""


@bench.command("candidates")
@click.option("--library", "libraries", multiple=True, help="One library (repeatable); default all.")
def bench_candidates(libraries: tuple[str, ...]) -> None:
    """List symbol pairs and keyword-level pairs to mine for concepts, with counts per library."""
    from varag.bench.candidates import counts, format_counts, format_rows, keyword_pairs, symbol_pairs
    from varag.config import library_names

    summary = {}
    for library in libraries or library_names():
        symbol_rows, keyword_rows = symbol_pairs(library), keyword_pairs(library)
        click.echo(format_rows(f"{library}: symbol pairs", symbol_rows))
        click.echo(format_rows(f"{library}: keyword pairs", keyword_rows))
        summary[library] = counts(symbol_rows, keyword_rows)
    click.echo(format_counts(summary))


@bench.command("make-error-clue")
@click.argument("concept")
@click.option("--target", type=click.Choice(["old", "new"]), required=True)
def bench_make_error_clue(concept: str, target: str) -> None:
    """Run other-version code in the target environment and save the traceback as a clue."""
    _todo("M5")


@bench.command("validate")
@click.argument("concepts", nargs=-1)
def bench_validate(concepts: tuple[str, ...]) -> None:
    """Run the validation matrix and update data/tasks/MANIFEST.json."""
    from varag.bench.validate import validate

    records = validate(concepts, log=click.echo)
    failed = [cid for cid, r in records.items() if not r["passed"]]
    click.echo(f"{len(records) - len(failed)}/{len(records)} concept(s) validated")
    if failed:
        raise click.ClickException("validation failed for: " + ", ".join(failed))


# --- serve -----------------------------------------------------------------


@main.group()
def serve() -> None:
    """Model serving checks."""


@serve.command("check")
@click.option("--model", required=True)
def serve_check(model: str) -> None:
    """Print the rendered prompt and effective sampling parameters, then run the serving-noise check."""
    _todo("M6")


# --- run / report / audit / smoke -----------------------------------------


@main.command("run")
@click.option("--methods", default="all", show_default=True, help="Comma-separated method ids or all.")
@click.option("--model", required=True, help="Backend id from configs/models.yaml.")
@click.option("--split", type=click.Choice(["dev", "test", "all"]), default="dev", show_default=True)
@click.option("--user-arm", type=click.Choice(["knows", "unsure"]), default=None)
def run(methods: str, model: str, split: str, user_arm: str | None) -> None:
    """Generate, execute in both environments, write results and traces."""
    from varag.eval.run import run as run_eval

    run_eval(methods, model, split, user_arm, log=click.echo)


@main.command("report")
@click.argument("run_id")
def report(run_id: str) -> None:
    """Compute metrics, intervals, the risk-coverage curve and the detectable-effect table."""
    _todo("M7")


@main.group()
def audit() -> None:
    """Hand-labelling exports."""


@audit.command("sample")
@click.argument("run_id")
@click.option("--n", default=50, show_default=True)
def audit_sample(run_id: str, n: int) -> None:
    """Export outputs with the blend detector verdict for hand labelling."""
    _todo("M7")


@main.command("smoke")
def smoke() -> None:
    """Verify, audit, validate, run all methods on mock backends and the 7B endpoint, report."""
    _todo("M7")


if __name__ == "__main__":
    main()
