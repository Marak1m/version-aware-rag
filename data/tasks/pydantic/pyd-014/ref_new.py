from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(validate_default=True)

    workers: int = "4"


def make_settings(data):
    return Settings(**data)
