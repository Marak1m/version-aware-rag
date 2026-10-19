from pydantic import BaseModel, ConfigDict


class Login(BaseModel):
    model_config = ConfigDict(str_min_length=8)

    secret: str


def make_login(secret):
    return Login(secret=secret)
