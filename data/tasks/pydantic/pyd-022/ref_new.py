from pathlib import Path

from pydantic import BaseModel


class AppConfig(BaseModel):
    name: str
    port: int


def load_config(path):
    return AppConfig.model_validate_json(Path(path).read_text(encoding="utf-8"))
