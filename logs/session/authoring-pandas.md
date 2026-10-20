# Authoring session: pandas test concepts and controls (2026-10-19)

Worktree `/home/vansh/code/varag-author-pandas`, branch `author-pandas`. No model calls were made.
Every concept below was validated with `uv run varag bench validate` (steps 1 to 10) on this
worktree's environments (pandas 1.5.3 and 3.0.6). Error clues were produced only with
`varag bench make-error-clue`; the failing snippets were written to a scratch file first.

`control_eligible: true` on pd-006, pd-007, pd-009, pd-011; `false` on every other pandas test concept.

## Concepts

### pd-006 (removal, param_value): `DataFrame.resample("Q")` to `"QE"`
- Query: `quarterly_totals(df)`, column sums per calendar quarter labelled by the quarter's last
  day, empty quarters included, with `resample` and a quarter-end alias.
- Refs: old `df.resample("Q").sum()`; new `df.resample("QE").sum()`.
- Portable: `plain`, `df.resample(pd.offsets.QuarterEnd()).sum()` (the offset object is accepted by both).
- wrong.py: `"QS"`, quarter-start labels.
- Gold: `pandas.DataFrame.resample(rule="Q")` / `(rule="QE")`, linked by the confirmed value rule.
- Clues: old pin, old code (`DataFrame.append`, `iteritems`), old error (`DataFrame.map` missing
  in the old env); new pin, new code (`read_csv(date_format)`, `DataFrame.map`), new error
  (`DataFrame.append` missing in the new env). All off_target.

### pd-007 (removal, param_value): mixed ISO strings, `to_datetime(format="ISO8601")`
- Query: `parse_stamps(values)`, a list of ISO 8601 strings, some dates only and some with a
  time, to a datetime64 Series, in one `pd.to_datetime` call without a strftime pattern.
- Refs: old `pd.to_datetime(values, infer_datetime_format=True)` (1.5.3 parses each ISO string;
  3.0.6 rejects the keyword); new `pd.to_datetime(values, format="ISO8601")` (1.5.3 rejects the value).
  The bare old form `pd.to_datetime(values)` also fails in 3.0.6 (one format inferred from the
  first value), but it uses no old-only symbol, so step 4 needs the keyword form.
- Portable: `plain`, `pd.to_datetime([pd.Timestamp(v) for v in values])` wrapped in a Series.
- wrong.py: returns `pd.to_datetime(...)` of the list directly, a DatetimeIndex rather than a Series.
  (A first draft with an explicit ISO-like strftime pattern passed in 1.5.3, whose ISO fast
  path ignores the pattern, so it was replaced.)
