from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


def user_from_orm(obj):
    return User.model_validate(obj)
