from pydantic import BaseModel, Field


class Account(BaseModel):
    user_name: str = Field(..., alias="userName")


def make_account(data):
    data = dict(data)
    if "user_name" in data and "userName" not in data:
        data["userName"] = data.pop("user_name")
    return Account(**data)
