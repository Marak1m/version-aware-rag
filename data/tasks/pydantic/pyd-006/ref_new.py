from pydantic import BaseModel, field_validator


class User(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("name must not be blank")
        return value


def make_user(name):
    return User(name=name)
