# NumPy test concepts and controls: authoring session, 2026-10-19

Worktree `/home/vansh/code/varag-author-numpy`, branch `author-numpy`. No model calls were made. The
binding list is `docs/plans/composition.md`, "Frozen test split", NumPy rows np-004 to np-013.

**Outcome:** 8 of the 10 frozen NumPy test ids are validated, with 2 substitutions from the
reserve list. All 3 test controls are validated. np-005 and np-006 are not authored, because the
framework blocks them (see "Blocked"). There is no removal reserve, so their places stay empty.
NumPy's test split now has 1 removal and 7 one_directional concepts, not 3 and 7.

## Validated concepts

All are `split: test`. Clue overlaps are all `off_target`. A one_directional concept carries
new-side clues only, like np-003.

### np-004: removal, param_rename, `np.reshape(newshape=)` → `np.reshape(shape=)`
- Query: `to_grid(values, rows, cols)` fills a 2-D array row by row. It must use `np.reshape` and
  pass the target shape as a keyword argument, so a size mismatch raises NumPy's own error.
- Refs: `ref_old` uses `np.reshape(a, newshape=(rows, cols))`; `ref_new` uses `np.reshape(a, shape=(rows, cols))`.
- portable_alternative: **guard_only**. The query asks for the shape keyword, and the keyword's
  name is the version-specific part. The positional call `np.reshape(a, (r, c))` passes both
  environments but ignores the query, so it does not count as plain. `ref_portable` tries `shape=`
  and falls back to `newshape=` on `TypeError`.
- wrong.py: `np.resize`, which repeats or truncates on a size mismatch instead of raising
  (`DID NOT RAISE ValueError` in both environments).
- Clues:
  - old: pin `numpy<2`; code using `np.NaN`, `np.msort`, `np.product`; error from
    `np.sort(stable=True)` run on old (`TypeError ... 'stable'`).
  - new: pin `numpy>=2`; code using `np.cumulative_sum`, `np.linalg.vector_norm`, `np.isdtype`;
    error from `np.corrcoef(bias=1)` run on new (`TypeError ... 'bias'`).
- Gold: `numpy.reshape(newshape)` (old_only) and `numpy.reshape(shape)` (new_only). Linked by the
  existing replacement rule.
- control_eligible: **true**.

### np-007: one_directional, symbol_removed, `np.NaN` → `np.nan`
- Query: `mask_negatives(values)` returns a new float array with the negatives replaced by NumPy's
  NaN constant, leaving the input unchanged.
- Refs: `ref_old` uses `np.NaN`; `ref_portable` uses `np.nan`.
- portable_alternative: plain, since `np.nan` exists in both versions.
- wrong.py: assigns NaN in place on the integer array that `np.asarray` returns. This raises
  `ValueError: cannot convert float NaN to integer`.
- Clues (new): pin `numpy>=2`; code using `np.cumulative_sum`, `np.matrix_transpose`, `np.isdtype`;
  error from `np.reshape(newshape=)` run on new.
- Gold: `numpy.NaN` (old_only) and `numpy.nan` (shared_same), linked by a replacement rule.
  control_eligible false.

### np-008: one_directional, symbol_removed, `np.float_` → `np.float64`
- Query: `as_doubles(values)` converts to double precision. It must pass NumPy's default float
  scalar type object as `dtype`, not a string or the builtin `float`.
- Refs: `ref_old` uses `dtype=np.float_`; `ref_portable` uses `dtype=np.float64`.
- portable_alternative: plain.
- wrong.py: `np.float32` (single precision).
- Clues (new): pin; code using `np.acos`, `np.pow`, `np.unique_counts`; error from
  `np.corrcoef(ddof=1)` run on new.
- Gold: `numpy.float_` (old_only) and `numpy.float64` (shared_changed), linked by a replacement
  rule. control_eligible false.

### np-009: one_directional, symbol_rename, `np.cumproduct` → `np.cumprod`
- Query: `growth_path(factors)` returns the running product, computed with NumPy's
  cumulative-product function.
