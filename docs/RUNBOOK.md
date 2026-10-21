# Runbook: model runs on OpenRouter

Status: 2026-10-19. All model inference runs on OpenRouter; nothing needs WSL GPU access. Local
vLLM serving (the first GPU session) is retired but its code is kept; its runs are archived in
`runs/_archive_local/`. The spec is `docs/HANDOFF.md`, every deviation is dated in
`docs/DECISIONS.md`, the frozen test split is in `docs/plans/composition.md`, and workflow facts
are in `docs/NOTES.md`.

## State

- **Built:** M0 to M7, the OpenRouter backend, the budget guard, endpoint checks, `varag sweep`,
  the logbook. Dev: 15 seed concepts and 6 controls, all passing `bench validate` steps 1 to 10.
- **Frozen:** decision-rule thresholds (`tau_commit` 3.0, `tau_noise` 1.5; checked on 28 dev clue
  instances and 13 dev contradiction instances); the 48 test concepts (ids, classes, changes) in
  `composition.md`; the dev/test split; version pins; outcome classes (now including
  `no_entry_point`); metric definitions; the three model pins below; the prompts
  (`prompts.sha256` in `configs/experiment.yaml`, 2026-10-21, small accepted at 6.5%
  no_entry_point by the user), renewed once to add the portable-first line.
- **Methods:** the eleven of 2026-10-19 plus `va_rag_portable_first` (L16, 2026-10-21).
- **Repeats:** small and large answer every (instance, method) 3 times in one session, mid once
  (`repeats` in `configs/models.yaml`); an instance's score is the mean over its repeats.
- **Never** change prompts, thresholds or concepts after seeing test results.

## Setup

Any Linux machine (WSL2 Ubuntu here) with the repository on the Linux filesystem:

```bash
uv sync
uv run varag env build && uv run varag env verify      # never --relock
uv run pytest
export OPENROUTER_API_KEY=sk-or-...    # or put it in ./openrouter-api-key (git-ignored)
uv run varag preflight                 # must end "without failure"
```

## Models (`configs/models.yaml`)

| Role | OpenRouter id | Pinned provider | Price ($/M in, out) | Repeats | Notes |
| --- | --- | --- | --- | --- | --- |
| small | `qwen/qwen-2.5-7b-instruct` | `phala` | 0.10, 0.20 | 3 | `qwen/qwen2.5-coder-7b-instruct` has no endpoint |
| mid | `qwen/qwen-2.5-coder-32b-instruct` | `cloudflare` | 0.66, 1.00 | 1 | honours seed and repetition penalty |
| large | `qwen/qwen3-coder` | `deepinfra/turbo` (fp4) | 0.30, 1.00 | 3 | served as fp4; Google Vertex rejected: it ignores repetition_penalty |

Every request: temperature 0, top_p 1, repetition_penalty 1, max_tokens 1024, seed 1234, and
`provider: {order: [pin], allow_fallbacks: false, require_parameters: true}`. 429 and 5xx are
retried with exponential backoff. The provider, model id and usage OpenRouter reports are on every
result row.

## Steps

Each step: command, acceptance check, what to do if it fails.

1. **Preflight.** `uv run varag preflight`. Accept: no `fail`. A degraded endpoint is a warning.
2. **Endpoint check.** `uv run varag endpoint check`. Accept: `ok` per model (same prompt twice
   identical, provider matches the pin, repetition penalty honoured). On a problem, do not run:
   pick another provider, re-probe, record why in DECISIONS.
3. **Dev sweep** (done 2026-10-20). `uv run varag sweep --stage dev --max-usd 15`: smoke, every
   method on dev for each model and both user arms, the noise check. Accept per model:
   `no_entry_point` under 5% and second questions under 2% of answers; then
   `uv run varag bench freeze-prompts --note "..."` (done 2026-10-21).
4. **A new method on dev** (`va_rag_portable_first`, 2026-10-21):
   `uv run varag run --methods va_rag,va_rag_portable_first --model <m> --split dev --fresh-cache --repeats 1`
   per model, then renew the prompt freeze and commit.
