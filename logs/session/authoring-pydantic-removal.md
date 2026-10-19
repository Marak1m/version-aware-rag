# Authoring: pydantic removal test concepts and portable controls (2026-10-19)

Worktree `varag-author-pyd-removal`, branch `author-pyd-removal`. No model calls were made.
Split: test. Ids: pyd-008 to pyd-018, ctl-pyd-003 to ctl-pyd-005.

## Probes of the two not-yet-probed substitutes

Run with each environment's interpreter (`envs/pydantic_{old,new}/.venv/bin/python -W always`).

**`constr(regex=)` -> `constr(pattern=)`: two-directional by error (removal).**
- Old form on the new side (2.13.4): error, not a warning, at class definition:
  `TypeError: constr() got an unexpected keyword argument 'regex'`.
- New form on the old side (1.10.13): error at class definition:
  `TypeError: constr() got an unexpected keyword argument 'pattern'` (from `pydantic/types.py`, line 449).
- Each form works on its own side and rejects a non-matching string with `ValidationError`.
- Buckets: `pydantic.constr(regex)` old_only, `pydantic.constr(pattern)` new_only; both have
  `constr` chunks in the corpus. No rule linked them, so one was added (see "Rules added").
- Also recorded in `data/candidates/probes.json` (hand snippet added to `snippets.json`):
  verdict two_directional, class removal.

**`__root__` model -> `RootModel`: two-directional by error (removal).**
- Old form on the new side: error at class definition (`Tags(BaseModel): __root__: List[str]`):
  `TypeError: To define root models, use `pydantic.RootModel` rather than a field called '__root__'`
  (`pydantic/_internal/_model_construction.py`, `inspect_namespace`).
- New form on the old side: `ImportError: cannot import name 'RootModel' from 'pydantic'`.
- `__root__` is a field name, not an inventory symbol, so it cannot be gold. A gold pair that steps
  4 and 7 accept does exist: the natural V1 way to build a custom-root model from a list is
  `Scores.parse_obj(data)` (`BaseModel.parse_obj`, deprecated_in_new) and the V2 one is
  `RootModel` with `Scores.model_validate(data)` (both new_only). Gold is
  `old: [BaseModel.parse_obj]`, `new: [RootModel, BaseModel.model_validate]`; step 7 links the pair
  through the existing BP009 replacement `parse_obj -> model_validate`. The concept is two-directional
  because of `__root__`/`RootModel` (ref_old fails on V2 at class creation, not by the parse_obj
  warning). The concept passed honestly, so no substitution was needed for pyd-018. Not added to
  probes.json: the probe tool only takes rule pairs and release-note candidates of pandas/NumPy.

**Reserve check, `GenericModel`:** `from pydantic.generics import GenericModel` on 2.13.4 only warns
(`PydanticDeprecatedSince20: pydantic.generics:GenericModel has been moved to pydantic.BaseModel`)
and the generic model then works, so it is deprecation class, not removal, and was skipped as a
removal reserve (the frozen list says "if V2 raises on import").

**Reserve check, `Config.keep_untouched` -> `ignored_types`: two-directional by error.**
- Old form on V2: `PydanticUserError: A non-annotated attribute was detected: unit = <...Unit object>`.
- New form on V1: `RuntimeError: no validator found for <class 'Unit'>, see arbitrary_types_allowed in Config`.
- Recorded in probes.json (hand snippet added): verdict two_directional, class removal.

`probes.json` was updated by running `varag.bench.probe.probe_library("pydantic")` and replacing only
the pydantic rows and pydantic counts: `varag bench probe --library pydantic` would rewrite the file
with pydantic rows only and drop the pandas and NumPy rows. None of the 36 existing pydantic rows
changed outcome or verdict; two rows were added.

## Substitution

