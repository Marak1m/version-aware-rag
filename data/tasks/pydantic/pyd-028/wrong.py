from typing import Callable

from pydantic import BaseModel


class Hook(BaseModel):
    target: Callable


def load_hook(path):
    return Hook(target=path)
