"""The ``varag`` command line. Every command from the handoff is listed here; the
ones a later milestone builds raise ``not implemented until M<n>``."""

from __future__ import annotations

from pathlib import Path

import click


@click.group()
@click.version_option(package_name="varag")
def main() -> None:
    """VA-RAG: version-aware RAG benchmark, pipeline and two-environment harness."""
    import sys

    from varag.logbook import tee_command

    tee_command(sys.argv[1:])


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
    from varag.pipeline.thresholds import contradiction_instances, contradiction_sweep

    conflicts = contradiction_instances(split)
    tau_commit, tau_noise = thresholds()
    click.echo(f"{len(conflicts)} {split} contradiction instances (right decision: CONTEXT_CONFLICT), tau_commit {tau_commit:g}")
    for tn, hit, total in contradiction_sweep(conflicts, tau_commit):
        click.echo(f"  tau_noise {tn:4g}: {hit}/{total} CONTEXT_CONFLICT" + ("  <- configured" if tn == tau_noise else ""))
    stamp = frozen()
    click.echo(f"frozen on {stamp['frozen_on']} ({stamp.get('frozen_split', 'dev')})" if stamp else "thresholds are NOT frozen")


@bench.command("freeze-prompts")
@click.option("--note", required=True, help="Why the prompts are frozen now (the dev evidence).")
def bench_freeze_prompts(note: str) -> None:
    """Write the hash of every prompt text into configs/experiment.yaml (prompts.sha256); test runs
    then refuse to start if any wording changes."""
    import re
    from datetime import date

    from varag.config import configs_dir
    from varag.pipeline.prompts import prompts_sha256

    path = configs_dir() / "experiment.yaml"
    text = path.read_text(encoding="utf-8")
    block = (f"# Frozen prompts (`varag bench freeze-prompts`): sha256 over every prompt text the methods send\n"
             f"# (varag.pipeline.prompts). Test runs refuse to start when the live hash differs.\n"
             f"prompts:\n  sha256: \"{prompts_sha256()}\"\n  frozen_on: \"{date.today().isoformat()}\"\n  note: {json_quote(note)}\n")
    text = re.sub(r"# Frozen prompts \(`varag bench freeze-prompts`\).*?\nprompts:\n(?:  .*\n)+", "", text, flags=re.S)
    path.write_text(text.rstrip("\n") + "\n\n" + block, encoding="utf-8", newline="\n")
    click.echo(block)


def json_quote(text: str) -> str:
    import json

    return json.dumps(text)


# --- serve -----------------------------------------------------------------


@main.group()
def serve() -> None:
    """Model serving checks."""


@serve.command("start")
@click.option("--model", required=True, help="A vLLM backend id from configs/models.yaml.")
@click.option("--timeout", default=1800, show_default=True, help="Seconds to wait for the server (includes the first download).")
def serve_start(model: str, timeout: int) -> None:
    """Start vLLM for one backend with the pinned revision and serve_args; wait until it answers."""
    from varag.serving import start

    start(model, timeout_s=timeout, log=click.echo)


@serve.command("stop")
@click.option("--model", required=True)
def serve_stop(model: str) -> None:
    """Stop the server started by `varag serve start`."""
    from varag.serving import stop

    if not stop(model, log=click.echo):
        click.echo(f"{model} is not running")


@serve.command("command")
@click.option("--model", required=True)
def serve_command_cmd(model: str) -> None:
    """Print the exact vLLM command `serve start` runs for a backend."""
    from varag.serving import serve_command

    click.echo(" ".join(serve_command(model)))


@main.group()
def endpoint() -> None:
    """OpenRouter endpoint checks."""


@endpoint.command("check")
@click.option("--model", "models", multiple=True, help="An openrouter backend (repeatable); default all active ones.")
def endpoint_check_cmd(models: tuple[str, ...]) -> None:
    """Endpoint live, parameters declared, same prompt twice identical, reported provider matches the pin."""
    from varag.config import load_models
    from varag.eval.serve import endpoint_check, format_endpoint_report

    names = list(models) or [k for k, v in load_models()["backends"].items() if v.get("type") == "openrouter" and v.get("active", True)]
    failed = []
    for name in names:
        report = endpoint_check(name)
        click.echo(format_endpoint_report(report))
        if report["problems"]:
            failed.append(name)
    if failed:
        raise SystemExit(1)


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
@click.option("--user-arm", type=click.Choice(["knows", "unsure", "leak_audit"]), default=None,
              help="leak_audit: every question is replaced by an irrelevant one (the leak audit only).")
@click.option("--limit", type=int, default=None, help="Only the first N instances (parsing checks with cpu_tiny).")
@click.option("--instances", "instances_file", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None,
              help="A file of instance ids, one per line: run only those (the serving-noise subset).")
@click.option("--fresh-cache", is_flag=True, help="Use a cache private to this run: every request reaches the server (serving-noise check).")
@click.option("--max-usd", type=float, default=None, help="Spending cap: refuse to start when the estimate exceeds it, stop when the running total reaches it.")
@click.option("--repeats", type=int, default=None, help="Repeat indices 0..N-1 per (instance, method); default the backend's `repeats` in configs/models.yaml.")
def run(methods: str, model: str, split: str, user_arm: str | None, limit: int | None, instances_file: Path | None, fresh_cache: bool,
        max_usd: float | None, repeats: int | None) -> None:
    """Generate, execute in both environments, write results and traces."""
    from varag.eval.run import run as run_eval

    ids = [line.strip() for line in instances_file.read_text(encoding="utf-8").splitlines()
           if line.strip() and not line.startswith("#")] if instances_file else None
    run_eval(methods, model, split, user_arm, log=click.echo, limit=limit, instance_ids=ids, fresh_cache=fresh_cache, max_usd=max_usd,
             repeats=list(range(repeats)) if repeats else None)


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
def compare() -> None:
    """Run-to-run checks: serving noise, the L1 generation-config test, the leak audit."""


