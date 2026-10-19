# GPU session handoff

Status: filled 2026-10-19 by the first GPU session, after the dev phase (steps 1 to 7 of the
session brief). The test split is frozen but not authored, so no test run has happened.

## What this project is

VA-RAG is a version-aware RAG benchmark and pipeline for pandas, NumPy and pydantic: every answer
is executed in two pinned environments per library (old and new), a rule-based extractor infers
the user's version from their context, the system asks when it cannot, and a blend guard checks
the generated code. The spec is `docs/HANDOFF.md`, every deviation is dated in `docs/DECISIONS.md`,
the plans are in `docs/plans/` (the frozen test split is in `docs/plans/composition.md`), and
workflow facts are in `docs/NOTES.md`.

## Exact state at handoff

- **Built:** M0 to M7; 15 dev seed concepts and one control (ctl-np-001), all passing `bench
  validate` steps 1 to 10 (step 10, new: `wrong.py`, a plausible wrong answer, fails in both
  environments). The full `varag smoke` passes 28/28 on this PC with both models.
- **Frozen, do not change:** the decision-rule thresholds (`tau_commit` 3.0, `tau_noise` 1.5,
  `frozen_on: 2026-10-19` in `configs/experiment.yaml`; `varag run` refuses the test split
  without it); the 48 test concepts (ids, classes and changes in `docs/plans/composition.md`;
  substitute only when validation forces it, from the reserve list, logged in DECISIONS); the
  dev/test split; the version pins; the output protocol; the metric definitions; the outcome
  classes; both model revisions.
- **Not done:** the 48 test concepts and the 14 missing controls (5 dev, 9 test) are not authored;
  no test-split run exists. The prompt review (below) is pending.

## Setup on the PC

WSL2 Ubuntu 24.04 on Windows, RTX 5070 Ti 16 GB, driver 617.14, 24 cores, 23 GB RAM for WSL. Clone
inside the WSL filesystem (`~/code/version-aware-rag`), never under `/mnt/c`.

```bash
uv sync                                   # uv 0.13.1 here; 0.11 or newer works
uv run varag env build                    # never --relock; Python 3.11.17 here (laptop: 3.11.15)
uv run varag env verify
uv run pytest                             # 316 passed
# vLLM in its own venv, outside the repo (configs/models.yaml, serving.vllm):
uv venv --python 3.12 ~/.venvs/vllm-0.31.0
VIRTUAL_ENV=~/.venvs/vllm-0.31.0 uv pip install vllm==0.31.0 --torch-backend=auto
uv run varag preflight                    # 13 checks; must end "without failure"
```

vLLM 0.31.0 brings torch 2.13.0+cu132 (CUDA 13.2, sm_120 kernels). The host CUDA toolkit (12.8)
is not used; FlashInfer's sampler says "SM 12.x requires CUDA >= 12.9" and vLLM falls back to its
own sampler, which is harmless. No Hugging Face token is needed: both repos are public. Weights go
to `~/.cache/huggingface` (5.2 GiB and 9.3 GiB).

**VRAM is shared with Windows.** Desktop apps (browsers, Discord, Parsec, VS Code, the NVIDIA
overlay) held 5.3 to 6.7 GiB at the start. The 7B runs with that; the 14B needs other processes at
about 2.2 GiB or less, so close GPU-heavy Windows apps first. `varag preflight` shows the free
memory against each model's need; `/mnt/c/Windows/System32/nvidia-smi.exe` lists the Windows
processes.

## Serving

One model on the GPU at a time. `varag serve start|stop|command --model <backend>` builds the
command from `configs/models.yaml`, logs to `runs/_serve/<backend>.log` (with every request's
resolved sampling parameters) and waits until `/v1/models` answers.

```
# primary (port 8000), ready in 45 s once cached (first start with download: about 4 min)
vllm serve Qwen/Qwen2.5-Coder-7B-Instruct-AWQ --revision 8e8ed243bbe6f9a5aff549a0924562fc719b2b8a
  --tokenizer-revision 8e8ed243bbe6f9a5aff549a0924562fc719b2b8a --served-model-name primary
  --host localhost --port 8000 --seed 1234 --enable-log-requests --generation-config vllm
  --max-model-len 8192 --quantization awq --gpu-memory-utilization 0.5 --max-num-seqs 4

# vllm_large (port 8001), ready in 25 to 35 s once cached
vllm serve Qwen/Qwen2.5-Coder-14B-Instruct-AWQ --revision eb3172f06a6d6b3a15f08947b0668d782e4d2d2c
  --tokenizer-revision eb3172f06a6d6b3a15f08947b0668d782e4d2d2c --served-model-name vllm_large
  --host localhost --port 8001 --seed 1234 --enable-log-requests --generation-config vllm
  --max-model-len 8192 --quantization awq --gpu-memory-utilization 0.86 --max-num-seqs 4
```

Both run vLLM's AWQ Marlin kernel, FlashAttention 2, torch.compile and CUDA graphs; they differ
only in the memory fraction. The 14B's settings were found by trial (DECISIONS, "Serving the
14B"): 0.62 and 0.78 ran out of memory in the profiling pass; `--enforce-eager` and a smaller
prefill budget would also have worked but change kernels or chunking. KV cache: 3.84 GiB, 20,976
tokens, at 0.86. Weight offload is not an option under WSL2 (no pinned memory).

