from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


def load_user(data):
    return User.construct(**data)
