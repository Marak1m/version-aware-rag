from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


def coerce_user(value):
    return User.model_validate(value)