- Refs: `ref_old` uses `np.cumproduct`, which raises a DeprecationWarning on old (recorded at
  step 9). `ref_portable` uses `np.cumprod`.
- portable_alternative: plain.
- wrong.py: an exclusive scan that starts at 1 (an off-by-one).
- Clues (new): pin; code using `np.unique_values`, `np.linalg.vector_norm`; error from
  `np.nanpercentile(interpolation=)` run on new.
- Gold is linked by a replacement rule. control_eligible false.

### np-010: one_directional, symbol_removed, `np.alltrue` → `np.all`
- Query: `rows_all_positive(matrix)` returns one bool per row, using NumPy's all-elements-true
  function with the axis argument.
- Refs: `ref_old` uses `np.alltrue(..., axis=1)`, which raises a DeprecationWarning on old.
  `ref_portable` uses `np.all(..., axis=1)`.
- portable_alternative: plain.
- wrong.py: `np.any` instead of `np.all`.
- Clues (new): pin; code using `np.concat`, `np.unstack`, `np.cumulative_prod`; error from
  `np.quantile(interpolation=)` run on new.
- Gold is linked by a replacement rule. control_eligible false.

### np-011 (substitute): one_directional, symbol_removed, `np.asfarray` → `np.asarray(dtype=float)`
- Why it was substituted: the frozen pick, `np.row_stack` → `np.vstack`, **fails step 2**. Its
  `ref_old/new` run is `pass`: on 2.4.6 `row_stack` only raises a DeprecationWarning, and
  warnings are errors only for deprecation-class concepts. A pair that only warns cannot be
  one_directional, so it was replaced by the first NumPy one_directional reserve. The row_stack
  draft and its validation.json are kept in `logs/session/authoring-numpy-drafts/np-011-row-stack/`.
- Query: `as_float(values)` converts numbers, possibly integers, to a float array, using NumPy's
  convenience function that returns its input as an array of float type.
- Refs: `ref_old` uses `np.asfarray(values)`; `ref_portable` uses `np.asarray(values, dtype=float)`.
- portable_alternative: plain.
- wrong.py: `np.asarray(values)` with no dtype, which leaves the integers as integers.
- Clues (new): pin; code using `np.linalg.matrix_norm`, `np.unique_all`, `np.isdtype`; error from
  `np.quantile(interpolation=)` run on new.
- Gold: `numpy.asfarray` (old_only) and `numpy.asarray` (shared_changed), linked by a replacement
  rule. control_eligible false.

### np-012: one_directional, param_value, `np.take(mode="c")` → `mode="clip"`
- Query: `clamped_lookup(table, indices)` uses `np.take` with its clipping mode. Out-of-range
  positions are clamped at both ends.
- Refs: `ref_old` uses `mode="c"`, which raises a DeprecationWarning on old and ValueError on new.
  `ref_portable` uses `mode="clip"`.
- portable_alternative: plain.
- wrong.py: clamps only the upper bound with `np.minimum`, so `-4` raises IndexError.
- Clues (new): pin; code using `np.vecdot`, `np.astype`, `np.bitwise_left_shift`; error from
  `np.corrcoef(bias=0)` run on new.
- Gold: `numpy.take(mode="c")` (old_only, by confirmed value rule) and `numpy.take(mode="clip")`
  (shared_same). Linked by the existing value rule (c→clip). control_eligible false.

### np-013 (substitute): one_directional, symbol_removed, `np.find_common_type` → `np.promote_types`
- Why it was substituted: the frozen pick, NEP 50 (`uint8 + 300` → `astype(np.uint16) + 300`),
  **fails step 4**: "ref_old uses no old_only or deprecated_in_new symbol; gold.old numpy.array
  is in shared_unknown". Steps 1, 2, 5, 6, 7 and 10 passed. The cause is structural. Step 4 is
  skipped only for `exclusivity: behavior`. A one_directional concept always gets the static
  check, so a one_directional concept with `change_type: behavior` can never pass it. The next
  reserve after asfarray (already used for np-011) is find_common_type. The two later reserves,
  string→bool cast and `float(array)`, are behaviour changes and would fail the same way. The
  NEP 50 draft is kept in `logs/session/authoring-numpy-drafts/np-013-nep50/`.