`primary_genconfig` (port 8000) is the L1 test's other arm: the same 7B with `--generation-config
auto`, requests sending only `max_tokens` and `seed`. It is `report: false`.

## Steps, in order

Each step: command, acceptance check, what to do if it fails.

1. **Preflight.** `uv run varag preflight`. Accept: no `fail`. A `warn` on `vram:vllm_large` means
   close Windows apps before the 14B.
2. **Serve check per model.** `varag serve start --model primary`, then `varag serve check --model
   primary` (the same for `vllm_large`). Accept: `ok`; effective repetition_penalty 1.0,
   temperature 0.0, top_p 1.0, seed 1234 from the server log; the rendered prompt starts with our
   system prompt. On a problem do not run: the numbers would not be ours.
3. **Full smoke.** `uv run varag smoke` (serves each model itself). Accept: `PASS: 28/28 steps`.
4. **Dev runs.** The smoke's runs are the dev runs: every method, both models, both arms.
5. **L1 test.** Serve `primary_genconfig`, `varag run --methods plain_rag --model primary_genconfig
   --split dev --user-arm knows`, then `varag compare l1 <primary knows run> <that run>`.
6. **Serving noise.** `varag run --methods all --model <m> --split dev --user-arm knows --instances
   configs/noise_subset_dev.txt --fresh-cache`, twice; `varag compare noise <a> <b>`.
7. **Leak audit.** `varag run --methods all --model <m> --split dev --user-arm leak_audit`, then
   `varag compare leak <leak run> <unsure run> --tolerance <noise share>`.
8. **STOP for the prompt review.**
9. **Test runs** (after the 48 concepts are authored and validated): `uv run varag gpu-day`.
10. **Audit sample:** gpu-day exports it (`varag audit sample <primary knows run> --n 50`).
11. **v1 experiments** if time allows, `va_rag_portable_first` first.

## Rules

- No tuning on the test split; thresholds and prompts are tuned on dev only, and are frozen.
- Record every deviation in `docs/DECISIONS.md`. Commit and push after each step.
- Never edit `configs/` while a run is in progress: `run.json` records the config hash and the
  dirty tracked files as of the run's start.
- Serve one model at a time; `varag serve start` refuses a second vLLM backend.

## Runtime estimates and resumption

Measured here, with generation sequential (one request in flight) and execution on 8 threads
(`execution.workers`): the 7B takes about 0.4 s per (instance, method) answer, 342 s for a fresh
dev run of 11 methods x 83 instances; the 14B about 1.0 s, 932 s. A run whose generations come
from the response cache takes 80 to 125 s (execution only). Validation of the 16 dev concepts
takes about 10 minutes; the full smoke about 45 minutes.

`varag gpu-day` prints the plan before it starts: per model, the answers it will generate, the
seconds per answer (from the newest uncached full run, else `seconds_per_answer` in
`configs/models.yaml`) and the minutes that makes, plus 1 to 5 minutes per server start. Then:
preflight; per model, serve start, serve check, the serving-noise pair, one run per arm with
reports, serve stop; the audit sample; a summary in `runs/gpu-day-<stamp>.json`. `--dry-run`
prints the plan only; `--resume` skips a (model, arm) whose newest run has the same split,
methods, commit, configs and task manifest.

An interruption loses only execution time: every generation is in the response cache
(`runs/_cache/`, keyed by backend, revision, messages and sampling), so a rerun replays it without
a model call; `results.jsonl` is flushed after each method.

## Dev results and checks (2026-10-19)

Reports (committed `report.md`, `run.json`, `metrics.json`, `results.jsonl.gz` under `runs/`):

| Model | knows | unsure |
| --- | --- | --- |
| 7B (`primary`) | `20261019T111727Z-primary-2266f7e7` | `20261019T111858Z-primary-ac41cde3` |
| 14B (`vllm_large`) | `20261019T112205Z-vllm_large-7462f484` | `20261019T113804Z-vllm_large-412461b7` |

Intended-version pass on the 82 targeted dev instances (knows arm; 16 concepts, so these are
smoke readings, not results): 7B `va_rag` 46.3%, `plain_rag` 41.5%, `oracle_docs` 37.8%,
`no_retrieval` 25.6%; 14B `va_rag` 69.5%, `plain_rag` 54.9%, `oracle_docs` 65.9%, `no_retrieval`
48.8%. `varag gpu-day --split dev` (summary `runs/gpu-day-20261019T123931Z.json`, 18 minutes
from start to finish) reproduced every figure from the response cache.

Checks (details in DECISIONS, "Dev checks"):

- **L1:** 7B `plain_rag` 42.2% pinned against 37.3% under the repository's generation config
  (−4.8 points; 69 of 83 responses differ). The serve-check output for all three backends and
  example prompts are in `docs/serve_check_2026-10-19.txt`.
- **Serving noise:** within one server session 0.9% (7B) and 0% (14B) of 220 responses change;
  across server restarts about 10.5% and 10.9% of responses and 6.4% and 2.3% of outcomes. Keep a
  model's comparable runs inside one server session.
- **Leak audit:** passes for both models (leak arm never above the uninformative-reply arm).

Open for the prompt review: pydantic answers that omit the entry-point function (7B 225 answers,
14B 117), a second question after "I'm not sure." in the unsure arm, and the 7B's over-asking under
`mind_version`. None was acted on.
