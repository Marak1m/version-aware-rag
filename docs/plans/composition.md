# Benchmark composition plan (draft for review)

Status: written 2026-10-15, before any new concept is authored. Nothing here is authored or
validated yet. A concept enters the benchmark only by passing `varag bench validate`; a
candidate that fails is dropped or re-tagged, never weakened.

## Constraints

- **Size.** The handoff's full benchmark is 60 concepts plus 15 no-conflict controls, 5 per
  library. This plan keeps 60 concepts and 15 controls. It does not split them 20 per library,
  because pandas and NumPy have little two-directional supply (see "Supply").
- **Caps** (`configs/experiment.yaml`):
  - `one_directional` is at most a third of the whole benchmark.
  - `behavior` is at most 15% of each library, except pandas and NumPy, which may exceed it.
    Behaviour concepts are reported separately (`by_exclusivity`).
- **Parameter level.** At least 40% of concepts are parameter-level (`param_rename`,
  `param_removed`, `default_change`).
- **Split.** About 20% of concepts are dev (`split.dev_fraction`), stratified by library and
  class. The seed concepts are dev.
- **Gold examples.** Keyword-level concepts are all `gold_examples: neither`. Results report
  gold_examples and change_type together.

## Supply

Inventory pairs come from `varag bench candidates`. They are `data/rules` mappings plus inferred
keyword renames.

| Library | Two-directional | One-directional |
| --- | --- | --- |
| pandas | 2: `DataFrame.applymap -> map` (pd-001), `read_csv(date_parser) -> date_format` | 24: 15 symbol, 9 keyword |
| numpy | 2: `trapz -> trapezoid` (np-001), `reshape(newshape) -> shape` | 34: 30 symbol, 4 keyword |
| pydantic | 32: 9 `Config` keys, 16 deprecated-in-V2 methods and helpers, `Field(regex)` (pyd-001), `Field(allow_mutation)`, 5 inferred keyword renames | 4 |

Release-note candidates the inventory cannot see are in `data/candidates/release_notes.json`.
They were mined from the pandas 2.0, 2.1, 2.2 and 3.0 notes and the NumPy 2.0 to 2.4 notes (plus
the NumPy 2.0 migration guide). Each candidate has a quote, a URL, and an `old`/`new` snippet pair
probed in both environments with `varag bench probe`.

- **Probes.** Every call-level direction the notes claim held up, except where marked below.
- **Grades.** The `concept_grade` column is a judgment about concepts, not calls. A concept is
  two-directional only if each version's natural solution breaks on the other under one shared
  test. Several call-level splits only make contrived tasks (asking for an alias string, or for a
  dtype 1.5.3 cannot produce).

| Grade | pandas | numpy |
| --- | --- | --- |
| two_directional | ME, QE, BME, YE-JUN (one alias family); `as_unit` ns integers; `date_range(unit=)`; `value_counts` naming; zoneinfo `.key` vs pytz `.zone`; `future_stack`; `format="ISO8601"`; `include_groups` | `copy=False` vs `copy=None`; `loadtxt` converters (bytes vs str); `unique_inverse` shape |
| one_directional | timedelta `astype("timedelta64[D]")`; `H -> h`; `T -> min`; `errors="ignore"`; Copy-on-Write chained assignment; `numeric_only` default | string-to-bool casts; NEP 50 (each direction a separate task); `float(array)`; `meshgrid` tuple; `count_nonzero` scalar; `mode` abbreviations; `linalg.solve` stacks; uint8 overflow |
| weak or reverse | `datetime64[D]` dtype; `resolution_string`; `freqstr`; `inplace` returning self; out-of-bounds dates; `str` dtype | `floor` integer dtype; `"i8,"` dtype; `copyto` casting; complex `sign`; object `any` |

## Target composition

| Library | removal | deprecation | behavior (two-directional) | one_directional | Concepts | Controls |
| --- | --- | --- | --- | --- | --- | --- |
| pandas | 2 | 0 | 4 | 9 | 15 | 5 |
| numpy | 2 | 0 | 3 | 8 | 13 | 5 |
| pydantic | 12 | 16 | 2 | 2 | 32 | 5 |
| Total | 16 | 16 | 9 | 19 | 60 | 15 |

Checks against the constraints:

- **one_directional:** 19 of 60 (32%), under the cap with one concept of slack. A two-directional
  concept that fails validation removes that slack, so author the two-directional concepts
  first.
- **behavior:** pandas 4 of 15 and NumPy 3 of 13 are exempt; pydantic 2 of 32 is 6%.
- **Two-directional:** pandas 6 and NumPy 5 (your range was 3 to 6); pydantic 30.
- **Parameter level:** about 27 of 60 (45%).
  - pandas 7: `read_csv(date_parser)`, ME and ISO8601 (argument values, see D-a),
    `fillna(method)`, `date_range(closed)`, `read_csv(delim_whitespace)`,
    `read_csv(error_bad_lines)`.
  - NumPy 4: `reshape(newshape)`, `copy=None` (argument value), `loadtxt` encoding default,
    `percentile(interpolation)`.
  - pydantic 16: `Field(regex)`, 9 Config keys, `constr(regex)`, `conlist(min_items)`,
    `Field(allow_mutation)`, `Field(min_items)`, `Config.allow_mutation`, and the int-to-str
    coercion default.
  - Without D-a it is 25 (42%).