- Query: `common_dtype(dtypes)` returns the smallest dtype all inputs safely cast to, as a
  `np.dtype`, using NumPy's type-promotion helpers.
- Refs: `ref_old` uses `np.find_common_type(dtypes, [])`, which raises a DeprecationWarning on old.
  `ref_portable` folds `np.promote_types` over the list, starting from `np.dtype(dtypes[0])`.
- portable_alternative: plain.
- Test inputs avoid cases where pairwise promotion and `result_type` disagree, such as
  uint16+int16+float16.
- wrong.py: picks the input dtype with the largest itemsize (int8+uint8 gives int8).
- Clues (new): pin; code using `np.unique_counts`, `np.argsort(stable=True)`; error from
  `np.reshape(newshape=)` run on new.
- Gold: `numpy.find_common_type` (old_only) and `numpy.promote_types` (shared_changed), linked by
  a replacement rule. control_eligible false.

## Validated controls (kind: no_conflict, split: test)

Each control's gold is `shared_same`. Each one passes both environments with no warnings, and its
retrieved set has no conflict. None of them involves NEP 50 promotion, copy semantics, string
dtypes, or any probed or value-rule change.

| Id | Query | Gold | ref_portable | wrong.py |
| --- | --- | --- | --- | --- |
| ctl-np-003 | `moving_sum(values, window)`: sums over full windows only | `numpy.convolve` | `np.convolve(a, np.ones(window, dtype=int), mode="valid")` | `mode="same"` (wrong length) |
| ctl-np-004 | `resample_linear(x_new, x, y)`: piecewise-linear values, ends held outside the range | `numpy.interp` | `np.interp` on float arrays | a straight-line `np.polyfit` fit |
| ctl-np-005 | `label_counts(labels, n_labels)`: counts per label, with zeros | `numpy.bincount` | `np.bincount(..., minlength=n_labels)` | `np.unique(return_counts=True)`, which drops labels that never occur |

## Blocked: not authored, no reserve

There is no NumPy removal reserve, so neither place is filled. The drafts are complete (refs,
tests, wrong.py, clues and the error clues np-005 had) and are kept under
`logs/session/authoring-numpy-drafts/` together with their validation.json. They are outside
`data/tasks`, so no unvalidated test concept sits in the task tree.

### np-005: `np.array(copy=False)` → `np.array(copy=None)`, removal, param_value
Steps 1, 2, 3, 5, 6 and 10 pass. The concept is two-directional at run time:
- `copy=False` on a list raises "Unable to avoid copy" on 2.4.6.
- `copy=None` raises "NoneType copy mode not allowed" on 1.26.4.

The framework blocks it in two places.
- **Step 4.** `varag.pipeline.signals._literal` matches only `str` and `None` literals against
  value rules, so the value `copy=False` is never seen as a value usage. Even with a confirmed
  value rule for `numpy.array copy False side old`, `ref_old` "uses no old_only or
  deprecated_in_new symbol".
  - Without that rule, `gold_bucket` also puts `numpy.array(copy=False)` in shared_same.
  - I added that rule, probed it with the existing `snippets.json` template
    `np.array([1, 2, 3], copy=VALUE)`, and got old ok, new error, confirmed.
  - I then **reverted it**, because nothing can use it while bool literals are not matched.
  - Record for later, if wanted: `{"callable": "numpy.array", "parameter": "copy", "value":
    false, "side": "old", "replacement": null, "version": "2.0.0", "url":
    "https://numpy.org/doc/stable/release/2.0.0-notes.html", "quote": "The meaning of False
    changed as it now raises an exception if a copy is needed."}`.
  - A `replacement` of null is also ambiguous: `rule_links` reads null as "no replacement", while
    `linked_pairs` reads it as the value None.
