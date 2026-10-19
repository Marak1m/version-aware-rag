from pydantic import BaseModel, constr


class Username(BaseModel):
    name: constr(min_length=3, max_length=12)


def make_username(name):
    return Username(name=name)
