"""The ``varag`` command line. Every command from the handoff is listed here; the
ones a later milestone builds raise ``not implemented until M<n>``."""

from __future__ import annotations

from pathlib import Path

import click


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
        symbol_rows, (keyword_rows, unreadable) = symbol_pairs(library), keyword_pairs(library)
        click.echo(format_rows(f"{library}: symbol pairs", symbol_rows))
        click.echo(format_rows(f"{library}: keyword pairs", keyword_rows))
        summary[library] = counts(symbol_rows, keyword_rows, unreadable)
    click.echo(format_counts(summary))


@bench.command("probe")
@click.option("--library", "libraries", multiple=True, help="One library (repeatable); default all.")
def bench_probe(libraries: tuple[str, ...]) -> None:
    """Run every candidate's old and new form in both environments; classify each as two_directional,
    one_directional or not_discriminative. Writes data/candidates/probes.json and the value-rule probes."""
    from varag.bench.probe import format_report, probe
    from varag.envs.verify import require_verified

    require_verified()
    report = probe(list(libraries) or None, log=click.echo)
    for c in report["candidates"]:
        if c["status"] == "probed":
            click.echo(f"  {c['verdict']:18} {c.get('concept_class') or '-':15} {c['kind']:9} {c['id']}")
        else:
            click.echo(f"  {'unprobed':18} {'-':15} {c['kind']:9} {c['id']}  ({c['reason']})")
    click.echo(format_report(report))


@bench.command("make-error-clue")
@click.argument("concept")
@click.option("--target", type=click.Choice(["old", "new"]), required=True, help="The environment the snippet fails in.")
@click.option("--snippet", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=True,
              help="The author's failing snippet (5 to 15 lines using the other version's API).")
@click.option("--overlap", type=click.Choice(["on_target", "off_target"]), default="off_target", show_default=True)
def bench_make_error_clue(concept: str, target: str, snippet: Path, overlap: str) -> None:
    """Run the snippet in the target environment, capture its traceback, and write clues/<target>_error.txt.
    Refuses a traceback that names no exclusive symbol, keyword, rejected value or migration message."""
    from varag.bench.error_clues import make_error_clue
    from varag.bench.schema import find_concept_dir, load_concept
    from varag.envs.verify import require_verified

    loaded = load_concept(find_concept_dir(concept))
    require_verified([f"{loaded.library}_{target}"])
    result = make_error_clue(loaded, target, snippet.read_text(encoding="utf-8"), overlap)
    click.echo(f"wrote {result['file']}; names {', '.join(result['named'])}; alone it infers {result['decision']}"
               + ("" if result["infers_target"] else "  (does NOT infer the target: step 6 will fail)"))
    click.echo("add to concept.yaml under clues." + target + ":")
    click.echo(result["yaml"])


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


@bench.command("thresholds")
@click.option("--split", type=click.Choice(["dev"]), default="dev", show_default=True,
              help="Thresholds are tuned on dev clue instances only.")
def bench_thresholds(split: str) -> None:
    """Sweep tau_commit and tau_noise over the dev clue instances and print commits, wrong commits
    and uncommitted instances per point, marking the configured (and possibly frozen) point."""
    from varag.pipeline.infer import thresholds
    from varag.pipeline.thresholds import clue_instances, format_sweep, frozen, sweep

    instances = clue_instances(split)
    click.echo(f"{len(instances)} {split} clue instances")
    click.echo(format_sweep(sweep(instances), thresholds()))
    stamp = frozen()
    click.echo(f"frozen on {stamp['frozen_on']} ({stamp.get('frozen_split', 'dev')})" if stamp else "thresholds are NOT frozen")


# --- serve -----------------------------------------------------------------


@main.group()
def serve() -> None:
    """Model serving checks."""


@serve.command("check")
@click.option("--model", required=True, help="An openai_chat backend id from configs/models.yaml.")
def serve_check(model: str) -> None:
    """Check the served model, the sampling parameters we send, the rendered prompt and determinism."""
    from varag.eval.serve import format_report, serve_check as check

    report = check(model)
    click.echo(format_report(report))
    if report["problems"]:
        raise SystemExit(1)


@main.command("preflight")
def preflight() -> None:
    """GPU, CUDA, vLLM, VRAM, disk, Hugging Face access to the pinned repos, uv, environments
    against the committed manifest, and the execution isolation. Non-zero exit on any failure."""
    from varag.preflight import format_checks, preflight as run_preflight

    checks = run_preflight()
    click.echo(format_checks(checks))
    if any(c.status == "fail" for c in checks):
        raise SystemExit(1)


# --- run / report / audit / smoke -----------------------------------------


@main.command("run")
@click.option("--methods", default="all", show_default=True, help="Comma-separated method ids or all.")
@click.option("--model", required=True, help="Backend id from configs/models.yaml.")
@click.option("--split", type=click.Choice(["dev", "test", "all"]), default="dev", show_default=True)
@click.option("--user-arm", type=click.Choice(["knows", "unsure"]), default=None)
@click.option("--limit", type=int, default=None, help="Only the first N instances (parsing checks with cpu_tiny).")
def run(methods: str, model: str, split: str, user_arm: str | None, limit: int | None) -> None:
    """Generate, execute in both environments, write results and traces."""
    from varag.eval.run import run as run_eval

    run_eval(methods, model, split, user_arm, log=click.echo, limit=limit)


@main.command("report")
@click.argument("run_id")
def report(run_id: str) -> None:
    """Compute metrics, intervals, the risk-coverage curve and the detectable-effect table; write report.md."""
    from varag.eval.report import write_report
    from varag.eval.run import runs_dir

    run_dir = runs_dir() / run_id
    if not (run_dir / "run.json").exists():
        raise click.ClickException(f"no run at {run_dir}")
    path = write_report(run_dir)
    click.echo(path.read_text(encoding="utf-8"))
    click.echo(f"written to {path} and {run_dir / 'metrics.json'}")


@main.group()
def audit() -> None:
    """Hand-labelling exports."""


@audit.command("sample")
@click.argument("run_id")
@click.option("--n", default=50, show_default=True)
@click.option("--seed", default=1234, show_default=True)
def audit_sample(run_id: str, n: int, seed: int) -> None:
    """Export outputs with the blend detector verdict for hand labelling (audit_sample.jsonl and .md)."""
    from varag.eval.audit import audit_sample as export
    from varag.eval.run import runs_dir

    run_dir = runs_dir() / run_id
    if not (run_dir / "run.json").exists():
        raise click.ClickException(f"no run at {run_dir}")
    path = export(run_dir, n, seed)
    click.echo(f"written {path} and {path.with_suffix('.md')}")


@main.command("smoke")
@click.option("--offline", is_flag=True, help="Mocks and cpu_tiny only; no GPU model.")
def smoke(offline: bool) -> None:
    """Verify, validate, run every method on the mock backends (and cpu_tiny), check the anchors, report;
    without --offline also serve-check and run the real models on the dev split."""
    from varag.eval.smoke import smoke as run_smoke

    record = run_smoke(offline, log=click.echo)
    if not record["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
