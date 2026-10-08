# VA-RAG handoff for Claude Code

Oct 8, 2026 · @YUVRIK

This is the build spec for a working base of VA-RAG: two pinned environments per library, a small validated benchmark, the version-aware pipeline, the baselines, and a two-environment execution harness. Start at Build order; every other section is the reference for a milestone.

Revision 2 folds in a literature review of roughly 200 papers and tools. The changes it produced are numbered L1 to L18 under Changes from the literature review, and each affected section below is already updated.

## Scope of the base version

The base version (v0) is the whole pipeline running end to end on a small seed benchmark, testable without a GPU through a mock model.

In scope:

- Six isolated library environments (old and new for pandas, NumPy and pydantic), built from hash-pinned lock files and verified.
- An API inventory per environment and an old/new diff per library.
- A version-tagged documentation corpus with gold-chunk injection.
- 15 seed concepts (5 per library). They expand to 60 ambiguous instances, 12 version-stated controls and 6 no-conflict controls.
- VA-RAG (version inference, selective asking, blend guard), seven baselines and three ablations.
- Execution of every answer in both environments, outcome classification, metrics with confidence intervals, and a report.

Out of scope until the base works: the full 60-concept benchmark, the larger model, embedding retrieval, the 50-failure taxonomy, and the changes marked v1 under Changes from the literature review.

Done means one command, `varag smoke`, passes. It verifies the environments, validates every seed concept, runs every method on the mock backends and on the 7B endpoint, and writes a report.

Two harness sanity anchors must hold before any real model is run:

- A mock model that returns the target-version reference scores 100% intended-version pass rate.
- A mock model that returns the other version's reference scores 0%, with every instance classified `wrong_version`.

## Changes from the proposal

The method is unchanged: infer the version from context, ask when unsure, guard against blends. These twelve changes tighten the benchmark and the measurement around it.

| # | Proposal | v0 does | Why |
| --- | --- | --- | --- |
| 1 | 120 ambiguous tasks, each with one hidden target | 60 concepts, each run for both targets, with and without a clue: 240 ambiguous instances | Both references and tests are already required per task. The factorial halves authoring, balances old/new by construction, and gives paired comparisons. |
| 2 | Version pairs not specified | Pairs that span a removal boundary: pandas 1.5.3 vs 3.0.6, NumPy 1.26.4 vs 2.4.x, pydantic 1.10.13 vs 2.13.4 | "Each reference passes only in its own environment" needs the old API to be gone, not just deprecated. pandas 2.x and NumPy 2.0 to 2.3 still run several old calls, such as applymap and np.trapz, with only a warning. |
| 3 | Each reference passes only in its own environment | Kept, and each concept also declares how it is exclusive (`removal`, `deprecation`, `behavior`) and whether a portable third solution is known | A removed API usually has a replacement that already existed in the old version (`pd.concat` for `DataFrame.append`). A model that writes that passes both environments without resolving any ambiguity. The benchmark has to see that. |
| 4 | Outcome is pass or fail in the intended version | Four outcomes from the two runs: `target_only`, `portable`, `wrong_version`, `broken` | Separates a correct commit from a lucky portable answer, and a wrong commit from broken code. |
| 5 | Error messages are a version clue | Errors are negative evidence: "no attribute 'append'" means the installed version lacks it. An error overrides the code that caused it. | A user pasting failing code is the common case. Reading that code as positive evidence infers the wrong version. |
| 6 | Blend = mixed APIs | Code that mixes APIs inside a version guard (`try/except ImportError`, `hasattr`, `__version__` check) is not a blend | That is deliberate portability. Counting it would inflate blend rate. |
| 7 | Simulated user answers a question | Every method shares one ask protocol, and the simulated user only answers questions about the version | Makes ask rates comparable across baselines and stops irrelevant questions from being rewarded. |
| 8 | Chunks tagged with version | Tag shown to the model by default, with a no-tag ablation. Deprecation notes in old docstrings kept by default, with a strip ablation. | Both tell the model which side is newer. The effect should be measured, not assumed. |
| 9 | Thresholds not discussed | Concepts split 20% dev, 80% test. Thresholds and prompts tuned on dev only. | Keeps the reported numbers honest. |
| 10 | Bootstrap CIs, paired tests | Bootstrap resamples concepts, not instances. Holm correction across comparisons. | Four instances of one concept are correlated. Instance-level resampling understates the interval. |
| 11 | Realistic version clues | Error clues are real tracebacks captured by running wrong-version code in the target environment | Authentic text, no hand-written error strings. |
| 12 | Models served with vLLM | Same, plus mock backends and a response cache | The whole pipeline is testable on a laptop and reruns are deterministic. |

## Prior work and where VA-RAG is new

No paper we found combines an unstated version, mixed-version retrieved documentation, a clarify-or-answer decision and execution in both environments. Each piece has its own literature, and it supports the shape of this design while exposing specific weak points in revision 1.

