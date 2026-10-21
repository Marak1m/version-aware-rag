# Logs

Everything the sessions do, kept for later reading (`src/varag/logbook.py`). No file here holds
the OpenRouter key: request headers are never logged and key-shaped text is redacted.

| Path | Holds |
| --- | --- |
| `commands/<stamp>-<command>.log` | stdout and stderr of every `varag` invocation, with its arguments |
| `openrouter/<date>-<backend>.jsonl` (`<date>.jsonl` before 2026-10-21; from 2026-10-21 committed as `.jsonl.gz`, the raw file kept locally) | every OpenRouter request (full body: messages, sampling, provider routing), the full response (text, provider, model, usage, cost), HTTP status, attempt number, backoff, latency, session; cache hits as one-line records |
| `costs.jsonl` | one line per paid call: backend, model, provider, session, instance, prompt and completion tokens, cost, the run's running total |
| `events.jsonl` | run start and end, cost estimates, budget stops |
| `checks/endpoint-<model>-<stamp>.json` | endpoint checks |
| `checks/noise-<model>-<stamp>.json` | serving-noise checks |
| `checks/sweep-<stage>-<stamp>.json` | sweep summaries |
| `sweep/final-<stamp>-<model>.log` | the final sweep's per-model log: every answer's outcome, each run's cost and time |
| `session/` | notes written by the working session (what was done, in order) |

Run results themselves are under `runs/<run_id>/` (`report.md`, `run.json`, `metrics.json`,
`results.jsonl.gz`, and the uncompressed `results.jsonl` and `traces.jsonl` while local).
