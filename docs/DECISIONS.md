# Decisions and deviations from docs/HANDOFF.md

One dated entry per deviation or judgement call, newest last.

## 2026-10-08 Toolchain: uv from the official installer, uv-managed CPython 3.11 for everything

`uv` was not installed; the official PowerShell installer put 0.12.23 in `~/.local/bin`. The only
system Python was 3.14, so `uv python install 3.11` supplies the interpreter the six library
environments need, and the orchestrator uses the same 3.11 (`.python-version`) so one interpreter
serves all seven environments.

## 2026-10-08 Git: repo initialised at M0, one commit per milestone

The handoff requires a committed manifest (M1 acceptance) and a git commit in every run record, so
the repo was initialised at M0 and each milestone ends in a commit once its gate passes.

## 2026-10-08 The two source documents moved to docs/

`VA-RAG handoff for Claude Code.md` became `docs/HANDOFF.md` and the literature review became
`docs/LITERATURE.md`, the paths the handoff's layout names. No copies remain at the root.

## 2026-10-08 Execution limits on Windows: timeout and stripped environment only

The harness applies the 60 s timeout, a temp cwd and a stripped environment everywhere. The 2 GB
address-space limit (`resource.RLIMIT_AS`) and the no-network namespace (`unshare -n`) exist only
on POSIX and are applied there. Windows has neither; the handoff already says "where the OS allows
it". Moving execution into containers is the handoff's open question 7, default "process limits".

## 2026-10-08 Validation steps 6 and 7 recorded as skipped until M5 and M4

Step 6 (each clue alone infers its version; error tracebacks reproduce) needs the M5 signal
extractor and `make-error-clue`; step 7 (gold chunks exist in the corpus) needs the M4 corpus.
`bench validate` records them as `skipped` with the reason, and a concept enters the manifest when
no step *failed*. M4 and M5 remove the skips and re-validate. Error clues are therefore not
authored in M3; pin and code clues are, and the clue rotation draws from the types a concept
declares.

Update, same day, on the user's instruction: the skip is tied to the module, not to a milestone
label. Step 7 imports `varag.corpus.retrieve` and calls `check_gold_chunks(concept)`; step 6 imports
`varag.pipeline.infer` and calls `check_clues(concept)`. Each returns a list of problems. While the
module does not exist the step is skipped; as soon as the module exists without its check the step
fails, so M4 and M5 cannot land without wiring the check.

## 2026-10-08 Version-number lint scope

The lint rejects a version number in the query, in code clues and in the user-written snippet of
an error clue. Pin clues are exempt (a pin is a version by definition) and captured tracebacks are
exempt (NumPy 2 says "was removed in the NumPy 2.0 release", which is the decisive migration-message
signal the design wants).

## 2026-10-08 Mock anchors are computed over targeted instances

`mock_ref` must score 100% and `mock_wrong` 0% with every instance `wrong_version`. Both are
computed over ambiguous and version-stated instances. No-conflict controls have no "other
version", so they are excluded from the anchor check; their outcomes are `pass_both`, `pass_one`
or `broken` as the handoff defines.

## 2026-10-08 Seed concepts are `split: dev`

The three M3 concepts (and the later seed set) are smoke concepts. They are marked `dev` so that
nothing tuned on them touches the test split.

## 2026-10-08 Lock files are resolved for one interpreter and platform, not universally

`uv pip compile --universal` resolves for every Python from 3.11 upward. On 3.14 pandas 3.0.6
requires NumPy 2.3 or later, which conflicts with the NumPy 1.26.4 pin that keeps both pandas
environments on the same NumPy, so the universal resolution has no solution. Locks are therefore
compiled for Python 3.11 on the building platform (win_amd64 here), with hashes. On another
platform, run `varag env build --relock` once and commit the new locks and manifest.

## 2026-10-08 Inventory walks dir() plus __all__ plus rule-set names, with an `in_all` flag

The handoff says to honour `__all__`. Walking only `__all__` lost reachable public names that user
code calls: `np.INF`, `np.round`, `np.compat` are absent from NumPy 1.26's `__all__`, and pydantic 2
serves `validate_arguments` through its migration `__getattr__` without listing it in `dir()`. The
extractor now probes the union of `dir()`, `__all__` and every name the rule sets mention under
that root, records `in_all` per entry, and lets the real `getattr` decide presence.

## 2026-10-08 pydantic config keys are keyed `pydantic.Config.<key>`

`pydantic.config` is a real module (BaseConfig, Extra, ConfigDict, and V1 helpers that V2 removed),
so it is an inventory root of its own. Config keys use the synthetic `pydantic.Config.<key>` path.

## 2026-10-08 Rule-set corrections after the first audit, with the environment evidence

The environments contradicted five hand-transcribed rules. The rules were changed, the
environments were not. Evidence was collected by probing each environment's interpreter
(`scratchpad/evidence.py`, 8 October 2026):

1. `pandas.Series.dt.week`, expected `old_only`, found `shared_same`. In pandas 3.0.6,
   `"week" in dir(pandas.core.indexes.accessors.CombinedDatetimelikeProperties)` is True, and
   `pd.Series(pd.period_range("2020-01-01", periods=2, freq="D")).dt.week` returns `[1, 1]`, while
   the same access on a datetime Series raises `AttributeError: 'DatetimeProperties' object has no
   attribute 'week'`. The accessor-class symbol exists on both sides; only the datetime behaviour
   was removed. Rule dropped. `pandas.DatetimeIndex.week` (present in 1.5.3, `hasattr` False in
   3.0.6) stays and captures the removal.
2. `pandas.Series.dt.weekofyear`: identical evidence to item 1. Rule dropped.
3. `pandas.DataFrame.resample(convention)`, expected `old_only`, found `shared_same`.
   `inspect.signature(pd.DataFrame.resample)` in 3.0.6 contains
   `convention: "Literal['start', 'end', 's', 'e']" = 'start'`; in 1.5.3 it contains
   `convention: 'str' = 'start'`. The keyword is accepted by both. Rule dropped.
4. `pydantic.PaymentCardNumber`, expected `old_only`, found `deprecated_in_new`. In 2.13.4,
   `getattr(pydantic, "PaymentCardNumber")` returns a class without raising, no warning is emitted on
   access, and the class carries `__deprecated__`, which is how the inventory marks it. Expected
   bucket changed to `deprecated_in_new`.
5. `pydantic.Color`, expected `old_only`. In 1.10.13, `getattr(pydantic, "Color")` raises
   `AttributeError: module 'pydantic' has no attribute 'Color'` and `pydantic.color.Color` exists; the
   same holds in 2.13.4. The symbol never lived at the top level. Rule re-pointed to
   `pydantic.color.Color`, which is outside the inventory roots and therefore informational.

One audit expectation changed for the same reason: pydantic's MOVED_IN_V2 names may be served with
a warning rather than removed. In 2.13.4, `getattr(pydantic, "PyObject")` succeeds and emits
`PydanticDeprecatedSince20: pydantic:PyObject has been moved to pydantic.types:ImportString`, so the
inventory files it under `deprecated_in_new` (route `warning_on_access`) and the audit accepts
`old_only` or `deprecated_in_new` for that table.

## 2026-10-08 Deprecation directive scope, and rule-listed deprecations

A `.. deprecated::` directive counts only in the docstring's summary region (before the first
numpydoc section header). Searching the whole docstring marked `pandas.concat` deprecated because
one of its parameters carries a directive. Names a rule set lists as deprecated or removed are
filed under `deprecated_in_new` when they exist on both sides: NumPy's `row_stack` warns only when
called, so no static route sees it. pydantic's MOVED_IN_V2 names may be served with a warning
(`PyObject`) rather than removed, so the audit accepts either bucket for them.

## 2026-10-08 Two ruff NPY201 names never existed in NumPy 1.26.4; Styler is not inventoried

The audit reports `numpy.INF` and `numpy.DTypePromotionError` as misses because ruff lists them
and the inventory has them on neither side. A probe of the old environment confirms neither name
is reachable at the top level of 1.26.4 (`DTypePromotionError` lives in `numpy.exceptions`), so
these are rule-set quirks, not extraction gaps, and they stay as reported misses. NumPy recall is
98.6% against the 95% gate. `pandas.Styler` is listed as an inventory root by the handoff but
importing it needs jinja2, which the environments do not include. On the user's instruction the
root was removed from `configs/libraries.yaml` and jinja2 was not added: each environment holds
only the library, its dependencies and pytest.

## 2026-10-08 Keyword binding against callees that accept **kwargs

The handoff has the guard abstain "on calls that forward **kwargs", which is read as call sites
that splat a dict. A keyword explicitly declared in exactly one version's signature is recorded
as a usage of that side even when the other side's callee accepts **kwargs (pydantic.Field takes
**extra on both sides, and `Field(regex=...)` is the canonical parameter rename). Such a usage is
flagged `uncertain`, because the call might still run on the other side.

Rule for M5 and M6, set by the user on 8 October 2026: an `uncertain` keyword is a full exclusive
usage when a rule set under `data/rules/` lists the rename or removal (`pydantic.Field(regex)` is
listed by bump-pydantic BP003, so it counts in full and the guard flags it). Otherwise the signal
extractor gives it half weight and the blend guard abstains on it.

Superseded on 2026-10-15: an unconfirmed absorbed keyword is now `shared_unknown`, with weight 0
(see "Keywords absorbed by **kwargs need confirmation").

## 2026-10-08 Inventory entries carry `found_by: walk | rule_seed`; the audit prints both recalls

