from pydantic import BaseModel, Field


class Account(BaseModel):
    user_name: str = Field(..., alias="userName")


def make_account(data):
    return Account(**data)
