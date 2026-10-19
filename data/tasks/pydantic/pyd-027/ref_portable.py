from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


def coerce_user(value):
    return value if isinstance(value, User) else User(**value)
