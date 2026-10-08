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