Every inventory entry records whether the plain walk (`dir()`, `__all__`, submodules) reached it
or whether a rule-set name had to seed the probe. The diff carries the tag (a shared symbol is
`walk` only when both sides' walks reached it). `varag inventory audit` gates on overall recall and
prints walk-only recall beside it, so rule-set seeding cannot hide extraction gaps.

## 2026-10-08 All six environments run Python 3.11.17, and verify now checks it

`envs/manifest.json` records `python_version` 3.11.17 for pandas_old, pandas_new, numpy_old,
numpy_new, pydantic_old and pydantic_new, each at `envs/<name>/.venv/Scripts/python.exe`.
`varag env verify` now also compares the probed interpreter against `python` in
`configs/libraries.yaml`, so a drift to another minor version fails verification.

## 2026-10-08 Real-model output is executed only under WSL2 or a container

Rule set by the user: before any real-model output is executed, the harness runs under WSL2 or a
container so that the 2 GB address-space limit and the network isolation apply. `varag run`
enforces it: for any backend that is not a mock, `require_isolation_for` refuses to start unless
`isolation_status()` reports both `memory_limit` (POSIX `RLIMIT_AS`) and `network_isolation`
(`unshare -n` works). Mock backends return reference code and stay runnable on Windows.

## 2026-10-08 Memory addresses are masked in inventory signatures and defaults

`numpy.errstate(call)` has a default whose repr embeds an object address, so every build produced
a different inventory line and the content hash moved for no reason. The extractor masks
` at 0x<hex>` in signature strings and default reprs, so inventories are byte-identical across
builds and `shared_changed` cannot fire on an address. A unit test checks that only the hex
digits change and the type name in the repr is kept.

## 2026-10-08 pandas accessor members are keyed by accessor class; Series.dt.week was a real removal

On the user's instruction the three combined accessor roots (`pandas.Series.str`, `.dt`, `.cat`)
were replaced by the classes that define the members: `pandas.StringMethods`,
`pandas.DatetimeProperties`, `pandas.TimedeltaProperties`, `pandas.PeriodProperties` and
`pandas.CategoricalAccessor`. All five exist under the same import paths in 1.5.3 and 3.0.6, and
`type(series.dt)` is `DatetimeProperties` for datetimes and `PeriodProperties` for periods on both.

Finding: the `Series.dt.week` rule dropped in the first audit was a real removal for datetime
series. In 1.5.3 `"week" in dir(DatetimeProperties)` is True (with a FutureWarning on use); in
3.0.6 it is False, while `PeriodProperties.week` is True on both. The combined
`CombinedDatetimelikeProperties` class inherits from all three, so keying by it reported
`shared_same`. The rules now list `pandas.DatetimeProperties.week` and `.weekofyear` as
`old_only` and `pandas.PeriodProperties.week` as kept. The signal extractor maps
`s.str.x` to `pandas.StringMethods.x`, `s.cat.x` to `pandas.CategoricalAccessor.x`, and `s.dt.x`
to the three dt classes; when the candidates disagree on the bucket (as `week` does) it abstains,
because the dtype decides and static analysis cannot see it.

## 2026-10-08 pydantic migration-served names, classified by behaviour on V2

Rule set by the user: a migration-table name that resolves on V2 with a deprecation warning
belongs in `deprecated_in_new`; one that raises `PydanticImportError` belongs in `old_only`.
`dump_rules.py` now records, for every name in pydantic's `_migration` tables, what `getattr` does
on 2.13.4 (`served_behaviour`), and the audit derives the expected bucket from that behaviour,
printing one line per name. Observed on 2.13.4: every REMOVED_IN_V2 name under the roots raises
`PydanticImportError` and sits in `old_only`; `PyObject` (MOVED_IN_V2) resolves with
`PydanticDeprecatedSince20` and sits in `deprecated_in_new`; `BaseConfig`, `Extra` and
`validate_arguments` (DEPRECATED_MOVED_IN_V2) resolve without a warning on access but carry
`__deprecated__`, and sit in `deprecated_in_new` through that route.

## 2026-10-08 Field() V1 keywords mined from pydantic 2.13.4; deprecated_in_new covers keywords

`dump_rules.py` reads the names that `Field()` pops from `**extra` in its source, then executes
`Field(<name>=...)` on 2.13.4 and records the outcome and the library's own message in
`data/rules/pydantic/field_v1_kwargs.json`:

- `regex`, `const`, `unique_items`: `PydanticUserError`, code `removed-kwargs`, therefore
  `old_only` keywords. The three messages are the first decisive migration-message patterns in
  `configs/migration_messages.yaml` (side `new`, reproduced in pydantic_new 2.13.4).
- `min_items`, `max_items`, `allow_mutation`, `include`: accepted with `PydanticDeprecatedSince20`,
  therefore `deprecated_in_new` keywords.

The diff now extends `deprecated_in_new` to keywords: a keyword declared only on the old side,
whose owner on the new side accepts `**kwargs`, moves to `deprecated_in_new` when a rule set lists
it as deprecated-but-working (`absorbed_by_var_kwargs: true`). Without the rule, or without
`**kwargs` on the new side, it stays `old_only`. The bump-pydantic transcription was aligned
(`min_items`, `max_items`, `allow_mutation` were wrongly `old_only`; `include` was missing).

Confirmation: `pydantic.Field(regex)` is `old_only`, listed by bump-pydantic BP003 and by the mined
removed-kwargs table, and a usage of it in pyd-001's `ref_old.py` is reported by the extractor
with `uncertain: true` (Field takes `**extra`) and `corroborated: true`. The diff carries
`rule_listed`, the set of symbols any rule set names, which is what `corroborated` reads.

## 2026-10-08 M4 change: chunk examples are checked by execution, not by the signal extractor

Rule set by the user for M4. Each chunk example runs in its tagged environment with pandas or
NumPy preloaded and printed output ignored. It is kept only if it runs without error; any
deprecation warning is recorded on the chunk. It also runs in the other environment, and the
chunk gets `discriminative: true` when it fails there. Examples that time out are dropped. The
signal extractor is not used for this check (it is M5).

## 2026-10-08 soft_fail attribution by stack, migration-message warnings, reference subtraction

Rules set by the user and how the harness implements them:

- Attribution. A warning belongs to the solution when any frame whose file is named exactly
  `solution.py` is on the stack when it fires. The injected conftest installs a
  `warnings.showwarning` hook at import, before pytest imports `test_solution.py` and through it
  `solution.py`, so warnings raised during import (module-level class definitions, decorators)
  count as well as those raised during test calls. Probe evidence: pydantic 2.13.4 reports its
  config-key warning against `pydantic/_internal/_config.py`, so the old attribution by reported
  module (`-W ...:solution` and `pytest_warning_recorded` filenames) missed it.
- pytest runs with `-p no:warnings`, because its warnings plugin swaps `showwarning` around every
  phase. pytest's `-W` option goes with the plugin, so warnings-as-errors is now applied by the
  hook: with `VARAG_WARNINGS_AS_ERRORS=1` an attributed soft warning is raised as an exception
  (verified to propagate out of `warnings.warn`, both at call time and at import time). The
  conftest refuses to run (infra_error) if the hook was replaced.
- What counts. DeprecationWarning, FutureWarning and their subclasses (PydanticDeprecatedSince20
  is one), plus any warning whose message contains a `pattern` or matches a `regex` in
  `configs/migration_messages.yaml`, whatever its category. pydantic's "Valid config keys have
  changed in V2" (a UserWarning; reproduced on 2.13.4, absent on 1.10.13) was added there.
  PendingDeprecationWarning is not counted. Warnings-as-errors raises all three kinds.
- Subtraction. Validation step 9 now records, per reference and environment, the signatures
  (category plus normalised message, addresses masked) of its soft warnings. A model answer's
  soft_fail is computed net of the signatures that the native reference raises in the same
  environment (ref_old in old, ref_new in new, ref_portable for a control). Validation step 5
  applies the same subtraction to ref_portable on concepts; a control's ref_portable is its own
  baseline and must raise none.
- Fixtures on pydantic_new that are soft_fail: a `.dict()` call, a module-level `@validator`, a
  class-based `Config` (with a V2-valid key, so only the class-config deprecation fires), and
  `model_config = {"anystr_strip_whitespace": True}` (counted through the pattern). A clean V2
  model is not soft_fail, a warning the test file raises itself is not attributed, and the
  V1-style validator run on pydantic_old is not soft_fail.

## 2026-10-08 M4 built with the user's decisions on docs/plans/M4.md

- D1: chunk tokens are counted with the Qwen2.5-Coder-7B-Instruct `tokenizer.json`, pinned by model
  revision `c03e6d35...` and sha256 in `configs/models.yaml`, downloaded on demand to the gitignored
  `data/tokenizer/`. Every chunk's provenance records repo, revision, file and sha256.
- D2: only the 350-token cap is enforced. Trim order: drop the example if it does not fit
  (examples are executed, so they are never cut), then shorten the description, then strip
  signature annotations, then shorten the parameter list while keeping version-exclusive and gold
  keywords. Lengths are reported in `data/corpus/<library>/build_report.json`; the median chunk is
  74 to 84 tokens and almost every chunk is under 200.
- D3 (changed by the user): distractors are drawn the same way for every instance, controls
  included, from the whole corpus minus the concept's gold chunks. The BM25 query is the concept's
  task text only, so all instances of a concept share distractors. `doc_conflict` conflicts only on
  a linked pair across versions: a `shared_changed` symbol with chunks from both versions, or an
  old-side symbol (`old_only` or `deprecated_in_new`) in an old-version chunk and its
  `data/rules` replacement in a new-version chunk. Chunk `symbols` lists the owner and its
  keywords, so keyword pairs (`Field(regex)` to `Field(pattern)`) link through owner chunks. Each
  pair is a `conflict_reason`, written to `runs/<id>/traces.jsonl` per instance. Step 7 reports per
  concept whether the gold pair is linked by the rules alone and fails when it is not. On the real
  corpus the control's distractors include `numpy.cumproduct` (old_only) and
  `numpy.cumulative_sum` (new_only) and the set does not conflict, because no rule maps one to the
  other.
- D4: migration chunks are not built in M4; when the ablation runs they are generated from
  `data/rules`.
- D5: when a concept's gold is a keyword, the owner chunk prefers an example whose call to the
  owner passes that keyword (checked on the call's own arguments, so `constr(regex=...)` beside
  `Field(...)` does not count). `keyword_example` on the chunk reports whether the final chunk's
  example passes it. 2.13.4's `docs/errors/*.md` were added as sources because the only
  `Field(pattern=...)` example outside the migration guide is there.
- D6: superseded by D3 (a `deprecated_in_new` symbol plus its replacement is a linked pair).
- D7: examples run on this host. Each runs in its own temp directory, with stdout, stderr and stdin
  detached; examples naming a URL are dropped unrun; a failed example is re-run in a fresh worker
  process before it is dropped; timeouts (10 s) are dropped. Discriminative status uses the same
  retry in the other environment.
- D8: corpora (`data/corpus/<library>/<version>.jsonl`, about 11 MB in total), the example-check
  cache, the build reports, the pinned pydantic docs and `seed_map.yaml` are committed.
- Order: targeted instances are balanced per concept; controls are balanced across a library's
  controls (with one control, its new-side gold comes first).

Open issue for review: both `pydantic.Field` gold chunks carry no example. `Field`'s signature
alone takes 326 tokens in 1.10.13 and about 330 after trimming in 2.13.4, so under the D2 trim order
no example fits. No 1.10.13 doc example passes `regex=` to `Field` at all; the 2.13.4
`Field(pattern='test')` example exists but is dropped for length.

## 2026-10-14 Linux (WSL2, Ubuntu 24.04) is the build platform; locks and derived data rebuilt there

The user moved the work to WSL2 with Ubuntu and uv, and real-model output has to run there anyway
(2026-10-08). Locks are resolved per platform (2026-10-08), so the six locks were recompiled on
Linux x86_64. Every file that records a lock hash was then rebuilt from them in WSL2:
`envs/manifest.json`, the inventories and diffs, the dumped rule tables, the corpora and their
example-check caches, the validation records and `data/tasks/MANIFEST.json`. Windows no longer
builds the environments; the unit tests still run there.

- No pinned version changed. The Linux locks drop `colorama`, which pytest needs on Windows only.
- pandas_new gets `tzdata==2026.5` as an extra pin, the version its Windows lock carried. pandas
  3.0.6 requires `tzdata` only on Windows; on Linux `zoneinfo` reads the host database, and Ubuntu
  24.04 ships `US/Eastern` and the other legacy names only in `tzdata-legacy`. Without the package
  six pandas 3.0.6 examples failed with `ZoneInfoNotFoundError: 'No time zone found with key
  US/Eastern'`, and two 1.5.3 `tz_localize` examples became discriminative for a reason that has
  nothing to do with pandas. `zoneinfo` falls back to the package for any name the host lacks.
- All six environments and the orchestrator run Python 3.11.15, the newest 3.11 that uv 0.11.6
  installs; the Windows build ran 3.11.17. `env verify` checks the minor version, and `env build`
  records the patch in the manifest, so a machine whose uv installs another 3.11 patch still
  verifies against the same locks.
- Against the Windows build: the inventory diffs are identical apart from Linux-only NumPy names
  (`numpy.float128` and `numpy.complex256` in `shared_unknown`, their parameters in `new_only`,
  `numpy.kernel_version` in `old_only`). Audit recall is unchanged (NumPy 98.6%, pydantic 100%,
  pandas 100%). Corpus: pandas 1.5.3 1196 chunks, 578 examples kept, 56 discriminative; pandas
  3.0.6 1130, 837, 24 (26 on Windows); NumPy 1.26.4 1011, 675, 29; NumPy 2.4.6 990, 771, 94;
  pydantic unchanged (1.10.13 425, 62, 11; 2.13.4 361, 108, 86). `bench validate` passes 4/4, the
  mock anchors score 100% and 0%, and all tests pass.
- Every per-chunk difference was a Windows artifact. The two pandas 3.0.6 `DatetimeTZDtype`
  examples were discriminative on Windows only because pandas_old there has no time-zone database
  at all (`'No time zone found with key UTC'`). The NumPy `load` and `savez_compressed` examples
  errored on Windows and run on Linux. The new NumPy chunks are the Linux-only names above.
- Harness: `unshare -n` needs root, so when it fails the network namespace comes from
  `unshare -rn`, inside a new user namespace. New tests on Linux check that a solution can neither
  connect out nor allocate past the 2 GB `RLIMIT_AS`. Both limits apply on WSL2, so `varag run`
  accepts real-model backends there.
- Files whose hashes are recorded are now written with LF line endings on every platform; on
  Windows several were written with CRLF, which a Linux checkout would not reproduce.

## 2026-10-15 Gold examples are shown on both sides or on neither

User decision. pyd-001's two `pydantic.Field` gold chunks stay without an example: the D2 trim
order is unchanged and no example is hand-written. General rule, applied when gold chunks are
injected and never in the corpus: a concept's two gold chunks either both show an example that
uses the gold symbol (for a keyword gold, one that passes the keyword to its owner) or neither
does. When only one side shows one, that example is stripped for the concept's instances
(`Retrieved.example_stripped`, written to the traces). Validation step 7 records
`gold_examples: both | neither` in `validation.json`; every result row carries it, `run.json`
slices the intended-version pass rate by it, and `varag run` refuses to start when the corpus now
gives a different value than validation recorded. Seed concepts: pd-001, np-001 and ctl-np-001
`both`, pyd-001 `neither`; none needs stripping.

## 2026-10-15 tzdata pinned in all six environments; zoneinfo never reads the host database

User decision, superseding the pandas_new-only pin of 2026-10-14. Every environment pins
`tzdata==2026.5`, and the stripped environment used by the harness, the probes and the example
workers sets `PYTHONTZPATH=""`. CPython's `zoneinfo` reads that variable from `os.environ` even
under `-I`, and an empty value leaves `zoneinfo.TZPATH` empty, so every zone name resolves from the
pinned package. A harness test checks, in each of the six environments, that `TZPATH == ()` and
that `US/Eastern` resolves. The relock added `tzdata` to the five locks that lacked it and changed
nothing else; every lock-derived file was rebuilt. Inventory buckets, audit recall and every
chunk's example result are unchanged.

pandas 1.5.3 and 3.0.6 resolve zone names through different libraries, so their time-zone data
sources differ. In pandas_old, `pd.Timestamp("2020-01-01", tz="US/Eastern").tz` is a `pytz` zone
(`pytz.tzfile.US/Eastern`) from pytz's bundled database; in pandas_new it is a `zoneinfo.ZoneInfo`
from the `tzdata` package. Both are IANA release 2026e here (pytz 2026.5, tzdata 2026.5), so the
data agree today, but a relock could move them apart.

## 2026-10-15 `bench candidates` lists keyword-level pairs

Before more concepts are written (user request). Symbol pairs are rule-set replacements whose old
side is a symbol. Keyword pairs are keywords present on one side only, or renamed, on an owner
present in both versions whose signature was read on both sides. A rename comes from
`data/rules` when listed; otherwise it is inferred when the two names are related (one a prefix or
suffix of the other, or at least 75% similar), best match first, one to one. Pairing the only
lost keyword with the only gained one was tried first and rejected: it paired
`percentile(interpolation)` with `weights` and `ffill(downcast)` with `limit_area`, and missed
`reshape(newshape)` to `shape`. An inferred rename needs its mapping added to `data/rules` from
the release notes before a concept uses it (step 7). `--library` is now optional and repeatable.

Counts on 2026-10-15:

| Library | Symbol pairs | Keyword rows | From rules | Inferred renames | Removed | Added | Left out (unreadable owner) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pandas | 16 | 323 | 10 | 1 | 179 | 133 | 176 |
| numpy | 31 | 71 | 0 | 1 | 12 | 58 | 667 |
| pydantic | 26 | 123 | 5 | 6 | 38 | 74 | 86 |

No keyword row has gold examples on both sides: the owner chunks' examples never pass the
changed keyword, so every keyword-level concept will be `gold_examples: neither`. One symbol pair
per library has discriminative examples on both sides. NumPy's `percentile`/`quantile`
`interpolation` keyword is listed as removed: its replacement, `method`, exists on both sides
and no rule set maps it.

Open issue for review: `inventory/diff.py` buckets a symbol as `shared_same` when its old entry is
not a callable kind (an `attribute` or `module` whose signature was not read) and its new entry is
a function or class, because `_bucket` only compares signatures when the old kind is callable. 70
`shared_same` symbols have an unreadable signature on one side (pandas 17, for example
`DataFrameGroupBy.corr`; NumPy 50, for example `numpy.ma.all`; pydantic 3). `shared_same` is the
portable-answer allowlist, so these should probably be `shared_unknown`; changing it re-buckets
validated data and was left for the user.

## 2026-10-15 shared_same needs the entry read on both sides; text signatures

User decision, resolving the open issue above. `shared_same` now holds only entries read on both
sides that match: both signatures read and equal, or both non-callables of the same kind (module,
constant, config key). A kind mismatch, or a callable whose signature was not read on either
side, is `shared_unknown`. Parameters compare defaults as before.

The extractor records `callable` on every entry and `signature_source: inspect | text | none` on
callables. When `inspect.signature` fails or gives a bare `(*args, **kwargs)`, it tries a text
signature before giving up: `__text_signature__`, then a docstring first line that names the
object and parses as a signature. Text is parsed with `ast`, never executed; defaults are kept as
source text. Callable objects that are not routines (NumPy ufuncs, NumPy 1.26's `numpy.ma.all`, a
`_frommethod` instance) are still classified `attribute`, but their signatures are now read too.

Callables by signature source:

| Environment | inspect | text | none |
| --- | --- | --- | --- |
| pandas 1.5.3 | 790 | 4 | 168 |
| pandas 3.0.6 | 827 | 0 | 99 |
| NumPy 1.26.4 | 578 | 154 | 199 |
| NumPy 2.4.6 | 921 | 6 | 23 |
| pydantic 1.10.13 | 220 | 0 | 176 |
| pydantic 2.13.4 | 222 | 0 | 120 |

Extension of the rule, not in the user's instruction: a parameter present on one side only,
whose owner exists on both sides but was not read on the other (an unread signature or a kind
mismatch), is `shared_unknown`, with `present_on` and `owner_unread_on` on the entry. Without it,
reading NumPy 2's ufunc signatures while 1.26's stay unreadable made 1,134 new `new_only`
parameters (`numpy.abs(casting)`), and older cases such as `numpy.arange(device)` and
`pandas.DataFrameGroupBy.corr(method)` were already false exclusives. The signal extractor already
abstains on keywords whose callee is `shared_unknown`, so inference is unaffected.

Symbols that moved, against the diffs committed before the change (`None` means the entry did not
exist before):

- pandas, 195: new_only to shared_unknown 171 (one-sided parameters of owners unread on the old
  side), shared_same to shared_unknown 17, new_only to shared_same 2, new_only to
  shared_changed 2, None to shared_unknown 2, old_only to shared_unknown 1.
- NumPy, 2,224. New entries, 1,290: to shared_unknown 866, new_only 276 (mostly owners new in
  2.x, such as `numpy.acos`), shared_same 117, old_only 31. Existing entries, 934: new_only to
  shared_same 409 (1.26 signatures now read from text), new_only to shared_unknown 222,
  shared_same to shared_unknown 141, shared_unknown to shared_same 82, shared_unknown to
  shared_changed 57, new_only to shared_changed 11, old_only to shared_unknown 10, old_only to
  shared_same 2.
- pydantic, 105: old_only to shared_unknown 85, None to new_only 10, shared_same to
  shared_unknown 9, new_only to shared_unknown 1.

Diff sizes after the change:

| Library | old_only | new_only | deprecated_in_new | shared_changed | shared_unknown | shared_same |
| --- | --- | --- | --- | --- | --- | --- |
| pandas | 416 | 209 | 8 | 734 | 334 | 2768 |
| NumPy | 232 | 583 | 3 | 149 | 1322 | 2488 |
| pydantic | 541 | 668 | 30 | 98 | 152 | 213 |

Audit recall is unchanged (NumPy 98.6%, pydantic 100%, pandas 100%).

Seed check: every gold symbol, every symbol of every gold chunk, and every library symbol the
references name kept its bucket, with one exception. `numpy.asarray`, which the np-001 and
ctl-np-001 references call, moved from shared_unknown to shared_changed. Its 1.26 signature is now
read from the docstring (`(a, dtype=None, order=None, *, like=None)`), and 2.4 adds `device` and
`copy`. The references' exclusive usages are unchanged (`numpy.trapz` old, `numpy.trapezoid` new);
`np.asarray(..., dtype=...)` is no longer abstained. All four concepts re-validate, the control's
retrieved set still does not conflict, and every chunk's example result is unchanged.

Caveat: comparing a text signature on one side with an inspected one on the other decides the new
buckets of 67 NumPy owners and `pandas.describe_option`. Most changes are real (`asarray` gains
`device` and `copy`), but some come from the docstring form:
- `numpy.ndarray.mean(keepdims)` is now old_only because 2.4 declares `**kwargs`, which is the
  existing `uncertain` keyword case.
- `numpy.busday_count` differs only in `holidays=[]` against `holidays=()`.

`signature_source` is on every entry, so M5 can discount a text-against-inspect difference.

## 2026-10-15 NumPy keyword rules from the 2.4.0 release notes

`data/rules/numpy/release_notes.json` is hand-mined like the pandas file and quotes the notes. It
maps:
- `interpolation` to `method` for `percentile`, `nanpercentile`, `quantile` and `nanquantile`
  (gh-29973);
- `reshape(newshape)` to `reshape(shape)` (gh-29994).

All five land in old_only as expected. The rename `reshape(newshape)` to `shape`, previously
inferred, is now backed by the rules.

## 2026-10-15 `bench candidates` marks one-directional pairs

User request. A pair is `one_directional` when its new-side form also exists in the old version:
code written the new way runs on both, so only the old form is version-specific. Otherwise it is
`two_directional`.

| Library | Symbol pairs (two / one) | Keyword pairs (two / one) |
| --- | --- | --- |
| pandas | 1 / 15 | 2 / 9 |
| numpy | 1 / 30 | 1 / 4 |
| pydantic | 25 / 1 | 8 / 3 |

The two-directional supply for pandas and NumPy is small:
- pandas: `DataFrame.applymap -> map`, `read_csv(date_parser) -> date_format`, and the inferred
  `Rolling.quantile(quantile) -> q`;
- NumPy: `trapz -> trapezoid` and `reshape(newshape) -> shape`.

Two of these five pairs are already seed concepts. With one_directional capped at a third, each of
these libraries can hold at most one one-directional concept per two two-directional ones.

## 2026-10-15 Concept class `exclusivity: one_directional`

User decision, extending the handoff's exclusivity types and validation steps.

- References: `ref_old` (passes old, fails new) and `ref_portable` (passes both, no deprecation
  warning). There is no `ref_new`: the loader rejects one and requires
  `portable_alternative: plain`. `ref_portable` is the new side's native reference, used as the
  soft-warning baseline and as the mock answer.
- Instances: target new only, `new/no-clue` and `new/clue-<type>`. There is no version-stated
  instance, since the instruction names only the clue conditions.
- Validation:
  - Step 1 checks `ref_old` in old and `ref_portable` in new.
  - Step 2 checks `ref_old` only.
  - Step 5 checks `ref_portable` in both. In old its warnings are counted net of `ref_old`'s; in
    new it must be clean, because it is its own baseline.
  - Step 4 checks that `ref_old` uses an old-side symbol and no new_only one, `ref_portable` uses
    no exclusive symbol, gold.old is old_only or deprecated_in_new, and gold.new is in a shared
    bucket.
- Cap: at most one third of each library's concepts, controls excluded. `bench validate` prints
  the class counts per library and any library over the cap. `varag run` refuses to start while
  any library is over.
- Reporting: results report the class separately, as `by_exclusivity` in `run.json`, and every
  result row carries `exclusivity`.
- Test: a synthetic concept in the test fixtures (`np.percentile(interpolation=...)` to
  `method=`) validates end to end. It is not in `data/tasks`.

## 2026-10-15 Keyword-level concepts are all `gold_examples: neither`

No keyword pair's owner chunks show an example that passes the changed keyword, in any library.
So every keyword-level concept (`param_rename`, `param_removed`, `default_change`) is
`gold_examples: neither`. The gold_examples and change_type slices therefore overlap: the
`neither` slice is largely the parameter-level concepts. They must be reported together, as a
cross-tabulation, never one without the other.

## 2026-10-15 The parameter extension stays

User decision: a parameter on one side only, whose owner was not read on the other side, stays
`shared_unknown`, as built above.

## 2026-10-15 Keywords absorbed by **kwargs need confirmation

User decision. It replaces the half-weight rule of 2026-10-08 ("Keyword binding against callees
that accept **kwargs") and the M5/M6 rule recorded with it.

A keyword declared on one side only, whose owner on the other side accepts `**kwargs`, is
`shared_unknown`. The exception is a keyword that `data/rules` names, as an old symbol or a
replacement; that includes execution probes stored there, such as the Field probe in
`field_v1_kwargs.json`. A confirmed keyword keeps its exclusive bucket: the signal extractor
flags it `uncertain` and `corroborated`, and it counts as a full exclusive usage. An unconfirmed
one now has weight 0. The extractor records it as an abstention ("keyword not confirmed on both
sides"), and the guard abstains. Each such entry carries `present_on` and
`absorbed_by_var_kwargs_on`. The earlier `deprecated_in_new` route for rule-kept keywords
(`Field(min_items)`) is unchanged.

178 keywords moved to `shared_unknown`:

| Library | Total | From old_only | From new_only | Examples |
| --- | --- | --- | --- | --- |
| pandas | 103 | 50 | 53 | `DataFrame.all(level)`, `DataFrame.apply(engine)` |
| NumPy | 21 | 12 | 9 | `numpy.clip(min)`, `numpy.errstate(all)` |
| pydantic | 54 | 10 | 44 | `Field(validation_alias)` and most V2-only Field keywords |

Diff sizes after the change:

| Library | old_only | new_only | deprecated_in_new | shared_changed | shared_unknown | shared_same |
| --- | --- | --- | --- | --- | --- | --- |
| pandas | 366 | 156 | 8 | 734 | 437 | 2768 |
| NumPy | 220 | 574 | 3 | 149 | 1343 | 2488 |
| pydantic | 531 | 624 | 30 | 98 | 206 | 213 |

Audit recall is unchanged.

Regression tests on the real diffs:
- `numpy.ndarray.mean(keepdims)` is `shared_unknown`, not exclusive.
- `numpy.asarray(copy)` and `numpy.asarray(device)` stay `new_only`, because 1.26's `asarray` takes
  no `**kwargs`.
- `pydantic.Field(regex)` stays `old_only` and `Field(pattern)` stays `new_only`, both through the
  rules.

Seed check: no gold symbol, reference symbol or reference usage changed. pyd-001's 2.13.4 gold
chunk lists 16 V2-only Field keywords that moved from `new_only` to `shared_unknown`, such as
`Field(strict)` and `Field(validation_alias)`. pyd-001 still validates, and its conflict still
comes from `Field(regex)` and `Field(pattern)`.

Some moved keywords are real additions that only a probe would confirm. NumPy 2.1's
`clip(min=, max=)`, for example, raises `TypeError` on 1.26, even though 1.26's `clip` takes
`**kwargs`. Such a keyword returns to its exclusive bucket once a rule or a probe result is added
to `data/rules`. A concept that needs one must add it first.

## 2026-10-15 Class caps move to configuration; one_directional is capped benchmark-wide

User decision. The caps live in `configs/experiment.yaml` under `composition.caps`:
- `one_directional`: one third of the whole benchmark, no longer of each library.
- `behavior`: the handoff's 15%, applied to each library, with pandas and NumPy exempt (user
  decision: their behaviour concepts may exceed it). Behaviour concepts are reported separately
  through `by_exclusivity`.

Controls are excluded from the counts. `bench validate` prints the counts and any cap exceeded;
`varag run` refuses to start while one is.

## 2026-10-15 Release-note candidates and `varag bench probe`

User request. Before more concepts are authored, the pandas 2.0, 2.1, 2.2 and 3.0 notes and the
NumPy 2.0 to 2.4 notes (with the NumPy 2.0 migration guide) were mined for two-directional changes
the inventory cannot see: changed argument values, and behaviour changes whose new form needs a
new-only API. There are 39 candidates in `data/candidates/release_notes.json`. Each has a quote,
a URL, and `old`/`new` snippets that assert each version's behaviour.

`varag bench probe <file>` runs both snippets in both environments of the library, using the
corpus example runner. It records the outcome, a form-level verdict and the lock hashes. Every
direction the notes claim held up on the Linux environments. A form-level verdict is not a
concept: `concept_grade` records whether a concept with one shared test can be two-directional,
which needs each version's natural solution to break on the other. That leaves 11 pandas
candidates and 3 NumPy candidates graded two-directional.

The target composition and the decisions it needs are in `docs/plans/composition.md`.
Behaviour concepts cannot pass validation step 7 as built: step 7 requires a gold pair linked by
`data/rules`, and a behaviour concept's gold is the same symbol, or a pair no rule maps. That
plan's D-b proposes the fix; nothing is authored until it is decided.

## 2026-10-18 Value rules, and a probe for every candidate kind

User instruction (2026-10-18), completing the composition work.

- **Value rules.** `data/rules/<library>/value_rules.json` records argument values valid on one
  side only, as `(callable, parameter, value, side)` with the other side's spelling as
  `replacement` where the notes give one, and the quote and URL. pandas has 198 records: the
  end-of-period aliases (`M`, `BM`, `SM`, `CBM`, `Q`, `BQ`, `Y`, `BY`, `A`, `BA` against `ME`,
  `BME`, `SME`, `CBME`, `QE`, `BQE`, `YE`, `BYE`) on seven callables, the sub-day aliases (`H`,
  `BH`, `CBH`, `T`, `L`, `U`, `N`), the Timedelta units, `errors="ignore"`, `format="ISO8601"`
  and `"mixed"`, and `dtype="datetime64[D]"`. NumPy has 20: `copy=None`, the `mode` and `side`
  abbreviations, `casting="same_value"` and `dtype="T"`. `rules.value_rules(library)` returns
  the confirmed records; the M5 extractor reads those.
- **Probe.** `varag bench probe` now covers symbol pairs (attribute access through the inventory
  root), keyword pairs and call-only changes (hand-written snippets in
  `data/candidates/snippets.json`), value rules (a call template per callable and parameter) and
  the release-note candidates. Each old and new form runs in both environments; the verdict is
  `two_directional`, `one_directional` or `not_discriminative`, and a pair whose old form breaks
  on the new side only by a soft warning is a `deprecation`-class concept. Results go to
  `data/candidates/probes.json`; each value record gets `probe.confirmed`.
- **Results** (Linux environments, locks as committed): 136 probe-level two-directional rows,
  so the 35 checkpoint is met at that level. 216 of 218 value records confirmed; the two
  unconfirmed are `timedelta_range` with business-hour aliases, which no side accepts. Three
  first-pass verdicts were snippet artifacts and were fixed before the plan: `import numpy.char`
  fails on 1.26 (it is an attribute there), so access snippets now walk attributes from the
  package; `BaseModel.json` compared JSON text; `update_forward_refs` lacked a namespace.
- **Distinct changes.** Probe rows overstate supply: the alias cross product alone is 79 rows for
  one change. `docs/plans/composition.md` counts distinct changes per library and class and sets
  the target composition. Nothing is authored until it is approved.
- **GPU.** This laptop has no GPU (`nvidia-smi` in WSL: "Failed to initialize NVML"). The
  isolation check passes here. All GPU work moves to the user's PC in a fresh session; everything
  that session needs is committed (see `docs/NOTES.md` and, later, `docs/GPU_HANDOFF.md`).

## 2026-10-18 Composition decisions settled; deprecation scoring; model pins

The user settled the composition plan's decisions (`docs/plans/composition.md`, "Decisions"):
`param_value` change type; value gold written `pandas.date_range(freq="M")` and linked through
confirmed value rules; behaviour gold linked through `data/rules/<library>/behaviour.json`, filled
from every probed behaviour change and counting only probe-confirmed entries, feeding the
doc-conflict test only, never signals; value gold chunks prefer an example passing the gold value
under the both-or-neither rule; behaviour-only one-directional candidates left out; Config-key
changes count as parameter-level, and the M5 extractor and M6 guard check config keys in `class
Config` bodies, `ConfigDict(...)` calls and `model_config` dict literals; the five pydantic
controls are `kind: portable_control` (docs may conflict, the task does not depend on the version,
one answer with no question, `conflict_reason` recorded, reported apart from the 10 no-conflict
controls); dev is the 15 seed concepts (3 NumPy, 5 pandas, 7 pydantic), test the other 48, and
seeds may include behaviour; sizes 20 / 13 / 30.

Scoring of deprecation concepts: a strict score (deprecated usage fails, through
warnings-as-errors) is primary; a lenient score (it passes, flagged `soft_fail`) is also reported.
Recorded in `configs/experiment.yaml` (`scoring.deprecation`) before any test-split run. M7
computes both from one execution per answer; `classify` keeps its four outcome classes and gains
the strictness as an input, which is a change to how an outcome is derived, not to the classes.

Models (`configs/models.yaml`): `primary` is `Qwen/Qwen2.5-Coder-7B-Instruct-AWQ` at revision
`8e8ed243bbe6f9a5aff549a0924562fc719b2b8a`; `vllm_large` is `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ`
at `eb3172f06a6d6b3a15f08947b0668d782e4d2d2c`. Both are AWQ 4-bit, group size 128, GEMM kernels,
fp16 activations (from each repo's `config.json`), so the comparison is about scale. `cpu_tiny` is
`Qwen/Qwen2.5-Coder-0.5B-Instruct` at `ea3f2471cf1b1f0db85067f1ef93848e38e88c25`, served on CPU for
output-parsing checks only, never reported. `max_model_len` is 8192 for all three. The client speaks
only the OpenAI chat-completions protocol, so a llama.cpp server can replace vLLM at the same
`base_url`. `varag run` records the backend block and the sampling block in `run.json`. The
revisions were read from the Hugging Face API on 2026-10-18; no weights were downloaded on the
laptop. The chunk tokenizer stays pinned to the fp16 7B repo, which ships the same tokenizer.

## 2026-10-18 M5 plan decisions; Part C groundwork

User decisions on `docs/plans/M5.md`: positional argument values are bound to parameter names
through both versions' signatures and matched against value rules when the parameter sits at the
same position on both sides (skipped when the positions differ or the argument falls into
`*args`); config keys under an unresolved `BaseModel` base count at 1.5; `make-error-clue`
refuses a traceback that names no exclusive symbol, keyword, rejected value or migration message;
behaviour concepts carry pin and code clues only, and the clue-type balance is computed over the
other concepts; an error naming a value a confirmed value rule rejects is negative evidence at
weight 4 for the other side. To bind positions, diff parameter summaries now carry `param_kind`,
which needs the diffs rebuilt (data only; buckets do not change).

Part C groundwork done early, as the user asked: `.gitignore` keeps `report.md`, `run.json` and
`results.jsonl.gz` per run and ignores the response cache (`runs/_cache/`), raw traces,
uncompressed results, model weights (`models/`, `*.gguf`, `*.safetensors`, `*.bin`) and built
environments; `CLAUDE.md` opens with the GPU line; `docs/GPU_HANDOFF.md` is a skeleton with the
section headings, to be filled after M7. `varag preflight` and `varag gpu-day` come after M7.
M5, M6 and M7 are built without stopping; the next stop is after the 15 seed concepts.

## 2026-10-19 M5, M6 and M7 built; offline smoke passes

Built in one pass after the composition decisions, as the user asked.

**M5.** `pipeline/extract.py` extracts every signal of the handoff table with span, symbol, side
and weight; `pipeline/signals.py` (the AST core) binds positional arguments through both
versions' signatures and matches confirmed value rules, reads pydantic config keys from `class
Config` bodies, `model_config` literals and `ConfigDict(...)` calls, and records spans.
`pipeline/infer.py` is the decision rule with the logged margin and `check_clues` for step 6, now
enforced. `pipeline/policy.py`, `questions.py` and `user.py` implement the handoff's policy,
templates and two-arm simulated user; `va_rag` and its three ablations run through `RunContext`.
`varag bench make-error-clue` captures a real traceback in the target environment and refuses one
that names nothing exclusive. Deviations and findings:
- An assignment's value is visited before the target is rebound, so `summary =
  summary.append(row)` scores the call on the DataFrame `summary` was. Without this pd-001's old
  code clue scored 1.5 and step 6 failed.
- Each distinct symbol counts once at its heaviest signal: a symbol imported and then called is one
  signal at the import weight, as the handoff's "each distinct symbol counts once" requires.
- A keyword on a callable that is itself `old_only` or `new_only` adds nothing: the callable is the
  evidence (`ConfigDict(str_strip_whitespace=True)` on V1-less code scored 10 before).
- Value literals count even when the callee is `shared_unknown` (`numpy.array` on 1.26): value
  rules are confirmed by execution, unlike signatures.
- `ConfigDict` exists in pydantic 1.10 as a TypedDict, so it is `shared_unknown`; config keys, not
  the class, carry the V2 evidence.
- Migration messages admitted after reproduction: pandas "The frame.append method is deprecated"
  (1.5.3 only), the 3.0 "Invalid frequency: ... Failed to parse with error message" wrapper and
  "for Period, please use" (3.0.6 only); pydantic `errors.pydantic.dev/2.`, the V2 exception class
  names and "has been moved to the `pydantic-settings` package" (V2 only). NumPy 2.4.6 raises plain
  AttributeErrors for expired names, with no 2.0-era text, so nothing was admitted for NumPy.
- `to_period("M")` works on both pandas versions (checked), so it is no signal; `to_period("ME")`
  fails on both.
- 51 extractor fixtures (acceptance asked for 40), plus decision-rule, question, user, value,
  policy and clue tests.

**M6.** `llm/client.py` speaks the OpenAI chat-completions protocol only, with every sampling
parameter explicit, a sha256 response cache with byte-identical replay and a request log, and
vLLM's tokenize/detokenize for the rendered prompt; a llama.cpp server receives `repeat_penalty`.
`pipeline/guard.py` is the blend guard with the handoff's violation table, fresh-prompt repair,
acceptance check and `guard_rejected`/`guard_unresolved`. `methods/baselines.py` holds the seven
baselines; `mock_blend` and `mock_ask` were added; `varag serve check` checks the served model,
the parameters sent, the rendered prompt and determinism. `varag run` executes the pre-guard code
too, records `blend_static`, `blend_exec` and `guarded_portable`, scores deprecation concepts
strict (primary) and lenient from one execution without `-W error` (the hook records the same
attributed warnings), takes `--limit`, and marks runs of `report: false` backends. On the mocks:
`va_rag` 100% on `mock_blend` against 16.7% for `va_rag_no_guard`, all 18 blends flagged and
fixed; `plain_rag` asks and passes on `mock_ask`; `assume_state` never asks.

**M7.** `eval/stats.py` (cluster bootstrap, Wilson, paired bootstrap, exact McNemar, Holm, Miller's
detectable difference reproducing the handoff's 10.7/12.8/15.7 points, ICC, risk-coverage, AUROC),
`eval/metrics.py` (the full table with slices, the gold_examples x change_type cross-table, inference
and guard metrics, primary contrasts, detectable-effect table), `eval/report.py` (metrics.json and
report.md), `eval/audit.py` (the 50-output sample) and `eval/smoke.py`. `varag smoke --offline`
passed 15/15 on Linux: environments, validation, five mock runs with reports, the anchors, and ten
dev instances through every method on `cpu_tiny`.

**cpu_tiny.** llama.cpp build b11723 (`scripts/serve_cpu_tiny.sh`) serving the Q8_0 GGUF of
`Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF` at revision `ebb2015119c9…` on the CPU; weights live in
`~/.cache/llama.cpp`, outside the repository. Its runs are marked not for reporting. The ten-instance
run exercised the parsing paths with real output: fenced code, `QUESTION:` lines (mind_version asked
on 8 of 10), 10 `no_code` of 110 (assume_state's suppressed questions and unparsable replies), no
multi-block answers, and real wrong-version and broken outcomes.

## 2026-10-19 Seed concepts authored (15, dev)

Per `docs/plans/composition.md`: pandas pd-001 (exists), pd-002 `date_range(freq="M")` to `"ME"`
(removal, `param_value`, the first value gold), pd-003 `read_csv(date_parser)` to `date_format`
(removal, param_rename), pd-004 `as_unit` ns integers (behaviour), pd-005 `fillna(method)` to
`ffill` (one_directional); NumPy np-001 (exists), np-002 `unique_inverse` (behaviour), np-003
`percentile(interpolation)` to `method` (one_directional); pydantic pyd-001 (exists), pyd-002
`orm_mode` to `from_attributes`, pyd-003 `anystr_strip_whitespace` to `str_strip_whitespace`,
pyd-004 `root_validator` to `model_validator` (removal), pyd-005 `dict` to `model_dump`, pyd-006
`validator` to `field_validator`, pyd-007 `Field(min_items)` to `min_length` (deprecation,
`warnings_as_errors`). Every concept carries pin and code clues; the two-directional and
one-directional ones get error clues from `make-error-clue`; behaviour concepts carry pin and code
only. Choices worth knowing:
- pyd-003's new-side error clue cannot come from the gold itself (`class Config` keys only warn on
  V2), so it uses `from pydantic import BaseSettings`, which raises `PydanticImportError` on V2:
  an off-target clue, as the handoff prefers.
- pyd-005 and pyd-007's new-side error clues likewise use `Field(regex=)` and `Field(const=)`,
  whose removed-kwargs errors are migration messages, since `.dict()` and `min_items` only warn.
- The SecretStr keyword pair planned for pydantic was dropped: `SecretStr("x")` is positional in
  natural code, so a keyword concept would be contrived; `anystr_strip_whitespace` took its place.
- `Field(min_items→min_length)` was dropped after validation: `min_length` exists on V1 too
  (`shared_changed`), so step 4 found no new-only gold and `ref_new` used no new-only symbol. The
  pair is two-directional only by behaviour (V1 ignores `min_length` on a list), which the static
  matrix cannot certify. `Field(allow_mutation→frozen)` took its place (`frozen` is new-only). The
  same applies to `Field(max_items)` and `conlist(min_items)`.
- pd-004's test gave two datetime strings in different formats; pandas 2+ parses a column with one
  inferred format and raised. The inputs now share a format.
- Error clues: `make-error-clue` writes the snippet, a `# --- output (stderr) ---` marker, then the
  captured warnings and traceback; the lint reads only the snippet. Two extractor rules were added
  for them: every name the output quotes is removed from the code signals, and the failing
  snippet's remaining code counts at half weight, since the code that failed says little about
  what is installed; pins and named versions are read from the user-written part only, because
  pydantic's own messages say "Pydantic V1 style". Without these, six of the eighteen clues came
  out `CONTEXT_CONFLICT`. Three off-target error clues use a different V1/V2 API than the gold
  because the gold itself only warns on V2 (`BaseSettings`, `Field(regex)`, `Field(const)`).
- Config keys now have corpus chunks (`config_key` kind; the docs line naming the key as the
  description, the inventory entry as source when there is no docstring), so config-key concepts
  have gold chunks and their replacement links make the retrieved sets conflict.
- Portable alternatives: pd-002 `pd.offsets.MonthEnd()`, pd-003 `to_datetime` after reading,
  pd-004 `(series - epoch) // Timedelta(1, "ns")`, pd-005 `ffill()`, np-002 `.ravel()` of the
  inverse, np-003 `method="lower"`, pyd-002 keyword construction, pyd-005 `dict(model)`, pyd-006
  `constr(min_length=1)`; pyd-003, pyd-004 and pyd-007 have none.

## 2026-10-19 GPU PC: environments rebuilt from the committed locks

The GPU session runs on the PC (WSL2 Ubuntu 24.04, kernel 6.18.54.1-microsoft-standard-WSL2, RTX
5070 Ti 16 GB), clone at `~/code/version-aware-rag`, uv 0.13.1. `uv sync`, `varag env build` (no
`--relock`) and `varag env verify` passed on the first try. Against the committed manifest, every
lock sha256, library version and distribution list is identical; only the interpreter paths, the
platform string and the CPython patch differ: uv here installs 3.11.17, the laptop's WSL had
3.11.15. `env verify` checks the minor version only, so no derived file moves. All 294 unit tests
passed before any change.

## 2026-10-19 Seed fixes before any model run (user instruction, GPU session step 1)

- **Failing-snippet code weighs 0 when the error is a version error.** Replaces the half-weight
  rule of 2026-10-19 ("Seed concepts authored"). In a snippet followed by its traceback, when the
  output names an exclusive symbol, keyword or value (an error signal, or a quoted exclusive name),
  or carries a migration message, the snippet's other code is recorded at weight 0 with detail
  `failing snippet`: it was written for the version it fails on, so any weight points the wrong way.
  A snippet whose error is unrelated to versions (a `ZeroDivisionError`) keeps normal weight. The
  migration-message case is my reading of "names an exclusive symbol, keyword or value": a
  library-authored migration message is the strongest version error there is. The zero-weight
  signals stay in the signal list, so negative constraints (L5) still see the other-version calls.
  Step 6 re-run: all 73 clues infer their own side; the only score that moved is pyd-002's
  `old_error.txt`, whose new-side residue went from 1.5 to 0. Three new extractor tests.
- **Test hygiene.** Expected values are literals: pd-003 compares formatted dates and checks the
  dtype instead of building `pd.Timestamp` expectations; ctl-np-001 compares with `math.isclose`
  instead of `np.allclose`; np-001 passes a literal array instead of `2 * x`; pd-005 uses
  `math.isnan` and a literal mask. Exact exception types: pyd-001 expects `ValidationError` (was
  `ValueError`, which a hand-raised error would also satisfy); pyd-007 expects `TypeError` on V1
  and `ValidationError` on V2 (was the tuple `(TypeError, ValueError)`), chosen by
  `pydantic.VERSION`. No test used a bare `pytest.raises(Exception)`.
- **Portable answers.** pd-001 `df.apply(lambda column: column.map(...))` (unchanged); pd-002
  `pd.offsets.MonthEnd()` (unchanged); pd-003 now `read_csv(parse_dates=..., dayfirst=True)` (the
  old `to_datetime` after reading contradicted the query's "through read_csv itself"); pd-004 now
  `Timestamp.value` per element (was epoch subtraction); pd-005 `ffill()`; np-001 the hand-written
  trapezoid sum (unchanged); np-002 now `np.unique(..., return_inverse=True, return_counts=True)`
  with `inverse.reshape(values.shape)`; np-003 `method="lower"`; pyd-002 keyword construction;
  pyd-003 now `plain` with `constr(strip_whitespace=True)` (was `none`); pyd-005 `dict(model)`;
  pyd-006 `constr(strip_whitespace=True, min_length=1)` (unchanged). pyd-001, pyd-004 and pyd-007
  have no plain portable answer, but each has a version-guarded one, so they are now `guard_only`
  (were `none`) with a guarded `ref_portable.py`: `pydantic.VERSION` for pyd-001 and pyd-007,
  `try: from pydantic import model_validator except ImportError` for pyd-004. Every concept with
  both references admits such a guard, so `none` would have understated what a model can write.
  Step 5 passes for all twelve two-directional concepts and both one-directional ones.
- **Plausible wrong answers.** Every concept and control now has `wrong.py`, one natural mistake
  that must fail in both environments; the loader requires it and `bench validate` checks it as
  step 10 (fail by test failure or exception, not timeout or infra error, and repeated under step
  3). The mistakes: a list instead of an array (ctl-np-001), a left Riemann sum (np-001), counts by
  value instead of by unique index (np-002), `np.median` (np-003), `df.apply` on whole columns
  (pd-001), month starts `"MS"` (pd-002), no `dayfirst` (pd-003), `Timestamp.timestamp()` seconds
  (pd-004), one-step `fillna(df.shift())` (pd-005), a length constraint instead of the pattern
  (pyd-001), `parse_obj` on an ORM object (pyd-002), the wrong config key `strip_whitespace`
  (pyd-003), a plain `ValueError` raised outside the model (pyd-004), `.json()` (pyd-005),
  `constr(min_length=1)` without stripping (pyd-006), `allow_mutation=False` without
  `validate_assignment` (pyd-007).
- **Re-validated.** 16/16 pass `bench validate` on this machine, steps 1 to 10.

## 2026-10-19 Test split and thresholds frozen before any model run (GPU session step 2)

- **Test split.** The 48 test concepts are listed in `docs/plans/composition.md`, "Frozen test
  split": id, library, class, change type and the change each uses (pandas 15, NumPy 10, pydantic
  23). They follow the picks the user settled on 2026-10-18, minus the dev seeds, plus the four
  substitutions already forced before authoring (SecretStr and SecretBytes keyword concepts would
  be contrived; `Field(min_items)` and `Field(max_items)` have no new-only gold). The four
  replacements, `constr(regex→pattern)`, `__root__→RootModel`, `validate_arguments→validate_call`
  and `parse_obj_as→TypeAdapter`, come from the composition plan's own candidate list and the
  handoff's candidate pairs; they are not probed yet. From now on a test concept changes only when
  validation forces it, logged here with the failing step, and the replacement comes from the
  frozen reserve list of the same library and class. Parameter-level share: 27 of 63 (42.9%)
  across the benchmark, 19 of 48 (39.6%) on the test split alone.
- **Thresholds.** Frozen at the handoff defaults, `tau_commit` 3.0 and `tau_noise` 1.5, on the 28
  dev clue instances (`varag bench thresholds`, new). Every `tau_commit` up to 3.0 commits all 28
  with no wrong commit; 3.5 and 4.0 leave 2 uncommitted (the single resolved exclusive symbol of
  pd-002's and pd-003's new code clues, weight 3), 4.5 leaves 6, 5.0 leaves 7. No dev clue puts
  any weight on the other side, so dev does not identify `tau_noise`; it keeps the default. 3.0 is
  the most conservative full-coverage point. `configs/experiment.yaml` carries `frozen_on` and
  `frozen_split`, and `varag run --split test|all` now refuses while `frozen_on` is missing. A unit
  test pins the frozen values.

## 2026-10-19 `varag preflight`; vLLM 0.31.0 in its own venv (GPU session step 3)

- **vLLM.** None was installed. vLLM 0.32.0 was released the day before (2026-10-18), so the pin is
  0.31.0 (2026-10-05), installed with `uv pip install vllm==0.31.0 --torch-backend=auto` into
  `~/.venvs/vllm-0.31.0` (Python 3.12), outside the repository and the orchestrator's environment.
  It brings torch 2.13.0+cu132 (CUDA 13.2, above the 12.8 Blackwell needs) with sm_120 kernels; the
  Windows driver is 617.14 and the host CUDA toolkit is 12.8 (unused by vLLM). The venv path, the
  version and the install command live in `configs/models.yaml` under `serving`.
- **Preflight.** `varag preflight` checks: GPU visible from WSL (`nvidia-smi`); the vLLM venv's
  torch sees it, CUDA at least 12.8, kernels for the GPU's compute capability; the pinned vLLM
  version; free VRAM against each model's safetensors size plus 1.5 GiB (a warning, since the
  models are served one at a time); at least 20 GB free at `HF_HOME`; the Hugging Face API serves
  both pinned revisions with a `config.json` (no token needed: neither repo is gated); uv 0.11 or
  newer; `env verify` clean; the manifest matches the committed one on lock hashes, library
  versions and distribution lists (interpreter paths, platform, CPython patch and timestamps may
  differ); the harness applies `RLIMIT_AS` and `unshare -rn`. First run: 12/12 without failure,
  and no drift against the laptop's manifest at bbbe9e2 either.
- **VRAM is the open risk.** Windows desktop apps hold 6.5 to 6.7 GiB of the 16 GiB (browsers,
  Discord, VS Code, Parsec, the NVIDIA overlay; WSL cannot see or stop them), leaving about 9 GiB.
  The 7B (5.6 GB of weights) fits; the 14B (10.0 GB) does not until some of that is freed.

## 2026-10-19 Serving the 7B with vLLM; serve check reads the effective parameters (GPU session step 4)

- **Command.** `varag serve start --model primary` (new, with `serve stop` and `serve command`)
  builds the command from `configs/models.yaml`: `vllm serve Qwen/Qwen2.5-Coder-7B-Instruct-AWQ
  --revision 8e8ed24… --tokenizer-revision 8e8ed24… --served-model-name primary --host localhost
  --port 8000 --seed 1234 --enable-log-requests --generation-config vllm --max-model-len 8192
  --quantization awq --gpu-memory-utilization 0.5 --max-num-seqs 4`. `--tokenizer-revision` pins
  the tokenizer and chat template to the same commit (vLLM otherwise reads them from the default
  branch). vLLM 0.31 maps `--quantization awq` onto its AWQ Marlin kernel on this GPU and picks
  FlashAttention 2. First start, including the 5.6 GB download, took about 4 minutes.
- **Memory.** `--gpu-memory-utilization 0.5` (8 GiB) is needed because Windows apps hold about
  6.6 GiB: vLLM refuses to start when less than the requested fraction is free, and the default 0.9
  asks for 14.7 GiB. `--max-num-seqs 4` because the client sends one request at a time. Context
  stays at 8192.
- **Effective parameters.** `--enable-log-requests` makes vLLM log each request's resolved
  `SamplingParams`; `serve check` now reads the last one from `runs/_serve/<model>.log`. For the 7B:
  repetition_penalty 1.0, temperature 0.0, top_p 1.0, top_k 0, seed 1234, presence and frequency
  penalties 0.0, max_tokens 1024. With `--generation-config vllm` the server reports no generation
  config of the model's.
- **Bug fixed: the rendered prompt was never readable from vLLM.** The client posted to
  `/v1/tokenize`, which vLLM does not serve (404), so `serve check` reported "no tokenize endpoint"
  as if the server were llama.cpp. vLLM serves `/tokenize` and `/detokenize` at the root; the client
  now tries the root first. The rendered prompt starts `<|im_start|>system\nYou are a Python coding
  assistant.` (ours), not Qwen's default system prompt.
- **run.json now logs the serving record** the handoff asks for once per run (L1): server and
  version, model, revision, serve args, sampling profile, GPU and driver, concurrency 1, call and
  cache-hit counts, and the first instance's prompt after chat templating. It was missing.
- **Run speed.** `varag run` executes answers in a thread pool (`execution.workers: 8` in
  `configs/experiment.yaml`) while generation stays strictly sequential, one request in flight,
  in instance order; rows are written in instance order. Outputs cannot change, only wall time.
  Because `preexec_fn` is unsafe once threads run, the 2 GB `RLIMIT_AS` is now applied by
  util-linux `prlimit --as` as a command prefix (after `unshare -rn`); `preexec_fn` remains the
  fallback where `prlimit` is missing. The memory-cap and no-network harness tests pass.
- **For step 6.** `varag run` gained `--instances FILE` (the noise subset), `--fresh-cache` (a
  run-private cache, so the repeat reaches the server and the shared cache is untouched) and the
  `leak_audit` user arm. The L1 test's other arm is the backend `primary_genconfig`: the same
  weights served with `--generation-config auto`, and requests that send only `max_tokens` and
  `seed`, so the repository's temperature 0.7, top_p 0.8, top_k 20 and repetition penalty 1.1
  apply. The seed keeps that arm reproducible.

## 2026-10-19 Serving the 14B: memory, and why the compiled path needed 0.86 (GPU session step 4)

- **The ladder, as tried.** With Windows apps holding 5.3 to 6.7 GiB, about 10.3 GiB was free;
  the 14B needs 9.38 GiB of weights (as loaded) plus 1.5 GiB of KV for one 8192-token sequence.
  `--gpu-memory-utilization 0.62 --max-num-seqs 1` loaded the weights and ran out of memory while
  profiling. Lowering either knob cannot help when the weights alone fill the budget. Weight
  offload does not rescue it here: vLLM reports "Pinned memory is not available on this platform"
  under WSL2 and falls back to device memory for UVA buffers, so `--cpu-offload-gb` would offload
  nothing; the prefetch backend would stream about 3 GiB of layers per token from pageable memory,
  roughly hours per run. The context was not shortened.
- **What worked.** After the GPU-heavy Windows apps were closed (other processes at about 1.4 GiB),
  `--gpu-memory-utilization 0.78` still failed in the compiled profiling pass with an asynchronous
  `CUDA error: out of memory`, although torch could allocate 16 GiB under WSL (WDDM spills into
  shared memory). `--enforce-eager` at 0.78 started (2.61 GiB KV); compiled at 0.78 with
  `--max-num-batched-tokens 1024` got past profiling but left 1.31 GiB of KV (vLLM proposed a
  7168-token context, refused). The choice: compiled, CUDA graphs, default prefill budget,
  `--gpu-memory-utilization 0.86 --max-num-seqs 4`, KV 3.84 GiB (20,976 tokens). It differs from
  the 7B's settings only in the memory fraction, which has no numerical effect, so both models run
  the same kernels and modes. It needs other processes to hold at most about 2.2 GiB of the GPU;
  `varag preflight` warns when they hold more.
- **Serve check.** Effective repetition_penalty 1.0, temperature 0.0, top_p 1.0, top_k 0, seed
  1234; the rendered prompt starts with our system prompt; two identical requests matched.
- **Smoke and gpu-day serve one model at a time.** The full `varag smoke` now starts a vLLM backend
  that is not already up, runs its serve check (printed), both arms and the reports, and stops it.
  `varag gpu-day` does the same per model, plus the serving-noise check and the audit sample.
- **run.json records the git commit, a `git_dirty` flag and the config hash as of the start.**
  Before, both were read at the end, from whatever the working tree then held. The first smoke on
  this machine (21/22 steps; only the 14B start failed, before the apps were closed) ran from an
  uncommitted tree, so its runs were deleted and the reported runs repeat from a clean commit.

## 2026-10-19 Dev checks: L1, serving noise, leak audit (GPU session step 6)

Dev runs: the smoke's (`runs/20261019T111727Z-primary-2266f7e7` knows, `…111858Z-primary-ac41cde3`
unsure, `…112205Z-vllm_large-7462f484` knows, `…113804Z-vllm_large-412461b7` unsure), every method
and ablation at serving concurrency 1. The extra runs come from `scripts/gpu_session_step6.sh`.

- **L1 test** (`varag compare l1`). `plain_rag` on the 83 dev instances with the 7B: our pinned
  sampling 42.2%, the repository's generation config 37.3% (−4.8 points; rates include the
  control). With `--generation-config auto` and only `max_tokens` and `seed` sent, the server
  applied repetition_penalty 1.1, temperature 0.7, top_p 0.8, top_k 20 (read from its request
  log). 69 of 83 responses differ; 10 instances went from pass to fail and 6 from fail to pass; the
  model asked 22 questions instead of 14. On 16 concepts this is within noise (see below), but its
  direction matches the handoff's warning and every request keeps sending the pinned block.
