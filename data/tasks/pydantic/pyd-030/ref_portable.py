from pydantic import BaseModel


class _Ids(BaseModel):
    items: list[int]


def parse_ids(values):
    return _Ids(items=values).items
