# Authoring: pydantic deprecation test concepts (pyd-019 to pyd-030)

Date: 2026-10-19. Branch `author-pyd-deprecation`, worktree `~/code/varag-author-pyd-deprecation`.
Split `test`, all `exclusivity: deprecation`, `warnings_as_errors: true`. No model calls were made.

Result: **11 of 12 validate (steps 1 to 10)**: pyd-019 to pyd-028 and pyd-030. **pyd-029 is blocked at
step 7 by the framework** (rule precedence in `src/varag/inventory/rules.py`, see below). Its authored files
are parked in `logs/session/authoring-pydantic-deprecation/pyd-029-blocked/`, outside `data/tasks`, so
they do not enter the benchmark or break the corpus unit test.

## Probes of the two substitutes

Run directly with each environment's interpreter (`-I`, `warnings.simplefilter("always")`).

| | old form on V2 (2.13.4) | new form on V1 (1.10.13) |
| --- | --- | --- |
| pyd-029 `@validate_arguments` / `@validate_call` | runs, warns at decoration: `PydanticDeprecatedSince20: The `validate_arguments` method is deprecated; use `validate_call` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.13/migration/` | `ImportError: cannot import name 'validate_call' from 'pydantic'` |
| pyd-030 `parse_obj_as(List[int], ...)` / `TypeAdapter(List[int]).validate_python(...)` | runs, warns at call: `PydanticDeprecatedSince20: `parse_obj_as` is deprecated. Use `pydantic.TypeAdapter.validate_python` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. ...` | `ImportError: cannot import name 'TypeAdapter' from 'pydantic'` |

Both forms pass on their own side. Both pairs are deprecation-class (two-directional with the old form
breaking on V2 only by a warning).

Inventory buckets (`load_diff` + `bucket_of`): `pydantic.validate_arguments` deprecated_in_new,
`pydantic.validate_call` new_only, `pydantic.parse_obj_as` deprecated_in_new, `pydantic.TypeAdapter`
new_only (`pydantic.TypeAdapter.validate_python` is not inventoried: TypeAdapter is not an inventory
root, so gold is the class). All BaseModel gold: every V1 method (`json`, `parse_obj`, `parse_raw`,
`parse_file`, `copy`, `construct`, `schema`, `schema_json`, `validate`) deprecated_in_new, every
`model_*` method new_only; `pydantic.PyObject` deprecated_in_new, `pydantic.types.ImportString` and
`pydantic.ImportString` new_only.

## Rules added

