from pydantic import BaseModel, ConfigDict, Field


class Account(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_name: str = Field(..., alias="userName")


def make_account(data):
    return Account(**data)
