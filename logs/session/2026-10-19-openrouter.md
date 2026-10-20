# Session log: the move to OpenRouter (2026-10-19 to 2026-10-20)

In order. Details and reasons are in docs/DECISIONS.md; every command's output is in logs/commands/.

1. Key file `openrouter-api-key` git-ignored and chmod 600 before anything else.
2. Endpoint lists read for the candidate models: the 7B coder has no endpoint; the general 7B on
   Phala, the 32B coder on Cloudflare, qwen3-coder on Google Vertex, DeepInfra and Venice.
3. OpenRouterBackend written (pinned provider, no fallbacks, require_parameters, retries, per-call
   provider/model/usage on result rows), budget guard and dry-pass cost estimate, logbook.
4. Behaviour probes of seed and repetition_penalty: Vertex accepts repetition_penalty and ignores
   it, so large is pinned to DeepInfra. No provider honours the seed under sampling.
5. Prompt-review note applied (stub, no-question line, no_entry_point, oracle_docs wording, five
   dev controls, contradiction instances and the tau_noise check, instance-major runs, sessions).
6. Endpoint checks: all three ok. Preflight 9/9 (DeepInfra degraded: warning).
7. Dev sweep: $1.24, mid and large meet the acceptance, small misses it (no_entry_point 6.5%);
   serving noise is large on Phala and DeepInfra. Prompts not frozen.
8. Test split authored by four parallel agents in git worktrees (no model calls), merged; four
   framework blockers fixed (bool values, owner-chunk fallback, None replacement, deprecated-module
   replacements); pd-017 substituted by hand; 78/78 concepts and controls validate; 335 tests pass.
9. STOP before any test run.
