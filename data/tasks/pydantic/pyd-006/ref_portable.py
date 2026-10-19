from pydantic import BaseModel, constr


class User(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)


def make_user(name):
    return User(name=name)
