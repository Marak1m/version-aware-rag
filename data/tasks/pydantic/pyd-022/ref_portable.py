import json
from pathlib import Path

from pydantic import BaseModel


class AppConfig(BaseModel):
    name: str
    port: int


def load_config(path):
    return AppConfig(**json.loads(Path(path).read_text(encoding="utf-8")))
