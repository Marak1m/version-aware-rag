from pydantic import BaseModel, constr


class Login(BaseModel):
    secret: constr(min_length=8)


def make_login(secret):
    return Login(secret=secret)
