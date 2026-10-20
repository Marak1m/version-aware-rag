from pydantic import BaseModel, Field


class Account(BaseModel):
    user_name: str = Field(..., alias="userName")

    class Config:
        allow_population_by_field_name = True


def make_account(data):
    return Account(**data)
