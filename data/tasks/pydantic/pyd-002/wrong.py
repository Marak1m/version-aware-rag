from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


def user_from_orm(obj):
    return User.parse_obj(obj)
