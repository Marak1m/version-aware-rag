from pydantic import BaseModel


class Login(BaseModel):
    secret: str

    class Config:
        min_length = 8


def make_login(secret):
    return Login(secret=secret)
