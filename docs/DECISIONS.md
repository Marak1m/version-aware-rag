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

## 2026-10-08 Rule-set corrections after the first audit

The environments contradicted five hand-transcribed rules, and the rules were changed: pandas
`Series.dt.week`, `Series.dt.weekofyear` (still exposed by the combined accessor for period dtypes in
3.0.6) and `resample(convention)` (still accepted in 3.0.6) were dropped; pydantic
`PaymentCardNumber` is deprecated-but-present in 2.13.4, and `Color` was never a top-level name.

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
importing it needs jinja2, which the environments do not include; the root is logged as
unavailable on both sides and left out.

## 2026-10-08 Keyword binding against callees that accept **kwargs

The handoff has the guard abstain "on calls that forward **kwargs", which is read as call sites
that splat a dict. A keyword explicitly declared in exactly one version's signature is recorded
as a usage of that side even when the other side's callee accepts **kwargs (pydantic.Field takes
**extra on both sides, and `Field(regex=...)` is the canonical parameter rename). Such a usage is
flagged `uncertain`: version inference counts it, and the blend guard (M6) abstains on it by
default, because the call might still run on the other side.