- Gold: `pandas.to_datetime(infer_datetime_format)` / `pandas.to_datetime(format="ISO8601")`.
- Rule added (step 7 found the pair unlinked): `data/rules/pandas/removals.json`, entry
  `pandas.to_datetime(infer_datetime_format)` now has `replacement: pandas.to_datetime(format="ISO8601")`,
  with `quote` ("Deprecated argument infer_datetime_format in to_datetime() and read_csv(), as a
  strict version of it is now the default (GH 48621)"; "... or, if your formats are all ISO8601
  (but possibly not identically-formatted)" with the example `pd.to_datetime(ser, format='ISO8601')`)
  and `url` https://pandas.pydata.org/docs/whatsnew/v2.0.0.html, plus a dated line in its
  `corrections`. `replacements.json` was regenerated with `varag.inventory.rules.write_replacements`;
  the only change is this one entry.
- Clues: old pin, old code (`read_csv(squeeze)`, `iteritems`, `mad`), old error
  (`read_csv(date_format)` rejected in the old env); new pin, new code (`read_csv(dtype_backend)`,
  `DataFrame.map`), new error (`Series.iteritems` missing in the new env).

### pd-008 (removal, param_value): SUBSTITUTED, now `date_range(freq="A-JUN")` to `"YE-JUN"`
- Frozen change `Series.astype("timedelta64[D]")` to a `timedelta64[s]` result failed validation
  and was replaced by the first removal reserve, the fiscal year end.
- Failing attempt: `whole_days(td)`, whole days as floats by `astype` to a day-unit timedelta.
  ref_old `td.astype("timedelta64[D]")`, ref_new `td.astype("timedelta64[s]").dt.days`.
  Steps 1 to 3 passed; **step 4 failed**: "ref_old uses no old_only or deprecated_in_new symbol;
  ref_new uses no new_only symbol; gold.old ... is in shared_same; gold.new ... is in shared_same";
  step 5 and 7 also failed. Reason: both dtype strings are accepted by both versions (1.5.3 turns
  `timedelta64[s]` into float seconds instead of raising), so no confirmed value rule can make
  either side exclusive, and a task that asks for a `timedelta64[s]` dtype has no 1.5.3 answer
  (1.5.3 holds only ns timedeltas). The natural new answer (`td.dt.days`) is portable, so the
  change is one-directional as a concept, as the composition plan already suspected. The failing
  validation record is kept at the session scratchpad
  (`pd008_timedelta_validation.json`), not in the repository.
- Replacement query: `fiscal_year_ends(start, n)`, the `n` year-end dates of a fiscal year
  closing on 30 June, with `date_range` and an annual year-end alias anchored on June.
- Refs: old `freq="A-JUN"` (1.5.3 rejects `Y-JUN` and `YE-JUN`); new `freq="YE-JUN"` (3.0.6
  rejects `A-JUN` and `Y-JUN`).
- Portable: `plain`, `pd.offsets.YearEnd(month=6)`.
- wrong.py: `pd.offsets.YearEnd()`, the anchor forgotten (December ends).
- Gold: `pandas.date_range(freq="A")` / `pandas.date_range(freq="YE")`; the gold names the alias
  family because `gold_bucket` matches the rule value exactly, while the references use the
  anchored forms, which the static step matches through `anchored` rules. Linked by the value rule
  `A` to `YE`.
- Clues: old pin, old code (`DataFrame.append`, `iteritems`), old error (`read_csv(dtype_backend)`
  rejected); new pin, new code (`read_csv(date_format)`, `DataFrame.map`), new error
  (`read_csv(squeeze)` rejected). `control_eligible: false`.

### pd-009 (behavior): `value_counts().reset_index()` column names
- Query: `tally(s)`, a two-column frame `value`, `n`, most frequent first, from `value_counts()`,
  `reset_index()` and a rename of the produced columns.
- Refs: old renames `{"index": "value", s.name: "n"}`; new renames `{s.name: "value", "count": "n"}`.
- Portable: `plain`, `s.value_counts().rename_axis("value").reset_index(name="n")`.
- wrong.py: `pd.DataFrame({"value": s.unique(), "n": s.value_counts().values})`, appearance order
  paired with frequency order.
- Gold: `pandas.Series.value_counts` on both sides, linked by behaviour rule `pd-v04-value-counts-name`.
- Clues: old pin, old code (`is_monotonic`, `mad`, `iteritems`); new pin, new code
  (`read_csv(dtype_backend)`, `DataFrame.map`).

### pd-010 (behavior): `date_range` no longer defaults to ns, `unit="ns"`
- Query: `day_stamps_ns(start, n)`, epoch nanoseconds of `n` consecutive midnights via
  `pd.date_range` and an int64 cast.
- Refs: old `pd.date_range(...).astype("int64")` (3.0.6 gives microseconds); new
  `pd.date_range(..., unit="ns").astype("int64")` (1.5.3 rejects `unit`).
- Portable: `plain`, `(days - pd.Timestamp(0)) // pd.Timedelta(1, "ns")`.
- wrong.py: `int(ts.timestamp() * 1000)`, milliseconds.
- Gold: `pandas.date_range` / `pandas.date_range(unit)`, behaviour rule `pd-v07-date-range-unit`.
- Clues: old pin, old code (`read_csv(squeeze)`, `append`, `tshift`); new pin, new code
  (`dtype_backend`, `date_format`, `DataFrame.map`).

### pd-011 (behavior): time zones, pytz `.zone` to zoneinfo `.key`
- Query: `zone_of(index)`, the IANA name of a `tz_localize`d index's zone, taken from `index.tz`.
- Refs: old `index.tz.zone`; new `index.tz.key` (each attribute exists on one library's tz class only).
- Portable: `plain`, `str(index.tz)`.
- wrong.py: `index[0].tzname()`, the abbreviation (`CET`).
- Gold: `pandas.DatetimeIndex.tz_localize` on both sides, behaviour rule `pd-v08-tz-zoneinfo`.
- Clues: old pin, old code (`DatetimeIndex.weekofyear`, `is_monotonic`); new pin, new code
  (`date_format`, `DataFrame.map`). Pins carry an unrelated package (no `pytz` or `tzdata`, which
  would hint at the answer).

### pd-012 (behavior): `stack()` NaN handling, `future_stack=True`
- Query: `long_form(df)`, a (row, column) Series with every cell, missing cells kept as NaN, with
  `DataFrame.stack`.
- Refs: old `df.stack(dropna=False)` (3.0.6 raises ValueError on `dropna`); new
  `df.stack(future_stack=True)` (1.5.3 rejects the keyword).
- Portable: `plain`, `df.T.unstack()`. A first portable, `MultiIndex.from_product`, raised NumPy's
  `cumproduct`/`product` DeprecationWarning inside pandas 1.5.3 and failed step 5, so it was replaced.
- wrong.py: `df.unstack()`, column-major order. (`df.stack()` would pass on the new side, so it
  is not a valid step-10 mistake.)
- Gold: `pandas.DataFrame.stack` / `pandas.DataFrame.stack(future_stack)`, behaviour rule `pd-v09-future-stack`.
- Clues: old pin, old code (`append`, `swapaxes`); new pin, new code (`dtype_backend`, `DataFrame.map`).

### pd-013 (behavior): `groupby.apply` grouping columns, `include_groups=False`
- Query: `group_ranges(df, key)`, max minus min of every other column per group with
  `groupby(key).apply` and a function receiving each group's frame.
- Refs: old drops `key` inside the function (3.0.6 no longer passes it: KeyError); new
  `apply(..., include_groups=False)` (1.5.3 forwards the keyword to the function: TypeError).
- Portable: `plain`, select the other columns first: `df.groupby(key)[others].apply(...)`.
- wrong.py: `groupby(key).transform(...)`, one row per input row.
- Gold: `pandas.DataFrameGroupBy.apply` / `pandas.DataFrameGroupBy.apply(include_groups)`,
  behaviour rule `pd-v12-include-groups`.
- Step 9: ref_old raises NumPy's `find_common_type` DeprecationWarning inside pandas 1.5.3 (recorded).
- Clues: old pin, old code (`append`, `iteritems`, `mad`); new pin, new code (`dtype_backend`, `DataFrame.map`).

### pd-014 (one_directional, symbol_removed): `DataFrame.append` to `pd.concat`
- Query: `add_row(df, row)`, append a dict row, renumber the index, leave `df` unchanged.
- Refs: old `df.append(row, ignore_index=True)`; portable `pd.concat([df, pd.DataFrame([row])], ignore_index=True)`.
- wrong.py: `df.loc[len(df)] = row` (mutates the input, keeps the old labels).
- Gold: `pandas.DataFrame.append` / `pandas.concat`, replacement rule.
- Clues (new only): pin, code (`dtype_backend`, `DataFrame.map`), error (`Series.iteritems` missing).

### pd-015 (one_directional, symbol_rename): `Series.iteritems` to `Series.items`
- Query: `label_pairs(s)`, "label=value" strings via the Series' own (label, value) iterator.
- Refs: old `s.iteritems()`; portable `s.items()`.
- wrong.py: `enumerate(s)`, positions instead of labels.
- Gold: `pandas.Series.iteritems` / `pandas.Series.items`, replacement rule.
- Clues (new only): pin, code (`date_format`, `DataFrame.map`), error (`DataFrame.applymap` missing).

### pd-016 (one_directional, symbol_removed): `DataFrame.swapaxes` to `transpose`
- Query: `flip(df)`, exchange the two axes with a DataFrame method, not from the raw values.
- Refs: old `df.swapaxes(0, 1)`; portable `df.transpose()`.
- wrong.py: `pd.DataFrame(df.values.T)`, labels lost.
- Gold: `pandas.DataFrame.swapaxes` / `pandas.DataFrame.transpose`, replacement rule.
- Clues (new only): pin, code (`dtype_backend`, `DataFrame.map`), error (`DataFrame.mad` missing).

### pd-017 (one_directional, symbol_removed): `Series.dt.week`: NOT AUTHORED, framework blocker
- Draft: `iso_weeks(dates)`, ISO week numbers through the Series `.dt` accessor; ref_old
  `stamps.dt.week`, ref_portable `stamps.dt.isocalendar().week`, wrong `strftime("%W")`.
  Steps 1 to 3, 5 to 10 passed; **step 4 failed**: "ref_old uses no old_only or
  deprecated_in_new symbol".
- Blocker: `pipeline/signals.py` resolves `.dt.<member>` to the accessor classes
  `DatetimeProperties`, `TimedeltaProperties`, `PeriodProperties` and abstains when they disagree:
  "accessor member differs by dtype: pandas.DatetimeProperties.week=old_only,
  pandas.PeriodProperties.week=shared_same". So no `.dt.week` reference can show an old-only
  symbol, and step 4 cannot pass for this change as frozen. Code was not patched.
- The draft (with its failing validation.json) is kept outside the repository, in the session
  scratchpad (`pd-017-dt-week-blocked/`), and is not committed.
- Options for the owner: (a) the same removal on its index host, `DatetimeIndex.week` to
  `DatetimeIndex.isocalendar().week` (removed in 2.0 in the same release note; `pandas.DatetimeIndex.week`
  is `old_only` and statically detected; replacement already in `replacements.json`); a scratch
  ref pair was checked statically (ref_old shows `pandas.DatetimeIndex.week`, ref_portable no
  exclusive symbol) but not authored, because it changes the frozen change; or (b) substitute the
  first one_directional reserve, `read_csv(error_bad_lines→on_bad_lines)`.

### pd-018 (one_directional, param_rename): `date_range(closed=)` to `inclusive=`
- Query: `days_before(start, end)`, daily dates with `start` kept and `end` dropped, via the
  `date_range` argument that controls the endpoints.
- Refs: old `closed="left"` (FutureWarning in 1.5.3, recorded in step 9); portable `inclusive="left"`.
- wrong.py: default endpoints (both kept).
- Gold: `pandas.date_range(closed)` / `pandas.date_range(inclusive)`, replacement rule.
- Clues (new only): pin, code (`dtype_backend`, `DataFrame.map`), error (`read_csv(error_bad_lines)` rejected).

### pd-019 (one_directional, param_removed): `read_csv(delim_whitespace=True)` to `sep=r"\s+"`
- Query: `load_table(path)`, a file whose columns are separated by runs of blanks, with `read_csv`.
- Refs: old `delim_whitespace=True`; portable `sep=r"\s+"`.
- wrong.py: `sep=" "`, a single space.
- Gold: `pandas.read_csv(delim_whitespace)` / `pandas.read_csv(sep)`, replacement rule.
- Clues (new only): pin, code (`date_format`, `DataFrame.map`), error (`DataFrame.tshift` missing).

### pd-020 (one_directional, param_value): `freq="H"` to `"h"`
- Query: `hour_marks(start, n)`, `n` hourly timestamps with `pd.date_range` and an hourly alias.
- Refs: old `freq="H"`; portable `freq="h"` (accepted by 1.5.3).
- wrong.py: `date_range(start, start + n hours, freq="h")`, one mark too many.
- Gold: `pandas.date_range(freq="H")` / `pandas.date_range(freq="h")`, value rule `H` to `h`.
- Clues (new only): pin, code (`dtype_backend`, `DataFrame.map`), error (`read_csv(date_parser)` rejected).

## Controls (kind: no_conflict, split: test)

All gold symbols are `shared_same` (checked with `load_diff` and `bucket_of`), none touches
frequencies, datetimes, dtype inference, Copy-on-Write, `numeric_only` or `value_counts`.

- **ctl-pd-003** `pandas.cut`: `age_bands(ages, edges, labels)`, labels per age with right-closed
  bands. wrong.py: `right=False`.
- **ctl-pd-004** `pandas.Series.explode`: `one_tag_per_row(tags)`, one row per list element
  keeping the source label. wrong.py: a flattened list comprehension (labels lost).
- **ctl-pd-005** `pandas.Series.nunique`: `distinct_count(s)`, distinct non-missing values as an
  int. wrong.py: `len(s.unique())` (counts NaN). Substituted for a first pick,
  `Series.combine_first` (`patch(primary, fallback)`), which failed **step 7**: its BM25
  distractors were `DataFrame.unstack` and `Series.unstack`, `shared_changed` with chunks from
  both versions, so the retrieved set conflicted; replaced rather than reworded, as dev did for
  `Series.isin`.

## Rules added

- `data/rules/pandas/removals.json`: `pandas.to_datetime(infer_datetime_format)` replacement
  `pandas.to_datetime(format="ISO8601")`, with quote, URL and a dated `corrections` line;
  `data/rules/pandas/replacements.json` regenerated (one new entry). Nothing else under `data/rules` changed.

## Substitutions and items for docs/DECISIONS.md (not edited here, `docs/` is out of scope)

- pd-008: `astype("timedelta64[D]")` failed step 4 (no exclusive symbol on either side; see above);
  replaced by the removal reserve `date_range(freq="YE-JUN")`.
- pd-017: `Series.dt.week` blocked by the accessor abstention in step 4; not authored, owner to choose.
- ctl-pd-005: `Series.combine_first` failed step 7 (conflicting distractors); replaced by `Series.nunique`
  (controls are not part of the freeze).

## Final validate summary

`uv run varag bench validate pd-006 pd-007 pd-008 pd-009 pd-010 pd-011 pd-012 pd-013 pd-014 pd-015 pd-016 pd-018 pd-019 pd-020 ctl-pd-003 ctl-pd-004 ctl-pd-005`
(every step 1 to 10 ok or skipped as designed for each; final lines):

```
pandas: concepts by exclusivity {'behavior': 6, 'one_directional': 7, 'removal': 6}
17/17 concept(s) validated
```

pd-017 is absent (see above), so pandas has 19 concepts, one_directional 7.

The dev pandas concepts (pd-001 to pd-005, ctl-pd-001, ctl-pd-002) were re-validated after the
rule change: 7/7 pass; their regenerated validation.json files differed only in timings and
memory addresses and were restored from git.

`uv run pytest -q`: 330 passed, 1 failed:
`tests/test_sweep.py::test_test_split_is_refused_while_it_has_no_concepts` asserts that the test
split is empty ("no concepts in split 'test'"). Authoring test concepts ends that state, so the
test has to change (it is under `tests/`, out of scope here). `refusals("test")` still refuses,
now with "the prompts are not frozen".

`data/tasks/MANIFEST.json` and `envs/manifest.json` are not committed, as instructed; after the
merge the new concepts must be re-validated on the main checkout to enter its manifest.