def _run_dir(run_id: str) -> Path:
    from varag.eval.run import runs_dir

    path = runs_dir() / run_id
    if not (path / "run.json").exists():
        raise click.ClickException(f"no run at {path}")
    return path


@compare.command("noise")
@click.argument("run_a")
@click.argument("run_b")
def compare_noise(run_a: str, run_b: str) -> None:
    """Share of (instance, method) responses and outcomes that changed between two fresh-cache runs."""
    from varag.eval.compare import format_noise, noise

    click.echo(format_noise(noise(_run_dir(run_a), _run_dir(run_b))))


@compare.command("l1")
@click.argument("run_pinned")
@click.argument("run_genconfig")
@click.option("--method", default="plain_rag", show_default=True)
def compare_l1(run_pinned: str, run_genconfig: str, method: str) -> None:
    """plain_rag under our pinned sampling against the model's own generation config (handoff L1)."""
    from varag.eval.compare import format_l1, l1

    click.echo(format_l1(l1(_run_dir(run_pinned), _run_dir(run_genconfig), method)))


@compare.command("leak")
@click.argument("run_leak")
@click.argument("run_unsure")
@click.option("--tolerance", default=0.0, show_default=True, help="Allowed excess, e.g. the measured serving-noise share.")
@click.option("--no-ask-run", default=None, help="A run with va_rag_no_ask, printed as the no-question reference.")
def compare_leak(run_leak: str, run_unsure: str, tolerance: float, no_ask_run: str | None) -> None:
    """Leak audit: the leak_audit arm must not pass more often than the uninformative (unsure) arm."""
    from varag.eval.compare import format_leak, leak

    result = leak(_run_dir(run_leak), _run_dir(run_unsure), tolerance, _run_dir(no_ask_run) if no_ask_run else None)
    click.echo(format_leak(result))
    if not result["passed"]:
        raise SystemExit(1)


@main.group()
def audit() -> None:
    """Hand-labelling exports."""


@audit.command("sample")
@click.argument("run_ids", nargs=-1, required=True)
@click.option("--n", default=50, show_default=True)
@click.option("--seed", default=1234, show_default=True)
@click.option("--stratify", is_flag=True, help="Half from answers the detector flags, half from the rest, with weights for recall.")
@click.option("--out", "out_dir", type=click.Path(file_okay=False, path_type=Path), default=None,
              help="Where to write audit_sample.jsonl and .md (default: the first run's directory).")
def audit_sample(run_ids: tuple[str, ...], n: int, seed: int, stratify: bool, out_dir: Path | None) -> None:
    """Export outputs with the blend detector verdict for hand labelling (audit_sample.jsonl and .md);
    several runs are pooled."""
    from varag.eval.audit import audit_sample as export

    path = export([_run_dir(r) for r in run_ids], n, seed, out_dir=out_dir, stratify=stratify)
    click.echo(f"written {path} and {path.with_suffix('.md')}")


@main.command("sweep")
@click.option("--stage", type=click.Choice(["dev", "test", "final"]), default="dev", show_default=True)
@click.option("--models", default="", help="Comma-separated OpenRouter backends; default all active ones.")
@click.option("--arms", default="knows,unsure", show_default=True)
@click.option("--methods", default="all", show_default=True)
@click.option("--max-usd", type=float, default=None, help="Spending cap for the whole sweep.")
@click.option("--resume", is_flag=True, help="Skip a (model, arm) whose newest run has the same split, methods, commit, configs and tasks; "
              "final: continue the newest final sweep on the same commit, with its sessions and caches.")
@click.option("--dry-run", is_flag=True, help="Print the plan only.")
def sweep_cmd(stage: str, models: str, arms: str, methods: str, max_usd: float | None, resume: bool, dry_run: bool) -> None:
    """dev: preflight, endpoint checks, smoke, dev runs in both arms with reports, the noise check, STOP.
    test: endpoint checks and the test runs (refused until prompts and thresholds are frozen and the
    test concepts are validated). final: frozen code and prompts; dev and test, both arms, the
    models' repeats, one session per model, models side by side under one cap; reports, the
    combined summary, the audit sample, STOP."""
    from varag.sweep import final_sweep, sweep

    chosen = [m for m in models.split(",") if m] or None
    arm_list = [a for a in arms.split(",") if a]
    if stage == "final":
        record = final_sweep(chosen, arm_list, methods, max_usd=max_usd, resume=resume, dry_run=dry_run, log=click.echo)
    else:
        record = sweep(stage, chosen, arm_list, methods, max_usd=max_usd, resume=resume, dry_run=dry_run, log=click.echo)
    if not record["ok"]:
        raise SystemExit(1)


@main.command("summary")
@click.argument("record", required=False, type=click.Path(exists=True, dir_okay=False, path_type=Path))
def summary_cmd(record: Path | None) -> None:
    """Write the final sweep's combined summary, per-model reports and audit sample under
    docs/results/final-<stamp>/ (default: the newest runs/sweep-final-*.json)."""
    import json

    from varag.eval.run import runs_dir
    from varag.eval.summary import write_final

    if record is None:
        found = sorted(runs_dir().glob("sweep-final-*.json"))
        if not found:
            raise click.ClickException("no runs/sweep-final-*.json")
        record = found[-1]
    path = write_final(json.loads(record.read_text(encoding="utf-8")), log=click.echo)
    click.echo(path.read_text(encoding="utf-8"))


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
