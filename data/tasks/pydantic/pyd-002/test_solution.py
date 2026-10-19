from types import SimpleNamespace

from solution import user_from_orm


class Row:
    def __init__(self, id, name):
        self.id = id
        self.name = name


def test_builds_from_attributes():
    user = user_from_orm(Row(7, "Ada"))
    assert (user.id, user.name) == (7, "Ada")
    assert user_from_orm(SimpleNamespace(id="8", name="Bob")).id == 8
