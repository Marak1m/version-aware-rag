from solution import product_schema


def test_schema_is_a_dict():
    schema = product_schema()
    assert isinstance(schema, dict)
    assert schema["title"] == "Product"
    assert schema["type"] == "object"


def test_schema_describes_the_fields():
    schema = product_schema()
    assert schema["required"] == ["name", "price"]
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["price"]["type"] == "number"
