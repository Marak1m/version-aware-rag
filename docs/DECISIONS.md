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
