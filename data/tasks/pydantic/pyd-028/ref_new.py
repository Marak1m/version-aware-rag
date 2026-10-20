from pydantic import BaseModel, ImportString


class Hook(BaseModel):
    target: ImportString


def load_hook(path):
    return Hook(target=path)
