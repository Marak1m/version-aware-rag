# Benchmark composition plan (for review, 2026-10-18)

Status: for review. Nothing below is authored. A concept enters the benchmark only by passing
`varag bench validate`; a candidate that fails is dropped or re-tagged, never weakened.

## Checkpoint

**Met at the probe level, thin for pandas and NumPy.** 136 probe rows are two-directional, well
over the 35 threshold. Rows overstate supply: the pandas alias cross product alone is 74 rows for
one change. Counting distinct changes, 52 are two-directional: pandas 11, NumPy 7, pydantic 34
(31 after merging the `types.*` duplicate paths). At the concept level, where each version's
natural solution must break on the other under one shared test, pandas has 12 usable
two-directional concepts and NumPy 5. The 60-concept target is reachable without a fourth
library, but pandas and NumPy depend on behaviour and value changes the inventory cannot see,
and NumPy's two-directional set is five concepts deep. If the plan should hold more than about 65
concepts, or NumPy should carry more than 13, a fourth library is the way to get it.

## Probed counts

Every candidate's old and new form was run in both environments (`varag bench probe`,
`data/candidates/probes.json`, Linux environments, locks as committed). A pair is two-directional
when each form breaks on the other side (error, timeout, or a deprecation or migration warning);
a pair whose old form breaks on the new side only by warning is `deprecation` class.

Probe rows per library, kind and verdict:

| Library | Kind | two_directional | one_directional | not_discriminative | unprobed |
| --- | --- | --- | --- | --- | --- |
| pandas | symbol | 1 | 15 | 0 | 0 |
| pandas | keyword | 1 | 8 | 0 | 1 (`read_excel(squeeze)`, no Excel engine) |
| pandas | value | 79 | 71 | 2 | 0 |
| pandas | behaviour | 9 | 2 | 0 | 0 |
| numpy | symbol | 1 | 30 | 0 | 0 |
| numpy | keyword | 1 | 4 | 0 | 0 |
| numpy | value | 4 | 17 | 0 | 0 |
| numpy | behaviour | 6 | 5 | 0 | 0 |
| pydantic | symbol | 26 | 0 | 0 | 0 |
| pydantic | keyword | 8 | 1 | 0 | 1 (`ValidationError(errors)`, not a user task) |

Value rules: 216 of 218 records confirmed (the two unconfirmed are `timedelta_range` with
business-hour aliases, which neither side accepts).

Distinct changes per library and class, after collapsing the value cross product into one change
per alias family. "Weak" means the probe is two-directional but no natural task is: the
difference shows only in an alias string, a dtype 1.5.3 cannot produce, or a return value nobody
asks for.

| Library | removal | deprecation | behavior | one_directional | weak or reverse |
| --- | --- | --- | --- | --- | --- |
| pandas | 5: end-of-period aliases (M→ME, Q→QE, Y→YE, BM→BME and the others, 7 callables); `applymap→map`; `read_csv(date_parser→date_format)`; timedelta `astype`; `format="ISO8601"` | 0 | 6: `as_unit` ns integers; `value_counts` naming; `date_range(unit=)`; zoneinfo `.key` vs pytz `.zone`; `future_stack`; `include_groups` | 29: 15 symbols, 8 keywords, sub-day aliases, Timedelta units, `errors="ignore"`, `dtype="datetime64[D]"`, Copy-on-Write, `numeric_only` | 6 |
| numpy | 4: `trapz→trapezoid`; `reshape(newshape→shape)`; `copy=None`; `loadtxt` converters (bytes→str) | 0 | 3: `unique_inverse` shape; string→bool casts; NEP 50 promotion | 40: 30 symbols, 4 keywords, `mode`/`side` abbreviations, 5 behaviours | 5 |
| pydantic | 18 (16 distinct): 9 Config keys; `Field(regex)`; `SecretStr(value)`, `SecretBytes(value)`; `root_validator`; `from_orm`; `update_forward_refs` | 16 (15 distinct): 10 BaseModel methods; `validator`; `PyObject`; `Field(allow_mutation)`, `Field(min_items)`, `Field(max_items)` | 0 | 1: `Field(include→exclude)` | 0 |

NumPy's string→bool and NEP 50 behaviours are two-directional as snippets but each direction
solves a different input, so no single shared test holds both. They are one-directional as
concepts. pandas's timedelta `astype` is two-directional only when the task asks for a timedelta
dtype; the natural new form (`.dt.days`) is portable.

## Target composition

63 concepts, 15 no-conflict controls.