**pyd-015 `Config.allow_mutation -> frozen` replaced by `Config.keep_untouched -> ignored_types`.**
Failing step: **4**. Authored as designed (`class Config: allow_mutation = False` vs
`ConfigDict(frozen=True)`, test on assignment raising `TypeError` on V1 and `ValidationError` on V2),
it passed steps 1, 2, 3, 6, 7, 8, 9 and 10 but failed step 4: "ref_new uses no new_only symbol;
gold.new pydantic.Config.frozen is in shared_same". `frozen` is a V1 config key too (1.10.13 has
`Config.frozen`), so the V2 answer has no new-only symbol and a V1 user can write `frozen = True`
as well; the pair is not two-directional at the symbol level. Reserves in order: `GenericModel`
only warns on V2 (see above), so the next reserve, `keep_untouched -> ignored_types`, took the id
pyd-015. This needs a dated entry in `docs/DECISIONS.md` (not written here: docs/ is outside this
task's write scope).

## Rules added

`data/rules/pydantic/bump_pydantic.json` (two rules and a `corrections` line), then
`data/rules/pydantic/replacements.json` regenerated with `varag.inventory.rules.write_replacements`
(before the edit the generated mapping equalled the committed file; the only change is the two
entries below).

1. `{"id": "BP008", "symbol": "pydantic.constr(regex)", "expected": ["old_only"], "replacement":
   "pydantic.constr(pattern)"}`. Note quotes bump-pydantic BP008 (`bump_pydantic/codemods/con_func.py`
   at commit a111d41 renames the keyword `regex` to `pattern` when rewriting `constr`) and the
   migration guide, "Changes to pydantic.Field": "`regex` (use `pattern` instead)",
   https://docs.pydantic.dev/2.13/migration/#changes-to-pydanticfield. The guide names the rename for
   `Field`; it does not mention `constr` explicitly, so bump-pydantic's codemod is the primary source
   for the `constr` keyword.
2. `{"id": "BP002", "symbol": "pydantic.Config.keep_untouched", "expected": ["old_only"],
   "replacement": "pydantic.Config.ignored_types"}`. Note quotes bump-pydantic `RENAMED_KEYS`
   (`replace_config.py`, a111d41: `"keep_untouched": "ignored_types"`) and the migration guide,
   "Changes to config": "`keep_untouched` → `ignored_types`",
   https://docs.pydantic.dev/2.13/migration/#changes-to-config. The first transcription had missed it.

Side effect checked: the dev pydantic concepts and controls (pyd-001 to pyd-007, ctl-pyd-001,
ctl-pyd-002) give the same step 7 result and the same recorded `gold_examples` and conflict fields
with the new rules; their validation.json files were not rewritten. Retrieved sets with a `constr`
chunk now also list `rule_replacement:pydantic.constr(regex)` as a conflict reason.

## Concepts

Every removal concept has `warnings_as_errors: false`, pin, code and error clues for both sides
(all `off_target`), error clues made only with `varag bench make-error-clue`.

| Id | Class / change type | Query (entry point) | Gold old -> new | portable | control_eligible |
| --- | --- | --- | --- | --- | --- |
| pyd-008 | removal / param_rename | `make_account(data)`: `user_name` with alias `userName`, accept either through config | `Config.allow_population_by_field_name` -> `Config.populate_by_name` | plain | true |
| pyd-009 | removal / param_rename | `make_contact(email)`: lower-case string fields through config | `Config.anystr_lower` -> `Config.str_to_lower` | plain | false |
| pyd-010 | removal / param_rename | `make_ticker(symbol)`: upper-case string fields through config | `Config.anystr_upper` -> `Config.str_to_upper` | plain | false |
| pyd-011 | removal / param_rename | `make_comment(text)`: cap string fields at 20 chars in config | `Config.max_anystr_length` -> `Config.str_max_length` | plain | false |
| pyd-012 | removal / param_rename | `make_login(secret)`: string fields at least 8 chars in config | `Config.min_anystr_length` -> `Config.str_min_length` | plain | false |
| pyd-013 | removal / param_rename | `product_schema()`: schema with top-level `examples` from config, model's own schema method | `Config.schema_extra` -> `Config.json_schema_extra` | guard_only | true |
| pyd-014 | removal / param_rename | `make_settings(data)`: default `"4"` validated to int 4 through config | `Config.validate_all` -> `Config.validate_default` | plain | false |
| pyd-015 | removal / param_rename (substitute) | `make_reading(value)`: unannotated class attribute `unit = Unit("m")` left untouched through config | `Config.keep_untouched` -> `Config.ignored_types` | plain | false |
| pyd-016 | removal / symbol_rename | `build_org_models()`: models defined in a function, `Optional["Manager"]` forward ref resolved with the class's own method | `BaseModel.update_forward_refs` -> `BaseModel.model_rebuild` | plain | true |
| pyd-017 | removal / param_rename | `make_plate(number)`: `constr` with pattern ^[A-Z]{2}-\d{3}$ in the call | `constr(regex)` -> `constr(pattern)` | guard_only | true |
| pyd-018 | removal / symbol_rename | `parse_scores(data)`: custom-root model of `List[int]`, built with the class's validation classmethod, returns the list | `BaseModel.parse_obj` -> `RootModel`, `BaseModel.model_validate` | plain | false |

References: ref_old uses `class Config` with the V1 key (pyd-016 `Employee.update_forward_refs(Manager=Manager)`,
pyd-017 `constr(regex=)`, pyd-018 `__root__: List[int]` with `parse_obj`); ref_new uses
`model_config = ConfigDict(<V2 key>)` (pyd-013 with `model_json_schema()`, pyd-016 `model_rebuild()`,
pyd-017 `constr(pattern=)`, pyd-018 `RootModel[List[int]]` with `model_validate`).

Why each concept is two-directional: on V2 a class-based V1 key only warns ("Valid config keys have
changed in V2") and is ignored, so the behaviour test fails; on V1 `model_config = ConfigDict(...)`
is ignored, so the test fails the other way. pyd-016: on V2 `update_forward_refs(**localns)` raises
`TypeError: localns arguments are not longer accepted` (without localns it fails on both sides,
which is why the local forward reference makes localns the natural V1 call); on V1 `model_rebuild`
is an AttributeError. pyd-017 and pyd-018: errors as in the probes.

portable_alternative (following the dev precedent that `plain` means a version-independent answer
passes the tests in both environments without a deprecation warning, even when it sidesteps the
query's approach):
- pyd-008: rename `user_name` to the alias by hand before construction (plain).
- pyd-009 / 010 / 011 / 012: `constr(to_lower=True)`, `constr(to_upper=True)`, `constr(max_length=20)`,
  `constr(min_length=8)` (plain).
- pyd-013: guard_only. Generating the schema needs `schema()` on V1 and `model_json_schema()` on V2
  (`schema()` warns on V2), so only a `pydantic.VERSION` guard works.
- pyd-014: declare the default as the integer 4 (plain).
- pyd-015: `unit: ClassVar[Unit] = Unit("m")` (plain).
- pyd-016: declare `Manager` before `Employee`, so no forward reference is needed (plain).
- pyd-017: guard_only, `constr(regex=)` or `constr(pattern=)` chosen by `pydantic.VERSION`.
- pyd-018: a wrapper model with a named field `values: List[int]` (plain).

wrong.py (one natural mistake, fails in both environments):
- pyd-008: alias only, no configuration (field-name input rejected).
- pyd-009: `Field(..., to_lower=True)` (the constr keyword put on Field; no effect).
- pyd-010: `class Config: case_sensitive = False` (a settings key; no effect).
- pyd-011: `class Config: max_length = 20` (wrong key name; no effect).
- pyd-012: `class Config: min_length = 8` (wrong key name; no effect).
- pyd-013: examples on the fields with `Field(example=...)`, schema method picked with getattr (no top-level `examples`).
- pyd-014: `validate_assignment = True` instead of validating defaults (default stays `"4"`).
- pyd-015: annotate `unit: Unit` (no validator / no core schema for `Unit` on either side).
- pyd-016: `Employee.update_forward_refs()` without the local namespace (NameError on V1, PydanticUndefinedAnnotation on V2).
- pyd-017: `constr(min_length=6, max_length=6, to_upper=True)` (a length check instead of the pattern).
- pyd-018: `[int(item) for item in data]` (raises ValueError/TypeError, not ValidationError).

Clues (all off_target). Pins: one `pydantic<2`-style and one `pydantic>=2`-style line among two
unrelated packages, varied per concept. Code clues use exclusive symbols other than the gold
(e.g. `BaseSettings`, `validator`, `parse_obj`, `orm_mode` on the old side; `field_validator`,
`computed_field`, `ConfigDict(...)` keys, `model_dump` on the new side). Error clues:

| Id | old_error (V2 code run on V1) | new_error (V1 code run on V2) |
| --- | --- | --- |
| pyd-008 | `.model_dump()` AttributeError | `ConstrainedStr` PydanticImportError |
| pyd-009 | `computed_field` ImportError | `Field(regex=)` removed-kwargs |
| pyd-010 | `TypeAdapter` ImportError | `Field(unique_items=)` removed-kwargs |
| pyd-011 | `field_serializer` ImportError | `BaseSettings` PydanticImportError |
| pyd-012 | `model_validator` ImportError | `ConstrainedInt` PydanticImportError |
| pyd-013 | `field_validator` ImportError | `Field(const=)` removed-kwargs |
| pyd-014 | `.model_validate()` AttributeError | `constr(regex=)` unexpected keyword |
| pyd-015 | `constr(pattern=)` unexpected keyword | `pydantic.error_wrappers.ErrorWrapper` PydanticImportError |
| pyd-016 | `field_validator` ImportError | `Field(regex=)` removed-kwargs |
| pyd-017 | `.model_dump_json()` AttributeError | `BaseSettings` PydanticImportError |
| pyd-018 | `field_serializer` ImportError | `Field(unique_items=)` removed-kwargs |

pyd-017's first new-side error snippet had a URL default (`"https://example.org/plates"`); step 6's
reproduction classed that run as `network`, so the snippet was changed to a file name and the clue
regenerated.

## Portable controls (D-g, kind portable_control)

| Id | Query | gold.shared (bucket) | wrong.py |
| --- | --- | --- | --- |
| ctl-pyd-003 | `make_rating(stars)`: `conint` from 1 to 5 inclusive | `conint(ge)`, `conint(le)` (shared_same; owner `conint` shared_changed) | `conint(gt=1, lt=5)`, exclusive bounds |
| ctl-pyd-004 | `make_progress(percent)`: `confloat` from 0 to 100 inclusive, fractions allowed | `confloat(ge)`, `confloat(le)` (shared_same; owner shared_changed) | `conint(ge=0, le=100)`, integers only |
| ctl-pyd-005 | `make_username(name)`: `constr` of 3 to 12 characters | `constr(min_length)`, `constr(max_length)` (shared_same; owner shared_changed) | `constr(max_length=12)`, no minimum |

Buckets were checked with `load_diff` + `gold_bucket`/`bucket_of`. Rejected candidates:
`constr(strip_whitespace/to_lower/to_upper)` and every `Field(...)` keyword except `default` are
shared_changed keywords, which the D-g rule (usage touches only shared_same keywords) does not admit;
plain `BaseModel` is shared_unknown. Each control's retrieved set conflicts (recorded, not judged).

## Final validate summary

`uv run varag bench validate pyd-008 pyd-009 pyd-010 pyd-011 pyd-012 pyd-013 pyd-014 pyd-015 pyd-016 pyd-017 pyd-018 ctl-pyd-003 ctl-pyd-004 ctl-pyd-005`:
**14/14 validated**, every step 1 to 10 ok (step 2 skipped for the controls, as for all controls;
step 5 run for every concept, none has `portable_alternative: none`). pydantic now counts
deprecation 3, removal 15 (dev 4 + test 11).

`uv run pytest -q`: 330 passed, 1 failed. The failure is
`tests/test_sweep.py::test_test_split_is_refused_while_it_has_no_concepts`, which asserts the test
split has no concepts; it fails because test concepts now exist. The test split is still refused
(`refusals("test")` returns "the prompts are not frozen"), only the "no concepts" reason is gone.
The test needs updating by whoever owns `tests/` (outside this task's write scope).