5. **Final sweep** (frozen code and prompts; refused while anything under src/, configs/, data/,
   scripts/ or envs/ differs from the commit): `uv run varag sweep --stage final --max-usd 20`.
   Preflight, endpoint checks, offline smoke, the whole sweep priced before the first paid call,
   then per model in its own thread (one session id and one session-private cache per model): dev
   and test in both arms with the model's repeats, plus mid's noise-subset repeat. Writes each
   run's report and `docs/results/final-<stamp>/` (`summary.md`, `summary.json`, `<model>.md`,
   the guard audit sample). `--resume` continues the newest final sweep on the same commit with
   its sessions and caches. `uv run varag summary` rewrites the summary from the sweep record.
6. **STOP** and post the combined summary, the cost and anything that failed.

## Rules

- No tuning on the test split. Compare methods only within one session (`session` on every row:
  provider plus run start time); the sweep's noise check says how much differs across sessions.
- Never edit `configs/` while a run is in progress: `run.json` records the config hash, the prompt
  hash and the dirty tracked files as of the start.
- Keep the key out of every file except the git-ignored key file.

## Costs, runtimes, resumption

`varag run --max-usd` prints the estimate before the first paid call and refuses to start above
the cap; at the cap it stops cleanly between instances. Every paid call is in `logs/costs.jsonl`;
`logs/openrouter/` holds every request and response. Generations are cached in `runs/_cache/`
(keyed by backend, model, pinned provider, messages and sampling), so a rerun after an interruption
pays only for requests that never completed, and instance-major order means every method has the
same completed instances. `--resume` on the sweep skips finished (model, arm) runs.

## Dev results (2026-10-20)

Sweep `runs/sweep-dev-20261020T005802Z.json`, $1.24 (session total $1.25). Intended-version pass,
knows arm, 95 targeted dev instances:

| Method | small | mid | large |
| --- | --- | --- | --- |
| va_rag | 57.9% | 80.0% | 85.3% |
| plain_rag | 42.1% | 64.2% | 69.5% |
| mind_version | 42.1% | 75.8% | 69.5% |
| two_branch | 52.6% | 72.6% | 83.2% |
| always_ask | 52.6% | 72.6% | 83.2% |
| oracle_docs | 54.7% | 71.6% | 83.2% |
| no_retrieval | 36.8% | 50.5% | 55.8% |

- Acceptance: mid and large met (no no_entry_point, no second question); small not met
  (no_entry_point 6.5%, all pydantic class-without-function answers). Prompts not frozen.
- Serving noise within one session: small 32.7% of responses (12.7% of outcomes), mid 3.2% (0.5%),
  large 57.3% (12.7%); across sessions about 11 to 67% of responses. Compare methods within a
  session only.
- Test split: 48 concepts and 9 controls authored and validated (78/78 with dev). Not run.

## Final sweep (2026-10-21)

`runs/sweep-final-20261021T082811Z.json`; summary, per-model reports and the guard audit sample in
`docs/results/final-20261021T082811Z/`. $4.75 over the three sessions. Test split, knows arm,
strict intended-version pass with 95% concept-bootstrap intervals:

| Method | small | mid | large |
| --- | --- | --- | --- |
| va_rag | 42.1 [31.7, 53.1] | 71.5 [60.9, 81.4] | 81.1 [71.2, 89.6] |
| va_rag_portable_first | 42.1 [32.2, 52.4] | 70.2 [59.3, 80.4] | 78.9 [69.5, 87.3] |
| two_branch | 37.3 [27.6, 47.8] | 67.1 [55.2, 78.4] | 79.7 [69.6, 88.6] |
| oracle_docs | 39.8 [28.7, 51.6] | 68.4 [57.7, 78.7] | 81.7 [71.5, 90.6] |
| plain_rag | 30.6 [21.0, 41.0] | 54.4 [44.6, 63.8] | 60.1 [51.8, 67.9] |
| no_retrieval | 26.8 [18.0, 36.3] | 52.2 [42.2, 61.8] | 59.5 [50.8, 67.7] |

- Large's test-knows was interrupted by a DeepInfra outage (11:13 to 12:09 UTC) and resumed in the
  same session from the session cache (DECISIONS, 2026-10-21 "Final sweep").
- Nothing is to change after these results: prompts, thresholds, concepts and code stay frozen.