| Facet | Closest prior work | What it lacks relative to VA-RAG |
| --- | --- | --- |
| Benchmark construction and scoring | [GitChameleon 2.0](https://arxiv.org/abs/2507.12367): 328 problems, 26 libraries, hidden tests | Version is stated; one environment; no wrong-version outcome |
| One answer run under several versions | [CodeUpdateArena](https://arxiv.org/abs/2407.06249) (must pass new, fail old); [quantum-api-drift](https://arxiv.org/abs/2607.04072) (three Qiskit environments) | Version or update is given to the model; no retrieval conflict |
| Version not stated | [LibEvoBench](https://arxiv.org/abs/2606.25402); [PinTrace](https://arxiv.org/abs/2605.06279) | Static scoring, or measures which pin the model picks |
| Mixed-version corpus | [VersionRAG](https://arxiv.org/abs/2510.08109) | Question answering, not code; version named in the query |
| Blending old and new APIs | [Ashik et al.](https://arxiv.org/abs/2604.09515); [AmbigDocs](https://arxiv.org/abs/2404.12447) | A share of one failure subset; AmbigDocs is not code |
| Asking when unsure, for code | [ClarifyCodeBench](https://arxiv.org/abs/2607.00711); [HumanEvalComm](https://arxiv.org/abs/2406.00215) | Library version is not an ambiguity category |
| Version inference from code | [SnifferDog](https://arxiv.org/abs/2103.02959) | Reports "does the notebook run", not old-vs-new accuracy |
| Inventory-based output guard | [Khati et al.](https://arxiv.org/abs/2601.19106) | One version, curated samples, no keyword check |

**Findings that drive the changes:**

| Finding | Number | Source |
| --- | --- | --- |
| A version tag shown to the model barely helps; version-matched docs do | +0.2 to +1.0 F1 vs +4.5 to +14.2 | [LibEvolutionEval](https://aclanthology.org/2025.naacl-long.348.pdf) |
| One outdated passage beside the current one misleads 7B models, even with timestamps and a "prefer current" instruction | 17% (Llama-3.1-8B), 22% (Qwen2.5-7B) harmful answers | [HoH](https://aclanthology.org/2025.acl-long.301.pdf) |
| The surrounding code decides which API a model emits | 70 to 90% deprecated usage in old-style context, 9 to 18% in current context | [Wang et al.](https://arxiv.org/abs/2406.09834) |
| Small models merge sources | 19 to 22% merged answers for 7B models | [AmbigDocs](https://arxiv.org/abs/2404.12447) |
| Document order alone moves a 7B model | 33% to 83% (Llama2-7B) | [Xie et al.](https://arxiv.org/abs/2305.13300) |
| 7B models cannot decide from a prompt when to ask | 0.00 detection F1 (Mistral 7B, direct prompting) | [APA](https://arxiv.org/abs/2404.11972) |
| Over-asking is costly on clean inputs | 65.6% to 27.5% Pass@1 | [HumanEvalComm](https://arxiv.org/abs/2406.00215) |
| Version confusion sits in keyword arguments, not names | Negligible at name level; 6 to 14% anachronistic parameters | [LibEvoBench](https://arxiv.org/abs/2606.25402) |
| An inventory guard is precise but incomplete | 100% precision, 87.6% recall on 200 curated snippets | [Khati et al.](https://arxiv.org/abs/2601.19106) |
| Naming the replacement is what makes a repair prompt work | 95.5% fixed (CodeLlama-7b) | [Wang et al.](https://arxiv.org/abs/2406.09834) |
| Self-repair can hurt this exact model when the verdict is noisy | 81.7 to 78.0 on HumanEval+ (Qwen2.5-Coder-7B) | [Chen et al.](https://aclanthology.org/2025.acl-long.881.pdf) |
| The signature is the part of a doc that drives valid calls | 41.8% to 86.8% valid with the signature added | [Jain et al.](https://arxiv.org/abs/2407.09726) |

Three claims are defensible as new, each worded "to our knowledge": the benchmark combination, a measured blend rate for code generated from mixed-version documentation, and accuracy figures for inferring a major version from user context.

Two cautions. The novelty finding rests on keyword search, not a full citation crawl. The numbers above were transcribed by an automated reader during the review, so check each against its PDF before quoting it in the paper. The full review, with every source, is the file "Version aware RAG literature review.md".

## Changes from the literature review

Eighteen changes: fourteen in the base version, three as later experiments, and one split between the two. The method keeps its shape: the review supports rule-based inference outside the model, a hard version filter, a deterministic guard, one regeneration and a templated question.

"v0" means build it now. "v1" means an experiment to run once the base works. "Evidence" means a cited measurement supports the mechanism. "Inference" means it is our design extrapolation and needs its own test.

| # | Change | Why | Stage | Basis |
| --- | --- | --- | --- | --- |
| L1 | Pin the decoding configuration: start vLLM with `--generation-config vllm`, send every sampling parameter explicitly, log the rendered prompt | vLLM loads the model's own generation config by default. For Qwen2.5-Coder-7B-Instruct that is temperature 0.7 and repetition penalty 1.1 ([vLLM](https://docs.vllm.ai/en/latest/cli/serve/), [Qwen config](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/blob/main/generation_config.json)). | v0 | Evidence for the facts; the effect on scores is inference |
| L2 | Inventory gains a `deprecated_in_new` bucket and an `unknown` signature state, and is audited against published migration rule sets | Pydantic V1 methods such as `.dict()` still exist on V2 and only warn, so an existence diff files them under "same" ([migration guide](https://pydantic.dev/docs/validation/latest/get-started/migration/)). `inspect` has known holes for all three libraries. | v0 | Evidence |
| L3 | Blend guard binds keyword arguments against per-version signatures, and abstains when it cannot attribute a call | Version confusion sits in parameters ([LibEvoBench](https://arxiv.org/abs/2606.25402)). A rename breaks only calls that pass the keyword ([PCART](https://arxiv.org/abs/2406.03839)). | v0 | Evidence for the parts; the combined rule is inference |
| L4 | Regeneration uses a fresh prompt with the replacement's signature and one example, and is accepted only if violations go down | Naming the replacement fixed 95.5% of cases; error plus retrieved context beats error alone ([Wang et al.](https://arxiv.org/abs/2406.09834), [CoCoGen](https://aclanthology.org/2024.findings-acl.138.pdf)). Noisy repair hurts Qwen2.5-Coder-7B. | v0 | Evidence; the acceptance check is inference |
| L5 | An error clue becomes a negative constraint in the generation prompt: "X is not available in your version" | The user's failing code primes the model toward the API that failed ([Wang et al.](https://arxiv.org/abs/2406.09834)). | v0 | Inference from evidence |
| L6 | The question is a closed choice with a way to find out and a "not sure" option. "Not sure" falls back to one labelled answer per version. | Options-style questions are preferred; fixed templates suit 7B models ([Lee et al.](https://arxiv.org/abs/2305.13808), [APA](https://arxiv.org/abs/2404.11972)). Merged answers are the failure to avoid. | v0 | Evidence for options and template; the fallback is inference |
| L7 | Simulated user runs in two arms, `knows` and `unsure`, and is audited for leakage | An always-informed user is an upper bound. An LLM simulator leaked the answer unasked in 32 to 41% of cases ([HumanEvalComm](https://arxiv.org/abs/2406.00215)). | v0 | Evidence for the need; the arms are inference |
| L8 | Two new baselines: `two_branch` (answer per version, no question) and `assume_state` (pick the likelier version, say so) | No head-to-head of ask, answer-both and assume-and-state exists for code. | v0 | Inference |
| L9 | Every run records deprecation warnings from the solution as a `soft_fail` flag; validation gains a portable reference | Deprecated-but-working code otherwise scores as cleanly portable ([quantum-api-drift](https://arxiv.org/abs/2607.04072), [VersiBCB](https://arxiv.org/abs/2601.12262)). | v0 | Evidence |
| L10 | No-conflict controls: mixed-version docs for an API that is identical in both versions | Conflict handling degrades conflict-free inputs in three benchmarks ([FaithEval](https://arxiv.org/abs/2410.03727)). Over-asking and over-hedging must be measured. | v0 | Evidence |
| L11 | Chunks lead with the exact signature; each example is checked against its version tag before indexing | The signature drives valid calls ([Jain et al.](https://arxiv.org/abs/2407.09726)). A wrong API name in an example costs Qwen-7B 37% ([Chen et al.](https://arxiv.org/abs/2503.15231)). | v0 | Evidence |
| L12 | Chunk order is counterbalanced by version (v0). Chunk ratio and an end-to-end retrieval arm are flags (v1). | Order and repetition decide which document a 7B model follows ([Xie et al.](https://arxiv.org/abs/2305.13300), [Schuster et al.](https://arxiv.org/abs/2601.03746)). | v0 / v1 | Evidence |
| L13 | Asking is reported as selective prediction: the evidence margin is logged, with risk-coverage, AUROC and cost-penalised utility | The abstention literature's standard ([Wen et al.](https://arxiv.org/abs/2407.18418)); cost-aware rules beat fixed thresholds ([Dong et al.](https://arxiv.org/abs/2601.06407)). | v0 | Evidence |
| L14 | Reports state the minimum detectable effect and add Wilson intervals | 240 instances in 60 clusters detect paired differences of roughly 8 to 16 points ([Miller](https://arxiv.org/abs/2411.00640), our calculation). | v0 | Evidence; the figures are our calculation |
| L15 | Signals are scored per call site; library-authored migration messages become decisive | Error type does not give direction; only strings a single version can emit do ([Huang et al.](https://arxiv.org/abs/2207.10347)). | v0 | Evidence |
| L16 | Portable-first variant: when unsure, try an answer that uses only APIs present in both versions, and ask only if that fails the guard | Asking has no value when the answer does not depend on the version ([Dong et al.](https://arxiv.org/abs/2601.06407)). Gating on a check of the draft follows DAG++ ([Jain et al.](https://arxiv.org/abs/2407.09726)). | v1 | Inference; new in this design |
| L17 | Calibrated evidence combiner: fit per-signal weights on the dev split and compare with the hand weights and a plain cascade | No environment-inference tool calibrates mixed evidence; all use constraint solving or execution. | v1 | Inference |
| L18 | Wider benchmark and stronger repair: behaviour-change concepts, files that mix `pydantic.v1` and V2, a small tier of real questions, prefix-forced repair, an execution self-debug upper bound | Behaviour changes are the hardest class ([RustEvo2](https://arxiv.org/abs/2503.16922)). Forcing the replacement's tokens fixed 85 to 99.6% ([Wang et al.](https://arxiv.org/abs/2406.09834)). | v1 | Evidence for the need |

**Considered and left out:**

- An always-on "watch for conflicting versions" instruction. It helps on real conflicts and degrades conflict-free inputs. It stays only as the `mind_version` baseline.
- Contrastive decoding. It targets context-versus-memory conflict and costs accuracy on non-conflicting inputs.
- Grammar or whitelist constrained decoding. The one Python experiment lowered pass rates.
- More than one repair round. First-round gains dominate, and each round risks breaking correct code.

## Version pairs and environments

Six environments, all on Python 3.11, one per library and side. Python 3.11 is the only interpreter all six support: pandas 3.0 and NumPy 2.4 need 3.11 or later, and pandas 1.5.3 stops at 3.11.

| Library | Old | New | Held constant | Notes |
| --- | --- | --- | --- | --- |
| pandas | 1.5.3 | 3.0.6 | NumPy 1.26.4 in both, no pyarrow | pandas 3.0 accepts NumPy 1.26.0 or later, so only pandas differs. Without pyarrow the 3.0 `str` dtype falls back to object storage. |
| NumPy | 1.26.4 | 2.4.6 | nothing else installed | 2.4 removed `np.trapz` and `np.in1d`, which 2.0 to 2.3 only deprecated. NumPy 2.5.0 is now the newest line; 2.4.6 is the last 2.4 patch. |
| pydantic | 1.10.13 | 2.13.4 | nothing else installed | 2.14 is still in beta. Later 1.10.x releases are believed to ship a `pydantic.v1` shim namespace, which would let one import line work in both. Confirm 1.10.13 lacks it with a canary. |

If pandas 1.5.3 emits its own warnings under NumPy 1.26.4, pin NumPy 1.24.4 in the pandas-old environment only and record it in `docs/DECISIONS.md`.

The model predates pandas 3.0 and NumPy 2.4. Most new-side APIs (`DataFrame.map`, `np.trapezoid`) were added earlier and should be known to it, but the removals are not. The `no_retrieval` baseline measures this. To stay inside the model's training window instead, set pandas 2.2.3 and NumPy 2.0.2 as the new side in `configs/libraries.yaml` and expect more `deprecation` concepts and fewer `removal` ones.

Environment rules:

- Use `uv` for virtual environments and locks. Each lives at `envs/{library}_{side}/` with `requirements.in` and a hash-pinned `requirements.lock`.
- Each library environment holds only the library, its dependencies and pytest. No project code is installed there.
- Anything that runs inside a library environment is a single stdlib-only script, started as a subprocess with that environment's interpreter. It prints JSON to stdout.
- The orchestrator has its own environment (`pyproject.toml`, Python 3.11 or later) and never imports pandas, NumPy or pydantic for benchmark purposes.
- Version pairs live in `configs/libraries.yaml`. Nothing in the code hardcodes a version string.

```yaml
# configs/libraries.yaml
python: "3.11"
libraries:
  pandas:
    old: {version: "1.5.3", extra_pins: ["numpy==1.26.4"]}
    new: {version: "3.0.6", extra_pins: ["numpy==1.26.4"]}
  numpy:
    old: {version: "1.26.4"}
    new: {version: "2.4.*"}      # resolved to an exact patch in the lock
  pydantic:
    old: {version: "1.10.13"}
    new: {version: "2.13.4"}
```

## Version verification

Every artifact is tied to an environment whose version was checked by execution, and every result records the version that actually ran. Seven checks, from the environment outward:

| # | Check | What it proves | When it runs | On failure |
| --- | --- | --- | --- | --- |
| 1 | Lock file with hashes (`uv pip compile --generate-hashes`), its sha256 stored | The environment is reproducible byte for byte | `varag env build` | Build aborts |
| 2 | Manifest probe: `envs/manifest.json` holds, per environment, the interpreter path and version, platform, `lib.__version__`, `importlib.metadata` version of every installed distribution, and the lock sha256. `varag env verify` re-probes and diffs. | The installed versions are the pinned ones and nothing extra is present | Before every extract, validate and run command | Command refuses to start |
| 3 | Canary probes: 5 to 10 symbols per environment in `configs/canaries.yaml`, each marked `present` or `absent` | The code behaves like the labelled version, even if metadata is wrong | With check 2 | Command refuses to start |
| 4 | Runtime stamp: the harness injects a `conftest.py` that asserts the library version equals `VARAG_EXPECT_VERSION` and writes it into the result | Each individual test run used the intended version | Every execution | Result is `infra_error`, never `fail` |
| 5 | Provenance block on every inventory file, corpus chunk and validation record: `library`, `version`, `lock_sha256`, `source`, `content_sha256`, `created_at` | A derived file came from a specific verified environment | On write; checked on read | Stale artifact rejected; regenerate |
| 6 | Upstream doc pinning: migration guides and pydantic markdown docs are fetched at a release tag; the tag, commit SHA, path and file sha256 are stored | Non-docstring text belongs to the version it is tagged with | Corpus build | Chunk dropped and logged |
| 7 | Benchmark manifest: `data/tasks/MANIFEST.json` lists the sha256 of every concept file and its `validation.json`. Each run stores the manifest hash, git commit and config hash. | A result can be traced to exact tasks, code and settings | Run start | Run refuses unvalidated or changed concepts |

Canary examples (the starting set; extend per library):

```yaml
# configs/canaries.yaml
pandas:
  old: {present: [pandas.DataFrame.append, pandas.DataFrame.applymap], absent: [pandas.DataFrame.map]}
  new: {present: [pandas.DataFrame.map], absent: [pandas.DataFrame.append, pandas.DataFrame.applymap]}
numpy:
  old: {present: [numpy.trapz, numpy.in1d], absent: [numpy.trapezoid]}
  new: {present: [numpy.trapezoid], absent: [numpy.trapz, numpy.in1d]}
pydantic:
  old: {present: [pydantic.validator], absent: [pydantic.field_validator, pydantic.v1]}
  new: {present: [pydantic.field_validator, pydantic.ConfigDict], absent: []}
```

Docstring chunks need no separate check: they are read from the installed package inside a verified environment, so their version tag is true by construction.

If a canary disagrees with this document, the environment is right and the document is wrong. Fix the canary file, and note it in `docs/DECISIONS.md`.

## API inventory and diff

The inventory diff is the single source of truth for which symbols belong to which version. Version inference, the blend guard and task mining all read it.

**Extraction.** `scripts/inventory_extract.py` (stdlib only) runs inside each environment and walks the roots listed per library:

- pandas: top-level `pandas`, `DataFrame`, `Series`, `Index`, `DatetimeIndex`, the `.str` / `.dt` / `.cat` accessor classes, `DataFrameGroupBy`, `SeriesGroupBy`, `Rolling`, `Resampler`, `Styler`, `pandas.api.types`.
- NumPy: top-level `numpy`, `ndarray`, `numpy.linalg`, `numpy.random`, `numpy.fft`, `numpy.ma`, `numpy.char`, `numpy.strings`.
- pydantic: top-level `pydantic`, `BaseModel` members, `pydantic.fields`, `pydantic.types`, `Field` keyword arguments, and config keys (v1: attributes of `BaseConfig`; v2: `ConfigDict.__annotations__`).

Public names only (no leading underscore; honour `__all__` where present). Wrap every `getattr` in `try/except` with warnings captured: NumPy 2 raises on expired attributes.

**Known extraction pitfalls** (L2). Each one gets a unit test:

- Key every symbol by its public access path (`pandas.DataFrame.map`), never by `__module__`. pandas 3.0 changed `__module__` to point at public modules, which would show up as spurious moves.
- Import NumPy's lazily loaded submodules (`linalg`, `fft`, `random`, `ma`, `char`, `strings` and the rest) explicitly before walking them. NumPy's `__dir__` hides some reachable members, and its module `__getattr__` raises for expired names.
- `inspect.signature` raises `ValueError` on many C-implemented callables. Record `signature_known: false` for those and for bare `(*args, **kwargs)` signatures. Never treat an unknown signature as unchanged.
- Mark a symbol `deprecated` when any of these holds: it has a `__deprecated__` attribute (verify that pydantic V2 sets it on `dict`, `json`, `parse_obj` and `copy`); its docstring carries a deprecation directive; accessing it emits a deprecation warning; or a published rule set lists it.

**Entry schema.** One JSON line per symbol; keyword parameters get their own entries.

```json
{"symbol": "pandas.DataFrame.append", "library": "pandas", "version": "1.5.3",
 "kind": "method", "owner": "pandas.DataFrame", "name": "append",
 "params": ["other", "ignore_index", "verify_integrity", "sort"],
 "signature": "(self, other, ignore_index=False, verify_integrity=False, sort=False)",
 "deprecated": true, "doc_sha256": "..."}
{"symbol": "pandas.read_csv(squeeze)", "kind": "param", "owner": "pandas.read_csv", "name": "squeeze", "...": "..."}
```

`kind` is one of `module`, `function`, `class`, `method`, `attribute`, `param`, `config_key`. `deprecated` is true when the docstring carries a deprecation directive.

**Diff.** `data/inventories/{library}/diff.json` holds:

- `old_only` and `new_only`: symbols and parameters present on one side.
- `deprecated_in_new`: present on both sides, deprecated on the new side only (pydantic's `.dict()`, `.json()`, `.parse_obj()`, `@validator`). These run in both environments but mark old-style code.
- `shared_changed`: same symbol, different parameters or defaults.
- `shared_unknown`: same symbol, signature not introspectable on at least one side. The guard and the signal extractor abstain on these.
- `shared_same`: everything else. This bucket is also the allowlist for portable answers.
- `method_name_index`: bare method name to the owners that define it on each side, with `generic: true` for names that are also common builtin or container methods (`append`, `map`, `copy`, `update`, `round`, `replace`, `items`, `get`, `join`, `index`, `count`, `sort`, `view`, `first`, `last`, `dict`, `json`). The stoplist lives in config.

**Audit** (L2). `varag inventory audit` checks the diff against rule sets that the library authors or their tooling publish, stored under `data/rules/` with their source commit:

- NumPy: the name table in ruff's `NPY201` rule and `numpy/_expired_attrs_2_0.py`. Every name they list as removed must land in `old_only`. The rule's backwards-compatible flag marks replacements that exist in both versions.
- pydantic: `pydantic/_migration.py` (removed and moved names) and the `bump-pydantic` rules BP001 to BP010.
- pandas: no machine-readable set exists. Mine the 2.0, 2.x and 3.0 release notes; the 3.0 notes alone do not cover removals made in 2.0.

Any listed name missing from the expected bucket is an extraction bug. The audit prints recall per library, and M2 does not pass below 95%.

The same rule sets give the old-to-new mapping (`np.trapz` to `np.trapezoid`) that the blend guard's repair message needs.

**Limit.** The inventory cannot see a behaviour change behind an unchanged signature. Concepts that rely on one are tagged `exclusivity: behavior`, capped at 15% of concepts, kept out of the seed set, and reported separately because the detector is blind to them.

## Documentation corpus and retrieval

The corpus is one chunk per API symbol per version, plus migration-guide sections, and the gold chunks for both versions are always injected so the conflict never depends on retrieval luck.

**Chunk schema** (`data/corpus/{library}/{version}.jsonl`):

```json
{"chunk_id": "pandas-1.5.3-DataFrame.applymap", "library": "pandas", "version": "1.5.3",
 "kind": "api", "symbols": ["pandas.DataFrame.applymap"], "title": "DataFrame.applymap",
 "text": "...", "n_tokens": 212,
 "source": {"type": "docstring", "ref": "pandas.DataFrame.applymap", "sha256": "..."},
 "provenance": {"lock_sha256": "...", "created_at": "..."}}
```

**Sources by library:**

- pandas and NumPy: the installed docstring. Keep the signature, summary, parameters and first example; cap at 350 tokens.
- pydantic: v1 docstrings are thin, so use sections of the upstream docs markdown at the release tag, split by heading. Map sections to symbols by hand for seed concepts and by backticked names for the rest.
- Migration chunks (`kind: migration`, with `from_version` and `to_version`): the pandas 2.0 and 3.0 release notes, the NumPy 2.0 migration guide and 2.4 release notes, and the pydantic migration guide, each fetched at a pinned tag.

**Chunk composition** (L11). Every API chunk has the same five parts in this order: fully qualified name, version tag, the exact signature for that version (from the inventory, not the docstring), a one-line description, and one short example.

- The signature comes first because it is the part that drives valid calls.
- Before indexing, run each example through the signal extractor against the chunk's own version tag. If the example uses a symbol or keyword exclusive to the other version, drop the example and log it. A wrong API name inside example code is the most damaging kind of noise for this model.
- Keep chunks between 200 and 350 tokens.

**Retrieval in v0:**

- Gold injection: each concept lists `gold.old` and `gold.new` symbols. Their chunks are always present in mixed-version conditions.
- Distractors: `k_distract` BM25 hits per version from the rest of the corpus (default 2), identical across methods for the same instance. With one gold chunk per side this gives six chunks before filtering and three after.
- Order (L12): counterbalanced, not just shuffled. The target version's gold chunk comes first in exactly half of each concept's instances, and the assignment is seeded and identical for every method. Reports include an order-sensitivity row.
- Header on every chunk: `[{library} {version} | {kind}] {title}`. Controlled by `show_version_tags` (default true). Expect the tag alone to do little; the filter is what acts on it.
- Migration chunks are off by default (`include_migration: false`). They describe both APIs side by side and largely settle the conflict, so they are an ablation. When they are on, pass short distilled rules ("`np.trapz` was removed in 2.4; use `np.trapezoid`"), never raw release notes.
- `strip_deprecation_notes` (default false) removes deprecation directives from chunk text.
- v1 flags (L12): `chunk_ratio` (`1:1`, `2:1`, `1:2` old to new, to test whether repetition overrides the user's context) and `retrieval: end_to_end` (no gold injection, reported as a separate arm). BM25 is weak on natural-language queries over library docs, so the end-to-end arm also needs a dense retriever.

**Doc conflict test** (used by the policy): a retrieved set conflicts when it holds chunks from both versions and at least one chunk's symbols fall in `old_only`, `new_only` or `shared_changed`. Otherwise the set is deduplicated to one chunk per symbol and treated as conflict-free.

## Benchmark

A concept is one programming need with two version-exclusive reference solutions; an instance is a concept run for one target version under one clue condition.

|  | Concepts | Ambiguous instances (2 targets x clue / no clue) | Version-stated controls (2 targets) | No-conflict controls |
| --- | --- | --- | --- | --- |
| v0 seed | 15 (5 per library) | 60 | 12 (from 6 concepts) | 6 (2 per library) |
| Full | 60 (20 per library) | 240 | 30 (from 15 concepts) | 15 (5 per library) |

**Layout of one concept:**

```
data/tasks/pydantic/pyd-003/
  concept.yaml
  ref_old.py            # reference for the old side
  ref_new.py            # reference for the new side
  ref_portable.py       # only when portable_alternative is not "none"
  test_solution.py      # shared, behaviour-only; imports only `solution` and the library
  clues/                # old_pin.txt, old_code.txt, old_error.txt, new_pin.txt, ...
  validation.json       # generated by `varag bench validate`
```

```yaml
# concept.yaml
id: pyd-003
library: pydantic
split: test                      # dev | test
query: >
  Write `make_sku(code: str)` returning a model instance with a `code` field.
  Reject any code that does not match ^[A-Z]{3}-\d{4}$ using a constraint on
  the field itself, not a custom validator.
entry_point: make_sku
exclusivity: removal             # removal | deprecation | behavior
change_type: param_rename        # symbol_rename | symbol_removed | moved_import |
                                 # param_rename | param_removed | default_change | behavior
warnings_as_errors: false        # true only when exclusivity is deprecation
portable_alternative: plain      # none | guard_only | plain
gold:
  old: ["pydantic.Field(regex)"]
  new: ["pydantic.Field(pattern)"]
clues:
  old:
    - {type: pin,   file: clues/old_pin.txt,   overlap: off_target}
    - {type: code,  file: clues/old_code.txt,  overlap: off_target}
    - {type: error, file: clues/old_error.txt, overlap: on_target}
  new:
    - {type: pin,   file: clues/new_pin.txt,   overlap: off_target}
    - {type: code,  file: clues/new_code.txt,  overlap: off_target}
    - {type: error, file: clues/new_error.txt, overlap: on_target}
control_eligible: true
```

**Instances.** Instance ids look like `pyd-003/new/clue-error`. In the clue condition the clue type rotates over pin, code and error so the three are balanced within a library. Control instances add one sentence naming the version to the query and carry no context.

**No-conflict controls** (L10). A no-conflict control is a task whose API is in `shared_same`. The model still receives chunks tagged with both versions, and one reference must pass in both environments. The right behaviour is to answer once, without a question and without a per-version split. These instances measure over-asking and over-hedging, which most clarification papers never test. They live under `data/tasks/{library}/ctl-*/` with `kind: no_conflict`.

**Exclusivity types:**

- `removal`: the old API raises in the new version, and the new API does not exist in the old one. Preferred.
- `deprecation`: the old API still runs in the new version but warns. The harness turns warnings attributed to the solution into errors for these concepts only.
- `behavior`: same call, different result. Not in the seed set.

**Change types** (L3, L18). `change_type` records what changed, separately from how the concept is exclusive. At least 40% of concepts must be parameter-level (`param_rename`, `param_removed`, `default_change`), because that is where version confusion concentrates and where a name-only guard is blind. Results are sliced by change type.

**Clue rules:**

- Pin: requirement lines where exactly one side satisfies the specifier (`pandas>=1.3,<2`), among a few unrelated packages.
- Code: 5 to 15 lines of the user's existing code that use at least one symbol exclusive to the target version.
- Error: a failing snippet plus its real traceback, produced by `varag bench make-error-clue`, which runs other-version code in the target environment and captures stderr.
- Prefer `off_target` clues, which reveal the version through a symbol the solution does not need. `on_target` clues give part of the answer away; tag them so results can be split.
- No ambiguous query or clue may name a version number in prose. A regex lint enforces it.

Real contexts are less helpful than pins suggest: most published notebooks declare no dependencies, and most declared dependencies are ranges. Report every result by clue type, and do not let pin clues carry the headline number.

**Validation.** `varag bench validate` must pass all of these before a concept enters the manifest:

1. `ref_old` passes the tests in the old environment and `ref_new` passes in the new one.
2. `ref_old` fails in the new environment and `ref_new` fails in the old one, by test failure or exception, not by timeout or infrastructure error. This proves the tests exercise the version-sensitive behaviour.
3. All four runs repeat three times with identical results.
4. Statically, `ref_old` uses at least one `old_only` or `deprecated_in_new` symbol or keyword and no `new_only` one, and the reverse for `ref_new` (skipped for `behavior`).
5. If `portable_alternative` is not `none`, `ref_portable` passes in both environments with no deprecation warning. This proves the tests judge behaviour and do not reject a legitimate answer for using a different API.
6. Each clue alone makes the signal extractor point at its intended version, and each error clue's traceback reproduces.
7. The gold chunks exist in the corpus for both versions.
8. The query names the entry point and passes the version-number lint.
9. Deprecation warnings raised from the reference solutions are recorded per environment, so a `soft_fail` in a model's answer can be compared with what the reference does.

**Candidate pairs to start from.** These are hypotheses; the validation matrix decides.

| Library | Old side | New side | Expected type |
| --- | --- | --- | --- |
| pandas | `DataFrame.applymap` | `DataFrame.map` | removal |
| pandas | `resample("M")`, `date_range(freq="M")` | `"ME"` alias | removal |
| pandas | `read_csv(date_parser=...)` | `read_csv(date_format=...)` | removal, verify |
| NumPy | `np.trapz` | `np.trapezoid` | removal |
| NumPy | `np.reshape(a, newshape=...)` | `np.reshape(a, shape=...)` | removal, verify |
| pydantic | `Field(regex=...)` | `Field(pattern=...)` | removal |
| pydantic | `__root__` model | `RootModel` | removal |
| pydantic | `orm_mode` with `from_orm` | `from_attributes` with `model_validate` | removal |
| pydantic | `GenericModel` | `BaseModel` with `Generic[T]` | removal |
| pydantic | `@validator`, `.dict()` | `@field_validator`, `.model_dump()` | deprecation |

`DataFrame.append` and `np.in1d` are removed on the new side, but their replacements (`pd.concat`, `np.isin`) run in both versions. Use them in clues, not as concepts. `varag bench candidates` lists further `old_only` and `new_only` pairs from the diff, and GitChameleon 2.0 and VersiCode are idea sources as the proposal says.

## Conflict resolution

Conflicting documents are never resolved by recency: the user's context decides the version, and when it cannot, the system asks. All of this is rule-based and deterministic in v0; the model only writes code.

&#91;embedded content: VA-RAG decision flow · 2 decisions, 1 question at most\]

A version reaches generation by one of two routes: inference from the user's context, or a single question. Documents with no real conflict skip both, and every answer passes the blend check once. One branch is not drawn: when the user answers "not sure", the system generates once per version and returns both answers, each labelled (L6).

**The four conflicts and who wins:**

| Conflict | Example | Resolution |
| --- | --- | --- |
| Document vs document | Chunks for `DataFrame.applymap` (1.5.3) and `DataFrame.map` (3.0.6) are both retrieved | Keep only the inferred version's chunks. No inference: ask. |
| Context vs document | The user's code uses `Field(regex=...)`; v2 chunks are retrieved too | Context wins. Other-version chunks are dropped before generation. |
| Context vs context | Requirements pin `pandas<2`, but the pasted code calls `DataFrame.map` | Ask, and name the contradiction in the question. |
| Output vs committed version | The generated code calls an API from the other version | Blend guard: one regeneration that names the offending calls. |

**Signals.** `pipeline/signals.py` extracts these from the query and context. Each signal carries its source span, the symbol, the side it supports and a weight.

| Signal | Detection | Supports | Weight |
| --- | --- | --- | --- |
| Version named in text ("pandas 1.5", "pydantic v2") | Regex on query and context | The named side | decisive |
| Requirement pin | Parse requirement, pyproject, conda and `pip freeze` lines with `packaging`; exactly one side satisfies the specifier | That side | decisive |
| Library-authored migration message that only one version can emit ("was removed in the NumPy 2.0 release", `PydanticImportError`, `PydanticDeprecatedSince20`, `errors.pydantic.dev/2.`, "frame.append method is deprecated") (L15) | Pattern list per library in config. Each pattern is admitted only after it is reproduced in exactly one environment. | The side that emits it | decisive |
| Error names a missing symbol or parameter (`has no attribute 'append'`, `unexpected keyword argument 'squeeze'`, `cannot import name 'field_validator'`) | Regex over tracebacks, then inventory lookup. Direction comes from the inventory, never from the exception type. | The side that lacks it | 4 |
| Exclusive import (`from pydantic import field_validator`) | AST | The side that has it | 4 |
| Exclusive symbol on a resolved receiver (`np.trapz(...)`) | AST with import-alias resolution | The side that has it | 3 |
| Exclusive keyword passed by name to a resolved callable (`pd.read_csv(squeeze=True)`) (L15) | AST, bound against both versions' signatures | The side that accepts it | 3 |
| Exclusive, non-generic method on an unresolved receiver (`.iteritems()`, `.model_dump()`) | AST with `method_name_index` | The side that has it | 1.5 |
| Deprecated-in-new usage on a resolved receiver (`.dict()` on a `BaseModel` subclass) (L2) | AST with the `deprecated_in_new` bucket | The old side, weakly: the code still runs on the new side | 1 |
| Generic method name on an unresolved receiver (`.append(...)`, `.map(...)`), or a callable in `shared_unknown` | Stoplist and inventory | Neither | 0 |

Extraction rules:

- A symbol named in an error is removed from the code signals. The code is what failed, so it says nothing about what is installed.
- Score the call site, not the symbol (L15). A renamed or removed parameter is evidence only when the call passes it by keyword. A call that never passes it supports neither side.
- Each distinct symbol or keyword counts once, however often it appears.
- A pin that both sides satisfy (`pandas>=1.3`) is not a signal.
- Usage inside a version guard counts for neither side.
- Receiver resolution: follow import aliases; track variables assigned from library constructors and readers (`pd.DataFrame(...)`, `pd.read_csv(...)`) and classes that subclass `BaseModel`. Name heuristics such as `df` count at weight 1.5.
- Parsing order: fenced code blocks, then `ast.parse`, then dedent and retry, then line-by-line salvage. A regex fallback counts at half weight.

**Decision rule** (`pipeline/infer.py`):

```python
# S[v] = sum of non-decisive weights for side v; D[v] = True if a decisive signal supports v
strong = lambda v: D[v] or S[v] >= TAU_COMMIT      # default 3.0
weak   = lambda v: not D[v] and S[v] <= TAU_NOISE  # default 1.5

if   strong(old) and weak(new): decision = INFER(old)
elif strong(new) and weak(old): decision = INFER(new)
elif not weak(old) and not weak(new): decision = CONTEXT_CONFLICT
else: decision = UNCERTAIN

margin = S[old] - S[new]    # logged for every instance, with D[old] and D[new]
```

Thresholds live in `configs/experiment.yaml`, are tuned on dev concepts only, and are frozen before any test run.

**Asking as a cost decision** (L13). The two thresholds are one operating point, and the weights are hand-set priors. Because every trace logs the margin, `varag report` can sweep a single threshold on its absolute value after the fact and draw the whole trade-off between wrong-version commits and questions asked. The frozen thresholds are the point reported as VA-RAG; the curve shows whether the conclusion depends on them. Fitting the weights from dev data is L17 (v1).

**Policy** (`pipeline/policy.py`):

```python
signals  = extract_signals(query, context)
decision = infer(signals)                            # INFER(v) | UNCERTAIN | CONTEXT_CONFLICT
docs     = retrieve(query, context)                  # gold chunks from both versions + distractors

if decision.kind == INFER:
    versions, by = [decision.version], "inferred"
elif not doc_conflict(docs):
    versions, by = [], "no_conflict"                 # nothing to resolve: answer once
else:
    reply = simulated_user(make_question(library, decision))
    v = parse_version(reply)                         # None for "not sure" or an unusable reply
    versions, by = ([v], "asked") if v else ([old, new], "both")

if not versions:                                     # no conflict
    code = generate(query, context, dedupe(docs), UNRESOLVED)
    return [(None, blend_guard(code, UNRESOLVED))]

answers = []
for v in versions:                                   # one pass, or two for "both"
    state = COMMITTED(v, by)                         # prompt states the version
    code  = generate(query, context, keep_version(docs, v), state,
                     avoid=unavailable_symbols(signals, v))
    answers.append((v, blend_guard(code, state)))    # at most one regeneration each
return answers                                       # two answers are returned under version labels
```

Notes on the policy:

- When committed, the generation prompt says: "The user is on {library} {version}. Use only APIs available in that version."
- Negative constraints (L5). `unavailable_symbols` returns every symbol or keyword from the user's context that does not exist in the committed version: the one an error names, and any other-version call in pasted code. The prompt adds, for each: "`{symbol}` is not available in {library} {version}." When the rule sets give a replacement, it adds "Use `{replacement}`." The user's failing code otherwise pulls the model back to the API that failed.
- Question for `UNCERTAIN` (L6): "Which version of {library} are you on: {old\_major}.x or {new\_major}.x? The answer differs between them. You can check with `python -c "import {module}; print({module}.__version__)"`. If you are not sure, say so and I will give both."
- Question for `CONTEXT_CONFLICT`: "Your requirements say {pin}, but your code uses {symbol}, which only exists in {library} {other\_major}.x. Which is installed: {old\_major}.x or {new\_major}.x?"
- The "both" fallback makes two separate generation calls, each on documents filtered to one version, and returns the two answers under the labels `# --- for {library} {old} ---` and `# --- for {library} {new} ---`. It never asks one call to write both: mixed documents in one prompt are what produce merged answers.
- Simulated user (L7). It is rule-based, so it cannot leak the solution. It has two arms, set by `user_arm`: `knows` replies "I'm on {library} {v\*}." and `unsure` replies "I'm not sure." Either arm answers only if the question mentions the library name or the word "version". Otherwise it replies "I'm not sure what you're asking." and the run logs `question_relevant: false`.
- Report both arms. `knows` is an upper bound on what asking can deliver, and `unsure` is the floor. No study measures how often real developers can state their installed version.
- Leak audit, run once per model: replace every question with an irrelevant one and confirm the pass rate does not rise above the no-question rate.
- One question per instance at most.
- Every instance writes a trace record to `runs/{run_id}/traces.jsonl`: signals with spans and weights, both scores, the margin, the decision, chunks kept and dropped, the question and answer, and guard activity. The failure taxonomy is built from these.

## Blend guard

The guard is a static check on the generated code that runs before execution and allows exactly one regeneration.

**Detection** (L3). Run the signal extractor on the output to get `U_old` and `U_new`: the exclusive usages found outside any version guard. A usage is one of:

- A symbol in `old_only` or `new_only`, on a resolved receiver or with a non-generic name.
- A keyword argument passed by name to a resolved callable, where one version's signature accepts that keyword and the other's does not. This is the check revision 1 lacked, and it is where most version confusion sits.
- A `deprecated_in_new` symbol on a resolved receiver. It counts toward `U_old` as a soft usage: a violation when committed to the new version, never when committed to the old one.

The guard abstains, and logs `guard_abstain`, on unresolved receivers with generic names, on callables in `shared_unknown`, and on calls that forward `**kwargs`. A false flag triggers a regeneration that can break correct code, so precision matters more than recall here.

| State | Violation |
| --- | --- |
| Committed to version v | Any usage exclusive to the other version, including soft usages when v is the new side |
| No conflict, or unresolved | `U_old` and `U_new` both non-empty, soft usages excluded |

**Regeneration** (L4). On a violation, start a fresh conversation. Do not append to the first one: a long repair transcript keeps the bad code in view. The new prompt holds the original query and context, the version statement, and one repair block per offending call:

```
Your previous answer used `df.applymap` (line 4), which does not exist in pandas 3.0.6.
Use `DataFrame.map` instead:
  DataFrame.map(func, na_action=None, **kwargs)
  Example: df.map(lambda x: x * 2)
Previous answer:
<the code>
Rewrite it using only pandas 3.0.6 APIs.
```

The replacement comes from the audited rule sets or the concept's `gold` mapping. Its signature and example come from the committed version's chunk. When no replacement is known, the block names the offending call and attaches the two most similar committed-version chunks.

- Acceptance check: keep the regenerated code only if it parses, has strictly fewer violations than the first answer, and introduces no new one. Otherwise return the first answer and log `guard_rejected`.
- No second retry. If the accepted output still violates, return it and log `guard_unresolved`.
- The guard never sees tests or execution results.
- Execute both the pre-guard and post-guard code. The difference gives the guard's fix rate and harm rate at no extra model cost.

**How blending is measured** (for every method, guarded or not):

- `blend_static`: `U_old` and `U_new` both non-empty outside version guards.
- `blend_exec`: `blend_static`, and the code fails in both environments, and at least one failure is an `AttributeError`, `ImportError`, unexpected-keyword `TypeError` or library error that names an exclusive symbol. This is the execution-verified blend rate the proposal asks for.
- `guarded_portable`: both sides used inside version guards, and the code passes both environments. Reported, not counted as a blend.

**Detector audit.** `varag audit sample` exports 50 outputs with the detector's verdict for hand labelling, giving precision and recall as the proposal's feasibility section requires.

**Guard accuracy against execution** (L3). The two-environment run is an oracle for the guard. For every output, compare "guard flagged a violation" with "the code failed in the committed version with an error that names an exclusive symbol or keyword". Report precision and recall overall and by change type. No published work reports these for a version guard on natural model output, so this table is a result in its own right. Expect recall well below 100%: static methods have a ceiling, and behaviour changes are invisible to them.

## Interaction protocol, baselines and ablations

Every method speaks the same protocol, so pass rates and ask rates are comparable across them.

**Protocol:**

- One system prompt for all methods. The model must reply with either a single fenced Python block that defines the entry point, or a single line starting `QUESTION:` when it needs information from the user.
- Methods that answer for both versions return exactly two fenced blocks. Each block starts with the comment `# --- for {library} {version} ---`.
- At most one question per instance. After the simulated user's reply the model must produce code.
- Code extraction: the last fenced Python block; if none, the whole message when it parses as Python; otherwise the result is `no_code`. Labelled two-block answers are split by label. A response with several unlabelled blocks is scored on the last one and counted in `multi_block_rate`, because which block is picked can flip the outcome.
- Generation settings: temperature 0, top\_p 1.0, repetition penalty 1.0, max 1024 new tokens, fixed seed, one sample. Every one of these is sent explicitly in each request (L1).

**Methods:**

| Id | Documents given | Prompt addition | Who decides to ask | Guard |
| --- | --- | --- | --- | --- |
| `no_retrieval` | None | None | Model | No |
| `plain_rag` | Mixed, both versions | None | Model | No |
| `mind_version` | Mixed, both versions | "The documents may describe different versions. Work out the user's version from their context. If you cannot, ask." | Model | No |
| `assume_state` (L8) | Mixed, both versions | "If the version is unclear, pick the one the user's context suggests, say which you assumed in a comment, and add one line on what changes for the other." | Never asks | No |
| `two_branch` (L8) | Two calls, each with one version's documents | Version stated in each call | Never asks; always returns both labelled answers when documents conflict | No |
| `always_ask` | Mixed, then filtered by the answer | Version stated after the answer | Forced, templated question | No |
| `oracle_docs` | Target version only | None | Model | No |
| `va_rag` | Set by the policy | Version stated when committed | Policy | Yes |

`two_branch` is the strongest question-free baseline: it cannot commit to the wrong version. It pays with twice the tokens and by leaving the choice to the user, so it is always reported with its cost. `oracle_docs` separates inference error from generation error: the gap between it and `va_rag` is what better inference could still win.

Expect `mind_version` to move little and `always_ask` with the `knows` user to sit near `oracle_docs`. Both predictions come from the literature and are worth confirming.

**Ablations of VA-RAG:**

- `va_rag_no_infer`: the decision is always `UNCERTAIN`, so every doc conflict leads to a question.
- `va_rag_no_ask`: `UNCERTAIN` and `CONTEXT_CONFLICT` generate on the mixed documents without asking.
- `va_rag_no_guard`: the blend guard is skipped.

**v1 variants** (build after the base works):

- `va_rag_portable_first` (L16). When the decision is `UNCERTAIN` or `CONTEXT_CONFLICT`, first generate from chunks restricted to `shared_same` symbols, with the instruction "Use only APIs that exist in both {library} {old} and {new}." If the guard finds no exclusive or deprecated usage in that draft, return it without a question. Otherwise ask as usual. The idea: a question is only worth its cost when no version-independent answer exists. Success shows up as fewer questions at the same pass rate, with more `portable` outcomes.
- `va_rag_fitted` (L17). Replace the hand weights with per-signal weights fitted by logistic regression on dev-split clue instances, and compare against the hand weights and a plain cascade (pin, then migration message, then majority of exclusive hits). Report calibration.
- `va_rag_prefix_repair` (L18). On a guard violation, truncate the first answer at the offending call, force the replacement symbol's tokens, and let the model continue. This needs raw completion access to the local model.
- `self_debug_oracle` (L18). An upper bound, not a deployable method: one round of repair with the real traceback from the target environment.

Corpus flags (`show_version_tags`, `include_migration`, `strip_deprecation_notes`, `k_distract`) apply to any method and are run after the base works.

**Model backends** (`configs/models.yaml`), all behind one OpenAI-compatible chat client:

| Backend | Behaviour | Use |
| --- | --- | --- |
| `mock_ref` | Returns the target-version reference | Harness anchor: 100% pass |
| `mock_wrong` | Returns the other version's reference | Harness anchor: 0% pass |
| `mock_blend` | Returns code using one symbol from each side | Guard and blend-metric tests |
| `mock_ask` | Always asks a version question, then returns the reference | Ask-path tests |
| `vllm_qwen7b` | `Qwen/Qwen2.5-Coder-7B-Instruct` served by vLLM | Primary model |
| `vllm_large` | One larger code model, to be chosen | Second model |

Every request and response is cached on disk under a key of sha256(model, messages, parameters), and logged. A cache hit must be byte-identical to the original response.

**Serving configuration** (L1). Do this before the first real run; it changes every number.

- Start vLLM with `--generation-config vllm`. The default, `auto`, loads the model repository's generation config, which for Qwen2.5-Coder-7B-Instruct sets sampling on, temperature 0.7, top\_p 0.8, top\_k 20 and repetition penalty 1.1. A request that sets only the temperature may still inherit the penalty, which punishes code for repeating identifiers.
- Log once per run: vLLM version, model revision hash, GPU model, concurrency, seed, and the fully rendered prompt of the first instance after chat templating. Check in that rendering that the system prompt is ours and not the model's default.
- Use a fixed concurrency for reported runs. vLLM does not guarantee identical outputs across batch sizes or hardware.
- Serving-noise check: run a fixed 20-instance subset twice. If any output differs, report the rate and treat differences of that size between methods as noise.
- One-off test of L1 itself: run `plain_rag` on the dev split with and without the model's default config, and record the difference in `docs/DECISIONS.md`.

## Execution harness, outcomes and metrics

Every answer is executed in both environments of its library, and the pair of results gives one of four outcomes.

**Harness** (`eval/execute.py`), per instance, method and code version:

1. Create a temp directory with `solution.py`, the concept's test file and the injected `conftest.py`.
2. Run `{env_python} -m pytest -q -x -p no:cacheprovider` in the old and the new environment.
3. Limits: 60 s timeout, 2 GB address space, temp directory as cwd, a stripped environment, and no network where the OS allows it (`unshare -n` on Linux).
4. For `warnings_as_errors` concepts add `-W error::DeprecationWarning:solution -W error::FutureWarning:solution`, which targets warnings attributed to the solution module. Verify on a known deprecated call that the filter fires.
5. Record status (`pass`, `fail`, `error`, `timeout`, `infra_error`), exception type, last traceback line, the runtime version stamp and duration.

Generated code is untrusted. It never runs in the orchestrator process.

**Outcome per instance:**

| Passes target version | Passes other version | Outcome |
| --- | --- | --- |
| Yes | No | `target_only` |
| Yes | Yes | `portable` |
| No | Yes | `wrong_version` |
| No | No | `broken` |

Three additions to the outcome record (L9, L10):

- `soft_fail`. Every run, not only `warnings_as_errors` concepts, records the `DeprecationWarning` and `FutureWarning` count attributed to the solution module. An answer that passes while warning is flagged `soft_fail`. Without this, pydantic V1-style code that still runs on V2 scores as cleanly portable.
- Two-answer responses. The block labelled with the target version is the scored answer and gets an outcome like any other. The record also stores `answers_returned: 2` and `both_correct` (the old block passes in the old environment and the new block passes in the new one).
- No-conflict controls have no target. Their outcome is `pass_both`, `pass_one` or `broken`.

**Metrics:**

| Metric | Definition |
| --- | --- |
| Intended-version pass rate (primary) | Share of instances that pass in the target version: `target_only` plus `portable` |
| Wrong-version, portable and broken rates | Share of instances with each outcome |
| Soft-fail rate (L9) | Share of passing answers that raise a deprecation warning from the solution |
| Blend rate | `blend_static` and `blend_exec`, as defined under Blend guard |
| Ask recall | Share of no-clue ambiguous instances with a relevant question. High is good. |
| Ask precision (L13) | Share of questions asked that fall on no-clue ambiguous instances |
| Over-ask rate | Share of clue, version-stated and no-conflict instances with any question. Low is good. |
| Over-hedge rate (L10) | Share of clue, version-stated and no-conflict instances answered with two versions. Low is good. |
| Risk-coverage and AUROC (L13) | Sweep a threshold on the absolute margin: wrong-version commit rate against the share answered without a question. AUROC of the absolute margin for predicting a correct commit. |
| Cost-penalised utility (L13) | Intended-version pass rate minus c times the share of instances with a question or a two-answer response, at c = 0, 0.1 and 0.3 |
| Silent-commit direction | Among no-clue instances answered without a question: share using only old-side, only new-side, both, or neither exclusive symbols |
| Clue following | Among clue instances answered without a question: share whose exclusive symbols match the clue's version |
| Inference precision and coverage | For VA-RAG: share of `INFER` decisions that equal the target, and share of clue instances that reach `INFER` |
| Guard precision and recall (L3) | Guard verdict against the execution oracle, as defined under Blend guard |
| Guard fix and harm rates | Share of guard triggers where regeneration turned a fail into a pass, and a pass into a fail |
| Order sensitivity (L12) | Intended-version pass rate when the target version's chunk comes first, minus when it comes last |
| Cost | Model calls, tokens, turns and answers returned per instance |

Slice every metric by library, target (old or new), clue condition and type, exclusivity type, change type and user arm. Report the test split only.

**Statistics** (`eval/stats.py`):

- 95% percentile bootstrap intervals from 10,000 resamples of concepts, with a fixed seed.
- Wilson intervals on concept-level proportions alongside the bootstrap (L14). Below a few hundred items, normal-approximation intervals are too narrow.
- Method comparisons: paired bootstrap on per-concept mean differences, with an exact McNemar test on instance pairs as a cross-check.
- Holm correction across the comparisons of each baseline against VA-RAG.
- Primary contrasts, fixed before any test-split run: `va_rag` against `plain_rag`, `mind_version`, `two_branch` and `always_ask`, on intended-version pass rate and on `blend_exec`.

**What size of difference the benchmark can show** (L14). These are our own calculations from Miller's formula at 80% power, not published figures. The discordant rate is the share of instances on which two methods disagree; rho is the correlation between instances of one concept.

| Benchmark | Discordant rate 0.2, rho 0.25 | Discordant rate 0.2, rho 0.5 | Discordant rate 0.3, rho 0.5 |
| --- | --- | --- | --- |
| Full: 60 concepts, 240 instances | 10.7 points | 12.8 points | 15.7 points |

So the full benchmark supports claims about differences of roughly ten points or more, and nothing under five. The 15-concept seed is a smoke test: report no method comparisons from it. More concepts help; more instances per concept barely do. Estimate rho from the first full run and print the resulting table in `report.md`.

**Outputs** in `runs/{run_id}/`: `results.jsonl` (one row per instance, method and code version), `traces.jsonl`, `report.md`, and `run.json` with the manifest hash, git commit, config hash and environment manifest.

## Repository layout and commands

One Python package, `varag`, with a CLI; data, environments and runs sit beside it.

```
va-rag/
  CLAUDE.md                 # commands, conventions, pointer to docs/HANDOFF.md
  pyproject.toml            # orchestrator package and dev tools
  docs/
    HANDOFF.md              # this document, exported as Markdown
    LITERATURE.md           # the literature review file
    DECISIONS.md            # every deviation from this spec, dated, with the reason
  configs/
    libraries.yaml          # version pairs and inventory roots
    canaries.yaml
    models.yaml             # backends and the pinned serving configuration
    experiment.yaml         # methods, thresholds, corpus flags, user arm, seeds
  envs/
    pandas_old/ pandas_new/ numpy_old/ numpy_new/ pydantic_old/ pydantic_new/
    manifest.json
  scripts/                  # stdlib-only, run inside library environments
    inventory_extract.py
    probe_env.py
    conftest_template.py    # version stamp and warning capture
  src/varag/
    cli.py
    envs/        build.py  verify.py  runner.py
    inventory/   schema.py  diff.py  audit.py
    corpus/      build.py  migration.py  retrieve.py
    bench/       schema.py  validate.py  clues.py  candidates.py  instances.py
    pipeline/    signals.py  infer.py  policy.py  clarify.py  generate.py  blend.py  repair.py
    methods/     registry.py  baselines.py  va_rag.py
    llm/         client.py  cache.py  mock.py  simulated_user.py
    eval/        execute.py  outcomes.py  metrics.py  stats.py  report.py
  data/
    inventories/{library}/{version}.jsonl, diff.json
    rules/{library}/        # published migration rule sets, with source commit
    corpus/{library}/{version}.jsonl
    tasks/{library}/{concept_id}/...
    tasks/MANIFEST.json
  runs/{run_id}/
  tests/                    # unit tests plus fixtures of context snippets
```

| Command | Does |
| --- | --- |
| `varag env build` | Creates the six environments from locks and writes the manifest |
| `varag env verify` | Re-probes versions and canaries; non-zero exit on any mismatch |
| `varag inventory build` | Extracts inventories in each environment and writes the diffs |
| `varag inventory audit` | Checks the diffs against the published rule sets and prints recall per library |
| `varag corpus build` | Builds version-tagged chunks with provenance and checks each example against its tag |
| `varag bench candidates --library pandas` | Lists `old_only` and `new_only` pairings to mine for concepts |
| `varag bench make-error-clue <concept> --target new` | Runs other-version code in the target environment and saves the traceback as a clue |
| `varag bench validate [concept]` | Runs the validation matrix and updates the manifest |
| `varag serve check --model vllm_qwen7b` | Prints the rendered prompt and effective sampling parameters, then runs the serving-noise check |
| `varag run --methods all --model mock_ref --split dev --user-arm knows` | Generates, executes in both environments, writes results and traces |
| `varag report <run_id>` | Computes metrics, intervals, the risk-coverage curve and the detectable-effect table, and writes `report.md` |
| `varag audit sample <run_id> --n 50` | Exports outputs for hand-labelling the blend detector |
| `varag smoke` | Verify, audit, validate, run all methods on mock backends and the 7B endpoint, report |

## Build order

Build in eight milestones, each ending in a check that must pass before the next starts. The harness comes before the pipeline so every later piece is tested by execution.

1. **M0 Scaffold.** Repo layout, `pyproject.toml`, CLI skeleton, config files, `CLAUDE.md`, `docs/DECISIONS.md`, unit-test runner.
   - Accept: `varag --help` lists every command; the test suite runs.
2. **M1 Environments.** `env build`, `env verify`, probe script, canaries.
   - Accept: verify is green on all six; changing one pin by hand makes verify fail; the manifest is committed.
3. **M2 Inventory, diff and audit.** Extraction script with the pitfall handling, schema, diff with the `deprecated_in_new` and `shared_unknown` buckets, `method_name_index`, rule sets under `data/rules/`, `inventory audit`.
   - Accept: every canary symbol lands in the expected bucket; audit recall is at least 95% for NumPy and pydantic; pydantic's `.dict()` lands in `deprecated_in_new`; each pitfall has a passing unit test.
4. **M3 Harness and first concepts.** Concept schema, two-environment execution, runtime stamp, warning capture, `bench validate`, three hand-written concepts (one per library, at least one parameter-level) and one no-conflict control.
   - Accept: the nine-step validation matrix holds for all three; `mock_ref` scores 100% and `mock_wrong` scores 0% with every instance `wrong_version`; a pydantic V1-style answer run on V2 is flagged `soft_fail`.
5. **M4 Corpus and retrieval.** Chunks in the five-part composition, example check against version tags, pydantic markdown chunks, gold injection, BM25 distractors, counterbalanced order, doc conflict test.
   - Accept: gold chunks exist for both versions of every concept; provenance is complete; no indexed example uses an other-version symbol; the conflict test is true for all three concepts and false for the control.
6. **M5 Signals, inference, policy.** Extractor with call-site scoring, decision rule with the logged margin, closed-choice question templates, simulated user with both arms, negative constraints, the "both" fallback, traces, `make-error-clue`.
   - Accept: unit tests pass on at least 40 fixture snippets covering pins, code, keyword arguments, errors, migration messages, guards and contradictions; every seed clue infers its intended version; the `unsure` arm returns two labelled answers.
7. **M6 Methods and guard.** Model client, cache, mock backends, seven baselines, VA-RAG, three ablations, blend guard with keyword binding, fresh-prompt repair with the acceptance check, `serve check`.
   - Accept: every method completes on mock backends; the guard triggers on `mock_blend` and abstains on a generic `.append()` on a list; a cached rerun makes zero model calls; `serve check` shows repetition penalty 1.0 and our system prompt.
8. **M7 Metrics and first real run.** Outcomes, the full metric table, bootstrap and Wilson intervals, risk-coverage curve, guard precision and recall, detectable-effect table, report; grow to 15 seed concepts and 6 no-conflict controls; run the 7B model on the dev split in both user arms.
   - Accept: `varag smoke` passes end to end; `report.md` shows every metric with intervals; the leak audit and the serving-noise check are recorded.

After M7, in this order:

1. Scale to 60 concepts and 15 no-conflict controls, then freeze thresholds on the dev split. Nothing below is worth comparing on fewer concepts.
2. Run every v0 method on the test split, in both user arms, and build the failure taxonomy from the traces.
3. `va_rag_portable_first` (L16). It reuses the guard and the `shared_same` bucket, so it is the cheapest v1 experiment and the most novel.
4. Corpus flags: `chunk_ratio`, `show_version_tags`, `strip_deprecation_notes`, `include_migration`, then the end-to-end retrieval arm (L12).
5. `va_rag_fitted` (L17), then `va_rag_prefix_repair` and `self_debug_oracle` (L18).
6. The larger model, behaviour-change concepts, files that mix `pydantic.v1` with V2, and a small tier of real Stack Overflow or GitHub questions whose true version is established by reproducing the error in one environment only (L18).

**Working rules for Claude Code:**

- A concept does not exist until `bench validate` passes. Never weaken a test or a reference to make the matrix pass; drop or re-tag the concept instead.
- Version facts in this document marked "verify", and every candidate pair, are hypotheses. The environments are the authority.
- Do not tune thresholds or prompts on test-split concepts.
- Scripts that run inside library environments stay stdlib-only.
- Stop and ask before changing version pins, the output protocol, metric definitions or the outcome classes.
- Record every deviation from this spec in `docs/DECISIONS.md` with the date and the reason.
- Write unit tests alongside each module. The signal extractor and decision rule need the densest coverage.

Do not start any v1 item before `varag smoke` passes. Numbers quoted from the literature in this document are expectations to test, not targets to hit.

## Open questions and risks

Seven decisions are yours; each has a default the build proceeds with until you say otherwise.

- [ ] Version pairs: keep pandas 3.0.6 and NumPy 2.4.6 as the new side, or stay inside the model's training window with pandas 2.2.3 and NumPy 2.0.2? Default: 3.0.6 and 2.4.6. NumPy 2.5.0 exists but adds nothing the benchmark needs.
- [ ] Benchmark shape: 60 concepts run as 240 ambiguous instances, in place of 120 single-target tasks? Default: yes.
- [ ] Benchmark size: 60 concepts can show differences of about ten points. Accept that, or plan for about 100 concepts? Default: 60, with the detectable-effect table in every report.
- [ ] Deprecation-only concepts: allowed with warnings as errors, or removal-only? Default: allowed and tagged.
- [ ] When the user is not sure of their version, return one labelled answer per version, or guess the likelier one and say so? Default: return both.
- [ ] Where vLLM runs, and which larger model is the second one. Default: none set; M0 to M6 need neither.
- [ ] Sandboxing: are a timeout, memory limit and no-network enough, or should execution move into containers? Default: process limits.

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Too few naturally exclusive pairs in NumPy, where most replacements already existed in 1.26 | High | Concepts that combine one old-only and one new-only call; `deprecation` concepts; uneven library quotas (for example 15 / 20 / 25) |
| Portable answers dominate, so ambiguity stops mattering | Medium | Portable rate is reported; `portable_alternative` is tracked; queries constrain the approach where natural; pydantic carries more weight. L16 turns this from a threat into a policy. |
| The benchmark is too small to show effects under about ten points | Certain | Detectable-effect table in every report; primary contrasts fixed in advance; grow concepts before anything else |
| The always-informed simulated user overstates what asking delivers | Certain | Two user arms; leak audit; the `knows` result is labelled an upper bound |
| Guard recall is low on parameter and behaviour changes | High | Keyword binding; at least 40% parameter-level concepts; guard precision and recall reported by change type |
| Blend detector false positives on generic method names | Medium | Stoplist, receiver resolution, version-guard exclusion, abstention, the acceptance check, the 50-sample audit |
| Serving defaults silently change decoding | High until L1 is done | `varag serve check` before every reported run |
| pandas 1.5.3 emits internal warnings on Python 3.11 with NumPy 1.26.4 | Medium | Warning capture scoped to the solution module; fall back to NumPy 1.24.4 in pandas-old |
| The model has not seen pandas 3.0 or NumPy 2.4 | Certain | Measured by `no_retrieval`; alternate pairs are one config change away; report the model's training cutoff |
| Old docstrings carry deprecation notes that hint which side is newer | Certain | `strip_deprecation_notes` ablation |
| On-target clues leak the solution | Medium | Prefer off-target clues; results split by `overlap` |
| Figures quoted from the literature were transcribed by an automated reader | Medium | Check each against its PDF before it goes into the paper |

## Sources

Version facts were checked against these pages on 8 October 2026; everything else follows the attached proposal.

- [pandas: What's new in 3.0.0](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html): released 21 January 2026; requires Python 3.11 or later and NumPy 1.26.0 or later; removes functionality deprecated in 2.x, including the `M`, `Q` and `Y` offset aliases; the string dtype falls back to object storage without pyarrow. The page's version list shows 3.0.6 (17 September 2026) as the latest patch.
- [NumPy 2.4.0 release notes](https://numpy.org/devdocs/release/2.4.0-notes.html): supports Python 3.11 to 3.14; removes `numpy.in1d`, `numpy.trapz` and the `newshape` parameter of `numpy.reshape`.
- [pydantic HISTORY.md](https://github.com/pydantic/pydantic/blob/main/HISTORY.md): 2.13.4 (6 May 2026) is the latest stable release and 2.14 is in beta; the bundled `pydantic.v1` namespace matches 1.10.26.

Not checked against a source, and marked "verify" above: that pydantic 1.10.13 predates the `pydantic.v1` shim in the 1.x line; that pandas 3.0 removed `DataFrame.applymap` and `read_csv(date_parser=...)`; that `numpy.reshape` gained its `shape` keyword before 2.4.

**Checked directly for revision 2:**

- [vLLM serve reference](https://docs.vllm.ai/en/latest/cli/serve/): `--generation-config` defaults to `auto`, which loads the generation config from the model path; `vllm` disables that.
- [Qwen2.5-Coder-7B-Instruct generation config](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/blob/main/generation_config.json): sampling on, temperature 0.7, top\_p 0.8, top\_k 20, repetition penalty 1.1.
- [NumPy release notes](https://numpy.org/doc/stable/release.html): 2.5.0 is the newest release; 2.4.6 is the last 2.4 patch.

**Literature behind L1 to L18.** These were read during the review by an automated reader, not by hand. The review file lists all sources, with caveats on which were read only as abstracts.

- Version-aware code generation: [GitChameleon 2.0](https://arxiv.org/abs/2507.12367), [CodeUpdateArena](https://arxiv.org/abs/2407.06249), [LibEvolutionEval](https://aclanthology.org/2025.naacl-long.348.pdf), [LibEvoBench](https://arxiv.org/abs/2606.25402), [VersiBCB](https://arxiv.org/abs/2601.12262), [quantum-api-drift](https://arxiv.org/abs/2607.04072), [PinTrace](https://arxiv.org/abs/2605.06279), [RustEvo2](https://arxiv.org/abs/2503.16922), [Wang et al., deprecated API usage](https://arxiv.org/abs/2406.09834), [Ashik et al., When LLMs Lag Behind](https://arxiv.org/abs/2604.09515).
- Knowledge conflicts in RAG: [Xie et al.](https://arxiv.org/abs/2305.13300), [HoH](https://aclanthology.org/2025.acl-long.301.pdf), [AmbigDocs](https://arxiv.org/abs/2404.12447), [VersionRAG](https://arxiv.org/abs/2510.08109), [Schuster et al.](https://arxiv.org/abs/2601.03746), [FaithEval](https://arxiv.org/abs/2410.03727).
- Asking and abstaining: [HumanEvalComm](https://arxiv.org/abs/2406.00215), [ClarifyCodeBench](https://arxiv.org/abs/2607.00711), [APA](https://arxiv.org/abs/2404.11972), [Dong et al., value of information](https://arxiv.org/abs/2601.06407), [Wen et al., abstention survey](https://arxiv.org/abs/2407.18418), [Lee et al.](https://arxiv.org/abs/2305.13808).
- API hallucination, guards and repair: [Khati et al.](https://arxiv.org/abs/2601.19106), [Jain et al., CloudAPIBench](https://arxiv.org/abs/2407.09726), [Chen et al., documentation content](https://arxiv.org/abs/2503.15231), [Chen et al., self-debugging harm](https://aclanthology.org/2025.acl-long.881.pdf), [CoCoGen](https://aclanthology.org/2024.findings-acl.138.pdf).
- Version inference and API diffing: [SnifferDog](https://arxiv.org/abs/2103.02959), [PCART](https://arxiv.org/abs/2406.03839), [Huang et al., dependency bugs](https://arxiv.org/abs/2207.10347), [ruff NPY201](https://docs.astral.sh/ruff/rules/numpy2-deprecation/), [pydantic migration guide](https://pydantic.dev/docs/validation/latest/get-started/migration/).
- Evaluation: [Miller, Adding Error Bars to Evals](https://arxiv.org/abs/2411.00640), [Bowyer et al.](https://arxiv.org/abs/2503.01747).
