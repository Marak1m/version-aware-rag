# GPU session handoff

Status: skeleton, 2026-10-18. Filled in after M7 (Part C step 9). Until then the headings are the
contract: every section below will be present when the GPU session starts.

## What this project is

One paragraph on VA-RAG, and where the spec (`docs/HANDOFF.md`), the decisions
(`docs/DECISIONS.md`), the plans (`docs/plans/`) and the working notes (`docs/NOTES.md`) live.

## Exact state at handoff

- Last commit and what it contains.
- What is built (M0 to M7, concepts, controls) and what each `varag` command does.
- What is frozen and must not change: decision-rule thresholds, concepts and their tests, the
  dev/test split, version pins, the output protocol, metric definitions, outcome classes.

## Setup on the PC

Clone inside the WSL filesystem (`~/`), not under `/mnt/c`. `uv sync`, `varag env build`,
`varag env verify` (manifests must match the committed locks), `varag preflight`.

## Steps, in order

Each step names its command, its acceptance check, and what to do if it fails.

1. Preflight (`varag preflight`).
2. Serve check per model (`varag serve check`).
3. Full smoke (`varag smoke`).
4. Dev runs: both models, both user arms.
5. The L1 generation-config test.
6. Serving-noise check.
7. Leak audit.
8. STOP for the prompt review.
9. Test runs.
10. Export the 50-output audit sample (`varag audit sample`).
11. v1 experiments if time allows, `va_rag_portable_first` first.

## Rules

- No tuning on the test split.
- Record every deviation in `docs/DECISIONS.md`.
- Commit and push after each step.

## Runtime estimates and resumption

What `varag gpu-day` prints before starting, how runs resume from the response cache, and what
an interruption loses (nothing: results are saved after each method).
