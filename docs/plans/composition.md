# Benchmark composition plan

Status: decided 2026-10-18 (decisions D-a to D-i below, as the user settled them). Nothing is
authored yet; concepts are authored in Part B step 7, after M5 and M6. A concept enters the
benchmark only by passing `varag bench validate`; a candidate that fails is dropped or re-tagged,
never weakened.

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

63 concepts; 10 no-conflict controls (pandas 5, NumPy 5) and 5 portable controls (pydantic).

| Library | removal | deprecation | behavior | one_directional | Concepts | Controls |
| --- | --- | --- | --- | --- | --- | --- |
| pandas | 6 | 0 | 6 | 8 | 20 | 5 no_conflict |
| numpy | 4 | 0 | 1 | 8 | 13 | 5 no_conflict |
| pydantic | 15 | 15 | 0 | 0 | 30 | 5 portable_control |
| Total | 25 | 15 | 7 | 16 | 63 | 15 |

Checks:

- **one_directional:** 16 of 63 (25%); the global cap is 21. Five of slack, so up to five
  two-directional concepts can fail validation before a one-directional one has to go.
- **behavior:** pandas 6 of 20 and NumPy 1 of 13, both exempt from the 15% cap and reported
  separately; pydantic 0.
- **Two-directional:** pandas 12, NumPy 5, pydantic 30.
- **Parameter level:** 29 of 63 (46%): `param_rename`, `param_removed`, `default_change`, the
  new `param_value` (D-a), and Config-key changes (D-f).
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

**No-conflict controls (10).** Five each for pandas and NumPy, on `shared_same` callables (189 and
455 available). Picks are checked against `probes.json` and `value_rules.json` so no control sits
on a changed value or behaviour (no frequency strings, no datetime parsing).

**Portable controls (5, pydantic, D-g).** `kind: portable_control`. The owner is `shared_changed`,
so the retrieved docs may conflict, but the task does not depend on the version: a `BaseModel`
with annotated fields and plain instantiation, `Field(default=)`, `Field(ge=, le=)`,
`Field(description=)`, `conint(gt=)`. Selection rule: the usage touches only `shared_same`
keywords and the portable reference passes both environments without warnings (step 5). The right
behaviour is one answer with no question. `conflict_reason` is recorded, and these are reported
separately from the no-conflict controls.

## Scoring of deprecation concepts

Two scores (user decision 2026-10-18, `configs/experiment.yaml` `scoring.deprecation`):
**strict**, where deprecated usage fails because warnings attributed to the solution are errors;
and **lenient**, where it passes and is flagged `soft_fail`. Strict is the primary score. Both are
reported for every run. The choice is recorded before any test-split run.

## Split (D-h)

Dev is the 15 seed concepts only, about 25% per library; test keeps the remaining 48. Every
class present in a library has a seed. Controls: two per library in dev (the existing ctl-np-001
plus one more NumPy, two pandas, two pydantic portable controls), nine in test.

| | pandas | numpy | pydantic | Total |
| --- | --- | --- | --- | --- |
| dev (seeds) | 5 | 3 | 7 | 15 |
| test | 15 | 10 | 23 | 48 |

Thresholds are frozen on dev clue instances before any test-split run.

## The 15 seed concepts (M7)

Seeds may include behaviour (D-h); each library's seeds cover every class it has.

| Library | Seeds |
| --- | --- |
| pandas (5) | pd-001 `applymap→map` (removal, exists); `read_csv(date_parser→date_format)` (removal); `date_range(freq="M"→"ME")` (removal, param_value); `as_unit` ns integers (behavior); `fillna(method)→ffill` (one_directional) |
| numpy (3) | np-001 `trapz→trapezoid` (removal, exists); `unique_inverse` shape (behavior); `percentile(interpolation→method)` (one_directional) |
| pydantic (7) | pyd-001 `Field(regex→pattern)` (removal, exists); pyd-002 `Config.orm_mode→from_attributes` (removal); pyd-003 `Config.anystr_strip_whitespace→str_strip_whitespace` (removal); pyd-004 `root_validator→model_validator` (removal); pyd-005 `dict→model_dump` (deprecation); pyd-006 `validator→field_validator` (deprecation); pyd-007 `Field(allow_mutation→frozen)` (deprecation) |

Authored and validated 2026-10-19 (all 15 pass `bench validate`, step 6 included). Two substitutions
against the first draft of this table: `SecretStr(value→secret_value)` was dropped because
`SecretStr("x")` is positional in natural code, so a keyword concept would be contrived;
`Field(min_items→min_length)` was dropped because `min_length` exists on V1 too (`shared_changed`),
so step 4 has no new-only gold for it; the same holds for `Field(max_items→max_length)` and
`conlist(min_items)`. Their places went to the `anystr_strip_whitespace` config key and
`Field(allow_mutation→frozen)`. For the full set this removes 3 of the 30 pydantic two-directional
picks; candidates to replace them, to be probed before authoring: `validate_arguments→validate_call`,
`parse_obj_as→TypeAdapter`, `constr(regex→pattern)` (needs a rule mapping from the migration guide).

## Decisions (settled 2026-10-18)

- **D-a, yes.** Change type `param_value` for changed argument values (aliases, `ISO8601`,
  `copy=None`, `mode="c"`); counted as parameter-level.
- **D-b, yes, with conditions.** Value gold is written `pandas.date_range(freq="M")` and linked
  through confirmed value rules: step 7 links the pair through a `value_rules` record with
  `probe.confirmed`, step 4 treats a confirmed value as old- or new-side evidence, and
  `doc_conflict` counts a confirmed value pair as linked when both versions' owner chunks are in
  the set. Behaviour gold is linked through `data/rules/<library>/behaviour.json`, filled from
  every probed behaviour change in the release notes, not only the chosen concepts, counting only
  probe-confirmed entries; behaviour rules feed the doc-conflict test only, never signals. Value
  gold chunks prefer an example that passes the gold value (`freq="M"` in 1.5.3, `freq="ME"` in
  3.0.6), under the both-or-neither example rule.
- **D-c, yes.** Behaviour-only one-directional candidates (Copy-on-Write, `numeric_only`,
  `float(array)`, `meshgrid` tuples) are left out.
- **D-f, yes.** Config-key changes count as parameter-level. The M5 extractor and the M6 guard
  check config keys wherever they appear: `class Config` bodies, `ConfigDict(...)` calls and
  `model_config` dict literals.
- **D-g, changed.** The five pydantic controls are `kind: portable_control`, as above.
- **D-h, changed.** Dev is the 15 seeds only; test keeps 48. Seeds may include behaviour.
- **D-i, yes.** 20 / 13 / 30.

## Authoring order (Part B step 7, after M5 and M6)

1. Infrastructure for D-b and D-g: value-gold syntax in steps 4 and 7 and in `doc_conflict`;
   `behaviour.json` from every probed behaviour change; `kind: portable_control` in the schema,
   instances and reporting; `param_value` in the schema.
2. The 15 seed concepts, each passing `bench validate`; then stop for the test review.
3. The remaining two-directional concepts (pandas and NumPy first, they are scarce), then the
   one-directional ones, checking the cap after each validation.
4. The 15 controls.
5. Splits as above; `control_eligible` on the two-directional concepts chosen for version-stated
   controls (15 concepts, 30 instances).
6. Error clues wait for `make-error-clue` (M5); until then concepts carry pin and code clues.
