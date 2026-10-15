# VA-RAG

Version-aware RAG for pandas, NumPy and pydantic: a benchmark whose answers are executed
in two pinned environments per library, a rule-based version-inference pipeline, baselines,
and a report. The full spec is `docs/HANDOFF.md`; the literature behind it is
`docs/LITERATURE.md`; every deviation from the spec is dated in `docs/DECISIONS.md`.

## Setup (Linux: WSL2 Ubuntu)

The environments are built and locked on Linux x86_64. Work inside WSL2 (Ubuntu 24.04 here), with
the clone on the Linux filesystem (`~/...`), not under `/mnt/c`.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh    # uv 0.11 or newer, if missing
git clone <repo-url> ~/projects/VA-Rag && cd ~/projects/VA-Rag
uv sync
uv run varag env build     # the six environments from the committed locks; never --relock unless pins change
uv run varag env verify
uv run pytest
```

- `env build` rewrites `envs/manifest.json` with this machine's interpreter paths. The lock
  hashes stay the same, so the committed inventories, corpus and validation records stay valid.
- The first `corpus build` downloads the pinned tokenizer into `data/tokenizer/` (ignored) and
  checks its sha256. Nothing else needs it; the corpus itself is committed.
- Every environment pins `tzdata`, and the stripped environment sets `PYTHONTZPATH=""`, so
  `zoneinfo` reads only the pinned package, never the host's time-zone database.
- The harness caps memory with `RLIMIT_AS` and removes the network with `unshare -rn`. `varag run`
  refuses real-model backends on a host where either is missing.

## Commands

All commands run through uv from the repo root (`uv run ...`).

| Command | Does |
| --- | --- |
| `uv sync` | Creates `.venv` (Python 3.11) with the orchestrator package and pytest |
| `uv run pytest` | Unit tests; tests marked `envs` skip until the environments exist |
| `uv run varag env build` | Creates the six environments from hash-pinned locks, writes `envs/manifest.json` |
| `uv run varag env verify` | Re-probes versions and canaries; non-zero exit on any mismatch |
| `uv run varag inventory build` | Extracts inventories in each environment and writes the diffs |
| `uv run varag inventory audit` | Checks the diffs against published rule sets; prints recall per library |
| `uv run varag corpus build [--library ...]` | Builds the version-tagged chunks, executing every example in both environments |
| `uv run varag bench candidates [--library ...]` | Lists symbol and keyword-level pairs to mine for concepts, with counts per library |
| `uv run varag bench validate [concept]` | Runs the validation matrix, updates `data/tasks/MANIFEST.json` |
| `uv run varag run --methods ... --model ... --split dev` | Generates, executes in both environments, writes `runs/<id>/` |
| `uv run varag --help` | Lists every command, including those later milestones build |

## Layout

- `configs/` holds every version pair, canary, backend and threshold. No version string is hardcoded in code.
- `scripts/` holds the only code that runs inside a library environment. Stdlib only. Started as a subprocess with that environment's interpreter; prints or writes JSON.
- `src/varag/` is the orchestrator. It never imports pandas, NumPy or pydantic.
- `envs/<library>_<side>/` holds `requirements.in`, `requirements.lock` (committed) and `.venv` (ignored).
- `data/` holds inventories, rule sets, corpus and tasks. `runs/` is ignored.

## Working rules

- A concept does not exist until `bench validate` passes. Never weaken a test or a reference to make the matrix pass; drop or re-tag the concept instead.
- The environments are the authority on version facts. If a canary disagrees with the handoff, fix the canary and record it.
- Do not tune thresholds or prompts on test-split concepts.
- Stop and ask before changing version pins, the output protocol, metric definitions or the outcome classes.
- Record every deviation from the spec in `docs/DECISIONS.md` with the date and the reason.
- Write unit tests alongside each module. The signal extractor and decision rule need the densest coverage.
- Generated code is untrusted. It never runs in the orchestrator process.
