from pydantic import BaseModel


class Settings(BaseModel):
    workers: int = "4"

    class Config:
        validate_assignment = True


def make_settings(data):
    return Settings(**data)
