import json

from pydantic import BaseModel


class AppConfig(BaseModel):
    name: str
    port: int


def load_config(path):
    return AppConfig(**json.load(path))
