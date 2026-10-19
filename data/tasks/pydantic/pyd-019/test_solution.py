import json
from datetime import date

from pydantic import BaseModel

from solution import to_json


class Event(BaseModel):
    name: str
    day: date
    tags: list[str] = []


def test_returns_json_text():
    text = to_json(Event(name="launch", day=date(2024, 3, 9), tags=["a", "b"]))
    assert isinstance(text, str)
    assert json.loads(text) == {"name": "launch", "day": "2024-03-09", "tags": ["a", "b"]}


def test_defaults_are_included():
    assert json.loads(to_json(Event(name="x", day=date(2000, 1, 31)))) == {"name": "x", "day": "2000-01-31", "tags": []}