- **Serving noise** (`varag compare noise`, the committed 20-instance subset, all 11 methods, 220
  answers, `--fresh-cache`). Within one server session: 7B 2/220 responses changed (0.9%), no
  outcome changed; 14B 0/220. Across server restarts (a fresh run against the cached dev run, which
  an earlier server process generated): 7B 23/220 responses (10.5%) and 14/220 outcomes (6.4%);
  14B 24/220 responses (10.9%) and 5/220 outcomes (2.3%). So method differences of a few points on
  dev are noise, and most of the noise comes from restarting the server. The likely cause is that
  vLLM 0.31 picks kernels at start-up by timing them under torch.compile
  (`benchmark_combo_kernel: True` in the logged compilation config), with prefix caching as a
  second candidate; neither was changed, since that would alter the serving configuration the dev
  runs used. For test runs: generate each model's runs within one server session (gpu-day does) and
  compare methods within a run, never across restarts.
- **Leak audit** (`varag compare leak`, arm `leak_audit`: every question is replaced by an
  irrelevant one, so the user only ever says "I'm not sure what you're asking."). The handoff's
  "no-question rate" is read as the rate the same method reaches when its question brings back no
  version: the `unsure` arm. Result: PASS for both models. 7B: every asking method's leak-arm rate
  equals its unsure rate (excess 0.0); 14B: equal, except `no_retrieval` 1.2 points lower.
  `va_rag_no_ask`, the policy without any question, is printed beside them: 43.4% (7B) and 62.7%
  (14B), below `va_rag`'s leak-arm 47.0% and 69.9%. That gap is the "both" fallback (two labelled
  answers when the reply names no version), not a leak, and it is why the comparison is with
  `unsure` and not with `va_rag_no_ask`. This reading is mine; flagged for review.