- **Step 7.** "no 1.26.4 chunk for gold numpy.array(copy=False)". `numpy.array` is
  `shared_unknown`, because its 1.26.4 signature cannot be introspected, so the 1.26.4 corpus has
  no `numpy.array(copy)` keyword chunk. With no old chunk the retrieved set is not a conflict
  either: "retrieved set conflict is False, expected True".

### np-006: `loadtxt` converters receive bytes → str, removal, default_change
Steps 1, 2, 3, 5, 6 and 10 pass. `ref_old` uses a bytes converter and `ref_new` a str converter;
each raises ValueError on the other side. `ref_portable`, with `encoding="utf-8"` and a str
converter, passes both. The framework blocks it in two places.
- **Step 4.** "ref_old uses no old_only or deprecated_in_new symbol; ref_new uses no new_only
  symbol; gold numpy.loadtxt is in shared_changed". The two references call the same API and
  differ only in what the converter does with its argument. For a removal or default_change
  concept the static check demands exclusive symbols on both sides, and none exist here. I found
  no honest value rule either: `encoding="bytes"` and `encoding=None` are accepted by both
  versions (checked in both environments).
- **Step 7.** "gold pair not linked by data/rules". This could be fixed with a `behaviour.json`
  entry for probe `np-v03-loadtxt-str`, but step 4 would still fail, so I did not add one.

Both need a framework decision: skip or relax step 4 for value-literal and default-change
concepts, and index the old `numpy.array(copy)` keyword. That falls under `src/`, which this
session does not edit.

## Rules added

None committed. The one value rule added during the session (`numpy.array copy=False`, above)
was reverted, so `data/rules/` is unchanged.

## Notes

- Error clues were all made with `varag bench make-error-clue`. I preferred keyword `TypeError`
  snippets, because their tracebacks have no frame inside the library.
  - An AttributeError from `numpy.__getattr__` includes a frame path such as
    `.../envs/numpy_new/.venv/...`. That path puts the words "numpy_new" or "numpy_old" in front
    of the model.
  - Existing clues pd-003 and pyd-003 carry such paths. No error clue authored here does.
- NumPy 2.4.6's "`np.X` was removed in the NumPy 2.0 release" messages are not recognised by the
  extractor, because `configs/migration_messages.yaml` has `numpy: []`. `make-error-clue` refuses
  them, for example for `np.sometrue`. So the error clues use names or keywords that 2.4.6
  reports as missing: `has no attribute`, or `unexpected keyword argument`.
- Class-cap warning: in this worktree only the NumPy test concepts exist, so the benchmark-wide
  one_directional count is 9 of 23 and `CAP EXCEEDED` is printed. With the other libraries'
  frozen test concepts it is 16 of 61 (26%), under the one-third cap.
- `uv run pytest -q`: 328 passed, 3 failed. All three depend on the live task set; none
  concerns a concept's content.
  - `tests/test_sweep.py::test_test_split_is_refused_while_it_has_no_concepts` asserts that the
    test split is empty. It fails as soon as any test concept exists and needs updating by
    whoever owns `tests/`.
  - `tests/test_bench.py::test_class_caps` and
    `tests/test_thresholds.py::test_test_split_run_refuses_unfrozen_thresholds` fail on the
    benchmark-wide cap described above. They should pass once the pandas and pydantic test
    concepts are merged: 17 of 62 and 16 of 61 one_directional.

## Final validate summary

`uv run varag bench validate np-004 np-007 np-008 np-009 np-010 np-011 np-012 np-013 ctl-np-003 ctl-np-004 ctl-np-005`:
every id passes steps 1 to 10 (step 2 is skipped for controls). Summary lines:

```
numpy: concepts by exclusivity {'behavior': 1, 'one_directional': 8, 'removal': 2}
pandas: concepts by exclusivity {'behavior': 1, 'one_directional': 1, 'removal': 3}
pydantic: concepts by exclusivity {'deprecation': 3, 'removal': 4}
CAP EXCEEDED benchmark: 9 of 23 concepts are one_directional; the cap is 1/3; `varag run` refuses until it is met
11/11 concept(s) validated
```
