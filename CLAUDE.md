# VA-RAG

Version-aware RAG for pandas, NumPy and pydantic: a benchmark whose answers are executed
in two pinned environments per library, a rule-based version-inference pipeline, baselines,
and a report. The full spec is `docs/HANDOFF.md`; the literature behind it is
`docs/LITERATURE.md`; every deviation from the spec is dated in `docs/DECISIONS.md`.

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