- **Runtimes.** Fresh dev runs (913 answers): 7B 342 s, 14B 932 s. One 14B noise run took 1,305 s
  for 220 answers against 293 s for its repeat, consistent with the Windows apps reopening and
  WDDM spilling GPU memory into system memory; keep them closed while the 14B runs.

Findings for the prompt review (not acted on: the prompts and the output protocol are frozen
pending the user's review):

1. **Missing entry point.** In pydantic tasks the models often write the model class but not the
   function the task names (`make_range`, `make_tag`, …), so the test cannot import it and the
   answer is `broken` in both environments. 7B: 225 of 913 answers with code in the knows run,
   20 to 24 per method, 60 to 70% of all `broken` outcomes; 14B: 117. This hides version effects on
   pydantic, where most of the benchmark sits. The system prompt already says "defines the function
   named in the task".
2. **A second question after "I'm not sure."** In the unsure arm the 7B answers the user's "I'm not
   sure." with another question (`mind_version` 80 of 83 `no_code`; `always_ask` and `plain_rag` 14
   each). The handoff's protocol says the model must produce code after the reply, but nothing in
   the conversation tells it so, and a second question scores as `no_code`.
3. **Over-asking.** The 7B's `mind_version` asks on 81 of 83 instances, clue and stated ones
   included (over-ask 96.4%); the 14B asks almost never (`mind_version` 2, `plain_rag` 0).

## 2026-10-19 GPU_HANDOFF filled; `varag gpu-day` (GPU session step 7)

`docs/GPU_HANDOFF.md` now holds the exact serve commands, versions, memory settings, measured
runtimes, the steps with acceptance checks, and the dev results. `varag gpu-day` repeats the GPU
work in one command: preflight; per model, serve start, serve check (stops on a problem), a
serving-noise pair on the committed subset (`plain_rag` and `va_rag`), one run per user arm with
reports, serve stop; the 50-output audit sample; a summary in `runs/gpu-day-<stamp>.json`. It
prints the plan and a runtime estimate first (from the newest uncached full run, else
`seconds_per_answer` in `configs/models.yaml`), refuses a split with no concepts or with
unvalidated ones, and refuses the test split while the thresholds are not frozen; `--resume` skips
finished (model, arm) runs with the same commit, configs and tasks. Verified on dev: 18 minutes,
every figure identical to the smoke's runs. The test split is refused today ("no concepts").