### Picks per library

**pandas.**
- *removal:* pd-001 (seed); `read_csv(date_parser) -> date_format`.
- *behavior:* ME (the alias family is limited to two concepts; YE-JUN is the reserve);
  `as_unit` ns integers; `value_counts` naming; `format="ISO8601"`. Reserves: zoneinfo `.key`,
  `future_stack`, `include_groups`, `date_range(unit=)`.
- *one_directional:* `DataFrame.append -> concat`, `iteritems -> items`,
  `swapaxes -> transpose`, `DatetimeProperties.week -> isocalendar`,
  `Series.is_monotonic -> is_monotonic_increasing`, `fillna(method) -> ffill`,
  `date_range(closed) -> inclusive`, `read_csv(delim_whitespace) -> sep`,
  `read_csv(error_bad_lines) -> on_bad_lines`.

**numpy.**
- *removal:* np-001 (seed); `reshape(newshape) -> shape`.
- *behavior:* `copy=None`; `loadtxt` converters; `unique_inverse`.
- *one_directional:* `percentile(interpolation) -> method`, `NaN -> nan`, `float_ -> float64`,
  `cumproduct -> cumprod`, `alltrue -> all`, `asfarray -> asarray`, `row_stack -> vstack`,
  `find_common_type -> promote_types`.

**pydantic.**
- *removal:* pyd-001 (seed); the nine Config key renames (`orm_mode -> from_attributes` and the
  others); `constr(regex -> pattern)` and `conlist(min_items -> min_length)`. These last two need
  a `data/rules` mapping from the migration guide before step 7 can link them.
- *deprecation:* `BaseModel.dict`, `json`, `copy`, `construct`, `parse_obj`, `parse_raw`,
  `parse_file`, `from_orm`, `schema`, `schema_json`, `update_forward_refs` and `validate`;
  `validator`, `root_validator`, `PyObject -> ImportString`; `Field(allow_mutation -> frozen)`.
  All use `warnings_as_errors`.
- *behavior:* int-to-str coercion (V2 needs `coerce_numbers_to_str`) and `Optional` fields without
  a default becoming required. Neither is probed yet.
- *one_directional:* `Field(min_items) -> min_length`, `Config.allow_mutation -> frozen`.

**Controls (14 more):** five per library, each on a `shared_same` symbol whose behaviour did not
change. A pick must be checked against the release-note candidates, so that no control sits on a
behaviour change.

## Decisions needed before authoring

- **D-a.** Add a change type `param_value` for changed argument values (ME, ISO8601, `copy=None`),
  counted as parameter-level. Without it they would be `behavior`, and the parameter-level share
  drops from 45% to 42%.
- **D-b, blocking for behaviour concepts.** Validation step 7 requires the gold pair to be linked
  by `data/rules`, and `doc_conflict` links only old-side symbols to their replacements. A
  behaviour concept's gold is the same symbol on both sides (`date_range`), or a pair no rule maps
  (`Series.astype -> DatetimeProperties.as_unit`). As built, step 7 fails every behaviour
  concept. Proposal:
  - Turn each authored release-note candidate into a `data/rules/<library>/behaviour.json` entry:
    old gold, new gold, quote and URL.
  - Step 7 accepts that entry as the link.
  - `doc_conflict` treats it as a linked pair. A same-symbol entry counts when both versions'
    chunks are in the set.
- **D-c.** The inventory-blind one-directional candidates (pandas H, T, `errors="ignore"`,
  Copy-on-Write, `numeric_only`; NumPy `float(array)`, `meshgrid`, `count_nonzero`, `mode`,
  `solve`, overflow) cannot be `one_directional` concepts. That class's step 4 requires the old
  gold in old_only and the new gold in a shared bucket. Options:
  - let step 4 be skipped for a one_directional concept whose `change_type` is `behavior` or
    `param_value`;
  - or leave them out. They are 11 strong candidates, and no target above depends on them.
- **D-d.** The seed set (M7: 15 concepts, 5 per library) would put 6 one_directional concepts in
  15, because pandas and NumPy have only two inventory two-directional concepts each and the
  handoff keeps behaviour out of the seed set. That breaks the one-third cap. Proposal: allow one
  behaviour concept per pandas and NumPy seed, which gives 4 of 15. The other option is to apply
  the cap only to the full benchmark.
- **D-e.** The per-library sizes depart from the handoff's 20 each: pandas 15, NumPy 13, pydantic
  32. Supply is the reason.

## Authoring order

1. Settle D-a to D-d, and add the rules the picks need: migration-guide mappings for `constr` and
   `conlist`, and behaviour links if D-b is accepted.
2. Author the scarce two-directional concepts first: pandas and NumPy removal and behaviour, then
   pydantic. Run `bench validate` after each, and drop any concept that fails.
3. Author the one_directional concepts, checking the cap after each validation.
4. Author the 14 controls.
5. Assign splits (dev about 20%, stratified), and mark 15 concepts `control_eligible` for the
   version-stated controls (one_directional concepts get none).
6. Error clues wait for `make-error-clue` (M5); until then concepts carry pin and code clues.
