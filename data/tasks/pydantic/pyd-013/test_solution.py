from solution import product_schema


def test_schema_carries_the_example():
    schema = product_schema()
    assert isinstance(schema, dict)
    assert schema["examples"] == [{"name": "pen", "price": 1.5}]


def test_schema_describes_the_fields():
    schema = product_schema()
    assert schema["title"] == "Product"
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["price"]["type"] == "number"
    assert sorted(schema["required"]) == ["name", "price"]
