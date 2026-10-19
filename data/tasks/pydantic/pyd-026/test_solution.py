import json

from solution import order_schema_text


def test_schema_is_indented_json_text():
    text = order_schema_text()
    assert isinstance(text, str)
    assert text.startswith('{\n  "')


def test_schema_content():
    schema = json.loads(order_schema_text())
    assert schema["title"] == "Order"
    assert schema["type"] == "object"
    assert schema["required"] == ["id", "paid"]
    assert schema["properties"]["id"]["type"] == "integer"
    assert schema["properties"]["paid"]["type"] == "boolean"