| Library | removal | deprecation | behavior | one_directional | Concepts | Controls |
| --- | --- | --- | --- | --- | --- | --- |
| pandas | 6 | 0 | 6 | 8 | 20 | 5 |
| numpy | 4 | 0 | 1 | 8 | 13 | 5 |
| pydantic | 15 | 15 | 0 | 0 | 30 | 5 |
| Total | 25 | 15 | 7 | 16 | 63 | 15 |

Checks:

- **one_directional:** 16 of 63 (25%); the global cap is 21. Five of slack, so up to five
  two-directional concepts can fail validation before a one-directional one has to go.
- **behavior:** pandas 6 of 20 and NumPy 1 of 13, both exempt from the 15% cap and reported
  separately; pydantic 0.
- **Two-directional:** pandas 12, NumPy 5, pydantic 30.
- **Parameter level:** 29 of 63 (46%) if Config-key changes count as parameter-level (D-f below);
  20 of 63 (32%) if not. The 40% requirement turns on that decision.
- **Instances:** two-directional concepts give 4 ambiguous instances each (two targets, with and
  without a clue) plus 2 version-stated controls when `control_eligible`; one-directional
  concepts give 2. About 220 ambiguous instances in total.

### Picks

**pandas, removal (6).** pd-001 `applymap→map` (exists); `read_csv(date_parser→date_format)`;
end-of-period aliases as two concepts with different tasks (`date_range` month-end;
`resample` quarter-end), the family's cap; `to_datetime(format="ISO8601")` for mixed ISO strings;
timedelta `astype("timedelta64[s]")`. Reserve: `YE-JUN` fiscal year end.

**pandas, behavior (6).** `as_unit` for ns integers; `value_counts` column names; `date_range(unit=)`;
zoneinfo `.key`; `future_stack`; `include_groups`.

**pandas, one_directional (8).** `DataFrame.append→concat`; `iteritems→items`;
`swapaxes→transpose`; `DatetimeProperties.week→isocalendar`; `fillna(method)→ffill`;
`date_range(closed→inclusive)`; `read_csv(delim_whitespace→sep)`; `freq="H"→"h"` (value). Reserve:
`read_csv(error_bad_lines→on_bad_lines)`, `Series.view→astype`, `errors="ignore"→"coerce"`.

**numpy, removal (4).** np-001 `trapz→trapezoid` (exists); `reshape(newshape→shape)`;
`np.array(copy=None)`; `loadtxt` converters receiving `str`.

**numpy, behavior (1).** `unique_inverse` shape.

**numpy, one_directional (8).** `percentile(interpolation→method)`; `NaN→nan`; `float_→float64`;
`cumproduct→cumprod`; `alltrue→all`; `row_stack→vstack`; `take(mode="c"→"clip")` (value);
NEP 50: `uint8 + 300` written as `astype(uint16) + 300`. Reserve: `asfarray→asarray`,
`find_common_type→promote_types`, string→bool cast, `float(array)→.item()`.

**pydantic, removal (15).** pyd-001 `Field(regex→pattern)` (exists); the nine Config keys
(`orm_mode→from_attributes` with `from_orm→model_validate` in the same concept,
`allow_population_by_field_name→populate_by_name`, `anystr_lower→str_to_lower`,
`anystr_strip_whitespace→str_strip_whitespace`, `anystr_upper→str_to_upper`,
`max_anystr_length→str_max_length`, `min_anystr_length→str_min_length`,
`schema_extra→json_schema_extra`, `validate_all→validate_default`); `Config.allow_mutation→frozen`;
`SecretStr(value→secret_value)`; `SecretBytes(value→secret_value)`; `root_validator→model_validator`;
`update_forward_refs→model_rebuild`.

**pydantic, deprecation (15), all `warnings_as_errors`.** `dict→model_dump`; `json→model_dump_json`;
`parse_obj→model_validate`; `parse_raw→model_validate_json`; `parse_file→model_validate_json`;
`copy→model_copy`; `construct→model_construct`; `schema→model_json_schema`;
`schema_json→model_json_schema`; `validate→model_validate`; `validator→field_validator`;
`PyObject→ImportString`; `Field(allow_mutation→frozen)`; `Field(min_items→min_length)`;
`Field(max_items→max_length)`. Reserve: `Field(include→exclude)` (one_directional).

**Controls (15, 5 per library).** pandas and NumPy have 189 and 455 `shared_same` callables; picks
are checked against `probes.json` and `value_rules.json` so no control sits on a changed value or
behaviour (no frequency strings, no datetime parsing). pydantic has 10 `shared_same` callables,
all typing re-exports (`Json`, `types.UUID`, `types.Decimal`); see D-g.

