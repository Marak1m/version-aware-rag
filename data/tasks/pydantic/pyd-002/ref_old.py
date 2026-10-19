from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


def user_from_orm(obj):
    return User.from_orm(obj)
