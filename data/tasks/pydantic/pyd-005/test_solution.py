from pydantic import BaseModel

from solution import to_record


class User(BaseModel):
    id: int
    name: str
    tags: list = []


def test_record_has_every_field():
    record = to_record(User(id=1, name="Ada", tags=["x"]))
    assert record == {"id": 1, "name": "Ada", "tags": ["x"]}
    assert type(record) is dict