## Split

`dev_fraction` is 0.2 today. The seed set below is 15 concepts and must be dev, since M7 runs it
on the dev split; stratifying by library and class on top of it gives:

| | pandas | numpy | pydantic | Controls |
| --- | --- | --- | --- | --- |
| dev | 5 seeds + 1 behavior = 6 | 5 seeds + 1 behavior = 6 | 5 seeds + 1 removal + 1 deprecation = 7 | 2 per library = 6 |
| test | 14 | 7 | 23 | 9 |

Dev is 19 of 63 concepts (30%). Every class with at least two concepts in a library has one in dev.
This needs `dev_fraction` raised to 0.3 (D-h). Thresholds are frozen on dev clue instances before
any test-split run.

## The 15 seed concepts (M7)

Five per library, the most robust two-directional changes plus one one-directional each, no
behaviour concept (handoff: behaviour is kept out of the seed set):

| Library | Seeds |
| --- | --- |
| pandas | pd-001 `applymap→map` (exists); `read_csv(date_parser→date_format)`; `date_range(freq="M"→"ME")`; `to_datetime(format="ISO8601")`; `fillna(method)→ffill` (one_directional) |
| numpy | np-001 `trapz→trapezoid` (exists); `reshape(newshape→shape)`; `np.array(copy=None)`; `loadtxt` converters; `percentile(interpolation→method)` (one_directional) |
| pydantic | pyd-001 `Field(regex→pattern)` (exists); `Config.orm_mode→from_attributes`; `dict→model_dump`; `validator→field_validator`; `Field(min_items→min_length)` |

Seed controls: ctl-np-001 (exists) plus one more NumPy, two pandas, two pydantic.

## Decisions needed before authoring

- **D-a.** Add change type `param_value` for changed argument values (aliases, `ISO8601`,
  `copy=None`, `mode="c"`), counted as parameter-level.
- **D-b, blocking for value and behaviour concepts.** Step 7 requires the gold pair linked by
  `data/rules`; `doc_conflict` links an old-side symbol to its replacement. Proposal:
  - Value gold is written `pandas.date_range(freq="M")` / `pandas.date_range(freq="ME")`. Step 7
    links it through a confirmed `value_rules` record; `doc_conflict` counts a confirmed value pair
    as linked when both versions' owner chunks are in the set. Step 4 treats a confirmed value
    as old- or new-side evidence (the M5 extractor does the same at keyword weight).
  - Behaviour gold is linked through `data/rules/<library>/behaviour.json`: one entry per authored
    candidate (old gold, new gold, quote, URL, probe id). Same-symbol entries (`date_range` on both
    sides) count when both versions' chunks are present.
- **D-c.** Behaviour-level one-directional candidates (Copy-on-Write, `numeric_only`,
  `float(array)`, `meshgrid` tuples) have no old-side symbol for step 4. Leave them out; the
  targets above do not use them. Value-level ones (`H→h`, `errors="ignore"`) are covered by D-b.
- **D-f.** Count Config-key changes as parameter-level (they are keyword-style settings on a
  class). Without it the parameter-level share is 32%.
- **D-g.** pydantic controls: allow a control whose gold is a `shared_changed` owner when the
  usage touches only `shared_same` keywords and the portable reference passes both environments
  without warnings (step 5 already checks that). Candidates: a `BaseModel` with annotated fields
  and plain instantiation, `Field(default=)`, `Field(ge=, le=)`, `Field(description=)`,
  `conint(gt=)`. Otherwise pydantic has at most two controls (`Json`, `types.UUID`).
- **D-h.** `dev_fraction` 0.2 → 0.3 so the seed set fits in dev with one extra concept per
  library for class coverage.
- **D-i.** Per-library sizes depart from the handoff's 20 each: pandas 20, NumPy 13, pydantic 30.

## Authoring order (after approval)

1. D-a to D-i; add the rules the picks need (`behaviour.json`, migration-guide mappings for
   `constr`/`conlist` if used).
2. The 15 seed concepts, each passing `bench validate`; then stop for the test review.
3. The remaining two-directional concepts (pandas and NumPy first, they are scarce), then the
   one-directional ones, checking the cap after each validation.
4. The 15 controls.
5. Splits as above; `control_eligible` on the two-directional concepts chosen for version-stated
   controls (15 concepts, 30 instances).
6. Error clues wait for `make-error-clue` (M5); until then concepts carry pin and code clues.
