from varag.inventory.rules import GONE, GONE_OR_DEPRECATED, _field_kwarg_rules, _migration_expectation

FIELD_KWARGS = {
    "field_params": ["default", "pattern", "min_length", "max_length", "frozen", "exclude", "extra"],
    "keywords": {
        "regex": {"handling": "removed", "exception": "PydanticUserError", "code": "removed-kwargs", "message": "`regex` is removed. use `pattern` instead"},
        "const": {"handling": "removed", "exception": "PydanticUserError", "code": "removed-kwargs", "message": "`const` is removed, use `Literal` instead"},
        "min_items": {"handling": "deprecated", "warning": "PydanticDeprecatedSince20", "message": "`min_items` is deprecated and will be removed, use `min_length` instead"},
        "include": {"handling": "deprecated", "warning": "PydanticDeprecatedSince20", "message": "`include` is deprecated and does nothing. It will be removed, use `exclude` instead"},
    },
}


def test_field_kwarg_rules_classify_and_find_replacements():
    rules = {r.symbol: r for r in _field_kwarg_rules(FIELD_KWARGS)}
    assert rules["pydantic.Field(regex)"].expected == GONE and rules["pydantic.Field(regex)"].replacement == "pydantic.Field(pattern)"
    assert rules["pydantic.Field(const)"].expected == GONE and rules["pydantic.Field(const)"].replacement is None   # Literal is not a Field keyword
    assert rules["pydantic.Field(min_items)"].expected == ("deprecated_in_new",)
    assert rules["pydantic.Field(min_items)"].replacement == "pydantic.Field(min_length)"
    assert rules["pydantic.Field(include)"].replacement == "pydantic.Field(exclude)"
    assert rules["pydantic.Field(regex)"].extra["code"] == "removed-kwargs"


def test_migration_expectation_follows_behaviour_on_the_new_side():
    assert _migration_expectation("MOVED_IN_V2", {"outcome": "raises", "type": "PydanticImportError"}) == GONE
    assert _migration_expectation("MOVED_IN_V2", {"outcome": "resolves", "warnings": ["PydanticDeprecatedSince20"]}) == ("deprecated_in_new",)
    assert _migration_expectation("MOVED_IN_V2", None) == GONE_OR_DEPRECATED
    assert _migration_expectation("DEPRECATED_MOVED_IN_V2", {"outcome": "resolves", "warnings": []}) == ("deprecated_in_new",)
    assert _migration_expectation("REMOVED_IN_V2", None) == GONE