`data/rules/pydantic/bump_pydantic.json`: four entries with `"id": "migration-guide"` appended at the end
of `rules` (the only hand-written pydantic rule file the loader reads), each note quoting the Pydantic V2
migration guide (https://docs.pydantic.dev/2.13/migration/) and stating the environment evidence:

- `pydantic.parse_obj_as` (deprecated_in_new) -> `pydantic.TypeAdapter`; quote, section "Introduction of
  TypeAdapter": "This serves as a complete replacement for `parse_obj_as` and `schema_of` (which are now
  deprecated)."
- `pydantic.TypeAdapter` (new_only).
- `pydantic.validate_arguments` (deprecated_in_new) -> `pydantic.validate_call`; quote, section
  "@validate_arguments has been renamed to @validate_call": "In Pydantic V2, the `@validate_arguments`
  decorator has been renamed to `@validate_call`."
- `pydantic.validate_call` (new_only).

`data/rules/pydantic/replacements.json` regenerated with `varag.inventory.rules.write_replacements("pydantic")`
(no inventory rebuild): one new mapping, `pydantic.parse_obj_as -> pydantic.TypeAdapter`. `varag inventory
audit` still reports pydantic recall 100% (102/102).

## pyd-029 blocker (step 7)

`rules.replacements()` keeps the first rule per old symbol (`setdefault`), and `_pydantic_rules()` loads
`migration.json` before `bump_pydantic.json`. `pydantic._migration.DEPRECATED_MOVED_IN_V2` lists
`pydantic:validate_arguments -> pydantic.deprecated.decorator:validate_arguments`, so the replacement for
`pydantic.validate_arguments` stays `pydantic.deprecated.decorator.validate_arguments` (where the deprecated
shim lives, not a replacement) and the migration-guide entry is shadowed. Step 7 then reports "gold pair not
linked by data/rules" and "retrieved set conflict is False, expected True". Everything else passes
(steps 1 to 6 and 8 to 10 green).

A data-only fix is not available: the alternative old symbols (`pydantic.decorator.validate_arguments`) are
shadowed the same way, and `migration.json` is a dump of the installed package. The fix belongs in
`src/varag/inventory/rules.py` (for example: let hand-written rules take precedence over
`DEPRECATED_MOVED_IN_V2` targets, or do not treat a `pydantic.deprecated.*` relocation as a replacement),
followed by `write_replacements("pydantic")`. The same precedence makes the blend guard's repair message
for `validate_arguments` point at `pydantic.deprecated.decorator.validate_arguments`. Once fixed, move
`pyd-029-blocked/` back to `data/tasks/pydantic/pyd-029/` and run `varag bench validate pyd-029`. No
reserve exists for deprecation except `Field(include)` as one_directional, so nothing was substituted.

## Concepts

Common to all: `split: test`, `change_type: symbol_rename` unless noted, pin and code clues for both sides
(off_target), error clues for both sides from `varag bench make-error-clue` (off_target), each clue
inferring its side alone (step 6). The model is defined in the solution, or the receiver is a parameter
named `model`/`item` (the extractor's pydantic name hints), so step 4 resolves the V1 method call.

| Id | Change | Query (entry point) | ref_old / ref_new | portable_alternative | wrong.py | control_eligible |
| --- | --- | --- | --- | --- | --- | --- |
| pyd-019 | `json` -> `model_dump_json` | `to_json(model)`: any model as a JSON string, dates as ISO, with the model's own JSON method | `model.json()` / `model.model_dump_json()` | plain: `json.dumps(dict(model), default=str)` | `json.dumps(dict(model))`: date not serialisable (TypeError both) | true |
| pyd-020 | `parse_obj` -> `model_validate` | `load_user(data)`: `User(id: int, name: str)` from a dict with the model's dict-parsing classmethod; ValidationError on bad data | `User.parse_obj` / `User.model_validate` | plain: `User(**data)` | `User.construct(**data)`: no coercion (V1 `'7' != 7`; V2 deprecation error) | true |
| pyd-021 | `parse_raw` -> `model_validate_json` | `parse_order(raw)`: `Order(id: int, items: list[str])` from JSON text; malformed JSON and bad fields both ValidationError | `Order.parse_raw` / `Order.model_validate_json` | plain: a wrapper model with a `Json[Order]` field, `_Raw(order=raw).order` (ValidationError for malformed JSON on both sides) | `Order(**json.loads(raw))`: JSONDecodeError on malformed input | false |
| pyd-022 | `parse_file` -> `model_validate_json` on the file text | `load_config(path)`: `AppConfig(name: str, port: int)` from a JSON file path with the model's file-parsing classmethod | `AppConfig.parse_file(path)` / `model_validate_json(Path(path).read_text())` | plain: `AppConfig(**json.loads(Path(path).read_text()))` | `json.load(path)` on a path string (AttributeError both) | false |
| pyd-023 | `copy` -> `model_copy` | `with_price(item, price)`: copy with `price` replaced, original unchanged, with the model's copy method and an update | `item.copy(update=...)` / `item.model_copy(update=...)` | plain: `type(item)(**{**dict(item), "price": price})` | mutates `item` and returns it | true |
| pyd-024 | `construct` -> `model_construct` | `trusted_point(x, y)`: `Point(x: int, y: int)` without validation, values stored as given | `Point.construct` / `Point.model_construct` | guard_only: building an unvalidated instance needs version-specific internals | `Point(x=x, y=y)`: validates and coerces `"1"` | false |
| pyd-025 | `schema` -> `model_json_schema` | `product_schema()`: defines `Product(name: str, price: float)`, returns its JSON Schema dict | `Product.schema()` / `Product.model_json_schema()` | guard_only | `Product.schema_json()`: a string, not a dict | false |
| pyd-026 | `schema_json` -> `json.dumps(model_json_schema())` | `order_schema_text()`: defines `Order(id: int, paid: bool)`, returns its schema as JSON text indented by two spaces | `Order.schema_json(indent=2)` / `json.dumps(Order.model_json_schema(), indent=2)` | guard_only | no indent | false |
| pyd-027 | `validate` -> `model_validate` | `coerce_user(value)`: a `User` instance or a dict to a validated `User` | `User.validate` / `User.model_validate` | plain: `value if isinstance(value, User) else User(**value)` | `User(**value)`: TypeError on an instance | false |
| pyd-028 | `PyObject` -> `ImportString` (`moved_import`) | `load_hook(path)`: `Hook.target` from a dotted path such as "math.sqrt", with pydantic's own field type; ValidationError for an unknown path | `target: PyObject` / `target: ImportString` | guard_only: `try: from pydantic import ImportString except ImportError: PyObject` | `target: Callable`: rejects the string | false |
| pyd-029 (blocked) | `validate_arguments` -> `validate_call` | `scale(value: int, factor: int)`: arguments validated by pydantic's function decorator; `scale("3", "2") == 6`, ValidationError otherwise | `@validate_arguments` / `@validate_call` | guard_only: `try: from pydantic import validate_call ... except ImportError` | `int(value) * int(factor)`: ValueError, not ValidationError | true |
| pyd-030 | `parse_obj_as` -> `TypeAdapter(...).validate_python` | `parse_ids(values)`: validate as `list[int]` with pydantic's helper for a plain type | `parse_obj_as(list[int], values)` / `TypeAdapter(list[int]).validate_python(values)` | plain: a private wrapper model `_Ids(items=values).items` | `[int(v) for v in values]`: ValueError | false |

Gold: old = the V1 symbol above, new = `pydantic.BaseModel.model_*`, `pydantic.types.ImportString`
(pyd-028, the rule's replacement target), `pydantic.validate_call`, `pydantic.TypeAdapter`. Step 9: in every
concept the only soft warning is ref_old's own `PydanticDeprecatedSince20` on V2, and ref_old fails on V2 only
through it; every ref_new fails on V1 by AttributeError or ImportError (collection error).

Notes on portable classification: the queries steer to the model's own method (as pyd-005 does), but
`portable_alternative` records honestly whether a version-independent answer passes the tests: pyd-020,
pyd-021, pyd-022, pyd-027 and pyd-030 have plain answers that bypass the version API. pyd-021 was
first drafted as guard_only; a check before committing found the `Json[Order]` wrapper passes both
environments without warnings, so it is `plain`.

### Clues

| Id | old code (off_target) | new code | old error (V2 API on V1) | new error (V1 API on V2) |
| --- | --- | --- | --- | --- |
| pyd-019 | `Field(regex)`, `anystr_strip_whitespace` | `ConfigDict`, `field_validator` | `field_serializer` ImportError | `Field(regex=)` removed-kwargs |
| pyd-020 | `BaseSettings` | `computed_field`, `model_dump_json` | `AfterValidator` ImportError | `BaseSettings` moved to pydantic-settings |
| pyd-021 | `orm_mode`, `from_orm` | `TypeAdapter`, `model_dump` | `.model_dump()` AttributeError | `@root_validator` without `skip_on_failure` |
| pyd-022 | `ConstrainedStr` | `RootModel` | `computed_field` ImportError | `Field(const=)` removed-kwargs |
| pyd-023 | `max_anystr_length`, `validate_all`, `@validator` | `model_validator` | `model_validator` ImportError | `validate_model` removed (PydanticImportError) |
| pyd-024 | `allow_mutation`, `schema_extra`, `@root_validator` | `field_serializer` | `Model.model_fields` AttributeError | `ConstrainedStr` removed |
| pyd-025 | `BaseSettings`, `anystr_lower` | `ConfigDict(frozen)`, `validate_call` | `TypeAdapter` ImportError | `Field(unique_items=)` removed-kwargs |
| pyd-026 | `Field(unique_items)`, `min_anystr_length`, `parse_obj`, `copy` | `AliasChoices`, `model_validate` | `RootModel` ImportError | `constr(regex=)` unexpected keyword |
| pyd-027 | `allow_population_by_field_name`, `update_forward_refs` | `model_serializer` | `field_validator` ImportError | `NoneStr` removed |
| pyd-028 | `Field(const)`, `Field(regex)`, `parse_obj` | `ConfigDict(from_attributes)`, `model_validate` | `.model_copy()` AttributeError | `parse_raw_as` removed |
| pyd-029 | `BaseSettings`, `@validator` | `field_validator` | `AliasChoices` ImportError | `create_model_from_typeddict` removed |
| pyd-030 | `Field(regex)`, `orm_mode`, `parse_raw` | `ConfigDict`, `Field(pattern)` | `validate_call` ImportError | `pydantic.error_wrappers` removed |

Pins vary per concept (for example `pydantic<2`, `pydantic~=1.10`, `pydantic==1.10.*`, `pydantic>=1.7,<2`
against `pydantic>=2.4,<3`, `pydantic~=2.5`, `pydantic==2.*`, `pydantic>=2.0.3`), each with two unrelated
packages; every pin is decisive for its side only.

## What failed along the way, and the fixes

- pyd-025 and pyd-026, step 4, first draft: `json_schema(model_cls)` taking the class as a parameter. The
  extractor resolves a method receiver only through imports, local BaseModel subclasses or name hints, and
  `schema`/`schema_json` exist on both sides, so `model_cls.schema()` counted as nothing. Rather than
  renaming the parameter to hit a name hint, both queries now define the model in the solution
  (`product_schema()`, `order_schema_text()`); tests and references were not weakened.
- Error clues: `ConfigDict` imports fine on pydantic 1.10.13 (it exists there), so pyd-020's old error uses
  `AfterValidator`; a `__root__` model on V2 raises a TypeError the extractor cannot attribute, so pyd-023's
  new error uses `validate_model`; `stricturl` reproduced as a `network` status in step 6, so pyd-028's new
  error uses `parse_raw_as`.

## Final validate summary

`uv run varag bench validate pyd-019 pyd-020 pyd-021 pyd-022 pyd-023 pyd-024 pyd-025 pyd-026 pyd-027
pyd-028 pyd-029 pyd-030`: 11/12 validated; pyd-029 failed step 7 only (above). After parking pyd-029,
the 11 are in `data/tasks/MANIFEST.json` (not committed, per instruction).

`uv run pytest -q`: 330 passed, 1 failed: `tests/test_sweep.py::test_test_split_is_refused_while_it_has_no_concepts`
asserts that the test split is empty, so it fails as soon as any test concept exists. It is not caused by a
defect in these concepts and needs a test update (outside this assignment's scope). With pyd-029 in
`data/tasks`, `tests/test_corpus_envs.py::test_conflict_true_for_concepts_false_for_control_with_uniform_distractors`
also failed on `pyd-029/old/no-clue` (no conflict, the step-7 blocker); parking it fixed that.
