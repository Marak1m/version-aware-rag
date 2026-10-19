from pydantic import BaseModel


class Settings(BaseModel):
    workers: int = 4


def make_settings(data):
    return Settings(**data)
